#!/usr/bin/env python3
"""v10 build: runs build_v9, then adds the Backend & Software Foundations track (scripts/v10/backend_*.py),
five FDE engagement-craft lessons in the architect track (scripts/v10/fde10.py), two concept cards, the FDE capstone,
role and path mappings, the 'Forward Deployed Engineer (Dhanush N roadmap)' path and glossary terms (scripts/v10/extras10.py).
Idempotent: v10 subjects are replaced wholesale on every run."""
import json, re, sys, subprocess, importlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "scripts/v10"))
subprocess.run([sys.executable, str(ROOT / "scripts/build_v9.py")] + (["--force"] if "--force" in sys.argv else []), check=True, stdout=subprocess.DEVNULL)
import extras10 as X
from fde10 import S as FDE, CONCEPTS
BK = {}
for m in ("backend_a", "backend_b", "backend_c"):
    for s in importlib.import_module(m).S: BK[s["id"]] = s
FD = {s["id"]: s for s in FDE}; NEW = {**BK, **FD}
cur = json.loads((ROOT / "data/curriculum.json").read_text()); concepts = json.loads((ROOT / "data/concepts.json").read_text())
def clean(s):
    s = json.loads(json.dumps(s)); s["lesson"] = {k: v for k, v in s["lesson"].items() if v is not None}; return s
# track + architect placement (replace wholesale)
cur["tracks"] = [t for t in cur["tracks"] if t["id"] != "backend"]
track = dict(id=X.TRACK["id"], name=X.TRACK["name"], role=X.TRACK["role"], icon=X.TRACK["icon"],
             levels=[dict(id=i, name=n, subjects=[clean(BK[s]) for s in ids]) for i, n, ids in X.LEVELS])
assert sorted(s for _, _, ids in X.LEVELS for s in ids) == sorted(BK)
cur["tracks"].insert(0, track)
arch = next(t for t in cur["tracks"] if t["id"] == "architect")
for l in arch["levels"]:
    l["subjects"] = [s for s in l["subjects"] if s["id"] not in FD] + [clean(FD[s]) for s in X.ARCH_PLACEMENT.get(l["id"], [])]
# concepts
ids = {c["id"] for c in CONCEPTS}; concepts = [c for c in concepts if c["id"] not in ids] + CONCEPTS
cur["conceptIds"] = [c["id"] for c in concepts]
# capstone, roles, paths, glossary
cur["capstones"]["backend"] = X.CAPSTONE
for r in cur["roles"]:
    for sid in X.ROLE_ADD.get(r["id"], []):
        if sid not in r["subjects"]: r["subjects"].append(sid)
    if r["id"] == "fde" and X.FDE_CAPSTONE_TEXT not in r["capstone"]: r["capstone"] = r["capstone"].rstrip() + " " + X.FDE_CAPSTONE_TEXT
u = next(p for p in cur["paths"] if p["id"] == "universal-agentic")
st = [x for x in u["steps"] if x[1] not in NEW]
k = max(i for i, x in enumerate(st) if x[0] == "shared") + 1 if any(x[0] == "shared" for x in st) else 0
st = st[:k] + X.UNIVERSAL_INSERT + st[k:]
j = next(i for i, x in enumerate(st) if x[1] == X.UNIVERSAL_FDE_AFTER) + 1
u["steps"] = st[:j] + X.UNIVERSAL_FDE + st[j:]
cur["paths"] = [p for p in cur["paths"] if p["id"] != X.PATH["id"]] + [X.PATH]
have = {g["term"] for g in cur["glossary"]}
cur["glossary"] += [dict(term=t, definition=d) for t, d in X.GLOSSARY if t not in have]
cur["glossary"].sort(key=lambda g: g["term"].lower())
# validate (v7 + v8 + v9 bars) for the new subjects, plus global path/role integrity
def W(s): return len(json.dumps(s, ensure_ascii=False).split()) if not isinstance(s, str) else len(s.split())
ALL = {s["id"]: s for s in cur["shared_core"]["subjects"]}; ALL.update({s["id"]: s for t in cur["tracks"] for l in t["levels"] for s in l["subjects"]})
TR = {s["id"]: t["id"] for t in cur["tracks"] for l in t["levels"] for s in l["subjects"]}; TR.update({s["id"]: "shared" for s in cur["shared_core"]["subjects"]})
WID = {"softmax", "tokenizer", "attention", "kvcache", "batching", "quant", "rag", "agentloop", "eval", "routing", "budget"}
errs = []; e = lambda c, sid, m: c or errs.append((sid, m))
ref = next(iter(ALL.values()))
for sid in NEW:
    s = ALL[sid]; L = s["lesson"]
    e(set(ref) <= set(s), sid, f"keys missing {set(ref)-set(s)}")
    e(W(L["intuition"]) >= 40 and len(L["how"]) >= 3 and W(L["example"]) >= 40, sid, "intuition/how/example")
    e(len(L["mistakes"]) >= 3 and W(L["enterprise"]) >= 25 and len(L["takeaways"]) >= 3, sid, "mistakes/enterprise/takeaways")
    e(L.get("diagram") and len(L.get("diagramAlt", "")) > 30, sid, "diagram"); e(not L.get("widget") or L["widget"] in WID, sid, "widget")
    e(L.get("code") or L.get("conceptual"), sid, "code-or-conceptual"); e(L.get("enterpriseLabel") == "Illustrative scenario", sid, "label")
    if "case" in L:
        c = L["case"]; e(c["url"].startswith("https://") and 2 <= len(re.findall(r"[.!?](\s|$)", c["summary"])) <= 5, sid, "case")
    e(len(s["quiz"]) >= 3 and all(q.get("why") and q["answer"] in range(len(q["choices"])) for q in s["quiz"]), sid, "quiz")
    e(len(s["resources"]) >= 3 and all(r.get("level") and len(r.get("why", "")) > 60 and r["url"].startswith("https://") for r in s["resources"]), sid, "resources")
    for c in s["conceptIds"]: e(c in cur["conceptIds"], sid, "concept " + c)
    for t in s["topics"]:
        e(60 <= W(t["explainer"]) <= 150, sid, f"topic words {t['id']} {W(t['explainer'])}")
        e(sum(1 for x in t["subtopics"] if x.get("text")) >= 2, sid, "subs " + t["id"])
for p in cur["paths"]:
    for tr, sid, _ in p["steps"]: e(TR.get(sid) == tr or (tr == "capstone" and sid in cur["capstones"]), p["id"], f"step {tr}/{sid}")
for r in cur["roles"]:
    for sid in r["subjects"]: e(sid in ALL, r["id"], "role subj " + sid)
for x in errs: print("FAIL", x)
if errs and "--force" not in sys.argv: sys.exit(1)
cur["meta"]["version"] = "10.0.0"
(ROOT / "data/curriculum.json").write_text(json.dumps(cur, indent=2, ensure_ascii=False))
(ROOT / "data/concepts.json").write_text(json.dumps(concepts, indent=2, ensure_ascii=False))
for t in cur["tracks"]: (ROOT / f"data/_{t['id']}.json").write_text(json.dumps(t, indent=2, ensure_ascii=False))
h = (ROOT / "index.html").read_text(); emb = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
for tag, obj in (("curriculum-data", cur), ("concepts-data", concepts)):
    assert f'<script id="{tag}"' in h, tag
    h = re.sub(rf'(<script id="{tag}" type="application/json">).*?(</script>)', lambda m: m.group(1) + "\n" + emb(obj) + "\n" + m.group(2), h, flags=re.S)
(ROOT / "index.html").write_text(h)
S = list(ALL.values()); code = [s for s in S if s["lesson"].get("code")]
stats = json.loads((ROOT / "docs/stats.json").read_text())
stats.update(version="10.0.0", tracks=len(cur["tracks"]), subjects=len(S), lessons=len(S), concepts=len(concepts), paths=len(cur["paths"]), glossary=len(cur["glossary"]), capstones=len(cur["capstones"]), roles=len(cur["roles"]),
    topics=sum(len(s["topics"]) for s in S), subtopics=sum(len(t["subtopics"]) for s in S for t in s["topics"]), quiz=sum(len(s["quiz"]) for s in S),
    resources=sum(len(s["resources"]) for s in S), annotated_resources=len({r["url"] for s in S for r in s["resources"]}), lesson_diagrams=sum(1 for s in S if s["lesson"].get("diagram")),
    concept_diagrams=sum(1 for c in concepts if c.get("mermaid")), subtopic_explanations=sum(1 for s in S for t in s["topics"] for x in t["subtopics"] if x.get("text")),
    words=W(cur), words_with_concepts=W(cur) + W(concepts), real_case_studies=sum(1 for s in S if "case" in s["lesson"]),
    case_sources=len({s["lesson"]["case"]["url"] for s in S if "case" in s["lesson"]}), illustrative_only=sum(1 for s in S if "case" not in s["lesson"]),
    lessons_with_code=len(code), code_by_lang={l: sum(1 for s in code if s["lesson"]["lang"] == l) for l in sorted({s["lesson"]["lang"] for s in code})},
    conceptual_lessons=sum(1 for s in S if s["lesson"].get("conceptual")), resource_notes_unique=len({r["url"] for s in S for r in s["resources"]}),
    v10_new_subjects=len(NEW), v10_new_concepts=len(CONCEPTS), v10_source=X.SRC)
(ROOT / "docs/stats.json").write_text(json.dumps(stats, indent=2)); print(json.dumps(stats))
