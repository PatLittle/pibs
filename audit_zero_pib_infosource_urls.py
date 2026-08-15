#!/usr/bin/env python3
"""Audit zero-PIB institution URLs and recover/build usable bilingual corpora."""

import csv
import hashlib
import io
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markitdown import MarkItDown

from build_infosource_markdown_corpus import slugify, write_format_md
from build_pib_table_from_markdown import process_folder


INPUT_CSV = Path("infosource_institutions_en_fr.csv")
OUTPUT_JSON = Path("infosource_zero_pib_url_report.json")
CORPUS_ROOT = Path("institutions_infosource_docs")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PIBS-Zero-PIB-URL-Audit/1.0; "
        "+https://github.com/PatLittle/pibs)"
    )
}
INFO_SOURCE_TERMS = [
    "info source",
    "sources of federal government and employee information",
    "sources de renseignements sur le gouvernement et les employes federaux",
    "personal information bank",
    "personal information banks",
    "fichier de renseignements personnels",
    "fichiers de renseignements personnels",
    "bank number",
    "numero de fichier",
]
LANGUAGE_TEXT = {
    "en": {"english", "anglais"},
    "fr": {"francais", "french"},
}


def clean_space(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\xa0", " ")).strip()


def has_zero_or_empty_pib_count(value: object) -> bool:
    text = clean_space(value)
    if not text:
        return True
    try:
        return float(text) == 0
    except ValueError:
        return False


def ascii_text(value: object) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", clean_space(value)).encode("ascii", "ignore").decode("ascii")
    return text.casefold()


@dataclass
class FetchResult:
    report: Dict[str, object]
    content: bytes = b""
    markdown: str = ""

    @property
    def valid(self) -> bool:
        return bool(self.report.get("candidate_is_infosource"))

    @property
    def final_url(self) -> str:
        return clean_space(self.report.get("final_url"))


def response_markdown(response: requests.Response) -> str:
    try:
        result = MarkItDown().convert_response(response)
        return result.markdown or ""
    except Exception:
        return ""


def analyze_response(original_url: str, response: requests.Response) -> FetchResult:
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    content = response.content
    title = ""
    page_language = ""
    evidence: List[str] = []
    markdown = ""

    if "html" in content_type or content.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        soup = BeautifulSoup(content, "lxml")
        title_element = soup.find("title") or soup.find("h1")
        title = clean_space(title_element.get_text(" ", strip=True) if title_element else "")
        html = soup.find("html")
        page_language = clean_space(html.get("lang", "") if html else "").lower().split("-", 1)[0]
        searchable = ascii_text(soup.get_text(" ", strip=True))
    elif content_type == "application/pdf" or content.startswith(b"%PDF"):
        markdown = response_markdown(response)
        first_line = next((clean_space(line.lstrip("# ")) for line in markdown.splitlines() if clean_space(line)), "")
        title = first_line[:300]
        searchable = ascii_text(markdown)
    else:
        searchable = ascii_text(content[:2_000_000].decode(response.encoding or "utf-8", errors="replace"))
        title = searchable[:300]

    url_text = ascii_text(response.url.replace("-", " ").replace("_", " ").replace("/", " "))
    title_text = ascii_text(title)
    score = 0
    if "info source" in url_text or "infosource" in url_text:
        score += 1
        evidence.append("Info Source marker in final URL")
    if "info source" in title_text or "sources of federal government" in title_text or "sources de renseignements" in title_text:
        score += 2
        evidence.append("Info Source marker in page title")
    matched_terms = sorted({term for term in INFO_SOURCE_TERMS if ascii_text(term) in searchable})
    if matched_terms:
        score += 2
        evidence.append("Content markers: " + ", ".join(matched_terms))
    if any(term in searchable for term in ["bank number", "numero de fichier"]):
        score += 1
    supported_type = "html" in content_type or content_type == "application/pdf" or content.startswith(b"%PDF")
    valid = response.ok and supported_type and score >= 2

    chain = []
    for item in response.history:
        chain.append(
            {
                "url": item.url,
                "status_code": item.status_code,
                "location": item.headers.get("location", ""),
            }
        )
    chain.append({"url": response.url, "status_code": response.status_code, "location": ""})

    report = {
        "original_url": original_url,
        "status_code": response.status_code,
        "final_url": response.url,
        "redirected": bool(response.history) or response.url.rstrip("/") != original_url.rstrip("/"),
        "redirect_chain": chain,
        "content_type": content_type,
        "content_length": len(content),
        "content_sha256": hashlib.sha256(content).hexdigest(),
        "page_title": title,
        "page_language": page_language,
        "candidate_score": score,
        "candidate_is_infosource": valid,
        "evidence": evidence,
        "error": "",
    }
    return FetchResult(report=report, content=content, markdown=markdown)


def fetch_url(url: str) -> FetchResult:
    original_url = clean_space(url)
    if not original_url:
        return FetchResult(
            report={
                "original_url": "",
                "status_code": None,
                "final_url": "",
                "redirected": False,
                "redirect_chain": [],
                "content_type": "",
                "content_length": 0,
                "content_sha256": "",
                "page_title": "",
                "page_language": "",
                "candidate_score": 0,
                "candidate_is_infosource": False,
                "evidence": [],
                "error": "missing URL",
            }
        )
    try:
        response = requests.get(original_url, headers=HEADERS, allow_redirects=True, timeout=(12, 45))
        return analyze_response(original_url, response)
    except requests.RequestException as exc:
        return FetchResult(
            report={
                "original_url": original_url,
                "status_code": None,
                "final_url": "",
                "redirected": False,
                "redirect_chain": [],
                "content_type": "",
                "content_length": 0,
                "content_sha256": "",
                "page_title": "",
                "page_language": "",
                "candidate_score": 0,
                "candidate_is_infosource": False,
                "evidence": [],
                "error": f"{type(exc).__name__}: {exc}",
            }
        )


def language_candidates(result: FetchResult, target_language: str) -> List[Dict[str, str]]:
    if not result.content or "html" not in clean_space(result.report.get("content_type")):
        return []
    soup = BeautifulSoup(result.content, "lxml")
    candidates: List[Dict[str, str]] = []

    for link in soup.find_all("link", href=True):
        rel = link.get("rel", [])
        rel = [rel] if isinstance(rel, str) else rel
        hreflang = clean_space(link.get("hreflang", "")).lower().split("-", 1)[0]
        if "alternate" in {str(value).lower() for value in rel} and hreflang == target_language:
            candidates.append(
                {
                    "url": urljoin(result.final_url, link["href"]),
                    "source": "alternate hreflang link",
                }
            )

    for anchor in soup.find_all("a", href=True):
        href = clean_space(anchor.get("href", ""))
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        anchor_lang = clean_space(anchor.get("lang", anchor.get("hreflang", ""))).lower().split("-", 1)[0]
        text = ascii_text(anchor.get_text(" ", strip=True))
        parsed_path = urlparse(urljoin(result.final_url, href)).path.lower()
        is_toggle = anchor_lang == target_language or text in LANGUAGE_TEXT[target_language]
        if not is_toggle and not re.search(rf"/(?:{target_language})(?:/|$)", parsed_path):
            continue
        candidates.append(
            {
                "url": urljoin(result.final_url, href),
                "source": "on-page language toggle",
            }
        )

    unique: List[Dict[str, str]] = []
    seen = set()
    for candidate in candidates:
        url = candidate["url"]
        if url not in seen and url != result.final_url:
            seen.add(url)
            unique.append(candidate)
    return unique[:5]


def find_corpus_folder(row: Dict[str, str]) -> Path:
    orgid = clean_space(row.get("gc_orgID"))
    if orgid:
        matches = sorted(CORPUS_ROOT.glob(f"{orgid}_*"))
        if matches:
            return matches[0]
    name = clean_space(row.get("institution_name_en")) or clean_space(row.get("institution_name_fr"))
    slug = slugify(name)
    if not orgid:
        matches = sorted(CORPUS_ROOT.glob(f"na_{slug}*"))
        if matches:
            return matches[0]
    return CORPUS_ROOT / f"{orgid or 'na'}_{slug}"


def metadata_final_urls(folder: Path) -> Dict[str, str]:
    path = folder / "metadata.txt"
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            values[key.strip()] = value.strip()
    return values


def write_corpus(
    folder: Path,
    row: Dict[str, str],
    results: Dict[str, FetchResult],
) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    for language in ["en", "fr"]:
        result = results[language]
        content_type = clean_space(result.report.get("content_type"))
        extension = ".pdf" if content_type == "application/pdf" or result.content.startswith(b"%PDF") else ".html"
        source_path = folder / f"infosource_{language}{extension}"
        source_path.write_bytes(result.content)
        markdown = result.markdown
        if not markdown:
            try:
                markdown = converter.convert_local(source_path).markdown or ""
            except Exception:
                markdown = ""
        (folder / f"infosource_{language}.md").write_text(markdown, encoding="utf-8")

    name_en = clean_space(row.get("institution_name_en")) or clean_space(row.get("harmonized_name"))
    name_fr = clean_space(row.get("institution_name_fr")) or clean_space(row.get("nom_harmonise"))
    write_format_md(folder, name_en, name_fr)
    metadata = [
        f"institution_name_en: {name_en}",
        f"institution_name_fr: {name_fr}",
        f"gc_orgID: {clean_space(row.get('gc_orgID')) or 'na'}",
        f"infosource_url_en: {results['en'].final_url}",
        f"infosource_url_fr: {results['fr'].final_url}",
        f"audit_timestamp_utc: {datetime.now(timezone.utc).isoformat()}",
    ]
    (folder / "metadata.txt").write_text("\n".join(metadata) + "\n", encoding="utf-8")


def audit_rows(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, object]], Dict[str, int]]:
    audit_rows = [row for row in rows if has_zero_or_empty_pib_count(row.get("pib_count"))]
    initial_urls = sorted(
        {
            clean_space(row.get(f"infosource_url_{language}"))
            for row in audit_rows
            for language in ["en", "fr"]
            if clean_space(row.get(f"infosource_url_{language}"))
        }
    )
    fetched: Dict[str, FetchResult] = {}
    print(f"Auditing {len(audit_rows)} institution rows and {len(initial_urls)} supplied URLs...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in initial_urls}
        for index, future in enumerate(as_completed(future_to_url), start=1):
            url = future_to_url[future]
            fetched[url] = future.result()
            if index % 10 == 0 or index == len(initial_urls):
                print(f"Fetched {index}/{len(initial_urls)} supplied URLs", flush=True)

    reports: List[Dict[str, object]] = []
    summary = {
        "rows_audited": len(audit_rows),
        "valid_bilingual_candidates": 0,
        "language_urls_recovered": 0,
        "corpora_built_or_refreshed": 0,
        "corpora_already_present": 0,
        "pib_tables_built": 0,
    }

    for index, row in enumerate(audit_rows, start=1):
        effective: Dict[str, FetchResult] = {}
        supplied: Dict[str, FetchResult] = {}
        recovery_attempts: Dict[str, List[Dict[str, object]]] = {"en": [], "fr": []}
        for language in ["en", "fr"]:
            url = clean_space(row.get(f"infosource_url_{language}"))
            result = fetched.get(url) if url else fetch_url("")
            supplied[language] = result
            effective[language] = result

        for language, other_language in [("en", "fr"), ("fr", "en")]:
            if effective[language].valid or not effective[other_language].valid:
                continue
            for candidate in language_candidates(effective[other_language], language):
                result = fetched.get(candidate["url"])
                if result is None:
                    result = fetch_url(candidate["url"])
                    fetched[candidate["url"]] = result
                attempt = {**candidate, "result": result.report}
                recovery_attempts[language].append(attempt)
                if result.valid:
                    effective[language] = result
                    summary["language_urls_recovered"] += 1
                    break

        folder = find_corpus_folder(row)
        corpus_action = "not_bilingual_valid"
        processing = {"status": "not_run", "en_records": 0, "fr_records": 0, "merged_records": 0}
        if effective["en"].valid and effective["fr"].valid:
            summary["valid_bilingual_candidates"] += 1
            existing_complete = all((folder / f"infosource_{language}.md").exists() for language in ["en", "fr"])
            prior_urls = metadata_final_urls(folder)
            final_urls_changed = any(
                prior_urls.get(f"infosource_url_{language}", "").rstrip("/")
                != effective[language].final_url.rstrip("/")
                for language in ["en", "fr"]
            )
            recovered = any(recovery_attempts[language] for language in ["en", "fr"])
            redirected = any(bool(effective[language].report.get("redirected")) for language in ["en", "fr"])
            if not existing_complete or final_urls_changed or recovered or redirected:
                try:
                    write_corpus(folder, row, effective)
                    corpus_action = "built" if not existing_complete else "refreshed"
                    summary["corpora_built_or_refreshed"] += 1
                    status, en_count, fr_count, merged_count = process_folder(folder)
                    processing = {
                        "status": status,
                        "en_records": en_count,
                        "fr_records": fr_count,
                        "merged_records": merged_count,
                    }
                    if status == "processed":
                        summary["pib_tables_built"] += 1
                except Exception as exc:
                    corpus_action = "error"
                    processing["error"] = f"{type(exc).__name__}: {exc}"
            else:
                corpus_action = "already_present"
                summary["corpora_already_present"] += 1

        reports.append(
            {
                "gc_orgID": clean_space(row.get("gc_orgID")),
                "institution_name_en": clean_space(row.get("institution_name_en")),
                "institution_name_fr": clean_space(row.get("institution_name_fr")),
                "pib_count": clean_space(row.get("pib_count")),
                "status_statut": clean_space(row.get("status_statut")),
                "languages": {
                    language: {
                        "supplied": supplied[language].report,
                        "recovery_attempts": recovery_attempts[language],
                        "effective": effective[language].report,
                    }
                    for language in ["en", "fr"]
                },
                "corpus_folder": str(folder),
                "corpus_action": corpus_action,
                "processing": processing,
            }
        )
        if index % 10 == 0 or index == len(audit_rows):
            print(f"Evaluated {index}/{len(audit_rows)} institution rows", flush=True)
    return reports, summary


def main() -> None:
    with INPUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    reports, summary = audit_rows(rows)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_csv": str(INPUT_CSV),
        "selection": "pib_count is zero or empty",
        "validity_rule": "HTTP success, supported HTML/PDF content, and Info Source or PIB evidence score >= 2",
        "summary": summary,
        "institutions": reports,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote audit report to {OUTPUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
