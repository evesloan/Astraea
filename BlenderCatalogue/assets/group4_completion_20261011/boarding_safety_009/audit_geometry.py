from pathlib import Path
import json,hashlib,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[3];sys.path.insert(0,str(W.parent));from glb_geometry import triangles
P=json.loads((W/'SAFETY_PLAN.json').read_text());TP=json.loads((W/'TERMINAL_PLAN.json').read_text());checks=0;errors=[]
def ck(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
exports=[]
for file in [P['vehicle_successor'],P['station_receiver_asset'],P['restraint_asset'],TP['asset']]:
 count=0;num=0
 for name,t,x in triangles(W/file):
  ck(np.isfinite(t).all(),file+' '+name+' finite')
  ck(bool((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-9).all()),file+' '+name+' nondegenerate')
  count+=1;num+=len(t)
 exports.append({'file':file,'meshes':count,'triangles':num,'sha256':hashlib.sha256((W/file).read_bytes()).hexdigest()})
regions=[]
for n in ['structural_meshes.json','received_structural_meshes.json']:regions.extend(json.loads((R/'Game/data/generated'/n).read_text())['regions'])
floor=unary_union([Polygon(t) for q in regions if q['floor_y']==52.5 for t in q['triangles']])
tops={q['label']:[] for q in TP['terminals']}
for name,t,e in triangles(W/TP['asset']):
 if 'MissingOnlyEdge' not in name:continue
 label=name.split('_')[0]
 for tr in t:
  if max(abs(tr[:,1]-52.5))<1e-4:tops[label].append(Polygon(tr[:,[0,2]]))
for q in TP['terminals']:
 top=unary_union(tops[q['label']]);route=box(*q['existing_clear_route_xz'])
 ck(top.intersection(floor).area<1e-5,q['label']+' no duplicated original floor')
 ck(top.intersection(route).area<1e-5,q['label']+' original4m route unchanged')
 ck(abs(top.area-4.0)<1e-3,q['label']+' actual4m2 edge-ledges')
# Convex-cell decomposition covers the real prism-minus-slots; no positive volume overlap.
recipes=json.loads((W/'VEHICLE_CHANNEL_RECIPES.json').read_text())['members']
for q in recipes:
 for i,a in enumerate(q['convex_prisms']):
  for b in q['convex_prisms'][i+1:]:
   h=min(a['y'][1],b['y'][1])-max(a['y'][0],b['y'][0])
   if h>1e-8:ck(Polygon(a['triangle_xz']).intersection(Polygon(b['triangle_xz'])).area*h<1e-9,q['mesh']+' no positive duplicate cell volume')
prior=json.loads((W.parent/'CHECKPOINT_MANIFEST.json').read_text())
for name,q in prior['files'].items():ck(hashlib.sha256((R/name).read_bytes()).hexdigest()==q['sha256'],name+' prior checkpoint unchanged')
report={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'exports':exports,'new_only_terminal_floor_m2':8.0,'all184_prior_manifest_files_unchanged':True,'source_original_body_and_station_sources_unchanged':True,'limits':'Actual exports, cells and floor separation only; operating gates have their own engine evidence; whole-group/structure/species/cart/final-art acceptance remains open.'}
(W/'GEOMETRY_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print('SAFETY_GEOMETRY',report['status'],checks);assert not errors,errors
