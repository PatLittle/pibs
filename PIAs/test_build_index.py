"""Offline regression checks for extraction and bounded list navigation."""
import unittest
from unittest.mock import patch
import build_index as b


class IndexTests(unittest.TestCase):
    def test_context_link_and_relative_url(self):
        text = 'TBS conducts privacy impact assessments. [Summaries of completed PIAs](/en/lists.html) are available.'
        label, url, context, _ = next(b.links(text, 'https://www.canada.ca/en/info.html'))
        self.assertEqual(url, 'https://www.canada.ca/en/lists.html')
        self.assertGreaterEqual(b.score(label, url, context), 5)

    def test_url_and_menu_mentions_are_not_pia_evidence(self):
        context = '[Info Source](/agency/pia-efvp/infosource.html) [Open data](/data)'
        self.assertEqual(b.score('Open data', '/data', context), 0)
        self.assertEqual(b.score('Privacy policy', '/policy', 'PIA summaries are available'), 0)

    def test_bilingual_navigation_labels(self):
        for label in ('Privacy Impact Assessment summaries', 'Summaries of completed PIAs',
                      'Sommaires d’évaluations des facteurs relatifs à la vie privée',
                      'Résumés des évaluations des facteurs relatifs à la vie privée (EFPV)',
                      'Annual Reports and Privacy Impact Assessments'):
            self.assertTrue(b.generic_pia_label(label), label)
        self.assertFalse(b.generic_pia_label('Privacy Impact Assessment for the payroll system'))
        self.assertFalse(b.generic_pia_label('Évaluation des facteurs relatifs à la vie privée du système X'))

    def test_navigation_stops_at_program_named_list(self):
        pages = {
            'https://example.ca/publications': '<main><h1>Publications</h1><a href="/pias">Privacy impact assessments</a></main>',
            'https://example.ca/pias': '<main><h1>Privacy impact assessments</h1><h2>2025</h2><a href="/one">Payroll</a><a href="/two">Security cards</a></main>',
        }
        def fetch(url, refresh=False):
            return dict(requested_url=url, final_url=url, http_status=200, checked_at_utc='2026-11-12T00:00:00+00:00', error='', text=b.Page(pages[url]).text)
        with patch.object(b, 'fetch', side_effect=fetch) as mocked:
            result = b.resolve({'url': 'https://example.ca/publications'})
        self.assertEqual(result['resolution'], 'list_detected')
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(result['url'], 'https://example.ca/pias')

    def test_navigation_budget_does_not_fetch_individuals(self):
        def fetch(url, refresh=False):
            number = int(url.rsplit('/', 1)[1])
            html = f'<main><h1>Publications</h1><a href="/{number + 1}">Privacy impact assessments</a><a href="/individual">Privacy impact assessment for payroll</a></main>'
            return dict(requested_url=url, final_url=url, http_status=200, checked_at_utc='now', error='', text=b.Page(html).text)
        with patch.object(b, 'fetch', side_effect=fetch) as mocked:
            result = b.resolve({'url': 'https://example.ca/0'})
        self.assertEqual(mocked.call_count, 3)
        self.assertEqual(result['resolution'], 'needs_review')
        self.assertTrue(all('/individual' not in call.args[0] for call in mocked.call_args_list))

    def test_http_failure_retained(self):
        response = dict(requested_url='https://example.ca/pias', final_url='https://example.ca/pias', http_status=403, checked_at_utc='now', error='Forbidden', text='')
        with patch.object(b, 'fetch', return_value=response):
            result = b.resolve({'url': response['requested_url']})
        self.assertEqual(result['http_status'], 403)
        self.assertEqual(result['resolution'], 'http_error')


if __name__ == '__main__': unittest.main()
