# Sub-memory — Sales Toolkit website / Jerry Log

Parent: `../memory.md`. Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.
Query by trigger and domain. Working state must be verified each session.

## Working memory — 2026-11-05

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W-DingTalkUI | state | platform,deploy | continuing the Microsoft-to-DingTalk replacement | Microsoft OAuth entry and new-session endpoints retired; DingTalk entry and waiting page prepared. Pending callback rejects authentication even with environment settings. Existing password access and role checks retained. Local security tests pass; publication and real provider activation must be checked separately. | templates/sub-memory.md; scripts/sub-memory.md | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | platform,verification | Jerry Log reports that the server cannot be reached | Check authenticated data endpoints; the sign-in redirect and health endpoint alone do not verify log data | E1 | stable |
| R2 | rule | platform | recovering a cached Postgres connection | Handle InterfaceError as well as OperationalError and clear cached None; persistent portal failure must be HTTP 503 rather than empty success | scripts/test_jerrylog_recovery.py | stable |
| F1 | fact | platform | granting Jerry Log access to a VIP | VIP model access and company-wide log review are separate; Jimmy is in EXTRA_VIP_EMAILS and EXTRA_JERRY_LOG_EMAILS, without leadership pricing clearance | login.py | stable |
| F2 | fact | deploy | publishing this website | Push to origin/main triggers Render; synchronize the app.py banner and server.py APP_VERSION, run scripts/test_resource_links.py, then verify /healthz | E1 | stable |

## Short-term memory

### E-DingTalkUI — 2026-11-05

The owner requested replacing Microsoft login with DingTalk QR and explicitly allowed a waiting page until IT is ready. This release implements the waiting UI, retires Microsoft start/callback, preserves safe return paths and existing account permissions, and does not implement DingTalk token exchange or member mapping. No QR success or authenticated DingTalk session is claimed. Older working-state deployment claims were not assumed current.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-DingTalkUI | episode | platform,verification | replacing Microsoft sign-in before DingTalk is configured | Ship truthful pending UI and disable old callbacks; no configuration alone may activate unimplemented authentication. | templates/sub-memory.md; scripts/sub-memory.md | consolidating |


### E-IAM — 2026-10-30 Company DingTalk sign-in

User requested using the existing company IAM DingTalk QR method for Toolkit and Jerry. Inspected the provided page: Streamax IAM with DingTalk and Password. The OA context link cannot be reused as a Toolkit client. Implemented a separately configured, default-off OIDC bridge (RS256, PKCE S256, state/nonce, verified company email and active employee assertion), preserving current clearance and session lifetime. IT must confirm deployed protocol support and register the client. Chinese handoff and preview evidence are linked below; no live scan is claimed.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-IAM | episode | platform,verification | adding company QR sign-in to Toolkit | Use IAM as identity provider with a dedicated application; default disabled until IT configures and validates the claim contract. | DINGTALK_IAM_SETUP_ZH.md; scripts/test_iam_auth.py | consolidating |

### E2 — Trucking homepage logo links, 2026-10-20

The owner requested return navigation from all sites linked on the trucking
homepage. Both the login logo and signed-in toolkit header now link to
`https://www.streamax-trucking.com/`. Version is 10.3.6 (2026); build and all
33 resource/version checks pass. Production health reports commit 65efddc and version 10.3.6; live login HTML has the home link. Unrelated i18n changes remain outside this commit.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E2 | episode | product | verifying the Streamax logo destination | Login and toolkit logos return to the trucking homepage in the same tab | templates/sub-memory.md; app.py | consolidating |


| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E1 | episode | platform,verification | reviewing the October Jerry Log failure | Closed-connection failure reproduced in all three portal reads; recovery, explicit errors, and Jimmy's scoped permissions implemented | scripts/test_jerrylog_recovery.py; scripts/test_jerrylog_portal.py | consolidating |

### E1 — Jerry Log recovery and Jimmy access, 2026-10-12

The user reported the portal shell loaded but showed “Could not reach the server,”
and requested VIP and log access for jimmy@streamax.com. Production /healthz
reported 1bfcbf9 / 9.9.9. A closed psycopg2 connection reproduced an uncaught
InterfaceError in log_search, log_stats, and log_filters; the old liveness probe
caught only OperationalError. The frontend also classified JSON parsing and
session/access failures as connectivity failures. Added one read-only reconnect
retry, safe JSON 503 responses, sign-in/retry UI, and explicit reviewer permission
separate from VIP and leadership. Version advances to 10.1.1 for October.

Pre-existing changes in i18n.py and scripts/test_i18n.py, plus untracked translation
and knowledge files, belong to other work and must not be committed with this fix.

Verification before deployment: 45 access/portal checks passed; 7 recovery tests
(including 12 closed/dropped-connection subcases) passed; identity suite and static
build passed. Browser checks with synthetic data verified the outage/retry path,
recovered table and summary, expired-session sign-in link, and non-JSON HTTP 502
message. No production log contents were exported.

Production verification: bf0e4ff deployed the repair and access change. The signed-in
Safari portal then displayed summary statistics and 808 matching questions across
31 users. The previous “Could not reach the server” error was absent. A follow-up
commit de02e6e synchronized the server's separate APP_VERSION constant with the
header (the previous documentation incorrectly said there was only one version
string); all 33 resource/version checks passed. `/healthz` then confirmed
`10.1.1 (2026)`, commit `de02e6e`, and strict login mode. No Jimmy sign-in was
attempted; his access is verified by the deployed resolver and local HTTP gate tests.

## Subtask memory

- [IAM sign-in verification](iam_verification/sub-memory.md) — protocol assumptions, local preview and release evidence.

- [Curated Jerry knowledge](jerry_gpt_knowledge/sub-memory.md) — construction vehicle source distillation and protected original downloads.

- [Website templates](templates/sub-memory.md) — login logo returns to the trucking homepage.

- [Jerry's online daily learning](learning/sub-memory.md) — evidence review, private
  reservoir, visibility, hosted schedule, checkpoints and production verification.

- [Jerry neural dashboard](neural/sub-memory.md) — personal evolution view, four
  learning routes, original neural renderer and online source intake.

## Short-term — Microsoft sign-in

### E-MS — 2026-10-27

Microsoft integration deployed: Toolkit 10.4.7 commit 7fae814; Trucking production 740102f5-37ab-4fca-a19d-c2e89429fd34. 136 Microsoft-specific local checks, 13 live access checks and desktop/mobile UI checks passed. Company Entra configuration and real-account Authenticator acceptance remain pending. Reverify live state next session.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-MS | episode | platform,verification | enabling Microsoft Authenticator | Microsoft integration deployed: Toolkit 10.4.7 commit 7fae814; Trucking production 740102f5-37ab-4fca-a19d-c2e89429fd34. 136 Microsoft-specific local checks, 13 live access checks and desktop/mobile UI checks passed. Company Entra configuration and real-account Authenticator acceptance remain pending. Reverify live state next session. | ms_auth.py; scripts/test_ms_auth.py; scripts/test_ms_routes.py | consolidating |

- [Sign-in tests](scripts/sub-memory.md)

### E-IAM-NoChange — 2026-10-30

The owner selected research without changing IAM. Paused publication and unstaged only this task’s staged files. Direct DingTalk OAuth avoids IAM changes but still needs authorized DingTalk application configuration. A server-side browser broker is not verified because a supported identity-validation contract has not been established. No real employee scan or production change occurred.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-IAM-NoChange | episode | platform | continuing DingTalk login after the no-IAM constraint | Research precedes activation; current OIDC code is an unpublished fallback, not the selected rollout. | DINGTALK_NO_IAM_FEASIBILITY_ZH.md | consolidating |

DingTalk UI references: [templates/sub-memory.md](templates/sub-memory.md); [scripts/sub-memory.md](scripts/sub-memory.md).
