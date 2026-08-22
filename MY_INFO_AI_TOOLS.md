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
| `my_info_advance` | Create or update client-owned state and return the next question or timing prompt. |
| `my_info_evaluate` | Return ranked candidate PIBs and conservative holding estimates. |
| `my_info_explain_result` | Explain one result using question triggers and full derivation evidence. |

Every tool is read-only, idempotent, non-destructive, and closed-world. `advance` returns a new
state object but does not store a server-side session.

## State and privacy

State uses controlled values only:

```json
{
  "schema_version": "1.0",
  "contract_version": "2026-08-22.1",
  "locale": "en-CA",
  "answers": {
    "q_tax_customs": {
      "value": "yes",
      "timing": {"kind": "within_1_year"}
    }
  }
}
```

The engine rejects fields outside the state, answer, and timing schemas. It does not accept a
name, account number, case description, medical detail, exact travel history, or narrative free
text. `not_sure` and `prefer_not_to_answer` remain uncertainty signals; they are not converted to
negative answers.

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

The endpoint is `http://127.0.0.1:8000/mcp`. The server uses stateless JSON responses. A hosted
or publicly listed plugin endpoint is not part of this implementation.

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

## Current limitations and next tool work

This is an executable baseline, not the final public questionnaire. It still uses the 19 broad
top-level gates. The voice-session fixture demonstrates that the tools preserve answers and
produce explainable results, but broad questions can still nominate unrelated PIBs.

The next tool-engine milestone should add versioned adaptive child routes before public hosting:

1. split taxes from customs and infer CRA or CBSA;
2. split Canadian Armed Forces service from Veterans Affairs programs;
3. split security screening from police and corrections matters;
4. add explicit firearms licensing, pleasure-craft operator card, and pleasure-craft licence
   routes; and
5. add institution/program selection only where the answer materially reduces candidates.

Those branches should be implemented in the shared contract and engine, then exercised through
the same MCP tools. Tool names and top-level schemas can remain stable.

## Validation

```bash
.venv/bin/python -m unittest tests.test_my_info_agent_tools
.venv/bin/python -m unittest discover -s tests
.venv/bin/python validate_my_info_features.py
git diff --check
```

The MCP tests connect through the SDK's in-memory protocol client, inspect all advertised
schemas and annotations, call the manifest tool, run the prior voice-session answers through the
engine, correct an answer, reject narrative fields, evaluate candidates, and explain a result.
