---
name: streamax-knowledge
description: Streamax Technology product knowledge, positioning, and sales strategy for B2B commercial vehicle video telematics. Use this skill when writing Streamax-branded content for fleet operators, TSP (telematics service provider) partners, or insurance partners — including cold emails, sales pitches, value propositions, product comparisons, competitive positioning, discovery questions, objection handling, or any output that represents Streamax to an external audience. Trigger this skill whenever the user mentions Streamax, video telematics sales, ADAS/DMS cameras, SafeGPT, fleet safety pitches, trucking/transit/mining/school-bus/taxi sales, or asks about competitors like Samsara, Motive, Geotab, MiTac, Lytx, Netradyne, Teltonika, Hikvision, or Jimilab.
---

# Streamax Sales Knowledge

A distilled knowledge base for representing Streamax Technology in any sales context. Built from the Product Marketing Director's internal strategy documents, white papers, and sales playbook.

## When to use this skill

Use it whenever you are producing content **on behalf of Streamax** for an external audience — cold emails, sales decks, discovery scripts, partner pitches, RFP responses, value propositions, competitive replies, or persona descriptions for AI sales agents. Use it also when the user asks strategic questions about Streamax's positioning, products, competitors, or markets.

Do NOT use it for generic fleet management or telematics questions that aren't about Streamax.

## The two-minute Streamax summary

Streamax Technology (SZ:002970, founded 2003, HQ Shenzhen) is the **world's #1 video telematics hardware provider by installed base** — ranked #1 by Berg Insight for **6 consecutive years**. 5 million+ vehicles deployed across **100+ countries**, 500+ channel partners across 7 industries, CNY 2.78B (~$385M USD) 2024 revenue. Subsidiaries in 8 countries (US, Mexico, Brazil, UAE, Singapore, Japan, Netherlands, Vietnam) with 180+ international staff. 700+ engineers; AI development since 2015; manufacturing in China and Vietnam.

**Only vendor offering three commercial-vehicle product lines from one source:**

1. **Video Telematics** — AI dashcams (2CH–6CH: DS100, C6 Lite, AD Plus, AD Max) + MDVRs (5CH–24CH) + SafeGPT cloud behavioral AI
2. **Visibility Assistance** — DVS/BSIS/MOIS regulatory compliance cameras (UN R151/R155/R158, London DVS, EU GSR2) + AVM 360° + CMS digital mirrors (UN R46)
3. **Asset Protection** — Z5 trailer camera + Sentinel exterior camera (June 2026) + driver biometric ID + vehicle immobilisation

**The category-creating differentiator: SafeGPT.** A cloud-based behavioral AI that moves from event-based alerting (every camera vendor) to continuous behavioral assessment. Reduces alerts 90%, detects fatigue 5–15 minutes before eyes close, classifies risk type, builds persistent driver behavioral profiles, and auto-prioritizes coaching clips.

**The one-device revolution.** Streamax cameras now read native vehicle data via CAN/J1939/OBD-II/FMS (Inventure + CANGO partnerships) — replacing the separate telematics tracker. One device, one cable, one cellular plan, 15-minute plug-and-play installation, 3–4 vehicles per hour per installer.

## Reference files — read on demand

Pull the right file for the task. **Most short outputs (cold emails, one-line pitches) only need the summary above + one reference file.** For deeper work (decks, RFPs, strategy), read multiple.

| File | When to read it |
|---|---|
| `reference/company-snapshot.md` | Need company facts, credentials, scale, regional footprint |
| `reference/product-portfolio.md` | Need product names, model numbers, specs, channel count, pricing tiers |
| `reference/safegpt.md` | Writing about SafeGPT, behavioral AI, alert fatigue, fatigue detection, Evidence Cards |
| `reference/value-propositions.md` | Need the six fleet-operator value props or industry-specific pain points (trucking, school bus, transit, mining, taxi, OEM, insurance) |
| `reference/competitive-intel.md` | Writing against Samsara, Motive, Geotab, MiTac, Lytx, Netradyne, Teltonika+Howen, Hikvision, Jimilab, LightMetrics, Xirgo, Surfsight |
| `reference/market-data.md` | Need cited industry statistics — cargo theft costs, accident data, market sizes, regulatory deadlines |
| `reference/pricing-and-tco.md` | Need platform tier pricing ($1/$3/$6), TSP margin economics, TCO comparison vs competitors |
| `reference/sales-pitches.md` | Need 60-second pitches, objection handling, discovery questions, driver-buy-in talking points |

## Style and tone guardrails

When writing as Streamax:

- **Personal salutation is mandatory.** Every cold email body MUST begin with `Hi {first_name},` on its own line, then a blank line, then the opening paragraph. The first name comes from the prospect's CSV record. If the CSV has no first name, use `Hello,`. Never start with a different greeting, never skip the salutation, never address the prospect generically ("Hi there,", "Hello team,").
- **Lead with outcomes, not specs.** "90% fewer false alerts" beats "QCS6490 processor." "Doubles recurring revenue per vehicle" beats "white-label platform."
- **Use concrete, citable numbers.** Berg Insight rankings, market sizes, ATRI/TAPA theft data, accident reduction percentages. Always anchored, never hand-wavy.
- **Acknowledge real pain credibly.** Alert fatigue, driver resistance to cameras, the cost of "having cameras but not being safer." Streamax wins by understanding the problem, not by claiming magic.
- **Never speak ill of partners.** TSPs are channel partners — even when displacing competitors, frame as enabling the partner, not replacing them.
- **Be honest about limitations.** Cellular jamming defeats real-time alerts. Cameras can't see through obstructions. Z5 doesn't yet support refrigerated trailers. Honesty builds trust.
- **Drop the filler.** Never write "I hope this email finds you well." Get to the point in the first sentence after the salutation.

## Confidential boundaries

The Knowledge Base files include both **external-safe** content (white papers, end-user value propositions) and **INTERNAL-ONLY** content (competitive intelligence, partner names, pricing strategy, displacement playbooks, three-year financial projections, internal product gap analysis).

**Default to external-safe.** When generating customer-facing content (cold emails, public marketing copy, customer-shareable decks), never include:
- Specific competitor displacement plans or win-probability percentages
- Internal partner names tied to specific revenue figures
- Streamax's strategic weaknesses (NA struggles, AI training gaps, the "self-defeating loop")
- Streamax's roadmap dates beyond what is publicly announced
- TSP margin analysis or internal cost structures

When the user explicitly asks for internal strategy work, all of `competitive-intel.md` and `pricing-and-tco.md` are available — use judgement.
