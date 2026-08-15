#!/usr/bin/env python3
"""Build the legacy operational Info Source institution directory.

Use ``build_institution_registry.py`` for the authoritative Access to
Information Act Schedule I registry. This broader directory remains useful for
publication collection because it includes organizations outside Schedule I.
"""

import difflib
import io
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qsl, urljoin, urlparse, urlunparse, urlencode

import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from institution_pib_counts import load_pib_counts

URL_EN = (
    "https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/"
    "access-information/info-source/list-institutions.html"
)
URL_FR = (
    "https://www.canada.ca/fr/secretariat-conseil-tresor/services/acces-information-"
    "protection-reseignements-personnels/acces-information/info-source/liste-organisations.html"
)
CKAN_DATASTORE_API = "https://open.canada.ca/data/api/3/action/datastore_search"
CKAN_RESOURCE_ID = "3faaafb4-00e2-4303-947d-ac786b62559f"
ORG_INFO_URL = (
    "https://open.canada.ca/data/dataset/57180b36-3428-4a7f-afe3-2161a6b44ec5/"
    "resource/cb5b5566-f599-4d12-abae-8279a0230928/download/gc_org_info.csv"
)

OUT_CSV = "infosource_institutions_en_fr.csv"
OUT_XLSX = "infosource_institutions_en_fr.xlsx"
SITE_OUT_CSV = "site/data/infosource_institutions_en_fr.csv"
COMBINED_PIB_CSV = Path("institutions_infosource_docs/pib_table_en_fr_all.csv")
BASELINE_CAPTURE_DATE = "2026-03-11"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InfoSource-Institutions-Scraper/1.0; +https://example.local)"
}

# Curated EN<->FR institution equivalents for rows that remain unmatched after gcOrgID and alternate-link matching.
MANUAL_PAIR_RULES = [
    {"id": "nfb", "en_name": "national film board of canada", "fr_name": "office national du film du canada"},
    {
        "id": "oci",
        "en_name": "office correctional investigator",
        "fr_name": "bureau lenqueteur correctionnel",
        "fr_url": "infosource2018-1",
    },
    {
        "id": "erc",
        "en_name": "royal canadian mounted police external review committee",
        "fr_name": "comite externe examen gendarmerie royale canada",
    },
    {"id": "cer", "en_name": "canada energy regulator", "fr_name": "office national lenergie"},
    {"id": "parks", "en_name": "parks canada agency", "fr_name": "agence parcs canada"},
    {
        "id": "sdtc",
        "en_name": "sustainable development technology canada",
        "fr_name": "technologies developpement durable canada",
    },
    {
        "id": "cnsopb",
        "en_name": "canada nova scotia offshore petroleum board",
        "fr_name": "office canada nouvelle ecosse hydrocarbures extracotiers",
    },
    {
        "id": "hopa",
        "en_name": "oshawa port authority",
        "fr_name": "administration portuaire hamilton",
        "en_url": "hopaports",
    },
    {
        "id": "history_war_museum",
        "en_name": "canadian museum history canadian war museum",
        "fr_name": "musee canadien histoire musee canadien guerre",
    },
    {
        "id": "nsira",
        "en_name": "national security intelligence review agency",
        "fr_name": "comite surveillance activites renseignement securite",
    },
    {"id": "nac", "en_name": "national arts centre", "fr_name": "centre national arts"},
    {
        "id": "ingenium",
        "en_name": "ingenium canadas museums science innovation",
        "fr_name": "ingenium musees sciences innovation canada",
    },
    {"id": "dcc", "en_name": "defence construction canada", "fr_name": "construction defense canada"},
    {
        "id": "bc_treaty",
        "en_name": "british columbia treaty commission",
        "fr_name": "commission traites colombie britannique",
    },
    {"id": "cdev_eldor", "en_name": "canada eldor inc", "fr_name": "canada eldor inc"},
    {
        "id": "cdev_hibernia",
        "en_name": "canada hibernia holding corporation",
        "fr_name": "societe gestion canada hibernia",
    },
    {"id": "canada_post", "en_name": "canada post", "fr_name": "postes canada"},
    {
        "id": "crown_indigenous",
        "en_name": "crown indigenous northern affairs canada",
        "fr_name": "relations couronne autochtones affaires nord canada",
    },
    {
        "id": "fraidg",
        "en_name": "fund railway accidents involving designated goods",
        "fr_name": "caisse indemnisation accidents ferroviaires impliquant marchandises designees",
    },
    {"id": "gwichin_lwb", "en_name": "gwichin land water board", "fr_name": "office gwichin terres eaux"},
    {"id": "infrastructure", "en_name": "infrastructure canada", "fr_name": "infrastructure canada"},
    {"id": "nunavut_water", "en_name": "nunavut water board", "fr_name": "office eaux nunavut"},
    {
        "id": "ombudsman_dnd",
        "en_name": "office ombudsman national defence canadian forces",
        "fr_name": "bureau ombudsman ministere defense nationale forces canadiennes",
    },
    {"id": "port_vancouver", "en_name": "port vancouver", "fr_name": "port vancouver"},
    {"id": "sahtu_lwb", "en_name": "sahtu land water board", "fr_name": "office terres eaux sahtu"},
    {
        "id": "seaway_bridge",
        "en_name": "seaway international bridge corporation limited",
        "fr_name": "corporation pont international voie maritime limitee",
    },
    {"id": "wage", "en_name": "women gender equality", "fr_name": "femmes legalite genres"},
    {
        "id": "yesab",
        "en_name": "yukon environmental socio economic assessment board",
        "fr_name": "office evaluation environnementale socioeconomique yukon",
    },
]


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def normalize_name(name: str) -> str:
    s = unidecode(clean_space(name)).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[’']", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(the|of|and|for|to|du|de|des|la|le|les|et|d|l)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def make_url_key(url: str) -> Optional[str]:
    if not isinstance(url, str) or not url.strip():
        return None
    p = urlparse(url.strip())
    if p.scheme not in {"http", "https"}:
        return None

    host = p.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    segments = [seg for seg in p.path.split("/") if seg]
    filtered = [seg for seg in segments if seg.lower() not in {"en", "fr", "eng", "fra"}]
    path = "/" + "/".join(filtered)
    path = re.sub(r"/+", "/", path).rstrip("/")

    qs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in {"lang", "language"}]
    query = urlencode(sorted(qs))

    normalized = urlunparse(("https", host, path, "", query, ""))
    return normalized


def fetch_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def scrape_institutions(page_url: str, lang: str) -> pd.DataFrame:
    soup = fetch_soup(page_url)
    content = soup.find("div", class_="mwstext")
    if content is None:
        raise RuntimeError(f"Could not find main content container on {page_url}")

    skip_text = {"top of page", "haut de la page", "english", "francais", "français"}
    rows: List[Dict[str, object]] = []
    for section in content.find_all("section", recursive=False):
        for a in section.find_all("a", href=True):
            name = clean_space(a.get_text(" ", strip=True))
            href = clean_space(a.get("href", ""))
            if not name or not href:
                continue
            if href.startswith("#"):
                continue
            if name.lower() in skip_text:
                continue
            if re.search(r"\b(see|voir)\b", name.lower()):
                continue

            url = clean_space(urljoin(page_url, href))
            if url in {URL_EN, URL_FR}:
                continue
            if not url.lower().startswith(("http://", "https://")):
                continue

            rows.append(
                {
                    "lang": lang,
                    "institution_name": name,
                    "infosource_url": url,
                    "url_key": make_url_key(url),
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.drop_duplicates(subset=["institution_name", "infosource_url"]).reset_index(drop=True)
    df["name_norm"] = df["institution_name"].apply(normalize_name)
    return df


def fetch_ckan_records() -> pd.DataFrame:
    records: List[Dict[str, object]] = []
    offset = 0
    limit = 1000
    while True:
        r = requests.get(
            CKAN_DATASTORE_API,
            headers=HEADERS,
            params={"resource_id": CKAN_RESOURCE_ID, "limit": limit, "offset": offset},
            timeout=60,
        )
        r.raise_for_status()
        payload = r.json()
        if not payload.get("success"):
            raise RuntimeError("CKAN datastore_search returned success=false")
        chunk = payload["result"]["records"]
        records.extend(chunk)
        if len(chunk) < limit:
            break
        offset += limit
    df = pd.DataFrame(records)
    df["gc_orgID"] = pd.to_numeric(df["gc_orgID"], errors="coerce").astype("Int64")
    return df


def fetch_org_statuses() -> Dict[int, str]:
    response = requests.get(ORG_INFO_URL, headers=HEADERS, timeout=60)
    response.raise_for_status()
    status_df = pd.read_csv(io.BytesIO(response.content), encoding="utf-8-sig")
    required = {"gc_orgID", "status_statut"}
    if not required.issubset(status_df.columns):
        raise RuntimeError(f"Organization Information CSV is missing columns: {required - set(status_df.columns)}")
    status_df["gc_orgID"] = pd.to_numeric(status_df["gc_orgID"], errors="coerce").astype("Int64")
    status_df = status_df.dropna(subset=["gc_orgID"]).drop_duplicates(subset=["gc_orgID"], keep="first")
    statuses = {}
    for _, row in status_df.iterrows():
        if pd.isna(row["gc_orgID"]):
            continue
        status = row.get("status_statut", "")
        statuses[int(row["gc_orgID"])] = "" if pd.isna(status) else clean_space(str(status)).lower()
    return statuses


def build_name_indexes(
    ckan_df: pd.DataFrame,
) -> Tuple[Dict[str, set], Dict[str, set], Dict[str, set], Dict[str, set]]:
    en_exact: Dict[str, set] = {}
    fr_exact: Dict[str, set] = {}
    en_fuzzy: Dict[str, set] = {}
    fr_fuzzy: Dict[str, set] = {}

    def add(target: Dict[str, set], key: str, gc_orgid: int):
        if not key:
            return
        target.setdefault(key, set()).add(int(gc_orgid))

    for _, row in ckan_df.iterrows():
        gc_orgid = row.get("gc_orgID")
        if pd.isna(gc_orgid):
            continue
        gc_orgid = int(gc_orgid)

        for field in ["harmonized_name", "ati", "abbreviation"]:
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                n = normalize_name(value)
                add(en_exact, n, gc_orgid)
                if field in {"harmonized_name", "ati"}:
                    add(en_fuzzy, n, gc_orgid)

        for field in ["nom_harmonise", "abreviation"]:
            value = row.get(field)
            if isinstance(value, str) and value.strip():
                n = normalize_name(value)
                add(fr_exact, n, gc_orgid)
                if field == "nom_harmonise":
                    add(fr_fuzzy, n, gc_orgid)

    return en_exact, fr_exact, en_fuzzy, fr_fuzzy


def fuzzy_match_id(name_norm: str, fuzzy_index: Dict[str, set], cutoff: float = 0.9) -> Tuple[Optional[int], Optional[float]]:
    if not name_norm or not fuzzy_index:
        return None, None
    scored = []
    for candidate in fuzzy_index.keys():
        score = difflib.SequenceMatcher(None, name_norm, candidate).ratio()
        scored.append((score, candidate))
    scored.sort(reverse=True, key=lambda x: x[0])
    best_score, best_name = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    if best_score < cutoff or (best_score - second_score) < 0.03:
        return None, None
    ids = fuzzy_index.get(best_name, set())
    if len(ids) == 1:
        return list(ids)[0], best_score
    return None, None


def resolve_gc_orgids(df: pd.DataFrame, lang: str, exact_index: Dict[str, set], fuzzy_index: Dict[str, set]) -> pd.DataFrame:
    out = df.copy()
    gc_ids: List[Optional[int]] = []
    methods: List[Optional[str]] = []
    scores: List[Optional[float]] = []

    for _, row in out.iterrows():
        key = row["name_norm"]
        ids = exact_index.get(key, set())
        if len(ids) == 1:
            gc_ids.append(list(ids)[0])
            methods.append("exact")
            scores.append(None)
            continue
        if len(ids) > 1:
            gc_ids.append(None)
            methods.append("ambiguous_exact")
            scores.append(None)
            continue

        fuzzy_id, fuzzy_score = fuzzy_match_id(key, fuzzy_index, cutoff=0.9)
        if fuzzy_id is not None:
            gc_ids.append(fuzzy_id)
            methods.append("fuzzy")
            scores.append(round(float(fuzzy_score), 4))
        else:
            gc_ids.append(None)
            methods.append("unmatched")
            scores.append(None)

    out[f"gc_orgID_{lang}"] = pd.Series(gc_ids, dtype="Int64")
    out[f"match_method_{lang}"] = methods
    out[f"match_score_{lang}"] = scores
    return out


def apply_historical_gc_orgids(
    df: pd.DataFrame,
    lang: str,
    previous: pd.DataFrame,
) -> pd.DataFrame:
    if previous.empty:
        return df

    name_column = f"institution_name_{lang}"
    if name_column not in previous.columns or "gc_orgID" not in previous.columns:
        return df

    historical_ids: Dict[str, set] = {}
    for _, row in previous.iterrows():
        gc_orgid = row.get("gc_orgID")
        name = row.get(name_column)
        if pd.isna(gc_orgid) or not isinstance(name, str) or not name.strip():
            continue
        historical_ids.setdefault(normalize_name(name), set()).add(int(gc_orgid))

    out = df.copy()
    gc_column = f"gc_orgID_{lang}"
    method_column = f"match_method_{lang}"
    score_column = f"match_score_{lang}"
    applied = 0
    for idx, row in out[out[gc_column].isna()].iterrows():
        ids = historical_ids.get(row["name_norm"], set())
        if len(ids) != 1:
            continue
        out.at[idx, gc_column] = next(iter(ids))
        out.at[idx, method_column] = "historical_exact"
        out.at[idx, score_column] = None
        applied += 1

    out[gc_column] = out[gc_column].astype("Int64")
    print(f"Historical exact-name gcOrgID matches ({lang.upper()}): {applied}")
    return out


def fetch_alternate_hreflang_links(url: str) -> Dict[str, str]:
    if not isinstance(url, str) or not url.strip():
        return {}
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=20)
        r.raise_for_status()
    except requests.RequestException:
        return {}

    soup = BeautifulSoup(r.text, "lxml")
    out: Dict[str, str] = {}
    for link in soup.find_all("link", href=True):
        rel = link.get("rel", [])
        if isinstance(rel, str):
            rel = [rel]
        rel_norm = {x.lower() for x in rel}
        if "alternate" not in rel_norm:
            continue
        hreflang = clean_space(link.get("hreflang", "")).lower()
        if not hreflang:
            continue
        lang = hreflang.split("-")[0]
        if lang not in {"en", "fr"}:
            continue
        out[lang] = clean_space(urljoin(r.url, link["href"]))
    return out


def apply_alternate_url_pairing(df_en: pd.DataFrame, df_fr: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    en = df_en.copy()
    fr = df_fr.copy()
    en["alternate_row_key"] = pd.NA
    fr["alternate_row_key"] = pd.NA
    en["alternate_target_url"] = pd.NA
    fr["alternate_target_url"] = pd.NA

    en_keys = set(en["url_key"].dropna().astype(str).tolist())
    fr_keys = set(fr["url_key"].dropna().astype(str).tolist())
    alt_cache: Dict[str, Dict[str, str]] = {}

    def get_alt(url: str) -> Dict[str, str]:
        if url not in alt_cache:
            alt_cache[url] = fetch_alternate_hreflang_links(url)
        return alt_cache[url]

    en_alt_matches = 0
    for idx, row in en[en["gc_orgID_en"].isna()].iterrows():
        alt_links = get_alt(row["infosource_url"])
        alt_fr = alt_links.get("fr")
        alt_fr_key = make_url_key(alt_fr) if alt_fr else None
        if alt_fr_key and alt_fr_key in fr_keys:
            en.at[idx, "alternate_row_key"] = f"url:{alt_fr_key}"
            en.at[idx, "alternate_target_url"] = alt_fr
            en_alt_matches += 1

    fr_alt_matches = 0
    for idx, row in fr[fr["gc_orgID_fr"].isna()].iterrows():
        alt_links = get_alt(row["infosource_url"])
        alt_en = alt_links.get("en")
        alt_en_key = make_url_key(alt_en) if alt_en else None
        if alt_en_key and alt_en_key in en_keys:
            fr.at[idx, "alternate_row_key"] = f"url:{alt_en_key}"
            fr.at[idx, "alternate_target_url"] = alt_en
            fr_alt_matches += 1

    print(f"Alternate-link URL matches (EN unmatched -> FR list): {en_alt_matches}")
    print(f"Alternate-link URL matches (FR unmatched -> EN list): {fr_alt_matches}")
    return en, fr


def apply_manual_name_pairing(df_en: pd.DataFrame, df_fr: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    en = df_en.copy()
    fr = df_fr.copy()
    en["manual_row_key"] = pd.NA
    fr["manual_row_key"] = pd.NA

    used_en = set()
    used_fr = set()
    manual_matches = 0

    def candidate_indexes(
        df: pd.DataFrame,
        lang: str,
        name_pattern: str,
        url_pattern: Optional[str],
        used: set,
    ) -> List[int]:
        if not name_pattern:
            return []
        name_pattern_norm = normalize_name(name_pattern)
        if not name_pattern_norm:
            return []
        mask = df["name_norm"].astype(str).str.contains(name_pattern_norm, regex=False, na=False)
        if url_pattern:
            mask = mask & df["infosource_url"].astype(str).str.lower().str.contains(url_pattern.lower(), regex=False, na=False)
        mask = mask & df["manual_row_key"].isna()
        idxs = [i for i in df.index[mask].tolist() if i not in used]
        # Prioritize rows still missing a gcOrgID in this language.
        gc_col = f"gc_orgID_{lang}"
        idxs.sort(key=lambda i: (pd.notna(df.at[i, gc_col]), i))
        return idxs

    for rule in MANUAL_PAIR_RULES:
        en_idxs = candidate_indexes(en, "en", rule.get("en_name", ""), rule.get("en_url"), used_en)
        fr_idxs = candidate_indexes(fr, "fr", rule.get("fr_name", ""), rule.get("fr_url"), used_fr)
        if not en_idxs or not fr_idxs:
            continue

        en_idx = en_idxs[0]
        fr_idx = fr_idxs[0]

        if pd.notna(en.at[en_idx, "gc_orgID_en"]):
            key = f"gc:{int(en.at[en_idx, 'gc_orgID_en'])}"
        elif pd.notna(fr.at[fr_idx, "gc_orgID_fr"]):
            key = f"gc:{int(fr.at[fr_idx, 'gc_orgID_fr'])}"
        else:
            key = f"manual:{rule['id']}"

        en.at[en_idx, "manual_row_key"] = key
        fr.at[fr_idx, "manual_row_key"] = key
        used_en.add(en_idx)
        used_fr.add(fr_idx)
        manual_matches += 1

    print(f"Manual bilingual name matches applied: {manual_matches}")
    return en, fr


def coalesce_gc_orgid(gc_en: pd.Series, gc_fr: pd.Series) -> Tuple[pd.Series, pd.Series]:
    gc_orgid = []
    conflict = []
    for en_val, fr_val in zip(gc_en, gc_fr):
        en_ok = pd.notna(en_val)
        fr_ok = pd.notna(fr_val)
        if en_ok and fr_ok:
            if int(en_val) == int(fr_val):
                gc_orgid.append(int(en_val))
                conflict.append(False)
            else:
                gc_orgid.append(pd.NA)
                conflict.append(True)
        elif en_ok:
            gc_orgid.append(int(en_val))
            conflict.append(False)
        elif fr_ok:
            gc_orgid.append(int(fr_val))
            conflict.append(False)
        else:
            gc_orgid.append(pd.NA)
            conflict.append(False)
    return pd.Series(gc_orgid, dtype="Int64"), pd.Series(conflict, dtype="boolean")


def probe_status_code(url: str) -> Tuple[Optional[int], Optional[str]]:
    if not isinstance(url, str) or not url.strip():
        return None, "empty URL"
    try:
        r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
        if r.status_code in {400, 401, 403, 405, 406, 429, 500, 501, 503}:
            r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15, stream=True)
        return int(r.status_code), None
    except requests.RequestException as exc:
        return None, str(exc)


def probe_urls_parallel_and_stream(
    merged: pd.DataFrame,
    urls: List[str],
    csv_path: str,
    max_workers: int = 24,
) -> Dict[str, Optional[int]]:
    status_cache: Dict[str, Optional[int]] = {}
    total = len(urls)
    if total == 0:
        return status_cache

    print(f"Testing {total} Info Source URL(s) in parallel (workers={max_workers})...")
    bar_width = 32
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(probe_status_code, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                code, err = future.result()
            except Exception as exc:  # defensive; probe_status_code handles request exceptions
                code, err = None, str(exc)

            completed += 1
            status_cache[url] = code

            # Stream partial results into the output CSV as each URL completes.
            merged.loc[merged["infosource_url_en"] == url, "infosource_status_en"] = code
            merged.loc[merged["infosource_url_fr"] == url, "infosource_status_fr"] = code
            merged.to_csv(csv_path, index=False)

            filled = int((completed / total) * bar_width)
            bar = "#" * filled + "." * (bar_width - filled)
            print(f"\rURL checks: [{bar}] {completed}/{total}", end="", flush=True)

            if code != 200:
                if code is None:
                    print(f"\n[{completed}/{total}] ERROR {url} -> {err}", flush=True)
                else:
                    print(f"\n[{completed}/{total}] HTTP {code} {url}", flush=True)

    print("")
    return status_cache


def history_key(row: pd.Series) -> str:
    gc_orgid = row.get("gc_orgID")
    if pd.notna(gc_orgid):
        return f"gc:{int(gc_orgid)}"
    row_key = row.get("row_key")
    if isinstance(row_key, str) and row_key.strip():
        return row_key.strip()
    raise RuntimeError("Institution row is missing both gc_orgID and row_key")


def merge_institution_history(
    current: pd.DataFrame,
    previous: pd.DataFrame,
    as_of_date: str,
) -> Tuple[pd.DataFrame, int, int]:
    current = current.copy()
    current["_history_key"] = current.apply(history_key, axis=1)
    if current["_history_key"].duplicated().any():
        duplicates = current.loc[current["_history_key"].duplicated(False), "_history_key"].tolist()
        raise RuntimeError(f"Duplicate current institution history keys: {duplicates}")

    if previous.empty:
        current["date_captured"] = as_of_date
        current["date_removed"] = pd.NA
        return current.drop(columns=["_history_key"]), len(current), 0

    previous = previous.copy()
    if "date_captured" not in previous.columns:
        previous["date_captured"] = BASELINE_CAPTURE_DATE
    else:
        previous["date_captured"] = previous["date_captured"].fillna(BASELINE_CAPTURE_DATE)
    if "date_removed" not in previous.columns:
        previous["date_removed"] = pd.NA

    previous["_history_key"] = previous.apply(history_key, axis=1)
    if previous["_history_key"].duplicated().any():
        duplicates = previous.loc[previous["_history_key"].duplicated(False), "_history_key"].tolist()
        raise RuntimeError(f"Duplicate previous institution history keys: {duplicates}")

    previous_by_key = previous.set_index("_history_key")
    previous_keys = set(previous_by_key.index)

    historical_name_keys: Dict[str, set] = {}
    for _, row in previous.iterrows():
        for column in ["institution_name_en", "institution_name_fr"]:
            name = row.get(column)
            if isinstance(name, str) and name.strip():
                historical_name_keys.setdefault(normalize_name(name), set()).add(row["_history_key"])

    claimed_keys = set(current.loc[current["_history_key"].isin(previous_keys), "_history_key"])
    for idx, row in current.loc[~current["_history_key"].isin(previous_keys)].iterrows():
        candidate_keys = set()
        for column in ["institution_name_en", "institution_name_fr"]:
            name = row.get(column)
            if isinstance(name, str) and name.strip():
                keys = historical_name_keys.get(normalize_name(name), set())
                if len(keys) == 1:
                    candidate_keys.update(keys)
        if len(candidate_keys) != 1:
            continue
        historical_key = next(iter(candidate_keys))
        if historical_key in claimed_keys:
            continue
        current.at[idx, "_history_key"] = historical_key
        claimed_keys.add(historical_key)

    captured_by_key = previous_by_key["date_captured"].to_dict()
    current["date_captured"] = current["_history_key"].map(captured_by_key).fillna(as_of_date)
    current["date_removed"] = pd.NA

    current_keys = set(current["_history_key"])
    removed = previous.loc[~previous["_history_key"].isin(current_keys)].copy()
    newly_removed_mask = removed["date_removed"].isna()
    removed.loc[newly_removed_mask, "date_removed"] = as_of_date

    all_columns = list(dict.fromkeys(list(current.columns) + list(removed.columns)))
    current = current.reindex(columns=all_columns)
    removed = removed.reindex(columns=all_columns)
    merged = pd.concat([current, removed], ignore_index=True)
    new_count = int((~current["_history_key"].isin(previous_keys)).sum())
    removed_count = int(newly_removed_mask.sum())
    return merged.drop(columns=["_history_key"]), new_count, removed_count


def main():
    previous = pd.read_csv(OUT_CSV) if Path(OUT_CSV).exists() else pd.DataFrame()
    df_en = scrape_institutions(URL_EN, lang="en")
    df_fr = scrape_institutions(URL_FR, lang="fr")
    print(f"Scraped EN institutions: {len(df_en)}")
    print(f"Scraped FR institutions: {len(df_fr)}")

    ckan_df = fetch_ckan_records()
    ckan_df = ckan_df.drop_duplicates(subset=["gc_orgID"])
    print(f"CKAN organizations loaded: {len(ckan_df)}")

    en_exact, fr_exact, en_fuzzy, fr_fuzzy = build_name_indexes(ckan_df)
    df_en = resolve_gc_orgids(df_en, "en", en_exact, en_fuzzy)
    df_fr = resolve_gc_orgids(df_fr, "fr", fr_exact, fr_fuzzy)
    df_en = apply_historical_gc_orgids(df_en, "en", previous)
    df_fr = apply_historical_gc_orgids(df_fr, "fr", previous)
    df_en, df_fr = apply_alternate_url_pairing(df_en, df_fr)
    df_en, df_fr = apply_manual_name_pairing(df_en, df_fr)

    print("EN gcOrgID match methods:")
    print(df_en["match_method_en"].value_counts(dropna=False).to_string())
    print("FR gcOrgID match methods:")
    print(df_fr["match_method_fr"].value_counts(dropna=False).to_string())

    df_en["row_key"] = df_en["gc_orgID_en"].map(lambda x: f"gc:{int(x)}" if pd.notna(x) else None)
    df_en["row_key"] = df_en["row_key"].fillna(df_en["manual_row_key"])
    df_en["row_key"] = df_en["row_key"].fillna(df_en["alternate_row_key"])
    df_en["row_key"] = df_en["row_key"].fillna(
        df_en["url_key"].map(lambda x: f"url:{x}" if isinstance(x, str) else pd.NA)
    )

    df_fr["row_key"] = df_fr["gc_orgID_fr"].map(lambda x: f"gc:{int(x)}" if pd.notna(x) else None)
    df_fr["row_key"] = df_fr["row_key"].fillna(df_fr["manual_row_key"])
    df_fr["row_key"] = df_fr["row_key"].fillna(df_fr["alternate_row_key"])
    df_fr["row_key"] = df_fr["row_key"].fillna(
        df_fr["url_key"].map(lambda x: f"url:{x}" if isinstance(x, str) else pd.NA)
    )

    en_keep = [
        "row_key",
        "gc_orgID_en",
        "institution_name",
        "infosource_url",
        "match_method_en",
        "match_score_en",
        "url_key",
    ]
    fr_keep = [
        "row_key",
        "gc_orgID_fr",
        "institution_name",
        "infosource_url",
        "match_method_fr",
        "match_score_fr",
        "url_key",
    ]
    en_wide = df_en[en_keep].drop_duplicates(subset=["row_key"], keep="first").rename(
        columns={
            "institution_name": "institution_name_en",
            "infosource_url": "infosource_url_en",
            "url_key": "url_key_en",
        }
    )
    fr_wide = df_fr[fr_keep].drop_duplicates(subset=["row_key"], keep="first").rename(
        columns={
            "institution_name": "institution_name_fr",
            "infosource_url": "infosource_url_fr",
            "url_key": "url_key_fr",
        }
    )

    merged = pd.merge(en_wide, fr_wide, on="row_key", how="outer")
    merged["gc_orgID"], merged["gc_orgID_conflict"] = coalesce_gc_orgid(
        merged["gc_orgID_en"], merged["gc_orgID_fr"]
    )
    merged["gc_orgID"] = merged["gc_orgID"].astype("Int64")

    ckan_cols = [
        "gc_orgID",
        "harmonized_name",
        "nom_harmonise",
        "abbreviation",
        "abreviation",
        "website",
        "site_web",
        "open_gov_ouvert",
        "infobaseID",
        "rg",
        "pop",
        "phoenix",
    ]
    ckan_lookup = ckan_df[ckan_cols].copy()
    merged = merged.merge(ckan_lookup, on="gc_orgID", how="left")

    merged, new_count, removed_count = merge_institution_history(
        merged,
        previous,
        date.today().isoformat(),
    )
    merged["gc_orgID"] = pd.to_numeric(merged["gc_orgID"], errors="coerce").astype("Int64")

    org_statuses = fetch_org_statuses()
    merged["status_statut"] = merged["gc_orgID"].map(
        lambda value: org_statuses.get(int(value), "") if pd.notna(value) else ""
    )

    pib_counts = load_pib_counts(COMBINED_PIB_CSV)
    merged["pib_count"] = merged["gc_orgID"].map(
        lambda value: pib_counts.get(str(int(value)), 0) if pd.notna(value) else pd.NA
    ).astype("Int64")

    merged["infosource_status_en"] = pd.NA
    merged["infosource_status_fr"] = pd.NA

    final_order = [
        "gc_orgID",
        "pib_count",
        "date_captured",
        "date_removed",
        "status_statut",
        "gc_orgID_conflict",
        "harmonized_name",
        "nom_harmonise",
        "abbreviation",
        "abreviation",
        "institution_name_en",
        "institution_name_fr",
        "infosource_url_en",
        "infosource_status_en",
        "infosource_url_fr",
        "infosource_status_fr",
        "website",
        "site_web",
        "open_gov_ouvert",
        "infobaseID",
        "rg",
        "pop",
        "phoenix",
        "match_method_en",
        "match_score_en",
        "match_method_fr",
        "match_score_fr",
        "row_key",
        "url_key_en",
        "url_key_fr",
    ]
    merged = merged[final_order].sort_values(
        by=["gc_orgID", "institution_name_en", "institution_name_fr"],
        na_position="last",
    )

    # Save an initial file, then stream URL status updates into CSV as checks complete.
    merged.to_csv(OUT_CSV, index=False)

    unique_urls = pd.unique(
        pd.concat([merged["infosource_url_en"], merged["infosource_url_fr"]], ignore_index=True)
        .dropna()
        .astype(str)
    ).tolist()
    status_cache = probe_urls_parallel_and_stream(merged, unique_urls, OUT_CSV, max_workers=24)
    merged["infosource_status_en"] = merged["infosource_url_en"].map(status_cache)
    merged["infosource_status_fr"] = merged["infosource_url_fr"].map(status_cache)

    merged.to_csv(OUT_CSV, index=False)
    merged.to_csv(SITE_OUT_CSV, index=False)
    merged.to_excel(OUT_XLSX, index=False, engine="openpyxl")

    print(f"Saved CSV -> {OUT_CSV}")
    print(f"Saved Excel -> {OUT_XLSX}")
    print(f"Rows in output: {len(merged)}")
    print(f"Rows with gcOrgID: {merged['gc_orgID'].notna().sum()}")
    print(f"Rows with EN URL status: {merged['infosource_status_en'].notna().sum()}")
    print(f"Rows with FR URL status: {merged['infosource_status_fr'].notna().sum()}")
    print(f"New institutions captured: {new_count}")
    print(f"Institutions first detected as removed: {removed_count}")


if __name__ == "__main__":
    main()
