import {enumLabels} from "./vocabulary.mjs";
import {VERSION,clone,uid,at,put,resolve,component,newDocument,validate,validateSchemaDefinition,collect,label,chartLayout,validURL,synchronizePrograms} from './model.mjs';
import {exportMarkdown,importDocument,cleanMarkdown,additionalInformation} from './markdown.mjs';
const $=id=>document.getElementById(id),el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined&&text!==null)n.textContent=text;if(cls)n.className=cls;return n;};
let lang=new URLSearchParams(location.search).get('lang')==='fr'?'fr':'en';
const text=(en,fr)=>lang==='fr'?fr:en;
const labels={back:['Back to PIBs','Retour aux PIB'],sources:['Template sources','Sources des modèles'],bilingual:['ONE DOCUMENT · ENGLISH + FRENCH','UN DOCUMENT · ANGLAIS + FRANÇAIS'],new:['New document','Nouveau document'],open:['Open','Ouvrir'],draft:['Save draft .md','Enregistrer le brouillon .md'],download:['Download review-ready .md','Télécharger le .md prêt pour examen'],outline:['Document outline','Plan du document'],drafts:['Saved on this browser','Enregistrés dans ce navigateur'],outlineHint:['Choose a section to write. Add or repeat the parts you need.','Choisissez une section à rédiger. Ajoutez ou répétez les éléments nécessaires.'],guide:['How documents and templates work','Fonctionnement des documents et modèles'],showOutline:['Show outline','Afficher le plan'],review:['items to complete','éléments à compléter'],localNote:['Drafts stay in this browser. Download a .md file to keep or share your work. Review-ready means the template checks passed; it does not submit or approve a publication.','Les brouillons restent dans ce navigateur. Téléchargez un .md pour conserver ou partager votre travail. Prêt pour examen signifie que les contrôles du modèle sont réussis; aucune publication n’est soumise ou approuvée.'],library:['TEMPLATE LIBRARY','BIBLIOTHÈQUE DE MODÈLES'],checks:['DOCUMENT CHECKS','CONTRÔLES DU DOCUMENT'],complete:['Complete the document','Compléter le document'],json:['Download structured JSON','Télécharger le JSON structuré'],extensionNote:['The People chart and position/program assignments are requested project extensions, separate from the official Info Source publication requirements.','L’organigramme et les affectations poste-programme sont des ajouts demandés au projet, distincts des exigences officielles de publication Info Source.'],schema:['Read the document schema','Consulter le schéma documentaire'],coverage:['Read the requirement-to-template map','Consulter la correspondance exigences-modèles']};

const KEY='pibs-document-studio-v1';
let storageWritable=true,recoveryText=null,saveState='loading';
function renderSaveStatus(){const values={saved:['Saved in this browser · bilingual document','Enregistré dans ce navigateur · document bilingue'],unavailable:['Browser saving is unavailable. Download your draft to keep it.','Enregistrement du navigateur indisponible. Téléchargez votre brouillon pour le conserver.'],preserved:['Existing browser drafts are preserved. Download this draft to keep your changes.','Les brouillons existants du navigateur sont préservés. Téléchargez ce brouillon pour conserver vos changements.'],loading:['Loading templates…','Chargement des modèles…']};$('save-status').textContent=text(...values[saveState]);}
let schema,catalogue,library,sourceInfo,programLibrary,doc,selected=['payload'],documents=Object.create(null),currentEditor=null,savedRange=null,issues=[],chooser=null,category='all',undo=[],redo=[],lastEdit='',lastEditTime=0,saveTimer;
const titleOf=definition=>definition?.['x-label']?.[lang]||definition?.['x-label']?.en||'';
function btn(value,action,cls){const b=el('button',value,cls);b.type='button';b.onclick=action;return b;}
function error(message){$('app-error').hidden=!message;$('app-error').textContent=message||'';}
function localize(){document.documentElement.lang=lang;for(const node of document.querySelectorAll('[data-i18n]'))node.textContent=labels[node.dataset.i18n]?.[lang==='fr'?1:0]||node.textContent;$('language').textContent=lang==='fr'?'English':'Français';$('language').lang=lang==='fr'?'en':'fr';}
function snapshot(path='action'){
 const now=Date.now();if(path==='action'||path!==lastEdit||now-lastEditTime>1000){undo.push(clone(doc));if(undo.length>50)undo.shift();redo=[];}
 lastEdit=path;lastEditTime=now;
}
function mutate(action,{render=true}={}){snapshot();action();changed();if(render)renderAll();}
function changed(){synchronizePrograms(doc);doc.status='draft';clearTimeout(saveTimer);saveTimer=setTimeout(save,120);refreshChecks();updateTitle();}
function save(){
 documents[doc.document_id]=clone(doc);
 if(!storageWritable){saveState='preserved';renderSaveStatus();renderSaved();return;}
 try{localStorage.setItem(KEY,JSON.stringify({version:VERSION,current:doc.document_id,documents}));saveState='saved';renderSaveStatus();}
 catch{saveState='unavailable';renderSaveStatus();}
 renderSaved();
}
function renderSaved(){const select=$('saved-documents'),chosen=doc.document_id;select.replaceChildren();for(const d of Object.values(documents)){const option=el('option',label(d.payload,lang)||schema.$defs[d.payload.kind]?.['x-label']?.[lang]||d.payload.kind);option.value=d.document_id;select.append(option);}if(!documents[chosen]){const option=el('option',label(doc.payload,lang)||titleOf(schema.$defs[doc.payload.kind]));option.value=chosen;select.append(option);}select.value=chosen;}
function updateTitle(){$('document-title').textContent=label(doc.payload,lang)||titleOf(schema.$defs[doc.payload.kind]);}
function ruleAt(path){let rule=schema.$defs[doc.payload.kind];for(const key of path.slice(1)){rule=resolve(schema,rule);rule=rule.type==='array'?rule.items:rule.properties[key];if(!rule)throw Error('Unknown document section');}return resolve(schema,rule);}
function go(path){currentEditor=null;selected=path;renderAll();$('paper').focus({preventScroll:true});$('paper').scrollIntoView({block:'start'});}
function pathTitle(path){const value=at(doc,path),rule=ruleAt(path);return (value?.kind&&(label(value,lang)||titleOf(rule)))||titleOf(rule)||text('Document','Document');}
function renderOutline(){
 const nav=$('outline');nav.replaceChildren();
 function item(path,title,count,depth=0){const b=btn('',()=>go(path));b.style.paddingLeft=(10+depth*12)+'px';b.append(el('span',title));if(count!==undefined)b.append(el('small',String(count)));if(JSON.stringify(path)===JSON.stringify(selected))b.setAttribute('aria-current','location');nav.append(b);}
 item(['payload'],text('Document overview','Aperçu du document'));
 const root=schema.$defs[doc.payload.kind];
 for(const[key,field]of Object.entries(root.properties)){
  const rule=resolve(schema,field),value=doc.payload[key];
  if(rule.type==='array'||(rule.type==='object'&&rule['x-ui']!=='bilingual')){
   const path=['payload',key];item(path,titleOf(rule)||key,Array.isArray(value)?value.length:undefined);
   if(Array.isArray(value)&&selected[1]===key)value.forEach((v,i)=>{if(v&&typeof v==='object'&&v.kind)item([...path,i],label(v,lang)||text('Untitled','Sans titre'),undefined,1);});
  }
 }
}
function renderBreadcrumbs(){const box=$('breadcrumbs');box.replaceChildren();for(let i=1;i<=selected.length;i++){
 const path=selected.slice(0,i);if(i>1)box.append(el('span','›'));const name=pathTitle(path);box.append(i===selected.length?el('span',name):btn(name,()=>go(path)));
}}
function inline(parent,value){
 const pattern=/\*\*([^*]+)\*\*|\*([^*\n]+)\*|\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;let offset=0;
 for(const match of String(value).matchAll(pattern)){parent.append(document.createTextNode(value.slice(offset,match.index)));if(match[1])parent.append(el('strong',match[1]));else if(match[2])parent.append(el('em',match[2]));else{const a=el('a',match[3]);a.href=match[4];a.rel='noopener noreferrer';parent.append(a);}offset=match.index+match[0].length;}parent.append(document.createTextNode(String(value).slice(offset)));
}
function markdownDOM(value,container){
 const lines=String(value||'').split('\n');let list=null;
 lines.forEach((line,index)=>{const match=/^\s*[-*] (.*)$/.exec(line);if(match){if(!list){list=el('ul');container.append(list);}const li=el('li');inline(li,match[1]);list.append(li);}else{list=null;if(index&&container.childNodes.length)container.append(el('br'));inline(container,line);}});
}
function DOMMarkdown(root){
 function walk(node){if(node.nodeType===Node.TEXT_NODE)return node.textContent.replace(/\u00a0/g,' ');if(node.nodeType!==Node.ELEMENT_NODE)return '';const inner=[...node.childNodes].map(walk).join('');switch(node.tagName){case 'BR':return '\n';case 'B':case 'STRONG':return '**'+inner+'**';case 'I':case 'EM':return '*'+inner+'*';case 'A':return validURL(node.getAttribute('href')||'')?'['+inner+']('+node.getAttribute('href')+')':inner;case 'LI':return '- '+inner.trim()+'\n';case 'UL':case 'OL':return '\n'+inner+'\n';case 'DIV':case 'P':return inner+'\n';default:return inner;}}
 return [...root.childNodes].map(walk).join('').replace(/\n{3,}/g,'\n\n').trimEnd();
}
function fieldLabel(rule,path,required){const line=el('div',titleOf(rule),'field-label');if(required)line.append(el('small',text('required','obligatoire'),'required'));return line;}
function binding(path,value){snapshot(path.join('/'));put(doc,path,value);changed();}
function renderField(value,definition,path,parent,required=false){
 const rule=resolve(schema,definition);required=rule['x-ui']==='bilingual'?(rule.properties.en.minLength||0)>0:(rule.minLength||0)>0;if(rule['x-hidden']||rule['x-ui']==='id')return;
 if(rule['x-guidance']){const details=el('details',null,'section-note');details.append(el('summary',text('Official template guidance · EN / FR','Consignes officielles du modèle · EN / FR')));for(const language of ['en','fr']){details.append(el('strong',language.toUpperCase()));const content=el('div',null,'locked-content');content.lang=language;markdownDOM(value?.[language]||'',content);details.append(content);}parent.append(details);return;}
 if(rule['x-ui']==='bilingual'){
  const wrap=el('section',null,'field bilingual-field');wrap.dataset.fieldPath=JSON.stringify(path);wrap.append(fieldLabel(rule,path,required));const pair=el('div',null,'language-pair');
  for(const language of ['en','fr']){
   const cell=el('div',null,'language-block');cell.append(el('div',language==='en'?'ENGLISH':'FRANÇAIS','language-label'));const editor=el('div',null,rule.readOnly?'locked-content':'editable');editor.lang=language;editor.dataset.editPath=JSON.stringify([...path,language]);
   markdownDOM(rule['x-template']==='additional_information'?additionalInformation(doc,value,language):(value?.[language]||''),editor);
   if(!rule.readOnly){editor.contentEditable='true';editor.setAttribute('role','textbox');editor.setAttribute('aria-multiline','true');editor.setAttribute('aria-label',titleOf(rule)+' · '+(language==='en'?'English':'Français'));editor.dataset.placeholder=language==='en'?'Write here…':'Rédigez ici…';editor.onfocus=()=>{currentEditor=editor;};editor.oninput=()=>binding([...path,language],DOMMarkdown(editor));editor.onpaste=e=>{e.preventDefault();document.execCommand('insertText',false,e.clipboardData.getData('text/plain'));};}
   cell.append(editor);if(rule.readOnly)cell.append(el('span',text('Fixed official template text','Texte officiel fixe du modèle'),'lock-label'));pair.append(cell);
  }
  wrap.append(pair);parent.append(wrap);return;
 }
 if(rule.type==='array'){renderArray(value,rule,path,parent);return;}
 if(rule.type==='object'){
  const block=el('section',null,'nested-object');block.dataset.fieldPath=JSON.stringify(path);block.append(el('h3',titleOf(rule)));renderObject(value,rule,path,block);parent.append(block);return;
 }
 const wrap=el('div',null,'field');wrap.dataset.fieldPath=JSON.stringify(path);const id='field-'+path.join('-');const lab=el('label',titleOf(rule),'field-label');lab.htmlFor=id;if(required)lab.append(el('small',text('required','obligatoire'),'required'));wrap.append(lab);
 let input;
 if(path.at(-1)==='reports_to'){
  input=el('select');const none=el('option',text('No manager recorded / top of chart','Aucun supérieur indiqué / sommet du diagramme'));none.value='';input.append(none);
  const person=at(doc,path.slice(0,-1));for(const p of collect(doc.payload,'person').filter(p=>p.id!==person.id)){const option=el('option',p.name+' · '+(p.position_title?.[lang]||''));option.value=p.id;input.append(option);}if(value&&!Array.from(input.options).some(o=>o.value===value)){const option=el('option',text('Missing manager: ','Supérieur manquant : ')+value);option.value=value;input.append(option);}input.value=value;
 }else if(rule.enum){input=el('select');for(const value of rule.enum){const option=el('option',enumLabels[value]?.[lang==='fr'?1:0]||value);option.value=value;input.append(option);}input.value=value;}
 else{input=el('input');input.type=rule.type==='boolean'?'checkbox':(rule.format||rule['x-input-format'])==='date'?'date':(rule.format||rule['x-input-format'])==='email'?'email':(rule.format||rule['x-input-format'])==='uri'?'url':'text';if(rule.type==='boolean')input.checked=value;else input.value=value||'';}
 input.id=id;input.dataset.inputPath=JSON.stringify(path);input.onchange=()=>{snapshot();put(doc,path,rule.type==='boolean'?input.checked:input.value);changed();if(path.at(-1)==='reports_to')renderAll();};input.oninput=()=>{if(input.tagName==='INPUT'&&input.type!=='checkbox')binding(path,input.value);};wrap.append(input);parent.append(wrap);
}
function renderObject(value,rule,path,parent){
 let neutrals=null;
 for(const[key,definition]of Object.entries(rule.properties)){
  const sub=resolve(schema,definition);if(sub['x-hidden']||sub['x-ui']==='id')continue;
  if(sub.type==='string'&&!sub.const){if(!neutrals){neutrals=el('div',null,'neutral-fields');parent.append(neutrals);}renderField(value[key],definition,[...path,key],neutrals,(rule.required||[]).includes(key));}
  else{neutrals=null;renderField(value[key],definition,[...path,key],parent,(rule.required||[]).includes(key));}
 }
}
function addItem(rule,path){const item=resolve(schema,rule.items),kind=item.properties?.kind?.const;
 if(!kind){mutate(()=>at(doc,path).push(item.type==='object'?{en:'',fr:''}:''));return;}
 if(['cor','pib','program'].includes(kind))openChooser({kind,path});
 else{let index;mutate(()=>{const values=at(doc,path);index=values.length;values.push(component(schema,kind));},{render:false});go([...path,index]);}
}
function programPicker(path,parent){
 const wrap=el('div',null,'program-picker'),select=el('select');select.setAttribute('aria-label',text('Assign a program','Assigner un programme'));const empty=el('option',text('Choose a program from this document or the inventory…','Choisir un programme du document ou de l’inventaire…'));empty.value='';select.append(empty);const options=new Map();
 const local=el('optgroup');local.label=text('Programs in this document','Programmes du document');for(const p of collect(doc.payload,'program')){const key='local:'+p.id;options.set(key,{program_id:p.program_id||p.id,program_title:clone(p.title),owner_org:'',document_program_id:p.id});const option=el('option',label(p,lang)+(p.program_id?' · '+p.program_id:''));option.value=key;local.append(option);}if(local.children.length)select.append(local);
 const inventory=el('optgroup');inventory.label=text('Observed Service Inventory program codes','Codes observés dans l’Inventaire des services');for(const[pIndex,p]of programLibrary.programs.entries()){const key='inventory:'+pIndex;options.set(key,{...clone(p),document_program_id:''});const option=el('option',p.program_title[lang]+' · '+p.program_id+' · '+p.owner_org);option.value=key;inventory.append(option);}select.append(inventory);
 wrap.append(select,btn(text('Assign selected program','Assigner le programme choisi'),()=>{const assignment=options.get(select.value);if(!assignment)return;mutate(()=>at(doc,path).push({...component(schema,'program_assignment'),...assignment}));}));parent.append(wrap);
}
function renderArray(value,rule,path,parent){
 const section=el('section',null,'repeat-section');section.dataset.fieldPath=JSON.stringify(path);const heading=el('div',null,'repeat-heading');heading.append(el('h3',titleOf(rule)+' · '+value.length),btn(text('+ Add','+ Ajouter'),()=>addItem(rule,path)));section.append(heading);
 if(path.at(-1)==='people'&&value.length)renderChart(value,path,section);
 if(path.at(-1)==='programs'&&at(doc,path.slice(0,-1))?.kind==='person')programPicker(path,section);
 if(!value.length)section.append(el('p',text('No items yet. Add the parts that apply.','Aucun élément. Ajoutez les éléments applicables.'),'empty-note'));
 value.forEach((item,index)=>{
  const itemRule=resolve(schema,rule.items);
  if(itemRule.type!=='object'||itemRule['x-ui']==='bilingual'){
   const line=el('div',null,'repeat-item'),body=el('div');body.style.flex='1';renderField(item,rule.items,[...path,index],body,true);line.append(body,btn('×',()=>mutate(()=>value.splice(index,1)),'icon'));section.append(line);return;
  }
  const row=el('div',null,'repeat-item'),open=btn('',()=>go([...path,index]),'item-open');open.append(el('strong',label(item,lang)||text('Untitled · click to complete','Sans titre · cliquer pour compléter')));
  const code=item.record_number||item.bank_number||item.program_id||[item.classification_group,item.classification_level].filter(Boolean).join('-');let detail=code;
  if(item.kind==='person'){const manager=collect(doc.payload,'person').find(p=>p.id===item.reports_to);detail=[item.position_title?.[lang],code,manager?text('Reports to ','Relève de ')+manager.name:'',...(item.programs||[]).map(p=>p.program_title?.[lang]||p.program_id)].filter(Boolean).join(' · ');}
  open.append(el('span',detail||titleOf(itemRule)));row.append(open);const actions=el('div',null,'item-actions');
  const up=btn('↑',()=>mutate(()=>{[value[index-1],value[index]]=[value[index],value[index-1]];}));up.disabled=index===0;up.setAttribute('aria-label',text('Move up','Déplacer vers le haut'));
  const down=btn('↓',()=>mutate(()=>{[value[index+1],value[index]]=[value[index],value[index+1]];}));down.disabled=index===value.length-1;down.setAttribute('aria-label',text('Move down','Déplacer vers le bas'));
  const copy=btn('⧉',()=>mutate(()=>{const duplicate=component(schema,item.kind,item);value.splice(index+1,0,duplicate);}));copy.setAttribute('aria-label',text('Duplicate item','Dupliquer l’élément'));
  const remove=btn('×',()=>mutate(()=>value.splice(index,1)));remove.setAttribute('aria-label',text('Remove item · undo available','Supprimer l’élément · annulation disponible'));
  actions.append(up,down,copy,remove);row.append(actions);section.append(row);
 });parent.append(section);
}
function renderChart(people,path,parent){
 const section=el('section',null,'org-chart');section.append(el('h3',text('Chain of command','Chaîne de commandement')),el('p',text('Entered reporting lines · select a position to edit its programs and details.','Liens hiérarchiques saisis · sélectionner un poste pour modifier ses programmes et détails.'),'chart-note'));
 const scroll=el('div',null,'chart-scroll');scroll.tabIndex=0;scroll.setAttribute('aria-label',text('Organization chart. Scroll to see all positions.','Organigramme. Faire défiler pour voir tous les postes.'));
 const canvas=el('div',null,'chart-canvas'),layout=chartLayout(people);canvas.style.width=layout.width+'px';canvas.style.height=layout.height+'px';
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('width',layout.width);svg.setAttribute('height',layout.height);svg.setAttribute('aria-hidden','true');const defs=document.createElementNS(svg.namespaceURI,'defs'),marker=document.createElementNS(svg.namespaceURI,'marker');marker.id='org-arrow';marker.setAttribute('viewBox','0 0 8 8');marker.setAttribute('refX','7');marker.setAttribute('refY','4');marker.setAttribute('markerWidth','6');marker.setAttribute('markerHeight','6');marker.setAttribute('orient','auto');const arrow=document.createElementNS(svg.namespaceURI,'polygon');arrow.setAttribute('points','0,0 8,4 0,8');arrow.setAttribute('fill','#637f92');marker.append(arrow);defs.append(marker);svg.append(defs);const byId=new Map(layout.nodes.map(n=>[n.person.id,n]));
 for(const edge of layout.edges){const from=byId.get(edge.source),to=byId.get(edge.target),p=document.createElementNS(svg.namespaceURI,'path'),x1=from.x+170,y1=from.y+225,x2=to.x+170,y2=to.y;p.setAttribute('d',`M ${x1} ${y1} V ${y1+15} H ${x2} V ${y2}`);p.setAttribute('marker-end','url(#org-arrow)');p.dataset.source=edge.source;p.dataset.target=edge.target;svg.append(p);}canvas.append(svg);
 for(const node of layout.nodes){const p=node.person,index=people.indexOf(p),card=btn('',()=>go([...path,index]),'chart-node');card.style.transform=`translate(${node.x+10}px,${node.y}px)`;card.dataset.positionId=p.id;card.append(el('strong',p.name||text('Name to complete','Nom à compléter')));card.append(el('span',[p.position_title.en,p.position_title.fr].filter(Boolean).join(' / '),'position'));
 const classification=[p.classification_group,p.classification_level].filter(Boolean).join('-');if(classification)card.append(el('span',classification,'classification'));card.append(el('span',[p.organization.en,p.organization.fr].filter(Boolean).join(' / '),'chart-unit'));
 if(!p.programs.length)card.append(el('span',text('Program assignment required','Affectation à un programme requise'),'chart-program'));
 for(const a of p.programs)card.append(el('span',a.program_id+' · '+[a.program_title.en,a.program_title.fr].filter(Boolean).join(' / '),'chart-program'));canvas.append(card);
 }
 scroll.append(canvas);section.append(scroll);const key=el('div',null,'chart-key');key.append(el('span',text('Manager above → reporting position below','Supérieur au-dessus → poste subordonné au-dessous')),el('span',text('No reporting lines are inferred.','Aucun lien hiérarchique n’est déduit.')));section.append(key);parent.append(section);
}
function renderPaper(){
 const paper=$('paper');paper.replaceChildren();let value=at(doc,selected),rule;
 if(value===undefined){selected=['payload'];value=doc.payload;}rule=ruleAt(selected);
 if(selected.length>1)paper.append(btn(text('← Back to parent section','← Revenir à la section parente'),()=>go(selected.slice(0,-1)),'back-to-parent'));
 const top=el('div',null,'paper-top'),left=el('div');left.append(el('span',value?.kind?titleOf(rule):text('DOCUMENT SECTION','SECTION DU DOCUMENT'),'section-type'),el('h2',pathTitle(selected)));top.append(left,el('span','EN / FR','page-mark'));paper.append(top);
 if(rule['x-source']){
  const source=rule['x-source'];let note=source;
  if(/User-requested|user-requested|project-model/.test(source))note=text('Project addition · explicitly entered positions and relationships','Ajout au projet · postes et relations saisis explicitement');
  else if(/privacy_|pia_web|Official bilingual|Official question/.test(source))note=text('Based on the official bilingual TBS template','Fondé sur le modèle bilingue officiel du SCT');
  else note=text('Template basis: ','Fondement du modèle : ')+source;
  paper.append(el('p',note,'section-note'));
 }
 if(rule.type==='array'){renderArray(value,rule,selected,paper);return;}
 if(rule['x-ui']==='bilingual'){renderField(value,rule,selected,paper);return;}
 if(selected.length===1&&(doc.payload.kind==='infosource'||rule['x-document-sections'])){
  const basics=el('div');paper.append(basics);const basicKeys=doc.payload.kind==='infosource'?['institution_name','institution_id','last_updated','introduction']:['title'];for(const key of basicKeys)renderField(value[key],rule.properties[key],[...selected,key],basics,true);
  const sections=el('section',null,'repeat-section');sections.append(el('h3',text('Continue through the document','Poursuivre la rédaction du document')));
  for(const[key,definition]of Object.entries(rule.properties)){if(['kind','id',...basicKeys].includes(key))continue;const row=el('div',null,'repeat-item'),open=btn('',()=>go([...selected,key]),'item-open');open.append(el('strong',titleOf(resolve(schema,definition))),el('span',Array.isArray(value[key])?text(value[key].length+' items',value[key].length+' éléments'):text('Open section','Ouvrir la section')));row.append(open);sections.append(row);}paper.append(sections);
 }else if(rule.type==='object')renderObject(value,rule,selected,paper);
}
function refreshChecks(){
 if(!doc)return;issues=validate(doc,schema);$('issue-count').textContent=issues.length;$('review').classList.toggle('ready',!issues.length);$('review').querySelector('[data-i18n]').textContent=issues.length?text('items to complete','éléments à compléter'):text('Ready for review','Prêt pour examen');
 for(const n of document.querySelectorAll('.editable')){const path=JSON.parse(n.dataset.editPath);n.dataset.invalid=String(issues.some(i=>JSON.stringify(i.parts)===JSON.stringify(path)));}
 $('undo').disabled=!undo.length;$('redo').disabled=!redo.length;
}
function renderAll(){localize();renderSaveStatus();updateTitle();renderSaved();renderOutline();renderBreadcrumbs();renderPaper();refreshChecks();}
function nearestSection(parts){for(let i=parts.length;i>=1;i--){const path=parts.slice(0,i);try{const rule=ruleAt(path);if(rule.type==='array'||(rule.type==='object'&&rule['x-ui']!=='bilingual'))return path;}catch{}}return ['payload'];}
function showReview(){refreshChecks();$('review-summary').textContent=issues.length?text(`${issues.length} items need attention. Drafts can always be saved. Choose an item to go to its section.`,`${issues.length} éléments à compléter. Vous pouvez toujours enregistrer un brouillon. Choisissez un élément pour ouvrir sa section.`):text('The document passes the current schema and content checks. Review factual accuracy, official wording and applicability before publication.','Le document satisfait aux contrôles actuels du schéma et du contenu. Vérifiez l’exactitude, les formulations officielles et l’applicabilité avant publication.');$('issues').replaceChildren();
 for(const issue of issues){const li=el('li'),button=btn(issue.message,()=>{$('review-dialog').close();go(nearestSection(issue.parts));const key=JSON.stringify(issue.parts);const field=[...document.querySelectorAll('[data-edit-path],[data-input-path]')].find(n=>(n.dataset.editPath||n.dataset.inputPath)===key);field?.focus();});li.append(button,el('small',issue.path));$('issues').append(li);}$('review-dialog').showModal();}
function download(content,suffix,mime){const title=label(doc.payload,'en')||doc.payload.kind,name=title.replace(/[^\p{L}\p{N} _-]/gu,'').trim().replace(/\s+/g,'-').slice(0,90)||'document';const blob=new Blob([content],{type:mime}),url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download=name+suffix;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);}
function saveMarkdown(ready){try{const content=exportMarkdown(doc,schema,{ready});download(content,ready?'.md':'.draft.md','text/markdown;charset=utf-8');error('');}catch(e){if(ready)showReview();else error(e.message);}}
function openChooser(context=null){chooser=context;category=context?'all':'publication';$('template-search').value='';$('template-heading').textContent=context?text('Add a reusable component','Ajouter un composant réutilisable'):text('Start from a template','Commencer avec un modèle');renderTemplates();$('template-dialog').showModal();}
function renderTemplates(){
 const categories={all:text('All','Tous'),publication:text('Full documents','Documents complets'),component:text('Reusable components','Composants réutilisables'),internal_service:text('Internal services','Services internes'),standard_cor:text('Standard record classes','Catégories de documents ordinaires'),standard_pib:text('Standard PIBs','FRP ordinaires')};
 let options=catalogue.templates.filter(t=>!chooser||t.kind===chooser.kind);
 if(chooser?.kind==='program'&&chooser.path.at(-1)==='institution_specific')options=options.filter(t=>t.category!=='internal_service');
 $('template-categories').replaceChildren();for(const[key,name]of Object.entries(categories)){if(key!=='all'&&!options.some(t=>t.category===key))continue;const b=btn(name,()=>{category=key;renderTemplates();});b.setAttribute('aria-pressed',String(category===key));$('template-categories').append(b);}
 const query=$('template-search').value.toLocaleLowerCase();$('template-list').replaceChildren();
 for(const template of options.filter(t=>(category==='all'||t.category===category)&&[t.title.en,t.title.fr,t.id,t.seed?.bank_number,t.seed?.record_number].join(' ').toLocaleLowerCase().includes(query))){
  const button=btn('',()=>{if(chooser){const path=chooser.path;let index;mutate(()=>{const values=at(doc,path);index=values.length;const item=component(schema,template.kind,template.seed);if(item.kind==='pib'){const parent=at(doc,path.slice(0,-1));if(parent?.kind==='cor')item.related_record_numbers=[parent.record_number];}values.push(item);},{render:false});go([...path,index]);}else{save();doc=newDocument(schema,template);selected=['payload'];undo=[];redo=[];save();renderAll();}$('template-dialog').close();});button.dataset.templateId=template.id;button.append(el('strong',template.title[lang]||template.title.en),el('small',[template.seed?.bank_number||template.seed?.record_number,categories[template.category]].filter(Boolean).join(' · ')));$('template-list').append(button);
 }
}
async function init(){
 try{
  const paths=['document.schema.json','catalogue.json','library.json','sources.json','programs.json'];const values=await Promise.all(paths.map(async p=>{const response=await fetch('templates/'+p);if(!response.ok)throw Error('Template HTTP '+response.status);return response.json();}));[schema,catalogue,library,sourceInfo,programLibrary]=values;validateSchemaDefinition(schema);
  try{
   recoveryText=localStorage.getItem(KEY);const saved=JSON.parse(recoveryText||'null');
   if(saved){
    if(saved.version!==VERSION)throw Error('Stored version differs');
    for(const[id,value]of Object.entries(saved.documents||{})){try{documents[id]=importDocument(JSON.stringify(value),schema);}catch{storageWritable=false;}}
    doc=documents[saved.current];
   }
  }catch{storageWritable=false;}
  if(!storageWritable&&recoveryText){error(text('Some saved drafts could not be loaded with this schema. The saved data has been preserved; download its recovery JSON before making changes.','Certains brouillons ne peuvent pas être chargés avec ce schéma. Les données enregistrées sont préservées; téléchargez le JSON de récupération avant de modifier.'));$('recover-drafts').hidden=false;}

  if(!doc)doc=newDocument(schema,catalogue.templates.find(t=>t.id==='infosource'));
  localize();renderAll();save();
  $('language').onclick=()=>{lang=lang==='en'?'fr':'en';const url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(null,'',url);renderAll();};
  $('recover-drafts').onclick=()=>download(recoveryText||'{}','.recovery.json','application/json');
  $('new-document').onclick=()=>openChooser();$('template-search').oninput=renderTemplates;
  $('open-document').onclick=()=>$('open-file').click();$('open-file').onchange=async()=>{const file=$('open-file').files[0];if(!file)return;try{const incoming=importDocument(await file.text(),schema);save();doc=incoming;selected=['payload'];undo=[];redo=[];save();renderAll();error('');}catch(e){error(text('The file was not opened. Your current draft is unchanged. ','Le fichier n’a pas été ouvert. Votre brouillon actuel reste intact. ')+e.message);}$('open-file').value='';};
  $('draft-download').onclick=()=>saveMarkdown(false);$('ready-download').onclick=()=>saveMarkdown(true);$('review').onclick=showReview;$('json-download').onclick=()=>download(JSON.stringify(doc,null,2)+'\n','.json','application/json');
  $('saved-documents').onchange=()=>{const chosen=$('saved-documents').value;save();const value=documents[chosen];if(value){doc=clone(value);selected=['payload'];undo=[];redo=[];renderAll();}};
  $('undo').onclick=()=>{if(!undo.length)return;redo.push(clone(doc));doc=undo.pop();save();renderAll();};$('redo').onclick=()=>{if(!redo.length)return;undo.push(clone(doc));doc=redo.pop();save();renderAll();};
  for(const b of document.querySelectorAll('[data-command]')){b.onmousedown=e=>e.preventDefault();b.onclick=()=>{if(!currentEditor?.isConnected)return;currentEditor.focus();document.execCommand(b.dataset.command);currentEditor.dispatchEvent(new Event('input'));};}
  $('insert-link').onmousedown=e=>e.preventDefault();$('insert-link').onclick=()=>{if(!currentEditor?.isConnected)return;const selection=getSelection();savedRange=selection.rangeCount?selection.getRangeAt(0).cloneRange():null;$('link-text').value=selection.toString();$('link-url').value='';$('link-dialog').showModal();};
  $('link-form').onsubmit=e=>{e.preventDefault();if(!validURL($('link-url').value))return;const a=el('a',$('link-text').value);a.href=$('link-url').value;if(savedRange&&currentEditor?.contains(savedRange.commonAncestorContainer)){savedRange.deleteContents();savedRange.insertNode(a);}else currentEditor?.append(a);currentEditor?.dispatchEvent(new Event('input'));$('link-dialog').close();};
  const toggle=hide=>{document.body.classList.toggle('outline-hidden',hide);$('show-outline').hidden=!hide;};$('toggle-outline').onclick=()=>toggle(true);$('show-outline').onclick=()=>toggle(false);
  for(const b of document.querySelectorAll('[data-close]'))b.onclick=()=>b.closest('dialog').close();
  $('sources').onclick=()=>{$('source-summary').textContent=text(`Version ${VERSION} · ${sourceInfo.counts.internal_groups} Internal Services groups · ${sourceInfo.counts.standard_classes} standard record classes · ${sourceInfo.counts.standard_pibs} standard PIBs.`,`Version ${VERSION} · ${sourceInfo.counts.internal_groups} groupes de services internes · ${sourceInfo.counts.standard_classes} catégories de documents ordinaires · ${sourceInfo.counts.standard_pibs} FRP ordinaires.`);$('source-list').replaceChildren();for(const source of sourceInfo.sources){const rootId=source.id.replace(/-(?:en|fr)$/,'');const names={requirements:text('Info Source publishing requirements','Exigences de publication Info Source'),internal:text('Internal Services template','Modèle des services internes'),classes:text('Standard classes of records','Catégories de documents ordinaires'),banks:text('Standard personal information banks','Fichiers de renseignements personnels ordinaires'),'pib-submission':titleOf(schema.$defs.pib_submission)};const title=names[rootId]||titleOf(schema.$defs[rootId])||source.id;const li=el('li'),a=el('a',title+' · '+source.language.toUpperCase());a.href=source.url;a.target='_blank';a.rel='noopener';li.append(a);$('source-list').append(li);}$('sources-dialog').showModal();};
  window.addEventListener('pagehide',save);
 }catch(e){error(text('The editor could not load its templates. Reload to try again. ','Impossible de charger les modèles. Rechargez pour réessayer. ')+e.message);$('save-status').textContent=text('Templates unavailable','Modèles indisponibles');}
}
init();
