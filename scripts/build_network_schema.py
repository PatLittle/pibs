#!/usr/bin/env python3
"""Inventory field names/types/keys only; never store external AIA record values."""
import argparse
import csv
import hashlib
import html
import json
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/data/network-schema.json'

def schema(rows, maps=None):
    fields = defaultdict(set)
    def walk(value, path):
        typ = 'null' if value is None else 'boolean' if isinstance(value, bool) else 'number' if isinstance(value, (int, float)) else 'object' if isinstance(value, dict) else 'array' if isinstance(value, list) else 'string'
        if path: fields[path].add(typ)
        if isinstance(value, dict):
            for key, item in value.items():
                key=(maps or {}).get(path,key)
                if path.endswith('source_status_counts'): key='{status}'
                walk(item, path + '.' + key if path else key)
        elif isinstance(value, list):
            for item in value: walk(item, path + '[]')
    for row in rows: walk(row, '')
    return [dict(name=key, types=sorted(types)) for key, types in sorted(fields.items())]

def build(aia_file=None):
    model = json.loads((ROOT / 'data_model.json').read_text())
    tables, relations = [], []
    def table(ident, label, source, rows, layer, keys=(), fields=None, note=''):
        item = dict(id=ident, label=label, source=source, layer=layer, rows=len(rows), primary_key=list(keys), fields=fields if fields is not None else schema(rows), note=note)
        tables.append(item); return item
    def relation(a, b, label, basis='documented', fields=None):
        relations.append(dict(source=a, target=b, label=label, basis=basis, fields=fields or []))
    for ident, definition in model['tables'].items():
        with (ROOT / definition['path']).open() as handle:
            reader = csv.DictReader(handle); rows = list(reader); header = reader.fieldnames
        layer = 'support' if ident.startswith('my_info_') else 'vocabulary' if ident in ('personal_information_categories','pib_type_values') else 'records'
        fields = [dict(name=key, types=['json-array' if key in definition.get('json_array_fields',[]) else 'string']) for key in header]
        table(ident, ident.replace('_',' '), definition['path'], rows, layer, definition['primary_key'], fields, definition.get('description',''))['foreign_keys']=definition.get('foreign_keys',[])
        for fk in definition.get('foreign_keys',[]): relation(ident, fk['references'], ' → '.join([', '.join(fk['fields']), ', '.join(fk['reference_fields'])]), fields=fk['fields'])
    relation('pib_cor_links','institution_classes_of_records','resolved institutional class', fields=['institution_id','cor_record_number'])
    relation('pib_cor_links','standard_classes_of_records','resolved standard class', fields=['cor_record_number'])
    relation('my_info_pib_category_assignments','my_info_pib_features','source-scoped record_id', 'derived', ['record_id'])
    relation('my_info_pib_features','institution_personal_information_banks','source-scoped record identity', 'derived')
    manifest=json.loads((ROOT/'PIAs/collection_manifest.json').read_text())
    table('pia_manifest','PIA collection manifest','PIAs/collection_manifest.json',[manifest],'assessments',fields=schema([manifest],maps={'organizations':'{institution_id}'}),note='Collection-level schema, counts and provenance, not a record entity.')
    relation('pias','pia_manifest','collection provenance and collection date')
    relation('standard_personal_information_banks','standard_classes_of_records','literal PRN/NDP reference, if uniquely resolved')
    inventories, pias, sources, refs = [], [], [], []
    for path in sorted((ROOT/'PIAs').glob('*/collection.json')):
        org=json.loads(path.read_text()); inventories.append({**{k:v for k,v in org.items() if k!='pias'},'pias':[]})
        for pia in org['pias']:
            pias.append({'institution_id':org['institution_id'],**{k:v for k,v in pia.items() if k not in ('sources','references')},'sources':{},'references':{'extraction_version':pia.get('references',{}).get('extraction_version')}})
            for language, source in pia['sources'].items(): sources.append({'institution_id':org['institution_id'],'pia_id':pia['pia_id'],'language':language,**source})
            for kind in ('pibs','classes_of_records'):
                for ref in pia.get('references',{}).get(kind,[]): refs.append({'institution_id':org['institution_id'],'pia_id':pia['pia_id'],'kind':kind,**ref})
    table('pia_inventories','PIA organization inventories','PIAs/*/collection.json (organization)',inventories,'assessments',['institution_id'])
    table('pias','Privacy assessments','PIAs/*/collection.json → pias[]',pias,'assessments',['institution_id','pia_id'])
    table('pia_sources','PIA language sources','pias[].sources.{language}',sources,'assessments',['institution_id','pia_id','language'])
    table('pia_references','PIA citations and evidence','pias[].references.{kind}[]',refs,'assessments',['institution_id','pia_id','kind','id'])
    relation('pia_inventories','institution_registry','institution_id',fields=['institution_id'])
    relation('pias','pia_inventories','inherits institution_id'); relation('pia_sources','pias','assessment + language'); relation('pia_references','pias','assessment identity')
    relation('pia_references','institution_personal_information_banks','unique matched_records[] → PIB')
    relation('pia_references','standard_personal_information_banks','unique matched_records[] → standard PIB')
    relation('pia_references','institution_classes_of_records','unique matched_records[] → class')
    relation('pia_references','standard_classes_of_records','unique matched_records[] → standard class')
    service_base=ROOT/'data/service_inventory'
    service_manifest=json.loads((service_base/'manifest.json').read_text())
    table('service_import_manifest','Service Inventory import provenance','data/service_inventory/manifest.json',[service_manifest],'support',fields=schema([service_manifest],maps={'source_inputs':'{resource}','outputs':'{path}'}))
    catalogue=json.loads((service_base/'schema_fields.json').read_text())
    table('service_schema_metadata','Service Inventory supplied field definitions','data/service_inventory/schema_fields.json',[catalogue],'support',note='All 70 field definitions; allowed-value counts only, not an inferred service-program relationship table.')
    audit=json.loads((service_base/'field_join_audit.json').read_text())
    table('service_field_audit','Service Inventory field join decisions','data/service_inventory/field_join_audit.json',audit,'support',['resource','field'])
    relation('service_inventory','service_import_manifest','normalized source snapshot, resource IDs and checksums')
    relation('service_standards','service_import_manifest','normalized source snapshot, resource IDs and checksums')
    relation('service_field_audit','service_schema_metadata','resource + field definition')
    accounts_audit_path = 'site/data/public-accounts-join-audit.json'
    accounts_audit = json.loads((ROOT / accounts_audit_path).read_text(encoding='utf-8'))
    table('public_accounts_join_audit', 'Public Accounts import and unmatched service references',
          accounts_audit_path, [accounts_audit], 'support')
    relation('public_accounts_codes', 'public_accounts_codes', 'published parent in same fiscal year and entity',
             fields=['fiscal_yr', 'accounts_entity', 'parent_code'])
    relation('public_accounts_codes', 'public_accounts_departments', 'fiscal year and accounting entity',
             fields=['fiscal_yr', 'accounts_entity'])
    relation('public_accounts_service_links', 'public_accounts_join_audit', 'same-year join outcomes and source checksum')
    relation('public_accounts_infobase_links', 'public_accounts_join_audit', 'resource scope, join outcomes and snapshot checksum')
    graph=json.loads((ROOT/'site/data/graph.json').read_text())
    shards={path:json.loads((ROOT/'site'/path).read_text()) for path in graph['attribute_files']}
    for node in graph['nodes']:
        if node.get('attribute_url'): node['attributes']=shards[node['attribute_url']][node['id']]
    evidence=[item for shard in graph['evidence_files'] for items in json.loads((ROOT/'site'/shard).read_text()).values() for item in items]
    config=json.loads((ROOT/'site/aia-source.json').read_text())
    external=[]
    if aia_file:
        raw=Path(aia_file).read_bytes(); rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
        for ident,label,values in [
            ('aia_source','AIA source records',[{**{k:v for k,v in r.items() if k not in ('data','translationsOnResult','derived')},'data':{},'translationsOnResult':{},'derived':{}} for r in rows]),
            ('aia_answers','AIA survey answers',[r.get('data',{}) for r in rows]),
            ('aia_translations','AIA translated answers',[r.get('translationsOnResult',{}) for r in rows]),
            ('aia_derived','AIA calculated results',[r.get('derived',{}) for r in rows])]:
            item=table(ident,label,config['url'],values,'external',['package_id (parent)'] if ident!='aia_source' else ['package_id'],note='External JSONL; schema only is stored here. No AIA values are copied into this repository.')
            external.append(item)
        # Observe the runtime projection from its owning implementation, returning only schemas.
        js="""import fs from 'node:fs'; import {webcrypto} from 'node:crypto';globalThis.crypto ||= webcrypto;
import {parseJSONL,integrateAIA} from './site/aia-data.mjs';
const graph=JSON.parse(fs.readFileSync(process.argv[1]));
const result=await integrateAIA(graph,parseJSONL(fs.readFileSync(process.argv[2],'utf8')));
function shape(rows){const keys=new Map();function walk(v,p){if(p){if(!keys.has(p))keys.set(p,new Set());keys.get(p).add(v===null?'null':Array.isArray(v)?'array':typeof v);}if(Array.isArray(v)){for(const a of v)walk(a,p+'[]');}else if(v&&typeof v==='object'){for(const[k,a]of Object.entries(v))walk(a,p?p+'.'+k:k);}}for(const r of rows)walk(r,'');return [...keys].sort((a,b)=>a[0].localeCompare(b[0])).map(([name,t])=>({name,types:[...t].sort()}));}
const edges=result.graph.edges.filter(e=>e.id.startsWith('aia-edge:'));console.log(JSON.stringify({...Object.fromEntries(['aia','official','reference'].map(t=>[t,{fields:shape(result.graph.nodes.filter(n=>n.type===t)),rows:result.graph.nodes.filter(n=>n.type===t).length}])),matches:{fields:shape(result.records.map(r=>({id:r.id,package_id:r.package_id,institution_id:r.institution_id,organization_match:r.organization_match,official:r.official,service_match:r.service_match,references:r.references}))),rows:result.records.length},edges:{fields:shape(edges),rows:edges.length},evidence:{fields:shape(edges.flatMap(e=>e.evidence)),rows:edges.reduce((n,e)=>n+e.evidence.length,0)}}));"""
        runtime=json.loads(subprocess.check_output(['node','--input-type=module','-e',js,str(ROOT/'site/data/graph.json'),str(Path(aia_file).resolve())],cwd=ROOT))
        external_meta=dict(inspected_on=date.today().isoformat(),sha256=hashlib.sha256(raw).hexdigest(),url=config['url'])
    else:
        previous=json.loads(OUT.read_text()) if OUT.exists() else {'tables':[]}
        external=[t for t in previous['tables'] if t['layer']=='external'];tables.extend(external)
        runtime=previous.get('runtime_shapes',{});external_meta=previous.get('external_source',{})
    for ident in ('aia_answers','aia_translations','aia_derived'): relation(ident,'aia_source','same source line / package_id (parent)')
    relation('aia_source','institution_registry','unique exact bilingual organization name/alias')
    relation('aia_answers','institution_personal_information_banks','explicit literal PIB code; uniquely resolved')
    relation('aia_answers','standard_personal_information_banks','explicit literal standard PIB code')
    relation('aia_answers','pias','exact cited PIA source URL')
    relation('aia_answers','service_inventory','ServiceID = service_id + unique matched institution; stable identity, no year inferred', fields=['ServiceID'])
    if 'matches' in runtime:
        table('aia_matches','AIA normalized identities and citations','site/aia-data.mjs → records[] (browser memory)',[None]*runtime['matches']['rows'],'projection',['package_id'],runtime['matches']['fields'],note='Normalized service/organization status, organization-scoped official name_en/name_fr/u_id and literal citation groups. Schema only; no AIA values are stored.')
        relation('aia_matches','aia_source','package_id → source UUID')
        relation('aia_matches','institution_registry','nullable institution_id; unique organization match')
        relation('node_official','aia_matches','official.u_id → organization-scoped observed name','projection')
    for typ in sorted({n['type'] for n in graph['nodes']}):
        rows=[n for n in graph['nodes'] if n['type']==typ]
        merged={f['name']:f for f in schema(rows)}
        for field in runtime.get(typ,{}).get('fields',[]): merged.setdefault(field['name'],field)
        table('node_'+typ,'Network '+typ,'site/data/graph.json → nodes[] + lazy attributes; AIA references may add runtime fields',rows,'projection',['id'],list(merged.values()))
    for typ,definition in runtime.items():
        if typ not in ('aia','official'): continue
        table('node_'+typ,'Network '+typ,'site/aia-data.mjs (browser memory)',[None]*definition['rows'],'projection',['id'],definition['fields'])
    edge_fields={f['name']:f for f in schema(graph['edges'])}
    for f in runtime.get('edges',{}).get('fields',[]): edge_fields.setdefault(f['name'],f)
    table('graph_edges','Network relationships','site/data/graph.json → edges[]; AIA edges inline',graph['edges'],'projection',['id'],list(edge_fields.values()))
    evidence_fields={f['name']:f for f in schema(evidence)}
    for f in runtime.get('evidence',{}).get('fields',[]): evidence_fields.setdefault(f['name'],f)
    table('graph_evidence','Relationship evidence','site/data/graph-evidence/*.json; AIA evidence inline',evidence,'projection',['edge_id (shard parent)','ordinal (array)'],list(evidence_fields.values()))
    table('graph_manifest','Graph manifest','site/data/graph.json (manifest)',[{k:v for k,v in graph.items() if k not in ('nodes','edges','attribute_files','evidence_files','inputs')}],'projection')
    manifest=tables[-1];manifest['fields'].extend([dict(name=k,types=['object']) for k in ('inputs','attribute_files','evidence_files')]);manifest['fields'].extend([dict(name=k+'.{path}',types=['sha256 string']) for k in ('inputs','attribute_files','evidence_files')]);manifest['fields'].extend([dict(name=k,types=['array']) for k in ('nodes','edges')]);manifest['fields'].extend([dict(name='summary.node_types.'+k,types=['number']) for k in ('aia','official')])
    relation('graph_edges','graph_evidence','edge id → evidence[]')
    for typ in ('institution','pib','class','pia','reference','aia','official','service','program','service_standard'): relation('graph_edges','node_'+typ,'source / target node id')
    for typ in ('account_code', 'infobase_program'):
        relation('graph_edges', 'node_' + typ, 'source / target node id')
    relation('node_account_code', 'public_accounts_codes', 'fiscal year + accounting entity + code', 'projection')
    relation('node_infobase_program', 'public_accounts_infobase_links',
             'fiscal year + InfoBase organization ID + code', 'projection')
    for a,b in [('node_institution','institution_registry'),('node_pib','institution_personal_information_banks'),('node_pib','standard_personal_information_banks'),('node_class','institution_classes_of_records'),('node_class','standard_classes_of_records'),('node_pia','pias'),('node_aia','aia_source'),('node_official','aia_answers'),('node_service','service_inventory'),('node_program','service_programs'),('node_service_standard','service_standards')]: relation(a,b,'projection / retained source identity','projection')
    return dict(schema_version=1,scope='All canonical tables used by the network; Service Inventory and year-scoped program/standard joins; supporting My Info tables; nested PIA and external AIA source shapes; browser graph projection. Field names/types/keys only, never external AIA record values.',external_source=external_meta,runtime_shapes=runtime,tables=tables,relationships=relations,summary=dict(tables=len(tables),fields=sum(len(t['fields']) for t in tables),relationships=len(relations)))

def write(model):
    OUT.write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    # Every field is present in a selectable, zoomable standalone SVG.
    lanes=['records','assessments','external','vocabulary','support','projection']; width=650*len(lanes); positions={}; ypos={k:90 for k in lanes}
    for t in model['tables']:
        x=lanes.index(t['layer'])*650+30;y=ypos[t['layer']];height=84+len(t['fields'])*20
        positions[t['id']]=(x,y,height);ypos[t['layer']]+=height+85
    height=max(ypos.values())+40
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">PIBS full network data model — every table and field</title><desc id="desc">{html.escape(model["scope"])}</desc><style>text{{font-family:Arial,sans-serif;fill:#26374a}}.field{{font-family:monospace;font-size:12px}}.link{{fill:none;stroke:#8797a8;stroke-width:1.3}}.table{{fill:#fff;stroke:#bec7d0}}.heading{{fill:#edf3f8}}</style><rect width="100%" height="100%" fill="#f5f7f9"/>']
    for i,lane in enumerate(lanes):parts.append(f'<text x="{i*650+30}" y="40" font-size="20" font-weight="700">{lane.title()}</text>')
    for rel in model['relationships']:
        a,b=positions[rel['source']],positions[rel['target']];x1,y1=a[0]+590,a[1]+24;x2,y2=b[0],b[1]+24
        if a[0]>=b[0]:x1=a[0];x2=b[0]+590
        mid=(x1+x2)/2
        parts.append(f'<path class="link" stroke-dasharray="{'5 4' if rel['basis']=='derived' else '2 4' if rel['basis']=='projection' else 'none'}" d="M{x1},{y1} C{mid},{y1} {mid},{y2} {x2},{y2}"><title>{html.escape(rel["label"]+" · "+rel["basis"])}</title></path>')
    for t in model['tables']:
        x,y,h=positions[t['id']];ident=html.escape(t['id']);parts.append(f'<g id="{ident}" data-table="{ident}"><rect class="table" x="{x}" y="{y}" width="590" height="{h}" rx="4"/><rect class="heading" x="{x+1}" y="{y+1}" width="588" height="62"/><text x="{x+12}" y="{y+24}" font-size="15" font-weight="700">{html.escape(t["label"])}</text><text x="{x+12}" y="{y+46}" font-size="12">{len(t["fields"])} fields · {t["rows"]} observed records · {html.escape(t["layer"])}</text>')
        for i,f in enumerate(t['fields']):
            marks=[]
            if f['name'] in t['primary_key']: marks.append('PK')
            if any(f['name'] in fk['fields'] for fk in t.get('foreign_keys',[])): marks.append('FK')
            prefix='/'.join(marks)+' ' if marks else ''
            parts.append(f'<text class="field" data-field="{html.escape(f["name"])}" x="{x+12}" y="{y+82+i*20}">{html.escape(prefix+f["name"])}<title>{html.escape(", ".join(f["types"]))}</title></text>')
        parts.append('</g>')
    parts.append('</svg>');(ROOT/'site/data/network-schema.svg').write_text(''.join(parts))
    print(model['summary'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--aia-file');args=parser.parse_args();write(build(args.aia_file))
