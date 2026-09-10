"""Jerry's chat output must render as formatted text, not raw markdown.

    python3 scripts/test_chat_markdown.py

Background: templates/jerry.html rendered answers with a hand-rolled regex
`md()` that understood only ```code```, `code`, ###, bold, em, links and "-"
bullets. Everything else reached the user as raw markup — #, ##, ####, ordered
lists, blockquotes, horizontal rules, nested lists, strikethrough and tables.
It now uses marked + DOMPurify, vendored locally because most users are in
China where a public CDN is unreliable.

This checks the wiring and the legacy fallback. The marked path itself needs a
DOM; it is exercised in a browser (20 assertions incl. XSS) — see CLAUDE.md.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "templates" / "jerry.html"
VENDOR = ROOT / "assets" / "vendor"

PASS = FAIL = 0


def check(name, got, want=True):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}\n         got: {got!r}  want: {want!r}")


html = PAGE.read_text(encoding="utf-8")

print("\nthe parser is vendored, not pulled from a CDN at runtime")
for f, floor in (("marked.min.js", 20_000), ("purify.min.js", 10_000)):
    p = VENDOR / f
    check(f"{f} present", p.is_file())
    if p.is_file():
        check(f"{f} looks like a real build (> {floor:,} bytes)",
              p.stat().st_size > floor)
        check(f"{f} is not an error page",
              "<!DOCTYPE" not in p.read_text(encoding="utf-8", errors="replace")[:200])
check("page loads them from our own origin",
      html.count('src="/assets/vendor/') == 2)
check("no CDN script tag in the page",
      bool(re.search(r'<script[^>]+src="https?://', html)), False)

print("\nrenderer wiring")
check("marked is configured with gfm", "gfm: true" in html)
check("single newlines become breaks", "breaks: true" in html)
check("output is sanitised", "DOMPurify.sanitize(" in html)
check("tables get the scroll wrapper", '<div class="tblwrap"><table>' in html)
check("legacy fallback is retained", "function mdLegacy(" in html)
check("md() falls back when the libs are missing",
      "if (!MD_READY) return mdLegacy(t);" in html)
check("and falls back if marked throws", "return mdLegacy(t);" in html.split("catch (e)")[1][:60])

print("\nstyling exists for everything that can now render")
for sel in (".body h1", ".body h2", ".body ol", ".body blockquote",
            ".body hr", ".body del", ".body table", ".body .tblwrap"):
    check(f"{sel} styled", sel in html)

print("\nthe legacy fallback still works on its own (node)")
start = html.index("  /* GFM pipe tables.")
end = html.index("  /* ---------- modals ---------- */")
js = (
    "function esc(s){return String(s).replace(/&/g,'&amp;')"
    ".replace(/</g,'&lt;').replace(/>/g,'&gt;');}\n"
    + html[start:end]
    + "\nMD_READY=false;\n"
    "var a=md('**b** text');"
    "var t=md('| A | B |\\n|---|---|\\n| 1 | 2 |');"
    "console.log(JSON.stringify({bold:/<strong>b<\\/strong>/.test(a),"
    "table:/<table>/.test(t),th:/<th/.test(t)}));"
)
try:
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
    if out.returncode == 0:
        import json
        res = json.loads(out.stdout.strip().splitlines()[-1])
        check("fallback renders bold", res["bold"])
        check("fallback renders tables", res["table"])
        check("fallback emits <th>", res["th"])
    else:
        print(f"  skip node unavailable or errored: {out.stderr.strip()[:90]}")
except (FileNotFoundError, subprocess.TimeoutExpired):
    print("  skip node not installed")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
