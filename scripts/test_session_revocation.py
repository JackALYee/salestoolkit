"""A retired account must not survive in an already-issued session cookie.

    python3 scripts/test_session_revocation.py

The bug this pins: retiring `test_account` blocked new logins but evicted
nobody. An existing signed cookie stayed valid for SESSION_DAYS, so the account
kept asking Jerry questions for five days after the block shipped, because
read_token only verified the signature and the expiry — never whether the
identity was still allowed.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("AUTH_SECRET", "test-secret-for-session-revocation")
os.environ.setdefault("APP_MODE", "html")

import server as S                                                  # noqa: E402
import login as L                                                   # noqa: E402

PASS = FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")


print("\na normal account's session still works")
tok = S.make_token("kiki@streamax.com")
check("valid cookie -> the user", S.read_token(tok), "kiki@streamax.com")

print("\na retired account's session is refused, however it was issued")
for who in ("test_account", "TEST_ACCOUNT", "test_account@streamax.com"):
    # make_token is exactly what /api/login called before the retirement,
    # so this is a cookie minted under the old rules.
    stale = S.make_token(who)
    check(f"pre-existing cookie for {who!r:26s} -> refused",
          S.read_token(stale), None)

print("\nthe cookie is otherwise perfectly valid — it fails ONLY on the identity")
stale = S.make_token("test_account")
import base64                                                       # noqa: E402
raw = base64.urlsafe_b64decode(stale.encode()).decode()
user, expiry, sig = raw.rsplit("|", 2)
check("signature is genuine", S._sign(f"{user}|{expiry}") == sig, True)
check("not expired", float(expiry) > __import__("time").time(), True)
check("and still refused", S.read_token(stale), None)

print("\nthe check is wired to login.py, not a second copy of the list")
check("login.py owns the list", hasattr(L, "RETIRED_ACCOUNTS"), True)
check("server.py calls the shared helper",
      "_login.is_retired_account" in Path(ROOT / "server.py").read_text(encoding="utf-8"),
      True)
check("server.py does NOT redefine the list",
      "RETIRED_ACCOUNTS =" in Path(ROOT / "server.py").read_text(encoding="utf-8"),
      False)

print("\ntampered and expired cookies still fail as before")
check("garbage token", S.read_token("not-a-token"), None)
check("empty token", S.read_token(""), None)
check("None token", S.read_token(None), None)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
