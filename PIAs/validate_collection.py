#!/usr/bin/env python3
"""Validate organization metadata, paired exports, raw bytes and aggregate counts."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    index = list(csv.DictReader((ROOT / 'index.csv').open()))
    manifest = json.loads((ROOT / 'collection_manifest.json').read_text())
    assert manifest['source_index_sha256'] == digest(ROOT / 'index.csv'), 'stale source index'
    assert manifest['collector_sha256'] == digest(ROOT / 'collect_content.py'), 'stale collector version'
    totals, count, paired, populated = Counter(), 0, 0, 0
    for org in index:
        folder = ROOT / org['institution_id']
        assert len(list(folder.glob('*.json'))) == 1, folder
        data = json.loads((folder / 'collection.json').read_text())
        assert data['institution_id'] == org['institution_id']
        assert data['source_index_sha256'] == manifest['source_index_sha256']
        assert len({p['pia_id'] for p in data['pias']}) == len(data['pias'])
        expected, statuses = set(), Counter()
        for page in data['list_pages'].values():
            for capture in page['captures']:
                if capture['raw_path']:
                    assert digest(folder / capture['raw_path']) == capture['sha256']
        for pia in data['pias']:
            assert pia['pairing_status'] == ('paired' if len(pia['sources']) == 2 else 'missing_counterpart')
            for lang, source in pia['sources'].items():
                assert lang in ('en', 'fr')
                assert source['url'] == pia['url_' + lang]
                assert source['status'] != 'pending'
                statuses[source['status']] += 1
                if source['raw_path']:
                    assert digest(folder / source['raw_path']) == source['http']['sha256']
                if source['kind'] == 'inline':
                    assert '#' in source['url'] and source['anchor']
                if source['status'] == 'exported':
                    assert source['http']['http_status'] == 200 and not source['http']['error']
                    relative = source['markdown_path']
                    assert relative.endswith('_' + lang + '.md')
                    path = folder / relative
                    assert digest(path) == source['markdown_sha256']
                    text = path.read_text()
                    assert text.startswith('---\n')
                    assert len(text.split('\n---\n', 1)[1].strip()) >= 180
                    assert source['word_count'] > 0 and pia['title_' + lang]
                    expected.add(relative)
                else:
                    assert source['markdown_path'] is None
        assert expected == {p.name for p in folder.glob('pia-*_??.md')}, f'stale or missing exports: {folder}'
        summary = dict(pia_count=len(data['pias']), paired_count=sum(p['pairing_status'] == 'paired' for p in data['pias']), source_status_counts=dict(statuses))
        assert summary == data['summary'] == manifest['organizations'][org['institution_id']]
        count += summary['pia_count']
        paired += summary['paired_count']
        populated += bool(summary['pia_count'])
        totals.update(statuses)
    assert manifest['organization_count'] == len(index)
    assert manifest['pia_count'] == count and manifest['paired_count'] == paired
    assert manifest['organizations_with_pias'] == populated
    assert manifest['source_status_counts'] == dict(totals)
    print(json.dumps(dict(organizations=len(index), organizations_with_pias=populated, pia_entries=count, paired_entries=paired, source_status_counts=dict(totals)), indent=2))
    print('Validated all organization JSON, source statuses, raw/Markdown checksums, language suffixes and manifest totals.')


if __name__ == '__main__': validate()
