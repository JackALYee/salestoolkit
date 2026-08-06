# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app is

A single-tenant Streamlit app deployed to Streamlit Community Cloud as the **Streamax Sales Toolkit** — internal tooling for the Trucking BU sales org. Entry point is `app.py`. The app combines a heavyweight HTML/JS UI (rendered inside `streamlit.components.v1.html`) with native Streamlit pages for the interactive features. SMTP-credential login gates access; a signed cookie keeps sessions alive across reloads.

## ⚠️ ALWAYS bump the version + date on every change

The main header (`app.py`, the `header-meta` div — search `Version `) shows `Version X.Y.Z • 货运产品线 Trucking BU • <Month Year>`. **Every time you make a change to this repo, before finishing, update that line in the same edit batch.** This is a hard, standing rule — never skip it, never ask whether to do it.

**Version scheme `X.Y.Z`:**
- **X** — the **current month number** (January = 1 … August = 8 … December = 12). Set it to the month the change is made, so the version reads as a date stamp alongside the trailing `<Month Year>`. It is NOT a semantic major version — don't reserve it for milestones. When the month rolls over, the next change bumps X to the new month (e.g. August `8.14.20` → the first September change becomes `9.15.20`) and Y/Z keep counting up as normal.
- **Y** — Sales Toolkit change counter. Increment by 1 whenever the change touches the toolkit surface: `app.py`, `streamaxpedia_app.py`, `terminology_db.py`, `prospecting_flow.py`, `discovery_meeting.py`, `presentation.py`, `value_calculator.py`, `sales_onboarding.py`, `login.py`, `auth.py`, the email/drip tooling, or shared assets/styles.
- **Z** — Jerry GPT change counter. Increment by 1 whenever the change touches the Jerry GPT surface or its sibling AI modules: `jerry_gpt.py`, `jerry_gpt_knowledge/*`, `pm_skills.py`/`pm_skills/`, `file_io.py`, `downloads.py`/`assets/downloads/`, `product_images.py`/`assets/products/`, `usage_logger.py`, `chat_history.py`, plus the sales-method modules (`marketing_skills.py`/`marketing_skills/`, `sales_process_skills.py`/`sales_process_skills/`, `topology.py`).

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

1. **SMTP credential check** (`login.py`): user types `@streamax.com` email + password; `verify_streamax_credentials()` verifies by attempting an SMTP AUTH login against the backends in `_mail_servers()` — Coremail (`mail.streamax.com:465`, implicit SSL) then Microsoft/Outlook (`smtp.office365.com:587`, STARTTLS) — accepting the login if **either** authenticates, since Streamax mailboxes live on one system or the other. Per-server outcome is logged to stderr as `[LOGIN] …`. ⚠️ The Outlook path only works if that M365 tenant/mailbox still allows **SMTP AUTH (basic auth)** with no MFA/Conditional Access block; Microsoft disables SMTP AUTH by default on modern tenants (error `535 5.7.139` / "disabled for the Tenant", surfaced as `disabled=True`) — which is why **Sign in with Microsoft** (below) exists. Set `MS_SMTP_AUTH=0` to drop the Microsoft SMTP probe once OAuth is live. Easter-egg shortcut accounts (`jerry_test`, `hekun_test`, etc.) bypass SMTP.

   **Sign in with Microsoft** (`ms_auth.py` + routes in `server.py`) — the supported path for M365 mailboxes, and the only one that survives MFA/Conditional Access. Standard OIDC authorization-code flow with PKCE (S256), `state` and `nonce`; all three plus the post-login destination ride in ONE short-lived HMAC-signed cookie (`stmx_oauth`, signed with the same `AUTH_SECRET`), so the flow is stateless across Render instances. Deliberately **stdlib-only** — no `msal`, no `cryptography`. The ID token arrives over the server-to-server token call, so per OIDC Core §3.1.3.7 TLS validation stands in for JWT signature verification; `iss`, `aud`, `tid`, `exp` and `nonce` are all still checked, plus a domain gate (`MS_ALLOWED_DOMAINS`, default `streamax.com`). **The button only renders once `MS_TENANT_ID` + `MS_CLIENT_ID` + `MS_CLIENT_SECRET` are all set** — deploying the code changes nothing until the tenant is configured. Entra needs the redirect URI `https://streamax-salestoolkit.com/auth/microsoft/callback` registered as a **Web** platform, byte-for-byte. HTML server only — the Streamlit path keeps password-only sign-in. Run `python3 scripts/test_ms_auth.py` (no network, no pytest) after touching any of it: 31 checks covering the happy path, cross-tenant/audience/issuer/nonce/expiry rejection, CSRF, cookie tampering and open-redirect clamping.

2. **Cookie-based persistence** (`auth.py`): on successful login, `persist_login()` writes a signed cookie (`HMAC(user, expiry, AUTH_SECRET)`) via `extra-streamlit-components.CookieManager`. On every script run, `restore_session()` validates the cookie and rehydrates `st.session_state["authenticated"]`, `["user_name"]`, `["is_leadership"]`. Without this layer, every page reload or `?view=jerry_gpt` navigation forces re-login because Streamlit's session_state is per-WebSocket.

3. **LEADERSHIP clearance** (`login.py`): `LEADERSHIP_EMAILS` is a frozenset of streamax.com addresses that may access Streamax-internal pricing inside Jerry GPT. `resolve_leadership()` and `resolve_special_relationship()` are case-insensitive lookups that also map easter-egg display names → canonical emails. `SPECIAL_RELATIONSHIPS` is a separate map (Jerry himself, Kun He, Rui Wang) that controls address form and one-time greetings — orthogonal to leadership.

Important: the cookie manager has an async-cookie quirk. `extra_streamlit_components.CookieManager(key=...)` is a Streamlit widget and **cannot be wrapped in `@st.cache_resource`** (raises `CachedWidgetWarning`). It also **cannot be instantiated twice in the same run** with the same key. `auth.py` works around both by storing the manager in `st.session_state` and re-creating it once per run via `restore_session()` popping the stored marker. Anything that needs the manager later in the same run (e.g., `persist_login`) reuses the cached instance.

**The cookie WRITE must happen on a committed run — never right before `st.rerun()`.** `CookieManager.set`/`delete` send the write as part of the run's frontend delta; `st.rerun()` discards that delta, so the write never reaches the browser. The old code persisted inside `login.py` immediately before `st.rerun()`, so a fresh login's cookie was silently dropped and the next `?view=jerry_gpt` cross-navigation (a new connection that restores identity from the cookie) read the **previous** user. Fix: `app.py` calls `persist_login()` **once per connection from the authenticated render path** (a committed run, guarded by `_stmx_cookie_synced`), and `restore_session()` runs whenever unauthenticated *or* not-yet-synced so that committed run has a freshly-instantiated manager to write through. Logout uses `auth.logout_and_redirect(view)` which deletes the cookie and then navigates via `st.stop()` (which commits the delta, unlike `st.rerun`) — and **preserves the `view`** (`window.top.location.search = "?view=jerry_gpt"`), so signing out of Jerry GPT returns to Jerry GPT after re-login, not the toolkit. Jerry's sign-out link is therefore `/?view=jerry_gpt&logout=1` (not `/?logout=1`). JS is used only for navigation (writing `location.search` is cross-origin-safe); cookie reads/writes stay on the same-origin `CookieManager`.

### Jerry GPT — the chat subsystem

`jerry_gpt.py` is its own self-contained subsystem (~1500 lines) that runs whenever `?view=jerry_gpt` is in the URL. Key concepts:

**Knowledge base** lives in `jerry_gpt_knowledge/` as numbered markdown files. `_load_system_blocks()` reads every `*.md` file in lexicographic order, concatenates them, and returns a single Anthropic system-prompt block marked with `cache_control: ephemeral`. **Adding a new `.md` file to that directory automatically includes it** — no code change needed. The Streamaxpedia product database (`terminology_db.py`) is also pulled in via `_generate_streamaxpedia_knowledge()` at module load and appended to the same cached block.

**Per-turn clearance block** is built fresh on every API call by `_build_clearance_block()` and appended **after** the cached knowledge block. This is critical: the big knowledge prefix stays cached across users (cheap), while the small clearance suffix varies per-request (user identity, leadership flag, first-turn greeting, special-relationship treatment). Cache hits stay high; per-user behavior stays correct.

**Multi-provider routing (Claude + DeepSeek).** Jerry supports two providers, chosen by the selected model id via `_provider_for()` (ids starting `deepseek` → DeepSeek, else Anthropic). The model catalog `MODEL_OPTIONS` lists **DeepSeek V4 Pro** (id `deepseek-v4-pro`, configurable via secret `JERRY_DEEPSEEK_MODEL`) plus the Claude models. **Access policy:** non-leadership users may use **only DeepSeek** with the org key; Claude models are leadership-only — *unless* a user adds their own Anthropic key in **Settings → Bring your own API key**, which unlocks Claude for them (billed to their key). `_allowed_models()` computes the selectable set; `_resolve_provider_key()` returns the right key (BYO wins → org DeepSeek for all → org Anthropic for leadership). **BYO keys are session-only** — stored in `st.session_state` (`jerry_byo_anthropic_key` / `jerry_byo_deepseek_key`), never persisted to DB/Sheets and never logged. Keys/secrets: `ANTHROPIC_API_KEY` (org Claude, leadership), `DEEPSEEK_API_KEY` (org DeepSeek, everyone). DeepSeek is OpenAI-compatible, reached through the `openai` SDK pointed at `https://api.deepseek.com` (`_run_deepseek_stream`); Claude stays on the Anthropic SDK (`_run_anthropic_stream`) — the two share the same `{text, input, output, cache_read, cache_creation}` return contract so the post-work (history, usage, logging, artifacts, product images, downloads, ecosystem map) is provider-agnostic. **DeepSeek caveats:** no web tools (Anthropic server-side only), no prompt caching, no native image/PDF (those blocks are flattened/omitted; Office files still extract to text); the Anthropic-style system blocks are concatenated into one system message via `_build_deepseek_messages()`. The former VIP/Opus gating was replaced by this leadership-based gating.

**Web browsing**: every Jerry request attaches `WEB_TOOLS` (Anthropic server-side `web_search_20260209` + `web_fetch_20260209`, capped via `max_uses`). Jerry searches/reads the live web for current/external info (competitor moves, pricing, news) and is told via a system-prompt `<interface_capabilities>` note to cite sources and prefer built-in Streamax knowledge for Streamax facts. No client-side tool loop is needed — server tools run on Anthropic's side and the answer text still flows through `stream.text_stream`.

**Continuation / stop-reason handling** in `_submit_message()`: each response streams inside a `while True:` loop. **On Opus 4.8 the old assistant-text-prefill continuation for `max_tokens` returns a 400 (last-assistant-turn prefills are rejected), so it was removed** — a `max_tokens` stop now keeps the partial answer instead of erroring. The loop resumes only on `stop_reason == "pause_turn"` (the server web-tool loop hitting its iteration cap), by echoing `final_message.content` (the trailing `server_tool_use` block tells the API to resume) — never add a "continue" user message. Token usage is accumulated across rounds for the audit log.

**PM skills library** (`pm_skills.py` + bundled `pm_skills/<category>/<skill>/SKILL.md`, 68 skills): the catalog (name + description, ~5K tokens) plus a usage hint are injected into the cached knowledge block. Jerry suggests or applies the matching PM framework and tells the user which skill he used. The catalog is static so it stays cache-stable; full skill bodies are bundled and loadable via `pm_skills.load_skill_body(name)` for future on-demand deep application (not in the base prompt).

**Solution Selling method + process plays** (`jerry_gpt_knowledge/16_solution_selling_method.md` + `sales_process_skills.py` with bundled `sales_process_skills/<play>/SKILL.md`, 8 plays): Streamax's core sales methodology, distilled from *The New Solution Selling* (Keith Eades) into Streamax's own wording/examples (frameworks & process — not book text). The knowledge md makes it Jerry's **default sales process** (no-pain-no-change, diagnose-before-prescribe, 3 levels of need, Looking vs Not Looking / Column A, buyer-phase risk, Pain×Power×Vision×Value×Control). The 8 plays (`diagnose-9block`, `build-pain-chain`, `value-proposition`, `qualify-opportunity`, `competitive-strategy`, `evaluation-plan`, `negotiation-prep`, `business-development-prompter`) are the apply-on-demand toolkit, injected as a `<sales_process_skills>` catalog like the PM/marketing libraries, plus three `QUICK_PROMPTS` chips (Diagnose my deal / Pain-based cold email / Qualify this opportunity). "P1" wired the same plays into three toolkit tabs (all client-side JS in the `content` HTML strings): **Value Calculator** — a Value Proposition & Justification panel in the TCO sub-tab that assembles the SS value-prop statement + payback from the calculator's numbers (`vp-statement`/`vp-justification`, populated inside `calculateROI()` in `app.py`, `copyVP()`); **Email Tool** — a Business Development Prompter generator (`genBDPrompter()`/`BD_PLAYBOOK`/`copyBD()` in the `email_tool_content` string) that emits a pain-based cold email per buyer title using `{first_name}`/`{company}` Drip-Mailer merge vars; **Discovery Meeting** — a "9-Block & Pain Sheet" sub-tab with the diagnostic model + per-title Pain Sheets. P2 (Deal Strategy / Deal Tracker / Negotiation prep) remains.

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

## Sales Configurator (vendored — author: Kevin Wang)

`/configurator/` serves the **Streamax Sales Configurator**, a guided BOM builder for the NA sales list (pick a host/solution, answer install questions, it applies camera/interface/cable rules and exports the approved Excel material list).

**It is a separate project owned by Kevin Wang (kevinwang@streamax.com) — credit him wherever it is surfaced, and send product-rule/SKU issues to him, not into this repo.** Source lives at `~/Desktop/Streamax/Product-sales-kit`.

Its runtime files are vendored into `./configurator` (≈80 MB) — Render builds from *this* repo and can't see the other checkout: `index.html`, `styles.css`, `catalog-data.js`, `js/`, `data/`, `vendor/`, `assets/`, **and `North America Sales List-FILE/`**. `server/`, `scripts/`, `docs/` and the 13 MB source `.xlsx` are excluded.

⚠️ **`North America Sales List-FILE/` is required, despite the name and the ~72 MB.** It is not a source folder — it is the product image library. `catalog-data.js`, `js/02-dom-state.js` and `js/04-product-meta.js` reference **246 files** inside it by *relative* path (many with spaces and CJK segments like `图片/`, which is fine — StaticFiles URL-decodes them). Omitting it renders every product card with a broken image, which is exactly what happened on the first vendoring pass. `sync_configurator.sh` now resolves every referenced path after copying and exits non-zero if any is missing — that check is the guard against repeating it.

Because it's vendored it **will drift**. Refresh with `./sync_configurator.sh` after Kevin ships changes; it rewrites `configurator/VENDORED.md` with the source revision and date, then verifies every referenced asset resolves. Never hand-edit files under `configurator/` — the next sync overwrites them. That includes image optimisation: several assets are far larger than they need to be (one Z5 PNG is 8192×5464 / 14.9 MB), but shrinking them here would be reverted on the next sync — raise it with Kevin so it's fixed upstream.

Its beta *Annotate / Send feedback* buttons call `/api/annotations`, `/api/feedback`, `/api/solutions`, served by the source project's own Node server (`server/server.js`), which is **not** deployed here — so those beta features are inactive in the toolkit. The configurator itself works fully.

Surfaced in three places: the **Sales Configurator** tab (`configurator_tab.py`, credits Kevin on the card), the `/configurator` StaticFiles mount in `server.py`, and `jerry_gpt_knowledge/17_sales_configurator.md` so Jerry hands users over to it (naming Kevin) once a conversation turns to "what exactly do I order?".

## Required secrets

`st.secrets` (or `.streamlit/secrets.toml` locally):

- `ANTHROPIC_API_KEY` — org Claude key for Jerry GPT. With Jerry's multi-provider routing this is the **leadership-only** key (Claude models). Optional if `DEEPSEEK_API_KEY` is set (non-leadership users can run on DeepSeek alone).
- `DEEPSEEK_API_KEY` — org DeepSeek key, available to **all** Jerry users; the only org-key model non-leadership may use. Jerry needs at least one of `ANTHROPIC_API_KEY` / `DEEPSEEK_API_KEY`.
- `JERRY_MODEL` — optional, leadership default, defaults to `claude-opus-5`. Retired Opus ids (`claude-opus-4-8/4-7/4-6/4-5`) set here are auto-upgraded to Opus 5 via `_LEGACY_MODEL_ALIASES` (logged to stderr) — otherwise a stale secret would name a model missing from `MODEL_OPTIONS` and the settings panel would silently downgrade leadership to DeepSeek. Update the secret to clear the warning.
- `JERRY_DEEPSEEK_MODEL` — optional, defaults to `deepseek-v4-pro` (set this to DeepSeek's exact public model name if it differs)
- `AUTH_SECRET` — required for session cookie signing (generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `JERRY_GPT_SHEET_ID` + `[gcp_service_account]` table — optional, enables Google Sheets logging for Jerry GPT
- `JERRY_GPT_DB_URL` — optional, enables cross-session chat history for Jerry GPT via Supabase Postgres

If `JERRY_GPT_SHEET_ID` is absent, the app still works — usage logging falls through to stdout-only.

### Microsoft sign-in (HTML server, environment variables)

Set on the Render service, not in `secrets.toml`. Sign in with Microsoft stays hidden until all three required values are present.

- `MS_TENANT_ID` — **required.** Entra *Directory (tenant) ID*.
- `MS_CLIENT_ID` — **required.** Entra *Application (client) ID*.
- `MS_CLIENT_SECRET` — **required.** The secret **Value** (not the Secret ID). Entra secrets expire — a 24-month secret must be rotated before it lapses or every Microsoft sign-in breaks at once.
- `MS_REDIRECT_URI` — optional. Pin this if the auto-derived value is ever wrong; otherwise it is built from `X-Forwarded-Proto`/`X-Forwarded-Host` (correct behind Cloudflare → Render). It must equal the URI registered in Entra **exactly**, or Microsoft returns `AADSTS50011`.
- `MS_ALLOWED_DOMAINS` — optional CSV, default `streamax.com`.
- `MS_SMTP_AUTH` — optional; set `0` to stop probing `smtp.office365.com` on the password path once OAuth is live.

Entra app registration: **single tenant**, platform **Web**, redirect URI `https://streamax-salestoolkit.com/auth/microsoft/callback`, delegated permissions `openid` + `profile` + `email` (all no-admin-consent). Nothing needs `Mail.*` — the app only reads who signed in.

## Jack GPT — removed

Jack GPT (the Emily-only private workspace: `jack_gpt.py`, `jack_chat_history.py`, `jack_usage_logger.py`, the `?view=jack_gpt` route, the Emily-card launch button, and the jhsun login easter egg / VIP grant) was **removed** in v5.8.14. Jerry GPT is the only AI chat surface now. The Emily terminology row (`jhsun_only`) and the jhsun-gated "Global Trucking" header rename still exist but no longer have a Jack GPT target — remove them too if jhsun-specific behavior is no longer wanted.
