"""Streamax ecosystem topology — single source of truth.

Curated product/relationship graph distilled from the Jerry knowledge base.
Used in two places:
  - streamaxpedia_app.py imports TOPOLOGY / topology_json for the in-page
    "Ecosystem map" modal (D3 rendered inside the toolkit iframe).
  - jerry_gpt.py imports ecosystem_map_html() to pop the same interactive map
    inside a Streamlit dialog when Jerry suggests it.

cat ∈ capability | device | camera | platform | solution | competitor
"""
from __future__ import annotations

import json

_TOPO_NODES = [
    # Capabilities
    ("ADAS", "capability", "Advanced Driver Assistance — forward-collision, lane-departure, headway and pedestrian warnings."),
    ("DMS", "capability", "Driver Monitoring — fatigue, distraction, phone, smoking, seatbelt via in-cab face-tracing AI."),
    ("BSD", "capability", "Blind Spot Detection — warns of pedestrians/cyclists in the vehicle's blind zones; predicts trajectory."),
    ("AVM", "capability", "Around-View Monitor — stitched seamless 360° bird's-eye view of the vehicle."),
    ("DSC", "capability", "Driver Safety Camera — entry-level driver-facing safety, below a full DMS."),
    ("Child Check", "capability", "Anti-left-behind — guarantees no child is left on a school bus (button + AI camera + motion sensor)."),
    ("APC", "capability", "Automatic Passenger Counting — boarding/alighting counts plus origin-destination analysis."),
    ("Stop-Arm Capture", "capability", "Captures vehicles illegally passing a stopped school bus with court-grade evidence."),
    ("ANPR", "capability", "Automatic Number Plate Recognition — reads license plates for evidence/enforcement."),
    ("V2V", "capability", "Vehicle-to-vehicle warning beyond line of sight, independent of network infrastructure."),
    ("Blacklight", "capability", "Full-colour night vision in near-darkness (down to ~0.5 / 0.02 lux)."),
    ("CAN / OBD", "capability", "Reads the vehicle bus (fuel, RPM, DTCs) — the $20 inherent-CAN license on the AD Plus 2.0."),
    ("eSIM", "capability", "Built-in connectivity (eSIM / eUICC) — OTA carrier provisioning, lower TCO, higher uptime."),
    # Platforms / cloud
    ("SafeGPT", "platform", "Cloud behavioural-AI engine — prioritises risk, profiles & coaches drivers, real-time accident response."),
    ("FT Cloud", "platform", "Fleet management platform (trucking) — devices, video, telematics, CAN, alerts."),
    ("SBS Cloud", "platform", "School Bus Solution cloud — attendance, child-check, stop-arm evidence."),
    ("PT Cloud", "platform", "Public Transport platform — safety, passenger-flow analytics, operations."),
    ("MineSync-Cloud", "platform", "Mining production + transportation safety platform (big-data + video AI)."),
    # Devices / MDVRs
    ("AD Plus 2.0", "device", "Flagship 3-channel AI dashcam/MDVR — hosts ADAS + DMS, inherent CAN."),
    ("C6 Lite 2.0", "device", "Cost-effective 2-channel AI dashcam — ADAS + DSC."),
    ("M1N 2.0", "device", "Entry MDVR — child check + attendance + surveillance (school bus / mining basic)."),
    ("X3N", "device", "MDVR for 2–4 lane stop-arm capture and standard buses."),
    ("X5N Pro", "device", "MDVR for 5–8 lane stop-arm capture / regional regulatory needs."),
    ("IBCU", "device", "Intelligent Bus Central Unit (A16Max) — all-in-one flagship, up to 24 HD ch, 6 TOPS."),
    ("M10", "device", "Mining MDVR (Advanced tier)."),
    ("M10 PRO", "device", "Mining MDVR flagship (+ thermal cam, fuel management)."),
    ("DC MAX", "device", "Next-gen AI dashcam — dual 2K lenses, onboard large AI model, dual tamper-proof storage."),
    ("GT1", "device", "Independent telematics gateway pairing with DC MAX."),
    ("FMS Tracker", "device", "Compact dead-reckoning asset tracker — positioning without GPS."),
    # Cameras / sensors
    ("C29N", "camera", "DMS driver-monitoring camera with face-tracing IR."),
    ("CA20S", "camera", "Single-lens ADAS camera."),
    ("C20D", "camera", "Dual-lens ADAS camera (adds near-pedestrian + close-range)."),
    ("CA20D", "camera", "Triple-lens ADAS camera (adds ANPR)."),
    ("C46", "camera", "Top-down BSD camera (16 m both sides)."),
    ("C53", "camera", "Flagship long-range black-light BSD (50 m lateral)."),
    ("CA24S", "camera", "Rear-to-front BSD camera for core blind-spot zones."),
    ("AI-AVM", "camera", "360° around-view monitor with transparent-vehicle effect."),
    ("CMS20", "camera", "Digital rear-view mirror (Blacklight 1.8T)."),
    ("C34", "camera", "AI child-check camera (92% accuracy)."),
    ("DP7S", "camera", "Motion sensor for child check (99.9% accuracy)."),
    ("P3", "camera", "Automatic passenger counter (99%)."),
    ("P3D", "camera", "Passenger counter + origin-destination (85%)."),
    ("Palm Vein Reader", "camera", "Palm-vein student attendance — forget/lose/copy-proof."),
    ("C28", "camera", "Stop-arm AI detection camera."),
    ("C27", "camera", "Stop-arm license-plate camera."),
    ("B2", "camera", "Stop-arm audio-visual alarm."),
    ("Thermal Smart CAM", "camera", "Thermal imaging camera (mining loading hazards)."),
    ("mmWave Radar", "camera", "Millimeter-wave radar — dust-penetrating, mining BSD / fusion."),
    # Solutions / verticals
    ("Fleet / Trucking", "solution", "Core video-telematics for commercial trucking fleets and TSP partners."),
    ("School Bus", "solution", "Known · protected · never left behind — attendance, stop-arm, child check."),
    ("Public Transport", "solution", "One platform, four jobs — driving safety, operations, passenger service, recording."),
    ("Mining", "solution", "Safety + intelligent dispatch for open-pit & underground mining fleets."),
    ("Cargo Security", "solution", "Trailer / cargo theft prevention with black-light in-cargo cameras."),
    # Competitors
    ("Samsara", "competitor", "US fleet-telematics incumbent — subscription dashcam + platform."),
    ("Motive", "competitor", "US fleet safety/ELD platform; missing fatigue/FCW/PCW today."),
    ("Lytx", "competitor", "Video-based driver-risk / DMS vendor."),
    ("Netradyne", "competitor", "AI dashcam / driver-behaviour vendor (Driveri)."),
    ("Geotab", "competitor", "Telematics / OBD data platform."),
    ("MiTac", "competitor", "OEM AI camera competitor."),
    ("Hikvision", "competitor", "Surveillance / camera vendor."),
]

_TOPO_LINKS = [
    ("AD Plus 2.0", "ADAS"), ("AD Plus 2.0", "DMS"), ("AD Plus 2.0", "DSC"),
    ("AD Plus 2.0", "CAN / OBD"), ("AD Plus 2.0", "SafeGPT"),
    ("C6 Lite 2.0", "ADAS"), ("C6 Lite 2.0", "DSC"),
    ("DC MAX", "ADAS"), ("DC MAX", "DMS"), ("DC MAX", "DSC"), ("DC MAX", "SafeGPT"),
    ("GT1", "FT Cloud"), ("GT1", "eSIM"),
    ("FMS Tracker", "FT Cloud"), ("FMS Tracker", "eSIM"),
    ("IBCU", "ADAS"), ("IBCU", "DMS"), ("IBCU", "BSD"), ("IBCU", "AVM"),
    ("IBCU", "APC"), ("IBCU", "SafeGPT"),
    ("M10", "DMS"), ("M10", "BSD"), ("M10", "ADAS"),
    ("M10 PRO", "DMS"), ("M10 PRO", "BSD"), ("M10 PRO", "ADAS"), ("M10 PRO", "Thermal Smart CAM"),
    ("M1N 2.0", "Child Check"),
    ("X3N", "Stop-Arm Capture"), ("X3N", "Child Check"),
    ("X5N Pro", "Stop-Arm Capture"), ("X5N Pro", "BSD"),
    ("C29N", "DMS"), ("CA20S", "ADAS"), ("C20D", "ADAS"),
    ("CA20D", "ADAS"), ("CA20D", "ANPR"),
    ("C46", "BSD"), ("C53", "BSD"), ("C53", "Blacklight"), ("CA24S", "BSD"),
    ("AI-AVM", "AVM"), ("CMS20", "BSD"), ("CMS20", "Blacklight"),
    ("C34", "Child Check"), ("DP7S", "Child Check"),
    ("P3", "APC"), ("P3D", "APC"),
    ("C28", "Stop-Arm Capture"), ("C27", "Stop-Arm Capture"), ("C27", "ANPR"),
    ("B2", "Stop-Arm Capture"),
    ("Thermal Smart CAM", "Mining"), ("mmWave Radar", "BSD"), ("mmWave Radar", "Mining"),
    ("SafeGPT", "ADAS"), ("SafeGPT", "DMS"), ("SafeGPT", "BSD"),
    ("SafeGPT", "FT Cloud"), ("SafeGPT", "SBS Cloud"), ("SafeGPT", "PT Cloud"),
    ("SafeGPT", "MineSync-Cloud"),
    ("FT Cloud", "Fleet / Trucking"), ("SBS Cloud", "School Bus"),
    ("PT Cloud", "Public Transport"), ("MineSync-Cloud", "Mining"),
    ("eSIM", "FT Cloud"), ("CAN / OBD", "FT Cloud"),
    ("Fleet / Trucking", "AD Plus 2.0"), ("Fleet / Trucking", "C6 Lite 2.0"),
    ("Fleet / Trucking", "DC MAX"), ("Fleet / Trucking", "GT1"), ("Fleet / Trucking", "FMS Tracker"),
    ("Fleet / Trucking", "ADAS"), ("Fleet / Trucking", "DMS"), ("Fleet / Trucking", "DSC"),
    ("School Bus", "M1N 2.0"), ("School Bus", "X3N"), ("School Bus", "X5N Pro"),
    ("School Bus", "IBCU"), ("School Bus", "Palm Vein Reader"), ("School Bus", "C34"),
    ("School Bus", "DP7S"), ("School Bus", "C28"), ("School Bus", "C27"), ("School Bus", "B2"),
    ("School Bus", "Child Check"), ("School Bus", "Stop-Arm Capture"),
    ("Public Transport", "IBCU"), ("Public Transport", "C29N"), ("Public Transport", "CA20D"),
    ("Public Transport", "C53"), ("Public Transport", "C46"), ("Public Transport", "AI-AVM"),
    ("Public Transport", "CMS20"), ("Public Transport", "P3"), ("Public Transport", "P3D"),
    ("Public Transport", "APC"), ("Public Transport", "BSD"), ("Public Transport", "AVM"),
    ("Mining", "M10"), ("Mining", "M10 PRO"), ("Mining", "V2V"), ("Mining", "DMS"), ("Mining", "BSD"),
    ("Cargo Security", "Blacklight"), ("Cargo Security", "FT Cloud"), ("Cargo Security", "Fleet / Trucking"),
    ("Samsara", "Fleet / Trucking"), ("Samsara", "ADAS"), ("Samsara", "DMS"),
    ("Motive", "Fleet / Trucking"), ("Motive", "ADAS"), ("Motive", "DMS"),
    ("Lytx", "DMS"), ("Lytx", "ADAS"),
    ("Netradyne", "DMS"), ("Netradyne", "ADAS"),
    ("Geotab", "Fleet / Trucking"), ("Geotab", "CAN / OBD"),
    ("MiTac", "ADAS"), ("MiTac", "DMS"),
    ("Hikvision", "BSD"), ("Hikvision", "Public Transport"),
]

TOPOLOGY = {
    "nodes": [{"id": n, "cat": c, "desc": d} for (n, c, d) in _TOPO_NODES],
    "links": [{"source": a, "target": b} for (a, b) in _TOPO_LINKS],
}
topology_json = json.dumps(TOPOLOGY)


# Standalone interactive map (D3) for embedding via st.components.v1.html —
# self-contained: own dark theme, D3 from cdnjs, legend/zoom/drag/hover/click.
_MAP_TEMPLATE = r"""
<div id="wrap">
  <div id="hd">
    <div>
      <div id="ttl">Streamax Ecosystem Map</div>
      <div id="sub">__SUB__</div>
    </div>
    <div id="tools">
      <input id="q" placeholder="Find a term…" autocomplete="off">
      <button id="fit">Fit</button>
    </div>
  </div>
  <div id="legend"></div>
  <div id="vp">
    <svg id="svg"></svg>
    <div id="tip"></div>
    <div id="detail"></div>
  </div>
</div>
<style>
  html,body{margin:0;height:100%;background:#0b0d12;}
  #wrap{height:100%;display:flex;flex-direction:column;font-family:Inter,system-ui,sans-serif;color:#E6EAF0;padding:6px 4px;box-sizing:border-box;}
  #hd{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;padding:0 4px;}
  #ttl{font-size:1.05rem;font-weight:700;}
  #sub{font-size:0.72rem;color:#A0AEC0;margin-top:3px;}
  #tools{display:flex;gap:8px;align-items:center;}
  #q{background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.14);border-radius:8px;color:#fff;padding:6px 11px;font-size:.82rem;outline:none;width:150px;}
  #q:focus{border-color:#2AF598;}
  #fit{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);color:#A0AEC0;border-radius:8px;padding:6px 12px;font-size:.78rem;font-weight:600;cursor:pointer;}
  #fit:hover{border-color:#2AF598;color:#2AF598;}
  #legend{display:flex;flex-wrap:wrap;gap:6px 12px;margin:8px 4px 4px;}
  .lg{display:inline-flex;align-items:center;gap:6px;font-size:.72rem;color:#A0AEC0;cursor:pointer;padding:2px 6px;border-radius:6px;}
  .lg:hover{background:rgba(255,255,255,.05);color:#fff;}
  .lg.off{opacity:.35;text-decoration:line-through;}
  .dot{width:10px;height:10px;border-radius:50%;}
  #vp{flex:1;position:relative;overflow:hidden;background:rgba(0,0,0,.25);border:1px solid rgba(255,255,255,.06);border-radius:10px;margin:6px 4px 4px;cursor:grab;}
  #vp:active{cursor:grabbing;}
  #svg{width:100%;height:100%;display:block;}
  #svg text{pointer-events:none;user-select:none;}
  .nd{cursor:pointer;}
  #tip{position:absolute;pointer-events:none;background:rgba(5,8,16,.96);border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:8px 11px;font-size:.78rem;max-width:260px;line-height:1.45;opacity:0;transition:opacity .12s;box-shadow:0 8px 24px rgba(0,0,0,.5);z-index:5;}
  #tip.show{opacity:1;}
  #tip .c{font-size:.6rem;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:3px;}
  #detail{position:absolute;top:12px;left:12px;width:280px;max-width:62%;background:rgba(5,8,16,.97);border:1px solid rgba(255,255,255,.12);border-left:4px solid #2AF598;border-radius:10px;padding:14px 16px;box-shadow:0 12px 32px rgba(0,0,0,.6);display:none;z-index:6;}
  #detail.show{display:block;}
  #detail .c{font-size:.6rem;text-transform:uppercase;letter-spacing:1.2px;font-weight:700;margin-bottom:5px;}
  #detail .t{font-size:1.05rem;font-weight:700;margin-bottom:6px;}
  #detail .d{font-size:.86rem;color:#A0AEC0;line-height:1.5;}
  #detail .cn{font-size:.76rem;color:#A0AEC0;margin-top:9px;}
  #detail .cn b{color:#fff;}
  #detail .x{position:absolute;top:6px;right:9px;background:none;border:none;color:#A0AEC0;cursor:pointer;font-size:1.1rem;line-height:1;}
  #detail .x:hover{color:#fff;}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
(function(){
  const TOPO = __TOPO_JSON__;
  const FOCUS = "__FOCUS__";
  const CAT = {capability:{label:'Capability',color:'#2AF598'},device:{label:'Device / MDVR',color:'#009EFD'},camera:{label:'Camera / Sensor',color:'#7F77DD'},platform:{label:'Platform / Cloud',color:'#1D9E75'},solution:{label:'Solution',color:'#EF9F27'},competitor:{label:'Competitor',color:'#E24B4A'}};
  let ST=null;
  function nbrs(id,links){const s=new Set();links.forEach(l=>{const a=(l.source.id||l.source),b=(l.target.id||l.target);if(a===id)s.add(b);else if(b===id)s.add(a);});return s;}
  function run(){
    if(typeof d3==='undefined'){return;}
    const vp=document.getElementById('vp'),svgEl=document.getElementById('svg');
    const W=vp.clientWidth||820,H=vp.clientHeight||420;
    const nodes=TOPO.nodes.map(n=>Object.assign({},n));
    const links=TOPO.links.map(l=>Object.assign({},l));
    const svg=d3.select(svgEl);svg.selectAll('*').remove();svg.attr('viewBox','0 0 '+W+' '+H);
    const root=svg.append('g');
    const zoom=d3.zoom().scaleExtent([0.3,3]).on('zoom',e=>root.attr('transform',e.transform));
    svg.call(zoom).on('dblclick.zoom',null);
    const deg={};nodes.forEach(n=>deg[n.id]=0);links.forEach(l=>{deg[l.source]=(deg[l.source]||0)+1;deg[l.target]=(deg[l.target]||0)+1;});
    const link=root.append('g').selectAll('line').data(links).join('line').attr('class','lk').attr('stroke','rgba(255,255,255,0.13)').attr('stroke-width',1.2);
    const node=root.append('g').selectAll('g').data(nodes).join('g').attr('class','nd');
    node.append('circle').attr('r',d=>7+Math.min(10,deg[d.id]||0)).attr('fill',d=>(CAT[d.cat]||{}).color||'#888').attr('stroke','#050810').attr('stroke-width',1.5);
    node.append('text').text(d=>d.id).attr('x',d=>11+Math.min(10,deg[d.id]||0)).attr('y',4).attr('fill','#E6EAF0').attr('font-size','10px').attr('font-weight','500');
    const sim=d3.forceSimulation(nodes)
      .force('link',d3.forceLink(links).id(d=>d.id).distance(72).strength(0.5))
      .force('charge',d3.forceManyBody().strength(-280))
      .force('center',d3.forceCenter(W/2,H/2))
      .force('collide',d3.forceCollide().radius(d=>24+Math.min(10,deg[d.id]||0)))
      .on('tick',()=>{link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);node.attr('transform',d=>'translate('+d.x+','+d.y+')');});
    ST={svg,zoom,nodes,links,deg,hidden:new Set(),W,H};
    node.call(d3.drag()
      .on('start',(e,d)=>{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;})
      .on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y;})
      .on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));
    const tip=document.getElementById('tip');
    node.on('mouseenter',(e,d)=>{
      const nb=nbrs(d.id,links);nb.add(d.id);
      node.style('opacity',n=>nb.has(n.id)?1:0.12);
      link.style('stroke',l=>(l.source.id===d.id||l.target.id===d.id)?((CAT[d.cat]||{}).color||'#fff'):'rgba(255,255,255,0.04)').style('stroke-width',l=>(l.source.id===d.id||l.target.id===d.id)?2:1);
      const c=CAT[d.cat]||{};tip.innerHTML='<div class="c" style="color:'+(c.color||'#fff')+'">'+(c.label||'')+'</div><b>'+d.id+'</b><br>'+(d.desc||'');tip.classList.add('show');
    }).on('mousemove',e=>{const r=vp.getBoundingClientRect();let x=e.clientX-r.left+14,y=e.clientY-r.top+14;if(x+280>r.width)x-=300;tip.style.left=x+'px';tip.style.top=y+'px';})
      .on('mouseleave',()=>{node.style('opacity',1);link.style('stroke',null).style('stroke-width',null);tip.classList.remove('show');});
    node.on('click',(e,d)=>{e.stopPropagation();detail(d,links);focus(d.id);});
    legend();applyHidden();
    sim.tick(140);
    setTimeout(()=>{FOCUS?focus(FOCUS,true):fit();},360);
  }
  function fit(){const s=ST;if(!s||!s.nodes.length)return;const xs=s.nodes.map(n=>n.x),ys=s.nodes.map(n=>n.y);const a=Math.min.apply(null,xs),b=Math.max.apply(null,xs),c=Math.min.apply(null,ys),d=Math.max.apply(null,ys);const gw=(b-a)||1,gh=(d-c)||1;const k=Math.min(1.6,0.82*Math.min(s.W/gw,s.H/gh));s.svg.transition().duration(450).call(s.zoom.transform,d3.zoomIdentity.translate(s.W/2-k*(a+b)/2,s.H/2-k*(c+d)/2).scale(k));}
  function focus(id,open){const s=ST;if(!s)return;const n=s.nodes.find(x=>x.id===id);if(!n)return;const k=1.35;s.svg.transition().duration(450).call(s.zoom.transform,d3.zoomIdentity.translate(s.W/2-k*n.x,s.H/2-k*n.y).scale(k));if(open)detail(n,s.links);}
  function detail(d,links){const el=document.getElementById('detail');const c=CAT[d.cat]||{};const nb=Array.from(nbrs(d.id,links)).sort();
    el.innerHTML='<button class="x" onclick="document.getElementById(\'detail\').classList.remove(\'show\')">&times;</button><div class="c" style="color:'+(c.color||'#fff')+'">'+(c.label||'')+'</div><div class="t">'+d.id+'</div><div class="d">'+(d.desc||'')+'</div>'+(nb.length?'<div class="cn"><b>Connects to:</b> '+nb.join(' · ')+'</div>':'');el.classList.add('show');}
  function legend(){const lg=document.getElementById('legend');lg.innerHTML='';Object.keys(CAT).forEach(cat=>{const c=CAT[cat];const el=document.createElement('div');el.className='lg'+(ST.hidden.has(cat)?' off':'');el.innerHTML='<span class="dot" style="background:'+c.color+'"></span>'+c.label;el.onclick=()=>{if(ST.hidden.has(cat))ST.hidden.delete(cat);else ST.hidden.add(cat);el.classList.toggle('off');applyHidden();};lg.appendChild(el);});}
  function applyHidden(){const h=ST.hidden;ST.svg.selectAll('.nd').style('display',d=>h.has(d.cat)?'none':null);ST.svg.selectAll('.lk').style('display',l=>(h.has((l.source.cat)||'')||h.has((l.target.cat)||''))?'none':null);}
  document.getElementById('fit').onclick=fit;
  document.getElementById('q').addEventListener('keydown',e=>{if(e.key!=='Enter')return;const q=e.target.value.trim().toLowerCase();if(!q||!ST)return;const hit=ST.nodes.find(n=>n.id.toLowerCase().includes(q));if(hit)focus(hit.id,true);});
  document.getElementById('vp').addEventListener('click',e=>{if(e.target.id==='vp'||e.target.id==='svg')document.getElementById('detail').classList.remove('show');});
  run();
})();
</script>
"""


def ecosystem_map_html(focus: str = "") -> str:
    """Return a self-contained interactive ecosystem-map HTML fragment for
    st.components.v1.html. `focus` (optional) centers the map on that node."""
    sub = (f"Focused on {focus} — drag · scroll to zoom · click any node"
           if focus else
           "Drag to pan · scroll to zoom · hover to focus · click a node for details")
    safe_focus = (focus or "").replace("\\", "").replace('"', "")
    return (
        _MAP_TEMPLATE
        .replace("__TOPO_JSON__", topology_json)
        .replace("__FOCUS__", safe_focus)
        .replace("__SUB__", sub)
    )
