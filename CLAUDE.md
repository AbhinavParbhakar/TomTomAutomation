# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An async Python tool that works with traffic studies on the iNode road analytics platform (`inode.app`, TomTom probe data): it aggregates sample-size metrics to Excel/CSV, downloads per-study CSV report exports, and mass-creates study reports from an existing study used as a template. There are no tests or linter configured.

## Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Recompile the lockfile after editing requirements.in (uses uv)
uv pip compile .\requirements.in -o .\requirements.txt

# Run the metrics-aggregation pipeline (from repo root; imports resolve relative to src/)
python src\main.py

# Run the raw CSV export pipeline (downloads per-study report zips into exports/)
python src\export_main.py
```

Running requires a `.env` file at the repo root with `TOMTOM_API_TOKEN` (loaded by `src/constants.py`). The token comes from the iNode dashboard: Settings > My Profile > API Access (Owner role only). Never commit the token; `.env` is git-ignored.

## The iNode v1 Flow API

All requests go to the documented REST API under `https://inode.app/api/v1/flow` (`INODE_API_BASE` in `constants.py`) with an `Authorization: Token <key>` header (`tomtom_interactions/auth.py::get_auth_headers`). There is no login/cookie/CSRF handling anywhere.

Endpoints used:

- `GET /ts/?no_pagination=true` — all studies (`get_traffic_studies.py::get_studies`)
- `GET /ts/{id}/` — study detail incl. `sample_detail` metrics (`get_route_response`)
- `GET /ts/{id}/results/?export_format=csv&selection=route` — returns the CSV report as a zip, synchronously (`export_study.py::download_study_csv`)
- `POST /ts/` — create a study report (`post_template_body.py::post_template`)

Swagger schema: `https://inode.app/api/v1/flow/docs/?format=openapi` (works with the token header; the human-readable `/docs/` page needs a browser login).

API quirks discovered by testing (do not "fix" these blindly):

- **Never send `is_draft: true` to `POST /ts/`** — the server's draft path 500s with an HTML page. Omit the field entirely (`post_template` uses `exclude_none=True` and `TemplateBody` has no `is_draft`).
- A 500 with an HTML body from `POST /ts/` means a body-shape problem; a JSON 400 is a real validation message worth reading (e.g. date ranges must overlap the time sets' days-of-week).
- `messages` in the detail response is `""` when empty, a list otherwise.
- The API rate-limits: 429 with `retry_after_seconds` in the JSON body.
- Detail responses omit per-network-item `timezone`; POST bodies should include it on each item.

## Architecture

All code lives under `src/`, and imports assume `src/` is on the path (i.e. `from tomtom_interactions...`), so run scripts via `python src\main.py` rather than as a module from the root.

Three pipelines in `src/tomtom_interactions/orchestration.py`:

1. **`get_results`** (entry `src/main.py`) — lists studies, keeps those whose names contain any of `STUDY_NAME_FORMATS` (`constants.py`), pulls each study's `sample_detail` summaries, parses `locationName` as `"<MiovisionID> <Direction>"`, then groups by `(project_name, miovision_id, date_range_name)` summing `average_sample_size` (directions collapse) and writes `.csv`/`.xlsx` based on the output path's extension (`helpers/formatting.py`).
2. **`export_study_csvs`** (entry `src/export_main.py`) — downloads the platform's CSV report zip for each study matching `EXPORT_STUDY_NAME_FILTERS` (case-insensitive) and extracts it into the save dir.
3. **`create_template_copies`** (commented out in `src/main.py`) — finds template studies named `{TEMPLATE_FILTER_PREFIX}{N} (2024-01-01-2024-01-24)`, and for each generates reports covering `TEMPLATE_START_DATE`→`TEMPLATE_END_DATE` in `DAYS_PER_PROJECT`-day chunks (one single-day date-range per day, `helpers/get_templates.py`), POSTing each. The source study's `dayToTimeRanges` time sets are converted to the POST's advanced `time_groups` form (`convert_time_sets`); a template source must have time sets covering all days of the week or the platform rejects non-overlapping date ranges.

Pydantic models are split by concern: `helpers/models.py` holds the study-list item (`StudyInfo`), the flat `StudyMetrics` output record, and `DateRange`; `tomtom_interactions/models.py` holds the detail-response schema (`RouteResponse`) and the `POST /ts/` body (`TemplateBody`). On a `ValidationError`, the raw JSON is appended to `errors.json` and the status code printed before re-raising — that output is the primary debugging aid when the API schema drifts.

To change which studies are pulled or where results are saved, edit the constants in `src/constants.py` and the output paths in `src/main.py` / `src/export_main.py` — there is no CLI argument parsing.
