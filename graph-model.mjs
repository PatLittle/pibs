// UI-independent traversal and URL state. IDs are opaque, source-scoped strings.
export const PAGE = 25;
export const MAX_NODES = 250;
export const fold = value => String(value || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
export const label = (node, lang) => node['label_' + lang] || node.label_en || node.label_fr || node.identifier;
export const matchesType = (node, type) => !type || node.type === type ||
  (type === 'standard-pib' && node.type === 'pib' && node.scope === 'standard') ||
  (type === 'standard-class' && node.type === 'class' && node.scope === 'standard');

export function indexGraph(graph) {
  const nodes = new Map(graph.nodes.map(n => [n.id, n]));
  const edges = new Map(graph.edges.map(e => [e.id, e]));
  const adjacency = new Map(graph.nodes.map(n => [n.id, []]));
  for (const e of graph.edges) {
    if (!nodes.has(e.source) || !nodes.has(e.target)) throw new Error('Dangling graph edge');
    adjacency.get(e.source).push(e);
    adjacency.get(e.target).push(e);
  }
  return { nodes, edges, adjacency };
}

export function search(index, query, type = '', institution = '', lang = 'en') {
  const terms = fold(query).split(/\s+/).filter(Boolean);
  return [...index.nodes.values()].filter(n => matchesType(n, type) &&
    (!institution || n.institution_id === institution) &&
    terms.every(t => fold([n.identifier, n.label_en, n.label_fr, ...(n.aliases || [])].join(' ')).includes(t)))
    .sort((a, b) => {
      const rank = { pia: 0, pib: 1, institution: 2, class: 3, category: 4, pib_type: 5, reference: 6 };
      const priority = !terms.length && !type ? rank[a.type] - rank[b.type] : 0;
      return priority || label(a, lang).localeCompare(label(b, lang), lang) || a.id.localeCompare(b.id);
    });
}

export function connections(index, id, relation = '') {
  return (index.adjacency.get(id) || []).filter(e => !relation || e.type === relation)
    .sort((a, b) => (a.type === 'listed_by') - (b.type === 'listed_by') || a.id.localeCompare(b.id));
}

export function neighborhood(index, state) {
  const ids = new Set(index.nodes.has(state.root) ? [state.root] : []);
  let capped = false;
  // Expansion order preserves the path from the root to each new seed.
  for (const [id, limit] of state.expanded) {
    if (!ids.has(id)) continue;
    for (const e of connections(index, id, state.relation).slice(0, limit)) {
      const other = e.source === id ? e.target : e.source;
      if (ids.size >= MAX_NODES && !ids.has(other)) { capped = true; continue; }
      ids.add(other);
    }
  }
  // Include all observed edges between visible endpoints, including cross-links.
  const edges = [...index.edges.values()].filter(e => ids.has(e.source) && ids.has(e.target) && (!state.relation || e.type === state.relation));
  return { nodes: [...ids].map(id => index.nodes.get(id)), edges, capped };
}

export function parseState(url, index) {
  const p = new URL(url).searchParams;
  const root = p.get('root') || p.get('node') || '';
  const expanded = new Map();
  if (index.nodes.has(root)) expanded.set(root, PAGE);
  for (const value of p.getAll('expand').slice(0, 100)) {
    const match = /^(\d+):(.+)$/.exec(value);
    if (match && index.nodes.has(match[2])) expanded.set(match[2], Math.min(MAX_NODES, Math.max(PAGE, Number(match[1]))));
  }
  return { root, selected: p.get('node') || root, edge: p.get('edge') || '', expanded,
    lang: p.get('lang') === 'fr' ? 'fr' : 'en',
    relation: ['listed_by', 'references', 'related_class', 'has_type', 'category_match'].includes(p.get('relation')) ? p.get('relation') : '' };
}

export function stateURL(base, state) {
  const url = new URL(base);
  url.search = '';
  url.searchParams.set('lang', state.lang);
  if (state.root) url.searchParams.set('root', state.root);
  if (state.selected) url.searchParams.set('node', state.selected);
  if (state.edge) url.searchParams.set('edge', state.edge);
  if (state.relation) url.searchParams.set('relation', state.relation);
  for (const [id, count] of state.expanded) url.searchParams.append('expand', count + ':' + id);
  return url;
}
