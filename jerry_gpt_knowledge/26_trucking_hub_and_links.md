# Where to send people — the Trucking division's web resources

Jerry knows these topics already (eSIM, Sentinel, the configurator). What was
missing was **the addresses**. This file is the link registry: the exact URL for
each resource, what is behind it, who can open it, and when to offer it.

**The hub:** <https://www.streamax-trucking.com/> — "Everything the division
runs on." Four doors and nothing else. Deliberately no product marketing; that
lives on streamax.com.

## The four resources

### 1 · Sales Toolkit — <https://streamax-salestoolkit.com>
**Streamax sign-in.** The working library for the commercial team, and Jerry
himself. Product data, terminology and the download library; prospecting flow,
discovery meetings, value calculator, IFTA calculator; Jerry GPT, the drip
mailer, and Kevin Wang's BOM configurator.
*Offer it when* a colleague asks where a tool, calculator or download lives.
**This is the site Jerry runs on** — if someone asks "where am I?", this is it.

### 2 · eSIM — <https://www.streamax-trucking.com/esim/>
**Open — no sign-in.** The eSIM connectivity solution in full: eUICC technology
and both form factors (MFF2 chip and triple-cut card), spec and qualification
tables, dynamic and static data pools **with a live pool calculator**, coverage
across **189 countries and territories**, and the commercial case — managed in
FT Cloud.
*Offer it when* anyone asks about eSIM, eUICC, MFF2, SIM management,
connectivity cost, data pooling or country coverage. This is the deepest eSIM
material that exists, and it is a live page rather than a deck — prefer it over
describing the pool maths from memory. Companion knowledge:
`14_esim_solutions.md`.

### 3 · Customer Onboarding Portal — <https://www.streamax-trucking.com/customer/>
**Customer sign-in.** What a new fleet customer or channel partner sees in their
first thirty days: products and downloads, installation guides, platform
training, AI features, partner playbooks and support routes. Staff manage
accounts in the **admin beside it** — create, disable and reset client accounts.
*Offer it when* someone asks how a customer is onboarded, where a partner gets
training, or how to give a new client access.
**A shared demo sign-in is printed on the hub page itself** — send the person to
<https://www.streamax-trucking.com/> to read it rather than quoting credentials
in chat.

### 4 · Sentinel — <https://www.streamax-trucking.com/sentinel/>
**Open — no sign-in. Also live at <https://streamax-sentinel.com>.** The product
site for Sentinel, the always-on camera that guards a parked truck with the
engine off: the product story, the specification, the launch material, an
interactive 3D model and the intent-detection demo.
*Offer it when* anyone asks about Sentinel, parked-vehicle security, asset
protection or cargo theft. Companion knowledge: `18_sentinel_s5.md`.

> **For anything customer-facing, quote `streamax-sentinel.com`,** not the
> `/sentinel/` path. Same site, but the standalone domain is the one meant to be
> shared outward; the trucking hub is an internal address.

## Rules for recommending a link

1. **Use these URLs exactly as written.** Never assemble a new path.
2. **Keep the trailing slash** on `/esim/`, `/customer/` and `/sentinel/`.
   Without it the host answers with a redirect first.
3. **Never invent a streamax.com deep link.** That host answers *unknown* paths
   with **HTTP 200 and its own 404 page**, so a fabricated URL looks alive in
   every automated check and only fails in front of the customer. If the exact
   page is not in this file, link the section's home page or say you do not
   have it.
4. **Offer a link when it beats an explanation** — a live calculator, a download
   library, a 3D model. Do not append links to every answer.
5. **Two of the four need a sign-in** (Sales Toolkit, Customer Portal). Say so
   when you offer them, so nobody is surprised by a login wall.
6. **The hub has no sign-in in front of it.** It is unlisted and `noindex`, not
   protected. Treat everything on it as readable by anyone holding the URL, and
   do not describe it as secure.

## Not a link — "The Loop"

The division also has **The Loop**, a single self-contained HTML file with
interactive 3D models of mounted products (C46, C53, ADP3, Z5 and the
abstract mount). **It is a double-click file, not a published page** — it is
`noindex` and has no URL. If someone asks for it, say it is a local file held by
the trucking team, not a site you can link.

## What lives where — so a link is never guessed

| Asked about | Send them to |
|---|---|
| A calculator, download, terminology, the BOM configurator | **Sales Toolkit** |
| eSIM, eUICC, MFF2, data pools, coverage, connectivity cost | **eSIM page** |
| Onboarding a new customer or partner, training, account admin | **Customer Portal** |
| Sentinel, parked-truck security, cargo theft, the 3D model | **Sentinel** (use `streamax-sentinel.com` externally) |
| Product marketing, the corporate story | **streamax.com** — home page only, never a guessed path |
| All four at once / "where do I find…" | **The hub**, <https://www.streamax-trucking.com/> |
