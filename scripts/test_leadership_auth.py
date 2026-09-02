"""Leadership must prove a mailbox — no toolkit password, no bootstrap door.

Also covers the two Outlook regressions: one SASL path for every password, and
policy rejections that must not be reported as a wrong password.

    python3 scripts/test_leadership_auth.py

SMTP is stubbed throughout; nothing here touches a real mail server.
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


# ── stub the mail servers ───────────────────────────────────────────────────
MAILBOX = {}          # email -> password the "mail server" accepts
POLICY_BLOCKED = set()   # mailboxes whose tenant refuses password sign-in


def fake_smtp_auth(host, port, mode, email, password, timeout=10):
    e = email.strip().lower()
    if e in POLICY_BLOCKED:
        return False, True, "535 5.7.139 SmtpClientAuthentication is disabled for the Tenant"
    if MAILBOX.get(e) == password:
        return True, False, ""
    return False, False, "535 authentication failed"


L._smtp_auth = fake_smtp_auth

TOOLKIT = {}          # email -> toolkit password


class FakeCustom:
    SELF_SERVICE_DOMAIN = "@streamax.com"

    def is_custom_user(self, e): return (e or "").lower() in TOOLKIT
    def can_self_serve(self, e): return (e or "").lower().endswith("@streamax.com")
    def has_password(self, e): return bool(TOOLKIT.get((e or "").lower()))
    def verify(self, e, pw): return TOOLKIT.get((e or "").lower()) == pw


L._custom = FakeCustom()

LEAD = "sunyan@streamax.com"
NORM = "kiki@streamax.com"
assert L.resolve_leadership(LEAD) and not L.resolve_leadership(NORM)

print("\n_test shortcuts must not carry a real person's clearance")
ok, ident = L.verify_streamax_credentials("jerry_test", "testme")
check("jerry_test still signs in", ok, True)
check("jerry_test is NOT leadership", L.resolve_leadership(ident), False)
check("jerry_test is NOT vip", L.resolve_vip(ident), False)
check("jerry_test gets no special relationship",
      L.resolve_special_relationship(ident), None)
check("jerry_test still plays its easter egg",
      bool(L.resolve_easter_egg(ident)), True)
ok, ident = L.verify_streamax_credentials("hekun_test", "testme")
check("hekun_test is NOT leadership", L.resolve_leadership(ident), False)
check("hekun_test still plays its easter egg", bool(L.resolve_easter_egg(ident)), True)

print("\nleadership: every non-mailbox path is closed")
TOOLKIT.clear(); MAILBOX.clear(); POLICY_BLOCKED.clear()
ok, msg = L.verify_streamax_credentials(LEAD, "anything-at-all")
check("no toolkit pw + junk pw -> REJECTED (bootstrap closed)", ok, False)
check("  and never returns the Setup marker", msg == "Setup", False)

TOOLKIT[LEAD] = "toolkit-secret"
ok, msg = L.verify_streamax_credentials(LEAD, "toolkit-secret")
check("correct toolkit pw -> still REJECTED", ok, False)
check("  message explains leadership needs the mailbox",
      "mailbox password" in msg, True)

MAILBOX[LEAD] = "real-mail-pw"
ok, msg = L.verify_streamax_credentials(LEAD, "real-mail-pw")
check("correct MAILBOX pw -> accepted", (ok, msg), (True, "Success"))

print("\nnon-leadership behaviour is unchanged")
TOOLKIT.clear(); MAILBOX.clear()
os.environ["LOGIN_MODE"] = "open"
ok, msg = L.verify_streamax_credentials(NORM, "whatever")
check("bootstrap door still open for everyone else (LOGIN_MODE=open)",
      (ok, msg), (True, "Setup"))
os.environ["LOGIN_MODE"] = "strict"
ok, _ = L.verify_streamax_credentials(NORM, "whatever")
check("  and shut again under the shipping default (strict)", ok, False)
TOOLKIT[NORM] = "my-toolkit-pw"
ok, msg = L.verify_streamax_credentials(NORM, "my-toolkit-pw")
check("toolkit password still works", (ok, msg), (True, "Custom"))
MAILBOX[NORM] = "mail-pw"
ok, msg = L.verify_streamax_credentials(NORM, "mail-pw")
check("mailbox is still the recovery path", (ok, msg), (True, "Success"))

print("\nOutlook: a policy block must not read as a wrong password")
TOOLKIT.clear(); MAILBOX.clear()
POLICY_BLOCKED.add(NORM)
TOOLKIT[NORM] = "set-so-bootstrap-is-off"
ok, msg = L.verify_streamax_credentials(NORM, "their-real-outlook-pw")
check("policy-blocked mailbox -> rejected", ok, False)
check("  message does NOT claim the password is wrong",
      "password incorrect" in msg.lower(), False)
check("  message points at Microsoft sign-in", "Sign in with Microsoft" in msg, True)

print("\nOne SASL path for every password (the ASCII/non-ASCII split is gone)")
src = Path("login.py").read_text(encoding="utf-8")
check("smtplib.login() is no longer used", "server.login(" in src, False)
# one definition + exactly one call site
check("_auth_sasl is the single entry point", src.count("_auth_sasl(server"), 2)
check("microsoft gets a longer timeout than coremail",
      '"timeout": 25' in src and '"timeout": 12' in src, True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
