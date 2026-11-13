// Ordered by task importance. Each stop names the controls it explains, including
// conditional controls revealed by prepare(). The highlighted area stays usable.
export const TOUR_STEPS = [
  ['examples', '#examples', 'search', 'Start exploring', 'Five paths into the evidence', 'Choose any of the five stories. Each opens real connected records; the counts describe direct links and represented institutions, not shared personal records.', 'Commencer', 'Cinq parcours dans les sources', 'Choisissez un des cinq parcours. Chacun ouvre de vrais documents liés; les comptes décrivent les liens directs et les institutions représentées, et non un partage de renseignements.'],
  ['find', '#search-heading', 'search', 'Start exploring', 'Reopen your starting points', 'Find a starting point opens or closes the examples and search controls. Return here whenever you want another starting point.', 'Commencer', 'Retrouver les points de départ', 'Trouver un point de départ ouvre ou ferme les exemples et la recherche. Revenez ici pour commencer un autre parcours.'],
  ['search', '#search', 'search', 'Start exploring', 'Search in either language', 'Search names, bank numbers and recorded aliases in English or French. Clear the search and both filters to return to the five examples.', 'Commencer', 'Chercher dans les deux langues', 'Cherchez des noms, numéros de fichier et alias en français ou en anglais. Effacez la recherche et les deux filtres pour retrouver les cinq exemples.'],
  ['header', 'gcds-header', 'search', 'Start exploring', 'Change language in the header', 'Use the header’s Français/English link to switch language while preserving your graph view. Its menus open the overview, institution and reference tables, privacy assessments and network explorer. On narrow screens, open the navigation menu first. Skip to main content bypasses the header.', 'Commencer', 'Changer de langue dans l’en-tête', 'Le lien Français/English de l’en-tête change la langue en conservant la vue. Les menus ouvrent aperçu, tableaux institutionnels et de référence, évaluations et explorateur. Sur petit écran, ouvrez d’abord le menu. Passer au contenu principal permet de sauter l’en-tête.'],
  ['node-type', '#node-type', 'search', 'Start exploring', 'Start from any kind of record', 'Choose banks, standard banks, classes, standard classes, assessments, institutions, personal-information categories or PIB types. Standard records remain distinct from institution-specific records.', 'Commencer', 'Choisir un type de document', 'Choisissez fichiers, fichiers ordinaires, catégories de documents, catégories ordinaires, évaluations, institutions, catégories de renseignements personnels ou types de FRP.'],
  ['institution', '#institution', 'search', 'Start exploring', 'Narrow to an institution', 'This filter restricts search to records attributed to one institution. Government-wide standards and vocabulary nodes have no institution owner, so clear it to find them.', 'Commencer', 'Préciser une institution', 'Ce filtre limite la recherche aux documents attribués à une institution. Les normes pangouvernementales et vocabulaires n’ont pas d’institution propriétaire : effacez le filtre pour les trouver.'],
  ['results', '#results', 'results', 'Start exploring', 'Open a result', 'Select a search result to open its record and connections. More results loads additional matches; it does not add them all to the diagram.', 'Commencer', 'Ouvrir un résultat', 'Sélectionnez un résultat pour ouvrir son document et ses liens. Plus de résultats affiche d’autres correspondances sans toutes les ajouter au graphique.'],
  ['diagram', '#cy', 'detail', 'Explore and inspect', 'Follow a node, then a line', 'Select a node to expand its neighbourhood and inspect it. Select a line to inspect that relationship. Drag the background to pan, scroll or pinch to zoom, and drag nodes to arrange them. The record browser also supports keyboard navigation.', 'Explorer et examiner', 'Suivre un nœud, puis une ligne', 'Sélectionnez un nœud pour explorer son voisinage, ou une ligne pour examiner sa relation. Déplacez le fond pour naviguer, faites défiler ou pincez pour zoomer et déplacez les nœuds. La liste est accessible au clavier.'],
  ['legend', '.graph-legend', 'detail', 'Explore and inspect', 'Read the types and evidence limits', 'Labels and colours identify record types. Dashed lines lead to unresolved references. Dotted category links are derived estimates, not official category assignments. A citation does not establish that an assessment covers an entire bank. In mobile fullscreen, swipe the legend to see more types.', 'Explorer et examiner', 'Lire les types et les limites', 'Les libellés et couleurs identifient les types. Les pointillés mènent aux références non résolues; les liens de catégorie en petits points sont des estimations. Une citation ne garantit pas la couverture de tout un fichier. En plein écran mobile, balayez la légende pour voir les autres types.'],
  ['detail', '#detail .record-card', 'detail', 'Explore and inspect', 'Read the selected record', 'The Record tab shows the title, identifier, standard or institution-specific scope, institution, description and direct connection counts. Counts follow the relationship filter and may exceed the visible drawing.', 'Explorer et examiner', 'Lire le document sélectionné', 'L’onglet Document affiche titre, identifiant, portée ordinaire ou institutionnelle, institution, description et comptes de liens directs. Les comptes suivent le filtre de relation et peuvent dépasser le dessin visible.'],
  ['attributes', '.record-attributes', 'attributes', 'Explore and inspect', 'Open the record attributes', 'Expand the available fields to read purpose, people covered, consistent uses, retention and disposal, or document types. Open full record shows the complete table entry. Use Retry if attributes cannot load. Missing attributes are not invented.', 'Explorer et examiner', 'Ouvrir les attributs', 'Dépliez les champs disponibles : fin, personnes visées, usages compatibles, conservation et élimination, ou types de documents. Ouvrir le document complet affiche l’entrée complète. Réessayer relance le chargement en cas d’échec. Les attributs absents ne sont pas inventés.'],
  ['chips', '.type-chips', 'detail', 'Explore and inspect', 'Navigate by connected type', 'Each coloured count is clickable. It opens the browser with only that type of connected record. The institution name on a record also opens its institution node.', 'Explorer et examiner', 'Naviguer par type lié', 'Chaque compte coloré ouvre la liste filtrée sur ce type de document lié. Le nom de l’institution ouvre également son nœud.'],
  ['actions', '.record-actions', 'detail', 'Explore and inspect', 'Continue or begin a fresh view', 'Connected records opens the selected record’s neighbours. Start here begins a new graph rooted at this record. Open full record opens the underlying table entry or assessment reader.', 'Explorer et examiner', 'Continuer ou recommencer', 'Documents liés ouvre les voisins du document. Commencer ici crée un nouveau graphique à partir de ce document. Ouvrir le document complet mène au tableau ou au lecteur d’évaluation.'],
  ['relation', '#relation', 'detail', 'Explore and inspect', 'Choose the relationship to follow', 'Filter references, related classes, institution attribution, PIB type or derived category matches. This changes the diagram, connected-record list and summary counts. A category match includes its rule and confidence in the evidence panel.', 'Explorer et examiner', 'Choisir la relation à suivre', 'Filtrez références, catégories connexes, attribution institutionnelle, types de FRP ou correspondances de catégorie dérivées. Le graphique, la liste et les comptes suivent ce filtre. Les preuves d’une correspondance indiquent sa règle et sa confiance.'],
  ['tabs', '.inspector-tabs', 'browse', 'Browse records', 'Switch between details and the list', 'Record opens the selected record or relationship. Browse records opens a searchable, paginated list. Use Left/Right arrow keys to switch tabs.', 'Parcourir les documents', 'Passer du document à la liste', 'Document ouvre le document ou la relation sélectionnée. Parcourir les documents ouvre une liste avec recherche et pagination. Les flèches gauche et droite changent d’onglet.'],
  ['browser-filters', '#browser-filters summary', 'browse', 'Browse records', 'Show or hide list filters', 'Find and sort records collapses the browser controls to make room for the list. On small screens these controls begin collapsed.', 'Parcourir les documents', 'Afficher ou masquer les filtres', 'Trouver et trier les documents replie les commandes pour agrandir la liste. Sur petit écran, elles sont repliées au départ.'],
  ['scope', '#browser-scope', 'browse', 'Browse records', 'Connections or the whole inventory', 'Choose Connected records for the fixed anchor shown below, or All collected records for the complete inventory. Browsing is independent of the 250-node drawing limit.', 'Parcourir les documents', 'Liens ou inventaire complet', 'Choisissez Documents liés pour le point d’ancrage indiqué, ou Tous les documents recueillis pour l’inventaire complet. La liste est indépendante de la limite de 250 nœuds.'],
  ['anchor', '#use-selected', 'browse', 'Browse records', 'Move the connection anchor deliberately', 'Connections of selected record makes the current selection the new list anchor. Opening successive list records otherwise keeps the same anchor, so the list does not unexpectedly change.', 'Parcourir les documents', 'Déplacer le point d’ancrage', 'Liens du document sélectionné change le point d’ancrage de la liste. Ouvrir plusieurs documents conserve autrement cet ancrage pour éviter des changements inattendus.'],
  ['browser-query', '#browser-query', 'browse', 'Browse records', 'Search within this list', 'Filter the current list by bilingual names, identifiers and aliases. This only changes the list; it preserves the diagram and its positions.', 'Parcourir les documents', 'Chercher dans cette liste', 'Filtrez la liste par noms bilingues, identifiants et alias. Le graphique et ses positions restent en place.'],
  ['browser-type', '#browser-type', 'browse', 'Browse records', 'Filter the list by record type', 'Choose a type, including standard banks, standard classes, categories and PIB types. Combine it with the text filter or clear both to see the full list again.', 'Parcourir les documents', 'Filtrer la liste par type', 'Choisissez un type, y compris fichiers ordinaires, catégories ordinaires, catégories de renseignements et types de FRP. Combinez-le avec le texte ou effacez les filtres.'],
  ['sort', '#browser-sort', 'browse', 'Browse records', 'Discover highly connected records', 'Sort alphabetically or by Most connected. Connectivity counts observed direct relationships across the collected graph; it is not a privacy-risk or completeness score.', 'Parcourir les documents', 'Découvrir les documents très liés', 'Triez par nom ou par nombre de liens. Ce nombre mesure les relations directes du graphique recueilli, et non un risque pour la vie privée ou un niveau d’exhaustivité.'],
  ['list', '#connections', 'browse', 'Browse records', 'Open records or their evidence', 'Select a record title to open it. Inspect evidence opens the specific relationship to the anchor. Standard labels, derived labels and resolution status explain what each connection represents.', 'Parcourir les documents', 'Ouvrir documents et preuves', 'Sélectionnez un titre pour l’ouvrir. Consulter les preuves ouvre la relation précise avec le point d’ancrage. Les libellés indiquent normes, correspondances dérivées et état de résolution.'],
  ['pagination', '.record-pagination', 'all', 'Browse records', 'Page without moving the graph', 'Previous and Next page through the complete filtered list. The page and record counts show your position. Paging does not expand, move or reset the map.', 'Parcourir les documents', 'Changer de page sans déplacer le graphique', 'Précédent et Suivant parcourent la liste filtrée complète. Les comptes indiquent votre position. La pagination ne développe ni ne déplace le graphique.'],
  ['size', '#records-per-page', 'all', 'Browse records', 'Choose the list length', 'Show 8, 16 or 24 records per page. This changes list pagination, not the number of nodes drawn.', 'Parcourir les documents', 'Choisir la longueur de la liste', 'Affichez 8, 16 ou 24 documents par page. Ce choix change la pagination, pas le nombre de nœuds dessinés.'],
  ['record-navigation', '#record-navigation', 'detail', 'Browse records', 'Read successive records', 'Previous record and Next record follow the current filtered list. The fixed anchor stays unchanged until you explicitly choose Connections of selected record.', 'Parcourir les documents', 'Lire les documents successifs', 'Document précédent et Document suivant suivent la liste filtrée. Le point d’ancrage demeure jusqu’au choix explicite Liens du document sélectionné.'],
  ['evidence', '.graph-evidence', 'evidence', 'Verify and adjust', 'Inspect the source behind a relationship', 'Read the source excerpt, then open Original source or Repository evidence. The endpoint buttons return to either record. For derived category matches, inspect the matching text, rule and confidence.', 'Vérifier et ajuster', 'Examiner la source d’une relation', 'Lisez l’extrait, puis ouvrez Source originale ou Preuve dans le dépôt. Les boutons des extrémités ouvrent les deux documents. Les correspondances dérivées montrent texte, règle et confiance.'],
  ['audit', '.evidence-audit', 'evidence', 'Verify and adjust', 'Check provenance details', 'Expand Collection details for extraction method, observed date and checksum where available. Repository links include source line numbers when the collection records them.', 'Vérifier et ajuster', 'Vérifier la provenance', 'Dépliez les détails pour consulter méthode d’extraction, date observée et somme de contrôle disponibles. Les liens du dépôt indiquent les lignes lorsque la collecte les fournit.'],
  ['sources', '.record-sources', 'detail', 'Verify and adjust', 'Open the record’s sources', 'Expand Sources and collection details for original English/French sources, repository evidence, retrieval status and collection date where available. Source text retains its original language.', 'Vérifier et ajuster', 'Ouvrir les sources du document', 'Dépliez les sources pour consulter les pages anglaises et françaises, preuves du dépôt, états de récupération et dates disponibles. Le texte des sources conserve sa langue.'],
  ['expand', '#expand', 'expand', 'Verify and adjust', 'Reveal more connections', 'Add more connections to graph adds another batch of 25 neighbours for the selected node. The map is limited to 250 nodes; start a new view at a record to continue beyond that bound.', 'Vérifier et ajuster', 'Afficher davantage de liens', 'Ajouter des liens au graphique ajoute 25 voisins au document sélectionné. Le dessin est limité à 250 nœuds; commencez une nouvelle vue depuis un document pour poursuivre.'],
  ['fit', '#fit', 'detail', 'Verify and adjust', 'Bring the drawing back into view', 'Fit graph adjusts the viewport to include the visible nodes. It does not change the selected record or add connections.', 'Vérifier et ajuster', 'Revoir le dessin entier', 'Ajuster le graphique cadre les nœuds visibles sans changer le document sélectionné ni ajouter de liens.'],
  ['reset', '#reset', 'detail', 'Verify and adjust', 'Reset around the selection', 'Reset to selected node starts a fresh neighbourhood at the current selection and clears the previous expansion path.', 'Vérifier et ajuster', 'Recentrer sur la sélection', 'Recentrer sur le nœud sélectionné crée un nouveau voisinage à partir de la sélection et efface l’ancien parcours.'],
  ['highlight', '.highlight-control', 'detail', 'Verify and adjust', 'Control visual emphasis', 'Highlight direct connections dims unrelated visible elements. Turn it off to see the full view at equal emphasis; counts and relationships do not change.', 'Vérifier et ajuster', 'Régler la mise en évidence', 'La mise en évidence atténue les éléments non directement liés. Désactivez-la pour tout voir au même niveau; comptes et relations ne changent pas.'],
  ['panel', '#toggle-panel', 'detail', 'Share and more', 'Give the graph more space', 'Hide records temporarily hides the record panel. Show records brings it back without changing the selected record or list.', 'Partager et autres outils', 'Agrandir le graphique', 'Masquer les documents cache temporairement le panneau. Afficher les documents le rétablit sans changer la sélection ni la liste.'],
  ['fullscreen', '#fullscreen', 'detail', 'Share and more', 'Explore in full screen', 'Full screen keeps the graph, browser and controls together. Exit full screen or Escape returns to the page. The header language switch is available after leaving full screen; there is no duplicate switch.', 'Partager et autres outils', 'Explorer en plein écran', 'Le plein écran réunit graphique, liste et commandes. Quitter le plein écran ou Échap revient à la page. Le sélecteur de langue de l’en-tête redevient accessible; il n’y a pas de doublon.'],
  ['share', '#share', 'detail', 'Share and more', 'Share the evidence path', 'Copy view link preserves the root, selected record or relationship, expanded connections, relationship filter and language. If copying is unavailable, copy the displayed URL field. Browser Back/Forward revisits views. List filters, positions and zoom are not saved.', 'Partager et autres outils', 'Partager le parcours', 'Copier le lien conserve point de départ, sélection, relation, développements, filtre de relation et langue. Si la copie échoue, copiez le champ affiché. Précédent/Suivant du navigateur retrouve les vues. Les filtres de liste, positions et zoom ne sont pas sauvegardés.'],
  ['footer', '#graph-footer', 'search', 'Share and more', 'Download the data or read the method', 'The footer opens the overview and assessments, downloads the graph JSON, and explains graph methodology and evidence limits. Reopen this tour anytime; every stop is available from its step menu. Your earlier view is restored when you finish or exit.', 'Partager et autres outils', 'Télécharger les données ou lire la méthode', 'Le pied de page ouvre aperçu et évaluations, télécharge le graphique JSON et décrit méthode et limites. Relancez la visite à tout moment et choisissez une étape dans son menu. Votre vue précédente est rétablie à la fin ou à la sortie.']
].map(([id, target, setup, chapter_en, title_en, text_en, chapter_fr, title_fr, text_fr]) =>
  ({ id, target, setup, chapter_en, title_en, text_en, chapter_fr, title_fr, text_fr }));

export function createTour({ lang, prepare, snapshot, restore }) {
  const host = document.createElement('div'); host.id = 'graph-tour'; host.hidden = true;
  host.innerHTML = `<div class="tour-spotlight" aria-hidden="true"></div><section class="tour-card" role="dialog" aria-modal="false" aria-labelledby="tour-title" aria-describedby="tour-text" tabindex="-1"><div class="tour-top"><span id="tour-chapter"></span><button id="tour-close" type="button">×</button></div><p id="tour-progress" role="status" aria-live="polite"></p><h2 id="tour-title"></h2><p id="tour-text"></p><label for="tour-step" id="tour-step-label"></label><select id="tour-step"></select><div class="tour-buttons"><button id="tour-restart" type="button"></button><button id="tour-back" type="button"></button><button id="tour-next" type="button"></button></div></section>`;
  document.body.append(host);
  const $ = id => host.querySelector('#' + id), card = host.querySelector('.tour-card'), spot = host.querySelector('.tour-spotlight');
  let active = false, current = 0, target, saved, returnFocus, token = 0;
  const fr = () => lang() === 'fr';
  function position() {
    if (!active || !target?.isConnected) return;
    const r = target.getBoundingClientRect(), w = innerWidth, h = innerHeight;
    const left = Math.max(4, Math.min(w - 8, r.left - 5)), top = Math.max(4, Math.min(h - 8, r.top - 5));
    const right = Math.max(left + 4, Math.min(w - 4, r.right + 5)), bottom = Math.max(top + 4, Math.min(h - 4, r.bottom + 5));
    Object.assign(spot.style, { left: left + 'px', top: top + 'px', width: right - left + 'px', height: bottom - top + 'px' });
    const cw = card.offsetWidth, ch = card.offsetHeight;
    let x = right + 16, y = top;
    if (w - right < cw + 28) x = left >= cw + 24 ? left - cw - 16 : Math.max(12, w - cw - 12);
    if (x < right && x + cw > left) y = h - bottom >= ch + 24 ? bottom + 12 : top >= ch + 24 ? top - ch - 12 : h - ch - 12;
    Object.assign(card.style, { left: Math.max(8, Math.min(w - cw - 8, x)) + 'px', top: Math.max(8, Math.min(h - ch - 8, y)) + 'px' });
  }
  const targetObserver = new ResizeObserver(position);
  function languageLink(root = document.querySelector('gcds-header')) {
    if (!root) return null;
    if (root.shadowRoot) {
      const found = languageLink(root.shadowRoot);
      if (found) return found;
    }
    const alternate = fr() ? 'en' : 'fr';
    for (const a of root.querySelectorAll('a[href]')) {
      if (new URL(a.href, location.href).searchParams.get('lang') === alternate) return a;
    }
    for (const element of root.querySelectorAll('*')) {
      const found = element.shadowRoot && languageLink(element.shadowRoot);
      if (found) return found;
    }
    return null;
  }
  async function go(i) {
    const request = ++token; current = Math.max(0, Math.min(TOUR_STEPS.length - 1, i));
    card.setAttribute('aria-busy', 'true');
    const step = TOUR_STEPS[current];
    $('tour-chapter').textContent = step['chapter_' + lang()];
    $('tour-title').textContent = step['title_' + lang()]; $('tour-text').textContent = step['text_' + lang()];
    $('tour-progress').textContent = fr() ? `Étape ${current + 1} sur ${TOUR_STEPS.length}` : `Step ${current + 1} of ${TOUR_STEPS.length}`;
    $('tour-step-label').textContent = fr() ? 'Aller à une étape' : 'Jump to a step';
    $('tour-close').setAttribute('aria-label', fr() ? 'Quitter la visite' : 'Exit tour');
    $('tour-restart').textContent = fr() ? 'Recommencer' : 'Restart';
    $('tour-back').textContent = fr() ? 'Précédent' : 'Back'; $('tour-back').disabled = current === 0;
    $('tour-next').textContent = current === TOUR_STEPS.length - 1 ? (fr() ? 'Terminer' : 'Finish') : (fr() ? 'Suivant' : 'Next');
    $('tour-step').replaceChildren(...TOUR_STEPS.map((s, n) => { const o = document.createElement('option'); o.value = n; o.textContent = `${n + 1}. ${s['chapter_' + lang()]} · ${s['title_' + lang()]}`; return o; }));
    $('tour-step').value = current;
    await prepare(step);
    if (!active || request !== token) return;
    target = step.id === 'header' ? languageLink() : document.querySelector(step.target);
    targetObserver.disconnect();
    if (target) targetObserver.observe(target);
    targetObserver.observe(card);
    host.dataset.step = step.id;
    card.setAttribute('aria-busy', 'false');
    target?.scrollIntoView({ block: innerWidth < 700 ? 'start' : 'center', inline: 'nearest', behavior: 'instant' });
    if (innerWidth < 700 && target) window.scrollBy(0, -30);
    requestAnimationFrame(() => {
      if (!active || request !== token) return;
      position();
      $('tour-next').focus({ preventScroll: true });
    });
  }
  async function close() {
    if (!active) return;
    active = false; ++token; host.hidden = true; targetObserver.disconnect();
    await restore(saved);
    (returnFocus?.isConnected ? returnFocus : document.getElementById('tour-launch')).focus({ preventScroll: true });
  }
  $('tour-close').onclick = close;
  $('tour-next').onclick = () => current === TOUR_STEPS.length - 1 ? close() : go(current + 1);
  $('tour-back').onclick = () => go(current - 1);
  $('tour-restart').onclick = () => go(0);
  $('tour-step').onchange = () => go(Number($('tour-step').value));
  window.addEventListener('keydown', e => {
    if (!active) return;
    if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); close(); }
    if (['ArrowRight', 'ArrowLeft'].includes(e.key) && !['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) {
      e.preventDefault(); go(current + (e.key === 'ArrowRight' ? 1 : -1));
    }
  }, true);
  document.addEventListener('fullscreenchange', () => { (document.fullscreenElement || document.body).append(host); requestAnimationFrame(position); });
  window.addEventListener('resize', position);
  document.addEventListener('scroll', position, { capture: true, passive: true });
  // Nonmodal: keep the highlighted feature clickable and keyboard-accessible.
  return { get active() { return active; }, async start() {
    if (active) return;
    returnFocus = document.activeElement; saved = snapshot(); active = true; host.hidden = false;
    (document.fullscreenElement || document.body).append(host);
    await go(0);
  }, close };
}
