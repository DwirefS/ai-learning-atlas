"""Syntax-check every Python snippet with ast.parse; execute those that use only the stdlib (no network/GPU)."""
import ast, sys, io, json, contextlib, importlib, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "code"))
import subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cur = json.load(open(os.path.join(ROOT, "data/curriculum.json")))
def subjects():
    for s in cur["shared_core"]["subjects"]: yield s
    for t in cur["tracks"]:
        for l in t["levels"]: yield from l["subjects"]
CODE = {s["id"]: ("conceptual" if s["lesson"].get("conceptual") else (s["lesson"]["lang"], s["lesson"]["code"])) for s in subjects()}
STD = set(sys.stdlib_module_names)
res = {"python": 0, "parsed": 0, "executed": 0, "exec_ok": 0, "skipped_thirdparty": [], "failures": [], "other_lang": 0, "conceptual": 0}
for sid, v in sorted(CODE.items()):
    if v == "conceptual": res["conceptual"] += 1; continue
    lang, src = v
    if lang != "python":
        res["other_lang"] += 1
        if lang == "yaml":
            import yaml
            try: list(yaml.safe_load_all(src)); res["yaml_ok"] = res.get("yaml_ok", 0) + 1
            except Exception as e: res["failures"].append((sid, f"yaml: {e}"))
        if lang == "bash":
            r = subprocess.run(["bash", "-n"], input=src, text=True, capture_output=True)
            if r.returncode: res["failures"].append((sid, "bash -n: " + r.stderr))
            else: res["bash_ok"] = res.get("bash_ok", 0) + 1
        continue
    res["python"] += 1
    try: tree = ast.parse(src); res["parsed"] += 1
    except SyntaxError as e: res["failures"].append((sid, f"syntax: {e}")); continue
    mods = {n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import)} | \
           {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    import importlib.util
    if any(importlib.util.find_spec(m) is None for m in mods - STD): res["skipped_thirdparty"].append(sid); continue
    res["executed"] += 1
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf): exec(compile(tree, sid, "exec"), {"__name__": "snippet"})
        res["exec_ok"] += 1
    except BaseException as e: res["failures"].append((sid, repr(e)))
print(json.dumps(res, indent=1))
sys.exit(1 if res["failures"] else 0)
