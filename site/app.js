(function () {
  "use strict";

  const DATASETS = {
    institutions: {
      label: "Authoritative institutions",
      csv: "data/institution_registry.csv",
      description: "The legal Schedule I institution list, enriched with bilingual publication due dates, identifiers, source evidence and institution-specific Info Source URLs.",
      columns: ["legal_name_en", "legal_name_fr", "gc_orgID", "annual_due_date", "infosource_url_en", "infosource_url_fr"],
      titleFields: ["legal_name_en", "legal_name_fr", "institution_id"],
      facets: [
        { field: "annual_due_date", label: "Annual due date" },
        { field: "infosource_validation_en", label: "English source status" },
      ],
    },
    pibs: {
      label: "Institution-specific Personal Information Banks",
      csv: "data/pib_table_en_fr_all.csv",
      description: "Bilingual Personal Information Bank descriptions compiled from institution publications and keyed to the authoritative institution registry.",
      columns: ["institution_name_en", "bank_number_key", "pib_type", "title_en", "title_fr", "related_record_number_en"],
      titleFields: ["title_en", "title_fr", "bank_number_key"],
      facets: [
        { field: "institution_id", label: "Institution", displayField: "institution_name_en" },
        { field: "pib_type", label: "PIB type" },
      ],
    },
    classes: {
      label: "Institution Classes of Records",
      csv: "data/cor_table_en_fr_all.csv",
      description: "Program- and activity-level records published by institutions, including bilingual names and the types of documents held.",
      columns: ["institution_name_en", "record_number", "name_en", "name_fr", "document_types_en", "document_types_fr"],
      titleFields: ["name_en", "name_fr", "record_number"],
      facets: [{ field: "institution_id", label: "Institution", displayField: "institution_name_en" }],
    },
    links: {
      label: "PIB-to-class linkages",
      csv: "data/pib_cor_links_explorer.csv",
      downloadCsv: "data/pib_cor_links.csv",
      description: "Normalized related-record references parsed from PIBs. Resolution status identifies whether each reference maps to a known institution or standard class.",
      columns: ["institution_name_en", "bank_number_key", "language_label", "related_record_number", "relationship_scope_label", "resolution_label", "cor_record_number_display"],
      titleFields: ["bank_number_key", "related_record_number"],
      facets: [
        { field: "institution_id", label: "Institution", displayField: "institution_name_en" },
        { field: "language", label: "Language", displayField: "language_label" },
        { field: "relationship_scope", label: "Class scope", displayField: "relationship_scope_label" },
        { field: "resolved", label: "Resolution", displayField: "resolution_label" },
      ],
    },
    "standard-pibs": {
      label: "Standard Personal Information Banks",
      csv: "data/spib_en_fr.csv",
      description: "Government-wide standard PIBs that describe common administrative personal information holdings used by multiple institutions.",
      columns: ["bank_number_key", "pib_type", "entry_title_en", "entry_title_fr", "date_last_modified", "url_en"],
      titleFields: ["entry_title_en", "entry_title_fr", "bank_number_key"],
      facets: [{ field: "pib_type", label: "PIB type" }],
    },
    "standard-classes": {
      label: "Standard Classes of Records",
      csv: "data/standard_classes_of_records_en_fr.csv",
      description: "Government-wide administrative record classes with language-neutral keys and bilingual PRN/NDP identifiers.",
      columns: ["record_number", "record_number_en", "record_number_fr", "title_en", "title_fr", "document_types_en"],
      titleFields: ["title_en", "title_fr", "record_number_en"],
    },
    categories: {
      label: "Categories of Personal Information",
      csv: "data/pi_categories_en_fr.csv",
      description: "A bilingual controlled vocabulary of personal information categories and examples. Current publications do not explicitly assign these values to individual PIBs.",
      columns: ["PI_CAT_ID", "name_en", "name_fr", "examples_en", "examples_fr"],
      titleFields: ["name_en", "name_fr", "PI_CAT_ID"],
    },
    "pib-types": {
      label: "PIB type codes",
      csv: "data/pib_type_values.csv",
      description: "Controlled values derived from Treasury Board PIB number series and used by both institution-specific and standard PIB tables.",
      columns: ["pib_code", "pib_type", "scope_en", "scope_fr"],
      titleFields: ["pib_type", "pib_code"],
    },
  };

  const COLUMN_LABELS = {
    gc_orgID: "GC organization ID",
    legal_name_en: "Legal name (English)",
    legal_name_fr: "Legal name (French)",
    annual_due_date: "Annual due date",
    infosource_url_en: "Info Source (English)",
    infosource_url_fr: "Info Source (French)",
    institution_name_en: "Institution (English)",
    institution_name_fr: "Institution (French)",
    bank_number_key: "PIB number",
    pib_type: "PIB type",
    title_en: "Title (English)",
    title_fr: "Title (French)",
    name_en: "Name (English)",
    name_fr: "Name (French)",
    document_types_en: "Document types (English)",
    document_types_fr: "Document types (French)",
    related_record_number_en: "Related records (English)",
    related_record_number_fr: "Related records (French)",
    record_number: "Record number",
    record_number_en: "Record number (English)",
    record_number_fr: "Record number (French)",
    entry_title_en: "Title (English)",
    entry_title_fr: "Title (French)",
    date_last_modified: "Last modified",
    relationship_scope: "Class scope",
    relationship_scope_label: "Class scope",
    resolved: "Resolved",
    resolution_label: "Resolution status",
    cor_record_number: "Resolved class key",
    cor_record_number_display: "Resolved class",
    language_label: "Language",
    PI_CAT_ID: "Category ID",
    scope_en: "Scope (English)",
    scope_fr: "Scope (French)",
  };

  const state = {
    datasetId: "",
    config: null,
    headers: [],
    sourceRows: [],
    filteredRows: [],
    visibleRows: [],
    search: "",
    page: 1,
    pageSize: 25,
    sortColumn: "",
    sortDirection: 1,
    urlFilters: [],
  };

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function humanize(value) {
    if (COLUMN_LABELS[value]) {
      return COLUMN_LABELS[value];
    }
    const language = /_(en|fr)$/.exec(String(value || ""));
    const base = String(value || "").replace(/_(en|fr)$/, "");
    const acronyms = { id: "ID", url: "URL", http: "HTTP", pib: "PIB", cor: "Class of Records", gc: "GC", ati: "ATI" };
    let label = base.split("_").map(function (part) {
      return acronyms[part.toLocaleLowerCase("en-CA")] || part.charAt(0).toUpperCase() + part.slice(1);
    }).join(" ");
    if (language) { label += language[1] === "en" ? " (English)" : " (French)"; }
    return label;
  }

  function normalize(value) {
    return String(value == null ? "" : value).replace(/\s+/g, " ").trim().toLocaleLowerCase("en-CA");
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("en-CA").format(Number(value || 0));
  }

  function parseCsv(text) {
    const matrix = [];
    let row = [];
    let field = "";
    let quoted = false;
    for (let index = 0; index < text.length; index += 1) {
      const character = text[index];
      if (quoted) {
        if (character === '"' && text[index + 1] === '"') {
          field += '"';
          index += 1;
        } else if (character === '"') {
          quoted = false;
        } else {
          field += character;
        }
      } else if (character === '"') {
        quoted = true;
      } else if (character === ",") {
        row.push(field);
        field = "";
      } else if (character === "\n") {
        row.push(field.replace(/\r$/, ""));
        matrix.push(row);
        row = [];
        field = "";
      } else {
        field += character;
      }
    }
    if (field || row.length) {
      row.push(field.replace(/\r$/, ""));
      matrix.push(row);
    }
    const headers = (matrix.shift() || []).map(function (header, index) {
      return index === 0 ? header.replace(/^\uFEFF/, "") : header;
    });
    const rows = matrix
      .filter(function (values) { return values.some(function (value) { return value !== ""; }); })
      .map(function (values) {
        const record = {};
        headers.forEach(function (header, index) { record[header] = values[index] || ""; });
        return record;
      });
    return { headers: headers, rows: rows };
  }

  function datasetUrl(datasetId, filters) {
    const params = new URLSearchParams({ dataset: datasetId });
    Object.keys(filters || {}).forEach(function (key) {
      const value = filters[key];
      if (value !== undefined && value !== null && String(value) !== "") {
        params.set(key, value);
      }
    });
    return "table.html?" + params.toString();
  }

  function isUrl(value) {
    return /^https?:\/\//i.test(String(value || "").trim());
  }

  function renderValue(value, compact) {
    const text = String(value == null ? "" : value).trim();
    if (!text) {
      return '<span class="muted">—</span>';
    }
    if (isUrl(text)) {
      return '<a href="' + escapeHtml(text) + '" target="_blank" rel="noopener">Open source <span aria-hidden="true">↗</span></a>';
    }
    if (text.toLocaleLowerCase("en-CA") === "true" || text.toLocaleLowerCase("en-CA") === "false") {
      return '<span class="status-badge status-badge--' + text.toLocaleLowerCase("en-CA") + '">' + escapeHtml(text) + "</span>";
    }
    const shown = compact && text.length > 180 ? text.slice(0, 177).trimEnd() + "…" : text;
    return escapeHtml(shown);
  }

  function applyUrlFilters(rows, headers, params) {
    state.urlFilters = [];
    params.forEach(function (value, key) {
      if (key !== "dataset" && headers.indexOf(key) !== -1 && value !== "") {
        state.urlFilters.push({ key: key, value: value });
      }
    });
    if (!state.urlFilters.length) {
      return rows;
    }
    return rows.filter(function (row) {
      return state.urlFilters.every(function (filter) {
        return normalize(row[filter.key]) === normalize(filter.value);
      });
    });
  }

  function renderActiveFilter() {
    const container = document.getElementById("active-filter");
    if (!container || !state.urlFilters.length) {
      if (container) { container.hidden = true; }
      return;
    }
    const params = new URLSearchParams(window.location.search);
    const description = state.urlFilters.map(function (filter) {
      const facet = (state.config.facets || []).find(function (item) { return item.field === filter.key; });
      const row = state.sourceRows.find(function (item) { return normalize(item[filter.key]) === normalize(filter.value); });
      const display = row && facet && facet.displayField ? row[facet.displayField] : humanize(filter.value);
      const next = new URLSearchParams(params);
      next.delete(filter.key);
      return '<span class="filter-chip"><strong>' + escapeHtml(facet ? facet.label : humanize(filter.key)) + ":</strong> " + escapeHtml(display) + ' <a aria-label="Remove ' + escapeHtml(facet ? facet.label : humanize(filter.key)) + ' filter" href="table.html?' + escapeHtml(next.toString()) + '">×</a></span>';
    }).join("");
    container.innerHTML = '<span><strong>Filtered view</strong> ' + description + '</span><a href="' + escapeHtml(datasetUrl(state.datasetId)) + '">Clear all</a>';
    container.hidden = false;
  }

  function renderFacets() {
    const container = document.getElementById("dataset-facets");
    const facets = state.config.facets || [];
    if (!container || !facets.length) { return; }
    const params = new URLSearchParams(window.location.search);
    container.innerHTML = facets.map(function (facet) {
      const values = new Map();
      state.sourceRows.forEach(function (row) {
        const value = String(row[facet.field] || "").trim();
        if (value && !values.has(value)) {
          values.set(value, facet.displayField ? String(row[facet.displayField] || value).trim() : humanize(value));
        }
      });
      const options = Array.from(values.entries()).sort(function (left, right) {
        return left[1].localeCompare(right[1], "en-CA", { numeric: true, sensitivity: "base" });
      });
      return '<div class="facet-control"><label for="facet-' + escapeHtml(facet.field) + '"><strong>' + escapeHtml(facet.label) + '</strong></label><select class="form-control" id="facet-' + escapeHtml(facet.field) + '" data-facet="' + escapeHtml(facet.field) + '"><option value="">All</option>' + options.map(function (option) {
        return '<option value="' + escapeHtml(option[0]) + '"' + (normalize(params.get(facet.field)) === normalize(option[0]) ? " selected" : "") + '>' + escapeHtml(option[1]) + '</option>';
      }).join("") + "</select></div>";
    }).join("");
    container.querySelectorAll("select[data-facet]").forEach(function (select) {
      select.addEventListener("change", function () {
        const next = new URLSearchParams(window.location.search);
        if (select.value) { next.set(select.dataset.facet, select.value); } else { next.delete(select.dataset.facet); }
        next.delete("open");
        window.location.assign("table.html?" + next.toString());
      });
    });
  }

  function compareRows(left, right) {
    const a = left[state.sortColumn] || "";
    const b = right[state.sortColumn] || "";
    const aNumber = Number(a);
    const bNumber = Number(b);
    if (a !== "" && b !== "" && Number.isFinite(aNumber) && Number.isFinite(bNumber)) {
      return (aNumber - bNumber) * state.sortDirection;
    }
    return String(a).localeCompare(String(b), "en-CA", { numeric: true, sensitivity: "base" }) * state.sortDirection;
  }

  function refreshVisibleRows() {
    const query = normalize(state.search);
    state.visibleRows = query
      ? state.filteredRows.filter(function (row) {
          return state.headers.some(function (header) { return normalize(row[header]).includes(query); });
        })
      : state.filteredRows.slice();
    if (state.sortColumn) {
      state.visibleRows.sort(compareRows);
    }
    const pages = Math.max(1, Math.ceil(state.visibleRows.length / state.pageSize));
    state.page = Math.min(state.page, pages);
    renderTable();
  }

  function sortIndicator(column) {
    if (state.sortColumn !== column) {
      return '<span class="sort-affordance" aria-hidden="true">↕</span>';
    }
    return state.sortDirection === 1 ? '<span class="sort-affordance" aria-hidden="true">▲</span>' : '<span class="sort-affordance" aria-hidden="true">▼</span>';
  }

  function renderTable() {
    const container = document.getElementById("dataset-table-container");
    const status = document.getElementById("table-status");
    const pagination = document.getElementById("table-pagination");
    if (!container || !status || !pagination) {
      return;
    }
    const columns = state.config.columns.filter(function (column) { return state.headers.indexOf(column) !== -1; });
    const start = (state.page - 1) * state.pageSize;
    const pageRows = state.visibleRows.slice(start, start + state.pageSize);
    let html = '<table class="data-table" aria-describedby="table-status"><thead><tr>';
    columns.forEach(function (column) {
      const ariaSort = state.sortColumn === column ? (state.sortDirection === 1 ? "ascending" : "descending") : "none";
      html += '<th scope="col" aria-sort="' + ariaSort + '"><button type="button" data-sort="' + escapeHtml(column) + '">' + escapeHtml(humanize(column)) + sortIndicator(column) + "</button></th>";
    });
    html += '<th scope="col">Details</th></tr></thead><tbody>';
    if (!pageRows.length) {
      html += '<tr><td colspan="' + (columns.length + 1) + '">No records match this view.</td></tr>';
    } else {
      pageRows.forEach(function (row, index) {
        html += "<tr>";
        columns.forEach(function (column) { html += "<td>" + renderValue(row[column], true) + "</td>"; });
        html += '<td><button class="details-button" type="button" data-row="' + index + '">View details<span class="wb-inv"> for ' + escapeHtml(recordTitle(row)) + "</span></button></td></tr>";
      });
    }
    html += "</tbody></table>";
    container.innerHTML = html;
    status.textContent = "Showing " + formatNumber(pageRows.length ? start + 1 : 0) + "–" + formatNumber(Math.min(start + pageRows.length, state.visibleRows.length)) + " of " + formatNumber(state.visibleRows.length) + " matching records.";

    container.querySelectorAll("button[data-sort]").forEach(function (button) {
      button.addEventListener("click", function () {
        const column = button.getAttribute("data-sort");
        if (state.sortColumn === column) {
          state.sortDirection *= -1;
        } else {
          state.sortColumn = column;
          state.sortDirection = 1;
        }
        state.page = 1;
        refreshVisibleRows();
      });
    });
    container.querySelectorAll("button[data-row]").forEach(function (button) {
      button.addEventListener("click", function () {
        const row = pageRows[Number(button.getAttribute("data-row"))];
        if (row) { openRecord(row); }
      });
    });

    const pages = Math.max(1, Math.ceil(state.visibleRows.length / state.pageSize));
    pagination.hidden = state.visibleRows.length <= state.pageSize;
    document.getElementById("page-summary").textContent = "Page " + state.page + " of " + pages;
    document.getElementById("page-previous").disabled = state.page <= 1;
    document.getElementById("page-next").disabled = state.page >= pages;
    document.getElementById("page-first").disabled = state.page <= 1;
    document.getElementById("page-last").disabled = state.page >= pages;
  }

  function recordTitle(row) {
    for (let index = 0; index < state.config.titleFields.length; index += 1) {
      const value = row[state.config.titleFields[index]];
      if (value) { return value; }
    }
    return state.config.label;
  }

  function actionLink(label, datasetId, filters) {
    return '<a class="button-link button-link--small" href="' + escapeHtml(datasetUrl(datasetId, filters)) + '">' + escapeHtml(label) + "</a>";
  }

  function relatedActions(row) {
    const actions = [];
    const institutionFilter = row.institution_id ? { institution_id: row.institution_id } : null;
    if (state.datasetId === "institutions") {
      actions.push(actionLink("Institution PIBs", "pibs", institutionFilter));
      actions.push(actionLink("Institution classes", "classes", institutionFilter));
      actions.push(actionLink("PIB-to-class links", "links", institutionFilter));
    } else if (state.datasetId === "pibs") {
      actions.push(actionLink("Institution", "institutions", institutionFilter));
      actions.push(actionLink("Related-class references", "links", { institution_id: row.institution_id, bank_number_key: row.bank_number_key }));
      actions.push(actionLink("All institution classes", "classes", institutionFilter));
    } else if (state.datasetId === "classes") {
      actions.push(actionLink("Institution", "institutions", institutionFilter));
      actions.push(actionLink("PIBs citing this class", "links", { institution_id: row.institution_id, cor_record_number: row.record_number }));
      actions.push(actionLink("All institution PIBs", "pibs", institutionFilter));
    } else if (state.datasetId === "links") {
      actions.push(actionLink("Source PIB", "pibs", { institution_id: row.institution_id, bank_number_key: row.bank_number_key }));
      actions.push(actionLink("Institution", "institutions", institutionFilter));
      if (normalize(row.resolved) === "true") {
        if (row.relationship_scope === "standard") {
          actions.push(actionLink("Resolved standard class", "standard-classes", { record_number: row.cor_record_number }));
        } else {
          actions.push(actionLink("Resolved institution class", "classes", { institution_id: row.institution_id, record_number: row.cor_record_number }));
        }
      }
    } else if (state.datasetId === "standard-classes") {
      actions.push(actionLink("PIBs citing this standard class", "links", { relationship_scope: "standard", cor_record_number: row.record_number }));
    } else if (state.datasetId === "pib-types") {
      actions.push(actionLink("Institution PIBs of this type", "pibs", { pib_type: row.pib_type }));
      actions.push(actionLink("Standard PIBs of this type", "standard-pibs", { pib_type: row.pib_type }));
    }
    return actions.join("");
  }

  function openRecord(row) {
    const dialog = document.getElementById("record-dialog");
    const body = document.getElementById("record-dialog-body");
    document.getElementById("record-dialog-title").textContent = recordTitle(row);
    document.getElementById("record-dialog-kicker").textContent = state.config.label;
    const actions = relatedActions(row);
    const links = document.getElementById("record-dialog-links");
    links.innerHTML = actions ? '<strong>Explore related data</strong><div class="record-links mrgn-tp-sm">' + actions + "</div>" : "This reference table has no explicit record-level relationships in the current model.";
    const groups = [
      { label: "Sources and collection evidence", test: function (header) { return /url|source|match|http|evidence|validation|checksum|collected/i.test(header); } },
      { label: "English publication", test: function (header) { return /_en$/.test(header); } },
      { label: "French publication", test: function (header) { return /_fr$/.test(header); } },
      { label: "Identity", test: function (header) { return /(^|_)(id|name|title|number|type|scope|language|resolved|status)($|_)/i.test(header) && !/source|validation|http/i.test(header); } },
      { label: "Lifecycle, use and other details", test: function () { return true; } },
    ];
    const remaining = state.headers.filter(function (header) { return String(row[header] || "").trim() !== ""; });
    body.innerHTML = groups.map(function (group) {
      const headers = remaining.filter(group.test);
      headers.forEach(function (header) { remaining.splice(remaining.indexOf(header), 1); });
      if (!headers.length) { return ""; }
      return '<tr class="record-section"><th colspan="2" scope="colgroup">' + escapeHtml(group.label) + "</th></tr>" + headers.map(function (header) {
        return '<tr><th scope="row">' + escapeHtml(humanize(header)) + "</th><td>" + renderValue(row[header], false) + "</td></tr>";
      }).join("");
    }).join("");
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
  }

  function wireControls() {
    const search = document.getElementById("table-search");
    const pageSize = document.getElementById("page-size");
    search.addEventListener("input", function () { state.search = search.value; state.page = 1; refreshVisibleRows(); });
    pageSize.addEventListener("change", function () { state.pageSize = Number(pageSize.value); state.page = 1; refreshVisibleRows(); });
    document.getElementById("page-previous").addEventListener("click", function () { if (state.page > 1) { state.page -= 1; renderTable(); } });
    document.getElementById("page-next").addEventListener("click", function () { state.page += 1; renderTable(); });
    document.getElementById("page-first").addEventListener("click", function () { state.page = 1; renderTable(); });
    document.getElementById("page-last").addEventListener("click", function () { state.page = Math.max(1, Math.ceil(state.visibleRows.length / state.pageSize)); renderTable(); });
    const dialog = document.getElementById("record-dialog");
    document.getElementById("record-dialog-close").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) {
        const bounds = dialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) { dialog.close(); }
      }
    });
  }

  async function initialize() {
    const params = new URLSearchParams(window.location.search);
    state.datasetId = document.body.getAttribute("data-dataset") || params.get("dataset") || "institutions";
    state.config = DATASETS[state.datasetId];
    if (!state.config) {
      document.getElementById("dataset-title").textContent = "Dataset not found";
      document.getElementById("dataset-description").textContent = "Choose a dataset from the overview page.";
      return;
    }
    document.title = state.config.label + " - Info Source Data Explorer";
    document.getElementById("dataset-title").textContent = state.config.label;
    document.getElementById("dataset-description").textContent = state.config.description;
    document.getElementById("dataset-download").href = state.config.downloadCsv || state.config.csv;
    document.querySelectorAll("[data-dataset-nav]").forEach(function (link) {
      if (link.getAttribute("data-dataset-nav") === state.datasetId) {
        link.setAttribute("current", "");
        link.setAttribute("aria-current", "page");
      }
    });
    wireControls();
    try {
      const responses = await Promise.all([fetch(state.config.csv), fetch("data/site_summary.json")]);
      const response = responses[0];
      if (!response.ok) { throw new Error("HTTP " + response.status); }
      const parsed = parseCsv(await response.text());
      state.headers = parsed.headers;
      state.sourceRows = parsed.rows;
      state.filteredRows = applyUrlFilters(parsed.rows, parsed.headers, params);
      document.getElementById("dataset-row-count").textContent = formatNumber(state.filteredRows.length);
      if (responses[1].ok) {
        const summary = await responses[1].json();
        document.getElementById("snapshot-date").textContent = summary.snapshot_date;
        document.getElementById("footer-snapshot-date").textContent = summary.snapshot_date;
      }
      renderFacets();
      renderActiveFilter();
      refreshVisibleRows();
      if (params.get("open") === "record" && state.visibleRows.length) {
        openRecord(state.visibleRows[0]);
      }
    } catch (error) {
      document.getElementById("table-status").textContent = "The dataset could not be loaded: " + error.message;
    }
  }

  initialize();
})();
