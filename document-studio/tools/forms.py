"""Preserve official Word template sections, fixed questions and repeatable tables.

Only OpenXML text/styles/tables are read. No macros, embedded links or document
instructions execute. EN/FR alignment is checked per heading, block and row.
"""
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
FAMILIES={'pia_web_summary':'privacy-impact-assessment-web-summary-template','privacy_checklist':'privacy-checklist-template','privacy_impact_assessment':'privacy-impact-assessment-template','privacy_protocol':'privacy-protocol-template'}

def paragraphs(element):return [''.join(t.text or '' for t in p.findall('.//w:t',NS)).strip() for p in element.findall('w:p',NS)]
def read_word(path):
    root=ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'));sections=[]
    for element in root.find('w:body',NS):
        if element.tag.endswith('}p'):
            text=''.join(t.text or '' for t in element.findall('.//w:t',NS)).strip();style=element.find('./w:pPr/w:pStyle',NS);style=style.get('{'+NS['w']+'}val','') if style is not None else ''
            if text and style.startswith('Heading'):sections.append(dict(title=text,style=style,blocks=[]))
            elif text:
                if not sections:sections.append(dict(title='',style='',blocks=[]))
                sections[-1]['blocks'].append(text)
        elif element.tag.endswith('}tbl'):
            rows=[['\n'.join(paragraphs(cell)) for cell in row.findall('w:tc',NS)] for row in element.findall('w:tr',NS)]
            if not sections:sections.append(dict(title='',style='',blocks=[]))
            sections[-1]['blocks'].append(dict(table=rows))
    return sections

def capture(directory,out):
    data={};sources=[]
    for kind,stem in FAMILIES.items():
        languages={}
        for lang in ['en','fr']:
            path=directory/(stem+'-'+lang+'.docx');raw=path.read_bytes();languages[lang]=read_word(path)
            sources.append(dict(id=kind+'-'+lang,language=lang,url='https://www.canada.ca/content/dam/tbs-sct/documents/forms/'+stem+'-'+lang+'.docx',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
        if len(languages['en'])!=len(languages['fr']):raise ValueError(kind+': heading counts differ; review bilingual alignment')
        for i,(en,fr) in enumerate(zip(languages['en'],languages['fr'])):
            if en['style']!=fr['style'] or len(en['blocks'])!=len(fr['blocks']):raise ValueError(f'{kind} section {i}: bilingual block alignment differs')
            for j,(a,b) in enumerate(zip(en['blocks'],fr['blocks'])):
                if isinstance(a,str)!=isinstance(b,str):raise ValueError(f'{kind} section {i} block {j}: block types differ')
                if isinstance(a,dict) and len(a['table'])!=len(b['table']):raise ValueError(f'{kind} section {i} table {j}: row counts differ')
        data[kind]=languages
    (out/'forms.json').write_text(json.dumps(dict(forms=data,sources=sources),ensure_ascii=False,indent=2)+'\n')


def extend(defs,form_data,bi,text,neutral,enum,obj,ref,array):
    public=[];coverage=[]
    def guidance(en,fr):return {**text('Official template guidance','Consignes du modèle officiel',False),'const':bi(en,fr),'default':bi(en,fr),'readOnly':True,'x-guidance':True}
    def choice(en,fr,na=True):return {**neutral(en,fr,minLength=1),'enum':['','yes','no','not_applicable'],'default':'','x-conditional-na-extension':not na}
    def response(en,fr,required=True):return text(en,fr,required)
    for kind,languages in form_data['forms'].items():
        public.append(kind);properties={'title':{**text('Document title','Titre du document'),'default':bi(languages['en'][0]['title'],languages['fr'][0]['title'])}}
        for s_index,(en,fr) in enumerate(zip(languages['en'],languages['fr'])):
            section_key='section_'+str(s_index+1).zfill(2);section_kind=kind+'_'+section_key;fields={};field_index=0
            all_en=[];all_fr=[]
            for block in en['blocks']:all_en.append(block if isinstance(block,str) else '\n'.join(' | '.join(row) for row in block['table']))
            for block in fr['blocks']:all_fr.append(block if isinstance(block,str) else '\n'.join(' | '.join(row) for row in block['table']))
            fields['not_applicable_explanation']=text('Explain any conditionally inapplicable answers','Expliquer les réponses conditionnellement non applicables',False)
            fields['guidance']=guidance('\n\n'.join(all_en),'\n\n'.join(all_fr))
            def add_field(rule):
                nonlocal field_index
                field_index+=1;key='response_'+str(field_index).zfill(3);fields[key]=rule;return key
            created_paragraphs=set()
            for b_index,(a,b) in enumerate(zip(en['blocks'],fr['blocks'])):
                if isinstance(a,str):
                    previous_en=en['blocks'][b_index-1] if b_index else en['title'];previous_fr=fr['blocks'][b_index-1] if b_index else fr['title']
                    if not isinstance(previous_en,str):previous_en=en['title'];previous_fr=fr['title']
                    stripped=a.strip();rule=None
                    if re.match(r'^Enter (?:Yes|yes)',stripped):rule=choice(previous_en,previous_fr,'applicable' in a.lower())
                    elif re.search(r'Enter Yes or No\s*:',a):rule=choice(a,b,'applicable' in a.lower())
                    elif re.search(r'\[(?:Insert|insert|Name|name)',a):
                        # If the immediately preceding source label already creates an input, retain one response.
                        if b_index-1 in created_paragraphs:continue
                        rule=response(en['title'] if 'Insert text' in a and b_index>1 else previous_en,fr['title'] if 'Insert text' in a and b_index>1 else previous_fr)
                    elif stripped.endswith(':') and not re.match(r'^(?:Note|Example|If |The |Provide|Describe|Indicate|For |Such |Select |List |In )',stripped):
                        if re.search(r'^(?:Date)',stripped):rule=neutral(a,b,format='date',minLength=1)
                        elif re.search(r'^(?:Email)',stripped):rule=neutral(a,b,format='email',minLength=1)
                        elif re.search(r'^(?:Name|Telephone|Signature)',stripped):rule=neutral(a,b,minLength=1)
                        else:rule=response(a,b)
                    if rule:
                        key=add_field(rule);created_paragraphs.add(b_index);rule['x-source-location']=f'{kind}/section/{s_index}/paragraph/{b_index}';coverage.append(dict(document_type=kind,section=section_key,field=key,source_location=rule['x-source-location']))
                    continue
                table_en=a['table'];table_fr=b['table'];tname='table_'+str(b_index+1).zfill(2)
                if not table_en:continue
                header_en,header_fr=table_en[0],table_fr[0]
                if len(header_en)!=len(header_fr):raise ValueError(f'{kind}/{section_key}/{tname}: header columns differ')
                # Risk/likelihood grids and category annexes are read-only reference data, never blank answer rows.
                is_reference=any(w in en['title'].lower() for w in ['likelihood scale','risk assessment grid','non-compliance grid','appendix: categories'])
                if is_reference:continue
                fixed_questions=(len(header_en)==2 and header_en[0].strip().lower() in ['questions','question','provide the following information']) or (len(header_en)==4 and header_en[0].strip().lower()=='question')
                if fixed_questions:
                    question_fields={}
                    for r_index,(row_en,row_fr) in enumerate(zip(table_en[1:],table_fr[1:]),1):
                        if len(row_en)!=len(row_fr):raise ValueError(f'{kind}/{section_key}/{tname}/{r_index}: bilingual row widths differ')
                        if not row_en or not row_en[0].strip():continue
                        key='question_'+str(r_index).zfill(3);row_kind=section_kind+'_'+tname+'_'+key
                        source_q={**text('Official question','Question officielle'),'const':bi(row_en[0],row_fr[0]),'default':bi(row_en[0],row_fr[0]),'readOnly':True}
                        answer_cell=row_en[1] if len(row_en)>1 else ''
                        is_choice=bool(re.search(r'Enter Yes|Select the appropriate response',answer_cell))
                        q_fields={'question':source_q,'answer':choice('Answer','Réponse','not applicable' in answer_cell.lower()) if is_choice else response('Response · explain not applicable where relevant','Réponse · expliquer les cas non applicables')}
                        if len(row_en)>2:q_fields['justification']=response('Justification, if necessary','Justification, au besoin',False)
                        if 'justification' not in q_fields:q_fields['justification']=text('Explanation if conditionally not applicable','Explication si conditionnellement non applicable',False)
                        if len(row_en)>3:q_fields['risk_or_compliance_issue']=response('Risk / compliance issue · privacy official review','Risque / non-conformité · examen du responsable de la vie privée',False)
                        defs[row_kind]=obj(row_kind,'Question '+str(r_index),'Question '+str(r_index),q_fields,source=kind+' '+section_key+' '+tname+' row '+str(r_index))
                        question_fields[key]=ref(row_kind)
                        coverage.append(dict(document_type=kind,section=section_key,field=tname+'/'+key,source_location=f'{kind}/section/{s_index}/table/{b_index}/row/{r_index}'))
                    table_kind=section_kind+'_'+tname;defs[table_kind]=obj(table_kind,'Questions and responses','Questions et réponses',question_fields,source=kind+' '+section_key)
                    fields[tname]=ref(table_kind)
                else:
                    row_kind=section_kind+'_'+tname+'_row';columns={}
                    for c_index,(title_en,title_fr) in enumerate(zip(header_en,header_fr)):
                        column='column_'+str(c_index+1).zfill(2);columns[column]=response(title_en,title_fr)
                    if en['title'] in ['Risk Mitigation Action Plan','Compliance Issue Action Plan']:
                        columns['lead']=neutral('Lead responsible','Responsable',minLength=1)
                        columns['target_completion_date']=neutral('Target completion date','Date cible',format='date',minLength=1)
                    defs[row_kind]=obj(row_kind,'Entry','Entrée',columns,source=kind+' '+section_key+' '+tname)
                    table_kind=section_kind+'_'+tname
                    props={'applicability':{**neutral('Applicability','Applicabilité',minLength=1),'enum':['','applicable','not_applicable'],'default':''},'not_applicable_reason':text('Reason if not applicable','Motif si non applicable',False),'rows':array(row_kind,'Rows · add as needed','Lignes · ajouter au besoin')}
                    defs[table_kind]=obj(table_kind,en['title'],fr['title'],props,source=kind+' '+section_key+' '+tname);defs[table_kind]['x-repeating-table']=True
                    fields[tname]=ref(table_kind)
                    coverage.append(dict(document_type=kind,section=section_key,field=tname+'/rows[]',source_location=f'{kind}/section/{s_index}/table/{b_index}',columns=len(columns)))
            if 'multi-institutional' in en['title'].lower():
                fields['participating_institutions']=array('participating_institution','Participating institutions · repeat as needed','Institutions participantes · répéter au besoin')
            # The web summary has six named response sections with one explicit placeholder each.
            # When a section is only explanatory headings, it still remains in the document with its source text.
            defs[section_kind]=obj(section_kind,en['title'] or 'Instructions',fr['title'] or 'Instructions',fields,source=kind+' source section '+str(s_index+1))
            properties[section_key]=ref(section_kind)
        defs[kind]=obj(kind,languages['en'][0]['title'],languages['fr'][0]['title'],properties,source='Official bilingual TBS Word template');defs[kind]['x-document-sections']=True
    return public,coverage
