import test from 'node:test';
import assert from 'node:assert/strict';
import {filterRecords, sortRecords, readableLabel} from '../site/privacy-assessment-utils.js';
const records = [
 {id:'a', institution_id:'alpha', name_en:'Alpha', name_fr:'Énergie', gc_orgID:'2', title_en:'Payroll', title_fr:'Rémunération', available_languages:['en','fr']},
 {id:'b', institution_id:'beta', name_en:'Beta', name_fr:'Bêta', gc_orgID:'10', title_en:'Security', title_fr:null, available_languages:[]},
 {id:'c', institution_id:'alpha', name_en:'Alpha', name_fr:'Énergie', gc_orgID:'2', title_en:'Workplace', title_fr:'Milieu de travail', available_languages:['fr']},
];
test('department, bilingual text and availability filters compose',()=>{
 assert.deepEqual(filterRecords(records,{department:'alpha',q:'remuneration',availability:'both'}).map(r=>r.id),['a']);
 assert.deepEqual(filterRecords(records,{q:'10',availability:'none'}).map(r=>r.id),['b']);
 assert.equal(filterRecords(records,{department:'unknown'}).length,0);
 assert.equal(filterRecords(records,{availability:'readable'}).length,2);
});
test('sorting is numeric where appropriate and does not mutate the catalogue',()=>{
 assert.deepEqual(sortRecords(records,'gc_orgID',true).map(r=>r.id),['b','c','a']);
 assert.deepEqual(records.map(r=>r.id),['a','b','c']);
});
test('availability labels reflect actual exports',()=>{
 assert.equal(readableLabel(records[0]),'EN + FR');
 assert.equal(readableLabel(records[1]),'No readable copy');
 assert.equal(readableLabel(records[2]),'Français only');
});
test('PIB and CoR IDs are searchable and reference filters compose',()=>{
 const referenced=[{...records[0],pib_ids:['ABC PPU 001'],pib_count:1,cor_ids:['ABC DOC 100'],cor_count:1}, {...records[1],pib_ids:[],pib_count:0,cor_ids:[],cor_count:0}];
 assert.equal(filterRecords(referenced,{q:'abc ppu 001'}).length,1);
 assert.equal(filterRecords(referenced,{q:'ABC DOC 100',references:'cors'}).length,1);
 assert.equal(filterRecords(referenced,{references:'pibs',availability:'none'}).length,0);
 assert.deepEqual(sortRecords([{id:'a',pib_count:2},{id:'b',pib_count:10}], 'pib_count').map(r=>r.id),['a','b']);
});
