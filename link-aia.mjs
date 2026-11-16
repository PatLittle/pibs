import { loadAIA, fold } from './aia-data.mjs';
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search), lang = params.get('lang') === 'fr' ? 'fr' : 'en';
const fr = lang === 'fr';
const words = {
  skip:'Aller au contenu principal', eyebrow:'Algorithmes et responsabilité', title:'Liens EIA', intro:'Explorez les évaluations de l’incidence algorithmique, les cadres qui y sont nommés et leurs liens avec les fonds de renseignements fédéraux.',
  browse:'Parcourir les évaluations', network:'Explorer le réseau', loading:'Chargement de la source EIA externe…', retry:'Réessayer',
  notice:'Les chiffres décrivent cette source, pas tous les systèmes d’IA fédéraux. Les niveaux d’incidence proviennent de la source d’analyse; ils ne sont pas recalculés ici. Un nom de cadre est une observation de source, sans confirmation du mandat actuel. Les répondants sont distincts.',
  scope:'Portée et composition', scopeNote:'Les graphiques décrivent toute la source chargée. Les filtres ci-dessous s’appliquent au tableau.', risk:'Niveau d’incidence', version:'Version du questionnaire', organizations:'Organisations', organization:'Organisation', provenance:'Provenance',
  officials:'Cadres supérieurs responsables', officialNote:'Seul le champ ADMresponsible fournit ce rôle. Les noms de la source et de sa traduction sont conservés dans les champs EN/FR. Le u_id généré regroupe le même nom normalisé dans une organisation; ce n’est pas un identifiant officiel de personne. Les noms absents restent absents.',
  nameEN:'Nom (EN/source)', nameFR:'Nom (FR/traduction)', records:'Évaluations', find:'Trouver une EIA', search:'Titre, nom, identifiant ou document cité', all:'Tous', named:'Nommé', missing:'Non indiqué', clear:'Effacer les filtres', assessment:'Évaluation / ID', references:'Références explicites',
  matching:'Quels éléments relier?', inventory:'Inventaire des champs et disponibilité', inventoryNote:'Valeurs non vides par champ dans les données chargées. Un champ peut être absent selon la version du questionnaire. Les codes de réponse sont conservés; leur sens doit être vérifié dans cette version.', field:'Champ source', available:'Documents disponibles', types:'Types de valeurs', methodology:'Inventaire et méthode de rapprochement', source:'Source EIA externe'
};
const text = (en, french) => fr ? french : en;
const el = (tag, value, cls) => { const n=document.createElement(tag); if(value!=null)n.textContent=value; if(cls)n.className=cls; return n; };
const link = (label, href) => { const a=el('a',label); try { const u=new URL(href,location.href); if(['http:','https:'].includes(u.protocol))a.href=u.href; } catch {} return a; };
const name = r => (fr ? r.title_fr : r.title_en) || r.title_en || r.title_fr || r.package_id;
const org = r => { const parts=String((fr?r.organization_fr:r.organization_en)||r.organization_en||'').split('|'); return (fr ? parts[1] || parts[0] : parts[0]).trim(); };
const missing = () => text('Not recorded','Non indiqué');
const level = r => [1,2,3,4].includes(r.derived?.impact_level) ? String(r.derived.impact_level) : missing();
let loaded;
function localize() {
  document.documentElement.lang=lang; document.title=text('Link AIA','Liens EIA')+' - Info Source Data Explorer';
  if(fr)document.querySelectorAll('[data-aia]').forEach(n=>{ n.textContent=words[n.dataset.aia]||n.textContent; });
  const alternate=new URL(location.href); alternate.searchParams.set('lang',fr?'en':'fr');
  document.querySelector('gcds-header').setAttribute('lang-href',alternate.href);
  const nav={'Overview':'Aperçu','Institution data':'Données institutionnelles','Reference data':'Données de référence','PIBs':'FRP','Classes of Records':'Catégories de documents','PIB-to-class linkages':'Liens FRP-catégories','Standard PIBs':'FRP ordinaires','Standard classes':'Catégories ordinaires','Categories':'Catégories','PIB types':'Types de FRP','Privacy Assessments':'Évaluations de la vie privée','PI Network Explorer':'Explorateur du réseau','Link AIA':'Liens EIA'};
  document.querySelectorAll('gcds-nav-link').forEach(n=>{
    if(fr)n.textContent=nav[n.textContent.trim()]||n.textContent;
    const u=new URL(n.getAttribute('href'),location.href); u.searchParams.set('lang',lang); n.setAttribute('href',u.pathname.split('/').pop()+u.search);
  });
  if(fr)document.querySelectorAll('gcds-nav-group').forEach(n=>{ const label=nav[n.getAttribute('open-trigger')]; n.setAttribute('open-trigger',label); n.setAttribute('close-trigger','Fermer : '+label); n.setAttribute('menu-label',label); });
}
function bars(id, values) {
  const counts=new Map(); values.forEach(v=>counts.set(v,(counts.get(v)||0)+1)); $(id).replaceChildren();
  [...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).forEach(([label,count])=>{
    const row=el('div',null,'aia-chart-row'), heading=el('div'); heading.append(el('span',label),el('strong',`${count} / ${values.length}`));
    const progress=el('progress'); progress.max=values.length||1; progress.value=count; progress.setAttribute('aria-label',`${label}: ${count} / ${values.length}`); row.append(heading,progress); $(id).append(row);
  });
}
function optionList(id, values) { $(id).replaceChildren(); const all=el('option',text('All','Tous')); all.value=''; $(id).append(all); [...new Set(values)].sort((a,b)=>a.localeCompare(b)).forEach(v=>{const o=el('option',v);o.value=v;$(id).append(o);}); }
function graphLink(id, title=text('Explore network','Explorer le réseau')) { return link(title,'graph.html?node='+encodeURIComponent(id)+'&lang='+lang); }
function refList(record, container) {
  if(!record.references.length) { container.append(el('p',text('No explicit identifiers or matched PIA URLs detected.','Aucun identifiant explicite ni URL d’EFVP correspondante détecté.'))); return; }
  const nodes=new Map(loaded.graph.nodes.map(n=>[n.id,n]));
  for(const ref of record.references) {
    const box=el('div',null,'aia-reference'); box.append(el('strong',ref.mention));
    if(ref.resolution==='resolved') { const target=nodes.get(ref.candidates[0]); box.append(el('p',target['label_'+lang]||target.label_en||target.label_fr),graphLink(target.id)); }
    else box.append(el('p',ref.resolution==='ambiguous'?text('Ambiguous: no unique target.','Ambigu : aucune cible unique.'):text('Unresolved: no matching collected record.','Non résolu : aucun document recueilli correspondant.')));
    const details=el('details'); details.append(el('summary',text('Source evidence','Preuve dans la source')));
    for(const e of ref.evidence)details.append(el('p',e.field+' · '+e.language),el('blockquote',e.excerpt),link(text('Original dataset','Jeu de données original'),e.source_url));
    box.append(details);container.append(box);
  }
}
function openRecord(record, navigate=true) {
  const section=$('record-detail'); section.hidden=false; section.replaceChildren(el('h2',name(record)),el('p',record.package_id));
  const fields=el('dl',null,'aia-detail-fields');
  const official=record.official;
  const pairs=[['Organization','Organisation',org(record)],['Responsible official (EN/source)','Cadre responsable (EN/source)',official?.name_en],['Responsible official (FR/translation)','Cadre responsable (FR/traduction)',official?.name_fr],['Official u_id','u_id du cadre',official?.u_id],['Respondent (separate role)','Répondant (rôle distinct)',record.data.projectDetailsRespondent],['Impact level (feed-derived)','Niveau d’incidence (calculé par la source)',level(record)],['Survey version','Version du questionnaire',record.version],['Raw risk score (source-derived)','Score de risque brut (source)',record.derived?.raw_risk_score],['Mitigation score (source-derived)','Score d’atténuation (source)',record.derived?.mitigation_score],['Final score (source-derived)','Score final (source)',record.derived?.final_score],['Project phase','Phase du projet',record.derived?.project_phase],['Completeness (%)','Complétude (%)',record.derived?.completeness_pct],['Program','Programme',record.data.projectDetailsProgram],['Service ID (source value)','ID du service (valeur source)',record.data.ServiceID],['Project ID (not a global key)','ID du projet (pas une clé globale)',record.data.projectDetailsID],['AIA number (source value)','Numéro EIA (valeur source)',record.data.projectAIAnumber],['Provenance','Provenance',record.source],['Metadata modified','Métadonnées modifiées',record.metadata_modified]];
  for(const [en,french,value]of pairs)fields.append(el('dt',text(en,french)),el('dd',value===0?0:value||missing()));
  section.append(fields,el('p',(fr?record.translationsOnResult?.projectDetailsDescription:record.data.projectDetailsDescription)||record.data.projectDetailsDescription||''));
  const actions=el('div',null,'aia-detail-actions'); actions.append(graphLink(record.id),link(text('Original dataset','Jeu de données original'),record.dataset_url));
  if(record.institution_id)actions.append(graphLink('institution:'+record.institution_id,text('Institution and its holdings','Institution et ses fonds')));
  if(official)actions.append(graphLink('official:'+official.u_id,text('Official in network','Cadre dans le réseau')));
  section.append(actions,el('h3',text('Explicit references','Références explicites')));refList(record,section);
  const privacy=el('details');privacy.append(el('summary',text('Privacy-assessment evidence and review leads','Éléments relatifs à la vie privée et pistes à examiner')));
  for(const parent of ['data','translationsOnResult'])for(const[k,v]of Object.entries(record[parent]||{}))if(/^privacy/.test(k)&&typeof v==='string'&&!/^item\d/.test(v)&&v.trim())privacy.append(el('h4',parent+'.'+k),el('p',v));
  const q=record.data.projectDetailsTitle||name(record);
  privacy.append(el('p',text('Similar project titles are review leads; they do not create confirmed relationships.','Les titres de projets similaires sont des pistes; ils ne créent pas de relations confirmées.')),link(text('Search collected PIAs','Rechercher les EFVP recueillies'),'privacy-assessments.html?q='+encodeURIComponent(q)));
  section.append(privacy);
  if(navigate){const u=new URL(location.href);u.searchParams.set('record',record.package_id);u.searchParams.delete('official');u.hash='record-detail';history.pushState(null,'',u);section.scrollIntoView({behavior:'smooth'});section.focus({preventScroll:true});}
}
function renderRecords() {
  const query=fold($('aia-search').value), organization=$('aia-organization').value, risk=$('aia-risk').value, version=$('aia-version').value, official=$('aia-official').value;
  const matches=loaded.records.filter(r=>(!query||fold([r.title_en,r.title_fr,r.package_id,r.data.projectDetailsTitle,r.data.projectDetailsID,r.data.projectAIAnumber,org(r),r.official?.name_en,r.official?.name_fr,r.official?.u_id,r.data.projectDetailsRespondent,...r.references.map(x=>x.mention)].join(' ')).includes(query))&&(!organization||org(r)===organization)&&(!risk||level(r)===risk)&&(!version||(r.version||missing())===version)&&(!official||(official==='yes')===!!r.official));
  $('aia-results').textContent=text(`${matches.length} of ${loaded.records.length} assessments`,`${matches.length} évaluations sur ${loaded.records.length}`);$('aia-rows').replaceChildren();
  for(const r of matches){const tr=el('tr'),title=el('td'),button=el('button',name(r),'aia-link-button');button.type='button';button.addEventListener('click',()=>openRecord(r));title.append(button,el('code',r.package_id),graphLink(r.id));const officialCell=el('td',r.official?.['name_'+lang]||r.official?.name_en||missing());if(r.official)officialCell.append(el('code',r.official.u_id));tr.append(title,el('td',org(r)),officialCell,el('td',level(r)),el('td',r.version||missing()));const refs=el('td'); for(const ref of r.references)refs.append(el('div',ref.mention+' · '+(ref.resolution==='resolved'?text('matched','lié'):ref.resolution==='ambiguous'?text('ambiguous','ambigu'):text('unresolved','non résolu'))));if(!r.references.length)refs.textContent='—';tr.append(refs);$('aia-rows').append(tr);}
  if(!matches.length){const td=el('td',text('No matching assessments. Clear filters to see all records.','Aucun résultat. Effacez les filtres pour tout voir.'));td.colSpan=6;const tr=el('tr');tr.append(td);$('aia-rows').append(tr);}
}
function inventory() {
  const counts=new Map();
  const walk=(obj,prefix='')=>{for(const[k,v]of Object.entries(obj||{})){const field=prefix+k;if(v&&typeof v==='object'&&!Array.isArray(v))walk(v,field+'.');else if(v!==null&&v!==''&&v!==undefined&&(!Array.isArray(v)||v.length)){const entry=counts.get(field)||{count:0,types:new Set()};entry.count++;entry.types.add(Array.isArray(v)?'array':typeof v);counts.set(field,entry);}}};
  loaded.records.forEach(r=>{const {id,institution_id,organization_match,official,references,...source}=r;walk(source);});
  $('inventory-rows').replaceChildren();for(const[field,entry]of [...counts].sort((a,b)=>a[0].localeCompare(b[0]))){const tr=el('tr');tr.append(el('td',field),el('td',`${entry.count} / ${loaded.records.length}`),el('td',[...entry.types].join(', ')));$('inventory-rows').append(tr);}
}
function renderOverview() {
  const rows=loaded.records, named=rows.filter(r=>r.official), officials=new Map();
  named.forEach(r=>{if(!officials.has(r.official.u_id))officials.set(r.official.u_id,{...r.official,organization:org(r),records:[]});officials.get(r.official.u_id).records.push(r);});
  $('aia-stats').replaceChildren();for(const[count,label,note]of [[rows.length,text('AIA records','Documents EIA'),text('one per source package UUID','un par UUID de jeu de données')],[new Set(rows.map(org)).size,text('organizations','organisations'),text(`${rows.filter(r=>r.institution_id).length} assessments matched to registry`,`${rows.filter(r=>r.institution_id).length} évaluations liées au registre`)],[officials.size,text('named senior officials','cadres supérieurs nommés'),text(`${named.length} / ${rows.length} assessments`,`${named.length} évaluations sur ${rows.length}`)],[rows.length-named.length,text('without a named senior official','sans cadre supérieur nommé'),text('respondents excluded','répondants exclus')]]){const card=el('article',null,'stat-card');card.append(el('span',count,'stat-card__value'),el('span',label,'stat-card__label'),el('span',note,'stat-card__note'));$('aia-stats').append(card);}
  $('source-details').replaceChildren(link(loaded.config.label,loaded.config.url),document.createTextNode(text(` · Loaded: ${loaded.loaded_at} · Source last modified: ${loaded.source_modified||'not supplied'}. Temporary source location; review after ${loaded.config.location_review_after}.`,` · Chargé : ${loaded.loaded_at} · Dernière modification de la source : ${loaded.source_modified||'non fournie'}. Emplacement temporaire; révision après le ${loaded.config.location_review_after}.`)));
  $('aia-source-link').href=loaded.config.url;
  bars('risk-bars',rows.map(r=>level(r)===missing()?missing():text('Level ','Niveau ')+level(r)));bars('version-bars',rows.map(r=>r.version||missing()));bars('organization-bars',rows.map(org));bars('provenance-bars',rows.map(r=>r.source||missing()));
  $('official-rows').replaceChildren();for(const o of officials.values()){const tr=el('tr');tr.append(el('td',o.name_en||missing()),el('td',o.name_fr||missing()),el('td',o.u_id),el('td',o.organization));const td=el('td');o.records.forEach(r=>{const b=el('button',name(r),'aia-link-button');b.type='button';b.addEventListener('click',()=>openRecord(r));td.append(b);});tr.append(td);$('official-rows').append(tr);}
  if(!officials.size){const tr=el('tr'),td=el('td',missing());td.colSpan=5;tr.append(td);$('official-rows').append(tr);}
  optionList('aia-organization',rows.map(org));optionList('aia-risk',rows.map(level));optionList('aia-version',rows.map(r=>r.version||missing()));
  const refs=rows.flatMap(r=>r.references), resolved=refs.filter(r=>r.resolution==='resolved').length;
  $('match-summary').textContent=text(`${rows.filter(r=>r.institution_id).length}/${rows.length} organization matches · ${resolved} matched reference groups · ${refs.length-resolved} unresolved or ambiguous reference groups. Bilingual mentions with the same matched targets form one group.`,`${rows.filter(r=>r.institution_id).length}/${rows.length} rapprochements d’organisation · ${resolved} groupes de références liés · ${refs.length-resolved} groupes non résolus ou ambigus. Les mentions bilingues avec les mêmes cibles forment un groupe.`);
  const plan=[text('Organization → institution: unique exact match against bilingual registry names and aliases. Department survey numbers are retained as source values, never treated as gc_orgID.','Organisation → institution : correspondance exacte et unique avec les noms et alias bilingues du registre. Les numéros de ministère du questionnaire ne sont pas traités comme des gc_orgID.'),text('PIB / Class of Records: link explicit identifiers to a unique collected record. Bare institutional PIB numbers resolve within the owner; full prefixes can cite another institution. Follow PIB → class links in the network for indirect paths.','FRP / catégorie de documents : relier les identifiants explicites à un document unique. Les numéros de FRP sans préfixe sont limités à l’institution; un préfixe complet peut citer une autre institution. Suivre les liens FRP → catégorie pour les parcours indirects.'),text('PIA: exact cited source URL can establish a reference. Program names, project titles and privacy narratives are review leads requiring confirmation.','EFVP : une URL source citée exacte peut établir une référence. Les noms de programmes, titres et récits sont des pistes à confirmer.'),text('Senior official: ADMresponsible → organization-scoped name and stable u_id. Match to the senior officials collection only after name + organization + date review; no automatic person merge.','Cadre supérieur : ADMresponsible → nom limité à l’organisation et u_id stable. Rapprocher avec la collection des cadres seulement après examen du nom, de l’organisation et des dates; aucune fusion automatique.'),text('Survey version and impact level: retain the supplied version and derived impact_level. Do not compare raw answer codes or recompute risk across versions without the correct survey definitions.','Version et niveau d’incidence : conserver la version et derived.impact_level fournis. Ne pas comparer les codes bruts ni recalculer les scores entre versions sans leurs définitions.')];
  const ul=el('ul');plan.forEach(p=>ul.append(el('li',p)));$('match-plan').replaceChildren(ul);inventory();renderRecords();
  const selected=rows.find(r=>r.package_id===params.get('record'));if(selected)openRecord(selected,false);
  if(params.has('record')&&!selected)$('aia-status').textContent=text('The requested AIA is not in the current feed. Browse the available records below.','L’EIA demandée ne figure pas dans la source actuelle. Consultez les documents ci-dessous.');
  const official=rows.find(r=>r.official?.u_id===params.get('official'));if(official){$('aia-search').value=official.official.u_id;renderRecords();}
}
async function init(){ $('retry').hidden=true; $('aia-status').setAttribute('role','status');$('aia-status').textContent=text('Loading the external AIA source…','Chargement de la source EIA externe…');try{const response=await fetch('data/graph.json');if(!response.ok)throw new Error('Holdings HTTP '+response.status);loaded=await loadAIA(await response.json());$('aia-content').hidden=false;$('aia-status').textContent=text('External AIA source loaded.','Source EIA externe chargée.');renderOverview();}catch(error){$('aia-content').hidden=true;$('aia-status').setAttribute('role','alert');$('aia-status').textContent=text('The external AIA feed could not be loaded. Retry or open the external source below. No saved copy is held in this repository.','La source EIA externe n’a pas pu être chargée. Réessayez ou ouvrez la source ci-dessous. Aucune copie n’est conservée dans ce dépôt.');$('retry').hidden=false;console.warn(error);}}
localize();$('retry').addEventListener('click',init);$('aia-filters').addEventListener('submit',e=>e.preventDefault());for(const id of ['aia-search','aia-organization','aia-risk','aia-version','aia-official'])$(id).addEventListener(id==='aia-search'?'input':'change',()=>loaded&&renderRecords());$('clear').addEventListener('click',()=>{$('aia-filters').reset();renderRecords();});window.addEventListener('popstate',()=>{if(!loaded)return;const id=new URLSearchParams(location.search).get('record');const record=loaded.records.find(r=>r.package_id===id);if(record)openRecord(record,false);else $('record-detail').hidden=true;});init();
