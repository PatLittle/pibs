"""Independent schema, source coverage and offline-rebuild checks."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'site/document-studio'

class DocumentStudioTests(unittest.TestCase):
    def test_schema_is_standard_json_schema_and_example_is_bilingual_and_valid(self):
        schema=json.loads((APP/'templates/document.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        validator=Draft202012Validator(schema,format_checker=FormatChecker())
        example=json.loads((APP/'examples/organization-chart.json').read_text())
        self.assertEqual(list(validator.iter_errors(example)),[])
        example['payload']['people'][0]['position_title']['fr']=''
        self.assertTrue(list(validator.iter_errors(example)))
        example=json.loads((APP/'examples/organization-chart.json').read_text())
        example['payload']['people'][0]['programs']=[]
        self.assertTrue(list(validator.iter_errors(example)))

    def test_every_official_word_form_has_english_and_french_sources_and_source_hashes(self):
        source=json.loads((APP/'templates/sources.json').read_text())
        word=[s for s in source['sources'] if s['url'].endswith('.docx')]
        self.assertEqual(len(word),10)
        for row in source['sources']:
            self.assertEqual(len(row['sha256']),64)
            self.assertTrue(row['url'].startswith('https://www.canada.ca/'))
        forms=json.loads((APP/'templates/forms.json').read_text())
        for kind,langs in forms['forms'].items():
            self.assertEqual(len(langs['en']),len(langs['fr']),kind)
            for en,fr in zip(langs['en'],langs['fr']):self.assertEqual(len(en['blocks']),len(fr['blocks']))
        self.assertEqual(source['counts'],dict(internal_groups=11,standard_classes=33,standard_pibs=49))
        self.assertTrue(source['link_exceptions'],'Preserve legacy-link differences rather than hiding them')

    def test_atip_provenance_and_bundled_pdf_assets(self):
        atip=json.loads((APP/'templates/atip.json').read_text())
        self.assertEqual(len(atip['register']),13)
        self.assertEqual(len(atip['sources']),16)
        for source in atip['sources']:
            self.assertEqual(len(source['sha256']),64)
            self.assertTrue(source['url'].startswith('https://www.canada.ca/'))
        for asset in json.loads((APP/'vendor/manifest.json').read_text()):
            content=(APP/asset['path']).read_bytes()
            self.assertEqual(len(content),asset['bytes'])
            self.assertEqual(hashlib.sha256(content).hexdigest(),asset['sha256'])

    def test_offline_template_build_is_deterministic(self):
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (APP/'templates').glob('*.json')}
        subprocess.run([sys.executable,str(APP/'tools/build_templates.py')],cwd=ROOT,check=True,capture_output=True)
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (APP/'templates').glob('*.json')})

    def test_feature_is_self_contained_and_only_linked_in_main_site_footers(self):
        for p in ROOT.glob('site/*.html'):
            soup=BeautifulSoup(p.read_text(),'html.parser')
            for a in soup.select('a[href="document-studio/"]'):self.assertIsNotNone(a.find_parent('footer'),str(p))
        index=BeautifulSoup((ROOT/'site/index.html').read_text(),'html.parser')
        self.assertIsNotNone(index.select_one('footer a[href="document-studio/"]'))
        own=BeautifulSoup((APP/'index.html').read_text(),'html.parser')
        for element,attribute in [('script','src'),('link','href')]:
            for node in own.find_all(element):
                value=node.get(attribute,'')
                self.assertFalse(value.startswith(('http:','https:','../')),value)
                if value:self.assertTrue((APP/value).exists(),value)

if __name__=='__main__':unittest.main()
