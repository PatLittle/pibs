import { PAGE, MAX_NODES, label, indexGraph, search, connections, neighborhood, parseState, stateURL } from './graph-model.mjs';

const $ = id => document.getElementById(id);
const words = {
  en: {
    skip: 'Skip to main content', eyebrow: 'Follow the evidence', title: 'PIB / PIA network explorer',
    intro: 'Start with a bank or an assessment. Select a node to reveal its connections; select a line to inspect the source evidence.',
    notice: 'A reference is a citation, not proof that an assessment covers the entire bank. Missing links reflect collected evidence, not the absence of an assessment. Dashed lines lead to unresolved references.',
    find: 'Find a starting point', search: 'Name or identifier (English or French)', recordType: 'Record type', allTypes: 'All types',
    pib: 'PIB', pia: 'Privacy assessment', institution: 'Institution', class: 'Class of Records', reference: 'Unresolved reference',
    allInstitutions: 'All institutions', moreResults: 'More results', network: 'Explore connections', relationship: 'Relationship',
    allRelations: 'All relationships', references: 'References', related_class: 'Related class', listed_by: 'Listed under institution',
    fit: 'Fit graph', reset: 'Reset to selected node', share: 'Copy view link', loading: 'Loading graph data…',
    empty: 'Choose a search result to start exploring.', details: 'Record and evidence', connections: 'Connections of the selected node',
    expand: 'Show more connections', overview: 'Overview', navPia: 'Privacy Assessments', navGraph: 'Network explorer',
    download: 'Download graph JSON', methodology: 'Graph methodology', open: 'Open full record', source: 'Original source',
    artifact: 'Repository evidence', inspect: 'Inspect evidence', focus: 'Start here', resolved: 'Matched record',
    unresolved: 'No unique matching record', ambiguous: 'Ambiguous reference', standard: 'Government-wide standard',
    noMatch: 'No matching records. Try another identifier or clear the filters.', unavailable: 'No readable assessment copy was collected.',
    copied: 'View link copied.', copyFallback: 'Copy the view link below.', noConnections: 'No connections in this relationship filter.',
    cap: `The view is limited to ${MAX_NODES} nodes. Start here on a selected node to explore further.`,
    loadError: 'The graph could not be loaded. Reload to try again, or use the PIB tables and Privacy Assessments pages.',
    unknown: 'This record is not in the current graph. Search for another starting point.',
    noCanvas: 'The diagram could not be loaded. Search, record details and the connection list remain available.',
    canvasLabel: 'Record network; use the connection list for keyboard navigation.', line: 'Line', method: 'Method',
    observed: 'Observed', candidates: 'Candidate identifiers (no match asserted)', legend: 'Legend',
    evidenceError: 'Evidence could not be loaded. Select this relationship again to retry.',
    copyLabel: 'View link', exported: 'Readable copy collected', http_error: 'Source retrieval failed',
    insufficient_content: 'Insufficient collected text', soft_error_page: 'Source returned an error page',
    not_pia_content: 'Source content requires review', language_mismatch: 'Source language requires review',
    results: (shown, total) => `${shown} of ${total} matching records`,
    view: (n, e) => `${n} visible nodes · ${e} relationships`,
    connectionCount: (n, total) => `${n} of ${total} connections shown for this node`,
    summary: s => `${s.nodes.toLocaleString('en-CA')} nodes · ${s.node_types.pib.toLocaleString('en-CA')} PIBs · ${s.node_types.pia.toLocaleString('en-CA')} assessments · source evidence on every relationship`,
  },
  fr: {
    skip: 'Passer au contenu principal', eyebrow: 'Suivre les sources', title: 'Explorateur de liens FRP / EFVP',
    intro: 'Commencez par un fichier ou une évaluation. Sélectionnez un nœud pour découvrir ses liens, puis une ligne pour consulter les preuves.',
    notice: 'Une référence est une citation, sans garantir que l’évaluation couvre tout le fichier. Les liens absents reflètent les preuves recueillies, sans démontrer l’absence d’une évaluation. Les lignes pointillées mènent à des références non résolues.',
    find: 'Trouver un point de départ', search: 'Nom ou identifiant (français ou anglais)', recordType: 'Type de document', allTypes: 'Tous les types',
    pib: 'FRP', pia: 'Évaluation de la vie privée', institution: 'Institution', class: 'Catégorie de documents', reference: 'Référence non résolue',
    allInstitutions: 'Toutes les institutions', moreResults: 'Plus de résultats', network: 'Explorer les liens', relationship: 'Relation',
    allRelations: 'Toutes les relations', references: 'Fait référence à', related_class: 'Catégorie connexe', listed_by: 'Répertorié sous l’institution',
    fit: 'Ajuster le graphique', reset: 'Recentrer sur le nœud sélectionné', share: 'Copier le lien de cette vue', loading: 'Chargement du graphique…',
    empty: 'Choisissez un résultat pour commencer.', details: 'Document et preuves', connections: 'Liens du nœud sélectionné',
    expand: 'Afficher plus de liens', overview: 'Aperçu', navPia: 'Évaluations de la vie privée', navGraph: 'Explorateur de liens',
    download: 'Télécharger le graphique JSON', methodology: 'Méthode du graphique', open: 'Ouvrir le document complet', source: 'Source originale',
    artifact: 'Preuve dans le dépôt', inspect: 'Consulter les preuves', focus: 'Commencer ici', resolved: 'Document correspondant',
    unresolved: 'Aucune correspondance unique', ambiguous: 'Référence ambiguë', standard: 'Norme pangouvernementale',
    noMatch: 'Aucun résultat. Essayez un autre identifiant ou effacez les filtres.', unavailable: 'Aucune copie lisible de cette évaluation n’a été recueillie.',
    copied: 'Lien de la vue copié.', copyFallback: 'Copiez le lien ci-dessous.', noConnections: 'Aucun lien pour ce filtre de relation.',
    cap: `La vue est limitée à ${MAX_NODES} nœuds. Recommencez au nœud sélectionné pour poursuivre l’exploration.`,
    loadError: 'Impossible de charger le graphique. Rechargez la page ou consultez les tableaux de FRP et les évaluations de la vie privée.',
    unknown: 'Ce document ne figure pas dans le graphique actuel. Cherchez un autre point de départ.',
    noCanvas: 'Impossible de charger le diagramme. La recherche, les détails et la liste de liens restent accessibles.',
    canvasLabel: 'Réseau de documents; utilisez la liste des liens pour naviguer au clavier.', line: 'Ligne', method: 'Méthode',
    observed: 'Observé le', candidates: 'Identifiants possibles (aucune correspondance affirmée)', legend: 'Légende',
    evidenceError: 'Impossible de charger les preuves. Sélectionnez à nouveau cette relation pour réessayer.',
    copyLabel: 'Lien de la vue', exported: 'Copie lisible recueillie', http_error: 'Échec de récupération de la source',
    insufficient_content: 'Texte recueilli insuffisant', soft_error_page: 'La source a renvoyé une page d’erreur',
    not_pia_content: 'Contenu source à vérifier', language_mismatch: 'Langue de la source à vérifier',
    results: (shown, total) => `${shown} résultats affichés sur ${total}`,
    view: (n, e) => `${n} nœuds visibles · ${e} relations`,
    connectionCount: (n, total) => `${n} liens affichés sur ${total} pour ce nœud`,
    summary: s => `${s.nodes.toLocaleString('fr-CA')} nœuds · ${s.node_types.pib.toLocaleString('fr-CA')} FRP · ${s.node_types.pia.toLocaleString('fr-CA')} évaluations · preuves pour chaque relation`,
  }
};
let index, data, state, cy, resultLimit = 12, currentView;
const evidenceCache = new Map();
const t = key => words[state?.lang || (new URLSearchParams(location.search).get('lang') === 'fr' ? 'fr' : 'en')][key] || key;
const el = (tag, text, cls) => { const node = document.createElement(tag); if (text != null) node.textContent = text; if (cls) node.className = cls; return node; };
function button(text, action) { const b = el('button', text); b.type = 'button'; b.addEventListener('click', action); return b; }
function link(text, href) {
  const a = el('a', text);
  try { const url = new URL(href, location.href); if (['http:', 'https:'].includes(url.protocol)) a.href = url.href; } catch {}
  return a;
}
function repositoryLink(path, line) {
  return 'https://github.com/PatLittle/pibs/blob/main/' + path.split('/').map(encodeURIComponent).join('/') + (line ? '#L' + Number(line) : '');
}
function localize() {
  document.documentElement.lang = state.lang;
  document.title = t('title') + ' - Info Source Data Explorer';
  document.querySelectorAll('[data-i18n]').forEach(n => { n.textContent = t(n.dataset.i18n); });
  $('language').textContent = state.lang === 'en' ? 'Français' : 'English';
  $('language').lang = state.lang === 'en' ? 'fr' : 'en';
  $('cy').setAttribute('aria-label', t('canvasLabel'));
  $('share-link').setAttribute('aria-label', t('copyLabel'));
  document.querySelector('.graph-legend').setAttribute('aria-label', t('legend'));
  const header = document.querySelector('gcds-header');
  header?.setAttribute('lang', state.lang);
  const alternate = stateURL(location.href, { ...state, lang: state.lang === 'en' ? 'fr' : 'en' });
  header?.setAttribute('lang-href', alternate.href);
  // The existing site navigation remains available in both interface languages.
  const nav = { 'index.html': ['Overview', 'Aperçu'], 'table.html?dataset=institutions': ['Institutions', 'Institutions'],
    'table.html?dataset=pibs': ['PIBs', 'FRP'], 'table.html?dataset=classes': ['Classes of Records', 'Catégories de documents'],
    'table.html?dataset=links': ['PIB-to-class linkages', 'Liens FRP-catégories'], 'table.html?dataset=standard-pibs': ['Standard PIBs', 'FRP ordinaires'],
    'table.html?dataset=standard-classes': ['Standard classes', 'Catégories ordinaires'], 'table.html?dataset=categories': ['Categories', 'Catégories'],
    'table.html?dataset=pib-types': ['PIB types', 'Types de FRP'] };
  document.querySelectorAll('gcds-nav-link').forEach(n => { if (nav[n.getAttribute('href')]) n.textContent = nav[n.getAttribute('href')][state.lang === 'fr' ? 1 : 0]; });
  document.querySelectorAll('gcds-nav-group').forEach((n, i) => {
    const group = state.lang === 'fr' ? ['Données institutionnelles', 'Données de référence'][i] : ['Institution data', 'Reference data'][i];
    n.setAttribute('open-trigger', group);
    n.setAttribute('close-trigger', (state.lang === 'fr' ? 'Fermer : ' : 'Close: ') + group);
    n.setAttribute('menu-label', group);
  });
  const selected = $('institution').value;
  $('institution').replaceChildren(el('option', t('allInstitutions')));
  $('institution').firstChild.value = '';
  [...index.nodes.values()].filter(n => n.type === 'institution').sort((a, b) => label(a, state.lang).localeCompare(label(b, state.lang), state.lang)).forEach(n => {
    const option = el('option', label(n, state.lang)); option.value = n.institution_id; $('institution').append(option);
  });
  $('institution').value = selected;
  $('data-summary').textContent = t('summary')(data.summary);
}
function renderSearch() {
  const matches = search(index, $('search').value, $('node-type').value, $('institution').value, state.lang);
  $('results').replaceChildren();
  for (const node of matches.slice(0, resultLimit)) {
    const li = el('li');
    const b = button(label(node, state.lang), () => selectNode(node.id, true));
    b.append(el('small', `${t(node.type)} · ${node.identifier}`));
    li.append(b); $('results').append(li);
  }
  $('search-status').textContent = matches.length ? t('results')(Math.min(resultLimit, matches.length), matches.length) : t('noMatch');
  $('more-results').hidden = matches.length <= resultLimit;
}
async function evidenceList(edge, container) {
  container.textContent = t('loading');
  try {
    if (!evidenceCache.has(edge.evidence_url)) evidenceCache.set(edge.evidence_url, fetch(edge.evidence_url).then(async r => {
      if (!r.ok) throw new Error('Evidence HTTP ' + r.status);
      return r.json();
    }));
    const shard = await evidenceCache.get(edge.evidence_url);
    container.replaceChildren();
    for (const item of shard[edge.id]) {
      const section = el('div', null, 'graph-evidence');
      section.append(el('strong', (item.language || '').toUpperCase() + ' · ' + (item.mention || item.field || '')));
      if (item.excerpt) { const quote = el('blockquote', item.excerpt); if (item.language) quote.lang = item.language; section.append(quote); }
      if (item.source_url) section.append(link(t('source'), item.source_url), document.createTextNode(' · '));
      section.append(link(t('artifact') + (item.line ? ` · ${t('line')} ${item.line}` : ''), repositoryLink(item.source_path, item.line)));
      if (item.method) section.append(el('small', t('method') + ': ' + item.method));
      if (item.checked_at_utc) section.append(el('small', t('observed') + ': ' + item.checked_at_utc));
      if (item.markdown_sha256) section.append(el('small', 'SHA-256: ' + item.markdown_sha256));
      container.append(section);
    }
  } catch {
    evidenceCache.delete(edge.evidence_url);
    container.textContent = t('evidenceError');
  }
}
function inspect() {
  $('detail').replaceChildren();
  const edge = index.edges.get(state.edge);
  if (edge) {
    $('detail').append(el('h4', t(edge.type)), el('p', t(edge.resolution)));
    for (const id of [edge.source, edge.target]) $('detail').append(button(label(index.nodes.get(id), state.lang), () => selectNode(id)));
    const evidence = el('div'); $('detail').append(evidence); evidenceList(edge, evidence);
    return;
  }
  const node = index.nodes.get(state.selected);
  if (!node || !currentView.nodes.some(n => n.id === node.id)) return;
  $('detail').append(el('p', t(node.type) + (node.scope === 'standard' ? ' · ' + t('standard') : '')),
    el('h4', label(node, state.lang)), el('p', node.identifier));
  if (!node['label_' + state.lang] && (node.label_en || node.label_fr)) $('detail').lastElementChild.previousElementSibling.lang = node.label_en ? 'en' : 'fr';
  const description = node['description_' + state.lang];
  if (description) $('detail').append(el('p', description));
  if (node.resolution) $('detail').append(el('p', t(node.resolution)));
  if (node.candidates?.length) $('detail').append(el('p', t('candidates') + ': ' + node.candidates.join('; ')));
  if (node.type === 'pia' && !node.available_languages.length) $('detail').append(el('p', t('unavailable')));
  for (const [lang, status] of Object.entries(node.source_status || {})) $('detail').append(el('p', lang.toUpperCase() + ' · ' + t(status)));
  if (node.collected_at_utc) $('detail').append(el('p', t('observed') + ': ' + node.collected_at_utc));
  if (node.record_url) { const url = new URL(node.record_url, location.href); url.searchParams.set('lang', state.lang); $('detail').append(link(t('open'), url.href), el('br')); }
  for (const [lang, url] of Object.entries(node.sources || {})) if (url) $('detail').append(link(`${t('source')} · ${lang.toUpperCase()}`, url), el('br'));
  if (node.source_path) $('detail').append(link(t('artifact'), repositoryLink(node.source_path)), el('br'));
  $('detail').append(button(t('focus'), () => selectNode(node.id, true)));
}
function renderConnections() {
  const id = state.selected;
  const all = connections(index, id, state.relation);
  const shown = all.slice(0, state.expanded.get(id) || PAGE);
  $('connections').replaceChildren();
  for (const edge of shown) {
    const other = index.nodes.get(edge.source === id ? edge.target : edge.source);
    const li = el('li');
    li.append(el('small', `${t(edge.type)} · ${t(edge.resolution)}`),
      button(label(other, state.lang), () => selectNode(other.id)), button(t('inspect'), () => selectEdge(edge.id)));
    $('connections').append(li);
  }
  $('connections-status').textContent = !index.nodes.has(id) ? t('empty') : all.length ? t('connectionCount')(shown.length, all.length) : t('noConnections');
  $('expand').hidden = shown.length >= all.length || !index.nodes.has(id);
  $('expand').disabled = currentView.capped || (state.expanded.get(id) || 0) >= MAX_NODES;
}
function draw() {
  if (!cy) return;
  const selected = state.selected;
  cy.elements().remove();
  cy.add(currentView.nodes.map(n => ({ data: { id: n.id, type: n.type,
    label: label(n, state.lang), color: { pib: '#1f5a94', pia: '#087a82', institution: '#754b94', class: '#b47700', reference: '#d7dee5' }[n.type] } })));
  cy.add(currentView.edges.map(e => ({ data: { ...e, label: t(e.type) } })));
  cy.getElementById(selected).addClass('active');
  if (state.edge) cy.getElementById(state.edge).addClass('active');
  cy.layout({ name: currentView.nodes.length > 12 ? 'cose' : 'concentric', animate: false, padding: 40,
    nodeDimensionsIncludeLabels: true, nodeRepulsion: () => 8500, idealEdgeLength: () => 100,
    minNodeSpacing: 35, spacingFactor: 1.2,
    concentric: n => n.id() === state.root ? 10 : 1, levelWidth: () => 1 }).run();
}
function render(push = false) {
  currentView = neighborhood(index, state);
  if (currentView.nodes.length && !currentView.nodes.some(n => n.id === state.selected)) state.selected = state.root;
  $('relation').value = state.relation;
  localize(); renderSearch(); inspect(); renderConnections(); draw();
  $('empty-view').hidden = currentView.nodes.length > 0;
  $('view-status').textContent = state.root && !index.nodes.has(state.root) ? t('unknown') : t('view')(currentView.nodes.length, currentView.edges.length);
  if (currentView.capped) $('view-status').textContent += ' · ' + t('cap');
  if (!cy) $('view-status').textContent += ' · ' + t('noCanvas');
  $('reset').disabled = !currentView.nodes.length;
  $('share-link').hidden = true; $('share-status').textContent = '';
  const url = stateURL(location.href, state);
  if (push) history.pushState(null, '', url);
}
function selectNode(id, start = false) {
  if (!index.nodes.has(id)) return;
  if (start || !currentView.nodes.some(n => n.id === id)) { state.root = id; state.expanded = new Map(); }
  $('search-panel').open = false;
  state.selected = id; state.edge = '';
  if (!state.expanded.has(id)) state.expanded.set(id, PAGE);
  render(true);
  $('inspector-heading').tabIndex = -1;
  $('inspector-heading').focus({ preventScroll: true });
}
function selectEdge(id) {
  state.edge = id; render(true);
  $('inspector-heading').tabIndex = -1;
  $('inspector-heading').focus({ preventScroll: true });
  $('inspector').scrollIntoView({ block: 'nearest' });
}
async function init() {
  // Localize the initial failure message even if the dataset is unavailable.
  try {
    const response = await fetch('data/graph.json');
    if (!response.ok) throw new Error('Graph HTTP ' + response.status);
    data = await response.json(); index = indexGraph(data); state = parseState(location.href, index);
    $('search-panel').open = !state.root || !index.nodes.has(state.root);
    if (typeof window.cytoscape === 'function') {
      cy = window.cytoscape({ container: $('cy'), elements: [], minZoom: .1, maxZoom: 3, wheelSensitivity: .2,
        style: [
          { selector: 'node', style: { 'background-color': 'data(color)', label: 'data(label)', color: '#26374a', 'font-size': 11,
            'text-wrap': 'ellipsis', 'text-max-width': 130, 'text-valign': 'bottom', 'text-margin-y': 7, width: 32, height: 32, 'border-color': '#26374a', 'border-width': 1 } },
          { selector: 'node[type="pia"]', style: { shape: 'diamond', width: 42, height: 42 } },
          { selector: 'node[type="institution"]', style: { shape: 'round-rectangle', width: 46 } },
          { selector: 'node[type="class"]', style: { shape: 'rectangle' } },
          { selector: 'node[type="reference"]', style: { shape: 'hexagon', 'border-style': 'dashed' } },
          { selector: 'edge', style: { width: 1.5, 'line-color': '#7a8b9b', 'target-arrow-color': '#7a8b9b', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier' } },
          { selector: 'edge[resolution != "resolved"]', style: { 'line-style': 'dashed' } },
          { selector: '.active', style: { 'border-width': 4, 'border-color': '#ce4a00', 'line-color': '#ce4a00', 'target-arrow-color': '#ce4a00', width: 4 } },
          { selector: 'node.active', style: { width: 42, height: 42 } }
        ] });
      cy.on('tap', 'node', event => selectNode(event.target.id()));
      cy.on('tap', 'edge', event => selectEdge(event.target.id()));
    }
    for (const id of ['search', 'node-type', 'institution']) $(id).addEventListener(id === 'search' ? 'input' : 'change', () => { resultLimit = 12; renderSearch(); });
    $('more-results').addEventListener('click', () => { resultLimit += 24; renderSearch(); });
    $('expand').addEventListener('click', () => { state.expanded.set(state.selected, (state.expanded.get(state.selected) || PAGE) + PAGE); render(true); });
    $('relation').addEventListener('change', () => { state.relation = $('relation').value; state.expanded = new Map([[state.root, PAGE]]); state.selected = state.root; state.edge = ''; render(true); });
    $('fit').addEventListener('click', () => cy?.fit(undefined, 40));
    $('reset').addEventListener('click', () => selectNode(state.selected, true));
    $('language').addEventListener('click', () => { state.lang = state.lang === 'en' ? 'fr' : 'en'; render(true); });
    $('share').addEventListener('click', async () => {
      const url = stateURL(location.href, state).href;
      try { await navigator.clipboard.writeText(url); $('share-status').textContent = t('copied'); }
      catch { $('share-link').value = url; $('share-link').hidden = false; $('share-link').select(); $('share-status').textContent = t('copyFallback'); }
    });
    window.addEventListener('popstate', () => { state = parseState(location.href, index); render(); });
    render();
  } catch (error) {
    $('view-status').textContent = t('loadError'); $('view-status').setAttribute('role', 'alert');
    for (const id of ['search', 'node-type', 'institution', 'relation', 'fit', 'reset', 'share']) $(id).disabled = true;
    console.error(error);
  }
}
init();
