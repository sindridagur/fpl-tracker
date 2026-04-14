# â½ FPL Gap Tracker

A GitHub Pages site that tracks the points gap between two Fantasy Premier League managers across the season. Data is fetched automatically each week via GitHub Actions and committed back to the repo.

## Live Site

`https://<your-github-username>.github.io/fpl-tracker/`

## How It Works

1. A scheduled GitHub Actions workflow runs every **Tuesday at 08:00 UTC** (after GW results settle).
2. `scripts/fetch_fpl.py` calls the FPL API for both managers and writes the results to `data/fpl_data.json`.
3. The workflow commits the updated JSON back to `main`.
4. `index.html` reads `data/fpl_data.json` and renders the gap chart + table.

You can also trigger the workflow manually from **Actions â Fetch FPL Data â Run workflow**.

## Repository Variables

Set these under **Settings â Secrets and variables â Actions â Variables**:

| Variable | Description |
|---|---|
| `MANAGER_1_ID` | FPL entry ID for Manager 1 |
| `MANAGER_2_ID` | FPL entry ID for Manager 2 |

## File Structure

```
fpl-tracker/
âââ index.html                        # GitHub Pages frontend
âââ README.md
âââ data/
â   âââ fpl_data.json                 # Auto-generated; committed by CI
âââ scripts/
â   âââ fetch_fpl.py                  # FPL data fetcher
âââ .github/
    âââ workflows/
        âââ fetch_fpl.yml             # GitHub Actions workflow
```

## Setup

1. Fork or clone this repo.
2. Add `MANAGER_1_ID` and `MANAGER_2_ID` as repository **Variables** (not Secrets).
3. Enable GitHub Pages: **Settings â Pages â Deploy from branch â main / (root)**.
4. Run the workflow manually once to generate the initial `data/fpl_data.json`.
5. The workflow then runs automatically every Tuesday.
