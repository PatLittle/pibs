#!/usr/bin/env python3
"""Fetch and extract one deterministic batch of institution Info Source jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from markitdown import MarkItDown
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from build_cor_table_from_markdown import parse_records as parse_cor_records
from build_cor_table_from_markdown import process_folder as process_cor_folder
from build_pib_table_from_markdown import parse_records as parse_pib_records
from build_pib_table_from_markdown import process_folder as process_pib_folder


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PIBS-Institution-Collector/3.0; +https://github.com/PatLittle/pibs)"
}
ROLE_NAMES = ("pibs_en", "pibs_fr", "classes_of_records_en", "classes_of_records_fr")


def session() -> requests.Session:
    client = requests.Session()
    retries = Retry(
        total=3,
        connect=3,
        read=2,
        status=2,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    client.mount("http://", HTTPAdapter(max_retries=retries))
    client.mount("https://", HTTPAdapter(max_retries=retries))
    client.headers.update(HEADERS)
    return client


def load_jobs(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def content_extension(content_type: str, final_url: str) -> str:
    media_type = content_type.split(";", 1)[0].casefold()
    known = {
        "text/html": ".html",
        "application/xhtml+xml": ".html",
        "application/pdf": ".pdf",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
    }
    if media_type in known:
        return known[media_type]
    suffix = Path(urlparse(final_url).path).suffix
    return suffix if suffix and len(suffix) <= 8 else mimetypes.guess_extension(media_type) or ".bin"


def scoped_html(content: bytes, fragment: str) -> bytes:
    if not fragment:
        return content
    soup = BeautifulSoup(content, "lxml")
    target = soup.find(id=unquote(fragment)) or soup.find(attrs={"name": unquote(fragment)})
    if target is None:
        return content
    heading = target if target.name and re.fullmatch(r"h[1-6]", target.name) else target.find_parent(re.compile(r"^h[1-6]$"))
    if heading is None:
        heading = target.find_next(re.compile(r"^h[1-6]$"))
    if heading is None:
        return content
    level = int(heading.name[1])
    selected = [heading]
    sibling = heading.find_next_sibling()
    while sibling is not None:
        if sibling.name and re.fullmatch(r"h[1-6]", sibling.name) and int(sibling.name[1]) <= level:
            break
        selected.append(sibling)
        sibling = sibling.find_next_sibling()
    html = "<!doctype html><html><body>" + "".join(str(item) for item in selected) + "</body></html>"
    return html.encode("utf-8")


def normalized_html(content: bytes, encoding: str) -> bytes:
    utf8_text = content.decode("utf-8", errors="replace")
    replacement_ratio = utf8_text.count("\ufffd") / max(len(utf8_text), 1)
    if replacement_ratio < 0.002:
        # Some legacy federal pages declare ISO-8859-1 and contain a handful
        # of Latin-1 bytes, while the substantive page body is UTF-8.
        text = utf8_text
    else:
        try:
            text = content.decode(encoding or "utf-8", errors="replace")
        except LookupError:
            text = utf8_text
    return BeautifulSoup(text, "lxml").encode("utf-8")


def convert_to_markdown(
    source_path: Path, content: bytes, content_type: str, fragment: str, encoding: str = ""
) -> str:
    conversion_path = source_path
    derived_path = source_path.with_name(source_path.stem + "_conversion.html")
    if source_path.suffix.casefold() in {".html", ".htm"}:
        normalized = normalized_html(content, encoding)
        derived_path.write_bytes(scoped_html(normalized, fragment) if fragment else normalized)
        conversion_path = derived_path
    try:
        return MarkItDown().convert(str(conversion_path)).markdown or ""
    finally:
        if conversion_path == derived_path:
            derived_path.unlink(missing_ok=True)


def crawl_score(text: str, url: str, role: str) -> int:
    value = re.sub(r"\s+", " ", text).casefold()
    path = urlparse(url).path.casefold()
    if any(marker in path for marker in (
        "standard-personal-information", "fichiers-renseignements-personnels-ordinaires",
        "standard-classes-records", "categories-documents-ordinaires",
    )):
        return -100
    score = 0
    if role.startswith("pibs"):
        if any(marker in value for marker in (
            "personal information bank", "fichier de renseignements personnels",
            "fichiers de renseignements personnels",
        )):
            score += 10
        if re.search(r"(?:pib|personal-information|p5\.html)", path):
            score += 6
        if re.search(r"\b[A-Z]{2,6}\s+(?:PPU|PPE|PCU|POU)\s+\d{3}\b", text, re.I):
            score += 8
    else:
        if any(marker in value for marker in (
            "class of records", "classes of records", "categorie de documents",
            "categories de documents",
        )):
            score += 10
        if re.search(r"(?:class|record|p3\.html)", path):
            score += 6
        if re.search(r"\b[A-Z]{2,6}(?:\s+[A-Z]{2,6})?\s+\d{3}\b", text, re.I):
            score += 5
    if any(marker in value for marker in (
        "institutional functions, programs and activities",
        "fonctions, programmes et activites de l'institution",
        "fonctions, programmes et activités de l'institution",
    )):
        score += 7
    return score


def same_site_namespace(initial_url: str, candidate_url: str) -> bool:
    """Keep discovery inside the institution and language namespace.

    Canada.ca hosts many institutions on one hostname, so same-host crawling is
    not a sufficient boundary. Its first two path components identify the
    language and institution (for example, ``en/immigration-refugees-citizenship``).
    """
    initial = urlparse(initial_url)
    candidate = urlparse(candidate_url)
    if initial.netloc.casefold() != candidate.netloc.casefold():
        return False
    initial_parts = [part.casefold() for part in initial.path.split("/") if part]
    candidate_parts = [part.casefold() for part in candidate.path.split("/") if part]
    host = initial.netloc.casefold()
    if host in {"canada.ca", "www.canada.ca"}:
        return len(initial_parts) >= 2 and initial_parts[:2] == candidate_parts[:2]
    if initial_parts and initial_parts[0] in {"en", "eng", "fr", "fra"}:
        return bool(candidate_parts) and initial_parts[0] == candidate_parts[0]
    return True


def discover_role_pages(
    role: str,
    initial_url: str,
    initial_content: bytes,
    initial_type: str,
    client: requests.Session,
    raw_folder: Path,
    max_pages: int = 6,
) -> tuple[list[str], list[dict[str, object]]]:
    if "html" not in initial_type.casefold():
        return [], []
    host = urlparse(initial_url).netloc.casefold()
    queue: list[tuple[str, bytes]] = [(initial_url, initial_content)]
    visited = {urlunparse(urlparse(initial_url)._replace(fragment=""))}
    markdown_parts: list[str] = []
    discovered: list[dict[str, object]] = []
    while queue and len(discovered) < max_pages:
        page_url, content = queue.pop(0)
        soup = BeautifulSoup(content, "lxml")
        candidates: list[tuple[int, str]] = []
        for anchor in soup.find_all("a", href=True):
            absolute = urljoin(page_url, str(anchor["href"]))
            parsed = urlparse(absolute)
            normalized = urlunparse(parsed._replace(fragment=""))
            if (
                parsed.scheme not in {"http", "https"}
                or parsed.netloc.casefold() != host
                or not same_site_namespace(initial_url, normalized)
                or normalized in visited
            ):
                continue
            score = crawl_score(anchor.get_text(" ", strip=True), absolute, role)
            if score >= 6:
                candidates.append((score, normalized))
        for _, candidate in sorted(set(candidates), key=lambda item: (-item[0], item[1])):
            if candidate in visited or len(discovered) >= max_pages:
                continue
            visited.add(candidate)
            try:
                response = client.get(candidate, allow_redirects=True, timeout=(15, 75))
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "html" not in content_type.casefold():
                    continue
                index = len(discovered) + 1
                source_path = raw_folder / f"{role}_linked_{index}.html"
                source_path.write_bytes(response.content)
                markdown = convert_to_markdown(
                    source_path, response.content, content_type, "", response.encoding or ""
                )
                markdown_parts.append(markdown)
                discovered.append({
                    "url": candidate,
                    "final_url": response.url,
                    "http_status": response.status_code,
                    "byte_count": len(response.content),
                    "sha256": hashlib.sha256(response.content).hexdigest(),
                    "raw_path": str(source_path),
                })
                queue.append((response.url, response.content))
            except requests.RequestException as exc:
                discovered.append({"url": candidate, "status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return markdown_parts, discovered


def collect_job(job: dict[str, object], client: requests.Session) -> dict[str, object]:
    folder = Path(str(job["content_folder"]))
    snapshot_date = str(job["snapshot_date"])
    raw_folder = folder / "snapshots" / snapshot_date / "raw"
    raw_folder.mkdir(parents=True, exist_ok=True)
    urls = dict(job["urls"])
    response_cache: dict[str, tuple[bytes, str, int, str, str]] = {}
    sources: dict[str, object] = {}

    for role in ROLE_NAMES:
        url = str(urls.get(role, "") or "").strip()
        markdown_path = folder / f"{role}.md"
        if not url:
            markdown_path.write_text("", encoding="utf-8")
            sources[role] = {"status": "missing_url", "url": ""}
            continue
        requested_without_fragment = url.split("#", 1)[0]
        fragment = urlparse(url).fragment
        try:
            if requested_without_fragment not in response_cache:
                response = client.get(requested_without_fragment, allow_redirects=True, timeout=(15, 75))
                response.raise_for_status()
                response_cache[requested_without_fragment] = (
                    response.content,
                    response.headers.get("content-type", ""),
                    response.status_code,
                    response.url,
                    response.encoding or "",
                )
            content, content_type, status_code, final_url, encoding = response_cache[requested_without_fragment]
            extension = content_extension(content_type, final_url)
            source_path = raw_folder / f"{role}{extension}"
            source_path.write_bytes(content)
            markdown = convert_to_markdown(source_path, content, content_type, fragment, encoding)
            parser = parse_pib_records if role.startswith("pibs") else parse_cor_records
            linked_markdown, discovered = discover_role_pages(
                role, final_url, content, content_type, client, raw_folder
            )
            if linked_markdown:
                combined = "\n\n".join([markdown, *linked_markdown])
                # Only add crawled pages when they improve record coverage.
                if len(parser(combined)) > len(parser(markdown)):
                    markdown = combined
            markdown_path.write_text(markdown, encoding="utf-8")
            sources[role] = {
                "status": "collected",
                "requested_url": url,
                "final_url": final_url + (f"#{fragment}" if fragment else ""),
                "http_status": status_code,
                "content_type": content_type,
                "encoding": encoding,
                "byte_count": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "raw_path": str(source_path),
                "markdown_path": str(markdown_path),
                "fragment": fragment,
                "discovered_pages": discovered,
            }
        except Exception as exc:
            markdown_path.write_text("", encoding="utf-8")
            sources[role] = {
                "status": "error",
                "requested_url": url,
                "error": f"{type(exc).__name__}: {exc}",
            }

    _, pib_en, pib_fr, pib_merged = process_pib_folder(folder)
    cor_en, cor_fr, cor_merged = process_cor_folder(folder)
    report = {
        **{key: job[key] for key in (
            "snapshot_date", "registry_sha256", "institution_id", "gc_orgID",
            "institution_name_en", "institution_name_fr", "access_act_order", "content_folder",
        )},
        "collector_version": 3,
        "parser_versions": {"pibs": 4, "classes_of_records": 1},
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "extraction": {
            "pibs": {"english": pib_en, "french": pib_fr, "merged": pib_merged},
            "classes_of_records": {"english": cor_en, "french": cor_fr, "merged": cor_merged},
        },
    }
    (folder / "source_manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-file", type=Path, required=True)
    parser.add_argument("--batch-index", type=int, default=0)
    parser.add_argument("--batch-count", type=int, default=1)
    parser.add_argument("--institution-id", action="append", default=[])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.batch_count < 1 or not 0 <= args.batch_index < args.batch_count:
        raise SystemExit("--batch-index must be in [0, --batch-count)")

    jobs = [job for job in load_jobs(args.jobs_file) if job.get("collectable")]
    if args.institution_id:
        requested = set(args.institution_id)
        jobs = [job for job in jobs if job["institution_id"] in requested]
        missing = requested - {str(job["institution_id"]) for job in jobs}
        if missing:
            raise SystemExit(f"Unknown or uncollectable institution IDs: {sorted(missing)}")
    else:
        jobs = [job for index, job in enumerate(jobs) if index % args.batch_count == args.batch_index]

    client = session()
    reports = []
    for index, job in enumerate(jobs, 1):
        print(f"[{index}/{len(jobs)}] {job['institution_id']}", flush=True)
        reports.append(collect_job(job, client))
    report_path = args.report or args.jobs_file.with_name(
        f"{args.jobs_file.stem}_batch_{args.batch_index + 1}_of_{args.batch_count}.json"
    )
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = sum(
        source.get("status") == "error"
        for report in reports
        for source in report["sources"].values()
    )
    print(f"Completed {len(reports)} institutions with {errors} source errors; report={report_path}")


if __name__ == "__main__":
    main()
