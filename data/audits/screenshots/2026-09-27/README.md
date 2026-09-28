# Canadian High Arctic Research Station Info Source visual check

Captured on 2026-09-27 in a 1440-pixel-wide headless Chromium browser, using
the owner-supplied English and French URLs. The matching machine-readable URL
results are in `../../institution_registry_url_audit_2026-09-27.json`.

| Language | Requested URL | Observed response | Screenshot |
| --- | --- | --- | --- |
| English | https://www.canada.ca/en/polar-knowledge/infosource.html | HTTP 200. The page contains only “This is a content page” and no Info Source holdings. | [chars-en-placeholder.png](chars-en-placeholder.png) |
| French | https://www.canada.ca/fr/savoir-polaire/infosource.html | HTTP 404, “Page non trouvée”. | [chars-fr-404.png](chars-fr-404.png) |

Neither page displayed a “Request Rejected” message. These images document
the actual incomplete/error states, not institution-specific PIBs or classes.
