#!/usr/bin/env python3
"""Extract explicit PIB/CoR identifiers from preserved assessment Markdown."""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = 1
PIB_TOKEN = re.compile(r'(?<![A-Z0-9])(PPU|PPE|PCE|PCU|PSE|PSU|POE|POU)[\s._:\-]*(\d{2,6})(?!\d)', re.I)
STANDARD_COR = re.compile(r'(?<![A-Z0-9])(PRN|NDP)[\s\[\]():._\-]*(\d{3})(?!\d)', re.I)
COR_CONTEXT = re.compile(r'class(?:es)? of records?|\bcor\b|related record|record number|categorie[s]? de documents|catégorie[s]? de documents|numéro de (?:dossier|document)|numéro.*(?:catégorie|categorie)|document connexe|dossier connexe', re.I)
GENERIC_ID = re.compile(r'\b[A-Z][A-Z&./-]{1,14}(?:\s+[A-Z][A-Z0-9&./-]{0,14}){0,2}[\s:-]+\d{1,6}(?:[.-]\d{1,4})*\b')
TYPE_ALIAS = {'POE':'PSE', 'POU':'PSU'}


def key(value):
    value = re.sub(r'[^A-Z0-9]', '', value.upper())
    return re.sub(r'(PPU|PPE|PCE|PCU|PSE|PSU|POE|POU)(\d{2,3})$', lambda m:m[1]+m[2].zfill(3), value)
def rows(path): return list(csv.DictReader(io.StringIO(path.read_text())))
def normalized(value): return re.sub(r'\s+', ' ', value.replace('\xa0', ' ')).strip()


@lru_cache(maxsize=1)
def holdings():
    data = {'pibs': defaultdict(list), 'classes_of_records': defaultdict(list)}
    prefixes = defaultdict(set)
    registry_prefixes = {}
    cor_labels = set()
    for institution in rows(ROOT / 'institution_registry.csv'):
        en, fr = institution['abbreviation'], institution['abreviation']
        if en and fr:
            prefixes[fr.upper()].add(en.upper())
            registry_prefixes[fr.upper()] = en.upper()
    for row in rows(ROOT / 'institutions_infosource_docs/pib_table_en_fr_all.csv'):
        match = {'dataset': 'pibs', 'institution_id': row['institution_id'], 'record_id': row['bank_number_key']}
        en_prefix = re.match(r'^([A-Z]+)\s+P[A-Z]{2}', row['bank_number_key'])
        fr_prefix = re.match(r'^([A-Z]+)\s+P[A-Z]{2}', row['bank_number_fr'])
        if en_prefix and fr_prefix: prefixes[fr_prefix[1]].add(en_prefix[1])
        for label in {row['bank_number_key'], row['bank_number_en'], row['bank_number_fr']} - {''}:
            data['pibs'][key(label)].append(match)
    for row in rows(ROOT / 'spib_en_fr.csv'):
        match = {'dataset':'standard-pibs', 'institution_id':None, 'record_id':row['bank_number_key']}
        for label in {row['bank_number_key'], row['bank_number_en'], row['bank_number_fr'], row['entry_id_en'], row['entry_id_fr']} - {''}:
            data['pibs'][key(label)].append(match)
    for row in rows(ROOT / 'institutions_infosource_docs/cor_table_en_fr_all.csv'):
        if not re.search(r'[A-Za-z]', row['record_number']): continue
        match = {'dataset':'classes', 'institution_id':row['institution_id'], 'record_id':row['record_number']}
        data['classes_of_records'][key(row['record_number'])].append(match)
        cor_labels.add(row['record_number'])
    for row in rows(ROOT / 'standard_classes_of_records_en_fr.csv'):
        match = {'dataset':'standard-classes', 'institution_id':None, 'record_id':row['record_number']}
        for label in (row['record_number_en'], row['record_number_fr']):
            data['classes_of_records'][key(label)].append(match)
            cor_labels.add(label)
    data['prefix_aliases'] = {alias:next(iter(variants)) for alias,variants in prefixes.items() if len(variants) == 1}
    # Current bilingual registry abbreviations take precedence over historical
    # acronym variants when an otherwise unmatched identifier is normalized.
    data['prefix_aliases'].update(registry_prefixes)
    # Historical department names refer to the same legal institution.
    data['prefix_aliases'].update({'PWGSC':'PSPC','TPSGC':'PSPC'})
    for ident, matches in list(data['pibs'].items()):
        match = re.fullmatch(r'([A-Z]+)(PPU|PPE|PCE|PCU|PSE|PSU|POE|POU)(\d+)', ident)
        if match:
            alias = data['prefix_aliases'].get(match[1],match[1]) + TYPE_ALIAS.get(match[2],match[2]) + match[3]
            data['pibs'][alias].extend(matches)
    for mapping in (data['pibs'], data['classes_of_records']):
        for ident, matches in mapping.items():
            mapping[ident] = list({(m['dataset'], m['institution_id'], m['record_id']): m for m in matches}.values())
    # Recover French CoR aliases from the already-joined bilingual holding
    # titles and the preserved French source; require a unique exact title.
    sys.path.insert(0, str(ROOT))
    from build_cor_table_from_markdown import parse_records
    french_titles = defaultdict(list)
    for row in rows(ROOT / 'institutions_infosource_docs/cor_table_en_fr_all.csv'):
        if row['name_fr']:
            french_titles[(row['institution_id'], normalized(row['name_fr']).casefold())].append({'dataset':'classes','institution_id':row['institution_id'],'record_id':row['record_number']})
    for path in (ROOT / 'institutions_infosource_docs').glob('*/classes_of_records_fr.md'):
        for record in parse_records(path.read_text()):
            matches = french_titles.get((path.parent.name, normalized(record['name']).casefold()), [])
            if len({m['record_id'] for m in matches}) == 1 and re.search('[A-Za-z]',record['record_number']):
                data['classes_of_records'][key(record['record_number'])].extend(matches)
                cor_labels.add(record['record_number'])
    # Scan identifier-shaped spans and validate their suffixes in the lookup.
    # This avoids a thousands-of-alternatives regex at every text position.
    data['cor_pattern'] = re.compile(r'(?<![A-Za-z0-9])(?:[A-Za-z][A-Za-z&./-]{0,18}[\s:#/-]*){1,4}\d{1,7}(?:[.-]\d{1,4})*(?![A-Za-z0-9])')
    return data


def visible_lines(markdown):
    # Ignore collector front matter and link destinations, particularly text-
    # fragment URLs that may contain incidental identifiers outside the citation.
    front = re.match(r'\A---\r?\n.*?\r?\n---\r?\n', markdown, flags=re.S)
    offset = markdown[:front.end()].count('\n') if front else 0
    body = markdown[front.end():] if front else markdown
    for i, line in enumerate(body.splitlines(), offset + 1):
        line = re.sub(r'!?\[([^\]]*)\]\([^\s]*(?:\s+"[^"]*")?\)', r'\1', line)
        line = re.sub(r'https?://\S+', '', line)
        line = re.sub('<[^>]+>', '', line)
        yield i, normalized(html.unescape(line).replace('*', '').replace('`', ''))


def resolve(kind, observed, institution_id):
    registry = holdings()[kind]
    lookup = re.sub(r'\b(?:POE|POU)\b', lambda m:TYPE_ALIAS[m[0]], observed) if kind == 'pibs' else observed
    matches = registry.get(key(lookup), [])
    if kind == 'pibs':
        prefix = re.match(r'^([A-Z]+)\s+(P[A-Z]{2}\s+\d+)$', lookup)
        if prefix:
            lookup = holdings()['prefix_aliases'].get(prefix[1],prefix[1]) + ' ' + prefix[2]
            if not matches: matches = registry.get(key(lookup), [])
    if not matches:
        token = PIB_TOKEN.fullmatch(observed)
        if (kind == 'pibs' and token and token[1].upper() not in ('PSE', 'PSU', 'POE', 'POU')) or kind == 'classes_of_records':
            # A bare institution-specific code resolves only within its owner
            # and only when its canonical ID is unique there.
            suffix = key(observed)
            candidates = [m for k, mm in registry.items() if k.endswith(suffix) for m in mm if m['institution_id'] == institution_id]
            if len({m['record_id'] for m in candidates}) == 1: matches = candidates
    if kind == 'classes_of_records' and any(m['dataset'] == 'standard-classes' for m in matches):
        matches = [m for m in matches if m['dataset'] == 'standard-classes']
    unique = list({(m['dataset'], m['institution_id'], m['record_id']):m for m in matches}.values())
    canonical = {m['record_id'] for m in unique}
    ident = next(iter(canonical)) if len(canonical) == 1 else lookup
    if unique and unique[0]['dataset'] == 'standard-classes': ident = 'PRN ' + unique[0]['record_id']
    return ident, unique


def extract(markdown, institution_id, language, source_path):
    found = {'pibs': {}, 'classes_of_records': {}}
    recent = []
    def add(kind, observed, line_number, text, method):
        observed = normalized(observed.upper())
        ident, matches = resolve(kind, observed, institution_id)
        item = found[kind].setdefault(ident, {'id':ident, 'matched_records':matches, 'evidence':[]})
        item['evidence'].append({'language':language, 'source_path':source_path, 'line':line_number, 'mention':observed, 'method':method, 'excerpt':text[:600]})
    lines = list(visible_lines(markdown))
    for line_index, (number, line) in enumerate(lines):
        if re.search(r'\b(?:PPU|PPE|PCE|PCU|PSE|PSU|POE|POU|PRN|NDP)$', line, re.I) and line_index + 1 < len(lines):
            continuation = re.match(r'^(\d{2,6})\b', lines[line_index + 1][1])
            if continuation: line += ' ' + continuation[1]
        for token in PIB_TOKEN.finditer(line):
            typ, digits = token[1].upper(), token[2]
            observed = typ + ' ' + digits
            if typ not in ('PSE', 'PSU', 'POE', 'POU'):
                prefix = re.search(r'([A-Z][A-Z&./-]{1,14})\s+(?:(?:PIB|FRP)\s+)?$', line[:token.start()])
                if prefix and prefix[1] not in ('PIB','FRP','STANDARD','BANK','THE','COR','NUMBER'):
                    observed = prefix[1] + ' ' + observed
            add('pibs', observed, number, line, 'explicit_pib_id')
        for token in STANDARD_COR.finditer(line):
            add('classes_of_records', token[0], number, line, 'explicit_standard_cor_id')
        for token in holdings()['cor_pattern'].finditer(line):
            if PIB_TOKEN.search(token[0]): continue
            candidates = [token[0][i:].strip() for i in [0, *[m.end() for m in re.finditer(r'[\s:#/]+', token[0])]]]
            for candidate in candidates:
                if STANDARD_COR.fullmatch(candidate): continue
                if key(candidate) in holdings()['classes_of_records']:
                    add('classes_of_records', candidate, number, line, 'known_cor_id')
                    break
        context = ' '.join(recent[-2:] + [line])
        if COR_CONTEXT.search(context):
            for token in GENERIC_ID.finditer(line):
                if PIB_TOKEN.search(token[0]) or STANDARD_COR.search(token[0]): continue
                # Unknown IDs are kept only in explicit CoR context and with a
                # recognizable code prefix, never a naked year/registration #.
                value = token[0]
                value = re.sub(r'^(?:COR|PIB|FRP)\s+', '', value)
                if key(value) in holdings()['classes_of_records']: continue
                if re.search(r'\b(?:HTTP|ISBN|COVID|HTML|ISO|PAGE|APPENDIX|PIA|EFVP|EFRVP|EFPV|ATIP|AIPRP)\b|^S\.C\.|\d{3}[-.]\d{3}[-.]\d{4}', value): continue
                add('classes_of_records', value, number, line, 'explicit_cor_context')
        if line: recent.append(line)
    for kind, items in found.items():
        for ident in list(items):
            if ident not in items or items[ident]['matched_records']: continue
            longer = [other for other in items if other != ident and key(other).endswith(key(ident)) and len(key(other)) > len(key(ident))]
            if len(longer) == 1:
                items[longer[0]]['evidence'].extend(items.pop(ident)['evidence'])
    return {kind:list(items.values()) for kind, items in found.items()}


def enrich_assessment(pia, folder):
    union = {'pibs':{}, 'classes_of_records':{}}
    for lang, source in pia['sources'].items():
        refs = {'pibs':[], 'classes_of_records':[]}
        if source['status'] == 'exported' and source.get('markdown_path'):
            path = folder / source['markdown_path']
            refs = extract(path.read_text(), folder.name, lang, str(path.relative_to(ROOT)))
        source['pib_ids'] = sorted(r['id'] for r in refs['pibs'])
        source['cor_ids'] = sorted(r['id'] for r in refs['classes_of_records'])
        for kind, entries in refs.items():
            for item in entries:
                if item['id'] not in union[kind]: union[kind][item['id']] = item
                else:
                    previous = union[kind][item['id']]
                    previous['evidence'].extend(item['evidence'])
                    previous['matched_records'] = list({(m['dataset'],m['institution_id'],m['record_id']):m for m in previous['matched_records'] + item['matched_records']}.values())
    pia['references'] = {'extraction_version':VERSION, **{k:[v[ident] for ident in sorted(v)] for k,v in union.items()}}
    pia['pib_ids'] = sorted(union['pibs'])
    pia['pib_count'] = len(pia['pib_ids'])
    pia['cor_ids'] = sorted(union['classes_of_records'])
    pia['cor_count'] = len(pia['cor_ids'])
    for lang in ('en','fr'):
        source = pia['sources'].get(lang,{})
        pia['word_count_' + lang] = source.get('word_count') if source.get('status') == 'exported' else None
    pia['word_count_language'] = 'en' if pia['word_count_en'] is not None else 'fr' if pia['word_count_fr'] is not None else None
    pia['word_count'] = pia['word_count_' + pia['word_count_language']] if pia['word_count_language'] else None
    return pia


def enrich_collections():
    index = []
    for path in sorted((ROOT / 'PIAs').glob('*/collection.json')):
        org = json.loads(path.read_text())
        for pia in org['pias']:
            enrich_assessment(pia, path.parent)
            row = {k:org[k] for k in ('institution_id','name_en','name_fr','gc_orgID')}
            row.update({k:pia[k] for k in ('pia_id','title_en','title_fr','url_en','url_fr','pib_ids','pib_count','cor_ids','cor_count','word_count_en','word_count_fr','word_count','word_count_language')})
            row['pib_ids'], row['cor_ids'] = json.dumps(row['pib_ids'],ensure_ascii=False),json.dumps(row['cor_ids'],ensure_ascii=False)
            index.append(row)
        path.write_text(json.dumps(org,ensure_ascii=False,indent=2)+'\n')
    if index:
        with (ROOT / 'PIAs/assessment_index.csv').open('w',newline='') as f:
            writer = csv.DictWriter(f,fieldnames=list(index[0]));writer.writeheader();writer.writerows(index)
    return index


if __name__ == '__main__':
    records = enrich_collections()
    print(f"Enriched {len(records)} PIAs: {sum(bool(r['pib_count']) for r in records)} with PIB IDs; {sum(bool(r['cor_count']) for r in records)} with CoR IDs")
