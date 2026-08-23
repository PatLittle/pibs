#!/usr/bin/env python3
"""Render synthetic My Info personas and their survey evaluations as PDFs.

The HTML intermediates are deliberately retained: they are deterministic,
reviewable artifacts and can be generated on systems where Chromium is not
installed.  PDFs are produced by a local Chromium-family browser when one is
available.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PERSONAS = ROOT / "data/test_personas/personas.json"
DEFAULT_EVALUATIONS = ROOT / "data/test_personas/generated/evaluation.json"
DEFAULT_PORTRAITS = ROOT / "data/test_personas/portraits"
DEFAULT_OUTPUT = ROOT / "data/test_personas/generated"

STATUS_ORDER = {
    "likely_held": 0,
    "may_still_be_held": 1,
    "retention_unknown": 2,
    "likely_disposed": 3,
}
STATUS_LABELS = {
    "likely_held": "Likely still held",
    "may_still_be_held": "May still be held",
    "retention_unknown": "Retention unknown",
    "likely_disposed": "Likely disposed",
}
STATUS_COLOURS = {
    "likely_held": "#19705b",
    "may_still_be_held": "#a65e00",
    "retention_unknown": "#6b4fa1",
    "likely_disposed": "#59636e",
}


class RenderError(RuntimeError):
    """An actionable artifact-generation failure."""


def _text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _esc(value: object) -> str:
    return html.escape(_text(value), quote=True)


def _as_list(value: object) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _load_json(path: Path, label: str) -> Any:
    if not path.is_file():
        raise RenderError(f"{label} file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RenderError(f"Invalid JSON in {label} file {path}: {exc}") from exc


def _records(payload: Any, key: str, label: str) -> list[dict[str, Any]]:
    records = payload.get(key) if isinstance(payload, Mapping) else payload
    if not isinstance(records, list):
        raise RenderError(f"{label} must be a JSON array or an object containing '{key}'")
    if not all(isinstance(item, Mapping) for item in records):
        raise RenderError(f"Every item in {label} must be a JSON object")
    return [dict(item) for item in records]


def _persona_id(persona: Mapping[str, Any]) -> str:
    identifier = _text(persona.get("persona_id") or persona.get("id")).strip()
    if not identifier or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for ch in identifier):
        raise RenderError(
            "Each persona_id must contain only lowercase letters, numbers, hyphens, and underscores"
        )
    return identifier


def _portrait_data_uri(path: Path) -> str:
    if not path.is_file():
        raise RenderError(
            f"Portrait not found: {path}. Generate the real persona portrait before rendering; "
            "this pipeline never creates placeholders."
        )
    if path.suffix.lower() != ".png":
        raise RenderError(f"Persona portraits must be PNG files: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _safe_url(value: object) -> str | None:
    url = _text(value).strip()
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else None


def _list_items(values: Iterable[object]) -> str:
    rendered = "".join(f"<li>{_esc(value)}</li>" for value in values if _text(value).strip())
    return f"<ul>{rendered}</ul>" if rendered else ""


def _entry_title(entry: Mapping[str, Any]) -> str:
    return _text(
        entry.get("title")
        or entry.get("role")
        or entry.get("degree")
        or entry.get("name")
        or entry.get("activity")
        or entry.get("organization")
        or entry.get("institution")
        or "Experience"
    )


def _entry_meta(entry: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in ("organization", "institution", "employer", "location", "period", "dates", "year"):
        value = _text(entry.get(key)).strip()
        if value and value not in parts and value != _entry_title(entry):
            parts.append(value)
    return " · ".join(parts)


def _render_cv_entry(entry: object) -> str:
    if not isinstance(entry, Mapping):
        return f'<div class="timeline-entry"><p>{_esc(entry)}</p></div>'
    title = _entry_title(entry)
    meta = _entry_meta(entry)
    description = _text(entry.get("description") or entry.get("summary") or entry.get("details")).strip()
    bullets = _as_list(entry.get("highlights") or entry.get("bullets") or entry.get("activities"))
    ignored = {
        "title", "role", "degree", "name", "activity", "organization", "institution",
        "employer", "location", "period", "dates", "year", "description", "summary",
        "details", "highlights", "bullets", "activities",
    }
    extra = [
        f"<dt>{_esc(key.replace('_', ' ').title())}</dt><dd>{_esc(value)}</dd>"
        for key, value in entry.items()
        if key not in ignored and value not in (None, "", [], {}) and not isinstance(value, (list, dict))
    ]
    heading = f'<article class="timeline-entry"><h3>{_esc(title)}</h3>'
    if meta:
        heading += f'<p class="entry-meta">{_esc(meta)}</p>'
    return heading + (
        f"<p>{_esc(description)}</p>" if description else ""
    ) + _list_items(bullets) + (
        f'<dl class="compact-details">{"".join(extra)}</dl>' if extra else ""
    ) + "</article>"


def _human_heading(key: str) -> str:
    preferred = {
        "experience": "Professional experience",
        "professional_experience": "Professional experience",
        "education": "Education",
        "memberships": "Professional memberships",
        "awards": "Awards and distinctions",
        "community": "Community and public participation",
        "community_participation": "Community and public participation",
        "federal_interactions": "Selected federal interactions",
        "life_events": "Selected life events",
        "skills": "Skills and expertise",
    }
    return preferred.get(key, key.replace("_", " ").title())


BASE_CSS = """
@page { size: A4; margin: 13mm 13mm 15mm; }
:root { --navy:#17365d; --blue:#176ca4; --red:#c7352c; --ink:#243142;
  --muted:#526477; --line:#ccd6e0; --soft:#f1f6fa; --white:#fff; }
* { box-sizing:border-box; }
html { background:#e9edf1; }
body { width:184mm; margin:0 auto; background:#fff; color:var(--ink);
  font:10pt/1.45 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body::after { content:"SYNTHETIC TEST PERSONA"; position:fixed; right:1mm; bottom:1mm;
  color:#8b1f1a; font-size:7pt; font-weight:800; letter-spacing:.05em; opacity:.78; }
main { padding:0; }
h1,h2,h3,p { margin-top:0; }
h1 { color:var(--navy); font:700 28pt/1.08 Georgia,serif; margin-bottom:2mm; }
h2 { color:var(--navy); font:700 15pt/1.2 Georgia,serif; border-bottom:1px solid var(--line);
  padding-bottom:1.5mm; margin:7mm 0 3mm; break-after:avoid; }
h3 { color:var(--navy); font-size:10.5pt; margin-bottom:.5mm; }
p { margin-bottom:2.5mm; }
ul { margin:1.5mm 0 2.5mm; padding-left:5mm; }
li + li { margin-top:.8mm; }
.synthetic-banner { background:var(--red); color:#fff; padding:2.2mm 4mm; font-weight:800;
  letter-spacing:.08em; text-align:center; text-transform:uppercase; }
.document-footer { margin-top:7mm; border-top:1px solid var(--line); padding-top:2.5mm;
  color:var(--muted); font-size:8.5pt; }
.document-footer strong { color:var(--red); }
.avoid-break,.timeline-entry,.result-card,.stat { break-inside:avoid; }
@media print { html { background:#fff; } body { width:auto; margin:0; } }
"""


CV_CSS = """
.cv-head { display:grid; grid-template-columns:38mm 1fr; gap:7mm; align-items:center;
  padding:8mm 2mm 6mm; border-bottom:4px solid var(--red); }
.portrait { width:36mm; height:36mm; object-fit:cover; border-radius:50%;
  border:1.5mm solid #e8eef4; }
.subtitle { color:var(--blue); font-size:12pt; font-weight:700; margin-bottom:1.5mm; }
.contact { color:var(--muted); margin:0; }
.summary { margin:6mm 0; padding:4mm 5mm; border-left:1.5mm solid var(--blue); background:var(--soft); }
.cv-grid { display:grid; grid-template-columns:1.75fr 1fr; gap:7mm; }
.timeline-entry { border-left:1mm solid var(--line); padding:0 0 3mm 4mm; margin-bottom:3mm; }
.entry-meta { color:var(--blue); font-weight:650; font-size:9pt; margin-bottom:1.3mm; }
.compact-details { display:grid; grid-template-columns:auto 1fr; gap:.6mm 2mm; margin:1.5mm 0; }
.compact-details dt { color:var(--muted); font-weight:700; }
.compact-details dd { margin:0; }
.sidebar section { background:#f7f9fb; padding:1mm 4mm 4mm; margin-bottom:3mm; }
"""


RESULT_CSS = """
.result-head { padding:8mm 2mm 5mm; border-bottom:4px solid var(--red); }
.eyebrow { color:var(--blue); font-weight:800; letter-spacing:.06em; text-transform:uppercase;
  font-size:8.5pt; margin-bottom:1mm; }
.lede { color:var(--muted); font-size:11pt; max-width:145mm; }
.caveat { border-left:1.5mm solid var(--red); background:#fff1ef; padding:3mm 4mm; margin:5mm 0; }
.summary-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:2.5mm; margin:5mm 0; }
.stat { border:1px solid var(--line); border-top:1.5mm solid var(--status); padding:3mm; }
.stat strong { display:block; font-size:17pt; color:var(--navy); }
.status-section { margin-top:7mm; }
.status-heading { border-left:2mm solid var(--status); padding-left:3mm; }
.status-heading h2 { border:0; margin:0; padding:0; }
.institution { color:var(--navy); font-size:11pt; margin:4mm 0 1.5mm; }
.result-card { border:1px solid var(--line); border-radius:2mm; padding:3mm 4mm; margin:0 0 2.5mm; }
.result-card h3 { margin-bottom:1mm; }
.meta { display:flex; flex-wrap:wrap; gap:1.5mm; margin:1.5mm 0; }
.pill { background:#e8eef4; border-radius:10mm; padding:.6mm 2mm; font-size:8pt; }
.rationale { color:var(--muted); margin-bottom:0; }
.category-list { color:var(--muted); font-size:8.5pt; }
.analysis { background:var(--soft); padding:4mm; margin:5mm 0; }
.inventory-gap { border-left:1.5mm solid #d99b00; background:#fff7dd; padding:3mm 4mm; }
a { color:#0b4f80; text-decoration:none; }
"""


def _document(title: str, css: str, body: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{_esc(title)}</title><style>{BASE_CSS}{css}</style></head>"
        f'<body><div class="synthetic-banner">Synthetic test persona · Not a real person</div>{body}</body></html>\n'
    )


def render_cv_html(persona: Mapping[str, Any], portrait_uri: str) -> str:
    name = _text(persona.get("display_name") or persona.get("name") or _persona_id(persona))
    subtitle = _text(persona.get("subtitle") or persona.get("headline"))
    summary = _text(persona.get("summary"))
    contact = _text(persona.get("contact_line"))
    cv = persona.get("cv") if isinstance(persona.get("cv"), Mapping) else {}

    primary_keys = [key for key in ("experience", "professional_experience", "education") if key in cv]
    sidebar_keys = [key for key in cv if key not in primary_keys]

    def section(key: str) -> str:
        values = _as_list(cv.get(key))
        content = "".join(_render_cv_entry(value) for value in values)
        return f'<section><h2>{_esc(_human_heading(key))}</h2>{content}</section>' if content else ""

    body = (
        '<main><header class="cv-head">'
        f'<img class="portrait" src="{portrait_uri}" alt="Cartoon portrait of {_esc(name)}">'
        f'<div><h1>{_esc(name)}</h1><p class="subtitle">{_esc(subtitle)}</p>'
        f'<p class="contact">{_esc(contact)}</p></div></header>'
        f'<p class="summary">{_esc(summary)}</p>'
        '<div class="cv-grid"><div>'
        + "".join(section(key) for key in primary_keys)
        + '</div><aside class="sidebar">'
        + "".join(section(key) for key in sidebar_keys)
        + "</aside></div>"
        '<footer class="document-footer"><strong>SYNTHETIC TEST PERSONA.</strong> '
        "Created solely to test the My Info survey. This is not a biography, official record, "
        "or confirmation that any institution holds personal information.</footer></main>"
    )
    return _document(f"{name} — synthetic persona CV", CV_CSS, body)


def _evaluation_record(entry: Mapping[str, Any]) -> Mapping[str, Any]:
    evaluation = entry.get("evaluation") or entry.get("survey_results") or entry.get("results")
    return evaluation if isinstance(evaluation, Mapping) else entry


def _count(summary: Mapping[str, Any], status: str, results: Sequence[Mapping[str, Any]]) -> int:
    counts = summary.get("holding_status_counts")
    if isinstance(counts, Mapping) and status in counts:
        return int(counts[status])
    return sum(1 for row in results if row.get("holding_status") == status)


def _categories(result: Mapping[str, Any]) -> list[str]:
    categories = result.get("categories_of_personal_information") or result.get("categories") or []
    labels: list[str] = []
    for item in _as_list(categories):
        if isinstance(item, Mapping):
            labels.append(_text(item.get("name") or item.get("category_id") or item.get("id")))
        else:
            labels.append(_text(item))
    return [label for label in labels if label]


def _render_result_card(result: Mapping[str, Any]) -> str:
    title = _text(result.get("title") or result.get("bank_title") or "Untitled personal information bank")
    bank = _text(result.get("bank_number") or result.get("record_id"))
    scope = _text(result.get("scope")).replace("_", " ").title()
    band = _text(result.get("match_band")).replace("_", " ").title()
    retention = result.get("retention") if isinstance(result.get("retention"), Mapping) else {}
    rationale = _text(retention.get("rationale") or result.get("retention_rationale"))
    categories = _categories(result)
    url = _safe_url(result.get("source_url"))
    title_html = f'<a href="{_esc(url)}">{_esc(title)}</a>' if url else _esc(title)
    pills = "".join(f'<span class="pill">{_esc(value)}</span>' for value in (bank, scope, band) if value)
    category_html = (
        f'<p class="category-list"><strong>Categories:</strong> {_esc(", ".join(categories))}</p>'
        if categories else ""
    )
    return (
        f'<article class="result-card"><h3>{title_html}</h3><div class="meta">{pills}</div>'
        f'{category_html}<p class="rationale">{_esc(rationale)}</p></article>'
    )


def _analysis_html(analysis: object) -> str:
    if not isinstance(analysis, Mapping) or not analysis:
        return ""
    items: list[str] = []
    for key, value in analysis.items():
        if isinstance(value, list):
            value_html = _list_items(
                json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item, Mapping) else item
                for item in value
            )
        elif isinstance(value, Mapping):
            value_html = _list_items(
                f"{str(item_key).replace('_', ' ').title()}: {_text(item_value)}"
                for item_key, item_value in value.items()
            )
        else:
            value_html = f"<p>{_esc(value)}</p>"
        items.append(f"<h3>{_esc(str(key).replace('_', ' ').title())}</h3>{value_html}")
    return f'<section class="analysis"><h2>Test analysis</h2>{"".join(items)}</section>'


def render_results_html(
    persona: Mapping[str, Any], evaluation_entry: Mapping[str, Any], assessment_year: object
) -> str:
    name = _text(persona.get("display_name") or persona.get("name") or _persona_id(persona))
    evaluation = _evaluation_record(evaluation_entry)
    summary = evaluation.get("summary") if isinstance(evaluation.get("summary"), Mapping) else {}
    assessment = evaluation.get("assessment") if isinstance(evaluation.get("assessment"), Mapping) else {}
    results_value = evaluation.get("results")
    results = [dict(row) for row in results_value] if isinstance(results_value, list) and all(isinstance(row, Mapping) for row in results_value) else []
    results.sort(key=lambda row: (
        STATUS_ORDER.get(_text(row.get("holding_status")), 99),
        _text(row.get("institution_name")).casefold(),
        _text(row.get("title")).casefold(),
        _text(row.get("record_id")),
    ))
    total = summary.get("total_matches", len(results))
    effective_year = assessment.get("as_of_year") or assessment_year or "Not supplied"
    caveat = _text(assessment.get("caveat") or "These are candidate PIBs, not confirmation that an institution holds information about this person.")
    stats = "".join(
        f'<div class="stat" style="--status:{STATUS_COLOURS[status]}"><strong>{_count(summary, status, results)}</strong>{_esc(STATUS_LABELS[status])}</div>'
        for status in STATUS_ORDER
    )
    grouped: dict[str, dict[str, list[Mapping[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for result in results:
        grouped[_text(result.get("holding_status"), "retention_unknown")][
            _text(result.get("institution_name"), "Institution not identified")
        ].append(result)
    sections: list[str] = []
    for status in STATUS_ORDER:
        institutions = grouped.get(status, {})
        if not institutions:
            continue
        cards: list[str] = []
        for institution in sorted(institutions, key=str.casefold):
            cards.append(f'<h3 class="institution">{_esc(institution)}</h3>')
            cards.extend(_render_result_card(result) for result in institutions[institution])
        sections.append(
            f'<section class="status-section" style="--status:{STATUS_COLOURS[status]}">'
            f'<header class="status-heading"><h2>{_esc(STATUS_LABELS[status])}</h2></header>'
            f'{"".join(cards)}</section>'
        )
    gaps = assessment.get("inventory_gaps") if isinstance(assessment.get("inventory_gaps"), list) else []
    gaps_html = (
        '<section class="inventory-gap"><h2>Known inventory gaps</h2>'
        + _list_items(
            item.get("message") if isinstance(item, Mapping) else item
            for item in gaps
        )
        + "</section>"
        if gaps else ""
    )
    analysis = evaluation_entry.get("analysis") if isinstance(evaluation_entry, Mapping) else None
    if not results:
        sections.append('<p class="caveat">No candidate PIB result records were supplied for this persona.</p>')
    body = (
        '<main><header class="result-head"><p class="eyebrow">My Info survey · Beta · Synthetic test run</p>'
        f'<h1>{_esc(name)}</h1><p class="lede">Estimated personal information banks as of {_esc(effective_year)}. '
        f'{_esc(total)} candidate result(s) identified.</p></header>'
        f'<p class="caveat"><strong>Important:</strong> {_esc(caveat)}</p>'
        f'<div class="summary-grid">{stats}</div>{gaps_html}{_analysis_html(analysis)}'
        + "".join(sections)
        + '<footer class="document-footer"><strong>SYNTHETIC TEST PERSONA.</strong> '
        "Generated from a deterministic survey fixture for business-logic testing. Results estimate "
        "published Personal Information Banks and do not confirm actual holdings.</footer></main>"
    )
    return _document(f"{name} — My Info synthetic survey results", RESULT_CSS, body)


def find_browser(explicit: str | None = None) -> str | None:
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            # Preserve a snap alias such as /snap/bin/chromium. Resolving that
            # symlink to /usr/bin/snap changes argv[0] and invokes the snap CLI
            # instead of the Chromium application.
            return str(path.absolute())
        discovered = shutil.which(explicit)
        if discovered:
            return discovered
        raise RenderError(f"Requested browser executable was not found: {explicit}")
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    return None


def render_pdf(html_path: Path, pdf_path: Path, browser: str) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="my-info-pdf-") as profile:
        command = [
            browser,
            "--headless",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if completed.returncode != 0 or not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
        diagnostic = (completed.stderr or completed.stdout or "no browser diagnostic").strip()
        raise RenderError(
            f"Chromium failed to render {html_path.name} (exit {completed.returncode}): {diagnostic}"
        )


def render_all(
    personas_path: Path,
    evaluations_path: Path,
    portrait_dir: Path,
    output_dir: Path,
    *,
    persona_ids: set[str] | None = None,
    html_only: bool = False,
    browser_name: str | None = None,
) -> list[Path]:
    persona_payload = _load_json(personas_path, "personas")
    evaluation_payload = _load_json(evaluations_path, "evaluation")
    personas = _records(persona_payload, "personas", "personas")
    evaluations = _records(evaluation_payload, "personas", "evaluation personas")
    by_id = {_persona_id(item): item for item in evaluations}
    selected = [item for item in personas if persona_ids is None or _persona_id(item) in persona_ids]
    missing_requested = (persona_ids or set()) - {_persona_id(item) for item in selected}
    if missing_requested:
        raise RenderError(f"Unknown persona_id(s): {', '.join(sorted(missing_requested))}")
    if not selected:
        raise RenderError("No personas selected for rendering")
    missing_evaluations = [_persona_id(item) for item in selected if _persona_id(item) not in by_id]
    if missing_evaluations:
        raise RenderError(f"Missing evaluation data for: {', '.join(missing_evaluations)}")

    browser = None if html_only else find_browser(browser_name)
    if not html_only and not browser:
        raise RenderError(
            "No Chromium-family browser found. Install Chromium, pass --browser PATH, "
            "or use --html-only to generate reviewable HTML intermediates."
        )

    assessment_year = persona_payload.get("assessment_year") if isinstance(persona_payload, Mapping) else None
    outputs: list[Path] = []
    for persona in selected:
        identifier = _persona_id(persona)
        portrait_uri = _portrait_data_uri(portrait_dir / f"{identifier}.png")
        destination = output_dir / identifier
        destination.mkdir(parents=True, exist_ok=True)
        cv_html = destination / f"{identifier}-cv.html"
        results_html = destination / f"{identifier}-survey-results.html"
        cv_pdf = destination / f"{identifier}-cv.pdf"
        results_pdf = destination / f"{identifier}-survey-results.pdf"
        cv_html.write_text(render_cv_html(persona, portrait_uri), encoding="utf-8", newline="\n")
        results_html.write_text(
            render_results_html(persona, by_id[identifier], assessment_year),
            encoding="utf-8",
            newline="\n",
        )
        outputs.extend((cv_html, results_html))
        if browser:
            render_pdf(cv_html, cv_pdf, browser)
            render_pdf(results_html, results_pdf, browser)
            outputs.extend((cv_pdf, results_pdf))
    return outputs


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--personas", type=Path, default=DEFAULT_PERSONAS)
    parser.add_argument("--evaluations", type=Path, default=DEFAULT_EVALUATIONS)
    parser.add_argument("--portrait-dir", type=Path, default=DEFAULT_PORTRAITS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--persona-id", action="append", dest="persona_ids")
    parser.add_argument("--html-only", action="store_true", help="Retain HTML without invoking a browser")
    parser.add_argument("--browser", help="Chromium-family executable name or path")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        outputs = render_all(
            args.personas.resolve(),
            args.evaluations.resolve(),
            args.portrait_dir.resolve(),
            args.output_dir.resolve(),
            persona_ids=set(args.persona_ids) if args.persona_ids else None,
            html_only=args.html_only,
            browser_name=args.browser,
        )
    except (RenderError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
