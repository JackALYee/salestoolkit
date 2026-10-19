"""Private dashboard, graph provenance, and cloud-source ingestion regression checks.
Uses only a disposable local database and mocked AI responses, never production data.
"""
import json
import os
import sys
import unittest
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
os.environ['AUTH_SECRET']='neural-test-only'
os.environ['JERRY_LEARN_ENABLED']='0'
import server as S
from learning import store as D, engine as E
from neural import feeds as F, graph as G
from fastapi.testclient import TestClient
OWNER='jcyi@streamax.com'
WEB=dict(id='W1',type='web',url='https://example.org/lte',title='LTE standard',text='LTE is a cellular standard used in connected vehicle devices.')

def payload(**extra):
    return dict(request_id=str(uuid.uuid4()),kind='information',title='Connected vehicle communications',
                content='LTE is a cellular standard used in connected vehicle devices.',scope='leadership',**extra)

def claim(**extra):
    return dict(index=0,title='LTE terminology',content=WEB['text'],kind='internal',scope='internal',owner_email='',question_ids=[],**extra)

def verdict(**extra):
    v=dict(index=0,title='LTE terminology',supported=True,content=WEB['text'],confidence=.95,
           source_ids=['W1'],sensitivity='internal',ttl_days=30,reason='The source supports the claim.')
    v.update(extra);return {'verdicts':[v]}

class AccessAndEvidence(unittest.TestCase):
    def client(self,user=None):
        client=TestClient(S.app)
        if user:client.cookies.set(S.COOKIE_NAME,S.make_token(user))
        return client
    def test_personal_routes_gate_before_database(self):
        with patch.object(G,'snapshot',return_value={'nodes':[]}) as snapshot,patch.object(F,'submit',return_value={'id':1}) as submit:
            for user,status in ((None,401),('jimmy@streamax.com',403),('sunyan@streamax.com',403),('kiki@streamax.com',403),(OWNER,200)):
                client=self.client(user)
                self.assertEqual(client.get('/api/neural').status_code,status,user)
                self.assertEqual(client.post('/api/neural/inputs',json=payload(),headers={'Origin':'http://testserver'}).status_code,202 if status==200 else status,user)
            self.assertEqual(snapshot.call_count,1);self.assertEqual(submit.call_count,1)
            self.assertEqual(self.client().get('/neural',follow_redirects=False).status_code,302)
            self.assertEqual(self.client('sunyan@streamax.com').get('/neural').status_code,403)
            self.assertEqual(self.client(OWNER).get('/neural').headers['cache-control'],'private, no-store')
    def test_csrf_content_type_and_size(self):
        c=self.client(OWNER)
        with patch.object(F,'submit') as submit:
            self.assertEqual(c.post('/api/neural/inputs',json=payload(),headers={'Origin':'https://evil.example'}).status_code,403)
            self.assertEqual(c.post('/api/neural/inputs',content='{}',headers={'Origin':'http://testserver'}).status_code,415)
            self.assertEqual(c.post('/api/neural/inputs',content='x'*60001,headers={'Origin':'http://testserver','Content-Type':'application/json'}).status_code,413)
            submit.assert_not_called()
    def test_shared_network_uses_caller_clearance_and_no_cache(self):
        with patch.object(G,'snapshot',return_value={'nodes':[]}) as mock:
            r=self.client('jimmy@streamax.com').get('/api/neural/network')
            self.assertEqual(r.status_code,200);self.assertEqual(mock.call_args.args,('jimmy@streamax.com',False))
            self.assertIn('no-store',r.headers['cache-control'])
        with patch.object(G,'snapshot',side_effect=RuntimeError()):
            r=self.client('jimmy@streamax.com').get('/api/neural/network')
            self.assertTrue(r.json()['degraded']);self.assertNotIn('$20',r.text)
    def test_supplied_evidence_is_only_accepted_for_source_pipeline(self):
        evidence=[dict(WEB,type='supplied',scope='leadership')]
        self.assertEqual(E.verified_cards([claim()],verdict(),evidence)[0]['status'],'pending')
        card=E.verified_cards([claim()],verdict(),evidence,allow_supplied=True)[0]
        self.assertEqual((card['status'],card['scope']),('active','leadership'))
        external=claim();external['kind']='external'
        self.assertEqual(E.verified_cards([external],verdict(),evidence,allow_supplied=True)[0]['status'],'pending')
    def test_secret_private_url_and_restricted_research_never_reach_search(self):
        for url in ('https://localhost','https://127.0.0.1','https://10.0.0.1/x','http://example.org','https://a:b@example.org'):
            p=payload();p.update(kind='website',scope='internal',url=url)
            with self.assertRaises(ValueError):F.submit(OWNER,p)
        for text in ('Confidential customer deployment','What is our margin?', 'password=secret123', 'jcyi@streamax.com'):
            p=payload();p.update(kind='internet',scope='internal',title=text)
            with self.assertRaises(ValueError):F.submit(OWNER,p)
    def test_website_requires_evidence_from_requested_page(self):
        item={'id':4,'kind':'website','url':'https://example.org/specific-page','title':'LTE facts','content':'','scope':'internal','author':OWNER}
        with patch.object(E,'research',return_value=[WEB]),patch.object(E,'json_call') as extract:
            self.assertEqual(F.review({},item),[]);extract.assert_not_called()
    def test_graph_labels_provenance_and_never_calls_weights(self):
        card=dict(id=1,title='LTE in ADPlus 2.0',content='ADPlus 2.0 uses cellular communications.',status='active',kind='external',sources=[WEB],question_ids=[9],input_ids=[7])
        result=G.projection([card],[{'id':7,'kind':'website'}],False,False)
        knowledge=next(n for n in result['nodes'] if n['id']=='k:1')
        self.assertEqual(knowledge['card']['channels'],['chats','website'])
        self.assertTrue(any(e['kind']=='mentions concept' for e in result['edges']))
        self.assertNotIn('$20',json.dumps(result))
        self.assertNotIn('weight',json.dumps(result['edges']))

DB=os.environ.get('JERRY_LEARN_TEST_DB_URL','')
@unittest.skipUnless(DB,'Set JERRY_LEARN_TEST_DB_URL to run real Postgres tests.')
class Database(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from urllib.parse import urlsplit
        u=urlsplit(DB);assert u.hostname in ('localhost','127.0.0.1') and u.path=='/jerry_learning_test'
        cls.env=patch.dict(os.environ,{'JERRY_GPT_DB_URL':DB});cls.env.start();D.initialize()
        with D.db() as c:c.execute('CREATE TABLE IF NOT EXISTS public.jerry_gpt_chats(id BIGSERIAL PRIMARY KEY,session_id TEXT,user_email TEXT,role TEXT,content TEXT,model TEXT,is_leadership BOOL DEFAULT FALSE,sensitive_flagged BOOL DEFAULT FALSE,created_at TIMESTAMPTZ DEFAULT now())')
    @classmethod
    def tearDownClass(cls):cls.env.stop()
    def setUp(self):
        with D.db() as c:c.execute('TRUNCATE jerry_learning.knowledge_inputs,jerry_learning.inputs,jerry_learning.comments,jerry_learning.knowledge,jerry_learning.runs,jerry_learning.reviews,jerry_learning.audit,jerry_learning.turn_evidence,public.jerry_gpt_chats RESTART IDENTITY')
    def test_submit_redaction_idempotency_and_restriction(self):
        p=payload();p.update(scope='internal',content='A company licence price is $20. password=secret123. Contact person@example.org for context.')
        first=F.submit(OWNER,p);self.assertEqual(first,F.submit(OWNER,p))
        with D.db() as c:
            c.execute('SELECT * FROM jerry_learning.inputs');row=c.fetchone()
            self.assertEqual(row['scope'],'leadership');self.assertNotIn('secret123',row['content']);self.assertNotIn('person@example',row['content'])
    def test_end_to_end_source_to_graph_and_retrieval(self):
        F.submit(OWNER,payload());F.enqueue();run=D.claim();item=F.batch(run)
        raw={'candidates':[dict(title='LTE terminology',content=WEB['text'],kind='internal',sensitivity='internal',question_ids=[item['id']])]}
        with patch.object(E,'json_call',side_effect=[raw,verdict(source_ids=['I1'])]),patch.object(E,'curated_evidence',return_value=[]),patch.object(E,'research',return_value=[]):cards=F.review(run,item)
        self.assertEqual(cards[0]['question_ids'],[]);self.assertIn('Owner-supplied reference',cards[0]['content']);D.finish_batch(run,[],cards,input_row=item);D.release(run,'complete')
        self.assertIsNone(F.batch(run));self.assertEqual(D.retrieve('LTE',False,'jimmy@streamax.com'),[])
        self.assertEqual(len(D.retrieve('LTE',True,OWNER)),1)
        graph=G.snapshot(OWNER,True,True)
        self.assertEqual(graph['reviewed_questions'],0);self.assertEqual(graph['available'],1);self.assertEqual(graph['inputs'][0]['state'],'complete')
        learned=next(n for n in graph['nodes'] if n['type']=='knowledge')
        self.assertEqual(learned['card']['channels'],['information']);self.assertNotIn('text',learned['card']['sources'][0])
        self.assertEqual(graph['timeline'][0]['learned'],1)
        self.assertFalse(any(n['type']=='knowledge' for n in G.snapshot('jimmy@streamax.com')['nodes']))
    def test_daily_and_sources_share_budget_and_carry_forward(self):
        F.submit(OWNER,payload());F.enqueue();r=D.claim();self.assertTrue(D.reserve(r,4.75));D.release(r,'budget_limit')
        D.enqueue();daily=D.claim();self.assertFalse(D.reserve(daily,.5));D.release(daily,'budget_limit')
        F.enqueue();self.assertIsNone(D.claim());F.enqueue(datetime.now(timezone.utc)+timedelta(days=1));n=D.claim();self.assertTrue(D.reserve(n,.5));self.assertIsNotNone(F.batch(n))
    def test_lease_loss_does_not_mark_source_processed(self):
        F.submit(OWNER,payload());F.enqueue();r=D.claim();i=F.batch(r)
        with D.db() as c:c.execute("UPDATE jerry_learning.runs SET lease_until=now()-interval '1 second'")
        new=D.claim()
        with self.assertRaises(RuntimeError):D.finish_batch(r,[],[],input_row=i)
        self.assertEqual(F.batch(new)['id'],i['id'])
    def test_duplicate_fact_preserves_both_input_provenance_without_chat_inflation(self):
        cards=E.verified_cards([claim()],verdict(),[dict(WEB,type='curated')])
        for _ in range(2):
            F.submit(OWNER,payload());F.enqueue();r=D.claim();i=F.batch(r);D.finish_batch(r,[],cards,input_row=i);D.release(r,'complete')
        graph=G.snapshot(OWNER,True,True);self.assertEqual(graph['available'],1)
        k=next(n for n in graph['nodes'] if n['type']=='knowledge');self.assertEqual(len(k['card']['input_ids']),2)
        self.assertEqual(graph['reviewed_questions'],0)
    def test_owner_only_material_is_excluded_even_from_other_leaders(self):
        D.enqueue('backfill');r=D.claim();c=claim();c.update(scope='owner',owner_email='someone@streamax.com')
        D.finish_batch(r,[],E.verified_cards([c],verdict(),[dict(WEB,type='curated')]))
        self.assertEqual(G.snapshot(OWNER,True,True)['total'],0)

if __name__=='__main__':unittest.main(verbosity=2)
