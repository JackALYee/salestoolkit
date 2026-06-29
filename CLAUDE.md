# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app is

A single-tenant Streamlit app deployed to Streamlit Community Cloud as the **Streamax Sales Toolkit** — internal tooling for the Trucking BU sales org. Entry point is `app.py`. The app combines a heavyweight HTML/JS UI (rendered inside `streamlit.components.v1.html`) with native Streamlit pages for the interactive features. SMTP-credential login gates access; a signed cookie keeps sessions alive across reloads.

## ⚠️ ALWAYS bump the version + date on every change

The main header (`app.py`, the `header-meta` div — search `Version `) shows `Version X.Y.Z • 货运产品线 Trucking BU • <Month Year>`. **Every time you make a change to this repo, before finishing, update that line in the same edit batch.** This is a hard, standing rule — never skip it, never ask whether to do it.

**Version scheme `X.Y.Z`:**
- **X** — major version. Bump only on a big milestone, and only when the user explicitly asks. Otherwise leave it.
- **Y** — Sales Toolkit change counter. Increment by 1 whenever the change touches the toolkit surface: `app.py`, `streamaxpedia_app.py`, `terminology_db.py`, `prospecting_flow.py`, `discovery_meeting.py`, `presentation.py`, `value_calculator.py`, `sales_onboarding.py`, `login.py`, `auth.py`, the email/drip tooling, or shared assets/styles.
- **Z** — Jerry GPT change counter. Increment by 1 whenever the change touches the Jerry GPT surface or its sibling AI modules: `jerry_gpt.py`, `jerry_gpt_knowledge/*`, `pm_skills.py`/`pm_skills/`, `file_io.py`, `downloads.py`/`assets/downloads/`, `product_images.py`/`assets/products/`, `usage_logger.py`, `chat_history.py`. (Jack GPT changes — `jack_gpt.py` etc. — also bump **Z**, since it's an AI chat surface.)

Rules of thumb:
- A change that spans both surfaces bumps **both** Y and Z (+1 each).
- A change to neither (docs-only, CLAUDE.md, requirements housekeeping) needs no bump — but if in doubt, bump the surface most affected.
- One logical change = +1 (not +1 per file touched).
- **Always** update the trailing `<Month Year>` to the current month/year of the change (e.g. `June 2026`).

The version string lives in exactly one place (the `header-meta` div) — that's the single source of truth; don't duplicate it elsewhere.

## Common commands

```bash
# Local development
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then fill in real keys
streamlit run app.py

# Deploy
git push origin main           # Streamlit Cloud auto-deploys from main

# Roadmap scraper (separate venv — playwright is heavy, not a runtime dep)
python3 -m venv .scrape_venv
source .scrape_venv/bin/activate
pip install playwright pdfplumber python-docx openpyxl python-pptx
playwright install chromium
python scrape_roadmap.py                # capture pages + downloads from the portal
python scripts/distill_downloads.py     # re-distill _scrape_dump/downloads/ → 09_roadmap_documents.md
```

There are no tests or linters in this repo. `requirements.txt` is the only runtime dependency manifest; Streamlit Cloud installs from it automatically.

## High-level architecture

### Render pipeline — two paths in one app

`app.py` checks `st.query_params["view"]` early and chooses between two completely different rendering strategies:

1. **Default toolkit (no `?view=`)** — assembles a giant HTML string by concatenating `html_head` + the `content` HTML strings exported by each module (`streamaxpedia_app.py`, `prospecting_flow.py`, `discovery_meeting.py`, `presentation.py`, `value_calculator.py`, `dripmailer.py`, plus `email_tool_content` inline) + `html_tail`, then renders the whole thing through `components.html(..., height=1800, scrolling=True)`. Each module's `content` is a static HTML+JS string with no Python interactivity — navigation between tabs is pure client-side JavaScript inside the iframe.

2. **`?view=jerry_gpt`** — bypasses the components.html assembly entirely and calls `jerry_gpt.render()` for a native Streamlit chat UI. This is the only way to embed live API-call interactivity, because Streamlit widgets can't live inside a `components.html` iframe.

The launch button inside Streamaxpedia uses `<a target="_top" href="?view=jerry_gpt">` so the click escapes the iframe and navigates the parent frame, triggering a Streamlit rerun that picks up the query param. The same pattern is used for `?logout=1`.

### Authentication and clearance — three layers

1. **SMTP credential check** (`login.py`): user types `@streamax.com` email + password; `verify_streamax_credentials()` attempts SMTP-SSL login against `mail.streamax.com:465` as the auth check. Easter-egg shortcut accounts (`jerry_test`, `hekun_test`, etc.) bypass SMTP.

2. **Cookie-based persistence** (`auth.py`): on successful login, `persist_login()` writes a signed cookie (`HMAC(user, expiry, AUTH_SECRET)`) via `extra-streamlit-components.CookieManager`. On every script run, `restore_session()` validates the cookie and rehydrates `st.session_state["authenticated"]`, `["user_name"]`, `["is_leadership"]`. Without this layer, every page reload or `?view=jerry_gpt` navigation forces re-login because Streamlit's session_state is per-WebSocket.

3. **LEADERSHIP clearance** (`login.py`): `LEADERSHIP_EMAILS` is a frozenset of streamax.com addresses that may access Streamax-internal pricing inside Jerry GPT. `resolve_leadership()` and `resolve_special_relationship()` are case-insensitive lookups that also map easter-egg display names → canonical emails. `SPECIAL_RELATIONSHIPS` is a separate map (Jerry himself, Kun He, Rui Wang) that controls address form and one-time greetings — orthogonal to leadership.

Important: the cookie manager has an async-cookie quirk. `extra_streamlit_components.CookieManager(key=...)` is a Streamlit widget and **cannot be wrapped in `@st.cache_resource`** (raises `CachedWidgetWarning`). It also **cannot be instantiated twice in the same run** with the same key. `auth.py` works around both by storing the manager in `st.session_state` and re-creating it once per run via `restore_session()` popping the stored marker. Anything that needs the manager later in the same run (e.g., `persist_login`) reuses the cached instance.

### Jerry GPT — the chat subsystem

`jerry_gpt.py` is its own self-contained subsystem (~1500 lines) that runs whenever `?view=jerry_gpt` is in the URL. Key concepts:

**Knowledge base** lives in `jerry_gpt_knowledge/` as numbered markdown files. `_load_system_blocks()` reads every `*.md` file in lexicographic order, concatenates them, and returns a single Anthropic system-prompt block marked with `cache_control: ephemeral`. **Adding a new `.md` file to that directory automatically includes it** — no code change needed. The Streamaxpedia product database (`terminology_db.py`) is also pulled in via `_generate_streamaxpedia_knowledge()` at module load and appended to the same cached block.

**Per-turn clearance block** is built fresh on every API call by `_build_clearance_block()` and appended **after** the cached knowledge block. This is critical: the big knowledge prefix stays cached across users (cheap), while the small clearance suffix varies per-request (user identity, leadership flag, first-turn greeting, special-relationship treatment). Cache hits stay high; per-user behavior stays correct.

**Multi-provider routing (Claude + DeepSeek).** Jerry supports two providers, chosen by the selected model id via `_provider_for()` (ids starting `deepseek` → DeepSeek, else Anthropic). The model catalog `MODEL_OPTIONS` lists **DeepSeek V4 Pro** (id `deepseek-v4-pro`, configurable via secret `JERRY_DEEPSEEK_MODEL`) plus the Claude models. **Access policy:** non-leadership users may use **only DeepSeek** with the org key; Claude models are leadership-only — *unless* a user adds their own Anthropic key in **Settings → Bring your own API key**, which unlocks Claude for them (billed to their key). `_allowed_models()` computes the selectable set; `_resolve_provider_key()` returns the right key (BYO wins → org DeepSeek for all → org Anthropic for leadership). **BYO keys are session-only** — stored in `st.session_state` (`jerry_byo_anthropic_key` / `jerry_byo_deepseek_key`), never persisted to DB/Sheets and never logged. Keys/secrets: `ANTHROPIC_API_KEY` (org Claude, leadership), `DEEPSEEK_API_KEY` (org DeepSeek, everyone). DeepSeek is OpenAI-compatible, reached through the `openai` SDK pointed at `https://api.deepseek.com` (`_run_deepseek_stream`); Claude stays on the Anthropic SDK (`_run_anthropic_stream`) — the two share the same `{text, input, output, cache_read, cache_creation}` return contract so the post-work (history, usage, logging, artifacts, product images, downloads, ecosystem map) is provider-agnostic. **DeepSeek caveats:** no web tools (Anthropic server-side only), no prompt caching, no native image/PDF (those blocks are flattened/omitted; Office files still extract to text); the Anthropic-style system blocks are concatenated into one system message via `_build_deepseek_messages()`. The former VIP/Opus gating was replaced by this leadership-based gating.

**Web browsing**: every Jerry request attaches `WEB_TOOLS` (Anthropic server-side `web_search_20260209` + `web_fetch_20260209`, capped via `max_uses`). Jerry searches/reads the live web for current/external info (competitor moves, pricing, news) and is told via a system-prompt `<interface_capabilities>` note to cite sources and prefer built-in Streamax knowledge for Streamax facts. No client-side tool loop is needed — server tools run on Anthropic's side and the answer text still flows through `stream.text_stream`.

**Continuation / stop-reason handling** in `_submit_message()`: each response streams inside a `while True:` loop. **On Opus 4.8 the old assistant-text-prefill continuation for `max_tokens` returns a 400 (last-assistant-turn prefills are rejected), so it was removed** — a `max_tokens` stop now keeps the partial answer instead of erroring. The loop resumes only on `stop_reason == "pause_turn"` (the server web-tool loop hitting its iteration cap), by echoing `final_message.content` (the trailing `server_tool_use` block tells the API to resume) — never add a "continue" user message. Token usage is accumulated across rounds for the audit log.

**PM skills library** (`pm_skills.py` + bundled `pm_skills/<category>/<skill>/SKILL.md`, 68 skills): the catalog (name + description, ~5K tokens) plus a usage hint are injected into the cached knowledge block. Jerry suggests or applies the matching PM framework and tells the user which skill he used. The catalog is static so it stays cache-stable; full skill bodies are bundled and loadable via `pm_skills.load_skill_body(name)` for future on-demand deep application (not in the base prompt).

**Sales & Marketing skills library** (`marketing_skills.py` + bundled `marketing_skills/<skill>/SKILL.md`, 45 skills from Corey Haines' marketingskills): same mechanism as the PM library — a grouped catalog + usage hint go into the cached system block as `<marketing_skills_library>`, and Jerry applies/suggests the matching marketing or sales playbook (cold-email, prospecting, pricing, copywriting, CRO, SEO, ads, launch, PR, retention, …) and names which one he used. The source repo is **flat** (`skills/<name>/SKILL.md`, no category folders), so `marketing_skills.py` adds a curated `_CATEGORY_BY_SKILL` grouping (unmapped skills fall into "Other Marketing Skills" — new skills appear automatically). The source descriptions are long trigger-keyword lists, so `_trim_desc()` keeps only the first sentence to keep the catalog ~1.6K tokens. Full bodies via `marketing_skills.load_skill_body(name)`. To add/refresh skills, re-copy `SKILL.md` files into `marketing_skills/<name>/` — no code change needed.

**File I/O** (`file_io.py`): bidirectional. **Uploads** — a `st.file_uploader` under the composer accepts images/PDF/Word/Excel/PowerPoint; `build_user_content()` turns them into Anthropic content blocks (images→image, PDF→document both native; docx/xlsx/pptx→extracted text via python-docx/openpyxl/python-pptx). Attachments are sent **only on the turn they're uploaded** — stored history keeps a text-only "attached: …" note, so they aren't re-sent every turn. **Generation** — when the user asks for a document, Jerry emits a fenced ```artifact``` JSON block (schema in `file_io.ARTIFACT_HINT`, injected into the system prompt); `extract_artifacts()` parses it and `render_artifact()` builds a real .docx/.pptx/.xlsx/.pdf (python-docx / python-pptx / openpyxl / reportlab). PDF uses reportlab's built-in `STSong-Light` CID font so Chinese renders without bundling a TTF. `strip_artifacts()` hides the JSON from the displayed answer; a `st.download_button` replaces it (live + replay). Requires `python-docx`, `python-pptx`, `openpyxl`, `reportlab` in requirements.

**Anthropic prompt cache quirk** worth knowing: max 4 `cache_control` breakpoints per request. The knowledge base is a single block with one breakpoint. The clearance block deliberately has no cache_control so it doesn't consume a breakpoint and can vary freely.

### Usage logging — two sinks, never raises

`usage_logger.py` `log_query()` is called once per successful Jerry response. It writes to two sinks:

1. **stdout/stderr** (always): JSON-prefixed line `[JERRY_GPT_LOG] {...}` — visible in Streamlit Cloud's Manage app → Logs.
2. **Google Sheets** (optional): activates only when `st.secrets["gcp_service_account"]` AND `JERRY_GPT_SHEET_ID` are configured. Auto-creates the worksheet tab and header row on first write. The header schema is the `HEADERS` constant — when changing it, existing rows in the sheet will be misaligned and need manual cleanup.

The `_is_pricing_sensitive()` heuristic flags questions matching pricing-related keywords (English + Chinese). Combined with the `is_leadership` column, this gives an audit view: `is_leadership=FALSE AND sensitive_flagged=TRUE` rows are attempted-pricing-access events worth reviewing.

Timestamps are in China Standard Time (UTC+8, fixed offset — China doesn't observe DST). The column is named `timestamp_cn` not `timestamp_utc`.

### Roadmap scraper

`scrape_roadmap.py` runs separately from the deployed app — it's a local Mac-only tool that uses Playwright to log into the internal version portal at `http://10.20.51.20:5173` (Streamax intranet only) and pulls roadmap pages + downloadable documents. Key design notes:

- The 8 sidebar sections are walked by **clicking** the visible Chinese labels (e.g., `路线规划`), not by guessing URLs — the SPA's actual routes are followed implicitly.
- Document downloads aren't `<a href>` links — they're JavaScript cloud-download icons. `_harvest_docs_center()` clicks each category tab, expands all model rows, then clicks every element with `[title*="下载"]` etc. Each click is wrapped in `with page.expect_download() as dl_info:` which **consumes the download event** — so `_save_download()` must be called explicitly inside the with-block, not via the context-level listener (which never fires inside an `expect_download` scope).
- Raw outputs go to `_scrape_dump/` (gitignored). Distilled markdown goes to `jerry_gpt_knowledge/08_roadmap_portal.md` (pages) and `09_roadmap_documents.md` (extracted DOCX/XLSX/PDF/PPTX text). Jerry's loader auto-picks these up on next deploy.

### Module conventions

Each toolkit section (Streamaxpedia, Prospecting Flow, etc.) lives in its own `.py` file and exports a single module-level string named `content` containing the HTML/JS for that tab. `streamaxpedia_app.py` is exceptional in two ways: it builds `content` programmatically from `terminology_db.py` data, and it has its own sub-navigation (Search Engine / Product Matrix / Jerry GPT launch card) inside the iframe.

`terminology_db.py` is the single source of truth for product terms (114+ entries) and validated product architectures (70+ entries). It's imported by both `streamaxpedia_app.py` (for the toolkit UI) and `jerry_gpt.py` (so Jerry knows every SKU + the download URLs for spec sheets/manuals). Updating an entry there propagates to both places on next deploy.

`topology.py` is the single source of truth for the **interactive Ecosystem Map** — a curated force-directed graph (60 nodes / 125 edges) of products, cameras/sensors, capabilities, cloud platforms, solutions, and competitors and how they connect (`cat ∈ capability | device | camera | platform | solution | competitor`). It exposes `TOPOLOGY` + `topology_json` (the data) and `ecosystem_map_html(focus="")` (a self-contained D3 widget for `st.components.v1.html`). Two consumers: `streamaxpedia_app.py` embeds the data into its in-iframe "Ecosystem map" modal (per-term button → opens focused on that term, D3 loaded from cdnjs); `jerry_gpt.py` imports `ecosystem_map_html()` and pops the same map in an `st.dialog`. Jerry offers it by emitting a `[[ECOSYSTEM_MAP]]` / `[[ECOSYSTEM_MAP:Exact Node]]` marker (described in a cached `<interface_capabilities>` block) — `_ECO_RE` strips it from the displayed text via `_clean_display()` and `_render_ecosystem()` turns it into an "Open Ecosystem Map" button. **Edit the graph data only in `topology.py`** so both surfaces stay in sync. The map depends on D3 from `cdnjs.cloudflare.com`; a network that blocks cdnjs renders a blank graph (nothing else is affected).

## Required secrets

`st.secrets` (or `.streamlit/secrets.toml` locally):

- `ANTHROPIC_API_KEY` — org Claude key for Jerry GPT. With Jerry's multi-provider routing this is the **leadership-only** key (Claude models). Optional if `DEEPSEEK_API_KEY` is set (non-leadership users can run on DeepSeek alone).
- `DEEPSEEK_API_KEY` — org DeepSeek key, available to **all** Jerry users; the only org-key model non-leadership may use. Jerry needs at least one of `ANTHROPIC_API_KEY` / `DEEPSEEK_API_KEY`.
- `JERRY_MODEL` — optional, leadership default, defaults to `claude-opus-4-8`
- `JERRY_DEEPSEEK_MODEL` — optional, defaults to `deepseek-v4-pro` (set this to DeepSeek's exact public model name if it differs)
- `JACK_GPT_ANTHROPIC_API_KEY` — required for Jack GPT (Emily-only private workspace). **Intentionally a different key from Jerry's** so the two surfaces are isolated for cost / quota / abuse. `jack_gpt._get_api_key()` does NOT fall back to `ANTHROPIC_API_KEY` — a missing Jack key produces a clean configuration error rather than silently routing Jack's traffic through Jerry's account.
- `JACK_GPT_MODEL` — optional, defaults to `claude-opus-4-8`
- `AUTH_SECRET` — required for session cookie signing (generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `JERRY_GPT_SHEET_ID` + `[gcp_service_account]` table — optional, enables Google Sheets logging for Jerry GPT
- `JERRY_GPT_DB_URL` — optional, enables cross-session chat history for Jerry GPT via Supabase Postgres
- `JACK_GPT_SHEET_ID` (+ optional `[jack_gpt_service_account]` table — falls back to the shared `[gcp_service_account]`) — optional, enables Google Sheets logging for Jack GPT. **Separate Sheet** from Jerry's audit log.
- `JACK_GPT_DB_URL` — optional, enables cross-session chat history for Jack GPT via Postgres. **Separate Postgres URL** and **separate table** (`jack_gpt_chats`) from Jerry's. No fallback to `JERRY_GPT_DB_URL`.

If `JERRY_GPT_SHEET_ID` is absent, the app still works — usage logging falls through to stdout-only.

## Jack GPT — Emily's private workspace

`jack_gpt.py` is structurally similar to `jerry_gpt.py` but with a tighter access model:

- **Whitelist**: `JACK_GPT_WHITELIST = frozenset({"jhsun@streamax.com", "jcyi@streamax.com"})`. Two users only — Emily (jhsun) and Jack himself (jcyi, owner/admin). Even other authenticated Streamax employees who guess the URL get the access-denied screen — this is not a team tool.
- **Routing**: launched from Emily's terminology card in Streamaxpedia (gated to jhsun via `streamaxpedia_app.build_content(user_email)`). The card's "Special Feature → Jack GPT" button opens `?view=jack_gpt`, which `app.py` routes to `jack_gpt.render()`.
- **Knowledge bundle**: lives at `salestoolkit/jack_gpt_knowledge/` (committed to git, ~190KB). Contains `personas/emily.md`, `boundaries/emily.md`, `memory/*.md` (excluding `raw_chats/`), `sources/*.md`, plus `external_skills/streamax-knowledge.md` and `external_skills/sales-automator.md` (the two skill files Jack normally reads from outside the toolkit repo). `jack_gpt._find_jack_gpt_root()` tries the bundled location first, falls back to the canonical `~/Documents/我的档案/jack_gpt/` for local dev.
- **Runtime contract from upstream README**: only the Emily channel files are loaded — `philosophy/`, `internal/`, `personas/jack_self.md`, `boundaries/jack_self.md`, `memory/raw_chats/` are explicitly excluded and **not bundled**. When the upstream `jack_gpt/` content updates, re-run the bundling step (`cp` the same file list from `~/Documents/我的档案/jack_gpt/`); do not add files that aren't on the Emily-channel allowlist.
- **Model + sampling**: `claude-opus-4-8`, `max_tokens=1500`, `temperature=1.0` (Jack needs lexical variety — deterministic sampling produces same-opener responses).
- **Logging + persistence**: mirrors Jerry's pattern but with dedicated side-car modules. `jack_usage_logger.py` writes to Google Sheets (`JACK_GPT_SHEET_ID`); `jack_chat_history.py` persists to Postgres (`JACK_GPT_DB_URL`) using a separate `jack_gpt_chats` table. Both modules are imported with graceful failure — if secrets are missing or the underlying packages aren't installed, Jack still works (just without audit log / cross-session restore). Token usage is accumulated across max-tokens auto-continuations so the logged row reflects the full reply, not just the first segment.
- **⚠️ Plaintext password logging**: `jack_usage_logger.HEADERS` includes a `user_password` column written in plaintext to Google Sheets and to stdout. This was an explicit product-owner decision for the Emily-only workspace and is NOT a bug. Do **not** propagate this column into `usage_logger.py` (Jerry's, which serves the whole team) without an explicit, repeated decision — the risk model is different there. If the decision ever gets revoked, removing the column from `HEADERS` will auto-rewrite the sheet header on the next write; do a manual cleanup of existing rows below it at that point.
