"""Microsoft Entra ID (Azure AD) sign-in — OpenID Connect authorization-code flow.

Why this module exists
----------------------
Streamax runs BOTH Coremail and Microsoft 365. `login.py` verifies a password by
performing an SMTP AUTH login, which works against Coremail but fails for M365:
Microsoft turns SMTP AUTH (basic authentication) off tenant-wide by default and
answers `535 5.7.139 ... SmtpClientAuthentication is disabled for the Tenant`.
That is a tenant policy, not a wrong password, and it cannot be worked around
from our side. The supported way to authenticate an M365 user is OAuth2/OIDC —
"Sign in with Microsoft" — which is what this module implements.

It is deliberately dependency-free (stdlib `urllib` only): no `msal`, no
`cryptography`, nothing new in the Docker image.

Security model
--------------
* PKCE (S256) + `state` + `nonce`. All three, plus the post-login destination,
  travel in ONE short-lived HMAC-signed cookie, so the flow keeps no server-side
  state and works across multiple Render instances.
* The ID token is fetched by this server directly from Microsoft's token
  endpoint over certificate-validated TLS. Per OIDC Core §3.1.3.7, TLS server
  validation may stand in for verifying the JWT signature when the token arrives
  over that direct back-channel — which is the only way it arrives here. We
  still validate every claim that decides *who the user is*: `iss`, `aud`,
  `tid`, `exp` and `nonce`.
* The app registration is single-tenant AND `tid` is re-checked here, so a
  Microsoft account belonging to any other tenant cannot sign in even if the
  registration is later loosened by accident.
* The resulting address must still sit in MS_ALLOWED_DOMAINS (default
  `streamax.com`) — the same domain gate the password path applies.

Configuration (environment variables)
-------------------------------------
    MS_TENANT_ID       Directory (tenant) ID   — required
    MS_CLIENT_ID       Application (client) ID — required
    MS_CLIENT_SECRET   Client secret VALUE     — required
    MS_REDIRECT_URI    Optional override; otherwise derived from the request
                       (honouring X-Forwarded-Proto/Host behind Cloudflare).
    MS_ALLOWED_DOMAINS Optional CSV, default "streamax.com".

Sign-in is simply hidden until all three required values are present, so
deploying this file changes nothing until the tenant is configured.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AUTHORITY = "https://login.microsoftonline.com"
SCOPES = "openid profile email"
STATE_COOKIE = "stmx_oauth"
STATE_TTL = 900          # 15 minutes to complete a sign-in
HTTP_TIMEOUT = 15

CALLBACK_PATH = "/auth/microsoft/callback"


# ── config ──────────────────────────────────────────────────────────────────

def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def tenant_id() -> str:
    return _env("MS_TENANT_ID")


def client_id() -> str:
    return _env("MS_CLIENT_ID")


def _client_secret() -> str:
    return _env("MS_CLIENT_SECRET")


def allowed_domains() -> list[str]:
    raw = _env("MS_ALLOWED_DOMAINS", "streamax.com")
    return [d.strip().lower().lstrip("@") for d in raw.split(",") if d.strip()]


def is_configured() -> bool:
    """True once tenant + client id + secret are all present."""
    return bool(tenant_id() and client_id() and _client_secret())


def _log(msg: str) -> None:
    print(f"[MSAUTH] {msg}", file=sys.stderr, flush=True)


# ── signed state cookie ─────────────────────────────────────────────────────
# Shares AUTH_SECRET with the session cookie in server.py — one secret to set.

def _secret() -> bytes:
    return (_env("AUTH_SECRET") or "insecure-development-fallback").encode()


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def safe_next(path: str) -> str:
    """Clamp a post-login destination to a same-site absolute path.

    `startswith("/")` alone is NOT enough: "//evil.com" and "/\\evil.com" are
    protocol-relative URLs that browsers happily follow off-site.
    """
    p = (path or "").strip()
    if not p.startswith("/") or p.startswith("//") or p.startswith("/\\"):
        return "/"
    return p


def _pack(data: dict) -> str:
    body = _b64e(json.dumps(data, separators=(",", ":")).encode())
    sig = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{body}.{sig}"


def _unpack(token: str) -> dict | None:
    if not token or "." not in token:
        return None
    body, _, sig = token.rpartition(".")
    expect = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(expect, sig):
        return None
    try:
        data = json.loads(_b64d(body))
    except Exception:
        return None
    if not isinstance(data, dict) or time.time() > float(data.get("exp") or 0):
        return None
    return data


# ── step 1: send the browser to Microsoft ───────────────────────────────────

def begin(redirect_uri: str, next_path: str = "/") -> tuple[str, str]:
    """Return (authorize_url, state_cookie_value).

    The caller redirects to `authorize_url` and sets STATE_COOKIE to the second
    value (HttpOnly, SameSite=Lax — the callback is a top-level GET, so Lax
    still sends it).
    """
    verifier = _b64e(secrets.token_bytes(48))
    challenge = _b64e(hashlib.sha256(verifier.encode("ascii")).digest())
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)

    cookie = _pack({
        "s": state,
        "n": nonce,
        "v": verifier,
        "next": safe_next(next_path),
        "exp": int(time.time()) + STATE_TTL,
    })

    query = urllib.parse.urlencode({
        "client_id": client_id(),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "response_mode": "query",
        "scope": SCOPES,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        # Always show the account picker: shared machines and multi-account
        # browsers otherwise silently reuse whoever signed in last.
        "prompt": "select_account",
    })
    return f"{AUTHORITY}/{tenant_id()}/oauth2/v2.0/authorize?{query}", cookie


# ── step 2: handle Microsoft's callback ─────────────────────────────────────

def _post_token(form: dict) -> tuple[dict | None, str]:
    body = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(
        f"{AUTHORITY}/{tenant_id()}/oauth2/v2.0/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT,
                                    context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode("utf-8")), ""
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            payload = json.loads(e.read().decode("utf-8"))
            detail = payload.get("error_description") or payload.get("error") or ""
        except Exception:
            pass
        _log(f"token endpoint HTTP {e.code}: {detail[:300]}")
        return None, detail.splitlines()[0] if detail else f"Microsoft returned HTTP {e.code}."
    except Exception as e:
        _log(f"token endpoint unreachable: {e}")
        return None, "Could not reach Microsoft. Try again."


def _claims(id_token: str) -> dict | None:
    """Decode the ID token payload. Signature is NOT checked — see module docstring."""
    parts = (id_token or "").split(".")
    if len(parts) != 3:
        return None
    try:
        data = json.loads(_b64d(parts[1]))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _email_from(claims: dict) -> str:
    """Best available address. Work accounts normally carry `preferred_username`
    (the UPN); `email` appears when the optional claim / mail attribute is set."""
    for key in ("email", "preferred_username", "upn", "unique_name"):
        val = str(claims.get(key) or "").strip().lower()
        if "@" in val:
            return val
    return ""


def complete(code: str, state_param: str, cookie_value: str,
             redirect_uri: str) -> tuple[str, str, str]:
    """Finish the flow. Returns (email, next_path, error) — email is "" on failure."""
    data = _unpack(cookie_value or "")
    if not data:
        return "", "/", "Sign-in took too long or the browser dropped the session. Please try again."
    next_path = safe_next(str(data.get("next") or "/"))

    if not code:
        return "", next_path, "Microsoft did not return an authorization code."
    if not hmac.compare_digest(str(data.get("s") or ""), state_param or ""):
        return "", next_path, "Sign-in could not be verified. Please try again."

    payload, err = _post_token({
        "client_id": client_id(),
        "client_secret": _client_secret(),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": data.get("v") or "",
        "scope": SCOPES,
    })
    if payload is None:
        return "", next_path, err or "Microsoft sign-in failed."

    claims = _claims(payload.get("id_token") or "")
    if not claims:
        return "", next_path, "Microsoft did not return a readable identity token."

    # --- claim validation ---------------------------------------------------
    if str(claims.get("tid") or "") != tenant_id():
        _log(f"tenant mismatch: token tid={claims.get('tid')!r}")
        return "", next_path, "That account belongs to a different organisation."
    if str(claims.get("aud") or "") != client_id():
        _log(f"audience mismatch: aud={claims.get('aud')!r}")
        return "", next_path, "Sign-in could not be verified. Please try again."
    if str(claims.get("iss") or "") != f"{AUTHORITY}/{tenant_id()}/v2.0":
        _log(f"issuer mismatch: iss={claims.get('iss')!r}")
        return "", next_path, "Sign-in could not be verified. Please try again."
    if not hmac.compare_digest(str(claims.get("nonce") or ""), str(data.get("n") or "")):
        _log("nonce mismatch")
        return "", next_path, "Sign-in could not be verified. Please try again."
    try:
        if time.time() > float(claims.get("exp") or 0):
            return "", next_path, "Microsoft sign-in expired. Please try again."
    except (TypeError, ValueError):
        return "", next_path, "Sign-in could not be verified. Please try again."

    email = _email_from(claims)
    if not email:
        return "", next_path, "Microsoft did not return an email address for that account."

    domains = allowed_domains()
    if domains and email.rsplit("@", 1)[-1] not in domains:
        _log(f"domain rejected: {email}")
        return "", next_path, "Please sign in with your Streamax account."

    _log(f"signed in {email} (oid={claims.get('oid')})")
    return email, next_path, ""
