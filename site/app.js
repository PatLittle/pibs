(function () {
  "use strict";

  const TABLE_CONFIG = [
    {
      containerId: "spib-table-container",
      csvPath: "data/spib_en_fr.csv",
      tableId: "spib-table",
      columns: [
        "bank_number_key",
        "entry_title_en",
        "entry_title_fr",
        "description_en",
        "description_fr",
        "date_last_modified",
        "url_en",
        "url_fr",
      ],
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
    html += ' data-wb-tables=\'{"ordering": true, "pageLength": 25}\'';
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

        const columns = config.columns.filter((col) => Object.prototype.hasOwnProperty.call(rows[0], col));
        if (!columns.length) {
          container.innerHTML = "<p>Expected columns were not found in the CSV.</p>";
          return;
        }

        container.innerHTML = buildTableHtml(config.tableId, columns, rows);
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

