# Sub-memory — Construction vehicle solutions

Parent: `../sub-memory.md`. Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.

## Working memory — 2026-10-23

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W1 | state | platform,verification | resuming the construction knowledge release | Distillation and private download code pass local tests; deployment and live-answer check pending | ../../scripts/test_construction_knowledge.py | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | product | source excerpts conflict about a route or part | S1 Routes and 02_Master_SKUs plus S3 current baselines/interfaces govern; historical source C07 is M3N, canonical C07 is M1N two cameras | ../27_construction_vehicle_solutions.md | stable |
| R2 | rule | product | specifying five-camera wiring or kit inclusion | C09 is one direct plus four switched; M3N current 20-pin 0539 is included; C06 0017 camera fallback is PoC only | S2 pp. 2,7,9,10; S1 master | stable |
| R3 | rule | platform | offering construction source documents | Serve all three original files through authenticated allowlisted routes; keep them outside public assets and preserve source hashes | ../../downloads.py; source-manifest.json | stable |
| R4 | rule | verification | treating a configuration or version as released | Confirmed SKUs, recorded integration and signed QA/region approvals are separate; DEBUG filename and legacy drawings do not establish production approval or current pinouts | S3 verification policy; ../27_construction_vehicle_solutions.md | stable |

## Short-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E1 | episode | product,platform | tracing the first construction import | Read 11 BOM sheets, 8 technical sheets and all 12 PDF pages; preserve three originals and use a source-linked distilled module | source-manifest.json; ../27_construction_vehicle_solutions.md | consolidating |

### E1 — First import, 2026-10-23

The owner requested answers distilled from the three supplied documents, with
all originals downloadable for complicated construction visibility questions.
The new module covers five detailed C06–C10 routes, six project-reference routes,
regional SKUs, inclusion/cable/display/alarm rules, recorded software, open QA,
TCO and customer-release review. Source hashes are in `source-manifest.json`.
No original file was modified. S3 B02's legacy `C07/03/04` action cell and C04's
`C02 / 03B` suffix are flagged against the canonical baseline rather than copied
as current route definitions. Old visibility module 05 now defers construction
selection to module 27 instead of prescribing local AHD for every jobsite.

The private downloads are `/api/jerry/documents/construction_bom`,
`/api/jerry/documents/construction_diagrams`, and
`/api/jerry/documents/construction_validation`. They work for ordinary signed-in
users and VIP/owner users; anonymous reads receive 401, unknown IDs 404. Three
documents take priority together within the existing four-download cap.
Maintainer memory is excluded from model knowledge and the daily evidence search.

Local verification: 8 construction tests (including byte hashes, attachment/MIME,
all-user access, absent public copies, EN/Chinese triggers, real prompt loading,
and daily evidence retrieval), 19 existing download checks and 33 resource/version
checks pass. Production verification is recorded after deployment below.
