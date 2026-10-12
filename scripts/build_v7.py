#!/usr/bin/env python3
"""v7 build: runs build_v6, then deepens the stages of Suraj Sharma's 12-stage Agentic AI Engineer post (scripts/v7)."""
import json, random, re, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts/v7"))
subprocess.run([sys.executable,str(ROOT/"scripts/build_v6.py")],check=True,stdout=subprocess.DEVNULL)
import content7 as C
cur=json.loads((ROOT/"data/curriculum.json").read_text()); concepts=json.loads((ROOT/"data/concepts.json").read_text())
def all_subjects():
    for s in cur["shared_core"]["subjects"]: yield s
    for t in cur["tracks"]:
        for l in t["levels"]: yield from l["subjects"]
S={s["id"]:s for s in all_subjects()}
ids=[c["id"] for c in concepts]
for c in C.CONCEPTS:
    if c["id"] in ids: concepts[ids.index(c["id"])]=c
    else: concepts.append(c)
cur["conceptIds"]=[c["id"] for c in concepts]
for sid,(topic,quiz,res,cids) in C.EXTRA.items():
    s=S[sid]
    if not any(t["id"]==topic["id"] for t in s["topics"]): s["topics"].append(topic)
    for q in quiz:
        if any(x["q"]==q["q"] for x in s["quiz"]): continue
        ch=q["choices"][q["answer"]]; q=dict(q,choices=list(q["choices"])); random.Random(q["q"]).shuffle(q["choices"]); q["answer"]=q["choices"].index(ch); s["quiz"].append(q)
    for r in res:
        if r["url"] not in [x["url"] for x in s["resources"]]: s["resources"].append(r)
    for c in cids:
        if c not in s["conceptIds"]: s["conceptIds"].append(c)
pids=[p["id"] for p in cur["projects"]]
for p in C.NEW_PROJECTS:
    if p["id"] not in pids: cur["projects"].append(p)
cur["projects"].sort(key=lambda p:p["tier"])
path=dict(id="suraj-12-stage",title="Agentic AI Engineer (Suraj Sharma's 12 stages)",untimed=True,emoji="🧭",
  who="Untimed path following Suraj Sharma's '6 months to become an AI Engineer in the Agentic Era'. Each stage names the Project Ladder build that proves the skill.",
  steps=[[ "engineer" if sid.startswith("e-") else "agentic" if sid.startswith("g-") else "trust" if sid.startswith("t-") else "architect", sid, label] for sid,label in C.STAGES])
cur["paths"]=[p for p in cur["paths"] if p["id"]!=path["id"]]+[path]
cur["meta"]["version"]="7.0.0"
# validate
pidset={p["id"] for p in cur["projects"]}; rids={r["id"] for r in cur["roles"]}
for p in cur["projects"]:
    assert set(p["subjects"])<=set(S),p["id"]; assert set(p["roles"])<=rids,(p["id"],p["roles"])
for sid,label in C.STAGES:
    assert sid in S; for_p=re.findall(r"p-[a-z0-9-]+",label); assert for_p and set(for_p)<=pidset,label
for p in cur["paths"]:
    for k,ref,_ in p["steps"]: assert (k=="capstone" and ref in cur["capstones"]) or ref in S,(p["id"],ref)
    tr={t["id"]:{s["id"] for l in t["levels"] for s in l["subjects"]} for t in cur["tracks"]}
for k,ref,_ in path["steps"]: assert ref in tr[k],(k,ref)
for s in S.values():
    assert len(s["quiz"])>=3 and len(s["resources"])>=3
    for q in s["quiz"]: assert 0<=q["answer"]<len(q["choices"])
    for c in s["conceptIds"]: assert c in cur["conceptIds"],(s["id"],c)
    for t in s["topics"]:
        n=len(t["explainer"].split()); assert 60<=n<=150,(t["id"],n)
(ROOT/"data/curriculum.json").write_text(json.dumps(cur,indent=2,ensure_ascii=False))
(ROOT/"data/concepts.json").write_text(json.dumps(concepts,indent=2,ensure_ascii=False))
for t in cur["tracks"]: (ROOT/f"data/_{t['id']}.json").write_text(json.dumps(t,indent=2,ensure_ascii=False))
(ROOT/"data/_shared.json").write_text(json.dumps(cur["shared_core"],indent=2,ensure_ascii=False))
(ROOT/"data/_projects.json").write_text(json.dumps(cur["projects"],indent=2,ensure_ascii=False))
h=(ROOT/"index.html").read_text(); emb=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")
h=re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(cur)+"\n"+m.group(2),h,flags=re.S)
h=re.sub(r'(<script id="concepts-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(concepts)+"\n"+m.group(2),h,flags=re.S)
(ROOT/"index.html").write_text(h)
subs=list(S.values()); tops=[t for s in subs for t in s["topics"]]
stats=dict(subjects=len(subs),topics=len(tops),subtopics=sum(len(t["subtopics"]) for t in tops),quiz=sum(len(s["quiz"]) for s in subs),
 resources=len({r["url"] for s in subs for r in s["resources"]}),concepts=len(concepts),glossary=len(cur["glossary"]),paths=len(cur["paths"]),
 capstones=len(cur["capstones"]),roles=len(cur["roles"]),projects=len(cur["projects"]),tracks=len(cur["tracks"])+1)
(ROOT/"docs/stats.json").write_text(json.dumps(stats,indent=2)); print(stats)
