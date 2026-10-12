# Sub-memory — Jerry's online learning

Parent: `../sub-memory.md`. Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.

## Working memory — 2026-10-12

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W1 | state | deploy | resuming daily learning rollout | Hosted 4c61e36 / 10.2.2 is live; cloud wakes verified; latest verified snapshot: 80 questions, 4 active entries and 36 pending proposals; full 808-question catch-up continues online | ../scripts/test_learning.py | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | platform,verification | converting a past answer into reusable knowledge | Require independent curated or cited web evidence; prior model output alone is not evidence | engine.py | stable |
| R2 | rule | platform | learning from another user's conversation | Preserve source visibility floors in storage, UI and retrieval; reviewer access is not leadership clearance | store.py; ../scripts/test_learning.py | stable |
| R3 | rule | deploy,verification | claiming that daily learning works online | Verify saved cards and completed runs plus installed cloud Cron jobs; a daemon or health endpoint alone is insufficient | README.md | stable |
| R4 | rule | platform | resuming an interrupted review | Use durable question checkpoints, transaction-scoped claims, expiring row leases and spending reservations; never mark failed batches reviewed | store.py | stable |
| F1 | fact | platform | explaining how Jerry improves | The reservoir improves retrieval and answer grounding, not provider model weights or program code | README.md | stable |

## Short-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
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
