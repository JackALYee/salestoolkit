"""One-off: move the Google Sheet's Jerry log into Postgres, behind /jerrylog.

    python3 scripts/migrate_sheet_to_portal.py --dry-run
    python3 scripts/migrate_sheet_to_portal.py

Idempotent — re-running inserts nothing twice.

Why a migration is needed at all, when both sinks were written by the same
code: they diverged in both directions.

  * The Sheet holds turns Postgres lost. `save_turn` retries a stale pooled
    connection exactly once; when the retry also failed the turn was dropped,
    and only the Sheet has it.
  * Postgres holds turns the Sheet no longer has, because rows were deleted
    from the Sheet by hand, and because Postgres logging started earlier.
  * The Sheet carried two fields Postgres never had: `is_leadership` and
    `sensitive_flagged`.

So this backfills the two columns for every existing row and inserts only the
turns that exist solely in the Sheet.

The sheet tab is `queries`, NOT the first tab — exporting without `&sheet=`
returns an empty file and looks like an access problem.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# login.py and usage_logger.py both import streamlit. Stub it, exactly as
# server.py does, so this runs as a plain script.
import types                                                        # noqa: E402

_st = types.ModuleType("streamlit")
_st.session_state = {}
_st.secrets = {}
for _n in ("cache_resource", "cache_data"):
    setattr(_st, _n, lambda *a, **k: (lambda f: f))
sys.modules.setdefault("streamlit", _st)

try:
    import psycopg2
except ImportError:
    sys.exit("psycopg2 is required:  pip install psycopg2-binary")

SHEET_ID = os.environ.get("JERRY_GPT_SHEET_ID",
                          "1F5V5NYfY8sFa1juk_aDWMbTM3PQ8Nth4pXkAh3pr2GM")
SHEET_TAB = os.environ.get("JERRY_GPT_SHEET_TAB", "queries")
CSV_URL = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
           f"/gviz/tq?tqx=out:csv&sheet={SHEET_TAB}")


def db_url() -> str:
    u = os.environ.get("JERRY_GPT_DB_URL", "").strip()
    if not u:
        sys.exit("JERRY_GPT_DB_URL is not set.")
    return u


def norm(s: str) -> str:
    """Match key. Whitespace-collapsed and truncated, because the Sheet wraps
    long cells and the two stores do not agree on trailing whitespace."""
    return " ".join((s or "").split())[:400]


def fetch_sheet() -> list[dict]:
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "jerrylog-migrate"})
    raw = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
    if len(raw) < 200:
        sys.exit(f"Sheet export returned {len(raw)} bytes — is the tab still "
                 f"called {SHEET_TAB!r}?")
    return list(csv.DictReader(io.StringIO(raw)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    import login as _login
    import usage_logger as _usage

    rows = fetch_sheet()
    print(f"Sheet    : {len(rows)} rows from tab {SHEET_TAB!r}")

    conn = psycopg2.connect(db_url(), connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("""
        ALTER TABLE jerry_gpt_chats
            ADD COLUMN IF NOT EXISTS is_leadership BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS sensitive_flagged BOOLEAN DEFAULT FALSE;
    """)
    print("Schema   : is_leadership + sensitive_flagged present")

    cur.execute("SELECT id, user_email, role, content FROM jerry_gpt_chats")
    existing = cur.fetchall()
    have = {norm(c) for _id, _e, r, c in existing if r == "user"}
    print(f"Postgres : {len(existing)} rows, {len(have)} distinct questions")

    # ---- backfill the two columns on rows already here ---------------------
    sheet_sensitive = {norm(r["question"]): (r.get("sensitive_flagged") or "").upper() == "TRUE"
                       for r in rows if r.get("question")}
    lead_updates, sens_updates = [], []
    for rid, email, role, content in existing:
        lead = bool(_login.resolve_leadership(email or ""))
        lead_updates.append((lead, rid))
        if role == "user":
            key = norm(content)
            flag = sheet_sensitive.get(key)
            if flag is None:                      # not in the Sheet — recompute
                flag = bool(_usage._is_pricing_sensitive(content or ""))
            sens_updates.append((flag, rid))

    # ---- turns that exist ONLY in the Sheet --------------------------------
    missing = [r for r in rows if r.get("question") and norm(r["question"]) not in have]
    print(f"Backfill : {len(lead_updates)} rows get is_leadership, "
          f"{len(sens_updates)} get sensitive_flagged")
    print(f"Insert   : {len(missing)} turns exist only in the Sheet")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        for r in missing[:5]:
            print(f"  would insert {r['timestamp_cn'][:19]}  {r['user_email']:28s} "
                  f"{norm(r['question'])[:52]}")
        conn.rollback()
        return 0

    cur.executemany("UPDATE jerry_gpt_chats SET is_leadership=%s WHERE id=%s",
                    lead_updates)
    cur.executemany("UPDATE jerry_gpt_chats SET sensitive_flagged=%s WHERE id=%s",
                    sens_updates)

    def num(v, cast=int):
        try:
            return cast(v)
        except (TypeError, ValueError):
            return cast(0)

    inserted = 0
    for r in missing:
        lead = (r.get("is_leadership") or "").upper() == "TRUE"
        sens = (r.get("sensitive_flagged") or "").upper() == "TRUE"
        email = r.get("user_email") or r.get("user_name") or "unknown"
        # A synthetic session id, marked so the portal can show these as
        # recovered rather than pretending they were normal sessions.
        sid = f"sheet_{r.get('timestamp_cn','')[:19].replace(':','').replace('-','')}"
        cur.execute("""
            INSERT INTO jerry_gpt_chats
                (user_email, user_name, role, content, model, length,
                 input_tokens, output_tokens, cache_read_tokens,
                 cache_creation_tokens, cost_usd, session_id,
                 is_leadership, sensitive_flagged, created_at)
            VALUES
                (%s, %s, 'user', %s, NULL, %s, 0,0,0,0,0, %s, %s, %s, %s),
                (%s, %s, 'assistant', %s, %s, %s, %s,%s,%s,%s, %s, %s, %s, %s, %s)
        """, (
            email, r.get("user_name") or email, r["question"], r.get("length") or "",
            sid, lead, sens, r.get("timestamp_cn") or None,
            email, r.get("user_name") or email, r.get("answer") or "",
            r.get("model") or "", r.get("length") or "",
            num(r.get("input_tokens")), num(r.get("output_tokens")),
            num(r.get("cache_read_tokens")), num(r.get("cache_creation_tokens")),
            num(r.get("cost_usd"), float), sid, lead, sens,
            r.get("timestamp_cn") or None,
        ))
        inserted += 1

    conn.commit()
    print(f"\nDone. Inserted {inserted} recovered turns; "
          f"backfilled {len(lead_updates)} rows.")
    cur.execute("SELECT COUNT(*) FILTER (WHERE role='user') FROM jerry_gpt_chats")
    print(f"Portal now holds {cur.fetchone()[0]} questions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
