"""HTTP-level Microsoft sign-in regression checks. No real credentials/network."""
import os
import pathlib
import sys
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ['AUTH_SECRET'] = 'isolated-test-only-signing-key'
from fastapi.testclient import TestClient
import server

checks = 0
def check(condition, label):
    global checks
    assert condition, label
    checks += 1

client = TestClient(server.app, base_url='https://streamax-salestoolkit.com')
with patch.dict(os.environ, {'MS_TENANT_ID':'', 'MS_CLIENT_ID':'', 'MS_CLIENT_SECRET':''}):
    r = client.get('/login?next=/jerry')
    check(r.status_code == 200 and 'Sign in with Microsoft' in r.text, 'Microsoft entry visible')
    check('awaiting company setup' in r.text, 'honest pending state')
    check(r.text.index('Sign in with Microsoft') < r.text.index('id="email"'), 'Microsoft first')
    r = client.get('/auth/microsoft/start?next=/jerry', follow_redirects=False)
    check(r.status_code == 302 and 'next=/jerry' in r.headers['location'], 'unconfigured keeps destination')
    check('no-store' in r.headers['cache-control'], 'auth redirects not cached')
with patch.dict(os.environ, {'MS_TENANT_ID':'11111111-2222-3333-4444-555555555555',
        'MS_CLIENT_ID':'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee','MS_CLIENT_SECRET':'test-only'}):
    r = client.get('/auth/microsoft/start?next=/jerry/log', follow_redirects=False)
    check(r.status_code == 302 and r.headers['location'].startswith('https://login.microsoftonline.com/'), 'provider redirect')
    cookie = r.headers['set-cookie']
    check(all(s in cookie for s in ['HttpOnly', 'Secure', 'SameSite=lax']), 'secure state cookie')
    with patch.object(server._ms,'complete',return_value=('staff@streamax.com','/jerry','')):
        r = client.get('/auth/microsoft/callback?code=fake&state=fake',follow_redirects=False)
    check(r.status_code == 302 and r.headers['location'] == '/jerry', 'successful provider result')
    check('stmx_session=' in r.headers['set-cookie'], 'existing toolkit session established')
    check('Max-Age=0' in r.headers['set-cookie'], 'state cookie consumed')
    check(client.get('/api/me').json()['user'] == 'staff@streamax.com', 'same identity on protected API')
    check(client.get('/jerrylog', follow_redirects=False).status_code == 403, 'no extra log permissions')
    check(client.get('/neural', follow_redirects=False).status_code == 403, 'personal dashboard stays restricted')
    check(client.get('/api/me').json()['is_vip'] is False, 'no extra VIP permissions')
    check(client.get('/login?next=/account',follow_redirects=False).headers['location'] == '/account', 'signed-in deep link')
    check(client.get('/login?next=//evil.example',follow_redirects=False).headers['location'] == '/', 'signed-in open redirect blocked')
    client.cookies.clear()
    with patch.object(server._ms,'complete',return_value=('','/jerry','Please try again.')):
        r = client.get('/auth/microsoft/callback?code=bad&state=bad',follow_redirects=False)
    check('stmx_session=' not in r.headers.get('set-cookie',''), 'failure grants no session')
    check('Max-Age=0' in r.headers['set-cookie'], 'failure clears state')
    r = client.get('/auth/microsoft/callback?error=access_denied&error_description=PROVIDER_PRIVATE_DETAIL',follow_redirects=False)
    check('PROVIDER_PRIVATE_DETAIL' not in r.headers['location'], 'raw provider error not exposed')
print(f'Microsoft HTTP routes: {checks} checks passed.')
