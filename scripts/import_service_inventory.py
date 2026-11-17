#!/usr/bin/env python3
"""Import published Service Inventory rows and inspect a supplied Recombinant schema.

Attached descriptions/validation messages are source metadata, never instructions.
Raw downloads may stay outside the checkout; deterministic normalized snapshots,
field definitions and a source manifest are the reproducible owning inputs.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATASET='https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c'
SCHEMA_URL='https://open.canada.ca/data/recombinant-published-schema/service.json'
YAML_URL='https://github.com/open-data/ckanext-canada/blob/master/ckanext/canada/tables/service.yaml'
RESOURCES={'service':'c0cf9766-b85b-48c3-b295-34f72305aaf6','service-std':'8736cd7e-9bf9-4a45-9eee-a6cb3c43c07e'}
BASE=ROOT/'data/service_inventory'

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle); rows=list(reader); fields=reader.fieldnames
    return fields,rows

def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)

def tokens(value):
    if isinstance(value,list): return [str(v).strip() for v in value if str(v).strip()]
    value=str(value or '').strip()
    if value.startswith('['): return tokens(json.loads(value))
    if value.startswith('{') and value.endswith('}'): value=value[1:-1]
    return [v.strip() for v in next(csv.reader([value],skipinitialspace=True)) if v.strip()]

def check_keys(rows,fields,name):
    seen=set()
    for row in rows:
        key=tuple(row.get(f,'').strip() for f in fields)
        if not all(key):raise ValueError(f'{name}: blank key {key}')
        if key in seen:raise ValueError(f'{name}: duplicate key {key}')
        seen.add(key)
    return seen

def normalize(schema, services, standards, registry):
    resources={r['resource_name']:r for r in schema['resources']}
    skeys=check_keys(services,['owner_org','fiscal_yr','service_id'],'service')
    check_keys(standards,['owner_org','fiscal_yr','service_id','service_standard_id'],'service-std')
    for row in standards:
        key=tuple(row[f] for f in ['owner_org','fiscal_yr','service_id'])
        if key not in skeys: raise ValueError(f'Orphan service standard: {key}')
    by_slug=defaultdict(set)
    for r in registry:
        if r['open_canada_org_slug']:by_slug[r['open_canada_org_slug']].add(r['institution_id'])
    owners=[]
    for slug in sorted({r['owner_org'] for r in services}):
        matches=sorted(by_slug[slug]);title=next(r['owner_org_title'] for r in services if r['owner_org']==slug)
        owners.append(dict(owner_org=slug,owner_org_title=title,institution_id=matches[0] if len(matches)==1 else '',resolution='resolved' if len(matches)==1 else 'ambiguous' if matches else 'unresolved',method='exact_open_canada_org_slug',candidates=json.dumps(matches)))
    definitions={f['id']:f for f in resources['service']['fields']}
    choices=definitions['program_id'].get('choices',{})
    programs={}; links=[]; refs=[]
    for row in services:
        for code in sorted(set(tokens(row['program_id']))):
            choice=choices.get(code);allowed=choice.get('valid_orgs',{}) if choice else {}
            status='invalid_suffix' if code.endswith('-INV') else 'unknown_code' if not choice else 'owner_not_listed' if row['owner_org'] not in allowed else 'resolved'
            years=allowed.get(row['owner_org'],[])
            period='listed' if row['fiscal_yr'] in years else 'unspecified' if not years else 'not_listed_in_current_choice_snapshot'
            ref={k:row[k] for k in ['owner_org','fiscal_yr','service_id']};ref.update(program_id=code,resolution=status,vocabulary_year_status=period);refs.append(ref)
            if status!='resolved':continue
            key=(row['owner_org'],code)
            programs[key]=dict(owner_org=row['owner_org'],program_id=code,name_en=choice.get('en',''),name_fr=choice.get('fr',''),valid_fiscal_years=json.dumps(years),label_source='Recombinant program_id choices; labels describe the inspected code list, not a historical program name')
            links.append({k:ref[k] for k in ['owner_org','fiscal_yr','service_id','program_id','vocabulary_year_status']})
    return owners,[programs[k] for k in sorted(programs)],sorted(links,key=lambda r:tuple(r.values())),sorted(refs,key=lambda r:tuple(r.values()))

def import_files(schema_file,service_file,standard_file,root=ROOT):
    root=Path(root);output=root/'data/service_inventory';output.mkdir(parents=True,exist_ok=True)
    raw_schema=Path(schema_file).read_bytes();definition=json.loads(raw_schema)
    resource_defs={r['resource_name']:r for r in definition['resources']}
    inputs={};tables={}
    for name,path in [('service',service_file),('service-std',standard_file)]:
        fields,rows=read_csv(path);expected=[f['id'] for f in resource_defs[name]['fields']]
        if fields!=expected:raise ValueError(f'{name}: input columns differ from the supplied schema')
        tables[name]=(fields,rows);raw=Path(path).read_bytes()
        inputs[name]=dict(resource_id=RESOURCES[name],url=DATASET.replace('/en','')+'/resource/'+RESOURCES[name]+'/download/'+name+'.csv',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rows=len(rows))
    _,registry=read_csv(root/'institution_registry.csv')
    owners,programs,links,refs=normalize(definition,tables['service'][1],tables['service-std'][1],registry)
    for name,(fields,rows) in tables.items():write_csv(output/(name+'.csv'),fields,sorted(rows,key=lambda r:tuple(r[f] for f in ['owner_org','fiscal_yr','service_id']+(['service_standard_id'] if name=='service-std' else []))))
    for name,rows,fields in [
      ('organizations',owners,['owner_org','owner_org_title','institution_id','resolution','method','candidates']),
      ('programs',programs,['owner_org','program_id','name_en','name_fr','valid_fiscal_years','label_source']),
      ('service_program_links',links,['owner_org','fiscal_yr','service_id','program_id','vocabulary_year_status']),
      ('program_references',refs,['owner_org','fiscal_yr','service_id','program_id','resolution','vocabulary_year_status'])]:write_csv(output/(name+'.csv'),fields,rows)
    catalog=dict(dataset_type=definition['dataset_type'],title=definition['title'],source_url=SCHEMA_URL,sha256=hashlib.sha256(raw_schema).hexdigest(),resources=[])
    field_audit=[]
    id_fields={'owner_org':'join: exact registry open_canada_org_slug','owner_org_title':'context only; never substitute for organization ID','fiscal_yr':'annual observation key and temporal join guard','service_id':'organization-scoped service identity; annual observation key','service_standard_id':'service-scoped standard identity; annual standard observation key','program_id':'split repeated literal codes; join on owner_org + program_id; never strip -INV','program_name_en':'labels only; not positionally zipped to program IDs','program_name_fr':'labels only; not positionally zipped to program IDs'}
    for r in definition['resources']:
        fields=[]
        for f in r['fields']:
            reduced={k:v for k,v in f.items() if k!='choices'};reduced['choice_count']=len(f.get('choices',{}));fields.append(reduced)
            ident=f['id'];treatment=id_fields.get(ident)
            if not treatment:
                if 'uri_' in ident:treatment='source URL attribute; exact assessment-page matches only; no domain-only joins'
                elif ident in ('automated_decision_system','sin_usage','cra_bn_identifier_usage'):treatment='reported attribute, not an entity identifier or proof of an assessment/individual/business link'
                elif ident.startswith('automated_decision_system_description'):treatment='narrative attribute; explicit PIA URLs/identifiers may provide evidence, not title-similarity joins'
                elif f['datastore_type']=='_text':treatment='repeated categorical attribute; not extra graph nodes'
                else:treatment='annual source attribute; not an identity join'
            field_audit.append(dict(resource=r['resource_name'],field=ident,label_en=f['label']['en'],label_fr=f['label']['fr'],type=f['datastore_type'],treatment=treatment))
        catalog['resources'].append(dict(resource_name=r['resource_name'],title=r['title'],fields=fields,recombinant_key=['fiscal_yr','service_id']+(['service_standard_id'] if r['resource_name']=='service-std' else []),aggregate_key=['owner_org','fiscal_yr','service_id']+(['service_standard_id'] if r['resource_name']=='service-std' else [])))
    (output/'schema_fields.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    (output/'field_join_audit.json').write_text(json.dumps(field_audit,ensure_ascii=False,indent=2)+'\n')
    manifest=dict(schema_version=1,inspected_at_utc=datetime.now(timezone.utc).isoformat(),dataset_url=DATASET,schema_url=SCHEMA_URL,schema_sha256=catalog['sha256'],key_authority_url=YAML_URL,source_inputs=inputs,summary=dict(service_observations=len(tables['service'][1]),services=len({(r['owner_org'],r['service_id']) for r in tables['service'][1]}),standard_observations=len(tables['service-std'][1]),standards=len({(r['owner_org'],r['service_id'],r['service_standard_id']) for r in tables['service-std'][1]}),programs=len(programs),service_program_observations=len(links),program_reference_statuses=dict(Counter(r['resolution'] for r in refs)),organization_statuses=dict(Counter(r['resolution'] for r in owners)),fields_audited=len(field_audit)),outputs={})
    service_choices=next(f for f in resource_defs['service']['fields'] if f['id']=='service_id').get('choices',{})
    exceptions=[];identifier_statuses=Counter()
    for row in tables['service'][1]:
        choice=service_choices.get(row['service_id'])
        status='unknown_code' if not choice else 'owner_not_listed' if row['owner_org'] not in choice.get('valid_orgs',{}) else 'listed'
        identifier_statuses[status]+=1
        if status!='listed':exceptions.append({**{k:row[k] for k in ['owner_org','fiscal_yr','service_id']},'status':status,'catalog_owners':sorted(choice.get('valid_orgs',{})) if choice else []})
    manifest['summary']['service_identifier_statuses']=dict(identifier_statuses)
    manifest['service_identifier_exceptions']=sorted(exceptions,key=lambda r:(r['owner_org'],r['fiscal_yr'],r['service_id']))
    for p in sorted(output.glob('*')):
        if p.name!='manifest.json':manifest['outputs'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(manifest['summary']))
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--schema',required=True);p.add_argument('--services',required=True);p.add_argument('--standards',required=True);args=p.parse_args();import_files(args.schema,args.services,args.standards)
