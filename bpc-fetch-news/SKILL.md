---
name: bpc-fetch-news
description: Fetch paywalled news articles from Bypass Paywalls Clean supported sites with the bpc-fetch CLI and save clean Markdown plus local images. Use when the user asks for The Economist, NYT, WSJ, Financial Times, Wired, Nature, or other paid news site article discovery, crawling, URL filtering, batch download, markdown/image extraction, or bpc-fetch installation troubleshooting.
---

# BPC Fetch News

## Overview

Use the locally cloned `Sophomoresty/bpc-fetch` CLI to discover, filter, crawl, and fetch supported news articles into Markdown directories with downloaded images. Default to the user's local source checkout at `E:\Code_new\bpc-fetch`, unless the current environment shows a different clone.

## First Step

Run a setup check before fetching:

```powershell
bpc-fetch doctor --compact
```

If the command is missing, `doctor` reports issues, Playwright Chromium is absent, or the user tried `pip install bpc-fetch`, run the bundled repair script:

```powershell
powershell -ExecutionPolicy Bypass -File E:\Code_new\skills\bpc-fetch-news\scripts\ensure_bpc_fetch.ps1 -RepoPath E:\Code_new\bpc-fetch -FixPipWarning
```

Important install fact: `bpc-fetch` may not be available from PyPI or the user's configured mirror. The reliable install path is:

```powershell
python -m pip install -e E:\Code_new\bpc-fetch
python -m playwright install chromium
```

## Workflow Decision Tree

- Known article URL: use `fetch`.
- Many known URLs: write a one-URL-per-line file and use `batch --file`.
- Need recent articles from a site: use `discover`, then pass returned URLs to `batch` or follow `next_command`.
- Need keyword search across supported sites: use `crawl` if `BRAVE_API_KEY` is available; otherwise use `discover` by domain or ask the user for URLs.
- Need to confirm support for a publication: use `sites --filter`.
- Need to avoid duplicate work: add `--incremental` to `fetch` or `batch`, then inspect `bpc-fetch history`.

## Commands

List or confirm supported domains:

```powershell
bpc-fetch sites --filter economist.com --limit 10 --compact
bpc-fetch sites --filter nytimes --limit 10 --compact
bpc-fetch sites --filter wsj --limit 10 --compact
bpc-fetch sites --filter ft.com --limit 10 --compact
```

Discover recent articles:

```powershell
bpc-fetch discover economist.com --since today --limit 20 --compact
bpc-fetch discover ft.com --since 7d --limit 20 --compact
```

Fetch one URL, preserving images:

```powershell
bpc-fetch fetch "https://www.example.com/article-url" --out-dir E:\Code_new\articles --compact
```

Batch fetch known URLs:

```powershell
bpc-fetch batch --file E:\Code_new\urls.txt --out-dir E:\Code_new\articles --concurrency 3 --incremental --compact
```

Crawl recent articles by keyword and site list:

```powershell
bpc-fetch crawl "AI regulation" --sites economist.com,ft.com,wsj.com --since 7d --limit 20 --out-dir E:\Code_new\articles --concurrency 3 --progress --compact
```

## Output Handling

- Treat stdout as JSON. Check `ok`, `path`, `images`, `success`, `failed`, `results`, and `next_command`.
- Successful fetch output is `out-dir/article-slug/article-slug.md` plus `out-dir/article-slug/images/`.
- Do not report completion until the JSON says success and the Markdown path exists on disk.
- Keep `--no-images` off unless the user explicitly wants text only.
- Use absolute output directories when the user wants to reuse the downloaded Markdown and images later.

## Troubleshooting

- `pip install bpc-fetch` fails with "No matching distribution found": install from the local clone with `python -m pip install -e E:\Code_new\bpc-fetch`.
- `WARNING: Ignoring invalid distribution ~ip`: run the bundled script with `-FixPipWarning`; it removes only `~ip*` stubs under Python `site-packages`.
- Browser or JS interception errors: run `bpc-fetch install-browser` or `python -m playwright install chromium`.
- `crawl` or `search` returns zero results without site filters: set `BRAVE_API_KEY` or use `discover` for specific domains.
- `sites.js not found`: pass `--sites-js E:\Code_new\bpc-fetch\data\sites.js` or reinstall from the local clone.
