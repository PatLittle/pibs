import unittest
from reference_extraction import extract, enrich_assessment

ORG = 'ati-schedule-i-treasury-board-secretariat'


class ReferenceTests(unittest.TestCase):
    def ids(self, text, kind='pibs', lang='en'):
        return {r['id']:r for r in extract(text, ORG, lang, 'fixture.md')[kind]}

    def test_bilingual_bank_and_standard_cor_ids(self):
        self.assertIn('TBS PCE 754', self.ids('SCT PCE 754', lang='fr'))
        self.assertIn('PSE 901', self.ids('POE 901', lang='fr'))
        refs = self.ids('PRN 946; NDP 946', 'classes_of_records')
        self.assertEqual(set(refs), {'PRN 946'})
        self.assertEqual(refs['PRN 946']['evidence'][1]['mention'], 'NDP 946')

    def test_ids_in_urls_and_frontmatter_do_not_inflate_mentions(self):
        text = '---\nsource_url: https://example.gc.ca/#PPU901\n---\n[DFO PPU 460](https://example.gc.ca/#:~:text=DFO%20PPU%20065)'
        refs = self.ids(text)
        self.assertEqual(set(refs), {'DFO PPU 460'})
        self.assertEqual(refs['DFO PPU 460']['evidence'][0]['line'], 4)

    def test_years_phones_and_assessment_file_numbers_are_not_cors(self):
        text = 'Numéro de dossier des services de l’AIPRP: PIA-2021-00006\nAIPRP 343-542-5195\nClass of records: S.C. 2007, COVID 19'
        self.assertEqual(self.ids(text, 'classes_of_records'), {})

    def test_known_and_unknown_explicit_cor_ids_are_kept(self):
        refs = self.ids('Class of Record SSC TS 400\nRelated Class of Record number: CNSC 1.5.4', 'classes_of_records')
        self.assertIn('SSC TS 400', refs)
        self.assertIn('CNSC 1.5.4', refs)

    def test_pdf_line_wrapped_codes_are_recovered(self):
        refs = self.ids('Standard PIB PSE\n902')
        self.assertEqual(set(refs), {'PSE 902'})
        self.assertEqual(refs['PSE 902']['evidence'][0]['line'], 1)
        self.assertEqual(set(self.ids('Class of Record PRN\n946', 'classes_of_records')), {'PRN 946'})

    def test_repeated_mentions_count_once_and_have_evidence(self):
        refs = self.ids('PSE 902\nPSE 902\nPSE 902')
        self.assertEqual(len(refs), 1)
        self.assertEqual(len(refs['PSE 902']['evidence']), 3)

    def test_bare_institution_specific_id_not_assigned_to_an_arbitrary_department(self):
        refs = self.ids('PPU 999')
        self.assertEqual(set(refs), {'PPU 999'})
        self.assertEqual(refs['PPU 999']['matched_records'], [])


if __name__ == '__main__': unittest.main()

class EnrichmentTests(unittest.TestCase):
    def test_counts_deduplicate_languages_and_words_are_not_added_together(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import reference_extraction as module
        module.holdings()  # Load the real lookup before temporarily changing the evidence root.
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / ORG
            folder.mkdir()
            (folder/'test_en.md').write_text('PSE 902 and PRN 946')
            (folder/'test_fr.md').write_text('POE 902 et NDP 946')
            pia = {'sources': {lang:{'status':'exported','markdown_path':f'test_{lang}.md','word_count':count} for lang,count in [('en',10),('fr',12)]}}
            with patch.object(module, 'ROOT', Path(temp)):
                result = enrich_assessment(pia,folder)
            self.assertEqual(result['pib_ids'],['PSE 902'])
            self.assertEqual(result['pib_count'],1)
            self.assertEqual(result['cor_ids'],['PRN 946'])
            self.assertEqual(result['cor_count'],1)
            self.assertEqual(result['word_count'],10)
            self.assertEqual(result['word_count_fr'],12)
            self.assertEqual({e['language'] for e in result['references']['pibs'][0]['evidence']},{'en','fr'})
