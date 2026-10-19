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
# Fail closed for monetary/commercial material even if a model or old worker
# labelled it as general company knowledge. Shared by status and retrieval.
COMMERCIAL_PATTERN = r'(\$|€|£|¥)[[:space:]]*[0-9]|(^|[^a-z])(usd|eur|gbp|cny|rmb|prices?|pricing|costs?|margin|discount|confidential|roadmap|profit)([^a-z]|$)|报价|价格|定价|成本|费用|美元|欧元|人民币|毛利|机密|保密|底价|客户名|未发布'


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
        CREATE TABLE IF NOT EXISTS jerry_learning.comments (
            id BIGSERIAL PRIMARY KEY, knowledge_id BIGINT NOT NULL REFERENCES jerry_learning.knowledge(id),
            author TEXT NOT NULL, body TEXT NOT NULL, request_id UUID NOT NULL,
            state TEXT NOT NULL DEFAULT 'queued', run_id UUID,
            result TEXT NOT NULL DEFAULT '', created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            processed_at TIMESTAMPTZ, UNIQUE(author, request_id));
        CREATE INDEX IF NOT EXISTS jerry_learning_comments_pending
            ON jerry_learning.comments(knowledge_id, id) WHERE processed_at IS NULL;
        CREATE INDEX IF NOT EXISTS jerry_learning_comments_entry ON jerry_learning.comments(knowledge_id, id);
        CREATE INDEX IF NOT EXISTS jerry_learning_comments_author ON jerry_learning.comments(author, created_at);
        REVOKE ALL ON ALL TABLES IN SCHEMA jerry_learning FROM PUBLIC;
        ''')
        from neural.feeds import initialize as initialize_inputs
        initialize_inputs(c)
        c.execute("REVOKE ALL ON ALL TABLES IN SCHEMA jerry_learning FROM PUBLIC")
        # Repair any older overly broad classification without removing evidence.
        c.execute("""WITH hardened AS (
            UPDATE jerry_learning.knowledge SET scope='leadership',updated_at=now()
            WHERE scope='internal' AND (title||' '||content||' '||reason||' '||sources::text) ~* %s RETURNING id)
            INSERT INTO jerry_learning.audit(knowledge_id,action,actor)
            SELECT id,'restrict-commercial','privacy-migration' FROM hardened""", (COMMERCIAL_PATTERN,))
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
                     ORDER BY (kind='feedback') DESC,created_at LIMIT 1 FOR UPDATE SKIP LOCKED''')
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
        if run.get('kind') in ('daily','feedback','sources'):
            # Comments share the existing daily allowance, not a second budget.
            c.execute('SELECT pg_advisory_xact_lock(739231402)')
            c.execute('''SELECT COALESCE(sum(spent_usd+reserved_usd),0) AS used
                         FROM jerry_learning.runs WHERE kind IN ('daily','feedback','sources') AND cutoff=%s''',
                      (run['cutoff'],))
            if float(c.fetchone()['used']) + amount > float(run['budget_usd']):
                return False
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


def finish_batch(run, rows, cards, input_row=None):
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
            if input_row:
                c.execute('SELECT id FROM jerry_learning.knowledge WHERE fingerprint=%s',(fingerprint,))
                linked=c.fetchone()
                if linked:
                    c.execute('INSERT INTO jerry_learning.knowledge_inputs(knowledge_id,input_id) VALUES(%s,%s) ON CONFLICT DO NOTHING',
                              (linked['id'],input_row['id']))
        if input_row:
            c.execute("""UPDATE jerry_learning.inputs SET state=%s,processed_at=now(),result=%s
                         WHERE id=%s AND processed_at IS NULL""",
                      ('complete' if cards else 'needs_review',
                       f'{accepted} new available entries; {pending} new entries need review.' if cards else
                       'No supported reusable facts found. Add a more specific source or provide its text.',input_row['id']))
            c.execute("INSERT INTO jerry_learning.audit(action,actor,detail) VALUES('source-distilled','source-learner',%s)",
                      (Json({'input_id':input_row['id'],'accepted':accepted,'pending':pending}),))
        for row in rows:
            outcome = 'distilled' if any(row['id'] in x['question_ids'] for x in cards) else 'reviewed-no-new-supported-fact'
            c.execute('INSERT INTO jerry_learning.reviews(question_id,run_id,outcome) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING',
                      (row['id'],run['id'],outcome))
        c.execute('''UPDATE jerry_learning.runs SET reviewed=reviewed+%s,accepted=accepted+%s,
                     pending=pending+%s,failures=0,error='',lease_until=now()+interval '10 minutes',updated_at=now()
                     WHERE id=%s AND owner=%s''', (1 if input_row else len(rows),accepted,pending,run['id'],run['owner']))


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
    from .engine import evidence_reason
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
        c.execute('''SELECT id,title,content,kind,scope,status,sources,confidence,reason,created_at,updated_at,expires_at,
                     (SELECT count(*) FROM jerry_learning.comments cm WHERE cm.knowledge_id=knowledge.id) AS comment_count,
                     (SELECT count(*) FROM jerry_learning.comments cm WHERE cm.knowledge_id=knowledge.id AND cm.processed_at IS NULL) AS comments_waiting
                     FROM jerry_learning.knowledge WHERE (scope='internal' AND NOT ((title||' '||content||' '||reason||' '||sources::text) ~* %s)) OR %s OR (scope='owner' AND owner_email=%s)
                     ORDER BY created_at DESC LIMIT 200''', (COMMERCIAL_PATTERN,is_leadership,user))
        cards=[dict(r) for r in c.fetchall()]
        for card in cards:
            card['reason']=evidence_reason(card['reason'])
            card['sources']=[{k:v for k,v in source.items() if k!='text'} for source in card['sources']]
        c.execute('''SELECT status,COUNT(*) AS n FROM jerry_learning.knowledge
                     WHERE (scope='internal' AND NOT ((title||' '||content||' '||reason||' '||sources::text) ~* %s)) OR %s OR (scope='owner' AND owner_email=%s) GROUP BY status''', (COMMERCIAL_PATTERN,is_leadership,user))
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
                       AND ((scope='internal' AND NOT ((title||' '||content||' '||reason||' '||sources::text) ~* %s)) OR (scope IN ('internal','leadership') AND %s) OR (scope='owner' AND owner_email=%s))
                       AND EXISTS(SELECT 1 FROM unnest(%s::text[]) t WHERE title ILIKE '%%'||t||'%%' OR content ILIKE '%%'||t||'%%')
                     ORDER BY relevance DESC,confidence DESC,updated_at DESC LIMIT %s''',
                  (terms,COMMERCIAL_PATTERN,is_leadership,user,terms,limit))
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
        c.execute("""UPDATE jerry_learning.comments SET state='withdrawn',processed_at=now(),
                     result='Entry removed from use before feedback was applied.'
                     WHERE knowledge_id=%s AND processed_at IS NULL""", (knowledge_id,))
        c.execute("INSERT INTO jerry_learning.audit(knowledge_id,action,actor) VALUES(%s,'retired',%s)",(knowledge_id,actor))
        return True


class FeedbackError(ValueError):
    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(message)


def visible_entry(c, knowledge_id, is_leadership, user, lock=False):
    c.execute("""SELECT * FROM jerry_learning.knowledge WHERE id=%s AND (
        (scope='internal' AND NOT ((title||' '||content||' '||reason||' '||sources::text) ~* %s))
        OR %s OR (scope='owner' AND owner_email=%s))""" + (' FOR UPDATE' if lock else ''),
        (knowledge_id, COMMERCIAL_PATTERN, is_leadership, user))
    entry = c.fetchone()
    if not entry:
        raise FeedbackError(404, 'Knowledge entry not found or not available to you.')
    return dict(entry)


def add_comment(knowledge_id, user, is_leadership, body, request_id, confidential=False):
    from .engine import redact, SENSITIVE
    body = redact(body).strip()
    if not 3 <= len(body) <= 2000:
        raise FeedbackError(400, 'Write a comment between 3 and 2,000 characters.')
    with db() as c:
        # Serialize per-author rate limits; entry lock serializes revisions with AI saves.
        c.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,739231403))', (user,))
        c.execute('SELECT id,knowledge_id FROM jerry_learning.comments WHERE author=%s AND request_id=%s',
                  (user, request_id))
        previous = c.fetchone()
        if previous:
            if previous['knowledge_id'] != knowledge_id:
                raise FeedbackError(409, 'This submission identifier was already used for another entry.')
            return {'ok': True, 'id': previous['id'], 'duplicate': True}
        entry = visible_entry(c, knowledge_id, is_leadership, user, lock=True)
        if entry['status'] != 'pending':
            raise FeedbackError(409, 'This entry is no longer awaiting review. Refresh to see its latest state.')
        c.execute("SELECT count(*) AS n FROM jerry_learning.comments WHERE author=%s AND created_at>now()-interval '1 hour'", (user,))
        if c.fetchone()['n'] >= 20:
            raise FeedbackError(429, 'You have sent 20 comments this hour. Please try again later.')
        c.execute('SELECT count(*) AS n FROM jerry_learning.comments WHERE knowledge_id=%s AND processed_at IS NULL', (knowledge_id,))
        if c.fetchone()['n'] >= 20:
            raise FeedbackError(429, 'This entry has 20 comments waiting for AI review. Please wait for the review to finish.')
        # Privacy only tightens, and happens before feedback can be read or searched.
        restricted = bool(confidential or SENSITIVE.search(body))
        if restricted and entry['scope'] == 'internal':
            c.execute("UPDATE jerry_learning.knowledge SET scope='leadership',updated_at=now() WHERE id=%s", (knowledge_id,))
        c.execute("""INSERT INTO jerry_learning.comments(knowledge_id,author,body,request_id)
                     VALUES(%s,%s,%s,%s) RETURNING id""", (knowledge_id,user,body,request_id))
        comment_id = c.fetchone()['id']
        c.execute("INSERT INTO jerry_learning.audit(knowledge_id,action,actor,detail) VALUES(%s,'comment-added',%s,%s)",
                  (knowledge_id,user,Json({'comment_id':comment_id,'restricted':restricted})))
        return {'ok':True,'id':comment_id,'restricted':restricted and entry['scope']=='internal' and not is_leadership}


def comments(knowledge_id, is_leadership, user):
    with db() as c:
        entry = visible_entry(c, knowledge_id, is_leadership, user)
        c.execute("""SELECT cm.id,cm.author,cm.body,cm.state,cm.result,cm.created_at,cm.processed_at,
                     r.status AS run_status FROM jerry_learning.comments cm
                     LEFT JOIN jerry_learning.runs r ON r.id=cm.run_id
                     WHERE cm.knowledge_id=%s ORDER BY cm.id DESC LIMIT 50""", (knowledge_id,))
        return {'comments':list(reversed([dict(r) for r in c.fetchall()])),
                'can_comment':entry['status']=='pending','scope':entry['scope']}


def enqueue_feedback(now=None):
    cutoff = due_cutoff(now)
    budget = max(0,min(100,float(os.environ.get('JERRY_LEARN_DAILY_BUDGET','5'))))
    with db() as c:
        c.execute("""INSERT INTO jerry_learning.runs(id,slot,kind,cutoff,budget_usd)
            SELECT %s,%s,'feedback',%s,%s WHERE EXISTS(
                SELECT 1 FROM jerry_learning.comments cm JOIN jerry_learning.knowledge k ON k.id=cm.knowledge_id
                WHERE cm.processed_at IS NULL AND k.status='pending')
            ON CONFLICT(slot) DO UPDATE SET status='queued',finished_at=NULL,updated_at=now()
                WHERE jerry_learning.runs.status='complete'""",
            (str(uuid.uuid4()),'feedback-'+cutoff.date().isoformat(),cutoff,budget))


def feedback_batch(run):
    with db() as c:
        c.execute("""SELECT k.* FROM jerry_learning.knowledge k WHERE k.status='pending'
            AND EXISTS(SELECT 1 FROM jerry_learning.comments cm WHERE cm.knowledge_id=k.id AND cm.processed_at IS NULL)
            ORDER BY (SELECT min(id) FROM jerry_learning.comments cm WHERE cm.knowledge_id=k.id AND cm.processed_at IS NULL)
            LIMIT 1 FOR UPDATE""")
        entry = c.fetchone()
        if not entry:
            return None
        c.execute("""UPDATE jerry_learning.comments SET state='reviewing',run_id=%s
            WHERE knowledge_id=%s AND processed_at IS NULL RETURNING *""", (run['id'],entry['id']))
        pending = sorted([dict(r) for r in c.fetchall()], key=lambda r:r['id'])
        c.execute("""SELECT * FROM jerry_learning.comments WHERE knowledge_id=%s AND processed_at IS NOT NULL
                     ORDER BY id DESC LIMIT 10""", (entry['id'],))
        history = list(reversed([dict(r) for r in c.fetchall()]))
        return {'entry':dict(entry),'comments':history+pending,'pending_ids':[r['id'] for r in pending]}


def finish_feedback(run, batch, card):
    entry_id = batch['entry']['id']
    ids = batch['pending_ids']
    with db() as c:
        c.execute("SELECT id FROM jerry_learning.runs WHERE id=%s AND owner=%s AND status='running' FOR UPDATE", (run['id'],run['owner']))
        if not c.fetchone():
            raise RuntimeError('Learning lease lost')
        c.execute('SELECT * FROM jerry_learning.knowledge WHERE id=%s FOR UPDATE', (entry_id,))
        before = dict(c.fetchone())
        if before['status'] != 'pending':
            return False  # Removed while the model was running; never resurrect it.
        c.execute('SELECT id FROM jerry_learning.comments WHERE knowledge_id=%s AND processed_at IS NULL ORDER BY id', (entry_id,))
        if [r['id'] for r in c.fetchall()] != ids:
            c.execute("UPDATE jerry_learning.comments SET state='queued' WHERE knowledge_id=%s AND processed_at IS NULL", (entry_id,))
            return False  # A newer correction arrived. Recheck the complete feedback.
        # Source and comment restrictions cannot be downgraded by the model.
        if before['scope'] != 'internal':
            card['scope'],card['owner_email'] = before['scope'],before['owner_email']
        if card['scope'] == 'owner':
            card['status'] = 'pending'
        fingerprint = hashlib.sha256((card['scope']+'|'+card['owner_email']+'|'+card['content'].casefold()).encode()).hexdigest()
        topic = re.sub(r'\W+',' ',card['title'].casefold()).strip()
        c.execute('SELECT id FROM jerry_learning.knowledge WHERE fingerprint=%s AND id<>%s LIMIT 1', (fingerprint,entry_id))
        duplicate = c.fetchone()
        if duplicate:
            # Retain the proposal/history without violating the unique fact index.
            card = {**before,'status':'pending','reason':'The revised fact already exists in another entry. This proposal remains for review.','ttl_days':30}
            fingerprint,topic = before['fingerprint'],before['topic']
        else:
            c.execute("""SELECT id FROM jerry_learning.knowledge WHERE topic=%s AND scope=%s
                         AND owner_email=%s AND status='active' AND id<>%s LIMIT 1""", (topic,card['scope'],card['owner_email'],entry_id))
            if c.fetchone():
                card.update(status='pending',reason='A different active entry covers this topic; review the conflict.')
        c.execute("""UPDATE jerry_learning.knowledge SET fingerprint=%s,topic=%s,title=%s,content=%s,kind=%s,
            scope=%s,owner_email=%s,status=%s,sources=%s,confidence=%s,reason=%s,run_id=%s,
            expires_at=now()+%s*interval '1 day',updated_at=now() WHERE id=%s""",
            (fingerprint,topic,card['title'],card['content'],card['kind'],card['scope'],card['owner_email'],card['status'],
             Json(card['sources']),card['confidence'],card['reason'],run['id'],card['ttl_days'],entry_id))
        c.execute("""UPDATE jerry_learning.comments SET state=%s,result=%s,processed_at=now()
                     WHERE id=ANY(%s)""", ('learned' if card['status']=='active' else 'needs_review',card['reason'],ids))
        snapshot={k:before[k] for k in ('title','content','kind','scope','owner_email','status','sources','confidence','reason')}
        c.execute("INSERT INTO jerry_learning.audit(knowledge_id,action,actor,detail) VALUES(%s,'feedback-distilled','feedback-learner',%s)",
            (entry_id,Json({'run_id':str(run['id']),'comment_ids':ids,'before':snapshot,'after_status':card['status']})))
        c.execute("""UPDATE jerry_learning.runs SET reviewed=reviewed+1,accepted=accepted+%s,pending=pending+%s,
            failures=0,error='',lease_until=now()+interval '10 minutes',updated_at=now() WHERE id=%s AND owner=%s""",
            (int(card['status']=='active'),int(card['status']=='pending'),run['id'],run['owner']))
        return True
