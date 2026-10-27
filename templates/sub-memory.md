# Website templates — sub-memory

Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.
Parent: [Website memory](../sub-memory.md).

## Working memory — 2026-10-27

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W-MS | state | platform,deploy | continuing Microsoft Authenticator rollout | Microsoft entry appears before password form, with a pending company-setup notice when unconfigured. Mobile logo overflow fixed; 390px layout rechecked. | login.html | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | product | changing the login Streamax logo | Keep it linked in the same tab to https://www.streamax-trucking.com/ | E1 | stable |

## Short-term memory

### E1 — Return to trucking, 2026-10-20

The owner requested every page linked from the trucking homepage to return there
when its Streamax logo is clicked. Wrapped the login logo in a named link and
kept its missing-image fallback working with the new wrapper. The signed-in
landing-page logo is updated in app.py. Build and 33 resource/version checks pass.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E1 | episode | product,verification | checking the login logo destination | Both entry surfaces now use the absolute trucking homepage URL | login.html; ../app.py | consolidating |

## Short-term — Microsoft sign-in

### E-MS — 2026-10-27

Microsoft entry appears before password form, with a pending company-setup notice when unconfigured. Mobile logo overflow fixed; 390px layout rechecked.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-MS | episode | platform,verification | enabling Microsoft Authenticator | Microsoft entry appears before password form, with a pending company-setup notice when unconfigured. Mobile logo overflow fixed; 390px layout rechecked. | login.html | consolidating |
