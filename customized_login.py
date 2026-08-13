"""Override credentials — a fallback for people the mail servers can't authenticate.

Why this exists
---------------
`login.py` proves identity by doing an SMTP AUTH against Coremail or Microsoft.
That fails for perfectly legitimate users: mailboxes on an M365 tenant that
blocks basic auth, contractors and partners without a Streamax mailbox, or
anyone mid-migration. This module is the escape hatch.

**It is only ever consulted after BOTH mail backends have refused.** A real
mailbox password always wins, so adding someone here can never weaken or
shadow their normal sign-in.

Passwords are never stored in the clear
---------------------------------------
Entries hold a PBKDF2-HMAC-SHA256 hash (stdlib, 240k iterations, per-user salt).
The plaintext exists only for the moment it takes to verify it. This repo is on
GitHub and has already needed one credential clean-up, so a literal password in
a tracked file is not an option — `scripts/custom_login.py` generates the hash
lines to paste into `SEED_HASHES` below.

Where the passwords live
------------------------
Two layers, because Render's filesystem is ephemeral and a password change has
to survive the next deploy:

* `SEED_HASHES` (this file) — the baseline list, committed. Safe: hashes only.
* A `custom_login` table in the Postgres already configured for chat history
  (`JERRY_GPT_DB_URL`). Anything set at runtime lands here and **overrides the
  seed**. Without a database the store falls back to a local JSON file and logs
  a warning that changes will not survive a redeploy — a real limitation, not a
  silent one.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from pathlib import Path

try:
    import psycopg2
except Exception:                                                    # noqa: BLE001
    psycopg2 = None                                                  # type: ignore

_LOCAL_STORE = Path(__file__).parent / "customized_login_store.json"

_ITERATIONS = 240_000
_MIN_PASSWORD = 8


# ── the list ────────────────────────────────────────────────────────────────
# email -> PBKDF2 hash. Generate a line with:
#     python3 scripts/custom_login.py set someone@streamax.com
#
# An email listed with an empty hash is *allowed* but cannot sign in until a
# password is set — useful for pre-authorising someone before you've agreed a
# password with them.
SEED_HASHES: dict[str, str] = {
    # "partner@example.com": "pbkdf2$240000$<salt>$<hash>",
    #
    # ⚠️ lucian's seed password is "12345678" — one of the most-guessed passwords
    # in existence. PBKDF2 stops a rainbow-table lookup, but not someone trying
    # the obvious list. Have him change it on /account at first sign-in.
    "lucian@streamax.com": "pbkdf2$240000$16ff0ac86b49b2b215c57412ae8e7dca$c63d0c9eec37690a409b595ed634e8f4975a4b1ccb7e7cd27c894ba8d71d6eef",
}


def _log(msg: str) -> None:
    print(f"[CUSTOMLOGIN] {msg}", file=sys.stderr, flush=True)


# ── hashing ─────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"pbkdf2${_ITERATIONS}${salt.hex()}${dk.hex()}"


def _check(password: str, stored: str) -> bool:
    try:
        algo, iters, salt_hex, hash_hex = (stored or "").split("$")
        if algo != "pbkdf2":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 bytes.fromhex(salt_hex), int(iters))
    except Exception:                                                # noqa: BLE001
        return False
    return hmac.compare_digest(dk.hex(), hash_hex)


def validate_new_password(password: str) -> str:
    """Return an error message, or '' if the password is acceptable."""
    if len(password or "") < _MIN_PASSWORD:
        return f"Password must be at least {_MIN_PASSWORD} characters."
    if password.strip() != password:
        return "Password cannot start or end with a space."
    return ""


# ── storage ─────────────────────────────────────────────────────────────────

def _db_url() -> str | None:
    url = os.environ.get("JERRY_GPT_DB_URL", "").strip()
    if url:
        return url
    try:
        import streamlit as st
        v = st.secrets.get("JERRY_GPT_DB_URL")
        return v.strip() if isinstance(v, str) and v.strip() else None
    except Exception:                                                # noqa: BLE001
        return None


def _db():
    url = _db_url()
    if not url or psycopg2 is None:
        return None
    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        with conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS custom_login (
                    email      TEXT PRIMARY KEY,
                    pw_hash    TEXT NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        return conn
    except Exception as exc:                                         # noqa: BLE001
        _log(f"database unavailable ({exc}) — falling back to the local file")
        return None


def _load_local() -> dict:
    if not _LOCAL_STORE.is_file():
        return {}
    try:
        d = json.loads(_LOCAL_STORE.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:                                                # noqa: BLE001
        return {}


def _save_local(data: dict) -> None:
    _LOCAL_STORE.write_text(json.dumps(data, indent=1), encoding="utf-8")
    try:
        os.chmod(_LOCAL_STORE, 0o600)
    except Exception:                                                # noqa: BLE001
        pass


def _overrides() -> dict:
    """Runtime-set hashes, which take precedence over SEED_HASHES."""
    conn = _db()
    if conn is None:
        return _load_local()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT email, pw_hash FROM custom_login")
            return {e.strip().lower(): h for e, h in cur.fetchall()}
    except Exception as exc:                                         # noqa: BLE001
        _log(f"read failed ({exc})")
        return {}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def storage_backend() -> str:
    return "database" if _db_url() and psycopg2 is not None else "local file"


# ── public API ──────────────────────────────────────────────────────────────

def _seed() -> dict:
    return {e.strip().lower(): h for e, h in SEED_HASHES.items() if e and e.strip()}


def all_emails() -> list[str]:
    """Every address the override list knows about."""
    return sorted(set(_seed()) | set(_overrides()))


def is_custom_user(email: str) -> bool:
    """Is this address on the override list at all?"""
    return (email or "").strip().lower() in set(all_emails())


def verify(email: str, password: str) -> bool:
    """Check an override password. Runtime overrides beat the committed seed."""
    e = (email or "").strip().lower()
    if not e or not password:
        return False
    stored = _overrides().get(e) or _seed().get(e) or ""
    if not stored:
        return False                    # listed but no password set yet
    ok = _check(password, stored)
    _log(f"override auth for {e}: {'ok' if ok else 'rejected'}")
    return ok


def set_password(email: str, new_password: str) -> tuple[bool, str]:
    """Change an override password. Returns (ok, message-or-hash)."""
    e = (email or "").strip().lower()
    if not is_custom_user(e):
        return False, "This account is not on the override list."
    err = validate_new_password(new_password)
    if err:
        return False, err

    pw_hash = hash_password(new_password)
    conn = _db()
    if conn is not None:
        try:
            with conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO custom_login (email, pw_hash, updated_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (email)
                    DO UPDATE SET pw_hash = EXCLUDED.pw_hash, updated_at = NOW()
                """, (e, pw_hash))
            _log(f"password updated for {e} (database)")
            return True, pw_hash
        except Exception as exc:                                     # noqa: BLE001
            _log(f"database write failed ({exc}) — using the local file")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    data = _load_local()
    data[e] = pw_hash
    _save_local(data)
    _log(f"password updated for {e} (local file — will NOT survive a redeploy)")
    return True, pw_hash
