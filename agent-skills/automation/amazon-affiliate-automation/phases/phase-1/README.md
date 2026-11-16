# Phase 1 — Product Scout foundation

Phase 1 establishes the offline product-ranking workflow.

## Files

- `SKILL.md`: original Phase 1 operating instructions.
- `ENGINE_SPEC.md`: architecture and acceptance criteria.
- `PRODUCT_SCOUT.md`: scoring framework and shortlist requirements.
- `scripts/product_scout.py`: standard-library CSV scorer.
- `templates/product_candidates.csv`: input template.
- `references/COMPLIANCE.md`: compliance checklist.

## Run

From this directory:

```powershell
python scripts/product_scout.py templates/product_candidates.csv --top 20
```

The template is intentionally empty. Populate it only with data from lawful, permitted sources and include source and observation date. The scorer makes no network requests and never approves a product automatically.

Phase 2 extends this foundation with SQLite persistence and a human review queue.
