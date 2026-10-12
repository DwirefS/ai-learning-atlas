import asyncio, sys, json
from playwright.async_api import async_playwright
URL="file:///workspace/ai-learning-atlas/index.html"; SS="/workspace/ai-learning-atlas/docs/screenshots/"
async def run(b,vp,label,full):
    pg=await b.new_page(viewport=vp,is_mobile=label=="mobile"); errs=[]
    pg.on("pageerror",lambda e:errs.append("pageerror "+str(e)))
    pg.on("console",lambda m:errs.append("console "+m.text) if m.type=="error" else None)
    await pg.goto(URL+"#/"); await pg.wait_for_timeout(600)
    ids=await pg.evaluate("(()=>{const D=JSON.parse(document.getElementById('curriculum-data').textContent);const a=D.shared_core.subjects.map(s=>s.id);D.tracks.forEach(t=>t.levels.forEach(l=>l.subjects.forEach(s=>a.push(s.id))));return a;})()")
    bad=[];wbad=[];v9bad=[];ncase=0
    for i in (ids if full else ids[::10]):
        await pg.evaluate(f"location.hash='#/lesson/{i}'")
        try: await pg.wait_for_function("document.querySelector('#sec-diagram pre.mermaid svg')||getComputedStyle(document.querySelector('#sec-diagram .mermaid-fallback')).display!=='none'",timeout=8000)
        except Exception: pass
        ok=await pg.evaluate("!!document.querySelector('#sec-diagram pre.mermaid svg')")
        if not ok: bad.append(i)
        w=await pg.evaluate("[...document.querySelectorAll('[data-widget]')].filter(e=>!e.querySelector('svg')).length")
        if w: wbad.append(i)
        v9=await pg.evaluate("({code:!!document.querySelector('#sec-code pre.code code')||!!document.querySelector('#sec-code .conceptual'),scen:!!document.querySelector('#sec-enterprise .badge.illus'),case:!!document.querySelector('#sec-enterprise .case a[href^=\\'https\\']')})")
        if not (v9['code'] and v9['scen']): v9bad.append(i)
        ncase+=v9['case']
    for r in ["#/","#/track/agentic","#/roles","#/projects","#/paths","#/capstones","#/glossary","#/playground","#/concepts"]:
        await pg.evaluate(f"location.hash='{r}'"); await pg.wait_for_timeout(300 if r!="#/concepts" else 5000)
    cbad=await pg.eval_on_selector_all("pre.mermaid","els=>els.filter(e=>!e.querySelector('svg')).length")
    pw=await pg.eval_on_selector_all("#content [data-widget]","els=>els.filter(e=>!e.querySelector('svg')).length") 
    # keyboard: tab to skip link
    await pg.goto(URL+"#/playground"); await pg.wait_for_timeout(500); nw=await pg.eval_on_selector_all("#content .widget svg","e=>e.length"); await pg.keyboard.press("Tab")
    skip=await pg.evaluate("document.activeElement.className")
    # quiz -> mastery
    await pg.evaluate("i=>location.hash='#/lesson/'+i",ids[5]); await pg.wait_for_timeout(1500)
    nq=await pg.evaluate("document.querySelectorAll('#sec-quiz .qitem').length")
    for k in range(nq):
        ans=await pg.evaluate(f"document.querySelectorAll('#sec-quiz [data-check]')[{k}].dataset.ans")
        await pg.click(f"#sec-quiz .qitem:nth-of-type({k+1}) input[value='{ans}']"); await pg.click(f"#sec-quiz .qitem:nth-of-type({k+1}) [data-check]")
    chip=await pg.inner_text(".l-meta .mchip") if False else await pg.inner_text("#sec-quiz h3 small")
    hscroll=await pg.evaluate("[...document.querySelectorAll('#content *')].filter(e=>e.getBoundingClientRect().right>window.innerWidth+2 && !e.closest('.mermaid-wrap,pre,svg')).length")
    print(label,"lessons",len(ids),"diagram-missing",bad,"widget-missing",wbad,"concept-mermaid-missing",cbad,"playground-widgets",await pg.eval_on_selector_all("#content .widget","e=>e.length") if False else 0,"pw-missing",pw,"playground-svgs",nw,"skip-focus",skip,"quiz",chip,"h-overflow",hscroll,"errors",len(errs),"v9-missing",v9bad,"cases-rendered",ncase)
    for e in errs[:10]: print(" ",e)
    if "--shots" in sys.argv:
        if label=="desktop":
            await pg.evaluate("localStorage.clear()"); await pg.goto(URL+"#/"); await pg.wait_for_timeout(800); await pg.screenshot(path=SS+"16-desktop-home.png")
            await pg.evaluate("location.hash='#/lesson/g-mental'"); await pg.wait_for_timeout(2500); await pg.screenshot(path=SS+"17-desktop-lesson.png")
            await pg.evaluate("document.getElementById('sec-widget').scrollIntoView()"); [await pg.click("#sec-widget button") for _ in range(4)]; await pg.wait_for_timeout(500); await pg.screenshot(path=SS+"19-desktop-lesson-diagram-widget.png")
            await pg.evaluate("location.hash='#/lesson/e-rag'"); await pg.wait_for_timeout(2500); await pg.evaluate("document.getElementById('sec-code').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=SS+"22-desktop-lesson-code-and-case.png")
            await pg.evaluate("location.hash='#/playground'"); await pg.wait_for_timeout(800); await pg.screenshot(path=SS+"20-desktop-playground.png")
        else:
            await pg.evaluate("location.hash='#/lesson/i-mem'"); await pg.wait_for_timeout(2500); await pg.screenshot(path=SS+"18-mobile-lesson.png")
            await pg.evaluate("location.hash='#/'"); await pg.wait_for_timeout(800); await pg.screenshot(path=SS+"21-mobile-home.png")
            await pg.evaluate("location.hash='#/lesson/t-judge'"); await pg.wait_for_timeout(2500); await pg.evaluate("document.getElementById('sec-enterprise').scrollIntoView()"); await pg.wait_for_timeout(300); await pg.screenshot(path=SS+"23-mobile-lesson-case-study.png")
    await pg.close()
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--allow-file-access-from-files"])
    await run(b,{"width":1440,"height":1000},"desktop","--full" in sys.argv)
    await run(b,{"width":390,"height":844},"mobile","--full" in sys.argv)
    await b.close()
asyncio.run(main())
