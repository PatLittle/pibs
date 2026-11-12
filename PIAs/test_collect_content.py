"""Offline checks for PIA boundaries, bilingual pairing and export failures."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import collect_content as c


def response(url, html, status=200):
    data = html.encode()
    return dict(requested_url=url, final_url=url, http_status=status, content_type='text/html; charset=utf-8',
                encoding='utf-8', checked_at_utc='2026-11-12T00:00:00+00:00', error=None,
                byte_count=len(data), sha256=c.sha(data), redirects=[]), data


class CollectTests(unittest.TestCase):
    def test_list_range_does_not_cross_wrapper_into_tapi_or_reports(self):
        html = '''<main><h1>Publications</h1><div><h2>Privacy Impact Assessment summaries</h2>
        <ul><li><a href="/pay">Payroll</a></li></ul></div><div>
        <h2>Technology Assessment for Privacy Implications summaries</h2><ul><li><a href="/technology">New technology</a></li></ul>
        <h2>Annual reports</h2><a href="/annual">Annual report</a></div></main>'''
        records, _ = c.discover(*response('https://example.ca/list', html), 'en')
        self.assertEqual([r['url'] for r in records], ['https://example.ca/pay'])

    def test_aside_headings_are_content_and_related_links_are_excluded(self):
        html = '''<main><h1>Annual reports and Privacy Impact Assessments</h1><aside><h2>Privacy Impact Assessments</h2></aside>
        <ul><li><a href="/pay">Payroll</a></li></ul><aside><h2>Related links</h2></aside>
        <ul><li><a href="/library">Library and Archives</a></li></ul></main>'''
        records, _ = c.discover(*response('https://example.ca/list', html), 'en')
        self.assertEqual([r['title'] for r in records], ['Payroll'])

    def test_numbered_inline_summaries_are_independent_and_have_text_anchors(self):
        prose = '<p>' + ('Personal information is protected under this program. ' * 12) + '</p>'
        html = '<main><h1>Privacy impact assessments</h1>' + ''.join(
            f'<h2>{n}. September 2025</h2><h3>Title</h3><p>Program {n}</p><h3>Description</h3>{prose}' for n in (1, 2)) + '</main>'
        records, _ = c.discover(*response('https://example.ca/list', html), 'en')
        self.assertEqual(len(records), 2)
        self.assertEqual([r['title'] for r in records], ['Program 1', 'Program 2'])
        self.assertTrue(all(r['anchor_type'] == 'text_fragment' for r in records))
        self.assertNotIn('Program 2', records[0]['html'])
        self.assertEqual(c.inline_pair_key(records[0]), ('numbered_date', '1', '2025', '09'))

    def test_native_inline_anchor_is_retained(self):
        html = '<main><h1>Privacy impact assessments</h1><h2 id="pay">Payroll</h2><p>' + 'Protected data in the payroll program. ' * 20 + '</p></main>'
        records, _ = c.discover(*response('https://example.ca/list', html), 'en')
        self.assertEqual(records[0]['url'], 'https://example.ca/list#pay')
        self.assertEqual(records[0]['anchor_type'], 'native_id')

    def test_bilingual_pairs_use_urls_instead_of_position(self):
        en = 'https://example.ca/pay-eng.html'
        fr = 'https://example.ca/pay-fra.html'
        records = [{'url': en, 'language': 'en', 'kind': 'page'}, {'url': 'https://example.ca/other-fr.html', 'language': 'fr', 'kind': 'page'}, {'url': fr, 'language': 'fr', 'kind': 'page'}]
        results = {r['url']: response(r['url'], '<html><main>PIA</main></html>') for r in records}
        groups = c.pair_records(records, results)
        pair = next(group for group, _, _ in groups if 'en' in group)
        self.assertEqual(pair['fr']['url'], fr)
        self.assertEqual(len(groups), 2)

    def test_reverse_language_switch_can_pair_a_document(self):
        en, fr = 'https://example.ca/pay', 'https://example.ca/paie'
        records = [{'url': en, 'language': 'en', 'kind': 'page'}, {'url': fr, 'language': 'fr', 'kind': 'page'}]
        results = {en: response(en, '<html><main>Payroll</main></html>'), fr: response(fr, '<html><a lang="en" href="/pay">English</a><main>Paie</main></html>')}
        groups = c.pair_records(records, results)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0][1], 'explicit_language_link')

    def test_http_and_soft_errors_do_not_become_markdown(self):
        for status, title, expected in ((403, 'Forbidden', 'http_error'), (200, 'Not Found', 'soft_error_page'), (200, 'Errors / Erreur', 'soft_error_page')):
            url = 'https://example.ca/error'
            result = response(url, f'<html lang="en"><main><h1>{title}</h1><p>Some error page content</p></main></html>', status)
            record = {'url': url, 'title': 'Payroll PIA', 'kind': 'page', 'discovery_method': 'pia_section_link'}
            with tempfile.TemporaryDirectory() as temp, patch.object(c, 'persist_raw', return_value=None):
                source = c.export_source(Path(temp), 'pia-test', record, 'en', {url: result})
                self.assertEqual(source['status'], expected)
                self.assertIsNone(source['markdown_path'])
                self.assertEqual(list(Path(temp).glob('*.md')), [])


if __name__ == '__main__': unittest.main()

class ReviewedListLayoutTests(unittest.TestCase):
    def test_summary_section_preferred_and_program_titles_not_filtered_as_navigation(self):
        html = '''<main><h1>Privacy assessments</h1><h2>Privacy impact assessment</h2><p>General explanation.</p>
        <h2>Privacy assessment summaries</h2><ul>
        <li><a href="/assessments/contact">Contact Centre Program</a></li>
        <li><a href="/assessments/passport">Passport Guarantor Policy and Directive on Loss of Citizenship</a></li>
        <li><a href="/directive">Directive on PIAs</a></li></ul></main>'''
        records,_=c.discover(*response('https://example.canada.ca/list',html),'en')
        self.assertEqual([r['url'] for r in records],['https://example.canada.ca/assessments/contact','https://example.canada.ca/assessments/passport'])

    def test_french_cra_summary_heading(self):
        html='''<main><h1>Sommaires d’évaluations des facteurs relatifs à la vie privée</h1><h2>Évaluation des facteurs relatifs à la vie privée</h2><p>Introduction.</p>
        <h2>Sommaires d’évaluations de la protection de la vie privée</h2><ul><li><a href="/evaluation/prestations">Prestations</a></li></ul></main>'''
        records,_=c.discover(*response('https://example.canada.ca/liste',html),'fr')
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['title'],'Prestations')
