#!/usr/bin/env python3
"""Offline candidate scorer. Reads user-supplied CSV; makes no network requests."""
import argparse
import csv
import math
from pathlib import Path

def number(row, key, default=None):
    raw = (row.get(key) or "").strip()
    if raw == "":
        return default
    try:
        value = float(raw)
        return value if math.isfinite(value) else default
    except (TypeError, ValueError):
        return default

def clamp(value, low, high):
    return max(low, min(high, value))

def score(row):
    rating = number(row, "rating")
    reviews = number(row, "review_count")
    price = number(row, "price_usd")
    commission = number(row, "commission_rate")
    content = number(row, "content_potential_0_20")
    demand = 0 if reviews is None else clamp(math.log10(max(0, reviews) + 1) / 4 * 25, 0, 25)
    if rating is None or reviews is None or not 0 <= rating <= 5 or reviews < 0:
        quality = 0
    else:
        confidence = clamp(math.log10(reviews + 1) / 3, 0, 1)
        quality = clamp((rating / 5) * confidence * 20, 0, 20)
    content_score = 0 if content is None else clamp(content, 0, 20)
    if price is None or commission is None or price < 0 or commission < 0:
        economics = 0
    else:
        economics = clamp((price * commission) / 5 * 20, 0, 20)
    evidence = 15 if (row.get("source") or "").strip() and (row.get("observed_at") or "").strip() else 0
    total = round(demand + quality + content_score + economics + evidence, 1)
    warnings = []
    for key, value in [("rating",rating),("review_count",reviews),("price",price),
                       ("commission_rate",commission),("content_potential_0_20",content)]:
        if value is None: warnings.append("missing " + key)
    if not (row.get("source") or "").strip(): warnings.append("missing source")
    if not (row.get("observed_at") or "").strip(): warnings.append("missing observed_at")
    if price is not None and commission is not None:
        warnings.append("economics are assumptions until commission eligibility and rate are verified")
    return total, demand, quality, content_score, economics, evidence, warnings

def main():
    parser = argparse.ArgumentParser(description="Rank user-supplied Amazon affiliate candidates offline.")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()
    if not args.csv_file.exists(): raise SystemExit(f"File not found: {args.csv_file}")
    with args.csv_file.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    ranked = []
    for row in rows:
        values = score(row)
        ranked.append((values[0], row, *values[1:]))
    ranked.sort(key=lambda item: item[0], reverse=True)
    print("PRODUCT SCOUT — ranking only; not an earnings forecast")
    print("=" * 76)
    for rank, item in enumerate(ranked[:max(0,args.top)],1):
        total,row,demand,quality,content,economics,evidence,warnings = item
        print(f"{rank}. {row.get('title') or row.get('product_id') or 'Untitled'} | score {total}/100")
        print(f"   Demand {demand:.1f}/25 | Quality {quality:.1f}/20 | Content {content:.1f}/20 | Economics {economics:.1f}/20 | Evidence metadata {evidence}/15")
        print("   Status: RESEARCH ONLY (never auto-approved)")
        if warnings: print("   Warnings: " + "; ".join(warnings))
    if not rows: print("No candidates supplied. Add sourced rows to the CSV template.")
    print("Human review and explicit approval are required before content production or publication.")

if __name__ == "__main__":
    main()
