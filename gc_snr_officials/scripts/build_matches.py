#!/usr/bin/env python3
"""Build explainable pairwise nickname candidates; never merge identities transitively."""
import argparse
import csv
import gzip
import hashlib
import io
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from names import VERSION, match_text, normalize_record, person_key

ROOT = Path(__file__).resolve().parents[1]
NICKNAME_URL = 'https://raw.githubusercontent.com/carltonnorthern/nicknames/master/names.csv'


def nickname_lookup(rows):
    parents = defaultdict(set)
    edges = set()
    for row in rows:
        if row.get('relationship') != 'has_nickname':
            continue
        a, b = match_text(row['name1']), match_text(row['name2'])
        if a and b:
            parents[b].add(a)
            edges.add(frozenset((a, b)))
    return parents, edges


def relation(a, b, lookup):
    parents, edges = lookup
    if frozenset((a, b)) in edges:
        return 'direct nickname', 60
    if parents[a] & parents[b]:
        return 'shared canonical given name', 55
    return None


def window(r):
    # Access/snapshot and expiry dates are not evidence of concurrent employment.
    values = [r.get('observed_from'), r.get('observed_to'), r.get('start_date'), r.get('end_date')]
    for a in r.get('appointment_details') or []:
        values += [a.get('original_date'), a.get('appointment_date')]
    valid = []
    for value in values:
        try:
            valid.append(date.fromisoformat(value))
        except (TypeError, ValueError):
            pass
    return (min(valid), max(valid)) if valid else None


def label(value):
    return match_text((value or '').split('|')[0])


def role_overlap(a, b):
    a, b = set(label(a).split()), set(label(b).split())
    return bool(a and b and len(a & b) / len(a | b) >= .65)


def score_pair(a, b, kind, base):
    best = (-100, [], [])
    for x in a:
        for y in b:
            same_org = bool(label(x.get('owner_org_title')) and label(x.get('owner_org_title')) == label(y.get('owner_org_title')))
            same_role = role_overlap(x.get('title_en'), y.get('title_en'))
            points = 18 * same_org + 17 * same_role
            reasons = [f'{kind}: +{base}', 'Same family-name token (candidate block)']
            reasons += ['Shared observed institution: +18' if same_org else 'Different or missing institution labels: +0']
            reasons += ['Matching / similar observed role: +17' if same_role else 'Different or missing role labels: +0']
            wx, wy = window(x), window(y)
            if wx and wy:
                overlap = max(wx[0], wy[0]) <= min(wx[1], wy[1])
                if overlap and (same_org or same_role):
                    points += 5
                    reasons.append('Overlapping observations with shared institution or role: +5')
                elif overlap:
                    reasons.append('Overlapping disclosure windows across different roles/institutions: +0; event ranges do not establish continuous tenure')
                else:
                    gap = (max(wx[0], wy[0]) - min(wx[1], wy[1])).days
                    increment = 10 if gap <= 5 * 366 else 5
                    points += increment
                    reasons.append(f'Non-overlapping event windows ({gap} days apart): +{increment}; compatible with a career transition, not proof')
            else:
                reasons.append('Event dates missing; access dates excluded: +0')
            if points > best[0]:
                best = points, reasons, [dict(name=r['name_normalized'], institution=r.get('owner_org_title', ''), role=r.get('title_en', ''), first=str(window(r)[0]) if window(r) else '', last=str(window(r)[1]) if window(r) else '', source=r.get('source', ''), source_url=r.get('source_url', '')) for r in (x, y)]
    # Check middle names across all forms. Missing middle names are neutral.
    def middles(rows):
        return {tuple(match_text(r['name_normalized']).split()[1:-1]) for r in rows} - {()}
    ma, mb = middles(a), middles(b)
    compatible = any(len(x) == len(y) and all(u == v or (min(len(u), len(v)) == 1 and u[0] == v[0]) for u, v in zip(x, y)) for x in ma for y in mb)
    conflict = bool(ma and mb and not compatible)
    score = base + best[0] + (-30 if conflict else 5 if compatible else 0)
    reasons = best[1] + (['Conflicting middle names: −30; score capped at 49'] if conflict else ['Compatible middle names/initials: +5'] if compatible else ['Missing middle-name evidence: +0'])
    return dict(score=max(0, min(49 if conflict else 95, score)), reasons=reasons, evidence=best[2],
                level='review' if conflict or score < 60 else 'strong' if score >= 80 else 'probable')


def build(records, lookup):
    groups = defaultdict(list)
    for r in records:
        if r.get('name_normalized') and r.get('name_normalization_review') != 'true':
            groups[person_key(r['name_normalized'])].append(r)
    families = defaultdict(list)
    for key in groups:
        if '|' in key:
            families[key.split('|')[-1]].append(key)
    links = []
    for keys in families.values():
        for i, a in enumerate(sorted(keys)):
            for b in sorted(keys)[i + 1:]:
                rel = relation(a.split('|')[0], b.split('|')[0], lookup)
                if rel:
                    links.append(dict(a=a, b=b, **score_pair(groups[a], groups[b], *rel)))
    return links


def write_gzip(path, value):
    path.write_bytes(gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode(), mtime=0))


def run(root=ROOT, refresh=False):
    data = root / 'data'
    manifest = json.loads((data / 'manifest.json').read_text())
    nickpath = data / 'nicknames.csv'
    if refresh:
        import requests
        try:
            response = requests.get(NICKNAME_URL, timeout=90)
            response.raise_for_status()
            rows = list(csv.DictReader(io.StringIO(response.text)))
            if len(rows) < 1000 or not all({'name1', 'relationship', 'name2'} <= r.keys() for r in rows):
                raise ValueError('Unexpected nickname schema or count')
            nickpath.write_text(response.text, encoding='utf-8')
            manifest['nicknames'] = dict(status='current', last_success=date.today().isoformat())
        except Exception as exc:
            if not nickpath.exists():
                raise
            manifest.setdefault('nicknames', {})['status'] = 'retained_after_error'
            manifest['nicknames']['error'] = str(exc)
    rows = list(csv.DictReader(nickpath.open(encoding='utf-8-sig', newline='')))
    rows += list(csv.DictReader((data / 'nickname-supplements.csv').open(encoding='utf-8', newline='')))
    records = []
    # Also migrate retained datasets so every deployment has the same schema.
    for source in json.loads((root / 'sources.json').read_text()) + [dict(file='appointments.csv')]:
        path = data / source['file']
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            authority = [normalize_record(r) for r in reader]
        for r in authority:
            details = [normalize_record(x) for x in json.loads(r.get('appointment_details') or '[]')]
            r['appointment_details'] = json.dumps(details, ensure_ascii=False, separators=(',', ':'))
            records.append(dict(r, appointment_details=details))
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(authority)
    for kind in ['travel', 'hospitality']:
        path = data / (kind + '.json.gz')
        observations = [normalize_record(r) for r in json.loads(gzip.decompress(path.read_bytes()))]
        write_gzip(path, observations)
        records += observations
    path = data / 'oic.json.gz'
    index = json.loads(gzip.decompress(path.read_bytes()))
    for values in index.values():
        for row in values:
            if row.get('matched_names'):
                row['matched_names'] = [normalize_record(n) for n in row['matched_names']]
    write_gzip(path, index)
    links = build(records, nickname_lookup(rows))
    write_gzip(data / 'matches.json.gz', dict(version=1, links=links))
    manifest['name_normalization_version'] = VERSION
    manifest.setdefault('nicknames', {}).update(url=NICKNAME_URL, sha256=hashlib.sha256(nickpath.read_bytes()).hexdigest(), relationship_rows=len(rows)-1)
    manifest['identity_matching'] = dict(version=1, pairs=len(links), method='Pairwise nickname candidates with institution, role, middle-name and event-window evidence; no automatic merges')
    (data / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(links)} pairwise nickname candidates from {len(records)} source combinations')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-nicknames', action='store_true')
    run(refresh=parser.parse_args().refresh_nicknames)
