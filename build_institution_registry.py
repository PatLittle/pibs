#!/usr/bin/env python3
"""Build the authoritative bilingual registry of institutions in Schedule I.

The Access to Information Act XML is the authority for membership. Treasury
Board and Open Government sources only enrich those legal rows; they never add
or remove a Schedule I institution.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from functools import lru_cache
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


ACT_XML_URL = "https://laws-lois.justice.gc.ca/eng/XML/A-1.xml"
DUE_DATES_EN_URL = (
    "https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/"
    "access-information/access-informatio-policies-guidance/"
    "programs-holdings-online-publishing-requirements.html"
)
DUE_DATES_FR_URL = (
    "https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-"
    "protection-renseignements-personnels/acces-information/politiques-directives-"
    "acces-information/exigences-publication-ligne-programmes-fonds.html"
)
CENTRAL_LIST_EN_URL = (
    "https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/"
    "access-information/info-source/list-institutions.html"
)
CENTRAL_LIST_FR_URL = (
    "https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-"
    "protection-reseignements-personnels/acces-information/info-source/liste-organisations.html"
)
ORGANIZATION_LIST_URL = (
    "https://open.canada.ca/data/api/action/organization_list?all_fields=true&include_extras=true"
)
DATASTORE_URL = "https://open.canada.ca/data/en/api/3/action/datastore_search"
ORG_INFO_RESOURCE_ID = "cb5b5566-f599-4d12-abae-8279a0230928"
ORG_NAMES_RESOURCE_ID = "3faaafb4-00e2-4303-947d-ac786b62559f"

RAW_ROOT = Path("data/raw/institution-registry")
OVERRIDES_PATH = Path("data/institution_registry_overrides.csv")
OUT_CSV = Path("institution_registry.csv")
OUT_XLSX = Path("institution_registry.xlsx")
SITE_OUT_CSV = Path("site/data/institution_registry.csv")

HEADERS = {
    "User-Agent": "PIBs institution registry (+https://github.com/PatLittle/pibs)"
}

SOURCE_SPECS = {
    "access_to_information_act.xml": (ACT_XML_URL, None),
    "tbs_due_dates_en.html": (DUE_DATES_EN_URL, None),
    "tbs_due_dates_fr.html": (DUE_DATES_FR_URL, None),
    "tbs_central_list_en.html": (CENTRAL_LIST_EN_URL, None),
    "tbs_central_list_fr.html": (CENTRAL_LIST_FR_URL, None),
    "open_canada_organization_list.json": (ORGANIZATION_LIST_URL, None),
    "open_canada_org_info.json": (
        DATASTORE_URL,
        {"resource_id": ORG_INFO_RESOURCE_ID, "limit": 500},
    ),
    "open_canada_org_names.json": (
        DATASTORE_URL,
        {"resource_id": ORG_NAMES_RESOURCE_ID, "limit": 500},
    ),
}

STOP_WORDS = {
    "the", "of", "and", "for", "to", "du", "de", "des", "la", "le",
    "les", "et", "d", "l", "inc", "incorporated", "limited", "ltd",
}


def clean_space(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\xa0", " ")).strip()


@lru_cache(maxsize=100_000)
def normalize_name(value: object) -> str:
    text = unidecode(clean_space(value)).casefold().replace("&", " and ")
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(word for word in text.split() if word not in STOP_WORDS)


@lru_cache(maxsize=250_000)
def name_score(left: object, right: object) -> float:
    a = normalize_name(left)
    b = normalize_name(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    token_score = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
    sequence_score = SequenceMatcher(None, a, b).ratio()
    return max(token_score, sequence_score)


def slugify(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", unidecode(value).casefold())).strip("-")


@dataclass
class FetchRecord:
    filename: str
    url: str
    status_code: int
    content_type: str
    fetched_at_utc: str
    sha256: str
    byte_count: int


def fetch_sources(snapshot_date: str, refresh: bool) -> tuple[Path, dict[str, bytes]]:
    raw_dir = RAW_ROOT / snapshot_date
    raw_dir.mkdir(parents=True, exist_ok=True)
    payloads: dict[str, bytes] = {}
    manifest: list[dict[str, object]] = []
    manifest_path = raw_dir / "manifest.json"
    previous_manifest: dict[str, dict[str, object]] = {}
    if manifest_path.exists():
        try:
            previous_manifest = {
                str(item["filename"]): item
                for item in json.loads(manifest_path.read_text(encoding="utf-8"))
            }
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            previous_manifest = {}

    for filename, (url, params) in SOURCE_SPECS.items():
        target = raw_dir / filename
        if target.exists() and not refresh:
            content = target.read_bytes()
            previous = previous_manifest.get(filename, {})
            status_code = int(previous.get("status_code", 200))
            content_type = str(previous.get("content_type", "application/octet-stream"))
            if content_type == "application/octet-stream":
                content_type = {
                    ".xml": "application/xml",
                    ".html": "text/html",
                    ".json": "application/json",
                }.get(target.suffix.casefold(), content_type)
            fetched_at = str(
                previous.get(
                    "fetched_at_utc",
                    datetime.fromtimestamp(target.stat().st_mtime, timezone.utc).isoformat(),
                )
            )
        else:
            response = requests.get(url, params=params, headers=HEADERS, timeout=(15, 90))
            response.raise_for_status()
            content = response.content
            target.write_bytes(content)
            status_code = response.status_code
            content_type = response.headers.get("content-type", "")
            fetched_at = datetime.now(timezone.utc).isoformat()
        payloads[filename] = content
        manifest.append(
            FetchRecord(
                filename=filename,
                url=url,
                status_code=status_code,
                content_type=content_type,
                fetched_at_utc=fetched_at,
                sha256=hashlib.sha256(content).hexdigest(),
                byte_count=len(content),
            ).__dict__
        )

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return raw_dir, payloads


def parse_schedule_i(xml: bytes) -> pd.DataFrame:
    soup = BeautifulSoup(xml, "xml")
    schedule = next(
        (
            item
            for item in soup.find_all("Schedule")
            if clean_space((item.find("Label") or {}).get_text(" ", strip=True) if item.find("Label") else "")
            == "SCHEDULE I"
        ),
        None,
    )
    if schedule is None:
        raise RuntimeError("Schedule I was not found in the Access to Information Act XML")

    rows: list[dict[str, object]] = []
    order = 0
    for group in schedule.find_all("BilingualGroup", recursive=False):
        heading = group.find("TitleText")
        if heading is None:
            continue
        names_en = group.find_all("BilingualItemEn", recursive=False)
        names_fr = group.find_all("BilingualItemFr", recursive=False)
        if len(names_en) != len(names_fr):
            raise RuntimeError(f"Unbalanced Schedule I bilingual group: {clean_space(heading.get_text())}")
        for en, fr in zip(names_en, names_fr):
            order += 1
            name_en = clean_space(en.get_text(" ", strip=True))
            name_fr = clean_space(fr.get_text(" ", strip=True))
            rows.append(
                {
                    "institution_id": f"ati-schedule-i-{slugify(name_en)}",
                    "access_act_schedule": "I",
                    "access_act_group": clean_space(heading.get_text(" ", strip=True)),
                    "access_act_order": order,
                    "legal_name_en": name_en,
                    "legal_name_fr": name_fr,
                    "access_act_source_url": ACT_XML_URL,
                }
            )

    frame = pd.DataFrame(rows)
    if len(frame) != 148:
        raise RuntimeError(f"Expected 148 Schedule I institutions; parsed {len(frame)}")
    return frame


def parse_due_dates(html: bytes, lang: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    dates = {
        "1": "03-31",
        "2": "06-30",
        "3": "09-30",
        "4": "12-31",
    }
    rows: list[dict[str, str]] = []
    for heading in soup.find_all("h3"):
        title = clean_space(heading.get_text(" ", strip=True))
        match = re.match(r"A\.([1-4])\b", title)
        if not match:
            continue
        sibling = heading.find_next_sibling()
        while sibling is not None and sibling.name not in {"h2", "h3"}:
            if sibling.name == "ul":
                for item in sibling.find_all("li", recursive=False):
                    rows.append(
                        {
                            "name": clean_space(item.get_text(" ", strip=True)),
                            "annual_due_date": dates[match.group(1)],
                            "appendix_section": f"A.{match.group(1)}",
                            "lang": lang,
                        }
                    )
            sibling = sibling.find_next_sibling()
    if len(rows) != 196:
        raise RuntimeError(f"Expected 196 {lang.upper()} TBS due-date entries; parsed {len(rows)}")
    return pd.DataFrame(rows)


def parse_central_list(html: bytes, page_url: str, lang: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", class_="mwstext")
    if content is None:
        raise RuntimeError(f"Could not locate the TBS central-list content container ({lang})")
    rows: list[dict[str, str]] = []
    for section in content.find_all("section", recursive=False):
        for item in section.find_all("li"):
            link = item.find("a", href=True)
            name = clean_space((link or item).get_text(" ", strip=True))
            href = clean_space(link.get("href")) if link else ""
            if not name:
                continue
            if name.casefold() in {"top of page", "haut de la page", "english", "français", "francais"}:
                continue
            if re.search(r"\b(see|voir)\b", name.casefold()):
                continue
            url = urljoin(page_url, href) if href and not href.startswith("#") else ""
            if url in {CENTRAL_LIST_EN_URL, CENTRAL_LIST_FR_URL}:
                url = ""
            rows.append({"name": name, "url": url or pd.NA, "lang": lang})
    return pd.DataFrame(rows).drop_duplicates(subset=["name", "url"]).reset_index(drop=True)


def datastore_records(payload: bytes) -> list[dict[str, object]]:
    parsed = json.loads(payload)
    if not parsed.get("success"):
        raise RuntimeError("Open Government datastore returned success=false")
    return parsed["result"]["records"]


def combine_open_government(payloads: dict[str, bytes]) -> pd.DataFrame:
    info = pd.DataFrame(datastore_records(payloads["open_canada_org_info.json"]))
    names = pd.DataFrame(datastore_records(payloads["open_canada_org_names.json"]))
    for frame in (info, names):
        frame["gc_orgID"] = pd.to_numeric(frame["gc_orgID"], errors="coerce").astype("Int64")
    info = info.drop_duplicates("gc_orgID")
    names = names.drop_duplicates("gc_orgID")
    duplicate_columns = [column for column in names if column in info and column not in {"gc_orgID", "_id"}]
    names = names.drop(columns=duplicate_columns + (["_id"] if "_id" in names else []))
    return info.merge(names, on="gc_orgID", how="outer")


def organization_list_frame(payload: bytes) -> pd.DataFrame:
    parsed = json.loads(payload)
    if not parsed.get("success"):
        raise RuntimeError("Open Government organization_list returned success=false")
    rows = []
    for item in parsed["result"]:
        title = item.get("title_translated") or {}
        short = item.get("shortform") or {}
        rows.append(
            {
                "open_canada_org_id": item.get("id", ""),
                "open_canada_org_slug": item.get("name", ""),
                "open_canada_title_en": clean_space(title.get("en") or short.get("en")),
                "open_canada_title_fr": clean_space(title.get("fr") or short.get("fr")),
                "open_canada_state": item.get("state", ""),
                "open_canada_approval_status": item.get("approval_status", ""),
                "open_canada_department_number": item.get("department_number", ""),
                "open_canada_umd_number": item.get("umd_number", ""),
                "open_canada_ati_email": item.get("ati_email", ""),
                "open_canada_registry_access": item.get("registry_access", ""),
            }
        )
    return pd.DataFrame(rows)


def load_overrides() -> dict[str, dict[str, str]]:
    if not OVERRIDES_PATH.exists():
        return {}
    with OVERRIDES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        return {row["legal_name_en"]: row for row in csv.DictReader(handle)}


OPEN_GOV_ALIAS_FIELDS = [
    "legal_title", "appellation_legale", "harmonized_name", "nom_harmonise",
    "preferred_name", "nom_prefere", "ati", "abbreviation", "abreviation",
]


def aliases_for(row: pd.Series, open_gov_row: pd.Series | None = None) -> list[str]:
    aliases = [row["legal_name_en"], row["legal_name_fr"]]
    if open_gov_row is not None:
        aliases.extend(clean_space(open_gov_row.get(field)) for field in OPEN_GOV_ALIAS_FIELDS)
    return [item for item in dict.fromkeys(aliases) if item]


def exact_candidates(aliases: Iterable[str], candidates: pd.DataFrame, fields: list[str]) -> list[int]:
    keys = {normalize_name(alias) for alias in aliases if normalize_name(alias)}
    matches = []
    for index, candidate in candidates.iterrows():
        candidate_keys = {normalize_name(candidate.get(field)) for field in fields if clean_space(candidate.get(field))}
        if keys & candidate_keys:
            matches.append(index)
    return matches


def best_candidate(
    aliases: Iterable[str], candidates: pd.DataFrame, name_field: str, minimum: float = 0.84
) -> tuple[int | None, str, float]:
    alias_list = list(aliases)
    exact = exact_candidates(alias_list, candidates, [name_field])
    if len(exact) == 1:
        return exact[0], "exact", 1.0
    scored = sorted(
        (
            (max(name_score(alias, candidate[name_field]) for alias in alias_list), index)
            for index, candidate in candidates.iterrows()
        ),
        reverse=True,
    )
    if not scored:
        return None, "unmatched", 0.0
    score, index = scored[0]
    runner_up = scored[1][0] if len(scored) > 1 else 0.0
    if score >= minimum and score - runner_up >= 0.025:
        return index, "fuzzy", round(score, 4)
    return None, "unmatched", round(score, 4)


def resolve_open_government(registry: pd.DataFrame, open_gov: pd.DataFrame) -> pd.DataFrame:
    fields = OPEN_GOV_ALIAS_FIELDS
    ids: list[object] = []
    methods: list[str] = []
    scores: list[object] = []
    for _, row in registry.iterrows():
        aliases = aliases_for(row)
        exact = exact_candidates(aliases, open_gov, fields)
        if len(exact) == 1:
            index = exact[0]
            ids.append(open_gov.at[index, "gc_orgID"])
            methods.append("exact")
            scores.append(1.0)
            continue
        scored = []
        for index, candidate in open_gov.iterrows():
            candidate_aliases = [clean_space(candidate.get(field)) for field in fields]
            score = max(
                name_score(alias, candidate_alias)
                for alias in aliases
                for candidate_alias in candidate_aliases
                if candidate_alias
            )
            scored.append((score, index))
        scored.sort(reverse=True)
        best, index = scored[0]
        runner_up = scored[1][0]
        if best >= 0.88 and best - runner_up >= 0.035:
            ids.append(open_gov.at[index, "gc_orgID"])
            methods.append("fuzzy")
            scores.append(round(best, 4))
        else:
            ids.append(pd.NA)
            methods.append("unmatched")
            scores.append(round(best, 4))
    out = registry.copy()
    out["gc_orgID"] = pd.Series(ids, dtype="Int64")
    out["open_gov_match_method"] = methods
    out["open_gov_match_score"] = scores
    return out


def match_enrichment(
    registry: pd.DataFrame,
    open_gov: pd.DataFrame,
    candidates: pd.DataFrame,
    candidate_name: str,
    prefix: str,
    value_fields: list[str],
    overrides: dict[str, dict[str, str]],
    override_name_field: str = "",
    minimum: float = 0.84,
) -> pd.DataFrame:
    out = registry.copy()
    values = {field: [] for field in value_fields}
    methods: list[str] = []
    scores: list[object] = []

    open_by_id = open_gov.set_index("gc_orgID", drop=False)
    for _, row in out.iterrows():
        open_row = None
        if pd.notna(row.get("gc_orgID")) and int(row["gc_orgID"]) in open_by_id.index:
            open_row = open_by_id.loc[int(row["gc_orgID"])]
        aliases = aliases_for(row, open_row)
        override = overrides.get(row["legal_name_en"], {})
        override_name = clean_space(override.get(override_name_field)) if override_name_field else ""
        if override_name:
            aliases.insert(0, override_name)
        index, method, score = best_candidate(aliases, candidates, candidate_name, minimum=minimum)
        if index is None:
            for field in value_fields:
                values[field].append(pd.NA)
        else:
            for field in value_fields:
                values[field].append(candidates.at[index, field])
        methods.append("override_" + method if override_name and index is not None else method)
        scores.append(score)

    for field, items in values.items():
        out[f"{prefix}_{field}"] = items
    out[f"{prefix}_match_method"] = methods
    out[f"{prefix}_match_score"] = scores
    return out


def build_registry(payloads: dict[str, bytes]) -> pd.DataFrame:
    registry = parse_schedule_i(payloads["access_to_information_act.xml"])
    open_gov = combine_open_government(payloads)
    registry = resolve_open_government(registry, open_gov)
    open_columns = [
        "gc_orgID", "harmonized_name", "nom_harmonise", "preferred_name", "nom_prefere",
        "lead_department", "ministere_responsable", "FAA_LGFP",
        "abbreviation", "abreviation", "status_statut", "end_date_fin", "website", "site_web",
        "open_gov_ouvert", "infobaseID", "rg", "ati", "pop", "phoenix",
    ]
    registry = registry.merge(open_gov[open_columns], on="gc_orgID", how="left")

    org_list = organization_list_frame(payloads["open_canada_organization_list.json"])
    org_by_slug = org_list.set_index("open_canada_org_slug", drop=False)
    org_columns = [
        "open_canada_org_id", "open_canada_org_slug", "open_canada_title_en",
        "open_canada_title_fr", "open_canada_state", "open_canada_approval_status",
        "open_canada_department_number", "open_canada_umd_number", "open_canada_ati_email",
        "open_canada_registry_access",
    ]
    org_rows = []
    for _, row in registry.iterrows():
        slug = clean_space(row.get("open_gov_ouvert"))
        if slug and slug in org_by_slug.index:
            matched = org_by_slug.loc[slug]
            if isinstance(matched, pd.DataFrame):
                matched = matched.iloc[0]
            values = {column: matched.get(column, pd.NA) for column in org_columns}
            values.update({"organization_list_match_method": "open_gov_slug", "organization_list_match_score": 1.0})
        else:
            aliases = aliases_for(row)
            candidates = []
            for index, candidate in org_list.iterrows():
                score = max(
                    name_score(alias, candidate[field])
                    for alias in aliases
                    for field in ["open_canada_title_en", "open_canada_title_fr"]
                )
                candidates.append((score, index))
            candidates.sort(reverse=True)
            best, index = candidates[0]
            runner_up = candidates[1][0]
            if best >= 0.92 and best - runner_up >= 0.03:
                matched = org_list.loc[index]
                values = {column: matched.get(column, pd.NA) for column in org_columns}
                values.update({"organization_list_match_method": "name", "organization_list_match_score": round(best, 4)})
            else:
                values = {column: pd.NA for column in org_columns}
                values.update({"organization_list_match_method": "unmatched", "organization_list_match_score": round(best, 4)})
        org_rows.append(values)
    registry = pd.concat([registry.reset_index(drop=True), pd.DataFrame(org_rows)], axis=1)

    overrides = load_overrides()
    due_en = parse_due_dates(payloads["tbs_due_dates_en.html"], "en")
    due_fr = parse_due_dates(payloads["tbs_due_dates_fr.html"], "fr")
    registry = match_enrichment(
        registry, open_gov, due_en, "name", "due_en",
        ["name", "annual_due_date", "appendix_section"], overrides, "tbs_due_name_en",
    )
    registry = match_enrichment(
        registry, open_gov, due_fr, "name", "due_fr",
        ["name", "annual_due_date", "appendix_section"], overrides, "tbs_due_name_fr",
    )

    central_en = parse_central_list(payloads["tbs_central_list_en.html"], CENTRAL_LIST_EN_URL, "en")
    central_fr = parse_central_list(payloads["tbs_central_list_fr.html"], CENTRAL_LIST_FR_URL, "fr")
    registry = match_enrichment(
        registry, open_gov, central_en, "name", "infosource_en", ["name", "url"],
        overrides, "central_list_name_en", minimum=0.93,
    )
    registry = match_enrichment(
        registry, open_gov, central_fr, "name", "infosource_fr", ["name", "url"],
        overrides, "central_list_name_fr", minimum=0.93,
    )

    # Curated values apply after source matching and remain visibly attributed.
    override_columns = [
        "reporting_entity_en", "reporting_entity_fr", "annual_due_date_override",
        "infosource_url_en_override", "infosource_url_fr_override", "pibs_url_en_override",
        "pibs_url_fr_override", "classes_url_en_override", "classes_url_fr_override",
        "url_evidence_en_override", "url_evidence_fr_override", "notes",
    ]
    for column in override_columns:
        registry[column] = registry["legal_name_en"].map(
            lambda name: clean_space(overrides.get(name, {}).get(column)) or pd.NA
        )

    registry["annual_due_date"] = registry["due_en_annual_due_date"].combine_first(
        registry["due_fr_annual_due_date"]
    )
    registry["annual_due_date"] = registry["annual_due_date_override"].combine_first(
        registry["annual_due_date"]
    )
    registry["due_date_match_status"] = "not_listed_in_tbs_appendix"
    direct = registry["due_en_annual_due_date"].notna() | registry["due_fr_annual_due_date"].notna()
    registry.loc[direct, "due_date_match_status"] = "direct"
    inherited = registry["annual_due_date_override"].notna()
    registry.loc[inherited, "due_date_match_status"] = "reporting_entity_override"
    mismatch = (
        registry["due_en_annual_due_date"].notna()
        & registry["due_fr_annual_due_date"].notna()
        & (registry["due_en_annual_due_date"] != registry["due_fr_annual_due_date"])
    )
    if mismatch.any():
        names = registry.loc[mismatch, "legal_name_en"].tolist()
        raise RuntimeError(f"English/French due-date disagreement: {names}")

    registry["infosource_url_en"] = registry["infosource_url_en_override"].combine_first(
        registry["infosource_en_url"]
    )
    registry["infosource_url_fr"] = registry["infosource_url_fr_override"].combine_first(
        registry["infosource_fr_url"]
    )
    for lang in ("en", "fr"):
        registry[f"pibs_url_{lang}"] = registry[f"pibs_url_{lang}_override"].combine_first(
            registry[f"infosource_url_{lang}"]
        )
        registry[f"classes_of_records_url_{lang}"] = registry[f"classes_url_{lang}_override"].combine_first(
            registry[f"infosource_url_{lang}"]
        )

    registry["tbs_due_dates_source_en"] = DUE_DATES_EN_URL + "#toc-a"
    registry["tbs_due_dates_source_fr"] = DUE_DATES_FR_URL + "#toc-a"
    registry["tbs_central_list_source_en"] = CENTRAL_LIST_EN_URL
    registry["tbs_central_list_source_fr"] = CENTRAL_LIST_FR_URL
    registry["infosource_url_evidence_en"] = registry["url_evidence_en_override"]
    registry["infosource_url_evidence_fr"] = registry["url_evidence_fr_override"]
    registry.loc[
        registry["infosource_url_en"].notna() & registry["infosource_url_evidence_en"].isna(),
        "infosource_url_evidence_en",
    ] = CENTRAL_LIST_EN_URL
    registry.loc[
        registry["infosource_url_fr"].notna() & registry["infosource_url_evidence_fr"].isna(),
        "infosource_url_evidence_fr",
    ] = CENTRAL_LIST_FR_URL
    registry["organization_list_source"] = ORGANIZATION_LIST_URL
    registry["org_info_source"] = (
        f"{DATASTORE_URL}?resource_id={ORG_INFO_RESOURCE_ID}&limit=500"
    )
    registry["org_names_source"] = (
        f"{DATASTORE_URL}?resource_id={ORG_NAMES_RESOURCE_ID}&limit=500"
    )
    registry["registry_as_of_date"] = datetime.now(timezone.utc).date().isoformat()
    return registry.sort_values("access_act_order").reset_index(drop=True)


def write_outputs(registry: pd.DataFrame) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    SITE_OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(OUT_CSV, index=False)
    registry.to_csv(SITE_OUT_CSV, index=False)
    registry.to_excel(OUT_XLSX, index=False, engine="openpyxl")


def print_summary(registry: pd.DataFrame, raw_dir: Path) -> None:
    print(f"Raw snapshot: {raw_dir}")
    print(f"Schedule I institutions: {len(registry)}")
    print(f"Matched gcOrgID: {registry['gc_orgID'].notna().sum()}")
    print(f"Matched annual due date: {registry['annual_due_date'].notna().sum()}")
    print(f"Info Source EN URLs: {registry['infosource_url_en'].notna().sum()}")
    print(f"Info Source FR URLs: {registry['infosource_url_fr'].notna().sum()}")
    print(f"Saved: {OUT_CSV}, {OUT_XLSX}, {SITE_OUT_CSV}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--refresh", action="store_true", help="Re-fetch a snapshot that already exists")
    args = parser.parse_args()
    raw_dir, payloads = fetch_sources(args.snapshot_date, args.refresh)
    registry = build_registry(payloads)
    write_outputs(registry)
    print_summary(registry, raw_dir)


if __name__ == "__main__":
    main()
