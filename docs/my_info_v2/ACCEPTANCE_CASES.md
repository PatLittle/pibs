# V2 acceptance and review cases

The executable cases are in `tests/my_info_v2.test.mjs`. Each checks a meaningful inclusion, exclusion or flow constraint. They do not replace review by program specialists or testing with members of the public.

| Situation | Required behaviour |
|---|---|
| Veterans education benefit | Infer Veterans Affairs; show VAC PPU 710; no Agent Orange bank or department question. |
| Veteran benefit, name unknown | Infer Veterans Affairs, offer its program directory; no benefit-specific record is presumed. |
| Applied for CAF, did not serve | Enrolment only; no Regular Force personnel file. |
| Served in the Regular Force | Infer DND; explain archive custody from the source without asking whether the person chose DND or LAC. |
| Served in the Reserve | Do not use the Regular Force-only bank; use the directory until the Reserve route is reviewed. |
| Common four plus NEXUS or a consultation | All remain available. A ten-year shortcut never suppresses whole topics. |
| None of the common four recently | Older and other activities remain available. Unselected is not a lifetime negative. |
| Voted federally | Voter registration/identification record; never ballot choice. |
| Filed taxes | Infer CRA and disclose the reviewed-route gap; no substitute PIB. |
| OAS and CPP | Select actual OAS 116 and CPP 146 from the ESDC publisher, not duplicate CEIC rows or CPP contribution records in place of OAS. |
| Generic complaint | Ask the recipient; require program detail before identifying an institutional complaint bank. |
| Specific CBSA service complaint | Infer CBSA; its complaint bank only. |
| RCMP member grievance | ERC 802 only after the explicit former-Act referral activity, not a general complaint against police. |
| Space launch attendance | CSA event record; no supplier role. Retention uses launch date, not registration date. |
| Contractor | Contract description; no employee pay, discipline or pension records without separate activities. |
| Passport reference | Explicit indirect-information role; no need to claim a personal passport application. |
| Standard record at an unknown institution | Show the reusable class and unknown owner, never all federal institutions. |
| Search result found | Nothing is personally matched until the person reads and confirms the program/population. |
| No reviewed timing rule | Show published text and uncertainty; no mandatory date. |
| Closure or release has not happened | Do not calculate elapsed time from the original application or complaint. |
| Approximate year overlaps threshold | Keep uncertainty. |
| Records transferred to archives | Explain possible archive custody; do not claim destruction. |
| Activity removed | Remove its dependent date/scope assumptions. |
| French interface | Same activity IDs and selectors; no different logic from English. |

Public-release review still needs: fluent French wording review; usability tests including low government-program knowledge, keyboard and screen-reader use; additional guided routes for directory-only programs; repair of source titles and missing population/purpose fields; confirmation of current retention schedules; and program specialist sign-off for eligibility and sharing claims. Benchmark scanning effort as well as screens: 56 statements hidden behind groups are not equivalent to one effortless question.
