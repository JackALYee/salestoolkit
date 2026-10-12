# Sub-memory — Jerry's online learning

Parent: `../sub-memory.md`. Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.

## Working memory — 2026-10-12

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W1 | state | deploy | resuming daily learning rollout | Implementation and local database checks pass; hosted scheduler and first review still require production verification | ../scripts/test_learning.py | volatile |

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
