import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {webcrypto} from 'node:crypto';
import {createPDF,pdfBlocks} from '../site/document-studio/pdf.mjs';
import {buildXMP,validateMetadata} from '../site/document-studio/metadata.mjs';
import {newDocument,validate} from '../site/document-studio/model.mjs';
import {exportMarkdown,importDocument} from '../site/document-studio/markdown.mjs';
globalThis.crypto ||= webcrypto;
const require=createRequire(import.meta.url),base=new URL('../site/document-studio/',import.meta.url);
const read=path=>JSON.parse(readFileSync(new URL(path,base),'utf8'));
const schema=read('templates/document.schema.json'),catalogue=read('templates/catalogue.json');
const doc=read('examples/organization-chart.json');
doc.metadata={title:{en:'English-only title',fr:'Titre exclusivement français'},description:{en:'English description',fr:'Description française'},creators:['Fictional Author'],keywords:['Privacy','Vie privée'],copyright_notice:{en:'Example rights',fr:'Droits fictifs'},rights_usage_terms:{en:'Example terms',fr:'Conditions fictives'},rights_url:'https://example.invalid/rights',credit:'Fictional institution',source:'Fictional source',headline:'Example headline',creator_job_title:'Example title',caption_writer:'Example writer',instructions:'Example instructions',creation_date:'2026-11-17',intellectual_genre:'Document',country_code:'CAN',subject_codes:['01000000'],scene_codes:['010100'],contact_email:'author@example.invalid',contact_phone:'+1 000 000 0000',contact_url:'https://example.invalid/',contact_address:'Example address',contact_city:'Ottawa',contact_region:'ON',contact_postal_code:'A0A 0A0',contact_country:'Canada',digital_source_type:'http://cv.iptc.org/newscodes/digitalsourcetype/digitalCreation',additional_properties:[{namespace:'http://iptc.org/std/Iptc4xmpExt/2008-02-29/',prefix:'Iptc4xmpExt',property:'OrganisationInImageName',type:'bag',value:'["Fictional institution"]'},{namespace:'https://example.invalid/ns/',prefix:'example',property:'Sequence',type:'seq',value:'["one","two"]'},{namespace:'https://example.invalid/ns/',prefix:'example',property:'Label',type:'lang_alt',value:'{"en":"Example","fr":"Exemple"}'},{namespace:'https://example.invalid/ns/',prefix:'example',property:'Provenance',type:'structure',value:'{"source":"Example & <source>","nested":{"value":"test","contributors":[{"name":"Fictional"}]}}'}]};

test('all 13 ATIP families are selectable with official bilingual provenance',()=>{
 assert.equal(catalogue.atip_forms.length,13);assert.equal(catalogue.atip_forms.filter(f=>f.group==='privacy').length,6);
 for(const form of catalogue.atip_forms){const t=catalogue.templates.find(t=>t.id===form.kind);assert.ok(t,form.kind);assert.equal(t.form.number,form.number);for(const language of ['en','fr'])assert.ok(form.official_sources[language].startsWith('https://www.canada.ca/'));}
 assert.equal(catalogue.atip_forms.find(f=>f.kind==='privacy_protocol').completion_mode,'adaptable_word_template');
 const requirements=read('templates/requirements.json'),capture=read('templates/atip.json');
 const breach=requirements.atip_fields.filter(f=>f.document_type==='material_privacy_breach').flatMap(f=>f.source_ids);
 assert.equal(new Set(breach).size,175);assert.deepEqual(new Set(breach),new Set(capture.breach.fields.map(f=>f.id)));
 for(const kind of ['access_statistics','privacy_statistics']){
  const source=capture.html[kind].metrics,coverage=requirements.atip_fields.filter(f=>f.document_type===kind);
  for(const language of ['en','fr'])assert.equal(coverage.filter(f=>f.source_ids[language]!==null).length,source.source_counts[language]);
  const d=newDocument(schema,catalogue.templates.find(t=>t.id===kind));d.payload.reporting_information.cell_0002='2026-04-01';d.payload.reporting_information.cell_0003='2027-03-31';assert.ok(!validate(d,schema).some(i=>i.path.match(/reporting_information\/cell_000[23]/)));
  const field=coverage.find(f=>f.field.startsWith('table_'));const[group,key]=field.field.split('/');d.payload[group][key]='-5';assert.ok(validate(d,schema).some(i=>i.keyword==='pattern'));d.payload[group][key]='0';assert.ok(!validate(d,schema).some(i=>i.keyword==='pattern'&&i.path==='/payload/'+group+'/'+key));
 }
});
test('material breach original and amended reports enforce different completion conditions',()=>{
 const d=newDocument(schema,catalogue.templates.find(t=>t.id==='material_privacy_breach'));d.payload.report.ReportState='ReportState-1';assert.ok(validate(d,schema).some(i=>i.path.endsWith('/InstitutionRefNumber')));
 d.payload.report.ReportState='ReportState-2';assert.ok(validate(d,schema).some(i=>i.path.endsWith('/OPCFileNumber')));d.payload.report.OPCFileNumber='EXAMPLE-1';d.payload.amendment_summary={en:'Fictional update',fr:'Mise à jour fictive'};assert.deepEqual(validate(d,schema),[]);
 d.payload.amendment_summary.fr='';assert.ok(validate(d,schema).some(i=>i.keyword==='breachRequired'));
});
test('metadata survives bilingual Markdown and rejects malformed namespace or duplicate fields',()=>{
 assert.deepEqual(validate(doc,schema),[]);assert.deepEqual(importDocument(exportMarkdown(doc,schema,{ready:true}),schema),doc);
 assert.match(buildXMP(doc),/Iptc4xmpCore:CreatorContactInfo/);assert.match(buildXMP(doc),/Example &amp; &lt;source&gt;/);
 assert.throws(()=>validateMetadata({additional_properties:[{namespace:'https://example.invalid/',prefix:'xml',property:'x',type:'text',value:'x'}]}),/non-reserved/);
 assert.throws(()=>buildXMP({...doc,metadata:{...doc.metadata,additional_properties:[{namespace:'http://purl.org/dc/elements/1.1/',prefix:'dc',property:'title',type:'text',value:'duplicate'}]}}),/duplicates/);
 assert.throws(()=>buildXMP({...doc,metadata:{creators:['invalid\u0001']}}),/control character/);
});
test('EN, FR and BIL PDF bodies and embedded XMP/IPTC are independently readable',async()=>{
 const output=process.env.STUDIO_PDF_OUTPUT||mkdtempSync(join(tmpdir(),'pibs-studio-pdf-'));
 const options={PDFLib:require('../site/document-studio/vendor/pdf-lib.min.js'),fontkit:require('../site/document-studio/vendor/fontkit.umd.min.js'),regularBytes:readFileSync(new URL('fonts/NotoSans-Regular.ttf',base)),boldBytes:readFileSync(new URL('fonts/NotoSans-Bold.ttf',base))};
 for(const mode of ['en','fr','bil']){
  const blocks=pdfBlocks(doc,schema,{mode});assert.equal(blocks.find(b=>b.labels?.includes(mode==='fr'?'Titre de l’organigramme':'Chart title')).values.length,mode==='bil'?2:1);
  const bytes=await createPDF(doc,schema,{...options,mode,now:'2026-11-17T12:00:00Z'});writeFileSync(join(output,mode+'.pdf'),bytes);
 }
 const python=process.env.PYTHON||(existsSync('.venv/bin/python')?'.venv/bin/python':'python3');
 const result=spawnSync(python,['tests/inspect_document_studio_pdf.py',output],{encoding:'utf8'});assert.equal(result.status,0,result.stdout+result.stderr);
});

test('every ATIP template can export a draft PDF with form provenance',async()=>{
 const options={PDFLib:require('../site/document-studio/vendor/pdf-lib.min.js'),fontkit:require('../site/document-studio/vendor/fontkit.umd.min.js'),regularBytes:readFileSync(new URL('fonts/NotoSans-Regular.ttf',base)),boldBytes:readFileSync(new URL('fonts/NotoSans-Bold.ttf',base))};
 for(const form of catalogue.atip_forms){
  const draft=newDocument(schema,catalogue.templates.find(t=>t.id===form.kind));
  assert.deepEqual(importDocument(exportMarkdown(draft,schema),schema),draft);
  const bytes=Buffer.from(await createPDF(draft,schema,{...options,form}));
  assert.ok(bytes.length>10000,form.kind);assert.ok(bytes.includes(Buffer.from('<ds:GovernmentFormNumber>'+form.number)),form.kind);assert.ok(bytes.includes(Buffer.from('<ds:DocumentStatus>draft')),form.kind);
 }
});
