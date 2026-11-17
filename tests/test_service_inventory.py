"""Reject false joins while retaining source observations and unresolved IDs."""
import copy
import csv
import hashlib
import json
import unittest
from pathlib import Path
from scripts.import_service_inventory import normalize, tokens
from scripts.build_graph import build

ROOT=Path(__file__).resolve().parents[1]

class ServiceInventoryTests(unittest.TestCase):
    def fixture(self):
        schema={'resources':[{'resource_name':'service','fields':[{'id':'program_id','choices':{
            'ISS00':{'en':'Internal services','fr':'Services internes','valid_orgs':{'one':['2024-2025'],'two':[]}},
            'OTHER':{'en':'Other','fr':'Autre','valid_orgs':{'two':[]}}}}]}]}
        rows=[dict(owner_org='one',owner_org_title='One',fiscal_yr='2023-2024',service_id='001',program_id='ISS00, ISS00, ISS00-INV, OTHER, UNKNOWN',program_name_en='Wrong positional name'),dict(owner_org='two',owner_org_title='Two',fiscal_yr='2024-2025',service_id='001',program_id='ISS00',program_name_en='Another name')]
        standards=[dict(owner_org='one',fiscal_yr='2023-2024',service_id='001',service_standard_id='1')]
        registry=[dict(open_canada_org_slug='one',institution_id='institution-one')]
        return schema,rows,standards,registry

    def test_repeated_codes_are_literal_and_zeroes_survive(self):
        self.assertEqual(tokens('{"001",ISS00}'),['001','ISS00'])
        self.assertEqual(tokens('["001", "ISS00"]'),['001','ISS00'])
        self.assertEqual(tokens(''),[])

    def test_scoped_programs_use_real_rows_and_invalid_markers_stay_unresolved(self):
        owners,programs,links,refs=normalize(*self.fixture())
        self.assertEqual({(r['owner_org'],r['program_id']) for r in programs},{('one','ISS00'),('two','ISS00')})
        self.assertEqual(len(links),2)
        self.assertEqual({r['program_id']:r['resolution'] for r in refs if r['owner_org']=='one'},dict(ISS00='resolved',**{'ISS00-INV':'invalid_suffix','OTHER':'owner_not_listed','UNKNOWN':'unknown_code'}))
        old=next(r for r in links if r['owner_org']=='one')
        self.assertEqual(old['vocabulary_year_status'],'not_listed_in_current_choice_snapshot')
        self.assertTrue(all(r['name_en']=='Internal services' for r in programs))
        self.assertEqual(next(r for r in owners if r['owner_org']=='two')['institution_id'],'')

    def test_duplicate_and_orphan_annual_keys_reject_import(self):
        args=list(self.fixture());args[1]=args[1]+[copy.deepcopy(args[1][0])]
        with self.assertRaisesRegex(ValueError,'duplicate key'):normalize(*args)
        for field,value in [('owner_org','two'),('fiscal_yr','2024-2025'),('service_id','1')]:
            args=list(self.fixture());args[2][0][field]=value
            with self.assertRaisesRegex(ValueError,'Orphan'):normalize(*args)

    def test_ambiguous_organization_mapping_does_not_choose_a_candidate(self):
        args=list(self.fixture());args[3].append(dict(open_canada_org_slug='one',institution_id='other'))
        owners,_,_,_=normalize(*args)
        row=next(r for r in owners if r['owner_org']=='one')
        self.assertEqual(row['resolution'],'ambiguous');self.assertEqual(row['institution_id'],'')

    def test_snapshot_hashes_and_all_seventy_field_dispositions(self):
        directory=ROOT/'data/service_inventory';m=json.loads((directory/'manifest.json').read_text())
        for path,sha in m['outputs'].items():self.assertEqual(hashlib.sha256((directory/path).read_bytes()).hexdigest(),sha,path)
        audit=json.loads((directory/'field_join_audit.json').read_text())
        self.assertEqual(len(audit),70);self.assertEqual(len({(r['resource'],r['field']) for r in audit}),70)
        schema=json.loads((directory/'schema_fields.json').read_text())
        for resource in schema['resources']:
            with (directory/(resource['resource_name']+'.csv')).open() as f:header=next(csv.reader(f))
            self.assertEqual(header,[f['id'] for f in resource['fields']])

    def test_real_graph_connects_service_program_standards_with_annual_evidence(self):
        graph=build();nodes={n['id']:n for n in graph['nodes']};service=nodes['service:cic:1428']
        self.assertEqual(len([n for n in nodes.values() if n['type']=='service']),1879)
        self.assertEqual(len([n for n in nodes.values() if n['type']=='program']),648)
        link=next(e for e in graph['edges'] if e['source']==service['id'] and e['target']=='program:cic:BGD02')
        self.assertEqual(link['type'],'under_program');self.assertTrue(all(r['fiscal_yr'] for r in link['evidence']))
        self.assertTrue(any(e['source']==service['id'] and e['type']=='has_standard' for e in graph['edges']))
        years={r['fiscal_yr']:r for r in service['attributes']['annual_observations']}
        self.assertEqual(years['2023-2024']['automated_decision_system'],'N')
        self.assertEqual(years['2024-2025']['automated_decision_system'],'Y')
        discrepancy=nodes['service:dfo-mpo:1036']
        self.assertEqual(discrepancy['owner_org'],'dfo-mpo')
        self.assertTrue(discrepancy['attributes']['identifier_catalog_exceptions'])
        self.assertTrue(all(r['catalog_owners']==['dnd-mdn'] for r in discrepancy['attributes']['identifier_catalog_exceptions']))
        for edge in graph['edges']:
            if edge['type']=='under_program':self.assertFalse(nodes[edge['target']]['identifier'].endswith('-INV'))
        for n in nodes.values():
            if n['type']=='service' and n['owner_org'] in ('fja-cmf','cas-satj','cics-scic'):self.assertIsNone(n['institution_id'])

if __name__=='__main__':unittest.main()
