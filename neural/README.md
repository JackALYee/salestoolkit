# Jerry Neural Observatory

The online personal dashboard is `/neural`, restricted server-side to the canonical
`jcyi@streamax.com` identity. `/network` and Jerry's existing `/api/ecosystem?focus=…`
iframe show the neural-style product and knowledge network to signed-in users,
with only active, unexpired knowledge allowed by their clearance.

This visualizes evidence-backed retrieval knowledge, not neural-network weights.
The design takes conceptual inspiration from the central-hub / connected-notes
interaction in `luoluo-121/neural-creator-dashboard`. Its current source and media
are not copied or bundled; this renderer and application are original.

## What the graph means

- Conversations: real question IDs recorded by the existing daily learner.
- Websites: a submitted public page with citations from that page (www aliases
  and trailing slashes are normalized). This does not crawl a whole domain.
- Supplied knowledge: owner-supplied notes and curated repository references.
- Internet research: real web citations obtained by the hosted research tool.

Routes overlap: one card can be distilled from a chat and checked against both a
curated reference and internet evidence. Counts beside routes are counts of loaded
cards with that provenance, not four disjoint totals. The graph loads at most
2,000 latest visible cards; the overview draws up to 160 at once. Search narrows
that loaded set. The list shows up to 500 matches. The displayed coverage makes
these limits explicit; headline totals query the entire authorized reservoir.

Product links come from `topology.py`. Learned-card-to-product links mean a named
concept appears in the card; they do not assert new compatibility. Evidence edges
mean the stored card cites the source. Node positions and glow are presentation,
not confidence, intelligence, neural training, or actual live signal traffic.

The 30-day chart uses persisted audit events in China time. It counts additions
and supported revisions, plus pending proposals; it is not a historical count of
currently active cards. No synthetic history or estimated improvement score is
shown. The activity feed, run states, expiry, confidence and source inspector
provide the underlying evidence. `/learning?entry=<id>` opens a specific card and
its existing comment/re-distillation thread, including older cards beyond the
latest-200 review list.

## Owner-submitted sources

`POST /api/neural/inputs` requires the owner, same-origin JSON, an idempotency UUID,
a 3–180-character title, and at most 12,000 characters of source text. Information
requires at least 30 characters. Ten submissions per hour are allowed. Notes
default to leadership-only use; monetary/confidential terms enforce that floor.
Credentials and contact identifiers are redacted. Public website/research inputs
must be explicitly company-visible and pass the public-topic checks; restricted
material never enters public web search. No server-side arbitrary URL fetch is
performed.

Private Postgres `inputs` and `knowledge_inputs` tables keep the queue and many-to-
many provenance. The hosted worker's `sources` runs use the existing global lease,
retry policy and shared daily US$5 estimated allowance. Source processing is
checkpointed with its cards in one transaction. Duplicate facts retain links to
both inputs without inflating question-review counts or reactivating old entries.
The five-minute Supabase recovery predicate includes waiting inputs, so a source
can resume even if Render was asleep. No desktop process is required.

Public pages/topics use actual hosted-search citation excerpts. A requested page
without matching citations stays `needs_review`. Owner text is separately
extracted and verified against the supplied source and relevant curated material.
Supplied evidence can support internal reference facts only in this source
pipeline, never external claims or normal chat/feedback auto-verification.
Supplied-only cards are explicitly attributed and labelled as not independently
verified. Personal/owner-classified cards remain pending under existing rules.
All candidates retain sensitivity floors, evidence requirements, conflict checks,
expiry and instruction-injection safeguards from `learning/engine.py`.

## Verification

Run `scripts/test_neural.py` and `scripts/test_learning.py` using the app's Python
dependencies. Set `JERRY_LEARN_TEST_DB_URL` only to a disposable localhost database
named `jerry_learning_test` for transaction, graph, idempotency, privacy, source
processing, lease recovery and shared-budget checks. Tests use mocked model output.
Run the existing portal/resource checks and static build as well. Inspect desktop
and phone views, search, trace expansion, source submission, retained drafts, and
review links. After publishing, verify `/healthz`, the authenticated personal
network, the installed online schedule and a real submitted-source outcome.
