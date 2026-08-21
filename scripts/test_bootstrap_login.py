"""Bootstrap sign-in + dedicated toolkit password.

    python3 scripts/test_bootstrap_login.py
"""
import pathlib, sys, tempfile, types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
_st = types.ModuleType("streamlit"); _st.session_state = {}
class _S:
    def get(self, k, d=None): return None
_st.secrets = _S(); sys.modules["streamlit"] = _st

import customized_login as cl, login

fails = 0
def check(label, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"   {detail}"))
    if not cond: fails += 1

cl._LOCAL_STORE = pathlib.Path(tempfile.mkdtemp()) / "s.json"
cl._db = lambda: None
cl.SEED_HASHES.clear()                      # start with nobody provisioned

smtp_calls = []
def no_mail(host, port, mode, email, password, timeout=10):
    smtp_calls.append(host)
    return (False, False, "(535, b'auth failed')")
login._smtp_auth = no_mail

NEW = "newperson@streamax.com"

print("=== 1. any @streamax.com address gets in with any password ===")
for pw in ("literally anything", "x", "hunter2", "不是密码"):
    ok, msg = login.verify_streamax_credentials(NEW, pw)
    check(f"admitted with {pw!r}", ok and msg == "Setup", f"({ok}, {msg})")

smtp_calls.clear()
login.verify_streamax_credentials(NEW, "whatever")
check("no SMTP round-trip while bootstrapping (fast path)", not smtp_calls, str(smtp_calls))

print("\n=== 2. non-Streamax addresses are still refused ===")
ok, msg = login.verify_streamax_credentials("outsider@gmail.com", "anything")
check("gmail rejected", not ok and "streamax.com" in msg, msg)
ok, msg = login.verify_streamax_credentials("nobody@example.com", "anything")
check("example.com rejected", not ok)

print("\n=== 3. setting a toolkit password CLOSES the open door ===")
ok, _ = cl.set_password(NEW, "MyToolkitPass1")
check("first-time set succeeds with no current password", ok)
check("has_password now true", cl.has_password(NEW))

ok, msg = login.verify_streamax_credentials(NEW, "MyToolkitPass1")
check("toolkit password signs in", ok and msg == "Custom", f"({ok}, {msg})")

ok, msg = login.verify_streamax_credentials(NEW, "any old rubbish")
check("ARBITRARY PASSWORD NOW REJECTED", not ok, f"({ok}, {msg})")
ok, msg = login.verify_streamax_credentials(NEW, "")
check("empty password rejected", not ok)

print("\n=== 4. the mail password remains a recovery path ===")
smtp_calls.clear()
def mail_ok(host, port, mode, email, password, timeout=10):
    smtp_calls.append(host)
    return (password == "TheRealMailPassword", False, "")
login._smtp_auth = mail_ok
ok, msg = login.verify_streamax_credentials(NEW, "TheRealMailPassword")
check("mail password still works after a toolkit password exists",
      ok and msg == "Success", f"({ok}, {msg})")
check("mailbox was actually consulted", bool(smtp_calls))
login._smtp_auth = no_mail

print("\n=== 5. toolkit password is checked BEFORE the mailbox ===")
smtp_calls.clear()
ok, _ = login.verify_streamax_credentials(NEW, "MyToolkitPass1")
check("correct toolkit password skips SMTP entirely", ok and not smtp_calls, str(smtp_calls))

print("\n=== 6. changing it later ===")
ok, _ = cl.set_password(NEW, "SecondPass99")
check("change succeeds", ok)
check("new password works", cl.verify(NEW, "SecondPass99"))
check("old password dead", not cl.verify(NEW, "MyToolkitPass1"))
check("stored as a hash, never plaintext",
      "SecondPass99" not in cl._LOCAL_STORE.read_text())

print("\n=== 7. weak passwords refused ===")
ok, msg = cl.set_password(NEW, "short")
check("under 8 chars refused", not ok, msg)

print("\n=== 8. easter eggs and display names survive ===")
ok, msg = login.verify_streamax_credentials("jerry_test", "testme")
check("jerry_test still works", ok and msg == "Jerry")
ok, msg = login.verify_streamax_credentials("jerry@streamax.com", "anything")
check("jerry@ bootstraps with the display name", ok and msg in ("Setup", "Jerry"), msg)

print(f"\n{'ALL PASS' if not fails else str(fails)+' FAILED'}")
sys.exit(1 if fails else 0)
