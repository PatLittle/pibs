"""Graph contracts against the real collection and adversarial join cases."""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.build_graph import ROOT, build, record_id, write
from scripts.public_accounts import FISCAL_YEAR, account_id
from scripts.validate_graph import validate


class GraphBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = build()
        cls.nodes = {n['id']: n for n in cls.graph['nodes']}

    def test_inventory_counts_and_source_scoped_identity(self):
        for dataset, path, key in [('pibs', 'institutions_infosource_docs/pib_table_en_fr_all.csv', 'bank_number_key'),
                                   ('classes', 'institutions_infosource_docs/cor_table_en_fr_all.csv', 'record_number'),
                                   ('standard-pibs', 'spib_en_fr.csv', 'bank_number_key')]:
            with (ROOT / path).open() as f: rows = list(csv.DictReader(f))
            for row in rows:
                self.assertIn(record_id(dataset, row.get('institution_id'), row[key]), self.nodes)
        self.assertNotEqual(record_id('pibs', 'a', 'PSU 901'), record_id('pibs', 'b', 'PSU 901'))
        self.assertNotEqual(record_id('pibs', 'a', 'PSU 901'), record_id('standard-pibs', None, 'PSU 901'))

    def test_edges_have_evidence_and_real_endpoints(self):
        ids = set()
        for edge in self.graph['edges']:
            self.assertNotIn(edge['id'], ids)
            ids.add(edge['id'])
            self.assertIn(edge['source'], self.nodes)
            target = self.nodes[edge['target']]
            self.assertTrue(edge['evidence'])
            if edge['resolution'] != 'resolved': self.assertEqual(target['type'], 'reference')
            for item in edge['evidence']:
                self.assertTrue((ROOT / item['source_path']).is_file())
                if edge['type'] == 'references' and self.nodes[edge['source']]['type'] == 'pia':
                    self.assertGreater(item['line'], 0)
                    self.assertTrue(item['excerpt'])
                    self.assertEqual(len(item['markdown_sha256']), 64)

    def test_ambiguous_pia_matches_stay_unresolved(self):
        ambiguous = [e for e in self.graph['edges'] if e['resolution'] == 'ambiguous']
        self.assertTrue(ambiguous, 'The collection contains ambiguous shared identifiers')
        for edge in ambiguous:
            self.assertEqual(self.nodes[edge['target']]['type'], 'reference')
            self.assertGreater(len(self.nodes[edge['target']]['candidates']), 1)

    def test_vocabulary_is_attributes_with_derived_evidence_preserved(self):
        self.assertFalse(any(n['type'] in ('category', 'pib_type') for n in self.nodes.values()))
        self.assertFalse(any(e['type'] in ('category_match', 'has_type') for e in self.graph['edges']))
        banks = [n for n in self.nodes.values() if n['type'] == 'pib']
        categories = [c for n in banks for c in n['attributes']['personal_information_categories']]
        self.assertTrue(categories)
        for category in categories:
            self.assertEqual(category['basis'], 'derived')
            self.assertTrue(category['label_en'])
            self.assertTrue(category['label_fr'])
            for item in category['evidence']:
                self.assertTrue(item['excerpt'])
                self.assertTrue(item['rule'])
                self.assertGreater(item['confidence'], 0)
                self.assertIn(item['field'], ['description_en', 'description_fr', 'specific_information_types_en', 'specific_information_types_fr'])
        typed = [n['attributes']['pib_type_details'] for n in banks if n['attributes']['pib_type_details']]
        self.assertTrue(typed)
        self.assertTrue(all(t['basis'] == 'documented' for t in typed))
        with (ROOT / 'spib_en_fr.csv').open() as handle:
            source = next(r for r in csv.DictReader(handle) if r['bank_number_key'] == 'PSU 905')
        self.assertTrue(all(self.nodes['pib:standard:PSU 905']['attributes'][k] == v for k, v in source.items() if v != ''))
        links = [e for e in self.graph['edges'] if e['source'] == 'pib:standard:PSU 901' and e['target'] == 'class:standard:930']
        self.assertEqual(len(links), 1)
        self.assertEqual({i['language'] for i in links[0]['evidence']}, {'en', 'fr'})

    def test_bilingual_alias_evidence_is_one_edge(self):
        ident = 'pia:ati-schedule-i-administrative-tribunals-support-service-of-canada/pia-95a42118fc3d'
        edges = [e for e in self.graph['edges'] if e['source'] == ident and e['target'] == 'pib:standard:PSU 905']
        self.assertEqual(len(edges), 1)
        self.assertEqual({e['language'] for e in edges[0]['evidence']}, {'en', 'fr'})
        self.assertEqual({e['mention'] for e in edges[0]['evidence']}, {'PSU 905', 'POU 905'})

    def test_public_accounts_bridges_same_year_service_and_infobase(self):
        entity = "Canadian Institutes of Health Research"
        chart_id = account_id(entity, "BUI01")
        info_id = f"infobase-program:{FISCAL_YEAR}:74:BUI01"
        edges = {(e["source"], e["target"], e["type"]): e for e in self.graph["edges"]}
        annual = edges["service:cihr-irsc:1121", chart_id, "reports_account_code"]
        self.assertEqual({e["fiscal_yr"] for e in annual["evidence"]}, {FISCAL_YEAR})
        self.assertEqual(annual["evidence"][0]["department_number"], "061")
        self.assertIn((chart_id, account_id(entity, "BUI00"), "account_core_responsibility"), edges)
        gc = edges[chart_id, info_id, "matches_infobase_program"]["evidence"]
        self.assertEqual({e["infobase_org_id"] for e in gc}, {"74"})
        self.assertEqual({e["department_number"] for e in gc}, {"061"})
        self.assertTrue({"federal_programs", "spending_fte"} <= {
            row["resource_kind"] for row in self.nodes[info_id]["attributes"]["infobase_resources"]
        })

    def test_accounts_keep_catalogue_matches_and_ambiguous_departments_separate(self):
        edges = self.graph["edges"]
        study_permit = [e for e in edges if e["source"] == "service:cic:1428"]
        self.assertFalse(any(e["type"] == "reports_account_code" for e in study_permit))
        self.assertTrue(any(e["type"] == "shares_account_code" and e["source"] == "program:cic:BGD02" for e in edges))

        account_nodes = [n for n in self.nodes.values() if n["type"] == "account_code"]
        ambiguous = {
            n["id"] for n in account_nodes
            if any(d["department_number"] == "096" and d["resolution"] == "ambiguous"
                   for d in n["attributes"]["department_links"])
        }
        self.assertTrue(ambiguous)
        self.assertFalse(any(e["type"] == "accounted_by" and e["source"] in ambiguous for e in edges))
        internal_services = [n for n in account_nodes if n["identifier"] == "ISS01"]
        self.assertGreater(len(internal_services), 1)
        self.assertEqual(len(internal_services), len({n["attributes"]["accounts_entity"] for n in internal_services}))

    def test_generated_assets_are_deterministic_and_shards_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Exercise serialization with actual records without copying the corpus.
            with patch('scripts.build_graph.build', side_effect=lambda _: copy.deepcopy(self.graph)):
                write(root)
                before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*.json')}
                write(root)
                self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*.json')})
            with patch('scripts.validate_graph.build', return_value=self.graph):
                validate(root)
                attribute_shard = next((root / 'site/data/graph-attributes').glob('*.json'))
                attribute_bytes = attribute_shard.read_bytes()
                attribute_shard.write_text('{}')
                with self.assertRaisesRegex(ValueError, 'Attribute checksum'):
                    validate(root)
                attribute_shard.write_bytes(attribute_bytes)
                shard = next((root / 'site/data/graph-evidence').glob('*.json'))
                shard.write_text('{}')
                with self.assertRaisesRegex(ValueError, 'checksum'): validate(root)


if __name__ == '__main__': unittest.main()
