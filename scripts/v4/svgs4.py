import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v3"))
import svgs as S
S.COL.update({"data":("#22d3ee","#34d399"),"trust":("#f472b6","#fbbf24"),"roles":("#a78bfa","#fb7185")})
def hero4(track):
    a,b=S.COL[track]; g=f"url(#g{track})"
    if track=="data":
        inner=""
        for i,x in enumerate([60,140,220]):
            inner+=f'<ellipse cx="{x}" cy="50" rx="30" ry="9" fill="#0e1520" stroke="{g}" stroke-width="2.5"/><path d="M{x-30} 50 v60 a30 9 0 0 0 60 0 v-60" fill="none" stroke="{g}" stroke-width="2.5"/><path d="M{x-30} 80 a30 9 0 0 0 60 0" fill="none" stroke="{a}" stroke-width="1.5" opacity=".6"/>'
        inner+=f'<path d="M255 80 C300 80 300 90 340 90" fill="none" stroke="{b}" stroke-width="3" stroke-dasharray="6 5" filter="url(#f{track})"/>'
        inner+=f'<rect x="340" y="60" width="100" height="60" rx="16" fill="#0e1520" stroke="{g}" stroke-width="3"/><circle cx="370" cy="88" r="7" fill="{a}"/><circle cx="410" cy="88" r="7" fill="{a}"/><rect x="372" y="102" width="36" height="5" rx="2.5" fill="{b}"/>'
        inner+="".join(f'<text x="{x}" y="140" text-anchor="middle" fill="#8b9cb3" font-size="10" font-family="Inter,sans-serif">{t}</text>' for x,t in [(60,"CDC"),(140,"lakehouse"),(220,"catalog"),(390,"agent")])
        inner+=f'<text x="300" y="70" text-anchor="middle" fill="{b}" font-size="10" font-family="monospace">MCP</text>'
    elif track=="trust":
        inner=f'<path d="M240 20 L300 42 V92 C300 128 270 150 240 162 C210 150 180 128 180 92 V42 Z" fill="#0e1520" stroke="{g}" stroke-width="3.5" filter="url(#f{track})"/><path d="M215 92 l18 18 32 -36" fill="none" stroke="{b}" stroke-width="5" stroke-linecap="round"/>'
        inner+=f'<polyline points="30,120 60,120 75,90 90,140 105,70 120,120 150,120" fill="none" stroke="{a}" stroke-width="2.5"/>'
        for i,(x,t) in enumerate([(360,"trace"),(360,"eval"),(360,"policy"),(360,"audit")]):
            y=40+i*32; inner+=f'<rect x="{x-35}" y="{y-12}" width="110" height="24" rx="12" fill="none" stroke="{g}" stroke-width="2"/><circle cx="{x-20}" cy="{y}" r="4" fill="{"#34d399" if i!=2 else b}"/><text x="{x-8}" y="{y+4}" fill="#e8eef8" font-size="11" font-family="Inter,sans-serif">{t}</text>'
    elif track=="roles":
        pts=[(240,90)]+[(240+120*__import__("math").cos(k*0.4833),90+62*__import__("math").sin(k*0.4833)) for k in range(13)]
        inner="".join(f'<line x1="240" y1="90" x2="{x:.0f}" y2="{y:.0f}" stroke="{a}" stroke-width="1.4" opacity=".45"/>' for x,y in pts[1:])
        inner+="".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="#0e1520" stroke="{g}" stroke-width="2.5"/>' for x,y in pts[1:])
        inner+=f'<circle cx="240" cy="90" r="24" fill="#0e1520" stroke="{g}" stroke-width="4" filter="url(#froles)"/><text x="240" y="95" text-anchor="middle" fill="{b}" font-size="13" font-family="Inter,sans-serif">agent</text>'
    else:
        return S.hero(track)
    return S.wrap(track,a,b,inner,label=f"{track} illustration")
def write_all(root):
    d=Path(root)/"assets/img"; n=0
    for t in ["data","trust","roles"]:
        (d/f"hero-{t}.svg").write_text(hero4(t)); n+=1
    for t in ["data","trust"]:
        for k in range(1,6): (d/f"level-{t}-{k}.svg").write_text(S.level(t,k)); n+=1
    return n
