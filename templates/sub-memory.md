# Website templates — sub-memory

Method: `/Users/jiachenyi/Documents/AI Skill/memory_method.md`.
Parent: [Website memory](../sub-memory.md).

## Working memory — 2026-11-05

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| W-DingTalkUI | state | platform,deploy | continuing the Microsoft-to-DingTalk replacement | Microsoft OAuth entry and new-session endpoints retired; DingTalk entry and waiting page prepared. Pending callback rejects authentication even with environment settings. Existing password access and role checks retained. Local security tests pass; publication and real provider activation must be checked separately. | login.html; dingtalk_pending.html | volatile |

## Long-term memory

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| R1 | rule | product | changing the login Streamax logo | Keep it linked in the same tab to https://www.streamax-trucking.com/ | E1 | stable |

## Short-term memory

### E-DingTalkUI — 2026-11-05

The owner requested replacing Microsoft login with DingTalk QR and explicitly allowed a waiting page until IT is ready. This release implements the waiting UI, retires Microsoft start/callback, preserves safe return paths and existing account permissions, and does not implement DingTalk token exchange or member mapping. No QR success or authenticated DingTalk session is claimed. Older working-state deployment claims were not assumed current.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-DingTalkUI | episode | platform,verification | replacing Microsoft sign-in before DingTalk is configured | Ship truthful pending UI and disable old callbacks; no configuration alone may activate unimplemented authentication. | login.html; dingtalk_pending.html | consolidating |


### E-IAM — 2026-10-30 Conditional DingTalk entry

Added a bilingual DingTalk QR sign-in option, rendered only when the server's IAM configuration is enabled and complete. Existing password and Microsoft entries remain. Local screenshots use synthetic settings; they do not demonstrate an activated production login.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-IAM | episode | platform,verification | interpreting the new QR login preview | The preview shows the activated UI condition, while production stays hidden until IT configuration. | ../iam_verification/mobile-preview.png; ../iam_verification/desktop-preview.png | consolidating |

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

### E-IAM-NoChange — 2026-10-30

The owner selected research without changing IAM. Paused publication and unstaged only this task’s staged files. Direct DingTalk OAuth avoids IAM changes but still needs authorized DingTalk application configuration. A server-side browser broker is not verified because a supported identity-validation contract has not been established. No real employee scan or production change occurred.

| id | kind | domain | trigger | claim | evidence | decay |
|---|---|---|---|---|---|---|
| E-IAM-NoChange | episode | platform | continuing DingTalk login after the no-IAM constraint | Research precedes activation; current OIDC code is an unpublished fallback, not the selected rollout. | ../DINGTALK_NO_IAM_FEASIBILITY_ZH.md | consolidating |

DingTalk UI references: [login.html](login.html); [dingtalk_pending.html](dingtalk_pending.html).
