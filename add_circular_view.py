#!/usr/bin/env python3
"""Post-process site/index.html to add the Circular view tab."""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "site", "index.html")

with open(INDEX) as f:
    html = f.read()

# 1. Add Circular tab after Traditional tab
html = html.replace(
    '<button class="tab active" data-tab="tree"><span class="ti">🌳</span><span>Tree</span></button>',
    '<button class="tab active" data-tab="tree"><span class="ti">🌳</span><span>Traditional</span></button>\n'
    '  <button class="tab" data-tab="circle"><span class="ti">🔵</span><span>Circular</span></button>'
)

# 2. Add Circular CSS before /* ---- people grid ---- */
CIRCULAR_CSS = """
/* ---- circular tree canvas ---- */
#wrap-circle{position:absolute;inset:0;overflow:hidden;touch-action:none;user-select:none}
#stage-circle{position:absolute;inset:0;overflow:hidden}
#svg-circle{position:absolute;top:0;left:0;width:100%;height:100%;display:block;cursor:grab}
#svg-circle:active{cursor:grabbing}
#svg-circle .edge{fill:none;stroke-linecap:round}
#svg-circle .edge.glow{stroke:#5af0ff;stroke-width:3.2;opacity:.85;filter:url(#glowC)}
#svg-circle .edge.core{stroke:#ffffff;stroke-width:1.4;opacity:1}
#svg-circle .edge.glow.mar{stroke:#f4c95d;stroke-width:2;opacity:.4;stroke-dasharray:4 4;filter:none}
#svg-circle .edge.core.mar{stroke:#f4c95d;stroke-width:.7;opacity:.4;stroke-dasharray:4 4}
#svg-circle .edge.glow.direct{stroke:#f4c95d;stroke-width:4;opacity:1}
#svg-circle .edge.core.direct{stroke:#fffbe6;stroke-width:2;opacity:1}
#svg-circle .edge.glow.dim{opacity:.12}
#svg-circle .edge.core.dim{opacity:.12}
#svg-circle .node{fill:none;stroke:#eaffff;stroke-width:2.2}
#svg-circle .node.dim{opacity:.3}
#svg-circle .node.direct{stroke:#f4c95d}
#svg-circle .node.root{fill:#9dfbff;stroke:#9dfbff;filter:url(#glowW)}
#svg-circle .node-dot{fill:#eaffff}
#svg-circle .lbl{fill:#dbe9ee;font-size:9px;font-family:'Segoe UI',system-ui,sans-serif;
  paint-order:stroke;stroke:#04060a;stroke-width:2.4px;stroke-linejoin:round;pointer-events:none;user-select:none}
#svg-circle .lbl.direct{fill:#f4c95d;font-weight:600}
#svg-circle .lbl.dim{opacity:.28}
"""
html = html.replace(
    '/* ---- people grid ---- */',
    CIRCULAR_CSS + '\n/* ---- people grid ---- */'
)

# 3. Add Circular view section after view-tree section
html = html.replace(
    '  <section id="view-people" class="view">',
    '  <section id="view-circle" class="view">\n'
    '    <div id="wrap-circle">\n'
    '      <div id="stage-circle">\n'
    '        <svg id="svg-circle"><defs>\n'
    '          <filter id="glowC" x="-60%" y="-60%" width="220%" height="220%">\n'
    '            <feGaussianBlur stdDeviation="3.6" result="b1"/>\n'
    '            <feGaussianBlur stdDeviation="6.5" result="b2"/>\n'
    '            <feMerge>\n'
    '              <feMergeNode in="b2"/>\n'
    '              <feMergeNode in="b1"/>\n'
    '              <feMergeNode in="SourceGraphic"/>\n'
    '              <feMergeNode in="SourceGraphic"/>\n'
    '            </feMerge>\n'
    '          </filter>\n'
    '          <filter id="glowW" x="-100%" y="-100%" width="300%" height="300%">\n'
    '            <feGaussianBlur stdDeviation="5" result="b1"/>\n'
    '            <feGaussianBlur stdDeviation="9" result="b2"/>\n'
    '            <feMerge>\n'
    '              <feMergeNode in="b2"/>\n'
    '              <feMergeNode in="b1"/>\n'
    '              <feMergeNode in="SourceGraphic"/>\n'
    '              <feMergeNode in="SourceGraphic"/>\n'
    '            </feMerge>\n'
    '          </filter>\n'
    '        </defs></svg>\n'
    '      </div>\n'
    '      <div class="hint" id="circlehint">drag to rotate · scroll to zoom · tap a person</div>\n'
    '      <div class="zbtns" id="circzbtns">\n'
    '        <button class="zbtn" id="czin">+</button>\n'
    '        <button class="zbtn" id="czout">−</button>\n'
    '        <button class="zbtn" id="czfit">⤢</button>\n'
    '      </div>\n'
    '    </div>\n'
    '  </section>\n'
    '\n'
    '  <section id="view-people" class="view">'
)

# 4. Add Circular tab handler to the tab switching code
html = html.replace(
    "    if(tab==='map')setTimeout(startMap,60);",
    "    if(tab==='circle')setTimeout(()=>window.fitCircle&&window.fitCircle(),60);\n"
    "    if(tab==='map')setTimeout(startMap,60);"
)

# 5. Add circular JS before </script></body>
CIRCULAR_JS = r'''
/* ---------- circular tree (radial) ---------- */
(function(){
  const svg=document.getElementById('svg-circle');
  if(!svg)return;
  const ns='http://www.w3.org/2000/svg';
  const cid=Object.fromEntries(D.people.map(p=>[p.id,p]));
  const parentsOf={}; const childUnionOf={}; const spouseUnionOf={};
  D.unions.forEach(u=>{
    const pars=[u.s1,u.s2].filter(Boolean);
    (u.children||[]).forEach(c=>{ parentsOf[c]=pars.slice(); if(!childUnionOf[c])childUnionOf[c]=u; });
    pars.forEach(s=>{ (spouseUnionOf[s]=spouseUnionOf[s]||[]).push(u); });
  });
  const ROOT=(D.people.find(p=>p.you)||D.people[0]).id;
  const anc=new Set([ROOT]); const depth={[ROOT]:0};
  const q=[ROOT];
  while(q.length){const c=q.shift();const d=depth[c];(parentsOf[c]||[]).forEach(p=>{if(cid[p]&&!(p in depth)){depth[p]=d+1;anc.add(p);q.push(p);}});}
  // downward spine (two lineage trunks converging)
  const directIds=new Set(); const found={val:false};
  function downward(id,target){ if(id===target){found.val=true;return true;}
    (spouseUnionOf[id]||[]).forEach(u=>{ if(found.val)return; (u.children||[]).forEach(c=>{ if(cid[c]&&downward(c,target)){directIds.add(id);found.val=true;} }); });
    return found.val;
  }
  downward(ROOT,'P001'); downward(ROOT,'P002'); found={val:false};
  downward(ROOT,'P050'||ROOT);
  const edges=[];
  anc.forEach(c=>{ (parentsOf[c]||[]).forEach(p=>{ if(anc.has(p)) edges.push({c,p,type:'line'}); }); });
  D.unions.forEach(u=>{ const s1=u.s1,s2=u.s2;
    if(s1&&s2&&anc.has(s1)&&anc.has(s2)) edges.push({c:s1,p:s2,type:'mar'}); });
  const maxDepth=Math.max(0,...Object.values(depth));
  const RING=92;
  const VB=(maxDepth*RING+80);
  svg.setAttribute('viewBox',(-VB/2)+' '+(VB*-0.4)+' '+VB+' '+(VB*1.4));
  svg.setAttribute('width',VB); svg.setAttribute('height',VB*1.4);
  const R=(a,d)=>({x:Math.sin(a)*d,y:-Math.cos(a)*d});
  const pos={}; pos[ROOT]={x:0,y:0,a:0,d:0};
  // layout ancestors by union (recursive)
  const placed=new Set([ROOT]); const seenU=new Set();
  function layoutUnion(u,a0,a1,depthL,dOffset){
    if(!u||seenU.has(u.id)) return; seenU.add(u.id);
    const s1=u.s1,s2=u.s2;
    if(s1&&s2&&anc.has(s1)&&anc.has(s2)&&pos[s1]&&pos[s2]){
      // already placed both
    }
    const w1=(s1&&anc.has(s1))?leavesUnder(s1):0;
    const w2=(s2&&anc.has(s2))?leavesUnder(s2):0;
    const tot=w1+w2||1; const aMid=a0+(a1-a0)*(w1/tot);
    const dR=depthL*RING;
    if(s1&&anc.has(s1)&&!pos[s1]){ pos[s1]={x:Math.sin(aMid-(a1-a0)*(w1/tot)/2)*dR,y:-Math.cos(aMid-(a1-a0)*(w1/tot)/2)*dR,a:aMid-(a1-a0)*(w1/tot)/2,d:depthL}; placed.add(s1); }
    if(s2&&anc.has(s2)&&!pos[s2]){ pos[s2]={x:Math.sin(aMid+(a1-a0)*(w2/tot)/2)*dR,y:-Math.cos(aMid+(a1-a0)*(w2/tot)/2)*dR,a:aMid+(a1-a0)*(w2/tot)/2,d:depthL}; placed.add(s2); }
    // lay out children of this union
    const children=(u.children||[]).filter(c=>anc.has(c));
    if(children.length>0){
      const childW=children.map(c=>leavesUnder(c));
      const total=childW.reduce((a,b)=>a+b,0)||1;
      let curA=a0;
      children.forEach(c=>{
        if(cid[c]&&!pos[cid[c].id]){
          const cw=childW.shift()||1;
          const frac=cw/total;
          layoutCid(cid[c],curA,curA+frac*(a1-a0),depthL+1);
          curA+=frac*(a1-a0);
        }
      });
    }
  }
  function layoutCid(p,a0,a1,depthL){
    if(pos[p.id]||!anc.has(p.id)) return;
    const d=depth[p.id];
    const aMid=(a0+a1)/2;
    const dR=d*RING;
    pos[p.id]={x:Math.sin(aMid)*dR,y:-Math.cos(aMid)*dR,a:aMid,d:d}; placed.add(p.id);
    (spouseUnionOf[p.id]||[]).forEach(u=>{
      const children=(u.children||[]).filter(c=>anc.has(c));
      if(children.length>0){
        const childW=children.map(c=>leavesUnder(c));
        const total=childW.reduce((a,b)=>a+b,0)||1;
        let curA=a0;
        children.forEach(c=>{
          const cw=childW.shift()||1;
          layoutCid(cid[c],curA,curA+(cw/total)*(a1-a0),depth[c]+1);
          curA+=(cw/total)*(a1-a0);
        });
      }
    });
  }
  const leafMemo={};
  function leavesUnder(pid){
    if(leafMemo[pid]) return leafMemo[pid];
    const u=childUnionOf[pid];
    if(!u){leafMemo[pid]=1;return 1;}
    let s=0;
    [u.s1,u.s2].forEach(sp=>{ if(sp&&cid[sp]) s+=leavesUnder(sp); });
    (u.children||[]).forEach(c=>{ s+=leavesUnder(c); });
    leafMemo[pid]=Math.max(1,s); return leafMemo[pid];
  }
  // Start layout from root
  const rootUnions=spouseUnionOf[ROOT]||[];
  if(rootUnions.length>0){
    const total=rootUnions.reduce((sum,u)=>sum+leavesUnder(u.s1)+leavesUnder(u.s2),0)||1;
    let curA=0;
    rootUnions.forEach(u=>{
      const w=leavesUnder(u.s1)+leavesUnder(u.s2);
      layoutUnion(u,curA,curA+(w/total)*Math.PI*2,1,0);
      curA+=(w/total)*Math.PI*2;
    });
  }
  // Place orphans (not reached by descent)
  anc.forEach(pid=>{ if(!pos[pid]) pos[pid]={x:0,y:0,a:0,d:depth[pid]||0}; });
  // Force-directed refinement pass
  const nodes=Object.keys(pos).map(id=>({id,px:pos[id].x,py:pos[id].y,x:pos[id].x,y:pos[id].y}));
  const adj={}; nodes.forEach(n=>{adj[n.id]=[];});
  edges.forEach(e=>{
    if(pos[e.c]&&pos[e.p]){
      adj[e.c].push(e.p); adj[e.p].push(e.c);
    }
  });
  const RADIUS=30;
  for(let it=0;it<80;it++){
    nodes.forEach(n=>{
      let fx=0,fy=0,k=0;
      adj[n.id].forEach(m=>{
        const dx=n.px-m.px,dy=n.py-m.py;
        const dist=Math.hypot(dx,dy)||0.1;
        const target=e.type==='mar'?30:80;
        const diff=(dist-target)/dist*0.1;
        fx+=(dx*diff); fy+=(dy*diff); k++;
      });
      if(k>0){n.px+=fx/k*n; n.py+=fy/k*n;}
      else{n.px+=n.px*0.01; n.py+=n.py*0.01;}
    });
  }
  // Update final positions
  nodes.forEach(n=>{
    pos[n.id].x=n.px; pos[n.id].y=n.py;
  });
  // Draw edges
  edges.forEach(e=>{
    if(pos[e.c]&&pos[e.p]){
      const pa=pos[e.c],pb=pos[e.p];
      const isDirect=directIds.has(e.c)||directIds.has(e.p);
      const g=document.createElementNS(ns,'g');
      g.setAttribute('class','edge-group');
      const core=document.createElementNS(ns,'path');
      core.setAttribute('class','edge core'+(isDirect?' direct':'')+((e.type==='mar')?' mar':''));
      const dx=pb.x-pa.x,dy=pb.y-pa.y;
      const len=Math.hypot(dx,dy)||1;
      core.setAttribute('d',`M${pa.x},${pa.y}L${pa.x+dx/len*3},${pa.y+dy/len*3}L${pb.x-dx/len*3},${pb.y-dy/len*3}L${pb.x},${pb.y}`);
      g.appendChild(core);
      const glow=document.createElementNS(ns,'path');
      glow.setAttribute('class','edge glow'+(isDirect?' direct':'')+((e.type==='mar')?' mar':''));
      glow.setAttribute('d',core.getAttribute('d'));
      g.appendChild(glow);
      svg.appendChild(g);
    }
  });
  // Draw nodes
  nodes.forEach(n=>{
    const p=cid[n.id];
    if(!p) return;
    const isRoot=n.id===ROOT;
    const isDirect=directIds.has(n.id);
    const isMetis=p.metis;
    const g=document.createElementNS(ns,'g');
    g.setAttribute('class','node-g');
    const c=document.createElementNS(ns,'circle');
    c.setAttribute('class','node'+(isRoot?' root':'')+(isDirect?' direct':''));
    c.setAttribute('cx',n.px);c.setAttribute('cy',n.py);
    c.setAttribute('r',isRoot?8:5);
    if(isRoot){const glow=document.createElementNS(ns,'circle');glow.setAttribute('class','node-dot');glow.setAttribute('cx',n.px);glow.setAttribute('cy',n.py);glow.setAttribute('r',isRoot?9:5);glow.setAttribute('filter','url(#glowW)');g.appendChild(glow);g.appendChild(c);}
    else{
      const core=document.createElementNS(ns,'circle');core.setAttribute('class','node-dot');core.setAttribute('cx',n.px);core.setAttribute('cy',n.py);core.setAttribute('r',2.4);
      g.appendChild(c);g.appendChild(core);
    }
    // Label
    if(n.px>-VB/2+20 && n.px<VB/2-20){
      const lbl=document.createElementNS(ns,'text');
      lbl.setAttribute('class','lbl'+(isDirect?' direct':'')+(p.metis?'':' dim'));
      lbl.setAttribute('x',n.px+9);lbl.setAttribute('y',n.py+3);
      lbl.setAttribute('text-anchor','start');
      const nm=p.name.split(' ')[0];
      lbl.textContent=p.name.length>18?p.name.split(' ')[0]+'...':p.name;
      g.appendChild(lbl);
    }
    // Click to open profile
    g.addEventListener('click',()=>openSheet([n.id]));
    svg.appendChild(g);
  });
  // Zoom/pan for circular view
  let rot=0,zoom=1;
  let fitC, zoomAtC;
  function applyC(){
    svg.style.transform=`scale(${zoom})`;
    svg.style.transformOrigin='50% 50%';
  }
  fitC=function(){ const vw=wrap.clientWidth,vh=wrap.clientHeight;
    zoom=Math.min(vw,vh)/((maxDepth*RING+90)*2)*0.94; zoom=Math.max(zoom,0.2); rot=0; applyC(); }
  zoomAtC=function(f){ zoom=Math.min(6,Math.max(0.2,zoom*f)); applyC(); }
  window.fitCircle=fitC;
  // Zoom buttons
  const cZin=document.getElementById('czin'), cZout=document.getElementById('czout'), cZfit=document.getElementById('czfit');
  if(cZin) cZin.onclick=()=>{ zoomAtC(1.35); };
  if(cZout) cZout.onclick=()=>{ zoomAtC(1/1.35); };
  if(cZfit) cZfit.onclick=fitC;
  fitC();
})();
'''

# Insert circular JS before the closing </script></body>
html = html.replace(
    '</script>\n</body></html>',
    CIRCULAR_JS + '\n</script>\n</body></html>'
)

with open(INDEX, 'w') as f:
    f.write(html)
print(f"Added circular view to {INDEX} ({len(html)} bytes)")
