import {enumText} from "./vocabulary.mjs";
import {VERSION,SCHEMA_ID,resolve,validate,collect,label} from './model.mjs';

export function cleanMarkdown(value){
  return String(value??'').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\[([^\]]+)\]\(([^\s)]+)\)/g,(all,title,url)=>/^https?:\/\//i.test(url)?all:title+' ('+url.replace(/[()]/g,'')+')');
}
function plain(value){return cleanMarkdown(value).replace(/[\n\r|]/g,' ').replace(/"/g,'&quot;');}
function bilingualHead(value){return [value?.en,value?.fr].filter(Boolean).join(' / ');}
export function mermaidChart(people){
  const keys=new Map(people.map((p,i)=>[p.id,'position_'+i]));
  const lines=['```mermaid','flowchart TB'];
  for(const p of people){
    const programs=(p.programs||[]).map(a=>bilingualHead(a.program_title)||a.program_id).join('; ');
    const text=[p.name,bilingualHead(p.position_title),[p.classification_group,p.classification_level].filter(Boolean).join('-'),programs].filter(Boolean).map(plain).join('<br/>');
    lines.push('  '+keys.get(p.id)+'["'+text+'"]');
  }
  for(const p of people)if(p.reports_to&&keys.has(p.reports_to)&&p.reports_to!==p.id)lines.push('  '+keys.get(p.reports_to)+' --> '+keys.get(p.id));
  lines.push('```');return lines.join('\n');
}
export function additionalInformation(doc,template,language){
 const fields=doc.payload.additional_information||{},institution=doc.payload.institution_name?.[language]||'—';
 let value=template[language]||'',linkIndex=0;
 const urls=[fields['completed_requests_url_'+language],fields['open_data_url_'+language],fields['pia_summaries_url_'+language]];
 value=value.replace(/\[(?:link|lien)\](?!\()/gi,()=>['__COMPLETED__','__OPEN__','__PIA__'][linkIndex++]||'');
 if(!urls[1])value=value.replace(/You may also wish to review available open data regarding[\s\S]*?__OPEN__\./,'').replace(/Vous pouvez également consulter les données ouvertes disponibles concernant[\s\S]*?__OPEN__\./,'');
 value=value.replace(/\[([^\]]+)\](?!\()/g,(whole,label)=>{
  const key=label.toLocaleLowerCase();
  if(/^(?:name of institution|nom de l’institution)$/.test(key))return cleanMarkdown(institution);
  if(/^(?:title and address|titre et adresse)/.test(key))return cleanMarkdown([fields.official_title?.[language],fields.mailing_address?.[language]].filter(Boolean).join(' · ')||'—');
  if(/^(?:either to the receiver|l’ordre du receveur)/.test(key))return cleanMarkdown(fields.fee_payee?.[language]||'—');
  if(/^(?:the address, telephone|l’adresse, le numéro)/.test(key))return cleanMarkdown(fields.informal_contact?.[language]||'—');
  if(/^(?:omit portion|omettre la partie)/.test(key))return '';
  return whole;
 });
 for(const[index,token]of ['__COMPLETED__','__OPEN__','__PIA__'].entries())value=value.replaceAll(token,urls[index]?'['+(language==='fr'?'consulter':'view')+']('+urls[index]+')':'—');
 return value.replace(/ +/g,' ').trim();
}
export function renderMarkdown(doc,schema){
  const root=doc.payload,rule=schema.$defs[root.kind],chunks=[];
  chunks.push('# '+cleanMarkdown(bilingualHead(root.institution_name||root.title)||bilingualHead(rule['x-label'])));
  chunks.push(doc.status==='review_ready'?'Review-ready document / Document prêt pour examen':'DRAFT · incomplete content may remain / BROUILLON · contenu possiblement incomplet');
  chunks.push('Schema / Schéma: `'+VERSION+'` · Document: `'+doc.document_id+'`');
  function heading(text,level){chunks.push('#'.repeat(Math.min(level,6))+' '+cleanMarkdown(text));}
  function render(value,definition,level=2,key=''){
    definition=resolve(schema,definition);const title=bilingualHead(definition['x-label'])||key;
    if(doc.status==='review_ready'&&definition['x-guidance'])return;
    if(definition['x-hidden']||definition['x-ui']==='id')return;
    if(definition['x-ui']==='bilingual'){
      if(!value?.en&&!value?.fr)return;
      if(definition['x-template']==='additional_information')value={en:additionalInformation(doc,value,'en'),fr:additionalInformation(doc,value,'fr')};
      heading(title,level);chunks.push('**English**\n\n'+cleanMarkdown(value.en||'—')+'\n\n**Français**\n\n'+cleanMarkdown(value.fr||'—'));return;
    }
    if(definition.type==='array'){
      if(!value?.length)return;heading(title,level);
      const rows=key==='manuals'?[...value].sort((a,b)=>label(a,'en').localeCompare(label(b,'en'),'en')):value;
      for(const item of rows){const itemRule=resolve(schema,definition.items);
        if(itemRule.type==='object'&&itemRule['x-ui']!=='bilingual'){
          heading(bilingualHead(item.title||item.position_title||item.program_title)||item.name||bilingualHead(itemRule['x-label']),level+1);render(item,definition.items,level+2);
        }else render(item,definition.items,level+1);
      }
      return;
    }
    if(definition.type==='object'){
      if(key&&key!=='payload')heading(title,level++);
      for(const[k,field]of Object.entries(definition.properties||{})){
        if(key==='additional_information'&&doc.status==='review_ready'&&k!=='standard_text')continue;
        if(k==='reports_to'&&value[k]){const manager=collect(root,'person').find(p=>p.id===value[k]);chunks.push('**Reports to / Relève de:** '+plain(manager?manager.name:value[k]));continue;}
        render(value?.[k],field,level,k);
      }
      return;
    }
    if(value!==''&&value!==undefined&&value!==null)chunks.push('**'+cleanMarkdown(title)+':** '+cleanMarkdown(typeof value==='boolean'?(value?'Yes / Oui':'No / Non'):definition.enum?enumText(value):value));
  }
  render(root,rule,2,'payload');
  const people=collect(root,'person');if(people.length){heading('Organization chart · entered reporting lines / Organigramme · liens hiérarchiques saisis',2);chunks.push(mermaidChart(people));}
  chunks.push('---\nTemplate sources / Sources des modèles: [Info Source requirements]('+ 'https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/access-information/access-informatio-policies-guidance/programs-holdings-online-publishing-requirements.html'+').\n\nPeople, classifications, reporting lines and position/program assignments are project additions; they are not presented as official Info Source requirements. / Les personnes, classifications, liens hiérarchiques et affectations poste-programme sont des ajouts du projet; ils ne sont pas présentés comme des exigences officielles d’Info Source.');
  return chunks.join('\n\n').trim()+'\n';
}
export function exportMarkdown(doc,schema,{ready=false}={}){
  const output=structuredClone(doc);output.status=ready?'review_ready':'draft';
  const issues=validate(output,schema,{complete:ready});if(issues.length)throw new Error('Document validation failed: '+issues.map(x=>x.path+' '+x.message).join('\n'));
  return '---\n'+JSON.stringify({document_studio:VERSION,document:output},null,2)+'\n---\n\n'+renderMarkdown(output,schema);
}
export function importDocument(text,schema){
  let doc;
  if(text.replace(/^\uFEFF/,'').trimStart().startsWith('{'))doc=JSON.parse(text.replace(/^\uFEFF/,''));
  else{
    const normalized=text.replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
    const match=/^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(normalized);
    if(!match)throw Error('Open a typed Document Studio .md or .json file / Ouvrir un fichier .md ou .json typé de l’atelier.');
    const meta=JSON.parse(match[1]);if(meta.document_studio!==VERSION)throw Error('Unsupported document version / Version de document non prise en charge.');
    if(Object.keys(meta).some(k=>!['document_studio','document'].includes(k)))throw Error('Unknown document metadata / Métadonnées inconnues.');
    doc=meta.document;
    const structural=validate(doc,schema,{complete:doc?.status==='review_ready'});if(structural.length)throw Error(structural.map(i=>i.path+' '+i.message).join('\n'));
    if(match[2].trim()!==renderMarkdown(doc,schema).trim())throw Error('The visible Markdown differs from its structured content. Open the original file or edit its JSON data and regenerate; no text has been discarded. / Le Markdown visible diffère du contenu structuré. Ouvrir l’original ou modifier les données JSON puis régénérer; aucun texte n’a été supprimé.');
  }
  if(doc?.schema_id!==SCHEMA_ID||doc?.schema_version!==VERSION)throw Error('This document uses another schema / Ce document utilise un autre schéma.');
  const issues=validate(doc,schema,{complete:doc.status==='review_ready'});if(issues.length)throw Error(issues.map(i=>i.path+' '+i.message).join('\n'));
  return doc;
}
