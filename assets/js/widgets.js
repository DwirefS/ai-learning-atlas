/* Atlas interactive explainers: dependency-free JS + SVG. Every control is a native,
   labelled input or button (keyboard accessible); results are announced via aria-live. */
(function(){
const NS='http://www.w3.org/2000/svg';
const C={blue:'#3b82f6',violet:'#8b5cf6',green:'#10b981',amber:'#f59e0b',rose:'#f43f5e',ink:'#1e293b',muted:'#64748b',grid:'#e2e8f0'};
let uid=0;
function h(tag,attrs,kids){const e=document.createElement(tag);for(const k in attrs||{}){if(k==='text')e.textContent=attrs[k];else e.setAttribute(k,attrs[k]);}(kids||[]).forEach(c=>e.appendChild(c));return e;}
function s(tag,attrs){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);return e;}
function svgText(x,y,t,o){const e=s('text',Object.assign({x,y,'font-size':12,fill:C.ink,'font-family':'Inter,system-ui,sans-serif'},o||{}));e.textContent=t;return e;}
function slider(label,min,max,step,val,fmt){const id='w'+(++uid);const out=h('output',{for:id});const inp=h('input',{type:'range',id,min,max,step,value:val});
  const wrap=h('div',{class:'w-ctl'},[h('label',{for:id,text:label}),inp,out]);const upd=()=>{out.textContent=fmt?fmt(+inp.value):inp.value;};upd();inp.addEventListener('input',upd);return {wrap,inp,get v(){return +inp.value;}};}
function numIn(label,val,step){const id='w'+(++uid);const inp=h('input',{type:'number',id,value:val,step:step||'any'});return {wrap:h('div',{class:'w-ctl'},[h('label',{for:id,text:label}),inp]),inp,get v(){return +inp.value;}};}
function frame(el,title,intro){el.innerHTML='';el.classList.add('widget');const live=h('div',{class:'w-out','aria-live':'polite'});
  const svg=s('svg',{viewBox:'0 0 560 220',width:'100%',role:'img','aria-label':title});
  el.append(h('h4',{class:'w-title',text:'🧪 '+title}),h('p',{class:'w-intro',text:intro}));const ctl=h('div',{class:'w-ctls'});el.append(ctl,svg,live);return {ctl,svg,live};}
function clear(svg){while(svg.firstChild)svg.removeChild(svg.firstChild);}
function bars(svg,items,max,opts){clear(svg);opts=opts||{};const n=items.length,W=560,H=220,pad=30,bw=(W-2*pad)/n;
  svg.appendChild(s('line',{x1:pad,y1:H-30,x2:W-pad,y2:H-30,stroke:C.grid}));
  items.forEach((it,i)=>{const hgt=max?Math.max(0,(H-60)*it.v/max):0;const x=pad+i*bw+bw*0.15;
    svg.appendChild(s('rect',{x,y:H-30-hgt,width:bw*0.7,height:hgt,rx:6,fill:it.c||C.blue}));
    svg.appendChild(svgText(x+bw*0.35,H-12,it.label,{'text-anchor':'middle','font-size':11}));
    svg.appendChild(svgText(x+bw*0.35,H-36-hgt,it.txt!=null?it.txt:String(it.v),{'text-anchor':'middle','font-size':11,fill:C.muted}));});}
const fmtB=b=>b>=2**30?(b/2**30).toFixed(2)+' GiB':b>=2**20?(b/2**20).toFixed(1)+' MiB':(b/1024).toFixed(1)+' KiB';
const pct=x=>(100*x).toFixed(1)+'%';

const W={};
W.softmax=el=>{const f=frame(el,'Softmax and temperature','Logits are raw scores. Softmax turns them into probabilities: p_i = exp(z_i/T) / Σ exp(z_j/T). Lower temperature sharpens, higher flattens.');
  const L=[slider('Logit "cat"',-5,5,0.1,2),slider('Logit "dog"',-5,5,0.1,1),slider('Logit "car"',-5,5,0.1,-1),slider('Temperature T',0.1,3,0.1,1)];
  L.forEach(x=>f.ctl.append(x.wrap));
  const draw=()=>{const T=L[3].v,z=L.slice(0,3).map(x=>x.v/T),m=Math.max(...z),e=z.map(v=>Math.exp(v-m)),S=e.reduce((a,b)=>a+b,0),p=e.map(v=>v/S);
    bars(f.svg,['cat','dog','car'].map((n,i)=>({label:n,v:p[i],txt:pct(p[i]),c:[C.blue,C.violet,C.amber][i]})),1);
    f.svg.setAttribute('aria-label','Softmax probabilities: cat '+pct(p[0])+', dog '+pct(p[1])+', car '+pct(p[2]));
    f.live.textContent=`At T=${T.toFixed(1)}: cat ${pct(p[0])}, dog ${pct(p[1])}, car ${pct(p[2])}. Probabilities always sum to 100%.`;};
  L.forEach(x=>x.inp.addEventListener('input',draw));draw();};

W.tokenizer=el=>{const f=frame(el,'Tokenization (illustrative)','Models read tokens, not characters. This toy tokenizer splits words and punctuation, then breaks long or rare words into pieces, mimicking how BPE handles unfamiliar words. Real tokenizers learn their pieces from data, so exact counts differ.');
  const id='w'+(++uid);const ta=h('textarea',{id,rows:3});ta.value='Tokenization splits unbelievably long words into pieces, e.g. "transformers" → trans|form|ers. 12345 too!';
  f.ctl.append(h('div',{class:'w-ctl w-wide'},[h('label',{for:id,text:'Text'}),ta]));
  const common=new Set('the a an of to and in is it for on with as was be by this that are or from at not but you we they he she i e.g. too into long words pieces'.split(' '));
  const pal=[C.blue,C.violet,C.green,C.amber,C.rose];
  const tok=t=>{const out=[];(t.match(/\s?[A-Za-z]+|\s?\d|\s?[^\sA-Za-z\d]|\s+/g)||[]).forEach(w=>{const core=w.trim().toLowerCase();if(core.length<=6||common.has(core)){out.push(w);return;}let r=w;while(r.length>0){const n=r.startsWith(' ')?5:4;out.push(r.slice(0,n));r=r.slice(n);}});return out;};
  const draw=()=>{const t=tok(ta.value);clear(f.svg);let x=10,y=24;t.forEach((p,i)=>{const w=Math.max(14,p.length*7.2+8);if(x+w>550){x=10;y+=28;}if(y>210)return;
      f.svg.appendChild(s('rect',{x,y:y-16,width:w,height:22,rx:5,fill:pal[i%5],'fill-opacity':0.18,stroke:pal[i%5]}));
      f.svg.appendChild(svgText(x+4,y,p.replace(/ /g,'·'),{'font-size':12,'font-family':'ui-monospace,monospace'}));x+=w+3;});
    const chars=ta.value.length;f.svg.setAttribute('aria-label',`${t.length} tokens for ${chars} characters`);
    f.live.textContent=`${t.length} tokens for ${chars} characters (${(chars/Math.max(1,t.length)).toFixed(2)} chars/token). English text with real tokenizers is often around 4 characters per token. · marks a leading space.`;};
  ta.addEventListener('input',draw);draw();};

W.attention=el=>{const f=frame(el,'Self-attention weights (toy vectors)','Pick a query token. Its attention over other tokens is softmax(q·k / √d). The vectors here are small hand-made examples so you can see the mechanics; real models learn them.');
  const words=['The','cat','sat','on','the','mat'];
  const E={The:[1,0,0,.2],cat:[0,1,.8,0],sat:[.1,.9,1,0],on:[.6,0,.2,1],the:[1,0,0,.2],mat:[0,.9,.6,.3]};
  const id='w'+(++uid);const sel=h('select',{id});words.forEach((w,i)=>sel.append(h('option',{value:i,text:`${i}: ${w}`})));sel.value=2;
  const cid='w'+(++uid);const cm=h('input',{type:'checkbox',id:cid,checked:'checked'});
  f.ctl.append(h('div',{class:'w-ctl'},[h('label',{for:id,text:'Query token'}),sel]),h('div',{class:'w-ctl'},[cm,h('label',{for:cid,text:'Causal mask (decoder: only look left)'})]));
  const draw=()=>{const q=+sel.value,d=4,sc=words.map((w,j)=>(cm.checked&&j>q)?-Infinity:E[words[q]].reduce((a,v,k)=>a+v*E[w][k],0)/Math.sqrt(d));
    const m=Math.max(...sc),e=sc.map(v=>v===-Infinity?0:Math.exp(v-m)),S=e.reduce((a,b)=>a+b,0),p=e.map(v=>v/S);
    bars(f.svg,words.map((w,i)=>({label:w,v:p[i],txt:pct(p[i]),c:i===q?C.violet:C.blue})),Math.max(...p));
    f.live.textContent=`"${words[q]}" attends most to "${words[p.indexOf(Math.max(...p))]}" (${pct(Math.max(...p))}).`+(cm.checked?' Masked future tokens get 0%.':'');};
  sel.addEventListener('change',draw);cm.addEventListener('change',draw);draw();};

W.kvcache=el=>{const f=frame(el,'KV cache memory calculator','KV bytes = 2 (K and V) × layers × KV heads × head dim × bytes per value × tokens × concurrent sequences. Defaults match a Llama-3-8B-style model (32 layers, 8 KV heads, head dim 128) in FP16.');
  const I=[numIn('Layers',32,1),numIn('KV heads',8,1),numIn('Head dim',128,1),numIn('Bytes/value (2=FP16, 1=FP8)',2,1),slider('Context tokens',512,131072,512,8192,v=>v.toLocaleString()),slider('Concurrent sequences',1,256,1,16)];
  I.forEach(x=>f.ctl.append(x.wrap));
  const draw=()=>{const per=2*I[0].v*I[1].v*I[2].v*I[3].v,tot=per*I[4].v*I[5].v;const gpus=[['24 GB',24],['80 GB',80],['141 GB',141]];
    bars(f.svg,gpus.map(([n,g])=>({label:n+' GPU',v:Math.min(tot/(g*1e9),1.5),txt:pct(tot/(g*1e9))+' of HBM',c:tot>g*1e9?C.rose:C.green})),1.5);
    f.svg.appendChild(svgText(10,16,'KV cache as share of GPU memory (red = does not fit, before weights)',{fill:C.muted,'font-size':11}));
    f.live.textContent=`${fmtB(per)} per token → ${fmtB(tot)} total for ${I[4].v.toLocaleString()} tokens × ${I[5].v} sequences.`;};
  I.forEach(x=>x.inp.addEventListener('input',draw));draw();};

W.batching=el=>{const f=frame(el,'Static vs continuous batching','Each bar is a request generating tokens. Static batching waits for the longest request before starting the next batch; continuous batching refills a slot as soon as a request finishes.');
  const n=slider('Requests',4,16,1,10),slots=slider('Batch slots',2,6,1,4);const id='w'+(++uid);const sel=h('select',{id});['continuous','static'].forEach(v=>sel.append(h('option',{value:v,text:v})));
  const btn=h('button',{type:'button',text:'New random lengths'});f.ctl.append(n.wrap,slots.wrap,h('div',{class:'w-ctl'},[h('label',{for:id,text:'Scheduler'}),sel]),btn);
  let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647;};let lens=[];const gen=()=>{lens=Array.from({length:16},()=>2+Math.floor(rnd()*14));};gen();
  const draw=()=>{const N=n.v,B=slots.v,L=lens.slice(0,N),sched=[];
    if(sel.value==='static'){let t=0;for(let i=0;i<N;i+=B){const g=L.slice(i,i+B);g.forEach((l,j)=>sched.push({slot:j,start:t,len:l,i:i+j}));t+=Math.max(...g);}}
    else{const free=Array(B).fill(0);L.forEach((l,i)=>{const j=free.indexOf(Math.min(...free));sched.push({slot:j,start:free[j],len:l,i});free[j]+=l;});}
    const T=Math.max(...sched.map(r=>r.start+r.len)),busy=L.reduce((a,b)=>a+b,0),util=busy/(T*B);clear(f.svg);
    const sx=500/T,rh=Math.min(30,180/B);sched.forEach(r=>{f.svg.appendChild(s('rect',{x:40+r.start*sx,y:10+r.slot*(rh+4),width:Math.max(1,r.len*sx-2),height:rh,rx:4,fill:[C.blue,C.violet,C.green,C.amber,C.rose][r.i%5],'fill-opacity':.75}));});
    for(let j=0;j<B;j++)f.svg.appendChild(svgText(4,10+j*(rh+4)+rh*0.65,'slot '+(j+1),{'font-size':10,fill:C.muted}));
    f.svg.setAttribute('aria-label',`${sel.value} batching: ${T} steps, ${pct(util)} slot utilization`);
    f.live.textContent=`${sel.value}: all ${N} requests finish in ${T} decode steps; slot utilization ${pct(util)}. Switch the scheduler to compare.`;};
  [n.inp,slots.inp].forEach(x=>x.addEventListener('input',draw));sel.addEventListener('change',draw);btn.addEventListener('click',()=>{gen();draw();});draw();};

W.quant=el=>{const f=frame(el,'Quantization: memory and rounding error','Weight memory = parameters × bits ÷ 8. Below, 8 sample weights are quantized with symmetric absmax scaling (scale = max|w| ÷ (2^(b−1)−1)) to show the rounding error.');
  const P=slider('Parameters (billions)',1,405,1,70),b=slider('Bits per weight',2,16,1,4);f.ctl.append(P.wrap,b.wrap);
  const w=[0.12,-0.48,0.91,-0.05,0.33,-1.27,0.07,0.6];
  const draw=()=>{const bits=b.v,mem=P.v*1e9*bits/8;const qmax=2**(bits-1)-1,sc=Math.max(...w.map(Math.abs))/qmax,dq=w.map(x=>Math.round(x/sc)*sc),err=Math.sqrt(w.reduce((a,x,i)=>a+(x-dq[i])**2,0)/w.length);
    clear(f.svg);const y0=110,k=70;f.svg.appendChild(s('line',{x1:20,y1:y0,x2:540,y2:y0,stroke:C.grid}));
    w.forEach((x,i)=>{const cx=50+i*64;f.svg.appendChild(s('rect',{x:cx-14,y:x>0?y0-x*k:y0,width:12,height:Math.abs(x)*k,fill:C.blue,rx:3}));f.svg.appendChild(s('rect',{x:cx+2,y:dq[i]>0?y0-dq[i]*k:y0,width:12,height:Math.abs(dq[i])*k,fill:C.amber,rx:3}));});
    f.svg.appendChild(svgText(20,16,'blue = original weight, amber = after '+bits+'-bit round trip',{fill:C.muted,'font-size':11}));
    f.svg.setAttribute('aria-label',`${bits}-bit quantization, RMS error ${err.toFixed(4)}`);
    f.live.textContent=`${P.v}B parameters at ${bits} bits ≈ ${(mem/1e9).toFixed(1)} GB of weights (FP16 would be ${(P.v*2).toFixed(0)} GB). Sample RMS rounding error: ${err.toFixed(4)}. Real methods (GPTQ, AWQ) use per-group scales to keep error lower.`;};
  [P.inp,b.inp].forEach(x=>x.addEventListener('input',draw));draw();};

W.rag=el=>{const f=frame(el,'RAG retrieval (lexical scoring demo)','Type a question. Each document is scored with TF-IDF cosine similarity, the top-k go into the prompt. Real systems add embeddings, hybrid search and reranking, but the shape is the same.');
  const docs=[['Refund policy','Customers may request a refund within 30 days of purchase with a receipt.'],['Shipping times','Standard shipping takes 3 to 5 business days; express takes 1 to 2 days.'],['Warranty','Electronics carry a one year warranty covering manufacturing defects.'],['Returns','Items can be returned within 30 days if unused and in original packaging.'],['Account security','Enable two factor authentication to protect your account from takeover.'],['Gift cards','Gift cards never expire and cannot be exchanged for cash.'],['Price match','We match competitor prices within 14 days of purchase.'],['Damaged items','Report damaged deliveries within 48 hours with photos for a replacement.']];
  const qid='w'+(++uid);const q=h('input',{type:'text',id:qid,value:'how many days do I have for a refund?'});const k=slider('Top-k',1,5,1,3);
  f.ctl.append(h('div',{class:'w-ctl w-wide'},[h('label',{for:qid,text:'Question'}),q]),k.wrap);
  const tokz=t=>t.toLowerCase().match(/[a-z0-9]+/g)||[];const D=docs.map(d=>tokz(d[0]+' '+d[1]));const df={};D.forEach(t=>new Set(t).forEach(w=>df[w]=(df[w]||0)+1));
  const vec=t=>{const v={};t.forEach(w=>{v[w]=(v[w]||0)+1;});for(const w in v)v[w]*=Math.log((docs.length+1)/((df[w]||0)+1))+1;return v;};
  const cos=(a,b)=>{let d=0,na=0,nb=0;for(const w in a){na+=a[w]**2;if(b[w])d+=a[w]*b[w];}for(const w in b)nb+=b[w]**2;return na&&nb?d/Math.sqrt(na*nb):0;};
  const DV=D.map(vec);const draw=()=>{const qv=vec(tokz(q.value)),sc=DV.map((v,i)=>({i,s:cos(qv,v)})).sort((a,b)=>b.s-a.s);clear(f.svg);
    sc.forEach((r,j)=>{const y=8+j*26,top=j<k.v;f.svg.appendChild(s('rect',{x:150,y,width:Math.max(2,r.s*380),height:18,rx:4,fill:top?C.green:C.grid}));
      f.svg.appendChild(svgText(4,y+13,docs[r.i][0],{'font-size':11}));f.svg.appendChild(svgText(156+r.s*380,y+13,r.s.toFixed(2),{'font-size':10,fill:C.muted}));});
    f.svg.setAttribute('aria-label','Top document: '+docs[sc[0].i][0]);
    f.live.textContent=`Context sent to the model: ${sc.slice(0,k.v).map(r=>'“'+docs[r.i][1]+'”').join(' ')}`;};
  q.addEventListener('input',draw);k.inp.addEventListener('input',draw);draw();};

W.agentloop=el=>{const f=frame(el,'The agent loop, step by step','An agent repeats: the model decides, calls a tool, reads the result, and decides again, until it answers or hits a budget. Step through a scripted refund task and watch the context and cost grow.');
  const steps=[['user','Refund order #1042, it arrived broken.',60],['model','Decide: need order details → call get_order(1042)',80],['tool','get_order → {status: delivered, total: $84, days_since: 3}',120],['model','Decide: policy check → call check_policy("damaged", 3 days)',70],['tool','check_policy → eligible: replacement or refund within 30 days',90],['model','Decide: refunds cannot be undone → request human approval',60],['tool','approval → granted by agent j.diaz',40],['model','Call issue_refund(1042, $84, idempotency_key=run77-step8)',60],['tool','issue_refund → ok, refund_id R-5531',50],['model','Final answer: refund of $84 issued (R-5531).',50]];
  const mx=slider('Max steps budget',3,10,1,10);const nb=h('button',{type:'button',text:'Next step ▶'}),rb=h('button',{type:'button',text:'Reset'});f.ctl.append(mx.wrap,nb,rb);let i=0;
  const draw=()=>{clear(f.svg);let ctx=0;const shown=steps.slice(0,i);shown.forEach((st,j)=>{ctx+=st[2];});
    const col={user:C.amber,model:C.violet,tool:C.green};shown.slice(-6).forEach((st,j)=>{const y=6+j*32;f.svg.appendChild(s('rect',{x:6,y,width:410,height:26,rx:6,fill:col[st[0]],'fill-opacity':.15,stroke:col[st[0]]}));f.svg.appendChild(svgText(12,y+17,(st[0]+': '+st[1]).slice(0,64),{'font-size':11}));});
    const ctxTok=shown.reduce((a,st,j)=>a+st[2],0);let cum=0,run=0;shown.forEach(st=>{run+=st[2];if(st[0]==='model')cum+=run;});
    f.svg.appendChild(svgText(430,30,'context: '+ctxTok+' tok',{'font-size':11}));f.svg.appendChild(svgText(430,50,'tokens billed: '+cum,{'font-size':11}));
    f.svg.appendChild(s('rect',{x:430,y:60,width:110,height:12,rx:6,fill:C.grid}));f.svg.appendChild(s('rect',{x:430,y:60,width:110*Math.min(1,i/mx.v),height:12,rx:6,fill:i>=mx.v?C.rose:C.blue}));
    f.svg.appendChild(svgText(430,90,`step ${i}/${mx.v}`,{'font-size':11}));
    const last=shown[shown.length-1];
    f.live.textContent=i===0?'Press Next step.':(i>=mx.v&&i<steps.length?`Budget hit at step ${i}: the loop stops and escalates instead of continuing.`:last[0]+': '+last[1])+` Each model call re-reads the whole context, so billed input tokens grow faster than the context itself.`;
    nb.disabled=i>=steps.length||i>=mx.v;};
  nb.addEventListener('click',()=>{i++;draw();});rb.addEventListener('click',()=>{i=0;draw();});mx.inp.addEventListener('input',()=>{i=Math.min(i,mx.v);draw();});draw();};

W.eval=el=>{const f=frame(el,'Eval math: pass@k, pass^k and sample size','With independent trials and per-trial success p: pass@k = 1 − (1 − p)^k (at least one success), pass^k = p^k (all succeed). The standard error of a measured pass rate on n cases is √(p(1 − p)/n).');
  const p=slider('Per-trial success p',0.05,1,0.01,0.8,v=>pct(v)),k=slider('Trials k',1,10,1,4),n=slider('Golden-set size n',25,2000,25,200);f.ctl.append(p.wrap,k.wrap,n.wrap);
  const draw=()=>{const a=1-(1-p.v)**k.v,b=p.v**k.v,se=Math.sqrt(p.v*(1-p.v)/n.v);
    bars(f.svg,[{label:'p (1 trial)',v:p.v,txt:pct(p.v),c:C.blue},{label:'pass@'+k.v,v:a,txt:pct(a),c:C.green},{label:'pass^'+k.v,v:b,txt:pct(b),c:C.violet}],1);
    f.live.textContent=`pass@${k.v} = ${pct(a)}, pass^${k.v} = ${pct(b)}. On n=${n.v} cases, a measured ${pct(p.v)} has a 95% interval of about ±${pct(1.96*se)}, so smaller changes may be noise.`;};
  [p,k,n].forEach(x=>x.inp.addEventListener('input',draw));draw();};

W.routing=el=>{const f=frame(el,'Model routing: cost vs quality','Send easy requests to a small model and hard ones to a large model. Compare blended cost and accuracy with sending everything to the large model. Numbers are illustrative inputs you control.');
  const e=slider('Share of easy requests',0,1,0.05,0.7,pct),cs=numIn('Small model $ / 1k requests',0.5),cl=numIn('Large model $ / 1k requests',10),ae=slider('Small model accuracy on easy',0.5,1,0.01,0.95,pct),al=slider('Large model accuracy (any)',0.5,1,0.01,0.96,pct),r=slider('Router accuracy',0.5,1,0.01,0.9,pct);
  [e,cs,cl,ae,al,r].forEach(x=>f.ctl.append(x.wrap));
  const draw=()=>{const E=e.v,R=r.v,toSmall=E*R+(1-E)*(1-R);// misrouted hard requests go small
    const accSmallHard=0.5;// assumed: small model gets half of hard requests right
    const acc=E*R*ae.v+E*(1-R)*al.v+(1-E)*R*al.v+(1-E)*(1-R)*accSmallHard,cost=toSmall*cs.v+(1-toSmall)*cl.v;
    bars(f.svg,[{label:'Cost: all large',v:cl.v,txt:'$'+cl.v.toFixed(2),c:C.rose},{label:'Cost: routed',v:cost,txt:'$'+cost.toFixed(2),c:C.green},{label:'Acc: all large',v:al.v*Math.max(cl.v,cost),txt:pct(al.v),c:C.violet},{label:'Acc: routed',v:acc*Math.max(cl.v,cost),txt:pct(acc),c:C.blue}],Math.max(cl.v,cost));
    f.live.textContent=`Routing sends ${pct(toSmall)} of traffic to the small model: cost $${cost.toFixed(2)} vs $${cl.v.toFixed(2)} per 1k (${pct(1-cost/cl.v)} saved), accuracy ${pct(acc)} vs ${pct(al.v)}. Assumes the small model gets 50% of misrouted hard requests right.`;};
  [e,cs,cl,ae,al,r].forEach(x=>x.inp.addEventListener('input',draw));draw();};

W.budget=el=>{const f=frame(el,'Context budget planner','A context window is shared by the system prompt, tool definitions, history, retrieved chunks and the reserved output. Fill it and see what fits and what each call costs.');
  const win=numIn('Context window (tokens)',128000,1000),sys=slider('System prompt',0,8000,100,2000),tools=slider('Tool definitions',0,20000,100,4000),hist=slider('Conversation history',0,100000,500,20000),ch=slider('Retrieved chunks',0,50,1,10),cs=slider('Tokens per chunk',100,2000,50,500),out=slider('Reserved output',0,16000,250,4000),price=numIn('Input $ per 1M tokens',3);
  [win,sys,tools,hist,ch,cs,out,price].forEach(x=>f.ctl.append(x.wrap));
  const draw=()=>{const parts=[['system',sys.v,C.violet],['tools',tools.v,C.amber],['history',hist.v,C.blue],['retrieved',ch.v*cs.v,C.green],['output',out.v,C.rose]],tot=parts.reduce((a,p)=>a+p[1],0),W0=Math.max(win.v,tot);clear(f.svg);
    let x=20;parts.forEach(([n,v,c])=>{const w=520*v/W0;f.svg.appendChild(s('rect',{x,y:60,width:w,height:50,fill:c,'fill-opacity':.8}));if(w>44)f.svg.appendChild(svgText(x+4,90,n,{'font-size':11,fill:'#fff'}));x+=w;});
    const wx=20+520*win.v/W0;f.svg.appendChild(s('line',{x1:wx,y1:40,x2:wx,y2:130,stroke:C.ink,'stroke-dasharray':'4 3'}));f.svg.appendChild(svgText(Math.min(wx,470),34,'window limit',{'font-size':11}));
    const inp=tot-out.v,cost=inp*price.v/1e6;f.svg.setAttribute('aria-label',`Context uses ${tot} of ${win.v} tokens`);
    f.live.textContent=(tot>win.v?`Over budget by ${(tot-win.v).toLocaleString()} tokens: trim history or retrieve fewer chunks. `:`Uses ${pct(tot/win.v)} of the window. `)+`Input per call: ${inp.toLocaleString()} tokens ≈ $${cost.toFixed(4)}; 1,000 calls ≈ $${(cost*1000).toFixed(2)}.`;};
  [win,sys,tools,hist,ch,cs,out,price].forEach(x=>x.inp.addEventListener('input',draw));draw();};

const INFO={softmax:'Softmax & temperature',tokenizer:'Tokenization',attention:'Self-attention',kvcache:'KV cache memory',batching:'Static vs continuous batching',quant:'Quantization',rag:'RAG retrieval',agentloop:'Agent loop',eval:'Eval math (pass@k, pass^k)',routing:'Model routing',budget:'Context budget'};
window.AtlasWidgets={list:INFO,mount(el,id){if(W[id]){try{W[id](el);}catch(e){el.textContent='Interactive explainer failed to load.';console.warn(e);}}}};
})();
