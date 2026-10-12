
(function(){
  const DATA = JSON.parse(document.getElementById('curriculum-data').textContent);
  const CONCEPTS = JSON.parse(document.getElementById('concepts-data').textContent);
  const LS='sapient-edge-atlas-v2';
  const state={track:'shared', query:'', mode:'track', progress:load(), quiz:{}, openSubject:null};
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

  const sidebar=document.getElementById('sidebar');
  const content=document.getElementById('content');

  function renderSidebar(){
    const items=[{id:'shared',name:'Shared Core'},...DATA.tracks.map(t=>({id:t.id,name:t.name}))];
    let h=`<div class="brand"><h1>${esc(DATA.meta.title)}</h1><p>${esc(DATA.meta.subtitle)} · ${esc(DATA.meta.as_of)}</p>
      <div class="xp"><div class="row"><span>XP ${(state.progress.xp||0)}</span><span>🔥 streak ${state.progress.streak||0}d</span></div><div class="rank">${rank(state.progress.xp||0)}</div><div class="bar"><i style="width:${Math.min(100,(state.progress.xp||0)/10)}%"></i></div></div></div>
      <div class="nav-label">Tracks</div>`;
    for(const it of items){
      const st=stats(it.id);
      h+=`<button type="button" class="nav-btn ${state.track===it.id&&state.mode==='track'?'active':''}" data-track="${it.id}"><span class="mascot">${ICONS[it.id]||'•'}</span><span style="flex:1;min-width:0"><div>${esc(it.name)}</div><div class="mini"><i style="width:${st.pct}%"></i></div></span><span class="meta">${st.pct}%</span></button>`;
    }
    h+=`<div class="nav-label">Explore</div>`;
    for(const [m,ic,label] of [['roles','🧑‍🚀','Roles ('+(DATA.roles||[]).length+')'],['projects','🪜','Project ladder ('+(DATA.projects||[]).length+')'],['paths','🧭','Learning paths'],['capstones','🏆','Capstone projects'],['concepts','💡','Concept cards ('+CONCEPTS.length+')'],['glossary','📖','Glossary ('+DATA.glossary.length+')']]){
      h+=`<button type="button" class="nav-btn ${state.mode===m?'active':''}" data-mode="${m}"><span class="mascot">${ic}</span><span style="flex:1">${label}</span></button>`;
    }
    h+=`<div class="side-actions"><button type="button" id="btnConcepts">Concept cards (${CONCEPTS.length})</button><button type="button" id="exportProg">Export progress</button><button type="button" id="importProg">Import progress</button></div>`;
    sidebar.innerHTML=h;
    sidebar.querySelectorAll('[data-track]').forEach(b=>b.onclick=()=>{state.track=b.dataset.track;state.mode='track';state.openSubject=null;closeMobile();render();});
    sidebar.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{state.mode=b.dataset.mode;closeMobile();render();window.scrollTo(0,0);});
    document.getElementById('btnConcepts').onclick=()=>{state.mode='concepts';closeMobile();render();};
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
      h+=`<div class="qitem" data-qk="${esc(key)}"><p>${esc(qz.q)}</p>`;
      qz.choices.forEach((c,ci)=>{h+=`<label><input type="radio" name="${esc(key)}" value="${ci}"/> ${esc(c)}</label>`;});
      h+=`<button type="button" data-check="${esc(key)}" data-ans="${qz.answer}" data-why="${esc(qz.why)}">Check</button><div class="qresult"></div></div>`;
    });
    return h+`</div>`;
  }
  function renderSubject(subject, forceOpen){
    if(!matches(subject)) return '';
    const st=subStats(subject); const open=forceOpen||!!state.query||state.openSubject===subject.id;
    let h=`<div class="subject ${open?'open':''}" id="subj-${esc(subject.id)}"><button type="button" class="subject-h" data-toggle="subject"><span class="chev">▶</span><span><strong>${highlight(subject.title)}</strong></span><span class="sp">${st.done}/${st.total}</span></button><div class="subject-body">`;
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
    content.querySelectorAll('input[data-sub]').forEach(inp=>inp.onchange=()=>{setDone(inp.dataset.sub,inp.checked);render();});
    content.querySelectorAll('[data-check]').forEach(btn=>btn.onclick=()=>{
      const key=btn.dataset.check; const ans=+btn.dataset.ans; const box=btn.parentElement;
      const picked=box.querySelector('input:checked'); const res=box.querySelector('.qresult');
      if(!picked){res.innerHTML='<span class="qbad">Pick an answer</span>';return;}
      if(+picked.value===ans){res.innerHTML=`<span class="qok">Correct — ${esc(btn.dataset.why)}</span>`; if(!state.quiz[key]){state.quiz[key]=1; state.progress.xp=(state.progress.xp||0)+5; save(); renderSidebar();}}
      else res.innerHTML=`<span class="qbad">Not quite — ${esc(btn.dataset.why)}</span>`;
    });
    content.querySelectorAll('[data-jump-concept]').forEach(a=>a.onclick=e=>{e.preventDefault();state.mode='concepts';state.query='';document.getElementById('search').value='';render(); setTimeout(()=>{const el=document.getElementById('concept-'+a.dataset.jumpConcept); if(el) el.scrollIntoView({behavior:'smooth'});},50);});
    content.querySelectorAll('[data-jump-subject]').forEach(a=>a.onclick=e=>{e.preventDefault();const f=findSubject(a.dataset.jumpSubject);if(!f)return;state.mode='track';state.track=f.track;state.openSubject=f.s.id;state.query='';document.getElementById('search').value='';render();setTimeout(()=>{const el=document.getElementById('subj-'+f.s.id);if(el)el.scrollIntoView({behavior:'smooth',block:'start'});},60);});
    content.querySelectorAll('[data-jump-cap]').forEach(a=>a.onclick=e=>{e.preventDefault();state.mode='capstones';render();setTimeout(()=>{const el=document.getElementById('cap-'+a.dataset.jumpCap);if(el)el.scrollIntoView({behavior:'smooth'});},60);});
    content.querySelectorAll('[data-role-jump]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('role-'+a.dataset.roleJump);if(el)el.scrollIntoView({behavior:'smooth'});});
    content.querySelectorAll('[data-mode-link]').forEach(a=>a.onclick=e=>{e.preventDefault();state.mode=a.dataset.modeLink;render();window.scrollTo(0,0);});
    content.querySelectorAll('[data-tier-jump]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('tier-'+a.dataset.tierJump);if(el)el.scrollIntoView({behavior:'smooth'});});
    content.querySelectorAll('[data-az]').forEach(a=>a.onclick=e=>{e.preventDefault();const el=document.getElementById('gl-'+a.dataset.az);if(el)el.scrollIntoView({behavior:'smooth'});});
    runMermaid();
  }

  function runMermaid(){
    const nodes=content.querySelectorAll('pre.mermaid');
    if(!nodes.length) return;
    if(window.mermaid){
      try{
        mermaid.initialize({startOnLoad:false, theme:'dark', securityLevel:'strict', fontFamily:'Inter,system-ui,sans-serif'});
        mermaid.run({nodes}).catch(()=>{content.querySelectorAll('.mermaid-fallback').forEach(n=>n.style.display='block');});
      }catch(e){content.querySelectorAll('.mermaid-fallback').forEach(n=>n.style.display='block');}
    } else {
      content.querySelectorAll('.mermaid-fallback').forEach(n=>n.style.display='block');
    }
  }

  function closeMobile(){sidebar.classList.remove('open');document.getElementById('backdrop').classList.remove('show');}

  function render(){
    renderSidebar();
    content.innerHTML = ({roles:renderRoles,projects:renderProjects,concepts:renderConcepts,paths:renderPaths,capstones:renderCapstones,glossary:renderGlossary}[state.mode]||renderTrack)();
    bind();
  }

  document.getElementById('search').oninput=e=>{state.query=e.target.value;render();};
  document.getElementById('expandAll').onclick=()=>content.querySelectorAll('.level,.subject,.topic,.concept').forEach(el=>el.classList.add('open'));
  document.getElementById('collapseAll').onclick=()=>content.querySelectorAll('.level,.subject,.topic,.concept').forEach(el=>el.classList.remove('open'));
  document.getElementById('tabConcepts').onclick=()=>{state.mode='concepts';render();};
  document.getElementById('tabRoles').onclick=()=>{state.mode='roles';render();window.scrollTo(0,0);};
  document.getElementById('tabProjects').onclick=()=>{state.mode='projects';render();window.scrollTo(0,0);};
  document.getElementById('tabPaths').onclick=()=>{state.mode='paths';render();};
  document.getElementById('tabGloss').onclick=()=>{state.mode='glossary';render();};
  document.getElementById('resetProgress').onclick=()=>{if(confirm('Reset XP and checkboxes?')){state.progress={done:{},xp:0,streak:0,last:null};save();render();}};
  document.getElementById('menuBtn').onclick=()=>{sidebar.classList.add('open');document.getElementById('backdrop').classList.add('show');};
  document.getElementById('backdrop').onclick=closeMobile;

  render();
})();
