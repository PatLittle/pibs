"""Graph contracts against the real collection and adversarial join cases."""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.build_graph import ROOT, build, record_id, write
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
                if edge['type'] == 'references':
                    self.assertGreater(item['line'], 0)
                    self.assertTrue(item['excerpt'])
                    self.assertEqual(len(item['markdown_sha256']), 64)

    def test_ambiguous_pia_matches_stay_unresolved(self):
        ambiguous = [e for e in self.graph['edges'] if e['resolution'] == 'ambiguous']
        self.assertTrue(ambiguous, 'The collection contains ambiguous shared identifiers')
        for edge in ambiguous:
            self.assertEqual(self.nodes[edge['target']]['type'], 'reference')
            self.assertGreater(len(self.nodes[edge['target']]['candidates']), 1)

    def test_bilingual_alias_evidence_is_one_edge(self):
        ident = 'pia:ati-schedule-i-administrative-tribunals-support-service-of-canada/pia-95a42118fc3d'
        edges = [e for e in self.graph['edges'] if e['source'] == ident and e['target'] == 'pib:standard:PSU 905']
        self.assertEqual(len(edges), 1)
        self.assertEqual({e['language'] for e in edges[0]['evidence']}, {'en', 'fr'})
        self.assertEqual({e['mention'] for e in edges[0]['evidence']}, {'PSU 905', 'POU 905'})

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
                shard = next((root / 'site/data/graph-evidence').glob('*.json'))
                shard.write_text('{}')
                with self.assertRaisesRegex(ValueError, 'checksum'): validate(root)


if __name__ == '__main__': unittest.main()
