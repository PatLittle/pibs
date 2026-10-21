#!/usr/bin/env python3
"""Refresh eight public authority CSVs; retain last good files on source failures."""
import argparse
import csv
import io
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['name', 'title_en', 'owner_org_title', 'source', 'start_date', 'end_date',
          'source_date', 'date_type', 'source_url', 'appointment_date', 'original_date',
          'expiry_date', 'appointment_details']
INDEX = 'https://federal-organizations.canada.ca/gindex.php?lang=en&t=1'


def text(node):
    return ' '.join(node.get_text(' ', strip=True).split()) if node else ''


def iso(value):
    value = value.strip()
    try:
        return date.fromisoformat(value).isoformat() if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) else ''
    except ValueError:
        return ''


def key(name):
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if not unicodedata.combining(c)).lower()
    if ',' in name:
        family, given = name.split(',', 1)
        name = given + ' ' + family
    return ' '.join(re.sub(r'[^a-z0-9 -]', ' ', name).split())


def valid_person(name):
    return bool(name and any(c.isalpha() for c in name) and not iso(name)
                and name.lower() not in {'name', 'vacant', 'vacancy', 'n/a', 'tbd', 'date modified:'})


def grid(table):
    """Expand row/column spans so headers and values retain their alignment."""
    spans = {}
    for tr in table.find_all('tr'):
        if tr.find_parent('table') is not table:
            continue
        row, col = [], 0
        for cell in tr.find_all(['th', 'td'], recursive=False):
            while col in spans:
                value, left = spans[col]
                row.append(value)
                if left == 1:
                    del spans[col]
                else:
                    spans[col] = (value, left - 1)
                col += 1
            for _ in range(int(cell.get('colspan', 1))):
                value = text(cell)
                row.append(value)
                if int(cell.get('rowspan', 1)) > 1:
                    spans[col] = (value, int(cell['rowspan']) - 1)
                col += 1
        while col in spans:
            value, left = spans[col]
            row.append(value)
            if left == 1:
                del spans[col]
            else:
                spans[col] = (value, left - 1)
            col += 1
        if row:
            yield row


def parse_roles(html, source, accessed):
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for table in soup.find_all('table'):
        headers = []
        for values in grid(table):
            if any(re.search(r'\b(name|official|executive|officer)\b', c, re.I) for c in values) and any(re.search(r'organization|institution|department|committee name', c, re.I) for c in values):
                headers = [c.lower() for c in values]
                continue
            if not headers:
                continue
            def get(pattern, fallback=''):
                i = next((i for i, h in enumerate(headers) if re.search(pattern, h)), -1)
                return values[i] if 0 <= i < len(values) else fallback
            org = get(r'organization|institution|department|committee name')
            if source['id'] == 'audit-committee':
                name = ' '.join(filter(None, [get(r'first name'), get(r'last name')]))
                title = get(r'committee role', 'Member') + ' — departmental audit committee'
            else:
                name = get(r'^name$|name of|official|executive|officer')
                title = source['role']
            if not org or org.lower().startswith('date modified') or not valid_person(name):
                continue
            start, end = iso(get(r'effective|start date')), iso(get(r'expiry|end date'))
            out.append(dict(name=name, title_en=title, owner_org_title=org,
                            source='designated:' + source['id'], start_date=start, end_date=end,
                            source_date=accessed, date_type='effective_range' if start or end else 'accessed',
                            source_url=source['url']))
    # Six TBS lists publish institution/name pairs as definition lists.
    # Scope to main content so the WET Date modified footer is never a person.
    main = soup.find('main') or soup
    if source['id'] != 'audit-committee':
        for dl in main.find_all('dl'):
            for term in dl.find_all('dt', recursive=False):
                org = text(term)
                definition = term.find_next_sibling(['dt', 'dd'])
                if not definition or definition.name != 'dd' or org.lower().startswith('date modified'):
                    continue
                lines = [line.strip() for line in definition.get_text('\n', strip=True).splitlines() if line.strip()]
                name = lines[0] if lines else ''
                if org and valid_person(name):
                    out.append(dict(name=name, title_en=source['role'], owner_org_title=org,
                                    source='designated:' + source['id'], start_date='', end_date='',
                                    source_date=accessed, date_type='accessed', source_url=source['url']))
    return unique(out)


def parse_index(html, accessed):
    out = []
    for tr in BeautifulSoup(html, 'html.parser').find_all('tr'):
        cells = tr.find_all(['th', 'td'], recursive=False)
        if len(cells) < 2:
            continue
        name, org = text(cells[0]), text(cells[1])
        link = cells[1].find('a', href=re.compile(r'profil\.php'))
        if valid_person(name) and ',' in name and org and link:
            url = urljoin(INDEX, link['href'])
            if urlparse(url).hostname != 'federal-organizations.canada.ca':
                continue
            out.append(dict(name=name, title_en='Governor in Council appointee', owner_org_title=org,
                            source='appointments', source_url=url, source_date=accessed, date_type='accessed'))
    return unique(out)


def parse_profile(html):
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for table in soup.find_all('table'):
        heading = table.find_previous(['h2', 'h3', 'h4', 'h5', 'h6'])
        title = text(table.find('caption')) or text(heading) or 'Governor in Council appointee'
        headers = []
        for values in grid(table):
            if 'Name' in values:
                headers = values
                continue
            def get(pattern):
                i = next((i for i, h in enumerate(headers) if re.search(pattern, h, re.I)), -1)
                return values[i] if 0 <= i < len(values) else ''
            name = get(r'^Name$')
            if not valid_person(name) or ',' not in name:
                continue
            out.append(dict(name=name, title=title,
                            appointment_date=iso(get(r'^Current appointment date')),
                            original_date=iso(get(r'^Original appointment date')),
                            expiry_date=iso(get(r'^Current expiry date'))))
    return out


def unique(rows):
    return list({(r['name'], r['title_en'], r['owner_org_title'], r['source']): r for r in rows}.values())


def get_html(url):
    session = requests.Session()
    session.headers['User-Agent'] = 'GC-Senior-Officials-Transparency/1.0 (+https://github.com/PatLittle/pibs)'
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    try:
        r = session.get(url, timeout=(10, 30))
        r.raise_for_status()
        r.encoding = r.apparent_encoding or 'utf-8'
        html = r.text
        if 'requested URL was rejected' in html or '<title>Request Rejected' in html:
            raise ValueError('Source server rejected the request')
        return html
    finally:
        session.close()


def read_csv(path):
    if not path.exists():
        return []
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save_csv(path, rows):
    rows = sorted(rows, key=lambda r: (r['owner_org_title'].casefold(), r['name'].casefold(), r['title_en'].casefold()))
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator='\n', extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    value = buffer.getvalue()
    if not path.exists() or path.read_text(encoding='utf-8') != value:
        temp = path.with_suffix('.csv.tmp')
        temp.write_text(value, encoding='utf-8')
        temp.replace(path)


def refresh(root=ROOT):
    data_dir = root / 'data'
    manifest_path = data_dir / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    sources = json.loads((root / 'sources.json').read_text())
    accessed = datetime.now(timezone.utc).date().isoformat()
    errors = []
    for source in sources:
        meta = manifest['sources'][source['id']]
        path = data_dir / source['file']
        try:
            rows = parse_roles(get_html(source['url']), source, accessed)
            if not rows:
                raise ValueError('No valid records parsed; refusing to replace previous CSV')
            previous = read_csv(path)
            if previous and len(rows) < len(previous) * .5:
                raise ValueError('Row count dropped by more than 50%; previous CSV retained for review')
            save_csv(path, rows)
            meta.update(row_count=len(rows), last_success=accessed, status='current')
            meta.pop('error', None)
            print(f"{source['id']}: {len(rows)} records")
        except Exception as exc:
            meta.update(status='retained_after_error', error=str(exc))
            errors.append(f"{source['id']}: {exc}")
    meta = manifest['sources']['appointments']
    try:
        rows = parse_index(get_html(INDEX), accessed)
        if not rows:
            raise ValueError('Appointments index yielded no records')
        previous = read_csv(data_dir / 'appointments.csv')
        if previous and len(rows) < len(previous) * .5:
            raise ValueError('Appointments count dropped by more than 50%')
        old = {(key(r['name']), r['owner_org_title']): r for r in previous}
        urls = sorted({r['source_url'].split('#')[0] for r in rows})
        profiles, profile_errors = {}, []
        with ThreadPoolExecutor(max_workers=6) as pool:
            work = {pool.submit(get_html, url): url for url in urls}
            for completed, future in enumerate(as_completed(work), 1):
                if completed % 20 == 0:
                    print(f'Appointment profiles: {completed}/{len(urls)} retrieved', flush=True)
                url = work[future]
                try:
                    parsed = parse_profile(future.result())
                    if not parsed:
                        raise ValueError('No appointment records parsed')
                    profiles[url] = parsed
                except Exception as exc:
                    profile_errors.append(f'{url}: {exc}')
        for r in rows:
            url = r['source_url'].split('#')[0]
            details = [a for a in profiles.get(url, []) if key(a['name']) == key(r['name'])]
            if not details and url not in profiles:
                prior = old.get((key(r['name']), r['owner_org_title']), {})
                details = json.loads(prior.get('appointment_details') or '[]')
            if details:
                r['title_en'] = ' / '.join(dict.fromkeys(a['title'] for a in details))
                r['appointment_details'] = json.dumps(details, ensure_ascii=False, separators=(',', ':'))
                for field in ['appointment_date', 'original_date', 'expiry_date']:
                    r[field] = '; '.join(sorted({a[field] for a in details if a[field]}))
        save_csv(data_dir / 'appointments.csv', rows)
        meta.update(row_count=len(rows), last_success=accessed, status='current' if not profile_errors else 'partial_profiles',
                    profile_count=len(urls), profile_failures=profile_errors)
        meta.pop('error', None)
        errors.extend(profile_errors)
        print(f'appointments: {len(rows)} records; {len(profiles)}/{len(urls)} profiles parsed')
    except Exception as exc:
        meta.update(status='retained_after_error', error=str(exc))
        errors.append(f'appointments: {exc}')
    manifest['last_attempt'] = accessed
    manifest['refresh_warnings'] = errors
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for error in errors:
        print('::warning::' + error.replace('\n', ' '))
    # A first deployment must include appointments; later failures retain last good data.
    if not read_csv(data_dir / 'appointments.csv'):
        raise RuntimeError('No appointment CSV is available; first refresh must succeed before deployment')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    refresh(parser.parse_args().root)
