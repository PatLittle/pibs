// One schema governs defaults, editing, import and export. No source prose executes.
export const VERSION = '1.0.0';
export const SCHEMA_ID = 'https://patlittle.github.io/pibs/document-studio/templates/document.schema.json';
const stable = v => JSON.stringify(v, function(k,value){return value && typeof value === 'object' && !Array.isArray(value) ? Object.fromEntries(Object.keys(value).sort().map(key=>[key,value[key]])) : value;});
export const clone = value => structuredClone(value);
export const uid = () => 'ds-' + crypto.randomUUID();
export const pointer = parts => '/' + parts.map(p=>String(p).replace(/~/g,'~0').replace(/\//g,'~1')).join('/');
export function at(object, parts) { return parts.reduce((v,k)=>v?.[k],object); }
export function put(object, parts, value) {
  if(parts.some(p=>['__proto__','prototype','constructor'].includes(String(p)))) throw Error('Invalid document path');
  let parent=object;for(const key of parts.slice(0,-1))parent=parent[key];parent[parts.at(-1)]=value;
}
export function resolve(schema, rule) {
  if(!rule.$ref)return rule;
  if(!/^#\/\$defs\/[^/]+$/.test(rule.$ref))throw Error('Only local schema definitions are supported');
  const definition=schema.$defs[rule.$ref.split('/').at(-1)];
  if(!definition)throw Error('Unknown schema reference');
  return {...definition,...Object.fromEntries(Object.entries(rule).filter(([k])=>k!=='$ref'))};
}
export function defaults(schema, rule) {
  rule=resolve(schema,rule);
  if('const' in rule)return clone(rule.const);
  if('default' in rule)return clone(rule.default);
  if(rule.type==='object')return Object.fromEntries(Object.entries(rule.properties).map(([k,v])=>[k,k==='id'?uid():defaults(schema,v)]));
  if(rule.type==='array')return [];
  if(rule.enum)return rule.enum[0];
  if(rule.type==='boolean')return false;
  return '';
}
export function renewIds(value) {
  const mapping=new Map();
  function walk(v){if(!v||typeof v!=='object')return;if(!Array.isArray(v)&&v.kind&&v.id){const old=v.id;v.id=uid();mapping.set(old,v.id);}for(const child of Object.values(v))walk(child);}
  walk(value);
  function links(v){if(!v||typeof v!=='object')return;for(const[k,item]of Object.entries(v)){if(['reports_to','document_program_id'].includes(k)&&mapping.has(item))v[k]=mapping.get(item);else links(item);}}
  links(value);return value;
}
export function component(schema, kind, seed=null) {
  const value=defaults(schema,schema.$defs[kind]);
  if(seed)Object.assign(value,renewIds(clone(seed)));
  return value;
}
export function newDocument(schema, template) {
  const payload=component(schema,template.kind,template.seed);
  if(payload.kind==='infosource')payload.last_updated=new Date().toISOString().slice(0,10);
  return {schema_version:VERSION,schema_id:SCHEMA_ID,document_id:uid(),status:'draft',payload};
}

const SUPPORTED=new Set(['$schema','$id','$defs','$ref','title','description','type','const','enum','properties','required','additionalProperties','items','minLength','minItems','uniqueItems','format','default','readOnly','oneOf','anyOf']);
export function validateSchemaDefinition(schema) {
  function walk(rule){if(rule.format&&!['date','uri','email'].includes(rule.format))throw Error('Unsupported schema format: '+rule.format);if(rule.type&&!['string','object','array','boolean'].includes(rule.type))throw Error('Unsupported schema type: '+rule.type);for(const key of Object.keys(rule))if(!SUPPORTED.has(key)&&!key.startsWith('x-'))throw Error('Unsupported schema keyword: '+key);
    for(const value of Object.values(rule.properties||{}))walk(value);
    for(const value of Object.values(rule.$defs||{}))walk(value);
    if(rule.items)walk(rule.items);for(const value of [...(rule.oneOf||[]),...(rule.anyOf||[])])walk(value);
  }
  walk(schema);return true;
}
export function validate(document,schema,{complete=true}={}) {
  const issues=[];
  const issue=(path,keyword,message)=>issues.push({path:pointer(path),parts:path,keyword,message});
  function visit(value,rule,path,locked=false){
    rule=resolve(schema,rule);locked=locked||Boolean(rule.readOnly);
    if(rule.anyOf){
      const base=issues.length;let matched=false;
      for(const branch of rule.anyOf){visit(value,branch,path,locked);if(issues.length===base)matched=true;issues.splice(base);if(matched)break;}
      if(!matched)issue(path,'anyOf','Use a valid value or leave this optional field empty / Utiliser une valeur valide ou laisser ce champ facultatif vide.');
    }
    if(rule.oneOf){
      // The document union is discriminated by its payload kind; unknown kinds fail closed.
      const choices=rule.oneOf.filter(r=>resolve(schema,r).properties?.kind?.const===value?.kind);
      if(choices.length!==1){issue(path,'oneOf','Choose a supported document type / Choisir un type de document reconnu.');return;}
      visit(value,choices[0],path);return;
    }
    const actual=value===null?'null':Array.isArray(value)?'array':typeof value;
    if(rule.type&&actual!==rule.type){issue(path,'type','Expected '+rule.type+' / Type attendu : '+rule.type);return;}
    if('const' in rule&&stable(value)!==stable(rule.const))issue(path,'const','The template identity or fixed source text has changed / Identité du modèle ou texte fixe modifié.');
    if(rule.enum&&!rule.enum.includes(value))issue(path,'enum','Choose an allowed value / Choisir une valeur permise.');
    if(actual==='object'&&value){
      for(const key of rule.required||[])if(!(key in value))issue([...path,key],'required','Required field / Champ obligatoire.');
      for(const[k,v]of Object.entries(value)){
        if(rule.properties?.[k])visit(v,rule.properties[k],[...path,k],locked);
        else if(rule.additionalProperties===false)issue([...path,k],'additionalProperties','This field is outside this document schema / Champ absent du schéma.');
      }
      if(complete&&rule['x-ui']==='bilingual'&&Boolean(value.en?.trim())!==Boolean(value.fr?.trim()))issue(path,'bilingual','Complete both English and French / Remplir en anglais et en français.');
    }
    if(actual==='array'){
      if(complete&&value.length<(rule.minItems||0))issue(path,'minItems','Add at least '+rule.minItems+' item(s) / Ajouter au moins '+rule.minItems+' élément(s).');
      if(rule.uniqueItems&&new Set(value.map(v=>JSON.stringify(v))).size!==value.length)issue(path,'uniqueItems','Remove duplicate values / Supprimer les doublons.');
      value.forEach((v,i)=>visit(v,rule.items,[...path,i],locked));
    }
    if(actual==='string'){
      if(complete&&value.trim().length<(rule.minLength||0))issue(path,'minLength','Complete this field / Remplir ce champ.');
      if(complete&&value&&rule.format==='uri'&&!validURL(value))issue(path,'format','Use a complete http(s) URL / Utiliser une URL http(s) complète.');
      if(complete&&value&&rule.format==='date'&&!validDate(value))issue(path,'format','Use a valid YYYY-MM-DD date / Utiliser une date AAAA-MM-JJ valide.');
      if(complete&&value&&rule.format==='email'&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))issue(path,'format','Use a valid email address / Utiliser une adresse courriel valide.');
      if(complete&&!locked&&/\[(?:insert|insérez|ins[eé]rer)\b|\bTODO\b|\bTBD\b/i.test(value))issue(path,'placeholder','Replace the placeholder / Remplacer le texte provisoire.');
    }
  }
  visit(document,schema,[]);
  const ids=new Set(),people=[],programs=new Map();
  function all(value,path=[]){
    if(!value||typeof value!=='object')return;
    if(value.kind&&value.id){if(ids.has(value.id))issue([...path,'id'],'uniqueId','Duplicate component ID / ID de composant en double.');ids.add(value.id);}
    if(value.kind==='program')programs.set(value.id,value);
    if(value.kind==='person')people.push({value,path});
    if(complete&&value.kind&&Object.prototype.hasOwnProperty.call(value,'not_applicable_explanation')&&Object.values(value).some(v=>v==='not_applicable')&&(!value.not_applicable_explanation?.en?.trim()||!value.not_applicable_explanation?.fr?.trim()))issue([...path,'not_applicable_explanation'],'conditionalReason','Explain conditional not-applicable answers in both languages / Expliquer les réponses conditionnellement non applicables dans les deux langues.');
    if(complete&&value.kind&&value.answer==='not_applicable'&&(!value.justification?.en?.trim()||!value.justification?.fr?.trim()))issue([...path,'justification'],'conditionalReason','Explain why this question does not apply in both languages / Expliquer dans les deux langues pourquoi cette question ne s’applique pas.');
    if(complete&&schema.$defs[value.kind]?.['x-repeating-table']){
      if(value.applicability==='applicable'&&!value.rows?.length)issue([...path,'rows'],'required','Add at least one row / Ajouter au moins une ligne.');
      if(value.applicability==='not_applicable'&&(!value.not_applicable_reason?.en?.trim()||!value.not_applicable_reason?.fr?.trim()))issue([...path,'not_applicable_reason'],'required','Explain why this table does not apply in both languages / Expliquer dans les deux langues pourquoi ce tableau ne s’applique pas.');
      if(value.applicability==='not_applicable'&&value.rows?.length)issue([...path,'rows'],'conflict','Remove rows or mark the table applicable / Supprimer les lignes ou indiquer que le tableau s’applique.');
    }
    if(complete&&value.kind==='cor'){
      if(value.disclosure_status==='not_reviewed')issue([...path,'disclosure_status'],'review','Record the disclosure review result / Indiquer le résultat de l’examen des communications.');
      if(value.disclosure_status==='none'&&(!value.no_disclosure_statement?.en?.trim()||!value.no_disclosure_statement?.fr?.trim()))issue([...path,'no_disclosure_statement'],'required','State that no applicable disclosures occurred in both languages / Indiquer dans les deux langues l’absence de communications applicables.');
      if(value.disclosure_status==='disclosed'&&!value.disclosures?.length)issue([...path,'disclosures'],'required','Add the applicable disclosure summaries / Ajouter les résumés des communications applicables.');
      if(value.disclosure_status==='none'&&value.disclosures?.length)issue([...path,'disclosures'],'conflict','Disclosures conflict with the none statement / Communications incompatibles avec la déclaration d’absence.');
      for(let i=0;i<(value.pibs||[]).length;i++)if(value.pibs[i].related_record_numbers?.length&&!value.pibs[i].related_record_numbers.includes(value.record_number))issue([...path,'pibs',i,'related_record_numbers'],'foreignKey','The PIB must refer to its containing class / Le FRP doit référencer sa catégorie parente.');
    }
    if(complete&&value.kind==='pib'){
      if(value.sin_collection==='not_reviewed')issue([...path,'sin_collection'],'review','Review whether SIN is collected / Vérifier si le NAS est recueilli.');
      if(value.sin_collection==='yes'&&(!value.sin_authority?.en?.trim()||!value.sin_authority?.fr?.trim()))issue([...path,'sin_authority'],'required','Provide the SIN authority in both languages / Indiquer l’autorisation de collecte du NAS dans les deux langues.');
      if(value.approval_status!=='registered'&&(!value.note?.en?.trim()||!value.note?.fr?.trim()))issue([...path,'note'],'required','Explain pending approval, modification or termination in both languages / Décrire l’approbation, modification ou suppression en attente dans les deux langues.');
    }
    if(complete&&value.kind==='pib_submission'){
      if(['modify_registered','transfer','terminate'].includes(value.request_type)&&!value.current_registration_number?.trim())issue([...path,'current_registration_number'],'required','Provide the existing registration number / Indiquer le numéro d’enregistrement existant.');
      const fields=value.request_type==='transfer'?['transfer_explanation','transfer_confirmations']:value.request_type==='terminate'?['termination_explanation','termination_confirmation']:[];
      for(const field of fields)if(!value[field]?.en?.trim()||!value[field]?.fr?.trim())issue([...path,field],'required','Complete the explanation and confirmation references in both languages / Fournir les explications et références aux confirmations dans les deux langues.');
    }
    if(complete&&value.kind==='infosource'&&Boolean(value.additional_information?.open_data_url_en)!==Boolean(value.additional_information?.open_data_url_fr))issue([...path,'additional_information','open_data_url_fr'],'bilingual','Provide both official-language open-data links or leave both empty / Fournir les deux liens de données ouvertes ou laisser les deux vides.');
    if(complete&&value.kind==='infosource'&&value.background?.subsidiaries?.length&&(!value.background.subsidiary_statement?.en?.trim()||!value.background.subsidiary_statement?.fr?.trim()))issue([...path,'background','subsidiary_statement'],'required','Explain coverage of subsidiaries / Expliquer la couverture des filiales.');
    for(const[k,v]of Object.entries(value))all(v,[...path,k]);
  }
  all(document);
  const byPerson=new Map(people.map(p=>[p.value.id,p]));
  for(const{value:p,path}of people){
    if(complete&&p.reports_to&&!byPerson.has(p.reports_to))issue([...path,'reports_to'],'foreignKey','Choose a manager in this document / Choisir un supérieur dans ce document.');
    const seen=new Set([p.id]);let manager=p.reports_to;
    while(complete&&manager&&byPerson.has(manager)){if(seen.has(manager)){issue([...path,'reports_to'],'cycle','Reporting lines must not form a cycle / Les liens hiérarchiques ne doivent pas former de cycle.');break;}seen.add(manager);manager=byPerson.get(manager).value.reports_to;}
    if(complete&&Boolean(p.classification_group?.trim())!==Boolean(p.classification_level?.trim()))issue([...path,'classification_level'],'classification','Provide classification group and level together, or leave both empty when not applicable / Fournir le groupe et le niveau ensemble, ou laisser les deux vides si non applicables.');
    if(complete&&p.effective_from&&p.effective_to&&p.effective_from>p.effective_to)issue([...path,'effective_to'],'dateOrder','End date precedes start date / La date de fin précède le début.');
    (p.programs||[]).forEach((assignment,i)=>{
      if(complete&&!assignment.document_program_id&&!assignment.owner_org?.trim())issue([...path,'programs',i,'owner_org'],'required','Provide the organization code for an external program / Indiquer le code d’organisation du programme externe.');
      if(complete&&assignment.document_program_id&&!programs.has(assignment.document_program_id))issue([...path,'programs',i,'document_program_id'],'foreignKey','The assigned document program was removed / Le programme assigné a été supprimé du document.');
    });
  }
  return issues;
}
export function validDate(value){return /^\d{4}-\d{2}-\d{2}$/.test(value)&&!Number.isNaN(Date.parse(value+'T00:00:00Z'))&&new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value;}
export function validURL(value){try{const u=new URL(value);return ['http:','https:'].includes(u.protocol)&&Boolean(u.hostname);}catch{return false;}}
export function collect(value,kind,result=[]){if(value&&typeof value==='object'){if(value.kind===kind)result.push(value);for(const v of Object.values(value))collect(v,kind,result);}return result;}
export function label(value,lang='en'){const result=value?.title?.[lang]||value?.institution_name?.[lang]||value?.position_title?.[lang]||value?.program_title?.[lang]||value?.name||value?.title?.en||'';return result.replace(/\[([^\]]+)\]\([^)]+\)/g,'$1').replace(/\*\*|\*|`/g,'').replace(/\s+/g,' ').trim();}
export function chartLayout(people){
  const byId=new Map(people.map(p=>[p.id,p])),children=new Map(people.map(p=>[p.id,[]])),roots=[];
  for(const person of people){if(person.reports_to&&byId.has(person.reports_to)&&person.reports_to!==person.id)children.get(person.reports_to).push(person);else roots.push(person);}
  const nodes=[],edges=[],visited=new Set();let nextColumn=0;
  function place(person,depth,stack=new Set()){
    if(visited.has(person.id)||stack.has(person.id))return null;visited.add(person.id);stack.add(person.id);
    const positions=children.get(person.id).map(child=>{const n=place(child,depth+1,new Set(stack));if(n)edges.push({source:person.id,target:child.id});return n;}).filter(Boolean);
    const x=positions.length?positions.reduce((sum,n)=>sum+n.x,0)/positions.length:nextColumn++*350;
    const node={person,x,y:depth*255};nodes.push(node);return node;
  }
  for(const root of roots)place(root,0);
  for(const p of people)if(!visited.has(p.id))place(p,0);
  return {nodes,edges,width:Math.max(350,nextColumn*350),height:Math.max(235,...nodes.map(n=>n.y+235))};
}

export function synchronizePrograms(doc){
 const programs=new Map(collect(doc.payload,'program').map(p=>[p.id,p]));
 for(const assignment of collect(doc.payload,'program_assignment')){
  const program=programs.get(assignment.document_program_id);
  if(program){assignment.program_id=program.program_id||program.id;assignment.program_title=clone(program.title);}
 }
}
