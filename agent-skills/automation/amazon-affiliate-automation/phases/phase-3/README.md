# Phase 3 — Video Factory

Phase 3 turns a Phase 2 product with status `APPROVED_FOR_CONTENT` into a complete, reviewable production pack. It does not discover products, verify Amazon metrics, scrape assets, generate fake product demonstrations or publish content.

## Outputs

- Creative brief and concept.
- Three alternative hooks and one selected hook.
- 20–45 second timed script and voiceover.
- Storyboard and practical shot list.
- SRT subtitles.
- TikTok, Instagram Reels, YouTube Shorts and Pinterest copy.
- Affiliate disclosure and metadata.
- Asset-rights register and human pre-publication checklist.

## Run (Windows PowerShell)

Prepare a JSON brief using `templates/video_job.example.json`. Replace the example with a real Phase 2 approved product, evidence-backed claims, verified affiliate URL or explicit placeholder, and an asset register.

```powershell
python .\scripts\video_factory.py .\templates\video_job.example.json --output .\output
```

The engine validates required fields and creates files. It cannot independently prove that claims are true or that asset rights are valid.

## Asset rules

Use creator-owned footage, user-supplied assets or assets with documented licences. Do not reuse Amazon listing images/videos unless the current licence expressly permits the exact use. Generated footage must not be presented as authentic product testing or customer footage.

## Approval

Generated pack status is always `draft`. A human must verify product details, claims, assets, disclosures and platform rules, then approve the final export. Publishing remains a separate manual step.
