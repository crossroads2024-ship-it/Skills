#!/usr/bin/env python3
"""Package an approved Amazon affiliate video brief into production documents. Offline only."""
import argparse, csv, json, re
from datetime import date
from pathlib import Path

DISCLOSURE = "#ad · As an Amazon Associate I earn from qualifying purchases."

def slug(value):
    return re.sub(r"[^a-zA-Z0-9]+","-",value.strip().lower()).strip("-")[:48] or "product"

def validate(data):
    errors=[]; p=data.get("product",{}); c=data.get("creative",{}); assets=data.get("assets",[])
    for key in ["name","asin","amazon_url","approval_status","approval_date","facts","buyer_problem","affiliate_url"]:
        if not p.get(key): errors.append("Missing product."+key)
    if p.get("approval_status")!="APPROVED_FOR_CONTENT":
        errors.append("Product must have Phase 2 status APPROVED_FOR_CONTENT.")
    if not p.get("facts"): errors.append("At least one evidence-backed product fact is required.")
    for i,f in enumerate(p.get("facts",[]),1):
        if not f.get("claim") or not f.get("evidence"): errors.append(f"Fact {i} needs claim and evidence.")
    duration=c.get("duration_seconds")
    if not isinstance(duration,int) or not 20<=duration<=45: errors.append("Video duration must be 20–45 seconds.")
    if len(c.get("hooks",[]))<3: errors.append("Provide at least three hooks.")
    for key in ["concept","selected_hook","scenes","voiceover","cta"]:
        if not c.get(key): errors.append("Missing creative."+key)
    if not assets: errors.append("At least one asset with source and rights_status is required.")
    for i,a in enumerate(assets,1):
        if not a.get("asset") or not a.get("source") or not a.get("rights_status"):
            errors.append(f"Asset {i} needs asset, source and rights_status.")
        if a.get("rights_status") not in ["owned","licensed","generated_concept"]:
            errors.append(f"Asset {i} is not cleared for production.")
    return errors

def write_csv(path,rows,fields):
    with path.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def timestamp(seconds):
    h,rem=divmod(int(seconds),3600); m,s=divmod(rem,60)
    return f"{h:02}:{m:02}:{s:02},000"

def build(data,out):
    errors=validate(data)
    if errors: raise ValueError("BLOCKED:\n- "+"\n- ".join(errors))
    p,c=data["product"],data["creative"]
    out.mkdir(parents=True,exist_ok=True)
    folder=out/f'{p["asin"]}_{date.today().isoformat()}_{slug(p["name"])}'
    folder.mkdir()
    facts="\n".join(f'- **{x["claim"]}** Evidence: {x["evidence"]}' for x in p["facts"])
    caveats="\n".join("- "+x for x in p.get("caveats",[])) or "- Confirm whether any material caveat applies."
    rights="\n".join(f'- {a["asset"]}: {a["source"]} | {a["rights_status"]}' for a in data["assets"])
    (folder/"01_brief.md").write_text(
      f'# Production brief: {p["name"]}\n\n- ASIN: {p["asin"]}\n- Amazon URL: {p["amazon_url"]}\n'
      f'- Approval: {p["approval_status"]} on {p["approval_date"]}\n- Buyer problem: {p["buyer_problem"]}\n'
      f'- Concept: {c["concept"]}\n- Duration: {c["duration_seconds"]} seconds, 9:16 vertical\n\n'
      f'## Evidence-backed facts\n{facts}\n\n## Caveats\n{caveats}\n\n## Asset rights\n{rights}\n',encoding="utf-8")
    hooks="\n".join(f"{i}. {h}" for i,h in enumerate(c["hooks"],1))
    scenes="\n".join(f'- **{s["start"]}–{s["end"]}s:** {s["visual"]}\n  - On-screen: {s["on_screen_text"]}\n  - Voiceover: {s["voiceover"]}' for s in c["scenes"])
    (folder/"02_script.md").write_text(f'# Video script\n\n**Selected hook:** {c["selected_hook"]}\n\n## Alternative hooks\n{hooks}\n\n## Timed scenes\n{scenes}\n\n**CTA:** {c["cta"]}\n',encoding="utf-8")
    write_csv(folder/"03_storyboard.csv",c["scenes"],["start","end","visual","on_screen_text","voiceover"])
    shot_rows=[{"shot":i,"asset":a["asset"],"source":a["source"],"rights_status":a["rights_status"],
                "framing":"9:16 vertical; respect platform safe areas",
                "note":"Do not imply authentic product testing unless the footage documents real testing."}
               for i,a in enumerate(data["assets"],1)]
    write_csv(folder/"04_shot_list.csv",shot_rows,["shot","asset","source","rights_status","framing","note"])
    (folder/"05_voiceover.txt").write_text(c["voiceover"].strip()+"\n",encoding="utf-8")
    subtitles=[]
    for i,s in enumerate(c["scenes"],1):
        if int(s["end"])<=int(s["start"]): raise ValueError(f"Scene {i}: end must exceed start.")
        line=s.get("voiceover","").strip()
        if line: subtitles += [str(i),f'{timestamp(s["start"])} --> {timestamp(s["end"])}',line,""]
    (folder/"06_subtitles.srt").write_text("\n".join(subtitles),encoding="utf-8")
    caption=c.get("caption") or c["concept"]; keywords=", ".join(c.get("keywords",[])); hashtags=" ".join(c.get("hashtags",[]))
    (folder/"07_platform_captions.md").write_text(
      f'# Platform copy\n\n## TikTok / Instagram Reels\n{caption}\n\n{DISCLOSURE}\n\nCTA: {c["cta"]}\n\n'
      f'Keywords: {keywords}\n\nHashtags: {hashtags}\n\n## YouTube Shorts\n{caption}\n\n{DISCLOSURE}\n\n'
      f'CTA: {c["cta"]}\n\n## Pinterest\n**Pin title:** {c["concept"]}\n\n**Description:** {caption} {DISCLOSURE}\n\n'
      f'**Search terms:** {keywords}\n\n**Alt text:** Short vertical video about {p["name"]}, addressing {p["buyer_problem"]}.\n',encoding="utf-8")
    metadata={"product_name":p["name"],"asin":p["asin"],"amazon_url":p["amazon_url"],"affiliate_url":p["affiliate_url"],
      "platforms":["TikTok","Instagram Reels","YouTube Shorts","Pinterest"],"format":"9:16 vertical",
      "duration_seconds":c["duration_seconds"],"disclosure":DISCLOSURE,
      "amazon_associates_statement":"As an Amazon Associate I earn from qualifying purchases.",
      "status":"draft","fact_check_status":"human verification required","publishing_status":"not_published",
      "created_date":date.today().isoformat(),"asset_rights":data["assets"]}
    (folder/"08_publish_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    checklist="""# Human pre-publication checklist

- [ ] Product identity, ASIN, price and availability rechecked.
- [ ] Affiliate URL/tag verified.
- [ ] Every factual claim matches current evidence.
- [ ] No false personal testing, endorsement or testimonial.
- [ ] All footage, images, graphics, music and sound effects have documented rights.
- [ ] Generated/concept visuals are not presented as real product demonstrations.
- [ ] 9:16 framing and platform safe areas checked.
- [ ] Captions are accurate and synchronised.
- [ ] Affiliate disclosure is clear and close to the recommendation/link.
- [ ] Current Amazon Associates and platform rules checked.
- [ ] Human reviewer approved the final export.

**Status: DRAFT. This tool does not approve or publish content.**
"""
    (folder/"09_preflight_checklist.md").write_text(checklist,encoding="utf-8")
    return folder

def main():
    parser=argparse.ArgumentParser(description="Package an approved product video production brief.")
    parser.add_argument("input",type=Path); parser.add_argument("--output",type=Path,default=Path("output"))
    args=parser.parse_args(); data=json.loads(args.input.read_text(encoding="utf-8"))
    try: result=build(data,args.output)
    except (ValueError,KeyError,TypeError) as e: raise SystemExit(str(e))
    print("READY FOR HUMAN REVIEW:",result.resolve())

if __name__=="__main__": main()
