"""Retired Microsoft and pending DingTalk routes must never grant identity."""
import os
import pathlib
import sys
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ['AUTH_SECRET'] = 'isolated-test-only-signing-key'
from fastapi.testclient import TestClient
import server

checks = 0
def check(ok, why):
    global checks
    assert ok, why
    checks += 1

client = TestClient(server.app, base_url='https://streamax-salestoolkit.com')
with patch.dict(os.environ, {'MS_TENANT_ID':'11111111-2222-3333-4444-555555555555',
        'MS_CLIENT_ID':'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee','MS_CLIENT_SECRET':'test-only',
        'DINGTALK_CLIENT_ID':'test-only', 'DINGTALK_CLIENT_SECRET':'test-only', 'DINGTALK_CORP_ID':'test-only'}), \
        patch.object(server._ms, 'begin', side_effect=AssertionError('Retired provider contacted')), \
        patch.object(server._ms, 'complete', side_effect=AssertionError('Retired callback accepted')):
    r = client.get('/login?next=/jerry')
    check(r.status_code == 200 and '钉钉扫码登录' in r.text, 'DingTalk entry visible')
    check('awaiting it setup' in r.text.lower(), 'honest pending state')
    check('Microsoft' not in r.text and 'Authenticator' not in r.text, 'retired UI absent')
    check('next=/jerry' in r.text and 'id="email"' in r.text, 'deep link and password form retained')
    r = client.get('/auth/dingtalk/start?next=/jerry')
    check(r.status_code == 200 and '/login?next=/jerry' in r.text, 'waiting page keeps target')
    check('disabled' in r.text and 'company setup and activation' in r.text, 'scan cannot start before setup')
    check('set-cookie' not in r.headers, 'waiting page creates no session')
    check('no-store' in r.headers['cache-control'], 'waiting page not cached')
    for path in ['/auth/dingtalk/callback?authCode=fake&state=fake&email=owner@streamax.com',
                 '/auth/microsoft/callback?code=fake&state=fake&error_description=PRIVATE_ERROR']:
        r = client.get(path, follow_redirects=False)
        check(r.status_code in (410,503), 'callback rejected')
        check('stmx_session=' not in r.headers.get('set-cookie',''), 'callback grants no session')
        check('fake' not in r.text and 'PRIVATE_ERROR' not in r.text, 'callback input not reflected')
    r = client.get('/auth/microsoft/start?next=/jerry', follow_redirects=False)
    check(r.status_code == 302 and r.headers['location'] == '/auth/dingtalk/start?next=/jerry', 'old entry redirects internally')
    for target in ['//evil.example', 'https://evil.example', '/\\evil.example']:
        r=client.get('/auth/dingtalk/start',params={'next':target})
        check('evil.example' not in r.text, 'unsafe return rejected')
    check(client.get('/auth/microsoft/status').json()['status'] == 'retired', 'retired even if configured')
    check(client.get('/auth/dingtalk/status').json()['available'] is False, 'secrets alone cannot activate placeholder')
    check(client.get('/api/me').status_code == 401, 'anonymous remains anonymous')
    check(client.get('/jerrylog',follow_redirects=False).status_code == 302, 'log still gated')
    with patch.object(server._login, 'verify_streamax_credentials', return_value=(True,'Success')):
        r=client.post('/api/login',json={'email':'staff@streamax.com','password':'test-only'})
    check(r.status_code == 200, 'existing password path works')
    check(client.get('/api/me').json()['user'] == 'staff@streamax.com', 'existing session identity preserved')
    check(client.get('/api/me').json()['is_vip'] is False, 'no automatic VIP')
    check(client.get('/jerrylog',follow_redirects=False).status_code == 403, 'ordinary staff have no log permission')
    check(client.get('/login?next=/jerry',follow_redirects=False).headers['location'] == '/jerry', 'signed-in return path')
import logging
record = logging.LogRecord('uvicorn.access',20,'',0,'%s %s %s %s %s',('ip','GET','/auth/dingtalk/callback?authCode=PRIVATE','1.1',503),None)
server._AuthCallbackLogFilter().filter(record)
check('PRIVATE' not in record.getMessage(), 'callback query redacted from access log')
print(f'Sign-in routes: {checks} checks passed.')
