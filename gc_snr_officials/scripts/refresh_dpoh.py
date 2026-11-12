#!/usr/bin/env python3
"""Join the OCL communications ZIP and aggregate exact DPOH/institution observations."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import shutil
import tempfile
import zipfile

from names import normalize_name, VERSION
from refresh_external import download, valid_date, write_gzip

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://lobbycanada.gc.ca/media/mqbbmaqk/communications_ocl_cal.zip'
PRIMARY = 'Communication_PrimaryExport.csv'
DPOH = 'Communication_DpohExport.csv'
PERSON_FIELDS = ('DPOH_LAST_NM_TCPD', 'DPOH_FIRST_NM_PRENOM_TCPD', 'INSTITUTION')
ROLE_FIELDS = ('DPOH_TITLE_TITRE_TCPD', 'BRANCH_UNIT_DIRECTION_SERVICE', 'OTHER_INSTITUTION_AUTRE')


def nullable(value):
    return '' if value is None or value.strip().lower() == 'null' else value


def read_member(archive, member, required):
    # OCL publishes these CSVs in Windows-1252, not UTF-8.
    with io.TextIOWrapper(archive.open(member), encoding='cp1252', newline='') as stream:
        reader = csv.DictReader(stream)
        if not required <= set(reader.fieldnames or []):
            raise ValueError(f'Unexpected schema in {member}')
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'Malformed row in {member}')
            yield row


def aggregate_zip(path, today):
    groups, stats = {}, Counter()
    with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory(prefix='dpoh-join-') as directory:
        # A disk-backed PK prevents a many-to-many multiplication and detects
        # conflicting primary IDs before any snapshot is replaced.
        db = sqlite3.connect(str(Path(directory) / 'reports.sqlite'))
        db.execute('CREATE TABLE reports (id TEXT PRIMARY KEY, comm_date TEXT NOT NULL)')
        for row in read_member(archive, PRIMARY, {'COMLOG_ID', 'COMM_DATE'}):
            stats['primary_raw_count'] += 1
            identity = row['COMLOG_ID'].strip()
            if not identity.isdigit():
                raise ValueError('Blank or nonnumeric primary COMLOG_ID')
            comm_date = row['COMM_DATE']
            previous = db.execute('SELECT comm_date FROM reports WHERE id=?', (identity,)).fetchone()
            if previous:
                if previous[0] != comm_date:
                    raise ValueError(f'Conflicting primary COMLOG_ID {identity}')
                stats['primary_duplicate_count'] += 1
                continue
            db.execute('INSERT INTO reports VALUES (?,?)', (identity, comm_date))
            stats['primary_unique_count'] += 1
        db.commit()
        if not stats['primary_unique_count']:
            raise ValueError('Empty primary export')
        for row in read_member(archive, DPOH, {'COMLOG_ID', *PERSON_FIELDS, *ROLE_FIELDS}):
            stats['dpoh_raw_count'] += 1
            identity = row['COMLOG_ID'].strip()
            primary = db.execute('SELECT comm_date FROM reports WHERE id=?', (identity,)).fetchone()
            if not primary:
                stats['orphan_row_count'] += 1
                continue
            stats['joined_row_count'] += 1
            key = tuple(nullable(row[field]) for field in PERSON_FIELDS)
            last, first, institution = key
            if key not in groups:
                original = f'{last}, {first}' if last and first else last or first
                groups[key] = dict(**normalize_name(original), first_name_original=first, last_name_original=last,
                    owner_org='', owner_org_title=institution, institution_original=institution, title_en='',
                    _source='dpoh', source='dpoh', source_url=SOURCE_URL, date_type='communication_date',
                    record_count=0, source_row_count=0, duplicate_report_person_rows=0,
                    observed_from='', observed_to='', date_anomaly_count=0, date_anomaly_examples=[],
                    first_record=None, last_record=None, _ids=set(), _roles={})
            group = groups[key]
            group['source_row_count'] += 1
            role = tuple(nullable(row[field]) for field in ROLE_FIELDS)
            group['_roles'].setdefault(role, set()).add(identity)
            if identity in group['_ids']:
                stats['duplicate_report_person_rows'] += 1
                group['duplicate_report_person_rows'] += 1
                continue
            group['_ids'].add(identity)
            group['record_count'] += 1
            stats['raw_count'] += 1
            communication_date = primary[0]
            value, invalid = valid_date(nullable(communication_date), today)
            if invalid:
                group['date_anomaly_count'] += 1
                stats['date_anomaly_count'] += 1
                if len(group['date_anomaly_examples']) < 5 and communication_date not in group['date_anomaly_examples']:
                    group['date_anomaly_examples'].append(communication_date)
            if not value:
                stats['missing_or_invalid_date_count'] += 1
                continue
            evidence = dict(comlog_id=identity, communication_date=value, dpoh=row)
            sort_key = (value, int(identity))
            for field, choose in [('first_record', min), ('last_record', max)]:
                previous = group[field]
                if previous is None or choose(sort_key, (previous['communication_date'], int(previous['comlog_id']))) == sort_key:
                    group[field] = evidence
            group['observed_from'] = group['first_record']['communication_date']
            group['observed_to'] = group['last_record']['communication_date']
        db.close()
        if not stats['raw_count']:
            raise ValueError('No joined DPOH observations; retain previous snapshot')
        if stats['orphan_row_count']:
            # An incomplete join cannot silently publish misleading counts/windows.
            raise ValueError(f"{stats['orphan_row_count']} DPOH rows have no primary COMLOG_ID")
        members = []
        for member in (PRIMARY, DPOH):
            digest = hashlib.sha256()
            with archive.open(member) as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            members.append(dict(file=member, bytes=archive.getinfo(member).file_size, sha256=digest.hexdigest(), encoding='windows-1252'))
    records = []
    for key in sorted(groups):
        group = groups[key]
        del group['_ids']
        group['roles'] = [dict(title_en=role[0], branch_unit=role[1], other_institution=role[2], record_count=len(ids))
                          for role, ids in sorted(group.pop('_roles').items(), key=lambda item: (-len(item[1]), item[0]))]
        group['titles'] = list(dict.fromkeys(r['title_en'] for r in group['roles'] if r['title_en']))
        group['title_en'] = group['titles'][0] if group['titles'] else ''
        records.append(group)
    for field in ('primary_duplicate_count','duplicate_report_person_rows','orphan_row_count','date_anomaly_count','missing_or_invalid_date_count'):
        stats.setdefault(field, 0)
    stats = dict(stats)
    stats.update(unique_count=len(records), earliest_observed_date=min((r['observed_from'] for r in records if r['observed_from']), default=''),
                 latest_observed_date=max((r['observed_to'] for r in records), default=''), members=members,
                 join_key='COMLOG_ID', grouping_fields=list(PERSON_FIELDS),
                 count_definition='Distinct COMLOG_ID per exact source first name + last name + institution; role variants do not multiply counts',
                 revision_policy='All distinct COMLOG_ID values retained; primary export used only for COMM_DATE; no inferred revision-chain collapse')
    assert sum(r['record_count'] for r in records) == stats['raw_count']
    assert stats['joined_row_count'] == stats['raw_count'] + stats['duplicate_report_person_rows']
    return records, dict(stats)


def write_snapshot(root, records):
    """Keep the searchable index small; full joined boundaries load on demand."""
    buckets, index = {}, []
    for record in records:
        identity = json.dumps([record['last_name_original'], record['first_name_original'], record['institution_original']], ensure_ascii=False, separators=(',', ':'))
        dpoh_id = hashlib.sha256(identity.encode()).hexdigest()[:24]
        bucket = dpoh_id[:2]
        buckets.setdefault(bucket, {})[dpoh_id] = dict(record, dpoh_id=dpoh_id)
        summary = {k:v for k,v in record.items() if k not in ('roles','first_record','last_record')}
        summary.update(dpoh_id=dpoh_id, detail_path=f'data/dpoh_details/{bucket}.json.gz')
        for field in ('first_record', 'last_record'):
            summary[field] = {k:record[field][k] for k in ('comlog_id','communication_date')} if record[field] else None
        index.append(summary)
    data = root / 'data'
    with tempfile.TemporaryDirectory(prefix='.dpoh-publish-', dir=data) as directory:
        stage = Path(directory); details = stage / 'details'; details.mkdir()
        for bucket, values in sorted(buckets.items()):
            write_gzip(details / (bucket+'.json.gz'), values)
        write_gzip(stage / 'index.json.gz', index)
        destination = data / 'dpoh_details'
        backup = stage / 'previous'
        if destination.exists(): destination.rename(backup)
        try:
            details.rename(destination)
            (stage / 'index.json.gz').replace(data / 'dpoh.json.gz')
        except Exception:
            if destination.exists(): shutil.rmtree(destination)
            if backup.exists(): backup.rename(destination)
            raise
    return dict(detail_bucket_count=len(buckets), detail_record_count=len(records), detail_layout='SHA-256 exact last/first/institution prefix buckets; full joined first/last communication evidence')


def refresh(root=ROOT, zip_file=None):
    manifest_path = root / 'data/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    today = datetime.now(timezone.utc).date()
    meta = manifest.setdefault('disclosures', {}).setdefault('dpoh', {})
    try:
        with tempfile.TemporaryDirectory(prefix='ocl-communications-') as directory:
            path = Path(zip_file) if zip_file else Path(directory) / 'communications.zip'
            if zip_file:
                provenance = dict(source_url=SOURCE_URL, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size,
                                  capture_method='local_archive', processed_at_utc=datetime.now(timezone.utc).isoformat())
            else:
                provenance = dict(**download(SOURCE_URL, path), capture_method='http_get')
            records, counts = aggregate_zip(path, today)
            if meta.get('raw_count') and counts['raw_count'] < meta['raw_count'] * .5:
                raise ValueError('Joined count dropped by more than 50%; retained for review')
            detail_counts = write_snapshot(root, records)
            meta.update(provenance, **counts, **detail_counts, status='current', last_success=today.isoformat())
            meta.pop('error', None)
            manifest['dpoh_refresh_warnings'] = []
            print(f"DPOH: {counts['primary_unique_count']:,} primary reports; {counts['dpoh_raw_count']:,} DPOH rows → {counts['raw_count']:,} report/person observations → {len(records):,} exact DPOH/institution groups")
    except Exception as exc:
        meta.update(status='retained_after_error', error=str(exc))
        manifest['dpoh_refresh_warnings'] = [str(exc)]
        print('::warning::DPOH: ' + str(exc).replace('\n', ' '))
    meta['last_attempt'] = today.isoformat()
    manifest['name_normalization_version'] = VERSION
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return meta['status'] == 'current'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip-file', type=Path, help='Replay a locally downloaded official ZIP; no network request.')
    refresh(zip_file=parser.parse_args().zip_file)
