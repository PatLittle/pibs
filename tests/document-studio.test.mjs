import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {webcrypto} from 'node:crypto';
import {newDocument,component,validate,validateSchemaDefinition,renewIds,chartLayout,collect,synchronizePrograms} from '../site/document-studio/model.mjs';
import {exportMarkdown,importDocument,renderMarkdown,additionalInformation} from '../site/document-studio/markdown.mjs';
globalThis.crypto ||= webcrypto;
const read=name=>JSON.parse(readFileSync(new URL('../site/document-studio/'+name,import.meta.url),'utf8'));
const schema=read('templates/document.schema.json'),catalogue=read('templates/catalogue.json'),library=read('templates/library.json'),example=read('examples/organization-chart.json');

test('all 110 templates instantiate with schema-constrained structure and unique component IDs',()=>{
 validateSchemaDefinition(schema);assert.equal(catalogue.templates.length,110);
 for(const template of catalogue.templates){const doc=newDocument(schema,template);assert.deepEqual(validate(doc,schema,{complete:false}),[],template.id);const copy=newDocument(schema,template);assert.notEqual(doc.document_id,copy.document_id);assert.notEqual(doc.payload.id,copy.payload.id);}
 const unsafe=structuredClone(schema);unsafe.$defs.person.properties.name.pattern='.*';assert.throws(()=>validateSchemaDefinition(unsafe),/Unsupported schema keyword/);
});
test('the complete Info Source family includes every standard template and official internal-service nesting',()=>{
 assert.equal(Object.keys(library.classes).length,33);assert.equal(Object.keys(library.pibs).length,49);assert.equal(library.internal_groups.length,11);
 const counts=new Map();for(const g of library.internal_groups)for(const c of g.classes){assert.ok(library.classes[c.number]);for(const p of c.pibs)assert.ok(library.pibs[p]);counts.set(c.number,true);}
 assert.equal(counts.size,33);assert.ok(library.introduction.en.includes('Info Source'));assert.ok(library.introduction.fr.includes('Info Source'));
});
test('all five official Word forms, every heading and fixed-question table remain represented',()=>{
 const forms=read('templates/forms.json'),coverage=read('templates/requirements.json');
 assert.ok(catalogue.templates.some(t=>t.id==='pib_submission'));
 for(const kind of Object.keys(forms.forms)){
  const template=catalogue.templates.find(t=>t.id===kind);assert.ok(template);const doc=newDocument(schema,template);
  for(let i=0;i<forms.forms[kind].en.length;i++){const section=doc.payload['section_'+String(i+1).padStart(2,'0')];assert.ok(section);assert.ok('guidance' in section);const rule=schema.$defs[section.kind];assert.equal(rule['x-label'].en,forms.forms[kind].en[i].title||'Instructions');}
 }
 assert.equal(coverage.form_fields.filter(f=>f.document_type==='pia_web_summary').length,6);
 assert.ok(coverage.form_fields.some(f=>f.columns===13));
});
test('review-ready enforces bilingual content, one program per position and both classification fields',()=>{
 assert.deepEqual(validate(example,schema),[]);
 let doc=structuredClone(example);doc.payload.people[0].position_title.fr='';assert.ok(validate(doc,schema).some(i=>i.path.endsWith('/position_title/fr')));
 doc=structuredClone(example);doc.payload.people[1].programs=[];assert.ok(validate(doc,schema).some(i=>i.keyword==='minItems'));
 assert.doesNotThrow(()=>exportMarkdown(doc,schema));assert.throws(()=>exportMarkdown(doc,schema,{ready:true}),/validation/);
 doc=structuredClone(example);doc.payload.people[1].classification_level='';assert.ok(validate(doc,schema).some(i=>i.keyword==='classification'));
});
test('reporting links reject cycles, unknown parents and date inversions without losing repairable drafts',()=>{
 let doc=structuredClone(example);doc.payload.people[0].reports_to=doc.payload.people[2].id;assert.ok(validate(doc,schema).some(i=>i.keyword==='cycle'));
 assert.doesNotThrow(()=>importDocument(exportMarkdown(doc,schema),schema));
 doc.payload.people[0].reports_to='missing';assert.ok(validate(doc,schema).some(i=>i.keyword==='foreignKey'));
 doc=structuredClone(example);doc.payload.people[0].effective_from='2026-11-10';doc.payload.people[0].effective_to='2026-11-01';assert.ok(validate(doc,schema).some(i=>i.keyword==='dateOrder'));
 const layout=chartLayout(example.payload.people);assert.equal(layout.nodes.length,3);assert.equal(layout.edges.length,2);assert.ok(layout.nodes.find(n=>n.person.role_level==='deputy_head').y<layout.nodes.find(n=>n.person.role_level==='director_general').y);
});
test('position-program assignments follow explicit document IDs and preserve external organization scope',()=>{
 const doc=newDocument(schema,catalogue.templates.find(t=>t.id==='infosource'));const program=component(schema,'program');program.title={en:'One',fr:'Un'};doc.payload.institution_specific.push(program);
 const person=structuredClone(example.payload.people[0]);person.programs[0].document_program_id=program.id;doc.payload.people.push(person);synchronizePrograms(doc);
 assert.equal(person.programs[0].program_id,program.id);assert.equal(person.programs[0].program_title.en,'One');program.program_id='001';program.title.fr='Modifié';synchronizePrograms(doc);assert.equal(person.programs[0].program_id,'001');assert.equal(person.programs[0].program_title.fr,'Modifié');
 doc.payload.institution_specific=[];assert.ok(validate(doc,schema).some(i=>i.keyword==='foreignKey'));
 const external=structuredClone(example);external.payload.people[0].programs[0].owner_org='';assert.ok(validate(external,schema).some(i=>i.path.endsWith('/owner_org')));
});
test('one bilingual Markdown file round-trips exactly and retains the chain of command and program codes',()=>{
 const markdown=exportMarkdown(example,schema,{ready:true});assert.deepEqual(importDocument(markdown,schema),example);assert.ok(markdown.includes('```mermaid'));assert.ok(markdown.includes('position_0 --> position_1'));assert.ok(markdown.includes('EXAMPLE-01'));assert.ok(markdown.includes('Programme exemple'));
 assert.throws(()=>importDocument(markdown.replace(/# Fictional organization · example/, '# Silent external edit'),schema),/visible Markdown differs/);
 const bad=structuredClone(example);bad.payload.arbitrary_field='wrong';assert.throws(()=>importDocument(JSON.stringify(bad),schema),/outside this document schema/);
 const version=structuredClone(example);version.schema_version='2.0.0';assert.throws(()=>importDocument(JSON.stringify(version),schema),/another schema/);
});
test('duplicate components receive fresh IDs and internal reporting links are rewired',()=>{
 const copy=renewIds(structuredClone(example.payload));assert.notEqual(copy.id,example.payload.id);assert.equal(copy.people[1].reports_to,copy.people[0].id);assert.equal(new Set(collect(copy,'person').map(p=>p.id)).size,3);
});
test('fixed official wording cannot change, and object key order does not invalidate a constant',()=>{
 const doc=newDocument(schema,catalogue.templates.find(t=>t.id==='infosource'));doc.payload.introduction={fr:library.introduction.fr,en:library.introduction.en};assert.deepEqual(validate(doc,schema,{complete:false}),[]);doc.payload.introduction.fr='Changed';assert.ok(validate(doc,schema,{complete:false}).some(i=>i.keyword==='const'));
});
test('additional information fills the official wording and optional bilingual open-data sentence',()=>{
 const doc=newDocument(schema,catalogue.templates.find(t=>t.id==='infosource'));doc.payload.institution_name={en:'Example Department',fr:'Ministère exemple'};const info=doc.payload.additional_information;
 for(const f of ['official_title','mailing_address','informal_contact','fee_payee'])info[f]={en:'Example EN',fr:'Exemple FR'};
 for(const l of ['en','fr']){info['completed_requests_url_'+l]='https://example.invalid/'+l+'/requests';info['pia_summaries_url_'+l]='https://example.invalid/'+l+'/pias';}
 const en=additionalInformation(doc,info.standard_text,'en'),fr=additionalInformation(doc,info.standard_text,'fr');assert.ok(en.includes('Example Department'));assert.ok(fr.includes('Ministère exemple'));assert.ok(en.includes('/en/pias'));assert.ok(fr.includes('/fr/pias'));assert.ok(!/\[(?:link|lien|name of institution|nom de l’institution)\]/i.test(en+fr));assert.ok(!en.includes('review available open data'));
});
test('conditional disclosure, SIN, submission and repeating-table requirements are enforced',()=>{
 const cor=newDocument(schema,catalogue.templates.find(t=>t.id==='cor'));cor.payload.disclosure_status='disclosed';assert.ok(validate(cor,schema).some(i=>i.path.endsWith('/disclosures')));cor.payload.disclosure_status='none';assert.ok(validate(cor,schema).some(i=>i.path.endsWith('/no_disclosure_statement')));
 const bank=newDocument(schema,catalogue.templates.find(t=>t.id==='pib'));bank.payload.sin_collection='yes';assert.ok(validate(bank,schema).some(i=>i.path.endsWith('/sin_authority')));
 const submission=newDocument(schema,catalogue.templates.find(t=>t.id==='pib_submission'));submission.payload.request_type='transfer';assert.ok(validate(submission,schema).some(i=>i.path.endsWith('/transfer_confirmations')));
 const pia=newDocument(schema,catalogue.templates.find(t=>t.id==='privacy_impact_assessment'));const table=Object.values(pia.payload).flatMap(s=>Object.values(s||{})).find(t=>t?.kind&&schema.$defs[t.kind]?.['x-repeating-table']);assert.ok(table);table.applicability='applicable';assert.ok(validate(pia,schema).some(i=>i.path.endsWith('/rows')));
});
test('source content and unsafe URL text are never executed or emitted as active HTML',()=>{
 const doc=structuredClone(example);doc.payload.people[0].name='<script>window.bad=true</script>';doc.payload.people[0].position_title.en='[click](javascript:alert)';const body=renderMarkdown(doc,schema);assert.ok(!body.includes('<script>'));assert.ok(!body.includes('](javascript:'));
});


test('conditionally not-applicable answers require bilingual reasons and action-plan rows retain leads and dates',()=>{
 const checklist=newDocument(schema,catalogue.templates.find(t=>t.id==='privacy_checklist'));
 const section=Object.values(checklist.payload).find(value=>value&&typeof value==='object'&&Object.keys(value).some(k=>k.startsWith('response_')&&schema.$defs[value.kind]?.properties[k]?.enum));
 const rule=schema.$defs[section.kind],key=Object.keys(rule.properties).find(k=>k.startsWith('response_')&&rule.properties[k].enum);
 section[key]='not_applicable';assert.ok(validate(checklist,schema).some(i=>i.keyword==='conditionalReason'));
 section.not_applicable_explanation={en:'The prerequisite condition does not apply.',fr:'La condition préalable ne s’applique pas.'};assert.ok(!validate(checklist,schema).some(i=>i.keyword==='conditionalReason'));
 const rows=Object.values(schema.$defs).filter(d=>d.properties?.lead&&d.properties?.target_completion_date);assert.equal(rows.length,2);
});
