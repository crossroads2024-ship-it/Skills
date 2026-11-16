---
name: amazon-affiliate-automation
description: Operate a compliant, local-first Amazon US affiliate workflow covering product research, evidence-based shortlisting, SQLite tracking, short-form video production packs, disclosures and human approval.
---

# Amazon Affiliate Automation

## Mission

Operate a low-cost Amazon US affiliate content workflow, initially focused on Home & Kitchen. The system has three sequential phases. Use the narrowest relevant phase and preserve the human approval gates.

## Non-negotiable rules

- Budget target is $0. Do not buy subscriptions, domains, assets, API access, equipment or services.
- Do not connect accounts, register for programmes, deploy software, publish content or make purchases without explicit user approval.
- Every public-facing asset requires human approval before publication.
- Never scrape Amazon pages, bypass access controls, automate browser extraction or use unauthorised feeds.
- Use Amazon product data, images, logos, prices, reviews and other Program Content only through currently authorised sources and within current programme terms.
- Never fabricate specifications, prices, ratings, reviews, test results, personal experience, testimonials, savings, availability or commission rates.
- Never imply Amazon endorsement or personal product testing that did not occur.
- Prefer original scripts, narration, editing, diagrams and visuals. Use only assets with documented rights.
- Record sources and observation dates for material claims. Recheck volatile information before approval.
- Do not place credentials, tokens, private account data or user databases in source control.

## Phase routing

### Phase 1: Product Scout foundation
Use for offline CSV candidate scoring and first-pass screening. Read `phases/phase-1/README.md`, `PRODUCT_SCOUT.md` and `ENGINE_SPEC.md`. The engine ranks supplied data only. It does not fetch Amazon data.

### Phase 2: Research operations
Use for SQLite persistence, CSV imports, score history, daily research records, human decision statuses and shortlist exports. Read `phases/phase-2/README.md`. Only the user can set `APPROVED_FOR_CONTENT`.

### Phase 3: Video Factory
Use only when a product is explicitly approved for content and its factual claims and asset plan are supplied. Read `phases/phase-3/README.md`. Produce a 20–45 second vertical creative pack with hooks, timed scenes, voiceover, shot list, subtitles, platform copy, disclosures and a human preflight checklist. The packager does not publish.

## Product Scout decision rules

- Distinguish verified facts, third-party estimates, assumptions and creative hypotheses.
- Require source and observation date for material evidence.
- A score is a prioritisation aid, not a prediction of clicks, conversion, commissions or profit.
- Flag missing or stale evidence. Never fill missing metrics with invented values.
- Exclude or flag unsafe, recalled, counterfeit, suspicious, poorly documented or medical-claim products.

## Video creative rules

- One video communicates one buyer problem and one main benefit.
- Open with a specific, truthful hook. Demonstrate the mechanism honestly.
- Include a useful caveat where relevant and a natural CTA.
- Do not invent urgency, scarcity, discounts, ratings, testimonials, comparisons or before/after results.
- If no authentic product footage exists, label the output as a concept/mock-up. Never portray generated visuals as real product testing or customer footage.
- Do not reuse Amazon listing images, videos, logos or reviews unless current terms expressly permit the exact use.
- Use licensed or platform-cleared audio only.

## Affiliate disclosure

Place a clear disclosure close to the recommendation and affiliate link, such as `#ad` or `(paid link)`, as appropriate. Include the required Amazon Associates statement in the relevant account/site context:

> As an Amazon Associate I earn from qualifying purchases.

Recheck current Amazon Associates and platform rules before publication. This skill is operational guidance, not legal advice.

## Status model

Research statuses: `RESEARCH`, `SHORTLIST`, `REJECT`, `APPROVED_FOR_CONTENT`.

Content statuses: `draft`, `fact_checked`, `approved_for_publish`, `published`.

A product approval for content is not publication approval. Only a human may move content to `approved_for_publish`. Never claim publication unless it has actually occurred and is confirmed.
