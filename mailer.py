"""Drip Mailer engine — signatures, merge rendering, and SMTP batch sending.

Ported from the standalone Streamlit app at `~/Desktop/Streamax/Sales Toolkit/
auto email/app.py`, which the toolkit's Email Tool tab used to link out to. This
module is the pure-Python half: no Streamlit, no FastAPI, no globals — so the
same code renders the on-screen preview and builds the message that actually
goes out. That parity is the point; a preview that isn't byte-identical to the
sent mail is worse than no preview.

Credentials are never persisted. They arrive on the request that uses them, live
in a local variable for the duration of the send, and are gone when it returns.

Improvements over the original, all of which exist because this is now a
company-wide tool rather than one person's script:
  * Sends via Coremail **or** Outlook — `connect()` walks the same backend list
    `login.py` authenticates against, instead of hardcoding mail.streamax.com.
  * Non-ASCII passwords work (a full-width ！ from a Chinese IME would otherwise
    raise UnicodeEncodeError before anything left the process — see login.py).
  * Recipients are de-duplicated and syntactically validated before the run.
  * MAX_RECIPIENTS backstop so a malformed CSV can't fire thousands of mails.
"""
from __future__ import annotations

import csv
import io
import re
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid, parseaddr

import login as _login

# A single run is capped. The original had no limit at all, so one bad CSV
# could have emptied a mailbox reputation in a minute.
MAX_RECIPIENTS = 500
MIN_DELAY_S = 0.3
DEFAULT_DELAY_S = 1.0

REQUIRED_COLUMNS = ("email", "first_name", "last_name", "company", "role")

CSV_TEMPLATE = (
    "Email,First_Name,Last_Name,Company,Role\n"
    "john.doe@acme.com,John,Doe,Acme Logistics,Fleet Manager\n"
)

SIGNATURE_LAYOUTS = ("Minimalist Professional", "Creative with Avatar", "Corporate with Logo")

DEFAULT_BODY = """Hi {first_name},

I noticed {company} runs a commercial fleet, and most operators we speak to are
carrying the same three costs without much visibility into them: fuel, accident
claims, and insurance premiums.

Streamax puts a camera and AI layer on the vehicle that turns those from
after-the-fact surprises into things you can see and act on the same day.

Worth a short call to see whether the numbers hold up for a fleet your size?

Best regards,"""

# Kept verbatim from the original tool — legal wording, not ours to reword.
DISCLAIMER_HTML = (
    '<div style="margin-top: 25px; padding-top: 15px; border-top: 1px solid #e2e8f0; '
    'font-family: Arial, sans-serif; font-size: 10px; color: #64748b; line-height: 1.4; '
    'text-align: justify;">'
    '<strong>Email Disclaimer:</strong> This e-mail is intended only for the person or entity '
    'to which it is addressed and may contain confidential and/or privileged material. Any '
    'review, retransmission, dissemination or other use of, or taking of any action in reliance '
    'upon, the information in this e-mail by persons or entities other than the intended '
    'recipient is prohibited and may be unlawful. If you received this e-mail in error, please '
    'contact the sender and delete it from any computer.'
    '</div>'
)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ── signatures ──────────────────────────────────────────────────────────────

def _esc(v) -> str:
    return (str(v or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _join(*parts: str, sep: str = " | ") -> str:
    """Join only the parts that have content, so an empty phone or website
    doesn't leave a dangling ' | ' in a signature a customer will read."""
    return sep.join(p for p in parts if p and p.strip())


def signature_html(layout: str, d: dict) -> str:
    """Render one of the three signature layouts. Values are HTML-escaped —
    the original interpolated them raw, so a name containing `<` produced
    broken markup in every mail of the batch."""
    name, title = _esc(d.get("name")), _esc(d.get("title"))
    company, phone = _esc(d.get("company")), _esc(d.get("phone"))
    email, website = _esc(d.get("email")), _esc(d.get("website"))
    avatar, logo = _esc(d.get("avatarUrl")), _esc(d.get("logoUrl"))

    if layout == "Creative with Avatar":
        body = (
            '<div style="font-family: \'Helvetica Neue\', Helvetica, Arial, sans-serif; '
            'margin-top: 20px; display: flex; align-items: center; gap: 15px;">'
            f'<img src="{avatar}" alt="" style="width: 60px; height: 60px; border-radius: 50%; '
            'object-fit: cover; border: 2px solid #e2e8f0;" /><div>'
            f'<p style="margin: 0; font-weight: 600; font-size: 15px; color: #1e293b;">{name}</p>'
            f'<p style="margin: 2px 0; font-size: 13px; color: #64748b;">{title}</p>'
            '<p style="margin: 2px 0; font-size: 13px; color: #3b82f6;">'
            + _join(email, f'<span style="color: #64748b;">{phone}</span>' if phone else '',
                    sep=' <span style="color: #94a3b8;">|</span> ')
            + '</p>'
            + (f'<a href="{website}" style="margin: 0; font-size: 13px; color: #3b82f6; '
               f'text-decoration: none;">{company}</a>' if company else '')
            + '</div></div>'
        )
    elif layout == "Corporate with Logo":
        body = (
            '<div style="font-family: Arial, sans-serif; margin-top: 25px;">'
            f'<p style="margin: 0; font-weight: bold; font-size: 14px; color: #0f172a;">{name}</p>'
            f'<p style="margin: 2px 0 5px 0; font-size: 12px; color: #475569;">{title}</p>'
            f'<p style="margin: 0; font-size: 12px; color: #AACD06;"><strong>'
            f'<a href="{website}" style="color: #AACD06; text-decoration: none;">{company}</a>'
            '</strong></p>'
            '<p style="margin: 4px 0 12px 0; font-size: 12px; color: #475569;">'
            + _join(f'<a href="mailto:{email}" style="color: #AACD06; text-decoration: none;">'
                    f'{email}</a>' if email else '', phone)
            + '</p>'
            + (f'<img src="{logo}" alt="" style="height: 45px; border-radius: 4px;" />' if logo else '')
            + '</div>'
        )
    else:  # Minimalist Professional
        body = (
            '<div style="font-family: Arial, sans-serif; color: #333; margin-top: 20px; '
            'border-top: 1px solid #eee; padding-top: 15px;">'
            f'<p style="margin: 0; font-weight: bold; font-size: 14px; color: #000000;">{name}</p>'
            '<p style="margin: 0; font-size: 12px; color: #666;">'
            + _join(title, f'<a href="{website}" style="color: #666; text-decoration: none;">'
                           f'{company}</a>' if company else '')
            + '</p><p style="margin: 0; font-size: 12px; color: #0066cc;">'
            + _join(email, phone) + '</p></div>'
        )
    return body + DISCLAIMER_HTML


# ── merge fields ────────────────────────────────────────────────────────────

def render_template(template: str, row: dict) -> str:
    """Substitute {first_name}-style merge fields, case-insensitively.

    An unresolved field renders as [first_name] rather than vanishing, so a
    gap in the CSV is glaringly obvious in the preview instead of shipping a
    sentence with a hole in it.
    """
    def sub(m):
        key = m.group(1).strip().lower()
        val = row.get(key, "")
        val = "" if val is None else str(val).strip()
        return val if val else f"[{m.group(1).strip()}]"
    return re.sub(r"\{([^}]+)\}", sub, template or "")


def build_html_body(body_template: str, row: dict, sig_html: str) -> str:
    rendered = render_template(body_template, row)
    return rendered.replace("\n", "<br>") + "<br><br>" + sig_html


# ── recipients ──────────────────────────────────────────────────────────────

def parse_recipients(csv_text: str) -> tuple[list[dict], list[str]]:
    """Parse the uploaded CSV. Returns (rows, problems).

    Columns are lower-cased so `Email`/`email`/`EMAIL` all work. Rows without a
    syntactically valid address are dropped and reported rather than silently
    skipped mid-send.
    """
    problems: list[str] = []
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        raw = list(reader)
    except Exception as exc:                                         # noqa: BLE001
        return [], [f"Could not read the CSV: {exc}"]
    if not raw:
        return [], ["The CSV has no data rows."]

    fields = {(f or "").strip().lower() for f in (reader.fieldnames or [])}
    missing = [c for c in REQUIRED_COLUMNS if c not in fields]
    if missing:
        return [], [f"Missing required column(s): {', '.join(missing)}"]

    rows, seen = [], set()
    for i, r in enumerate(raw, start=2):          # row 1 is the header
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items() if k}
        addr = parseaddr(row.get("email", ""))[1].strip()
        if not addr:
            problems.append(f"Row {i}: no email address — skipped")
            continue
        if not _EMAIL_RE.match(addr):
            problems.append(f"Row {i}: '{addr}' is not a valid address — skipped")
            continue
        key = addr.lower()
        if key in seen:
            problems.append(f"Row {i}: duplicate of {addr} — skipped")
            continue
        seen.add(key)
        row["email"] = addr
        rows.append(row)

    if len(rows) > MAX_RECIPIENTS:
        problems.append(
            f"{len(rows)} recipients exceeds the {MAX_RECIPIENTS}-per-run limit. "
            f"Split the list and run it in batches.")
        return [], problems
    return rows, problems


# ── SMTP ────────────────────────────────────────────────────────────────────

def connect(email: str, password: str, timeout: int = 30):
    """Open an authenticated SMTP session, trying the same backends login.py
    accepts (Coremail, then Microsoft). Returns (server, backend_label).

    Raises RuntimeError with a readable message if none accept the credentials.
    """
    errors = []
    for srv in _login._mail_servers():
        server = None
        try:
            ctx = ssl.create_default_context()
            if srv["mode"] == "ssl":
                server = smtplib.SMTP_SSL(srv["host"], srv["port"], timeout=timeout, context=ctx)
            else:
                server = smtplib.SMTP(srv["host"], srv["port"], timeout=timeout)
                server.ehlo()
                server.starttls(context=ctx)
                server.ehlo()
            # smtplib hardcodes ASCII for credentials; login._auth_utf8 handles
            # the rest (RFC 4616 says PLAIN is UTF-8).
            if _login._is_ascii(password):
                server.login(email, password)
            else:
                _login._auth_utf8(server, email, password)
            return server, srv["label"]
        except Exception as exc:                                     # noqa: BLE001
            errors.append(f"{srv['label']}: {exc}")
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    pass
    raise RuntimeError("Could not sign in to any Streamax mail server. " + " | ".join(errors))


def build_message(subject: str, html_body: str, to_addr: str,
                  from_name: str, from_email: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((from_name or from_email, from_email))
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=from_email.split("@")[-1])
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    return msg


def send_batch(*, email: str, password: str, from_name: str,
               subject_template: str, body_template: str, sig_html: str,
               rows: list[dict], delay_s: float = DEFAULT_DELAY_S):
    """Generator yielding one progress dict per recipient, then a final summary.

    A generator so the caller can stream results to the browser as they happen
    — a 200-recipient run takes minutes and a silent progress bar is the thing
    people kill halfway through.
    """
    delay_s = max(MIN_DELAY_S, float(delay_s or DEFAULT_DELAY_S))
    try:
        server, backend = connect(email, password)
    except Exception as exc:                                         # noqa: BLE001
        yield {"type": "fatal", "message": str(exc)}
        return

    yield {"type": "connected", "backend": backend, "total": len(rows)}
    sent = failed = 0
    try:
        for i, row in enumerate(rows, start=1):
            to_addr = row["email"]
            try:
                msg = build_message(
                    render_template(subject_template, row),
                    build_html_body(body_template, row, sig_html),
                    to_addr, from_name, email,
                )
                server.send_message(msg)
                sent += 1
                yield {"type": "sent", "index": i, "email": to_addr, "ok": True}
            except Exception as exc:                                 # noqa: BLE001
                failed += 1
                yield {"type": "sent", "index": i, "email": to_addr,
                       "ok": False, "error": str(exc)[:200]}
            if i < len(rows):
                time.sleep(delay_s)
    finally:
        try:
            server.quit()
        except Exception:
            pass
    yield {"type": "done", "sent": sent, "failed": failed, "total": len(rows)}
