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

# Optional side-cars — same graceful-degradation contract as the Streamlit app:
# if a dependency or secret is missing, Jerry still works, just without that
# feature. Never let an import here take the server down.
try:
    import chat_history as _history
except Exception:                                                        # noqa: BLE001
    _history = None
try:
    import file_io as _file_io
except Exception:                                                        # noqa: BLE001
    _file_io = None
try:
    import usage_logger as _usage
except Exception:                                                        # noqa: BLE001
    _usage = None
try:
    import product_images as _pimg
except Exception:                                                        # noqa: BLE001
    _pimg = None
try:
    import downloads as _downloads
except Exception:                                                        # noqa: BLE001
    _downloads = None
try:
    import topology as _topology
except Exception:                                                        # noqa: BLE001
    _topology = None

ROOT = Path(__file__).parent
SITE = ROOT / "site"
TEMPLATES = ROOT / "templates"

COOKIE_NAME = "stmx_session"
SESSION_DAYS = 7

app = FastAPI(title="Streamax Sales Toolkit", docs_url=None, redoc_url=None)

if (ROOT / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(ROOT / "assets")), name="assets")

# Streamax Sales Configurator — a separate project by Kevin Wang, vendored into
# ./configurator by sync_configurator.sh so it deploys alongside the toolkit.
# Served as-is (html=True makes /configurator/ resolve to its index.html).
if (ROOT / "configurator").is_dir():
    app.mount("/configurator",
              StaticFiles(directory=str(ROOT / "configurator"), html=True),
              name="configurator")


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
# Chat history (Postgres via chat_history.py — optional)
# ---------------------------------------------------------------------------

def _history_on() -> bool:
    try:
        return _history is not None and _history.is_configured()
    except Exception:
        return False


@app.get("/api/history")
def api_history(request: Request):
    """Most recent conversation for this user, so a reload resumes it."""
    user = require_user(request)
    if not _history_on():
        return {"enabled": False, "messages": [], "session_id": None}
    try:
        messages, session_id = _history.load_recent_session(user)
    except Exception as exc:
        print(f"[history] load failed: {exc}", file=sys.stderr, flush=True)
        messages, session_id = [], None
    return {
        "enabled": True,
        "messages": messages or [],
        "session_id": session_id or _history.new_session_id(),
    }


@app.get("/api/sessions")
def api_sessions(request: Request):
    user = require_user(request)
    if not _history_on():
        return {"enabled": False, "sessions": []}
    try:
        return {"enabled": True, "sessions": _history.list_past_sessions(user, limit=20)}
    except Exception as exc:
        print(f"[history] list failed: {exc}", file=sys.stderr, flush=True)
        return {"enabled": True, "sessions": []}


@app.get("/api/session/{session_id}")
def api_session(session_id: str, request: Request):
    user = require_user(request)
    if not _history_on():
        return {"messages": []}
    try:
        return {"messages": _history.load_session_by_id(user, session_id) or []}
    except Exception as exc:
        print(f"[history] load_by_id failed: {exc}", file=sys.stderr, flush=True)
        return {"messages": []}


@app.post("/api/session/new")
def api_session_new(request: Request):
    require_user(request)
    sid = _history.new_session_id() if _history is not None else str(int(time.time()))
    return {"session_id": sid}


@app.delete("/api/session/{session_id}")
def api_session_delete(session_id: str, request: Request):
    user = require_user(request)
    if not _history_on():
        return {"ok": False}
    try:
        return {"ok": bool(_history.delete_session(user, session_id))}
    except Exception as exc:
        print(f"[history] delete failed: {exc}", file=sys.stderr, flush=True)
        return {"ok": False}


# ---------------------------------------------------------------------------
# Rich response extras: product photos, deck downloads, generated documents,
# the ecosystem map. In Streamlit these were widgets rendered after the reply;
# here the server computes them once the answer is complete and pushes them to
# the browser on the same SSE stream.
# ---------------------------------------------------------------------------

def _asset_url(path: str) -> str:
    """Map an absolute assets/ path to the URL the /assets mount serves."""
    p = Path(path)
    return f"/assets/{p.parent.name}/{p.name}"


def _response_extras(answer: str, question: str) -> dict:
    """Everything that hangs off a finished answer."""
    out: dict = {"images": [], "downloads": [], "artifacts": [],
                 "ecosystem": None, "clean": answer}

    if _pimg is not None:
        try:
            out["images"] = [
                {"url": _asset_url(path), "caption": caption}
                for path, caption in _pimg.find_product_images(answer)
            ]
        except Exception as exc:
            print(f"[extras] images: {exc}", file=sys.stderr, flush=True)

    if _downloads is not None:
        try:
            # Scan the question too: an eSIM ask should surface the deck even if
            # Jerry's wording omits the keyword.
            out["downloads"] = [
                {"label": d["label"], "blurb": d.get("blurb", ""),
                 "url": _asset_url(d["path"])}
                for d in _downloads.find_downloads(f"{question}\n{answer}")
            ]
        except Exception as exc:
            print(f"[extras] downloads: {exc}", file=sys.stderr, flush=True)

    if _file_io is not None:
        try:
            specs = _file_io.extract_artifacts(answer)
            out["artifacts"] = [
                {"format": s.get("format", ""),
                 "filename": _file_io._safe_filename(s), "spec": s}
                for s in specs
            ]
            if specs:
                out["clean"] = _file_io.strip_artifacts(answer)
        except Exception as exc:
            print(f"[extras] artifacts: {exc}", file=sys.stderr, flush=True)

    if _topology is not None:
        m = _jerry._ECO_RE.search(answer or "") if hasattr(_jerry, "_ECO_RE") else None
        if m:
            out["ecosystem"] = (m.group(1) or "").strip()
            out["clean"] = _jerry._ECO_RE.sub("", out["clean"]).strip()

    return out


@app.post("/api/artifact")
async def api_artifact(request: Request):
    """Render a ```artifact``` spec into a real .docx/.pptx/.xlsx/.pdf."""
    require_user(request)
    if _file_io is None:
        raise HTTPException(503, "document generation unavailable")
    spec = (await request.json()).get("spec") or {}
    try:
        data, filename, mime = _file_io.render_artifact(spec)
    except Exception as exc:
        raise HTTPException(400, f"could not build the document: {exc}")
    return Response(content=data, media_type=mime, headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })


@app.get("/api/ecosystem", response_class=HTMLResponse)
def api_ecosystem(request: Request, focus: str = ""):
    """Interactive D3 ecosystem map, shown in a modal iframe."""
    require_user(request)
    if _topology is None:
        raise HTTPException(503, "ecosystem map unavailable")
    return HTMLResponse(_topology.ecosystem_map_html(focus))


# ---------------------------------------------------------------------------
# Jerry chat — keys stay server-side; response streams back as SSE
# ---------------------------------------------------------------------------

MAX_TOKENS = {"Short": 1024, "Medium": 4096, "Long": 8192}


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


def _attach_files(text: str, files: list) -> tuple:
    """Turn browser-uploaded files into Anthropic content blocks.

    `files` is [{name, mime, data}] where data is base64 (from FileReader).
    Reuses file_io.file_to_block so images/PDFs go native and Office files are
    text-extracted — exactly as the Streamlit uploader did. Returns
    (api_content, note) where note summarises attachments for the transcript.
    """
    if not files or _file_io is None:
        return (text or ""), ""
    blocks, names = [], []
    if text:
        blocks.append({"type": "text", "text": text})
    for f in files:
        name = (f.get("name") or "file").strip()
        try:
            raw = base64.b64decode((f.get("data") or "").split(",")[-1])
        except Exception:
            continue
        try:
            blocks.append(_file_io.file_to_block(name, f.get("mime") or "", raw))
            names.append(name)
        except Exception as exc:
            print(f"[upload] {name}: {exc}", file=sys.stderr, flush=True)
    if not blocks:
        return (text or ""), ""
    note = ("\n\n*attached: " + ", ".join(names) + "*") if names else ""
    return blocks, note


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

    # Bring-your-own-key: sent per request over HTTPS and used for this call
    # only. Never written to disk, the session cookie, or any log — same
    # session-only contract as the Streamlit settings panel.
    byo = (body.get("byo_key") or "").strip()
    if byo:
        key = byo
    else:
        key, _src = _jerry._resolve_provider_key(provider, is_leadership)
    if not key:
        raise HTTPException(503, f"no API key configured for provider '{provider}'")

    # Web browsing is opt-in per turn and Anthropic-only (they're server-side
    # tools); DeepSeek has no equivalent.
    web_enabled = bool(body.get("web")) and provider == "anthropic"
    request_tools = _jerry.WEB_TOOLS if web_enabled else []

    length = body.get("length") or "Medium"
    max_tokens = MAX_TOKENS.get(length, 4096)
    session_id = body.get("session_id") or ""

    # Attachments ride on the CURRENT turn only — stored history keeps a
    # text-only note, so binaries aren't re-sent on every later turn.
    files = body.get("files") or []
    question_text = ""
    if messages and messages[-1].get("role") == "user":
        question_text = messages[-1].get("content") or ""
        if files:
            content, note = _attach_files(question_text, files)
            messages = messages[:-1] + [{"role": "user", "content": content}]
            question_text = question_text + note

    system_blocks = list(_jerry._load_system_blocks())
    try:
        system_blocks.append(_jerry._build_clearance_block(
            user if "@" in user else "", user, is_leadership,
            is_first_turn=(len(messages) <= 1), special_relationship=None,
        ))
    except Exception as exc:  # clearance is best-effort, never fatal
        print(f"[chat] clearance block failed: {exc}", file=sys.stderr, flush=True)

    def stream():
        answer = ""
        usage = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
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
                    stream_options={"include_usage": True},
                )
                for chunk in resp:
                    u = getattr(chunk, "usage", None)
                    if u:
                        hit = getattr(u, "prompt_cache_hit_tokens", 0) or 0
                        usage["cache_read"] = hit
                        usage["input"] = max((getattr(u, "prompt_tokens", 0) or 0) - hit, 0)
                        usage["output"] = getattr(u, "completion_tokens", 0) or 0
                    choices = getattr(chunk, "choices", None) or []
                    if not choices:
                        continue
                    piece = getattr(choices[0].delta, "content", None)
                    if piece:
                        answer += piece
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
                    tools=request_tools,
                ) as s:
                    for piece in s.text_stream:
                        answer += piece
                        yield _sse({"delta": piece})
                    try:
                        u = s.get_final_message().usage
                        usage = {
                            "input": getattr(u, "input_tokens", 0) or 0,
                            "output": getattr(u, "output_tokens", 0) or 0,
                            "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                            "cache_creation": getattr(u, "cache_creation_input_tokens", 0) or 0,
                        }
                    except Exception:
                        pass
            extras = {}
            try:
                extras = _response_extras(answer, question_text)
            except Exception as exc:
                print(f"[extras] {exc}", file=sys.stderr, flush=True)
            yield _sse({"done": True, "model": model, "session_id": session_id,
                        "usage": usage, "extras": extras})
        except Exception as exc:
            print(f"[chat] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
            yield _sse({"error": f"{type(exc).__name__}: {exc}"})
        finally:
            # Post-work is best-effort and must never break the response the
            # user already received — each sink is isolated.
            if answer:
                cost = 0.0
                if _usage is not None:
                    try:
                        cost = _usage._estimate_cost_usd(
                            model, usage["input"], usage["output"],
                            usage["cache_read"], usage["cache_creation"])
                    except Exception:
                        pass
                if _history_on() and session_id:
                    try:
                        _history.save_turn(
                            user_email=user, user_name=user, session_id=session_id,
                            user_message=question_text, assistant_message=answer,
                            model=model, length=length,
                            input_tokens=usage["input"], output_tokens=usage["output"],
                            cache_read_tokens=usage["cache_read"],
                            cache_creation_tokens=usage["cache_creation"],
                            cost_usd=cost,
                        )
                    except Exception as exc:
                        print(f"[history] save failed: {exc}", file=sys.stderr, flush=True)
                if _usage is not None:
                    try:
                        _usage.log_query(
                            question=question_text, model=model, length=length,
                            answer=answer, is_leadership=is_leadership,
                            input_tokens=usage["input"], output_tokens=usage["output"],
                            cache_read_tokens=usage["cache_read"],
                            cache_creation_tokens=usage["cache_creation"],
                        )
                    except Exception as exc:
                        print(f"[usage] log failed: {exc}", file=sys.stderr, flush=True)

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })
