# Sub-memory — Sales Toolkit website / Jerry Log

Parent: `../memory.md`. Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.
Query by trigger and domain. Working state must be verified each session.

## Working memory — 2026-10-12

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W1 | state | platform | resuming Jerry Log recovery and Jimmy access | Completed: production de02e6e / 10.1.1 verified; authenticated portal displays 808 questions across 31 users | E1 | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | platform,verification | Jerry Log reports that the server cannot be reached | Check authenticated data endpoints; the sign-in redirect and health endpoint alone do not verify log data | E1 | stable |
| R2 | rule | platform | recovering a cached Postgres connection | Handle InterfaceError as well as OperationalError and clear cached None; persistent portal failure must be HTTP 503 rather than empty success | scripts/test_jerrylog_recovery.py | stable |
| F1 | fact | platform | granting Jerry Log access to a VIP | VIP model access and company-wide log review are separate; Jimmy is in EXTRA_VIP_EMAILS and EXTRA_JERRY_LOG_EMAILS, without leadership pricing clearance | login.py | stable |
| F2 | fact | deploy | publishing this website | Push to origin/main triggers Render; synchronize the app.py banner and server.py APP_VERSION, run scripts/test_resource_links.py, then verify /healthz | E1 | stable |

## Short-term memory

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

- [Jerry's online daily learning](learning/sub-memory.md) — evidence review, private
  reservoir, visibility, hosted schedule, checkpoints and production verification.
