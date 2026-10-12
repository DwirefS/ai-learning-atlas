#!/usr/bin/env python3
"""v4 build: runs build_v3 (idempotent), then adds data/trust tracks, delivery subjects, roles, concepts, universal path."""
import json, random, re, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V4=ROOT/"scripts/v4"; sys.path.insert(0,str(V4))
subprocess.run([sys.executable,str(ROOT/"scripts/build_v3.py")],check=True,stdout=subprocess.DEVNULL)
import data_track, trust_track, delivery, concepts as CN, roles as RL, svgs4
cur=json.loads((ROOT/"data/curriculum.json").read_text()); concepts=json.loads((ROOT/"data/concepts.json").read_text())
def shuf(s):
    for q in s["quiz"]:
        c=q["choices"][q["answer"]]; random.Random(q["q"]).shuffle(q["choices"]); q["answer"]=q["choices"].index(c)
def all_subjects():
    for s in cur["shared_core"]["subjects"]: yield ("shared",None,s)
    for t in cur["tracks"]:
        for l in t["levels"]:
            for s in l["subjects"]: yield (t["id"],l,s)
for T in [data_track.TRACK, trust_track.TRACK]:
    if not any(t["id"]==T["id"] for t in cur["tracks"]):
        for l in T["levels"]:
            for s in l["subjects"]: shuf(s)
        cur["tracks"].append(T)
have={s["id"] for _,_,s in all_subjects()}
for tr,lid,s in delivery.NEW:
    if s["id"] in have: continue
    shuf(s); t=next(x for x in cur["tracks"] if x["id"]==tr); next(l for l in t["levels"] if l["id"]==lid)["subjects"].append(s)
ids=[c["id"] for c in concepts]
for c in CN.CONCEPTS:
    if c["id"] in ids: concepts[ids.index(c["id"])]=c
    else: concepts.append(c)
cur["conceptIds"]=[c["id"] for c in concepts]
cur["roles"]=RL.ROLES
cur["paths"]=[p for p in cur["paths"] if p["id"]!=RL.UNIVERSAL["id"]]+[RL.UNIVERSAL]
cur["capstones"].update(RL.CAPSTONES)
g={x["term"]:x for x in cur["glossary"]}
for t,d in RL.GLOSSARY: g[t]={"term":t,"def":d}
cur["glossary"]=sorted(g.values(),key=lambda x:x["term"].lower())
cur["meta"].update(version="4.0.0",subtitle="0→100 expert paths for 13 agentic AI roles: explainers, diagrams, labs, capstones and learning paths",
  audience="Working engineers leveling into any of 13 enterprise agentic-AI roles")
svgs4.write_all(ROOT)
# validation
sid={s["id"] for _,_,s in all_subjects()}; cids=set(cur["conceptIds"])
for p in cur["paths"]:
    for kind,ref,_ in p["steps"]: assert (kind=="capstone" and ref in cur["capstones"]) or ref in sid,(p["id"],ref)
for r in cur["roles"]:
    for x in r["subjects"]: assert x in sid,(r["id"],x)
seen=set()
for _,_,s in all_subjects():
    assert s["id"] not in seen, s["id"]; seen.add(s["id"])
    assert len(s["quiz"])>=3 and len(s["resources"])>=3, s["id"]
    for q in s["quiz"]: assert 0<=q["answer"]<len(q["choices"])
    for c in s["conceptIds"]: assert c in cids,(s["id"],c)
    for t in s["topics"]:
        n=len(t.get("explainer","").split()); assert 60<=n<=150,(t["id"],n)
(ROOT/"data/curriculum.json").write_text(json.dumps(cur,indent=2,ensure_ascii=False))
(ROOT/"data/concepts.json").write_text(json.dumps(concepts,indent=2,ensure_ascii=False))
for t in cur["tracks"]: (ROOT/f"data/_{t['id']}.json").write_text(json.dumps(t,indent=2,ensure_ascii=False))
(ROOT/"data/_roles.json").write_text(json.dumps(cur["roles"],indent=2,ensure_ascii=False))
h=(ROOT/"index.html").read_text()
emb=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")
h=re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(cur)+"\n"+m.group(2),h,flags=re.S)
h=re.sub(r'(<script id="concepts-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(concepts)+"\n"+m.group(2),h,flags=re.S)
(ROOT/"index.html").write_text(h)
subs=list(all_subjects()); tops=[t for _,_,s in subs for t in s["topics"]]
stats=dict(subjects=len(subs),topics=len(tops),subtopics=sum(len(t["subtopics"]) for t in tops),quiz=sum(len(s["quiz"]) for _,_,s in subs),
  resources=len({r["url"] for _,_,s in subs for r in s["resources"]}),concepts=len(concepts),glossary=len(cur["glossary"]),paths=len(cur["paths"]),
  capstones=len(cur["capstones"]),roles=len(cur["roles"]),tracks=len(cur["tracks"])+1)
(ROOT/"docs/stats.json").write_text(json.dumps(stats,indent=2)); print(stats)
