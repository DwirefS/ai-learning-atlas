#!/usr/bin/env python3
"""v8 build: runs build_v7, then merges full lessons (scripts/v8/lessons) and resource annotations (scripts/v8/resnotes.py)."""
import json, re, sys, subprocess, importlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts/v8"))
subprocess.run([sys.executable,str(ROOT/"scripts/build_v7.py")],check=True,stdout=subprocess.DEVNULL)
from resnotes import note
cur=json.loads((ROOT/"data/curriculum.json").read_text()); concepts=json.loads((ROOT/"data/concepts.json").read_text())
def W(s): return len(json.dumps(s,ensure_ascii=False).split()) if not isinstance(s,str) else len(s.split())
words_before=W(cur)
LES={}
for m in "shared architect engineer1 engineer2 inference infra agentic data trust".split():
    LES.update(importlib.import_module("lessons."+m).LESSONS)
from lessons.subs_extra import X as SUBX
WIDGETS={"softmax","tokenizer","attention","kvcache","batching","quant","rag","agentloop","eval","routing","budget"}
def subjects():
    for s in cur["shared_core"]["subjects"]: yield s
    for t in cur["tracks"]:
        for l in t["levels"]: yield from l["subjects"]
S=list(subjects()); errs=[]
for s in S:
    L=dict(LES[s["id"]]); subs=L.pop("subs")
    for t in s["topics"]:
        for st in t["subtopics"]:
            if st["id"] in subs: st["text"]=subs[st["id"]]
            elif st["id"] in SUBX: st["text"]=SUBX[st["id"]]
    s["lesson"]={k:v for k,v in L.items() if v is not None}
    for r in s["resources"]:
        if "why" not in r: r.update(note(r["url"],r["title"],s["title"]))
    # validate the bar
    e=lambda c,m: c or errs.append((s["id"],m))
    e(W(L["intuition"])>=40,"intuition"); e(len(L["how"])>=3,"how"); e(W(L["example"])>=40,"example")
    e(len(L["mistakes"])>=3,"mistakes"); e(W(L["enterprise"])>=25,"enterprise"); e(len(L["takeaways"])>=3,"takeaways")
    e(L["diagram"] and len(L["diagramAlt"])>30,"diagram"); e(not L.get("widget") or L["widget"] in WIDGETS,"widget")
    e(len(s["quiz"])>=3 and all(q.get("why") for q in s["quiz"]),"quiz")
    e(all(r.get("why") and r.get("level") for r in s["resources"]),"resources")
    for t in s["topics"]:
        e(W(t["explainer"])>=60,"topic "+t["id"])
        n=sum(1 for st in t["subtopics"] if st.get("text")); e(n>=2,f"subs {t['id']} {n}")
for x in errs: print("FAIL",x)
nsub=sum(1 for s in S for t in s["topics"] for st in t["subtopics"] if st.get("text"))
if errs and "--force" not in sys.argv: sys.exit(1)
cur["meta"]["version"]="8.0.0"
(ROOT/"data/curriculum.json").write_text(json.dumps(cur,indent=2,ensure_ascii=False))
for t in cur["tracks"]: (ROOT/f"data/_{t['id']}.json").write_text(json.dumps(t,indent=2,ensure_ascii=False))
(ROOT/"data/_shared.json").write_text(json.dumps(cur["shared_core"],indent=2,ensure_ascii=False))
h=(ROOT/"index.html").read_text(); emb=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")
h=re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(cur)+"\n"+m.group(2),h,flags=re.S)
(ROOT/"index.html").write_text(h)
stats=json.loads((ROOT/"docs/stats.json").read_text())
stats.update(version="8.0.0",words_before_v8=82537,words=W(cur),words_with_concepts=W(cur)+W(concepts),lessons=len(S),lesson_diagrams=sum(1 for s in S if s["lesson"].get("diagram")),
  concept_diagrams=sum(1 for c in concepts if c.get("diagram") or c.get("mermaid")),subtopic_explanations=nsub,
  widgets=sorted(WIDGETS),lessons_with_widget=sum(1 for s in S if s["lesson"].get("widget")),annotated_resources=stats["resources"])
(ROOT/"docs/stats.json").write_text(json.dumps(stats,indent=2)); print(stats)
