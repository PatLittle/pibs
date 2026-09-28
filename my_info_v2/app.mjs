import { SurveyV2 } from "./engine.mjs";

const $ = (s) => document.querySelector(s);
const html = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
const safeUrl = (s) => /^https?:\/\//i.test(s || "") ? s : "";
const tableLink = (dataset, filters, highlight) => `../table.html?${new URLSearchParams({dataset,...filters})}#:~:text=${encodeURIComponent(highlight).replaceAll("-","%2D")}`;
const copy = {
  en: {
    prototype:"Comparison prototype · Version 2", title:"Find the federal records that may relate to you", lede:"Choose activities you recognize. See which organizations to start with, what their records describe, and where to ask. You can refine dates later.", privacy:"Your selections stay in this tab. No account, saved answers, or analytics.", activities:"Choose activities", directory:"Explore programs", results:"Your record map", logic:"Review the survey logic", v1:"Open Version 1", footer:"An independent prototype using published Info Source descriptions. A relevant description does not confirm that a personal record exists.", searchActivities:"Find an activity", searchPlaceholder:"For example, pension, passport, contractor…", common:"Start with the common four", commonNote:"The four activities below are selected with a broad ten-year window. Uncheck any that do not apply. Every other activity remains available below.", individualDates:"Remove the ten-year assumption", selected:"activities selected", reviewed:"directory records added", unsure:"Not sure", clear:"Clear selections", find:"Find records", quick:"Within the past 10 years", noActivities:"No matching activity labels. Try a program name or explore the full directory.", noSelection:"No activities have been selected. This does not rule out records. You can return to the activities or explore the directory.", searchRecords:"Search published descriptions", recordPlaceholder:"Program, institution, bank number or role…", institution:"Organization", all:"All organizations", unknownInstitution:"I don't know the organization", next:"Continue", back:"Back to activities", scopeNote:"Choose only organizations that handled this interaction. A reusable standard bank will be associated with your selection.", sources:"Published purpose and eligible population", population:"Who the description covers", purpose:"Why the information is collected", addRecord:"I reviewed the program and population; this description applies to my situation", directoryNote:"Search helps you discover programs. Reading or finding a record does not add it to your results; review its population before selecting it.", source:"Open Info Source", sourceFr:"French source", quality:"Source extraction needs review", originalTitle:"The source title is missing or poorly extracted. Review the population and purpose before relying on it.", previous:"Previous", more:"Next page", fromSource:"Institutional context from the collected Info Source", contextMissing:"No usable introductory context was extracted for this organization. Follow the source link to review its programs.", explore:"Explore this organization's programs", reviewBasis:"Added after you reviewed the source population", activityBasis:"Why this is here", standard:"Reusable standard bank", unknownOwner:"Organization not specified", retention:"What the published retention rule can tell us", refine:"Refine retention dates (optional)", printed:"Print / save PDF", download:"Download your record map", unreported:"Unselected activities are unreported, not lifetime 'no' answers. Older or indirect records may exist.", uncertainTitle:"Activities you were unsure about", uncertainNote:"These have not generated positive record matches. Review the program description or ask the organization.", gapTitle:"Places to start — more information needed", gapNote:"The program or organization is known, but this selection does not support a specific reviewed bank yet.", scopePending:"Some generic interactions still need an organization. You can use 'I don't know' to continue.", records:"published descriptions to check", noDates:"No additional dates can improve these estimates using the currently reviewed rules. The full published retention text remains available on each result.", when:"About what year did this happen:", unknownDate:"Not sure / skip", notYet:"This event has not happened", saveDate:"Use this year", timingNote:"Use only the event named here. An approximate year is enough. A date for applying or complaining cannot substitute for release or file closure.", finishDates:"Back to record map", latest:"Dates concern the latest reported episode and this bank's published rule. Other episodes or copies may follow different rules.", within_period:"Within the published period", period_elapsed:"Published period has elapsed", archive_possible:"May now be held by Library and Archives Canada", may_remain:"May remain; no firm disposal conclusion", unknown:"Cannot estimate from current answers", no_fixed_end:"No fixed retention end", event_not_reached:"The retention event has not happened", unreviewed_rule:"The source has not been reduced to a reviewed single-event rule. No date is requested.", date_optional:"A date is optional; the published rule uses a specific event.", indefinite:"The published rule has no fixed end.", boundary_overlap:"The approximate interval overlaps a retention boundary.", elapsedNote:"This describes the published schedule, not proof that a record was destroyed.", sourceLanguage:"English source text shown where the French field is unavailable.", loadingError:"The prototype could not load. Please refresh.", ownership:"Organization to start with", outsideGuided:"Guided choices cover only part of the collected inventory. The directory includes the full inventory and requires your review.", changeActivities:"Change activities", scopeFilter:"Find an organization", directoryCount:"matching descriptions", datesCount:"optional date questions", copyRule:"Published retention text", resetConfirm:"Clear the selections in this tab?"
  },
  fr: {
    prototype:"Prototype de comparaison · Version 2", title:"Trouvez les dossiers fédéraux qui pourraient vous concerner", lede:"Choisissez des activités que vous reconnaissez. Découvrez les organisations à contacter, le contenu de leurs dossiers et les sources à consulter. Vous pourrez préciser les dates ensuite.", privacy:"Vos choix restent dans cet onglet. Aucun compte, aucune réponse sauvegardée ni analyse d'utilisation.", activities:"Choisir des activités", directory:"Explorer les programmes", results:"Vos pistes de dossiers", logic:"Examiner la logique du questionnaire", v1:"Ouvrir la version 1", footer:"Prototype indépendant fondé sur les descriptions publiées dans Info Source. Une description pertinente ne confirme pas l'existence d'un dossier personnel.", searchActivities:"Trouver une activité", searchPlaceholder:"Par exemple : pension, passeport, fournisseur…", common:"Commencer par quatre activités courantes", commonNote:"Les quatre activités ci-dessous sont sélectionnées pour une période approximative de dix ans. Décochez celles qui ne s'appliquent pas. Toutes les autres activités restent accessibles ci-dessous.", individualDates:"Retirer l'hypothèse de dix ans", selected:"activités choisies", reviewed:"dossiers ajoutés du répertoire", unsure:"Je ne sais pas", clear:"Effacer les choix", find:"Trouver des dossiers", quick:"Au cours des dix dernières années", noActivities:"Aucune activité trouvée. Essayez un nom de programme ou explorez le répertoire complet.", noSelection:"Aucune activité n'a été choisie. Cela n'exclut pas l'existence de dossiers. Vous pouvez revenir aux activités ou explorer le répertoire.", searchRecords:"Rechercher dans les descriptions publiées", recordPlaceholder:"Programme, organisation, numéro de fichier ou rôle…", institution:"Organisation", all:"Toutes les organisations", unknownInstitution:"Je ne connais pas l'organisation", next:"Continuer", back:"Retour aux activités", scopeNote:"Choisissez seulement les organisations qui ont traité cette interaction. Un fichier ordinaire sera associé à votre choix.", sources:"Fin et population publiées", population:"Personnes visées par la description", purpose:"Pourquoi les renseignements sont recueillis", addRecord:"J'ai examiné le programme et la population; cette description correspond à ma situation", directoryNote:"La recherche aide à découvrir les programmes. Trouver ou lire une description ne l'ajoute pas à vos résultats; examinez sa population avant de la choisir.", source:"Ouvrir Info Source", sourceFr:"Source française", quality:"Extraction de la source à examiner", originalTitle:"Le titre de la source est absent ou mal extrait. Examinez la population et la fin avant de vous y fier.", previous:"Précédent", more:"Page suivante", fromSource:"Contexte institutionnel tiré de l'Info Source recueilli", contextMissing:"Aucun contexte introductif utilisable n'a été extrait pour cette organisation. Suivez le lien source pour examiner ses programmes.", explore:"Explorer les programmes de cette organisation", reviewBasis:"Ajouté après votre examen de la population visée", activityBasis:"Pourquoi cette piste apparaît", standard:"Fichier ordinaire réutilisable", unknownOwner:"Organisation non précisée", retention:"Ce que la règle de conservation publiée permet d'estimer", refine:"Préciser les dates de conservation (facultatif)", printed:"Imprimer / enregistrer en PDF", download:"Télécharger vos pistes de dossiers", unreported:"Les activités non choisies restent non déclarées; elles ne signifient pas « jamais ». Des dossiers anciens ou indirects peuvent exister.", uncertainTitle:"Activités incertaines", uncertainNote:"Elles n'ont produit aucune correspondance positive. Consultez la description du programme ou l'organisation.", gapTitle:"Points de départ — précisions nécessaires", gapNote:"Le programme ou l'organisation est connu, mais ce choix ne permet pas encore de désigner un fichier examiné précis.", scopePending:"Certaines interactions générales nécessitent encore une organisation. Vous pouvez répondre que vous ne savez pas pour continuer.", records:"descriptions publiées à examiner", noDates:"Aucune date supplémentaire ne peut améliorer ces estimations avec les règles actuellement examinées. Le texte intégral de conservation reste accessible pour chaque résultat.", when:"Vers quelle année cet événement s'est-il produit :", unknownDate:"Je ne sais pas / passer", notYet:"Cet événement ne s'est pas produit", saveDate:"Utiliser cette année", timingNote:"Utilisez seulement l'événement nommé ici. Une année approximative suffit. La date d'une demande ou d'une plainte ne remplace pas la libération ou la fermeture du dossier.", finishDates:"Retour aux pistes de dossiers", latest:"Les dates concernent le dernier épisode déclaré et la règle publiée de ce fichier. D'autres épisodes ou copies peuvent suivre des règles différentes.", within_period:"Dans la période de conservation publiée", period_elapsed:"La période publiée est écoulée", archive_possible:"Peut maintenant être conservé à Bibliothèque et Archives Canada", may_remain:"Peut être conservé; aucune conclusion certaine d'élimination", unknown:"Impossible à estimer avec les réponses actuelles", no_fixed_end:"Aucune fin de conservation fixée", event_not_reached:"L'événement de conservation ne s'est pas produit", unreviewed_rule:"La source n'a pas été réduite à une règle examinée fondée sur un seul événement. Aucune date n'est demandée.", date_optional:"La date est facultative; la règle publiée utilise un événement précis.", indefinite:"La règle publiée n'a pas de fin fixe.", boundary_overlap:"La période approximative chevauche une limite de conservation.", elapsedNote:"Il s'agit du calendrier publié, et non d'une preuve de destruction du dossier.", sourceLanguage:"Le texte anglais est affiché lorsque le champ français est absent.", loadingError:"Impossible de charger le prototype. Veuillez actualiser la page.", ownership:"Organisation à contacter d'abord", outsideGuided:"Les activités proposées couvrent seulement une partie de l'inventaire recueilli. Le répertoire contient l'inventaire complet et nécessite votre examen.", changeActivities:"Modifier les activités", scopeFilter:"Trouver une organisation", directoryCount:"descriptions correspondantes", datesCount:"questions de date facultatives", copyRule:"Texte de conservation publié", resetConfirm:"Effacer les choix dans cet onglet?"
  }
};

let engine, runtime, state, view = "activities", search = "", directorySearch = "", directoryInstitution = "", pageIndex = 0, scopeDraft = [], dateIndex = 0;
const openedGroups = new Set();
let quickPanel = false;
Object.assign(copy.en, {commonNote:"We selected tax filing, federal voting, passport applications and traveller declarations for the past ten years. Uncheck anything that does not apply. All other activities remain available.", noRecords:"Your selections do not identify a reviewed record yet. See the guidance above or explore the program directory.", population_missing:"eligible population missing", purpose_missing:"collection purpose missing", title_needs_review:"title needs review"});
Object.assign(copy.fr, {commonNote:"Nous avons sélectionné les déclarations de revenus, le vote fédéral, les demandes de passeport et les déclarations de voyageur au cours des dix dernières années. Décochez ce qui ne s'applique pas. Toutes les autres activités restent accessibles.", noRecords:"Vos choix ne désignent pas encore de fichier examiné. Consultez les indications ci-dessus ou explorez le répertoire des programmes.", population_missing:"population visée manquante", purpose_missing:"fin de la collecte manquante", title_needs_review:"titre à examiner"});
const t = (key) => copy[state?.locale || "en"][key] || key;
const local = (item, key) => item[`${key}_${state.locale}`] || item[`${key}_en`] || "";
const panel = () => $("#panel");
const owners = (ids) => ids.filter((id) => id !== "unknown").map((id) => engine.institutions.get(id)).filter(Boolean).map((i) => local(i, "name")).join(" · ") || t("unknownOwner");
const recordTitle = (r) => r.quality_flags.includes("title_needs_review") ? r.bank_number_key : local(r, "title");
const link = (url, label) => safeUrl(url) ? `<a href="${html(url)}" target="_blank" rel="noopener">${html(label)}</a>` : "";
const sourceText = (r) => `<h4>${html(t("population"))}</h4><p class="source-copy">${html(local(r,"class_of_individuals"))}</p><h4>${html(t("purpose"))}</h4><p class="source-copy">${html(local(r,"purpose"))}</p>${state.locale === "fr" && (!r.purpose_fr || !r.class_of_individuals_fr) ? `<p class="small">${html(t("sourceLanguage"))}</p>` : ""}`;

function selectionSummary() {
  $("#live-status").textContent = `${state.activities.length} ${t("selected")} · ${state.reviewed_records.length} ${t("reviewed")}`;
}

function render() {
  document.documentElement.lang = state.locale;
  for (const [id, key] of [["prototype","prototype"],["title","title"],["lede","lede"],["privacy","privacy"],["footer-copy","footer"],["logic-link","logic"],["v1-link","v1"]]) $(`#${id}`).textContent = t(key);
  $("#language").textContent = state.locale === "en" ? "Français" : "English";
  $("#navigation").innerHTML = ["activities","directory","results"].map((key) => `<button type="button" data-view="${key}" ${view === key ? 'aria-current="page"' : ""}>${html(t(key))}</button>`).join("");
  selectionSummary();
  if (view === "activities") renderActivities();
  if (view === "directory") renderDirectory();
  if (view === "scope") renderScope();
  if (view === "results") renderResults();
  if (view === "dates") renderDate();
}

function activityCard(a) {
  return `<div class="activity"><label><input type="checkbox" data-activity="${html(a.id)}" ${state.activities.includes(a.id) ? "checked" : ""}><span><strong>${html(local(a,"label"))}</strong>${state.quick_activities.includes(a.id) ? `<span class="tag">${html(t("quick"))}</span>` : ""}</span></label>${local(a,"help") ? `<p class="small">${html(local(a,"help"))}</p>` : ""}<button class="uncertain" type="button" data-unsure="${html(a.id)}" aria-pressed="${state.unsure.includes(a.id)}">${html(t("unsure"))}</button></div>`;
}

function renderActivities() {
  panel().innerHTML = `<h2 tabindex="-1">${html(t("activities"))}</h2><div class="actions"><button id="common" type="button">${html(t("common"))}</button><button id="clear" type="button">${html(t("clear"))}</button></div>${state.quick_activities.length ? `<aside class="notice"><p>${html(t("commonNote"))}</p><button id="unquick" type="button">${html(t("individualDates"))}</button></aside>` : ""}<div class="toolbar"><label>${html(t("searchActivities"))}<input id="activity-search" type="search" value="${html(search)}" placeholder="${html(t("searchPlaceholder"))}"></label></div><div id="groups"></div><div class="actions sticky"><button class="primary" type="button" data-action="find">${html(t("find"))}</button><button type="button" data-view="directory">${html(t("directory"))}</button></div><p class="small">${html(t("unreported"))}</p>`;
  renderGroups();
  $("#activity-search").addEventListener("input", (event) => {search = event.target.value; renderGroups();});
}

function renderGroups() {
  const active = document.activeElement;
  const focusedActivity = active?.dataset.activity;
  const focusedUnsure = active?.dataset.unsure;
  const words = search.toLocaleLowerCase().split(/\s+/).filter(Boolean);
  const candidates = runtime.activities.filter((a) => words.every((w) => [a.label_en,a.label_fr,a.help_en,a.help_fr].join(" ").toLocaleLowerCase().includes(w)));
  const showQuick = quickPanel && !search;
  $("#groups").innerHTML = (showQuick ? `<section class="group"><h3 style="padding:0 20px">${html(t("quick"))}</h3><div class="activity-list">${runtime.quick_activity_ids.map(id=>activityCard(engine.activities.get(id))).join("")}</div></section>` : "") + runtime.groups.map((group) => {
    const items = candidates.filter((a) => a.group === group.id && !(showQuick && runtime.quick_activity_ids.includes(a.id)));
    if (!items.length) return "";
    return `<details class="group" data-group="${group.id}" ${search || openedGroups.has(group.id) ? "open" : ""}><summary>${html(local(group,"label"))} <span class="tag">${items.length}</span></summary><div class="activity-list">${items.map(activityCard).join("")}</div></details>`;
  }).join("") || `<p class="empty">${html(t("noActivities"))}</p>`;
  document.querySelectorAll("[data-group]").forEach((d) => d.addEventListener("toggle", () => d.open ? openedGroups.add(d.dataset.group) : openedGroups.delete(d.dataset.group)));
  if (focusedActivity) document.querySelector(`[data-activity="${CSS.escape(focusedActivity)}"]`)?.focus();
  if (focusedUnsure) document.querySelector(`[data-unsure="${CSS.escape(focusedUnsure)}"]`)?.focus();
}

function goResults() {
  const next = engine.nextStep(state);
  view = next.type === "institution" ? "scope" : "results";
  scopeDraft = [];
  render();
  panel().querySelector("h2")?.focus();
}

function renderScope() {
  const next = engine.nextStep(state);
  if (next.type !== "institution") {view="results";render();return;}
  panel().innerHTML = `<h2 tabindex="-1">${html(local(next,"prompt"))}</h2><p>${html(t("scopeNote"))}</p><div class="toolbar"><label>${html(t("scopeFilter"))}<input type="search" id="scope-filter"></label></div><div class="scope-list" id="scope-list"></div><p id="scope-selected" class="small"></p><div class="actions"><button id="scope-continue" type="button" class="primary" ${scopeDraft.length ? "" : "disabled"}>${html(t("next"))}</button><button id="scope-unknown" type="button">${html(t("unknownInstitution"))}</button><button type="button" data-view="activities">${html(t("back"))}</button></div>`;
  const list = (query="") => {
    $("#scope-list").innerHTML = next.options.filter((i) => local(i,"name").toLowerCase().includes(query.toLowerCase())).map((i) => `<label class="institution-choice"><input type="checkbox" data-scope="${html(i.id)}" ${scopeDraft.includes(i.id) ? "checked" : ""}><span>${html(local(i,"name"))}</span></label>`).join("");
  };
  list();
  $("#scope-filter").addEventListener("input", (e) => list(e.target.value));
  $("#scope-continue").onclick = () => {state=engine.setScope(state,next.activity_id,scopeDraft);goResults();};
  $("#scope-unknown").onclick = () => {state=engine.setScope(state,next.activity_id,["unknown"]);goResults();};
}

function renderDirectory() {
  const choices = runtime.institutions.map((i) => `<option value="${html(i.id)}" ${directoryInstitution === i.id ? "selected" : ""}>${html(local(i,"name"))}</option>`).join("");
  panel().innerHTML = `<h2 tabindex="-1">${html(t("directory"))}</h2><p>${html(t("directoryNote"))}</p><div class="toolbar"><label>${html(t("searchRecords"))}<input type="search" id="record-search" value="${html(directorySearch)}" placeholder="${html(t("recordPlaceholder"))}"></label><label>${html(t("institution"))}<select id="directory-institution"><option value="">${html(t("all"))}</option>${choices}</select></label></div><div id="institution-context"></div><p id="directory-count" role="status"></p><div id="directory-records"></div><div class="actions"><button id="previous-records" type="button">${html(t("previous"))}</button><button id="next-records" type="button">${html(t("more"))}</button><button type="button" data-action="find" class="primary">${html(t("find"))}</button></div>`;
  renderRecords();
  $("#record-search").addEventListener("input",(e)=>{directorySearch=e.target.value;pageIndex=0;renderRecords();});
  $("#directory-institution").addEventListener("change",(e)=>{directoryInstitution=e.target.value;pageIndex=0;renderRecords();});
  $("#previous-records").onclick=()=>{pageIndex--;renderRecords();};
  $("#next-records").onclick=()=>{pageIndex++;renderRecords();};
}

function renderRecords() {
  const institution=engine.institutions.get(directoryInstitution);
  const context=institution?.[`context_${state.locale}`] || [];
  $("#institution-context").innerHTML = institution ? `<aside class="program-context"><strong>${html(local(institution,"name"))}</strong><details><summary>${html(t("fromSource"))}</summary>${context.length ? context.map(c=>`<p class="source-copy">${html(c.excerpt)}</p>`).join("") : `<p>${html(t("contextMissing"))}</p>`}${link(local(institution,"source_url"),t("source"))}</details></aside>` : "";
  const rows=engine.searchRecords(directorySearch,directoryInstitution);
  const page=rows.slice(pageIndex*20,pageIndex*20+20);
  $("#directory-count").textContent=`${rows.length} ${t("directoryCount")} · ${rows.length ? pageIndex*20+1 : 0}–${Math.min(rows.length,pageIndex*20+20)}`;
  $("#directory-records").innerHTML=page.map(r=>`<article class="card"><h3>${html(recordTitle(r))}</h3><p class="small">${html(local(r,"institution_name"))} · ${html(r.bank_number_key)}</p>${r.quality_flags.length ? `<p class="small">${html(t("quality"))}: ${html(r.quality_flags.map(t).join(", "))}</p>` : ""}<details><summary>${html(t("sources"))}</summary>${sourceText(r)}${link(local(r,"source_url"),t("source"))}<p><label class="record-select"><input type="checkbox" data-record="${html(r.record_id)}" ${state.reviewed_records.includes(r.record_id)?"checked":""}><span>${html(t("addRecord"))}</span></label></p></details></article>`).join("");
  $("#previous-records").disabled=pageIndex===0;
  $("#next-records").disabled=(pageIndex+1)*20>=rows.length;
}

function resultCard(r) {
  const pibLink=tableLink(r.scope==="standard"?"standard-pibs":"pibs",r.institution_id?{institution_id:r.institution_id}:{},r.bank_number_key);
  const names=owners(r.owner_ids);
  const reasons=r.bases.map(b=>b.activity_id?local(engine.activities.get(b.activity_id),"label"):t("reviewBasis"));
  const retention=r.retention;
  return `<article class="card"><h3><a href="${html(pibLink)}" target="_blank" rel="noopener">${html(recordTitle(r))}</a></h3><p>${html(names)} <span class="tag">${html(r.bank_number_key)}</span>${r.scope==="standard"?`<span class="tag">${html(t("standard"))}</span>`:""}</p>${r.quality_flags.includes("title_needs_review")?`<p class="small">${html(t("originalTitle"))}</p>`:""}<p><b>${html(t("activityBasis"))}:</b> ${reasons.map(html).join("; ")}</p><p>${r.categories.map(c=>`<a class="tag" href="${html(tableLink("categories",{},c.category_id))}" target="_blank" rel="noopener">${html(local(c,"name"))}</a>`).join("")}</p><p class="result-status">${html(t(retention.status))}</p><p class="small">${html(t(retention.reason))}</p>${retention.status==="period_elapsed"?`<p class="small">${html(t("elapsedNote"))}</p>`:""}<details><summary>${html(t("sources"))}</summary>${sourceText(r)}<h4>${html(t("copyRule"))}</h4><p class="source-copy">${html(local(r,"retention"))}</p></details><div class="actions">${link(local(r,"source_url"),t("source"))}${r.institution_id?`<button type="button" data-explore="${html(r.institution_id)}">${html(t("explore"))}</button>`:""}</div></article>`;
}

function renderResults() {
  const result=engine.evaluate(state);
  const dates=engine.timingQuestions(state);
  const pending=result.unanswered_scopes.length>0;
  panel().innerHTML=`<h2 tabindex="-1">${html(t("results"))}</h2><div class="counts"><span><strong>${result.results.length}</strong> ${html(t("records"))}</span><span><strong>${dates.length}</strong> ${html(t("datesCount"))}</span></div>${pending?`<div class="notice warning"><p>${html(t("scopePending"))}</p><button type="button" data-action="find">${html(t("next"))}</button></div>`:""}<div class="actions"><button id="refine" type="button">${html(t("refine"))}</button><button id="print" type="button">${html(t("printed"))}</button><button id="download" type="button">${html(t("download"))}</button><button type="button" data-view="activities">${html(t("changeActivities"))}</button></div><p class="small">${html(t("latest"))}</p>${result.gaps.length?`<aside class="notice warning"><h3>${html(t("gapTitle"))}</h3><p>${html(t("gapNote"))}</p>${result.gaps.map(a=>`<p><strong>${html(local(a,"label"))}</strong><br>${html(owners(a.scope==="choose_institution"?state.scopes[a.id]||[]:a.institution_ids))}<br>${html(local(a,"help"))}</p>${(a.scope==="choose_institution"?(state.scopes[a.id]||[]).filter(id=>id!=="unknown"):a.institution_ids).map(id=>`<button type="button" data-explore="${html(id)}">${html(t("explore"))}</button>`).join("")}`).join("")}</aside>`:""}${result.unresolved.length?`<aside class="notice"><h3>${html(t("uncertainTitle"))}</h3><p>${html(t("uncertainNote"))}</p><ul>${result.unresolved.map(a=>`<li>${html(local(a,"label"))}</li>`).join("")}</ul></aside>`:""}${result.results.length?result.results.map(resultCard).join(""):`<p class="empty">${html(t(state.activities.length||state.unsure.length?"noRecords":"noSelection"))}</p>`}<p class="notice">${html(t("outsideGuided"))}</p><button type="button" data-view="directory">${html(t("directory"))}</button>`;
  $("#refine").onclick=()=>{dateIndex=0;view="dates";render();};
  $("#print").onclick=()=>window.print();
  $("#download").onclick=download;
}

function renderDate() {
  const questions=engine.timingQuestions(state);
  const q=questions[dateIndex];
  if (!q) {panel().innerHTML=`<h2>${html(t("retention"))}</h2><p>${html(t("noDates"))}</p><button type="button" data-view="results">${html(t("finishDates"))}</button>`;return;}
  panel().innerHTML=`<p class="eyebrow">${dateIndex+1} / ${questions.length}</p><h2 tabindex="-1">${html(local(q,"label"))}</h2><p>${html(t("timingNote"))}</p><div class="date-question"><label for="date-year">${html(t("when"))} <strong>${html(local(q,"event_label"))}?</strong></label><input id="date-year" type="number" min="1800" max="${new Date().getUTCFullYear()}" inputmode="numeric" value="${q.answer?.kind==="year"?q.answer.year:""}"></div><div class="actions"><button id="date-save" class="primary" type="button">${html(t("saveDate"))}</button><button id="date-unknown" type="button">${html(t("unknownDate"))}</button><button id="date-not-yet" type="button">${html(t("notYet"))}</button></div><p id="date-error" role="alert"></p><button type="button" data-view="results">${html(t("finishDates"))}</button>`;
  const save=(answer)=>{try{state=engine.setDate(state,q.key,answer);if(++dateIndex>=questions.length)view="results";render();}catch(error){$("#date-error").textContent=error.message;}};
  $("#date-save").onclick=()=>save({kind:"year",year:Number($("#date-year").value)});
  $("#date-unknown").onclick=()=>save({kind:"unknown"});
  $("#date-not-yet").onclick=()=>save({kind:"not_yet"});
}

function download() {
  const result=engine.evaluate(state);
  const lines=[t("title"),t("footer"),"",...result.results.flatMap(r=>[recordTitle(r),owners(r.owner_ids),r.bank_number_key,t(r.retention.status),local(r,"source_url"),""]),...result.gaps.map(a=>`${local(a,"label")}: ${local(a,"help")}`),...result.unresolved.map(a=>`${t("unsure")}: ${local(a,"label")}`)];
  const url=URL.createObjectURL(new Blob([lines.join("\n")],{type:"text/plain;charset=utf-8"}));
  const a=document.createElement("a");a.href=url;a.download="my-info-record-map.txt";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

document.addEventListener("change",(event)=>{
  const input=event.target;
  if(input.dataset.activity){const id=input.dataset.activity;state=engine.select(state,{activities:input.checked?[...state.activities,id]:state.activities.filter(x=>x!==id),unsure:state.unsure.filter(x=>x!==id),reviewed_records:state.reviewed_records,quick_activities:state.quick_activities.filter(x=>x!==id||input.checked)});selectionSummary();renderGroups();}
  if(input.dataset.record){const id=input.dataset.record;state=engine.select(state,{...state,reviewed_records:input.checked?[...state.reviewed_records,id]:state.reviewed_records.filter(x=>x!==id)});selectionSummary();}
  if(input.dataset.scope){scopeDraft=input.checked?[...scopeDraft,input.dataset.scope]:scopeDraft.filter(x=>x!==input.dataset.scope);$("#scope-continue").disabled=!scopeDraft.length;$("#scope-selected").textContent=owners(scopeDraft);}
});

document.addEventListener("click",(event)=>{
  const b=event.target.closest("button");if(!b||!state)return;
  if(b.dataset.view){view=b.dataset.view;render();panel().querySelector("h2")?.focus();}
  if(b.dataset.action==="find")goResults();
  if(b.dataset.unsure){const id=b.dataset.unsure;state=engine.select(state,{activities:state.activities.filter(x=>x!==id),unsure:state.unsure.includes(id)?state.unsure.filter(x=>x!==id):[...state.unsure,id],reviewed_records:state.reviewed_records,quick_activities:state.quick_activities.filter(x=>x!==id)});renderGroups();selectionSummary();}
  if(b.dataset.explore){directoryInstitution=b.dataset.explore;directorySearch="";pageIndex=0;view="directory";render();}
  if(b.id==="common"){state=engine.select(state,{activities:[...new Set([...state.activities,...runtime.quick_activity_ids])],unsure:state.unsure.filter(x=>!runtime.quick_activity_ids.includes(x)),reviewed_records:state.reviewed_records,quick_activities:[...runtime.quick_activity_ids]});quickPanel=true;search="";render();}
  if(b.id==="unquick"){state.quick_activities=[];render();}
  if(b.id==="clear"&&window.confirm(t("resetConfirm"))){state=engine.createState(state.locale);quickPanel=false;render();}
});

$("#language").onclick=()=>{if(state){state.locale=state.locale==="en"?"fr":"en";render();}};
try {const response=await fetch("runtime.json");if(!response.ok)throw Error(response.status);runtime=await response.json();engine=new SurveyV2(runtime);state=engine.createState();render();}
catch(error){panel().innerHTML=`<p role="alert">${html(t("loadingError"))}</p>`;console.error(error);}
