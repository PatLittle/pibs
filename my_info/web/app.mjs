import { SurveyToolEngine } from "./engine.mjs";

const $ = (selector) => document.querySelector(selector);
const clone = (value) => structuredClone(value);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"
})[character]);

const copy = {
  "en-CA": {
    langButton: "Français", title: "What personal information might the federal government have about you?",
    lede: "Answer questions about your interactions with federal programs. My Info will estimate which published Personal Information Banks may apply and whether the records are likely still held.",
    privacyTitle: "Private by design", privacy: "Your answers stay in this browser tab. They are not saved or sent to the My Info MCP service.",
    clear: "Clear answers", back: "Back", continue: "Continue", viewResults: "View results",
    question: "Interaction", refinement: "A little more detail", timing: "Approximate timing", department: "Relevant departments",
    progress: (answered, total) => `${answered} of ${total} main interactions answered`,
    yes: "Yes", no: "No", not_sure: "Not sure", prefer_not_to_answer: "Prefer not to answer",
    examples: "Show real-world examples", why: "Why this is asked", selectAll: "Select all that apply.",
    year: "Approximate year", yearHint: "For example, 2019", current: "Current or ongoing", within_1_year: "Within the last year",
    "1_to_3_years": "1 to 3 years ago", "4_to_7_years": "4 to 7 years ago", "8_to_15_years": "8 to 15 years ago",
    more_than_15_years: "More than 15 years ago", approximate_year: "A specific approximate year", unknown: "I’m not sure",
    resultTitle: "Your estimated personal information holdings", resultIntro: "These are candidate matches based on published descriptions—not confirmation that an institution holds a record about you.",
    print: "Print results", restart: "Start over", matches: "candidate PIBs", filters: "Filter results",
    institution: "Institution", allInstitutions: "All institutions", scope: "PIB type", allScopes: "All types",
    status: "Holding estimate", allStatuses: "All estimates", standard: "Standard PIB", institution_specific: "Institution-specific PIB",
    strong_match: "Direct match", possible_match: "Possible match", review_if_relevant: "Review if relevant",
    likely_held: "Likely still held", may_still_be_held: "May still be held", likely_disposed: "Likely disposed of", retention_unknown: "Retention unknown",
    likely_heldHelp: "The approximate date is within the published retention period.", may_still_be_heldHelp: "The date overlaps a boundary or the rule is conditional.",
    likely_disposedHelp: "The approximate date is beyond a published disposal period.", retention_unknownHelp: "The published rule cannot support a date-based estimate.",
    source: "View source description", whyMatched: "Why this matched", categories: "Categories of personal information", noCategory: "No category was derived", specificTypes: "Specific information types described",
    noFiltered: "No results match these filters.", answerPath: "Review your answer path", change: "Change",
    inventoryGap: "Known inventory gap", gapText: "A selected interaction has no defensible direct match in the current source inventory.",
    personaExamples: "Explore example life stories and results", personaHint: "Four fictional personas show how different federal interactions affect the estimate.",
    fictionalExample: "Fictional example", viewLifeStory: "View life story", lifeStory: "Life story", selectedTimeline: "Selected timeline",
    close: "Close", closeExample: "Close example", results: "Results", exampleResultsFor: "Example results for",
    footer: "My Info is an experimental, source-backed estimate. It cannot confirm that an institution has a record about you.", sourceCode: "Source code and data",
    error: "The survey could not be loaded. Try refreshing the page.", confirmClear: "Clear every answer and start again?"
  },
  "fr-CA": {
    langButton: "English", title: "Quels renseignements personnels le gouvernement fédéral pourrait-il avoir à votre sujet?",
    lede: "Répondez à des questions sur vos interactions avec les programmes fédéraux. L’outil estimera quelles banques de renseignements personnels publiées pourraient s’appliquer et si les dossiers sont probablement encore conservés.",
    privacyTitle: "Confidentiel dès la conception", privacy: "Vos réponses restent dans cet onglet. Elles ne sont ni enregistrées ni envoyées au service MCP My Info.",
    clear: "Effacer les réponses", back: "Précédent", continue: "Continuer", viewResults: "Voir les résultats",
    question: "Interaction", refinement: "Un peu plus de détails", timing: "Période approximative", department: "Institutions concernées",
    progress: (answered, total) => `${answered} interactions principales sur ${total} ont une réponse`,
    yes: "Oui", no: "Non", not_sure: "Je ne sais pas", prefer_not_to_answer: "Je préfère ne pas répondre",
    examples: "Afficher des exemples concrets", why: "Pourquoi cette question est posée", selectAll: "Sélectionnez toutes les réponses pertinentes.",
    year: "Année approximative", yearHint: "Par exemple, 2019", current: "En cours", within_1_year: "Au cours de la dernière année",
    "1_to_3_years": "Il y a 1 à 3 ans", "4_to_7_years": "Il y a 4 à 7 ans", "8_to_15_years": "Il y a 8 à 15 ans",
    more_than_15_years: "Il y a plus de 15 ans", approximate_year: "Une année approximative précise", unknown: "Je ne sais pas",
    resultTitle: "Estimation de vos renseignements personnels", resultIntro: "Il s’agit de correspondances possibles fondées sur les descriptions publiées, et non d’une confirmation qu’une institution détient un dossier à votre sujet.",
    print: "Imprimer les résultats", restart: "Recommencer", matches: "BRP possibles", filters: "Filtrer les résultats",
    institution: "Institution", allInstitutions: "Toutes les institutions", scope: "Type de BRP", allScopes: "Tous les types",
    status: "Estimation de conservation", allStatuses: "Toutes les estimations", standard: "BRP ordinaire", institution_specific: "BRP propre à l’institution",
    strong_match: "Correspondance directe", possible_match: "Correspondance possible", review_if_relevant: "À examiner si pertinent",
    likely_held: "Probablement encore conservés", may_still_be_held: "Peut-être encore conservés", likely_disposed: "Probablement éliminés", retention_unknown: "Conservation inconnue",
    likely_heldHelp: "La date approximative se situe dans la période de conservation publiée.", may_still_be_heldHelp: "La date chevauche une limite ou la règle est conditionnelle.",
    likely_disposedHelp: "La date approximative dépasse une période d’élimination publiée.", retention_unknownHelp: "La règle publiée ne permet pas d’estimation fondée sur la date.",
    source: "Voir la description source", whyMatched: "Pourquoi cette correspondance", categories: "Catégories de renseignements personnels", noCategory: "Aucune catégorie n’a été dérivée", specificTypes: "Types précis de renseignements décrits",
    noFiltered: "Aucun résultat ne correspond à ces filtres.", answerPath: "Vérifier votre parcours de réponses", change: "Modifier",
    inventoryGap: "Lacune connue de l’inventaire", gapText: "Une interaction sélectionnée n’a aucune correspondance directe défendable dans l’inventaire source actuel.",
    personaExamples: "Explorer des récits de vie et des résultats", personaHint: "Quatre profils fictifs montrent comment différentes interactions fédérales influencent l’estimation.",
    fictionalExample: "Exemple fictif", viewLifeStory: "Voir le récit de vie", lifeStory: "Récit de vie", selectedTimeline: "Éléments du parcours",
    close: "Fermer", closeExample: "Fermer l’exemple", results: "Résultats", exampleResultsFor: "Exemple de résultats pour",
    footer: "My Info fournit une estimation expérimentale fondée sur les sources. Il ne peut pas confirmer qu’une institution détient un dossier à votre sujet.", sourceCode: "Code source et données",
    error: "Le questionnaire n’a pas pu être chargé. Essayez d’actualiser la page.", confirmClear: "Effacer toutes les réponses et recommencer?"
  }
};

const statusOrder = ["likely_held", "may_still_be_held", "likely_disposed", "retention_unknown"];
const statusColors = { likely_held: "#19705b", may_still_be_held: "#a65e00", likely_disposed: "#59636e", retention_unknown: "#6b4fa1" };
let locale = "en-CA";
let engine;
let manifest;
let state;
let current;
let history = [];
let allResults = [];
let evaluation;
let personas = [];
let activePersona = null;
let modalPersona = null;

const t = (key) => copy[locale][key] ?? key;
const questionFor = (code) => engine.questions[code];
const routeFor = (code) => engine.routes[code];
const localizedQuestion = (code) => locale === "fr-CA" ? questionFor(code).question_fr : questionFor(code).readability_en.candidate_question_en;
const localizedOption = (code, optionCode) => {
  const option = engine.routeOptions[code][optionCode];
  return locale === "fr-CA" ? option.label_fr : option.label_en;
};
const answerLabel = (value) => t(value);

function applyStaticCopy() {
  document.documentElement.lang = locale.slice(0, 2);
  document.documentElement.dir = "ltr";
  $("#language-toggle").textContent = t("langButton");
  $("#page-title").textContent = t("title");
  $("#page-lede").textContent = t("lede");
  $("#privacy-title").textContent = t("privacyTitle");
  $("#privacy-copy").textContent = t("privacy");
  $("#footer-copy").textContent = t("footer");
  $("#footer-source").textContent = t("sourceCode");
  $("#clear-button").textContent = t("clear");
  $("#back-button").textContent = t("back");
  $("#continue-button").textContent = t("continue");
  $("#persona-examples-title").textContent = t("personaExamples");
  $("#persona-examples-hint").textContent = t("personaHint");
  $("#persona-modal-label").textContent = t("fictionalExample");
  $("#persona-modal-close").textContent = t("close");
  $("#persona-results-button").textContent = t("results");
  $("#persona-modal-close-icon").setAttribute("aria-label", t("closeExample"));
}

const humanHeading = (value) => ({
  profile: locale === "fr-CA" ? "Profil" : "Profile",
  experience: locale === "fr-CA" ? "Expérience professionnelle" : "Professional experience",
  appointments_and_memberships: locale === "fr-CA" ? "Nominations et affiliations" : "Appointments and memberships",
  education: locale === "fr-CA" ? "Études" : "Education",
  sport: locale === "fr-CA" ? "Sport" : "Sport",
  additional_life_context: locale === "fr-CA" ? "Autres éléments du parcours" : "Additional life context",
  employment_events: locale === "fr-CA" ? "Événements professionnels" : "Employment events"
})[value] || value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

function renderPersonaExamples() {
  const section = $("#persona-examples");
  if (!personas.length) { section.hidden = true; return; }
  section.hidden = false;
  $("#persona-grid").innerHTML = personas.map((persona) => `<button class="persona-card" type="button" data-persona-id="${escapeHtml(persona.id)}" aria-label="${escapeHtml(`${t("viewLifeStory")}: ${persona.display_name}`)}"><img src="${escapeHtml(persona.portrait_path)}" alt=""><span><strong>${escapeHtml(persona.display_name)}</strong><small>${escapeHtml(persona.subtitle)}</small></span></button>`).join("");
  section.querySelectorAll("[data-persona-id]").forEach((button) => button.addEventListener("click", () => openPersona(button.dataset.personaId)));
}

function renderCvEntry(entry) {
  if (typeof entry !== "object" || !entry) return `<div class="persona-cv-entry"><p>${escapeHtml(entry)}</p></div>`;
  const title = entry.title || entry.role || entry.degree || entry.name || entry.activity || entry.organization || entry.institution || "";
  const meta = [entry.organization, entry.institution, entry.period, entry.year].filter((value, index, values) => value && value !== title && values.indexOf(value) === index).join(" · ");
  const description = entry.description || entry.summary || entry.details || "";
  const highlights = entry.highlights || entry.bullets || entry.activities || [];
  return `<article class="persona-cv-entry">${title ? `<h4>${escapeHtml(title)}</h4>` : ""}${meta ? `<p class="persona-entry-meta">${escapeHtml(meta)}</p>` : ""}${description ? `<p>${escapeHtml(description)}</p>` : ""}${highlights.length ? `<ul>${highlights.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}</article>`;
}

function openPersona(personaId) {
  const persona = personas.find((item) => item.id === personaId);
  if (!persona) return;
  modalPersona = persona;
  const sections = Object.entries(persona.cv || {}).map(([key, values]) => {
    const items = Array.isArray(values) ? values : [values];
    return `<section><h3>${escapeHtml(humanHeading(key))}</h3>${items.map(renderCvEntry).join("")}</section>`;
  }).join("");
  const timeline = (persona.episodes || []).length ? `<section class="persona-timeline"><h3>${escapeHtml(t("selectedTimeline"))}</h3><ol>${persona.episodes.map((episode) => `<li><strong>${escapeHtml(episode.year)}</strong><span><b>${escapeHtml(episode.title)}</b>${escapeHtml(episode.details)}</span></li>`).join("")}</ol></section>` : "";
  $("#persona-modal-content").innerHTML = `<header class="persona-modal-header"><img src="${escapeHtml(persona.portrait_path)}" alt=""><div><h2 id="persona-modal-title">${escapeHtml(persona.display_name)}</h2><p>${escapeHtml(persona.subtitle)}</p></div></header><section class="persona-story"><h3>${escapeHtml(t("lifeStory"))}</h3><p>${escapeHtml(persona.summary)}</p></section><div class="persona-cv-grid">${sections}</div>${timeline}`;
  $("#persona-modal").showModal();
}

async function showPersonaResults() {
  if (!modalPersona?.survey) return;
  let response = engine.advance(
    engine.createState(locale),
    clone(modalPersona.survey.answers || []),
    clone(modalPersona.survey.refinements || [])
  );
  while (!response.complete && response.next_step?.step_type === "department") {
    response = engine.advance(response.state, [], [], [{
      question_code: response.next_step.question_code,
      institution_ids: response.next_step.options.map((option) => option.institution_id)
    }]);
  }
  if (!response.complete) throw new Error(`Persona fixture ${modalPersona.id} did not complete the survey`);
  activePersona = modalPersona;
  state = response.state;
  history = [];
  $("#persona-modal").close();
  await renderResults();
}

function renderStep(response) {
  current = response;
  $("#loading").hidden = true;
  $("#results-region").hidden = true;
  $("#survey-card").hidden = false;
  const step = response.next_step;
  const answered = response.progress.answered_questions;
  $("#step-label").textContent = t(step.step_type);
  $("#progress-copy").textContent = t("progress")(answered, manifest.question_count);
  $("#progress-bar").style.width = `${Math.min(100, Math.round(answered / manifest.question_count * 100))}%`;
  $("#back-button").disabled = history.length === 0;
  $("#continue-button").disabled = true;
  $("#continue-button").textContent = t("continue");
  const region = $("#question-region");
  if (step.step_type === "question") renderQuestion(region, step);
  if (step.step_type === "refinement") renderRefinement(region, step);
  if (step.step_type === "timing") renderTiming(region, step);
  if (step.step_type === "department") renderDepartment(region, step);
  region.querySelector("input")?.focus();
}

function renderQuestion(region, step) {
  const options = ["yes", "no", "not_sure", "prefer_not_to_answer"];
  const examples = step.help.examples || [];
  const help = examples.length ? `<details class="examples"><summary>${escapeHtml(t("examples"))}</summary><ul>${examples.map((item) =>
    `<li><strong>${escapeHtml(item.institution)}</strong> — ${escapeHtml(item.activity)}</li>`).join("")}</ul></details>` : "";
  const split = step.help.split_recommendation ? `<p class="question-note"><strong>${escapeHtml(t("why"))}:</strong> ${escapeHtml(step.help.split_recommendation)}</p>` : "";
  region.innerHTML = `<h2 class="question-title">${escapeHtml(step.prompt)}</h2>${split}<fieldset class="choice-list" aria-label="${escapeHtml(step.prompt)}">${options.map((value) =>
    `<label class="choice"><input type="radio" name="answer" value="${value}"><span><strong>${escapeHtml(answerLabel(value))}</strong></span></label>`).join("")}</fieldset>${help}`;
  region.querySelectorAll('input[name="answer"]').forEach((input) => input.addEventListener("change", () => {
    $("#continue-button").disabled = false;
  }));
}

function renderRefinement(region, step) {
  region.innerHTML = `<p class="eyebrow">${escapeHtml(localizedQuestion(step.question_code))}</p><h2 class="question-title">${escapeHtml(step.prompt)}</h2><p class="question-note">${escapeHtml(t("selectAll"))}</p><fieldset class="choice-list" aria-label="${escapeHtml(step.prompt)}">${step.options.map((option) =>
    `<label class="choice"><input type="checkbox" name="route" value="${escapeHtml(option.code)}"><span><strong>${escapeHtml(option.label)}</strong><small>${escapeHtml(option.institution)}</small></span></label>`).join("")}</fieldset><p class="privacy-note">${escapeHtml(step.privacy_note)}</p>`;
  const update = () => { $("#continue-button").disabled = !region.querySelector('input[name="route"]:checked'); };
  region.querySelectorAll('input[name="route"]').forEach((input) => input.addEventListener("change", update));
}

function renderTiming(region, step) {
  region.innerHTML = `<p class="eyebrow">${escapeHtml(localizedQuestion(step.question_code))}</p><h2 class="question-title">${escapeHtml(step.prompt)}</h2><fieldset class="choice-list" aria-label="${escapeHtml(step.prompt)}">${step.timing_kinds.map((kind) =>
    `<label class="choice"><input type="radio" name="timing" value="${kind}"><span><strong>${escapeHtml(t(kind))}</strong></span></label>`).join("")}</fieldset><div id="year-field" class="year-field" hidden><label for="approximate-year">${escapeHtml(t("year"))}</label><input id="approximate-year" type="number" min="1800" max="2200" inputmode="numeric" placeholder="${escapeHtml(t("yearHint"))}"></div><p class="privacy-note">${escapeHtml(step.privacy_note)}</p>`;
  const update = () => {
    const selected = region.querySelector('input[name="timing"]:checked')?.value;
    const yearField = $("#year-field");
    yearField.hidden = selected !== "approximate_year";
    const year = Number($("#approximate-year").value);
    $("#continue-button").disabled = !selected || (selected === "approximate_year" && (!Number.isInteger(year) || year < 1800 || year > new Date().getUTCFullYear()));
  };
  region.querySelectorAll('input[name="timing"]').forEach((input) => input.addEventListener("change", update));
  $("#approximate-year").addEventListener("input", update);
}

function renderDepartment(region, step) {
  region.innerHTML = `<p class="eyebrow">${escapeHtml(localizedQuestion(step.question_code))}</p><h2 class="question-title">${escapeHtml(step.prompt)}</h2><p class="question-note">${escapeHtml(t("selectAll"))}</p><fieldset class="choice-list" aria-label="${escapeHtml(step.prompt)}">${step.options.map((option) =>
    `<label class="choice"><input type="checkbox" name="department" value="${escapeHtml(option.institution_id)}"><span><strong>${escapeHtml(option.label)}</strong></span></label>`).join("")}</fieldset><p class="privacy-note">${escapeHtml(step.privacy_note)}</p>`;
  const update = () => { $("#continue-button").disabled = !region.querySelector('input[name="department"]:checked'); };
  region.querySelectorAll('input[name="department"]').forEach((input) => input.addEventListener("change", update));
}

function submitCurrent() {
  const step = current.next_step;
  history.push(clone(state));
  if (step.step_type === "question") {
    const value = $("#question-region input[name=answer]:checked").value;
    current = engine.advance(state, [{ question_code: step.question_code, value }]);
  } else if (step.step_type === "refinement") {
    const selected = [...document.querySelectorAll('#question-region input[name="route"]:checked')].map((input) => input.value);
    current = engine.advance(state, [], [{ question_code: step.question_code, selected_options: selected, timings: {} }]);
  } else if (step.step_type === "timing") {
    const kind = $("#question-region input[name=timing]:checked").value;
    const timing = kind === "approximate_year" ? { kind, year: Number($("#approximate-year").value) } : { kind };
    if (step.route_option_code) {
      const refinement = clone(state.refinements[step.question_code]);
      refinement.timings[step.route_option_code] = timing;
      current = engine.advance(state, [], [{ question_code: step.question_code, ...refinement }]);
    } else {
      current = engine.advance(state, [{ question_code: step.question_code, value: "yes", timing }]);
    }
  } else {
    const institutionIds = [...document.querySelectorAll('#question-region input[name="department"]:checked')].map((input) => input.value);
    current = engine.advance(state, [], [], [{ question_code: step.question_code, institution_ids: institutionIds }]);
  }
  state = current.state;
  current.complete ? renderResults() : renderStep(current);
}

async function collectResults() {
  let offset = 0;
  let page;
  const results = [];
  do {
    page = engine.evaluate(state, { asOfYear: new Date().getUTCFullYear(), includePossible: false, maxResults: 500, offset });
    results.push(...page.results);
    offset = page.summary.next_offset;
  } while (offset !== null);
  return { evaluation: page, results };
}

async function renderResults() {
  ({ evaluation, results: allResults } = await collectResults());
  $("#survey-card").hidden = true;
  const region = $("#results-region");
  region.hidden = false;
  const counts = Object.fromEntries(statusOrder.map((status) => [status, allResults.filter((result) => result.holding_status === status).length]));
  const total = allResults.length || 1;
  const institutions = [...new Set(allResults.map((result) => result.institution_name))].sort((a, b) => a.localeCompare(b));
  const personaLabel = activePersona ? `<p class="persona-result-label">${escapeHtml(t("exampleResultsFor"))} <strong>${escapeHtml(activePersona.display_name)}</strong></p>` : "";
  region.innerHTML = `<div class="results-shell">${personaLabel}<div class="result-head"><div><p class="beta-label">Beta</p><h2>${escapeHtml(t("resultTitle"))}</h2><p>${escapeHtml(allResults.length)} ${escapeHtml(t("matches"))}</p></div><div><button id="print-button" class="button button-secondary" type="button">${escapeHtml(t("print"))}</button></div></div><p class="caveat">${escapeHtml(t("resultIntro"))}</p>${evaluation.assessment.inventory_gaps.length ? `<div class="privacy-note"><strong>${escapeHtml(t("inventoryGap"))}</strong><br>${escapeHtml(t("gapText"))}</div>` : ""}<div class="summary-grid">${statusOrder.map((status) => `<div class="summary-stat" style="--status:${statusColors[status]}"><strong>${counts[status]}</strong><span>${escapeHtml(t(status))}</span></div>`).join("")}</div><div class="stacked-bar" role="img" aria-label="${statusOrder.map((status) => `${t(status)}: ${counts[status]}`).join(", ")}">${statusOrder.filter((status) => counts[status]).map((status) => `<span style="width:${counts[status] / total * 100}%;background:${statusColors[status]}">${counts[status]}</span>`).join("")}</div><div class="filters" aria-label="${escapeHtml(t("filters"))}"><label>${escapeHtml(t("institution"))}<select id="institution-filter"><option value="">${escapeHtml(t("allInstitutions"))}</option>${institutions.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("")}</select></label><label>${escapeHtml(t("status"))}<select id="status-filter"><option value="">${escapeHtml(t("allStatuses"))}</option>${statusOrder.map((status) => `<option value="${status}">${escapeHtml(t(status))}</option>`).join("")}</select></label><label>${escapeHtml(t("scope"))}<select id="scope-filter"><option value="">${escapeHtml(t("allScopes"))}</option><option value="institution_specific">${escapeHtml(t("institution_specific"))}</option><option value="standard">${escapeHtml(t("standard"))}</option></select></label></div><div id="result-list"></div>${renderAnswerTree()}<div class="actions"><button id="restart-button" class="button button-primary" type="button">${escapeHtml(t("restart"))}</button></div></div>`;
  $("#print-button").addEventListener("click", () => window.print());
  $("#restart-button").addEventListener("click", resetSurvey);
  region.querySelectorAll("select").forEach((select) => select.addEventListener("change", renderFilteredResults));
  region.querySelectorAll("[data-edit]").forEach((button) => button.addEventListener("click", () => editQuestion(button.dataset.edit)));
  renderFilteredResults();
  region.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderFilteredResults() {
  const institution = $("#institution-filter").value;
  const statusFilter = $("#status-filter").value;
  const scope = $("#scope-filter").value;
  const filtered = allResults.filter((result) => (!institution || result.institution_name === institution) && (!statusFilter || result.holding_status === statusFilter) && (!scope || result.scope === scope));
  const list = $("#result-list");
  if (!filtered.length) { list.innerHTML = `<p class="empty">${escapeHtml(t("noFiltered"))}</p>`; return; }
  list.innerHTML = statusOrder.map((status) => {
    const statusResults = filtered.filter((result) => result.holding_status === status);
    if (!statusResults.length) return "";
    const groups = statusResults.reduce((output, result) => {
      (output[result.institution_name] ||= []).push(result);
      return output;
    }, {});
    return `<section class="status-section" style="--status:${statusColors[status]}"><div class="status-heading"><h3>${escapeHtml(t(status))} · ${statusResults.length}</h3><p>${escapeHtml(t(`${status}Help`))}</p></div>${Object.entries(groups).sort(([a], [b]) => a.localeCompare(b)).map(([name, results]) => `<div class="institution-group"><h4>${escapeHtml(name)} · ${results.length}</h4>${results.map(renderResultCard).join("")}</div>`).join("")}</section>`;
  }).join("");
}

function renderResultCard(result) {
  const routeReasons = result.matched_route_options.map((match) => localizedOption(match.question_code, match.route_option_code));
  const questionReasons = result.matched_question_codes.filter((code) => !result.matched_route_options.some((match) => match.question_code === code)).map(localizedQuestion);
  const reasons = [...routeReasons, ...questionReasons];
  const source = /^https?:\/\//.test(result.source_url || "") ? `<a href="${escapeHtml(result.source_url)}" target="_blank" rel="noopener">${escapeHtml(t("source"))}</a>` : "";
  const types = result.specific_information_types || [];
  return `<article class="result-card"><h5>${escapeHtml(result.title)}</h5><div class="result-meta"><span class="pill">${escapeHtml(result.bank_number)}</span><span class="pill">${escapeHtml(t(result.scope))}</span><span class="pill">${escapeHtml(t(result.match_band))}</span></div><details><summary>${escapeHtml(t("whyMatched"))}</summary><ul>${reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}</ul><p>${escapeHtml(result.retention.rationale)}</p></details><strong>${escapeHtml(t("categories"))}</strong>${result.categories_of_personal_information.length ? `<ul class="category-list">${result.categories_of_personal_information.map((category) => `<li class="pill">${escapeHtml(category.name)}</li>`).join("")}</ul>` : `<p>${escapeHtml(t("noCategory"))}</p>`}${types.length ? `<details><summary>${escapeHtml(t("specificTypes"))}</summary><ul>${types.map((type) => `<li>${escapeHtml(type)}</li>`).join("")}</ul></details>` : ""}${source}</article>`;
}

function renderAnswerTree() {
  const items = engine.questionOrder.filter((code) => state.answers[code]).map((code) => {
    const answer = state.answers[code];
    const refinement = state.refinements[code];
    const children = refinement ? `<ul>${refinement.selected_options.map((option) => `<li>${escapeHtml(localizedOption(code, option))} · ${escapeHtml(t(refinement.timings[option]?.kind || "unknown"))}</li>`).join("")}</ul>` : answer.timing ? `<ul><li>${escapeHtml(t(answer.timing.kind))}</li></ul>` : "";
    return `<li><strong>${escapeHtml(localizedQuestion(code))}</strong> — ${escapeHtml(answerLabel(answer.value))}<button class="text-button" type="button" data-edit="${escapeHtml(code)}">${escapeHtml(t("change"))}</button>${children}</li>`;
  }).join("");
  return `<details class="examples"><summary>${escapeHtml(t("answerPath"))}</summary><ol class="tree">${items}</ol></details>`;
}

function editQuestion(code) {
  activePersona = null;
  const fresh = engine.createState(locale);
  for (const questionCode of engine.questionOrder) {
    if (questionCode === code) break;
    if (state.answers[questionCode]) fresh.answers[questionCode] = clone(state.answers[questionCode]);
    if (state.refinements[questionCode]) fresh.refinements[questionCode] = clone(state.refinements[questionCode]);
  }
  state = fresh;
  history = [];
  renderStep(engine.advance(state));
  $("#survey-card").scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetSurvey() {
  activePersona = null;
  state = engine.createState(locale);
  history = [];
  renderStep(engine.advance(state));
}

$("#continue-button").addEventListener("click", submitCurrent);
$("#back-button").addEventListener("click", () => {
  if (!history.length) return;
  state = history.pop();
  renderStep(engine.advance(state));
});
$("#clear-button").addEventListener("click", () => { if (window.confirm(t("confirmClear"))) resetSurvey(); });
$("#persona-modal-close").addEventListener("click", () => $("#persona-modal").close());
$("#persona-modal-close-icon").addEventListener("click", () => $("#persona-modal").close());
$("#persona-modal").addEventListener("click", (event) => { if (event.target === $("#persona-modal")) $("#persona-modal").close(); });
$("#persona-results-button").addEventListener("click", () => showPersonaResults().catch((error) => {
  console.error("Persona fixture failed", error);
  $("#persona-modal").close();
  $("#error").hidden = false;
  $("#error").textContent = t("error");
}));
$("#language-toggle").addEventListener("click", () => {
  locale = locale === "en-CA" ? "fr-CA" : "en-CA";
  if (state) state.locale = locale;
  applyStaticCopy();
  renderPersonaExamples();
  if ($("#persona-modal").open && modalPersona) {
    $("#persona-modal").close();
    openPersona(modalPersona.id);
  }
  if (!$("#results-region").hidden) renderResults();
  else if (current) renderStep(engine.advance(state));
});

try {
  const [response, personaResponse] = await Promise.all([
    fetch("runtime.json", { cache: "no-store" }),
    fetch("personas.json", { cache: "no-store" })
  ]);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const runtime = await response.json();
  if (personaResponse.ok) {
    const personaPayload = await personaResponse.json();
    personas = Array.isArray(personaPayload.personas) ? personaPayload.personas : [];
  } else {
    console.warn(`Persona examples unavailable: HTTP ${personaResponse.status}`);
  }
  engine = new SurveyToolEngine(runtime.contract, runtime.features);
  manifest = engine.getManifest();
  state = engine.createState(locale);
  applyStaticCopy();
  renderPersonaExamples();
  renderStep(engine.advance(state));
} catch (error) {
  console.error("My Info initialization failed", error);
  $("#loading").hidden = true;
  $("#error").hidden = false;
  $("#error").textContent = t("error");
}
