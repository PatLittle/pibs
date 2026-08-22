"""Local MCP adapter for the My Info AI survey tools."""

from __future__ import annotations

import argparse
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp_types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field

from .agent_tools import advance, evaluate, explain_result, get_manifest


Locale = Literal["en-CA", "fr-CA"]
AnswerValue = Literal["yes", "no", "not_sure", "prefer_not_to_answer"]
TimingKind = Literal[
    "current",
    "within_1_year",
    "1_to_3_years",
    "4_to_7_years",
    "8_to_15_years",
    "more_than_15_years",
    "approximate_year",
    "unknown",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Timing(StrictModel):
    kind: TimingKind
    year: int | None = Field(default=None, ge=1800, le=2200)


class SurveyAnswer(StrictModel):
    value: AnswerValue
    timing: Timing | None = None


class SurveyState(StrictModel):
    schema_version: Literal["1.0"]
    contract_version: str
    locale: Locale
    answers: dict[str, SurveyAnswer]


class AnswerUpdate(StrictModel):
    question_code: str
    value: AnswerValue
    timing: Timing | None = None


class ManifestOutput(StrictModel):
    tool_api_version: str
    state_schema_version: str
    contract_schema_version: str
    contract_version: str
    generator_version: str
    data_snapshot: dict[str, Any]
    supported_locales: list[str]
    question_count: int
    pib_count: int
    answer_values: list[str]
    timing_kinds: list[str]
    tools: list[str]
    privacy: dict[str, Any]
    limitations: list[str]


class QuestionExample(StrictModel):
    institution: str
    activity: str
    source_pib_keys: list[str]
    evidence_note: str


class QuestionHelp(StrictModel):
    familiarity: Literal["common", "mixed", "unfamiliar"]
    agent_offer: Literal["proactive", "on_hesitation", "on_request"]
    examples: list[QuestionExample]
    split_recommendation: str


class QuestionStep(StrictModel):
    step_type: Literal["question"]
    question_code: str
    prompt: str
    source_prompt: str
    wording_status: Literal["current", "plain_language_candidate_for_testing"]
    answer_values: list[str]
    help: QuestionHelp


class TimingStep(StrictModel):
    step_type: Literal["timing"]
    question_code: str
    prompt: str
    timing_kinds: list[str]
    year_required_for: Literal["approximate_year"]
    privacy_note: str


class SurveyProgress(StrictModel):
    answered_questions: int
    total_questions: int
    yes_answers_with_timing: int


class AdvanceOutput(StrictModel):
    state: SurveyState
    complete: bool
    next_step: QuestionStep | TimingStep | None
    progress: SurveyProgress


class Assessment(StrictModel):
    as_of_year: int
    complete_survey: bool
    unanswered_question_codes: list[str]
    uncertain_question_codes: list[str]
    refinement_needed_question_codes: list[str]
    caveat: str


class CountItem(StrictModel):
    institution_name: str
    count: int


class EvaluationSummary(StrictModel):
    total_matches: int
    returned_matches: int
    truncated: bool
    offset: int
    next_offset: int | None
    holding_status_counts: dict[str, int]
    match_band_counts: dict[str, int]
    top_institutions: list[CountItem]


class RetentionResult(StrictModel):
    status: Literal[
        "likely_held", "may_still_be_held", "likely_disposed", "retention_unknown"
    ]
    confidence: str
    rationale: str
    timing: Timing | None
    rule_type: str
    reference_events: list[str]
    published_text_excerpt: str
    published_text_truncated: bool


class CategoryResult(StrictModel):
    category_id: str
    name: str


class PibCandidate(StrictModel):
    record_id: str
    bank_number: str
    scope: Literal["standard", "institution_specific"]
    institution_id: str
    institution_name: str
    title: str
    source_url: str
    match_band: Literal["strong_match", "possible_match", "review_if_relevant"]
    matched_question_codes: list[str]
    holding_status: Literal[
        "likely_held", "may_still_be_held", "likely_disposed", "retention_unknown"
    ]
    retention: RetentionResult
    categories_of_personal_information: list[CategoryResult]
    privacy_caveat_codes: list[str]


class ToolVersions(StrictModel):
    tool_api_version: str
    state_schema_version: str
    contract_version: str
    data_snapshot: dict[str, Any]


class EvaluationOutput(StrictModel):
    assessment: Assessment
    summary: EvaluationSummary
    results: list[PibCandidate]
    versions: ToolVersions


class ExplanationOutput(StrictModel):
    result: PibCandidate
    question_triggers: list[dict[str, Any]]
    supporting_features: list[dict[str, Any]]
    retention_derivation: dict[str, Any]
    category_derivation: dict[str, Any]
    holding_inference: Literal["candidate_only"]


READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)

SERVER_INSTRUCTIONS = (
    "My Info estimates which Government of Canada personal information banks may be relevant. "
    "Call my_info_get_manifest before starting, then my_info_advance for each controlled answer. "
    "Keep the returned state client-side. Never request names, account numbers, case details, "
    "medical details, or exact travel history. Use my_info_evaluate only for estimates and never "
    "claim that a record definitely exists."
)

mcp = MCPServer(
    name="my-info-canada",
    title="My Info Canada",
    description="Privacy-minimizing questionnaire tools for estimating relevant Government of Canada personal information banks.",
    instructions=SERVER_INSTRUCTIONS,
    version="0.1.0",
)


@mcp.tool(
    name="my_info_get_manifest",
    title="Get My Info survey manifest",
    description="Call before starting a My Info survey to get current versions, supported controlled values, privacy constraints, and limitations.",
    annotations=READ_ONLY,
    structured_output=True,
)
def my_info_get_manifest() -> ManifestOutput:
    return ManifestOutput.model_validate(get_manifest())


@mcp.tool(
    name="my_info_advance",
    title="Advance the My Info survey",
    description=(
        "Start or continue the survey. Pass back the complete client-owned state returned by the previous call and one or more controlled answer updates. "
        "Use this tool to obtain the next question or timing prompt; do not add narrative personal details to state."
    ),
    annotations=READ_ONLY,
    structured_output=True,
)
def my_info_advance(
    state: SurveyState | None = None,
    answers: list[AnswerUpdate] | None = None,
    locale: Locale = "en-CA",
) -> AdvanceOutput:
    result = advance(
        state.model_dump(exclude_none=True) if state else None,
        [answer.model_dump(exclude_none=True) for answer in answers] if answers else None,
        locale=locale,
    )
    return AdvanceOutput.model_validate(result)


@mcp.tool(
    name="my_info_evaluate",
    title="Evaluate My Info survey answers",
    description=(
        "Evaluate a client-owned survey state and return ranked candidate PIBs with conservative holding estimates. "
        "Results are estimates, never confirmation that an institution holds a record."
    ),
    annotations=READ_ONLY,
    structured_output=True,
)
def my_info_evaluate(
    state: SurveyState,
    as_of_year: int | None = None,
    include_possible: bool = False,
    max_results: int = 50,
    offset: int = 0,
) -> EvaluationOutput:
    result = evaluate(
        state.model_dump(exclude_none=True),
        as_of_year=as_of_year,
        include_possible=include_possible,
        max_results=max_results,
        offset=offset,
    )
    return EvaluationOutput.model_validate(result)


@mcp.tool(
    name="my_info_explain_result",
    title="Explain one My Info result",
    description=(
        "Explain why one candidate PIB matched the supplied client-owned state, including question triggers, source-text derivation evidence, categories, and retention reasoning."
    ),
    annotations=READ_ONLY,
    structured_output=True,
)
def my_info_explain_result(
    state: SurveyState,
    record_id: str,
    as_of_year: int | None = None,
) -> ExplanationOutput:
    result = explain_result(
        state.model_dump(exclude_none=True), record_id, as_of_year=as_of_year
    )
    return ExplanationOutput.model_validate(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        if args.transport == "stdio":
            mcp.run(transport="stdio")
        else:
            mcp.run(
                transport="streamable-http",
                host=args.host,
                port=args.port,
                stateless_http=True,
                json_response=True,
            )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
