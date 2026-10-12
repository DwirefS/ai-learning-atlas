#!/usr/bin/env python3
"""v9 build: runs build_v8, then adds real case studies (scripts/v9/cases.py), code snippets or conceptual flags
(scripts/v9/code/*.py) and page-specific resource notes (scripts/v9/resnotes9.py)."""
import json, re, sys, subprocess, importlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for p in ("scripts/v9", "scripts/v9/code"): sys.path.insert(0, str(ROOT / p))
subprocess.run([sys.executable, str(ROOT / "scripts/build_v8.py")] + (["--force"] if "--force" in sys.argv else []), check=True, stdout=subprocess.DEVNULL)
from cases import CASES
from resnotes9 import NOTES
CODE = {}
for m in ("science_arch", "engineer", "infer_infra", "agentic_data_trust"): CODE.update(importlib.import_module(m).CODE)
cur = json.loads((ROOT / "data/curriculum.json").read_text()); concepts = json.loads((ROOT / "data/concepts.json").read_text())
def W(s): return len(json.dumps(s, ensure_ascii=False).split()) if not isinstance(s, str) else len(s.split())
def subjects():
    for s in cur["shared_core"]["subjects"]: yield s
    for t in cur["tracks"]:
        for l in t["levels"]: yield from l["subjects"]
S = list(subjects()); errs = []
for s in S:
    L = s["lesson"]; sid = s["id"]
    if sid in CASES:
        L["case"] = dict(CASES[sid]); L["enterpriseLabel"] = "Illustrative scenario"
    else:
        L.pop("case", None); L["enterpriseLabel"] = "Illustrative scenario"
    if sid in CODE:
        v = CODE[sid]
        if v == "conceptual": L["conceptual"] = True; L.pop("code", None); L.pop("lang", None)
        else: L["lang"], L["code"] = v[0], v[1].strip("\n"); L.pop("conceptual", None)
    for r in s["resources"]:
        lv, why = NOTES[r["url"]]; r["level"], r["why"] = lv, why
    e = lambda c, m: c or errs.append((sid, m))
    e(L.get("code") or L.get("conceptual"), "code-or-conceptual")
    if "case" in L:
        c = L["case"]; e(c["url"].startswith("https://") and 2 <= len(re.findall(r"[.!?](\s|$)", c["summary"])) <= 5, "case summary/url")
    e(all(len(r["why"]) > 60 for r in s["resources"]), "notes specific")
for x in errs: print("FAIL", x)
if errs and "--force" not in sys.argv: sys.exit(1)
cur["meta"]["version"] = "9.0.0"
(ROOT / "data/curriculum.json").write_text(json.dumps(cur, indent=2, ensure_ascii=False))
for t in cur["tracks"]: (ROOT / f"data/_{t['id']}.json").write_text(json.dumps(t, indent=2, ensure_ascii=False))
(ROOT / "data/_shared.json").write_text(json.dumps(cur["shared_core"], indent=2, ensure_ascii=False))
h = (ROOT / "index.html").read_text(); emb = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
h = re.sub(r'(<script id="curriculum-data" type="application/json">).*?(</script>)', lambda m: m.group(1) + "\n" + emb(cur) + "\n" + m.group(2), h, flags=re.S)
(ROOT / "index.html").write_text(h)
stats = json.loads((ROOT / "docs/stats.json").read_text())
code = [s for s in S if s["lesson"].get("code")]
stats.update(version="9.0.0", words=W(cur), words_with_concepts=W(cur) + W(concepts),
    real_case_studies=sum(1 for s in S if "case" in s["lesson"]), case_sources=len({s["lesson"]["case"]["url"] for s in S if "case" in s["lesson"]}),
    illustrative_only=sum(1 for s in S if "case" not in s["lesson"]),
    lessons_with_code=len(code), code_by_lang={l: sum(1 for s in code if s["lesson"]["lang"] == l) for l in sorted({s["lesson"]["lang"] for s in code})},
    conceptual_lessons=sum(1 for s in S if s["lesson"].get("conceptual")),
    resource_notes_unique=len({r["url"] for s in S for r in s["resources"]}))
(ROOT / "docs/stats.json").write_text(json.dumps(stats, indent=2)); print(json.dumps(stats))
