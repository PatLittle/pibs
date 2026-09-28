#!/usr/bin/env python3
"""Check side-by-side assets, relative links, and deployment ownership boundaries."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                parsed = urlsplit(value)
                if parsed.path and not parsed.scheme and not parsed.netloc:
                    self.paths.append(unquote(parsed.path))


def validate():
    workflows = ROOT / ".github/workflows"
    explorer = (workflows / "deploy-pages.yml").read_text()
    original = (workflows / "deploy-my-info-pages.yml").read_text()
    candidate = (workflows / "deploy-my-info-v2-pages.yml").read_text()
    for content in [explorer, original, candidate]:
        assert "group: pages-branch-deploy" in content, "Shared branch writers must serialize"
        assert "queue: max" in content, "All three writers must queue without replacing pending siblings"
        assert "cancel-in-progress: false" in content, "Never cancel a partial deployment"
        assert "if: github.ref == 'refs/heads/main'" in content, "Feature branches must not overwrite published versions"
        assert "force: true" not in content, "Never force the shared pages branch"
    for folder in ["my_info", "my_info_v2", "my_info_compare"]:
        assert f'"!site/{folder}/**"' in explorer, f"Explorer trigger must exclude {folder}"
        assert f'--exclude "{folder}/"' in explorer, f"Explorer payload must exclude {folder}"
        clean_exclusions = explorer.split("clean-exclude:", 1)[1]
        assert f"{folder}/**" in clean_exclusions, f"Explorer cleanup must preserve {folder}"
    assert re.findall(r"target-folder: (\S+)", original) == ["my_info"]
    assert re.findall(r"target-folder: (\S+)", candidate) == ["my_info_v2", "my_info_compare"]
    assert "git diff --exit-code -- site/my_info my_info/web packages/my-info-mcp" in candidate

    for folder in ["my_info", "my_info_v2"]:
        for name in ["index.html", "runtime.json", "engine.mjs", "app.mjs", "styles.css"]:
            assert (SITE / folder / name).is_file(), f"Missing {folder}/{name}"
    header_pages = [SITE / name for name in [
        "index.html", "table.html", "my_info/index.html", "my_info_v2/index.html",
        "my_info_compare/index.html", "my_info_compare/v1-review.html",
        "my_info_v2/review/index.html",
    ]]
    assert (SITE / "prototype-label.css").is_file()
    for path in header_pages:
        content = path.read_text(encoding="utf-8")
        assert "<gcds-header" in content and '<gcds-signature></gcds-signature>' in content, path
        assert 'class="prototype-label-text" style="display:none">Prototype - For Discussion' in content, path
        assert "prototype-label.css" in content, path
    landing = (SITE / "index.html").read_text(encoding="utf-8")
    assert 'id="survey-heading"' not in landing
    assert '<nav aria-label="Footer navigation">' in landing and 'href="my_info_compare/"' in landing
    review = (SITE / "my_info_compare/v1-review.html").read_text(encoding="utf-8")
    assert 'href="#candidate-only-note"' in review and 'id="candidate-only-note"' in review
    for path in [SITE / "index.html", *list((SITE / "my_info_v2").rglob("*.html")), *list((SITE / "my_info_compare").glob("*.html"))]:
        links = Links()
        links.feed(path.read_text())
        for link in links.paths:
            target = (path.parent / link).resolve()
            assert target.is_relative_to(SITE), f"Link escapes the deployed site: {link}"
            assert target.exists(), f"Broken link in {path.relative_to(ROOT)}: {link}"
    for source, generated in [("my_info_v2/engine.mjs", "site/my_info_v2/engine.mjs"),
                              ("my_info_v2/web/app.mjs", "site/my_info_v2/app.mjs")]:
        assert (ROOT / source).read_bytes() == (ROOT / generated).read_bytes(), f"Stale generated file: {generated}"
    runtime = json.loads((SITE / "my_info_v2/runtime.json").read_text())
    assert runtime["coverage"]["inventory_rows"] == len(runtime["records"])
    assert len({r["record_id"] for r in runtime["records"]}) == len(runtime["records"])
    assert runtime["coverage"]["directory_record_count"] == len(runtime["records"])
    for rid in {rid for a in runtime["activities"] for rid in a["record_ids"]}:
        record = next(r for r in runtime["records"] if r["record_id"] == rid)
        assert record["source_url_en"].startswith(("http://", "https://")), rid
    print("Validated independent original, V2 and comparison deployment boundaries and local links.")


if __name__ == "__main__":
    validate()
