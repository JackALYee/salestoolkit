'use strict';
(() => {
const $=id=>document.getElementById(id), personal=document.body.dataset.personal==='true';
const colors={chats:'#9cd9d0',website:'#e5c68e',information:'#aebcf3',internet:'#df9e83',core:'#e7eee5',concept:'#9caebc',source:'#cfb997',foundation:'#b5c3cd'};
const categoryColors={capability:'#9cd9d0',device:'#aebcf3',camera:'#adc3d4',platform:'#e5c68e',solution:'#df9e83',competitor:'#beadb9'};
const names={chats:'Conversations',website:'Websites',information:'Supplied knowledge',internet:'Internet research'};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const date=v=>v?new Date(v).toLocaleString(undefined,{timeZone:'Asia/Shanghai',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})+' CST':'—';
const dayKey=v=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(v);
const stateName={active:'Available to Jerry',pending:'Needs review',expired:'Expired',retired:'Removed',running:'Reviewing online',queued:'Queued online',complete:'Complete',failed:'Needs retry',budget_limit:'Waiting for daily allowance',reviewing:'Reviewing online',needs_review:'Needs more evidence'};
const safeURL=u=>{try{const p=new URL(u);return p.protocol==='https:'&&!p.username&&!p.password?p.href:null}catch{return null}};
let data=null,busy=false,view=personal?'learning':'ecosystem',channel='',selected=null,expanded=false,paused=matchMedia('(prefers-reduced-motion: reduce)').matches;
let nodes=[],edges=[],lookup=new Map(),positions=new Map(),filtered=[],zoom=1,pan={x:0,y:0},size={w:1,h:1},hover=null,drag=null,frame=0;
const canvas=$('network'),ctx=canvas.getContext('2d'),stage=$('stage');
function color(n){return n.type==='knowledge'?colors[n.card.primary_channel||n.card.channels[0]]||colors.concept:n.type==='concept'?categoryColors[n.category]||colors.concept:colors[n.channel||n.type]||colors.core}
function effectiveState(c){return c.status==='active'&&c.expires_at&&new Date(c.expires_at)<=new Date()?'expired':c.status}
async function request(path,options={}){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),25000);
 try{const r=await fetch(path,{credentials:'same-origin',...options,signal:controller.signal});const d=await r.json();if(!r.ok)throw Error(r.status===401?'Your session expired. Sign in again through Ask Jerry.':d.detail||'The request could not be completed.');return d}
 catch(e){if(e.name==='AbortError')throw Error('The request timed out. Your draft is kept; retrying it will not submit it twice.');throw e}finally{clearTimeout(timer)}
}
function message(text){$('notice').textContent=text;$('notice').hidden=!text}
function neighbours(id,two=false){const set=new Set([id]);for(const e of data.edges){if(e.source===id)set.add(e.target);if(e.target===id)set.add(e.source)}if(two){const initial=new Set([...set].filter(x=>!['jerry','foundation'].includes(x)&&!x.startsWith('channel:')));for(const e of data.edges){if(initial.has(e.source))set.add(e.target);if(initial.has(e.target))set.add(e.source)}}return set}
function build(){
 if(!data)return;lookup=new Map(data.nodes.map(n=>[n.id,n]));
 const q=$('search').value.toLocaleLowerCase().trim(),status=$('state').value;
 filtered=data.nodes.filter(n=>view==='ecosystem'?n.type==='concept':n.type==='knowledge').filter(n=>(!q||(n.label+' '+n.description+' '+(n.card?.sources||[]).map(s=>s.title+' '+s.url+' '+s.locator).join(' ')).toLocaleLowerCase().includes(q))&&(!n.card||(!channel||n.card.channels.includes(channel))&&(!status||effectiveState(n.card)===status)));
 let chosen=filtered.slice(0,160),support=[];
 if(selected&&lookup.has(selected)&&!['core','channel','foundation'].includes(lookup.get(selected).type)){
   const near=neighbours(selected,expanded);
   const context=data.nodes.filter(n=>near.has(n.id)&&!['core','channel','foundation'].includes(n.type));
   // A selected node always remains reachable; controls still determine the overview list.
   chosen=[lookup.get(selected),...context.filter(n=>n.id!==selected)].slice(0,120);
 }else if(view==='ecosystem')chosen=filtered;
 support=data.nodes.filter(n=>n.id==='jerry'||(view==='learning'?n.type==='channel':n.type==='foundation'));
 nodes=[...support,...chosen.filter(n=>!support.some(x=>x.id===n.id))];const ids=new Set(nodes.map(n=>n.id));edges=data.edges.filter(e=>ids.has(e.source)&&ids.has(e.target));
 layout();renderList();updateTabs();
 const kshown=nodes.filter(n=>n.type==='knowledge').length;
 $('coverage').textContent=view==='ecosystem'?`${nodes.filter(n=>n.type==='concept').length} product neurons · documented relationships`:`${kshown} knowledge neurons shown · ${filtered.length} match · ${data.loaded} of ${data.total} loaded`;
 $('stage-label').textContent=selected&&lookup.get(selected)?'Tracing '+lookup.get(selected).label:view==='ecosystem'?'Curated product relationships':'Four paths into Jerry’s knowledge';
 for(const b of document.querySelectorAll('[data-channel]')){b.classList.toggle('selected',channel===b.dataset.channel);b.setAttribute('aria-pressed',channel===b.dataset.channel?'true':'false');b.querySelector('b').textContent=data.nodes.filter(n=>n.card?.channels.includes(b.dataset.channel)).length}
 $('channels').hidden=view!=='learning';$('category-legend').hidden=view!=='ecosystem';$('state').hidden=view!=='learning';
 draw();
}
function hash(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return(h>>>0)/4294967296}
function layout(){
 positions=new Map();const w=size.w,h=size.h,cx=w/2,cy=h/2;
 positions.set('jerry',{x:cx,y:cy,r:36});
 if(view==='learning'){
  const centers={chats:{x:w*.27,y:h*.28},website:{x:w*.73,y:h*.28},information:{x:w*.27,y:h*.73},internet:{x:w*.73,y:h*.73}};
  Object.keys(centers).forEach(k=>positions.set('channel:'+k,{...centers[k],r:12}));
  const groups={chats:[],website:[],information:[],internet:[]};for(const n of nodes){if(n.card)groups[n.card.primary_channel||n.card.channels[0]||'chats'].push(n)}
  for(const [key,group] of Object.entries(groups)){group.forEach((n,i)=>{const a=i*2.399963+hash(key)*6.28,r=32+Math.sqrt(i+.7)*Math.min(12,w/70),center=centers[key];positions.set(n.id,{x:Math.max(25,Math.min(w-25,center.x+Math.cos(a)*r)),y:Math.max(46,Math.min(h-28,center.y+Math.sin(a)*r*.78)),r:effectiveState(n.card)==='active'?4.6:3.5})})}
 }else{
  positions.set('foundation',{x:cx,y:cy+68,r:8});
  const cats=Object.keys(categoryColors),rx=Math.min(w*.32,270),ry=Math.min(h*.32,150);
  for(const [ci,cat] of cats.entries()){const group=nodes.filter(n=>n.category===cat),angle=-Math.PI/2+ci*Math.PI/3,center={x:cx+Math.cos(angle)*rx,y:cy+Math.sin(angle)*ry};group.forEach((n,i)=>{const a=i*2.399963,r=18+Math.sqrt(i)*13;positions.set(n.id,{x:center.x+Math.cos(a)*r,y:center.y+Math.sin(a)*r*.7,r:5+Math.min(4,data.edges.filter(e=>e.source===n.id||e.target===n.id).length/6)})})}
 }
 const others=nodes.filter(n=>!positions.has(n.id));others.forEach((n,i)=>{const a=i*2.399963,r=95+Math.sqrt(i)*19;positions.set(n.id,{x:cx+Math.cos(a)*Math.min(r,w*.43),y:cy+Math.sin(a)*Math.min(r,h*.38),r:n.type==='source'?4:6})});
 // In trace mode bring the selected neuron to the center, with its evidence nearby.
 if(selected&&positions.has(selected)&&!selected.startsWith('channel:')&&selected!=='jerry'&&selected!=='foundation'){
  positions.set('jerry',{x:cx,y:cy+125,r:24});positions.set(selected,{x:cx,y:cy,r:13});
  const rest=nodes.filter(n=>n.id!==selected&&n.id!=='jerry');rest.forEach((n,i)=>{const a=-Math.PI/2+i*2*Math.PI/rest.length,ring=i%2?1:.77;positions.set(n.id,{x:cx+Math.cos(a)*Math.min(w*.37,270)*ring,y:cy+Math.sin(a)*h*.36*ring,r:n.type==='channel'?9:n.type==='source'?5:6})});
 }
}
function renderList(){const items=filtered.slice(0,500);$('list-summary').textContent=`Browse ${filtered.length} ${view==='learning'?'knowledge entries':'product concepts'} as a list${filtered.length>500?' (first 500; search to narrow)':''}`;$('node-list').innerHTML=items.length?items.map(n=>`<button data-node="${esc(n.id)}">${esc(n.label)}${n.card?' · '+esc(stateName[effectiveState(n.card)]):''}</button>`).join(''):'<p>No matching entries. Try another search or learning path.</p>'}
function updateTabs(){document.querySelectorAll('[data-view]').forEach(b=>{const yes=b.dataset.view===view;b.classList.toggle('selected',yes);b.setAttribute('aria-pressed',String(yes))});$('motion').textContent=paused?'Resume motion':'Pause motion';$('motion').setAttribute('aria-pressed',String(paused))}
function screen(p){return{x:(p.x-size.w/2)*zoom+size.w/2+pan.x,y:(p.y-size.h/2)*zoom+size.h/2+pan.y}}
function draw(t=0){
 const dpr=Math.min(window.devicePixelRatio||1,2);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,size.w,size.h);
 const core=screen(positions.get('jerry')||{x:size.w/2,y:size.h/2});
 const glow=ctx.createRadialGradient(core.x,core.y,10,core.x,core.y,Math.min(size.w,size.h)*.48);glow.addColorStop(0,'#28433b25');glow.addColorStop(1,'#0c131a00');ctx.fillStyle=glow;ctx.fillRect(0,0,size.w,size.h);
 for(let i=0;i<70;i++){ctx.fillStyle=i%3?'#57707e22':'#78919338';ctx.beginPath();ctx.arc(hash('x'+i)*size.w,hash('y'+i)*size.h,.6,0,Math.PI*2);ctx.fill()}
 const near=hover?neighbours(hover):null;
 for(const e of edges){const a=positions.get(e.source),b=positions.get(e.target);if(!a||!b)continue;const p=screen(a),q=screen(b),n=lookup.get(e.target),hot=hover&&(e.source===hover||e.target===hover);const hub=e.source==='jerry'||e.source==='foundation';ctx.strokeStyle=(hot?color(n):hub?'#76998b':color(n))+(hot?'bb':hub?'28':'40');ctx.lineWidth=hot?1.4:hub?.6:.8;ctx.beginPath();ctx.moveTo(p.x,p.y);const dx=q.x-p.x,dy=q.y-p.y,bend=(hash(e.source+e.target)-.5)*50;ctx.bezierCurveTo(p.x+dx*.35+dy*.12,p.y+dy*.35-dx*.12+bend,p.x+dx*.7-dy*.08,p.y+dy*.7+dx*.08,q.x,q.y);ctx.stroke()}
 for(const n of nodes){const p=screen(positions.get(n.id)),base=positions.get(n.id),r=base.r*Math.min(zoom,1.8),c=color(n),highlight=n.id===hover||n.id===selected;ctx.globalAlpha=near&&!near.has(n.id)?.22:1;
  if(n.type==='core'){
   const phase=paused?0:Math.sin(t/3500)*2;
   for(let ring=0;ring<4;ring++){ctx.strokeStyle=ring===0?'#cfdddacc':'#9cb4ab'+['40','40','25','13'][ring];ctx.lineWidth=ring===0?1.1:.6;ctx.beginPath();ctx.ellipse(p.x,p.y,r+ring*7+phase,(r+ring*7+phase)*.86,ring*.4,0,Math.PI*2);ctx.stroke()}
   const g=ctx.createRadialGradient(p.x-r*.3,p.y-r*.3,1,p.x,p.y,r);g.addColorStop(0,'#c8e1cf66');g.addColorStop(1,'#244c4044');ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,r*.83,0,Math.PI*2);ctx.fill();ctx.fillStyle='#edf2ec';ctx.textAlign='center';ctx.font='500 11px system-ui';ctx.fillText('JERRY',p.x,p.y+4);continue;
  }
  const halo=ctx.createRadialGradient(p.x,p.y,1,p.x,p.y,r*4);halo.addColorStop(0,c+'45');halo.addColorStop(1,c+'00');ctx.fillStyle=halo;ctx.beginPath();ctx.arc(p.x,p.y,r*4,0,Math.PI*2);ctx.fill();
  // Fine dendrites make each item a neuron; their size does not encode intelligence.
  ctx.strokeStyle=c+'63';ctx.lineWidth=.6;for(let k=0;k<5;k++){const a=k*Math.PI*.4+hash(n.id)*3,outer=r+(n.type==='channel'?10:5);ctx.beginPath();ctx.moveTo(p.x+Math.cos(a)*r*.6,p.y+Math.sin(a)*r*.6);ctx.lineTo(p.x+Math.cos(a)*outer,p.y+Math.sin(a)*outer);ctx.stroke()}
  ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);const inactive=n.card&&effectiveState(n.card)!=='active';ctx.fillStyle=inactive?'#15232b':c;ctx.fill();ctx.strokeStyle=inactive?'#d0b482':c;ctx.lineWidth=1;ctx.stroke();
  if(highlight){ctx.strokeStyle=c;ctx.lineWidth=.7;ctx.beginPath();ctx.arc(p.x,p.y,r+6,0,Math.PI*2);ctx.stroke()}
  const label=n.type==='channel'||(n.type==='concept'&&zoom>1.8)||n.type==='foundation'||highlight||selected;
  if(label){ctx.textAlign='center';ctx.font=(n.type==='channel'?'500 11px':'10px')+' system-ui';ctx.fillStyle=n.type==='channel'?'#e0e6e5':'#bdc9ce';let text=n.label;if(text.length>29)text=text.slice(0,27)+'…';ctx.fillText(text,p.x,p.y+r+16)}
 }
 ctx.globalAlpha=1;
}
function animate(t){draw(t);if(!paused&&!document.hidden)frame=requestAnimationFrame(animate);else frame=0}
function startMotion(){if(frame)cancelAnimationFrame(frame);frame=0;if(!paused&&!document.hidden)frame=requestAnimationFrame(animate);else draw()}
function resize(){const r=stage.getBoundingClientRect();size={w:r.width,h:r.height};const dpr=Math.min(devicePixelRatio||1,2);canvas.width=r.width*dpr;canvas.height=r.height*dpr;if(data)layout();draw()}
function selectNode(id){if(lookup.get(id)?.type==='knowledge')view='learning';selected=id;expanded=false;pan={x:0,y:0};zoom=1;build();inspect(id)}
function inspect(id){const n=lookup.get(id);if(!n)return;const card=n.card;let html='';
 if(card){const state=effectiveState(card);html=`<span class="tag ${esc(state)}">${esc(stateName[state])}</span><span class="tag">${esc(card.scope==='internal'?'Company knowledge':card.scope==='leadership'?'Leadership only':'Individual restriction')}</span><h3>${esc(n.label)}</h3><p>${esc(n.description)}</p><dl><dt>Evidence confidence</dt><dd>${Math.round(card.confidence*100)}%</dd><dt>Updated</dt><dd>${esc(date(card.updated_at))}</dd><dt>Expires</dt><dd>${esc(date(card.expires_at))}</dd><dt>Source questions</dt><dd>${card.question_ids.length}</dd><dt>Reviewer comments</dt><dd>${card.comment_count}</dd></dl><p class="subtle">${esc(card.reason)}</p><h4>Evidence trail</h4>`;
  html+=card.sources.length?card.sources.map(s=>{const u=safeURL(s.url);return `<${u?'a':'div'} class="source-link"${u?' href="'+esc(u)+'" target="_blank" rel="noopener noreferrer"':''}>${esc(s.title||s.locator||s.url||'Source')} ${u?'↗':''}<small>${esc(s.type==='supplied'?'Owner-supplied reference':s.type==='web'?'Cited internet evidence':'Curated reference')} ${esc(s.locator||'')}</small></${u?'a':'div'}>`}).join(''):'<p class="subtle">No independently supported evidence yet.</p>';
  if(personal)html+=`<p style="margin-top:20px"><a class="source-link" href="/learning?entry=${card.id}">Open entry &amp; review comments ↗</a></p>`;
 }else{html=`<span class="tag">${esc(n.type==='concept'?n.category:n.type==='source'?'Evidence source':n.type==='channel'?'Learning route':'Knowledge network')}</span><h3>${esc(n.label)}</h3><p>${esc(n.description)}</p>`;if(n.source&&safeURL(n.source.url))html+=`<a class="source-link" href="${esc(safeURL(n.source.url))}" target="_blank" rel="noopener noreferrer">Open original source ↗</a>`;if(n.type==='core')html+='<p class="subtle">Knowledge becomes available after evidence review. Each neuron retains its visibility, source, and expiry. Connections express provenance and documented relationships.</p>';}
 const connected=data.edges.filter(e=>e.source===id||e.target===id).map(e=>({id:e.source===id?e.target:e.source,kind:e.kind})).filter(e=>lookup.has(e.id)&&e.id!=='jerry');
 html+='<h4>Connected neurons</h4><div class="related">'+connected.slice(0,25).map(e=>`<button data-node="${esc(e.id)}" title="${esc(e.kind)}">${esc(lookup.get(e.id).label)}</button>`).join('')+'</div>';
 if(!['core','channel','foundation'].includes(n.type))html+=`<button id="expand-trace" style="margin-top:16px;font-size:11px">${expanded?'Show direct connections':'Trace one step further'}</button>`;
 $('detail').innerHTML=html;if($('expand-trace'))$('expand-trace').onclick=()=>{expanded=!expanded;build();inspect(id)};
}
function paintPersonal(){
 $('metric-active').textContent=data.available;$('metric-pending').textContent=data.counts.pending||0;$('metric-reviewed').textContent=data.reviewed_questions;$('metric-waiting').textContent=`${Math.max(0,data.questions-data.reviewed_questions)} questions await review · all users`;
 const s=data.settings.scheduler||{},running=data.runs.find(r=>r.status==='running');$('signal').classList.toggle('ready',!!s.installed);$('cloud-state').textContent=running?'Jerry is reviewing online':s.installed?'Online learning is scheduled':'Online schedule needs attention';$('cloud-detail').textContent=s.installed?'Daily at 02:00 China time · checked '+new Date().toLocaleTimeString():s.error||'Waiting for the hosted schedule to initialize.';
 const points=new Map(data.timeline.map(d=>[d.day,d])),days=[];for(let i=29;i>=0;i--){const day=dayKey(new Date(Date.now()-i*86400000));days.push(points.get(day)||{day,learned:0,proposed:0,revised:0})}const max=Math.max(1,...days.flatMap(d=>[d.learned,d.proposed]));$('timeline').innerHTML=days.map((d,i)=>`<div class="day" tabindex="0" title="${esc(d.day)}: ${d.learned} learned or revised; ${d.proposed} proposed; ${d.revised} feedback revisions" aria-label="${esc(d.day)}: ${d.learned} learned or revised and ${d.proposed} proposed"><span class="bar" style="height:${d.learned/max*100}%"></span><span class="bar proposed" style="height:${d.proposed/max*100}%"></span>${[0,7,14,21,29].includes(i)?'<small>'+esc(d.day.slice(5))+'</small>':''}</div>`).join('');
 const actions={active:'Added to Jerry’s knowledge',pending:'Proposed for review','feedback-distilled':'Distilled reviewer feedback','comment-added':'Reviewer added guidance',retired:'Removed from use','restrict-commercial':'Restricted commercial information'};
 $('activity').innerHTML=data.events.slice(0,6).map(e=>`<div class="activity-row"><span class="event-mark ${e.action==='pending'?'pending':''}"></span><div><button data-node="k:${e.knowledge_id}">${esc(e.title)}</button><small>${esc(actions[e.action]||e.action)} · ${esc(date(e.created_at))}</small></div></div>`).join('')||'<p class="subtle">The learning history will appear after the first online review.</p>';
 $('runs').innerHTML=data.runs.map(r=>`<tr><td>${esc({daily:'Daily conversations',feedback:'Review comments',sources:'Submitted sources',backfill:'Earlier conversations'}[r.kind]||r.kind)}</td><td>${esc(stateName[r.status]||r.status)}${r.error?'<small>'+esc(r.error)+'</small>':''}</td><td>${r.reviewed}</td><td>${r.accepted}</td><td>${r.pending}</td><td>${esc(date(r.updated_at))}</td></tr>`).join('');
 $('queue-count').textContent='('+data.inputs.length+(data.inputs.length===100?' most recent':'')+')';$('queue').innerHTML=data.inputs.map(i=>`<article><b>${esc(i.title)}</b><small>${esc(names[i.kind]||i.kind)} · ${esc(i.scope==='internal'?'Company knowledge':'Leadership only')} · ${esc(date(i.created_at))}</small><p>${esc(stateName[i.processed_at?i.state:i.run_status]||stateName[i.state]||i.state)}</p><small>${esc(i.result||(i.state==='reviewing'&&i.run_status==='running'?'AI is checking evidence and distilling knowledge online.':'Waiting for a hosted review; the daily allowance is shared with conversations and feedback.'))}</small>${data.nodes.filter(n=>n.card?.input_ids.includes(i.id)).map(n=>`<button class="source-open" data-node="${esc(n.id)}">${esc(n.label)} ↗</button>`).join('')}</article>`).join('')||'<p class="subtle">No sources submitted here yet. Existing chat-derived and curated knowledge is already represented in the network.</p>';
}
async function load(){if(busy)return;busy=true;$('refresh').disabled=true;try{data=await request(personal?'/api/neural':'/api/neural/network');message(data.degraded?data.message:'');if(personal)paintPersonal();build();if(selected&&lookup.has(selected))inspect(selected);startMotion()}catch(e){message(e.message+(data?' Showing the last successfully loaded snapshot.':''));$('cloud-state').textContent='Connection needs attention';$('cloud-detail').textContent='Use refresh to retry.';$('signal').classList.remove('ready')}finally{busy=false;$('refresh').disabled=false}}
function hit(e){const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;return [...nodes].reverse().find(n=>{const p=screen(positions.get(n.id));return Math.hypot(p.x-x,p.y-y)<Math.max(10,positions.get(n.id).r*zoom+4)})}
canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,px:pan.x,py:pan.y,moved:false};canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener('pointermove',e=>{if(drag){const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.hypot(dx,dy)>4)drag.moved=true;pan={x:drag.px+dx,y:drag.py+dy};draw();return}const n=hit(e);hover=n?.id||null;canvas.style.cursor=n?'pointer':'grab';$('tooltip').hidden=!n;if(n){const r=stage.getBoundingClientRect();$('tooltip').textContent=n.label;$('tooltip').style.left=Math.min(size.w-240,Math.max(10,e.clientX-r.left+12))+'px';$('tooltip').style.top=Math.min(size.h-45,e.clientY-r.top+16)+'px'}draw()});
canvas.addEventListener('pointerup',e=>{const moved=drag?.moved;drag=null;if(!moved){const n=hit(e);if(n){if(n.type==='channel'){channel=channel===n.channel?'':n.channel;selected=null;build();inspect(n.id)}else selectNode(n.id)}}});canvas.addEventListener('pointercancel',()=>{drag=null});canvas.addEventListener('pointerleave',()=>{hover=null;$('tooltip').hidden=true;draw()});
canvas.addEventListener('wheel',e=>{if(!e.ctrlKey&&!e.metaKey)return;e.preventDefault();zoom=Math.max(.5,Math.min(3,zoom*(e.deltaY>0?.9:1.1)));draw()},{passive:false});
$('zoom-in').onclick=()=>{zoom=Math.min(3,zoom*1.2);draw()};$('zoom-out').onclick=()=>{zoom=Math.max(.5,zoom/1.2);draw()};$('fit').onclick=()=>{zoom=1;pan={x:0,y:0};selected=null;expanded=false;channel='';$('search').value='';$('state').value='';build();inspect('jerry')};$('motion').onclick=()=>{paused=!paused;updateTabs();startMotion()};$('refresh').onclick=load;
for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>{view=b.dataset.view;selected=null;channel='';$('search').value='';$('state').value='';zoom=1;pan={x:0,y:0};build();inspect(view==='learning'?'jerry':'foundation')};
for(const b of document.querySelectorAll('[data-channel]'))b.onclick=()=>{channel=channel===b.dataset.channel?'':b.dataset.channel;selected=null;build();inspect(channel?'channel:'+channel:'jerry')};
$('search').oninput=$('state').onchange=()=>{selected=null;build()};
document.addEventListener('click',e=>{const b=e.target.closest('[data-node]');if(b){if(!lookup.has(b.dataset.node)){message('This older entry is outside the latest 2,000-entry graph. Open Review knowledge to inspect the reservoir.');return}selectNode(b.dataset.node)}});
if(!personal){$('page-name').textContent='NEURAL NETWORK';$('heading').textContent='A connected view of Jerry’s knowledge.';$('eyebrow').textContent='PRODUCTS · CAPABILITIES · EVIDENCE';$('state').querySelectorAll('option').forEach(o=>{if(o.value&&o.value!=='active')o.remove()})}
$('category-legend').innerHTML=Object.entries(categoryColors).map(([cat,c])=>`<span><i style="background:${c}"></i>${esc({capability:'Capabilities',device:'Devices',camera:'Cameras & sensors',platform:'Cloud platforms',solution:'Solutions',competitor:'Competitors'}[cat])}</span>`).join('');
let submitID=null;
$('feed-form').addEventListener('input',()=>{submitID=null});
$('feed-kind').onchange=()=>{submitID=null;const kind=$('feed-kind').value,isInfo=kind==='information';$('url-field').hidden=kind!=='website';$('feed-url').required=kind==='website';$('scope-field').hidden=!isInfo;$('feed-content').required=isInfo;$('feed-content').minLength=isInfo?30:0;$('content-label').textContent=isInfo?'Source information':'Research focus (optional)';$('feed-help').textContent=isInfo?'Saved online. Jerry distills the supplied text and checks each claim. Supplied-only references are labelled; confidential information stays restricted.':'Public topics only. Jerry uses hosted web search and cited evidence; it does not crawl an entire site. Unavailable pages or unsupported claims remain visible for follow-up.'};
$('feed-form').onsubmit=async e=>{e.preventDefault();submitID=submitID||crypto.randomUUID();const payload={request_id:submitID,kind:$('feed-kind').value,title:$('feed-title').value,content:$('feed-content').value,url:$('feed-url').value,scope:$('feed-kind').value==='information'?$('feed-scope').value:'internal'};const controls=[...e.target.querySelectorAll('input,select,textarea,button')];controls.forEach(c=>c.disabled=true);$('feed-message').textContent='Saving your source online…';try{const result=await request('/api/neural/inputs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});$('feed-message').textContent=`Source #${result.id} saved for online review. You can close this page; its progress appears below.`;$('feed-title').value='';$('feed-content').value='';$('feed-url').value='';submitID=null;document.querySelector('.queue').open=true;await load()}catch(err){$('feed-message').textContent=err.message}finally{controls.forEach(c=>c.disabled=false)}};
new ResizeObserver(resize).observe(stage);document.addEventListener('visibilitychange',()=>{startMotion();if(!document.hidden)load()});setInterval(()=>{if(personal&&!document.hidden)load()},60000);
resize();load().then(()=>{const focus=new URLSearchParams(location.search).get('focus');if(focus&&lookup.has('t:'+focus)){view='ecosystem';selectNode('t:'+focus)}});
})();
