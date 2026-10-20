# Website templates — sub-memory

Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.
Parent: [Website memory](../sub-memory.md).

## Working memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W1 | state | platform | verifying the home-logo change | Login logo is published in commit 65efddc; live HTML and health version 10.3.6 confirm it | login.html | volatile |

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
