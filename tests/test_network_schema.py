import csv
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from scripts.build_network_schema import ROOT, build

class NetworkSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=json.loads((ROOT/'site/data/network-schema.json').read_text())
        cls.tables={t['id']:t for t in cls.actual['tables']}
    def test_every_canonical_csv_column_is_present_even_when_empty(self):
        model=json.loads((ROOT/'data_model.json').read_text())
        for name,table in model['tables'].items():
            with (ROOT/table['path']).open() as f: fields=next(csv.reader(f))
            self.assertEqual(fields,[f['name'] for f in self.tables[name]['fields']])
        self.assertEqual(model['graph_projection']['schema_version'],3)
        self.assertNotIn('category',model['graph_projection']['node_types'])
    def test_svg_contains_every_table_and_field_without_omissions(self):
        svg=ET.fromstring((ROOT/'site/data/network-schema.svg').read_text())
        groups={g.attrib['data-table']:g for g in svg.iter() if 'data-table' in g.attrib}
        self.assertEqual(set(groups),set(self.tables))
        for name,t in self.tables.items():
            fields=[n.attrib['data-field'] for n in groups[name].iter() if 'data-field' in n.attrib]
            self.assertEqual(fields,[f['name'] for f in t['fields']])
        for r in self.actual['relationships']:
            self.assertIn(r['source'],self.tables);self.assertIn(r['target'],self.tables)
    def test_external_aia_is_schema_only_and_has_required_fields(self):
        fields={f['name'] for f in self.tables['aia_answers']['fields']}
        self.assertTrue({'ADMresponsible','projectDetailsDepartment-NS','aboutDataSource12'}<=fields)
        self.assertIn('version',{f['name'] for f in self.tables['aia_source']['fields']})
        self.assertIn('impact_level',{f['name'] for f in self.tables['aia_derived']['fields']})
        for t in self.tables.values():
            for field in t['fields']:self.assertEqual(set(field),{'name','types'})
        self.assertEqual(len(self.actual['external_source']['sha256']),64)
    def test_offline_rebuild_is_current_and_preserves_external_schema_without_a_copy(self):
        self.assertEqual(build(),self.actual)
    def test_projection_fields_cover_all_base_node_shapes_and_graph_manifest(self):
        graph=json.loads((ROOT/'site/data/graph.json').read_text())
        for node in graph['nodes']:
            fields={f['name'] for f in self.tables['node_'+node['type']]['fields']}
            self.assertTrue(set(node)<=fields)
        self.assertTrue(set(graph)<={f['name'] for f in self.tables['graph_manifest']['fields']}|{'nodes','edges'})

if __name__=='__main__':unittest.main()
