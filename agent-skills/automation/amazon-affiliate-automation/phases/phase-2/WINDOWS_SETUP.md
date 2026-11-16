# Windows 11 setup

## Requirements

Python 3.9 or later. The engine uses only the Python standard library.

## Run from the Phase 2 directory

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db daily
```

Import candidate data:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db import .\templates\product_candidates.csv
```

Rank candidates:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db rank
```

Set a reviewed candidate to shortlist:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db decide PRODUCT_ID SHORTLIST --notes "Reviewed evidence and content angle"
```

Approve for content production:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db decide PRODUCT_ID APPROVED_FOR_CONTENT --notes "Approved for draft creation"
```

Export reviewed candidates:

```powershell
python .\scripts\amazon_scout.py --db .\data\amazon_scout.db export --out .\amazon_scout_shortlist.csv
```

The daily command creates a dated research record and prints a checklist. It does not discover products online. Windows Task Scheduler may run the command after the user has tested and approved the schedule.

Keep the SQLite database, exports containing user research and any credentials out of source control.
