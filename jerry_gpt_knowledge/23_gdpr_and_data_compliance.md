# GDPR & Data Compliance — EU privacy positioning

> **Companion file:** `24_gdpr_roles_and_contracting.md` — Controller vs
> Processor, who signs the DPA/LIA/DPIA/ROPA, Art. 9 triggers, cross-border
> transfer, and the in-vehicle notice obligation. This file is the technical
> architecture; that one is the legal and commercial frame.
>
> **HANDLING — read before using any of this.**
>
> Two source documents, both restricted:
> * `GDPR_Whitepaper_EN.docx` (v1.0, 2026-05) — **Confidential**, and its own
>   last line reads *"Draft — Legal review required before external
>   publication."* **Do not send this whitepaper to a customer.** Use it to
>   answer questions and shape a conversation; if a customer wants the document,
>   route the request through legal.
> * `守护数据边界，驱动合规未来` (10-slide deck) — carries the standing
>   disclaimer *"本材料为产品功能说明，不构成法律建议"* (product function
>   description, **not legal advice**) and *"具体功能实现、服务承诺及合规标准
>   以最终签署的商业合同约定及实物交付为准"* (actual scope is whatever the
>   signed contract and delivered goods say).
>
> **Jerry must never give legal advice.** Describe what the product does and
> which obligation it helps the customer meet — the customer's DPO or counsel
> decides whether their processing is lawful. Never confirm that a customer "is
> GDPR compliant"; compliance is a property of *their* deployment and process,
> not of a device.

## The frame that wins the conversation

Compliance is not a tax on the deal — in the EU it is the deal. The whole
Streamax argument is **subtraction at every stage**: mask at the source, filter
before upload, stop recording outside the work boundary, send only events, and
delete on a clock. A fleet that cannot show *less* data is a fleet with a
problem; every feature below removes data rather than adding safeguards on top
of it.

Anchor facts a buyer's DPO will ask for first:

| Topic | Streamax position |
|---|---|
| Processing location | **EU territory only** (EU-hosted servers) |
| Encryption in transit | **TLS 1.3**, plus the proprietary in-vehicle protocol (N9M); MDVR→cloud is **mTLS 1.3** |
| Encryption at rest | **AES-256** (platform config/credentials AES-GCM-256) |
| Certifications held | **ISO 27001**, **ISO 27701**, **SOC 2 Type II** |
| Biometric data | Faces and licence plates **masked before cloud upload** |
| Retention | Local loop overwrite + event locking; policy-based cloud retention |
| Release quality gate | Every release passes a formal DI defect review and security scan |

## The five privacy features, and the article each one serves

This is the sales layer — five configurable behaviours covering collection →
transmission → storage.

**1 · Intelligent mosaic / privacy masking** — device *and* platform side AI
identifies faces and plates in real time across DMS, DSC and forward channels.
Masking applies on display, playback and export.
→ *Art. 4(5)* pseudonymisation · *Art. 9* biometric protection · *Art. 5(1)(c)*
minimisation · *Art. 5(1)(a)* fairness to third parties · *Art. 5(1)(f)* security

**2 · AI alert tolerance (local filtering)** — an occasional behaviour only
prompts the driver locally. Data below the configured threshold (e.g. 3
occurrences in a window) **never leaves the device**. Only persistent behaviour
reaches the platform.
→ *Art. 5(1)(c)* minimisation · *(b)* purpose limitation · *(e)* storage
limitation · *(a)* fairness — it gives the driver a chance to self-correct
before anything is recorded against them, which is the argument that wins works
councils.

**3 · Geofence auto-stop recording** — leaving the business boundary or
entering a private/sensitive zone cuts the video source and stops recording.
Off-shift and off-site monitoring simply does not happen.
→ *Art. 5(1)(b)* purpose limitation · *(c)* minimisation · **Art. 88**
(employment context — the article that governs member-state workplace rules)

**4 · Event-triggered cloud upload** — routine video stays on the device in a
loop. The cloud receives **only alarm fragments and metadata**; an uneventful
trip leaves no trace off-vehicle. This also removes the mass-breach surface.
→ *Art. 5(1)(c)* · *(b)* · *(f)*

**5 · Tiered retention with automatic purge**

| Tier | Data | Where | Lifecycle |
|---|---|---|---|
| **L1** Normal | Routine video | Device, local loop | Auto-overwritten (deck: 48–72h cycle) |
| **L2** Alert | Alarm clips | Cloud, restricted access | Auto-purged at end of life (deck: 30/60 days; whitepaper: configurable, e.g. 6 months) |
| **L3** Evidence | Incident evidence | Legal hold | Manual clearance after human audit only |

→ *Art. 5(1)(e)* storage limitation · **Art. 5(2)** accountability (deletion is
logged, so an audit can be answered) · *Art. 5(1)(f)* security

⚠️ **Three internal documents give three different retention figure sets** —
this deck (30/60 days), the whitepaper ("e.g. 6 months"), and the EU regulatory
briefing (7–30 days normal, 3–6 months event, 30–90 days DMS behaviour).
Retention is a **configuration**, so **quote no fixed figure** — say it is
policy-driven and set with the customer. See the table in
`24_gdpr_roles_and_contracting.md`.

Overarching: **Art. 25** (data protection by design and by default) and
**Art. 5(2)** (accountability) are what the five together are demonstrating.

## Where data actually lives — the answer to "so what is stored where?"

The sensors are not storage nodes. This is the single most reassuring fact for a
privacy officer, and it is architectural rather than a policy promise.

| Device | Generates | Stores locally? | Archived to |
|---|---|---|---|
| ADAS camera | Alarm-triggered clips | **None** | MDVR local disk (locked) |
| In-vehicle IPC camera | Continuous stream | **None** — aggregated to MDVR | MDVR local disk |
| AVM around-view camera | Analog signal | **None** | MDVR via AVM host |
| AVM host | Processed alarm/business data | **None** (processing node) | MDVR local disk |
| iButton | Driver ID signal | **None** | Not stored |
| MDVR | All channels aggregated | **Yes** — local disk | Local (primary archive) |
| Cloud platform | Uploaded video, alarms, metadata | **Yes** — EU servers | EU servers, policy-based |

Driver display and the mobile app are **live preview only — no local
recording**.

### Transmission paths

| Path | Link | Protocol | Protection |
|---|---|---|---|
| IPC → MDVR | Dedicated in-vehicle line (non-public) | TCP + N9M | Physical isolation + proprietary protocol |
| AVM sensor → AVM host | Coaxial analog (AHD) | Analog, non-IP | **No digital remote tampering path** |
| AVM host → MDVR | In-vehicle Ethernet | TCP + proprietary | Vehicle-only |
| **MDVR → cloud** | 4G / 5G / Ethernet | **mTLS 1.3 + N9M** | Full-channel encryption |
| MDVR → driver display | VGA/CVBS | display signal | Never touches the public Internet |
| MDVR → mobile app | Local Wi-Fi | live stream | Local only; app does not record |
| Browser → platform | HTTPS | TLS | — |
| External API | HTTPS + signature | — | Sensitive fields AES-256 |

**N9M is the proprietary in-vehicle transport protocol** — not a hardware model.
See the note at the end of this file; this has been repeatedly misread as a
device.

## Retention and deletion, precisely

- **Mode 1, continuous loop:** all channels record to the local disk. Below ~1%
  free space the system overwrites the **oldest ordinary** footage first.
  Locked clips are never touched.
- **Mode 2, event/alarm video:** ADAS alarms, emergency button and driving-
  behaviour warnings are **locked**, exempt from loop overwrite, and kept until
  the lock expires or an authorised user unlocks them. Lock duration is
  configurable **per alarm type**.
- Cloud alarm evidence: configurable retention, automatic deletion at expiry.
- Credentials/configuration: AES-GCM-256, managed deletion.
- Audit logs: retained per SLA/regulatory requirement.

## Data subject rights (Art. 15–22) — what the platform can actually do

| Right | Implementation |
|---|---|
| Access (DSAR) | Data management console; per-user structured export (JSON/CSV); standard API |
| Erasure | Hard-deletion policy; physical deletion at selected DB levels; backup overwrite |
| Portability | API export, JSON/CSV |
| Restriction of processing | Channel-level and role-level isolation |
| Breach notification | Automated detection/alerting supporting the **Art. 33 72-hour** obligation |

## Security controls (TOMs) worth naming in a bid

RBAC by role · **MFA on all platform accounts** · least privilege ·
**multi-tenant logical isolation** · IP allowlisting + key auth on the open API ·
**bastion host with session recording** for all internal access to customer
environments · MDVR requires a device password to power on and read stored data ·
customer-managed keys supported (**BYOK / KMS**).

Access governance: no employee may enter a customer environment without the
customer's **written authorisation**; high-risk operations need internal approval
and run through the bastion host (*Platform Customer Environment Operation and
Management Standard V1.0*).

Release security: `DI = 10×Critical + 3×Major + 0.2×Minor + 0.1×Info`. **Any
critical defect blocks release.** Pre-release scanning: Nessus (infrastructure),
AWVS (web), OWASP Top 10 coverage, plus regular third-party penetration testing
(*Device Software Version Release Standard QMC-WI-53 V1.5*).

## Data residency and the three deployment answers

All EU customer platforms are hosted **inside the EU** — storage, processing and
backup. Personal data does not leave the EU without a lawful transfer mechanism.

When residency is the blocker, there are three escalating answers:

1. **On-premises** — platform runs on the customer's own EU infrastructure, no
   Streamax-hosted servers.
2. **Closed network** — platform operates on an internal network with no public
   Internet access.
3. **Fully local device operation** — MDVR and cameras run entirely on-vehicle,
   **all data stays in the vehicle, no cloud at all.**

Option 3 ends most residency objections outright. Reach for it when a customer
says cloud is categorically unacceptable.

## Certifications — mind the status column

| Certification | Status |
|---|---|
| ISO 27001 (ISMS) | **Certified** — annual surveillance audit |
| ISO 27701 (PIMS) | **Certified** — ongoing |
| SOC 2 Type II | **Certified** — annual third-party audit |
| GDPR compliance statement (DPA template, data mapping) | Completed, continuously maintained |
| ISO/SAE 21434 | **In progress** — not yet certified |
| UN R155 / R156 (CSMS / SUMS) | **Supported** — type-approval basis |

⚠️ **Never describe ISO/SAE 21434 as held, or R155/R156 as a certification.**
"In progress" and "supported" are not "certified", and a technical evaluator
will check.

## Incident response

Detection (automated) → containment (isolate, cut suspicious connections) →
**secure erasure of suspected-disclosure files before deletion** → recovery from
backup + patch → notification to the controller within SLA, supporting the
**Art. 33 72-hour** obligation. Streamax is typically the **processor**; the
customer is the controller and owns the regulator notification.

## Summary — requirement to response

| GDPR requirement | Streamax response |
|---|---|
| Lawful basis & transparency | DPA, privacy notice, purpose-bound collection |
| Data minimisation | No long-term sensor storage; configurable upload scope |
| Purpose limitation | Contractual restriction; DMS/ADAS data for safety only |
| Storage limitation | Loop overwrite + event locking + cloud retention policy |
| Integrity & confidentiality | TLS 1.3, AES-256, RBAC, bastion host |
| Data subject rights | API access/export/deletion; automated lifecycle |
| EU data residency | EU servers; on-prem option; fully local option |
| Accountability | ISO 27001/27701, SOC 2 Type II, DPA, audit logs, release process |
| Breach notification | Automated detection, SLA response, 72-hour support |

## Boundaries — what this file does not settle

- **Not legal advice, and not a compliance guarantee.** Product capability only.
- **The whitepaper is an unreleased draft.** Do not attach or forward it.
- Retention figures are **configuration**, and the two sources differ — agree
  them with the customer rather than quoting one.
- **DPA terms, liability and service commitments** are contractual — legal and
  regional sales own them.
- Member-state employment law under **Art. 88** varies (works councils, notice
  and consultation duties). Streamax provides the geofence and tolerance
  controls; the customer's local counsel decides what their jurisdiction needs.
- **"N9M" is the proprietary in-vehicle transmission protocol**, evidenced three
  times in the whitepaper (encryption-in-transit line, IPC→MDVR path, MDVR→cloud
  path). It has been asked about repeatedly as though it were a hardware model
  and refused as unknown — that refusal is now resolved *for the protocol
  sense*. A separate question about an "N9M2.0" device remains **unconfirmed**:
  no such model exists in the product database or any solution deck, so do not
  invent a relationship to A8Pro 2.0 or anything else.
