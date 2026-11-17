import { test } from 'node:test';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { parseJSONL, organizationMatch, officialIdentity, explicitReferences, integrateAIA, loadAIA } from '../site/aia-data.mjs';
import { indexGraph, connections, parseState, stateURL, search } from '../site/graph-model.mjs';
import { recordStats } from '../site/graph-records.mjs';
globalThis.crypto ||= webcrypto;
const uuid='11111111-1111-4111-8111-111111111111';
const row = () => ({ package_id:uuid,title_en:'A sample project',title_fr:'Un projet',organization_en:'Example Department | Ministère exemple',organization_fr:'Example Department | Ministère exemple',dataset_url:'https://example.gc.ca/dataset/'+uuid,version:'v1.0.1',source:'published',data:{projectDetailsTitle:'A sample project',projectDetailsRespondent:'A Respondent'},translationsOnResult:{},derived:{impact_level:2} });
const graph = () => ({nodes:[
  {id:'institution:one',type:'institution',institution_id:'one',label_en:'Department of Examples',aliases:['Example Department','Ministère exemple']},
  {id:'institution:two',type:'institution',institution_id:'two',label_en:'Other Department'},
  {id:'pib:one:EX PPU 123',type:'pib',institution_id:'one',scope:'institution',identifier:'EX PPU 123',aliases:['EX PPU 123','EE PPU 123']},
  {id:'pib:two:OT PPU 123',type:'pib',institution_id:'two',scope:'institution',identifier:'OT PPU 123',aliases:[]},
  {id:'pib:standard:PSU 905',type:'pib',scope:'standard',identifier:'PSU 905',aliases:['POU 905']},
  {id:'class:standard:930',type:'class',scope:'standard',identifier:'930',aliases:['PRN 930','NDP 930']},
  {id:'pia:one/sample',type:'pia',institution_id:'one',label_en:'A sample project',sources:{en:'https://example.gc.ca/pia/sample'},aliases:[]}
],edges:[],summary:{}});

test('JSONL validates records and UUID keys; rejects duplicates, bad JSON and missing identities',()=>{
  assert.equal(parseJSONL('\n'+JSON.stringify(row())+'\n').length,1);
  assert.throws(()=>parseJSONL('{broken}'));
  assert.throws(()=>parseJSONL(JSON.stringify({...row(),package_id:''})),/UUID/);
  assert.throws(()=>parseJSONL(JSON.stringify({...row(),data:null})),/Invalid/);
  assert.throws(()=>parseJSONL([row(),row()].map(JSON.stringify).join('\n')),/Duplicate/);
});
test('organization joins require unique exact bilingual names or registry aliases',()=>{
  assert.equal(organizationMatch(row(),graph().nodes).institution_id,'one');
  assert.equal(organizationMatch({...row(),organization_en:'Example',organization_fr:''},graph().nodes).resolution,'unresolved');
  const nodes=graph().nodes;nodes.push({id:'institution:three',type:'institution',institution_id:'three',aliases:['Example Department']});
  assert.equal(organizationMatch(row(),nodes).resolution,'ambiguous');
});
test('official names retain source forms and stable organization-scoped IDs; respondents are excluded',async()=>{
  const a=await officialIdentity('Émilie Example','Émilie Example','one');
  assert.equal(a.name_en,'Émilie Example');
  assert.equal(a.u_id,(await officialIdentity(' Emilie  Example ','Emilie Example','one')).u_id);
  assert.notEqual(a.u_id,(await officialIdentity('Émilie Example','','two')).u_id);
  assert.equal(await officialIdentity('N/A','','one'),null);
  assert.equal((await integrateAIA(graph(),[row()])).records[0].official,null);
});
test('explicit PIBs resolve with institutional scope; full prefixes support cross-institution references',()=>{
  const r=row();r.data.aboutDataSource12='PPU123, OT PPU 123, PSU905, PPU999';
  const refs=explicitReferences(r,'one',graph().nodes);
  assert.equal(refs.find(x=>x.mention==='PPU123').candidates[0],'pib:one:EX PPU 123');
  assert.equal(refs.find(x=>x.mention==='OT PPU 123').candidates[0],'pib:two:OT PPU 123');
  assert.equal(refs.find(x=>x.mention==='PSU905').candidates[0],'pib:standard:PSU 905');
  assert.equal(refs.find(x=>x.mention==='PPU999').resolution,'unresolved');
  assert.equal(explicitReferences(r,null,graph().nodes).find(x=>x.mention==='PPU123').resolution,'unresolved');
});
test('bilingual references consolidate evidence; duplicate source-scoped holdings stay ambiguous',()=>{
  const r=row();r.data.aboutDataSource12='EX PPU 123';r.translationsOnResult.aboutDataSource12='EE PPU 123';
  let refs=explicitReferences(r,'one',graph().nodes);assert.equal(refs.length,1);assert.equal(refs[0].evidence.length,2);
  const g=graph();g.nodes.push({...g.nodes[2],id:'pib:two:EX PPU 123',institution_id:'two'});
  refs=explicitReferences(r,'one',g.nodes);assert.equal(refs[0].resolution,'ambiguous');assert.equal(refs[0].candidates.length,2);
});
test('PIA links require literal source URLs, standard class citations resolve, and titles alone create no edge',()=>{
  const r=row();assert.equal(explicitReferences(r,'one',graph().nodes).length,0);
  r.data.privacyImplementation5='See https://example.gc.ca/pia/sample and NDP 930.';
  const refs=explicitReferences(r,'one',graph().nodes);assert.equal(refs.length,2);assert.ok(refs.every(r=>r.resolution==='resolved'));
});
test('runtime graph supports reverse traversal, official filtering, relation URLs and inline provenance',async()=>{
  const r=row();r.data.ADMresponsible='A Senior Official';r.data.aboutDataSource12='PPU 123, PPU 999';
  const result=await integrateAIA(graph(),[r]);const index=indexGraph(result.graph);
  assert.ok(connections(index,'institution:one').some(e=>e.source==='aia:'+uuid));
  assert.ok(connections(index,'pib:one:EX PPU 123').some(e=>e.source==='aia:'+uuid));
  assert.equal(search(index,'A Senior','official').length,1);
  const state=parseState('https://example.com/graph.html?node=aia:'+uuid+'&relation=responsible_official',index);
  assert.deepEqual(parseState(stateURL('https://example.com/graph.html',state),index),state);
  assert.equal(recordStats(index,'aia:'+uuid).types.official,1);
  assert.ok(result.graph.edges.every(e=>e.evidence.length));
  assert.equal(result.graph.summary.resolutions.unresolved,1);
  const unresolved=result.graph.edges.find(e=>e.resolution==='unresolved');assert.equal(index.nodes.get(unresolved.target).type,'reference');
});
test('loader uses configurable external URL and reports outages or empty feeds',async()=>{
  const config={url:'https://external.example/next.jsonl'},calls=[];
  const fetcher=async url=>{calls.push(url);return url==='aia-source.json'?{ok:true,json:async()=>config}:{ok:true,text:async()=>JSON.stringify(row()),headers:new Headers()};};
  assert.equal((await loadAIA(graph(),fetcher)).records.length,1);assert.deepEqual(calls,['aia-source.json',config.url]);
  await assert.rejects(loadAIA(graph(),async()=>({ok:false,status:503})),/503/);
  await assert.rejects(loadAIA(graph(),async url=>url==='aia-source.json'?{ok:true,json:async()=>config}:{ok:true,text:async()=>'',headers:new Headers()}),/empty/);
});

test('AIA service IDs resolve literally within the matched institution, with no year or risk propagation', async()=>{
  const g=graph();g.nodes.push({id:'service:one:001',type:'service',identifier:'001',institution_id:'one'}, {id:'service:two:001',type:'service',identifier:'001',institution_id:'two'});
  const r=row();r.data.ServiceID='001';
  const result=await integrateAIA(g,[r]),match=result.records[0].service_match;
  assert.deepEqual(match.candidates,['service:one:001']);assert.equal(match.resolution,'resolved');
  const edge=result.graph.edges.find(e=>e.type==='references_service');assert.equal(edge.target,'service:one:001');
  assert.equal(edge.evidence[0].field,'data.ServiceID');assert.equal(result.graph.nodes.find(n=>n.id===edge.target).attributes,undefined);
  assert.equal(recordStats(indexGraph(result.graph),'aia:'+uuid).types.service,1);
  const other=graph();other.nodes.push({id:'service:two:001',type:'service',identifier:'001',institution_id:'two'});
  const unresolved=await integrateAIA(other,[r]);assert.equal(unresolved.records[0].service_match.resolution,'unresolved');
  assert.equal(unresolved.graph.nodes.find(n=>n.id===unresolved.graph.edges.find(e=>e.type==='references_service').target).type,'reference');
  r.data.ServiceID='1';assert.equal((await integrateAIA(g,[r])).records[0].service_match.resolution,'unresolved');
  r.data.ServiceID='N/A';assert.ok(!(await integrateAIA(graph(),[r])).graph.edges.some(e=>e.type==='references_service'));
  const ambiguous=graph();ambiguous.nodes.push(...[1,2].map(i=>({id:'service:duplicate:'+i,type:'service',identifier:'001',institution_id:'one'})));
  r.data.ServiceID='001';assert.equal((await integrateAIA(ambiguous,[r])).records[0].service_match.resolution,'ambiguous');
});
