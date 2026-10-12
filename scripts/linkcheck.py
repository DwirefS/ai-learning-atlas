#!/usr/bin/env python3
import json, csv, subprocess, concurrent.futures
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
cur = json.loads((ROOT/"data/curriculum.json").read_text())
urls = {}
for s in cur["shared_core"]["subjects"]:
    for r in s["resources"]:
        urls[r["url"]] = r["title"]
for t in cur["tracks"]:
    for l in t["levels"]:
        for s in l["subjects"]:
            for r in s["resources"]:
                urls[r["url"]] = r["title"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
def _curl(url, head):
    args=["curl","-sL","--max-time","20","-A",UA,"-o","/dev/null","-w","%{http_code}|%{url_effective}"]
    if head: args.insert(1,"-I")
    try:
        out=subprocess.check_output(args+[url],stderr=subprocess.DEVNULL,text=True)
        return out.split("|",1)
    except Exception as e:
        return "000", str(e)
def check(url):
    code, final = _curl(url, True)
    if not code[:1] in ("2","3"):   # some servers reject HEAD; retry with GET
        code, final = _curl(url, False)
    return url, code, final
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
    for url, code, final in ex.map(check, urls):
        rows.append({"url":url,"status":code,"final_url":final,"title":urls[url]})
rows.sort(key=lambda r:r["url"])
out = ROOT/"docs/resources_linkcheck.csv"
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["url","status","final_url","title"])
    w.writeheader(); w.writerows(rows)
ok=sum(1 for r in rows if r["status"].startswith("2") or r["status"].startswith("3"))
print(f"wrote {out} pass≈{ok}/{len(rows)}")
