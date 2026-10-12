#!/usr/bin/env python3
"""Idempotent v3 build: merges scripts/v3/* content into data/*.json and re-embeds into index.html."""
import json, random, re, sys, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V3=ROOT/"scripts/v3"; sys.path.insert(0,str(V3))
import new_subjects as NS, concepts_new as CN, extras as EX, svgs

cur=json.loads((ROOT/"data/curriculum.json").read_text())
concepts=json.loads((ROOT/"data/concepts.json").read_text())

def all_subjects():
    for s in cur["shared_core"]["subjects"]: yield ("shared",None,s)
    for t in cur["tracks"]:
        for l in t["levels"]:
            for s in l["subjects"]: yield (t["id"],l,s)

# 1. new subjects
existing={s["id"] for _,_,s in all_subjects()}
for tr,lid,s in NS.NEW:
    if s["id"] in existing: continue
    t=next(x for x in cur["tracks"] if x["id"]==tr); l=next(x for x in t["levels"] if x["id"]==lid)
    l["subjects"].append(s)
# 2. extra topics
for sid,topic in NS.EXTRA_TOPICS.items():
    s=next(s for _,_,s in all_subjects() if s["id"]==sid)
    if not any(t["id"]==topic["id"] for t in s["topics"]): s["topics"].append(topic)
# 3. topic explainers
expl={}
for f in ["topics_a.txt","topics_b.txt","topics_c.txt"]:
    for line in (V3/f).read_text().splitlines():
        if "|" in line: k,v=line.split("|",1); expl[k]=v
for line in (V3/"topics_extra.txt").read_text().splitlines():
    k,v=line.split("|",1); expl[k]+=" "+v
for _,_,s in all_subjects():
    for t in s["topics"]:
        if t["id"] in expl: t["explainer"]=expl[t["id"]]
# 4. quizzes (shuffle choices deterministically so answers are not always B)
for f in ["quiz_a.txt","quiz_b.txt","quiz_c.txt"]:
    for line in (V3/f).read_text().splitlines():
        sid,q,ch,a,why=line.split("|")
        choices=[c.strip() for c in ch.split("~")]; correct=choices[int(a)]
        rnd=random.Random(q); rnd.shuffle(choices)
        s=next(s for _,_,s in all_subjects() if s["id"]==sid)
        if not any(x["q"]==q for x in s["quiz"]):
            s["quiz"].append({"q":q,"choices":choices,"answer":choices.index(correct),"why":why})
for tr,lid,s in NS.NEW:
    for qq in s["quiz"]:
        if not qq.get("_shuf"):
            correct=qq["choices"][qq["answer"]]; rnd=random.Random(qq["q"]); rnd.shuffle(qq["choices"]); qq["answer"]=qq["choices"].index(correct); qq["_shuf"]=1
    for qq in s["quiz"]: qq.pop("_shuf",None)
# 5. concepts
have={c["id"] for c in concepts}
for c in CN.NEW_CONCEPTS:
    if c["id"] not in have: concepts.append(c)
    else: concepts[[x["id"] for x in concepts].index(c["id"])]=c
for sid,ids in NS.EXTRA_CONCEPT_LINKS.items():
    s=next(s for _,_,s in all_subjects() if s["id"]==sid)
    for i in ids:
        if i not in s["conceptIds"]: s["conceptIds"].append(i)
cur["conceptIds"]=[c["id"] for c in concepts]
# 6. capstones / paths / glossary / illustrations
cur["capstones"]=EX.CAPSTONES
cur["paths"]=EX.PATHS
cur["glossary"]=[{"term":t,"def":d} for t,d in sorted(EX.GLOSSARY,key=lambda x:x[0].lower())]
cur["meta"]["version"]="3.0.0"; cur["meta"]["subtitle"]="0→100 expert paths with explainers, diagrams, labs, capstones and learning paths"
svgs.write_all(ROOT)

# validation
ids={s["id"] for _,_,s in all_subjects()}
for p in cur["paths"]:
    for kind,ref,_ in p["steps"]:
        assert (kind=="capstone" and ref in cur["capstones"]) or ref in ids, (p["id"],ref)
cids=set(cur["conceptIds"])
for _,_,s in all_subjects():
    assert len(s["quiz"])>=3, s["id"]; assert len(s["resources"])>=3, s["id"]
    for c in s["conceptIds"]: assert c in cids,(s["id"],c)
    for t in s["topics"]:
        n=len(t.get("explainer","").split()); assert 60<=n<=150,(t["id"],n)

(ROOT/"data/curriculum.json").write_text(json.dumps(cur,indent=2,ensure_ascii=False))
(ROOT/"data/concepts.json").write_text(json.dumps(concepts,indent=2,ensure_ascii=False))
for t in cur["tracks"]:
    (ROOT/f"data/_{t['id']}.json").write_text(json.dumps(t,indent=2,ensure_ascii=False))
(ROOT/"data/_shared.json").write_text(json.dumps(cur["shared_core"],indent=2,ensure_ascii=False))

# embed into index.html
h=(ROOT/"index.html").read_text()
def emb(o): return json.dumps(o,ensure_ascii=False).replace("</","<\\/")
h=re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(cur)+"\n"+m.group(2),h,flags=re.S)
h=re.sub(r'(<script id="concepts-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+"\n"+emb(concepts)+"\n"+m.group(2),h,flags=re.S)
h=h.replace('<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>','<script src="assets/vendor/mermaid.min.js"></script>')
h=h.replace('<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin/>\n','')
(ROOT/"index.html").write_text(h)

subs=list(all_subjects()); tops=[t for _,_,s in subs for t in s["topics"]]
stats=dict(subjects=len(subs),topics=len(tops),subtopics=sum(len(t["subtopics"]) for t in tops),
  quiz=sum(len(s["quiz"]) for _,_,s in subs),resources=len({r["url"] for _,_,s in subs for r in s["resources"]}),
  concepts=len(concepts),glossary=len(cur["glossary"]),paths=len(cur["paths"]),capstones=len(cur["capstones"]))
(ROOT/"docs/stats.json").write_text(json.dumps(stats,indent=2)); print(stats)
