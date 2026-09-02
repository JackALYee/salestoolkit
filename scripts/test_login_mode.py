"""LOGIN_MODE switch — strict vs open, for NON-leadership accounts.

    python3 scripts/test_login_mode.py

Leadership is covered by test_leadership_auth.py; it must be unaffected by this
switch, which is asserted here too. SMTP is stubbed — nothing hits a real
mail server.
"""
import os
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_st = types.ModuleType("streamlit")
_st.session_state = {}
_st.secrets = {}
for _n in ("cache_resource", "cache_data"):
    setattr(_st, _n, lambda *a, **k: (lambda f: f))
sys.modules.setdefault("streamlit", _st)

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


MAILBOX, TOOLKIT = {}, {}


def fake_smtp_auth(host, port, mode, email, password, timeout=10):
    if MAILBOX.get((email or "").lower()) == password:
        return True, False, ""
    return False, False, "535 authentication failed"


L._smtp_auth = fake_smtp_auth


class FakeCustom:
    def is_custom_user(self, e): return (e or "").lower() in TOOLKIT
    def can_self_serve(self, e): return (e or "").lower().endswith("@streamax.com")
    def has_password(self, e): return bool(TOOLKIT.get((e or "").lower()))
    def verify(self, e, pw): return TOOLKIT.get((e or "").lower()) == pw


L._custom = FakeCustom()

USER = "someone@streamax.com"
LEAD = "sunyan@streamax.com"


def mode(v):
    if v is None:
        os.environ.pop("LOGIN_MODE", None)
    else:
        os.environ["LOGIN_MODE"] = v


print("\nmode resolution")
for raw, want in [(None, "strict"), ("", "strict"), ("strict", "strict"),
                  ("STRICT", "strict"), ("real", "strict"),
                  ("open", "open"), ("Open", "open"), ("temp", "open"),
                  ("any", "open"), ("bootstrap", "open"),
                  ("nonsense", "strict"), ("yes", "strict")]:
    mode(raw)
    check(f"LOGIN_MODE={raw!r} -> {want}", L.login_mode(), want)

print("\nSTRICT (version 1): a real credential is required")
mode("strict")
MAILBOX.clear(); TOOLKIT.clear()
ok, msg = L.verify_streamax_credentials(USER, "any-old-thing")
check("no credential -> REJECTED", ok, False)
check("  and never returns Setup", msg == "Setup", False)
check("  message names the mailbox password", "mailbox password" in msg, True)

MAILBOX[USER] = "real-mail-pw"
ok, msg = L.verify_streamax_credentials(USER, "real-mail-pw")
check("correct mailbox password -> accepted", (ok, msg), (True, "Success"))

MAILBOX.clear(); TOOLKIT[USER] = "toolkit-pw"
ok, msg = L.verify_streamax_credentials(USER, "toolkit-pw")
check("correct toolkit password -> accepted", (ok, msg), (True, "Custom"))
ok, _ = L.verify_streamax_credentials(USER, "wrong")
check("wrong password -> rejected", ok, False)

print("\nOPEN (version 2): any password admits until one is set")
mode("open")
MAILBOX.clear(); TOOLKIT.clear()
ok, msg = L.verify_streamax_credentials(USER, "literally-anything")
check("no credential -> admitted as Setup", (ok, msg), (True, "Setup"))
TOOLKIT[USER] = "toolkit-pw"
ok, msg = L.verify_streamax_credentials(USER, "literally-anything")
check("door CLOSES once a password is set", ok, False)
ok, msg = L.verify_streamax_credentials(USER, "toolkit-pw")
check("  and the real one still works", (ok, msg), (True, "Custom"))

print("\nleadership ignores the switch entirely")
for m in ("strict", "open"):
    mode(m)
    MAILBOX.clear(); TOOLKIT.clear()
    ok, msg = L.verify_streamax_credentials(LEAD, "anything")
    check(f"LOGIN_MODE={m}: leadership + junk -> REJECTED", ok, False)
    TOOLKIT[LEAD] = "toolkit-pw"
    ok, _ = L.verify_streamax_credentials(LEAD, "toolkit-pw")
    check(f"LOGIN_MODE={m}: leadership + toolkit pw -> REJECTED", ok, False)
    MAILBOX[LEAD] = "mail-pw"
    ok, msg = L.verify_streamax_credentials(LEAD, "mail-pw")
    check(f"LOGIN_MODE={m}: leadership + mailbox pw -> accepted", (ok, msg),
          (True, "Success"))

print("\nthe set-a-password prompt only follows a credential-LESS admission")
# server.py decides this from the marker verify_streamax_credentials returns.
def prompts(marker):
    return marker == "Setup"

mode("open")
MAILBOX.clear(); TOOLKIT.clear()
_, m = L.verify_streamax_credentials(USER, "anything")
check("open + no credential (Setup) -> prompt shown", prompts(m), True)

MAILBOX.clear(); TOOLKIT.clear(); MAILBOX[USER] = "mail-pw"
_, m = L.verify_streamax_credentials(USER, "mail-pw")
check("open + real MAILBOX password -> NO prompt", prompts(m), False)

MAILBOX.clear(); TOOLKIT.clear(); TOOLKIT[USER] = "toolkit-pw"
_, m = L.verify_streamax_credentials(USER, "toolkit-pw")
check("open + real TOOLKIT password -> NO prompt", prompts(m), False)

mode("strict")
MAILBOX.clear(); TOOLKIT.clear(); MAILBOX[USER] = "mail-pw"
_, m = L.verify_streamax_credentials(USER, "mail-pw")
check("strict + real mailbox password -> NO prompt", prompts(m), False)
MAILBOX.clear(); TOOLKIT[USER] = "toolkit-pw"
_, m = L.verify_streamax_credentials(USER, "toolkit-pw")
check("strict + real toolkit password -> NO prompt", prompts(m), False)

src = Path("server.py").read_text(encoding="utf-8")
check("server.py gates the prompt on the Setup marker alone",
      'if message == "Setup":\n        payload["needs_password_setup"] = True' in src,
      True)

mode("strict")
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
