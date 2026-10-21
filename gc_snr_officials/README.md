# GC Senior Officials Transparency

Standalone explorer: https://patlittle.github.io/pibs/gc_snr_officials/

This directory owns its HTML, CSS, browser JavaScript, CSVs, compressed snapshots,
collector, and tests. It has no runtime dependency on the PIBS app, ChatGPT Sites,
a Worker, or an external API. Serve this directory over HTTP; opening the HTML as
`file://` cannot load the local data files.

## Authority data

`sources.json` lists the seven designated-role sources. The collector writes each
source to its own UTF-8 CSV in `data/`, plus `appointments.csv` for the appointments
index. Appointment rows include organization-profile dates and a structured
`appointment_details` column for multiple roles. All CSVs carry source links and
access dates. Effective/appointment dates remain separate from access dates.

`data/manifest.json` records the last successful refresh, row count, and status
for each source. Empty/failed scrapes and declines of more than 50% retain the last
good CSV and produce warnings. Failed appointment profile requests retain prior
profile details when possible; the manifest lists affected URLs. Unavailable dates
remain unknown. The initial migration included designated-role snapshots from August 27, 2026
and an October 21, 2026 appointment collection. The Action refreshes all eight
sources, including TBS definition lists and audit committee tables. Rejected upstream requests do not silently erase good data.

Travel/hospitality combinations and Orders in Council are compressed JSON snapshots
from August 27, 2026; the authority refresh does not update these. The browser
retains existing matching, counts, filters, sorting, date windows and detail dialogs.
The About dialog explains the pipeline and provides CSV links and source status.

## Refresh and publish

`.github/workflows/gc-snr-officials.yml` runs daily at **08:00 UTC**, on changes to
this directory/its workflow, and via **Run workflow**. It tests the standalone code,
collects authority sources with at most six concurrent profile requests, commits
changed CSVs and the manifest to `main`, and deploys only this app to
`pages/gc_snr_officials`. Publishing occurs in the same workflow because commits
made with `GITHUB_TOKEN` do not trigger another push workflow.

All Pages writers share the existing `pages-branch-deploy` concurrency group.
The main site's `clean-exclude` list preserves `gc_snr_officials/**`. This app's
workflow neither builds nor validates the other PIBS sections and publishes only
its target directory. The Pages source remains the existing `pages` branch. Scheduled/manual runs and
collector/configuration changes refresh upstream sources; UI-only pushes reuse
committed data. Queued jobs check out current main so they do not republish stale
CSVs after another job refreshes them.

## Local checks

From the repository root:

```sh
python -m pip install -r gc_snr_officials/requirements.txt
python -m unittest discover -s gc_snr_officials/tests -p 'test_*.py'
node --test gc_snr_officials/tests/app.test.mjs
python gc_snr_officials/scripts/validate.py
python gc_snr_officials/scripts/refresh_sources.py
python gc_snr_officials/scripts/validate.py --require-appointments
```

The tests run offline, covering source schemas, appointment dates, row spans,
failed-source retention, CSV quoting, all sort directions, data totals, local asset
paths, and dialog/OIC behaviour. The collector is the only command requiring live
source access. A first publication requires a nonempty appointments CSV.
