"""Capture the ATIP form register and static fields; never run PDF JavaScript."""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

SPECS=[
('access_request','350-57','Access to Information Request','Demande d’accès à l’information','access','official_request'),
('personal_information_request','350-58','Personal Information Request','Demande de renseignements personnels','access','official_request'),
('request_consent','350-60e','Consent for a Personal Information Request','Consentement pour une demande de renseignements personnels','access','official_signature'),
('request_authorization','350-55e','Authorization to Make a Personal Information Request','Autorisation de présenter une demande de renseignements personnels','access','official_signature'),
('record_correction','350-11','Record Correction Request','Demande de correction de dossier','access','official_request'),
('access_statistics','350-62','Statistical Report on the Access to Information Act','Rapport statistique sur la Loi sur l’accès à l’information','access','official_xml_xls'),
('privacy_statistics','350-63','Statistical Report on the Privacy Act','Rapport statistique sur la Loi sur la protection des renseignements personnels','access','official_xml_xls'),
('material_privacy_breach','350-64e','Privacy Act Material Breach Report','Rapport d’atteinte substantielle à la vie privée','privacy','official_dynamic_pdf'),
('privacy_checklist','350-65e','Privacy Checklist','Liste de vérification relative à la protection de la vie privée','privacy','prescribed_word'),
('privacy_impact_assessment','350-66e','Privacy Impact Assessment','Évaluation des facteurs relatifs à la vie privée','privacy','prescribed_word'),
('pib_submission','350-67e','Personal Information Bank Submission','Présentation d’un fichier de renseignements personnels','privacy','prescribed_word'),
('pia_web_summary','350-68e','Privacy Impact Assessment Web Summary','Résumé Web de l’évaluation des facteurs relatifs à la vie privée','privacy','prescribed_word'),
('privacy_protocol','350-69e','Privacy Protocol · non-mandatory template','Protocole de protection des renseignements personnels · modèle non obligatoire','privacy','adaptable_word_template')]
WORD={'privacy_checklist':'privacy-checklist-template','privacy_impact_assessment':'privacy-impact-assessment-template','pib_submission':'personal-information-bank-submission-form','pia_web_summary':'privacy-impact-assessment-web-summary-template','privacy_protocol':'privacy-protocol-template'}

def urls(kind,code):
 if kind in WORD:return {l:'https://www.canada.ca/content/dam/tbs-sct/documents/forms/'+WORD[kind]+'-'+l+'.docx' for l in ['en','fr']}
 if kind=='material_privacy_breach':return {'en':'https://www.canada.ca/content/dam/tbs-sct/documents/forms/350-64e-eng.pdf','fr':'https://www.canada.ca/content/dam/tbs-sct/documents/forms/350-64f-fra.pdf'}
 return {l:'https://www.canada.ca/'+('en/treasury-board-secretariat/corporate/forms/' if l=='en' else 'fr/secretariat-conseil-tresor/organisation/formulaires/')+code+'.html' for l in ['en','fr']}

def capture(directory,out):
 register=[];sources=[];html={}
 for kind,code,en,fr,group,mode in SPECS:
  links=urls(kind,code);number=code.upper();number_fr=number[:-1]+'F' if number.endswith('E') else number
  register.append(dict(kind=kind,number='TBS/SCT '+number,number_fr='TBS/SCT '+number_fr,title={'en':en,'fr':fr},group=group,completion_mode=mode,official_sources=links))
  if kind in WORD:continue
  if kind=='material_privacy_breach':continue
  pages={}
  for lang in ['en','fr']:
   p=directory/(code+'-'+lang+'.html');raw=p.read_bytes();main=BeautifulSoup(raw,'html.parser').find('main');pages[lang]=main
   sources.append(dict(id=kind+'-'+lang,language=lang,url=links[lang],sha256=hashlib.sha256(raw).hexdigest()))
  html[kind]={l:{'title':m.find('h1').get_text(' ',strip=True),'text':m.get_text('\n',strip=True)} for l,m in pages.items()}
  if 'statistics' in kind:html[kind]['metrics']=capture_metrics(pages)
 breach=capture_breach(directory);sources.extend(breach.pop('sources'))
 (out/'atip.json').write_text(json.dumps(dict(register=register,sources=sources,html=html,breach=breach),ensure_ascii=False,indent=2)+'\n')

def capture_metrics(pages):
 def fields(main):
  result=[];labels={x.get('for'):x for x in main.find_all('label',attrs={'for':True})};tables=main.find_all('table');table_indices={id(t):i for i,t in enumerate(tables)};row_indices={id(t):{id(r):i for i,r in enumerate(t.find_all('tr'))} for t in tables}
  for field in main.find_all('input'):
   ident=field.get('id');label=labels.get(ident);table=field.find_parent('table');context=field.get('title') or (label.get_text(' ',strip=True) if label else ident)
   coordinate=None;caption='Reporting period / Institution'
   if table:
    row=field.find_parent('tr');cell=field.find_parent(['td','th']);cells=row.find_all(['td','th'],recursive=False)
    coordinate=[table_indices[id(table)],row_indices[id(table)][id(row)],next(i for i,c in enumerate(cells) if c is cell),next(i for i,c in enumerate(cell.find_all('input')) if c is field)]
    c=table.find('caption');caption=c.get_text(' ',strip=True) if c else 'Table '+str(coordinate[0]+1)
   result.append(dict(id=ident,label=context,coordinate=coordinate,caption=caption))
  return result
 en,fr=fields(pages['en']),fields(pages['fr']);by_id={};by_coord={tuple(x['coordinate']):i for i,x in enumerate(fr) if x['coordinate']};used=set();rows=[];exceptions=[]
 for index,field in enumerate(fr):by_id.setdefault(field['id'],[]).append(index)
 for field in en:
  candidates=[i for i in by_id.get(field['id'],[]) if i not in used]
  coordinate=tuple(field['coordinate']) if field['coordinate'] else None;at_coordinate=by_coord.get(coordinate);method='exact_source_id'
  if at_coordinate in candidates:index=at_coordinate
  elif len(candidates)==1:index=candidates[0]
  elif at_coordinate is not None and at_coordinate not in used:index=at_coordinate;method='same_table_row_cell'
  else:raise ValueError('Missing/ambiguous French statistic field '+field['id'])
  partner=fr[index];used.add(index)
  if method!='exact_source_id' or partner['id']!=field['id']:exceptions.append(dict(en=field['id'],fr=partner['id'],coordinate=field['coordinate'],method=method))
  rows.append(dict(en=field,fr=partner,alignment=method))
 for index,field in enumerate(fr):
  if index not in used:
   rows.append(dict(en=None,fr=field,alignment='french_only_source_field'));exceptions.append(dict(fr=field['id'],method='french_only_source_field'))
 return dict(fields=rows,exceptions=exceptions,source_counts=dict(en=len(en),fr=len(fr)))

def capture_breach(directory):
 from pdfminer.pdfparser import PDFParser
 from pdfminer.pdfdocument import PDFDocument
 from pdfminer.pdftypes import resolve1
 from pdfminer.psparser import PSLiteral
 from pdfminer.utils import decode_text
 import pdfplumber
 def value(v):
  v=resolve1(v)
  if isinstance(v,bytes):return decode_text(v)
  if isinstance(v,PSLiteral):return v.name
  if isinstance(v,list):return [value(x) for x in v]
  return v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
 languages={};pages={};sources=[]
 for lang,name in [('en','350-64e-eng.pdf'),('fr','350-64-fr.pdf')]:
  p=directory/name;raw=p.read_bytes();sources.append(dict(id='material_privacy_breach-'+lang,language=lang,url=urls('material_privacy_breach','350-64e')[lang],sha256=hashlib.sha256(raw).hexdigest()))
  with p.open('rb') as stream:
   document=PDFDocument(PDFParser(stream));form=resolve1(document.catalog['AcroForm']);rows=[]
   def walk(ref,parent=None,prefix=''):
    field=resolve1(ref);name=value(field.get('T',''));key='.'.join(x for x in [prefix,name] if x);ft=value(field.get('FT',(parent or {}).get('FT')));kids=resolve1(field.get('Kids',[]));named=[k for k in kids if 'T' in resolve1(k)]
    if named:
     for kid in named:walk(kid,field,key)
    elif name:rows.append(dict(id=key,label=value(field.get('TU','')) or name,type=ft,flags=value(field.get('Ff',0)),max_length=value(field.get('MaxLen')),options=value(field.get('Opt',[]))))
   for item in resolve1(form['Fields']):walk(item)
  languages[lang]={r['id']:r for r in rows}
  with pdfplumber.open(p) as pdf:pages[lang]=[page.extract_text() or '' for page in pdf.pages]
 if set(languages['en'])!=set(languages['fr']):raise ValueError('Breach form EN/FR field identities changed; review before capture')
 return dict(fields=[dict(id=k,en=v,fr=languages['fr'][k]) for k,v in languages['en'].items()],pages=pages,sources=sources)


def extend(defs,data,bi,text,neutral,enum,obj,ref,array):
 public=[];coverage=[]
 def choice(en,fr,values):return {**neutral(en,fr,minLength=1),'enum':['']+list(values),'default':'','x-enum-labels':{k:bi(*v) for k,v in values.items()}}
 def identity(kind,en,fr):
  defs[kind]=obj(kind,en,fr,{'family_name':neutral('Family name','Nom de famille',minLength=1),'given_names':neutral('Given names','Prénoms',minLength=1),'address':neutral('Postal address','Adresse postale',minLength=1),'telephone':neutral('Telephone','Téléphone'),'email':neutral('Email','Courriel',format='email'),'fax':neutral('Fax, if used','Télécopieur, le cas échéant')},source='Official ATIP request forms')
  return ref(kind)
 contact=identity('atip_request_contact','Contact information','Coordonnées')
 common={'institution':text('Government institution','Institution fédérale'),'requester':contact}
 correspondence={'preferred_language':choice('Preferred correspondence language','Langue de correspondance souhaitée',{'en':('English','Anglais'),'fr':('French','Français')}),'preferred_method':choice('Preferred correspondence method','Mode de correspondance souhaité',{'email':('Email','Courriel'),'telephone':('Telephone','Téléphone'),'letter':('Letter','Lettre'),'fax':('Fax','Télécopieur')})}
 access_method=choice('Access method','Mode d’accès',{'electronic':('Electronic copies','Copies électroniques'),'paper':('Paper copies','Copies papier'),'onsite':('Examine at government offices','Consultation dans les bureaux du gouvernement')})
 ack=choice('Privacy notice acknowledgement','Reconnaissance de l’avis de confidentialité',{'acknowledged':('I acknowledge the source privacy notice','Je reconnais l’avis de confidentialité officiel')})
 specs={
 'access_request':{**common,'requested_records':text('Records sought · subject, dates and record types','Documents recherchés · sujet, dates et types'),'access_method':access_method,'eligibility':choice('Right of access','Admissibilité',{'citizen':('Canadian citizen','Citoyen canadien'),'permanent_resident':('Permanent resident','Résident permanent'),'present_in_canada':('Individual present in Canada','Personne présente au Canada'),'corporation':('Corporation present in Canada','Société présente au Canada')}),'applicant_category':choice('Applicant category','Catégorie de demandeur',{'media':('Media','Médias'),'academia':('Academia','Milieu universitaire'),'business':('Business organization','Entreprise'),'public':('Member of the public','Membre du public'),'decline':('Decline to identify','Refus de préciser')}),'request_date':neutral('Date','Date',format='date',minLength=1)},
 'personal_information_request':{**common,'privacy_notice':ack,'eligibility':choice('Requester status','Statut du demandeur',{'citizen_resident':('Canadian citizen or permanent resident','Citoyen canadien ou résident permanent'),'foreign_present':('Foreign national present in Canada','Ressortissant étranger présent au Canada'),'foreign_outside':('Foreign national outside Canada','Ressortissant étranger à l’extérieur du Canada')}),**correspondence,'information_language':choice('Requested information language','Langue des renseignements demandés',{'as_is':('As held','Telle quelle'),'en':('English','Anglais'),'fr':('French','Français')}),'request_description':text('Request description','Description de la demande'),'access_method':access_method,'attestation':choice('Attestation','Attestation',{'self':('About myself','À mon sujet'),'with_consent':('Includes another person’s information with consent','Comprend des renseignements sur une autre personne avec consentement'),'authorized':('On behalf of another person with authority','Au nom d’une autre personne avec autorisation'),'deceased':('About a deceased person with authority','Au sujet d’une personne décédée avec autorisation')}),'request_date':neutral('Date','Date',format='date',minLength=1)},
 'request_consent':{**common,'privacy_notice':ack,'request_description':text('Request for which consent is given','Demande faisant l’objet du consentement'),'consenting_individual':contact,'date_of_birth':neutral('Consenting individual’s date of birth','Date de naissance de la personne consentante',format='date',minLength=1),'relationship':text('Relationship to requester','Lien avec le demandeur'),'requester_signature_name':neutral('Requester signatory · typed name is not a digital signature','Signataire demandeur · le nom saisi n’est pas une signature numérique',minLength=1),'requester_signed_date':neutral('Requester signature date','Date de signature du demandeur',format='date',minLength=1),'consenting_signature_name':neutral('Consenting signatory · complete official signature separately','Signataire consentant · compléter la signature officielle séparément',minLength=1),'consenting_signed_date':neutral('Consent signature date','Date de signature du consentement',format='date',minLength=1)},
 'request_authorization':{**common,'privacy_notice':ack,'authorized_representative':contact,'relationship':text('Representative’s relationship to requester','Lien du représentant avec le demandeur'),'request_description':text('Request being authorized','Demande faisant l’objet de l’autorisation'),'requester_signature_name':neutral('Requester signatory · complete official signature separately','Signataire demandeur · compléter la signature officielle séparément',minLength=1),'requester_signed_date':neutral('Requester signature date','Date de signature du demandeur',format='date',minLength=1),'representative_signature_name':neutral('Authorized representative signatory','Signataire représentant autorisé',minLength=1),'representative_signed_date':neutral('Representative signature date','Date de signature du représentant',format='date',minLength=1)},
 'record_correction':{**common,'privacy_notice':ack,**correspondence,'previous_request_number':neutral('Previous personal-information request file number','Numéro du dossier de demande antérieure',minLength=1),'records_concerned':text('Records or items concerned','Documents ou éléments concernés'),'corrections_requested':text('Corrections requested','Corrections demandées'),'attestation':choice('Attestation','Attestation',{'self':('About myself','À mon sujet'),'authorized':('On behalf of another person with authority','Au nom d’une autre personne avec autorisation'),'deceased':('About a deceased person with authority','Au sujet d’une personne décédée avec autorisation')}),'request_date':neutral('Date','Date',format='date',minLength=1)}
 }
 for kind,properties in specs.items():
  record=next(r for r in data['register'] if r['kind']==kind);payload={'title':{**text('Document title','Titre du document'),'default':record['title']},'source_guidance':{**text('Official source guidance','Consignes officielles',False),'const':bi(data['html'][kind]['en']['text'],data['html'][kind]['fr']['text']),'default':bi(data['html'][kind]['en']['text'],data['html'][kind]['fr']['text']),'readOnly':True,'x-guidance':True},**properties}
  defs[kind]=obj(kind,*record['title'].values(),payload,source=record['number']);public.append(kind)
 for kind in ['access_statistics','privacy_statistics']:
  record=next(r for r in data['register'] if r['kind']==kind);properties={'title':{**text('Document title','Titre du document'),'default':record['title']}}
  groups={}
  for i,row in enumerate(data['html'][kind]['metrics']['fields']):
   en=row['en'];fr=row['fr'];coord=(en or fr)['coordinate'];group='table_'+str(coord[0]+1).zfill(2) if coord else 'reporting_information';key='cell_'+str(i+1).zfill(4)
   title=bi(en['label'] if en else fr['label'],fr['label']);label_en=en['caption'] if en else fr['caption'];label_fr=fr['caption'];entry=groups.setdefault(group,{'title':bi(label_en,label_fr),'fields':{}})
   if (en or fr)['id']=='NameOfInstitution':rule=text(title['en'],title['fr'])
   elif (en or fr)['id'] in ['ReportingPeriodStart','ReportingPeriodEnd']:rule=neutral(title['en'],title['fr'],format='date',minLength=1)
   else:rule={**neutral(title['en'],title['fr'],minLength=1),'pattern':r'^\d+(?:\.\d+)?$','x-numeric':True}
   rule['x-source-field-ids']={l:(row[l]['id'] if row[l] else None) for l in ['en','fr']};entry['fields'][key]=rule
   coverage.append(dict(document_type=kind,field=group+'/'+key,source_ids=rule['x-source-field-ids'],alignment=row['alignment']))
  for group,entry in groups.items():
   key=kind+'_'+group;defs[key]=obj(key,entry['title']['en'],entry['title']['fr'],entry['fields'],source=record['number']);defs[key]['x-statistical-table']=True;properties[group]=ref(key)
  defs[kind]=obj(kind,record['title']['en'],record['title']['fr'],properties,source=record['number']);defs[kind]['x-document-sections']=True;public.append(kind)
 # Every bilingual PDF field is retained under a stable source-key mapping. Radio groups become exclusive choices.
 record=next(r for r in data['register'] if r['kind']=='material_privacy_breach');groups={};pdf=data['breach']['fields'];processed=set()
 radio={}
 for item in pdf:
  m=re.match(r'^(.+)-(\d+)$',item['id'])
  if item['en']['type']=='Btn' and m:radio.setdefault(m[1],[]).append(item)
 def bucket(key):
  if key.startswith(('ReportState','InstitutionRef','OPCFile','FormID')):return 'report'
  if key.startswith(('InstitutionName','InstitutionCoordinator','InstitutionContactName','InstitutionContactTitle','InstitutionContactTelephone','InstitutionContactEmail','Representative')):return 'institution'
  if key.startswith(('BreachAffected','BreachDate','BreachTimeline')):return 'timeline'
  if key.startswith(('BreachType','BreachCause')):return 'type_cause'
  if key.startswith(('SecuritySafeguard','TechnicalSafeguard')):return 'safeguards'
  if key.startswith(('PersonalInfo','AccountDescription','IdentifyingNumber','Biometric','ContactDescription','Credential','Demographic','EducationDescription','EmploymentDescription','FinancialDescription','GeneticDescription','GovernmentIssued','HealthDescription','LawDescription','LocationDescription','OtherPreference','SecurityDescription')):return 'personal_information'
  if key.startswith(('IncludedInPersonal','InstitutionPib','TbsRegistration')):return 'pibs'
  if key.startswith(('Risk','InstitutionAnticipated')):return 'risk'
  if key.startswith(('NotifiedAffected','Notification','NotNotified')):return 'notification'
  if key.startswith(('LawEnforcement','OtherOrganization','OtherDate','OrganizationNotification')):return 'other_notifications'
  if key.startswith(('InstitutionIdentified','InstitutionContacted','CompromisedInformation','IndividualRisk')):return 'containment'
  if key.startswith('BreachRiskMitigation'):return 'prevention'
  if key.startswith('SubmitSelect'):return 'submission'
  return 'description'
 titles={'report':('Report identification','Identification du rapport'),'institution':('A · Institution and contacts','A · Institution et personnes-ressources'),'timeline':('B.1–B.2 · Affected individuals and timeline','B.1–B.2 · Personnes touchées et chronologie'),'type_cause':('B.3 · Type and cause','B.3 · Type et cause'),'description':('B.4 · Description','B.4 · Description'),'safeguards':('B.5 · Safeguards','B.5 · Mesures de protection'),'personal_information':('B.6 · Personal information categories · no affected identities','B.6 · Catégories de renseignements · aucune identité touchée'),'pibs':('B.6 · Related PIBs','B.6 · FRP connexes'),'risk':('B.7 · Significant harm','B.7 · Préjudice grave'),'notification':('C.1 · Notification to individuals','C.1 · Avis aux personnes'),'other_notifications':('C.2 · Other organizations','C.2 · Autres organisations'),'containment':('D · Containment and mitigation','D · Limitation et atténuation'),'prevention':('E · Prevention','E · Prévention'),'submission':('Official submission method · no sending from Studio','Mode de présentation officiel · aucun envoi depuis l’atelier')}
 for item in pdf:
  key=item['id'];m=re.match(r'^(.+)-(\d+)$',key);name=m[1] if item['en']['type']=='Btn' and m else key
  if name in processed:continue
  processed.add(name);section=bucket(name);fields=groups.setdefault(section,{})
  if name in radio:
   options=radio[name];rule=choice(options[0]['en']['label'],options[0]['fr']['label'],{x['id']:(x['en']['label'],x['fr']['label']) for x in options});rule['minLength']=0
   rule['x-source-field-ids']=[x['id'] for x in options]
  elif item['en']['type']=='Btn':rule={'type':'boolean','default':False,'x-label':bi(item['en']['label'],item['fr']['label']),'x-source-field-ids':[key]}
  elif key=='FormID':
   rule={**neutral('Source form identification','Identification du formulaire source'),'const':'TBS/SCT 350-64E / 350-64F','default':'TBS/SCT 350-64E / 350-64F','readOnly':True,'x-hidden':True,'x-source-field-ids':[key]}
  elif item['en']['type']=='Ch':rule=text(item['en']['label'],item['fr']['label'],False);rule['x-source-field-ids']=[key]
  elif any(part in key for part in ['Date','Email','Telephone','RefNumber','OPCFileNumber','TbsRegistrationNumber','CoordinatorName','ContactName']):
   rule=neutral(item['en']['label'],item['fr']['label']);rule['x-source-field-ids']=[key]
   if key.startswith('BreachDate') or key in ['NotificationStartDate','NotificationCompletedDate']:
    rule=neutral(item['en']['label'],item['fr']['label'],format='date');rule['x-source-field-ids']=[key]
   if 'Email' in key:rule=neutral(item['en']['label'],item['fr']['label'],format='email');rule['x-source-field-ids']=[key]
  else:rule=text(item['en']['label'],item['fr']['label'],False);rule['x-source-field-ids']=[key]
  fields[name]=rule;coverage.append(dict(document_type='material_privacy_breach',field=section+'/'+name,source_ids=rule['x-source-field-ids']))
 properties={'title':{**text('Document title','Titre du document'),'default':record['title']},'amendment_summary':text('Amendment / update summary, if applicable','Résumé des modifications, le cas échéant',False),'source_guidance':{**text('Official PDF instructions','Consignes du PDF officiel',False),'const':bi('\n\n'.join(data['breach']['pages']['en']),'\n\n'.join(data['breach']['pages']['fr'])),'default':bi('\n\n'.join(data['breach']['pages']['en']),'\n\n'.join(data['breach']['pages']['fr'])),'readOnly':True,'x-guidance':True}}
 for group in titles:
  fields=groups.get(group)
  if fields is None:continue
  key='material_privacy_breach_'+group;defs[key]=obj(key,*titles[group],fields,source=record['number']);properties[group]=ref(key)
 defs['material_privacy_breach']=obj('material_privacy_breach',record['title']['en'],record['title']['fr'],properties,source=record['number']);defs['material_privacy_breach']['x-document-sections']=True;public.append('material_privacy_breach')
 return public,coverage
