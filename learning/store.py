"""Durable learning jobs and knowledge, isolated from Supabase's public API."""
from __future__ import annotations
import hashlib
import json
import os
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import Json, RealDictCursor

CHINA = timezone(timedelta(hours=8))

@contextmanager
def db(timeout=20000):
    conn = psycopg2.connect(os.environ['JERRY_GPT_DB_URL'], connect_timeout=3,
                           options=f'-c statement_timeout={int(timeout)}')
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
    finally:
        conn.close()


def initialize():
    with db() as c:
        c.execute('''
        CREATE SCHEMA IF NOT EXISTS jerry_learning;
        REVOKE ALL ON SCHEMA jerry_learning FROM PUBLIC;
        CREATE TABLE IF NOT EXISTS jerry_learning.settings (
            key TEXT PRIMARY KEY, value JSONB NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT now());
        CREATE TABLE IF NOT EXISTS jerry_learning.runs (
            id UUID PRIMARY KEY, slot TEXT UNIQUE NOT NULL, kind TEXT NOT NULL,
            cutoff TIMESTAMPTZ NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
            owner UUID, lease_until TIMESTAMPTZ, retry_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            failures INT NOT NULL DEFAULT 0, reviewed INT NOT NULL DEFAULT 0,
            accepted INT NOT NULL DEFAULT 0, pending INT NOT NULL DEFAULT 0,
            input_tokens BIGINT NOT NULL DEFAULT 0, output_tokens BIGINT NOT NULL DEFAULT 0,
            searches INT NOT NULL DEFAULT 0, spent_usd NUMERIC NOT NULL DEFAULT 0,
            reserved_usd NUMERIC NOT NULL DEFAULT 0, budget_usd NUMERIC NOT NULL,
            error TEXT NOT NULL DEFAULT '', created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(), finished_at TIMESTAMPTZ);
        CREATE TABLE IF NOT EXISTS jerry_learning.reviews (
            question_id BIGINT PRIMARY KEY, run_id UUID NOT NULL,
            outcome TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
        CREATE TABLE IF NOT EXISTS jerry_learning.knowledge (
            id BIGSERIAL PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL, topic TEXT NOT NULL,
            title TEXT NOT NULL, content TEXT NOT NULL, kind TEXT NOT NULL,
            scope TEXT NOT NULL CHECK(scope IN ('internal','leadership','owner')),
            owner_email TEXT NOT NULL DEFAULT '', status TEXT NOT NULL,
            sources JSONB NOT NULL DEFAULT '[]', question_ids JSONB NOT NULL DEFAULT '[]',
            confidence REAL NOT NULL DEFAULT 0, reason TEXT NOT NULL DEFAULT '',
            run_id UUID NOT NULL, expires_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now());
        CREATE INDEX IF NOT EXISTS jerry_learning_lookup ON jerry_learning.knowledge(status, scope);
        CREATE INDEX IF NOT EXISTS jerry_learning_text ON jerry_learning.knowledge
          USING gin(to_tsvector('simple', title || ' ' || content));
        CREATE TABLE IF NOT EXISTS jerry_learning.audit (
            id BIGSERIAL PRIMARY KEY, knowledge_id BIGINT, action TEXT NOT NULL,
            actor TEXT NOT NULL, detail JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL DEFAULT now());
        CREATE TABLE IF NOT EXISTS jerry_learning.turn_evidence (
            user_email TEXT NOT NULL, session_id TEXT NOT NULL, question_hash TEXT NOT NULL, web_enabled BOOLEAN NOT NULL,
            sources JSONB NOT NULL DEFAULT '[]', created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY(user_email, session_id, question_hash));
        REVOKE ALL ON ALL TABLES IN SCHEMA jerry_learning FROM PUBLIC;
        ''')
        # Explicitly block browser-facing Supabase roles, including future default grants.
        for role in ('anon', 'authenticated'):
            c.execute('SELECT 1 FROM pg_roles WHERE rolname=%s', (role,))
            if c.fetchone():
                c.execute(f'REVOKE ALL ON SCHEMA jerry_learning FROM {role}')
                c.execute(f'REVOKE ALL ON ALL TABLES IN SCHEMA jerry_learning FROM {role}')


def setting(key, value):
    with db() as c:
        c.execute('''INSERT INTO jerry_learning.settings(key,value) VALUES(%s,%s)
                     ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=now()''', (key, Json(value)))


def due_cutoff(now=None):
    now = (now or datetime.now(timezone.utc)).astimezone(CHINA)
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return day if now.hour >= 2 else day - timedelta(days=1)


def enqueue(kind='daily', now=None):
    now = now or datetime.now(timezone.utc)
    cutoff = now if kind == 'backfill' else due_cutoff(now)
    slot = 'initial-backfill' if kind == 'backfill' else 'daily-' + cutoff.date().isoformat()
    budget = float(os.environ.get('JERRY_LEARN_BACKFILL_BUDGET' if kind == 'backfill' else 'JERRY_LEARN_DAILY_BUDGET',
                                  '20' if kind == 'backfill' else '5'))
    with db() as c:
        c.execute('''INSERT INTO jerry_learning.runs(id,slot,kind,cutoff,budget_usd)
                     VALUES(%s,%s,%s,%s,%s) ON CONFLICT(slot) DO NOTHING''',
                  (str(uuid.uuid4()), slot, kind, cutoff, max(0, min(100, budget))))
        c.execute("UPDATE jerry_learning.knowledge SET status='expired',updated_at=now() WHERE status='active' AND expires_at<=now()")


def claim():
    with db() as c:
        # Transaction-scoped lock works through Supabase's transaction pooler.
        c.execute('SELECT pg_try_advisory_xact_lock(739231401) AS locked')
        if not c.fetchone()['locked']:
            return None
        c.execute("""SELECT 1 FROM jerry_learning.runs WHERE status='running' AND lease_until>now() LIMIT 1""")
        if c.fetchone():
            return None
        c.execute('''SELECT * FROM jerry_learning.runs
                     WHERE (status='queued' AND retry_at<=now()) OR (status='running' AND lease_until<now())
                     ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED''')
        run = c.fetchone()
        if not run:
            return None
        owner = str(uuid.uuid4())
        c.execute('''UPDATE jerry_learning.runs SET status='running',owner=%s,
                     lease_until=now()+interval '10 minutes', updated_at=now()
                     WHERE id=%s RETURNING *''', (owner, run['id']))
        return dict(c.fetchone())


def batch(run, size=20):
    with db() as c:
        c.execute('''SELECT u.id,u.session_id,u.user_email,u.is_leadership,u.sensitive_flagged,u.created_at,
                     u.content AS question, COALESCE(a.content,'') AS answer, a.model
                     FROM public.jerry_gpt_chats u
                     LEFT JOIN LATERAL (
                         SELECT a2.content,a2.model FROM public.jerry_gpt_chats a2
                         WHERE a2.session_id=u.session_id AND a2.user_email=u.user_email
                           AND a2.role='assistant' AND a2.id>u.id
                           AND NOT EXISTS (SELECT 1 FROM public.jerry_gpt_chats next_u
                             WHERE next_u.session_id=u.session_id AND next_u.user_email=u.user_email
                               AND next_u.role='user' AND next_u.id>u.id AND next_u.id<a2.id)
                         ORDER BY a2.id LIMIT 1
                     ) a ON TRUE
                     WHERE u.role='user' AND u.created_at<=%s
                       AND NOT EXISTS (SELECT 1 FROM jerry_learning.reviews r WHERE r.question_id=u.id)
                     ORDER BY u.id LIMIT %s''', (run['cutoff'], size))
        rows=[dict(r) for r in c.fetchall()]
        for row in rows:
            c.execute('SELECT sources FROM jerry_learning.turn_evidence WHERE user_email=%s AND session_id=%s AND question_hash=%s',
                      (row['user_email'],row['session_id'],hashlib.sha256(row['question'].encode()).hexdigest()))
            evidence=c.fetchone()
            row['web_sources']=evidence['sources'] if evidence else []
        return rows


def reserve(run, amount):
    with db() as c:
        c.execute('''UPDATE jerry_learning.runs SET reserved_usd=reserved_usd+%s,
                     lease_until=now()+interval '10 minutes',updated_at=now()
                     WHERE id=%s AND owner=%s AND status='running'
                       AND spent_usd+reserved_usd+%s<=budget_usd RETURNING id''',
                  (amount, run['id'], run['owner'], amount))
        return bool(c.fetchone())


def charge(run, reservation, usage):
    inp, out = int(usage.get('input_tokens', 0)), int(usage.get('output_tokens', 0))
    search = int((usage.get('server_tool_use') or {}).get('web_search_requests', 0))
    # Sonnet 4.6 published rates; this is an estimate, actual provider billing wins.
    cost = inp * 3 / 1e6 + out * 15 / 1e6 + search * .01
    with db() as c:
        c.execute('''UPDATE jerry_learning.runs SET reserved_usd=greatest(0,reserved_usd-%s),
                     spent_usd=spent_usd+%s,input_tokens=input_tokens+%s,
                     output_tokens=output_tokens+%s,searches=searches+%s,updated_at=now()
                     WHERE id=%s AND owner=%s''', (reservation,cost,inp,out,search,run['id'],run['owner']))


def finish_batch(run, rows, cards):
    accepted = pending = 0
    with db() as c:
        c.execute("SELECT id FROM jerry_learning.runs WHERE id=%s AND owner=%s AND status='running' FOR UPDATE", (run['id'],run['owner']))
        if not c.fetchone():
            raise RuntimeError('Learning lease lost')
        for card in cards:
            # Repeating identical facts updates neither their authority nor their expiry.
            fingerprint = hashlib.sha256((card['scope']+'|'+card['owner_email']+'|'+card['content'].casefold()).encode()).hexdigest()
            topic = re.sub(r'\W+', ' ', card['title'].casefold()).strip()
            c.execute("""SELECT id FROM jerry_learning.knowledge WHERE topic=%s AND scope=%s
                         AND owner_email=%s AND status='active' AND fingerprint<>%s LIMIT 1""",
                      (topic,card['scope'],card['owner_email'],fingerprint))
            if c.fetchone():
                card.update(status='pending', reason='A different active entry covers this topic; review the conflict.')
            c.execute('''INSERT INTO jerry_learning.knowledge
                         (fingerprint,topic,title,content,kind,scope,owner_email,status,sources,question_ids,
                          confidence,reason,run_id,expires_at)
                         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now()+%s*interval '1 day')
                         ON CONFLICT(fingerprint) DO NOTHING RETURNING id''',
                      (fingerprint,topic,card['title'],card['content'],card['kind'],card['scope'],card['owner_email'],
                       card['status'],Json(card['sources']),Json(card['question_ids']),card['confidence'],
                       card['reason'],run['id'],card['ttl_days']))
            saved = c.fetchone()
            if saved:
                accepted += card['status']=='active'
                pending += card['status']=='pending'
                c.execute('INSERT INTO jerry_learning.audit(knowledge_id,action,actor,detail) VALUES(%s,%s,%s,%s)',
                          (saved['id'],card['status'],'daily-learner',Json({'run_id':str(run['id']),'reason':card['reason']})))
        for row in rows:
            outcome = 'distilled' if any(row['id'] in x['question_ids'] for x in cards) else 'reviewed-no-new-supported-fact'
            c.execute('INSERT INTO jerry_learning.reviews(question_id,run_id,outcome) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING',
                      (row['id'],run['id'],outcome))
        c.execute('''UPDATE jerry_learning.runs SET reviewed=reviewed+%s,accepted=accepted+%s,
                     pending=pending+%s,failures=0,error='',lease_until=now()+interval '10 minutes',updated_at=now()
                     WHERE id=%s AND owner=%s''', (len(rows),accepted,pending,run['id'],run['owner']))


def release(run, status='queued', error=''):
    with db() as c:
        c.execute('''UPDATE jerry_learning.runs SET status=%s,error=%s,owner=NULL,lease_until=NULL,
                     updated_at=now(),finished_at=CASE WHEN %s='complete' THEN now() ELSE finished_at END
                     WHERE id=%s AND owner=%s''', (status,error,status,run['id'],run['owner']))


def fail(run, error):
    with db() as c:
        c.execute('''UPDATE jerry_learning.runs SET failures=failures+1,
                     status=CASE WHEN failures>=2 THEN 'failed' ELSE 'queued' END,
                     error=%s,owner=NULL,lease_until=NULL,retry_at=now()+interval '15 minutes',updated_at=now()
                     WHERE id=%s AND owner=%s''', (error[:300],run['id'],run['owner']))


def status(is_leadership=False, user=''):
    with db() as c:
        c.execute('SELECT key,value FROM jerry_learning.settings')
        settings = {r['key']:r['value'] for r in c.fetchall()}
        c.execute('''SELECT id,slot,kind,status,reviewed,accepted,pending,spent_usd,budget_usd,error,
                            created_at,updated_at,finished_at FROM jerry_learning.runs ORDER BY created_at DESC LIMIT 12''')
        runs = [dict(r) for r in c.fetchall()]
        c.execute('SELECT COUNT(*) AS n FROM jerry_learning.reviews')
        reviewed = c.fetchone()['n']
        c.execute("SELECT COUNT(*) AS n FROM public.jerry_gpt_chats WHERE role='user'")
        questions = c.fetchone()['n']
        c.execute('''SELECT id,title,content,kind,scope,status,sources,confidence,reason,created_at,expires_at
                     FROM jerry_learning.knowledge WHERE scope='internal' OR %s OR (scope='owner' AND owner_email=%s)
                     ORDER BY created_at DESC LIMIT 200''', (is_leadership,user))
        cards=[dict(r) for r in c.fetchall()]
        for card in cards:
            card['sources']=[{k:v for k,v in source.items() if k!='text'} for source in card['sources']]
        c.execute('''SELECT status,COUNT(*) AS n FROM jerry_learning.knowledge
                     WHERE scope='internal' OR %s OR (scope='owner' AND owner_email=%s) GROUP BY status''', (is_leadership,user))
        counts={r['status']:r['n'] for r in c.fetchall()}
    return {'settings':settings,'runs':runs,'reviewed':reviewed,'questions':questions,
            'counts':counts,'cards':cards,'can_manage':is_leadership}


def retrieve(query, is_leadership=False, user='', limit=8):
    # English tokens + Chinese bigrams work with Postgres simple dictionaries.
    tokens=re.findall(r'[a-zA-Z0-9]{2,}|[\u4e00-\u9fff]{2,}', query or '')
    terms=[]
    for token in tokens:
        terms.extend([token[i:i+2] for i in range(len(token)-1)] if re.match(r'[\u4e00-\u9fff]',token) else [token.lower()])
    terms=list(dict.fromkeys(terms))[:24]
    if not terms:
        return []
    with db(timeout=1500) as c:
        c.execute('''SELECT id,title,content,scope,sources,created_at,expires_at,
                     (SELECT COUNT(*) FROM unnest(%s::text[]) t WHERE title ILIKE '%%'||t||'%%'
                       OR content ILIKE '%%'||t||'%%') AS relevance
                     FROM jerry_learning.knowledge WHERE status='active' AND expires_at>now()
                       AND (scope='internal' OR (scope='leadership' AND %s) OR (scope='owner' AND owner_email=%s))
                       AND EXISTS(SELECT 1 FROM unnest(%s::text[]) t WHERE title ILIKE '%%'||t||'%%' OR content ILIKE '%%'||t||'%%')
                     ORDER BY relevance DESC,confidence DESC,updated_at DESC LIMIT %s''',
                  (terms,is_leadership,user,terms,limit))
        return [dict(r) for r in c.fetchall()]


def record_evidence(user, session_id, question, web_enabled, sources):
    with db() as c:
        c.execute('''INSERT INTO jerry_learning.turn_evidence(user_email,session_id,question_hash,web_enabled,sources)
                     VALUES(%s,%s,%s,%s,%s) ON CONFLICT(user_email,session_id,question_hash)
                     DO UPDATE SET sources=excluded.sources,web_enabled=excluded.web_enabled''',
                  (user,session_id,hashlib.sha256(question.encode()).hexdigest(),web_enabled,Json(sources)))


def retry_failed(actor):
    """Retry transient failures without resetting reviews or spending limits."""
    with db() as c:
        c.execute("""UPDATE jerry_learning.runs SET status='queued',failures=0,retry_at=now(),error='',updated_at=now()
                     WHERE status='failed'""")
        c.execute("INSERT INTO jerry_learning.audit(action,actor) VALUES('retry-failed',%s)", (actor,))


def retire(knowledge_id, actor):
    with db() as c:
        c.execute("UPDATE jerry_learning.knowledge SET status='retired',updated_at=now() WHERE id=%s RETURNING id", (knowledge_id,))
        if not c.fetchone():
            return False
        c.execute("INSERT INTO jerry_learning.audit(knowledge_id,action,actor) VALUES(%s,'retired',%s)",(knowledge_id,actor))
        return True
