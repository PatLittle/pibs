import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { PAGE, MAX_NODES, indexGraph, search, connections, neighborhood, parseState, stateURL } from '../site/graph-model.mjs';
import { browseRecords, connectedRecords, pageRecords, recordStats } from '../site/graph-records.mjs';

const graph = JSON.parse(readFileSync(new URL('../site/data/graph.json', import.meta.url)));
const index = indexGraph(graph);
const pia = 'pia:ati-schedule-i-administrative-tribunals-support-service-of-canada/pia-95a42118fc3d';
const base = 'https://patlittle.github.io/pibs/graph.html';

test('French aliases, accent folding and institution/type filters search real records', () => {
  assert.ok(search(index, 'POU 905').some(n => n.id === 'pib:standard:PSU 905'));
  const bank = search(index, '', 'pib').find(n => n.label_fr.includes('é'));
  assert.ok(search(index, bank.label_fr.normalize('NFD').replace(/\p{Diacritic}/gu, ''), 'pib', bank.institution_id || '').some(n => n.id === bank.id));
  assert.equal(search(index, 'no-such-identifier-zzzzz').length, 0);
  assert.ok(search(index, '', 'pia').every(n => n.type === 'pia'));
});

test('one hop starts small; expanding a standard bank preserves prior paths', () => {
  const state = parseState(base + '?node=' + encodeURIComponent(pia), index);
  const first = neighborhood(index, state);
  assert.ok(first.nodes.length <= PAGE + 1);
  assert.ok(first.nodes.some(n => n.id === 'pib:standard:PSU 905'));
  state.expanded.set('pib:standard:PSU 905', PAGE);
  const next = neighborhood(index, state);
  assert.ok(next.nodes.length > first.nodes.length);
  assert.ok(first.nodes.every(n => next.nodes.some(m => m.id === n.id)));
  for (const e of next.edges) assert.ok(next.nodes.some(n => n.id === e.source) && next.nodes.some(n => n.id === e.target));
});

test('deep links round-trip selected edge, language, expansions and relation filter', () => {
  const state = parseState(base + '?node=' + encodeURIComponent(pia), index);
  state.lang = 'fr'; state.selected = 'pib:standard:PSU 905'; state.edge = connections(index, pia)[0].id;
  state.expanded.set(state.selected, 50); state.relation = 'references';
  assert.deepEqual(parseState(stateURL(base, state), index), state);
});

test('large neighborhoods and malformed URL expansion counts are bounded', () => {
  const institution = graph.nodes.filter(n => n.type === 'institution').sort((a, b) => connections(index, b.id).length - connections(index, a.id).length)[0];
  const state = parseState(base + '?node=' + encodeURIComponent(institution.id) + '&expand=' + encodeURIComponent('999999:' + institution.id), index);
  assert.equal(state.expanded.get(institution.id), MAX_NODES);
  const view = neighborhood(index, state);
  assert.ok(view.nodes.length <= MAX_NODES);
  assert.equal(view.capped, true);
  assert.equal(neighborhood(index, parseState(base + '?node=absent', index)).nodes.length, 0);
});

test('relation filters retain only requested observed relationships', () => {
  const state = parseState(base + '?node=' + encodeURIComponent(pia) + '&relation=references', index);
  const view = neighborhood(index, state);
  assert.ok(view.edges.length > 0);
  assert.ok(view.edges.every(e => e.type === 'references'));
  assert.ok(view.nodes.every(n => n.type !== 'institution'));
});

test('record pages cover the full connection list without duplicates or graph truncation', () => {
  const anchor = graph.nodes.filter(n => n.type === 'institution').sort((a, b) => connections(index, b.id).length - connections(index, a.id).length)[0];
  const entries = browseRecords(index, { anchor: anchor.id });
  assert.ok(entries.length > MAX_NODES, 'Browsing must include records beyond the drawing limit');
  const ids = [];
  for (let p = 1; p <= Math.ceil(entries.length / 8); p++) ids.push(...pageRecords(entries, p).items.map(r => r.node.id));
  assert.deepEqual(ids, entries.map(r => r.node.id));
  assert.equal(new Set(ids).size, ids.length);
  assert.equal(pageRecords(entries, 99999).page, Math.ceil(entries.length / 8));
  assert.deepEqual(pageRecords([], -1).items, []);
});

test('global record browsing composes French aliases, types and degree sorting', () => {
  const matches = browseRecords(index, { scope: 'all', query: 'POU 905', type: 'pib', lang: 'fr' });
  assert.ok(matches.some(r => r.node.id === 'pib:standard:PSU 905'));
  const ranked = browseRecords(index, { scope: 'all', type: 'pib', sort: 'degree' });
  assert.ok(ranked.every(r => r.node.type === 'pib'));
  assert.ok(ranked.slice(1).every((r, i) => index.adjacency.get(ranked[i].node.id).length >= index.adjacency.get(r.node.id).length));
  assert.equal(browseRecords(index, { scope: 'all', query: 'zz-no-record-here' }).length, 0);
});

test('connection summaries count observed records, edge resolution and reference types', () => {
  const target = graph.edges.find(e => e.resolution === 'ambiguous').source;
  const stats = recordStats(index, target);
  assert.equal(stats.relationships, connections(index, target).length);
  assert.equal(stats.records, connectedRecords(index, target).length);
  assert.equal(Object.values(stats.types).reduce((n, count) => n + count, 0), stats.records);
  assert.ok(stats.unresolved > 0);
  assert.ok(stats.types.reference > 0);
  assert.equal(connectedRecords(index, pia, 'references').every(r => r.edges.every(e => e.type === 'references')), true);
  const filtered = recordStats(index, pia, 'references');
  assert.equal(filtered.relationships, connections(index, pia, 'references').length);
  assert.equal(filtered.types.institution, 0, 'Summary chips must follow the active relationship filter');
});
