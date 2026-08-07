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
try:
    import ms_auth as _ms
except Exception:                                                        # noqa: BLE001
    _ms = None
try:
    import mailer as _mailer
except Exception:                                                        # noqa: BLE001
    _mailer = None

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
# Drip Mailer
#
# The mailer needs the user's MAIL password to send as them. The session cookie
# deliberately does not carry it (the login page promises credentials are never
# stored), so it is asked for in the mailer UI and travels on the request that
# uses it — held in a local variable for the length of the send and never
# written to disk, a database, the cookie, or a log line.
# ---------------------------------------------------------------------------

def _require_mailer():
    if _mailer is None:
        raise HTTPException(503, "mailer unavailable")
    return _mailer


@app.get("/api/mailer/template.csv")
def api_mailer_template(request: Request):
    require_user(request)
    return Response(
        _require_mailer().CSV_TEMPLATE, media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leadList.csv"'},
    )


@app.get("/api/mailer/defaults")
def api_mailer_defaults(request: Request):
    user = require_user(request)
    m = _require_mailer()
    return {
        "email": user if "@" in user else "",
        "layouts": list(m.SIGNATURE_LAYOUTS),
        "default_body": m.DEFAULT_BODY,
        "max_recipients": m.MAX_RECIPIENTS,
        "min_delay": m.MIN_DELAY_S,
        "default_delay": m.DEFAULT_DELAY_S,
        "required_columns": list(m.REQUIRED_COLUMNS),
    }


@app.post("/api/mailer/preview")
async def api_mailer_preview(request: Request):
    """Render exactly what would be sent, for the first recipient (or a sample).

    Rendered server-side by the same functions `send_batch` uses, so the
    preview cannot drift from the mail.
    """
    require_user(request)
    m = _require_mailer()
    body = await request.json()
    row = body.get("row") or {"first_name": "John", "last_name": "Doe",
                              "company": "Acme Logistics", "role": "Fleet Manager",
                              "email": "john.doe@acme.com"}
    sig = m.signature_html(body.get("layout") or "", body.get("signature") or {})
    return {
        "subject": m.render_template(body.get("subject") or "", row),
        "html": m.build_html_body(body.get("body") or "", row, sig),
    }


@app.post("/api/mailer/recipients")
async def api_mailer_recipients(request: Request):
    """Validate an uploaded CSV before anything is sent."""
    require_user(request)
    m = _require_mailer()
    body = await request.json()
    rows, problems = m.parse_recipients(body.get("csv") or "")
    return {"rows": rows[:50], "count": len(rows), "problems": problems[:40]}


@app.post("/api/mailer/test")
async def api_mailer_test(request: Request):
    """Send a single test to the signed-in user. The original tool had no dry
    run — the first thing anyone saw of a broken signature was the customer."""
    user = require_user(request)
    m = _require_mailer()
    body = await request.json()
    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    if not email or not password:
        return JSONResponse({"ok": False, "error": "Mail address and password are required."}, 400)

    row = body.get("row") or {"first_name": "John", "last_name": "Doe",
                              "company": "Acme Logistics", "role": "Fleet Manager"}
    sig = m.signature_html(body.get("layout") or "", body.get("signature") or {})
    to_addr = user if "@" in user else email
    try:
        server, backend = m.connect(email, password)
    except Exception as exc:                                         # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(exc)[:400]}, 400)
    try:
        msg = m.build_message(
            "[TEST] " + m.render_template(body.get("subject") or "", row),
            m.build_html_body(body.get("body") or "", row, sig),
            to_addr, body.get("from_name") or "", email,
        )
        server.send_message(msg)
    except Exception as exc:                                         # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(exc)[:400]}, 400)
    finally:
        try:
            server.quit()
        except Exception:
            pass
    return {"ok": True, "to": to_addr, "backend": backend}


@app.post("/api/mailer/send")
async def api_mailer_send(request: Request):
    """Run the batch, streaming one SSE event per recipient."""
    require_user(request)
    m = _require_mailer()
    body = await request.json()

    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    if not email or not password:
        raise HTTPException(400, "Mail address and password are required.")

    rows, problems = m.parse_recipients(body.get("csv") or "")
    if not rows:
        raise HTTPException(400, "; ".join(problems) or "No valid recipients.")

    sig = m.signature_html(body.get("layout") or "", body.get("signature") or {})
    params = dict(
        email=email, password=password, from_name=body.get("from_name") or "",
        subject_template=body.get("subject") or "", body_template=body.get("body") or "",
        sig_html=sig, rows=rows, delay_s=body.get("delay") or m.DEFAULT_DELAY_S,
    )

    def stream():
        yield f"data: {json.dumps({'type': 'start', 'total': len(rows), 'problems': problems})}\n\n"
        try:
            for event in m.send_batch(**params):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as exc:                                     # noqa: BLE001
            yield f"data: {json.dumps({'type': 'fatal', 'message': str(exc)[:300]})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


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
def login_page(request: Request, next: str = "/"):
    if current_user(request):
        return RedirectResponse("/", status_code=302)
    page = _page("login.html").replace("<!--MS_SIGNIN-->", _ms_signin_block(next))
    return HTMLResponse(page)


@app.get("/mailer", response_class=HTMLResponse)
def mailer_page(request: Request):
    if not current_user(request):
        return RedirectResponse("/login?next=/mailer", status_code=302)
    if _mailer is None:
        raise HTTPException(503, "mailer unavailable")
    return HTMLResponse(_page("mailer.html"))


@app.get("/jerry", response_class=HTMLResponse)
def jerry_page(request: Request):
    if not current_user(request):
        # Carry the destination so a cold /jerry link lands back on Jerry, not
        # on the toolkit, once the user has signed in.
        return RedirectResponse("/login?next=/jerry", status_code=302)
    return HTMLResponse(_page("jerry.html"))


# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------

def _is_https(request: Request) -> bool:
    """True when the *browser* is on https. Behind Cloudflare→Render the inbound
    hop to uvicorn is plain http, so trust X-Forwarded-Proto."""
    fwd = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip().lower()
    return (fwd or request.url.scheme) == "https"


def _set_session(resp, user: str, request: Request):
    resp.set_cookie(
        COOKIE_NAME, make_token(user),
        max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax",
        secure=_is_https(request),
    )
    return resp


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
    payload = {"ok": True, "user": user}
    # Some accounts get a full-screen transition before landing in the app —
    # the HTML port of what the Streamlit login played. Spec comes from
    # login.LOGIN_EASTER_EGGS so both front-ends stay identical.
    egg = _login.resolve_easter_egg(user)
    if egg:
        payload["easter_egg"] = dict(egg, ms=_login.EASTER_EGG_MS)
    return _set_session(JSONResponse(payload), user, request)


@app.get("/api/logout")
def api_logout(next: str = "/login"):
    resp = RedirectResponse(next if next.startswith("/") else "/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp


# ── Sign in with Microsoft (Entra ID / OIDC) ────────────────────────────────
# Only wired up when MS_TENANT_ID / MS_CLIENT_ID / MS_CLIENT_SECRET are set;
# until then the button is not rendered and /auth/microsoft/start bounces back.

_MS_BUTTON = """
    <div class="or"><span>or</span></div>
    <a class="msbtn" href="/auth/microsoft/start?next=__NEXT__">
      <svg viewBox="0 0 23 23" width="18" height="18" aria-hidden="true">
        <rect x="1"  y="1"  width="10" height="10" fill="#F25022"/>
        <rect x="12" y="1"  width="10" height="10" fill="#7FBA00"/>
        <rect x="1"  y="12" width="10" height="10" fill="#00A4EF"/>
        <rect x="12" y="12" width="10" height="10" fill="#FFB900"/>
      </svg>
      <span>Sign in with Microsoft</span>
    </a>
    <p class="hint">Use this if your Streamax mailbox is on Outlook / Microsoft 365.</p>
"""


def _ms_signin_block(next_path: str = "/") -> str:
    if not (_ms and _ms.is_configured()):
        return ""
    from urllib.parse import quote
    return _MS_BUTTON.replace("__NEXT__", quote(_ms.safe_next(next_path), safe="/"))


def _ms_redirect_uri(request: Request) -> str:
    """The redirect URI registered in Entra. Must match byte-for-byte on both
    the authorize and token calls, so it is derived once, here."""
    explicit = os.environ.get("MS_REDIRECT_URI", "").strip()
    if explicit:
        return explicit
    proto = "https" if _is_https(request) else "http"
    host = (request.headers.get("x-forwarded-host")
            or request.headers.get("host")
            or request.url.netloc)
    return f"{proto}://{host}{_ms.CALLBACK_PATH}"


def _login_error(message: str, next_path: str = "/"):
    """Bounce back to the login page with a readable reason, keeping the
    original destination so a password retry still lands where they meant."""
    from urllib.parse import quote
    url = f"/login?err={quote(message)}"
    safe = _ms.safe_next(next_path) if _ms else "/"
    if safe != "/":
        url += f"&next={quote(safe, safe='/')}"
    return RedirectResponse(url, status_code=302)


@app.get("/auth/microsoft/start")
def ms_start(request: Request, next: str = "/"):
    if not (_ms and _ms.is_configured()):
        return _login_error("Microsoft sign-in is not configured yet.")
    url, state = _ms.begin(_ms_redirect_uri(request), _ms.safe_next(next))
    resp = RedirectResponse(url, status_code=302)
    resp.set_cookie(_ms.STATE_COOKIE, state, max_age=_ms.STATE_TTL, httponly=True,
                    samesite="lax", secure=_is_https(request), path="/")
    return resp


@app.get("/auth/microsoft/callback")
def ms_callback(request: Request, code: str = "", state: str = "",
                error: str = "", error_description: str = ""):
    if not (_ms and _ms.is_configured()):
        return _login_error("Microsoft sign-in is not configured yet.")
    if error:
        return _login_error(error_description or error)

    email, next_path, err = _ms.complete(
        code, state, request.cookies.get(_ms.STATE_COOKIE) or "",
        _ms_redirect_uri(request),
    )
    if err:
        return _login_error(err, next_path)

    resp = RedirectResponse(next_path, status_code=302)
    _set_session(resp, email, request)
    resp.delete_cookie(_ms.STATE_COOKIE, path="/")
    return resp


@app.get("/api/me")
def api_me(request: Request):
    user = require_user(request)
    is_leadership = bool(_login.resolve_leadership(user))
    # VIP = LEADERSHIP ∪ EXTRA_VIP_EMAILS. Grants Claude models but NOT the
    # pricing clearance leadership gets.
    is_vip = bool(_login.resolve_vip(user))
    models = _jerry._allowed_models(is_leadership, is_vip)
    return {
        "user": user,
        "is_leadership": is_leadership,
        "is_vip": is_vip,
        "models": models,
        # VIP (⊇ LEADERSHIP) defaults to Opus 5; everyone else to DeepSeek.
        "default_model": (_jerry.DEFAULT_MODEL if is_vip
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
    is_vip = bool(_login.resolve_vip(user))
    allowed = set(_jerry._allowed_models(is_leadership, is_vip).values())

    model = body.get("model") or (_jerry.DEFAULT_MODEL if is_vip
                                  else _jerry.NON_LEADERSHIP_DEFAULT)
    # Server-side enforcement: never trust the client's model choice. The
    # fallback must itself be in `allowed`, or a VIP whose request we rejected
    # would land on a model they are not cleared for.
    if model not in allowed:
        model = (_jerry.DEFAULT_MODEL if _jerry.DEFAULT_MODEL in allowed
                 else _jerry.NON_LEADERSHIP_DEFAULT)

    provider = _jerry._provider_for(model)

    # Bring-your-own-key: sent per request over HTTPS and used for this call
    # only. Never written to disk, the session cookie, or any log — same
    # session-only contract as the Streamlit settings panel.
    byo = (body.get("byo_key") or "").strip()
    if byo:
        key = byo
    else:
        key, _src = _jerry._resolve_provider_key(provider, is_leadership, is_vip)
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
        # `user` is a streamax.com email for real logins, or an easter-egg
        # display name ("Jerry", "Hekun", "ZNTang"). resolve_* handle both —
        # they map the display names back to canonical emails first.
        #
        # This was previously pinned to None, which silently dropped Jerry's
        # inner-circle behaviour on the HTML site: no one-time greeting for
        # himself / Kun He / Rui Wang, and no 你 (informal) address-form
        # override — they got the default professional 您 register instead.
        system_blocks.append(_jerry._build_clearance_block(
            user if "@" in user else "", user, is_leadership,
            is_first_turn=(len(messages) <= 1),
            special_relationship=_login.resolve_special_relationship(user),
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
