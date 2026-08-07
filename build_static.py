"""Build the Sales Toolkit as a standalone static HTML site (no Streamlit).

Phase 1 of the Streamlit -> plain-HTML rebuild. The toolkit was always just an
HTML string that `app.py` concatenated and handed to `components.html()`, so
this emits exactly the same markup as a real page instead of an iframe.

  python3 build_static.py          ->  site/index.html

How it stays in sync with app.py: the page shell (`html_head`, `html_tail`) and
`email_tool_content` are literal string assignments inside app.py, so we pull
them out with `ast` at build time rather than duplicating them here. Every other
section is imported from its own module, exactly as app.py does it.

Streamlit-specific bits are rewired for a normal web server:
  ?view=jerry_gpt -> /jerry          (Jerry becomes its own page)
  ?logout=1       -> /api/logout     (server clears the session cookie)
  __USER_IDENTITY__ -> a span that /api/me fills in client-side
"""
from __future__ import annotations

import ast
import re
import sys
import types
from pathlib import Path

# Optional so a missing/broken i18n.py costs the language switcher, not the
# whole boot — build_static.py runs at container start in APP_MODE=html.
try:
    import i18n as _i18n
except Exception as _exc:                                            # noqa: BLE001
    print(f"[BUILD] WARNING: i18n unavailable ({_exc}) — no language switcher.",
          file=sys.stderr, flush=True)
    _i18n = None

ROOT = Path(__file__).parent
OUT_DIR = ROOT / "site"
OUT_FILE = OUT_DIR / "index.html"

# Sections in the same order app.py concatenates them.
SECTION_MODULES = [
    ("marketing_resources", "content"),
    ("streamaxpedia_app", "build_content"),   # callable: build_content(user_email)
    ("prospecting_flow", "content"),
    ("discovery_meeting", "content"),
    ("presentation", "content"),
    ("value_calculator", "content"),
    ("configurator_tab", "content"),
]


def _stub_streamlit() -> None:
    """Some section modules import streamlit at module scope. They only use it
    for secrets/caching, never to render the HTML we want, so a stub is enough
    to import them outside a Streamlit runtime."""
    if "streamlit" in sys.modules:
        return
    st = types.ModuleType("streamlit")

    class _SS(dict):
        def get(self, k, d=None):
            return super().get(k, d)

    st.session_state = _SS()

    class _Secrets:
        def get(self, k, d=None):
            return None

    st.secrets = _Secrets()

    def _passthrough_decorator(*a, **k):
        def wrap(fn):
            return fn
        return wrap

    st.cache_resource = _passthrough_decorator
    st.cache_data = _passthrough_decorator
    for name in ("markdown", "write", "error", "warning", "info", "stop", "rerun"):
        setattr(st, name, lambda *a, **k: None)
    sys.modules["streamlit"] = st

    comp = types.ModuleType("streamlit.components")
    v1 = types.ModuleType("streamlit.components.v1")
    v1.html = lambda *a, **k: None
    comp.v1 = v1
    sys.modules["streamlit.components"] = comp
    sys.modules["streamlit.components.v1"] = v1


def extract_literals(py_file: Path, names: set[str]) -> dict[str, str]:
    """Pull top-level string-literal assignments out of a module without
    executing it (app.py can't be imported — it *is* the Streamlit app)."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id in names
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                out[target.id] = node.value.value
    missing = names - set(out)
    if missing:
        raise SystemExit(f"ERROR: could not extract {sorted(missing)} from {py_file.name}")
    return out


def collect_sections() -> list[str]:
    """Import each tab module and collect its HTML.

    A missing or broken module degrades to a visible placeholder rather than
    killing the build — same contract `app.py` already applies to its own
    imports. This matters because in `APP_MODE=html` the Dockerfile runs this
    script at *container start*: an unhandled ImportError here means the service
    never boots at all, so one stale entry in SECTION_MODULES takes the whole
    site down instead of one tab. (That is exactly what a half-landed commit
    did: `sales_onboarding.py` deleted, this list not updated.)
    """
    _stub_streamlit()
    sections: list[str] = []
    for mod_name, attr in SECTION_MODULES:
        try:
            mod = __import__(mod_name)
            value = getattr(mod, attr)
            # streamaxpedia exposes build_content(user_email); "" = no user-gated rows
            sections.append(value("") if callable(value) else value)
        except Exception as exc:                                     # noqa: BLE001
            print(f"[BUILD] WARNING: section '{mod_name}.{attr}' unavailable "
                  f"({type(exc).__name__}: {exc}) — emitting a placeholder and "
                  f"continuing. Fix SECTION_MODULES or restore the module.",
                  file=sys.stderr, flush=True)
            sections.append(
                f"<div id='{mod_name}' class='content-section hidden'>"
                f"<h2 style='color:#ff4757; text-align:center; padding:40px;'>"
                f"⚠️ {mod_name}.py not available in this build</h2></div>"
            )
    return sections


def rewire_for_static(html: str) -> str:
    """Replace Streamlit-only navigation/identity with plain web equivalents."""
    # Jerry GPT: a query-param view inside one Streamlit app -> its own page.
    html = html.replace('?view=jerry_gpt', '/jerry')
    html = html.replace('"/jerry&logout=1"', '"/api/logout?next=/jerry"')
    html = html.replace('?logout=1', '/api/logout')
    # Dead code path (the old special-feature CTA) — keep it from emitting a
    # Streamlit-style ?view= URL if it is ever re-enabled.
    html = html.replace('?view=${encodeURIComponent(sp.view)}',
                        '/${encodeURIComponent(sp.view)}')

    # Strip the iframe-escape onclick handlers.
    #
    # In Streamlit the toolkit ran inside components.html, so links needed JS to
    # break out to the parent frame: read document.referrer / window.parent, then
    # rebuild the URL. There is no iframe here, and that JS actively breaks
    # navigation — it does `base + '/jerry'` where base already ends in '/',
    # yielding '//jerry', which FastAPI 404s. Removing the handler lets the
    # plain href do the right thing. Fixes the Jerry launch AND Sign out.
    def _drop_iframe_escape(m: re.Match) -> str:
        body = m.group(0)
        if "document.referrer" in body or "window.parent" in body or "window.top" in body:
            return ""
        return body

    html = re.sub(r'onclick="[^"]*"', _drop_iframe_escape, html)

    # The same iframe-escape logic also lives in named <script> functions (e.g.
    # window.obOpenJerry in the old Sales Onboarding tab), which the attribute pass
    # above cannot reach. Those build `base.split('?')[0].split('#')[0] + '/x'`
    # — and because base ends in '/', the result is '//x' -> 404. Normalise the
    # concatenation by stripping trailing slashes first. Generic, so it fixes
    # every current and future occurrence of the pattern.
    html = html.replace(
        ".split('#')[0] + '/",
        ".split('#')[0].replace(/\\/+$/, '') + '/",
    )
    # Identity pill is filled client-side from the session endpoint.
    html = html.replace(
        '__USER_IDENTITY__',
        '<span id="stmx-user">&nbsp;</span>',
    )
    # Page-wide language switcher — same three placeholders app.py fills at
    # render time, so the Streamlit and static paths behave identically.
    if _i18n is not None:
        html = (html
                .replace('__I18N_CSS__', '<style>' + _i18n.switcher_css() + '</style>')
                .replace('__I18N_SWITCHER__', _i18n.switcher_html())
                .replace('__I18N_ENGINE__', _i18n.engine_js()))
    else:
        for _ph in ('__I18N_CSS__', '__I18N_SWITCHER__', '__I18N_ENGINE__'):
            html = html.replace(_ph, '')      # never leak a raw placeholder
    return html


def build() -> Path:
    shell = extract_literals(ROOT / "app.py", {"html_head", "html_tail", "email_tool_content"})
    sections = collect_sections()

    page = "\n".join(
        [shell["html_head"]]
        + sections
        + [shell["email_tool_content"], shell["html_tail"]]
    )
    page = rewire_for_static(page)

    # Fill the identity pill + hard sign-out from the server session.
    page = page.replace(
        "</body>",
        """<script>
  fetch('/api/me', {credentials: 'same-origin'})
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      var el = document.getElementById('stmx-user');
      if (el && d && d.user) { el.textContent = d.user; }
      else if (d === null) { window.location.href = '/login'; }
    })
    .catch(function () {});
</script>
</body>""",
        1,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(page, encoding="utf-8")
    return OUT_FILE


if __name__ == "__main__":
    out = build()
    kb = out.stat().st_size / 1024
    print(f"built {out.relative_to(ROOT)}  ({kb:,.0f} KB)")
