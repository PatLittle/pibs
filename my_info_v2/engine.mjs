// V2 is deliberately independent of V1's keyword classifier and survey state.
export class SurveyV2 {
  constructor(runtime) {
    this.runtime = runtime;
    this.activities = new Map(runtime.activities.map((item) => [item.id, item]));
    this.records = new Map(runtime.records.map((item) => [item.record_id, item]));
    this.institutions = new Map(runtime.institutions.map((item) => [item.id, item]));
    this.rules = new Map(runtime.retention_rules.map((item) => [item.record_id, item]));
  }

  createState(locale = "en") {
    return { version: "2.0", locale, activities: [], unsure: [], reviewed_records: [], scopes: {}, dates: {}, quick_activities: [] };
  }

  validate(state) {
    if (!state || state.version !== "2.0" || !["en", "fr"].includes(state.locale)) throw Error("Invalid V2 state");
    const allowed = new Set(["version", "locale", "activities", "unsure", "reviewed_records", "scopes", "dates", "quick_activities"]);
    if (Object.keys(state).some((key) => !allowed.has(key))) throw Error("Unexpected state field");
    for (const key of ["scopes", "dates"]) if (!state[key] || typeof state[key] !== "object" || Array.isArray(state[key])) throw Error(`Invalid ${key}`);
    for (const key of ["activities", "unsure", "reviewed_records", "quick_activities"]) {
      if (!Array.isArray(state[key]) || new Set(state[key]).size !== state[key].length) throw Error(`Invalid ${key}`);
      const source = key === "reviewed_records" ? this.records : this.activities;
      if (state[key].some((id) => !source.has(id))) throw Error(`Unknown ${key} identifier`);
    }
    if (state.unsure.some((id) => state.activities.includes(id))) throw Error("An activity cannot be both selected and uncertain");
    if (state.quick_activities.some((id) => !state.activities.includes(id) || !this.runtime.quick_activity_ids.includes(id))) throw Error("Invalid quick activity");
    for (const [id, institutions] of Object.entries(state.scopes)) {
      if (!state.activities.includes(id) || this.activities.get(id).scope !== "choose_institution") throw Error("Unexpected institution answer");
      if (!Array.isArray(institutions) || !institutions.length || new Set(institutions).size !== institutions.length) throw Error("Invalid institution answer");
      if (institutions.includes("unknown") && institutions.length !== 1) throw Error("Unknown cannot be combined with named institutions");
      if (institutions.some((item) => item !== "unknown" && !this.institutions.has(item))) throw Error("Unknown institution");
    }
    for (const [key, date] of Object.entries(state.dates)) {
      if (!this.dateKeys(state).has(key)) throw Error("Unexpected timing answer");
      if (!date || !["year", "unknown", "not_yet"].includes(date.kind)) throw Error("Invalid timing answer");
      if (Object.keys(date).some((field) => !["kind", "year"].includes(field)) || (date.kind !== "year" && "year" in date)) throw Error("Unexpected timing field");
      if (date.kind === "year" && (!Number.isInteger(date.year) || date.year < 1800 || date.year > new Date().getUTCFullYear())) throw Error("Invalid approximate year");
    }
    return state;
  }

  // Changing the activity set invalidates dependent answers instead of preserving stale matches.
  select(state, { activities = [], unsure = [], reviewed_records = [], quick_activities = [] }) {
    const next = { ...structuredClone(state), activities, unsure, reviewed_records, quick_activities, dates: {}, scopes: {} };
    for (const id of activities) if (state.scopes[id]) next.scopes[id] = structuredClone(state.scopes[id]);
    this.validate(next);
    return next;
  }

  setScope(state, activityId, institutionIds) {
    const next = structuredClone(state);
    next.scopes[activityId] = [...institutionIds];
    next.dates = {};
    return this.validate(next);
  }

  setDate(state, key, value) {
    const next = structuredClone(state);
    next.dates[key] = value;
    return this.validate(next);
  }

  nextStep(state) {
    this.validate(state);
    const activity = state.activities.map((id) => this.activities.get(id)).find((item) => item.scope === "choose_institution" && !state.scopes[item.id]);
    if (!activity) return { type: "results" };
    return {
      type: "institution", activity_id: activity.id,
      prompt_en: `For “${activity.label_en}”, which federal organization was involved? If you are unsure, that is fine.`,
      prompt_fr: `Pour « ${activity.label_fr} », quelle organisation fédérale était concernée? Vous pouvez répondre que vous ne savez pas.`,
      options: this.runtime.institutions,
      unknown_allowed: true,
    };
  }

  entries(state) {
    const records = new Map();
    const add = (id, basis) => {
      if (!records.has(id)) records.set(id, { record: this.records.get(id), bases: [] });
      records.get(id).bases.push(basis);
    };
    for (const id of state.activities) {
      const activity = this.activities.get(id);
      for (const recordId of activity.record_ids) {
        const record = this.records.get(recordId);
        const scope = activity.scope === "choose_institution" ? state.scopes[id] || ["unknown"] : [record.institution_id].filter(Boolean);
        // A generic interaction can use a reusable standard description. It never
        // expands to every institution-specific bank with similar words.
        if (activity.scope === "choose_institution" && record.scope !== "standard" && !scope.includes(record.institution_id)) continue;
        add(recordId, { activity_id: id, owner_ids: scope, kind: "selected_activity" });
      }
    }
    for (const id of state.reviewed_records) add(id, { activity_id: null, owner_ids: [this.records.get(id).institution_id].filter(Boolean), kind: "source_reviewed" });
    return [...records.values()];
  }

  dateKey(entry, rule) {
    // Dates never leak between different programs or different retention events.
    const identity = entry.bases.find((basis) => basis.activity_id)?.activity_id || entry.record.record_id;
    return `${identity}::${rule.event}`;
  }

  dateKeys(state) {
    return new Set(this.entries(state).filter((entry) => this.rules.has(entry.record.record_id)).map((entry) => this.dateKey(entry, this.rules.get(entry.record.record_id))));
  }

  timingQuestions(state) {
    this.validate(state);
    const questions = new Map();
    for (const entry of this.entries(state)) {
      const rule = this.rules.get(entry.record.record_id);
      if (!rule || rule.mode === "indefinite") continue;
      const key = this.dateKey(entry, rule);
      if (!questions.has(key)) {
        const activity = entry.bases.find((basis) => basis.activity_id)?.activity_id;
        questions.set(key, {
          key, event: rule.event, event_label_en: rule.event_label_en, event_label_fr: rule.event_label_fr,
          label_en: activity ? this.activities.get(activity).label_en : entry.record.title_en,
          label_fr: activity ? this.activities.get(activity).label_fr : entry.record.title_fr,
          record_ids: [], answer: state.dates[key] || null,
        });
      }
      questions.get(key).record_ids.push(entry.record.record_id);
    }
    return [...questions.values()];
  }

  retention(entry, state, asOfYear) {
    const rule = this.rules.get(entry.record.record_id);
    if (!rule) return { status: "unknown", reason: "unreviewed_rule", rule: null, date: null };
    if (rule.mode === "indefinite") return { status: "no_fixed_end", reason: "indefinite", rule, date: null };
    let date = state.dates[this.dateKey(entry, rule)];
    // The quick assumption applies to the activity occurrence only. It cannot
    // substitute for release, closure, expiry or a later administrative action.
    if (!date && ["record_created", "document_issued", "event_occurred"].includes(rule.event)
        && entry.bases.some((basis) => state.quick_activities.includes(basis.activity_id))) date = { kind: "within_10_years" };
    if (!date || date.kind === "unknown") return { status: "unknown", reason: "date_optional", rule, date: date || null };
    if (date.kind === "not_yet") return { status: "event_not_reached", reason: "event_not_reached", rule, date };
    if (date.kind === "year" && date.year > asOfYear) throw Error("Date is after the assessment year");
    const low = date.kind === "year" ? Math.max(0, asOfYear - date.year - 1) : 0;
    const high = date.kind === "year" ? asOfYear - date.year + 1 : 10;
    if (high < rule.years) return { status: "within_period", reason: "within_period", rule, date };
    if (low > rule.years) {
      const status = rule.mode === "fixed" ? "period_elapsed" : rule.mode === "archive_after" ? "archive_possible" : "may_remain";
      return { status, reason: status, rule, date };
    }
    return { status: "may_remain", reason: "boundary_overlap", rule, date };
  }

  evaluate(state, asOfYear = new Date().getUTCFullYear()) {
    this.validate(state);
    if (!Number.isInteger(asOfYear) || asOfYear < 1800) throw Error("Invalid assessment year");
    const results = this.entries(state).map((entry) => ({
      ...entry.record, bases: entry.bases, retention: this.retention(entry, state, asOfYear),
      owner_ids: [...new Set(entry.bases.flatMap((basis) => basis.owner_ids))],
    }));
    const gaps = state.activities.map((id) => this.activities.get(id)).filter((item) => item.coverage === "source_gap" || !item.record_ids.length);
    return {
      results, gaps, unresolved: state.unsure.map((id) => this.activities.get(id)),
      unanswered_scopes: state.activities.filter((id) => this.activities.get(id).scope === "choose_institution" && !state.scopes[id]),
      selected_activity_count: state.activities.length, reviewed_record_count: state.reviewed_records.length,
      coverage: this.runtime.coverage,
    };
  }

  searchRecords(query = "", institutionId = "") {
    const words = query.toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return this.runtime.records.filter((row) => (!institutionId || row.institution_id === institutionId) && words.every((word) =>
      [row.title_en, row.title_fr, row.bank_number_key, row.institution_name_en, row.institution_name_fr, row.class_of_individuals_en, row.class_of_individuals_fr, row.purpose_en, row.purpose_fr].join(" ").toLocaleLowerCase().includes(word)
    ));
  }
}
