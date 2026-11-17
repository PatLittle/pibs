"""Project Service Inventory identities and literal, year-evidenced joins."""
from collections import defaultdict
import hashlib
import json
from urllib.parse import urlencode, quote

DATASET='https://open.canada.ca/data/en/dataset/3ac0d080-6149-499a-8b06-7ce5f00ec56c'
SERVICE_RESOURCE='c0cf9766-b85b-48c3-b295-34f72305aaf6'
STANDARD_RESOURCE='8736cd7e-9bf9-4a45-9eee-a6cb3c43c07e'
BASE='data/service_inventory/'

def service_id(owner,code):return 'service:'+quote(owner,safe='')+':'+quote(code,safe='')

def program_id(owner,code):return 'program:'+quote(owner,safe='')+':'+quote(code,safe='')

def standard_id(owner,service,code):return 'service-standard:'+quote(owner,safe='')+':'+quote(service,safe='')+':'+quote(code,safe='')

def source_record(resource,filters):
    return 'https://open.canada.ca/data/en/api/3/action/datastore_search?'+urlencode({'resource_id':resource,'filters':json.dumps(filters,separators=(',',':')),'limit':100})

def add_service_inventory(root,read,nodes,add_node,add_edge):
    manifest=read(BASE+'manifest.json');read(BASE+'schema_fields.json');read(BASE+'field_join_audit.json')
    owners={r['owner_org']:r for r in read(BASE+'organizations.csv',True)}
    services=read(BASE+'service.csv',True);standards=read(BASE+'service-std.csv',True)
    programs=read(BASE+'programs.csv',True);links=read(BASE+'service_program_links.csv',True);refs=read(BASE+'program_references.csv',True)
    def institution(owner):return owners[owner]['institution_id'] or None
    def ev(row,path,field,mention,method,resource=SERVICE_RESOURCE):
        return dict(source_path=BASE+path,field=field,mention=mention,method=method,fiscal_yr=row.get('fiscal_yr',''),owner_org=row['owner_org'],source_url=source_record(resource,{k:row[k] for k in ('owner_org','fiscal_yr','service_id','service_standard_id') if row.get(k)}),source_sha256=manifest['outputs'][path],checked_at_utc=manifest['inspected_at_utc'])
    grouped=defaultdict(list)
    for row in services:grouped[(row['owner_org'],row['service_id'])].append(row)
    for (owner,code),rows in sorted(grouped.items()):
        rows.sort(key=lambda r:r['fiscal_yr']);latest=rows[-1];ident=service_id(owner,code);org=institution(owner)
        add_node(dict(id=ident,type='service',identifier=code,institution_id=org,owner_org=owner,
                      label_en=latest['service_name_en'],label_fr=latest['service_name_fr'],
                      description_en=latest['service_description_en'][:1000],description_fr=latest['service_description_fr'][:1000],
                      aliases=sorted({r[k] for r in rows for k in ('service_name_en','service_name_fr') if r[k]}),
                      sources={'inventory':DATASET},source_path=BASE+'service.csv',
                      record_url=source_record(SERVICE_RESOURCE,{'owner_org':owner,'service_id':code}),
                      attributes=dict(owner_org=owner,organization_resolution=owners[owner]['resolution'],fiscal_years=[r['fiscal_yr'] for r in rows],annual_observations=rows,identifier_catalog_exceptions=[r for r in manifest.get('service_identifier_exceptions',[]) if r['owner_org']==owner and r['service_id']==code])))
        if org:
            add_edge(ident,'institution:'+org,'listed_by',[{**ev(r,'service.csv','owner_org',owner,'exact_registry_open_canada_org_slug'),'registry_source_path':'institution_registry.csv','registry_field':'open_canada_org_slug'} for r in rows])
    for row in programs:
        owner=row['owner_org'];ident=program_id(owner,row['program_id']);org=institution(owner)
        add_node(dict(id=ident,type='program',identifier=row['program_id'],institution_id=org,owner_org=owner,
                      label_en=row['name_en'],label_fr=row['name_fr'],aliases=[],sources={'code_list':manifest['schema_url']},source_path=BASE+'programs.csv',
                      attributes={**row,'valid_fiscal_years':json.loads(row['valid_fiscal_years']),'identity_scope':'owner_org + program_id; no numeric GC InfoBase program ID is inferred'}))
        if org:
            add_edge(ident,'institution:'+org,'listed_by',[dict(source_path=BASE+'programs.csv',field='owner_org',mention=owner,method='exact_registry_open_canada_org_slug',source_url=manifest['schema_url'],source_sha256=manifest['outputs']['programs.csv'])])
    for row in links:
        add_edge(service_id(row['owner_org'],row['service_id']),program_id(row['owner_org'],row['program_id']),'under_program',
                 [{**ev(row,'service_program_links.csv','program_id',row['program_id'],'literal_service_program_code_and_owner'),'vocabulary_year_status':row['vocabulary_year_status']}])
    unknown=defaultdict(list)
    for row in refs:
        if row['resolution']!='resolved':unknown[(row['owner_org'],row['service_id'],row['program_id'])].append(row)
    for (owner,code,program),rows in sorted(unknown.items()):
        source=service_id(owner,code);ident='reference:service-program:'+hashlib.sha256(json.dumps([owner,code,program]).encode()).hexdigest()[:24]
        add_node(dict(id=ident,type='reference',identifier=program,institution_id=institution(owner),label_en=program,label_fr=program,reference_kind='program',resolution='unresolved',candidates=[],sources={'inventory':DATASET},attributes=dict(reported_status=rows[0]['resolution'],owner_org=owner,reported_fiscal_years=sorted({r['fiscal_yr'] for r in rows}),note='The -INV suffix is not removed. Invalid or unknown identifiers are not promoted into program entities.')))
        add_edge(source,ident,'references',[ev(r,'program_references.csv','program_id',program,'unresolved_literal_program_reference') for r in rows],'unresolved')
    grouped=defaultdict(list)
    for row in standards:grouped[(row['owner_org'],row['service_id'],row['service_standard_id'])].append(row)
    for (owner,service,code),rows in sorted(grouped.items()):
        rows.sort(key=lambda r:r['fiscal_yr']);latest=rows[-1];ident=standard_id(owner,service,code)
        add_node(dict(id=ident,type='service_standard',identifier=code,institution_id=institution(owner),owner_org=owner,
                      label_en=latest['service_standard_en'],label_fr=latest['service_standard_fr'],aliases=[code],sources={'inventory':DATASET},source_path=BASE+'service-std.csv',
                      record_url=source_record(STANDARD_RESOURCE,{'owner_org':owner,'service_id':service,'service_standard_id':code}),
                      attributes=dict(service_id=service,service_standard_id=code,owner_org=owner,fiscal_years=[r['fiscal_yr'] for r in rows],annual_observations=rows)))
        add_edge(service_id(owner,service),ident,'has_standard',[ev(r,'service-std.csv','service_standard_id',code,'exact_owner_year_service_foreign_key',STANDARD_RESOURCE) for r in rows])
