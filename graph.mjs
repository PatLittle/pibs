import { indexGraph, label, connections } from "./graph-model.mjs";
import {
  focusGroups,
  bridgePaths,
  validTrail,
  findRecords,
} from "./graph-focus.mjs";
import { nodeAttributes, attributeLabel } from "./graph-attributes.mjs";
import { loadAIA } from "./aia-data.mjs";
import { EXAMPLES } from "./graph-examples.mjs";
const $ = (id) => document.getElementById(id),
  el = (tag, value, cls) => {
    const n = document.createElement(tag);
    if (value != null) n.textContent = value;
    if (cls) n.className = cls;
    return n;
  };
const params = new URLSearchParams(location.search),
  lang = params.get("lang") === "fr" ? "fr" : "en",
  fr = lang === "fr";
const text = (en, french) => (fr ? french : en);
const words = {
  navPia: ["Privacy Assessments", "Évaluations de la vie privée"],
  navGraph: ["PI Network Explorer", "Explorateur du réseau de RP"],
  skip: ["Skip to main content", "Aller au contenu principal"],
  eyebrow: ["Follow the evidence", "Suivre les sources"],
  title: [
    "See how the records connect",
    "Découvrez les liens entre les documents",
  ],
  model: [
    "Full data model · every table and field",
    "Modèle complet · toutes les tables et tous les champs",
  ],
  intro: [
    "Choose a record. See what links to it, inspect the evidence, then follow the next connection.",
    "Choisissez un document. Découvrez ses liens, examinez les preuves, puis suivez le prochain lien.",
  ],
  search: [
    "Find an institution, assessment, bank, class or named official",
    "Trouver une institution, une évaluation, un fichier, une catégorie de documents ou un cadre nommé",
  ],
  clear: ["Clear", "Effacer"],
  loading: ["Loading connections…", "Chargement des liens…"],
  shape: [
    "One connected information landscape",
    "Un ensemble de renseignements interconnectés",
  ],
  shapeNote: [
    "Institutions provide context. Assessments cite banks and classes. AIAs can name responsible officials. Each connection has source evidence.",
    "Les institutions donnent le contexte. Les évaluations citent des fichiers et catégories de documents. Les EIA peuvent nommer des cadres responsables. Chaque lien conserve ses preuves.",
  ],
  start: ["Start with a connected story", "Commencer par un parcours lié"],
  back: ["← Previous record", "← Document précédent"],
  share: ["Copy path link", "Copier le lien du parcours"],
  details: ["Record information", "Informations sur le document"],
  mapGuide: [
    "Select a record to continue. Choose Evidence to inspect its connection.",
    "Sélectionnez un document pour continuer. Choisissez Preuve pour examiner son lien.",
  ],
  beyond: ["Where this record can lead", "Où ce document peut vous mener"],
  beyondNote: [
    "These are two-step paths through documented connections, not additional direct relationships.",
    "Ces parcours comportent deux liens documentés; ils ne constituent pas des relations directes supplémentaires.",
  ],
  notice: [
    "A citation records a reference, not the full scope of an assessment. Missing links reflect the collected evidence. Type and personal-information category remain attributes of a bank.",
    "Une citation indique une référence, sans définir la portée complète d’une évaluation. Les liens absents reflètent les preuves recueillies. Le type et la catégorie de renseignements demeurent des attributs du fichier.",
  ],
  download: [
    "Download base graph JSON",
    "Télécharger le graphique de base JSON",
  ],
  method: ["Method and evidence limits", "Méthode et limites des preuves"],
  institution: ["Institution", "Institution"],
  pia: ["Privacy assessment", "Évaluation de la vie privée"],
  aia: [
    "Algorithmic impact assessment",
    "Évaluation de l’incidence algorithmique",
  ],
  pib: ["Personal Information Bank", "Fichier de renseignements personnels"],
  class: ["Class of Records", "Catégorie de documents"],
  official: ["Responsible senior official", "Cadre supérieur responsable"],
  reference: ["Unresolved citation", "Citation non résolue"],
  listed_by: ["Listed under institution", "Répertorié sous l’institution"],
  references: ["Explicit citation", "Citation explicite"],
  related_class: ["Related class", "Catégorie connexe"],
  responsible_official: [
    "Named responsible official",
    "Cadre responsable nommé",
  ],
  pib_type: ["PIB type", "Type de FRP"],
  personal_information_categories: [
    "Personal-information categories (derived)",
    "Catégories de renseignements personnels (dérivées)",
  ],
  pib_type_details: ["PIB type definition", "Définition du type de FRP"],
  purpose: ["Purpose", "Fin"],
  description: ["Description", "Description"],
  class_of_individuals: ["People covered", "Personnes visées"],
  consistent_uses: ["Consistent uses", "Usages compatibles"],
  retention_disposal: ["Retention and disposal", "Conservation et élimination"],
  document_types: ["Document types", "Types de documents"],
  survey_version: ["Survey version", "Version du questionnaire"],
  impact_level: ["Impact level (feed-derived)", "Niveau d’incidence (source)"],
  senior_official: ["Responsible official", "Cadre responsable"],
  senior_official_uid: ["Official u_id", "u_id du cadre"],
  project_id: ["Project ID", "ID du projet"],
  provenance: ["Source provenance", "Provenance"],
  label: ["Title", "Titre"],
  id: ["Unique ID", "ID unique"],
  identifier: ["Identifier", "Identifiant"],
  institution_id: ["Institution ID", "ID de l’institution"],
  scope: ["Scope", "Portée"],
  sources: ["Original sources", "Sources originales"],
  source_status: ["Source availability", "Disponibilité des sources"],
  available_languages: ["Available languages", "Langues disponibles"],
  aliases: ["Other recorded identifiers", "Autres identifiants"],
  source_path: ["Repository source", "Source dans le dépôt"],
  record_url: ["Full record URL", "URL du document complet"],
  basis: ["Basis", "Fondement"],
  resolution: ["Resolution", "Résolution"],
  source: ["Source", "Source"],
  target: ["Target", "Cible"],
  evidence_count: ["Evidence count", "Nombre de preuves"],
  type: ["Type", "Type"],
};
const t = (key) => words[key]?.[fr ? 1 : 0] || key;
const button = (name, action, cls) => {
  const b = el("button", name, cls);
  b.type = "button";
  b.onclick = action;
  return b;
};
const link = (name, href) => {
  const a = el("a", name);
  try {
    const u = new URL(href, location.href);
    if (["http:", "https:"].includes(u.protocol)) a.href = u.href;
  } catch {}
  return a;
};
const repo = (path, line) =>
  "https://github.com/PatLittle/pibs/blob/main/" +
  path.split("/").map(encodeURIComponent).join("/") +
  (line ? "#L" + line : "");
let index,
  data,
  focus = "",
  trail = [],
  edge = "",
  resultLimit = 12,
  renderSerial = 0,
  loadNote = "";
const groupLimits = new Map(),
  shards = new Map();
function localize() {
  document.documentElement.lang = lang;
  document.title = t("title") + " · PIBS";
  document
    .querySelectorAll("[data-i18n]")
    .forEach((n) => (n.textContent = t(n.dataset.i18n)));
  $("search").placeholder = text(
    "Name or identifier, in English or French",
    "Nom ou identifiant, en français ou en anglais",
  );
  const nav = {
    Overview: "Aperçu",
    PIBs: "FRP",
    "Classes of Records": "Catégories de documents",
    "PIB-to-class linkages": "Liens FRP-catégories",
    "Standard PIBs": "FRP ordinaires",
    "Standard classes": "Catégories ordinaires",
    Categories: "Catégories",
    "PIB types": "Types de FRP",
    "Privacy Assessments": "Évaluations de la vie privée",
    "PI Network Explorer": "Explorateur du réseau de RP",
    "Link AIA": "Liens EIA",
  };
  if (fr) {
    document
      .querySelectorAll("gcds-nav-link")
      .forEach(
        (n) => (n.textContent = nav[n.textContent.trim()] || n.textContent),
      );
    document.querySelectorAll("gcds-nav-group").forEach((n, i) => {
      const label = ["Données institutionnelles", "Données de référence"][i];
      n.setAttribute("open-trigger", label);
      n.setAttribute("close-trigger", "Fermer : " + label);
      n.setAttribute("menu-label", label);
    });
  }
  $("trail").setAttribute(
    "aria-label",
    text("Your evidence path", "Votre parcours dans les sources"),
  );
  $("connection-map").setAttribute(
    "aria-label",
    text("Documented connections", "Liens documentés"),
  );
  $("landscape").setAttribute(
    "aria-label",
    text("Record types in the network", "Types de documents dans le réseau"),
  );
  updateLanguageLink();
  setPanel(true);
}
function viewURL() {
  const u = new URL(location.href);
  u.search = "";
  u.hash = "";
  u.searchParams.set("lang", lang);
  if (focus) u.searchParams.set("node", focus);
  if (edge) u.searchParams.set("edge", edge);
  for (const id of trail) u.searchParams.append("trail", id);
  return u;
}
function updateLanguageLink() {
  const u = viewURL();
  u.searchParams.set("lang", fr ? "en" : "fr");
  document.querySelector("gcds-header")?.setAttribute("lang-href", u.href);
}
function save() {
  history.pushState(null, "", viewURL());
  updateLanguageLink();
}
function setPanel(show) {
  requestAnimationFrame(drawLinks);
  $("exploration").classList.toggle("panel-hidden", !show);
  $("inspector").inert = !show;
  const label = text(
    show ? "Hide information panel" : "Show information panel",
    show
      ? "Masquer le panneau d’information"
      : "Afficher le panneau d’information",
  );
  $("toggle-panel").setAttribute("aria-label", label);
  $("toggle-panel").title = label;
  $("toggle-panel").setAttribute("aria-expanded", String(show));
  $("close-panel").setAttribute(
    "aria-label",
    text("Hide information panel", "Masquer le panneau d’information"),
  );
}
function relationPhrase(group) {
  if (group.relation === "listed_by")
    return group.outgoing
      ? text("This record is listed under", "Ce document est répertorié sous")
      : text(
          "Published or listed by this institution",
          "Publié ou répertorié par cette institution",
        );
  if (group.relation === "references")
    return group.outgoing
      ? text(
          "Explicitly cited by this record",
          "Cité explicitement par ce document",
        )
      : text("Explicitly cite this record", "Cite explicitement ce document");
  if (group.relation === "related_class")
    return group.outgoing
      ? text(
          "Classes referenced by this bank",
          "Catégories citées par ce fichier",
        )
      : text(
          "Banks that reference this class",
          "Fichiers qui citent cette catégorie",
        );
  return group.outgoing
    ? text("Named in this assessment", "Nommé dans cette évaluation")
    : text(
        "Assessments naming this official",
        "Évaluations qui nomment ce cadre",
      );
}
function nodeMeta(node) {
  return [
    node.identifier,
    node.scope === "standard"
      ? text("Government-wide standard", "Norme pangouvernementale")
      : null,
  ]
    .filter(Boolean)
    .join(" · ");
}
function go(id, mode = "follow", path) {
  if (!index.nodes.has(id)) return;
  if (path) trail = path;
  else if (mode === "new") trail = [id];
  else {
    const previous = trail.indexOf(id);
    trail = previous >= 0 ? trail.slice(0, previous + 1) : [...trail, id];
  }
  focus = id;
  edge = "";
  groupLimits.clear();
  $("search").value = "";
  renderSearch();
  setPanel(true);
  render();
  save();
  $("focus-heading").focus({ preventScroll: true });
  $("exploration").scrollIntoView({ block: "start" });
}
function inspectEdge(id) {
  edge = id;
  setPanel(true);
  renderDetails();
  save();
  $("inspector-heading").focus({ preventScroll: true });
  $("inspector").scrollIntoView({ block: "nearest" });
}
function recordCard(record) {
  const { node, edges } = record,
    li = el("li");
  li.dataset.nodeType = node.type;
  li.dataset.recordId = node.id;
  li.append(
    button(label(node, lang), () => go(node.id), "connection-title"),
    el("small", nodeMeta(node)),
  );
  const row = el("div", null, "connection-evidence");
  for (const e of edges) {
    const b = button(
      text("Evidence", "Preuve"),
      () => inspectEdge(e.id),
      "evidence-button",
    );
    b.setAttribute(
      "aria-label",
      text("Inspect connection: ", "Examiner le lien : ") + label(node, lang),
    );
    b.title = text(
      "Inspect source evidence",
      "Examiner les preuves dans la source",
    );
    row.append(b);
  }
  const previous = trail.at(-2);
  if (previous) {
    const shared = connections(index, node.id).find(
      (e) => e.source === previous || e.target === previous,
    );
    if (shared)
      row.append(
        el(
          "small",
          text("Also linked to ", "Aussi lié à ") +
            label(index.nodes.get(previous), lang),
        ),
      );
  }
  li.append(row);
  return li;
}
function render() {
  renderSerial++;
  $("starting-points").hidden = !!focus;
  $("exploration").hidden = !focus;
  if (!focus) return;
  const node = index.nodes.get(focus);
  $("focus-card").replaceChildren();
  $("focus-card").dataset.nodeType = node.type;
  const h = el("h2", label(node, lang));
  h.id = "focus-heading";
  h.tabIndex = -1;
  $("focus-card").append(
    el("span", t(node.type), "record-kind"),
    h,
    el("p", nodeMeta(node), "record-identifier"),
  );
  const desc =
    node["description_" + lang] || node.description_en || node.description_fr;
  if (desc)
    $("focus-card").append(
      el(
        "p",
        desc.length > 240 ? desc.slice(0, 237) + "…" : desc,
        "focus-description",
      ),
    );
  $("trail").replaceChildren();
  trail.forEach((id, i) => {
    if (i) $("trail").append(el("span", "›"));
    $("trail").append(
      button(
        label(index.nodes.get(id), lang),
        () => go(id, "follow", trail.slice(0, i + 1)),
        "trail-step",
      ),
    );
  });
  $("back").disabled = trail.length < 2;
  const groups = focusGroups(index, focus, lang),
    total = new Set(groups.flatMap((g) => g.records.map((r) => r.node.id)))
      .size;
  $("connection-count").textContent = text(
    `${total} connected records · every connection sourced`,
    `${total} documents liés · chaque lien est sourcé`,
  );
  $("connection-groups").replaceChildren();
  for (const g of groups) {
    const section = el("section", null, "connection-group");
    section.dataset.nodeType = g.type;
    const header = el("div", null, "group-heading");
    header.append(
      el("h3", t(g.type) + " · " + g.records.length),
      el("p", relationPhrase(g)),
    );
    section.append(header);
    const list = el("ul");
    const limit = groupLimits.get(g.key) || 3;
    g.records.slice(0, limit).forEach((r) => list.append(recordCard(r)));
    section.append(list);
    if (limit < g.records.length)
      section.append(
        button(
          text(
            `Show ${Math.min(12, g.records.length - limit)} more · ${g.records.length - limit} remaining`,
            `Afficher ${Math.min(12, g.records.length - limit)} de plus · ${g.records.length - limit} restants`,
          ),
          () => {
            groupLimits.set(g.key, limit + 12);
            render();
          },
          "more-connections",
        ),
      );
    $("connection-groups").append(section);
  }
  if (!groups.length)
    $("connection-groups").append(
      el(
        "p",
        text(
          "No documented connections were collected for this record.",
          "Aucun lien documenté n’a été recueilli pour ce document.",
        ),
      ),
    );
  const paths = bridgePaths(index, focus);
  $("bridges").hidden = !paths.length;
  $("bridge-paths").replaceChildren();
  for (const path of paths) {
    const via = index.nodes.get(path.via),
      target = index.nodes.get(path.target),
      card = el("article", null, "bridge-path");
    card.append(
      el("p", text("Through ", "Par ") + label(via, lang), "bridge-via"),
      button(
        label(target, lang),
        () => go(target.id, "follow", [...trail, via.id, target.id]),
        "bridge-target",
      ),
    );
    const proof = button(
      text("See the two source links", "Voir les deux liens sources"),
      () => showPathEvidence(path),
      "bridge-proof",
    );
    card.append(el("small", t(target.type)), proof);
    $("bridge-paths").append(card);
  }
  renderDetails();
  $("share-status").textContent = "";
  updateLanguageLink();
  requestAnimationFrame(drawLinks);
}
function drawLinks() {
  const map = $("connection-map");
  map.querySelector("#map-links")?.remove();
  if (!focus) return;
  const origin = map.getBoundingClientRect(),
    root = $("focus-card").getBoundingClientRect();
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.id = "map-links";
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("viewBox", `0 0 ${map.clientWidth} ${map.scrollHeight}`);
  for (const heading of map.querySelectorAll(".group-heading")) {
    const r = heading.getBoundingClientRect(),
      x1 = root.left + root.width / 2 - origin.left,
      y1 = root.bottom - origin.top,
      x2 = r.left + r.width / 2 - origin.left,
      y2 = r.top - origin.top;
    const p = document.createElementNS(svg.namespaceURI, "path");
    p.setAttribute(
      "d",
      `M ${x1} ${y1} C ${x1} ${y1 + 25} ${x2} ${y2 - 25} ${x2} ${y2}`,
    );
    svg.append(p);
  }
  map.prepend(svg);
}
async function shard(path) {
  if (!shards.has(path))
    shards.set(
      path,
      fetch(path).then((r) => {
        if (!r.ok) throw Error("HTTP " + r.status);
        return r.json();
      }),
    );
  try {
    return await shards.get(path);
  } catch (e) {
    shards.delete(path);
    throw e;
  }
}
function attributeValue(value, container) {
  if (Array.isArray(value)) {
    if (!value.length) {
      container.append(el("p", "—"));
      return;
    }
    const list = el("ul");
    for (const item of value) {
      const li = el("li");
      if (item && typeof item === "object") {
        const d = el("details");
        d.append(
          el(
            "summary",
            item["label_" + lang] ||
              item.label_en ||
              item.id ||
              text("Evidence", "Preuve"),
          ),
        );
        if (item.basis === "derived")
          d.append(
            el(
              "p",
              text(
                "Estimated from description text; not an official category assignment.",
                "Estimation tirée de la description; pas une attribution officielle.",
              ),
              "record-note",
            ),
          );
        for (const [k, v] of Object.entries(item)) attribute(d, k, v);
        li.append(d);
      } else attributeValue(item, li);
      list.append(li);
    }
    container.append(list);
  } else if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value)) attribute(container, k, v);
  } else if (typeof value === "string" && /^https?:\/\//.test(value))
    container.append(link(value, value));
  else
    container.append(
      el("p", value == null || value === "" ? "—" : String(value)),
    );
}
function attribute(container, key, value) {
  const d = el("details", null, "record-attribute");
  d.dataset.attribute = key;
  d.append(
    el(
      "summary",
      attributeLabel(key, t) +
        (Array.isArray(value) ? " · " + value.length : ""),
    ),
  );
  const content = el("div", null, "attribute-value");
  if (["source_path", "vocabulary_path"].includes(key) && value)
    content.append(link(value, repo(value)));
  else attributeValue(value, content);
  d.append(content);
  container.append(d);
}
async function evidence(edge, container) {
  container.textContent = t("loading");
  try {
    const items = edge.evidence || (await shard(edge.evidence_url))[edge.id];
    container.replaceChildren();
    for (const item of items) {
      const block = el("article", null, "graph-evidence");
      block.append(el("strong", item.mention || item.field || t(edge.type)));
      if (item.field) block.append(el("small", item.field));
      if (item.excerpt) block.append(el("blockquote", item.excerpt));
      if (item.source_url)
        block.append(
          link(text("Original source", "Source originale"), item.source_url),
        );
      if (item.source_path)
        block.append(
          link(
            text("Repository evidence", "Preuve dans le dépôt"),
            repo(item.source_path, item.line),
          ),
        );
      const audit = el("details");
      audit.append(
        el("summary", text("Provenance details", "Détails de provenance")),
      );
      for (const [k, v] of Object.entries(item)) attribute(audit, k, v);
      block.append(audit);
      container.append(block);
    }
  } catch {
    container.replaceChildren(
      el(
        "p",
        text(
          "Evidence could not be loaded.",
          "Impossible de charger les preuves.",
        ),
      ),
      button(text("Retry", "Réessayer"), () => evidence(edge, container)),
    );
  }
}
function edgePanel(e, container) {
  container.append(el("h3", t(e.type)));
  const from = index.nodes.get(e.source),
    to = index.nodes.get(e.target);
  container.append(
    el("p", label(from, lang) + " → " + label(to, lang), "edge-endpoints"),
    el(
      "p",
      e.resolution === "resolved"
        ? text(
            "A documented source connection.",
            "Un lien documenté dans la source.",
          )
        : text(
            "This citation has no unique resolved target.",
            "Cette citation n’a pas de cible unique résolue.",
          ),
      "record-note",
    ),
  );
  const d = el("details", null, "edge-evidence");
  d.append(el("summary", text("Source evidence", "Preuves dans la source")));
  const content = el("div");
  d.append(content);
  let loaded = false;
  d.addEventListener("toggle", () => {
    if (d.open && !loaded) {
      loaded = true;
      evidence(e, content);
    }
  });
  container.append(d);
  const attrs = el("section", null, "record-attributes");
  for (const [k, v] of Object.entries(e))
    if (!["evidence", "evidence_url"].includes(k)) attribute(attrs, k, v);
  container.append(attrs);
}
async function renderDetails() {
  const serial = renderSerial,
    id = focus,
    selected = edge;
  $("detail").replaceChildren();
  $("detail").dataset.nodeType = index.nodes.get(id)?.type || "";
  if (selected && index.edges.has(selected)) {
    edgePanel(index.edges.get(selected), $("detail"));
    return;
  }
  const node = index.nodes.get(id);
  if (!node) return;
  $("detail").append(
    el("span", t(node.type), "record-kind"),
    el("h3", label(node, lang)),
  );
  if (node.record_url) {
    const u = new URL(node.record_url, location.href);
    u.searchParams.set("lang", lang);
    $("detail").append(
      link(
        text("Open full source record", "Ouvrir le document source complet"),
        u.href,
      ),
    );
  }
  const attrs = el("section", null, "record-attributes");
  $("detail").append(attrs);
  const display = (extra) => {
    const open = new Set(
      [...attrs.querySelectorAll(":scope>details[open]")].map(
        (n) => n.dataset.attribute,
      ),
    );
    attrs.replaceChildren(
      el("h4", text("All attributes", "Tous les attributs")),
    );
    for (const [k, v] of Object.entries(nodeAttributes(node, extra)))
      attribute(attrs, k, v);
    attrs
      .querySelectorAll(":scope>details")
      .forEach((n) => (n.open = open.has(n.dataset.attribute)));
  };
  display({});
  if (node.attribute_url) {
    const loading = el("p", t("loading"), "record-note");
    attrs.append(loading);
    try {
      const extra = (await shard(node.attribute_url))[id];
      if (serial === renderSerial && id === focus && selected === edge)
        display(extra);
    } catch {
      loading.replaceChildren(
        el(
          "span",
          text("Attributes unavailable. ", "Attributs indisponibles. "),
        ),
        button(text("Retry", "Réessayer"), renderDetails),
      );
    }
  }
}
function showPathEvidence(path) {
  edge = "";
  setPanel(true);
  $("detail").replaceChildren(
    el("h3", text("Two documented steps", "Deux liens documentés")),
    el(
      "p",
      text(
        "The intermediate record is the bridge; no direct relationship between the endpoints is asserted.",
        "Le document intermédiaire fait le pont; aucune relation directe n’est affirmée entre les extrémités.",
      ),
      "record-note",
    ),
  );
  for (const id of path.edges) {
    const s = el("section", null, "path-evidence");
    edgePanel(index.edges.get(id), s);
    $("detail").append(s);
  }
  $("inspector").scrollIntoView({ block: "nearest" });
}
function renderSearch() {
  if (!index) return;
  const q = $("search").value.trim();
  $("results").replaceChildren();
  $("results").hidden = !q;
  $("more-results").hidden = true;
  $("search-status").textContent = "";
  if (!q) return;
  const found = findRecords(index, q, lang);
  for (const n of found.slice(0, resultLimit)) {
    const li = el("li"),
      b = button(label(n, lang), () => go(n.id, "new"));
    b.append(el("small", t(n.type) + " · " + n.identifier));
    li.append(b);
    $("results").append(li);
  }
  $("search-status").textContent = text(
    `${Math.min(resultLimit, found.length)} of ${found.length} matches`,
    `${Math.min(resultLimit, found.length)} résultats sur ${found.length}`,
  );
  $("more-results").hidden = found.length <= resultLimit;
}
function readLocation() {
  const p = new URLSearchParams(location.search);
  focus = p.get("node") || p.get("root") || "";
  edge = p.get("edge") || "";
  if (edge && index.edges.has(edge) && !focus)
    focus = index.edges.get(edge).source;
  trail = focus ? validTrail(index, p.getAll("trail"), focus) : [];
  if (!index.nodes.has(focus)) {
    if (focus)
      $("load-status").textContent = text(
        "That record is not in the current collection. Search for another starting point.",
        "Ce document ne figure pas dans la collection actuelle. Cherchez un autre point de départ.",
      );
    focus = "";
    edge = "";
  }
  if (edge && !connections(index, focus).some((e) => e.id === edge)) edge = "";
  groupLimits.clear();
  render();
}
async function init() {
  localize();
  try {
    const r = await fetch("data/graph.json");
    if (!r.ok) throw Error("Graph HTTP " + r.status);
    data = await r.json();
    try {
      data = (await loadAIA(structuredClone(data))).graph;
    } catch {
      loadNote = text(
        "The external AIA feed is unavailable; the collected records remain accessible.",
        "La source EIA externe est indisponible; les documents recueillis restent accessibles.",
      );
    }
    index = indexGraph(data);
    $("load-status").textContent = loadNote;
    for (const n of document.querySelectorAll("[data-kind]")) {
      const kind = n.dataset.kind;
      n.append(
        el("strong", t(kind)),
        el("span", String(data.summary.node_types[kind] || 0)),
      );
    }
    $("stories").replaceChildren();
    for (const example of [EXAMPLES[2], EXAMPLES[3], EXAMPLES[4]])
      if (index.nodes.has(example.id)) {
        const b = button(
          example["title_" + lang],
          () => go(example.id, "new"),
          "story",
        );
        b.append(el("span", example["text_" + lang]));
        $("stories").append(b);
      }
    $("starting-points").hidden = false;
    readLocation();
    $("record-search").onsubmit = (e) => e.preventDefault();
    $("search").oninput = () => {
      resultLimit = 12;
      renderSearch();
    };
    $("search-clear").onclick = () => {
      $("search").value = "";
      renderSearch();
      $("search").focus();
    };
    $("more-results").onclick = () => {
      resultLimit += 20;
      renderSearch();
    };
    $("toggle-panel").onclick = () =>
      setPanel($("exploration").classList.contains("panel-hidden"));
    $("close-panel").onclick = () => {
      setPanel(false);
      $("toggle-panel").focus({ preventScroll: true });
    };
    $("back").onclick = () => {
      if (trail.length > 1) go(trail.at(-2), "follow", trail.slice(0, -1));
    };
    $("share").onclick = async () => {
      try {
        await navigator.clipboard.writeText(viewURL().href);
        $("share-status").textContent = text(
          "Path link copied.",
          "Lien du parcours copié.",
        );
      } catch {
        const input = el("input");
        input.value = viewURL().href;
        input.readOnly = true;
        $("share-status").replaceChildren(input);
        input.select();
      }
    };
    window.addEventListener("popstate", readLocation);
  } catch (e) {
    $("load-status").textContent = text(
      "Connections could not be loaded. Reload to retry, or browse the source tables.",
      "Impossible de charger les liens. Rechargez la page ou consultez les tableaux sources.",
    );
    $("load-status").setAttribute("role", "alert");
    console.error(e);
  }
}
new ResizeObserver(() => requestAnimationFrame(drawLinks)).observe(
  $("connection-map"),
);
init();
