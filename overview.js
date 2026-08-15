(function () {
  "use strict";

  function formatNumber(value) {
    return new Intl.NumberFormat("en-CA").format(Number(value || 0));
  }

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value;
    }
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderBars(containerId, items, labelKey, valueKey, linkBuilder) {
    const container = document.getElementById(containerId);
    if (!container || !items.length) {
      return;
    }
    const maximum = Math.max.apply(null, items.map(function (item) { return Number(item[valueKey]); }));
    container.innerHTML = items.map(function (item) {
      const label = escapeHtml(item[labelKey]);
      const value = Number(item[valueKey]);
      const labelHtml = linkBuilder
        ? '<a href="' + escapeHtml(linkBuilder(item)) + '">' + label + "</a>"
        : label;
      return [
        '<div class="bar-row">',
        '  <div class="bar-row__label"><span>' + labelHtml + "</span><strong>" + formatNumber(value) + "</strong></div>",
        '  <div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:' + (100 * value / maximum).toFixed(1) + '%"></div></div>',
        "</div>",
      ].join("");
    }).join("");
  }

  fetch("data/site_summary.json")
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Summary request failed");
      }
      return response.json();
    })
    .then(function (summary) {
      setText("stat-institutions", formatNumber(summary.headline.institutions));
      setText("stat-pibs", formatNumber(summary.headline.institution_pibs));
      setText("stat-classes", formatNumber(summary.headline.institution_classes));
      setText("stat-links", formatNumber(summary.headline.pib_cor_links));
      setText("snapshot-date", summary.snapshot_date);
      setText("footer-snapshot-date", summary.snapshot_date);

      Object.keys(summary.datasets).forEach(function (key) {
        setText("dataset-count-" + key.replace(/_/g, "-"), formatNumber(summary.datasets[key]));
      });

      setText("quality-pibs", summary.quality.pibs_bilingual_percent + "%");
      setText("quality-pibs-note", formatNumber(summary.quality.pibs_bilingual) + " bilingual title pairs");
      setText("quality-classes", summary.quality.classes_bilingual_percent + "%");
      setText("quality-classes-note", formatNumber(summary.quality.classes_bilingual) + " bilingual name pairs");
      setText("quality-links", summary.quality.links_resolved_percent + "%");
      setText("quality-links-note", formatNumber(summary.quality.links_resolved) + " references resolved");
      setText("quality-sources", (100 * summary.collection.any_source / summary.collection.collectable_institutions).toFixed(1) + "%");
      setText("quality-sources-note", formatNumber(summary.collection.any_source) + " of " + formatNumber(summary.collection.collectable_institutions) + " collectable institutions");

      setText("coverage-complete", formatNumber(summary.collection.collection_completed));
      setText("coverage-all", formatNumber(summary.collection.all_four_sources));
      setText("coverage-any", formatNumber(summary.collection.any_source));
      setText("coverage-none", formatNumber(summary.collection.no_successful_source));
      setText("coverage-no-url", formatNumber(summary.collection.no_source_urls));
      setText("coverage-failing", formatNumber(summary.collection.unique_failing_urls));

      renderBars("pib-type-bars", summary.pib_types, "name", "count");
      renderBars(
        "institution-bars",
        summary.top_institutions,
        "name_en",
        "total",
        function (item) {
          return "table.html?dataset=institutions&institution_id=" + encodeURIComponent(item.institution_id);
        }
      );
    })
    .catch(function () {
      const status = document.getElementById("overview-status");
      if (status) {
        status.textContent = "Overview statistics could not be loaded. The dataset links remain available.";
      }
    });
})();
