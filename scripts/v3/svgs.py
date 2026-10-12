from pathlib import Path
COL={"shared":("#5eb0ff","#a78bfa"),"architect":("#5eb0ff","#38bdf8"),"engineer":("#34d399","#5eb0ff"),
     "inference":("#fbbf24","#fb7185"),"infra":("#fb7185","#a78bfa"),"agentic":("#a78bfa","#34d399"),
     "paths":("#34d399","#fbbf24"),"glossary":("#38bdf8","#a78bfa"),"capstone":("#fbbf24","#34d399")}
def wrap(id,a,b,inner,w=480,h=180,label=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<defs><linearGradient id="g{id}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>
<radialGradient id="r{id}" cx=".3" cy=".2" r=".9"><stop stop-color="{a}" stop-opacity=".22"/><stop offset="1" stop-color="{b}" stop-opacity="0"/></radialGradient>
<filter id="f{id}"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect width="{w}" height="{h}" rx="16" fill="url(#r{id})"/>
<g fill="#fff" opacity=".35"><circle cx="30" cy="22" r="1.2"/><circle cx="440" cy="30" r="1.5"/><circle cx="400" cy="150" r="1"/><circle cx="60" cy="150" r="1.3"/><circle cx="250" cy="14" r="1"/></g>
{inner}
</svg>'''
def hero(track):
    a,b=COL[track]; g=f"url(#g{track})"
    if track=="shared":
        nodes=[(90,50),(90,90),(90,130),(200,40),(200,90),(200,140),(310,65),(310,115),(410,90)]
        edges=[(i,j) for i in range(3) for j in range(3,6)]+[(i,j) for i in range(3,6) for j in (6,7)]+[(6,8),(7,8)]
        inner="".join(f'<line x1="{nodes[i][0]}" y1="{nodes[i][1]}" x2="{nodes[j][0]}" y2="{nodes[j][1]}" stroke="{g}" stroke-width="1.6" opacity=".55"/>' for i,j in edges)
        inner+="".join(f'<circle cx="{x}" cy="{y}" r="11" fill="#0e1520" stroke="{g}" stroke-width="3" filter="url(#f{track})"/>' for x,y in nodes)
        inner+=f'<text x="395" y="94" font-size="10" fill="{a}" font-family="monospace">“hi”</text>'
    elif track=="architect":
        inner="".join(f'<line x1="{x}" y1="10" x2="{x}" y2="170" stroke="{a}" opacity=".12"/>' for x in range(20,480,24))
        inner+="".join(f'<line x1="10" y1="{y}" x2="470" y2="{y}" stroke="{a}" opacity=".12"/>' for y in range(20,180,24))
        inner+=f'<rect x="70" y="60" width="90" height="80" rx="8" fill="none" stroke="{g}" stroke-width="3"/><rect x="200" y="30" width="90" height="50" rx="8" fill="none" stroke="{g}" stroke-width="3"/><rect x="200" y="105" width="90" height="50" rx="8" fill="none" stroke="{g}" stroke-width="3"/><rect x="330" y="60" width="90" height="80" rx="8" fill="none" stroke="{g}" stroke-width="3" filter="url(#f{track})"/>'
        inner+=f'<path d="M160 100 H200 M290 55 H330 M290 130 H330" stroke="{b}" stroke-width="2.5" stroke-dasharray="5 4"/>'
        inner+="".join(f'<text x="{x}" y="{y}" fill="{a}" font-size="11" font-family="Inter,sans-serif">{t}</text>' for x,y,t in [(88,104,"Gateway"),(222,59,"Models"),(226,134,"Data"),(350,104,"Agents")])
    elif track=="engineer":
        inner=f'<rect x="60" y="25" width="360" height="130" rx="12" fill="#0e1520" stroke="{g}" stroke-width="3"/><circle cx="80" cy="42" r="5" fill="#fb7185"/><circle cx="96" cy="42" r="5" fill="#fbbf24"/><circle cx="112" cy="42" r="5" fill="#34d399"/>'
        lines=[("def","answer(q):"),("  docs","= retrieve(q)"),("  out","= llm(q, docs)"),("  return","cite(out)")]
        inner+="".join(f'<text x="85" y="{72+i*20}" font-family="monospace" font-size="13"><tspan fill="{b}">{k}</tspan><tspan fill="#e8eef8"> {v}</tspan></text>' for i,(k,v) in enumerate(lines))
        inner+=f'<text x="330" y="125" font-size="42" fill="{g}" font-family="monospace" filter="url(#f{track})">{{}}</text>'
    elif track=="inference":
        inner=f'<rect x="170" y="35" width="140" height="110" rx="14" fill="#0e1520" stroke="{g}" stroke-width="3"/><rect x="200" y="62" width="80" height="56" rx="6" fill="{g}" opacity=".25"/>'
        inner+="".join(f'<line x1="{x}" y1="22" x2="{x}" y2="35" stroke="{a}" stroke-width="3"/><line x1="{x}" y1="145" x2="{x}" y2="158" stroke="{a}" stroke-width="3"/>' for x in range(185,300,18))
        inner+=f'<path d="M248 66 L228 96 H244 L236 116 L258 84 H242 Z" fill="{b}" filter="url(#f{track})"/>'
        inner+="".join(f'<rect x="{330+i*24}" y="{82}" width="16" height="16" rx="4" fill="{g}" opacity="{1-i*0.18}"/>' for i in range(5))
        inner+="".join(f'<rect x="{40+i*24}" y="{82}" width="16" height="16" rx="4" fill="{a}" opacity="{0.3+i*0.15}"/>' for i in range(5))
        inner+=f'<text x="38" y="72" fill="#8b9cb3" font-size="10" font-family="Inter,sans-serif">prompt →</text><text x="330" y="72" fill="#8b9cb3" font-size="10" font-family="Inter,sans-serif">→ tokens</text>'
    elif track=="infra":
        inner=""
        for r,x in enumerate([90,200,310]):
            inner+=f'<rect x="{x}" y="25" width="80" height="135" rx="8" fill="#0e1520" stroke="{g}" stroke-width="2.5"/>'
            for k in range(6):
                y=35+k*20; inner+=f'<rect x="{x+8}" y="{y}" width="64" height="13" rx="3" fill="{a}" opacity=".18"/><circle cx="{x+62}" cy="{y+6.5}" r="2.6" fill="{"#34d399" if (k+r)%4 else "#fb7185"}"/>'
        inner+=f'<path d="M170 90 H200 M280 90 H310" stroke="{b}" stroke-width="3" filter="url(#f{track})"/><path d="M400 60 q30 30 0 60" fill="none" stroke="{b}" stroke-width="2" opacity=".7"/><path d="M415 50 q45 40 0 80" fill="none" stroke="{b}" stroke-width="2" opacity=".4"/>'
    elif track=="agentic":
        inner=f'<rect x="185" y="45" width="110" height="90" rx="22" fill="#0e1520" stroke="{g}" stroke-width="3"/><line x1="240" y1="45" x2="240" y2="25" stroke="{a}" stroke-width="3"/><circle cx="240" cy="20" r="6" fill="{b}" filter="url(#f{track})"/>'
        inner+=f'<circle cx="217" cy="85" r="10" fill="{a}"/><circle cx="263" cy="85" r="10" fill="{a}"/><rect x="215" y="108" width="50" height="8" rx="4" fill="{b}" opacity=".8"/>'
        for x,y,t in [(80,50,"plan"),(80,130,"act"),(400,50,"observe"),(400,130,"verify")]:
            inner+=f'<rect x="{x-40}" y="{y-14}" width="80" height="28" rx="14" fill="none" stroke="{g}" stroke-width="2"/><text x="{x}" y="{y+4}" text-anchor="middle" fill="#e8eef8" font-size="11" font-family="Inter,sans-serif">{t}</text>'
        inner+=f'<path d="M120 50 H185 M120 130 H185 M295 50 H360 M295 130 H360" stroke="{a}" stroke-width="1.8" stroke-dasharray="4 4"/>'
    elif track=="paths":
        inner=f'<path d="M30 150 C120 150, 110 40, 210 70 S330 150, 450 40" fill="none" stroke="{g}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 12"/>'
        inner+="".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#0e1520" stroke="{g}" stroke-width="3"/>' for x,y in [(30,150),(150,95),(260,100),(360,110)])
        inner+=f'<path d="M450 40 v-26 l22 9 -22 9" fill="{b}" stroke="{b}" filter="url(#fpaths)"/>'
    elif track=="glossary":
        inner=f'<rect x="150" y="30" width="180" height="125" rx="10" fill="#0e1520" stroke="{g}" stroke-width="3"/><line x1="240" y1="30" x2="240" y2="155" stroke="{a}" stroke-width="2"/>'
        inner+="".join(f'<line x1="{165 if i%2==0 else 255}" y1="{55+ (i//2)*20}" x2="{225 if i%2==0 else 315}" y2="{55+(i//2)*20}" stroke="{b}" stroke-width="3" opacity=".6"/>' for i in range(10))
        inner+=f'<text x="60" y="100" font-size="38" fill="{g}" font-family="Georgia,serif">Aa</text><text x="360" y="100" font-size="30" fill="{g}" font-family="monospace">KV</text>'
    elif track=="capstone":
        inner=f'<path d="M140 150 L240 40 L340 150 Z" fill="none" stroke="{g}" stroke-width="3"/><path d="M200 150 L240 100 L280 150" fill="{a}" opacity=".2"/><line x1="240" y1="40" x2="240" y2="10" stroke="{b}" stroke-width="3"/><path d="M240 10 h28 l-8 8 8 8 h-28" fill="{b}" filter="url(#fcapstone)"/>'
        inner+="".join(f'<text x="{x}" y="{y}" fill="#8b9cb3" font-size="10" font-family="Inter,sans-serif">{t}</text>' for x,y,t in [(40,60,"architecture"),(40,90,"infra · deploy"),(40,120,"security"),(370,60,"observability"),(370,90,"scaling"),(370,120,"cost")])
    return wrap(track,a,b,inner,label=f"{track} illustration")

LEVEL_NAMES=["Foundations","Builder","Systems","Scale","Frontier"]
def level(track,n):
    a,b=COL[track]; id=f"{track}{n}"; g=f"url(#g{id})"
    if n==1:  # building blocks
        inner="".join(f'<rect x="{x}" y="{y}" width="34" height="22" rx="4" fill="{g}" opacity="{o}"/>' for x,y,o in [(20,52,.9),(58,52,.7),(39,28,.8)])
        inner+=f'<path d="M110 70 q10 -30 0 -50 q-14 20 0 50" fill="{b}" opacity=".8"/>'
    elif n==2:  # gears
        def gear(cx,cy,r):
            t="".join(f'<rect x="{cx-3}" y="{cy-r-6}" width="6" height="9" fill="{a}" transform="rotate({k*45} {cx} {cy})"/>' for k in range(8))
            return t+f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{g}" stroke-width="5"/><circle cx="{cx}" cy="{cy}" r="{r/3}" fill="{b}"/>'
        inner=gear(50,46,20)+gear(98,36,13)
    elif n==3:  # network
        pts=[(25,60),(55,25),(85,60),(115,30),(70,45)]
        inner="".join(f'<line x1="{pts[i][0]}" y1="{pts[i][1]}" x2="{pts[j][0]}" y2="{pts[j][1]}" stroke="{a}" stroke-width="2" opacity=".6"/>' for i,j in [(0,1),(1,2),(2,3),(1,4),(4,2),(0,4),(4,3)])
        inner+="".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#0e1520" stroke="{g}" stroke-width="3"/>' for x,y in pts)
    elif n==4:  # rocket
        inner=f'<path d="M70 12 C88 25 92 50 84 62 H56 C48 50 52 25 70 12 Z" fill="none" stroke="{g}" stroke-width="3.5"/><circle cx="70" cy="36" r="6" fill="{b}"/><path d="M58 62 l-10 12 h14 M82 62 l10 12 h-14" stroke="{a}" stroke-width="3" fill="none"/><path d="M64 66 q6 14 12 0" fill="#fbbf24"/>'
    else:  # summit
        inner=f'<path d="M10 75 L50 25 L72 50 L92 30 L130 75 Z" fill="{g}" opacity=".35" stroke="{g}" stroke-width="3"/><line x1="50" y1="25" x2="50" y2="6" stroke="{b}" stroke-width="2.5"/><path d="M50 6 h16 l-5 5 5 5 h-16" fill="{b}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 80" role="img" aria-label="Level {n} {LEVEL_NAMES[n-1]}"><defs><linearGradient id="g{id}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient></defs>{inner}</svg>'

def write_all(root):
    d=Path(root)/"assets/img"; d.mkdir(parents=True,exist_ok=True); n=0
    for t in COL:
        (d/f"hero-{t}.svg").write_text(hero(t)); n+=1
    for t in ["shared","architect","engineer","inference","infra","agentic"]:
        for k in range(1,6):
            (d/f"level-{t}-{k}.svg").write_text(level(t,k)); n+=1
    return n
