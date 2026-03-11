(function () {
  "use strict";

  const TABLE_DATA_REGISTRY = {};
  let ACTIVE_MODAL_PAYLOAD = null;

  const TABLE_CONFIG = [
    {
      containerId: "spib-table-container",
      csvPath: "data/spib_en_fr.csv",
      tableId: "spib-table",
      tableLabel: "Standard PIBs",
      columns: [],
    },
    {
      containerId: "institutions-table-container",
      csvPath: "data/infosource_institutions_en_fr.csv",
      tableId: "institutions-table",
      tableLabel: "Institutions",
      columns: [
        "gc_orgID",
        "harmonized_name",
        "nom_harmonise",
        "institution_name_en",
        "institution_name_fr",
        "infosource_status_en",
        "infosource_url_en",
        "infosource_status_fr",
        "infosource_url_fr",
      ],
    },
    {
      containerId: "combined-pibs-table-container",
      csvPath: "data/pib_table_en_fr_all.csv",
      tableId: "combined-pibs-table",
      tableLabel: "Combined Standard PIBs",
      columns: [],
    },
  ];

  function sanitizeText(value) {
    if (value === null || value === undefined) {
      return "";
    }
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function isUrl(value) {
    return /^https?:\/\//i.test(String(value || "").trim());
  }

  function renderCell(value) {
    if (value === null || value === undefined || value === "") {
      return "";
    }
    const text = String(value);
    if (isUrl(text)) {
      const safe = sanitizeText(text);
      return '<a href="' + safe + '" target="_blank" rel="noopener">' + safe + "</a>";
    }
    return sanitizeText(text);
  }

  function buildTableHtml(tableId, columns, rows) {
    let html = '<table id="' + tableId + '" class="table table-striped table-hover table-sm wb-tables"';
    html +=
      ' data-wb-tables=\'{"ordering": true, "paging": true, "lengthChange": true, "info": true, "pageLength": 25, "lengthMenu": [10, 25, 50, 100], "scrollX": true, "autoWidth": false}\'';
    html += "><thead><tr>";

    columns.forEach((column) => {
      html += "<th>" + sanitizeText(column) + "</th>";
    });

    html += "</tr></thead><tbody>";
    rows.forEach((row, index) => {
      html += '<tr class="data-row-clickable" data-row-index="' + index + '" tabindex="0">';
      columns.forEach((column) => {
        html += "<td>" + renderCell(row[column]) + "</td>";
      });
      html += "</tr>";
    });
    html += "</tbody></table>";
    return html;
  }

  function getTopHeadingText() {
    const heading = document.querySelector('gcds-heading[tag="h1"]');
    const headingText = heading && heading.textContent ? heading.textContent.trim() : "";
    return headingText || document.title || "Info Source Data Explorer";
  }

  function escapeHtml(value) {
    return sanitizeText(value);
  }

  function humanizeColumn(columnName) {
    return String(columnName || "")
      .replace(/_/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .replace(/\b\w/g, function (ch) {
        return ch.toUpperCase();
      });
  }

  function hasJqueryModal() {
    return !!(window.jQuery && window.jQuery.fn && typeof window.jQuery.fn.modal === "function");
  }

  function getRowModalElement() {
    return document.getElementById("row-detail-modal");
  }

  function getRowModalBackdropElement() {
    return document.getElementById("row-detail-modal-backdrop");
  }

  function ensureRowModalBackdrop() {
    if (getRowModalBackdropElement()) {
      return;
    }
    const backdrop = document.createElement("div");
    backdrop.id = "row-detail-modal-backdrop";
    backdrop.className = "modal-backdrop fade in";
    document.body.appendChild(backdrop);
  }

  function removeRowModalBackdrop() {
    const backdrop = getRowModalBackdropElement();
    if (backdrop && backdrop.parentNode) {
      backdrop.parentNode.removeChild(backdrop);
    }
  }

  function isRowModalVisible() {
    const modal = getRowModalElement();
    if (!modal) {
      return false;
    }
    return modal.style.display === "block";
  }

  function openRowDetailsModalUi() {
    const modal = getRowModalElement();
    if (!modal) {
      return;
    }
    if (hasJqueryModal()) {
      window.jQuery(modal).modal("show");
      return;
    }
    modal.style.display = "block";
    modal.classList.add("in");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("row-detail-modal-open");
    ensureRowModalBackdrop();
  }

  function closeRowDetailsModalUi() {
    const modal = getRowModalElement();
    if (!modal) {
      return;
    }
    if (hasJqueryModal()) {
      window.jQuery(modal).modal("hide");
      return;
    }
    modal.style.display = "none";
    modal.classList.remove("in");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("row-detail-modal-open");
    removeRowModalBackdrop();
  }

  function ensureRowModalStyles() {
    if (document.getElementById("row-detail-modal-style")) {
      return;
    }
    const style = document.createElement("style");
    style.id = "row-detail-modal-style";
    style.textContent = [
      "#row-detail-modal .modal-dialog { margin-top: 3vh; margin-bottom: 3vh; }",
      "#row-detail-modal .modal-content { max-height: 88vh; display: flex; flex-direction: column; }",
      "#row-detail-modal .modal-body { overflow-y: auto; min-height: 0; }",
      "#row-detail-modal .table-responsive { overflow-x: auto; }",
      "#row-detail-modal .row-detail-modal-actions { position: sticky; top: 0; z-index: 2; background: #fff; padding-bottom: .5rem; margin-bottom: .5rem; }",
    ].join("\\n");
    document.head.appendChild(style);
  }

  function ensureRowModal() {
    ensureRowModalStyles();
    if (document.getElementById("row-detail-modal")) {
      return;
    }

    const modalHtml = [
      '<div class="modal fade" id="row-detail-modal" tabindex="-1" role="dialog" aria-labelledby="row-detail-modal-title">',
      '  <div class="modal-dialog modal-lg" role="document">',
      '    <div class="modal-content">',
      '      <div class="modal-header">',
      '        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>',
      '        <h4 class="modal-title" id="row-detail-modal-title">Row details</h4>',
      "      </div>",
      '      <div class="modal-body">',
      '        <div class="row-detail-modal-actions">',
      '          <button type="button" class="btn btn-primary" id="row-detail-download-pdf">Download PDF</button>',
      '          <button type="button" class="btn btn-default" id="row-detail-open-tab">Open in new tab</button>',
      "        </div>",
      '        <p id="row-detail-modal-subtitle" class="small text-muted"></p>',
      '        <div class="table-responsive">',
      '          <table class="table table-bordered table-condensed" id="row-detail-modal-table">',
      "            <tbody></tbody>",
      "          </table>",
      "        </div>",
      "      </div>",
      '      <div class="modal-footer">',
      '        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>',
      "      </div>",
      "    </div>",
      "  </div>",
      "</div>",
    ].join("");

    document.body.insertAdjacentHTML("beforeend", modalHtml);

    const modal = getRowModalElement();
    if (modal) {
      modal.setAttribute("aria-hidden", "true");
      modal.addEventListener("click", function (event) {
        if (!hasJqueryModal() && event.target === modal) {
          closeRowDetailsModalUi();
        }
      });
      modal.querySelectorAll('[data-dismiss="modal"]').forEach(function (button) {
        button.addEventListener("click", function (event) {
          if (!hasJqueryModal()) {
            event.preventDefault();
            closeRowDetailsModalUi();
          }
        });
      });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !hasJqueryModal() && isRowModalVisible()) {
        closeRowDetailsModalUi();
      }
    });

    const downloadButton = document.getElementById("row-detail-download-pdf");
    if (downloadButton) {
      downloadButton.addEventListener("click", function () {
        if (ACTIVE_MODAL_PAYLOAD) {
          downloadRowDetailsPdf(ACTIVE_MODAL_PAYLOAD);
        }
      });
    }

    const openTabButton = document.getElementById("row-detail-open-tab");
    if (openTabButton) {
      openTabButton.addEventListener("click", function () {
        if (ACTIVE_MODAL_PAYLOAD) {
          openRowDetailsInNewTab(ACTIVE_MODAL_PAYLOAD);
        }
      });
    }
  }

  function buildModalRows(columns, row) {
    const bodyRows = [];
    columns.forEach((column) => {
      const rawValue = row[column];
      if (rawValue === undefined || rawValue === null || String(rawValue).trim() === "") {
        return;
      }
      const label = escapeHtml(humanizeColumn(column));
      const value = renderCell(rawValue);
      bodyRows.push("<tr><th>" + label + "</th><td>" + value + "</td></tr>");
    });
    return bodyRows.length ? bodyRows.join("") : '<tr><td colspan="2">No row details available.</td></tr>';
  }

  function showRowDetailsModal(tableId, rowIndex) {
    const dataset = TABLE_DATA_REGISTRY[tableId];
    if (!dataset || !dataset.rows || !dataset.columns) {
      return;
    }

    const row = dataset.rows[rowIndex];
    if (!row) {
      return;
    }

    const possibleTitle =
      row.title_en ||
      row.title ||
      row.harmonized_name ||
      row.institution_name_en ||
      dataset.tableLabel ||
      "Row details";

    ACTIVE_MODAL_PAYLOAD = {
      tableLabel: dataset.tableLabel || tableId,
      rowTitle: String(possibleTitle),
      columns: dataset.columns.slice(),
      row: row,
    };

    const modalTitle = document.getElementById("row-detail-modal-title");
    const modalSubtitle = document.getElementById("row-detail-modal-subtitle");
    const modalBody = document.querySelector("#row-detail-modal-table tbody");
    if (!modalTitle || !modalSubtitle || !modalBody) {
      return;
    }

    modalTitle.textContent = ACTIVE_MODAL_PAYLOAD.rowTitle;
    modalSubtitle.textContent = ACTIVE_MODAL_PAYLOAD.tableLabel;
    modalBody.innerHTML = buildModalRows(dataset.columns, row);
    openRowDetailsModalUi();
  }

  function wireRowModal(tableId) {
    const table = document.getElementById(tableId);
    if (!table) {
      return;
    }

    table.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        return;
      }
      const row = event.target.closest("tr.data-row-clickable");
      if (!row) {
        return;
      }
      const rowIndex = Number(row.getAttribute("data-row-index"));
      if (!Number.isNaN(rowIndex)) {
        showRowDetailsModal(tableId, rowIndex);
      }
    });

    table.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }
      const row = event.target.closest("tr.data-row-clickable");
      if (!row) {
        return;
      }
      event.preventDefault();
      const rowIndex = Number(row.getAttribute("data-row-index"));
      if (!Number.isNaN(rowIndex)) {
        showRowDetailsModal(tableId, rowIndex);
      }
    });
  }

  function addPdfHeader(doc, pageTitle) {
    const pageWidth = doc.internal.pageSize.getWidth();
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text("Government of Canada", 40, 38);
    doc.setFontSize(12);
    doc.text(pageTitle, 40, 56);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text("Generated " + new Date().toISOString().slice(0, 10), 40, 72);
    doc.setDrawColor(140, 140, 140);
    doc.line(40, 80, pageWidth - 40, 80);
    return 102;
  }

  function safeFileName(value) {
    return String(value || "row-details")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 70) || "row-details";
  }

  function toMarkdownValue(value) {
    const text = String(value == null ? "" : value).trim();
    if (!text) {
      return "";
    }
    if (isUrl(text)) {
      return "[" + text + "](" + text + ")";
    }
    return text;
  }

  function buildRowMarkdown(payload) {
    const lines = [];
    lines.push("# " + (payload.rowTitle || "Row details"));
    lines.push("");
    lines.push("_Dataset: " + (payload.tableLabel || "") + "_");
    lines.push("");

    payload.columns.forEach(function (column) {
      const value = toMarkdownValue(payload.row[column]);
      if (!value) {
        return;
      }
      lines.push("## " + humanizeColumn(column));
      lines.push("");
      lines.push(value);
      lines.push("");
    });

    return lines.join("\\n");
  }

  function buildNewTabTemplate(payload, markdown) {
    const pageTitle = sanitizeText(getTopHeadingText());
    const rowTitle = sanitizeText(payload.rowTitle || "Row details");
    const safeMarkdown = JSON.stringify(markdown).replace(/</g, "\\u003c");

    return [
      "<!DOCTYPE html>",
      '<html dir="ltr" lang="en">',
      "<head>",
      '  <meta charset="utf-8" />',
      '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
      "  <title>" + rowTitle + " - " + pageTitle + "</title>",
      '  <link rel="stylesheet" href="https://cdn.design-system.canada.ca/@gcds-core/css-shortcuts@1.0.1/dist/gcds-css-shortcuts.min.css" />',
      '  <link rel="stylesheet" href="https://cdn.design-system.canada.ca/@gcds-core/components@1.0.0/dist/gcds/gcds.css" />',
      '  <script type="module" src="https://cdn.design-system.canada.ca/@gcds-core/components@1.0.0/dist/gcds/gcds.esm.js"></script>',
      '  <link rel="stylesheet" href="https://wet-boew.github.io/themes-dist/GCWeb/GCWeb/css/theme.min.css" />',
      "  <style>",
      "    #markdown-content h1, #markdown-content h2, #markdown-content h3 { margin-top: 1.25rem; }",
      "    #markdown-content pre, #markdown-content code { white-space: pre-wrap; word-break: break-word; }",
      "    #markdown-content table { width: 100%; }",
      "  </style>",
      "</head>",
      '<body vocab="http://schema.org/" typeof="WebPage">',
      '  <gcds-header lang-href="#" skip-to-href="#main-content">',
      '    <gcds-search slot="search"></gcds-search>',
      '    <gcds-breadcrumbs slot="breadcrumb">',
      '      <gcds-breadcrumbs-item href="index.html">' + pageTitle + "</gcds-breadcrumbs-item>",
      '      <gcds-breadcrumbs-item href="#">Modal export</gcds-breadcrumbs-item>',
      "    </gcds-breadcrumbs>",
      "  </gcds-header>",
      '  <gcds-container id="main-content" layout="page" tag="main">',
      '    <section><gcds-heading tag="h1">' + rowTitle + "</gcds-heading></section>",
      '    <section><div id="markdown-content"></div></section>',
      "  </gcds-container>",
      '  <gcds-footer display="full"></gcds-footer>',
      '  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>',
      "  <script>",
      "    const markdown = " + safeMarkdown + ";",
      "    const container = document.getElementById('markdown-content');",
      "    if (window.marked && container) {",
      "      container.innerHTML = marked.parse(markdown);",
      "    } else if (container) {",
      "      container.innerHTML = '<pre>' + markdown.replace(/[&<>]/g, function(c){ return ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]); }) + '</pre>';",
      "    }",
      "  </script>",
      "</body>",
      "</html>",
    ].join("\\n");
  }

  function openRowDetailsInNewTab(payload) {
    const newTab = window.open("", "_blank");
    if (!newTab) {
      alert("Unable to open a new tab. Please allow pop-ups for this site.");
      return;
    }
    const markdown = buildRowMarkdown(payload);
    const html = buildNewTabTemplate(payload, markdown);
    newTab.document.open();
    newTab.document.write(html);
    newTab.document.close();
  }

  function downloadRowDetailsPdf(payload) {
    if (!window.jspdf || !window.jspdf.jsPDF) {
      alert("PDF library is unavailable.");
      return;
    }

    const doc = new window.jspdf.jsPDF({ unit: "pt", format: "letter" });
    const pageTitle = getTopHeadingText();
    const pageHeight = doc.internal.pageSize.getHeight();
    const leftX = 40;
    const labelX = 40;
    const valueX = 220;
    const valueWidth = doc.internal.pageSize.getWidth() - valueX - 40;
    let y = addPdfHeader(doc, pageTitle);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    const titleLines = doc.splitTextToSize(payload.rowTitle || payload.tableLabel || "Row details", valueWidth + 140);
    doc.text(titleLines, leftX, y);
    y += titleLines.length * 14 + 6;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    const subtitleLines = doc.splitTextToSize(payload.tableLabel || "", valueWidth + 140);
    doc.text(subtitleLines, leftX, y);
    y += subtitleLines.length * 14 + 14;

    payload.columns.forEach((column) => {
      const rawValue = payload.row[column];
      const value = rawValue === null || rawValue === undefined ? "" : String(rawValue).trim();
      if (!value) {
        return;
      }

      const label = humanizeColumn(column) + ":";
      const valueLines = doc.splitTextToSize(value, valueWidth);
      const lineHeight = 12;
      const blockHeight = Math.max(lineHeight, valueLines.length * lineHeight) + 6;

      if (y + blockHeight > pageHeight - 40) {
        doc.addPage();
        y = addPdfHeader(doc, pageTitle);
      }

      doc.setFont("helvetica", "bold");
      doc.text(label, labelX, y);
      doc.setFont("helvetica", "normal");
      doc.text(valueLines, valueX, y);
      y += blockHeight;
    });

    const fileBase = safeFileName((payload.row.bank_number_key || payload.rowTitle || "row-details") + "-details");
    doc.save(fileBase + ".pdf");
  }

  function buildColumnSelectorHtml(selectorId, columns) {
    let html = '<details class="mrgn-bttm-md">';
    html += "<summary>Show or hide columns</summary>";
    html += '<div id="' + selectorId + '" class="mrgn-tp-sm">';
    html +=
      '<p class="mrgn-bttm-sm"><button type="button" data-action="all" class="btn btn-default btn-xs mrgn-rght-sm">Show all</button><button type="button" data-action="none" class="btn btn-default btn-xs">Hide all</button></p>';
    columns.forEach((column, index) => {
      html +=
        '<label style="display:inline-block; margin:0 1rem .5rem 0;"><input type="checkbox" data-col-index="' +
        index +
        '" checked /> ' +
        sanitizeText(column) +
        "</label>";
    });
    html += "</div></details>";
    return html;
  }

  function hideShowColumnFallback(table, colIndex, visible) {
    const rows = table.querySelectorAll("tr");
    rows.forEach((row) => {
      const cells = row.children;
      if (cells[colIndex]) {
        cells[colIndex].style.display = visible ? "" : "none";
      }
    });
  }

  function applyColumnVisibility(tableId, colIndex, visible) {
    const table = document.getElementById(tableId);
    if (!table) {
      return;
    }

    if (
      window.jQuery &&
      window.jQuery.fn &&
      window.jQuery.fn.dataTable &&
      window.jQuery.fn.dataTable.isDataTable(table)
    ) {
      const api = window.jQuery(table).DataTable();
      api.column(colIndex).visible(visible, false);
      api.columns.adjust().draw(false);
      return;
    }
    hideShowColumnFallback(table, colIndex, visible);
  }

  function wireColumnSelector(selectorId, tableId) {
    const selector = document.getElementById(selectorId);
    if (!selector) {
      return;
    }

    selector.addEventListener("change", function (event) {
      const target = event.target;
      if (!target || target.type !== "checkbox") {
        return;
      }
      const idx = Number(target.getAttribute("data-col-index"));
      if (Number.isNaN(idx)) {
        return;
      }
      applyColumnVisibility(tableId, idx, target.checked);
    });

    selector.addEventListener("click", function (event) {
      const target = event.target;
      if (!target || target.tagName !== "BUTTON") {
        return;
      }
      const action = target.getAttribute("data-action");
      if (!action) {
        return;
      }
      const checkboxes = selector.querySelectorAll('input[type="checkbox"][data-col-index]');
      const visible = action === "all";
      checkboxes.forEach((checkbox) => {
        checkbox.checked = visible;
        const idx = Number(checkbox.getAttribute("data-col-index"));
        if (!Number.isNaN(idx)) {
          applyColumnVisibility(tableId, idx, visible);
        }
      });
    });
  }

  function loadCsvTable(config) {
    const container = document.getElementById(config.containerId);
    if (!container) {
      return;
    }

    container.innerHTML = "<p>Loading table...</p>";
    Papa.parse(config.csvPath, {
      download: true,
      header: true,
      skipEmptyLines: "greedy",
      complete: function (results) {
        const rows = results.data || [];
        if (!rows.length) {
          container.innerHTML = "<p>No data found.</p>";
          return;
        }

        const columns =
          Array.isArray(config.columns) && config.columns.length > 0
            ? config.columns.filter((col) => Object.prototype.hasOwnProperty.call(rows[0], col))
            : Object.keys(rows[0]);
        if (!columns.length) {
          container.innerHTML = "<p>Expected columns were not found in the CSV.</p>";
          return;
        }

        TABLE_DATA_REGISTRY[config.tableId] = {
          tableLabel: config.tableLabel || config.tableId,
          columns: columns,
          rows: rows,
        };

        const selectorId = config.tableId + "-column-selector";
        container.innerHTML =
          buildColumnSelectorHtml(selectorId, columns) + buildTableHtml(config.tableId, columns, rows);
        wireColumnSelector(selectorId, config.tableId);
        wireRowModal(config.tableId);
        if (window.jQuery) {
          window.jQuery("#" + config.tableId).trigger("wb-init.wb-tables");
        }
      },
      error: function (err) {
        container.innerHTML = "<p>Failed to load CSV: " + sanitizeText(err.message || String(err)) + "</p>";
      },
    });
  }

  ensureRowModal();
  TABLE_CONFIG.forEach(loadCsvTable);
})();
