"""A toolkit password set in OPEN mode must keep working forever, in either mode.

The promise being pinned: switching LOGIN_MODE is a policy change for people who
have NO password yet. It must never invalidate, hide or drop a password someone
already set — including across a switch to strict and back again.

    python3 scripts/test_password_persistence.py

Uses the REAL customized_login module against a temporary store, so a future
change that makes storage mode-dependent fails here.
"""
import os
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_st = types.ModuleType("streamlit")
_st.session_state = {}
_st.secrets = {}
for _n in ("cache_resource", "cache_data"):
    setattr(_st, _n, lambda *a, **k: (lambda f: f))
sys.modules.setdefault("streamlit", _st)

# Force the local-file backend so the test never touches the production DB.
os.environ.pop("JERRY_GPT_DB_URL", None)

import customized_login as cl                                       # noqa: E402
import login as L                                                   # noqa: E402

cl._LOCAL_STORE = Path(tempfile.mkdtemp()) / "store.json"
L._custom = cl

PASS = FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}\n         got:  {got!r}\n         want: {want!r}")


def fake_smtp_auth(*a, **k):
    return False, False, "535 authentication failed"      # mailbox never helps


L._smtp_auth = fake_smtp_auth


def mode(v):
    os.environ["LOGIN_MODE"] = v


USER = "rollout.person@streamax.com"
PW = "SetDuringOpenMode!7"

print("\n1. someone sets a password while the site is in OPEN mode")
mode("open")
ok, _ = L.verify_streamax_credentials(USER, "any-old-thing")
check("admitted by the open door before setting one", ok, True)
saved, detail = cl.set_password(USER, PW)
check("password saved", saved, True)
check("store reports it exists", cl.has_password(USER), True)

print("\n2. the open door shuts for THEM specifically (still open mode)")
ok, _ = L.verify_streamax_credentials(USER, "any-old-thing")
check("junk password no longer admits them", ok, False)
ok, msg = L.verify_streamax_credentials(USER, PW)
check("their real password works", (ok, msg), (True, "Custom"))

print("\n3. switch to STRICT — the password must survive and keep working")
mode("strict")
check("still stored", cl.has_password(USER), True)
ok, msg = L.verify_streamax_credentials(USER, PW)
check("password still signs them in under strict", (ok, msg), (True, "Custom"))
ok, _ = L.verify_streamax_credentials(USER, "wrong-one")
check("a wrong password is still refused", ok, False)

print("\n4. switch BACK to open — still there, still working")
mode("open")
check("still stored", cl.has_password(USER), True)
ok, msg = L.verify_streamax_credentials(USER, PW)
check("password still works after the round trip", (ok, msg), (True, "Custom"))
ok, _ = L.verify_streamax_credentials(USER, "any-old-thing")
check("and the door stays shut for them", ok, False)

print("\n5. a password can still be CHANGED in either mode")
for m, newpw in (("strict", "ChangedUnderStrict!1"), ("open", "ChangedUnderOpen!2")):
    mode(m)
    saved, _ = cl.set_password(USER, newpw)
    check(f"set_password works under {m}", saved, True)
    ok, msg = L.verify_streamax_credentials(USER, newpw)
    check(f"  new password works under {m}", (ok, msg), (True, "Custom"))

print("\n6. storage is provably independent of the switch")
src = Path("customized_login.py").read_text(encoding="utf-8")
check("customized_login.py never reads LOGIN_MODE", "LOGIN_MODE" in src, False)
check("no delete path exists", "DELETE FROM custom_login" in src, False)
check("writes are upserts, not replaces",
      "ON CONFLICT (email)" in src and "DO UPDATE SET" in src, True)

# Every address that already has a password must be unaffected by the switch.
mode("strict")
strict_view = set(cl.all_emails())
mode("open")
check("the stored address list is identical in both modes",
      set(cl.all_emails()), strict_view)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
