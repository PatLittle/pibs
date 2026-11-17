// External AIA records live in memory only. Never added to the static graph assets.
export const fold = value => String(value ?? '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const present = value => typeof value === 'string' && value.trim() && !/^(n\/?a|none|null|unknown|not applicable)$/i.test(value.trim());
const key = value => String(value || '').toUpperCase().replace(/\bPOU\b/g, 'PSU').replace(/\bPOE\b/g, 'PSE').replace(/[^A-Z0-9]/g, '');
const canonicalURL = value => { try { const u = new URL(value); return ['http:', 'https:'].includes(u.protocol) ? u.origin + decodeURI(u.pathname).replace(/\/$/, '') : ''; } catch { return ''; } };
export function parseJSONL(text) {
  const seen = new Set();
  return text.split(/\r?\n/).filter(line => line.trim()).map((line, i) => {
    const row = JSON.parse(line);
    if (!row || typeof row.data !== 'object' || !row.data || Array.isArray(row.data)) throw new Error(`Invalid AIA record on line ${i + 1}`);
    // A UUID package key survives title, score, and source-resource updates.
    if (!/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(row.package_id || '')) throw new Error(`Missing AIA package UUID on line ${i + 1}`);
    row.package_id = row.package_id.toLowerCase();
    if (seen.has(row.package_id)) throw new Error('Duplicate AIA package UUID: ' + row.package_id);
    seen.add(row.package_id); return row;
  });
}
export function organizationMatch(row, nodes) {
  const names = [row.organization_en, row.organization_fr].flatMap(v => String(v || '').split('|')).map(fold).filter(Boolean);
  const matches = nodes.filter(n => n.type === 'institution' && [n.label_en, n.label_fr, ...(n.aliases || [])].some(v => names.includes(fold(v))));
  return { institution_id: matches.length === 1 ? matches[0].institution_id : null,
    resolution: matches.length === 1 ? 'resolved' : matches.length ? 'ambiguous' : 'unresolved', candidates: matches.map(n => n.id) };
}
export async function officialIdentity(nameEN, nameFR, institution) {
  if (!present(nameEN) && !present(nameFR)) return null;
  const identity = JSON.stringify([institution, fold(nameEN || nameFR)]);
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(identity)))].map(v => v.toString(16).padStart(2, '0')).join('').slice(0, 24);
  return { u_id: 'aia-official-' + hash, name_en: String(nameEN || '').trim(), name_fr: String(nameFR || '').trim() };
}
function referenceMatches(mention, kind, institution, nodes) {
  const normalized = key(mention);
  let matches = nodes.filter(n => n.type === kind && [n.identifier, ...(n.aliases || [])].filter(Boolean).some(v => key(v) === normalized));
  if (kind === 'pib' && /^(PSU|PSE)\d+$/.test(normalized)) matches = matches.filter(n => n.scope === 'standard');
  else if (kind === 'class' && /^(PRN|NDP)\d+$/.test(normalized)) matches = nodes.filter(n => n.type === 'class' && n.scope === 'standard' && key(n.identifier) === normalized.slice(3));
  else if (/^(PPU|PPE|PCU|PCE|PIB|FRP)\d+$/.test(normalized)) {
    matches = institution ? nodes.filter(n => n.type === kind && n.institution_id === institution &&
      [n.identifier, ...(n.aliases || [])].filter(Boolean).some(v => key(v).endsWith(normalized))) : [];
  }
  return [...new Map(matches.map(n => [n.id, n])).values()];
}
export function explicitReferences(row, institution, nodes) {
  const refs = new Map();
  const add = (kind, mention, field, text, language, matches) => {
    const id = kind + ':' + (matches.length ? matches.map(n => n.id).sort().join('|') : key(mention));
    const ref = refs.get(id) || { kind, mention, candidates: matches.map(n => n.id), resolution: matches.length === 1 ? 'resolved' : matches.length ? 'ambiguous' : 'unresolved', evidence: [] };
    ref.evidence.push({ field, excerpt: text, mention, language, source_url: row.dataset_url, method: kind === 'pia' ? 'explicit_pia_source_url' : 'explicit_record_identifier' });
    refs.set(id, ref);
  };
  for (const [parent, language] of [['data', 'source'], ['translationsOnResult', 'translation']]) {
    for (const [field, value] of Object.entries(row[parent] || {})) {
      if (typeof value !== 'string') continue;
      // Keep full explicit organization prefixes: cross-institution citations must
      // never be silently redirected to the AIA owner's similarly numbered bank.
      for (const m of value.matchAll(/\b(?:[A-Z]{2,8}\s+)?(?:PPU|PPE|PCU|PCE|PSU|PSE|POU|POE|PIB|FRP)[\s._:-]*\d{2,6}\b/g)) {
        let mention = m[0];
        // Generic labels are context, not institutional prefixes.
        mention = mention.replace(/^(?:PIB|FRP)\s+(?=(?:PPU|PPE|PSU|PSE)\b)/, '');
        add('pib', mention, parent + '.' + field, value, language, referenceMatches(mention, 'pib', institution, nodes));
      }
      for (const m of value.matchAll(/\b(?:PRN|NDP)[\s._:-]*\d{3}\b/g)) add('class', m[0], parent + '.' + field, value, language, referenceMatches(m[0], 'class', institution, nodes));
      for (const m of value.matchAll(/https?:\/\/[^\s<>"\])]+/g)) {
        const url = canonicalURL(m[0].replace(/[.,;]+$/, ''));
        const matches = nodes.filter(n => n.type === 'pia' && Object.values(n.sources || {}).some(v => canonicalURL(v) === url));
        if (matches.length) add('pia', m[0], parent + '.' + field, value, language, matches);
      }
    }
  }
  return [...refs.values()];
}
export function serviceMatch(value, institution, nodes) {
  const source_id = String(value ?? '').trim();
  if (!source_id || /^(?:n\/?a|none|not applicable|s\/?o|sans objet)$/i.test(source_id))
    return { source_id, resolution: 'missing', candidates: [] };
  const candidates = institution ? nodes.filter(n => n.type === 'service' && n.institution_id === institution && n.identifier === source_id).map(n => n.id) : [];
  return { source_id, resolution: candidates.length === 1 ? 'resolved' : candidates.length ? 'ambiguous' : 'unresolved', candidates };
}
export async function integrateAIA(graph, rows) {
  const originalNodes = [...graph.nodes];
  const records = [];
  const nodeMap = new Map(graph.nodes.map(n => [n.id, n]));
  const addNode = node => { if (!nodeMap.has(node.id)) { graph.nodes.push(node); nodeMap.set(node.id, node); } };
  const edgeMap = new Map();
  const addEdge = (source, target, type, evidence, resolution = 'resolved') => {
    const id = 'aia-edge:' + JSON.stringify([source, target, type]);
    if (!edgeMap.has(id)) edgeMap.set(id, { id, source, target, type, basis: 'documented', resolution, evidence: [] });
    edgeMap.get(id).evidence.push(...evidence);
  };
  for (const row of rows) {
    const organization = organizationMatch(row, originalNodes);
    const institution = organization.institution_id;
    const official = await officialIdentity(row.data.ADMresponsible, row.translationsOnResult?.ADMresponsible, institution || row.organization_en);
    const references = explicitReferences(row, institution, originalNodes);
    const service_match = serviceMatch(row.data.ServiceID, institution, originalNodes);
    if (service_match.resolution !== 'missing') references.push({ kind: 'service', mention: service_match.source_id, resolution: service_match.resolution, candidates: service_match.candidates,
      evidence: [{ field: 'data.ServiceID', mention: service_match.source_id, source_url: row.dataset_url, method: 'exact_service_id_with_unique_matched_institution' }] });
    const id = 'aia:' + row.package_id;
    const record = { ...row, id, institution_id: institution, organization_match: organization, official, service_match, references };
    records.push(record);
    const level = row.derived?.impact_level;
    addNode({ id, type: 'aia', identifier: row.package_id, institution_id: institution,
      label_en: row.title_en || row.data.projectDetailsTitle || '', label_fr: row.title_fr || '',
      description_en: row.data.projectDetailsDescription || '', description_fr: row.translationsOnResult?.projectDetailsDescription || '',
      aliases: [row.data.ServiceID, row.data.projectDetailsID, row.data.projectAIAnumber, row.data.projectDetailsTitle, row.translationsOnResult?.projectDetailsTitle].filter(Boolean),
      attributes: { service_id: service_match.source_id, service_match_resolution: service_match.resolution, survey_version: row.version || '', impact_level: level ?? '', senior_official: official ? (official.name_en || official.name_fr) : '', senior_official_uid: official?.u_id || '', project_id: row.data.projectDetailsID || '', provenance: row.source || '' },
      record_url: 'link-aia.html?record=' + encodeURIComponent(row.package_id), sources: { dataset: row.dataset_url }, external_source: true });
    if (institution) addEdge(id, 'institution:' + institution, 'listed_by', [{ field: 'organization_en / organization_fr', mention: row.organization_en, source_url: row.dataset_url, method: 'unique_exact_registry_name_alias' }]);
    if (official) {
      const oid = 'official:' + official.u_id;
      addNode({ id: oid, type: 'official', identifier: official.u_id, institution_id: institution, label_en: official.name_en, label_fr: official.name_fr,
        description_en: 'Responsible senior official named in an AIA. Identity is scoped to the organization; this does not establish current tenure.',
        description_fr: 'Cadre supérieur responsable nommé dans une EIA. Identité limitée à l’organisation; ne confirme pas le mandat actuel.',
        record_url: 'link-aia.html?official=' + encodeURIComponent(official.u_id), sources: { dataset: row.dataset_url }, external_source: true });
      addEdge(id, oid, 'responsible_official', [{ field: 'data.ADMresponsible', mention: official.name_en || official.name_fr, source_url: row.dataset_url, method: 'explicit_responsible_official' }]);
    }
    for (const ref of references) {
      const target = ref.resolution === 'resolved' ? ref.candidates[0] : 'aia-reference:' + row.package_id + '/' + encodeURIComponent(ref.kind + ':' + ref.mention);
      if (ref.resolution !== 'resolved') addNode({ id: target, type: 'reference', identifier: ref.mention, label_en: ref.mention, label_fr: ref.mention,
        institution_id: institution, reference_kind: ref.kind, resolution: ref.resolution, candidates: ref.candidates, sources: { dataset: row.dataset_url } });
      addEdge(id, target, ref.kind === 'service' ? 'references_service' : 'references', ref.evidence, ref.resolution);
    }
  }
  graph.edges.push(...edgeMap.values());
  graph.summary = { ...graph.summary, nodes: graph.nodes.length, edges: graph.edges.length,
    resolutions: Object.fromEntries([...new Set(graph.edges.map(e => e.resolution))].map(value => [value, graph.edges.filter(e => e.resolution === value).length])),
    node_types: Object.fromEntries([...new Set(graph.nodes.map(n => n.type))].map(type => [type, graph.nodes.filter(n => n.type === type).length])) };
  return { graph, records };
}
export async function loadAIA(graph, fetcher = fetch) {
  const configResponse = await fetcher('aia-source.json');
  if (!configResponse.ok) throw new Error('AIA configuration HTTP ' + configResponse.status);
  const config = await configResponse.json();
  const response = await fetcher(config.url, { signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error('AIA source HTTP ' + response.status);
  const rows = parseJSONL(await response.text());
  if (!rows.length) throw new Error('AIA source is empty');
  return { ...await integrateAIA(graph, rows), config, loaded_at: new Date().toISOString(), source_modified: response.headers.get('last-modified') };
}
