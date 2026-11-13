import { PAGE, MAX_NODES, label, indexGraph, search, connections, neighborhood, parseState, stateURL } from './graph-model.mjs';

import { NODE_COLORS, browseRecords, pageRecords, recordStats } from './graph-records.mjs';
import { EXAMPLES, exampleStats, exampleState } from './graph-examples.mjs';
import { createTour } from './graph-tour.mjs';

const $ = id => document.getElementById(id);
const words = {
  en: {
    tourLaunch: 'Start guided tour', examplesHeading: 'Five paths worth exploring',
    examplesIntro: 'Choose a story to open a connected view, or search the full inventory below.',
    examplesStatus: 'Five curated starting points. Enter a name or choose a filter to search all records.',
    exampleCounts: (r, i) => `${r} directly connected records · ${i} represented institutions`,
    standardPib: 'Standard PIB', standardClass: 'Standard Class of Records', category: 'Personal-information category', pib_type: 'PIB type',
    has_type: 'Has PIB type', category_match: 'Category match (derived)',
    derivedNote: 'Category links are estimated matches from PIB descriptions, not official assignments. Confidence describes the matching rule, not the likelihood that an institution holds your information.',
    derived: 'Derived match', documented: 'Documented relationship', confidence: 'Rule confidence', rule: 'Matching rule',
    attributes: 'Record attributes', purpose: 'Purpose', class_of_individuals: 'People covered', consistent_uses: 'Consistent uses', retention_disposal: 'Retention and disposal', document_types: 'Document types', date_last_modified: 'Source modification date',
    institutionalContext: 'Institution', represented: 'Represented institutions', institutionScope: 'Institution-specific',
    derivedLegend: 'Dotted: derived category match', unresolvedLegend: 'Dashed: unresolved reference',
    attributeError: 'Attributes could not be loaded. Retry or open the full record.', retry: 'Retry',
    aliasesLabel: 'Other recorded identifiers',
    skip: 'Skip to main content', eyebrow: 'Follow the evidence', title: 'PI Network Explorer',
    intro: 'Start with an example, a record, a personal-information category or a PIB type. Select a node to reveal its connections; select a line to inspect the source evidence.',
    notice: 'A reference is a citation, not proof that an assessment covers the entire bank. Missing links reflect collected evidence, not the absence of an assessment. Dashed lines lead to unresolved references.',
    find: 'Find a starting point', search: 'Name or identifier (English or French)', recordType: 'Record type', allTypes: 'All types',
    pib: 'PIB', pia: 'Privacy assessment', institution: 'Institution', class: 'Class of Records', reference: 'Unresolved reference',
    allInstitutions: 'All institutions', moreResults: 'More results', network: 'Explore connections', relationship: 'Relationship',
    allRelations: 'All relationships', references: 'References', related_class: 'Related class', listed_by: 'Listed under institution',
    fit: 'Fit graph', reset: 'Reset to selected node', share: 'Copy view link', loading: 'Loading graph data…',
    empty: 'Choose a search result to start exploring.', details: 'Record and evidence', connections: 'Connections of the selected node',
    expand: 'Show more connections', overview: 'Overview', navPia: 'Privacy Assessments', navGraph: 'PI Network Explorer',
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
    workspace: 'Explore the network', fullscreen: 'Full screen', exitFullscreen: 'Exit full screen', hidePanel: 'Hide records', showPanel: 'Show records', browseControls: 'Find and sort records',
    highlight: 'Highlight direct connections', recordTab: 'Record', browseTab: 'Browse records', previousRecord: 'Previous record', nextRecord: 'Next record',
    browseScope: 'Browse', connectedScope: 'Connected records', allScope: 'All collected records', useSelected: 'Connections of selected record',
    filterRecords: 'Filter these records', sort: 'Sort', sortName: 'Name', sortDegree: 'Most connected', previous: 'Previous', next: 'Next', pageSize: 'Records per page',
    directRecords: 'Connected records', directEdges: 'Direct relationships', typeBreakdown: 'Explore by record type', sourceDetails: 'Sources and collection details',
    evidenceAudit: 'Collection details', evidenceNote: 'A citation records a reference; it does not establish assessment coverage.',
    unresolvedCount: n => `${n} direct relationships need resolution`, degree: n => `${n} direct relationships across the collected graph`,
    page: (p, n) => `Page ${p} of ${n}`, range: (a, b, n) => `${a}–${b} of ${n} records`, position: (p, n) => p ? `Record ${p} of ${n}` : `${n} records in this list`,
    anchor: name => `Connected to: ${name}`, expandGraph: 'Add more connections to graph',
    results: (shown, total) => `${shown} of ${total} matching records`,
    view: (n, e) => `${n} visible nodes · ${e} relationships`,
    connectionCount: (n, total) => `${n} of ${total} connections shown for this node`,
    summary: s => `${s.nodes.toLocaleString('en-CA')} nodes · ${s.node_types.pib.toLocaleString('en-CA')} PIBs · ${s.node_types.pia.toLocaleString('en-CA')} assessments · source evidence on every relationship`,
  },
  fr: {
    tourLaunch: 'Commencer la visite guidée', examplesHeading: 'Cinq parcours à découvrir',
    examplesIntro: 'Choisissez un parcours pour ouvrir une vue connectée, ou cherchez dans l’inventaire ci-dessous.',
    examplesStatus: 'Cinq points de départ choisis. Saisissez un nom ou choisissez un filtre pour chercher tous les documents.',
    exampleCounts: (r, i) => `${r} documents directement liés · ${i} institutions représentées`,
    standardPib: 'FRP ordinaire', standardClass: 'Catégorie de documents ordinaire', category: 'Catégorie de renseignements personnels', pib_type: 'Type de FRP',
    has_type: 'A le type de FRP', category_match: 'Correspondance de catégorie (dérivée)',
    derivedNote: 'Les liens de catégorie sont des estimations tirées des descriptions des FRP, et non des attributions officielles. La confiance concerne la règle de correspondance, pas la probabilité qu’une institution détienne vos renseignements.',
    derived: 'Correspondance dérivée', documented: 'Relation documentée', confidence: 'Confiance de la règle', rule: 'Règle de correspondance',
    attributes: 'Attributs du document', purpose: 'Fin', class_of_individuals: 'Personnes visées', consistent_uses: 'Usages compatibles', retention_disposal: 'Conservation et élimination', document_types: 'Types de documents', date_last_modified: 'Date de modification de la source',
    institutionalContext: 'Institution', represented: 'Institutions représentées', institutionScope: 'Propre à une institution',
    derivedLegend: 'Petits points : catégorie dérivée', unresolvedLegend: 'Pointillés : référence non résolue',
    attributeError: 'Impossible de charger les attributs. Réessayez ou ouvrez le document complet.', retry: 'Réessayer',
    aliasesLabel: 'Autres identifiants dans les sources',
    skip: 'Passer au contenu principal', eyebrow: 'Suivre les sources', title: 'Explorateur du réseau de RP',
    intro: 'Commencez par un exemple, un document, une catégorie de renseignements personnels ou un type de FRP. Sélectionnez un nœud pour découvrir ses liens, puis une ligne pour consulter les preuves.',
    notice: 'Une référence est une citation, sans garantir que l’évaluation couvre tout le fichier. Les liens absents reflètent les preuves recueillies, sans démontrer l’absence d’une évaluation. Les lignes pointillées mènent à des références non résolues.',
    find: 'Trouver un point de départ', search: 'Nom ou identifiant (français ou anglais)', recordType: 'Type de document', allTypes: 'Tous les types',
    pib: 'FRP', pia: 'Évaluation de la vie privée', institution: 'Institution', class: 'Catégorie de documents', reference: 'Référence non résolue',
    allInstitutions: 'Toutes les institutions', moreResults: 'Plus de résultats', network: 'Explorer les liens', relationship: 'Relation',
    allRelations: 'Toutes les relations', references: 'Fait référence à', related_class: 'Catégorie connexe', listed_by: 'Répertorié sous l’institution',
    fit: 'Ajuster le graphique', reset: 'Recentrer sur le nœud sélectionné', share: 'Copier le lien de cette vue', loading: 'Chargement du graphique…',
    empty: 'Choisissez un résultat pour commencer.', details: 'Document et preuves', connections: 'Liens du nœud sélectionné',
    expand: 'Afficher plus de liens', overview: 'Aperçu', navPia: 'Évaluations de la vie privée', navGraph: 'Explorateur du réseau de RP',
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
    workspace: 'Explorer le réseau', fullscreen: 'Plein écran', exitFullscreen: 'Quitter le plein écran', hidePanel: 'Masquer les documents', showPanel: 'Afficher les documents', browseControls: 'Trouver et trier les documents',
    highlight: 'Surligner les liens directs', recordTab: 'Document', browseTab: 'Parcourir', previousRecord: 'Document précédent', nextRecord: 'Document suivant',
    browseScope: 'Parcourir', connectedScope: 'Documents liés', allScope: 'Tous les documents recueillis', useSelected: 'Liens du document sélectionné',
    filterRecords: 'Filtrer ces documents', sort: 'Trier', sortName: 'Nom', sortDegree: 'Le plus de liens', previous: 'Précédent', next: 'Suivant', pageSize: 'Documents par page',
    directRecords: 'Documents liés', directEdges: 'Relations directes', typeBreakdown: 'Explorer par type', sourceDetails: 'Sources et collecte',
    evidenceAudit: 'Détails de la collecte', evidenceNote: 'Une citation indique une référence, sans établir la portée de l’évaluation.',
    unresolvedCount: n => `${n} relations directes à résoudre`, degree: n => `${n} relations directes dans le graphique recueilli`,
    page: (p, n) => `Page ${p} sur ${n}`, range: (a, b, n) => `${a}–${b} documents sur ${n}`, position: (p, n) => p ? `Document ${p} sur ${n}` : `${n} documents dans cette liste`,
    anchor: name => `Liens avec : ${name}`, expandGraph: 'Ajouter des liens au graphique',
    results: (shown, total) => `${shown} résultats affichés sur ${total}`,
    view: (n, e) => `${n} nœuds visibles · ${e} relations`,
    connectionCount: (n, total) => `${n} liens affichés sur ${total} pour ce nœud`,
    summary: s => `${s.nodes.toLocaleString('fr-CA')} nœuds · ${s.node_types.pib.toLocaleString('fr-CA')} FRP · ${s.node_types.pia.toLocaleString('fr-CA')} évaluations · preuves pour chaque relation`,
  }
};
let index, data, state, cy, tour, resultLimit = 12, currentView, lastViewKey = '';
let recordEntries = [], activeTab = 'detail', expandedMode = false, nativeMode = false, previousFocus;
const browser = { anchor: '', scope: 'connected', query: '', type: '', sort: 'name', page: 1, size: 8 };
const inertElements = new Map();
const evidenceCache = new Map();
const attributeCache = new Map();
let evidenceReady = Promise.resolve();
let attributeReady = Promise.resolve();
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
  $('fullscreen').textContent = t(expandedMode ? 'exitFullscreen' : 'fullscreen');
  $('toggle-panel').textContent = t($('explorer').classList.contains('panel-hidden') ? 'showPanel' : 'hidePanel');
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
  const curated = !$('search').value.trim() && !$('node-type').value && !$('institution').value;
  $('examples').hidden = !curated;
  $('example-list').replaceChildren();
  for (const example of EXAMPLES.filter(e => index.nodes.has(e.id))) {
    const li = el('li'), node = index.nodes.get(example.id);
    const b = button(example['title_' + state.lang], () => openExample(example.id));
    b.dataset.example = example.id; b.dataset.nodeType = node.type;
    b.append(el('span', example['text_' + state.lang], 'example-description'));
    const stats = exampleStats(index, example.id);
    b.append(el('small', t('exampleCounts')(stats.records, stats.institutions)));
    li.append(b); $('example-list').append(li);
  }
  const matches = search(index, $('search').value, $('node-type').value, $('institution').value, state.lang);
  $('results').replaceChildren();
  if (curated) {
    $('search-status').textContent = t('examplesStatus'); $('more-results').hidden = true; return;
  }
  for (const node of matches.slice(0, resultLimit)) {
    const li = el('li');
    const b = button(label(node, state.lang), () => selectNode(node.id, true));
    b.dataset.nodeType = node.type;
    b.append(el('small', `${t(node.type)} · ${node.identifier}`));
    li.append(b); $('results').append(li);
  }
  $('search-status').textContent = matches.length ? t('results')(Math.min(resultLimit, matches.length), matches.length) : t('noMatch');
  $('more-results').hidden = matches.length <= resultLimit;
}
function openExample(id) {
  state = exampleState(index, id, state.lang);
  browser.anchor = id; browser.scope = 'connected'; browser.page = 1; browser.query = ''; browser.type = '';
  syncBrowserControls(); setTab('detail'); render(true);
  $('inspector-heading').focus({ preventScroll: true });
  $('explorer').scrollIntoView({ block: 'start' });
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
      if (edge.basis === 'derived') section.append(el('p', t('derivedNote'), 'record-alert'));
      if (item.confidence != null) section.append(el('p', t('confidence') + ': ' + Math.round(item.confidence * 100) + '%'));
      if (item.rule) section.append(el('p', t('rule') + ': ' + item.rule));
      if (item.source_url) section.append(link(t('source'), item.source_url), document.createTextNode(' · '));
      section.append(link(t('artifact') + (item.line ? ` · ${t('line')} ${item.line}` : ''), repositoryLink(item.source_path, item.line)));
      const audit = el('details', null, 'evidence-audit'); audit.append(el('summary', t('evidenceAudit')));
      if (item.method) audit.append(el('small', t('method') + ': ' + item.method));
      if (item.checked_at_utc) audit.append(el('small', t('observed') + ': ' + item.checked_at_utc));
      if (item.markdown_sha256) audit.append(el('small', 'SHA-256: ' + item.markdown_sha256));
      section.append(audit);
      container.append(section);
    }
  } catch {
    evidenceCache.delete(edge.evidence_url);
    container.textContent = t('evidenceError');
  }
}
async function recordAttributes(node, container) {
  container.textContent = t('loading');
  try {
    if (!attributeCache.has(node.attribute_url)) attributeCache.set(node.attribute_url, fetch(node.attribute_url).then(async r => {
      if (!r.ok) throw new Error('Attributes HTTP ' + r.status);
      return r.json();
    }));
    const attributes = (await attributeCache.get(node.attribute_url))[node.id];
    container.replaceChildren(el('h5', t('attributes')));
    for (const key of ['pib_type', 'purpose', 'class_of_individuals', 'consistent_uses', 'retention_disposal', 'document_types', 'date_last_modified']) {
      const value = attributes[key] || attributes[key + '_' + state.lang];
      if (!value) continue;
      const field = el('details'); field.append(el('summary', t(key)), el('p', value)); container.append(field);
    }
  } catch {
    attributeCache.delete(node.attribute_url);
    container.replaceChildren(el('p', t('attributeError')));
    container.append(button(t('retry'), () => recordAttributes(node, container)));
  }
}
function setTab(tab, focus = false) {
  activeTab = tab;
  $('explorer').classList.remove('panel-hidden'); $('inspector').inert = false;
  $('toggle-panel').setAttribute('aria-expanded', 'true'); $('toggle-panel').textContent = t('hidePanel');
  for (const name of ['detail', 'browser']) {
    const selected = name === tab;
    $('tab-' + name).setAttribute('aria-selected', String(selected));
    $('tab-' + name).tabIndex = selected ? 0 : -1;
    $(name === 'detail' ? 'record-panel' : 'browser-panel').hidden = !selected;
  }
  if (focus) $('tab-' + tab).focus({ preventScroll: true });
  requestAnimationFrame(() => cy?.resize());
}
function showConnections(type = '') {
  browser.anchor = state.selected; browser.scope = 'connected'; browser.type = type; browser.query = ''; browser.page = 1;
  syncBrowserControls(); renderConnections(); setTab('browser', true);
}
function syncBrowserControls() {
  $('browser-scope').value = browser.scope; $('browser-type').value = browser.type;
  $('browser-query').value = browser.query; $('browser-sort').value = browser.sort;
  $('records-per-page').value = String(browser.size);
}
function inspect() {
  $('detail').replaceChildren();
  const edge = index.edges.get(state.edge);
  if (edge) {
    const card = el('article', null, 'record-card'); card.dataset.nodeType = index.nodes.get(edge.target).type;
    card.append(el('span', t(edge.basis === 'derived' ? 'derived' : edge.resolution), 'record-badge'), el('h4', t(edge.type)), el('p', t(edge.basis === 'derived' ? 'derivedNote' : edge.type === 'references' ? 'evidenceNote' : 'documented'), 'record-note'));
    const endpoints = el('div', null, 'edge-endpoints');
    for (const id of [edge.source, edge.target]) {
      const node = index.nodes.get(id), b = button(label(node, state.lang), () => selectNode(id));
      b.dataset.nodeType = node.type; endpoints.append(b);
    }
    card.append(endpoints); $('detail').append(card);
    const evidence = el('div'); card.append(evidence); evidenceReady = evidenceList(edge, evidence);
    return;
  }
  const node = index.nodes.get(state.selected);
  if (!node || !currentView.nodes.some(n => n.id === node.id)) { $('detail').append(el('p', t('empty'), 'record-note')); return; }
  const card = el('article', null, 'record-card'); card.dataset.nodeType = node.type;
  const title = el('h4', label(node, state.lang));
  if (!node['label_' + state.lang]) title.lang = node.label_en ? 'en' : 'fr';
  card.append(el('span', t(node.type) + (node.scope ? ' · ' + t(node.scope === 'standard' ? 'standard' : 'institutionScope') : ''), 'record-badge'), title, el('p', node.identifier, 'record-identifier'));
  const aliases = [...new Set((node.aliases || []).filter(v => v && v !== node.identifier && /\s/.test(v)))];
  if (aliases.length) card.append(el('p', t('aliasesLabel') + ': ' + aliases.join(' · '), 'record-note'));
  if (node.institution_id && node.type !== 'institution') {
    const institution = index.nodes.get('institution:' + node.institution_id);
    if (institution) card.append(button(label(institution, state.lang), () => selectNode(institution.id)));
  }
  if (node.type === 'category') card.append(el('p', t('derivedNote'), 'record-alert'));
  const stats = recordStats(index, node.id, state.relation), metrics = el('div', null, 'record-metrics');
  const represented = new Set(connections(index, node.id, state.relation).map(e => index.nodes.get(e.source === node.id ? e.target : e.source).institution_id).filter(Boolean));
  for (const [count, name] of [[stats.records, 'directRecords'], [stats.relationships, 'directEdges'], [represented.size, 'represented']]) {
    const metric = el('div', null, 'record-metric'); metric.append(el('strong', count), el('span', t(name))); metrics.append(metric);
  }
  card.append(metrics);
  if (stats.unresolved) card.append(el('p', t('unresolvedCount')(stats.unresolved), 'record-alert'));
  const chips = el('div', null, 'type-chips'); chips.setAttribute('aria-label', t('typeBreakdown'));
  for (const [type, count] of Object.entries(stats.types)) if (count) {
    const chip = button(t(type) + ' · ' + count, () => showConnections(type)); chip.dataset.nodeType = type; chips.append(chip);
  }
  card.append(chips);
  const description = node['description_' + state.lang];
  if (description) card.append(el('p', description, 'record-description'));
  if (node.attribute_url) {
    const group = el('section', null, 'record-attributes'); card.append(group);
    attributeReady = recordAttributes(node, group);
  }
  if (node.resolution) card.append(el('p', t(node.resolution), 'record-alert'));
  if (node.candidates?.length) card.append(el('p', t('candidates') + ': ' + node.candidates.join('; '), 'record-note'));
  if (node.type === 'pia' && !node.available_languages.length) card.append(el('p', t('unavailable'), 'record-alert'));
  const actions = el('div', null, 'record-actions');
  const browse = button(t('connectedScope'), () => showConnections()); browse.className = 'primary-action'; actions.append(browse);
  actions.append(button(t('focus'), () => selectNode(node.id, true)));
  if (node.record_url) { const url = new URL(node.record_url, location.href); url.searchParams.set('lang', state.lang); actions.append(link(t('open'), url.href)); }
  card.append(actions);
  const sources = el('details', null, 'record-sources'); sources.append(el('summary', t('sourceDetails')));
  for (const [lang, status] of Object.entries(node.source_status || {})) sources.append(el('p', lang.toUpperCase() + ' · ' + t(status)));
  if (node.collected_at_utc) sources.append(el('p', t('observed') + ': ' + node.collected_at_utc));
  for (const [lang, url] of Object.entries(node.sources || {})) if (url) sources.append(link(`${t('source')} · ${lang.toUpperCase()}`, url));
  if (node.source_path) sources.append(link(t('artifact'), repositoryLink(node.source_path)));
  card.append(sources); $('detail').append(card);
}
function renderConnections() {
  recordEntries = browseRecords(index, { ...browser, relation: state.relation, lang: state.lang });
  const page = pageRecords(recordEntries, browser.page, browser.size); browser.page = page.page;
  $('connections').replaceChildren();
  for (const { node, edges } of page.items) {
    const li = el('li'); li.dataset.nodeType = node.type; li.dataset.recordId = node.id; li.dataset.selected = String(node.id === state.selected);
    const b = button(label(node, state.lang), () => selectNode(node.id, false, true)); b.className = 'record-row-title';
    li.append(el('span', t(node.type) + (node.scope === 'standard' ? ' · ' + t('standard') : ''), 'record-badge'), b, el('small', node.identifier), el('small', t('degree')(index.adjacency.get(node.id).length)));
    for (const edge of edges) {
      const evidence = button(t('inspect') + ' · ' + t(edge.type), () => selectEdge(edge.id)); evidence.className = 'evidence-button';
      li.append(el('small', t(edge.basis === 'derived' ? 'derived' : edge.resolution)), evidence);
    }
    $('connections').append(li);
  }
  $('connections-status').textContent = page.total ? t('range')(page.start, page.end, page.total) : t('noMatch');
  $('page-status').textContent = t('page')(page.page, page.pages);
  $('previous-page').disabled = page.page <= 1; $('next-page').disabled = page.page >= page.pages;
  const anchor = index.nodes.get(browser.anchor);
  $('browser-anchor').textContent = browser.scope === 'connected' && anchor ? t('anchor')(label(anchor, state.lang)) : t('allScope');
  $('use-selected').disabled = !index.nodes.has(state.selected);
  const position = recordEntries.findIndex(r => r.node.id === state.selected);
  $('record-position').textContent = t('position')(position + 1, recordEntries.length);
  $('previous-record').disabled = position <= 0;
  $('next-record').disabled = !recordEntries.length || position === recordEntries.length - 1;
  const all = connections(index, state.selected, state.relation);
  $('expand').textContent = t('expandGraph');
  $('expand').hidden = (state.expanded.get(state.selected) || PAGE) >= all.length || !index.nodes.has(state.selected);
  $('expand').disabled = currentView.capped || (state.expanded.get(state.selected) || 0) >= MAX_NODES;
}
function highlightSelection() {
  if (!cy) return;
  cy.elements().removeClass('active dimmed');
  const edge = cy.getElementById(state.edge), selected = cy.getElementById(state.selected);
  const focus = edge.length ? edge.union(edge.connectedNodes()) : selected.closedNeighborhood();
  selected.addClass('active'); edge.addClass('active');
  if ($('highlight').checked && focus.length) cy.elements().not(focus).addClass('dimmed');
}
function draw() {
  if (!cy) return;
  const key = currentView.nodes.map(n => n.id).sort().join('|') + currentView.edges.map(e => e.id).sort().join('|');
  if (key !== lastViewKey) {
    const ids = new Set([...currentView.nodes, ...currentView.edges].map(n => n.id));
    cy.batch(() => {
      cy.elements().filter(e => !ids.has(e.id())).remove();
      for (const n of currentView.nodes) if (!cy.getElementById(n.id).length) cy.add({ data: { id: n.id, type: n.type, label: label(n, state.lang), color: NODE_COLORS[n.type] } });
      for (const e of currentView.edges) if (!cy.getElementById(e.id).length) cy.add({ data: { ...e, label: t(e.type) } });
    });
    cy.layout({ name: currentView.nodes.length > 12 ? 'cose' : 'concentric', animate: false, padding: 40,
      nodeDimensionsIncludeLabels: true, nodeRepulsion: () => 8500, idealEdgeLength: () => 100,
      minNodeSpacing: 35, spacingFactor: 1.2,
      concentric: n => n.id() === state.root ? 10 : 1, levelWidth: () => 1 }).run();
    lastViewKey = key;
  }
  cy.nodes().forEach(n => n.data('label', label(index.nodes.get(n.id()), state.lang)));
  highlightSelection();
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
  if (push && !tour?.active) history.pushState(null, '', url);
}
function snapshotTour() {
  return { state: { ...state, expanded: new Map(state.expanded) }, browser: { ...browser }, activeTab,
    resultLimit, openSections: [...$('detail').querySelectorAll('details')].map(n => n.open),
    panelScroll: ['record-panel', 'connections', 'browser-panel', 'browser-filters'].map(id => [id, $(id).scrollTop]),
    searchOpen: $('search-panel').open, filtersOpen: $('browser-filters').open,
    search: $('search').value, type: $('node-type').value, institution: $('institution').value,
    hidden: $('explorer').classList.contains('panel-hidden'), expanded: expandedMode,
    highlight: $('highlight').checked, url: location.href, scroll: [scrollX, scrollY],
    positions: cy?.nodes().map(n => ({ id: n.id(), position: { ...n.position() } })),
    zoom: cy?.zoom(), pan: cy ? { ...cy.pan() } : null };
}
async function restoreTour(saved) {
  state = saved.state; Object.assign(browser, saved.browser);
  resultLimit = saved.resultLimit;
  $('search').value = saved.search; $('node-type').value = saved.type;
  $('institution').value = saved.institution; $('highlight').checked = saved.highlight;
  syncBrowserControls(); setTab(saved.activeTab); render();
  if (state.edge) await evidenceReady;
  else if (index.nodes.get(state.selected)?.attribute_url) await attributeReady;
  $('detail').querySelectorAll('details').forEach((n, i) => { n.open = saved.openSections[i] || false; });
  $('search-panel').open = saved.searchOpen; $('browser-filters').open = saved.filtersOpen;
  $('explorer').classList.toggle('panel-hidden', saved.hidden); $('inspector').inert = saved.hidden;
  $('toggle-panel').textContent = t(saved.hidden ? 'showPanel' : 'hidePanel'); $('toggle-panel').setAttribute('aria-expanded', String(!saved.hidden));
  if (expandedMode !== saved.expanded) await toggleFullscreen();
  await new Promise(requestAnimationFrame);
  if (cy && saved.positions) { cy.nodes().positions(n => saved.positions.find(p => p.id === n.id())?.position || n.position()); cy.zoom(saved.zoom); cy.pan(saved.pan); }
  for (const [id, top] of saved.panelScroll) $(id).scrollTop = top;
  history.replaceState(null, '', saved.url);
  window.scrollTo(...saved.scroll);
}
async function prepareTour(step) {
  if (expandedMode) await toggleFullscreen();
  $('search-panel').open = step.setup === 'search' || step.setup === 'results';
  if (step.setup === 'search') {
    $('search').value = ''; $('node-type').value = ''; $('institution').value = ''; renderSearch(); return;
  }
  if (step.setup === 'results') {
    $('search').value = ''; $('node-type').value = 'pib'; $('institution').value = ''; renderSearch(); return;
  }
  if (step.setup === 'attributes' || step.setup === 'expand') {
    const id = step.setup === 'attributes' ? 'pib:standard:PSU 905' : EXAMPLES[4].id;
    state = exampleState(index, id, state.lang); state.expanded = new Map([[id, PAGE]]); browser.anchor = id;
  }
  if (step.setup === 'evidence') {
    state = exampleState(index, EXAMPLES[0].id, state.lang);
    state.edge = connections(index, state.root).find(e => e.type === 'references').id;
  } else state.edge = '';
  if (!state.root || !index.nodes.has(state.selected)) state = exampleState(index, EXAMPLES[0].id, state.lang);
  state.relation = ''; browser.query = ''; browser.type = ''; browser.page = 1;
  browser.anchor = state.selected; browser.scope = step.setup === 'all' ? 'all' : 'connected';
  syncBrowserControls(); setTab(['browse', 'all'].includes(step.setup) ? 'browser' : 'detail'); render();
  $('browser-filters').open = true;
  if (step.setup === 'evidence') await evidenceReady;
  if (step.setup === 'attributes') await attributeReady;
}
function selectNode(id, start = false, keepBrowser = false) {
  if (!index.nodes.has(id)) return;
  if (keepBrowser && browser.scope === 'connected' && !currentView.nodes.some(n => n.id === id)) {
    const offset = connections(index, browser.anchor, state.relation).findIndex(e => e.source === id || e.target === id);
    if (offset >= 0 && offset < MAX_NODES - 1) {
      state.expanded.set(browser.anchor, Math.max(state.expanded.get(browser.anchor) || PAGE, offset + 1));
      currentView = neighborhood(index, state);
    }
  }
  if (start || !currentView.nodes.some(n => n.id === id)) { state.root = id; state.expanded = new Map(); }
  $('search-panel').open = false;
  state.selected = id; state.edge = '';
  if (!keepBrowser) { browser.anchor = id; browser.page = 1; browser.query = ''; browser.type = ''; syncBrowserControls(); }
  setTab('detail');
  if (!state.expanded.has(id)) state.expanded.set(id, PAGE);
  render(true);
  $('inspector-heading').tabIndex = -1;
  $('inspector-heading').focus({ preventScroll: true });
}
function selectEdge(id) {
  state.edge = id; setTab('detail'); render(true);
  $('inspector-heading').tabIndex = -1;
  $('inspector-heading').focus({ preventScroll: true });
  $('inspector').scrollIntoView({ block: 'nearest' });
}
function applyExpanded(enabled) {
  const workspace = $('explorer');
  if (enabled && !expandedMode) {
    previousFocus = $('fullscreen');
    document.querySelectorAll('body > gcds-header, body > .skip-link, body > footer, #main-content > :not(#explorer)').forEach(node => {
      inertElements.set(node, node.inert); node.inert = true;
    });
  }
  expandedMode = enabled;
  workspace.classList.toggle('is-expanded', enabled);
  document.body.classList.toggle('graph-expanded', enabled);
  workspace.setAttribute('role', enabled ? 'dialog' : 'region');
  if (enabled) workspace.setAttribute('aria-modal', 'true');
  else {
    workspace.removeAttribute('aria-modal');
    for (const [node, inert] of inertElements) node.inert = inert;
    inertElements.clear();
  }
  $('fullscreen').textContent = t(enabled ? 'exitFullscreen' : 'fullscreen');
  $('fullscreen').setAttribute('aria-pressed', String(enabled));
  if (enabled) $('fullscreen').focus({ preventScroll: true });
  else previousFocus?.focus({ preventScroll: true });
  requestAnimationFrame(() => { cy?.resize(); cy?.fit(undefined, 40); });
}
async function toggleFullscreen() {
  const workspace = $('explorer');
  $('fullscreen').disabled = true;
  try {
    if (expandedMode) {
      if (document.fullscreenElement === workspace) await document.exitFullscreen();
      nativeMode = false; applyExpanded(false);
    } else {
      applyExpanded(true);
      try {
        if (typeof workspace.requestFullscreen === 'function') {
          await workspace.requestFullscreen(); nativeMode = true;
        }
      } catch {
        // Keep the equally navigable, viewport-filling workspace when native
        // fullscreen is unavailable (including embedded or mobile browsers).
        nativeMode = false;
      }
    }
  } finally {
    $('fullscreen').disabled = false;
    if (expandedMode) $('fullscreen').focus({ preventScroll: true });
    else previousFocus?.focus({ preventScroll: true });
  }
}
function initializeWorkspace() {
  $('browser-filters').open = !matchMedia('(max-width: 700px)').matches;
  $('fullscreen').addEventListener('click', toggleFullscreen);
  document.addEventListener('fullscreenchange', () => {
    if (document.fullscreenElement === $('explorer')) { nativeMode = true; applyExpanded(true); }
    else if (nativeMode) { nativeMode = false; applyExpanded(false); }
  });
  $('explorer').addEventListener('keydown', event => {
    if (!expandedMode) return;
    if (event.key === 'Escape') { event.preventDefault(); toggleFullscreen(); }
    if (event.key === 'Tab') {
      const elements = [...$('explorer').querySelectorAll('button, input, select, a[href], summary, [tabindex="0"]')]
        .filter(n => !n.disabled && n.tabIndex >= 0 && n.getClientRects().length);
      const first = elements[0], last = elements.at(-1);
      if (event.shiftKey && (document.activeElement === first || document.activeElement === $('inspector-heading'))) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
  });
  $('toggle-panel').addEventListener('click', () => {
    const hidden = $('explorer').classList.toggle('panel-hidden'); $('inspector').inert = hidden;
    $('toggle-panel').setAttribute('aria-expanded', String(!hidden));
    $('toggle-panel').textContent = t(hidden ? 'showPanel' : 'hidePanel');
    requestAnimationFrame(() => cy?.resize());
  });
  for (const name of ['detail', 'browser']) {
    $('tab-' + name).addEventListener('click', () => setTab(name));
    $('tab-' + name).addEventListener('keydown', event => {
      if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
        event.preventDefault(); setTab(event.key === 'Home' ? 'detail' : event.key === 'End' ? 'browser' : activeTab === 'detail' ? 'browser' : 'detail', true);
      }
    });
  }
  for (const [id, key] of [['browser-scope', 'scope'], ['browser-query', 'query'], ['browser-type', 'type'], ['browser-sort', 'sort'], ['records-per-page', 'size']]) {
    $(id).addEventListener(id === 'browser-query' ? 'input' : 'change', () => {
      browser[key] = $(id).value; browser.page = 1; renderConnections(); $('connections').scrollTop = 0;
    });
  }
  for (const [id, change] of [['previous-page', -1], ['next-page', 1]]) $(id).addEventListener('click', () => {
    browser.page += change; renderConnections(); $('connections').scrollTop = 0;
  });
  for (const [id, change] of [['previous-record', -1], ['next-record', 1]]) $(id).addEventListener('click', () => {
    const position = recordEntries.findIndex(r => r.node.id === state.selected);
    const next = Math.max(0, position + change);
    if (recordEntries[next]) {
      browser.page = Math.floor(next / Number(browser.size)) + 1;
      selectNode(recordEntries[next].node.id, false, true); $('record-panel').scrollTop = 0;
    }
  });
  $('use-selected').addEventListener('click', () => showConnections());
  $('highlight').addEventListener('change', highlightSelection);
  new ResizeObserver(() => requestAnimationFrame(() => cy?.resize())).observe($('cy'));
  syncBrowserControls();
}
async function init() {
  // Localize the initial failure message even if the dataset is unavailable.
  try {
    const response = await fetch('data/graph.json');
    if (!response.ok) throw new Error('Graph HTTP ' + response.status);
    data = await response.json(); index = indexGraph(data); state = parseState(location.href, index);
    if (!state.root && !new URL(location.href).searchParams.has('node')) state = exampleState(index, EXAMPLES[0].id, state.lang);
    browser.anchor = state.selected;
    $('search-panel').open = !new URL(location.href).searchParams.has('node') || !index.nodes.has(state.root);
    if (typeof window.cytoscape === 'function') {
      cy = window.cytoscape({ container: $('cy'), elements: [], minZoom: .1, maxZoom: 3, wheelSensitivity: .2,
        style: [
          { selector: 'node', style: { 'background-color': 'data(color)', label: 'data(label)', color: '#26374a', 'font-size': 11,
            'text-wrap': 'ellipsis', 'text-max-width': 130, 'text-valign': 'bottom', 'text-margin-y': 7, width: 32, height: 32, 'border-color': '#26374a', 'border-width': 1 } },
          { selector: 'node[type="pia"]', style: { shape: 'diamond', width: 42, height: 42 } },
          { selector: 'node[type="institution"]', style: { shape: 'round-rectangle', width: 46 } },
          { selector: 'node[type="class"]', style: { shape: 'rectangle' } },
          { selector: 'node[type="category"]', style: { shape: 'tag' } },
          { selector: 'node[type="pib_type"]', style: { shape: 'pentagon' } },
          { selector: 'node[type="reference"]', style: { shape: 'hexagon', 'border-style': 'dashed' } },
          { selector: 'edge', style: { width: 1.5, 'line-color': '#7a8b9b', 'target-arrow-color': '#7a8b9b', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier' } },
          { selector: 'edge[resolution != "resolved"]', style: { 'line-style': 'dashed' } },
          { selector: 'edge[basis="derived"]', style: { 'line-style': 'dotted', 'line-color': '#a13d64', 'target-arrow-color': '#a13d64' } },
          { selector: 'edge.active', style: { 'line-color': '#087a82', 'target-arrow-color': '#087a82', width: 4 } },
          { selector: 'node.active', style: { 'border-width': 4, 'border-color': '#172b42', 'underlay-color': 'data(color)', 'underlay-opacity': .2, 'underlay-padding': 7 } },
          { selector: '.dimmed', style: { opacity: .15 } },
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
    initializeWorkspace();
    if (!index.nodes.has(state.selected)) { browser.scope = 'all'; syncBrowserControls(); setTab('browser'); }
    $('share').addEventListener('click', async () => {
      const url = stateURL(location.href, state).href;
      try { await navigator.clipboard.writeText(url); $('share-status').textContent = t('copied'); }
      catch { $('share-link').value = url; $('share-link').hidden = false; $('share-link').select(); $('share-status').textContent = t('copyFallback'); }
    });
    window.addEventListener('popstate', () => { state = parseState(location.href, index); browser.anchor = state.selected; browser.page = 1; render(); });
    render();
    tour = createTour({ lang: () => state.lang, prepare: prepareTour, snapshot: snapshotTour, restore: restoreTour });
    for (const id of ['tour-launch', 'workspace-tour']) { $(id).disabled = false; $(id).addEventListener('click', () => tour.start()); }
  } catch (error) {
    $('view-status').textContent = t('loadError'); $('view-status').setAttribute('role', 'alert');
    for (const id of ['search', 'node-type', 'institution']) $(id).disabled = true;
    $('explorer').querySelectorAll('button, input, select').forEach(node => { node.disabled = true; });
    console.error(error);
  }
}
init();
