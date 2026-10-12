#!/usr/bin/env python3
"""v6 build: runs build_v5, then fills coverage-audit gaps (scripts/v6) and writes docs/coverage_audit.csv."""
import json, random, re, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts/v6"))
subprocess.run([sys.executable,str(ROOT/"scripts/build_v5.py")],check=True,stdout=subprocess.DEVNULL)
import subjects6 as SB
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
    if tr=="shared": cur["shared_core"]["subjects"].append(s)
    else:
        t=next(x for x in cur["tracks"] if x["id"]==tr); next(l for l in t["levels"] if l["id"]==lid)["subjects"].append(s)
for sid,topic in SB.EXTRA_TOPICS.items():
    s=next(s for _,s in all_subjects() if s["id"]==sid)
    if not any(t["id"]==topic["id"] for t in s["topics"]): s["topics"].append(topic)
_d=next(s for _,s in all_subjects() if s["id"]=="e-docrag")["topics"][0]
_lp="Parsers compared: Docling, Unstructured, LlamaParse, cloud document AI"
if not any((x if isinstance(x,str) else x.get("title"))==_lp for x in _d["subtopics"]):
    _d["subtopics"].insert(0,_lp if isinstance(_d["subtopics"][0],str) else {"id":_d["id"]+"-s0","title":_lp})
role=lambda rid: next(r for r in cur["roles"] if r["id"]==rid)
for rid,sids in {"ai-engineer":["g-patterns","g-frameworks","e-reasoning"],"fde":["g-frameworks"],"ai-security":["t-agentattacks"],"governance":["t-responsible"],
  "ml-posttrain":["sc-found","e-rlenv"],"platform":["e-reasoning","g-frameworks"],"product":["t-responsible","e-genmedia"],"evals":["e-rlenv"],"solutions-architect":["g-frameworks"]}.items():
    for x in sids:
        if x not in role(rid)["subjects"]: role(rid)["subjects"].append(x)
u=next(p for p in cur["paths"] if p["id"]=="universal-agentic"); ids=[s[1] for s in u["steps"]]
def ins(after,step):
    if step[1] in [s[1] for s in u["steps"]]: return
    i=[s[1] for s in u["steps"]].index(after)+1; u["steps"].insert(i,step)
ins("sc-llm",["shared","sc-found","NLP foundations: word vectors to scaling laws"])
ins("g-mental",["agentic","g-patterns","Agentic design patterns and deep research"])
ins("e-prompt",["engineer","e-reasoning","Reasoning models and API platform features"])
ins("g-harness",["agentic","g-frameworks","Agent frameworks and managed platforms"])
ins("t-threat",["trust","t-agentattacks","Agent attacks deep dive"])
ins("t-reg",["trust","t-responsible","Responsible AI: fairness, transparency, safety"])
ins("g-train",["engineer","e-rlenv","RL environments and reward design"])
cur["meta"]["version"]="6.0.0"
g={x["term"]:x for x in cur["glossary"]}
for t,d in [("Goal hijacking","An attack where injected content replaces an agent's objective."),("Tool poisoning","Malicious instructions hidden in a tool's description or output."),
 ("Reward hacking","A policy maximizing the reward signal without achieving the intended task."),("Test-time compute","Extra inference computation, such as reasoning tokens, spent to improve answers."),
 ("Scaling laws","Empirical power laws relating loss to parameters, data and compute."),("Diffusion model","A generative model that creates data by iteratively removing noise."),
 ("Demographic parity","A fairness criterion requiring similar positive-outcome rates across groups."),("GEPA","A prompt optimizer that evolves prompts using reflection on trajectories.")]: g[t]={"term":t,"def":d}
cur["glossary"]=sorted(g.values(),key=lambda x:x["term"].lower())
sid={s["id"] for _,s in all_subjects()}
for p in cur["paths"]:
    for k,ref,_ in p["steps"]: assert (k=="capstone" and ref in cur["capstones"]) or ref in sid,(p["id"],ref)
for r in cur["roles"]:
    for x in r["subjects"]: assert x in sid
seen=set()
for _,s in all_subjects():
    assert s["id"] not in seen; seen.add(s["id"]); assert len(s["quiz"])>=3 and len(s["resources"])>=3
    for c in s["conceptIds"]: assert c in cur["conceptIds"],(s["id"],c)
    for t in s["topics"]:
        n=len(t["explainer"].split()); assert 60<=n<=150,(t["id"],n)
(ROOT/"data/curriculum.json").write_text(json.dumps(cur,indent=2,ensure_ascii=False))
for t in cur["tracks"]: (ROOT/f"data/_{t['id']}.json").write_text(json.dumps(t,indent=2,ensure_ascii=False))
(ROOT/"data/_shared.json").write_text(json.dumps(cur["shared_core"],indent=2,ensure_ascii=False))
(ROOT/"data/_roles.json").write_text(json.dumps(cur["roles"],indent=2,ensure_ascii=False))
h=(ROOT/"index.html").read_text(); emb=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")
h=re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(cur)+"\n"+m.group(2),h,flags=re.S)
(ROOT/"index.html").write_text(h)
subs=[s for _,s in all_subjects()]; tops=[t for s in subs for t in s["topics"]]
stats=dict(subjects=len(subs),topics=len(tops),subtopics=sum(len(t["subtopics"]) for t in tops),quiz=sum(len(s["quiz"]) for s in subs),
 resources=len({r["url"] for s in subs for r in s["resources"]}),concepts=len(concepts),glossary=len(cur["glossary"]),paths=len(cur["paths"]),
 capstones=len(cur["capstones"]),roles=len(cur["roles"]),projects=len(cur["projects"]),tracks=len(cur["tracks"])+1)
(ROOT/"docs/stats.json").write_text(json.dumps(stats,indent=2)); print(stats)
