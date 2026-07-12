"""Cookie-based session persistence for the Sales Toolkit.

The toolkit's login already sets st.session_state['authenticated']. The
problem: Streamlit's session_state lives only inside one WebSocket
connection. Refreshing the tab, or navigating to ?view=jerry_gpt with
target="_top", opens a new connection and wipes session_state — forcing
re-login.

This module adds a browser cookie that carries a signed session token
across reloads. On every Streamlit run, restore_session() checks the
cookie, verifies the signature, and re-hydrates session_state.

Security model:
- Token = "<user>:<expiry_unix>:<sha256_hmac_truncated>"
- Signature uses st.secrets["AUTH_SECRET"] (or env var AUTH_SECRET).
- An attacker who can read the user's cookie can impersonate them
  (same trust model as the existing shared SMTP-validated login —
  good enough for an internal sales tool, not for handling PII).
- Tokens expire after COOKIE_EXPIRY_DAYS so a leaked cookie is bounded.

If AUTH_SECRET isn't set, a built-in fallback secret is used. This works
but anyone with the source can forge tokens — set AUTH_SECRET in
secrets.toml for any non-trivial deployment.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components

try:
    import extra_streamlit_components as stx
    _STX_AVAILABLE = True
except ImportError:
    _STX_AVAILABLE = False


COOKIE_NAME = "stmx_auth"
COOKIE_EXPIRY_DAYS = 7
_FALLBACK_SECRET = "stmx-default-set-AUTH_SECRET-in-secrets-toml"


# ---------------------------------------------------------------------------
# Token signing / verification
# ---------------------------------------------------------------------------

def _get_secret() -> str:
    try:
        s = st.secrets.get("AUTH_SECRET")
        if s:
            return str(s)
    except Exception:
        pass
    return os.environ.get("AUTH_SECRET", _FALLBACK_SECRET)


def _sign(payload: str) -> str:
    """Truncated SHA-256 of payload + secret. Not full HMAC but adequate here."""
    secret = _get_secret()
    return hashlib.sha256(f"{payload}|{secret}".encode("utf-8")).hexdigest()[:24]


def _make_token(user: str) -> str:
    """Compose: 'user:expiry_unix:signature'."""
    expiry = int((datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)).timestamp())
    payload = f"{user}:{expiry}"
    return f"{payload}:{_sign(payload)}"


def _verify_token(token: str) -> str | None:
    """Return username if token is valid + non-expired, else None."""
    if not token or token.count(":") < 2:
        return None
    payload, sig = token.rsplit(":", 1)
    if _sign(payload) != sig:
        return None
    try:
        user, expiry_str = payload.rsplit(":", 1)
        expiry = int(expiry_str)
    except (ValueError, TypeError):
        return None
    if datetime.now().timestamp() > expiry:
        return None
    return user


# ---------------------------------------------------------------------------
# Cookie manager
# ---------------------------------------------------------------------------
#
# `stx.CookieManager(key=...)` is a Streamlit widget. Streamlit's rules:
#   - Cannot be wrapped in @st.cache_resource (raises CachedWidgetWarning).
#   - Cannot be instantiated twice in the same run with the same key.
#   - MUST be instantiated each run for the widget to be rendered/refreshed.
#
# Strategy: instantiate exactly once per run (inside `init()`), store the
# instance in st.session_state so any later helper (persist_login, logout)
# in the same run reuses it without re-creating the widget. The next run
# overwrites the stored instance with a fresh one.

_SESSION_CM_KEY = "_stmx_cookie_mgr"


def init() -> None:
    """Instantiate the cookie manager once for this Streamlit run.

    Call this near the top of app.py before any other auth helpers.
    Safe to call multiple times in one run (idempotent — only the first
    call actually creates the widget; subsequent calls are no-ops).
    """
    if not _STX_AVAILABLE:
        return
    # If something already instantiated the manager this run, leave it alone.
    # (This relies on the convention that `init()` is called once per run.
    # session_state persists across reruns, but the value we stash is itself
    # overwritten each call below, so stale references are fine.)
    if _SESSION_CM_KEY in st.session_state and st.session_state.get(
        "_stmx_cm_run_marker"
    ):
        return
    st.session_state[_SESSION_CM_KEY] = stx.CookieManager(key="stmx_cookie_mgr")
    st.session_state["_stmx_cm_run_marker"] = True


def _cm():
    """Return the run's cookie manager. Auto-inits if needed."""
    if _SESSION_CM_KEY not in st.session_state:
        init()
    return st.session_state.get(_SESSION_CM_KEY)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Session-state key set by logout() and respected by restore_session().
# Sticky across reruns within the same tab; only cleared by persist_login()
# (i.e. a fresh, explicit authentication). Defends against the async
# extra-streamlit-components CookieManager.delete() not propagating to the
# browser before the next rerun reads the cookie back — which used to cause
# silent auto-re-authentication immediately after Sign Out.
LOGOUT_FLAG_KEY = "_stmx_just_logged_out"


def restore_session() -> None:
    """Re-hydrate session_state from the auth cookie if valid.

    Call this once near the top of app.py, BEFORE checking
    st.session_state['authenticated']. Safe to call when already
    authenticated (no-op for the auth check; the cookie manager still
    initializes so persist_login/logout can use it later in the same run).
    """
    # Reset the per-run marker so init() will create a fresh CookieManager
    # widget for this run (Streamlit requires re-registration each run).
    st.session_state.pop("_stmx_cm_run_marker", None)
    st.session_state.pop(_SESSION_CM_KEY, None)
    init()

    if st.session_state.get("authenticated"):
        return

    # If the user just clicked Sign Out in this tab, refuse to auto-restore
    # from cookie. The flag stays set across reruns until persist_login()
    # explicitly pops it, so even multiple Streamlit auto-reruns triggered
    # by the cookie component reporting back can't silently re-authenticate.
    if st.session_state.get(LOGOUT_FLAG_KEY):
        return

    cm = _cm()
    if cm is None:
        return
    token = cm.get(COOKIE_NAME)
    if not token:
        return
    user = _verify_token(token)
    if user:
        st.session_state["authenticated"] = True
        st.session_state["user_name"] = user
        # Re-derive leadership clearance + canonical email from the restored
        # user identity so Jerry GPT enforces access control and the
        # jhsun-only Streamaxpedia customizations (Emily, Global Trucking
        # title, Jack GPT route) survive a page reload. The cookie carries
        # only the user_name (display name for easter-egg accounts, full
        # email for regular logins) — we look up the matching email here.
        try:
            from login import resolve_leadership, resolve_user_email, resolve_vip
            st.session_state["is_leadership"] = resolve_leadership(user)
            st.session_state["is_vip"] = resolve_vip(user)
            restored_email = resolve_user_email(user)
            if restored_email:
                st.session_state["user_email"] = restored_email
        except Exception:
            st.session_state["is_leadership"] = False
            st.session_state["is_vip"] = False


# Session keys cleared on logout.
_AUTH_KEYS = (
    "authenticated", "user_name", "user_email",
    "is_leadership", "is_vip", "user_password",
    "_stmx_cookie_synced",
)


def _nav_top_search(view: str) -> None:
    """Navigate the TOP window to the same path with query = ?view=<view> (or
    no query when view is empty). Writing location.search is allowed even when
    the component iframe is cross-origin to the top window (unlike reading
    location, or touching document.cookie), so this is the safe way to redirect
    + drop the ?logout param while preserving the view."""
    search = json.dumps(f"?view={view}" if view else "")
    components.html(
        f"""
        <script>
          setTimeout(function() {{
            try {{ window.top.location.search = {search}; }}
            catch (e) {{ window.location.search = {search}; }}
          }}, 300);
        </script>
        """,
        height=0,
    )


def persist_login(user_name: str) -> None:
    """Write the signed token to the auth cookie via CookieManager.

    IMPORTANT — call this on a run that COMMITS (i.e. is NOT followed by
    st.rerun() in the same run). CookieManager.set sends the write as part of
    the run's frontend delta; an st.rerun() right after discards that delta and
    the cookie is never written. app.py calls this once per connection from the
    authenticated render path (a committed run), which is what makes the
    CURRENT identity reach the cookie and survive the ?view=jerry_gpt
    cross-navigation. Also clears the post-logout guard.
    """
    cm = _cm()
    if cm is not None:
        expires_at = datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
        try:
            cm.set(COOKIE_NAME, _make_token(user_name), expires_at=expires_at)
        except Exception:
            pass
    st.session_state.pop(LOGOUT_FLAG_KEY, None)


def logout() -> None:
    """Clear session state and the auth cookie + set the sticky logout guard.

    Prefer logout_and_redirect() from the app's logout handler — it navigates
    via st.stop() so the cookie delete is actually committed. This bare
    logout() stays for callers that handle navigation themselves.
    """
    cm = _cm()
    if cm is not None:
        try:
            cm.set(COOKIE_NAME, "", expires_at=datetime.now() - timedelta(days=1))
        except Exception:
            pass
        try:
            cm.delete(COOKIE_NAME)
        except Exception:
            pass
    for key in _AUTH_KEYS:
        st.session_state.pop(key, None)
    st.session_state[LOGOUT_FLAG_KEY] = True


def logout_and_redirect(view: str = "") -> None:
    """Clear session + cookie and navigate to the (view-preserving) URL, then
    st.stop().

    st.stop() (unlike st.rerun) COMMITS the run's delta, so the CookieManager
    delete actually reaches the browser. The JS then navigates the top window
    to ?view=<view> (dropping ?logout). `view` ("jerry_gpt" / "") is preserved
    so signing out of Jerry GPT and signing back in returns to Jerry GPT, not
    the toolkit.
    """
    cm = _cm()
    if cm is not None:
        try:
            cm.set(COOKIE_NAME, "", expires_at=datetime.now() - timedelta(days=1))
        except Exception:
            pass
        try:
            cm.delete(COOKIE_NAME)
        except Exception:
            pass
    for key in _AUTH_KEYS:
        st.session_state.pop(key, None)
    st.session_state[LOGOUT_FLAG_KEY] = True
    _nav_top_search(view)
    st.stop()


def current_user() -> str | None:
    """Return the logged-in user's name, or None."""
    if not st.session_state.get("authenticated"):
        return None
    return st.session_state.get("user_name")
