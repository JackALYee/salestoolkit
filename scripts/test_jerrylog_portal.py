"""The Jerry log portal at /jerrylog — gate, wiring, and the retired Sheet.

    python3 scripts/test_jerrylog_portal.py
    JERRY_GPT_DB_URL=... python3 scripts/test_jerrylog_portal.py --db

The portal exposes EVERY user's questions, so the gate is the thing most worth
pinning: signed in is not enough, the address must be leadership or an explicitly approved log reviewer.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("AUTH_SECRET", "test-secret-jerrylog")
os.environ.setdefault("APP_MODE", "html")

import server as S                                                  # noqa: E402
import login as L                                                   # noqa: E402

PASS = FAIL = 0


def check(name, got, want=True):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}\n         got: {got!r}  want: {want!r}")


class Req:
    """Minimal stand-in for a Request carrying one cookie."""
    def __init__(self, token=None):
        self.cookies = {S.COOKIE_NAME: token} if token else {}
        self.headers = {}
        self.client = type("C", (), {"host": "127.0.0.1"})()


from fastapi import HTTPException                                   # noqa: E402

LEAD = "sunyan@streamax.com"
NORM = "kiki@streamax.com"
assert L.resolve_leadership(LEAD) and not L.resolve_leadership(NORM)

print("\nthe gate")
try:
    S.require_jerry_log_access(Req())
    check("anonymous is refused", False)
except HTTPException as e:
    check(f"anonymous is refused ({e.status_code})", e.status_code, 401)

try:
    S.require_jerry_log_access(Req(S.make_token(NORM)))
    check("signed in but not leadership is refused", False)
except HTTPException as e:
    check(f"signed in but not leadership is refused ({e.status_code})",
          e.status_code, 403)

check("leadership passes", S.require_jerry_log_access(Req(S.make_token(LEAD))), LEAD)

print("\nthe page route")
r = S.page_jerrylog(Req())
check("anonymous redirects to the login", getattr(r, "status_code", 0), 302)
r = S.page_jerrylog(Req(S.make_token(NORM)))
check("non-leadership gets 403, not a redirect", r.status_code, 403)
body = bytes(r.body).decode("utf-8", "replace")
check("  and is told who it is for", "approved log reviewers" in body)
check("  and which account they are on", NORM in body)

print("\nJimmy gets VIP and explicit log access, independently of pricing clearance")
JIMMY = "jimmy@streamax.com"
check("Jimmy is VIP", L.resolve_vip(JIMMY))
check("Jimmy remains outside leadership pricing clearance", L.resolve_leadership(JIMMY), False)
for who in (JIMMY, " JIMMY@STREAMAX.COM "):
    check("Jimmy's log permission normalizes case/whitespace", L.resolve_jerry_log_access(who))
check("Jimmy can load the portal", S.page_jerrylog(Req(S.make_token(JIMMY))).status_code, 200)
for who in ("caojun@streamax.com", "wangrui@streamax.com", "Jimmy", "jimmy@example.com", "Jerry (demo)"):
    check(f"{who} has no added log permission", L.resolve_jerry_log_access(who), False)

# Exercise every HTTP gate, rather than only the shared helper.
from fastapi.testclient import TestClient
from unittest.mock import patch
client = TestClient(S.app)
with patch.object(S, "_history_on", return_value=True), \
     patch.object(S._history, "log_search", return_value={"total": 0, "rows": []}), \
     patch.object(S._history, "log_stats", return_value={"questions": 0}), \
     patch.object(S._history, "log_filters", return_value={"users": [], "models": []}):
    for identity, expected in ((None, 401), (NORM, 403), ("caojun@streamax.com", 403),
                               ("Jerry (demo)", 403), (LEAD, 200), (JIMMY, 200)):
        client.cookies.clear()
        if identity:
            client.cookies.set(S.COOKIE_NAME, S.make_token(identity))
        for path in ("/api/jerrylog", "/api/jerrylog/meta", "/api/jerrylog/export"):
            check(f"{identity or 'anonymous'} {path}", client.get(path).status_code, expected)
client.close()

print("\nthe Google Sheet is retired")
srv = (ROOT / "server.py").read_text(encoding="utf-8")
check("no log_query() call remains", "_usage.log_query(" in srv, False)
check("the pricing heuristic still runs", "_is_pricing_sensitive" in srv)
check("a missing database is now loud", "NOT LOGGED" in srv)
check("the turn carries is_leadership", "is_leadership=bool(is_leadership)" in srv)
check("the turn carries sensitive_flagged", "sensitive_flagged=sensitive" in srv)

hist = (ROOT / "chat_history.py").read_text(encoding="utf-8")
check("schema adds both columns in place",
      "ADD COLUMN IF NOT EXISTS is_leadership" in hist
      and "ADD COLUMN IF NOT EXISTS sensitive_flagged" in hist)
check("portal queries exist",
      all(f"def {f}(" in hist for f in ("log_stats", "log_search", "log_filters")))

print("\nthe migration script")
mig = (ROOT / "scripts" / "migrate_sheet_to_portal.py").read_text(encoding="utf-8")
check("targets the 'queries' tab, not the first sheet", "sheet={SHEET_TAB}" in mig)
check("supports --dry-run", "--dry-run" in mig)
check("inserts only what is missing", "not in have" in mig)

if "--db" in sys.argv and os.environ.get("JERRY_GPT_DB_URL"):
    import chat_history as H
    print("\nagainst the live database")
    st = H.log_stats()
    check("stats come back", bool(st.get("questions")))
    tot = H.log_search(limit=1)["total"]
    sens = H.log_search(only_sensitive=True, limit=1)["total"]
    lead = H.log_search(only_leadership=True, limit=1)["total"]
    check(f"sensitive filter narrows ({sens} of {tot})", 0 < sens < tot)
    check(f"leadership filter narrows ({lead} of {tot})", 0 < lead < tot)
    check("stats agree with the filtered count", st["sensitive"], sens)
    one = H.log_search(limit=1)["rows"]
    check("a row carries its answer", bool(one and one[0]["answer"]))
    check("filters list users", bool(H.log_filters()["users"]))
else:
    print("\n  (run with --db and JERRY_GPT_DB_URL to check the live database)")

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
