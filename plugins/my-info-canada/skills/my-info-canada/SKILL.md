---
name: my-info-canada
description: Conduct the My Info questionnaire to estimate which Government of Canada personal information banks may relate to a person's interactions and whether records may still be held. Use when a person asks what personal information the federal government may have, wants to take the My Info survey, or wants a My Info result explained. Do not use to claim that a record exists or to retrieve actual government records.
---

# My Info Canada survey

Use the My Info MCP as the authority for question order, adaptive routes, matching, categories, and retention estimates. Do not reproduce those rules in the conversation.

Before starting, explain briefly that answers are sent through the person's AI client to a stateless My Info endpoint, while the AI platform may retain conversation content under its own policy. Ask whether they want to proceed.

1. Call `my_info_get_manifest` once. Stop if the tools are unavailable or the returned state/API version is incompatible; do not improvise an estimate.
2. Call `my_info_advance` without state to start. Preserve the complete returned `state` and pass it back on every later call.
3. Ask one `next_step.prompt` at a time. For a `question` step, map the response only to `yes`, `no`, `not_sure`, or `prefer_not_to_answer`. For a `refinement` step, map the response only to one or more returned option codes. For a `timing` step, map it only to a returned timing kind or an approximate year.
4. Send controlled question answers in `answers`. Send adaptive selections and their per-option timing in `refinements`. A correction replaces the earlier controlled value; never edit state by hand.
5. Offer `help.examples` according to `agent_offer`: give one short agency/activity example immediately for `proactive`, after hesitation for `on_hesitation`, and only when requested for `on_request`. Examples are illustrative, not proof of a record.
6. Never request or transmit a name, SIN, date of birth, account/passport/service/licence number, case facts, medical details, exact travel history, or other narrative. If volunteered, do not repeat or send it; return to the controlled choice.
7. When `complete` is true, call `my_info_evaluate` with `include_possible=false` and no more than 50 results. Group results by holding status, disclose any `inventory_gaps`, and say they are candidates rather than confirmation. Ask before including possible/review matches or fetching another page.
8. Call `my_info_explain_result` only for a result the person asks about. Do not retain or export raw survey state unless the person explicitly asks.
