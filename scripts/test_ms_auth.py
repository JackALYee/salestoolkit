"""Exercise ms_auth against a fake Microsoft — happy path + attacks.

Standalone, no pytest, no network:  python3 scripts/test_ms_auth.py
"""
import base64, importlib, json, os, pathlib, sys, time, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

TENANT = "11111111-2222-3333-4444-555555555555"
CLIENT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
os.environ.update(MS_TENANT_ID=TENANT, MS_CLIENT_ID=CLIENT,
                  MS_CLIENT_SECRET="shhh", AUTH_SECRET="unit-test-secret")

import ms_auth as ms
importlib.reload(ms)

REDIRECT = "https://streamax-salestoolkit.com/auth/microsoft/callback"
ok = fail = 0


def check(label, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}  {detail}")


def b64(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")


def id_token(**over):
    c = {"iss": f"{ms.AUTHORITY}/{TENANT}/v2.0", "aud": CLIENT, "tid": TENANT,
         "exp": time.time() + 3600, "oid": "user-object-id",
         "preferred_username": "JCYi@streamax.com", "name": "Jack Yi"}
    c.update(over)
    return f"{b64({'alg':'RS256'})}.{b64(c)}.fakesignature"


def fake_ms(**over):
    """Patch the token endpoint to hand back a token with these claim overrides.
    Real Microsoft echoes the request nonce into the id_token, so unless a test
    overrides it, so does this fake."""
    def _post(form):
        fake_ms.last_form = form
        claims = dict(over)
        claims.setdefault("nonce", fake_ms.nonce)
        return {"id_token": id_token(**claims), "access_token": "x"}, ""
    ms._post_token = _post


def run(next_path="/", **over):
    fake_ms(**over)
    url, cookie = ms.begin(REDIRECT, next_path)
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    fake_ms.nonce = q["nonce"][0]
    return ms.complete("the-code", q["state"][0], cookie, REDIRECT), url, cookie


print("\n--- authorize request ---")
_, url, cookie = run()
q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
check("authorize URL targets the configured tenant", f"/{TENANT}/oauth2/v2.0/authorize" in url, url)
check("PKCE S256 challenge sent", q.get("code_challenge_method") == ["S256"] and q.get("code_challenge"))
check("nonce sent", bool(q.get("nonce")))
check("response_type=code (no implicit token in the URL)", q.get("response_type") == ["code"])
check("account picker forced", q.get("prompt") == ["select_account"])
check("redirect_uri echoed exactly", q.get("redirect_uri") == [REDIRECT])
check("state cookie carries no plaintext secret", "streamax" not in cookie.lower())

print("\n--- happy path ---")
(email, nxt, err), _, _ = run()
check("signs in and lower-cases the UPN", email == "jcyi@streamax.com", f"got {email!r} err={err!r}")
check("no error", err == "")
check("verifier posted back to the token endpoint", "code_verifier" in fake_ms.last_form)
check("client secret posted server-side only", fake_ms.last_form.get("client_secret") == "shhh")

print("\n--- claim source fallbacks ---")
(email, _, _), _, _ = run(preferred_username="x", email="Real.Person@streamax.com")
check("prefers the email claim when present", email == "real.person@streamax.com", email)
(email, _, _), _, _ = run(preferred_username=None, upn="upn.user@streamax.com")
check("falls back to upn", email == "upn.user@streamax.com", email)
(email, _, e), _, _ = run(preferred_username=None, upn=None, unique_name=None, email=None)
check("rejects a token with no address", email == "" and "email address" in e, e)

print("\n--- attacks ---")
(email, _, e), _, _ = run(tid="99999999-9999-9999-9999-999999999999")
check("rejects another tenant's account", email == "" and "different organisation" in e, e)

(email, _, e), _, _ = run(aud="some-other-app")
check("rejects a token minted for a different app (aud)", email == "", e)

(email, _, e), _, _ = run(iss="https://login.microsoftonline.com/evil/v2.0")
check("rejects a bad issuer", email == "", e)

(email, _, e), _, _ = run(exp=time.time() - 60)
check("rejects an expired id_token", email == "", e)

(email, _, e), _, _ = run(preferred_username="attacker@gmail.com")
check("rejects a non-streamax domain", email == "" and "Streamax account" in e, e)

(email, _, e), _, _ = run(nonce="not-the-one-we-sent")
check("rejects a replayed token (nonce mismatch)", email == "", e)

url, cookie = ms.begin(REDIRECT, "/")
email, _, e = ms.complete("c", "attacker-chosen-state", cookie, REDIRECT)
check("rejects a forged state (CSRF)", email == "", e)

body, _, sig = cookie.rpartition(".")
email, _, e = ms.complete("c", "x", f"{body}.{'0' * 32}", REDIRECT)
check("rejects a tampered state cookie signature", email == "", e)

expired = ms._pack({"s": "s", "n": "n", "v": "v", "next": "/", "exp": time.time() - 1})
email, _, e = ms.complete("c", "s", expired, REDIRECT)
check("rejects an expired state cookie", email == "", e)

email, _, e = ms.complete("c", "s", "", REDIRECT)
check("rejects a missing state cookie", email == "", e)

print("\n--- open redirect ---")
for bad in ["//evil.com", "/\\evil.com", "https://evil.com", "javascript:alert(1)"]:
    (_, nxt, _), _, _ = run(next_path=bad)
    check(f"clamps next={bad!r} to /", nxt == "/", f"got {nxt!r}")
(_, nxt, _), _, _ = run(next_path="/jerry")
check("keeps a legitimate next=/jerry", nxt == "/jerry", nxt)

print("\n--- configuration gate ---")
saved = os.environ.pop("MS_CLIENT_SECRET")
check("hidden until fully configured", ms.is_configured() is False)
os.environ["MS_CLIENT_SECRET"] = saved
check("enabled once configured", ms.is_configured() is True)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
