# Toolkit authentication checks

## Working memory — 2026-11-05

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W-DingTalkUI | state | platform,deploy | continuing the Microsoft-to-DingTalk replacement | Microsoft OAuth entry and new-session endpoints retired; DingTalk entry and waiting page prepared. Pending callback rejects authentication even with environment settings. Existing password access and role checks retained. Local security tests pass; publication and real provider activation must be checked separately. | test_ms_routes.py; test_leadership_auth.py | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R-MS | rule | platform | adding Microsoft sign-in to a protected website | Authentication must preserve existing authorization; staff sign-in never automatically creates administrator or Jerry reviewer access | Microsoft integration 2026-10-27 | stable |

## Short-term — IAM sign-in

### E-DingTalkUI — 2026-11-05

The owner requested replacing Microsoft login with DingTalk QR and explicitly allowed a waiting page until IT is ready. This release implements the waiting UI, retires Microsoft start/callback, preserves safe return paths and existing account permissions, and does not implement DingTalk token exchange or member mapping. No QR success or authenticated DingTalk session is claimed. Older working-state deployment claims were not assumed current.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-DingTalkUI | episode | platform,verification | replacing Microsoft sign-in before DingTalk is configured | Ship truthful pending UI and disable old callbacks; no configuration alone may activate unimplemented authentication. | test_ms_routes.py; test_leadership_auth.py | consolidating |


### E-IAM — 2026-10-30

The new IAM suite verifies real RS256 signatures, client/issuer/nonce binding, PKCE, mandatory verified work email and employee status, redirects, transport limits, callback log redaction and existing role gates. Synthetic provider fixtures do not establish compatibility with the live IAM installation.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-IAM | episode | platform,verification | verifying DingTalk IAM login | Thirteen test methods cover the OIDC bridge and HTTP routes; still require real tenant acceptance. | test_iam_auth.py | consolidating |

## Short-term — Microsoft sign-in

### E-MS — 2026-10-27

OIDC 40 checks and HTTP route 19 checks pass with a mocked provider. Existing login-mode, leadership and bootstrap tests pass. Microsoft claims do not add VIP/log/personal-dashboard access.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-MS | episode | platform,verification | enabling Microsoft Authenticator | OIDC 40 checks and HTTP route 19 checks pass with a mocked provider. Existing login-mode, leadership and bootstrap tests pass. Microsoft claims do not add VIP/log/personal-dashboard access. | test_ms_auth.py; test_ms_routes.py | consolidating |

### E-IAM-NoChange — 2026-10-30

The owner selected research without changing IAM. Paused publication and unstaged only this task’s staged files. Direct DingTalk OAuth avoids IAM changes but still needs authorized DingTalk application configuration. A server-side browser broker is not verified because a supported identity-validation contract has not been established. No real employee scan or production change occurred.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-IAM-NoChange | episode | platform | continuing DingTalk login after the no-IAM constraint | Research precedes activation; current OIDC code is an unpublished fallback, not the selected rollout. | ../DINGTALK_NO_IAM_FEASIBILITY_ZH.md | consolidating |

DingTalk UI references: [test_ms_routes.py](test_ms_routes.py); [test_leadership_auth.py](test_leadership_auth.py).
