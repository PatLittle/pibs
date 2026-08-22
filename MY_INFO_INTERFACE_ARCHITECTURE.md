# My Info interface architecture

## Decision

Build one versioned, deterministic survey engine and put two interfaces over it:

1. a browser-first web experience; and
2. an AI-agent experience delivered as a **skill plus an MCP server**, packaged together as a plugin for ChatGPT and Codex.

The MCP tools should be the authoritative calculation interface. The skill should teach an agent how to conduct the conversation well: explain the purpose, ask only the next relevant question, offer examples when helpful, avoid collecting unnecessary details, and present the result with the correct caveats. Do not put matching or retention logic only in the skill prompt.

This division follows the product boundary in the official OpenAI documentation: [skills provide repeatable workflow instructions and resources, while MCP servers provide structured tools and controlled actions](https://developers.openai.com/plugins/concepts/skills). OpenAI's [plugin architecture](https://developers.openai.com/plugins/concepts/plugins) supports packaging both together. MCP is also an open specification, so the MCP endpoint is the better long-term compatibility surface for AI clients outside ChatGPT and Codex, subject to each client's MCP support.

The recommended delivery sequence is not “build a large hosted service first.” Start with the shared contract and a thin skill pilot, then add a small stateless MCP adapter once the question flow is stable. The browser remains the strongest privacy option because it can run entirely on the user's device.

## Shared architecture

```text
SPIB and institution-specific PIB source files
                    |
                    v
        deterministic feature builder
                    |
                    v
     versioned My Info survey contract
       |             |              |
       v             v              v
  browser engine   local/hosted    test fixtures
  and web UI       MCP adapter     and audit reports
                       |
                       v
                conversational skill
```

The current repository already supplies much of the lower layer:

- `my_info/interactions.py` defines stable question codes and maps PIB evidence to question triggers;
- `my_info/retention.py` parses retention rules and produces conservative holding estimates;
- `build_my_info_features.py` generates a bilingual questionnaire and auditable PIB feature datasets; and
- `data/derived/my_info/my_info_questionnaire.json` is the natural starting point for a portable contract.

The next step is to turn that generated questionnaire from a flat question list into an explicit state-machine contract. Both interfaces must consume the same generated artifact and call the same evaluation code. This prevents the web and agent experiences from silently producing different results.

## Canonical survey contract

The contract should be public, machine-readable JSON with a published JSON Schema. It should contain five sections.

### Manifest

- `schema_version`: compatibility version for the shape of the JSON;
- `content_version`: version for wording, examples, and routing changes;
- `data_snapshot`: date or immutable identifier for the PIB dataset used;
- `generator_version`: version of the feature derivation code;
- `supported_locales`: initially `en-CA` and `fr-CA`;
- `privacy_notice_version`; and
- links to methodology, limitations, and source data.

Schema and content versions should be separate. A wording improvement should not force clients to adopt a new API shape, while a routing or scoring change must remain traceable in saved or exported results.

### Question definitions

Each question should include:

- stable `question_code`;
- bilingual prompt, short label, and optional explanation;
- response type and allowed values;
- one or more real-world examples, each naming the institution and activity;
- routing conditions and any deterministic institution inference;
- follow-up question codes;
- whether an approximate year can change a retention result;
- linked interaction, role, action, and institution codes; and
- readability score, review status, and wording version.

The default top-level response set should be `yes`, `no`, `not_sure`, and `prefer_not_to_answer`. Timing should use a controlled choice such as `current`, `within_1_year`, `1_to_3_years`, `4_to_7_years`, `8_to_15_years`, `more_than_15_years`, or `approximate_year`. Free text should not be required.

### Client-owned survey state

The survey state should be plain JSON so it can move between web, MCP, command-line, and test clients:

```json
{
  "schema_version": "1.0",
  "content_version": "2026-08-22.1",
  "locale": "en-CA",
  "answers": {
    "q_tax": {"value": "yes", "timing": "within_1_year"}
  },
  "inferences": [
    {
      "code": "institution_cra",
      "basis": "q_tax=yes",
      "confidence": "deterministic"
    }
  ]
}
```

The state should not include a person's name, account number, tax number, case facts, medical facts, or exact travel history. Going back should replace an answer and recalculate downstream routing and results; it should not append an unbounded conversational transcript.

### Result contract

Each result should include:

- PIB record ID, bank number, title, institution, and scope (`standard` or `institution_specific`);
- match band (`strong_match`, `possible_match`, or `review_if_relevant`);
- holding status (`likely_held`, `may_still_be_held`, `likely_disposed`, or `retention_unknown`);
- the question, answer, institution inference, and source-text evidence that caused the match;
- relevant categories of personal information;
- retention trigger, timing assumption, source wording, and caveats;
- English and French source links when available; and
- the data snapshot and rules version used.

Scores may sort results, but should not be shown as a probability that a record exists. A standard PIB result must not imply that every federal institution holds a copy.

### Engine operations

Keep the domain API independent of HTTP, MCP, and the browser:

- `create_state(locale, versions)`
- `get_next_step(state)`
- `apply_answers(state, answers)`
- `get_question_help(question_code, locale)`
- `evaluate(state, as_of_date)`
- `explain_result(state, record_id, locale)`

All operations should be deterministic for a fixed contract version, data snapshot, answer set, and assessment date.

## Web interface

### Survey experience

Use one main question per page. Provide large radio-button targets, a visible Back button, a Continue button that activates only after a selection, and a persistent “Save on this device” option only if local persistence is added intentionally. Do not save answers by default.

Because branching makes the exact length uncertain, show progress as “Step 4 — about 7 questions left” or by completed sections rather than “4 of 21.” The browser history should not expose answer values in URLs.

Recommended layout for a question:

- short category label;
- plain-language question;
- `Yes`, `No`, `Not sure`, and `Prefer not to answer` radio buttons;
- a collapsed “Show examples” control when the interaction may be unfamiliar;
- one to three concrete examples with the department or agency bolded in the rendered interface;
- an explanation of why the question is being asked; and
- timing only after `yes`, and only when it can improve the holding estimate.

Common, deterministic interactions can be compact. For example, “Did you file federal taxes?” can route to the Canada Revenue Agency without asking the person to identify the department. International border crossing can route to the Canada Border Services Agency. Compound questions that span institutions or different retention triggers should be split into child questions after a broad affirmative answer.

### Results experience

Lead with a clear statement that the result is an estimate, not confirmation that the government holds a record. Then use four visually distinct, accessible result lanes:

1. likely still held;
2. may still be held;
3. likely disposed of; and
4. retention unknown.

Within each lane, group cards first by institution and then distinguish standard from institution-specific PIBs. Each card should show a concise “Why this matched” explanation, categories of personal information, the applicable timing assumption, and links to the source descriptions.

A compact stacked bar can summarize counts by holding status, and a second chart can summarize matched PIBs by institution or personal-information category. Charts must display counts, not risk scores or false probabilities. Every visual needs an equivalent text/table view and must not rely on colour alone.

Useful controls are:

- filter by institution, match band, PIB scope, and category;
- switch English/French without restarting;
- edit an answer and recalculate;
- print or download a local result report that excludes the raw answer history by default; and
- clear all answers immediately.

## AI-agent interface

### Why a skill alone is not enough

A skill-only pilot is fast and useful for testing tone and question sequencing. It can package the survey instructions, privacy language, examples, and expected output. Official OpenAI documentation confirms that a skill can work without an MCP server when packaged instructions and resources are sufficient ([Skills](https://developers.openai.com/plugins/concepts/skills)).

It should not be the production calculation layer, however. A prompt-only implementation can drift: an agent may paraphrase away a distinction, skip a required follow-up, apply stale retention data, or produce different results from the website. Updating a bundled data snapshot can also require distributing a new skill version.

### Why MCP should be the authoritative agent interface

MCP provides named tools with input and output schemas, server-side validation, and structured results. The [official MCP server documentation](https://developers.openai.com/plugins/concepts/mcp-server) describes this as the mechanism for exposing tools and data to AI clients. The OpenAI Responses API also supports MCP tools and function calls as structured tool categories ([Responses API reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)).

For My Info, MCP is valuable even though the source data is public because the important capability is controlled execution of a versioned state machine. It also lets rules and data snapshots be updated independently of conversational wording. Because MCP is an open protocol, the same tool contract can be usable by other supporting AI clients; maintain the JSON Schema and command-line adapter as fallbacks for clients that do not support MCP.

### Recommended MCP tools

Use a small, read-only tool surface. Fewer, higher-level tools reduce agent error and unnecessary disclosure.

#### `my_info_get_manifest`

Returns current contract versions, supported locales, methodology links, and privacy notice. It accepts no personal answers.

#### `my_info_advance`

Accepts client-owned state plus one or more controlled answers. It validates the answers, recalculates routing, and returns updated state and the next question or questions. It should return examples and explanations with the question rather than requiring a second round trip.

#### `my_info_evaluate`

Accepts client-owned state and an assessment date. It returns the complete structured result set, source evidence, and an agent-ready summary. It must never turn a candidate match into confirmation that a record exists.

#### `my_info_explain_result`

Accepts state, a PIB record ID, and locale. It returns the precise answer path, institution inference, retention reasoning, caveats, and source links for one result.

An optional `my_info_validate_state` tool can support third-party clients and migrations. Avoid separate tools for every survey question and avoid a server-side `session_id` unless later research establishes a real need.

### Skill responsibilities

The companion skill should instruct the agent to:

- obtain informed consent before starting;
- explain that answers pass through the person's AI client and, for a hosted MCP service, the MCP endpoint;
- ask one question at a time unless the user asks for a faster batch mode;
- accept natural speech such as “currently” or “about three years ago” and map it to controlled values without preserving the transcript;
- offer examples when the question is unfamiliar or when the user asks, without treating examples as an exhaustive list;
- use deterministic inferences instead of asking obvious department questions;
- never request identifiers or case details;
- use MCP output rather than independently recalculating matches;
- let the person correct any earlier answer; and
- present the four holding-status groups, evidence, limitations, and source links.

For ChatGPT and Codex distribution, package the skill and MCP connection as one plugin. Official OpenAI guidance explicitly supports a plugin containing both a skill and an MCP server ([Plugin architecture](https://developers.openai.com/plugins/concepts/plugins)). This is a distribution choice, not a reason to couple the domain engine to OpenAI-specific code.

## Privacy and trust boundary

The survey concerns potentially sensitive government interactions even when it avoids names. Privacy must be a feature of the protocol rather than a promise in the interface.

- Keep web answers in memory on the device by default.
- Keep MCP state client-owned and make every tool stateless.
- Do not log raw tool arguments, answer maps, prompts, or result bodies.
- Redact answer content from error reporting and telemetry; use contract version, error code, and a random correlation ID instead.
- Accept controlled values and approximate periods, not narrative case details.
- Do not require an account merely to use public survey data.
- Publish the exact data-retention policy for the hosted endpoint.
- Provide a local MCP/package mode for people who do not want answers sent to a hosted My Info service.
- Make clear that the AI platform may have its own data practices outside the My Info service.

OpenAI's [plugin security and privacy guidance](https://developers.openai.com/plugins/guides/security-privacy) calls for least privilege, explicit consent, retaining only necessary structured content, a published retention policy, and redacting personally identifiable information from logs. A hosted My Info MCP service should go further and retain no survey answers at all.

No authentication is needed for the public, read-only dataset in the initial design. If future tools retrieve a person's actual government records, that would be a different service requiring separate privacy, security, identity, consent, and legal review.

## Deployment modes

| Mode | Privacy | Update model | Client reach | Recommended use |
|---|---|---|---|---|
| Browser-only | Strongest: answers stay on device | Publish new static assets | Any modern browser | Primary public experience |
| Skill-only | Answers remain in the AI conversation; engine discipline is weaker | Reinstall/update skill | Skill-capable clients | Early conversational pilot only |
| Local MCP + skill | Tool execution and survey state stay on device | Update local package | MCP clients that can run local servers | Privacy-sensitive agent use |
| Hosted stateless MCP + skill | Answers transit the AI client and MCP endpoint but are not retained | Central server update | Remote-MCP clients | Convenient public agent experience |
| OpenAI plugin containing skill + MCP | Same as selected MCP mode | Plugin/server versioning | ChatGPT and Codex supported surfaces | Recommended OpenAI distribution |

## Phased delivery

### Phase 1 — Stabilize the contract

- Add response schemas, examples, routing, readability metadata, version fields, and result schemas to the generated questionnaire artifact.
- Implement the framework-independent state-machine operations.
- Add golden fixtures representing the voice-session path and edge cases such as corrections, `not_sure`, and different retention triggers.

### Phase 2 — Build the web interface and skill pilot

- Build the browser wizard and results visualization against the shared engine.
- Create an installable skill that uses the same question/help content and follows the conversational rules above.
- Test the skill with natural-language answers, interruptions, corrections, and requests for examples.
- Treat its results as a UX pilot unless it calls the deterministic engine.

### Phase 3 — Add the MCP adapter

- Expose the four small read-only tools.
- Offer a local package first; add a hosted stateless endpoint when its no-storage and no-raw-logging guarantees have been tested.
- Package the skill and MCP server as an OpenAI plugin while publishing the MCP and JSON contracts independently.

### Phase 4 — Prove parity and publish

- Run the same answer fixtures through the Python/domain engine, browser build, local MCP server, hosted MCP server, and skill flow.
- Require equivalent question routing and identical result record IDs, statuses, rule versions, and evidence.
- Add accessibility, bilingual, privacy, injection, malformed-state, and version-migration tests.
- Publish a machine-readable changelog and keep previous immutable data snapshots available for result provenance.

## Release gates

The second interface is ready for public use only when:

- the web and MCP paths return the same results for the same versioned state;
- the agent cannot omit required follow-ups or invent a PIB outside tool output;
- answer correction invalidates and recalculates dependent answers;
- English and French flows have equivalent routing and examples;
- the server produces no raw-answer logs under success and failure tests;
- every result identifies its source dataset snapshot and derivation evidence;
- `not_sure` and `prefer_not_to_answer` do not become negative answers; and
- the user can complete the survey without providing free-text personal details.

## Executive choices still required

Three choices affect implementation scope:

1. **Agent launch mode:** local MCP only for the first public release, or a hosted stateless endpoint as well.
2. **Persistence:** always ephemeral, or an explicit opt-in to save encrypted survey state on the person's device. Server-side answer persistence is not recommended.
3. **Portability commitment:** support only the OpenAI plugin initially, or publish and test the MCP/JSON contracts against at least one non-OpenAI client from the first release.

The recommended defaults are: browser-first; ephemeral answers; a local MCP plus skill pilot; then a hosted stateless MCP after privacy tests; and an OpenAI plugin that bundles the skill and MCP connection while leaving the core contract vendor-neutral.
