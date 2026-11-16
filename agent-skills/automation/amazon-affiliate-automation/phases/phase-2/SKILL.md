---
name: amazon-affiliate-research-operations
description: Run the local SQLite product research workflow for Amazon affiliate candidates, including CSV import, ranking, human review statuses and shortlist export.
---
# Phase 2: Research Operations

Use the local SQLite engine in `scripts/amazon_scout.py`. It imports user-supplied candidate CSV data, stores evidence metadata and score history, records daily research runs, and exports reviewed candidates.

Never scrape Amazon or imply the engine fetches live product data. Require source and observation date for material facts. Treat commission rates as assumptions until independently verified. Human decisions only: `RESEARCH`, `SHORTLIST`, `REJECT`, `APPROVED_FOR_CONTENT`.

Only `APPROVED_FOR_CONTENT` products may proceed to Phase 3. This status does not authorise publication.
