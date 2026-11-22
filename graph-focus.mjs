import { connections, label, fold } from "./graph-model.mjs";
const KINDS = [
  "pia",
  "aia",
  "service",
  "program",
  "account_code",
  "infobase_program",
  "service_standard",
  "pib",
  "class",
  "official",
  "institution",
  "reference",
];
const CONTEXT_RELATIONS = new Set(["listed_by", "accounted_by", "shares_account_code"]);
export function focusGroups(index, id, lang = "en") {
  const groups = new Map();
  for (const edge of connections(index, id)) {
    const outgoing = edge.source === id,
      other = index.nodes.get(outgoing ? edge.target : edge.source);
    const key = [other.type, edge.type, outgoing ? "out" : "in"].join(":");
    if (!groups.has(key))
      groups.set(key, {
        key,
        type: other.type,
        relation: edge.type,
        outgoing,
        records: new Map(),
      });
    const group = groups.get(key);
    if (!group.records.has(other.id))
      group.records.set(other.id, { node: other, edges: [] });
    group.records.get(other.id).edges.push(edge);
  }
  return [...groups.values()]
    .map((g) => ({
      ...g,
      records: [...g.records.values()].sort(
        (a, b) =>
          label(a.node, lang).localeCompare(label(b.node, lang), lang) ||
          a.node.id.localeCompare(b.node.id),
      ),
    }))
    .sort(
      (a, b) =>
        KINDS.indexOf(a.type) - KINDS.indexOf(b.type) ||
        a.key.localeCompare(b.key),
    );
}
export function bridgePaths(index, id, limit = 4) {
  const direct = new Set([
      id,
      ...connections(index, id).map((e) =>
        e.source === id ? e.target : e.source,
      ),
    ]),
    candidates = new Map();
  for (const first of connections(index, id)) {
    if (CONTEXT_RELATIONS.has(first.type)) continue;
    const via = first.source === id ? first.target : first.source;
    if (index.nodes.get(via).type === "reference") continue;
    for (const second of connections(index, via)) {
      if (CONTEXT_RELATIONS.has(second.type)) continue;
      const target = second.source === via ? second.target : second.source,
        node = index.nodes.get(target);
      if (
        direct.has(target) ||
        node.type === "reference" ||
        first.resolution !== "resolved" ||
        second.resolution !== "resolved"
      )
        continue;
      const score =
        (first.type === "listed_by" ? 0 : 4) +
        (second.type === "listed_by" ? 0 : 4) +
        (node.institution_id &&
        index.nodes.get(id).institution_id &&
        node.institution_id !== index.nodes.get(id).institution_id
          ? 2
          : 0);
      const path = {
        source: id,
        via,
        target,
        edges: [first.id, second.id],
        score,
      };
      if (!candidates.has(target) || candidates.get(target).score < score)
        candidates.set(target, path);
    }
  }
  const ranked = [...candidates.values()].sort(
      (a, b) => b.score - a.score || a.target.localeCompare(b.target),
    ),
    result = [],
    types = new Set();
  for (const p of ranked)
    if (!types.has(index.nodes.get(p.target).type)) {
      result.push(p);
      types.add(index.nodes.get(p.target).type);
      if (result.length === limit) return result;
    }
  for (const p of ranked)
    if (!result.includes(p)) {
      result.push(p);
      if (result.length === limit) break;
    }
  return result;
}
export function validTrail(index, ids, focus) {
  const result = [];
  for (const id of ids.slice(-10)) {
    if (!index.nodes.has(id)) continue;
    if (
      result.length &&
      !connections(index, result.at(-1)).some(
        (e) => e.source === id || e.target === id,
      )
    )
      break;
    if (result.at(-1) !== id) result.push(id);
  }
  return result.at(-1) === focus ? result : [focus];
}
export function findRecords(index, query, lang = "en") {
  const standardPattern = /\bservice standards?\b|\bnormes? de service\b/g;
  const accountsPattern = /\b(?:public accounts|chart of accounts|comptes publics|plan comptable)\b/g;
  const infobasePattern = /\b(?:infobase du gc|(?:gc )?info ?base)\b/g;
  const queryText = fold(query);
  const requestedType = queryText.match(infobasePattern) ? "infobase_program" :
    queryText.match(accountsPattern) ? "account_code" :
    queryText.match(standardPattern) ? "service_standard" : "";
  const terms = queryText.replace(infobasePattern, "").replace(accountsPattern, "").replace(standardPattern, "").split(/\s+/).filter(Boolean),
    types = {
      aia: "aia",
      eia: "aia",
      service: "service",
      services: "service",
      program: "program",
      programme: "program",
      pia: "pia",
      efvp: "pia",
      pib: "pib",
      frp: "pib",
    };
  return [...index.nodes.values()]
    .filter((n) =>
      (!requestedType || n.type === requestedType) && terms.every((t) =>
        !requestedType && types[t]
          ? n.type === types[t]
          : fold(
              [n.identifier, n.label_en, n.label_fr, ...(n.aliases || [])].join(
                " ",
              ),
            ).includes(t),
      ),
    )
    .sort(
      (a, b) =>
        label(a, lang).localeCompare(label(b, lang), lang) ||
        a.id.localeCompare(b.id),
    );
}
