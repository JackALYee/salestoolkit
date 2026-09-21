# Where to send people — the Trucking division's web resources

Jerry knows these topics already (eSIM, Sentinel, the configurator). What was
missing was **the addresses**. This file is the link registry: the exact URL for
each resource, what is behind it, who can open it, and when to offer it.

**Verified live on 2026-09-21.** Three things changed that day and they change
what Jerry is allowed to say — see *What changed* at the foot of this file.

**The hub:** <https://www.streamax-trucking.com/> — *"Streamax Trucking — a
full-lifecycle safety loop for cargo transportation."* It **opens on the loop**
(below), then lists the two open solution pages, then the two sign-in tools.

> **The hub is public now.** It was an unlisted `noindex` page until
> 2026-09-21; it is `index, follow` and meant to be read by anyone. **You may
> send it to a customer.** It carries no pricing and no credentials, which makes
> it a safe opener when you do not yet know which product fits.

## The loop — link the hub root, never `/loop`

The division's safety story runs on the hub as a live 3D page: **eleven stops
from the yard to the debrief**, with the cameras and boxes that watch each one
mounted on the truck. Eight stops are built with camera moves, detection areas
and real footage playing over the cards.

**Always link <https://www.streamax-trucking.com/> for it.** The loop had its
own address for one afternoon and is being folded back into the front page — a
`/loop` URL will redirect, so it is never the right thing to paste. The hub root
is correct today and correct after the fold.

What the loop names on screen: **C46** (front camera), **C53L / C53R**
(blind-spot cameras), **M1N 2.0** (in the glove box), **Z5** (inside the cargo
box), **ABS solar battery** (outside it), the **Sentinel** on the parked truck,
and the ADAS + DMS unit — labelled simply **"Dashcam"**.

> **Two rules the loop teaches, and Jerry follows them everywhere.**
>
> 1. **Call it a dashcam, not a model number.** The ADAS + DMS dashcam's model
>    name is on the pre-release list, so public material says "Dashcam". Do the
>    same in anything customer-facing. The **C46 is shipping and keeps its
>    name**; so do the C53s, M1N 2.0, Z5 and Sentinel.
> 2. **The detection areas on the loop are illustrative, not datasheet
>    figures.** If someone asks what coverage a camera has in metres or degrees,
>    answer from the spec knowledge — never from the shapes in the animation.

It needs a desktop-sized screen: below 900px, or with reduced motion asked for,
the page shows a still instead. Worth saying if someone is on a phone.

## The four resources

### 1 · Sales Toolkit — <https://streamax-salestoolkit.com>
**Streamax sign-in.** The working library for the commercial team, and Jerry
himself. Product data, terminology and the download library; prospecting flow,
discovery meetings, value calculator, IFTA calculator; Jerry GPT, the drip
mailer, and Kevin Wang's BOM configurator.
*Offer it when* a colleague asks where a tool, calculator or download lives.
**This is the site Jerry runs on** — if someone asks "where am I?", this is it.
Internal: never offer it to a customer.

### 2 · eSIM — <https://www.streamax-trucking.com/esim/>
**Open — no sign-in, safe to send to a customer.** *"Connectivity that ships
inside the camera."* eUICC technology and both form factors (MFF2 chip and
triple-cut card), spec and qualification tables, dynamic and static data pools
**with a live pool calculator**, and the published commercial figures:
**189 countries, 388 networks, from $1.50/GB** — managed in FT Cloud.
*Offer it when* anyone asks about eSIM, eUICC, MFF2, SIM management,
connectivity cost, data pooling or country coverage. This is the deepest eSIM
material that exists, and it is a live page rather than a deck — prefer it over
describing the pool maths from memory, and prefer sizing a pool on its
calculator in front of the customer. Companion knowledge: `14_esim_solutions.md`.

### 3 · Customer Onboarding Portal — <https://www.streamax-trucking.com/customer/>
**Customer sign-in.** What a new fleet customer or channel partner sees in their
first thirty days: products and downloads, installation guides, platform
training, AI features, partner playbooks and support routes. Staff manage
accounts in the **admin beside it** — create, disable and reset client accounts.
*Offer it when* someone asks how a customer is onboarded, where a partner gets
training, or how to give a new client access.

> **There is no shared demo sign-in to hand out.** One used to be printed on the
> hub page; it came off when the page went public on 2026-09-21. Accounts are
> issued by the division — say *"ask your Streamax contact for an account."*
> Never quote a credential in chat, and never send anyone to the hub to read one.

### 4 · Sentinel — <https://streamax-sentinel.com>
**Open — no sign-in, safe to send to a customer.** Also reachable at
<https://www.streamax-trucking.com/sentinel/>. The product site for Sentinel,
the always-on camera that guards a parked truck with the engine off: the product
story, the specification, the launch material, an interactive 3D model and the
intent-detection demo.
*Offer it when* anyone asks about Sentinel, parked-vehicle security, asset
protection or cargo theft. Companion knowledge: `18_sentinel_s5.md`.

> **For anything customer-facing, quote `streamax-sentinel.com`,** not the
> `/sentinel/` path. Same site, but the standalone domain is the one meant to be
> shared outward.

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
   when you offer them, so nobody hits a login wall — and offer them only to
   colleagues and partners, never to a customer.
6. **Three addresses are safe to send to a customer:** the hub, the eSIM page
   and `streamax-sentinel.com`. Everything else is internal.

## What lives where — so a link is never guessed

| Asked about | Send them to | Customer-safe |
|---|---|---|
| The safety story, the 3D loop, "what does Streamax trucking do" | **The hub**, <https://www.streamax-trucking.com/> | ✅ |
| eSIM, eUICC, MFF2, data pools, coverage, connectivity cost | **eSIM page** | ✅ |
| Sentinel, parked-truck security, cargo theft, the 3D model | **<https://streamax-sentinel.com>** | ✅ |
| A calculator, download, terminology, the BOM configurator | **Sales Toolkit** | ❌ sign-in |
| Onboarding a new customer or partner, training, account admin | **Customer Portal** | ❌ sign-in |
| Product marketing, the corporate story | **streamax.com** — home page only, never a guessed path | ✅ |

## What changed on 2026-09-21

Three corrections to what Jerry used to be told. If an older answer conflicts
with this file, this file wins.

1. **The hub went public and indexed.** It is no longer an unlisted internal
   address, and it is no longer wrong to send it outside Streamax.
2. **The demo sign-in came off the hub.** Any older instruction to send someone
   to that page to read a password is dead — there is nothing there to read.
3. **The loop is published.** It used to be a local double-click file with no
   URL; it is on the hub now. Link the hub root for it.
