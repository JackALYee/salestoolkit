# Toolkit authentication checks

## Working memory — 2026-10-27

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W-MS | state | platform,deploy | continuing Microsoft Authenticator rollout | OIDC 40 checks and HTTP route 19 checks pass with a mocked provider. Existing login-mode, leadership and bootstrap tests pass. Microsoft claims do not add VIP/log/personal-dashboard access. | test_ms_auth.py; test_ms_routes.py | volatile |


Uses `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R-MS | rule | platform | adding Microsoft sign-in to a protected website | Authentication must preserve existing authorization; staff sign-in never automatically creates administrator or Jerry reviewer access | Microsoft integration 2026-10-27 | stable |

## Short-term — Microsoft sign-in

### E-MS — 2026-10-27

OIDC 40 checks and HTTP route 19 checks pass with a mocked provider. Existing login-mode, leadership and bootstrap tests pass. Microsoft claims do not add VIP/log/personal-dashboard access.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-MS | episode | platform,verification | enabling Microsoft Authenticator | OIDC 40 checks and HTTP route 19 checks pass with a mocked provider. Existing login-mode, leadership and bootstrap tests pass. Microsoft claims do not add VIP/log/personal-dashboard access. | test_ms_auth.py; test_ms_routes.py | consolidating |
