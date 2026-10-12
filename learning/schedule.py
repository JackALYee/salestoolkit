"""Supabase Cron wakes the hosted worker; no desktop process is required."""
from __future__ import annotations
import hashlib
import hmac
import os
import threading
import time
from datetime import datetime, timezone

from psycopg2 import sql
from . import store, engine

STOP=threading.Event()
_thread=None
PUBLIC_URL='https://streamax-salestoolkit.com'


def wake_key():
    secret=os.environ.get('AUTH_SECRET','')
    if not secret:
        raise RuntimeError('AUTH_SECRET is required for the online learning schedule.')
    return hmac.new(secret.encode(),b'jerry-learning-wake-v1',hashlib.sha256).hexdigest()


def valid_wake(timestamp, signature, now=None):
    try:
        stamp=int(timestamp)
        if abs((time.time() if now is None else now)-stamp)>300:
            return False
        expected=hmac.new(wake_key().encode(),str(stamp).encode(),hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected,signature or '')
    except (TypeError,ValueError,RuntimeError):
        return False


def install():
    """Idempotent hosted scheduler with short-lived signed wake requests."""
    with store.db() as c:
        c.execute('CREATE EXTENSION IF NOT EXISTS pg_cron')
        c.execute('CREATE EXTENSION IF NOT EXISTS pg_net WITH SCHEMA extensions')
        c.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions')
        c.execute("SELECT n.nspname FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace WHERE e.extname='pgcrypto'")
        crypto_schema=c.fetchone()['nspname']
        c.execute("SELECT id FROM vault.secrets WHERE name='jerry_learning_wake_key'")
        secret=c.fetchone()
        if secret:
            c.execute('SELECT vault.update_secret(%s,%s)',(secret['id'],wake_key()))
        else:
            c.execute("SELECT vault.create_secret(%s,'jerry_learning_wake_key','Scoped daily-learning wake signing key')",(wake_key(),))
        c.execute(sql.SQL('''CREATE OR REPLACE FUNCTION jerry_learning.wake() RETURNS bigint
            LANGUAGE plpgsql SECURITY DEFINER SET search_path='' AS $body$
            DECLARE stamp text; signature text; secret text; request_id bigint;
            BEGIN
              stamp:=floor(extract(epoch FROM now()))::bigint::text;
              SELECT decrypted_secret INTO secret FROM vault.decrypted_secrets WHERE name='jerry_learning_wake_key';
              signature:=encode({crypto}.hmac(convert_to(stamp,'UTF8'),convert_to(secret,'UTF8'),'sha256'),'hex');
              SELECT net.http_post(url:='https://streamax-salestoolkit.com/api/learning/wake',
                headers:=jsonb_build_object('Content-Type','application/json','X-Learning-Time',stamp,'X-Learning-Signature',signature),
                body:='{{}}'::jsonb,timeout_milliseconds:=120000) INTO request_id;
              RETURN request_id;
            END $body$''').format(crypto=sql.Identifier(crypto_schema)))
        c.execute('REVOKE ALL ON FUNCTION jerry_learning.wake() FROM PUBLIC')
        # UTC 18:00 == 02:00 next day in China, with no DST ambiguity.
        c.execute("SELECT cron.schedule('jerry-learning-daily','0 18 * * *','SELECT jerry_learning.wake()')")
        # Continues interrupted batches and catches a missed daily wake. The SQL
        # predicate means no HTTP calls/cost when there is nothing due.
        c.execute('''SELECT cron.schedule('jerry-learning-resume','*/5 * * * *',%s)''', ('''
            SELECT jerry_learning.wake() WHERE
              EXISTS(SELECT 1 FROM jerry_learning.runs
                     WHERE (status='queued' AND retry_at<=now()) OR (status='running' AND lease_until<now()))
              OR NOT EXISTS(SELECT 1 FROM jerry_learning.runs
                 WHERE slot='daily-'||to_char((now() AT TIME ZONE 'Asia/Shanghai' - interval '2 hours')::date,'YYYY-MM-DD'))
              OR (EXISTS(SELECT 1 FROM jerry_learning.comments cm JOIN jerry_learning.knowledge k ON k.id=cm.knowledge_id
                    WHERE cm.processed_at IS NULL AND k.status='pending')
                  AND NOT EXISTS(SELECT 1 FROM jerry_learning.runs
                    WHERE slot='feedback-'||to_char((now() AT TIME ZONE 'Asia/Shanghai' - interval '2 hours')::date,'YYYY-MM-DD')
                      AND status IN ('queued','running','failed','budget_limit')))
            ''',))
        c.execute("SELECT jobname,schedule,active FROM cron.job WHERE jobname IN ('jerry-learning-daily','jerry-learning-resume') ORDER BY jobname")
        jobs=[dict(r) for r in c.fetchall()]
    store.setting('scheduler',{'installed':True,'timezone':'Asia/Shanghai','daily_time':'02:00',
                               'jobs':jobs,'checked_at':datetime.now(timezone.utc).isoformat()})


def tick():
    store.enqueue('daily')
    store.enqueue_feedback()
    engine.work()


def bootstrap():
    store.initialize()
    try:
        install()
    except Exception as exc:
        store.setting('scheduler',{'installed':False,'error':type(exc).__name__+' '+str(getattr(exc,'pgcode','') or '')+' '+str(getattr(getattr(exc,'diag',None),'message_primary','') or '')[:180],
                                   'timezone':'Asia/Shanghai','daily_time':'02:00'})
    store.enqueue('backfill')
    store.enqueue('daily')


def loop():
    initialized=False
    last_setup=0
    while not STOP.is_set():
        try:
            if not initialized or time.monotonic()-last_setup>3600:
                bootstrap()
                initialized=True
                last_setup=time.monotonic()
            tick()
        except Exception as exc:
            print(f'[LEARNING] online worker: {type(exc).__name__}',flush=True)
        STOP.wait(30)


def start():
    global _thread
    # Importing the application in tests/local development never performs real
    # learning or schedules production jobs. Enable only on the deployed host.
    if os.environ.get('JERRY_LEARN_ENABLED','1')=='0' or not os.environ.get('RENDER_GIT_COMMIT'):
        return
    if not os.environ.get('JERRY_GPT_DB_URL') or not os.environ.get('ANTHROPIC_API_KEY'):
        print('[LEARNING] online worker requires the database and organization Anthropic key.',flush=True)
        return
    if _thread is None or not _thread.is_alive():
        STOP.clear()
        _thread=threading.Thread(target=loop,name='jerry-learning',daemon=True)
        _thread.start()


def stop():
    STOP.set()
