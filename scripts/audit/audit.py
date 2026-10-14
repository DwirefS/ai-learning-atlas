import json, re, csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(Path(__file__).parent))
from checklist import ITEMS
cur=json.loads((ROOT/"data/curriculum.json").read_text()); con=json.loads((ROOT/"data/concepts.json").read_text())
units=[]  # (id, text)
titles=[]
for s in cur["shared_core"]["subjects"]+[s for t in cur["tracks"] for l in t["levels"] for s in l["subjects"]]:
    units.append((s["id"],"\n".join([s["title"],s["why"],s["explainer"],s["project"]]+[t["title"]+" "+t["explainer"]+" "+" ".join(x["title"] for x in t["subtopics"]) for t in s["topics"]]+[q["q"]+" "+" ".join(q["choices"])+" "+q["why"] for q in s["quiz"]])))
for s in cur["shared_core"]["subjects"]+[s for t in cur["tracks"] for l in t["levels"] for s in l["subjects"]]:
    titles.append(" | ".join([s["title"]]+[t["title"] for t in s["topics"]]+[x["title"] for t in s["topics"] for x in t["subtopics"]]))
for c in con: titles.append(c["title"])
for c in con: units.append(("concept:"+c["id"],c["title"]+" "+c["summary"]+" "+c["body"]+" "+c["example"]))
for p in cur.get("projects",[]): units.append(("project:"+p["id"],json.dumps(p)))
for k,c in cur.get("capstones",{}).items(): units.append(("capstone:"+k,json.dumps(c))); titles.append(c["title"])
rows=[];out=sys.argv[1] if len(sys.argv)>1 else str(ROOT/"docs/coverage_audit.csv")
for topic,rx,st,src in ITEMS:
    r=re.compile(rx,re.I); hits=[(u,len(r.findall(t))) for u,t in units if r.search(t)]
    n=sum(h for _,h in hits); k=len(hits)
    ded=any(r.search(t) for t in titles)
    status="covered" if k>=3 or n>=6 or ded else ("thin" if k>=1 else "missing")
    rows.append(dict(topic=topic,source_type=st,sources=src,regex=rx,status=status,dedicated_title=ded,units_matched=k,mentions=n,where="; ".join(u for u,_ in sorted(hits,key=lambda x:-x[1])[:6])))
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows),Counter(r["status"] for r in rows))
for r in rows:
    if r["status"]!="covered": print(r["status"],"|",r["topic"],"|",r["mentions"],r["where"])
