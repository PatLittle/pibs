#!/usr/bin/env python3
"""Aggregate PIA-list pointers from previously collected Info Source artifacts."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'PIAs'
CACHE = ROOT / 'work/pia_http_cache'
LINK = re.compile(r'\[([^\]]+)\]\(([^\s)]+)(?:\s+"[^"]*")?\)', re.S)


def norm(s):
    return unicodedata.normalize('NFKD', s.replace('’', "'").replace('‘', "'")).encode('ascii', 'ignore').decode().lower()


def pia(s):
    return bool(re.search(r'privacy impact|\bpias?\b|facteurs relatifs.{0,50}vie privee|\befr?vps?\b', norm(LINK.sub(r'\1', s))))


class Page(HTMLParser):
    """Small dependency-free HTML-to-text adapter preserving link context."""
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.parts, self.hrefs, self.skip = [], [], 0
        main = re.search(r'<main\b[^>]*>(.*?)</main>', html, re.S | re.I)
        self.feed(main[1] if main else html)
        self.text = ''.join(self.parts)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if self.skip: return
        if tag in ('p', 'li', 'h1', 'h2', 'h3', 'h4', 'div', 'section', 'br'): self.parts.append('\n\n')
        if tag in ('h1', 'h2', 'h3', 'h4'): self.parts.append('#' * int(tag[1]) + ' ')
        if tag == 'a':
            self.hrefs.append(attrs.get('href', ''))
            self.parts.append('[')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip: return
        if tag == 'a' and self.hrefs: self.parts.append('](' + self.hrefs.pop() + ')')
        if tag in ('p', 'li', 'h1', 'h2', 'h3', 'h4', 'div', 'section'): self.parts.append('\n\n')

    def handle_data(self, data):
        if not self.skip: self.parts.append(data.replace('[', '').replace(']', ''))


def links(text, base):
    for m in LINK.finditer(text):
        label, href = re.sub(r'\s+', ' ', m[1]).strip(), m[2]
        if href.startswith(('#', 'mailto:', 'javascript:')): continue
        start = text.rfind('\n\n', 0, m.start())
        end = text.find('\n\n', m.end())
        context = re.sub(r'\s+', ' ', text[max(0, start):end if end >= 0 else len(text)]).strip()
        url = urllib.parse.urljoin(base, href)
        if urllib.parse.urlsplit(url).scheme not in ('http', 'https'): continue
        yield label, url, context, m.start()


def score(label, url, context):
    n, c = norm(label), norm(LINK.sub('', context))
    if re.search(r'directive|standard on|policy on|privacy policy|politique|norme sur|treasury board', n): return 0
    direct = pia(label)
    contextual = pia(LINK.sub('', context)) and len(context) < 1800 and bool(re.search(r'summar|completed|conducts|available|resum|sommair|realise|effectue|consulter|disponib', c))
    if re.search(r'categorie de documents|class of record|classe de documents', n): return 0
    if not (direct or contextual): return 0
    if direct and re.search(r'privacy impact assessment (?:of|for|summary for|summary of)|evaluation des facteurs relatifs a la vie privee (?:de |du |pour )', n): return 0
    if re.search(r'francais|english|skip|passer|introduction|privacy act|loi sur|open data|donnees ouvertes|access.*requests|demandes.*acces', n): return 0
    if not direct and re.search(r'privacy commissioner|commissaire|canada.ca/en.html|request|demande', n): return 0
    value = 20 if direct else 5
    if re.search(r'summar|completed|resum|sommair', n): value += 5
    if re.search(r'publications|references|\bhere\b', n): value += 2
    if re.search(r'\bof the\b|\bfor the\b|survey initiative|research infrastructure funding', n): value -= 18
    return value


class LanguageLinks(HTMLParser):
    def __init__(self, html, base):
        super().__init__()
        self.urls, self.base = {}, base
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        lang = attrs.get('hreflang') or attrs.get('lang')
        if tag in ('a', 'link') and lang in ('en', 'fr') and attrs.get('href'):
            self.urls[lang] = urllib.parse.urljoin(self.base, attrs['href'])


def fetch(url, refresh=False):
    key = hashlib.sha256(('v3:' + url).encode()).hexdigest()
    path = CACHE / (key + '.json')
    if path.exists() and not refresh: return json.loads(path.read_text())
    result = {'requested_url': url, 'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'http_status': '', 'final_url': url, 'error': '', 'text': '', 'language_alternates': {}}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; PIBs-PIA-index/1.0)'})
        with urllib.request.urlopen(req, timeout=25) as response:
            result.update(http_status=response.status, final_url=response.url)
            body = response.read(5000000)
            if 'html' in response.headers.get('Content-Type', ''):
                html = body.decode(response.headers.get_content_charset() or 'utf-8', errors='replace')
                result['text'] = Page(html).text
                result['language_alternates'] = LanguageLinks(html, response.url).urls
    except urllib.error.HTTPError as exc:
        result.update(http_status=exc.code, final_url=exc.url, error=str(exc))
    except Exception as exc:
        result['error'] = type(exc).__name__ + ': ' + str(exc)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False))
    return result


def generic_pia_label(label):
    label = norm(label).strip().strip('# ').strip()
    label = re.sub(r'\([^)]*\)', '', label).strip()
    label = re.sub(r' +', ' ', label)
    label = re.sub(r'^(?:annual reports and |rapports annuels et )', '', label)
    label = label.replace("d’evaluation", 'des evaluation').replace("d'evaluation", 'des evaluation')
    label = label.replace('pia summaries', 'privacy impact assessment summaries')
    label = re.sub(r' completees$', '', label)
    return bool(re.fullmatch(
        r'(?:(?:executive )?summaries (?:of )?(?:completed )?|completed )?(?:privacy impact assessments?|pias?)(?:[ -]*(?:executive )?summaries)?'
        r'|(?:(?:resumes|sommaires) (?:des? |d[’\']|les )?)?evaluations? des facteurs relatifs a la vie privee(?:[ -]*(?:resumes|sommaires))?', label))


def resolve(candidate, refresh=False):
    """Follow at most two PIA-labelled navigation links; never fetch list items."""
    url = candidate['url']
    trail = []
    for depth in range(3):
        result = fetch(url, refresh)
        trail.append({k: v for k, v in result.items() if k != 'text'})
        text = result['text']
        found = list(links(text, result['final_url']))
        # An explicit list of multiple assessment links is sufficient evidence.
        assessment_links = [x for x in found if pia(x[0]) and not generic_pia_label(x[0]) and not re.search(r'directive|policy|standard|politique|norme', norm(x[0]))]
        distinct = {urllib.parse.urldefrag(x[1])[0] for x in assessment_links if urllib.parse.urldefrag(x[1])[0] != urllib.parse.urldefrag(result['final_url'])[0]}
        if result['http_status'] != 200:
            state = 'http_error' if result['http_status'] else 'request_error'
            break
        # A PIA heading with linked program names is also a list, including
        # institutions publishing only one summary. Do not count utility links.
        normalized = re.sub(r'(#{1,6})\s+', r'\1 ', text)
        headings = list(re.finditer(r'(?m)^\s*(#{1,6}) ([^\n]+)', normalized))
        list_section = False
        for i, heading in enumerate(headings):
            if not generic_pia_label(heading[2]): continue
            end = next((h.start() for h in headings[i+1:] if len(h[1]) <= len(heading[1])), len(normalized))
            content = normalized[heading.end():end]
            local = [x for x in links(content, result['final_url'])
                     if urllib.parse.urlsplit(x[1]).netloc == urllib.parse.urlsplit(result['final_url']).netloc
                     and urllib.parse.urldefrag(x[1])[0] != urllib.parse.urldefrag(result['final_url'])[0]
                     and not re.search(r'contact|privacy notice|avis|accessibil|top of|haut de|privacy policy|directive|norme|politique', norm(x[0]))]
            if local: list_section = True
        if len(distinct) >= 2 or list_section:
            state = 'list_detected'
            break
        choices = sorted([(score(a, b, c), a, b) for a, b, c, _ in found
                          if generic_pia_label(a)
                          and b not in [t['requested_url'] for t in trail]
                          and urllib.parse.urldefrag(b)[0] != urllib.parse.urldefrag(result['final_url'])[0]], reverse=True)
        if not choices:
            choices = [(0, a, b) for a, b, _, _ in found if re.fullmatch(r'access to information and privacy|acces a l[’\']information et protection (?:des renseignements personnels|de la vie privee)', norm(a)) and b not in [t['requested_url'] for t in trail]]
        if not choices or depth == 2:
            state = 'needs_review'
            break
        url = choices[0][2]
    return {'url': url, 'http_status': result['http_status'], 'final_url': result['final_url'], 'resolution': state, 'checked_at_utc': result['checked_at_utc'], 'navigation': trail, 'language_alternates': result.get('language_alternates', {})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Recheck cached HTTP requests')
    parser.add_argument('--offline', action='store_true', help='Extract artifact links without HTTP checks')
    args = parser.parse_args()
    registry = list(csv.DictReader((ROOT / 'institution_registry.csv').open()))
    manifests = {}
    for path in sorted((ROOT / 'institutions_infosource_docs').glob('*/source_manifest.json')):
        m = json.loads(path.read_text())
        manifests[m.get('institution_id')] = (path, m)
    registry_ids = {org['institution_id'] for org in registry}
    # Preserve artifact-only institutions instead of silently dropping history.
    for institution_id, (_, manifest) in manifests.items():
        if institution_id and institution_id not in registry_ids:
            registry.append({'institution_id': institution_id, 'gc_orgID': manifest.get('gc_orgID', ''), 'legal_name_en': manifest.get('institution_name_en', ''), 'legal_name_fr': manifest.get('institution_name_fr', '')})
    rows, evidence, tasks = [], [], {}
    for org in registry:
        row = {key: org.get(key, '') for key in ('institution_id', 'gc_orgID', 'open_canada_org_id', 'open_canada_org_slug', 'legal_name_en', 'legal_name_fr')}
        row['registry_membership'] = 'current_registry' if org['institution_id'] in registry_ids else 'artifact_only'
        entry = manifests.get(org['institution_id'])
        for lang in ('en', 'fr'):
            candidates, scanned = [], []
            if entry:
                manifest_path, manifest = entry
                for role in ('pibs_' + lang, 'classes_of_records_' + lang, 'infosource_' + lang):
                    source = manifest.get('sources', {}).get(role, {})
                    base = source.get('final_url') or source.get('requested_url') or org.get('infosource_url_' + lang, '')
                    markdown = source.get('markdown_path') or str(manifest_path.parent.relative_to(ROOT) / (role + '.md'))
                    # Rebuilt Markdown includes selected supplemental captures.
                    paths = [markdown] if (ROOT / markdown).exists() else []
                    replaced = any(s.get('replaces_previous') and role in s.get('roles', []) for s in manifest.get('supplemental_sources', []))
                    if source.get('raw_path') and not replaced: paths.append(source['raw_path'])
                    for relative in dict.fromkeys(p for p in paths if p):
                        path = ROOT / relative
                        if not path.exists() or path.suffix not in ('.md', '.html', '.htm'): continue
                        scanned.append(relative)
                        text = path.read_text(errors='replace')
                        if path.suffix != '.md': text = Page(text).text
                        for label, url, context, position in links(text, base):
                            rank = score(label, url, context)
                            if rank >= 5:
                                candidates.append({'label': label, 'url': url, 'context': context, 'artifact': relative, 'artifact_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source_url': base, 'score': rank, 'position': position / max(1, len(text))})
            # Highest semantic score, then prefer links near the end of the source.
            candidates.sort(key=lambda x: (x['score'], x['position']), reverse=True)
            selected = candidates[0] if candidates else None
            row['pia_link_in_infosource_' + lang] = 'Y' if selected else 'N'
            row['artifact_coverage_' + lang] = 'scanned' if scanned else 'no_artifact'
            row['infosource_pia_url_' + lang] = selected['url'] if selected else ''
            row['pia_list_url_' + lang] = selected['url'] if selected else ''
            row['discovery_method_' + lang] = 'infosource_artifact' if selected else ''
            row['review_note_' + lang] = ''
            row['infosource_pia_http_status_' + lang] = ''
            for field in ('http_status', 'final_url', 'checked_at_utc'): row[field + '_' + lang] = ''
            row['resolution_' + lang] = 'not_checked' if selected else ('no_link_found' if scanned else 'no_artifact')
            ev = {'institution_id': org['institution_id'], 'language': lang, 'scanned_artifacts': scanned, 'selected': selected, 'candidates': candidates}
            evidence.append(ev)
            if selected: tasks[(org['institution_id'], lang)] = (row, selected, ev)
        row['pia_link_in_infosource'] = 'Y' if any(row['pia_link_in_infosource_' + l] == 'Y' for l in ('en', 'fr')) else 'N'
        rows.append(row)
    if not args.offline:
        unique = {v[1]['url']: v[1] for v in tasks.values()}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(resolve, c, args.refresh): url for url, c in unique.items()}
            resolved = {}
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                resolved[url] = future.result()
                print(resolved[url]['http_status'], resolved[url]['resolution'], url, flush=True)
        for (_, lang), (row, selected, ev) in tasks.items():
            result = resolved[selected['url']]
            row['pia_list_url_' + lang] = result['url']
            for field in ('http_status', 'final_url', 'checked_at_utc', 'resolution'): row[field + '_' + lang] = result[field]
            row['infosource_pia_http_status_' + lang] = result['navigation'][0]['http_status']
            ev['navigation'] = result['navigation']
        # A source can omit its link or retain a stale one. Use an explicit
        # language switch on the working counterpart; never manufacture URLs.
        evidence_by_key = {(e['institution_id'], e['language']): e for e in evidence}
        for row in rows:
            for lang, other in (('en', 'fr'), ('fr', 'en')):
                if row['resolution_' + lang] == 'list_detected': continue
                partner = resolved.get(row['infosource_pia_url_' + other], {})
                if partner.get('resolution') != 'list_detected': continue
                # Known source misattribution must not propagate to a sibling.
                if row['institution_id'] == 'ati-schedule-i-immigration-and-refugee-board': continue
                alternate = partner.get('language_alternates', {}).get(lang)
                if not alternate or alternate == row['pia_list_url_' + lang]: continue
                result = resolve({'url': alternate}, args.refresh)
                if result['resolution'] != 'list_detected': continue
                row['pia_list_url_' + lang] = result['url']
                row['discovery_method_' + lang] = 'counterpart_language_link'
                for field in ('http_status', 'final_url', 'checked_at_utc', 'resolution'): row[field + '_' + lang] = result[field]
                ev = evidence_by_key[(row['institution_id'], lang)]
                ev['counterpart_discovery'] = {'from_url': partner['final_url'], 'alternate_url': alternate, 'navigation': result['navigation']}
        for row in rows:
            if row['institution_id'] == 'ati-schedule-i-immigration-and-refugee-board' and row['pia_link_in_infosource_fr'] == 'Y':
                row['resolution_fr'] = 'needs_review'
                row['review_note_fr'] = 'Info Source points to the IRCC list, not the Immigration and Refugee Board; institutional attribution needs review.'
            if row['institution_id'] == 'ati-schedule-i-financial-transactions-and-reports-analysis-centre-of-canada':
                for lang in ('en', 'fr'):
                    row['review_note_' + lang] = 'The source labels this as PIA summaries, but its URL is an access-to-information request search.'
            if row['institution_id'] == 'ati-schedule-i-patented-medicine-prices-review-board':
                row['review_note_fr'] = 'The French source links to an English URL, which redirects to a general ATIP page.'
    OUT.mkdir(exist_ok=True)
    with (OUT / 'index.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUT / 'evidence.jsonl').open('w') as handle:
        for ev in evidence: handle.write(json.dumps(ev, ensure_ascii=False) + '\n')
    summary = {lang: {state: sum(r['resolution_' + lang] == state for r in rows) for state in sorted({r['resolution_' + lang] for r in rows})} for lang in ('en', 'fr')}
    (OUT / 'build_manifest.json').write_text(json.dumps({'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'registry_sha256': hashlib.sha256((ROOT / 'institution_registry.csv').read_bytes()).hexdigest(), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'organization_count': len(rows), 'summary': summary, 'outputs_sha256': {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ('index.csv', 'evidence.jsonl')}}, indent=2) + '\n')
    print(f'Wrote {len(rows)} organizations; {len(tasks)} language-specific pointers.')


if __name__ == '__main__': main()
