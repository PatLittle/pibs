#!/usr/bin/env python3
"""Build a versioned Info Source template family; source text is data, not instructions.

Use --source-dir for inspected Canada.ca EN/FR HTML and PIB DOCX snapshots.
Offline builds preserve sources.json and source-derived library.json.
"""
import argparse
import csv
import hashlib
import json
import re
import forms
import atip
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup

APP=Path(__file__).resolve().parents[1]
ROOT=APP.parents[1]
OUT=APP/'templates'
REQ='https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/access-informatio-policies-guidance/programs-holdings-online-publishing-requirements.html'
INTERNAL='https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/information-about-programs-information-holdings/internal-services.html'
FORM='https://www.canada.ca/content/dam/tbs-sct/documents/forms/personal-information-bank-submission-form-'
SCHEMA_ID='https://patlittle.github.io/pibs/document-studio/templates/document.schema.json'
VERSION='1.0.0'

def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def bi(en='',fr=''):return dict(en=en,fr=fr)
def text(en,fr,required=True,help=None):
    d={'type':'object','properties':{l:{'type':'string','minLength':1 if required else 0} for l in ['en','fr']},'required':['en','fr'],'additionalProperties':False,'x-ui':'bilingual','x-label':bi(en,fr)}
    if help:d['x-help']=help
    return d
def neutral(en,fr,**kw):
    definition=dict(type='string',**{'x-label':bi(en,fr)},**kw)
    if definition.get('format') and not definition.get('minLength',0):
        fmt=definition.pop('format');definition['x-input-format']=fmt;definition['anyOf']=[{'const':''},{'type':'string','format':fmt}]
    return definition
def enum(en,fr,values,default=None):return {**neutral(en,fr), 'enum':values,'default':default if default is not None else values[0]}
def ref(name,label=None):return {'$ref':'#/$defs/'+name,**({'x-label':bi(*label)} if label else {})}
def array(name,en,fr,minItems=0):return dict(type='array',items=ref(name),minItems=minItems,**{'x-label':bi(en,fr)})
def obj(kind,en,fr,properties,required=None,source=None):
    p={'kind':{'const':kind,'type':'string','x-hidden':True},'id':{'type':'string','minLength':1,'x-ui':'id'},**properties}
    return dict(type='object',properties=p,required=['kind','id']+(list(properties) if required is None else required),additionalProperties=False,**{'x-label':bi(en,fr),'x-source':source or 'project-model'})
def url(en,fr,required=False):return neutral(en,fr,format='uri',minLength=1 if required else 0,default='')

def source_library(directory):
    """Inspect every linked standard entry and Internal Services nesting, in both languages."""
    sources=[];pages={}
    for name in ['requirements','internal','classes','banks']:
        for suffix in ['', '-fr']:
            p=directory/(name+suffix+'.html');raw=p.read_bytes();s=BeautifulSoup(raw,'html.parser');pages[name+suffix]=s.find('main')
            en={'requirements':REQ,'internal':INTERNAL,'classes':'https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-classes-records.html','banks':'https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/info-source/standard-personal-information-banks.html'}[name]
            lang_link=s.select_one('a[lang="fr"]');source_url=urljoin(en,lang_link['href']) if suffix and lang_link else en
            modified=s.select_one('time[property="dateModified"]')
            sources.append(dict(id=name+suffix,url=source_url,language='fr' if suffix else 'en',sha256=hashlib.sha256(raw).hexdigest(),date_modified=modified.get_text(' ',strip=True) if modified else None))
    for lang in ['en','fr']:
        p=directory/('pib-form-'+lang+'.docx')
        sources.append(dict(id='pib-submission-'+lang,url=FORM+lang+'.docx',language=lang,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    def md(tag):
        clone=BeautifulSoup(str(tag),'html.parser')
        for a in clone.select('a[href]'):
            target=urljoin(REQ,a['href'])
            if urlsplit(target).scheme in ('http','https'):a.replace_with('['+a.get_text(' ',strip=True)+']('+target+')')
        if tag.name in ['ul','ol']:
            return '\n\n'.join(re.sub(r'[ \t\xa0]+',' ',li.get_text(' ',strip=True)).strip() for li in (clone.find(tag.name) or clone).find_all('li',recursive=False))
        return re.sub(r'[ \t\xa0]+',' ',clone.get_text(' ',strip=True)).strip()
    def clause(code):
        result={}
        for lang,suffix in [('en',''),('fr','-fr')]:
            main=pages['requirements'+suffix]
            start=next(p for p in main.find_all('p') if p.get_text(' ',strip=True).startswith(code+' '))
            chunks=[]
            for sib in start.next_siblings:
                if getattr(sib,'name',None) in ['h2','h3']:break
                if getattr(sib,'name',None)=='p' and re.match(r'^4\.\d+\s',sib.get_text(' ',strip=True)):break
                if getattr(sib,'name',None):chunks.append(md(sib))
            result[lang]='\n\n'.join(chunks)
        return result
    # Parse standard descriptions afresh, retaining paragraphs under each source entry.
    def entries(name,suffix):
        rows={}
        for h in pages[name+suffix].find_all(['h2','h3','h4'],id=True):
            if not re.match(r'^(?:prn|ndp|psu|pse|pou|poe)\d+[a-z]?$',h['id'],re.I):continue
            fields={};current=None
            for sib in h.next_siblings:
                if getattr(sib,'name',None) in ['h2','h3']:break
                if not getattr(sib,'name',None):continue
                strong=sib.find('strong')
                if strong:
                    label=strong.get_text(' ',strip=True).lower().rstrip(': \xa0');clone=BeautifulSoup(str(sib),'html.parser');clone.find('strong').decompose();current=label;fields[label]=md(clone)
                elif current:fields[current]+='\n\n'+md(sib)
            rows[h['id'].lower()]={'title':h.get_text(' ',strip=True),'fields':fields}
        return rows
    classes={};banks={}
    aliases={'description':['description'],'document_types':['document types','types de documents'],'note':['note','remarque'],'class_of_individuals':['class of individuals','catégorie de personnes','catégories de personnes'],'purpose':['purpose','but','fin'],'consistent_uses':['consistent uses','utilisations compatibles','usages compatibles'],'retention_disposal':['retention and disposal standards','normes de conservation et de destruction','normes de conservation et disposition'],'rda_number':['rda number','numéro add','numéro de add'],'related_record_number':['related record number','numéros de renvoi au document','numéro de renvoi au document'],'bank_number':['bank number','numéro du fichier']}
    parsed={(n,s):entries(n,s) for n in ['classes','banks'] for s in ['', '-fr']}
    for kind,path in [('cor','standard_classes_of_records_en_fr.csv'),('pib','spib_en_fr.csv')]:
        with (ROOT/path).open() as f:rows=list(csv.DictReader(f))
        for row in rows:
            ident=row['record_number'] if kind=='cor' else row['bank_number_key']
            payload={'kind':kind,'id':'library-'+kind+'-'+re.sub(r'\W+','-',ident).lower(),'scope':'standard','source_urls':[]}
            for key in ['title','description','note','document_types','class_of_individuals','purpose','consistent_uses','retention_disposal']:
                if kind=='cor' and key not in ['title','description','note','document_types']:continue
                if kind=='pib' and key=='document_types':continue
                payload[key]=bi()
            for lang,suffix in [('en',''),('fr','-fr')]:
                heading=(('prn' if lang=='en' else 'ndp')+ident) if kind=='cor' else row['entry_id_'+lang].lower()
                entry=parsed[('classes' if kind=='cor' else 'banks',suffix)].get(heading)
                if not entry and kind=='cor':entry=parsed[('classes',suffix)].get('prn'+ident)
                if not entry:raise ValueError('Missing bilingual standard entry '+heading)
                payload['title'][lang]=entry['title']
                for key in payload:
                    if key in aliases and isinstance(payload[key],dict):payload[key][lang]=next((v for k,v in entry['fields'].items() if k in aliases[key]),row.get(key+'_'+lang,''))
                payload['source_urls'].append(row['url_'+lang])
            if kind=='cor':
                payload.update(record_number=row['record_number_en'],record_number_fr=row['record_number_fr'],format=bi(),disclosure_status='not_reviewed',disclosures=[],no_disclosure_statement=bi(),pibs=[])
                classes[ident]=payload
            else:
                payload.update(bank_number=row['bank_number_en'],bank_number_fr=row['bank_number_fr'],approval_status='registered',registration_number='',sin_collection='not_reviewed',sin_authority=bi(),rda_number=next((v for k,v in parsed[('banks','')][row['entry_id_en'].lower()]['fields'].items() if k in aliases['rda_number']),''),related_record_numbers=[x.strip() for x in next((v for k,v in parsed[('banks','')][row['entry_id_en'].lower()]['fields'].items() if k in aliases['related_record_number']),row['related_record_number_en']).split(',') if x.strip()],last_updated='')
                banks[ident]=payload
    for name,records in [('classes',classes),('banks',banks)]:
        for suffix in ['', '-fr']:
            if len(parsed[(name,suffix)])!=len(records):raise ValueError('The official standard catalogue changed; review new or removed identifiers before rebuilding: '+name+suffix)
    link_exceptions=[]
    def group_rows(suffix):
        result=[]
        for h in pages['internal'+suffix].find_all('h2',id=True):
            siblings=[]
            for sib in h.next_siblings:
                if getattr(sib,'name',None)=='h2':break
                if getattr(sib,'name',None):siblings.append(sib)
            ul=next((x for x in siblings if x.name=='ul'),None);description='\n\n'.join(md(x) for x in siblings if x.name=='p');cors=[]
            if ul:
                for li in ul.find_all('li',recursive=False):
                    a=li.find('a');fragment=urlsplit(a.get('href','')).fragment.lower() if a else '';number=re.sub(r'^(prn|ndp|npd)','',fragment)
                    if fragment.startswith('npd'):link_exceptions.append(dict(language='fr',source_fragment=fragment,target_class=number,method='published_link_prefix_typo',note='Internal Services uses npd rather than ndp; the numeric standard-record key is retained and checked against the bilingual catalogue.'))
                    if number not in classes and suffix:
                        observed=a.get_text(' ',strip=True).casefold();matches=[k for k,v in classes.items() if v['title']['fr'].casefold() in observed]
                        if len(matches)==1:
                            number=matches[0];link_exceptions.append(dict(language='fr',source_fragment=fragment,target_class=number,source_label=a.get_text(' ',strip=True),method='unique_literal_current_title_in_source_label',note='The French Internal Services label names a current standard class but its old fragment uses a different number.'))
                        else:
                            link_exceptions.append(dict(language='fr',source_fragment=fragment,source_label=a.get_text(' ',strip=True),method='unresolved_published_class_link'));continue
                    if number not in classes:raise ValueError('Unresolved standard CoR '+fragment)
                    linked=[]
                    for sub in li.find_all('li'):
                        a=sub.find('a');code=urlsplit(a.get('href','')).fragment.lower() if a else '';code=re.sub(r'^poe','pse',re.sub(r'^pou','psu',code));bank=next((k for k,v in banks.items() if any(urlsplit(u).fragment.lower()==code for u in v['source_urls']) or re.sub(r'\W','',v['bank_number']).lower()==code),None)
                        if not bank:
                            language='fr' if suffix else 'en'
                            observed=a.get_text(' ',strip=True)
                            title=re.sub(r'\s+(?:Personal Information Bank|Fichier de renseignements personnels)\s*$', '',observed,flags=re.I).strip().casefold()
                            matches=[k for k,v in banks.items() if v['title'][language].strip().casefold()==title]
                            if len(matches)==1:
                                bank=matches[0];link_exceptions.append(dict(language=language,source_fragment=code,source_label=observed,target_bank=bank,method='unique_exact_source_title',note='Published Internal Services anchor differs from the current standard-bank anchor; no identifier-only guess.'))
                        if not bank:
                            legacy=re.match(r'^(ps[eu])(\d{3})$',code)
                            if legacy:
                                pattern=re.compile(r'\b'+legacy[1]+r'\s*'+legacy[2]+r'\b',re.I)
                                matches=[k for k,v in banks.items() if pattern.search(v.get('note',{}).get('en',''))]
                                if len(matches)==1:
                                    bank=matches[0];link_exceptions.append(dict(language='fr' if suffix else 'en',source_fragment=code,source_label=a.get_text(' ',strip=True),target_bank=bank,method='explicit_prior_identifier_in_current_source_note',evidence=banks[bank]['note']['en'],note='A published standard-bank note explicitly identifies the former PIB; repeated links to its successor are deduplicated within the class.'))
                        if not bank and code=='psu9072' and 'PSE 917' in banks['PSU 907']['note']['en'] and 'PSU 907' in banks['PSU 907']['note']['en']:
                            bank='PSU 907';link_exceptions.append(dict(language='fr' if suffix else 'en',source_fragment=code,source_label=a.get_text(' ',strip=True),target_bank=bank,method='curated_consolidation_from_explicit_source_note',evidence=banks[bank]['note']['en'],note='The Internal Services template still names the former surveillance/visitor-log bank. The current TBS note explicitly consolidates that bank and PSE 917 into Physical Access Controls.'))
                        if not bank and suffix:
                            link_exceptions.append(dict(language='fr',source_fragment=code,source_label=a.get_text(' ',strip=True),method='unresolved_published_link',note='Retained for audit. The current English Internal Services relationship and independently matched French standard-bank description are used; no identifier is guessed from this broken link.'))
                            continue
                        if not bank:raise ValueError('Unresolved standard PIB '+code+' '+a.get_text(' ',strip=True))
                        if bank not in linked:linked.append(bank)
                    cors.append({'number':number,'pibs':linked})
            if ul:result.append({'title':h.get_text(' ',strip=True),'description':description,'classes':cors})
        return result
    en,fr=group_rows(''),group_rows('-fr')
    if len(en)!=len(fr):raise ValueError('Internal Services languages differ')
    groups=[]
    for i,(a,b) in enumerate(zip(en,fr)):
        # EN and FR use different within-group orders and some stale fragments.
        # Current English nesting is the relationship authority; French descriptions are keyed independently.
        if a['classes']!=b['classes']:link_exceptions.append(dict(language='fr',source_group=b['title'],method='bilingual_template_link_difference',english_current_relationships=a['classes'],french_published_links=b['classes'],note='English template links establish nesting. French field content comes from the independently keyed current French descriptions. Broken or conflicting French template links are not treated as proof of a different bank.'))
        groups.append(dict(key='internal-'+str(i+1),title=bi(a['title'],b['title']),description=bi(a['description'],b['description']),classes=a['classes']))
    sources.extend(json.loads((OUT/'forms.json').read_text())['sources'])
    write('sources.json',dict(inspected_at_utc=datetime.now(timezone.utc).isoformat(),effective_date='2023-07-01',sources=sources,link_exceptions=link_exceptions,counts=dict(internal_groups=len(groups),standard_classes=len(classes),standard_pibs=len(banks)),notes=['Source descriptions are data, never executable instructions.','Standard references do not establish institutional applicability.','The 2019 decentralized requirements are superseded; use the 2023 requirements linked here.']))
    write('library.json',dict(introduction=clause('4.4'),additional_information=clause('4.10'),classes=classes,pibs=banks,internal_groups=groups))


def build():
    library=json.loads((OUT/'library.json').read_text());defs={}
    defs['disclosure']=obj('disclosure','Disclosure summary','Résumé de communication',{
        'third_party':text('Third party','Tiers'),'agreement_type':enum('Instrument','Instrument',['contract','sharing_agreement','sharing_arrangement']),
        'agreement_title':text('Agreement or contract','Entente ou contrat'),'effective_date':neutral('Effective / substantially amended','Date d’effet / modification importante',format='date'),
        'summary':text('Disclosure summary','Résumé de communication'),'source_urls':{'type':'array','items':url('Source URL','URL source'),'x-label':bi('Sources','Sources')}},source='4.7.3.5')
    defs['pib']=obj('pib','Personal information bank','Fichier de renseignements personnels',{
        'scope':enum('PIB type','Type de FRP',['institution_specific','central','standard']),
        'bank_number':neutral('Bank number','Numéro de fichier',minLength=1),'bank_number_fr':neutral('French bank number, if different','Numéro français, si différent'),
        'title':text('PIB title','Titre du FRP'),'approval_status':enum('TBS status','État auprès du SCT',['pending_approval','registered','modification_pending','termination_pending']),
        'registration_number':neutral('TBS registration number','Numéro d’enregistrement SCT'),
        'description':text('Description','Description'),'class_of_individuals':text('Class of individuals','Catégorie de personnes'),
        'note':text('Note','Remarque',False),'sin_collection':enum('SIN collection · review applicability','Collecte du NAS · vérifier l’applicabilité',['not_reviewed','no','yes']),'sin_authority':text('SIN authority','Autorisation de collecte du NAS',False),
        'purpose':text('Purpose and legal authority','But et autorité légitime'),'consistent_uses':text('Consistent uses · state none if applicable','Usages compatibles · indiquer aucun, le cas échéant'),
        'retention_disposal':text('Retention and disposal standards','Normes de conservation et de destruction'),
        'rda_number':neutral('RDA number','Numéro ADD'),'related_record_numbers':{'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True,'x-label':bi('Related CoR numbers','Numéros de renvoi aux documents')},
        'last_updated':neutral('Last substantially updated','Dernière modification importante',format='date'),
        'source_urls':{'type':'array','items':url('Source','Source'),'x-label':bi('Sources','Sources')}},source='4.7.4; PIB submission form B–N')
    defs['cor']=obj('cor','Class of records','Catégorie de documents',{
        'scope':enum('Scope','Portée',['institution_specific','standard']),'record_number':neutral('Record number','Numéro du document',minLength=1),'record_number_fr':neutral('French record number, if different','Numéro français, si différent'),
        'title':text('Record class title','Titre de la catégorie'),'note':text('Note','Remarque',False),'description':text('Records description','Description des documents'),
        'document_types':text('Document types','Types de documents'),'format':text('Non-standard formats, if applicable','Supports non ordinaires, le cas échéant',False),
        'disclosure_status':enum('Disclosure review','Examen des communications',['not_reviewed','none','disclosed']),
        'no_disclosure_statement':text('No applicable disclosures statement','Déclaration d’absence de communications applicables',False),
        'disclosures':array('disclosure','Disclosure summaries','Résumés de communication'),'pibs':array('pib','Related personal information banks','Fichiers de renseignements personnels connexes'),
        'source_urls':{'type':'array','items':url('Source','Source'),'x-label':bi('Sources','Sources')}},source='4.7.3')
    defs['activity']=obj('activity','Activity','Activité',{'title':text('Activity','Activité'),'description':text('Activity description','Description de l’activité'),'classes':array('cor','Classes of records','Catégories de documents')},source='4.7.2')
    defs['program']=obj('program','Program / internal service','Programme / service interne',{'program_id':neutral('Program ID, if known','ID du programme, si connu'),'title':text('Program','Programme'),'description':text('Program description','Description du programme'),'activities':array('activity','Activities · optional','Activités · facultatives'),'classes':array('cor','Classes directly under this program','Catégories directement liées au programme')},source='4.7.2; Appendix B')
    defs['personal_information_class']=obj('personal_information_class','Class of personal information','Catégorie de renseignements personnels',{'title':text('Title','Titre'),'description':text('Information held · no administrative use or personal retrieval','Renseignements détenus · sans usage administratif ou recherche par identifiant'),'retention_disposal':text('Retention and disposal, if applicable','Conservation et destruction, le cas échéant',False)},source='4.8; Appendix C')
    defs['manual']=obj('manual','Manual','Manuel',{'title':text('Manual title','Titre du manuel'),'description':text('Description, if useful','Description, si utile',False),'url_en':url('English manual URL','URL du manuel anglais'),'url_fr':url('French manual URL','URL du manuel français')},source='4.9')
    defs['program_assignment']=obj('program_assignment','Program assignment','Affectation à un programme',{
        'program_id':neutral('Program code / identifier','Code / identifiant du programme',minLength=1),
        'program_title':text('Program title','Titre du programme'),
        'owner_org':neutral('Organization code, if known','Code d’organisation, si connu'),
        'document_program_id':neutral('Linked program in this document','Programme lié dans ce document',default='',**{'x-hidden':True})},source='User-requested position/program assignment')
    defs['person']=obj('person','Senior role','Poste de cadre supérieur',{
        'name':neutral('Name','Nom',minLength=1),'position_title':text('Position title','Titre du poste'),
        'role_level':enum('Role level','Niveau du poste',['director_general','assistant_deputy_minister','associate_deputy_minister','deputy_head','equivalent_senior_role']),
        'classification_group':neutral('Classification group, if applicable','Groupe de classification, le cas échéant'),
        'classification_level':neutral('Classification level, if applicable','Niveau de classification, le cas échéant'),
        'position_number':neutral('Position number, if known','Numéro du poste, si connu'),'organization':text('Organization / unit','Organisation / unité'),
        'programs':array('program_assignment','Assigned programs','Programmes assignés',1),
        'reports_to':neutral('Reports to · choose a person in this document','Relève de · choisir une personne dans ce document',default=''),
        'effective_from':neutral('Effective from, if known','En vigueur à compter du, si connu',format='date'),'effective_to':neutral('Effective to, if known','Jusqu’au, si connu',format='date'),
        'source_url':url('Official source, if available','Source officielle, si disponible')},source='User-requested extension; not a TBS Info Source requirement')
    defs['organization_chart']=obj('organization_chart','Organization chart · DG and above','Organigramme · DG et supérieurs',{'title':text('Chart title','Titre de l’organigramme'),'people':array('person','People and reporting lines','Personnes et liens hiérarchiques',1)},source='User-requested extension')
    defs['pib_submission']=obj('pib_submission','PIB submission form · A–N','Formulaire de présentation d’un FRP · A–N',{
        'institution_name':text('A · Institution','A · Institution'),'contact_name':neutral('A · Contact name','A · Nom de la personne-ressource',minLength=1),'contact_title':text('A · Contact title','A · Titre de la personne-ressource'),
        'telephone':neutral('A · Telephone','A · Téléphone',minLength=1),'email':neutral('A · Email','A · Courriel',format='email',minLength=1),
        'pia_or_protocol_provided':enum('A · PIA or protocol provided','A · EFVP ou protocole fourni',['yes','no']),'comments':text('A · Additional comments','A · Commentaires',False),
        'program_name':text('B · Program or activity name','B · Nom du programme ou activité'),
        'request_type':enum('D · Submission type','D · Type de présentation',['new','modify_registered','modify_pending','transfer','terminate']),
        'current_registration_number':neutral('D · Existing TBS number','D · Numéro SCT existant'),
        'transfer_explanation':text('D · Reason for transfer','D · Motif du transfert',False),'transfer_confirmations':text('D · Both section 10 officials’ confirmations / references','D · Confirmations des deux responsables de l’article 10 / références',False),
        'termination_explanation':text('D · Reason for termination','D · Motif de la suppression',False),'termination_confirmation':text('D · Section 10 disposal confirmation / reference','D · Confirmation de destruction du responsable de l’article 10 / référence',False),
        'bank':ref('pib',('C, E–N · Bank description','C, E–N · Description du fichier'))},source='Official PIB submission form A–N; Annexes A/B in source Word forms')
    defs['annual_update']=obj('annual_update','Annual update notification draft','Brouillon d’avis de mise à jour annuelle',{
        'institution_name':text('Institution','Institution'),'page_url_en':url('English Info Source URL','URL Info Source anglaise',True),'page_url_fr':url('French Info Source URL','URL Info Source française',True),
        'changes':text('Major changes, or state no changes','Modifications importantes, ou indiquer aucune modification'),'new_sin_programs':text('New programs collecting SIN, or none','Nouveaux programmes recueillant le NAS, ou aucun'),
        'feedback_response':text('Response to TBS feedback, if applicable','Réponse aux commentaires du SCT, le cas échéant',False)},source='4.3.1–4.3.4; draft only, nothing is sent')
    contact={'type':'object','properties':{'official_title':text('ATIP delegated official / head title','Titre du responsable délégué AIPRP / administrateur général'),'mailing_address':text('Mailing address','Adresse postale'),'informal_contact':text('General informal enquiries · not the ATIP office','Demandes informelles générales · pas le bureau AIPRP'),'fee_payee':text('Cheque / money order payee','Bénéficiaire du chèque / mandat'),'completed_requests_url_en':url('Completed requests URL · EN','URL des demandes traitées · EN',True),'completed_requests_url_fr':url('Completed requests URL · FR','URL des demandes traitées · FR',True),'pia_summaries_url_en':url('PIA summaries URL · EN','URL des résumés d’EFVP · EN',True),'pia_summaries_url_fr':url('PIA summaries URL · FR','URL des résumés d’EFVP · FR',True),'open_data_url_en':url('Open data URL · EN, if applicable','URL des données ouvertes · EN, le cas échéant'),'open_data_url_fr':url('Open data URL · FR, if applicable','URL des données ouvertes · FR, le cas échéant'),'standard_text':{**text('Additional information · publication text','Renseignements supplémentaires · texte publié'),'const':library['additional_information'],'default':library['additional_information'],'readOnly':True,'x-template':'additional_information'}},'required':['official_title','mailing_address','informal_contact','fee_payee','completed_requests_url_en','completed_requests_url_fr','pia_summaries_url_en','pia_summaries_url_fr','open_data_url_en','open_data_url_fr','standard_text'],'additionalProperties':False,'x-label':bi('Additional information','Renseignements supplémentaires'),'x-source':'4.10'}
    defs['infosource']=obj('infosource','Info Source · complete publication','Info Source · publication complète',{
        'institution_id':neutral('Institution ID, if known','ID de l’institution, si connu'),'institution_name':text('Institution','Institution'),'last_updated':neutral('Last updated','Dernière mise à jour',format='date',minLength=1),
        'introduction':{**text('Introduction to Info Source','Introduction à Info Source'),'const':library['introduction'],'default':library['introduction'],'readOnly':True,'x-source':'4.4'},
        'background':{'type':'object','properties':{'history':text('History · description or labelled links','Historique · description ou liens nommés'),'legislative_basis':text('Legislative foundation','Fondement législatif'),'parliament_reporting':text('Reporting to Parliament','Responsabilité devant le Parlement'),'subsidiary_statement':text('Subsidiary reporting statement, if applicable','Déclaration pour les filiales, le cas échéant',False),'subsidiaries':{'type':'array','items':text('Subsidiary','Filiale'),'x-label':bi('Subsidiaries without a separate page','Filiales sans page distincte')}},'required':['history','legislative_basis','parliament_reporting','subsidiary_statement','subsidiaries'],'additionalProperties':False,'x-label':bi('Background','Contexte'),'x-source':'4.5'},
        'responsibilities':{'type':'object','properties':{'mandate':text('Mandate','Mandat'),'program_responsibilities':text('Program responsibilities','Responsabilités des programmes'),'major_policies':text('Major policies','Principales politiques')},'required':['mandate','program_responsibilities','major_policies'],'additionalProperties':False,'x-label':bi('Responsibilities','Responsabilités'),'x-source':'4.6'},
        'institution_specific':array('program','Institution-specific programs and activities','Programmes et activités propres à l’institution'),
        'internal_services':array('program','Internal services · select applicable groups','Services internes · choisir les groupes applicables'),
        'personal_information_classes':array('personal_information_class','Classes of personal information','Catégories de renseignements personnels'),
        'manuals':array('manual','Manuals · sorted by title on export','Manuels · triés par titre à l’exportation'),
        'additional_information':contact,'people':array('person','People · DG and above / organization chart','Personnes · DG et supérieurs / organigramme')},source='4.1–4.10; People is a user-requested extension')
    defs['participating_institution']=obj('participating_institution','Participating institution','Institution participante',{
        'institution_name':text('Institution name','Nom de l’institution'),
        'branch':text('Branch, if applicable','Direction générale, le cas échéant',False),
        'directorate':text('Directorate, if applicable','Direction, le cas échéant',False),
        'program_official_name':neutral('Executive responsible for the program','Cadre responsable du programme',minLength=1),
        'program_official_title':text('Executive position title','Titre du poste du cadre'),
        'privacy_official_name':neutral('Delegated privacy official','Responsable délégué de la protection des renseignements personnels',minLength=1),
        'privacy_official_title':text('Privacy official position title','Titre du poste du responsable de la protection des renseignements personnels'),
        'roles_responsibilities':text('Roles and responsibilities','Rôles et responsabilités')},source='Multi-institutional PIA / privacy-checklist sections')
    public_kinds=list(defs)
    form_data=json.loads((OUT/'forms.json').read_text())
    form_kinds,form_coverage=forms.extend(defs,form_data,bi,text,neutral,enum,obj,ref,array)
    public_kinds.extend(form_kinds)
    atip_data=json.loads((OUT/'atip.json').read_text())
    atip_kinds,atip_coverage=atip.extend(defs,atip_data,bi,text,neutral,enum,obj,ref,array)
    public_kinds.extend(atip_kinds)
    # All validation keywords here are supported in the browser and independently checked with Draft 2020-12.
    metadata_fields={'title':text('PDF title','Titre du PDF',False),'description':text('Description / abstract','Description / résumé',False),'copyright_notice':text('Copyright notice','Mention de droit d’auteur',False),'rights_usage_terms':text('Rights and usage terms','Conditions d’utilisation',False)}
    for key,en,fr in [('creators','Creators / authors','Créateurs / auteurs'),('keywords','Keywords','Mots-clés'),('subject_codes','IPTC subject codes','Codes de sujet IPTC'),('scene_codes','IPTC scene codes','Codes de scène IPTC')]:metadata_fields[key]={'type':'array','items':{'type':'string','minLength':1},'uniqueItems':True,'x-label':bi(en,fr)}
    for key,en,fr in [('creator_job_title','Creator job title','Titre du poste du créateur'),('credit','Credit / provider','Crédit / fournisseur'),('source','Source','Source'),('headline','Headline','Titre principal'),('caption_writer','Description writer','Auteur de la description'),('instructions','Handling instructions','Consignes de traitement'),('intellectual_genre','IPTC intellectual genre','Genre intellectuel IPTC'),('country_code','IPTC country code','Code de pays IPTC'),('contact_phone','Creator telephone','Téléphone du créateur'),('contact_address','Creator address','Adresse du créateur'),('contact_city','City','Ville'),('contact_region','Region / province','Région / province'),('contact_postal_code','Postal code','Code postal'),('contact_country','Country','Pays')]:metadata_fields[key]=neutral(en,fr)
    for key,en,fr in [('rights_url','Rights statement URL','URL des droits'),('digital_source_type','IPTC digital source type URI','URI du type de source numérique IPTC'),('contact_url','Creator website','Site Web du créateur')]:metadata_fields[key]=url(en,fr)
    metadata_fields['contact_email']=neutral('Creator email','Courriel du créateur',format='email');metadata_fields['creation_date']=neutral('Creation date, if known','Date de création, si connue',format='date')
    metadata_fields['additional_properties']={'type':'array','items':{'type':'object','properties':{'namespace':neutral('Namespace URI','URI de l’espace de noms',minLength=1),'prefix':neutral('Prefix','Préfixe',minLength=1),'property':neutral('Property','Propriété',minLength=1),'type':{'enum':['text','bag','seq','lang_alt','structure']},'value':{'type':'string'}},'required':['namespace','prefix','property','type','value'],'additionalProperties':False},'x-label':bi('Additional XMP / IPTC properties','Propriétés XMP / IPTC supplémentaires')}
    pdf_metadata={'type':'object','properties':metadata_fields,'additionalProperties':False,'x-label':bi('PDF metadata','Métadonnées du PDF')}
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':SCHEMA_ID,'title':'Bilingual Info Source document envelope','type':'object','properties':{'schema_version':{'const':VERSION},'schema_id':{'const':SCHEMA_ID},'document_id':{'type':'string','minLength':1},'status':{'enum':['draft','review_ready']},'payload':{'oneOf':[ref(k) for k in public_kinds]}},'required':['schema_version','schema_id','document_id','status','payload'],'additionalProperties':False,'$defs':defs}
    schema['properties']['metadata']=pdf_metadata
    write('document.schema.json',schema)
    templates=[]
    for key in public_kinds:
        definition=defs[key]
        if key=='person':continue
        templates.append(dict(id=key,kind=key,title=definition['x-label'],category='publication' if key in ['infosource','organization_chart','pib_submission','annual_update']+form_kinds+atip_kinds else 'component',source=definition['x-source'],seed=None))
    for key,payload in library['classes'].items():templates.append(dict(id='standard-cor-'+key,kind='cor',title=payload['title'],category='standard_cor',source='classes',seed=payload))
    for key,payload in library['pibs'].items():templates.append(dict(id='standard-pib-'+key.lower().replace(' ','-'),kind='pib',title=payload['title'],category='standard_pib',source='banks',seed=payload))
    for group in library['internal_groups']:
        classes=[]
        for item in group['classes']:
            payload=json.loads(json.dumps(library['classes'][item['number']]))
            payload['pibs']=[library['pibs'][k] for k in item['pibs']];classes.append(payload)
        seed=dict(kind='program',id=group['key'],program_id='',title=group['title'],description=group['description'],activities=[],classes=classes)
        templates.append(dict(id=group['key'],kind='program',title=group['title'],category='internal_service',source='internal',seed=seed))
    register={r['kind']:r for r in atip_data['register']}
    for template in templates:
        if template['kind'] in register:template['form']=register[template['kind']]
    write('catalogue.json',dict(schema_version=VERSION,templates=templates,atip_forms=atip_data['register']))
    with (ROOT/'data/service_inventory/programs.csv').open() as f:programs=list(csv.DictReader(f))
    write('programs.json',dict(source='data/service_inventory/programs.csv',sha256=hashlib.sha256((ROOT/'data/service_inventory/programs.csv').read_bytes()).hexdigest(),note='Organization-scoped program codes observed in Service Inventory. These are suggested identifiers, not inferred assignments or current tenure.',programs=[dict(program_id=r['program_id'],owner_org=r['owner_org'],program_title=bi(r['name_en'],r['name_fr'])) for r in programs]))
    requirements=[dict(id=key,source=REQ,template=kind,coverage=description) for key,kind,description in [
      ('4.1.3','infosource','Last-updated date'),('4.3','annual_update','Bilingual links, changes, SIN programs and feedback response'),('4.4','infosource','Fixed bilingual introduction'),('4.5','infosource','History, legislative foundation, parliamentary reporting and subsidiaries'),('4.6','infosource','Mandate, program responsibilities and major policies'),('4.7.2','program','Repeatable programs, optional activities, classes and adjacent PIBs'),('4.7.3','cor','Title, note, records description, document types, disclosure summaries, format and number'),('4.7.4','pib','Registered and pending-status PIBs with bilingual notes'),('4.7.6','program','All 11 Internal Services groups, selected for applicability'),('4.8','personal_information_class','Repeatable classes of personal information'),('4.9','manual','Repeatable manuals, sorted by title in exported Markdown'),('4.10','infosource','Required access/contact fields and official additional-information wording'),('PIB A–N','pib_submission','All sections of the bilingual submission form; annexes remain source references'),('PROJECT-ORG','person','User-requested reporting links, name, position, classification and required program assignments')]]
    write('requirements.json',dict(schema_version=VERSION,requirements=requirements,form_fields=form_coverage,forms=[dict(kind=k,sections=len(form_data['forms'][k]['en'])) for k in form_kinds],supported_kinds=public_kinds,atip_fields=atip_coverage,atip_forms=atip_data['register']))
    print(dict(templates=len(templates),kinds=len(defs),**json.loads((OUT/'sources.json').read_text())['counts']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path);p.add_argument('--atip-source-dir',type=Path);args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if args.atip_source_dir:atip.capture(args.atip_source_dir,OUT)
    if args.source_dir:
        forms.capture(args.source_dir,OUT)
        source_library(args.source_dir)
    build()
