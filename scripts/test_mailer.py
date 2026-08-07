"""Drip Mailer engine tests — rendering, CSV validation, and a real SMTP batch.

Spins up a local SMTP server and sends through it, so `send_batch` is exercised
end to end without touching a real mail host.

    python3 scripts/test_mailer.py
"""
import asyncio, email, pathlib, ssl, sys, threading, types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
_st = types.ModuleType("streamlit"); _st.session_state = {}
class _S:
    def get(self, k, d=None): return None
_st.secrets = _S(); sys.modules["streamlit"] = _st

import login, mailer

fails = 0
def check(label, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"   {detail}"))
    if not cond: fails += 1

print("=== merge fields ===")
row = {"first_name": "Jia", "company": "Acme", "role": "Fleet Manager"}
check("substitutes a field", mailer.render_template("Hi {first_name}", row) == "Hi Jia")
check("case-insensitive", mailer.render_template("Hi {First_Name}", row) == "Hi Jia")
check("missing field is visible, not blank",
      mailer.render_template("Hi {nickname}", row) == "Hi [nickname]")
check("empty value is visible too",
      mailer.render_template("X {a}", {"a": "  "}) == "X [a]")

print("\n=== signatures ===")
sig = {"name": "Jack <Yi>", "title": "PMM", "company": "Streamax", "phone": "1",
       "email": "j@streamax.com", "website": "https://streamax.com",
       "avatarUrl": "", "logoUrl": ""}
for layout in mailer.SIGNATURE_LAYOUTS:
    h = mailer.signature_html(layout, sig)
    check(f"{layout[:24]:24s} renders + disclaimer", "Email Disclaimer" in h and "Streamax" in h)
check("HTML in a name is escaped, not injected",
      "&lt;Yi&gt;" in mailer.signature_html(mailer.SIGNATURE_LAYOUTS[0], sig))

print("\n=== CSV validation ===")
good = "Email,First_Name,Last_Name,Company,Role\na@x.com,A,B,C,D\nb@x.com,E,F,G,H\n"
rows, probs = mailer.parse_recipients(good)
check("parses valid rows", len(rows) == 2 and not probs, f"{rows} {probs}")
rows, probs = mailer.parse_recipients("First_Name\nA\n")
check("rejects a CSV missing columns", not rows and "Missing required column" in probs[0], str(probs))
rows, probs = mailer.parse_recipients(
    "Email,First_Name,Last_Name,Company,Role\na@x.com,A,B,C,D\na@x.com,A,B,C,D\nbroken,E,F,G,H\n,I,J,K,L\n")
check("drops duplicates", len(rows) == 1, str(rows))
check("reports the duplicate", any("duplicate" in p for p in probs), str(probs))
check("reports the invalid address", any("not a valid" in p for p in probs), str(probs))
check("reports the empty address", any("no email" in p for p in probs), str(probs))
big = "Email,First_Name,Last_Name,Company,Role\n" + "".join(
    f"u{i}@x.com,A,B,C,D\n" for i in range(mailer.MAX_RECIPIENTS + 1))
rows, probs = mailer.parse_recipients(big)
check(f"caps a run at {mailer.MAX_RECIPIENTS}", not rows and any("exceeds" in p for p in probs), str(probs[:1]))
check("uppercase headers accepted",
      len(mailer.parse_recipients("EMAIL,FIRST_NAME,LAST_NAME,COMPANY,ROLE\na@x.com,A,B,C,D\n")[0]) == 1)

print("\n=== real SMTP batch through a local server ===")
try:
    from aiosmtpd.controller import Controller
    from aiosmtpd.smtp import AuthResult, LoginPassword
except ImportError:
    print("  SKIP  aiosmtpd not installed (pip install aiosmtpd)")
    print(f"\n{'ALL PASS' if not fails else str(fails)+' FAILED'}")
    sys.exit(1 if fails else 0)

received = []
class Handler:
    async def handle_DATA(self, server, session, envelope):
        received.append(email.message_from_bytes(envelope.content))
        return "250 OK"

def authenticator(server, session, envelope, mechanism, auth_data):
    if isinstance(auth_data, LoginPassword) and auth_data.password == b"pw":
        return AuthResult(success=True)
    return AuthResult(success=False, handled=False)

# aiosmtpd's Controller.start() probes the port it was given, so port=0 fails
# on its own readiness check — pick a concrete free port first.
import socket as _socket
_probe = _socket.socket(); _probe.bind(("127.0.0.1", 0))
port = _probe.getsockname()[1]; _probe.close()

ctrl = Controller(Handler(), hostname="127.0.0.1", port=port,
                  authenticator=authenticator, auth_require_tls=False)
ctrl.start()

# Point the mailer at the local server instead of Streamax.
login._MAIL_SERVERS = ({"label": "local", "host": "127.0.0.1", "port": port, "mode": "plain"},)
_orig_connect = mailer.connect
def local_connect(email_addr, password, timeout=30):
    import smtplib
    s = smtplib.SMTP("127.0.0.1", port, timeout=timeout)
    s.ehlo()
    s.login(email_addr, password)
    return s, "local"
mailer.connect = local_connect

rows, _ = mailer.parse_recipients(
    "Email,First_Name,Last_Name,Company,Role\n"
    "a@x.com,Ann,Lee,Acme,Fleet Manager\nb@x.com,Bo,Ng,Beta,CFO\n")
events = list(mailer.send_batch(
    email="me@streamax.com", password="pw", from_name="Jack",
    subject_template="Hi {first_name} at {company}",
    body_template="Hello {first_name},\nAbout {company}.",
    sig_html=mailer.signature_html("Minimalist Professional", sig),
    rows=rows, delay_s=0.3))
ctrl.stop()

kinds = [e["type"] for e in events]
check("streams connected → sent × N → done",
      kinds[0] == "connected" and kinds.count("sent") == 2 and kinds[-1] == "done", str(kinds))
check("both delivered", len(received) == 2, str(len(received)))
check("summary counts are right", events[-1]["sent"] == 2 and events[-1]["failed"] == 0, str(events[-1]))
if received:
    m0 = received[0]
    check("subject merged", m0["Subject"] == "Hi Ann at Acme", m0["Subject"])
    check("From uses the display name", "Jack" in m0["From"], m0["From"])
    check("has a Message-ID", bool(m0["Message-ID"]))
    body = m0.get_payload(0).get_payload(decode=True).decode("utf-8")
    check("body merged", "Hello Ann," in body and "About Acme." in body, body[:70])
    check("newlines became <br>", "<br>" in body)
    check("signature attached", "Email Disclaimer" in body)
    check("second mail personalised differently",
          "Hi Bo at Beta" == received[1]["Subject"], received[1]["Subject"])

print("\n=== bad credentials fail cleanly, without sending ===")
mailer.connect = _orig_connect
login._MAIL_SERVERS = ({"label": "dead", "host": "127.0.0.1", "port": 1, "mode": "plain"},)
ev = list(mailer.send_batch(email="a@b.com", password="x", from_name="",
                            subject_template="s", body_template="b", sig_html="",
                            rows=rows, delay_s=0.3))
check("yields a single fatal event", len(ev) == 1 and ev[0]["type"] == "fatal", str(ev)[:120])

print(f"\n{'ALL PASS' if not fails else str(fails)+' FAILED'}")
sys.exit(1 if fails else 0)
