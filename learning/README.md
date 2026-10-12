# Jerry's online learning reservoir

The deployed website reviews all users' Q&A and distills reusable knowledge into
its existing hosted Postgres database. This is evidence-backed retrieval and
answer improvement, not neural-network weight training or automatic code edits.

## Runtime

1. The first deployment queues the existing log. Each review claims a ten-minute
   renewable lease and processes 20 questions per batch. A question is paired with
   its own next assistant answer, bounded by the next question and user identity.
2. Claude Sonnet 4.6 extracts up to ten small, independently checkable facts or domain answering lessons.
   Raw conversations are untrusted, redacted data. A separate evidence-review call
   checks claims against curated repository excerpts and actual hosted web-search
   citations. Previous assistant answers are never treated as proof. Mixed proposals are narrowed to
   supported factual subsets, with correspondingly narrow titles. Curated retrieval
   selects evidence per claim, balances coverage, ignores common words and uses
   Chinese bigrams as well as English terms.
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
- Monetary and confidential material has an additional deterministic restriction
  across titles, facts, review notes and evidence. Database retrieval excludes
  misclassified entries for ordinary users, and startup repairs older labels with
  an audit record.
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

## Reviewer comments

Pending entries have a comment thread and a **Send for AI review** form. Approved
Jerry Log reviewers can comment only on entries they can already read. Comments
and subsequent revisions inherit the entry's access restrictions. The form defaults
to leadership-only feedback; opting out is explicit. Monetary/confidential terms
also tighten visibility before saving. Credentials and contact identifiers are
redacted. Comments are durable in the private database with an author and timestamp.

The hosted worker gives feedback priority after its current batch group. It distills
one revised atomic claim from the proposal and comments, then independently checks
fresh curated/web evidence. Comments are guidance, not factual proof or permission
to change Jerry's instructions. Supported revisions update the same entry, retaining
its original question IDs, comment history and audited prior contents. Unsupported
revisions stay pending with the reason shown in the thread. Active entries retain
the thread for provenance; new comments are limited to pending entries.

Feedback and daily Q&A reviews share the existing US$5 estimated daily allowance;
they do not each get a separate US$5 budget. Unprocessed feedback carries forward
to the next daily allowance. The cloud resume job also wakes for newly saved
comments. Failed model calls leave comments unprocessed and use the existing retry
controls. Requests have per-author idempotency keys, a 2,000-character limit,
20 comments per author per hour, and at most 20 unprocessed comments per entry.

If another comment arrives during AI review, the stale revision is discarded and
the complete feedback is rechecked. Removing an entry cancels waiting feedback and
an in-flight review cannot restore it. Browser refresh preserves drafts and expanded
threads. No model call or worker is enabled by running the local preview.

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
