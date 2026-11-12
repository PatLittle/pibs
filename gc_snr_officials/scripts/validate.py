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
    for kind in ['travel', 'hospitality', 'dpoh']:
        records = json.loads(gzip.decompress((ROOT / 'data' / (kind + '.json.gz')).read_bytes()))
        meta = manifest['disclosures'][kind]
        assert len(records) == meta['unique_count']
        assert sum(r['record_count'] for r in records) == meta['raw_count']
        assert all(set(NAME_FIELDS) <= set(r) and r['name'] == re.sub(r'[,\.\s]', '', r['name_normalized']) for r in records)
        assert all(normalize_name(r['name_original'])['name_normalized'] == r['name_normalized'] for r in records)
    dpoh = json.loads(gzip.decompress((ROOT / 'data/dpoh.json.gz').read_bytes()))
    meta = manifest['disclosures']['dpoh']
    assert meta['joined_row_count'] == meta['raw_count'] + meta['duplicate_report_person_rows']
    assert meta['dpoh_raw_count'] == meta['joined_row_count'] + meta['orphan_row_count']
    assert meta['primary_raw_count'] == meta['primary_unique_count'] + meta['primary_duplicate_count']
    assert sum(r['source_row_count'] for r in dpoh) == meta['joined_row_count']
    assert len({(r['first_name_original'],r['last_name_original'],r['institution_original']) for r in dpoh}) == len(dpoh)
    for r in dpoh:
        assert r['source_row_count'] == r['record_count'] + r['duplicate_report_person_rows']
        assert r['detail_path'].startswith('data/dpoh_details/') and (ROOT / r['detail_path']).is_file()
        for field, date_field in [('first_record','observed_from'),('last_record','observed_to')]:
            evidence = r[field]
            if evidence:
                assert evidence['comlog_id'].isdigit()
                assert evidence['communication_date'] == r[date_field]
    detail_count = 0
    index_by_id = {r['dpoh_id']:r for r in dpoh}
    detail_files = list((ROOT / 'data/dpoh_details').glob('*.json.gz'))
    assert len(detail_files) == meta['detail_bucket_count']
    for path in detail_files:
        details = json.loads(gzip.decompress(path.read_bytes()))
        detail_count += len(details)
        for identity, detail in details.items():
            row = index_by_id[identity]
            assert row['detail_path'] == str(path.relative_to(ROOT))
            assert detail['record_count'] == row['record_count']
            assert detail['titles'] == row['titles']
            for field in ('first_record','last_record'):
                evidence = detail[field]
                if evidence:
                    assert evidence['comlog_id'] == evidence['dpoh']['COMLOG_ID']
                    assert evidence['communication_date'] == row[field]['communication_date']
                    assert 'primary' not in evidence
    assert detail_count == meta['detail_record_count'] == len(dpoh)
    assert len(meta['members']) == 2 and all(len(m['sha256']) == 64 for m in meta['members'])
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
