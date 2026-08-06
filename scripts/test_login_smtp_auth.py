"""Prove the non-ASCII SMTP AUTH path works, against a real local SMTP server.

Standalone, no pytest, no network:  python3 scripts/test_login_smtp_auth.py
"""
import base64, pathlib, smtplib, socket, sys, threading, types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
st = types.ModuleType("streamlit"); st.session_state = {}
class X:
    def get(self, k, d=None): return None
st.secrets = X()
sys.modules["streamlit"] = st
import login

USER = "emily.sun@streamax.com"
BAD_PW = "Str3amax！2026"        # U+FF01 full-width ! — the screenshot's failure

def serve(sock, want_user, want_pass, log, mechs=b"AUTH PLAIN LOGIN"):
    conn, _ = sock.accept()
    f = conn.makefile("rwb", buffering=0)
    f.write(b"220 test.local ESMTP\r\n")
    while True:
        line = f.readline()
        if not line: break
        cmd = line.decode("utf-8", "replace").strip(); up = cmd.upper()
        if up.startswith(("EHLO", "HELO")):
            f.write(b"250-test.local\r\n250-" + mechs + b"\r\n250 SMTPUTF8\r\n")
        elif up.startswith("AUTH PLAIN "):
            raw = base64.b64decode(cmd.split(None, 2)[2])
            try:
                _, u, p = raw.decode("utf-8").split("\0")
            except Exception as e:
                log["err"] = f"decode failed: {e}"; f.write(b"535 bad\r\n"); continue
            log["user"], log["password"] = u, p
            f.write(b"235 2.7.0 Authentication successful\r\n"
                    if (u == want_user and p == want_pass) else b"535 5.7.8 bad creds\r\n")
        elif up == "AUTH LOGIN":
            f.write(b"334 VXNlcm5hbWU6\r\n")
            u = base64.b64decode(f.readline().strip()).decode("utf-8")
            f.write(b"334 UGFzc3dvcmQ6\r\n")
            p = base64.b64decode(f.readline().strip()).decode("utf-8")
            log["user"], log["password"] = u, p
            f.write(b"235 2.7.0 Authentication successful\r\n"
                    if (u == want_user and p == want_pass) else b"535 5.7.8 bad creds\r\n")
        elif up.startswith("QUIT"):
            f.write(b"221 bye\r\n"); break
        else:
            f.write(b"250 ok\r\n")
    conn.close()

def attempt(password, want_pass, mechs=b"AUTH PLAIN LOGIN"):
    sock = socket.socket(); sock.bind(("127.0.0.1", 0)); sock.listen(1)
    port = sock.getsockname()[1]; log = {}
    threading.Thread(target=serve, args=(sock, USER, want_pass, log, mechs), daemon=True).start()
    srv = smtplib.SMTP("127.0.0.1", port, timeout=5)
    try:
        login._auth_utf8(srv, USER, password)
        return True, "", log
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", log
    finally:
        try: srv.quit()
        except Exception: pass
        sock.close()

fails = 0
def check(label, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"   {detail}"))
    if not cond: fails += 1

print("=== the exact password from the screenshot (contains U+FF01) ===")
ok, err, log = attempt(BAD_PW, BAD_PW)
check("authenticates over UTF-8 AUTH PLAIN", ok, err)
check("server received the password byte-for-byte", log.get("password") == BAD_PW,
      repr(log.get("password")))

print("\n=== plain smtplib would still have blown up on it ===")
try:
    base64.b64encode(f"\0{USER}\0{BAD_PW}".encode("ascii"))
    check("smtplib ASCII encode raises", False, "expected UnicodeEncodeError")
except UnicodeEncodeError as e:
    check("smtplib ASCII encode raises UnicodeEncodeError", True)
    print(f"        (original error: {e})")

print("\n=== wrong password still rejected ===")
ok, err, _ = attempt("WrongPassword", BAD_PW)
check("rejected", not ok, err)

print("\n=== Microsoft 365 style: LOGIN only, no PLAIN ===")
ok, err, log = attempt(BAD_PW, BAD_PW, mechs=b"AUTH LOGIN XOAUTH2")
check("falls back to AUTH LOGIN and authenticates", ok, err)
check("password arrived intact over AUTH LOGIN", log.get("password") == BAD_PW, repr(log.get("password")))

print("\n=== server with no usable password mechanism ===")
ok, err, _ = attempt(BAD_PW, BAD_PW, mechs=b"AUTH XOAUTH2")
check("clear SMTPNotSupportedError, not a crash",
      (not ok) and "non-ASCII" in err, err)

print("\n=== _smtp_auth picks the right branch ===")
check("ascii password -> smtplib.login()", login._is_ascii("PlainAscii123"))
check("non-ascii password -> utf8 path", not login._is_ascii(BAD_PW))

print("\n=== error classification (the misleading 'could not connect') ===")
for msg, expect in [("[Errno 61] Connection refused", True),
                    ("timed out", True),
                    ("[SSL: CERTIFICATE_VERIFY_FAILED]", True),
                    ("'ascii' codec can't encode character '\\uff01' in position 18", False),
                    ("(535, b'5.7.8 bad creds')", False)]:
    got = login._looks_like_connection_error(msg)
    check(f"connection-error={got!s:<5} for {msg[:46]!r}", got == expect)

print("\n=== 5.7.139 means two different things — don't conflate them ===")
import smtplib
def disabled_for(text):
    try:
        raise smtplib.SMTPAuthenticationError(535, text.encode())
    except smtplib.SMTPAuthenticationError as e:
        msg = str(e).lower()
        return ("disabled" in msg or "blocked" in msg) and ("auth" in msg or "tenant" in msg or "basic" in msg)
cases = [
    ("5.7.139 Authentication unsuccessful, the user credentials were incorrect.", False),
    ("5.7.139 Authentication unsuccessful, SmtpClientAuthentication is disabled for the Tenant.", True),
    ("5.7.139 Authentication unsuccessful, basic authentication is disabled.", True),
    ("5.7.3 Authentication unsuccessful", False),
]
for text, expect in cases:
    got = disabled_for(text)
    check(f"tenant-disabled={got!s:<5} for {text[:56]!r}", got == expect)

print("\n=== the hint the user now sees ===")
print("  ", login._describe_non_ascii(BAD_PW))
print("  ", login._describe_non_ascii("pass；word"))
check("no hint for a clean ascii password", login._describe_non_ascii("all-ascii") == "")

print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
