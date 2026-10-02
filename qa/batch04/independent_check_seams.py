"""Read actual GLB seam vertices, apply documented instance transforms, compare mating profiles."""
from pathlib import Path
import sys,json,hashlib,math,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa'))
from inspect_glb_independent import GLB
BASE=ROOT/'assets/botanical_planter';OUT=ROOT/'qa/batch04'
def vertices(file,translation=(0,0,0),angle=0):
 g=GLB(file);parts={};d=g.doc
 def visit(i,parent):
  n=d['nodes'][i];m=parent@g.matrix(n)
  if 'mesh' in n:
   for p in d['meshes'][n['mesh']]['primitives']:
    v=g.accessor(p['attributes']['POSITION']);w=np.c_[v,np.ones(len(v))]@m.T;xyz=w[:,[0,2,1]];xyz[:,1]*=-1
    a=math.radians(angle);rot=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    xyz=xyz@rot.T+translation;role=d['materials'][p['material']]['name'];parts.setdefault(role,[]).append(xyz)
  for c in n.get('children',[]):visit(c,m)
 for n in d['scenes'][d.get('scene',0)]['nodes']:visit(n,np.eye(4))
 return {k:np.concatenate(v) for k,v in parts.items()}
parts={'start':vertices(BASE/'derived/AST-BOT-006_START.glb'),'straight':vertices(BASE/'AST-BOT-004.glb'),'turn':vertices(BASE/'AST-BOT-005.glb',(2.4,0,0)),'end':vertices(BASE/'AST-BOT-006.glb',(3.8,1.4,0),90)}
rows=[]
for a,b,axis,coord in [('start','straight',0,0),('straight','turn',0,2.4),('turn','end',1,1.4)]:
 profiles=[]
 for role in sorted(parts[a].keys()&parts[b].keys()):
  av=parts[a][role];bv=parts[b][role];ax=av[np.abs(av[:,axis]-(coord-.001))<1e-5];bx=bv[np.abs(bv[:,axis]-(coord+.001))<1e-5]
  if not len(ax) or not len(bx):continue
  projected=[k for k in range(3) if k!=axis];ap=ax[:,projected];bp=bx[:,projected]
  dist=np.linalg.norm(ap[:,None,:]-bp[None,:,:],axis=2);haus=max(dist.min(axis=0).max(),dist.min(axis=1).max())
  profiles.append({'role':role,'left_seam_vertices':len(ax),'right_seam_vertices':len(bx),'gap_min_m':float(bx[:,axis].min()-ax[:,axis].max()),'gap_max_m':float(bx[:,axis].max()-ax[:,axis].min()),'projected_vertex_profile_hausdorff_m':float(haus),'profile_matches_0_1mm':bool(haus<.0001)})
 rows.append({'left':a,'right':b,'seam_axis':axis,'seam_datum_m':coord,'profiles':profiles,'all_profiles_match':all(x['profile_matches_0_1mm'] for x in profiles)})
(OUT/'independent_actual_seams.json').write_text(json.dumps({'scope':'Actual exported mating profiles, 2mm nominal air seams, Z-up metre positions; no engine or structural test','joins':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
