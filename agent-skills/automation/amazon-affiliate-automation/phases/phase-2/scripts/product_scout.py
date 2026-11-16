#!/usr/bin/env python3
"""Offline candidate scorer. Reads user-supplied CSV; makes no network requests."""
import argparse, csv, math
from pathlib import Path

def number(row, key, default=None):
    raw = (row.get(key) or "").strip()
    if not raw: return default
    try:
        value = float(raw)
        return value if math.isfinite(value) else default
    except (TypeError, ValueError): return default

def clamp(value, low, high): return max(low, min(high, value))

def score(row):
    rating=number(row,"rating"); reviews=number(row,"review_count")
    price=number(row,"price_usd"); commission=number(row,"commission_rate")
    content=number(row,"content_potential_0_20")
    demand=0 if reviews is None else clamp(math.log10(max(0,reviews)+1)/4*25,0,25)
    if rating is None or reviews is None or not 0<=rating<=5 or reviews<0: quality=0
    else: quality=clamp((rating/5)*clamp(math.log10(reviews+1)/3,0,1)*20,0,20)
    content_score=0 if content is None else clamp(content,0,20)
    economics=0 if price is None or commission is None or price<0 or commission<0 else clamp((price*commission)/5*20,0,20)
    evidence=15 if (row.get("source") or "").strip() and (row.get("observed_at") or "").strip() else 0
    total=round(demand+quality+content_score+economics+evidence,1)
    warnings=[]
    for key,val in [("rating",rating),("review_count",reviews),("price",price),("commission_rate",commission),("content_potential_0_20",content)]:
        if val is None: warnings.append("missing "+key)
    if not (row.get("source") or "").strip(): warnings.append("missing source")
    if not (row.get("observed_at") or "").strip(): warnings.append("missing observed_at")
    if price is not None and commission is not None: warnings.append("economics are assumptions until commission eligibility and rate are verified")
    return total,demand,quality,content_score,economics,evidence,warnings

def main():
    p=argparse.ArgumentParser(description="Rank user-supplied Amazon affiliate candidates offline.")
    p.add_argument("csv_file",type=Path); p.add_argument("--top",type=int,default=20); a=p.parse_args()
    if not a.csv_file.exists(): raise SystemExit(f"File not found: {a.csv_file}")
    with a.csv_file.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
    ranked=sorted([(score(r)[0],r,score(r)[1:]) for r in rows],key=lambda x:x[0],reverse=True)
    print("PRODUCT SCOUT — ranking only; not an earnings forecast")
    for i,(total,row,parts) in enumerate(ranked[:max(0,a.top)],1):
        demand,quality,content,economics,evidence,warnings=parts
        print(f"{i}. {row.get('title') or row.get('product_id') or 'Untitled'} | {total}/100")
        print(f"   Demand {demand:.1f}/25 | Quality {quality:.1f}/20 | Content {content:.1f}/20 | Economics {economics:.1f}/20 | Evidence {evidence}/15")
        print("   Status: RESEARCH ONLY")
        if warnings: print("   Warnings: "+"; ".join(warnings))
    if not rows: print("No candidates supplied.")
    print("Human review required. No automatic approval.")

if __name__=="__main__": main()
