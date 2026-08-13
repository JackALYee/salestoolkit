"""Override-credential list: precedence, hashing, and password change.

    python3 scripts/test_customized_login.py
"""
import pathlib, sys, tempfile, types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
_st = types.ModuleType("streamlit"); _st.session_state = {}
class _S:
    def get(self, k, d=None): return None
_st.secrets = _S(); sys.modules["streamlit"] = _st

import customized_login as cl
import login

fails = 0
def check(label, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"   {detail}"))
    if not cond: fails += 1

# Isolate the store so the test never touches a real one.
cl._LOCAL_STORE = pathlib.Path(tempfile.mkdtemp()) / "store.json"
cl._db = lambda: None

print("=== hashing ===")
h = cl.hash_password("correct horse battery")
check("hash is not the password", "correct horse battery" not in h)
check("salted: two hashes of the same password differ",
      cl.hash_password("x12345678") != cl.hash_password("x12345678"))
check("verifies the right password", cl._check("correct horse battery", h))
check("rejects the wrong password", not cl._check("wrong", h))
check("rejects a corrupted hash", not cl._check("correct horse battery", "garbage"))

print("\n=== the seeded account ===")
check("lucian is on the list", cl.is_custom_user("lucian@streamax.com"))
check("seed password works", cl.verify("lucian@streamax.com", "12345678"))
check("wrong password rejected", not cl.verify("lucian@streamax.com", "1234567"))
check("case-insensitive email", cl.verify("Lucian@Streamax.COM", "12345678"))
check("unlisted account rejected", not cl.verify("stranger@streamax.com", "12345678"))
check("empty password rejected", not cl.verify("lucian@streamax.com", ""))

print("\n=== password rules ===")
check("too short rejected", cl.validate_new_password("short1") != "")
check("padded rejected", cl.validate_new_password(" spaced12 ") != "")
check("8+ chars accepted", cl.validate_new_password("longenough") == "")

print("\n=== changing the password ===")
ok, _ = cl.set_password("lucian@streamax.com", "a-much-better-one")
check("change succeeds", ok)
check("new password works", cl.verify("lucian@streamax.com", "a-much-better-one"))
check("OLD SEED PASSWORD NO LONGER WORKS", not cl.verify("lucian@streamax.com", "12345678"))
check("store holds a hash, never the plaintext",
      "a-much-better-one" not in cl._LOCAL_STORE.read_text())
ok, msg = cl.set_password("stranger@streamax.com", "whatever12")
check("cannot set a password for an unlisted account", not ok, msg)
ok, msg = cl.set_password("lucian@streamax.com", "short")
check("rejects a weak new password", not ok, msg)

print("\n=== login precedence: mail servers are tried FIRST ===")
calls = []
def fake_smtp(host, port, mode, email, password, timeout=10):
    calls.append(host)
    return (False, False, "(535, b'auth failed')")
login._smtp_auth = fake_smtp

calls.clear()
ok, msg = login.verify_streamax_credentials("lucian@streamax.com", "a-much-better-one")
check("override accepted only after both mail backends refused", ok and msg == "Custom",
      f"({ok}, {msg})")
check("both mail servers were tried first", len(calls) == 2, str(calls))

calls.clear()
ok, msg = login.verify_streamax_credentials("lucian@streamax.com", "wrong-password")
check("wrong override password still fails", not ok)

# A real mailbox password must win outright.
def good_smtp(host, port, mode, email, password, timeout=10):
    calls.append(host)
    return (True, False, "")
login._smtp_auth = good_smtp
calls.clear()
ok, msg = login.verify_streamax_credentials("lucian@streamax.com", "their-real-mail-password")
check("a real mailbox password wins without consulting the override",
      ok and msg == "Success", f"({ok}, {msg})")
check("stopped at the first mail server", len(calls) == 1, str(calls))

login._smtp_auth = fake_smtp
print("\n=== domain gate ===")
ok, msg = login.verify_streamax_credentials("random@gmail.com", "whatever12")
check("non-streamax address still rejected when not on the list",
      not ok and "streamax.com" in msg, msg)

print("\n=== the session identity must be the email, not the marker ===")
# server.py maps the verify() marker to a session identity. "Custom" resolving
# to itself would give every override user one shared identity.
import re
src = pathlib.Path(__file__).resolve().parent.parent.joinpath("server.py").read_text()
check("server maps both Success and Custom to the email",
      'message in ("Success", "Custom")' in src)

print(f"\n{'ALL PASS' if not fails else str(fails)+' FAILED'}")
sys.exit(1 if fails else 0)
