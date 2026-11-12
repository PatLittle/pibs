import { connections, fold, label, search } from './graph-model.mjs';

// The same palette drives the diagram, record cards, chips and legend.
export const NODE_COLORS = { pib: '#1f5a94', pia: '#087a82', institution: '#754b94', class: '#b47700', reference: '#d7dee5' };

export function connectedRecords(index, id, relation = '') {
  const records = new Map();
  for (const edge of connections(index, id, relation)) {
    const other = edge.source === id ? edge.target : edge.source;
    if (!records.has(other)) records.set(other, { node: index.nodes.get(other), edges: [] });
    records.get(other).edges.push(edge);
  }
  return [...records.values()];
}

export function browseRecords(index, { anchor, scope = 'connected', relation = '', query = '', type = '', sort = 'name', lang = 'en' }) {
  const terms = fold(query).split(/\s+/).filter(Boolean);
  const entries = scope === 'all' ? search(index, query, type, '', lang).map(node => ({ node, edges: [] })) :
    connectedRecords(index, anchor, relation).filter(({ node }) => (!type || node.type === type) &&
      terms.every(term => fold([node.identifier, node.label_en, node.label_fr, ...(node.aliases || [])].join(' ')).includes(term)));
  return entries.sort((a, b) => (sort === 'degree' ? index.adjacency.get(b.node.id).length - index.adjacency.get(a.node.id).length : 0) ||
    label(a.node, lang).localeCompare(label(b.node, lang), lang) || a.node.id.localeCompare(b.node.id));
}

export function pageRecords(entries, requested = 1, size = 8) {
  const pageSize = [8, 16, 24].includes(Number(size)) ? Number(size) : 8;
  const pages = Math.max(1, Math.ceil(entries.length / pageSize));
  const page = Math.min(pages, Math.max(1, Math.floor(Number(requested) || 1)));
  const start = (page - 1) * pageSize;
  return { page, pages, pageSize, total: entries.length, start: entries.length ? start + 1 : 0,
    end: Math.min(start + pageSize, entries.length), items: entries.slice(start, start + pageSize) };
}

export function recordStats(index, id) {
  const edges = connections(index, id);
  const records = connectedRecords(index, id);
  const types = Object.fromEntries(Object.keys(NODE_COLORS).map(type => [type, records.filter(r => r.node.type === type).length]));
  return { records: records.length, relationships: edges.length, types,
    unresolved: edges.filter(e => e.resolution !== 'resolved').length };
}
