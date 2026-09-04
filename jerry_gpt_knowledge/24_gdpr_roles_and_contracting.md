# GDPR — roles, contracting, and the product red lines

> **Not legal advice.** Product and process description for internal use.
> Streamax's own compliance materials carry the same caveat. Never tell a
> customer they "are compliant" — that is a property of their deployment, and
> their DPO or counsel decides it. Sources: `GDPR.pdf` (7-page regulatory
> briefing) and the deck `GDPR 落地第一步：分清角色，再定签谁`
> ("Step one: settle the roles, then decide who signs"). Companion file:
> `23_gdpr_and_data_compliance.md` (technical architecture and TOMs).

## The one question that has to be answered first

**Who is the Controller?** The Controller decides *why* and *how* data is
processed. The Processor acts only on the Controller's instructions.

| | |
|---|---|
| **Controller** | The **European transit/fleet operator** — always |
| **Processor** | **Streamax** — devices and cloud platform, acting on the operator's instructions |
| Consequence | A **DPA under Art. 28 must be signed with every European customer.** No DPA is not a gap, it is a **direct violation** in itself. |

### The three things that silently promote Streamax to Controller

This is the highest-value warning in the whole file. Each of these changes the
legal role, and with it the liability:

1. **Training AI algorithms on European customer video** without the operator's
   authorisation.
2. **Aggregating data across multiple operators** for cross-analysis, reports,
   or sale.
3. **The China team accessing European customers' live or historical video** at
   will.

**The fix is contractual, not technical:** put a written authorisation in a
**DPA annex** stating the data types, the processing purpose, the
de-identification requirement, and the scope of use. With that annex Streamax
remains a Processor. Without it, doing any of the three makes Streamax a
Controller — with the operator's obligations and exposure.

## Who signs what — the compliance "four-piece set"

Most of these are the operator's documents. Streamax's commercial advantage is
**lowering the cost of signing them**, which is a sales argument, not a
back-office chore.

| # | Document | Who signs | Streamax's part |
|---|---|---|---|
| 1 | **DPA** — Data Processing Agreement (Art. 28(3)) | Both | **Streamax leads.** Provides the full clause template: instruction-bound processing, confidentiality, security measures, sub-processor management, audit cooperation |
| 2 | **LIA** — Legitimate Interests Assessment | **Operator signs**, Streamax supports | Supplies the data-security whitepaper as the necessity argument; encryption and permission isolation evidence the balancing test |
| 3 | **DPIA** — Data Protection Impact Assessment (Art. 35) | **Operator signs — mandatory** | Fleet deployment routinely trips systematic profiling and large-scale monitoring, so a DPIA is *required*, not optional. Streamax provides a mature template |
| 4 | **ROPA** — Record of Processing Activities (Art. 30(2)) | Each party maintains its own | Streamax maintains a complete "processor record" with the standard fields, structured for direct reuse |

Three commercial models change who sits where: **direct sales**, **channel /
agent**, and **system integration**. Settle the role map before drafting, not
after.

### The six DPA clauses that must be present

| # | Requirement | What it means for Streamax |
|---|---|---|
| 1 | Process only on the Controller's written instruction | The cloud platform must not exceed the operator's authorisation |
| 2 | Staff confidentiality obligations | Anyone touching EU data signs an NDA |
| 3 | Implement Art. 32 security measures | Encryption, access control, breach response |
| 4 | Sub-processors require approval | Cloud providers must be listed in the DPA and approved by the operator |
| 5 | Assist with data subject rights | Provide video retrieval and deletion interfaces |
| 6 | Delete or return data on termination | On customer churn, data must be thoroughly erased |

## Cross-border transfer — the sharpest risk for a Chinese vendor

European data reaching China — headquarters or an R&D team merely *accessing*
it — is a **transfer**, and triggers Art. 44–49. **China has no EU adequacy
decision**, so a transfer requires **SCCs plus a Transfer Impact Assessment**.

The TIA must actually assess:
- the effect of Chinese law on data protection — **Data Security Law,
  Cybersecurity Law, National Intelligence Law**;
- the realistic scope of Chinese government access, and the risk it creates;
- the technical supplementary measures that answer it (encryption, access
  control, data localisation).

**The recommended architecture sidesteps most of this:**

```
EU vehicle devices  →  EU data centre (e.g. AWS Frankfurt / Azure Amsterdam)
                    →  China HQ receives ANONYMISED, AGGREGATED data only
```

European personal data is processed and stored only in Europe. If headquarters
never receives personal data, the hardest part of the transfer problem does not
arise. **When residency is contested, lead with this diagram.**

## Article 9 — when DMS becomes special-category data

The single most useful table for a technical evaluation. Per **EDPB Guidelines
3/2019**:

| DMS use | Triggers Art. 9? |
|---|---|
| Detecting eye closure / yawning | **No** — a behavioural state judgement |
| Distraction detection (gaze / head pose) | **No** — a behavioural state judgement |
| **Face-recognition login (identity verification)** | **Yes** — uniquely identifies the driver |
| **Building a driver face profile, cross-shift tracking** | **Yes** — biometric processing |

If Art. 9 is triggered you need **an Art. 6 lawful basis *and* an Art. 9
condition** (a double threshold), a **mandatory DPIA**, and stricter security
measures. The product answer is configurability: whether to upload, whether to
store, whether to mask, and who may access.

### DMS design red lines — default OFF

| Must be default-off / disabled | Why |
|---|---|
| **Face login** | Trips Art. 9. Use an employee ID + password, or a physical RFID card, so no face template is retained |
| **Cross-shift face matching** | Cross-comparing biometric features across drivers is purpose drift |
| **Unauthorised upload of raw driver face images/video** for cloud AI training or tuning | This is red line #1 above — it makes Streamax a Controller |

### Driver profiling — also an Article 22 problem

Fatigue-score trends are physiological baseline data, which reads as **health
data**. Two rules:

- **A DPIA is mandatory** before launch or delivery for anything involving
  human-factors or driver profiling.
- **Profiling scores must never drive an automated penalty.** No automatic
  reassignment or dismissal — a **human review step must remain in the
  business flow**, or it becomes an **Art. 22** automated-decision violation.
- Access control must separate the **aggregate layer** (trend scores) from the
  **individual layer** (specific deductions): who can see what, and at which
  depth.

### The features that buy driver acceptance

Worth leading with in a works-council conversation, because they are concessions
that cost nothing:

- A **driver-facing personal data console** — makes portability and the right to
  be informed real rather than theoretical.
- **Positive feedback instead of pure punishment** — safe-driving points and
  rest reminders rather than only alarms.
- **Local tolerance** — the first few minor fatigue alerts stay in the cab and
  are never reported to the management platform.
- A **driver handbook, data commitment template and compliance Q&A** as a union
  negotiation toolkit.

## Article 13 — the in-vehicle notice obligation, now case law

**CJEU C-422/24 (December 2025, Stockholm public transport)** confirmed that
in-vehicle cameras must inform passengers **at the moment of collection** —
after-the-fact notice does not satisfy Art. 13.

**Two layers, plus a separate one for the driver:**

1. **On-board sticker** — short notice plus a QR code: purpose, controller,
   retention period.
2. **Online privacy policy** behind the QR — the full Art. 13(a)–(f)
   disclosure: controller name and contact, DPO contact, purpose and lawful
   basis, the specific legitimate interest if relying on Art. 6(f), retention
   period, data subject rights, and the right to complain to a supervisory
   authority.
3. **Separate driver disclosure** — delivered through onboarding documents.
   **In Germany this requires a written works agreement (Betriebsvereinbarung)
   with the works council** for driver-state monitoring.

**Streamax provides multi-language (EN/FR/DE/NL) in-vehicle notice templates and
matching privacy policy templates.** Treat this as a sales differentiator — it
removes work the operator would otherwise have to commission.

## Masking — the decision rule

Article 5(1)(c) in one question: **does this processing purpose actually require
identifying a face?**

| Answer | Case | Result |
|---|---|---|
| **Yes** — original purpose | Accident/safety evidence; genuinely need to check eye closure or distraction | Keep the original locally, readable only inside the secure domain |
| **No** — new purpose | Onward transfer: insurance claims, third-party fleet analytics | **Masking is mandatory** |

Automatic masked transmission is **on by default**, switchable from the admin
console, and every masking and retrieval action enters a tamper-proof audit log.

## Breach notification — note the 24-hour internal step

| When | Who | What |
|---|---|---|
| Immediately | Streamax | Detect and start incident response |
| **Within 24h** | **Streamax → operator** | The processor notifies the controller |
| **Within 72h** | **Operator → supervisory authority** | Art. 33 |
| If high risk | Operator → passengers | Art. 34 |

The 24-hour internal step is what makes the operator's 72-hour clock
achievable. Requires an internal detection/classification process, a
standardised operator-notification template, and a record of every incident.

## What enforcement actually costs

| Violation | Case | Fine |
|---|---|---|
| Failure to give in-vehicle notice (Art. 13) | **Stockholm transit, 2021** | SEK 16M ≈ **€1.4M** |
| Unlawful cross-border transfer | Meta Ireland, 2023 | **€1.2B** — the largest ever |
| Operating with a processor with no DPA | Multiple | Up to **€20M** |

**The two highest-risk areas, per Streamax's own assessment:** cross-border
transfer (China HQ access — complete SCC + TIA immediately) and **operating
without a signed DPA** (European sales contracts must front-load a standard
DPA).

## Retention periods — do not quote a number

Four internal documents give **three different sets of figures**:

| Source | Normal | Event / alarm | DMS behaviour |
|---|---|---|---|
| `GDPR.pdf` | 7–30 days | 3–6 months | 30–90 days |
| Data-boundary deck | 48–72h local loop | 30/60 days cloud | — |
| GDPR whitepaper | Until storage threshold | Configurable, "e.g. 6 months" | — |

They are not reconcilable and they do not need to be — **retention is a
configuration**, set per alarm type on both device and platform. Say that.
Quoting any single figure will contradict another Streamax document the customer
may also have seen.

What is *not* configurable and must be stated: expiry means **irreversible
physical deletion**; manual deletion by time, vehicle or driver ID is supported
and produces an exportable **deletion receipt** (Art. 17); and every deletion is
written to a tamper-proof log with operator, time and scope (Art. 5(2)).

One useful exception: **anonymised passenger-flow statistics are irreversibly
anonymised, so they fall outside GDPR and may be retained long term.**

## Boundaries

- Not legal advice; not a compliance guarantee.
- **DPA, LIA, DPIA and ROPA templates** are held by legal and the compliance
  team — Jerry describes what they cover, and does not draft or approve one.
- The **role map for a specific deal** (direct / channel / integrator) must be
  settled with legal before contracting.
- Member-state employment law varies under **Art. 88**; Germany's
  Betriebsvereinbarung requirement is the documented example, not the only one.
