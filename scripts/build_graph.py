#!/usr/bin/env python3
"""Generate a deterministic, evidence-bearing graph from the existing inventories.

No network calls or new entity resolution: PIA matches come from reference_extraction;
PIB/class matches come from compile_institution_tables. Ambiguity stays unresolved.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from my_info.categories import classify_record, load_category_definitions


def record_id(dataset, institution, identifier):
    prefix = {'pibs': 'pib', 'standard-pibs': 'pib', 'classes': 'class',
              'standard-classes': 'class'}[dataset]
    return f'{prefix}:{institution or "standard"}:{identifier}'


def build(root=ROOT):
    root = Path(root)
    inputs, nodes, edges = {}, {}, {}

    def read(path, table=False):
        raw = (root / path).read_bytes()
        inputs[path] = hashlib.sha256(raw).hexdigest()
        return list(csv.DictReader(raw.decode('utf-8').splitlines(keepends=True))) if table else json.loads(raw)

    def add_node(node):
        if node['id'] in nodes:
            raise ValueError(f'Duplicate graph identity: {node["id"]}')
        nodes[node['id']] = node

    def add_edge(source, target, kind, evidence, resolution='resolved'):
        if source not in nodes or target not in nodes:
            raise ValueError(f'Dangling relationship: {source} -> {target}')
        ident = 'edge:' + hashlib.sha256(json.dumps([source, target, kind], ensure_ascii=False).encode()).hexdigest()[:24]
        edge = edges.setdefault(ident, dict(id=ident, source=source, target=target,
                                          type=kind, resolution=resolution, evidence=[]))
        for item in evidence:
            if item not in edge['evidence']:
                edge['evidence'].append(item)

    registry = read('institution_registry.csv', True)
    orgs = {r['institution_id']: r for r in registry}
    for r in registry:
        add_node(dict(id='institution:' + r['institution_id'], type='institution',
                      identifier=r['institution_id'], institution_id=r['institution_id'],
                      label_en=r['legal_name_en'], label_fr=r['legal_name_fr'],
                      sources={lang: r.get('infosource_url_' + lang, '') for lang in ('en', 'fr')},
                      record_url='table.html?' + urlencode(dict(dataset='institutions', institution_id=r['institution_id'], open='record')),
                      source_path='institution_registry.csv'))

    category_path = 'pi_categories_en_fr.csv'
    for r in read(category_path, True):
        add_node(dict(id='category:' + r['PI_CAT_ID'], type='category', identifier=r['PI_CAT_ID'],
                      label_en=r['name_en'], label_fr=r['name_fr'],
                      description_en=r['examples_en'], description_fr=r['examples_fr'],
                      source_path=category_path, sources={},
                      record_url='table.html?' + urlencode(dict(dataset='categories', PI_CAT_ID=r['PI_CAT_ID'], open='record'))))
    definitions = load_category_definitions(root / category_path)
    inputs['my_info/categories.py'] = hashlib.sha256((root / 'my_info/categories.py').read_bytes()).hexdigest()
    type_path = 'pib_type_values.csv'
    type_rows = read(type_path, True)
    for r in type_rows:
        add_node(dict(id='pib-type:' + r['pib_code'], type='pib_type', identifier=r['pib_code'],
                      label_en=r['pib_type'], label_fr=r['scope_fr'],
                      description_en=r['scope_en'], description_fr=r['scope_fr'],
                      source_path=type_path, sources={},
                      record_url='table.html?' + urlencode(dict(dataset='pib-types', pib_code=r['pib_code'], open='record'))))

    tables = [('pibs', 'institutions_infosource_docs/pib_table_en_fr_all.csv', 'bank_number_key', 'title'),
              ('classes', 'institutions_infosource_docs/cor_table_en_fr_all.csv', 'record_number', 'name'),
              ('standard-pibs', 'spib_en_fr.csv', 'bank_number_key', 'entry_title'),
              ('standard-classes', 'standard_classes_of_records_en_fr.csv', 'record_number', 'title')]
    pib_rows, standard_pib_rows = {}, {}
    for dataset, path, key, title in tables:
        for r in read(path, True):
            org = r.get('institution_id') or None
            ident = record_id(dataset, org, r[key])
            if org and org not in orgs:
                raise ValueError(f'Unknown institution: {org}')
            source_role = 'pibs_url_' if dataset == 'pibs' else 'classes_of_records_url_'
            sources = {lang: (orgs[org].get(source_role + lang, '') if org else r.get('url_' + lang, '')) for lang in ('en', 'fr')}
            node = dict(id=ident, type='pib' if 'pibs' in dataset else 'class',
                        identifier=r[key], institution_id=org, scope='institution' if org else 'standard',
                        label_en=r.get(title + '_en', ''), label_fr=r.get(title + '_fr', ''),
                        description_en=r.get('description_en', '')[:1000],
                        description_fr=r.get('description_fr', '')[:1000],
                        attributes={field: r[field] for field in (
                            'pib_type', 'purpose_en', 'purpose_fr', 'class_of_individuals_en', 'class_of_individuals_fr',
                            'consistent_uses_en', 'consistent_uses_fr', 'retention_disposal_en', 'retention_disposal_fr',
                            'document_types_en', 'document_types_fr', 'date_last_modified') if r.get(field)},
                        aliases=[r.get(('bank_number_' if 'pibs' in dataset else 'record_number_') + lang, '') for lang in ('en', 'fr')] +
                                [r.get('entry_id_' + lang, '') for lang in ('en', 'fr')],
                        sources=sources, source_path=path,
                        record_url='table.html?' + urlencode({'dataset': dataset, **({'institution_id': org} if org else {}), key: r[key], 'open': 'record'}))
            add_node(node)
            if node['type'] == 'pib':
                for value in type_rows:
                    if r.get('pib_type') != value['pib_type']: continue
                    add_edge(ident, 'pib-type:' + value['pib_code'], 'has_type',
                             [dict(source_path=path, field='pib_type', mention=r['pib_type'],
                                   method='controlled_pib_type', vocabulary_path=type_path)])
                for assignment in classify_record(r, definitions).assignments:
                    add_edge(ident, 'category:' + assignment.category_id, 'category_match',
                             [dict(source_path=path, field=e.field, language=e.language,
                                   excerpt=e.matched_text, mention=assignment.category_id,
                                   method='derived_description_category_match', rule=e.rule,
                                   confidence=e.confidence, source_url=sources.get(e.language, ''))
                              for e in assignment.evidence])
            if dataset == 'pibs': pib_rows[(org, r[key])] = r
            if dataset == 'standard-pibs': standard_pib_rows[ident] = r
            if org:
                add_edge(ident, 'institution:' + org, 'listed_by', [dict(source_path=path,
                         field='institution_id', mention=org, source_url=url, language=lang)
                         for lang, url in sources.items()])

    def unresolved(source, kind, observed, candidates):
        # A literal source reference is a separate entity, never an invented PIB/CoR.
        ident = 'reference:' + hashlib.sha256(json.dumps([source, kind, observed], ensure_ascii=False).encode()).hexdigest()[:24]
        if ident not in nodes:
            add_node(dict(id=ident, type='reference', identifier=observed,
                          label_en=observed, label_fr=observed,
                          reference_kind=kind, institution_id=nodes[source].get('institution_id'),
                          resolution='ambiguous' if len(candidates) > 1 else 'unresolved',
                          candidates=candidates, sources={}))
        return ident

    links_path = 'institutions_infosource_docs/pib_cor_links.csv'
    for r in read(links_path, True):
        source = record_id('pibs', r['institution_id'], r['bank_number_key'])
        if source not in nodes: raise ValueError(f'Missing source PIB: {source}')
        target = record_id('classes', None if r['relationship_scope'] == 'standard' else r['institution_id'], r['cor_record_number'])
        resolved = r['resolved'].lower() == 'true' and target in nodes
        if not resolved: target = unresolved(source, 'class', r['related_record_number'], [])
        lang = r['language']
        add_edge(source, target, 'related_class', [dict(source_path=links_path,
                 field='related_record_number_' + lang, language=lang,
                 mention=r['related_record_number'], excerpt=pib_rows[(r['institution_id'], r['bank_number_key'])].get('related_record_number_' + lang, ''),
                 method='compiled_related_record_reference', relationship_scope=r['relationship_scope'],
                 source_url=nodes[source]['sources'].get(lang, ''))], 'resolved' if resolved else 'unresolved')

    # Standard PIBs carry explicit bilingual class references too. Resolve only
    # literal PRN/NDP identifiers; do not infer links from names or common topics.
    for source, row in standard_pib_rows.items():
        for lang in ('en', 'fr'):
            field = 'related_record_number_' + lang
            for match in re.finditer(r'\b(?:PRN|NDP)\s+(\d+(?:\.\d+)*)\b', row.get(field, ''), re.I):
                target = record_id('standard-classes', None, match[1])
                resolved = target in nodes
                if not resolved: target = unresolved(source, 'class', match[0], [])
                add_edge(source, target, 'related_class', [dict(source_path='spib_en_fr.csv',
                         field=field, language=lang, mention=match[0], excerpt=row[field],
                         method='explicit_standard_class_reference', relationship_scope='standard',
                         source_url=nodes[source]['sources'].get(lang, ''))],
                         'resolved' if resolved else 'unresolved')

    manifest = read('PIAs/collection_manifest.json')
    for path in sorted((root / 'PIAs').glob('*/collection.json')):
        relative = path.relative_to(root).as_posix()
        org = read(relative)
        if org['pias'] and org['institution_id'] not in orgs:
            # Historical artifact-only inventories retain their recorded identity.
            oid = org['institution_id']
            if 'institution:' + oid not in nodes:
                add_node(dict(id='institution:' + oid, type='institution', identifier=oid,
                              institution_id=oid, label_en=org['name_en'], label_fr=org['name_fr'],
                              registry_membership=org.get('registry_membership'), source_path=relative, sources={}))
        for pia in org['pias']:
            ident = 'pia:' + org['institution_id'] + '/' + pia['pia_id']
            sources = {lang: s['url'] for lang, s in pia['sources'].items()}
            add_node(dict(id=ident, type='pia', identifier=pia['pia_id'], institution_id=org['institution_id'],
                          **{'label_' + lang: ((pia.get('title_' + lang) or '') if pia['sources'].get(lang, {}).get('status') == 'exported'
                             else pia['sources'].get(lang, {}).get('title_from_list') or pia.get('title_' + lang) or '') for lang in ('en', 'fr')},
                          available_languages=[lang for lang, s in pia['sources'].items() if s['status'] == 'exported'],
                          source_status={lang: s['status'] for lang, s in pia['sources'].items()},
                          collected_at_utc=org['collected_at_utc'], sources=sources, source_path=relative,
                          record_url='privacy-assessment.html?' + urlencode(dict(institution_id=org['institution_id'], pia_id=pia['pia_id']))))
            add_edge(ident, 'institution:' + org['institution_id'], 'listed_by', [dict(source_path=relative,
                     field='institution_id', mention=org['institution_id'], method='collection_inventory',
                     source_url=s.get('list_url') or s['url'], language=lang,
                     checked_at_utc=s.get('http', {}).get('checked_at_utc')) for lang, s in pia['sources'].items()])
            for kind in ('pibs', 'classes_of_records'):
                for ref in pia['references'][kind]:
                    matches = ref['matched_records']
                    candidates = sorted({record_id(m['dataset'], m['institution_id'], m['record_id']) for m in matches})
                    resolved = len(candidates) == 1 and candidates[0] in nodes
                    target = candidates[0] if resolved else unresolved(ident, kind, ref['id'], candidates)
                    evidence = []
                    for item in ref['evidence']:
                        s = pia['sources'][item['language']]
                        # Ignore stale evidence from an unavailable copy; never upgrade it to fact.
                        if s['status'] != 'exported': continue
                        raw = (root / item['source_path']).read_bytes()
                        checksum = hashlib.sha256(raw).hexdigest()
                        if checksum != s['markdown_sha256']:
                            raise ValueError(f'Stale evidence: {item["source_path"]}')
                        inputs[item['source_path']] = checksum
                        evidence.append({**item, 'source_url': s['url'], 'markdown_sha256': checksum,
                                         'checked_at_utc': s.get('http', {}).get('checked_at_utc')})
                    if evidence:
                        add_edge(ident, target, 'references', evidence,
                                 'resolved' if resolved else nodes[target]['resolution'])

    for edge in edges.values():
        edge['basis'] = 'derived' if edge['type'] == 'category_match' else 'documented'
    result = dict(schema_version=2, collection_generated_at_utc=manifest['generated_at_utc'],
                  nodes=sorted(nodes.values(), key=lambda n: n['id']),
                  edges=sorted(edges.values(), key=lambda e: e['id']))
    result['summary'] = dict(nodes=len(nodes), edges=len(edges),
                            node_types=dict(sorted(Counter(n['type'] for n in nodes.values()).items())),
                            resolutions=dict(sorted(Counter(e['resolution'] for e in edges.values()).items())))
    result['inputs'] = dict(sorted(inputs.items()))
    return result


def write(root=ROOT):
    graph = build(root)
    output = Path(root) / 'site/data/graph.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    # Load provenance only when inspecting an edge, in 32 deterministic shards.
    shards = {}
    for edge in graph['edges']:
        bucket = f'{int(edge["id"].split(":")[1][:2], 16) % 32:02x}'
        path = f'data/graph-evidence/{bucket}.json'
        evidence = edge.pop('evidence')
        shards.setdefault(path, {})[edge['id']] = evidence
        edge.update(evidence_url=path, evidence_count=len(evidence))
    graph['evidence_files'] = {}
    for path, records in sorted(shards.items()):
        target = Path(root) / 'site' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(records, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
        target.write_bytes(raw)
        graph['evidence_files'][path] = hashlib.sha256(raw).hexdigest()
    for old in (output.parent / 'graph-evidence').glob('*.json'):
        if old.relative_to(Path(root) / 'site').as_posix() not in shards: old.unlink()
    attribute_shards = {}
    for node in graph['nodes']:
        attributes = node.pop('attributes', None)
        if not attributes: continue
        bucket = f'{int(hashlib.sha256(node["id"].encode()).hexdigest()[:2], 16) % 32:02x}'
        path = f'data/graph-attributes/{bucket}.json'
        attribute_shards.setdefault(path, {})[node['id']] = attributes
        node['attribute_url'] = path
    graph['attribute_files'] = {}
    for path, records in sorted(attribute_shards.items()):
        target = Path(root) / 'site' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(records, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
        target.write_bytes(raw)
        graph['attribute_files'][path] = hashlib.sha256(raw).hexdigest()
    for old in (output.parent / 'graph-attributes').glob('*.json'):
        if old.relative_to(Path(root) / 'site').as_posix() not in attribute_shards: old.unlink()
    output.write_text(json.dumps(graph, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'Built graph: {graph["summary"]}')
    return graph


if __name__ == '__main__': write()
