#!/usr/bin/env python3
"""v5 build: runs build_v4, then adds voice/doc-RAG/vision subjects, 3 concepts and the Project Ladder."""
import json, random, re, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts/v5"))
subprocess.run([sys.executable,str(ROOT/"scripts/build_v4.py")],check=True,stdout=subprocess.DEVNULL)
import concepts5 as CN, projects as PJ, subjects as SB
cur=json.loads((ROOT/"data/curriculum.json").read_text()); concepts=json.loads((ROOT/"data/concepts.json").read_text())
def all_subjects():
    for s in cur["shared_core"]["subjects"]: yield ("shared",s)
    for t in cur["tracks"]:
        for l in t["levels"]:
            for s in l["subjects"]: yield (t["id"],s)
have={s["id"] for _,s in all_subjects()}
for tr,lid,s in SB.NEW:
    if s["id"] in have: continue
    for q in s["quiz"]:
        c=q["choices"][q["answer"]]; random.Random(q["q"]).shuffle(q["choices"]); q["answer"]=q["choices"].index(c)
    t=next(x for x in cur["tracks"] if x["id"]==tr); next(l for l in t["levels"] if l["id"]==lid)["subjects"].append(s)
ids=[c["id"] for c in concepts]
for c in CN.CONCEPTS:
    if c["id"] in ids: concepts[ids.index(c["id"])]=c
    else: concepts.append(c)
cur["conceptIds"]=[c["id"] for c in concepts]
links={"e-multimodal-app":["docrag-pipeline","voice-latency"],"i-gateway":["model-router"],"e-cache":["model-router"],"e-llmops":["model-router"]}
for _,s in all_subjects():
    for c in links.get(s["id"],[]):
        if c not in s["conceptIds"]: s["conceptIds"].append(c)
cur["projects"]=PJ.PROJECTS; cur["projectTiers"]={str(k):v for k,v in PJ.TIERS.items()}
role=lambda rid: next(r for r in cur["roles"] if r["id"]==rid)
for rid,sid in [("ai-engineer","e-docrag"),("ai-engineer","e-vision"),("ai-engineer","e-voice"),("fde","e-voice"),("data-eng","e-docrag")]:
    if sid not in role(rid)["subjects"]: role(rid)["subjects"].append(sid)
u=next(p for p in cur["paths"] if p["id"]=="universal-agentic")
if not any(s[1]=="e-docrag" for s in u["steps"]):
    i=[s[1] for s in u["steps"]].index("d-unstruct")+1
    u["steps"][i:i]=[["engineer","e-docrag","Multimodal and document RAG"],["engineer","e-vision","Vision and document AI extraction"]]
    j=[s[1] for s in u["steps"]].index("t-durable")
    u["steps"].insert(j,["engineer","e-voice","Real-time voice agents"])
g={x["term"]:x for x in cur["glossary"]}
for t,d in [("Barge-in","The user interrupting a voice agent mid-speech; the agent must stop audio and truncate context to what was spoken."),
 ("ColPali","A visual document retrieval model that embeds page images as patch vectors and scores with late interaction."),
 ("Late interaction","Scoring by matching each query token to its best document vector (MaxSim) and summing."),
 ("Model router","A component that sends each request to the cheapest model likely to answer correctly, escalating when needed."),
 ("Speech-to-speech model","A realtime model that takes audio in and produces audio out without separate STT and TTS."),
 ("Straight-through processing","The share of documents processed end to end with no human review."),
 ("VAD","Voice activity detection: classifying audio frames as speech or silence."),
 ("Voice-to-voice latency","Time from the end of user speech to the first audible agent reply.")]: g[t]={"term":t,"def":d}
cur["glossary"]=sorted(g.values(),key=lambda x:x["term"].lower()); cur["meta"]["version"]="5.0.0"
sid={s["id"] for _,s in all_subjects()}; rids={r["id"] for r in cur["roles"]}
for p in cur["projects"]:
    assert p["tier"] in PJ.TIERS and all(x in sid for x in p["subjects"]) and all(r in rids for r in p["roles"]),p["id"]
for p in cur["paths"]:
    for k,ref,_ in p["steps"]: assert (k=="capstone" and ref in cur["capstones"]) or ref in sid
for _,s in all_subjects():
    assert len(s["quiz"])>=3 and len(s["resources"])>=3
    for c in s["conceptIds"]: assert c in cur["conceptIds"],(s["id"],c)
    for t in s["topics"]:
        n=len(t["explainer"].split()); assert 60<=n<=150,(t["id"],n)
(ROOT/"data/curriculum.json").write_text(json.dumps(cur,indent=2,ensure_ascii=False))
(ROOT/"data/concepts.json").write_text(json.dumps(concepts,indent=2,ensure_ascii=False))
for t in cur["tracks"]: (ROOT/f"data/_{t['id']}.json").write_text(json.dumps(t,indent=2,ensure_ascii=False))
(ROOT/"data/_roles.json").write_text(json.dumps(cur["roles"],indent=2,ensure_ascii=False))
(ROOT/"data/_projects.json").write_text(json.dumps(cur["projects"],indent=2,ensure_ascii=False))
h=(ROOT/"index.html").read_text(); emb=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")
h=re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(cur)+"\n"+m.group(2),h,flags=re.S)
h=re.sub(r'(<script id="concepts-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(concepts)+"\n"+m.group(2),h,flags=re.S)
(ROOT/"index.html").write_text(h)
subs=[s for _,s in all_subjects()]; tops=[t for s in subs for t in s["topics"]]
stats=dict(subjects=len(subs),topics=len(tops),subtopics=sum(len(t["subtopics"]) for t in tops),quiz=sum(len(s["quiz"]) for s in subs),
 resources=len({r["url"] for s in subs for r in s["resources"]}),concepts=len(concepts),glossary=len(cur["glossary"]),paths=len(cur["paths"]),
 capstones=len(cur["capstones"]),roles=len(cur["roles"]),projects=len(cur["projects"]),tracks=len(cur["tracks"])+1)
(ROOT/"docs/stats.json").write_text(json.dumps(stats,indent=2)); print(stats)
