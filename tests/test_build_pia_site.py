import unittest
from bs4 import BeautifulSoup
from scripts.build_pia_site import sanitized_html, record_type


class PiaSiteTests(unittest.TestCase):
    def test_markdown_tables_headings_and_frontmatter(self):
        html = sanitized_html('---\ntitle: "Example"\n---\n# Payroll\n\n| Risk | Mitigation |\n|---|---|\n| Access | Controls |\n')
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(soup.h2.text, 'Payroll')
        self.assertIsNone(soup.h1)
        self.assertIsNotNone(soup.table)
        self.assertNotIn('title:', html)

    def test_source_html_cannot_add_active_content(self):
        html = sanitized_html('''# Summary
<script>alert(1)</script><iframe src="https://example.ca"></iframe>
<form><input name="sensitive"></form><p onclick="alert(1)">Body</p>
<a href="javascript:alert(1)">Bad</a><a href="https://example.ca">Good</a>
<img src="data:text/html,evil" onerror="alert(1)" alt="Example">''')
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIsNone(soup.find(['script', 'iframe', 'form', 'input']))
        self.assertNotIn('onclick', html)
        self.assertNotIn('onerror', html)
        self.assertNotIn('javascript:', html)
        self.assertNotIn('data:text', html)
        self.assertEqual(soup.find('a', href=True)['href'], 'https://example.ca')

    def test_related_evaluations_are_not_renamed_pias(self):
        row = {'title_en': 'Quarantine privacy compliance evaluation', 'title_fr': None, 'sources': {}}
        self.assertEqual(record_type(row), 'Privacy compliance evaluation')
        row = {'title_en': 'Program homepage', 'title_fr': None, 'sources': {'en': {'status': 'not_pia_content'}}}
        self.assertEqual(record_type(row), 'Source requires review')


if __name__ == '__main__': unittest.main()
