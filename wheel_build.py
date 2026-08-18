#!/usr/bin/env python3
"""wheel_build.py — build a radial family "wheel" (pedigree fan, real connectors).

Design (user-confirmed):
  - Focal person (P050 Bayard) at the CENTER.
  - Ancestors radiate OUTWARD by generation (oldest roots on the outside edge).
  - Each couple = one unit; married-in spouses sit beside their blood partner.
  - Whole 91-person extended tree (every ancestor from every line).
  - Clean per-family-line wedge grouping is the priority; the two converging
    Spence lines may cross (accepted).
  - Real parent->child connector lines + marriage bars, touch rotate/zoom/tap.

Layout algorithm:
  ring  = generation depth from focal (0 center, +1 = parents, ... outward)
  wedge = family line (surname cluster); each line owns a contiguous angular sector
  Within a sector, members are fanned by generation so same-generation people
  spread across the wedge; parent->child lines stay roughly radial/in-sector.
  Cross-family marriages produce the (accepted) crossing lines.
"""
import sys, os, json, argparse, collections, math
from collections import defaultdict, deque

def _surname(name):
    toks = (name or "").split()
    if not toks: return "?"
    while toks and toks[-1] in ("Sr","Jr","I","II","III","IV"): toks.pop()
    if not toks: return "?"
    last = toks[-1].lower()
    if last.startswith("devries") or last in ("vries","devries"): return "deVries"
    if last == "vries": return "deVries"
    if len(toks) >= 2 and toks[-2].lower() in ("de","van","der","den","di","la","le","von"):
        return (toks[-2]+" "+toks[-1]).title()
    return toks[-1]

def build(people, unions, focal):
    byid={p["id"]:p for p in people}
    byunion={u["id"]:u for u in unions}
    children_of=defaultdict(list); parent_union={}
    for u in unions:
        for c in u.get("children",[]):
            children_of[u["spouse1"]].append(c); children_of[u["spouse2"]].append(c)
            parent_union.setdefault(c,u["id"])
    # generation depth from focal
    gen={}; q=deque([focal]); gen[focal]=0; seen={focal}
    while q:
        n=q.popleft(); g=gen[n]
        if n in parent_union:
            u=byunion[parent_union[n]]
            for sp in (u["spouse1"],u["spouse2"]):
                if sp not in seen: seen.add(sp); gen[sp]=g+1; q.append(sp)
        for c in children_of.get(n,[]):
            if c not in seen: seen.add(c); gen[c]=g-1; q.append(c)
    for p in people: gen.setdefault(p["id"],0)

    # ---- line (surname cluster) per person ----
    sn_count=collections.Counter(_surname(p.get("name","")) for p in people)
    spouse_of=defaultdict(list)
    for u in unions:
        spouse_of[u["spouse1"]].append(u["id"]); spouse_of[u["spouse2"]].append(u["id"])
    line={}
    for p in people: line[p["id"]]=_surname(p.get("name",""))
    for p in people:
        if sn_count.get(line[p["id"]],0)<2:
            for uid in spouse_of[p["id"]]:
                u=byunion[uid]
                for other in (u["spouse1"],u["spouse2"]):
                    if other!=p["id"] and sn_count.get(line.get(other,""),0)>=2:
                        line[p["id"]]=line[other]; break
                if sn_count.get(line[p["id"]],0)>=2: break
    by_line=defaultdict(list)
    for p in people: by_line[line[p["id"]]].append(p["id"])
    line_names=sorted(by_line.keys())
    palette=["#ff6b6b","#ffd166","#06d6a0","#118ab2","#ef476f","#f78c6b","#7b2cbf",
             "#4cc9f0","#f72585","#b5e48c","#90be6d","#9d4edd","#ff9e00","#00b4d8",
             "#e9c46a","#2ec4b6","#ff70a6","#70d6ff"]
    linecolor={ln:palette[i%len(palette)] for i,ln in enumerate(line_names)}

    # ---- UNION-TREE: couples as nodes, leaf-weighted angular wedges ----
    child_union={}
    for u in unions:
        for c in u.get("children",[]): child_union.setdefault(c,u["id"])
    union_out=defaultdict(list)
    for u in unions:
        for sp in (u["spouse1"],u["spouse2"]):
            if sp in child_union and child_union[sp]!=u["id"]:
                union_out[u["id"]].append(child_union[sp])
    for k in union_out: union_out[k]=list(dict.fromkeys(union_out[k]))
    root=child_union.get(focal)
    seenU={root} if root else set(); genU={root:1}; spanU={root:None}; orderU=[root]
    q=deque([root] if root else [])
    while q:
        u=q.popleft()
        for nb in union_out[u]:
            if nb not in seenU:
                seenU.add(nb); genU[nb]=genU[u]+1; spanU[nb]=u; q.append(nb); orderU.append(nb)
    chU=defaultdict(list)
    for u in orderU:
        if spanU.get(u): chU[spanU[u]].append(u)
    sys.setrecursionlimit(100000)
    subwU={}
    def swU(u):
        if u in subwU: return subwU[u]
        ch=chU.get(u,[])
        subwU[u]=1 if not ch else sum(swU(c) for c in ch)
        return subwU[u]
    angleU={}
    def assignU(u,a0,a1):
        angleU[u]=(a0+a1)/2
        ch=chU.get(u,[])
        if not ch: return
        tot=sum(swU(c) for c in ch) or 1
        cur=a0
        for c in ch:
            w=swU(c)/tot*(a1-a0)
            assignU(c,cur,cur+w); cur+=w
    if root: assignU(root,0,360)
    # graft unreached unions onto a connecting spouse's reached-union angle
    for u in unions:
        if u["id"] in angleU: continue
        # find a spouse whose OTHER union is reached
        for sp in (u["spouse1"],u["spouse2"]):
            for uid in spouse_of[sp]:
                if uid in angleU:
                    angleU[u["id"]]=angleU[uid]; genU[u["id"]]=genU.get(uid,1)+0  # same ring-ish
                    break
            if u["id"] in angleU: break
        if u["id"] not in angleU:
            angleU[u["id"]]=0; genU[u["id"]]=1
    # person angle = their birth-union angle (couple shares a spoke)
    person_ang={}
    for u in angleU:
        un=byunion[u]
        person_ang[un["spouse1"]]=angleU[u]; person_ang[un["spouse2"]]=angleU[u]
        for c in un.get("children",[]): person_ang.setdefault(c,angleU[u])
    person_ang[focal]=0
    for p in people: person_ang.setdefault(p["id"],0)

    # ---- radial position: ring from generation, fanned within each union's wedge ----
    gmax=max(max(gen.values()),1); R0,R1=80.0,520.0
    def radius(g): return R0+(g/gmax)*(R1-R0) if g>0 else R0-10*abs(g)
    # give each union an angular interval so its members fan out (avoid sibling overlap)
    # compute union widths from the leaf-weight tree
    union_width={}
    for u in unions:
        uid=u["id"]; w=swU(uid) if uid in subwU else 1
        # width ~ proportional to members, clamped
        n_mem=len(set([u["spouse1"],u["spouse2"]]+list(u.get("children",[]))))
        union_width[uid]=min(30.0, max(8.0, 6.0+n_mem*2.0))
    pos={}
    # process each union: spouses fanned, children fanned.
    # SPOUSE placement wins over CHILD placement (a person's own marriage is their home spoke).
    def add_member(pid,a,ang_dev,r):
        pos[pid]=(a+ang_dev,r)
    # PASS 1: spouses (their marriage union is authoritative)
    for u in unions:
        uid=u["id"]; base=angleU.get(uid,0)
        add_member(u["spouse1"], base, -2.5, radius(gen.get(u["spouse1"],0)))
        add_member(u["spouse2"], base, +2.5, radius(gen.get(u["spouse2"],0)))
    # PASS 2: children only if not already placed as a spouse
    for u in unions:
        uid=u["id"]; base=angleU.get(uid,0); w=union_width[uid]
        kids=list(u.get("children",[])); n=len(kids)
        for i,c in enumerate(kids):
            if c in pos: continue   # already placed as a spouse
            dev = -w/2 + (i+0.5)*(w/max(1,n))
            add_member(c, base, dev, radius(gen.get(c,0)))
    # people not in any union as child/spouse (isolated) get their line angle
    for p in people:
        if p["id"] not in pos:
            add_member(p["id"], person_ang.get(p["id"],0), 0, radius(gen.get(p["id"],0)))
    pos[focal]=(0.0,0.0)

    nodes=[]
    for p in people:
        a,r=pos[p["id"]]; a=(a+360)%360
        nodes.append({
            "id":p["id"],"name":p["name"],"a":round(a,2),"r":round(r,1),
            "g":gen[p["id"]],"c":linecolor[line[p["id"]]],
            "lc":round((person_ang.get(p["id"],0)+360)%360,2),"you":p["id"]==focal,
            "d":((p.get("birth","") or "")+(("-"+p.get("death","")) if p.get("death") else "")),
        })
    conn=[]
    for u in unions:
        s1,s2=u["spouse1"],u["spouse2"]
        if s1 in pos and s2 in pos:
            conn.append({"kind":"marriage","u":u["id"],"p1":s1,"p2":s2})
        for c in u.get("children",[]):
            if c in pos:
                conn.append({"kind":"child","u":u["id"],"child":c,"parent":s1})
    legend=[{"n":ln,"c":linecolor[ln],"lc":round((person_ang.get(by_line[ln][0],0)+360)%360,2)} for ln in line_names]
    return nodes,conn,legend

TEMPLATE=r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>__TITLE__ — Family Wheel</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#07070f;color:#e8e8f0;font-family:'Segoe UI',system-ui,sans-serif;overflow:hidden;height:100dvh;touch-action:none}
  #wrap{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:
    radial-gradient(circle at 50% 40%, #1a1a30 0%, #0b0b18 58%, #040409 100%)}
  svg{width:100%;height:100%}
  .node{cursor:pointer;opacity:0;transition:opacity .3s ease}
  .node:hover circle{filter:brightness(1.6) drop-shadow(0 0 6px currentColor)}
  .nodet{font-size:7.5px;fill:#e8e8f4;font-weight:600;pointer-events:none;text-anchor:middle;
    paint-order:stroke;stroke:#07070f;stroke-width:2.5px}
  .conn{fill:none;stroke-linecap:round;pointer-events:none}
  #hub text{fill:#ffd166;text-anchor:middle}
  #hub circle.me{fill:#ffd166;stroke:#fff;stroke-width:2}
  #hud{position:fixed;top:12px;left:12px;right:12px;display:flex;justify-content:space-between;align-items:flex-start;z-index:5;pointer-events:none}
  #title{font-size:13px;font-weight:700;letter-spacing:.5px;text-shadow:0 1px 4px #000}
  #title small{display:block;font-size:9px;font-weight:400;opacity:.55;margin-top:2px}
  #hint{font-size:9px;opacity:.5;text-align:right;max-width:160px;line-height:1.4}
  #legend{position:fixed;bottom:12px;left:12px;z-index:5;background:#ffffff0d;backdrop-filter:blur(8px);
    border:1px solid #ffffff1a;border-radius:12px;padding:8px 10px;font-size:9px;max-width:190px}
  #legend b{display:block;font-size:10px;margin-bottom:4px}
  #legend span{display:flex;align-items:center;gap:5px;margin:2px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;padding:2px 4px;border-radius:4px}
  #legend span:hover{background:#ffffff1c}
  #legend span.active{background:#ffffff1c;outline:1px solid currentColor}
  #legend i{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none}
  #sheet{position:fixed;left:0;right:0;bottom:0;background:#17172b;border-top:1px solid #ffffff22;
    border-radius:18px 18px 0 0;padding:16px 18px 28px;transform:translateY(110%);transition:transform .3s;z-index:10}
  #sheet.open{transform:translateY(0)}
  #sheet .n{font-size:18px;font-weight:700}
  #sheet .d{font-size:12px;opacity:.65;margin-top:2px}
  #sheet .l{font-size:10px;display:inline-block;margin-top:8px;padding:3px 10px;border-radius:20px;color:#0a0a12;font-weight:700}
  #sheet .close{position:absolute;top:12px;right:16px;font-size:20px;opacity:.5;background:none;border:none;color:#fff;cursor:pointer}
  .grab{cursor:grab}
  .btnrow{position:fixed;bottom:12px;right:12px;z-index:6;display:flex;gap:6px}
  .btnrow button{background:#ffffff14;border:1px solid #ffffff2a;color:#e8e8f0;border-radius:9px;width:34px;height:34px;font-size:14px;cursor:pointer}
  .btnrow button:hover{background:#ffffff2a}
</style>
</head>
<body>
<div id="wrap"><svg id="svg" viewBox="-620 -620 1240 1240"></svg></div>
<div id="hud">
  <div id="title">__TITLE__<small>drag to rotate · pinch to zoom · parents connect to children</small></div>
  <div id="hint">⟳ drag to rotate · pinch zoom<br>tap a person for details</div>
</div>
<div class="btnrow"><button onclick="rotBy(-30)">⟲</button><button onclick="rotBy(30)">⟳</button></div>
<div id="legend"><b>Family lines</b><div id="leglist"></div></div>
<div id="sheet"><button class="close" onclick="closeSheet()">✕</button><div class="n" id="s_name"></div><div class="d" id="s_dates"></div><div class="l" id="s_line"></div></div>
<script>
__DATA__
const SVG=document.getElementById('svg'),NS='http://www.w3.org/2000/svg';
const g=document.createElementNS(NS,'g');SVG.appendChild(g);
let rotation=0,scale=1,dragging=false,lastX=0,lastTap=0;
const byId={};NODES.forEach(n=>{n.x=Math.round(n.r*Math.cos(n.a*Math.PI/180));n.y=Math.round(n.r*Math.sin(n.a*Math.PI/180));byId[n.id]=n;});
// connectors (behind nodes)
CONN.forEach(c=>{
  if(c.kind==='marriage'){const a=byId[c.p1],b=byId[c.p2];if(!a||!b)return;
    const l=document.createElementNS(NS,'line');l.setAttribute('class','conn');
    l.setAttribute('x1',a.x);l.setAttribute('y1',a.y);l.setAttribute('x2',b.x);l.setAttribute('y2',b.y);
    l.setAttribute('stroke','#E8B45A');l.setAttribute('stroke-width',3);l.setAttribute('vector-effect','non-scaling-stroke');
    g.appendChild(l);
  } else if(c.kind==='child'){const ch=byId[c.child],pa=byId[c.parent];if(!ch||!pa)return;
    const l=document.createElementNS(NS,'line');l.setAttribute('class','conn');
    l.setAttribute('x1',pa.x);l.setAttribute('y1',pa.y);l.setAttribute('x2',ch.x);l.setAttribute('y2',ch.y);
    l.setAttribute('stroke','#A99BD9');l.setAttribute('stroke-width',2.2);l.setAttribute('vector-effect','non-scaling-stroke');
    g.appendChild(l);
  }
});
// hub
const hub=document.createElementNS(NS,'g');hub.setAttribute('id','hub');g.appendChild(hub);
const me=document.createElementNS(NS,'circle');me.setAttribute('r',12);me.setAttribute('class','me');hub.appendChild(me);
const ht=document.createElementNS(NS,'text');ht.setAttribute('y',-20);ht.setAttribute('font-size','11px');ht.setAttribute('font-weight','700');ht.textContent=__FOCAL_NAME__;hub.appendChild(ht);
// nodes
const nodeEls=[];
NODES.forEach((n,i)=>{
  const node=document.createElementNS(NS,'g');node.setAttribute('class','node');
  const cc=document.createElementNS(NS,'circle');cc.setAttribute('r',n.g>=0?5:4);cc.setAttribute('fill',n.c);
  cc.setAttribute('stroke','#fff');cc.setAttribute('stroke-width','1');node.appendChild(cc);
  const tx=document.createElementNS(NS,'text');tx.setAttribute('class','nodet');tx.setAttribute('y',10);tx.textContent=n.name;node.appendChild(tx);
  node.setAttribute('transform',`translate(${n.x} ${n.y})`);
  node.addEventListener('click',()=>openSheet(n));
  g.appendChild(node);nodeEls.push({el:node,tx,c:n.c,id:n.id});
  setTimeout(()=>node.style.opacity=1,120+i*5);
});
function applyScale(){g.setAttribute('transform',`rotate(${rotation}) scale(${scale})`);}
const wrap=document.getElementById('wrap');
const ptrs={};let pinchDist=0,pinchScale=1;
wrap.addEventListener('pointerdown',e=>{
  ptrs[e.pointerId]={x:e.clientX,y:e.clientY};
  const keys=Object.keys(ptrs);
  if(keys.length===2){
    dragging=false;
    const[a,b]=keys.map(k=>ptrs[k]);
    pinchDist=Math.hypot(a.x-b.x,a.y-b.y);pinchScale=scale;
    lastTap=0; // a second finger cancels any pending double-tap
  }else{
    dragging=true;lastX=e.clientX;
    const now=Date.now();
    if(now-lastTap<280){scale=scale>1.4?1:Math.min(5,scale*2.2);applyScale();lastTap=0;}
    else lastTap=now;
  }
});
// attach move/up to window AND wrap (no setPointerCapture so events reach the listener)
function pmove(e){
  if(!(e.pointerId in ptrs))return;
  ptrs[e.pointerId]={x:e.clientX,y:e.clientY};
  const keys=Object.keys(ptrs);
  if(keys.length===2){
    const[a,b]=keys.map(k=>ptrs[k]);
    const d=Math.hypot(a.x-b.x,a.y-b.y);
    if(pinchDist>0){scale=Math.min(5,Math.max(0.35,pinchScale*d/pinchDist));applyScale();}
  }else if(dragging){
    const dx=e.clientX-lastX;rotation+=dx*0.4;lastX=e.clientX;applyScale();
  }
}
function pend(e){delete ptrs[e.pointerId];if(Object.keys(ptrs).length<2)dragging=false;}
window.addEventListener('pointermove',pmove);
wrap.addEventListener('pointermove',pmove);
window.addEventListener('pointerup',pend);window.addEventListener('pointercancel',pend);
wrap.addEventListener('pointerup',pend);wrap.addEventListener('pointercancel',pend);
window.addEventListener('touchmove',e=>e.preventDefault(),{passive:false});
function rotBy(d){rotation+=d;applyScale();}
document.getElementById('leglist').innerHTML=LINES.map(l=>`<span data-lc="${l.lc}" data-c="${l.c}" style="color:${l.c}"><i style="background:${l.c}"></i>${l.n}</span>`).join('');
document.querySelectorAll('#leglist span').forEach(sp=>{sp.addEventListener('click',()=>{rotation=270-parseFloat(sp.dataset.lc);applyScale();document.querySelectorAll('#leglist span').forEach(x=>x.classList.toggle('active',x===sp));});});
function openSheet(n){
  document.getElementById('s_name').textContent=n.name;
  document.getElementById('s_dates').textContent=(n.d||'dates unknown')+(n.you?' · focal':(n.g>=0?' · ancestor':' · descendant'));
  const l=document.getElementById('s_line');l.textContent=n.you?'focal person':(n.g>=0?'ancestor':'descendant');l.style.background=n.c;
  document.getElementById('sheet').classList.add('open');
}
function closeSheet(){document.getElementById('sheet').classList.remove('open');}
applyScale();
</script>
</body>
</html>
"""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",nargs="?",default=os.path.expanduser("~/projects/deVries-family-tree/data/family-tree.json"))
    ap.add_argument("-o","--out",default=os.path.expanduser("~/projects/deVries-family-tree/site/wheel.html"))
    ap.add_argument("--focal",default=None)
    ap.add_argument("--title",default=None)
    a=ap.parse_args()
    d=json.load(open(a.input))
    people=d["people"];unions=d["unions"]
    focal=a.focal or next((p["id"] for p in people if p.get("you")),None)
    if not focal:
        kids=set(c for u in unions for c in u.get("children",[]))
        focal=next((p["id"] for p in people if p["id"] not in kids),people[0]["id"])
    title=a.title or (d.get("project",{}).get("title") if isinstance(d.get("project"),dict) else d.get("project")) or "Family"
    fname=next(p["name"] for p in people if p["id"]==focal).split()[0]
    nodes,conn,legend=build(people,unions,focal)
    data=("const NODES="+json.dumps(nodes,ensure_ascii=False)+";\nconst CONN="+json.dumps(conn,ensure_ascii=False)+";\nconst LINES="+json.dumps(legend,ensure_ascii=False)+";")
    html=TEMPLATE.replace("__DATA__",data).replace("__TITLE__",title).replace("__FOCAL_NAME__",json.dumps(fname))
    os.makedirs(os.path.dirname(a.out),exist_ok=True)
    open(a.out,"w").write(html)
    print(f"OK wheel -> {a.out} ({len(nodes)} people, {len(conn)} conn, {len(legend)} lines, focal={fname})")

if __name__=="__main__":
    main()
