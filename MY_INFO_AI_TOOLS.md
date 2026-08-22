# My Info AI tools

## Implemented slice

My Info now has a framework-neutral survey engine and a local Model Context Protocol (MCP)
adapter. Both use the generated questionnaire and PIB feature snapshot; neither reproduces
matching or retention logic in an agent prompt.

The tool surface follows the official OpenAI guidance to define one focused tool per user goal,
with explicit input and output schemas and accurate safety annotations:
[Build an MCP server](https://developers.openai.com/plugins/build/mcp-server).

| Tool | Purpose |
|---|---|
| `my_info_get_manifest` | Return versions, controlled values, privacy constraints, and limitations before a survey starts. |
| `my_info_advance` | Create or update client-owned state and return the next question, adaptive selection, or timing prompt. |
| `my_info_evaluate` | Return ranked candidate PIBs and conservative holding estimates. |
| `my_info_explain_result` | Explain one result using question triggers and full derivation evidence. |

Every tool is read-only, idempotent, non-destructive, and closed-world. `advance` returns a new
state object but does not store a server-side session.

## State and privacy

State uses controlled values only:

```json
{
  "schema_version": "1.1",
  "contract_version": "2026-08-22.2",
  "locale": "en-CA",
  "answers": {
    "q_tax_customs": {"value": "yes"}
  },
  "refinements": {
    "q_tax_customs": {
      "selected_options": ["customs_declaration"],
      "timings": {
        "customs_declaration": {"kind": "within_1_year"}
      }
    }
  }
}
```

The engine rejects fields outside the state, answer, refinement, and timing schemas. It does not accept a
name, account number, case description, medical detail, exact travel history, or narrative free
text. `not_sure` and `prefer_not_to_answer` remain uncertainty signals; they are not converted to
negative answers.

Adaptive routes are controlled multi-select values. Each selected route has its own timing, so
Canadian Armed Forces service and a later Veterans Affairs interaction can be assessed separately.
The agent should pass the complete returned state to the next call. Answer corrections replace
the prior controlled value and recalculate results without retaining a transcript.

## Run locally

Install the repository dependencies, then start the server over standard input/output:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m my_info.mcp_server
```

A local MCP client can configure:

```json
{
  "command": "/home/pat/pibs/.venv/bin/python",
  "args": ["-m", "my_info.mcp_server"],
  "cwd": "/home/pat/pibs"
}
```

For local Streamable HTTP testing:

```bash
.venv/bin/python -m my_info.mcp_server --transport streamable-http --host 127.0.0.1 --port 8000
```

The endpoint is `http://127.0.0.1:8000/mcp`. The server uses stateless JSON responses.

## Use the hosted MCP

Remote AI clients can use this Streamable HTTP endpoint:

```text
https://lovely-nasturtium-97f019.netlify.app/my-info/mcp
```

The Netlify function is a deployment adapter for the portable JavaScript runtime under
`packages/my-info-mcp`. The Python and JavaScript adapters share the generated contract and
feature data. The endpoint does not create survey sessions or store answer state. An AI platform
may retain the surrounding conversation under its own policy, which is separate from MCP storage.

The repo-contained Codex plugin is under `plugins/my-info-canada`. It combines the hosted MCP
connection with a small skill that tells an agent how to ask one controlled question at a time,
offer examples, handle corrections, and avoid collecting identifiers or narrative case details.

## Generate and inspect schemas

```bash
.venv/bin/python scripts/export_my_info_mcp_tools.py
```

This writes `data/derived/my_info/my_info_mcp_tools.json`, including server metadata, the
manifest, every tool's JSON input and output schema, and the safety annotations advertised to
MCP clients.

## Result behaviour

- A direct primary question match becomes `strong_match`.
- A broader candidate question match becomes `possible_match`.
- A match caused only by `not_sure` or `prefer_not_to_answer` becomes
  `review_if_relevant`.
- Holding results use `likely_held`, `may_still_be_held`, `likely_disposed`, or
  `retention_unknown`.
- A range is classified as disposed only when even its most recent possible date is beyond a
  published maximum followed by destruction.
- A distinct trigger such as file closure, departure, or last administrative action remains
  unknown until a future adaptive trigger question supplies that year.
- Results always state that a match is a candidate, not proof that a record exists.

The engine returns strong matches by default. A client must explicitly set
`include_possible=true` to add possible and review results. Each response contains at most 50
records by default, accepts an `offset`, and returns `next_offset` when another page exists. The
hard page limit is 500. Full published evidence stays in `my_info_explain_result`; evaluation
rows contain only a short retention-text excerpt so an agent is not flooded with narrative data.

## Adaptive routing

The contract contains 21 top-level gates and nine adaptive route groups. Direct route selections
supersede the broad classifier and become strong matches even when the underlying PIB was only a
candidate under the earlier keyword model. Implemented splits include:

- federal applicant versus employee records;
- named payment and benefit families;
- CRA tax filing versus CBSA customs declarations;
- passport, border-crossing, and trusted-traveller interactions;
- Canadian Armed Forces service versus Veterans Affairs programs;
- security screening, federal policing, and corrections/parole;
- federal contracting and aviation licences; and
- explicit firearms and boating routes, including separate operator-card, craft-licence, and
  vessel-registration choices.

The prior voice-session fixture falls from 347 broad strong matches to 54 route-aware strong
matches. Further child routes are still needed for broad civic, health, immigration, research,
and miscellaneous program answers. Tax filing currently produces an explicit inventory-gap
notice instead of falsely mapping the blank CRA source rows.

## Portable Netlify bundle

Build and test the JavaScript bundle used by the Netlify deployment adapter:

```bash
.venv/bin/python scripts/export_my_info_netlify_bundle.py
cd packages/my-info-mcp
npm install
npm test
```

The exporter creates a disposable `dist/` directory with the MCP server, compact runtime data,
lazy explanation evidence, and pinned upstream metadata. The deployment repository vendors that
generated directory; business logic remains here.

## Validation

```bash
.venv/bin/python -m unittest tests.test_my_info_agent_tools
.venv/bin/python scripts/export_my_info_netlify_bundle.py
npm --prefix packages/my-info-mcp test
.venv/bin/python -m unittest discover -s tests
.venv/bin/python validate_my_info_features.py
git diff --check
```

The MCP tests connect through the SDK's in-memory protocol client, inspect all advertised
schemas and annotations, call the manifest tool, run the prior voice-session answers through the
engine, correct an answer, reject narrative fields, evaluate candidates, and explain a result.
