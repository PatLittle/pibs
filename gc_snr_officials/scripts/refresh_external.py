#!/usr/bin/env python3
"""Refresh complete disclosure dumps and build an OIC candidate-evidence index."""
import csv
import gzip
import hashlib
import io
import json
import re
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import ijson
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from names import VERSION, normalize_record, normalize_name, match_text, person_key

ROOT = Path(__file__).resolve().parents[1]
DUMPS = {
    'travel': 'https://open.canada.ca/data/en/datastore/dump/8282db2a-878f-475c-af10-ad56aa8fa72c?format=json',
    'hospitality': 'https://open.canada.ca/data/en/datastore/dump/7b301f1a-2a7a-48bd-9ea9-e0ac4a5313ed?format=json',
}


def download(url, destination):
    session = requests.Session()
    session.headers['User-Agent'] = 'GC-Senior-Officials-Transparency/1.0 (+https://github.com/PatLittle/pibs)'
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    digest, size = hashlib.sha256(), 0
    try:
        with session.get(url, stream=True, timeout=(15, 90)) as response:
            response.raise_for_status()
            with destination.open('wb') as output:
                for chunk in response.iter_content(1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
                    output.write(chunk)
        if not size:
            raise ValueError('Empty download')
        return dict(source_url=url, sha256=digest.hexdigest(), bytes=size)
    finally:
        session.close()


def write_gzip(path, value):
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    blob = gzip.compress(raw, compresslevel=9, mtime=0)
    if not path.exists() or path.read_bytes() != blob:
        temp = path.with_suffix('.gz.tmp')
        temp.write_bytes(blob)
        temp.replace(path)


def valid_date(value, today):
    if value is None or not str(value).strip():
        return '', False
    try:
        text = str(value).strip()
        parsed = date.fromisoformat(text)
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', text) or parsed < date(1900, 1, 1) or parsed > today + timedelta(days=366):
            raise ValueError('Implausible date')
        return parsed.isoformat(), False
    except ValueError:
        return '', True


def aggregate_dump(path, kind, today):
    with path.open('rb') as stream:
        fields = [f['id'] for f in ijson.items(stream, 'fields.item')]
    required = {'name', 'title_en', 'owner_org', 'owner_org_title', 'start_date', 'end_date'}
    if not required <= set(fields):
        raise ValueError('Disclosure dump has an unexpected schema')
    groups, count, anomalies = {}, 0, 0
    with path.open('rb') as stream:
        for item in ijson.items(stream, 'records.item'):
            if isinstance(item, dict):
                row = item
            elif isinstance(item, list) and len(item) == len(fields):
                row = dict(zip(fields, item))
            else:
                raise ValueError('Malformed disclosure record')
            original, title, org = (str(row.get(k) or '') for k in ['name', 'title_en', 'owner_org'])
            key = (original, title, org)
            if key not in groups:
                groups[key] = dict(**normalize_name(original), title_en=title, owner_org=org,
                                   owner_org_title=str(row.get('owner_org_title') or org), record_count=0,
                                   _source=kind, observed_from='', observed_to='', date_type='observed_range',
                                   date_anomaly_count=0, date_anomaly_examples=[])
            group = groups[key]
            group['record_count'] += 1
            count += 1
            for field in ['start_date', 'end_date']:
                value, invalid = valid_date(row.get(field), today)
                if invalid:
                    anomalies += 1
                    group['date_anomaly_count'] += 1
                    example = str(row[field])
                    if example not in group['date_anomaly_examples'] and len(group['date_anomaly_examples']) < 5:
                        group['date_anomaly_examples'].append(example)
                if value:
                    if not group['observed_from'] or value < group['observed_from']:
                        group['observed_from'] = value
                    if not group['observed_to'] or value > group['observed_to']:
                        group['observed_to'] = value
            if count % 100000 == 0:
                print(f'{kind}: {count:,} rows read', flush=True)
    if not count:
        raise ValueError('No disclosure rows; previous snapshot retained')
    records = [groups[k] for k in sorted(groups)]
    assert sum(r['record_count'] for r in records) == count
    return records, dict(raw_count=count, unique_count=len(records), date_anomaly_count=anomalies,
                         latest_observed_date=max((r['observed_to'] for r in records), default=''))


def names_from_data(root):
    names = set()
    for path in (root / 'data').glob('*.csv'):
        with path.open(encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                names.add(row.get('name_normalized') or normalize_name(row.get('name', ''))['name'])
    for kind in DUMPS:
        records = json.loads(gzip.decompress((root / 'data' / (kind + '.json.gz')).read_bytes()))
        names.update(r.get('name_normalized') or normalize_name(r.get('name', ''))['name'] for r in records)
    return sorted(n for n in names if len(match_text(n).split()) >= 2)


def build_oic_index(path, names):
    # Match complete observed normalized names, never infer surnames from prose.
    trie = {}
    for name in names:
        tokens = match_text(name).split()
        if len(tokens) < 2:
            continue
        node = trie
        for token in tokens:
            node = node.setdefault(token, {})
        node.setdefault('', set()).add(name)
    index, total, matched_orders, latest = {}, 0, set(), ''
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not {'pcNumber', 'date', 'precis', 'attachments'} <= set(reader.fieldnames or []):
            raise ValueError('OIC CSV has an unexpected schema')
        for row in reader:
            total += 1
            latest = max(latest, row['date'])
            precis = row.get('precis') or ''
            # Token positions preserve original spelling/case for matched-name evidence.
            tokens = []
            for match in re.finditer(r'[^\W_]+', precis, flags=re.UNICODE):
                token = match_text(match[0])
                if token:
                    tokens.append((token, match.start(), match.end()))
            matches = {}
            for i in range(len(tokens)):
                node, j = trie, i
                while j < len(tokens) and tokens[j][0] in node:
                    node = node[tokens[j][0]]
                    j += 1
                    for candidate in node.get('', []):
                        original = precis[tokens[i][1]:tokens[j - 1][2]]
                        evidence = normalize_name(original)
                        evidence['observed_name_normalized'] = candidate
                        matches.setdefault(person_key(candidate), {})[(original, candidate)] = evidence
            if not matches:
                continue
            attachments = json.loads(row['attachments'] or '[]')
            urls = []
            for attachment in attachments:
                identity = attachment.get('id') if isinstance(attachment, dict) else attachment
                if str(identity).isdigit():
                    urls.append('https://orders-in-council.canada.ca/attachment.php?attach=' + str(identity) + '&lang=en')
            for key, evidence in matches.items():
                index.setdefault(key, []).append(dict(pcNumber=row['pcNumber'], date=row['date'], date_type='order_date',
                    department=row.get('department', ''), precis=precis, official_urls=sorted(set(urls)),
                    matched_names=list(evidence.values())))
            matched_orders.add(row['pcNumber'])
    if not total:
        raise ValueError('Empty OIC orders CSV')
    for rows in index.values():
        rows.sort(key=lambda row: (row['date'], row['pcNumber']), reverse=True)
    return index, dict(order_count=total, matched_order_count=len(matched_orders), person_key_count=len(index), latest_order_date=latest)


def refresh(root=ROOT):
    manifest_path = root / 'data/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    today = datetime.now(timezone.utc).date()
    external_warnings = []
    # Upgrade last-good files even if their upstream is temporarily unavailable.
    for kind in DUMPS:
        path = root / 'data' / (kind + '.json.gz')
        if path.exists():
            rows = json.loads(gzip.decompress(path.read_bytes()))
            write_gzip(path, [normalize_record(row) for row in rows])
    with tempfile.TemporaryDirectory(prefix='senior-officials-') as directory:
        temp = Path(directory)
        for kind, url in DUMPS.items():
            meta = manifest['disclosures'].setdefault(kind, {})
            try:
                print(f'Downloading full {kind} dump…', flush=True)
                provenance = download(url, temp / (kind + '.json'))
                records, counts = aggregate_dump(temp / (kind + '.json'), kind, today)
                if meta.get('raw_count') and counts['raw_count'] < meta['raw_count'] * .5:
                    raise ValueError('Row count dropped by more than 50%; retained for review')
                write_gzip(root / 'data' / (kind + '.json.gz'), records)
                meta.update(provenance, **counts, last_success=today.isoformat(), status='current')
                meta.pop('error', None)
                print(f'{kind}: {counts["raw_count"]:,} rows → {counts["unique_count"]:,} combinations', flush=True)
            except Exception as exc:
                meta.setdefault('last_success', manifest['disclosures'].get('snapshot_date'))
                meta.update(status='retained_after_error', error=str(exc))
                external_warnings.append(f'{kind}: {exc}')
        meta = manifest.setdefault('oic', dict(last_success=manifest.get('oic_snapshot_date')))
        try:
            provenance = download('https://api.github.com/repos/PatLittle/oic-data/commits/main', temp / 'oic-commit.json')
            commit = json.loads((temp / 'oic-commit.json').read_text())['sha']
            url = f'https://raw.githubusercontent.com/PatLittle/oic-data/{commit}/processed-csvs/orders.csv'
            print('Downloading OIC orders CSV at ' + commit, flush=True)
            provenance = download(url, temp / 'orders.csv')
            index, counts = build_oic_index(temp / 'orders.csv', names_from_data(root))
            if not index:
                raise ValueError('No OIC name matches; previous index retained')
            if meta.get('order_count') and counts['order_count'] < meta['order_count'] * .5:
                raise ValueError('OIC row count dropped by more than 50%')
            write_gzip(root / 'data/oic.json.gz', index)
            meta.update(provenance, **counts, source_commit=commit, last_success=today.isoformat(), status='current',
                        match_method='complete observed normalized name in order precis')
            meta.pop('error', None)
            print(f'OIC: {counts["order_count"]:,} orders; {counts["matched_order_count"]:,} candidate evidence matches', flush=True)
        except Exception as exc:
            meta.update(status='retained_after_error', error=str(exc))
            external_warnings.append(f'oic: {exc}')
    # Keep legacy summary dates consistent with source-specific freshness.
    dates = [manifest['disclosures'][kind].get('last_success') for kind in DUMPS]
    manifest['disclosures']['snapshot_date'] = min(dates) if all(dates) else None
    manifest['oic_snapshot_date'] = manifest.get('oic', {}).get('last_success')
    manifest['external_last_attempt'] = today.isoformat()
    manifest['external_refresh_warnings'] = external_warnings
    manifest['name_normalization_version'] = VERSION
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for warning in external_warnings:
        print('::warning::' + warning.replace('\n', ' '))
    if external_warnings:
        print('Previous good data retained for unavailable sources; see manifest for exact freshness.')


if __name__ == '__main__':
    refresh()
