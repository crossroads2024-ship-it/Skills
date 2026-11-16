# Engine specification, Phase 1

## Design principle

Keep agent judgement in `SKILL.md`; keep repeatable data handling in a small local Python engine. No MCP is required for the first version.

## Components

1. Portable skill layer: workflow, constraints, prompts and output formats.
2. Local engine: Python standard library only.
3. State store: CSV initially; SQLite added in Phase 2.
4. Input/output: CSV and Markdown first.
5. Media pipeline: FFmpeg for local assembly after the scout is validated.
6. Scheduler: not enabled. Daily scouting is manual until a permitted scheduler is selected and approved.

## Data model direction

- products: internal ID, ASIN if lawfully obtained, title, category, status and timestamps.
- evidence: product ID, field, value, source, observation date and permitted-use note.
- scores: product ID, score version, component scores, total and rationale.
- decisions: product ID, decision, reviewer, timestamp and notes.
- content_jobs: product ID, platform, format, script path, asset manifest and approval state.
- metrics: content job ID, metric name, value, period, source and observation date.

## Compliance boundaries

- No browser automation, scraping or bots against Amazon product pages.
- Integrate an Amazon API/feed only if the user has valid access and current terms permit the exact use.
- Treat Amazon product images and other Program Content as licensed, not free stock.
- Never expose API keys in prompts, logs, source control or reports.
- Keep account connections and publishing disabled unless explicitly authorised.

## Build sequence

1. Product Scout CSV workflow and transparent scoring.
2. SQLite persistence and approval queue.
3. Product evidence capture/import from authorised sources.
4. On-demand script and storyboard generator.
5. Local FFmpeg rendering using rights-cleared assets.
6. Optional dashboard.
7. Scheduler only after reliability, compliance and approval controls are tested.

## Acceptance criteria

- Runs offline with Python standard library.
- Makes no network requests.
- Rejects malformed numeric fields safely.
- Shows component scores and missing-data warnings.
- Never marks a product approved automatically.
