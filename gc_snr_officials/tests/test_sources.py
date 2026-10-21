import csv
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('refresh_sources', ROOT / 'scripts/refresh_sources.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

INDEX = '<table><tr><th>Name</th><th>Organizations</th></tr><tr><td>Able, Alice</td><td><a href="profil.php?OrgID=ABC&amp;lang=en">Agency</a></td></tr></table><table><tr><td>2026-01-01</td><td>Date modified:</td></tr></table>'
PROFILE = '''<h3>Appointments</h3><table><caption>Chair</caption><tr><th>Name</th><th>Current appointment date<br>(YYYY-MM-DD)</th><th>Current Expiry date</th><th>Original appointment date</th></tr><tr><th scope="row">Able, Alice</th><td>2026-01-01</td><td>2029-01-01</td><td>2020-01-01</td></tr></table>'''
ROLE = '<table><tr><th>Organization</th><th>Name</th></tr><tr><td>Agency</td><td>Alice Able</td></tr></table>'
AUDIT = '''<table><tr><th>Committee name</th><th>First Name</th><th>Last Name</th><th>Committee role</th><th>Effective date</th><th>Expiry date</th></tr><tr><td rowspan="2">Agency</td><td>Alice</td><td>Able</td><td>Chair</td><td>2020-01-01</td><td>2026-12-31</td></tr><tr><td>Bob</td><td>Baker</td><td>Member</td><td>2022-01-01</td><td>2027-01-01</td></tr></table>'''


class Parsers(unittest.TestCase):
    def test_index_excludes_footer(self):
        rows = r.parse_index(INDEX, '2026-10-21')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['source_url'], 'https://federal-organizations.canada.ca/profil.php?OrgID=ABC&lang=en')

    def test_profile_dates_and_heading(self):
        row = r.parse_profile(PROFILE)[0]
        self.assertEqual(row['title'], 'Chair')
        self.assertEqual(row['appointment_date'], '2026-01-01')
        self.assertEqual(row['original_date'], '2020-01-01')
        self.assertEqual(row['expiry_date'], '2029-01-01')
        self.assertEqual(r.iso('2026-02-30'), '')

    def test_roles_and_audit_rowspans(self):
        sources = json.loads((ROOT / 'sources.json').read_text())
        self.assertEqual(r.parse_roles(ROLE, sources[0], '2026-10-21')[0]['name'], 'Alice Able')
        rows = r.parse_roles(AUDIT, sources[1], '2026-10-21')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]['owner_org_title'], 'Agency')
        self.assertEqual(rows[1]['start_date'], '2022-01-01')

    def test_definition_lists_exclude_date_footer(self):
        source = json.loads((ROOT / 'sources.json').read_text())[0]
        html = '<main><dl><dt>Agency</dt><dd>Alice Able<br/>Director</dd><dt>Other</dt><dd>Vacant</dd></dl><dl><dt>Date modified:</dt><dd>2026-10-21</dd></dl></main>'
        rows = r.parse_roles(html, source, '2026-10-21')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Alice Able')
        self.assertEqual(rows[0]['owner_org_title'], 'Agency')

    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.csv'
            r.save_csv(path, [dict(name='Émilie "A", Able', title_en='Director\nChief', owner_org_title='Agency', source='test')])
            row = r.read_csv(path)[0]
            self.assertEqual(row['name'], 'Émilie "A", Able')
            self.assertEqual(row['title_en'], 'Director\nChief')

    def test_refresh_and_retain_last_good(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            sources = json.loads((ROOT / 'sources.json').read_text())
            (root / 'sources.json').write_text(json.dumps(sources))
            manifest = {'sources': {s['id']: dict(file=s['file'], row_count=0) for s in sources}}
            manifest['sources']['appointments'] = dict(file='appointments.csv', row_count=0)
            (root / 'data/manifest.json').write_text(json.dumps(manifest))
            def html(url):
                if 'gindex' in url:
                    return INDEX
                if 'profil' in url:
                    return PROFILE
                if 'appointed-members' in url:
                    return AUDIT
                return ROLE
            with patch.object(r, 'get_html', side_effect=html):
                r.refresh(root)
            before = (root / 'data/appointments.csv').read_bytes()
            self.assertIn(b'2020-01-01', before)
            with patch.object(r, 'get_html', side_effect=RuntimeError('upstream unavailable')):
                r.refresh(root)
            self.assertEqual((root / 'data/appointments.csv').read_bytes(), before)
            self.assertEqual(json.loads((root / 'data/manifest.json').read_text())['sources']['appointments']['status'], 'retained_after_error')


if __name__ == '__main__':
    unittest.main()
