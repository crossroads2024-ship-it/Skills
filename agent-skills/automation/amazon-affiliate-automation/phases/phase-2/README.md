# Phase 2 — Research operations

Phase 2 extends Phase 1 with a local SQLite database and human review workflow.

## Features

- SQLite records for products, evidence, score history and daily scout runs.
- CSV import and re-import by product ID.
- Ranked candidate review with component scores and warnings.
- Human status decisions: `RESEARCH`, `SHORTLIST`, `REJECT`, `APPROVED_FOR_CONTENT`.
- Export of reviewed shortlist records.
- No network calls, scraping, paid APIs or automatic publishing.

## Quick start (Windows PowerShell)

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db daily
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db import .\templates\product_candidates.csv
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db rank
```

Set a decision only after human review:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db decide PRODUCT_ID APPROVED_FOR_CONTENT --notes "Approved for draft creation"
```

Export:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db export --out .\amazon_scout_shortlist.csv
```

The SQLite database and any candidate exports are local working data and should not be committed to GitHub.
