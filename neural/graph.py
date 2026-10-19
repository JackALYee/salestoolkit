"""Evidence-labelled graph projections. Authorization precedes aggregation."""
from __future__ import annotations
import hashlib
import re
from datetime import datetime, timezone
from learning import store, engine
from topology import TOPOLOGY

CHANNELS={
    'chats':('Conversations','Reusable knowledge distilled from users’ questions and answers.'),
    'website':('Websites','Public pages you submitted, reviewed against cited page evidence.'),
    'information':('Supplied knowledge','Owner-supplied information and the curated reference library.'),
    'internet':('Internet research','Public claims checked against cited internet sources.'),
}


def visible_sql():
    # Even leaders do not gain other individuals' owner-only cards here.
    return """((k.scope='internal' AND NOT ((k.title||' '||k.content||' '||k.reason||' '||k.sources::text) ~* %s))
        OR (k.scope IN ('internal','leadership') AND %s) OR (k.scope='owner' AND k.owner_email=%s))"""


def source_id(source):
    value=source.get('url') or source.get('locator') or source.get('title','')
    return 'e:'+hashlib.sha256(value.encode()).hexdigest()[:16]


def projection(cards, inputs, leader, personal):
    nodes=[dict(id='jerry',label='Jerry GPT',type='core',description='Evidence-backed knowledge available to improve future answers.')]
    edges=[]
    for key,(label,desc) in CHANNELS.items():
        nodes.append(dict(id='channel:'+key,label=label,type='channel',channel=key,description=desc))
        edges.append(dict(source='jerry',target='channel:'+key,kind='learning path'))
    nodes.append(dict(id='foundation',label='Product ecosystem',type='foundation',description='Curated product relationships; connections are not learned model weights.'))
    edges.append(dict(source='jerry',target='foundation',kind='reference map'))
    catalogue=[]
    for original in TOPOLOGY['nodes']:
        node=dict(id='t:'+original['id'],label=original['id'],type='concept',category=original['cat'],description=original.get('desc',''))
        if not leader and engine.SENSITIVE.search(node['description']):
            node['description']='Product reference. Commercial details require leadership access.'
        nodes.append(node);catalogue.append(node)
        edges.append(dict(source='foundation',target=node['id'],kind='curated concept'))
    edges.extend(dict(source='t:'+e['source'],target='t:'+e['target'],kind='curated relationship') for e in TOPOLOGY['links'])
    by_input={i['id']:i for i in inputs}
    evidence_nodes={}
    for card in cards:
        channels=set()
        if card['question_ids']: channels.add('chats')
        origins=[by_input[x] for x in card.get('input_ids',[]) if x in by_input]
        channels.update(i['kind'] for i in origins)
        if any(s.get('type')=='curated' for s in card['sources']): channels.add('information')
        if any(s.get('type')=='web' for s in card['sources']) and 'website' not in channels: channels.add('internet')
        if any(s.get('type')=='supplied' for s in card['sources']): channels.add('information')
        if not channels: channels.add('chats') if card['question_ids'] else None
        explicit=[i['kind'] for i in origins]
        primary=next((x for x in ('website','information','internet') if x in explicit),
                     'internet' if card['kind']=='external' and 'internet' in channels else
                     'chats' if 'chats' in channels else 'information')
        card=dict(card,channels=sorted(channels),primary_channel=primary)
        node=dict(id='k:'+str(card['id']),label=card['title'],type='knowledge',description=card['content'],**{'card':card})
        nodes.append(node)
        edges.append(dict(source='jerry',target=node['id'],kind='learned reference' if card['status']=='active' else 'awaiting review or inactive'))
        for channel in channels:
            edges.append(dict(source='channel:'+channel,target=node['id'],kind='learning provenance'))
        for source in card['sources']:
            eid=source_id(source)
            evidence_nodes[eid]=dict(id=eid,label=source.get('title') or source.get('locator') or source.get('url') or 'Source',
                                    type='source',description=source.get('locator') or source.get('url',''),source=source)
            edges.append(dict(source=eid,target=node['id'],kind='cited evidence'))
        text=card['title']+' '+card['content']
        for concept in catalogue:
            if re.search(r'(?<![a-z0-9])'+re.escape(concept['label']).replace(r'\ ', r'\s*')+r'(?![a-z0-9])',text,re.I):
                edges.append(dict(source=node['id'],target=concept['id'],kind='mentions concept'))
    nodes.extend(evidence_nodes.values())
    return {'nodes':nodes,'edges':edges}


def snapshot(user, leader=False, personal=False):
    visibility=visible_sql()
    params=(store.COMMERCIAL_PATTERN,leader,user)
    state_filter='' if personal else " AND k.status='active' AND k.expires_at>now()"
    with store.db(timeout=8000) as c:
        # One database snapshot keeps totals and the graph in agreement.
        c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        c.execute('SELECT k.status,count(*) AS n FROM jerry_learning.knowledge k WHERE '+visibility+state_filter+' GROUP BY k.status',params)
        counts={r['status']:r['n'] for r in c.fetchall()}
        c.execute('''SELECT k.id,k.title,k.content,k.kind,k.scope,k.status,k.confidence,k.reason,k.sources,
            k.question_ids,k.created_at,k.updated_at,k.expires_at,
            ARRAY(SELECT input_id FROM jerry_learning.knowledge_inputs WHERE knowledge_id=k.id) AS input_ids,
            (SELECT count(*) FROM jerry_learning.comments WHERE knowledge_id=k.id) AS comment_count
            FROM jerry_learning.knowledge k WHERE '''+visibility+state_filter+''' ORDER BY k.updated_at DESC,k.id DESC LIMIT 2000''',params)
        cards=[dict(r) for r in c.fetchall()]
        for card in cards:
            for source in card['sources']:
                source.pop('text',None)
        c.execute('''SELECT i.id,i.kind,i.title,i.url,i.scope,i.state,i.result,i.created_at,i.processed_at,
                r.status AS run_status FROM jerry_learning.inputs i LEFT JOIN jerry_learning.runs r ON r.id=i.run_id
                WHERE i.author=%s ORDER BY i.id DESC LIMIT 100''',(user,))
        inputs=[dict(r) for r in c.fetchall()] if personal else []
        # All visible entry/input associations, not only the latest 100 queue rows.
        c.execute('''SELECT DISTINCT i.id,i.kind FROM jerry_learning.inputs i
            JOIN jerry_learning.knowledge_inputs ki ON ki.input_id=i.id
            JOIN jerry_learning.knowledge k ON k.id=ki.knowledge_id WHERE '''+visibility+state_filter,params)
        origins=[dict(r) for r in c.fetchall()]
        result={'counts':counts,'loaded':len(cards),'total':sum(counts.values()),'personal':personal,
                'generated_at':datetime.now(timezone.utc).isoformat(),**projection(cards,origins,leader,personal)}
        if personal:
            c.execute("SELECT count(*) AS n FROM jerry_learning.knowledge k WHERE "+visibility+" AND k.status='active' AND k.expires_at>now()",params)
            result['available']=c.fetchone()['n']
            c.execute('SELECT count(*) AS n FROM jerry_learning.reviews')
            result['reviewed_questions']=c.fetchone()['n']
            c.execute("SELECT count(*) AS n FROM public.jerry_gpt_chats WHERE role='user'")
            result['questions']=c.fetchone()['n']
            c.execute('''SELECT id,kind,status,reviewed,accepted,pending,spent_usd,budget_usd,error,created_at,updated_at,finished_at
                         FROM jerry_learning.runs ORDER BY created_at DESC LIMIT 20''')
            result['runs']=[dict(r) for r in c.fetchall()]
            c.execute("SELECT key,value FROM jerry_learning.settings WHERE key IN ('scheduler','last_wake')")
            result['settings']={r['key']:r['value'] for r in c.fetchall()}
            c.execute('''SELECT to_char(a.created_at AT TIME ZONE 'Asia/Shanghai','YYYY-MM-DD') AS day,
                    count(*) FILTER(WHERE a.action='active' OR (a.action='feedback-distilled' AND a.detail->>'after_status'='active')) AS learned,
                    count(*) FILTER(WHERE a.action='pending') AS proposed,
                    count(*) FILTER(WHERE a.action='feedback-distilled') AS revised
                FROM jerry_learning.audit a JOIN jerry_learning.knowledge k ON k.id=a.knowledge_id
                WHERE '''+visibility+''' AND a.created_at>now()-interval '30 days'
                GROUP BY day ORDER BY day''',params)
            result['timeline']=[dict(r) for r in c.fetchall()]
            c.execute('''SELECT a.id,a.action,a.created_at,k.id AS knowledge_id,k.title
                FROM jerry_learning.audit a JOIN jerry_learning.knowledge k ON k.id=a.knowledge_id
                WHERE '''+visibility+' ORDER BY a.id DESC LIMIT 30',params)
            result['events']=[dict(r) for r in c.fetchall()]
            result['inputs']=inputs
        return result
