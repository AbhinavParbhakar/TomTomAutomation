# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An async Python tool that pulls traffic study metrics from TomTom's road analytics platform (hosted at `inode.app`) and exports aggregated sample-size data to Excel/CSV. There are no tests or linter configured.

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

Running requires a `.env` file at the repo root with `TOMTOM_USERNAME` and `TOMTOM_PASSWORD` (loaded by `src/constants.py`).

## Architecture

All code lives under `src/`, and imports assume `src/` is on the path (i.e. `from tomtom_interactions...`, not `from src.tomtom_interactions...`), so run scripts via `python src\main.py` rather than as a module from the root.

The pipeline in `src/tomtom_interactions/orchestration.py::get_results` runs end-to-end:

1. **Auth** (`tomtom_interactions/auth.py`) — POSTs credentials to `https://inode.app/api/login/` and captures session cookies in an aiohttp `CookieJar`, which is passed to every subsequent request.
2. **List studies** (`tomtom_interactions/get_traffic_studies.py::get_studies`) — fetches all traffic studies in one request by using an oversized `page_size` (`MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT` in `constants.py`); there is no real pagination handling.
3. **Filter + fetch metrics** — studies whose names contain any string in `STUDY_NAME_FORMATS` (hardcoded in `src/constants.py`) get their per-study stats fetched from `/api/road_analytics/traffic_stats/{id}/`. Each summary's `locationName` is assumed to be exactly `"<MiovisionID> <Direction>"` (two space-separated tokens); anything else raises.
4. **Aggregate + export** (`helpers/formatting.py`) — metrics are grouped by `(project_name, miovision_id, date_range_name)` with `average_sample_size` summed (directions are collapsed), then written to `.csv` or `.xlsx` based on the output path's extension.

Pydantic models are split by concern: `helpers/models.py` holds the studies-list response and the flat `StudyMetrics` output record; `tomtom_interactions/models.py` holds the full `RouteResponse` schema for the per-study stats endpoint. On a `ValidationError`, the raw JSON response and status code are printed before re-raising — that output is the primary debugging aid when the API schema drifts.

A second pipeline, `export_study_csvs` (entry point `src/export_main.py`), downloads the platform's own CSV report for each study whose name matches `EXPORT_STUDY_NAME_FILTERS` (case-insensitive). It uses the async export API in `tomtom_interactions/export_study.py`: trigger `/export/` (returns a `task_id`), poll `/check_export_status/` until `SUCCESS`, then fetch the zip from `/export_download/` and extract it into the save directory. Export query parameters (time_set, date_range, route_id, mode, percentile, ...) default to `DEFAULT_EXPORT_PARAMS` and are study-specific selections mirroring the web UI's export dialog.

To change which studies are pulled or where results are saved, edit `STUDY_NAME_FORMATS` / `EXPORT_STUDY_NAME_FILTERS` in `src/constants.py` and the output paths in `src/main.py` / `src/export_main.py` — there is no CLI argument parsing.
