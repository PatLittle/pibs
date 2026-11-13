import { connections, PAGE } from './graph-model.mjs';

// Editorial starting points, using stable identities and live graph counts.
export const EXAMPLES = [
  { id: 'class:standard:931', title_en: 'Security connects institutions', title_fr: 'La sécurité relie les institutions',
    text_en: 'Follow one government-wide security class into banks and assessments from different institutions. A shared reference does not imply shared records.',
    text_fr: 'Suivez une catégorie de sécurité pangouvernementale vers les fichiers et évaluations de différentes institutions. Une référence commune ne signifie pas que les dossiers sont partagés.' },
  { id: 'class:standard:920', title_en: 'The common foundations of staffing', title_fr: 'Les fondements communs de la dotation',
    text_en: 'Recruitment and staffing connect institution-specific banks to assessments through the same standard class.',
    text_fr: 'Le recrutement et la dotation relient des fichiers institutionnels aux évaluations par une même catégorie ordinaire.' },
  { id: 'pib:standard:PSU 905', title_en: 'One network-monitoring bank, many assessments', title_fr: 'Un fichier de surveillance des réseaux, plusieurs évaluations',
    text_en: 'See how assessments from multiple institutions cite the standard Electronic Network Monitoring Logs bank.',
    text_fr: 'Découvrez comment des évaluations de plusieurs institutions citent le fichier ordinaire Journaux de contrôle des réseaux électroniques.' },
  { id: 'pia:ati-schedule-i-canada-revenue-agency/pia-96f2526f7582', title_en: 'Human resources analytics crosses record boundaries', title_fr: 'L’analytique des RH traverse les catégories de documents',
    text_en: 'One CRA assessment cites both banks and classes. Follow the connections to see the breadth of its documented references.',
    text_fr: 'Une évaluation de l’ARC cite des fichiers et des catégories de documents. Explorez l’étendue de ses références documentées.' },
  { id: 'pia:ati-schedule-i-office-of-the-privacy-commissioner/pia-01c195371b0b', title_en: 'A cloud project reaches across standard banks', title_fr: 'Un projet infonuagique touche plusieurs fichiers ordinaires',
    text_en: 'The Privacy Commissioner’s Microsoft Office 365 assessment connects many standard banks and includes references that still need resolution.',
    text_fr: 'L’évaluation de Microsoft Office 365 du Commissariat à la protection de la vie privée relie plusieurs fichiers ordinaires et comporte des références à résoudre.' }
];

export function exampleStats(index, id) {
  const edges = connections(index, id).filter(e => e.basis !== 'derived' && e.type !== 'has_type');
  const neighbors = new Set(edges.map(e => e.source === id ? e.target : e.source));
  const institutions = new Set([...neighbors].map(n => index.nodes.get(n).institution_id).filter(Boolean));
  return { records: neighbors.size, institutions: institutions.size };
}

export function exampleState(index, id, lang = 'en') {
  const expanded = new Map([[id, PAGE * 3]]), institutions = new Set();
  // Reveal a few institution paths as well as the starting node's immediate links.
  const peers = connections(index, id).map(e => index.nodes.get(e.source === id ? e.target : e.source))
    .filter(n => n.institution_id && n.type !== 'institution' && index.adjacency.get(n.id).length <= PAGE)
    .sort((a, b) => index.adjacency.get(a.id).length - index.adjacency.get(b.id).length || a.id.localeCompare(b.id));
  for (const n of peers) {
    if (institutions.has(n.institution_id)) continue;
    institutions.add(n.institution_id); expanded.set(n.id, PAGE);
    if (institutions.size === 3) break;
  }
  return { root: id, selected: id, edge: '', expanded, lang, relation: '' };
}
