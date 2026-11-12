#!/usr/bin/env python3
"""Build the assessment catalogue and sanitized readers from collected Markdown."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
import markdown

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'site/data/privacy_assessments.json'
CONTENT = ROOT / 'site/privacy-assessments/content'
ALLOWED_TAGS = set('p h1 h2 h3 h4 h5 h6 a ul ol li table thead tbody tr th td strong em del code pre blockquote hr br img sup sub dl dt dd div span'.split())
ALLOWED_ATTRS = {'a': {'href', 'title'}, 'img': {'src', 'alt', 'title'}, 'th': {'scope', 'colspan', 'rowspan'}, 'td': {'colspan', 'rowspan'}, 'ol': {'start'}}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sanitized_html(text: str) -> str:
    body = re.sub(r'\A---\r?\n.*?\r?\n---\r?\n', '', text, count=1, flags=re.S)
    html = markdown.markdown(body, extensions=['tables', 'fenced_code', 'sane_lists'])
    soup = BeautifulSoup(html, 'html.parser')
    for node in list(soup.find_all(True)):
        if node.parent is None: continue
        if node.name in {'script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'button', 'svg', 'math'}:
            node.decompose()
            continue
        if node.name not in ALLOWED_TAGS:
            node.unwrap()
            continue
        # The page already has its own h1. Demote source headings one level.
        if re.fullmatch('h[1-6]', node.name): node.name = 'h' + str(min(int(node.name[1]) + 1, 6))
        allowed = ALLOWED_ATTRS.get(node.name, set()) | {'id', 'lang'}
        for attr in list(node.attrs):
            if attr not in allowed: del node[attr]
        for attr in ('href', 'src'):
            if attr not in node.attrs: continue
            value = node[attr].strip()
            scheme = urlsplit(value).scheme.lower()
            if scheme not in ('', 'http', 'https', 'mailto') or value.startswith('//') or (attr == 'src' and scheme not in ('http', 'https')):
                del node[attr]
        if node.name == 'img': node['loading'] = 'lazy'
    return str(soup)


def record_type(pia: dict) -> str:
    titles = ' '.join(pia.get('title_' + lang) or '' for lang in ('en', 'fr')).casefold()
    if 'privacy compliance evaluation' in titles or 'évaluation de la conformité en matière de protection' in titles:
        return 'Privacy compliance evaluation'
    if any(s['status'] == 'not_pia_content' for s in pia['sources'].values()):
        return 'Source requires review'
    return 'Privacy assessment'


def build() -> dict:
    records, departments, expected_files = [], [], set()
    source_manifest = json.loads((ROOT / 'PIAs/collection_manifest.json').read_text())
    for path in sorted((ROOT / 'PIAs').glob('*/collection.json')):
        org = json.loads(path.read_text())
        if not org['pias']: continue
        department = {key: org.get(key) or '' for key in ('institution_id', 'name_en', 'name_fr', 'gc_orgID')}
        if re.fullmatch(r'\d+\.0', department['gc_orgID']): department['gc_orgID'] = department['gc_orgID'][:-2]
        departments.append(department)
        for pia in org['pias']:
            uid = org['institution_id'] + '/' + pia['pia_id']
            row = {**department, 'id': uid, 'pia_id': pia['pia_id'], 'title_en': pia['title_en'], 'title_fr': pia['title_fr'],
                   'type': record_type(pia), 'available_languages': [], 'sources': {}}
            # Failed pages can have an error-page title. Show the intended title from the institution's list instead.
            for lang in ('en', 'fr'):
                source = pia['sources'].get(lang, {})
                if source.get('status') != 'exported': row['title_' + lang] = source.get('title_from_list') or row['title_' + lang]
            document = {**row, 'pairing_status': pia['pairing_status'], 'pairing_method': pia['pairing_method'], 'collected_at_utc': org['collected_at_utc'], 'languages': {}}
            for lang, source in pia['sources'].items():
                row['sources'][lang] = {'status': source['status'], 'http_status': source['http']['http_status'], 'url': source['url'], 'checked_at_utc': source['http']['checked_at_utc']}
                language = {**row['sources'][lang], 'title': row['title_' + lang], 'kind': source['kind'], 'html': None, 'markdown_url': None,
                            'date_modified': source.get('date_modified'), 'date_published': source.get('date_published'), 'anchor_type': source.get('anchor_type')}
                if source['status'] == 'exported':
                    raw = (path.parent / source['markdown_path']).read_bytes()
                    if digest(raw) != source['markdown_sha256']: raise ValueError(f'Markdown checksum mismatch: {uid} {lang}')
                    output = CONTENT / org['institution_id'] / source['markdown_path']
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(raw)
                    expected_files.add(output)
                    language.update(html=sanitized_html(raw.decode('utf-8')), markdown_url=str(output.relative_to(ROOT / 'site')), markdown_sha256=digest(raw))
                    row['available_languages'].append(lang)
                document['languages'][lang] = language
            row['content_url'] = f'privacy-assessments/content/{uid}.json'
            document['available_languages'] = row['available_languages']
            target = ROOT / 'site' / row['content_url']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(document, ensure_ascii=False, separators=(',', ':')) + '\n')
            expected_files.add(target)
            records.append(row)
    for old in CONTENT.rglob('*'):
        if old.is_file() and old not in expected_files: old.unlink()
    records.sort(key=lambda r: (r['name_en'].casefold(), (r['title_en'] or r['title_fr'] or '').casefold(), r['id']))
    departments.sort(key=lambda r: r['name_en'].casefold())
    availability = Counter('both' if len(r['available_languages']) == 2 else r['available_languages'][0] if r['available_languages'] else 'none' for r in records)
    counts = Counter(r['institution_id'] for r in records)
    summary = {'records': len(records), 'departments': len(departments), 'markdown_exports': sum(len(r['available_languages']) for r in records),
               'readable_records': sum(bool(r['available_languages']) for r in records), 'availability': dict(availability),
               'document_types': dict(Counter(r['type'] for r in records)),
               'top_departments': [{**d, 'count': counts[d['institution_id']]} for d in sorted(departments, key=lambda d: (-counts[d['institution_id']], d['name_en']))[:6]]}
    payload = {'schema_version': 1, 'collection_generated_at_utc': source_manifest['generated_at_utc'], 'summary': summary, 'departments': departments, 'records': records}
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f"Built PIA site: {summary['records']} records, {summary['markdown_exports']} Markdown exports, {summary['departments']} departments")
    return payload


if __name__ == '__main__': build()
