"""Jerry recommends URLs, so the URLs have to be right.

    python3 scripts/test_resource_links.py           # offline checks
    python3 scripts/test_resource_links.py --live    # also fetch every URL

Why this exists: a wrong link is worse than no link. streamax.com answers
unknown paths with HTTP 200 and its own 404 page, so a fabricated URL passes a
naive status check and only fails in front of a customer — which is why --live
asserts the content type too, not just the status.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "jerry_gpt_knowledge"
REG = KB / "26_trucking_hub_and_links.md"

PASS = FAIL = 0


def check(name, got, want=True):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}\n         got: {got!r}  want: {want!r}")


reg = REG.read_text(encoding="utf-8")

EXPECTED = {
    "https://www.streamax-trucking.com/":          "the hub",
    "https://streamax-salestoolkit.com":           "Sales Toolkit",
    "https://www.streamax-trucking.com/esim/":     "eSIM",
    "https://www.streamax-trucking.com/customer/": "Customer Portal",
    "https://www.streamax-trucking.com/sentinel/": "Sentinel",
    "https://streamax-sentinel.com":               "Sentinel, public domain",
}

print("\nthe registry carries every resource")
check("registry file exists", REG.is_file())
for url, what in EXPECTED.items():
    check(f"{what:24s} {url}", url in reg)

print("\ntrailing slashes (without one the host costs a redirect first)")
for path in ("/esim/", "/customer/", "/sentinel/"):
    bare = f"https://www.streamax-trucking.com{path.rstrip('/')}"
    # the bare form may appear only as part of the slashed one
    stray = re.findall(re.escape(bare) + r"(?![/\w])", reg)
    check(f"{path:12s} never written without its slash", stray, [])

print("\nno credentials in the knowledge base")
kb_all = "\n".join(p.read_text(encoding="utf-8") for p in KB.glob("*.md"))
# The hub page prints a shared demo sign-in. Deliberately NOT hardcoded here:
# writing the password into this file would commit it to the very repo the
# check exists to keep it out of, and it would go stale the moment it rotates.
# --live reads the live credential from the hub and asserts the KB lacks it.
check("registry points at the hub rather than quoting credentials",
      "prints it" in reg or "read it" in reg)
check("no 'Demo' credential block copied into the registry",
      bool(re.search(r"(?i)\bpassword\s*[:=]", reg)), False)

print("\nJerry is told how to use them")
jg = (ROOT / "jerry_gpt.py").read_text(encoding="utf-8")
check("linking instruction present", "LINKING TO DIVISION RESOURCES" in jg)
check("told to use the URL exactly", "exactly as written" in jg)
check("warned off inventing streamax.com paths",
      "its own 404" in jg)
check("told to flag sign-in walls", "login wall" in jg)
check("told not to quote the demo password", "demo password" in jg)

print("\nthe deployed version is observable")
srv = (ROOT / "server.py").read_text(encoding="utf-8")
app = (ROOT / "app.py").read_text(encoding="utf-8")
m_srv = re.search(r'APP_VERSION = "([^"]+)"', srv)
m_app = re.search(r"Version (\d+\.\d+\.\d+ \(\d+\))", app)
check("server.py declares APP_VERSION", bool(m_srv))
check("app.py declares a version banner", bool(m_app))
if m_srv and m_app:
    check(f"they agree ({m_srv.group(1)})", m_srv.group(1), m_app.group(1))
check("/healthz reports the version", '"version": APP_VERSION' in srv)
check("/healthz reports the deployed commit", "RENDER_GIT_COMMIT" in srv)

print("\nno guessed streamax.com deep links anywhere in the KB")
deep = sorted(set(re.findall(r"https?://(?:www\.)?streamax\.com/\S+", kb_all)))
check("none present", deep, [])

if "--live" in sys.argv:
    import urllib.request

    print("\nthe live demo credential has not leaked into the KB")
    try:
        req = urllib.request.Request("https://www.streamax-trucking.com/",
                                     headers={"User-Agent": "link-check"})
        hub = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
        # the hub renders it as <code>user</code><code>password</code>
        creds = re.findall(r"<code>([^<]{4,64})</code>", hub)
        if creds:
            leaked = [c for c in creds if c in kb_all]
            check(f"none of the {len(creds)} hub credential(s) appear in the KB",
                  leaked, [])
        else:
            print("  skip could not find a credential block on the hub")
    except Exception as exc:                                         # noqa: BLE001
        print(f"  skip hub unreachable: {type(exc).__name__}")

    print("\nlive fetch")
    DOCS = re.findall(r"https://streamax-sentinel\.com/Docs/\S+?\.(?:docx|pptx)", kb_all)
    for url in list(EXPECTED) + sorted(set(DOCS)):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "link-check"})
            with urllib.request.urlopen(req, timeout=45) as r:
                ct = r.headers.get("Content-Type", "")
                ok = r.status == 200
                if url.endswith((".docx", ".pptx")):
                    ok = ok and "html" not in ct.lower()
                check(f"{url[:58]:60s} {r.status}", ok)
        except Exception as exc:                                     # noqa: BLE001
            check(f"{url[:58]:60s} unreachable", False, f"{type(exc).__name__}")
else:
    print("\n  (run with --live to fetch every URL)")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
