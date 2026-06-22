# Streamax eSIM Solutions

Distilled from the *Streamax eSIM Solutions v2* deck (June 2026). Theme:
**lower TCO, higher uptime.** A downloadable copy of this deck is offered
automatically in Jerry GPT whenever a user asks about eSIM (see the
interface note — name "eSIM" in the answer and a download button appears).

## The pain points it solves
1. **Self-sourced SIMs** — clients buy/install plastic SIMs themselves; re-pack costs ~$10–15/unit, and factories can't reliably test overseas SIMs before shipment.
2. **SIM malfunction** — plastic SIMs degrade under heat; 2–3 years later data silently fails → false RMAs and reputation risk.
3. **Hidden costs** — truck rolls and unplanned downtime add big operational expense that rarely shows up in the initial procurement budget.

## What it is
- **eSIM** — a tiny built-in SIM chip inside the device (dashcam, tracker, MDVR). Instead of inserting a plastic SIM, you download a carrier profile like installing an app — activate, switch carriers, or change plans **remotely (OTA)**, no opening devices, no swapping cards.
- **eUICC** — Embedded Universal Integrated Circuit Card: the underlying standard/architecture that lets a device remotely download, store, and switch between multiple operator profiles over the air. It's what makes remote carrier changes possible.

## Two form factors (both supported)
- **Triple-Cut SIM card** — removable, Mini/Micro/Nano. Like a phone SIM; field-swappable, familiar format, pre-provision per region.
- **MFF2 (soldered)** — M2M chip-on-board, soldered to the device board. No slot to corrode; vibration-proof, sealed & tamper-resistant, automotive-grade. Built for sealed deployments.

## Why Streamax eSIM
- **Proven reliability** — automotive-grade hardware for heat, vibration, continuous operation.
- **OTA management** — activate, switch carriers, update policies remotely. No truck rolls, no disassembly, no downtime.
- **Lower total cost** — eliminate re-packaging fees, reduce field visits, full cost visibility via per-device telemetry + automatic caps.
- **Single partner SLA** — one contact for hardware + connectivity + diagnostics; faster resolution, clearer accountability.

## Value propositions
- **Higher uptime / fewer mystery outages** — automotive-grade eSIMs tolerate heat & vibration far better than plastic, preventing the 2–3 year degradation that causes silent data loss → fewer false camera failures, fewer RMAs, more reliable video uploads.
- **Zero-touch provisioning / faster rollouts** — ship sealed devices; activate, assign APNs, set policies OTA. Bulk provisioning (IMEI ↔ ICCID mapping), policy templates, automated QA cut weeks from deployment.
- **Carrier agility without hardware swaps** — multi-profile eUICC switches carrier/IMSI OTA — ideal for coverage gaps, roaming cost, or 2G/3G sunsets. Pick LTE Cat-1 / Cat-M / NB-IoT per region without touching the truck.
- **Better video-telematics performance** — private APN/QoS, pooled data, burst allowances keep alert clips + evidence uploads flowing during spikes (collisions, storms, audits).
- **Stronger security & compliance** — private APN/VPN, IMEI lock, SIM-theft prevention, line-level audit trails; centralized policy = fewer field misconfigurations.
- **Deep diagnostics & cost control** — per-device telemetry on signal, registration state, fallback behavior, data usage; automatic alerts, caps, remote suspend/resume — no bill shocks.

## TCO & future-proofing
TCO = full lifecycle cost (purchase + operations + maintenance + disposal). eSIM lowers it: no re-packaging fees, no client labor to open/install/repack, far fewer SIM-fault site visits — a single avoided truck roll often offsets months of connectivity fees. **Future-proofing:** eUICC keeps you ready for new radio profiles (LTE-M / NB-IoT, 5G RedCap) as networks evolve — no hardware changes or field visits.

## Data plans — dynamic pooling (default)
Every Streamax data plan defaults to a **dynamic pool**: pick a per-device allowance, and the shared monthly pool scales automatically as devices join — no per-SIM overage juggling, usage shared fleet-wide.
- Formula: (per-device allowance) × N devices = shared monthly pool.
- Worked example at 3 GB/device/mo: 1 device → 3 GB pool; 10 devices → 30 GB; 11 devices → 33 GB. Adding a device adds its allowance to the shared pool — no stranded per-SIM allowances, no manual top-ups.

## Platform
Managed via the **FT Cloud Platform** (provisioning, policy, telemetry, alerts, suspend/resume).

## Downloadable asset
`Streamax-eSIM-Solutions-v2.pptx` — the full 13-slide deck. Offered as a download in Jerry GPT on any eSIM query.
