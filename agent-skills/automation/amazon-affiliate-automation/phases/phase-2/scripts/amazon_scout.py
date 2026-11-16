#!/usr/bin/env python3
"""Local SQLite Product Scout. Offline only; no scraping or network access."""
import argparse, csv, json, math, sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS products (
 product_id TEXT PRIMARY KEY, title TEXT NOT NULL, asin TEXT,
 status TEXT NOT NULL DEFAULT 'RESEARCH' CHECK(status IN ('RESEARCH','SHORTLIST','REJECT','APPROVED_FOR_CONTENT')),
 notes TEXT DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
 evidence_id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
 field_name TEXT NOT NULL, field_value TEXT, source TEXT NOT NULL DEFAULT '', observed_at TEXT NOT NULL DEFAULT '', use_note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS scores (
 score_id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
 score_version TEXT NOT NULL, total REAL NOT NULL, demand REAL NOT NULL, quality REAL NOT NULL, content REAL NOT NULL,
 economics REAL NOT NULL, evidence_metadata REAL NOT NULL, warnings TEXT NOT NULL DEFAULT '[]', scored_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scout_runs (
 run_id INTEGER PRIMARY KEY AUTOINCREMENT, run_date TEXT NOT NULL, run_type TEXT NOT NULL, status TEXT NOT NULL,
 notes TEXT DEFAULT '', created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_scores_product_date ON scores(product_id, scored_at);
"""

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def num(row,key):
    raw=(row.get(key) or "").strip()
    if not raw: return None
    try:
        x=float(raw); return x if math.isfinite(x) else None
    except ValueError: return None
def clamp(x,lo,hi): return max(lo,min(hi,x))

def calculate(row):
    rating=num(row,"rating"); reviews=num(row,"review_count"); price=num(row,"price_usd")
    rate=num(row,"commission_rate"); content=num(row,"content_potential_0_20")
    demand=0 if reviews is None or reviews<0 else clamp(math.log10(reviews+1)/4*25,0,25)
    if rating is None or reviews is None or not 0<=rating<=5 or reviews<0: quality=0
    else: quality=clamp((rating/5)*clamp(math.log10(reviews+1)/3,0,1)*20,0,20)
    content_score=0 if content is None else clamp(content,0,20)
    economics=0 if price is None or rate is None or price<0 or rate<0 else clamp((price*rate)/5*20,0,20)
    source=(row.get("source") or "").strip(); observed=(row.get("observed_at") or "").strip()
    evidence=15 if source and observed else 0
    warnings=[]
    for key,val in [("rating",rating),("review_count",reviews),("price_usd",price),("commission_rate",rate),("content_potential_0_20",content)]:
        if val is None: warnings.append("missing "+key)
    if not source: warnings.append("missing source")
    if not observed: warnings.append("missing observed_at")
    if price is not None and rate is not None: warnings.append("commission assumptions require independent programme verification")
    if observed and observed[:10] < datetime.now(timezone.utc).date().isoformat(): warnings.append("evidence date may be stale; verify before use")
    return round(demand+quality+content_score+economics+evidence,1),demand,quality,content_score,economics,evidence,warnings

def connect(path):
    con=sqlite3.connect(path); con.row_factory=sqlite3.Row; con.executescript(SCHEMA); return con

def import_csv(con,csv_path):
    count=0
    with open(csv_path,newline="",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            pid=(row.get("product_id") or "").strip(); title=(row.get("title") or "").strip()
            if not pid or not title: continue
            stamp=now()
            con.execute("""INSERT INTO products(product_id,title,asin,notes,created_at,updated_at) VALUES(?,?,?,?,?,?)
              ON CONFLICT(product_id) DO UPDATE SET title=excluded.title,asin=excluded.asin,notes=excluded.notes,updated_at=excluded.updated_at""",
              (pid,title,(row.get("asin") or "").strip(),(row.get("notes") or "").strip(),stamp,stamp))
            for field in ["price_usd","rating","review_count","commission_rate","content_potential_0_20"]:
                value=(row.get(field) or "").strip()
                if value:
                    con.execute("INSERT INTO evidence(product_id,field_name,field_value,source,observed_at,use_note) VALUES(?,?,?,?,?,?)",
                      (pid,field,value,(row.get("source") or "").strip(),(row.get("observed_at") or "").strip(),"Imported from user-supplied CSV; verify permitted source/use"))
            values=calculate(row)
            con.execute("INSERT INTO scores(product_id,score_version,total,demand,quality,content,economics,evidence_metadata,warnings,scored_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (pid,"v0.2",*values[:6],json.dumps(values[6]),stamp))
            count+=1
    con.commit(); return count

def main():
    p=argparse.ArgumentParser(description="Offline Amazon affiliate candidate database.")
    p.add_argument("--db",default="amazon_scout.db"); sub=p.add_subparsers(dest="cmd",required=True)
    imp=sub.add_parser("import"); imp.add_argument("csv_file")
    sub.add_parser("rank")
    dec=sub.add_parser("decide"); dec.add_argument("product_id"); dec.add_argument("status",choices=["RESEARCH","SHORTLIST","REJECT","APPROVED_FOR_CONTENT"]); dec.add_argument("--notes",default="")
    daily=sub.add_parser("daily"); daily.add_argument("--date",default=datetime.now().date().isoformat()); daily.add_argument("--notes",default="Daily discovery run. Import only evidence from authorised sources.")
    exp=sub.add_parser("export"); exp.add_argument("--out",default="amazon_scout_shortlist.csv")
    a=p.parse_args(); con=connect(a.db)
    if a.cmd=="import":
        n=import_csv(con,a.csv_file); print(f"Imported or updated {n} candidate rows into {a.db}")
    elif a.cmd=="rank":
        rows=con.execute("""SELECT p.product_id,p.title,p.asin,p.status,s.total,s.demand,s.quality,s.content,s.economics,s.evidence_metadata,s.warnings,s.scored_at
          FROM products p JOIN scores s ON s.score_id=(SELECT MAX(s2.score_id) FROM scores s2 WHERE s2.product_id=p.product_id) ORDER BY s.total DESC""").fetchall()
        if not rows: print("No candidates yet. Import a CSV of sourced candidates.")
        for i,r in enumerate(rows,1):
            print(f"{i}. {r['title']} [{r['product_id']}] {r['total']}/100 status={r['status']}")
            print(f"   demand {r['demand']:.1f}/25 | quality {r['quality']:.1f}/20 | content {r['content']:.1f}/20 | economics {r['economics']:.1f}/20 | evidence {r['evidence_metadata']}/15")
            warnings=json.loads(r["warnings"])
            if warnings: print("   flags: "+"; ".join(warnings))
    elif a.cmd=="decide":
        cur=con.execute("UPDATE products SET status=?,notes=?,updated_at=? WHERE product_id=?",(a.status,a.notes,now(),a.product_id)); con.commit()
        if cur.rowcount==0: raise SystemExit("Unknown product_id. No decision saved.")
        print(f"{a.product_id} status set to {a.status}.")
        if a.status=="APPROVED_FOR_CONTENT": print("Human approval recorded for content production only. Publishing remains disabled.")
    elif a.cmd=="daily":
        con.execute("INSERT INTO scout_runs(run_date,run_type,status,notes,created_at) VALUES(?,?,?,?,?)",(a.date,"DAILY_SCOUT","OPEN",a.notes,now())); con.commit()
        print(f"Daily scout run opened for {a.date}.")
        print("Checklist: verify authorised sources; capture facts and dates; import CSV; inspect warnings; make human decisions; never scrape or auto-publish.")
    elif a.cmd=="export":
        rows=con.execute("""SELECT p.product_id,p.title,p.asin,p.status,s.total,s.demand,s.quality,s.content,s.economics,s.evidence_metadata,s.warnings,s.scored_at
          FROM products p JOIN scores s ON s.score_id=(SELECT MAX(s2.score_id) FROM scores s2 WHERE s2.product_id=p.product_id)
          WHERE p.status IN ('SHORTLIST','APPROVED_FOR_CONTENT') ORDER BY s.total DESC""").fetchall()
        with open(a.out,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["product_id","title","asin","status","score","demand_25","quality_20","content_20","economics_20","evidence_metadata_15","warnings","scored_at"])
            for r in rows: w.writerow([r[k] for k in ["product_id","title","asin","status","total","demand","quality","content","economics","evidence_metadata","warnings","scored_at"]])
        print(f"Exported {len(rows)} reviewed products to {a.out}")
    con.close()

if __name__=="__main__": main()
