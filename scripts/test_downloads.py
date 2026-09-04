"""Download triggers must fire on the right topic and stay silent otherwise.

    python3 scripts/test_downloads.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import downloads as D                                              # noqa: E402

PASS = FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")


def ids(text):
    return sorted(d["id"] for d in D.find_downloads(text))


print("\nevery registered asset exists on disk")
for a in D.ASSETS:
    p = Path(__file__).resolve().parent.parent / "assets" / "downloads" / a["filename"]
    check(f"{a['id']:26s} file present", p.is_file(), True)

print("\nthe right deck for the right question")
check("masking question -> data-boundary deck",
      ids("How does privacy masking work on the dashcam?"), ["gdpr_data_boundary_deck"])
check("controller/processor -> roles deck",
      ids("Are we the controller or the processor here?"), ["gdpr_roles_deck"])
check("DPA question -> roles deck",
      ids("Do we need to sign a DPA with every EU customer?"), ["gdpr_roles_deck"])
check("China transfer -> regulatory briefing",
      ids("What about cross-border transfer to our China HQ?"),
      ["gdpr_regulatory_briefing"])
check("AI Act -> regulatory briefing",
      ids("When does the EU AI Act apply to our DMS?"), ["gdpr_regulatory_briefing"])

print("\nno false positives")
for text, why in [
    ("A bare mention of GDPR in passing.", "bare 'gdpr' must not trigger anything"),
    ("The customer can afford it.", "the English word 'can'"),
    ("Our ADAS detects pedestrians and lane departure.", "unrelated product answer"),
    ("Samsara closed FY2026 at $1.9B ARR.", "competitor financials"),
    ("He is obdurate about the price.", "'obd' inside a word"),
]:
    check(f"{why:38s} -> nothing", ids(text), [])

print("\nthe legal-review draft is never downloadable")
check("no asset ships the whitepaper",
      any("Whitepaper" in a["filename"] for a in D.ASSETS), False)
check("Jerry is told not to offer it",
      "never offer it" in D.DOWNLOAD_HINT, True)

print("\ncap clears a multi-match compliance answer")
many = ("Explain controller vs processor, privacy masking, and cross-border "
        "transfer to China.")
check("three GDPR assets all surface", len(D.find_downloads(many)), 3)
check("MAX_DOWNLOADS >= 3", D.MAX_DOWNLOADS >= 3, True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
