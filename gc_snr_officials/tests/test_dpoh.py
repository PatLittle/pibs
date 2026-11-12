import csv
from datetime import date
import gzip
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from refresh_dpoh import aggregate_zip, refresh, PRIMARY, DPOH, write_snapshot

PRIMARY_FIELDS = ['COMLOG_ID','COMM_DATE','PREV_COMLOG_ID_PRECEDNT','EN_CLIENT_ORG_CORP_NM_AN','POSTED_DATE_PUBLICATION']
DPOH_FIELDS = ['COMLOG_ID','DPOH_LAST_NM_TCPD','DPOH_FIRST_NM_PRENOM_TCPD','INSTITUTION','DPOH_TITLE_TITRE_TCPD','BRANCH_UNIT_DIRECTION_SERVICE','OTHER_INSTITUTION_AUTRE']


def archive(path, primary, people):
    with zipfile.ZipFile(path, 'w') as z:
        for name, fields, records in [(PRIMARY, PRIMARY_FIELDS, primary), (DPOH, DPOH_FIELDS, people)]:
            out = io.StringIO(newline='');writer = csv.DictWriter(out, fieldnames=fields);writer.writeheader()
            writer.writerows(dict(zip(fields, r)) for r in records)
            z.writestr(name, out.getvalue().encode('cp1252'))


class DPOHTests(unittest.TestCase):
    def test_join_deduplicates_report_person_roles_and_retains_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.zip'
            primary = [('2','2024-03-05','1','Client É','2025-01-01'),('1','2020-01-02','null','Client A','2026-01-01'),('3','bad','null','Client B','2022-01-01')]
            people = [('1','Bérubé','Jane','Agency','Director','null','null'),('1','Bérubé','Jane','Agency','Director','null','null'),('1','Bérubé','Jane','Agency','Adviser','Branch','null'),('2','Bérubé','Jane','Agency','Deputy','null','null'),('3','Bérubé','Jane','Agency','Deputy','null','null'),('2','Bérubé','Jane','Other agency','Chief','null','null')]
            archive(path, primary, people)
            records, meta = aggregate_zip(path, date(2026,11,12))
            self.assertEqual(meta['primary_unique_count'],3)
            self.assertEqual(meta['joined_row_count'],6)
            self.assertEqual(meta['raw_count'],4)
            self.assertEqual(meta['duplicate_report_person_rows'],2)
            self.assertEqual(meta['unique_count'],2)
            row = next(r for r in records if r['owner_org_title']=='Agency')
            self.assertEqual(row['name_normalized'],'Jane Bérubé')
            self.assertEqual(row['record_count'],3)
            self.assertEqual(row['source_row_count'],5)
            self.assertEqual((row['observed_from'],row['observed_to']),('2020-01-02','2024-03-05'))
            self.assertEqual(row['first_record']['comlog_id'],'1')
            self.assertEqual(row['last_record']['communication_date'],'2024-03-05')
            self.assertNotIn('primary',row['last_record'])
            self.assertEqual(row['date_anomaly_count'],1)
            self.assertEqual(set(row['titles']),{'Director','Adviser','Deputy'})
            self.assertEqual(row['roles'][0]['other_institution'],'')

    def test_primary_key_conflicts_and_orphans_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'data.zip';person=[('1','Able','Alice','Agency','Chief','null','null')]
            archive(path,[('1','2020-01-01','','A',''),('1','2021-01-01','','A','')],person)
            with self.assertRaisesRegex(ValueError,'Conflicting primary'):aggregate_zip(path,date(2026,11,12))
            archive(path,[('2','2020-01-01','','A','')],person)
            with self.assertRaises(ValueError):aggregate_zip(path,date(2026,11,12))

    def test_primary_export_only_requires_id_and_communication_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'data.zip'
            archive(path,[('1','2020-01-01','','Ignored client','')],[('1','Able','Alice','Agency','Chief','null','null')])
            with zipfile.ZipFile(path) as z: people=z.read(DPOH)
            with zipfile.ZipFile(path,'w') as z:
                z.writestr(PRIMARY,'COMLOG_ID,COMM_DATE\n1,2020-01-01\n')
                z.writestr(DPOH,people)
            records,_=aggregate_zip(path,date(2026,11,12))
            self.assertEqual(records[0]['first_record']['communication_date'],'2020-01-01')
            self.assertNotIn('primary',records[0]['first_record'])

    def test_duplicate_primary_row_does_not_multiply_join(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'data.zip';row=('1','2020-01-01','','A','')
            archive(path,[row,row],[('1','Able','Alice','Agency','Chief','null','null')])
            records,meta=aggregate_zip(path,date(2026,11,12))
            self.assertEqual(meta['primary_duplicate_count'],1)
            self.assertEqual(meta['primary_unique_count'],1)
            self.assertEqual(records[0]['record_count'],1)

    def test_compact_snapshot_keeps_full_joined_evidence_in_detail_bucket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();path=root/'data.zip'
            archive(path,[('1','2020-01-01','','Client','')],[('1','Able','Alice','Agency','Chief','Branch','null')])
            records,_=aggregate_zip(path,date(2026,11,12))
            counts=write_snapshot(root,records)
            index=json.loads(gzip.decompress((root/'data/dpoh.json.gz').read_bytes()))
            self.assertNotIn('primary',index[0]['first_record'])
            details=json.loads(gzip.decompress((root/index[0]['detail_path']).read_bytes()))
            self.assertEqual(details[index[0]['dpoh_id']]['first_record']['communication_date'],'2020-01-01')
            self.assertNotIn('primary',details[index[0]['dpoh_id']]['first_record'])
            self.assertEqual(counts['detail_record_count'],1)

    def test_failed_refresh_retains_last_good_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();out=root/'data/dpoh.json.gz';out.write_bytes(gzip.compress(b'[{"record_count":8}]'))
            previous=out.read_bytes();(root/'data/manifest.json').write_text(json.dumps({'disclosures':{'dpoh':{'raw_count':8,'last_success':'2020-01-01'}}}))
            with patch('refresh_dpoh.download', side_effect=RuntimeError('offline')):
                self.assertFalse(refresh(root))
            self.assertEqual(out.read_bytes(),previous)
            meta=json.loads((root/'data/manifest.json').read_text())['disclosures']['dpoh']
            self.assertEqual(meta['raw_count'],8)
            self.assertEqual(meta['last_success'],'2020-01-01')
            self.assertEqual(meta['status'],'retained_after_error')
