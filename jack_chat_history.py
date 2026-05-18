"""Per-user chat-history persistence for Jack GPT (Postgres backend).

Mirrors `chat_history.py` (Jerry's persistence layer) but targets a SEPARATE
Postgres instance via a SEPARATE secret and uses a SEPARATE table so the
two surfaces never share rows. Jack is jhsun-only so the user_email column
is effectively always `jhsun@streamax.com`, but the column is kept for
schema symmetry with Jerry's table.

Configuration:
    Set `JACK_GPT_DB_URL` in st.secrets (or env) to a Postgres connection
    string. Supabase: Project Settings → Database → Connection string →
    URI ("Pooler" / "Transaction" variant on port 6543 for serverless).

    There is NO fallback to `JERRY_GPT_DB_URL` — if Jack's URL is absent
    or psycopg2 isn't installed, persistence is silently disabled and
    chat still works (per-tab only). This matches the dedicated-API-key
    policy: Jack and Jerry are isolated for cost / quota / blast radius.

Failure handling:
    Every operation has its own try/except. DB failures NEVER break the
    user's chat — they print `[JACK_GPT_DB_ERROR]` to stderr and return
    empty/no-op.
"""
from __future__ import annotations

import os
import sys
import uuid

import streamlit as st

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    _PG_AVAILABLE = True
except ImportError:
    _PG_AVAILABLE = False
    psycopg2 = None  # type: ignore


MAX_HISTORY_LOAD = 50


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def _get_db_url() -> str | None:
    try:
        url = st.secrets.get("JACK_GPT_DB_URL")
        if url:
            return str(url)
    except Exception:
        pass
    return os.environ.get("JACK_GPT_DB_URL")


def is_configured() -> bool:
    """True if both psycopg2 is installed and JACK_GPT_DB_URL is set."""
    return _PG_AVAILABLE and bool(_get_db_url())


@st.cache_resource(show_spinner=False)
def _get_connection():
    """One Postgres connection per Streamlit process. Auto-creates schema
    on first call. Returns None if not configured or connect fails.
    """
    if not _PG_AVAILABLE:
        return None
    url = _get_db_url()
    if not url:
        return None
    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        conn.autocommit = True
        _init_schema(conn)
        return conn
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] connect failed: {type(e).__name__}: {e}",
              file=sys.stderr, flush=True)
        return None


def _init_schema(conn) -> None:
    """Idempotent — safe to call on every connect.

    Table name `jack_gpt_chats` is intentionally distinct from Jerry's
    `jerry_gpt_chats` so the two surfaces stay separable even when
    pointed at the same physical Postgres instance.
    """
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jack_gpt_chats (
                id BIGSERIAL PRIMARY KEY,
                user_email TEXT NOT NULL,
                user_name TEXT,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                model TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cache_read_tokens INTEGER DEFAULT 0,
                cache_creation_tokens INTEGER DEFAULT 0,
                cost_usd NUMERIC(12, 6) DEFAULT 0,
                session_id TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_jack_user_session
                ON jack_gpt_chats(user_email, session_id, created_at);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_jack_user_recent
                ON jack_gpt_chats(user_email, created_at DESC);
        """)


def _retry_get_connection():
    """Drop the cached connection and try again — used when a query fails
    because the connection went stale (Supabase poolers recycle idle conns)."""
    try:
        _get_connection.clear()
    except Exception:
        pass
    return _get_connection()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def new_session_id() -> str:
    """Generate a fresh session identifier."""
    return f"sess_{uuid.uuid4().hex[:16]}"


def load_recent_session(user_email: str) -> tuple[list[dict], str | None]:
    """Return (history, session_id) for the user's most recent conversation.

    `history` is a list of {"role": "user"|"assistant", "content": str}
    dicts in chronological order, ready to drop into
    `st.session_state["jack_gpt_history"]`. Returns ([], None) if there's
    no history yet, the DB isn't configured, or anything fails.
    """
    if not user_email or not is_configured():
        return [], None
    conn = _get_connection()
    if conn is None:
        return [], None
    try:
        return _load_recent_session_inner(conn, user_email)
    except psycopg2.OperationalError:
        conn = _retry_get_connection()
        if conn is None:
            return [], None
        try:
            return _load_recent_session_inner(conn, user_email)
        except Exception as e:
            print(f"[JACK_GPT_DB_ERROR] load (retry) failed: "
                  f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
            return [], None
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] load failed: {type(e).__name__}: {e}",
              file=sys.stderr, flush=True)
        return [], None


def _load_recent_session_inner(conn, user_email: str) -> tuple[list[dict], str | None]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT session_id FROM jack_gpt_chats
            WHERE user_email = %s
            ORDER BY created_at DESC LIMIT 1
            """,
            (user_email,),
        )
        row = cur.fetchone()
        if not row:
            return [], None
        session_id = row["session_id"]

        cur.execute(
            """
            SELECT role, content FROM jack_gpt_chats
            WHERE user_email = %s AND session_id = %s
            ORDER BY created_at ASC, id ASC
            LIMIT %s
            """,
            (user_email, session_id, MAX_HISTORY_LOAD),
        )
        rows = cur.fetchall()
    history = [{"role": r["role"], "content": r["content"]} for r in rows]
    return history, session_id


def save_turn(
    user_email: str,
    user_name: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    cost_usd: float = 0.0,
) -> bool:
    """Persist a user message + assistant response pair. Returns True on success.

    Two rows inserted in a single transaction so a partial save can't leave
    the conversation in an inconsistent state. Token counts and cost are
    attached to the assistant row only.
    """
    if not (user_email and session_id and is_configured()):
        return False
    conn = _get_connection()
    if conn is None:
        return False
    try:
        return _save_turn_inner(
            conn, user_email, user_name, session_id,
            user_message, assistant_message, model,
            input_tokens, output_tokens, cache_read_tokens,
            cache_creation_tokens, cost_usd,
        )
    except psycopg2.OperationalError:
        conn = _retry_get_connection()
        if conn is None:
            return False
        try:
            return _save_turn_inner(
                conn, user_email, user_name, session_id,
                user_message, assistant_message, model,
                input_tokens, output_tokens, cache_read_tokens,
                cache_creation_tokens, cost_usd,
            )
        except Exception as e:
            print(f"[JACK_GPT_DB_ERROR] save (retry) failed: "
                  f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
            return False
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] save failed: {type(e).__name__}: {e}",
              file=sys.stderr, flush=True)
        return False


def _save_turn_inner(
    conn, user_email, user_name, session_id,
    user_message, assistant_message, model,
    input_tokens, output_tokens, cache_read_tokens,
    cache_creation_tokens, cost_usd,
) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO jack_gpt_chats
                (user_email, user_name, role, content, model,
                 input_tokens, output_tokens, cache_read_tokens,
                 cache_creation_tokens, cost_usd, session_id)
            VALUES
                (%s, %s, 'user', %s, NULL,
                 0, 0, 0, 0, 0, %s),
                (%s, %s, 'assistant', %s, %s,
                 %s, %s, %s, %s, %s, %s)
            """,
            (
                user_email, user_name, user_message, session_id,
                user_email, user_name, assistant_message, model,
                input_tokens, output_tokens, cache_read_tokens,
                cache_creation_tokens, cost_usd, session_id,
            ),
        )
    return True


def load_session_by_id(user_email: str, session_id: str) -> list[dict]:
    """Return the full message history for ONE specific past session."""
    if not (user_email and session_id and is_configured()):
        return []
    conn = _get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT role, content FROM jack_gpt_chats
                WHERE user_email = %s AND session_id = %s
                ORDER BY created_at ASC, id ASC
                LIMIT %s
                """,
                (user_email, session_id, MAX_HISTORY_LOAD),
            )
            rows = cur.fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] load_session_by_id failed: "
              f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return []


def delete_session(user_email: str, session_id: str) -> bool:
    """Delete one specific session belonging to one user. Scoped by both
    user_email AND session_id."""
    if not (user_email and session_id and is_configured()):
        return False
    conn = _get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM jack_gpt_chats WHERE user_email = %s AND session_id = %s",
                (user_email, session_id),
            )
        return True
    except psycopg2.OperationalError:
        conn = _retry_get_connection()
        if conn is None:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM jack_gpt_chats WHERE user_email = %s AND session_id = %s",
                    (user_email, session_id),
                )
            return True
        except Exception as e:
            print(f"[JACK_GPT_DB_ERROR] delete_session (retry) failed: "
                  f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
            return False
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] delete_session failed: "
              f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return False


def delete_all_sessions(user_email: str) -> bool:
    """Delete ALL sessions belonging to one user. Destructive — use with
    explicit user confirmation in the UI."""
    if not (user_email and is_configured()):
        return False
    conn = _get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM jack_gpt_chats WHERE user_email = %s",
                (user_email,),
            )
        return True
    except psycopg2.OperationalError:
        conn = _retry_get_connection()
        if conn is None:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM jack_gpt_chats WHERE user_email = %s",
                    (user_email,),
                )
            return True
        except Exception as e:
            print(f"[JACK_GPT_DB_ERROR] delete_all (retry) failed: "
                  f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
            return False
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] delete_all failed: "
              f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return False


def list_past_sessions(user_email: str, limit: int = 20) -> list[dict]:
    """Summaries of the user's past sessions, most recent first.

    Each row: {session_id, started_at, message_count, first_question}.
    """
    if not (user_email and is_configured()):
        return []
    conn = _get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    session_id,
                    MIN(created_at) AS started_at,
                    COUNT(*) AS message_count,
                    (SELECT content FROM jack_gpt_chats inner_c
                     WHERE inner_c.session_id = outer_c.session_id
                       AND inner_c.role = 'user'
                       AND inner_c.user_email = %s
                     ORDER BY created_at ASC LIMIT 1) AS first_question
                FROM jack_gpt_chats outer_c
                WHERE user_email = %s
                GROUP BY session_id
                ORDER BY MIN(created_at) DESC
                LIMIT %s
                """,
                (user_email, user_email, limit),
            )
            return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[JACK_GPT_DB_ERROR] list_past_sessions failed: "
              f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return []
