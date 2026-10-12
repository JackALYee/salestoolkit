# Sub-memory — Jerry's online learning

Parent: `../sub-memory.md`. Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.

## Working memory — 2026-10-12

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W1 | state | deploy | resuming review comments | Comment threads, independent re-distillation and shared daily budget implemented; 34 learning tests plus portal/resource checks passed; local browser flow verified; deployment pending | ../scripts/test_learning.py; README.md | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | platform,verification | converting a past answer into reusable knowledge | Require independent curated or cited web evidence; prior model output alone is not evidence | engine.py | stable |
| R2 | rule | platform | learning from another user's conversation | Preserve source visibility floors in storage, UI and retrieval; reviewer access is not leadership clearance | store.py; ../scripts/test_learning.py | stable |
| R3 | rule | deploy,verification | claiming that daily learning works online | Verify saved cards and completed runs plus installed cloud Cron jobs; a daemon or health endpoint alone is insufficient | README.md | stable |
| R4 | rule | platform | resuming an interrupted review | Use durable question checkpoints, transaction-scoped claims, expiring row leases and spending reservations; never mark failed batches reviewed | store.py | stable |
| R5 | rule | privacy | classifying learned monetary or confidential information | Model labels are insufficient; deterministic storage, migration and retrieval restrictions cover facts, titles, review notes and evidence | store.py; engine.py; ../scripts/test_learning.py | stable |
| R6 | rule | platform,privacy | learning from reviewer feedback | Comments guide revisions but are not independent evidence; preserve visibility, discard revisions when newer comments arrive, and never reactivate retired entries | store.py; engine.py; ../scripts/test_learning.py | stable |
| F1 | fact | platform | explaining how Jerry improves | The reservoir improves retrieval and answer grounding, not provider model weights or program code | README.md | stable |

## Short-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E4 | episode | platform | resuming comment-driven learning | User requested comments on Needs review entries so Jerry can distill feedback; use the hosted worker and shared daily allowance | README.md | consolidating |
| E1 | episode | platform | reviewing the first daily learning implementation | User selected all users' Q&A with confidential entries restricted; schedule is 02:00 Asia/Shanghai and initial log catch-up is automatic | README.md | consolidating |

### E1 — Deployment verification in progress

24 learning tests passed, including four against a disposable local PostgreSQL 16
cluster. Existing portal (45), recovery (7), identity, and resource/version (33)
checks passed. The static site built and the knowledge page's removal control was
verified with synthetic local entries. Test servers and the test database were stopped.

Production `2dc589c` reports version `10.2.2`. Both named Supabase Cron jobs are active;
the resume job succeeded at 08:55 UTC and pg_net recorded HTTP 202 for wake requests
at 08:55 and 09:00 UTC. The UI confirms the last wake. The initial batch was interrupted
by the follow-up deployment; its 0.5 USD reservation remains and its lease expires at
09:02:10 UTC, with no questions incorrectly marked reviewed. Do not deploy further
cosmetic changes while verifying the initial batch; each restart may defer work until
lease recovery. No production conversation content was exported.

### E2 — Grounding refinement and verified first entries

The first 20 questions produced ten overly broad proposals, all correctly held
pending because evidence did not support every bundled claim. The next batch
brought the verified snapshot to 40 questions, one active source-backed card and
19 pending proposals. The active entry includes actual web citations plus curated
references; confidentiality restrictions were visible on the pending cards.

Commit `4c61e36` makes extraction atomic, allows the verifier to retain only an
independently supported subset with a narrow title, and retrieves curated evidence
per candidate using uncommon English terms and Chinese bigrams. Its /healthz
version/commit were verified. After this deployment, the exact interrupted run
lease was expired through an audited conditional update (matching run ID, owner,
40-question checkpoint and timestamp); no reviews, cards or source conversations
were deleted. The hosted worker resumes from that checkpoint. Historical catch-up
is still in progress, not claimed complete.

All 24 learning tests passed against the disposable database after the refinement,
including the live chat API's use of learned context with server-derived clearance.
Local preview and database processes are stopped. Development did not run real
learning locally. Production uses the existing hosted database and AI provider.

For docs/test-only follow-ups, `[skip render]` in the commit message avoids restarting
the ongoing review; official support is documented at https://render.com/docs/deploys.

Final live check at 17:18 China time: **80 / 808 questions reviewed, 4 active entries,
36 pending proposals, estimated spend US$1.80**. The refined algorithm has therefore
completed additional batches in production. The full historical review continues
online; it is not complete yet. Last visible cloud wake was 17:15 China time.

### E3 — Commercial confidentiality safeguard

A live CAN cost-comparison card contained monetary amounts but was labelled company
knowledge. Commit `0d963d3` adds deterministic monetary and commercial restrictions
to the model review and database access filters. Non-leadership retrieval and the
knowledge page exclude mislabelled entries; startup relabels older entries as
leadership-only and records an audit event. The checks cover titles, facts, review
notes and source evidence, including common English and Chinese pricing terms.

All 26 learning tests passed, including disposable PostgreSQL checks that deliberately
mislabel a pricing card, verify ordinary users cannot see or retrieve it, then verify
startup repairs its visibility. Test database is stopped. Production /healthz verified `0d963d3` / `10.2.2` in strict
login mode. The authenticated knowledge page now labels both CAN commercial
comparison cards LEADERSHIP ONLY, confirming the migration on live records.

Before this safeguard deployment, the 17:26 China snapshot showed 120 of 808 questions
reviewed, 11 active entries and 49 pending proposals, estimated cost US$2.87.

Final snapshot at 17:27 China: **140 / 808 questions reviewed, 13 active entries,
57 pending proposals, US$3.07 estimated spend**. Remaining catch-up continues online.
Screenshot: `../../jerry-learning-live.jpg`. Last cloud wake shown: 17:25 China.

### E4 — Comments that feed hosted learning

Added authenticated, same-origin comment endpoints and a comment form on pending
entries. Feedback is persisted in private Postgres and independently reverified by
the hosted learner. Comments do not count as proof; verified revisions update the
same entry and retain history. Confidential feedback tightens visibility immediately.
Feedback shares the daily allowance and continues through the cloud resume job.

34 tests passed, including comment identity/access checks, duplicate submissions,
privacy, shared budgets, carryover, interrupted leases, newer-comment races and
retirement during review. Existing portal (45) and resource/version (33) checks passed.
Local browser testing verified draft preservation, escaped HTML, saved comments, and
transition to active knowledge using synthetic evidence with no real model call.
Production verification is pending. Version 10.2.3.
