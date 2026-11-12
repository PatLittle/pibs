#!/usr/bin/env python3
"""Check the published assessment catalogue against organization collections."""
import hashlib
import csv
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def validate():
    errors = []
    site = ROOT / 'site'
    if not (site / '.nojekyll').exists(): errors.append('Static Pages marker missing: Markdown downloads must not be processed by Jekyll')
    payload = json.loads((site / 'data/privacy_assessments.json').read_text())
    manifest = json.loads((ROOT / 'PIAs/collection_manifest.json').read_text())
    records = payload['records']
    if len(records) != manifest['pia_count']: errors.append('PIA catalogue count differs from the collection')
    if len({r['id'] for r in records}) != len(records): errors.append('Duplicate PIA catalogue IDs')
    exports, both = 0, 0
    for row in records:
        source = json.loads((ROOT / 'PIAs' / row['institution_id'] / 'collection.json').read_text())
        pia = next(p for p in source['pias'] if p['pia_id'] == row['pia_id'])
        if row['name_en'] != source['name_en'] or row['name_fr'] != source['name_fr']: errors.append(f'Incorrect legal names: {row["id"]}')
        for field in ('pib_ids','cor_ids','pib_count','cor_count','word_count','word_count_en','word_count_fr'):
            if row.get(field) != pia.get(field): errors.append(f'PIA reference/word count mismatch: {row["id"]} {field}')
        document = json.loads((site / row['content_url']).read_text())
        available = []
        for lang, item in document['languages'].items():
            original = pia['sources'][lang]
            if item['status'] != original['status']: errors.append(f'Wrong source status: {row["id"]} {lang}')
            if original['status'] == 'exported':
                available.append(lang)
                path = site / item['markdown_url']
                if hashlib.sha256(path.read_bytes()).hexdigest() != original['markdown_sha256']: errors.append(f'PIA Markdown mismatch: {path}')
                soup = BeautifulSoup(item['html'], 'html.parser')
                if soup.find(['script', 'iframe', 'form', 'object', 'embed', 'h1']): errors.append(f'Unsafe or incorrectly headed PIA HTML: {row["id"]}')
                if any(key.lower().startswith('on') for tag in soup.find_all(True) for key in tag.attrs): errors.append(f'Unsafe PIA HTML attribute: {row["id"]}')
                if not item['html'].strip(): errors.append(f'Empty rendered PIA: {row["id"]} {lang}')
            elif item['html'] is not None or item['markdown_url'] is not None: errors.append(f'Unavailable PIA exported as content: {row["id"]} {lang}')
        if sorted(row['available_languages']) != sorted(available): errors.append(f'Incorrect PIA language availability: {row["id"]}')
        exports += len(available)
        both += len(available) == 2
    with (site / 'data/privacy_assessment_index.csv').open() as handle:
        csv_index = list(csv.DictReader(handle))
    if len(csv_index) != len(records): errors.append('Assessment CSV count differs from catalogue')
    with (ROOT / 'institutions_infosource_docs/pib_table_en_fr_all.csv').open() as handle:
        pib_rows = list(csv.DictReader(handle))
    expected_institutions = {r['institution_id'] for r in pib_rows}
    actual_institutions = {r['institution_id'] for r in records if r['available_languages']} & expected_institutions
    progress = payload['summary']['progress']
    if progress['institutions_with_pibs'] != len(expected_institutions) or progress['institutions_with_pibs_and_readable_pias'] != len(actual_institutions): errors.append('Incorrect collection progress denominator/numerator')
    summary = payload['summary']
    if exports != summary['markdown_exports'] or exports != manifest['source_status_counts']['exported']: errors.append('PIA export totals do not match')
    if both != summary['availability'].get('both'): errors.append('PIA bilingual totals do not match')
    for name in ('index.html', 'table.html', 'privacy-assessments.html', 'privacy-assessment.html'):
        soup = BeautifulSoup((site / name).read_text(), 'html.parser')
        nav = soup.find('gcds-top-nav')
        if not nav or not nav.find('gcds-nav-link', href='privacy-assessments.html'): errors.append(f'PIA navigation missing on {name}')
    return errors


if __name__ == '__main__':
    errors = validate()
    if errors: raise SystemExit('\n'.join(errors))
    print('Validated PIA catalogue, rendered documents, Markdown checksums, language availability, metrics and navigation.')
