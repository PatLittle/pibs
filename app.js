(function () {
  "use strict";

  const TABLE_CONFIG = [
    {
      containerId: "spib-table-container",
      csvPath: "data/spib_en_fr.csv",
      tableId: "spib-table",
      columns: [],
    },
    {
      containerId: "institutions-table-container",
      csvPath: "data/infosource_institutions_en_fr.csv",
      tableId: "institutions-table",
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
    rows.forEach((row) => {
      html += "<tr>";
      columns.forEach((column) => {
        html += "<td>" + renderCell(row[column]) + "</td>";
      });
      html += "</tr>";
    });
    html += "</tbody></table>";
    return html;
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

        const selectorId = config.tableId + "-column-selector";
        container.innerHTML =
          buildColumnSelectorHtml(selectorId, columns) + buildTableHtml(config.tableId, columns, rows);
        wireColumnSelector(selectorId, config.tableId);
        if (window.jQuery) {
          window.jQuery("#" + config.tableId).trigger("wb-init.wb-tables");
        }
      },
      error: function (err) {
        container.innerHTML = "<p>Failed to load CSV: " + sanitizeText(err.message || String(err)) + "</p>";
      },
    });
  }

  TABLE_CONFIG.forEach(loadCsvTable);
})();
