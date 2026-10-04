"""Neutral centre-section drawn from actual native GLB triangles, no source-geometry substitution."""
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('actual_glb',CAT/'qa/inspect_glb_independent.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
file=BASE/'exports/AST-RTL-001.glb';g=reader.GLB(file);d=g.doc;segments=[];loops=[];primitive_reports=[]
def visit(i,parent):
 node=d['nodes'][i];w=parent@g.matrix(node)
 if 'mesh'in node:
  for p in d['meshes'][node['mesh']]['primitives']:
   v=g.accessor(p['attributes']['POSITION']);native=(np.column_stack((v,np.ones(len(v))))@w.T)[:,:3];v=native[:,[0,2,1]].copy();v[:,1]*=-1;tris=g.accessor(p['indices']).ravel().reshape(-1,3);ss=[]
   for t in tris:
    q=v[t];pts=[]
    for a,b in zip(q,np.roll(q,-1,axis=0)):
     if abs(a[0])<1e-7:pts.append(a[1:])
     if a[0]*b[0]<0:pts.append((a+(b-a)*(-a[0]/(b[0]-a[0])))[1:])
    unique={tuple(np.round(q,7))for q in pts}
    if len(unique)==2:
     a,b=sorted(unique)
     if np.linalg.norm(np.array(a)-b)>1e-8:ss.append((a,b))
   edges=set(ss);adj={}
   for a,b in edges:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
   rest=set(edges);found=[]
   while rest:
    a,b=rest.pop();seq=[a,b]
    while seq[-1]!=seq[0]:
     choices=[q for q in adj[seq[-1]]if tuple(sorted((seq[-1],q)))in rest]
     if not choices:break
     q=choices[0];rest.remove(tuple(sorted((seq[-1],q))));seq.append(q)
    if seq[-1]==seq[0]:found.append(seq)
   segments.extend(edges);loops.extend(found);primitive_reports.append({'node':node['name'],'segment_count':len(edges),'closed_section_loops':len(found),'all_graph_vertices_degree_two':all(len(v)==2 for v in adj.values())})
 for child in node.get('children',[]):visit(child,w)
for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4))
fig,ax=plt.subplots(figsize=(8.2,8.2),dpi=150);fig.patch.set_facecolor('#f6f6f3');ax.set_facecolor('#f6f6f3')
for p in loops:ax.add_patch(Polygon(p,closed=True,facecolor='#bec2c1',edgecolor='none'))
for a,b in segments:ax.plot([a[0],b[0]],[a[1],b[1]],color='#222e32',lw=1.15)
ax.axhline(0,color='#7b8283',lw=.8,ls='--');ax.set_xlim(-1.23,1.45);ax.set_ylim(-.12,3.13);ax.set_aspect('equal');ax.set_xticks([-.45,0,.45]);ax.set_yticks([0,.23,.95,1.52,2.495,2.9]);ax.tick_params(labelsize=8);ax.grid(axis='y',alpha=.12);ax.spines[['top','right']].set_visible(False);ax.set_xlabel('Source Y depth (m)  |  front toward left',fontsize=9);ax.set_ylabel('Source Z height (m)',fontsize=9)
for text,target,end in [('Pale canopy profile',(-.38,2.72),(-1.18,2.88)),('90 mm recessed return',(-.30,2.535),(-1.18,2.32)),('Physical dark backing',(.37,2.08),(.62,2.2)),('Supported upper shelf',(-.14,1.49),(-1.18,1.63)),('Main tactile slab',(-.40,.91),(-1.18,1.12)),('Open lower storage',(-.17,.52),(.62,.56)),('Joined floor / plinth',(-.30,.11),(.62,.12))]:
 ax.annotate(text,xy=target,xytext=end,fontsize=8,ha='left',va='center',arrowprops={'arrowstyle':'-','color':'#647075','lw':.8},color='#28363c')
fig.suptitle('AST-RTL-001 · Neutral centre section',x=.12,y=.98,ha='left',fontsize=15,color='#22323b');fig.text(.12,.945,'Actual exported GLB, cut at source X = 0 m',fontsize=10,color='#4e5b60');fig.text(.12,.035,'All materials shown in the same neutral grey. Profile depth is actual geometry.\nInspection only: no recovered shop, host wall, ceiling, installation or runtime lighting.',fontsize=8,color='#586469');fig.subplots_adjust(left=.14,right=.98,top=.91,bottom=.13)
out=BASE/'qa/001_neutral_actual_glb_section.png';fig.savefig(out,dpi=150);plt.close(fig)
r={'asset':'AST-RTL-001','input_export_sha256':sha(file),'input_source_sha256':sha(BASE/'source/AST-RTL-001.blend'),'script_sha256':sha(Path(__file__)),'cut_frame':'source XYZ Z-up metres reconstructed once from actual native GLB node world coordinates','cut_plane_source_x_m':0,'method':'Intersect actual exported triangles with X=0, stitch connected line loops, fill every role neutral grey','section_segment_count':len(segments),'closed_loops':len(loops),'primitives':primitive_reports,'image':'qa/'+out.name,'image_sha256':sha(out),'pixels':[1230,1230],'limits':'Mesh-derived geometric diagnostic; neither runtime material/lighting nor finished host installation'}
(BASE/'qa/neutral_section_evidence.json').write_text(json.dumps(r,indent=2)+'\n');print('SECTION',len(segments),len(loops),out)
