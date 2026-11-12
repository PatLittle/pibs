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

class PiaProgressTests(unittest.TestCase):
    def test_coverage_counts_distinct_pibs_instead_of_assessment_count(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from scripts.build_pia_site import pib_progress
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'institutions_infosource_docs').mkdir()
            (root/'institutions_infosource_docs/pib_table_en_fr_all.csv').write_text('institution_id,bank_number_key\na,A PPU 001\nb,B PPU 002\n')
            row={'institution_id':'a','available_languages':['en'],'pib_count':1,'cor_count':0,'references':{'pibs':[{'matched_records':[{'dataset':'pibs','institution_id':'a','record_id':'A PPU 001'}]}]}}
            with patch('scripts.build_pia_site.ROOT',root): progress=pib_progress([row,row])
            self.assertEqual(progress['institutions_with_pibs'],2)
            self.assertEqual(progress['institutions_with_pibs_and_readable_pias'],1)
            self.assertEqual(progress['pib_records_cited'],1)
            self.assertEqual(progress['pib_reference_coverage_percent'],50.0)
