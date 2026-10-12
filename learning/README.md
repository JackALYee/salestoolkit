# Jerry's online learning reservoir

The deployed website reviews all users' Q&A and distills reusable knowledge into
its existing hosted Postgres database. This is evidence-backed retrieval and
answer improvement, not neural-network weight training or automatic code edits.

## Runtime

1. The first deployment queues the existing log. Each review claims a ten-minute
   renewable lease and processes 20 questions per batch. A question is paired with
   its own next assistant answer, bounded by the next question and user identity.
2. Claude Sonnet 4.6 extracts up to ten reusable claims or domain answering lessons.
   Raw conversations are untrusted, redacted data. A separate evidence-review call
   checks claims against curated repository excerpts and actual hosted web-search
   citations. Previous assistant answers are never treated as proof.
3. Supported claims with confidence at least 0.85 become active; unsupported,
   personal, or conflicting entries stay pending. Every card retains question IDs,
   evidence excerpts/digests, sources, dates, expiry, visibility and an audit event.
4. Future Jerry answers retrieve at most eight matching, active, unexpired cards,
   constrained by server-side user clearance. Learned reference data cannot change
   the curated instructions, identity, permissions, or executable code.
5. Supabase Cron wakes Render at 18:00 UTC (02:00 Asia/Shanghai). A five-minute
   recovery check wakes it only when work is queued, a lease expired, or a daily
   review is missing. The hosted worker continues batches independently of any
   desktop. Atomic checkpoints and unique question IDs prevent duplicate review.

The scheduler creates two named jobs, `jerry-learning-daily` and
`jerry-learning-resume`. Its narrowly scoped signing key is stored in Supabase
Vault. Requests carry timestamped HMAC signatures valid for five minutes and can
only wake the existing worker; they cannot read data or manage entries. Installing
Cron/pg_net/Vault requires the existing database role's extension privileges. The
knowledge page reports installation failure rather than claiming a schedule exists.

## Privacy and controls

- The `jerry_learning` schema is private; PUBLIC, anon and authenticated roles have
  no schema or table access. API queries enforce visibility before returning data.
- A leadership or flagged source conversation sets a leadership visibility floor.
  Individual material remains owner-restricted and cannot activate automatically.
  Confidential curated evidence also raises the floor. Jimmy's log-review access
  does not grant leadership access to learned entries or management controls.
- Restricted claims are never sent to public web search. Their external claims
  remain pending unless independently verified evidence is available. All logs are
  reviewed with the same organization AI provider already used by Jerry.
- Credentials, email addresses and long identifiers are redacted before distillation.
  This complements, rather than replaces, source visibility and model privacy checks.
- `/learning` shows progress, visible cards, citations and expiry. Leadership can
  retry failed runs and remove entries from use. All mutations are audited and
  require same-origin authenticated JSON requests. No pending card is auto-approved
  because a reviewer clicked retry.
- External facts expire within 30 days (the verifier can choose seven days for
  volatile facts); stable curated concepts within 180 days. Expired cards are not
  retrieved. The process does not currently re-research expired cards automatically.
- Initial spending limit: estimated US$20. Daily limit: US$5. Reservations precede
  provider calls and survive uncertain outcomes; a stopped run leaves questions
  unreviewed. Usage estimates use Sonnet's configured rates, not billing invoices.

## Configuration and operation

Existing hosted variables: `JERRY_GPT_DB_URL`, `ANTHROPIC_API_KEY`, `AUTH_SECRET`.
`RENDER_GIT_COMMIT` restricts worker startup to the deployed service. Local imports
and tests never start real learning.

Optional: `JERRY_LEARN_BACKFILL_BUDGET` / `JERRY_LEARN_DAILY_BUDGET` (clamped to
US$100 per run); `JERRY_LEARN_ENABLED=0` stops worker startup. To fully suspend the
schedule, also deactivate both named Cron jobs in Supabase. Never expose database
URLs, the provider key, or the Vault signing secret to the browser.

Inspect `/api/learning` through an approved authenticated account for scheduler
installation, durable run status, counters and safe failure descriptions. Three
consecutive batch failures park a run until a leadership retry. Each successful
batch resets the failure count. Provider failures never mark questions reviewed.

## Verification

`python scripts/test_learning.py` covers privacy floors, evidence requirements,
redaction, prompt injection, timezone boundaries, signed wake expiry, HTTP access,
CSRF, spending failures, and nonblocking retrieval failure. Set
`JERRY_LEARN_TEST_DB_URL=postgresql://127.0.0.1:55439/jerry_learning_test` for four
additional database tests: pairing, lease recovery, deduplication, atomic review,
visibility, expiry, removal and budget reservations. This option accepts only a
local disposable database with that exact name.

Also run the existing Jerry Log portal, recovery, identity and resource-link tests,
then build the static site. Production verification must observe actual saved
cards, completed runs and the two installed Cron jobs; a healthy website alone
is insufficient.

Provider and scheduler references:
- https://supabase.com/docs/guides/functions/schedule-functions
- https://supabase.com/docs/guides/cron/quickstart
- https://supabase.com/docs/guides/database/vault
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
