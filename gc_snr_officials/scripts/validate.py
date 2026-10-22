#!/usr/bin/env python3
"""Check the standalone payload and its committed datasets without network access."""
import argparse
import csv
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from names import NAME_FIELDS, normalize_name

ROOT = Path(__file__).resolve().parents[1]


def validate(require_appointments=False):
    sources = json.loads((ROOT / 'sources.json').read_text())
    assert len(sources) == 7
    manifest = json.loads((ROOT / 'data/manifest.json').read_text())
    for source in sources + [dict(id='appointments', file='appointments.csv')]:
        path = ROOT / 'data' / source['file']
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            assert {'name', 'title_en', 'owner_org_title', 'source', 'source_date', 'source_url', *NAME_FIELDS} <= set(reader.fieldnames)
            rows = list(reader)
        assert len(rows) == manifest['sources'][source['id']]['row_count'], source['file']
        if require_appointments or source['id'] != 'appointments':
            assert rows, source['file']
        for row in rows:
            assert row['name'] == re.sub(r'[,\.\s]', '', row['name_normalized'])
            assert normalize_name(row['name_original'])['name_normalized'] == row['name_normalized']
            assert row['name'] and row['owner_org_title'] != 'Date modified:'
            json.loads(row.get('appointment_details') or '[]')
    for kind in ['travel', 'hospitality']:
        records = json.loads(gzip.decompress((ROOT / 'data' / (kind + '.json.gz')).read_bytes()))
        meta = manifest['disclosures'][kind]
        assert len(records) == meta['unique_count']
        assert sum(r['record_count'] for r in records) == meta['raw_count']
        assert all(set(NAME_FIELDS) <= set(r) and r['name'] == re.sub(r'[,\.\s]', '', r['name_normalized']) for r in records)
        assert all(normalize_name(r['name_original'])['name_normalized'] == r['name_normalized'] for r in records)
    index = json.loads(gzip.decompress((ROOT / 'data/oic.json.gz').read_bytes()))
    assert index
    if manifest.get('oic', {}).get('status') == 'current':
        assert all(row.get('matched_names') for rows in index.values() for row in rows)
        assert all(set(NAME_FIELDS) <= set(n) for rows in index.values() for row in rows for n in row['matched_names'])
    matches = json.loads(gzip.decompress((ROOT / 'data/matches.json.gz').read_bytes()))
    assert len(matches['links']) == manifest['identity_matching']['pairs']
    assert all(0 <= l['score'] <= 95 and l['a'] != l['b'] and l['reasons'] and len(l['evidence']) == 2 for l in matches['links'])
    html = (ROOT / 'index.html').read_text()
    js = (ROOT / 'app.js').read_text()
    assert 'href="./styles.css"' in html and re.search(r'src="\./app\.js(?:\?[^"]*)?"', html)
    assert '/api/' not in js and 'chatgpt.site' not in js
    assert all((ROOT / p).exists() for p in ['index.html', 'styles.css', 'app.js', 'sources.json'])
    print('Standalone payload, eight CSV schemas, snapshot counts and local paths validated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-appointments', action='store_true')
    validate(parser.parse_args().require_appointments)
