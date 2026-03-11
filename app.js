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

  function ensureRowModal() {
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
      '        <p id="row-detail-modal-subtitle" class="small text-muted"></p>',
      '        <div class="table-responsive">',
      '          <table class="table table-bordered table-condensed" id="row-detail-modal-table">',
      "            <tbody></tbody>",
      "          </table>",
      "        </div>",
      "      </div>",
      '      <div class="modal-footer">',
      '        <button type="button" class="btn btn-primary" id="row-detail-download-pdf">Download PDF</button>',
      '        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>',
      "      </div>",
      "    </div>",
      "  </div>",
      "</div>",
    ].join("");

    document.body.insertAdjacentHTML("beforeend", modalHtml);

    const downloadButton = document.getElementById("row-detail-download-pdf");
    if (downloadButton) {
      downloadButton.addEventListener("click", function () {
        if (ACTIVE_MODAL_PAYLOAD) {
          downloadRowDetailsPdf(ACTIVE_MODAL_PAYLOAD);
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
    if (window.jQuery) {
      window.jQuery("#row-detail-modal").modal("show");
    }
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
