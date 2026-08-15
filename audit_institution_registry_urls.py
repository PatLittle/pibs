#!/usr/bin/env python3
"""Validate registry URLs and identify split PIB/Class-of-Records pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


INPUT_CSV = Path("institution_registry.csv")
OUTPUT_XLSX = Path("institution_registry.xlsx")
SITE_OUTPUT_CSV = Path("site/data/institution_registry.csv")
AUDIT_ROOT = Path("data/audits")
HEADERS = {"User-Agent": "PIBs institution URL audit (+https://github.com/PatLittle/pibs)"}

INFO_SOURCE_MARKERS = [
    "info source",
    "sources of federal government and employee information",
    "sources de renseignements du gouvernement federal",
    "information about programs and information holdings",
    "renseignements sur les programmes et les fonds de renseignements",
]
PIB_DETAIL_MARKERS = [
    "bank number", "numero de fichier", "personal information bank",
    "fichier de renseignements personnels",
]
CLASS_DETAIL_MARKERS = [
    "record number", "numero du dossier", "class of records", "classe de documents",
    "categorie de documents",
]
REJECTION_MARKERS = ["request rejected", "access denied", "error 403", "service unavailable"]


def clean_space(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\xa0", " ")).strip()


def ascii_text(value: object) -> str:
    return unidecode(clean_space(value)).casefold()


@dataclass
class UrlResult:
    requested_url: str
    final_url: str = ""
    status_code: int | None = None
    content_type: str = ""
    byte_count: int = 0
    sha256: str = ""
    title: str = ""
    page_language: str = ""
    validation: str = "request_error"
    error: str = ""
    has_pib_details: bool = False
    has_class_details: bool = False
    alternate_urls: dict[str, str] = field(default_factory=dict)
    pib_candidates: list[dict[str, object]] = field(default_factory=list)
    class_candidates: list[dict[str, object]] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return self.__dict__


def candidate_score(text: str, url: str, kind: str) -> int:
    value = ascii_text(text)
    normalized_url = ascii_text(url)
    score = 0
    if kind == "pib":
        if "institution-specific personal information bank" in value or "fichiers de renseignements personnels specifiques" in value:
            score += 10
        elif "personal information banks" in value or "fichiers de renseignements personnels" in value:
            score += 6
        elif value in {"pib", "pibs", "frp"}:
            score += 2
        if "standard" in value or "ordinaire" in value:
            score -= 5
    else:
        if "institution-specific class" in value or "categories de documents specifiques" in value:
            score += 10
        elif "classes of records" in value or "categories de documents" in value:
            score += 6
        if "standard" in value or "ordinaire" in value:
            score -= 5
    # Institution reports routinely link to Treasury Board's standard banks
    # and classes. Those are reference material, not institution-specific
    # holdings pages.
    if any(marker in normalized_url for marker in (
        "standard-personal-information-banks",
        "fichiers-renseignements-personnels-ordinaires",
        "standard-classes-of-records",
        "standard-classes-records",
        "categories-documents-ordinaires",
    )):
        score -= 20
    return score


def analyze_html(result: UrlResult, content: bytes) -> None:
    soup = BeautifulSoup(content, "lxml")
    title_node = soup.find("title") or soup.find("h1")
    result.title = clean_space(title_node.get_text(" ", strip=True) if title_node else "")
    html = soup.find("html")
    result.page_language = clean_space(html.get("lang", "") if html else "").casefold().split("-", 1)[0]
    searchable = ascii_text(soup.get_text(" ", strip=True))
    if any(marker in searchable[:5000] for marker in REJECTION_MARKERS):
        result.validation = "request_rejected"
        return
    marker_count = sum(marker in searchable for marker in INFO_SOURCE_MARKERS)
    result.has_pib_details = "bank number" in searchable or "numero de fichier" in searchable
    result.has_class_details = "record number" in searchable or "numero du dossier" in searchable
    result.validation = "verified_info_source" if marker_count else "reachable_unverified_content"

    for link in soup.find_all("link", href=True):
        rel = link.get("rel", [])
        rel = [rel] if isinstance(rel, str) else rel
        lang = clean_space(link.get("hreflang", "")).casefold().split("-", 1)[0]
        if "alternate" in {clean_space(item).casefold() for item in rel} and lang in {"en", "fr"}:
            result.alternate_urls[lang] = urljoin(result.final_url, link["href"])

    for anchor in soup.find_all("a", href=True):
        href = clean_space(anchor.get("href"))
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        text = clean_space(anchor.get_text(" ", strip=True))
        url = urljoin(result.final_url, href)
        for kind, target in (("pib", result.pib_candidates), ("class", result.class_candidates)):
            score = candidate_score(text, url, kind)
            if score >= 6:
                target.append({"url": url, "text": text, "score": score})
    result.pib_candidates.sort(key=lambda item: (-int(item["score"]), str(item["url"])))
    result.class_candidates.sort(key=lambda item: (-int(item["score"]), str(item["url"])))


def fetch_url(url: str) -> UrlResult:
    result = UrlResult(requested_url=url)
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=(12, 50))
        result.final_url = response.url
        result.status_code = response.status_code
        result.content_type = response.headers.get("content-type", "").split(";", 1)[0].casefold()
        result.byte_count = len(response.content)
        result.sha256 = hashlib.sha256(response.content).hexdigest()
        if not response.ok:
            result.validation = "http_error"
            return result
        if "html" in result.content_type or response.content.lstrip().casefold().startswith((b"<!doctype html", b"<html")):
            analyze_html(result, response.content)
        elif result.content_type == "application/pdf" or response.content.startswith(b"%PDF"):
            result.validation = "reachable_pdf"
            result.has_pib_details = True
            result.has_class_details = True
        elif "officedocument" in result.content_type or "msword" in result.content_type:
            result.validation = "reachable_document"
            result.has_pib_details = True
            result.has_class_details = True
        else:
            result.validation = "reachable_unverified_format"
    except requests.RequestException as exc:
        result.error = f"{type(exc).__name__}: {exc}"
    return result


def fetch_many(urls: list[str], workers: int) -> dict[str, UrlResult]:
    cache: dict[str, UrlResult] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_url, url): url for url in urls}
        for number, future in enumerate(as_completed(futures), 1):
            url = futures[future]
            try:
                cache[url] = future.result()
            except Exception as exc:  # defensive around worker failures
                cache[url] = UrlResult(requested_url=url, error=f"{type(exc).__name__}: {exc}")
            if number % 25 == 0 or number == len(urls):
                print(f"Fetched {number}/{len(urls)} URLs")
    return cache


def choose_deep_url(result: UrlResult, kind: str, fetched: dict[str, UrlResult]) -> str:
    candidates = result.pib_candidates if kind == "pib" else result.class_candidates
    for candidate in candidates:
        candidate_result = fetched.get(str(candidate["url"]))
        if candidate_result and candidate_result.validation in {
            "verified_info_source", "reachable_pdf", "reachable_document"
        }:
            return candidate_result.final_url or candidate_result.requested_url
    has_details = result.has_pib_details if kind == "pib" else result.has_class_details
    if has_details or result.validation in {"reachable_pdf", "reachable_document"}:
        return result.final_url or result.requested_url
    # A verified landing page remains the best available link when it describes
    # holdings but does not expose machine-detectable detail labels.
    if result.validation == "verified_info_source":
        return result.final_url or result.requested_url
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--as-of-date", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()

    frame = pd.read_csv(INPUT_CSV)
    initial_urls = sorted(
        {
            clean_space(value)
            for lang in ("en", "fr")
            for value in frame[f"infosource_url_{lang}"].dropna()
            if clean_space(value)
        }
    )
    fetched = fetch_many(initial_urls, args.workers)

    # Follow strong split-page candidates and alternate-language declarations.
    followups = set()
    for result in fetched.values():
        followups.update(result.alternate_urls.values())
        followups.update(str(item["url"]) for item in result.pib_candidates[:3])
        followups.update(str(item["url"]) for item in result.class_candidates[:3])
    followups.difference_update(fetched)
    if followups:
        fetched.update(fetch_many(sorted(followups), args.workers))

    audit_rows = []
    for index, row in frame.iterrows():
        row_audit: dict[str, object] = {
            "institution_id": row["institution_id"],
            "legal_name_en": row["legal_name_en"],
        }
        for lang, other in (("en", "fr"), ("fr", "en")):
            supplied = clean_space(row.get(f"infosource_url_{lang}"))
            result = fetched.get(supplied) if supplied else None
            if result is None and not supplied:
                other_url = clean_space(row.get(f"infosource_url_{other}"))
                other_result = fetched.get(other_url)
                alternate = other_result.alternate_urls.get(lang, "") if other_result else ""
                alternate_result = fetched.get(alternate)
                if alternate_result and alternate_result.validation in {
                    "verified_info_source", "reachable_pdf", "reachable_document"
                }:
                    supplied = alternate
                    result = alternate_result
                    frame.at[index, f"infosource_url_{lang}"] = alternate
                    frame.at[index, f"infosource_url_evidence_{lang}"] = f"alternate hreflang from {other_url}"

            if result is None:
                frame.at[index, f"infosource_validation_{lang}"] = "missing_url"
                frame.at[index, f"infosource_http_status_{lang}"] = pd.NA
                frame.at[index, f"infosource_final_url_{lang}"] = pd.NA
                row_audit[lang] = {"validation": "missing_url"}
                continue

            frame.at[index, f"infosource_validation_{lang}"] = result.validation
            frame.at[index, f"infosource_http_status_{lang}"] = result.status_code
            frame.at[index, f"infosource_final_url_{lang}"] = result.final_url or pd.NA
            pib_url = choose_deep_url(result, "pib", fetched)
            class_url = choose_deep_url(result, "class", fetched)
            if pib_url:
                frame.at[index, f"pibs_url_{lang}"] = pib_url
            if class_url:
                frame.at[index, f"classes_of_records_url_{lang}"] = class_url
            row_audit[lang] = result.as_dict()
        audit_rows.append(row_audit)

    for lang in ("en", "fr"):
        frame[f"infosource_http_status_{lang}"] = pd.to_numeric(
            frame[f"infosource_http_status_{lang}"], errors="coerce"
        ).astype("Int64")
    frame.to_csv(INPUT_CSV, index=False)
    frame.to_csv(SITE_OUTPUT_CSV, index=False)
    frame.to_excel(OUTPUT_XLSX, index=False, engine="openpyxl")

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    output = AUDIT_ROOT / f"institution_registry_url_audit_{args.as_of_date}.json"
    accepted = {"verified_info_source", "reachable_pdf", "reachable_document"}

    def split_page_count(lang: str) -> int:
        deep = frame[f"pibs_url_{lang}"].fillna("").astype(str).str.rstrip("/")
        final = frame[f"infosource_final_url_{lang}"].fillna("").astype(str).str.rstrip("/")
        valid = frame[f"infosource_validation_{lang}"].isin(accepted)
        return int((valid & deep.ne("") & final.ne("") & deep.ne(final)).sum())

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(INPUT_CSV),
        "summary": {
            "institutions": len(frame),
            "unique_seed_urls": len(initial_urls),
            "unique_followup_urls": len(followups),
            "english_urls": int(frame["infosource_url_en"].notna().sum()),
            "french_urls": int(frame["infosource_url_fr"].notna().sum()),
            "english_verified_or_document": int(frame["infosource_validation_en"].isin(accepted).sum()),
            "french_verified_or_document": int(frame["infosource_validation_fr"].isin(accepted).sum()),
            "english_split_pib_pages": split_page_count("en"),
            "french_split_pib_pages": split_page_count("fr"),
        },
        "institutions": audit_rows,
        "fetched_urls": {url: result.as_dict() for url, result in sorted(fetched.items())},
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Saved audit: {output}")


if __name__ == "__main__":
    main()
