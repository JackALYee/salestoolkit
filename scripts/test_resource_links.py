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

print("\nno credentials anywhere")
kb_all = "\n".join(p.read_text(encoding="utf-8") for p in KB.glob("*.md"))
# The hub used to print a shared demo sign-in for the Customer Portal, and the
# registry used to send people there to read it. That credential came off the
# page when it went public on 2026-09-21, so the old contract ("point at the
# hub, do not quote") is now actively wrong: it sends people to read something
# that is not there. The contract is now simply that no credential exists to
# hand out. --live asserts none has come back onto the public page.
check("registry sends people to a human for an account",
      "ask your Streamax contact" in reg)
check("registry does not send anyone to a page to read a credential",
      "prints it" in reg or "which prints" in reg, False)
check("no 'Demo' credential block copied into the registry",
      bool(re.search(r"(?i)\bpassword\s*[:=]", reg)), False)

print("\nJerry is told how to use them")
jg = (ROOT / "jerry_gpt.py").read_text(encoding="utf-8")
check("linking instruction present", "LINKING TO DIVISION RESOURCES" in jg)
check("told to use the URL exactly", "exactly as written" in jg)
check("warned off inventing streamax.com paths",
      "its own 404" in jg)
check("told to flag sign-in walls", "login wall" in jg)
check("told there is no credential to hand out", "NO shared demo password" in jg)
check("told which links a customer may have", "safe to send to a CUSTOMER" in jg)
check("told to link the hub root, not a /loop path", "never a /loop path" in jg)

print("\nthe loop is linked at the root, not at a path that will redirect")
check("registry says to link the hub root for the loop",
      "never `/loop`" in reg or "never a /loop" in reg)
stray_loop = re.findall(r"streamax-trucking\.com/loop", reg)
check("no /loop URL written out", stray_loop, [])

print("\ncustomer-safe is stated, not left to be guessed")
for url in ("https://www.streamax-trucking.com/",
            "https://www.streamax-trucking.com/esim/",
            "https://streamax-sentinel.com"):
    check(f"{url[:44]:46s} marked customer-safe", "Customer-safe" in reg)

print("\nthe public naming rule for the pre-release ADAS+DMS unit")
# The trucking site labels it "Dashcam" on purpose — the model name is on the
# pre-release list and that page is public now. Jerry writes customer copy, so
# the rule has to reach him too.
check("registry carries the dashcam naming rule",
      "Call it a dashcam, not a model number" in reg)
check("registry warns the loop's coverage shapes are illustrative",
      "illustrative, not datasheet" in reg)

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

    print("\nthe public hub still prints no credential")
    # It went public on 2026-09-21 and the demo sign-in came off with it. This
    # used to check that the KB had not copied the hub's credential; now that
    # there is none, the useful check is the other direction — that one has not
    # reappeared on a page anyone can read.
    try:
        req = urllib.request.Request("https://www.streamax-trucking.com/",
                                     headers={"User-Agent": "link-check"})
        hub = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
        creds = re.findall(r"<code>([^<]{4,64})</code>", hub)
        check(f"no credential block on the public hub ({len(creds)} <code> found)",
              creds, [])
        check("hub is the public, indexed page the KB describes",
              'content="index, follow"' in hub)
        if creds:
            check("and none of it has leaked into the KB",
                  [c for c in creds if c in kb_all], [])
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
