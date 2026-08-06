"""Streamax Sales Toolkit — plain-HTML web server (replaces Streamlit).

Phase 2 of the rebuild. Serves the static toolkit built by `build_static.py`,
a real login page, and a native Jerry GPT chat UI — with the API keys held
server-side where they belong.

Routes
  GET  /             toolkit (site/index.html)      [auth]
  GET  /login        login page
  POST /api/login    dual-backend SMTP check -> signed session cookie
  GET  /api/me       {user, is_leadership, models}  [auth]
  GET  /api/logout   clears the cookie
  GET  /jerry        Jerry chat UI                  [auth]
  POST /api/chat     SSE stream from Claude / DeepSeek [auth]

Why the streamlit stub: `login.py` and `jerry_gpt.py` still import streamlit at
module scope, but everything we reuse from them (credential verification, the
knowledge-base loader, the model catalog, clearance rules) is pure Python. The
stub lets us keep ONE source of truth instead of forking that logic. When the
Streamlit app is finally retired, the stub and its imports can go.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import types
from pathlib import Path

# --- streamlit stub (must run before importing login / jerry_gpt) -----------
if "streamlit" not in sys.modules:
    _st = types.ModuleType("streamlit")

    class _SessionState(dict):
        def get(self, k, d=None):
            return super().get(k, d)

    _st.session_state = _SessionState()

    class _Secrets:
        def get(self, k, d=None):
            return None

    _st.secrets = _Secrets()

    def _passthrough(*a, **k):
        def wrap(fn):
            return fn
        return wrap

    _st.cache_resource = _passthrough
    _st.cache_data = _passthrough
    for _n in ("markdown", "write", "error", "warning", "info", "stop", "rerun",
               "button", "columns", "expander", "chat_message", "empty",
               "set_page_config", "spinner", "selectbox", "radio", "text_input",
               "toggle", "caption", "download_button", "chat_input", "container"):
        setattr(_st, _n, lambda *a, **k: None)
    sys.modules["streamlit"] = _st
    _c = types.ModuleType("streamlit.components")
    _v = types.ModuleType("streamlit.components.v1")
    _v.html = lambda *a, **k: None
    _c.v1 = _v
    sys.modules["streamlit.components"] = _c
    sys.modules["streamlit.components.v1"] = _v

from fastapi import FastAPI, Request, Response, HTTPException           # noqa: E402
from fastapi.responses import (                                          # noqa: E402
    HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse,
)
from fastapi.staticfiles import StaticFiles                              # noqa: E402

import login as _login                                                   # noqa: E402
import jerry_gpt as _jerry                                               # noqa: E402

ROOT = Path(__file__).parent
SITE = ROOT / "site"
TEMPLATES = ROOT / "templates"

COOKIE_NAME = "stmx_session"
SESSION_DAYS = 7

app = FastAPI(title="Streamax Sales Toolkit", docs_url=None, redoc_url=None)

if (ROOT / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(ROOT / "assets")), name="assets")


# ---------------------------------------------------------------------------
# Session cookie — HMAC-signed "user|expiry", same trust model as the old
# auth.py but signed server-side with a real HMAC (not a truncated hash).
# ---------------------------------------------------------------------------

def _secret() -> str:
    s = os.environ.get("AUTH_SECRET", "")
    if not s:
        print("[WARN] AUTH_SECRET is not set — sessions are forgeable. Set it.",
              file=sys.stderr, flush=True)
        s = "insecure-development-fallback"
    return s


def _sign(payload: str) -> str:
    return hmac.new(_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]


def make_token(user: str) -> str:
    payload = f"{user}|{int(time.time()) + SESSION_DAYS * 86400}"
    raw = f"{payload}|{_sign(payload)}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def read_token(token: str | None) -> str | None:
    if not token:
        return None
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        user, expiry, sig = raw.rsplit("|", 2)
    except Exception:
        return None
    if not hmac.compare_digest(_sign(f"{user}|{expiry}"), sig):
        return None
    if time.time() > float(expiry):
        return None
    return user


def current_user(request: Request) -> str | None:
    return read_token(request.cookies.get(COOKIE_NAME))


def require_user(request: Request) -> str:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="not authenticated")
    return user


def _page(name: str) -> str:
    path = TEMPLATES / name
    if not path.is_file():
        raise HTTPException(500, f"missing template: {name}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def toolkit(request: Request):
    if not current_user(request):
        return RedirectResponse("/login", status_code=302)
    index = SITE / "index.html"
    if not index.is_file():
        raise HTTPException(500, "site/index.html not built — run: python3 build_static.py")
    return HTMLResponse(index.read_text(encoding="utf-8"))


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if current_user(request):
        return RedirectResponse("/", status_code=302)
    return HTMLResponse(_page("login.html"))


@app.get("/jerry", response_class=HTMLResponse)
def jerry_page(request: Request):
    if not current_user(request):
        return RedirectResponse("/login", status_code=302)
    return HTMLResponse(_page("jerry.html"))


# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------

@app.post("/api/login")
async def api_login(request: Request):
    body = await request.json()
    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    if not email or not password:
        return JSONResponse({"ok": False, "error": "Email and password are required."}, 400)

    ok, message = _login.verify_streamax_credentials(email, password)
    if not ok:
        return JSONResponse({"ok": False, "error": message}, 401)

    # `message` is the display name for easter-egg accounts, else "Success".
    user = email.strip().lower() if message == "Success" else message
    resp = JSONResponse({"ok": True, "user": user})
    resp.set_cookie(
        COOKIE_NAME, make_token(user),
        max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax",
        secure=request.url.scheme == "https",
    )
    return resp


@app.get("/api/logout")
def api_logout(next: str = "/login"):
    resp = RedirectResponse(next if next.startswith("/") else "/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp


@app.get("/api/me")
def api_me(request: Request):
    user = require_user(request)
    is_leadership = bool(_login.resolve_leadership(user))
    models = _jerry._allowed_models(is_leadership)
    return {
        "user": user,
        "is_leadership": is_leadership,
        "models": models,
        "default_model": (_jerry.DEFAULT_MODEL if is_leadership
                          else _jerry.NON_LEADERSHIP_DEFAULT),
    }


# ---------------------------------------------------------------------------
# Jerry chat — keys stay server-side; response streams back as SSE
# ---------------------------------------------------------------------------

MAX_TOKENS = {"Short": 1024, "Medium": 4096, "Long": 8192}


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


@app.post("/api/chat")
async def api_chat(request: Request):
    user = require_user(request)
    body = await request.json()
    messages = body.get("messages") or []
    if not messages:
        raise HTTPException(400, "no messages")

    is_leadership = bool(_login.resolve_leadership(user))
    allowed = set(_jerry._allowed_models(is_leadership).values())

    model = body.get("model") or (_jerry.DEFAULT_MODEL if is_leadership
                                  else _jerry.NON_LEADERSHIP_DEFAULT)
    # Server-side enforcement: never trust the client's model choice.
    if model not in allowed:
        model = _jerry.NON_LEADERSHIP_DEFAULT

    provider = _jerry._provider_for(model)
    key, _src = _jerry._resolve_provider_key(provider, is_leadership)
    if not key:
        raise HTTPException(503, f"no API key configured for provider '{provider}'")

    max_tokens = MAX_TOKENS.get(body.get("length") or "Medium", 4096)

    system_blocks = list(_jerry._load_system_blocks())
    try:
        system_blocks.append(_jerry._build_clearance_block(
            user if "@" in user else "", user, is_leadership,
            is_first_turn=(len(messages) <= 1), special_relationship=None,
        ))
    except Exception as exc:  # clearance is best-effort, never fatal
        print(f"[chat] clearance block failed: {exc}", file=sys.stderr, flush=True)

    def stream():
        try:
            if provider == "deepseek":
                from openai import OpenAI
                client = OpenAI(api_key=key, base_url=_jerry.DEEPSEEK_BASE_URL, max_retries=0)
                sys_text = "\n\n".join(
                    b.get("text", "") for b in system_blocks if isinstance(b, dict)
                )
                msgs = [{"role": "system", "content": sys_text}] + [
                    {"role": m["role"], "content": m["content"]} for m in messages
                ]
                resp = client.chat.completions.create(
                    model=model, messages=msgs, max_tokens=max_tokens, stream=True,
                )
                for chunk in resp:
                    choices = getattr(chunk, "choices", None) or []
                    if not choices:
                        continue
                    piece = getattr(choices[0].delta, "content", None)
                    if piece:
                        yield _sse({"delta": piece})
            else:
                import httpx
                from anthropic import Anthropic
                client = Anthropic(
                    api_key=key, max_retries=0,
                    timeout=httpx.Timeout(600.0, connect=15.0, read=90.0),
                )
                with client.messages.stream(
                    model=model, max_tokens=max_tokens,
                    system=system_blocks, messages=messages,
                ) as s:
                    for piece in s.text_stream:
                        yield _sse({"delta": piece})
            yield _sse({"done": True, "model": model})
        except Exception as exc:
            print(f"[chat] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
            yield _sse({"error": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })
