
(function(){
  const DATA = JSON.parse(document.getElementById('curriculum-data').textContent);
  const CONCEPTS = JSON.parse(document.getElementById('concepts-data').textContent);
  const LS='sapient-edge-atlas-v2';
  const state={track:'shared', query:'', mode:'home', progress:load(), openSubject:null, lesson:null};
  state.progress.qa=state.progress.qa||{}; state.quiz=state.progress.qa;
  const RANKS=[[0,'Curious Novice 🌱'],[200,'Apprentice ⚙️'],[600,'Practitioner 🧩'],[1500,'Engineer 🚀'],[3000,'Architect 🏔️'],[6000,'Atlas Master 🌌']];
  function rank(xp){let r=RANKS[0][1];for(const [m,n] of RANKS) if(xp>=m) r=n; return r;}
  const HERO = new Proxy({}, {get:(_,k)=>`<img class="svg-hero" src="assets/img/hero-${k}.svg" alt="${k} illustration" loading="lazy"/>`});
  const ICONS={shared:'◎',architect:'✦',engineer:'⚒',inference:'⚡',infra:'▣',agentic:'✶',data:'⛁',trust:'⛨'};

  function load(){try{return JSON.parse(localStorage.getItem(LS)||'{"done":{},"xp":0,"streak":0,"last":null}');}catch(e){return {done:{},xp:0,streak:0,last:null};}}
  function save(){localStorage.setItem(LS,JSON.stringify(state.progress));}
  function isDone(id){return !!state.progress.done[id];}
  function setDone(id,v){
    const was=isDone(id);
    if(v) state.progress.done[id]=1; else delete state.progress.done[id];
    if(v && !was){ state.progress.xp=(state.progress.xp||0)+10; bumpStreak(); }
    if(!v && was){ state.progress.xp=Math.max(0,(state.progress.xp||0)-10); }
    save();
  }
  function bumpStreak(){
    const today=new Date().toISOString().slice(0,10);
    if(state.progress.last===today) return;
    const y=new Date(Date.now()-864e5).toISOString().slice(0,10);
    state.progress.streak=(state.progress.last===y)?(state.progress.streak||0)+1:1;
    state.progress.last=today;
  }
  function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function highlight(text){
    const q = state.query.trim();
    const e = esc(text);
    if (!q) return e;
    try {
      const safe = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      return e.replace(new RegExp('(' + safe + ')', 'ig'), '<span class="hit">$1</span>');
    } catch (err) { return e; }
  }
  function allIds(trackId){
    const ids=[];
    if(trackId==='shared'){
      for(const s of DATA.shared_core.subjects) for(const t of s.topics) for(const st of t.subtopics) ids.push(st.id);
      return ids;
    }
    const tr=DATA.tracks.find(t=>t.id===trackId);
    for(const l of tr.levels) for(const s of l.subjects) for(const t of s.topics) for(const st of t.subtopics) ids.push(st.id);
    return ids;
  }
  function stats(trackId){const ids=allIds(trackId); const done=ids.filter(isDone).length; return {done,total:ids.length,pct:ids.length?Math.round(100*done/ids.length):0};}
  function subStats(subject){const ids=subject.topics.flatMap(t=>t.subtopics.map(s=>s.id)); const done=ids.filter(isDone).length; return {done,total:ids.length,pct:ids.length?Math.round(100*done/ids.length):0};}
  function levelStats(level){const ids=level.subjects.flatMap(s=>s.topics.flatMap(t=>t.subtopics.map(x=>x.id))); const done=ids.filter(isDone).length; return {done,total:ids.length,pct:ids.length?Math.round(100*done/ids.length):0};}
  function matches(subject){
    const q=state.query.trim().toLowerCase(); if(!q) return true;
    const blob=[subject.title,subject.why,subject.explainer,subject.project,...(subject.resources||[]).map(r=>r.title+' '+r.url),...subject.topics.flatMap(t=>[t.title,t.explainer||'',...t.subtopics.map(s=>s.title)])].join('\n').toLowerCase();
    return blob.includes(q);
  }
  function nextSuggestion(trackId){
    const ids=allIds(trackId);
    for(const id of ids){ if(!isDone(id)){
      // find title
      const walk=(subjects)=>{for(const s of subjects) for(const t of s.topics) for(const st of t.subtopics) if(st.id===id) return s.title+': '+st.title;};
      if(trackId==='shared') return walk(DATA.shared_core.subjects);
      for(const l of DATA.tracks.find(t=>t.id===trackId).levels){const r=walk(l.subjects); if(r) return r;}
    }}
    return 'Track complete — pick another path or review concept cards.';
  }

  /* ---------- v8: lessons, mastery, routes ---------- */
  const ORDER=[];(function(){for(const s of DATA.shared_core.subjects) ORDER.push({track:'shared',s,level:'Shared Core'});for(const t of DATA.tracks) for(const l of t.levels) for(const s of l.subjects) ORDER.push({track:t.id,s,level:l.name});})();
  const TRACKNAME=id=>id==='shared'?'Shared Core':(DATA.tracks.find(t=>t.id===id)||{}).name||id;
  function words(s){const L=s.lesson||{};const parts=[s.why,s.explainer,L.intuition,(L.how||[]).join(' '),L.example,L.code,(L.mistakes||[]).join(' '),L.enterprise,(L.takeaways||[]).join(' '),...s.topics.flatMap(t=>[t.explainer,...t.subtopics.map(x=>x.title+' '+(x.text||''))])];return parts.filter(Boolean).join(' ').split(/\s+/).length;}
  function readMin(s){return Math.max(1,Math.round(words(s)/200));}
  function qScore(s){const n=(s.quiz||[]).length;let ok=0;(s.quiz||[]).forEach((_,i)=>{if(state.progress.qa[s.id+':'+i])ok++;});return {ok,n,frac:n?ok/n:0};}
  const MLEVEL=[['none','Not started','○'],['familiar','Familiar','◔'],['proficient','Proficient','◑'],['mastered','Mastered','●']];
  function mastery(s){const q=qScore(s),st=subStats(s);if(q.frac===1&&st.pct===100)return 3;if(q.frac>=0.8)return 2;if(q.frac>=0.34||(state.progress.seen||{})[s.id])return 1;return 0;}
  function mchip(s){const m=MLEVEL[mastery(s)];return `<span class="mchip m-${m[0]}" title="Mastery: ${m[1]}">${m[2]} ${m[1]}</span>`;}
  function badges(){const b=[];const ms=ORDER.map(o=>mastery(o.s));const c=l=>ms.filter(x=>x>=l).length;
    if(c(1)>=1)b.push(['🌱','First lesson']);if(c(2)>=1)b.push(['🎯','First proficient']);if(c(3)>=1)b.push(['🏅','First mastered']);if(c(2)>=10)b.push(['📚','10 proficient']);
    for(const id of ['shared',...DATA.tracks.map(t=>t.id)]){const L=ORDER.filter(o=>o.track===id);if(L.length&&L.every(o=>mastery(o.s)>=2))b.push(['🏆',TRACKNAME(id)+' proficient']);}
    if((state.progress.streak||0)>=7)b.push(['🔥','7-day streak']);return b;}
  function go(h){if(location.hash===h)route();else location.hash=h;}
  function route(){const p=(location.hash||'#/').replace(/^#\/?/,'').split('/');const v=p[0]||'';
    if(v==='track'&&p[1]){state.mode='track';state.track=p[1];state.openSubject=p[2]||null;}
    else if(v==='lesson'&&p[1]&&ORDER.some(o=>o.s.id===p[1])){state.mode='lesson';state.lesson=p[1];state.progress.seen=state.progress.seen||{};state.progress.seen[p[1]]=1;state.progress.lastLesson=p[1];save();}
    else if(['roles','projects','paths','capstones','concepts','glossary','playground'].includes(v)){state.mode=v;}
    else state.mode='home';
    render(); if(!(v==='track'&&p[2])) window.scrollTo(0,0);
    if(state.mode==='track'&&p[2]) setTimeout(()=>{const el=document.getElementById('subj-'+p[2]);if(el)el.scrollIntoView({block:'start'});},40);
    if(routed){const t=document.getElementById('content'); t.focus({preventScroll:true});} routed=true;}
  let routed=false;
  const LV={intro:'Intro',intermediate:'Intermediate',advanced:'Advanced',reference:'Reference'};
  function renderHome(){
    const all=ORDER.length,ms=ORDER.map(o=>mastery(o.s)),cnt=l=>ms.filter(x=>x===l).length;const last=state.progress.lastLesson&&ORDER.find(o=>o.s.id===state.progress.lastLesson);
    const nxt=last?ORDER[Math.min(ORDER.length-1,ORDER.indexOf(last)+(mastery(last.s)>=2?1:0))]:ORDER[0];
    let h=`<section class="hero home-hero"><h2>Learn AI engineering, one lesson at a time</h2><p class="role">${all} full lessons across ${DATA.tracks.length+1} tracks, centered on agentic AI. Every lesson has an intuition, a step-by-step walkthrough, a diagram, a worked example, common mistakes, an enterprise case, key takeaways, a quiz and annotated resources. Pass quizzes to move from Familiar → Proficient → Mastered.</p>
      <div class="mstats"><span class="mchip m-familiar">◔ ${cnt(1)} familiar</span><span class="mchip m-proficient">◑ ${cnt(2)} proficient</span><span class="mchip m-mastered">● ${cnt(3)} mastered</span><span class="mchip">${Object.keys(window.AtlasWidgets?AtlasWidgets.list:{}).length} interactive explainers</span></div>
      <p><a class="cta" href="#/lesson/${nxt.s.id}">${last?'Continue':'Start'}: ${esc(nxt.s.title)} →</a> <a class="cta ghost" href="#/playground">Try the interactive explainers</a></p></section>
      <h3 class="map-h">Course map</h3><div class="cmap">`;
    for(const id of ['shared',...DATA.tracks.map(t=>t.id)]){const L=ORDER.filter(o=>o.track===id);const pm=Math.round(100*L.filter(o=>mastery(o.s)>=2).length/L.length);
      h+=`<section class="cm-track"><div class="cm-head"><span class="mascot">${ICONS[id]||'•'}</span><a href="#/track/${id}"><strong>${esc(TRACKNAME(id))}</strong></a><span class="pp">${L.length} lessons · ${pm}% proficient</span></div><ol class="cm-tiles">`+
      L.map(o=>{const m=MLEVEL[mastery(o.s)];return `<li><a class="tile m-${m[0]}" href="#/lesson/${o.s.id}" title="${esc(o.s.title)} — ${m[1]}"><span aria-hidden="true">${m[2]}</span> ${esc(o.s.title)}<span class="sr"> (${m[1]})</span></a></li>`;}).join('')+`</ol></section>`;}
    return h+`</div>`;}
  function renderSearch(){const q=state.query.trim().toLowerCase();const hits=ORDER.filter(o=>matches(o.s)||JSON.stringify(o.s.lesson||{}).toLowerCase().includes(q));
    return `<section class="hero"><h2>Search <span class="badge">${hits.length} lessons</span></h2><p class="role">Lessons matching “${esc(state.query)}”.</p></section><ul class="search-list">`+hits.map(o=>`<li><a href="#/lesson/${o.s.id}">${highlight(o.s.title)}</a> <small>${esc(TRACKNAME(o.track))} · ${readMin(o.s)} min</small> ${mchip(o.s)}<p>${highlight(o.s.why)}</p></li>`).join('')+`</ul>`;}
  function renderLesson(){
    const i=ORDER.findIndex(o=>o.s.id===state.lesson),o=ORDER[i],s=o.s,L=s.lesson||{};const prev=ORDER[i-1],next=ORDER[i+1];const q=qScore(s);
    const list=(a,tag)=>`<${tag||'ul'}>${(a||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</${tag||'ul'}>`;
    let h=`<nav class="crumbs" aria-label="Breadcrumb"><a href="#/">Home</a> › <a href="#/track/${o.track}">${esc(TRACKNAME(o.track))}</a> › <span>${esc(o.level)}</span></nav>
    <article class="lesson" aria-labelledby="lt"><header class="l-head"><h2 id="lt">${esc(s.title)}</h2><p class="l-meta">⏱ ${readMin(s)} min read · ${s.topics.length} topics · ${q.n} quiz questions · ${mchip(s)}</p><p class="why"><strong>Why it matters:</strong> ${esc(s.why)}</p>
    <nav class="toc" aria-label="On this page">${[['intuition','Intuition'],['how','How it works'],['diagram','Diagram'],['example','Worked example'],['topics','Topics'],['mistakes','Common mistakes'],['enterprise','In the enterprise'],['takeaways','Key takeaways'],['quiz','Quiz'],['resources','Resources']].map(([a,b])=>`<a href="#/lesson/${s.id}" data-sec="${a}">${b}</a>`).join('')}</nav></header>
    <section id="sec-intuition"><h3>💡 Intuition</h3><p class="lead">${esc(L.intuition||'')}</p></section>
    <section id="sec-how"><h3>⚙️ How it works</h3>${s.explainer?`<p>${esc(s.explainer)}</p>`:''}${list(L.how,'ol')}</section>
    <section id="sec-diagram"><h3>🗺️ Diagram</h3><figure class="ldiagram" role="group" aria-label="${esc(L.diagramAlt||'')}"><div class="mermaid-wrap light" role="img" aria-label="${esc(L.diagramAlt||'')}"><pre class="mermaid">${esc(L.diagram||'')}</pre><pre class="mermaid-fallback">${esc(L.diagram||'')}</pre></div><figcaption>${esc(L.diagramAlt||'')}</figcaption></figure></section>`;
    if(L.widget) h+=`<section id="sec-widget"><div class="widget-mount" data-widget="${L.widget}"></div></section>`;
    h+=`<section id="sec-example"><h3>🧮 Worked example</h3><div class="example">${esc(L.example||'')}</div>${L.code?`<pre class="code"><code>${esc(L.code)}</code></pre>`:''}</section>
    <section id="sec-topics"><h3>📚 Topics</h3>`;
    for(const t of s.topics){h+=`<div class="ltopic"><h4>${esc(t.title)}</h4><p>${esc(t.explainer||'')}</p><ul class="subs">`;
      for(const st of t.subtopics){const d=isDone(st.id);h+=`<li class="sub ${d?'done':''}"><input type="checkbox" id="${esc(st.id)}" data-sub="${esc(st.id)}" ${d?'checked':''}/><label for="${esc(st.id)}"><strong>${esc(st.title)}</strong>${st.text?` — <span class="stext">${esc(st.text)}</span>`:''}</label></li>`;}
      h+=`</ul></div>`;}
    h+=`</section><section id="sec-mistakes" class="box warnbox"><h3>⚠️ Common mistakes</h3>${list(L.mistakes)}</section>
    <section id="sec-enterprise" class="box"><h3>🏢 In the enterprise</h3><p>${esc(L.enterprise||'')}</p></section>
    <section id="sec-takeaways" class="box goodbox"><h3>✅ Key takeaways</h3>${list(L.takeaways)}</section>
    <section id="sec-quiz"><h3>📝 Quiz <small>(${q.ok}/${q.n} correct · 80% = Proficient, 100% + all topics ticked = Mastered)</small></h3>${quizHtml(s)}</section>
    <section id="sec-resources"><h3>🔗 Annotated resources</h3><ul class="res">${(s.resources||[]).map(r=>`<li><a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(r.title)}</a> <span class="lvl lvl-${esc(r.level||'')}">${esc(LV[r.level]||r.level||'')}</span><p>${esc(r.why||'')}</p></li>`).join('')}</ul>
    <div class="card"><h4>Hands-on lab</h4><p>${esc(s.project||'')}</p></div>${s.conceptIds&&s.conceptIds.length?`<p class="deep">Deep dives: ${s.conceptIds.map(id=>{const c=CONCEPTS.find(x=>x.id===id);return `<a href="#/concepts" data-jump-concept="${id}">💡 ${esc(c?c.title:id)}</a>`;}).join(' · ')}</p>`:''}</section>
    <nav class="pn" aria-label="Lesson navigation">${prev?`<a href="#/lesson/${prev.s.id}" rel="prev">← ${esc(prev.s.title)}</a>`:'<span></span>'}${next?`<a href="#/lesson/${next.s.id}" rel="next">${esc(next.s.title)} →</a>`:''}</nav></article>`;
    return h;}
  function renderPlayground(){const W=window.AtlasWidgets?AtlasWidgets.list:{};
    let h=`<section class="hero"><h2>Interactive explainers <span class="badge">${Object.keys(W).length}</span></h2><p class="role">Small, dependency-free simulations. Change the inputs and watch the numbers move. Each also appears inside the lessons that use it.</p></section>`;
    for(const [id,name] of Object.entries(W)){const uses=ORDER.filter(o=>(o.s.lesson||{}).widget===id);h+=`<div class="widget-mount" id="pg-${id}" data-widget="${id}"></div><p class="deep">Used in: ${uses.map(o=>`<a href="#/lesson/${o.s.id}">${esc(o.s.title)}</a>`).join(' · ')||'the playground'}</p>`;}
    return h;}

  const sidebar=document.getElementById('sidebar');
  const content=document.getElementById('content');

  function renderSidebar(){
    const items=[{id:'shared',name:'Shared Core'},...DATA.tracks.map(t=>({id:t.id,name:t.name}))];
    let h=`<div class="brand"><h1>${esc(DATA.meta.title)}</h1><p>${esc(DATA.meta.subtitle)} · ${esc(DATA.meta.as_of)}</p>
      <div class="xp"><div class="row"><span>XP ${(state.progress.xp||0)}</span><span>🔥 streak ${state.progress.streak||0}d</span></div><div class="rank">${rank(state.progress.xp||0)}</div><div class="bar"><i style="width:${Math.min(100,(state.progress.xp||0)/10)}%"></i></div>
      <div class="badges" aria-label="Badges">${badges().map(b=>`<span class="bdg" title="${esc(b[1])}">${b[0]} ${esc(b[1])}</span>`).join('')||'<span class="bdg muted">Pass a quiz to earn badges</span>'}</div></div>
      <a class="nav-btn ${state.mode==='home'?'active':''}" href="#/"><span class="mascot">🏠</span><span>Home · course map</span></a>
      <div class="nav-label">Tracks</div>`;
    for(const it of items){
      const st=stats(it.id);
      h+=`<a class="nav-btn ${state.track===it.id&&(state.mode==='track'||state.mode==='lesson')?'active':''}" href="#/track/${it.id}"><span class="mascot">${ICONS[it.id]||'•'}</span><span style="flex:1;min-width:0"><div>${esc(it.name)}</div><div class="mini"><i style="width:${st.pct}%"></i></div></span><span class="meta">${st.pct}%</span></a>`;
    }
    h+=`<div class="nav-label">Explore</div>`;
    for(const [m,ic,label] of [['roles','🧑‍🚀','Roles ('+(DATA.roles||[]).length+')'],['projects','🪜','Project ladder ('+(DATA.projects||[]).length+')'],['paths','🧭','Learning paths'],['capstones','🏆','Capstone projects'],['concepts','💡','Concept cards ('+CONCEPTS.length+')'],['glossary','📖','Glossary ('+DATA.glossary.length+')'],['playground','🧪','Interactive explainers']]){
      h+=`<a class="nav-btn ${state.mode===m?'active':''}" href="#/${m}"><span class="mascot">${ic}</span><span style="flex:1">${label}</span></a>`;
    }
    h+=`<div class="side-actions"><button type="button" id="exportProg">Export progress</button><button type="button" id="importProg">Import progress</button></div>`;
    sidebar.innerHTML=h;
    sidebar.querySelectorAll('a.nav-btn').forEach(b=>b.addEventListener('click',closeMobile));
    document.getElementById('exportProg').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(state.progress,null,2)],{type:'application/json'}));a.download='atlas-progress.json';a.click();};
    document.getElementById('importProg').onclick=()=>{const i=document.createElement('input');i.type='file';i.accept='.json,application/json';i.onchange=async()=>{try{state.progress=JSON.parse(await i.files[0].text());save();render();}catch(e){alert(e.message);}};i.click();};
  }

  function resourcesHtml(resources){
    return `<ul>${(resources||[]).map(r=>`<li><a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${highlight(r.title)}</a></li>`).join('')}</ul>`;
  }
  function quizHtml(subject){
    if(!subject.quiz||!subject.quiz.length) return '';
    let h=`<div class="quiz"><h4>Self-check</h4>`;
    subject.quiz.forEach((qz,qi)=>{
      const key=subject.id+':'+qi;
      h+=`<div class="qitem" data-qk="${esc(key)}"><p id="q-${esc(key).replace(/[^a-z0-9-]/gi,'_')}"><strong>Q${qi+1}.</strong> ${esc(qz.q)}${state.quiz[key]?' <span class="qok">✓</span>':''}</p>`;
      h+=`<div role="radiogroup" aria-labelledby="q-${esc(key).replace(/[^a-z0-9-]/gi,'_')}">`;qz.choices.forEach((c,ci)=>{h+=`<label><input type="radio" name="${esc(key)}" value="${ci}"/> ${esc(c)}</label>`;});h+=`</div>`;
      h+=`<button type="button" data-check="${esc(key)}" data-ans="${qz.answer}" data-why="${esc(qz.why)}">Check</button><div class="qresult" aria-live="polite"></div></div>`;
    });
    return h+`</div>`;
  }
  function renderSubject(subject, forceOpen){
    if(!matches(subject)) return '';
    const st=subStats(subject); const open=forceOpen||!!state.query||state.openSubject===subject.id;
    let h=`<div class="subject ${open?'open':''}" id="subj-${esc(subject.id)}"><button type="button" class="subject-h" data-toggle="subject"><span class="chev">▶</span><span><strong>${highlight(subject.title)}</strong></span><span class="sp">${mchip(subject)} ${st.done}/${st.total}</span></button><div class="subject-body"><p><a class="cta" href="#/lesson/${esc(subject.id)}">Open full lesson →</a> <small class="muted">⏱ ${readMin(subject)} min</small></p>`;
    h+=`<p class="why"><strong>Why it matters:</strong> ${highlight(subject.why)}</p>`;
    if(subject.explainer) h+=`<div class="explainer">${highlight(subject.explainer)}</div>`;
    h+=`<div class="meta-box"><div class="card"><h4>Resources</h4>${resourcesHtml(subject.resources)}</div><div class="card"><h4>Hands-on lab</h4><p>${highlight(subject.project)}</p></div></div>`;
    if(subject.conceptIds&&subject.conceptIds.length){
      h+=`<p style="font-size:.8rem;color:var(--muted)">Deep dives: ${subject.conceptIds.map(id=>{const c=CONCEPTS.find(x=>x.id===id);return `<a href="#" data-jump-concept="${id}">💡 ${esc(c?c.title:id)}</a>`;}).join(' · ')}</p>`;
    }
    for(const topic of subject.topics){
      h+=`<div class="topic ${open?'open':''}"><button type="button" class="topic-h" data-toggle="topic"><span class="chev">▶</span>${highlight(topic.title)}</button><div class="topic-body">`;
      if(topic.explainer) h+=`<p class="topic-ex">${highlight(topic.explainer)}</p>`;
      for(const sub of topic.subtopics){
        const done=isDone(sub.id);
        h+=`<div class="sub ${done?'done':''}"><input type="checkbox" id="${esc(sub.id)}" data-sub="${esc(sub.id)}" ${done?'checked':''}/><label for="${esc(sub.id)}">${highlight(sub.title)}</label></div>`;
      }
      h+=`</div></div>`;
    }
    h+=quizHtml(subject);
    return h+`</div></div>`;
  }

  function renderTrack(){
    let force=!!state.query;
    if(state.track==='shared'){
      const sc=DATA.shared_core; const st=stats('shared');
      let h=`<section class="hero"><div class="hero-grid"><div><h2>${esc(sc.title)} <span class="badge">cross-track</span></h2><p class="role">${esc(sc.blurb)}</p><div class="bar"><i style="width:${st.pct}%"></i></div><p style="font-size:.8rem;color:var(--muted);margin:.35rem 0 0">${st.pct}% · ${st.done}/${st.total}</p><div class="next">👉 What to learn next: ${esc(nextSuggestion('shared'))}</div></div><div>${HERO.shared}</div></div></section>`;
      for(const s of sc.subjects) h+=renderSubject(s,force);
      if(!state.query) h+=capstoneCard('shared',true);
      return h;
    }
    const track=DATA.tracks.find(t=>t.id===state.track); const st=stats(track.id);
    let h=`<section class="hero"><div class="hero-grid"><div><h2>${esc(track.name)}</h2><p class="role">${esc(track.role)}</p><div class="bar"><i style="width:${st.pct}%"></i></div><p style="font-size:.8rem;color:var(--muted);margin:.35rem 0 0">${st.pct}% · ${st.done}/${st.total}</p><div class="next">👉 What to learn next: ${esc(nextSuggestion(track.id))}</div></div><div>${HERO[track.id]||''}</div></div></section>`;
    track.levels.forEach((level,li)=>{
      const subjectsHtml=level.subjects.map(s=>renderSubject(s,force)).join('');
      if(state.query && !subjectsHtml.trim()) return;
      const ls=levelStats(level); if(state.openSubject && level.subjects.some(x=>x.id===state.openSubject)) force=true;
      const lf=force; force=!!state.query;
      h+=`<div class="level l${li+1} ${lf?'open':''}"><button type="button" class="level-h" data-toggle="level"><span class="chev">▶</span><img class="lvl-art" src="assets/img/level-${track.id}-${li+1}.svg" alt="" loading="lazy"/><span style="font-weight:650">${esc(level.name)}</span><span class="lvl-badge">${level.subjects.length} subjects</span><span style="margin-left:auto;font-size:.75rem;color:var(--muted)">${ls.done}/${ls.total}</span></button><div class="level-body">${subjectsHtml}</div></div>`;
    });
    if(!state.query) h+=capstoneCard(track.id,true);
    return h;
  }

  function capstoneCard(id,teaser){
    const c=DATA.capstones[id]; if(!c) return '';
    const rows=[['🏗️ Architecture',c.architecture],['🖥️ Infra',c.infra],['🚢 Deploy',c.deploy],['🛡️ Security',c.security],['📈 Observability',c.observability],['📐 Scaling',c.scaling],['💰 Cost',c.cost]];
    return `<section class="capstone" id="cap-${id}"><div class="cap-head"><span class="cap-trophy">🏆</span><div><div class="cap-kicker">${esc(id==='shared'?'Shared Core':(DATA.tracks.find(t=>t.id===id)||{}).name||id)} capstone</div><h3>${esc(c.title)}</h3><p>${esc(c.goal)}</p></div></div><div class="cap-grid">${rows.map(([k,v])=>`<div class="cap-cell"><h4>${k}</h4><p>${esc(v)}</p></div>`).join('')}<div class="cap-cell"><h4>📦 Deliverables</h4><ul>${c.deliverables.map(d=>`<li>${esc(d)}</li>`).join('')}</ul></div></div></section>`;
  }
  function findSubject(id){
    for(const s of DATA.shared_core.subjects) if(s.id===id) return {track:'shared',s};
    for(const t of DATA.tracks) for(const l of t.levels) for(const s of l.subjects) if(s.id===id) return {track:t.id,s};
  }
  function renderPaths(){
    let h=`<section class="hero"><div class="hero-grid"><div><h2>Learning paths <span class="badge">${DATA.paths.length}</span></h2><p class="role">Suggested sequences across tracks for common career moves. No deadlines: go at your own pace, skip what you already know, and tick subtopics to see progress fill in.</p></div><div>${HERO.paths}</div></div></section>`;
    for(const p of DATA.paths){
      let done=0,total=0;
      const steps=p.steps.map(([kind,ref,label],i)=>{
        if(kind==='capstone') return `<li class="pstep cap"><span class="pnum">🏆</span><a href="#" data-jump-cap="${ref}">${esc(label)}</a></li>`;
        const f=findSubject(ref); const st=f?subStats(f.s):{done:0,total:0,pct:0}; done+=st.done; total+=st.total;
        return `<li class="pstep ${st.pct===100?'ok':''}"><span class="pnum">${i+1}</span><div><a href="#" data-jump-subject="${ref}">${esc(f?f.s.title:ref)}</a><small>${esc(label)} · ${f?esc(f.track==='shared'?'Shared Core':DATA.tracks.find(t=>t.id===f.track).name):''}</small></div><span class="pp">${st.pct}%</span></li>`;
      }).join('');
      const pct=total?Math.round(100*done/total):0;
      h+=`<section class="path"><div class="path-h"><span class="path-emoji">${p.emoji}</span><div style="flex:1"><h3>${esc(p.title)}</h3><p>${esc(p.who)}</p><div class="bar"><i style="width:${pct}%"></i></div></div><span class="pp">${pct}%</span></div><ol class="psteps">${steps}</ol></section>`;
    }
    return h;
  }

  function roleStats(r){let done=0,total=0;for(const id of r.subjects){const f=findSubject(id);if(!f)continue;const st=subStats(f.s);done+=st.done;total+=st.total;}return {done,total,pct:total?Math.round(100*done/total):0};}
  function renderRoles(){
    const R=DATA.roles||[]; const q=state.query.trim().toLowerCase();
    const use={}; for(const r of R) for(const id of r.subjects) use[id]=(use[id]||0)+1;
    const list=R.filter(r=>!q||JSON.stringify(r).toLowerCase().includes(q));
    let h=`<section class="hero"><div class="hero-grid"><div><h2>Roles <span class="badge">${R.length}</span></h2><p class="role">Every enterprise agentic-AI role, mapped onto the Atlas. The 8 core roles (★) plus 5 roles most lists miss. Each card shows what the job is, what you do day to day, skills, tools, interview signals, a portfolio capstone and a mapped curriculum. Shared subjects are linked, not duplicated: the 🔗 count shows how many roles reuse a subject. Follow the <a href="#" data-mode-link="paths">Universal Agentic Path</a> to cover all of them.</p><div class="role-chips">${R.map(r=>`<a href="#" class="chip" data-role-jump="${r.id}">${r.emoji} ${esc(r.name)}</a>`).join('')}</div></div><div>${HERO.roles}</div></div></section><div class="roles">`;
    for(const r of list){
      const st=roleStats(r);
      const cur=r.subjects.map(id=>{const f=findSubject(id); if(!f) return ''; const s2=subStats(f.s); const tn=f.track==='shared'?'Shared Core':DATA.tracks.find(t=>t.id===f.track).name; return `<li class="${s2.pct===100?'ok':''}"><a href="#" data-jump-subject="${id}">${esc(f.s.title)}</a> <small>${esc(tn)}${use[id]>1?` · 🔗 ${use[id]} roles`:''}</small><span class="pp">${s2.pct}%</span></li>`;}).join('');
      const ul=a=>`<ul>${a.map(x=>`<li>${highlight(x)}</li>`).join('')}</ul>`;
      h+=`<section class="role-card" id="role-${r.id}"><div class="role-head"><span class="role-emoji">${r.emoji}</span><div style="flex:1"><div class="cap-kicker">${r.core?'★ Core role':'＋ Role the list misses'}</div><h3>${highlight(r.name)}</h3><p>${highlight(r.mission)}</p><div class="bar"><i style="width:${st.pct}%"></i></div></div><span class="pp">${st.pct}%</span></div>
      <div class="role-grid"><div class="cap-cell"><h4>📅 Day to day</h4>${ul(r.day)}</div><div class="cap-cell"><h4>🧠 Skills</h4>${ul(r.skills)}</div><div class="cap-cell"><h4>🧰 Tools</h4>${ul(r.tools)}</div><div class="cap-cell"><h4>🎤 Interview signals</h4>${ul(r.interview)}</div><div class="cap-cell"><h4>🏆 Portfolio capstone</h4><p>${highlight(r.capstone)}</p></div></div>
      <details class="role-cur" open><summary>📚 Mapped curriculum (${r.subjects.length} subjects)</summary><ol>${cur}</ol></details></section>`;
    }
    if(!list.length) h+=`<p class="why">No roles match “${esc(state.query)}”.</p>`;
    return h+`</div>`;
  }

  function renderProjects(){
    const P=DATA.projects||[]; const T=DATA.projectTiers||{}; const q=state.query.trim().toLowerCase();
    const list=P.filter(p=>!q||JSON.stringify(p).toLowerCase().includes(q));
    const rn=id=>{const r=(DATA.roles||[]).find(x=>x.id===id);return r?r.emoji+' '+r.name:id;};
    let h=`<section class="hero"><div class="hero-grid"><div><h2>Project ladder <span class="badge">${P.length}</span></h2><p class="role">One AI skill = one project. Each rung is a hands-on build with a goal, stack options, steps, stretch goals and clear "done" criteria, mapped to roles and to the subjects that teach it. Climb from Starter to Expert; tick each project's done criteria to track progress.</p><div class="role-chips">${Object.entries(T).map(([k,v])=>`<a href="#" class="chip" data-tier-jump="${k}">Tier ${k} · ${esc(v)}</a>`).join('')}</div></div><div>${HERO.capstone}</div></div></section>`;
    for(const [k,v] of Object.entries(T)){
      const items=list.filter(p=>String(p.tier)===k); if(!items.length) continue;
      h+=`<h3 class="tier-h" id="tier-${k}">Tier ${k} · ${esc(v)}</h3><div class="roles">`;
      for(const p of items){
        const ul=a=>`<ul>${a.map(x=>`<li>${highlight(x)}</li>`).join('')}</ul>`;
        const done=p.done.map((d,i)=>{const id=p.id+'-done-'+i;const ok=isDone(id);return `<div class="sub ${ok?'done':''}"><input type="checkbox" id="${id}" data-sub="${id}" ${ok?'checked':''}/><label for="${id}">${highlight(d)}</label></div>`;}).join('');
        const nd=p.done.filter((_,i)=>isDone(p.id+'-done-'+i)).length;
        h+=`<section class="role-card" id="proj-${p.id}"><div class="role-head"><span class="role-emoji">${p.emoji}</span><div style="flex:1"><div class="cap-kicker">Tier ${p.tier} · ${esc(v)}</div><h3>${highlight(p.title)}</h3><p>${highlight(p.goal)}</p></div><span class="pp">${nd}/${p.done.length}</span></div>
        <div class="role-grid"><div class="cap-cell"><h4>🧰 Stack options</h4>${ul(p.stack)}</div><div class="cap-cell"><h4>🪜 Steps</h4><ol>${p.steps.map(x=>`<li>${highlight(x)}</li>`).join('')}</ol></div><div class="cap-cell"><h4>🚀 Stretch goals</h4>${ul(p.stretch)}</div><div class="cap-cell"><h4>✅ Done when</h4>${done}</div></div>
        <p style="font-size:.82rem;margin:.7rem 0 0">👥 ${p.roles.map(r=>`<a href="#" data-mode-link="roles">${esc(rn(r))}</a>`).join(' · ')}<br/>📚 ${p.subjects.map(id=>{const f=findSubject(id);return `<a href="#" data-jump-subject="${id}">${esc(f?f.s.title:id)}</a>`;}).join(' · ')}</p></section>`;
      }
      h+=`</div>`;
    }
    if(!list.length) h+=`<p class="why">No projects match “${esc(state.query)}”.</p>`;
    return h;
  }
  function renderCapstones(){
    let h=`<section class="hero"><div class="hero-grid"><div><h2>Capstone projects <span class="badge">${Object.keys(DATA.capstones).length}</span></h2><p class="role">One portfolio-grade project per track. Each covers architecture, infrastructure, deployment, security, observability, scaling and cost, because that is what real AI systems are judged on.</p></div><div>${HERO.capstone}</div></div></section>`;
    for(const id of ['shared',...DATA.tracks.map(t=>t.id)]) h+=capstoneCard(id);
    return h;
  }
  function renderGlossary(){
    const q=state.query.trim().toLowerCase();
    const list=DATA.glossary.filter(g=>!q||(g.term+' '+g.def).toLowerCase().includes(q));
    const letters=[...new Set(DATA.glossary.map(g=>g.term[0].toUpperCase()))];
    let h=`<section class="hero"><div class="hero-grid"><div><h2>Glossary <span class="badge">${list.length}</span></h2><p class="role">Plain-language definitions of the terms used across the Atlas. Type in the search box above to filter.</p><div class="az">${letters.map(l=>`<a href="#" data-az="${l}">${l}</a>`).join('')}</div></div><div>${HERO.glossary}</div></div></section><dl class="gloss">`;
    let last='';
    for(const g of list){const L=g.term[0].toUpperCase(); if(L!==last){h+=`<div class="gl-letter" id="gl-${L}">${L}</div>`; last=L;} h+=`<div class="gl-item"><dt>${highlight(g.term)}</dt><dd>${highlight(g.def)}</dd></div>`;}
    if(!list.length) h+=`<p class="why">No terms match “${esc(state.query)}”.</p>`;
    return h+`</dl>`;
  }

  function renderConcepts(){
    let list=CONCEPTS;
    const q=state.query.trim().toLowerCase();
    if(q) list=list.filter(c=>(c.title+' '+c.summary+' '+c.body).toLowerCase().includes(q));
    let h=`<section class="hero"><h2>Concept cards <span class="badge">${list.length}</span></h2><p class="role">Deeper explainers with diagrams and worked examples. Diagrams render offline with a bundled copy of Mermaid; if rendering ever fails, the diagram source is shown instead.</p></section><div class="concepts">`;
    for(const c of list){
      h+=`<div class="concept open" id="concept-${esc(c.id)}"><button type="button" class="concept-h" data-toggle="concept"><span class="chev">▶</span>${esc(c.title)}</button><div class="concept-body"><p style="color:var(--muted);font-size:.88rem">${esc(c.summary)}</p><div class="body">${esc(c.body)}</div><div class="mermaid-wrap"><pre class="mermaid">${esc(c.mermaid)}</pre><pre class="mermaid-fallback">${esc(c.mermaid)}</pre></div><div class="example"><strong>Worked example:</strong> ${esc(c.example)}</div></div></div>`;
    }
    return h+`</div>`;
  }

  function bind(){
    content.querySelectorAll('[data-toggle]').forEach(btn=>btn.onclick=()=>btn.parentElement.classList.toggle('open'));
    content.querySelectorAll('input[data-sub]').forEach(inp=>inp.onchange=()=>{const y=window.scrollY;setDone(inp.dataset.sub,inp.checked);render();window.scrollTo(0,y);const el=document.getElementById(inp.id);if(el)el.focus({preventScroll:true});});
    content.querySelectorAll('[data-check]').forEach(btn=>btn.onclick=()=>{
      const key=btn.dataset.check; const ans=+btn.dataset.ans; const box=btn.parentElement;
      const picked=box.querySelector('input:checked'); const res=box.querySelector('.qresult');
      if(!picked){res.innerHTML='<span class="qbad">Pick an answer</span>';return;}
      if(+picked.value===ans){res.innerHTML=`<span class="qok">Correct — ${esc(btn.dataset.why)}</span>`; if(!state.quiz[key]){state.quiz[key]=1; state.progress.xp=(state.progress.xp||0)+5; bumpStreak(); save(); renderSidebar(); const hq=document.querySelector('#sec-quiz h3 small'); if(hq&&state.mode==='lesson'){const s=ORDER.find(o=>o.s.id===state.lesson).s,q=qScore(s);hq.textContent=`(${q.ok}/${q.n} correct · now ${MLEVEL[mastery(s)][1]})`;}}}
      else res.innerHTML=`<span class="qbad">Not quite — ${esc(btn.dataset.why)}</span>`;
    });
    content.querySelectorAll('[data-jump-concept]').forEach(a=>a.onclick=e=>{e.preventDefault();state.query='';document.getElementById('search').value='';go('#/concepts'); setTimeout(()=>{const el=document.getElementById('concept-'+a.dataset.jumpConcept); if(el) el.scrollIntoView({behavior:'smooth'});},50);});
    content.querySelectorAll('[data-jump-subject]').forEach(a=>a.onclick=e=>{e.preventDefault();state.query='';document.getElementById('search').value='';go('#/lesson/'+a.dataset.jumpSubject);});
    content.querySelectorAll('[data-jump-cap]').forEach(a=>a.onclick=e=>{e.preventDefault();go('#/capstones');setTimeout(()=>{const el=document.getElementById('cap-'+a.dataset.jumpCap);if(el)el.scrollIntoView({behavior:'smooth'});},60);});
    content.querySelectorAll('[data-role-jump]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('role-'+a.dataset.roleJump);if(el)el.scrollIntoView({behavior:'smooth'});});
    content.querySelectorAll('[data-mode-link]').forEach(a=>a.onclick=e=>{e.preventDefault();go('#/'+a.dataset.modeLink);});
    content.querySelectorAll('[data-tier-jump]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('tier-'+a.dataset.tierJump);if(el)el.scrollIntoView({behavior:'smooth'});});
    content.querySelectorAll('[data-az]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('gl-'+a.dataset.az);if(el)el.scrollIntoView({behavior:'smooth'});});
    content.querySelectorAll('[data-sec]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('sec-'+a.dataset.sec);if(el){el.scrollIntoView({behavior:'smooth'});el.setAttribute('tabindex','-1');el.focus({preventScroll:true});}});
    content.querySelectorAll('[data-widget]').forEach(el=>{if(window.AtlasWidgets)AtlasWidgets.mount(el,el.dataset.widget);});
    runMermaid();
  }

  function runMermaid(){
    const nodes=content.querySelectorAll('pre.mermaid');
    if(!nodes.length) return;
    if(window.mermaid){
      try{
        mermaid.initialize({startOnLoad:false, theme:'base', securityLevel:'strict', fontFamily:'Inter,system-ui,sans-serif', themeVariables:{background:'#f8fafc',primaryColor:'#e0ecff',primaryBorderColor:'#3b82f6',primaryTextColor:'#1e293b',secondaryColor:'#ede9fe',tertiaryColor:'#ecfdf5',lineColor:'#64748b',textColor:'#1e293b',fontSize:'14px'}});
        mermaid.run({nodes}).catch(()=>{content.querySelectorAll('.mermaid-fallback').forEach(n=>n.style.display='block');});
      }catch(e){content.querySelectorAll('.mermaid-fallback').forEach(n=>n.style.display='block');}
    } else {
      content.querySelectorAll('.mermaid-fallback').forEach(n=>n.style.display='block');
    }
  }

  function closeMobile(){sidebar.classList.remove('open');document.getElementById('backdrop').classList.remove('show');}

  function render(){
    renderSidebar();
    const searching=state.query.trim()&&['home','lesson'].includes(state.mode);
    content.innerHTML = searching?renderSearch():({home:renderHome,lesson:renderLesson,playground:renderPlayground,roles:renderRoles,projects:renderProjects,concepts:renderConcepts,paths:renderPaths,capstones:renderCapstones,glossary:renderGlossary}[state.mode]||renderTrack)();
    document.title=(state.mode==='lesson'&&!searching?ORDER.find(o=>o.s.id===state.lesson).s.title+' · ':'')+'AI Learning Atlas';
    bind();
  }

  document.getElementById('search').oninput=e=>{state.query=e.target.value;render();};
  document.getElementById('expandAll').onclick=()=>content.querySelectorAll('.level,.subject,.topic,.concept').forEach(el=>el.classList.add('open'));
  document.getElementById('collapseAll').onclick=()=>content.querySelectorAll('.level,.subject,.topic,.concept').forEach(el=>el.classList.remove('open'));

  document.getElementById('resetProgress').onclick=()=>{if(confirm('Reset XP and checkboxes?')){state.progress={done:{},xp:0,streak:0,last:null};save();render();}};
  document.getElementById('menuBtn').onclick=()=>{sidebar.classList.add('open');document.getElementById('backdrop').classList.add('show');};
  document.getElementById('backdrop').onclick=closeMobile;

  window.addEventListener('hashchange',route);
  route();
})();
