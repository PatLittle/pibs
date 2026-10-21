import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from names import normalize_name, normalize_record, person_key
from refresh_external import aggregate_dump, build_oic_index


class Names(unittest.TestCase):
    def test_orders_initials_accents_and_prefixes(self):
        cases = {
            'Bérubé, Paul-Claude': 'Paul-Claude Bérubé',
            'Smith, John A. B.': 'John A. B. Smith',
            'de la Cruz, María J.': 'María J. de la Cruz',
            '(MGen) Radiff, Francis': 'Francis Radiff',
            'Smith, Dr. Jane': 'Jane Smith',
            'Smith, John, Jr.': 'John Smith',
            'Smith Jr., John A.': 'John A. Smith',
            'Major, David': 'David Major',
            'M. Jean Smith': 'M. Jean Smith',
            'Émilie McDonald': 'Émilie McDonald',
        }
        for original, expected in cases.items():
            with self.subTest(original=original):
                result = normalize_name(original)
                self.assertEqual(result['name_original'], original)
                self.assertEqual(result['name_normalized'], expected)
                self.assertEqual(normalize_record(result), result)
        self.assertEqual(normalize_name('(MGen) Radiff, Francis')['name_prefix'], '(MGen)')
        self.assertEqual(normalize_name('Smith, John, Jr.')['name_suffix'], 'Jr.')
        self.assertEqual(normalize_name('Smith, John, Jane')['name_normalization_review'], 'true')
        self.assertEqual(normalize_name(None)['name'], '')
        self.assertEqual(person_key('Jane Smith-Jones'), 'jane|smith-jones')


class Disclosure(unittest.TestCase):
    def test_array_and_object_rows_counts_originals_and_invalid_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'dump.json'
            fields = ['name', 'title_en', 'owner_org', 'owner_org_title', 'start_date', 'end_date']
            records = [['Smith, Jane A.', 'Chief', 'abc', 'Agency', '2020-01-01', '2020-01-03'],
                       ['Smith, Jane A.', 'Chief', 'abc', 'Agency', '9999-01-01', 'bad'],
                       ['Jane A. Smith', 'Chief', 'abc', 'Agency', '2021-01-01', None],
                       ['', '', 'abc', 'Agency', '', '']]
            path.write_text(json.dumps(dict(fields=[dict(id=f) for f in fields], records=records)))
            rows, meta = aggregate_dump(path, 'travel', date(2026, 10, 21))
            self.assertEqual(meta['raw_count'], 4)
            self.assertEqual(meta['unique_count'], 3)
            self.assertEqual(meta['date_anomaly_count'], 2)
            original = next(r for r in rows if r['name_original'] == 'Smith, Jane A.')
            self.assertEqual(original['name'], 'Jane A. Smith')
            self.assertEqual(original['record_count'], 2)
            self.assertEqual(original['observed_to'], '2020-01-03')
            path.write_text(json.dumps(dict(fields=[dict(id=f) for f in fields], records=[dict(zip(fields, records[0]))])))
            self.assertEqual(aggregate_dump(path, 'travel', date(2026, 10, 21))[1]['raw_count'], 1)

    def test_failed_refresh_keeps_last_good_counts_and_dates(self):
        import gzip
        from unittest.mock import patch
        from refresh_external import refresh
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            meta = dict(disclosures=dict(snapshot_date='2020-01-01', travel=dict(raw_count=2, unique_count=1), hospitality=dict(raw_count=2, unique_count=1)), oic_snapshot_date='2020-01-01')
            (root / 'data/manifest.json').write_text(json.dumps(meta))
            for kind in ['travel', 'hospitality']:
                (root / 'data' / (kind + '.json.gz')).write_bytes(gzip.compress(json.dumps([dict(name='Able, Alice', record_count=2)]).encode()))
            (root / 'data/oic.json.gz').write_bytes(gzip.compress(b'{"alice|able":[{"pcNumber":"2020-0001"}]}'))
            with patch('refresh_external.download', side_effect=RuntimeError('network unavailable')):
                refresh(root)
            manifest = json.loads((root / 'data/manifest.json').read_text())
            self.assertEqual(manifest['disclosures']['travel']['raw_count'], 2)
            self.assertEqual(manifest['disclosures']['travel']['last_success'], '2020-01-01')
            self.assertEqual(manifest['disclosures']['travel']['status'], 'retained_after_error')
            self.assertEqual(json.loads(gzip.decompress((root / 'data/travel.json.gz').read_bytes()))[0]['name_normalized'], 'Alice Able')

    def test_oic_full_names_boundaries_and_links(self):
        import csv
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'orders.csv'
            with path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['pcNumber', 'date', 'precis', 'attachments'])
                writer.writeheader()
                writer.writerow(dict(pcNumber='2026-0001', date='2026-01-01', precis='Appointment of JANE A. SMITH, of Ottawa. Not Jane A. Smithson.', attachments='[123]'))
                writer.writerow(dict(pcNumber='2026-0002', date='2026-01-02', precis='A mention of Jane and an unrelated Smith.', attachments='[]'))
            index, meta = build_oic_index(path, ['Jane A. Smith', 'Jane Smith'])
            self.assertEqual(meta['order_count'], 2)
            self.assertEqual(meta['matched_order_count'], 1)
            self.assertEqual(len(index['jane|smith']), 1)
            evidence = index['jane|smith'][0]
            self.assertEqual(evidence['matched_names'][0]['name_original'], 'JANE A. SMITH')
            self.assertEqual(evidence['official_urls'], ['https://orders-in-council.canada.ca/attachment.php?attach=123&lang=en'])
