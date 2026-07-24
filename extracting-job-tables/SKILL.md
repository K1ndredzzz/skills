---
name: extracting-job-tables
description: Use when extracting Tencent Docs, Feishu sheets or bitables, and KDocs job tables through a user's logged-in browser, or when delivering auditable CSV results and a table-level campus-recruitment quality ranking.
---

# Extracting Job Tables

## Overview

Treat a shared job table as a versioned data source, not a web page to scroll. Read it through the user-authorized browser session, preserve source evidence, and make each CSV independently auditable.

## When to Use

- Tencent Docs SmartSheet/Sheet, Feishu Sheet/Bitable, or KDocs tables need logged-in extraction.
- A grid is virtualized, truncated, redirected, or has thousands of records.
- The result must preserve old outputs and support a later ranking of source-table quality.

Do not use for choosing jobs for a person. A table-quality ranking is a ranking of sources, not rows, companies, or candidates.

## Required Workflow

1. Read `opencli-browser`; run `opencli doctor`; create one named browser session. Inspect URL, title, and state before every new source.
2. Create a timestamped output directory. Never overwrite or rename prior outputs. Keep a per-source staging directory until CSV validation finishes.
3. Record requested URL, final URL, title, platform, table/sheet/view name and IDs, extraction time, raw record count, written rows, and columns.
4. Prefer authenticated page APIs or network responses over DOM scrolling. Browser `eval` is read-only; use it only to fetch and return source data with the current browser cookies.
5. Write UTF-8 with BOM CSV, then re-read it with a CSV parser. Require every row to have the header’s column count.
6. Write `manifest.json` and `提取说明.md`. A partial/failed source stays explicit; do not present it as complete.

## Platform Playbook

| Source | Read path | Reusable local tool |
|---|---|---|
| Feishu Bitable | `clientvars` for schema, then paged `records` response | `D:\Code_new\employment\求职信息池\work\ingest_feishu_bitable.py` |
| Feishu Sheet | authenticated `client_vars` and `sub_block` responses | `D:\Code_new\employment\求职信息池\work\ingest_opencli_feishu_sheet.py` |
| Tencent SmartSheet | captured `clientVarsCallback(...)` JSONP responses | `D:\Code_new\employment\求职信息池\work\ingest_opencli_qq_jsonp.py` |
| Rendered sheet rows | page-context row payload | `D:\Code_new\employment\求职信息池\work\ingest_opencli_sheet_rows.py` |

### Feishu Bitable

1. Fetch `.../clientvars?tableID=<tableId>...` in the page context. Gzip/Base64-decode `data.table` to obtain `meta.rev`, `fieldMap`, and `viewMap[viewId].property.fields`.
2. Fetch `.../records?...&tableRev=<rev>&offset=<n>&limit=3000...` from offset `0` until the unique-record count equals `tableRecordNum`/`recordsNum`.
3. Each browser result supplied to `ingest_feishu_bitable.py collect` must be one compact JSON line: one `kind: schema`, followed by `kind: records` pages. The script decodes `data.records`, deduplicates record IDs, and records used option IDs.
4. Before `write`, derive select labels from `fieldMap[fieldId].property.options`; pipe `{ "options": ... }` into `write`. Never expose browser cookies.

### Redirects and Login Dialogs

Use this result contract:

| Observable state | Result |
|---|---|
| Requested IDs resolve to the expected current table/view | `success` |
| Page redirects, but final table/view is verified and recorded | `success_with_redirect` plus requested and actual IDs |
| Login modal is visible but authenticated data APIs return complete data after closing a dismissible modal | continue and document evidence |
| Final table/view cannot be identified, or record count cannot be read | `blocked`/`source_uncertain`; do not silently substitute another table |

## Output Contract

`<timestamp>_<scope>/` contains numbered CSV files, `manifest.json`, and `提取说明.md`. CSV values preserve source text, field order, and optional preamble rows; do not merge, deduplicate, normalize, or remove records unless the user asks.

`manifest.json` must include: source URL, final URL if different, platform, title, sheet/table/view, status, source record count, written rows/columns, output file, and notes. For re-ranked copies, add `rank`, original file, ranking scope, and reason.

Validate: expected files exist; BOM is `EF BB BF`; CSV parses; rows are rectangular; manifest references existing files; source count and collected unique records agree when the API reports both.

If the request says “汇入前8个表” after new links are supplied, it means **add the new sources to the existing eight-source catalogue**. Keep all 12 successful source CSVs in the new directory, then number all 12 by quality. It does not mean “retain only the quality top 8” unless the user explicitly says to filter to top 8.

## Ranking Table Quality

When asked for “27届秋招信息表质量”, rank the **12 source tables**, not individual jobs. Use: 27届 coverage, autumn/early-batch coverage, recent update evidence, application-link and deadline completeness, useful filter fields, and redundant/noise columns. Raw row count is supporting evidence only.

For summer internships, call an item an **open signal** only when it is recently updated and its deadline says `招满即止/尽快投递` or is not past. This is not proof that the external application link still works; say so.

## Known Failure Modes

| Baseline failure | Required response |
|---|---|
| Native export is assumed available | Inspect network/API first; UI exports are an optional fallback. |
| Virtualized DOM is scraped | Use paged source responses and compare unique IDs with source count. |
| Redirected view is treated as the requested one | Record requested versus actual IDs and status. |
| “Quality” becomes a job-recommendation score | Produce a per-table ranking with reasons; do not score jobs. |
| Existing output is replaced | Make a new timestamped directory and copy only after validation. |

## Handoff Checklist

- [ ] All requested sources have an explicit status.
- [ ] Each successful CSV is UTF-8 BOM and rectangular.
- [ ] Counts, IDs, source URLs, and redirects are in the manifest.
- [ ] Old outputs remain intact.
- [ ] Ranking scope is table quality; summer “open signals” are qualified.
