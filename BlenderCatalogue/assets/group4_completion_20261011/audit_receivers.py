from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from glb_geometry import triangles
W=Path(__file__).resolve().parent;R=W.parents[2]
p=json.loads((W/'RECEIVING_PLAN.json').read_text());recipe={q['mesh']:q for q in json.loads((W/'MESH_PARTS.json').read_text())}
errors=[];checks=0;actual={};ntri=0
def ck(v,why):
 global checks
 checks+=1
 if not v:errors.append(why)
for name,t,extras in triangles(W/'AST-TRM-G4-023_station_receiving_r002.glb'):
 ck(np.isfinite(t).all(),name+' finite triangles')
 ck(bool((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-9).all()),name+' nondegenerate triangles')
 ck(name in recipe,name+' recipe identity')
 ck(np.allclose(t.min(axis=(0,1)),recipe[name]['min'],atol=1e-4),name+' actual minimum bounds')
 ck(np.allclose(t.max(axis=(0,1)),recipe[name]['max'],atol=1e-4),name+' actual maximum bounds')
 actual[name]=t;ntri+=len(t)
regions=[]
for n in ['structural_meshes.json','received_structural_meshes.json']:
 regions.extend(json.loads((R/'Game/data/generated'/n).read_text())['regions'])
floor=unary_union([Polygon(t) for q in regions if q['floor_y']==52.5 for t in q['triangles']])
floors=[];witnesses=[]
for st in p['stations']:
 if 'floor_triangles_xz' not in st:continue
 top=[]
 for name,t in actual.items():
  if name.startswith(st['label']+'_MissingFloor_'):
   for tr in t:
    if np.max(abs(tr[:,1]-52.5))<1e-4:top.append(Polygon(tr[:,[0,2]]))
 shape=unary_union(top);pit=box(*st['lower_lift_recess_xz'])
 ck(shape.intersection(floor).area<1e-4,st['label']+' no duplicated original floor')
 ck(shape.intersection(pit).area<1e-4,st['label']+' unchanged pit aperture')
 ck(abs(shape.area-st['missing_only_floor_m2'])<1e-3,st['label']+' exact actual exported floor area')
 floors.append({'station':st['label'],'actual_exported_floor_m2':shape.area,'original_overlap_m2':shape.intersection(floor).area,'pit_overlap_m2':shape.intersection(pit).area})
 # Actual tongue intersects original-script sill and retained/new landing edge.
 name=st['label']+'_LowerSillTongue';t=actual[name];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 sign=1 if st['lift_yaw_rad']>0 else -1;z=st['lift_root'][2]
 sill=sorted([z+sign*.010,z+sign*.100]);front=z+sign*.2
 ck(min(hi[2],sill[1])-max(lo[2],sill[0])>.019,st['label']+' 20mm fixed sill lap')
 ck(lo[2]<front<hi[2],st['label']+' tongue laps exact front aperture edge')
 ck(abs(hi[1]-52.501)<1e-4,st['label']+' 1mm threshold step')
 witnesses.append({'station':st['label'],'exported_tongue_min':lo.tolist(),'max':hi.tolist(),'script_sill_z':sill,'pit_front_z':front})
for name,t in actual.items():
 if 'LapLedger' not in name:continue
 lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));fp=box(lo[0],lo[2],hi[0],hi[2])
 ck(fp.intersection(floor).area>.05,name+' positive retained slab bearing')
 ck(52.26<lo[1]<hi[1]<52.5,name+' floor-depth receiving without lower columns')
 ck(not (lo[0]<2 and hi[0]>-2 and hi[1]>52.5),name+' protected pedestrian axis')
for cut in p['required_shared_floor_cuts']:
 ck(not box(*cut['bounds_xz']).intersects(box(-2,-530,2,530)),cut['station']+' pit outside four-metre pedestrian axis')
old=json.loads((W/'ORIGINAL_NATIVE_EXPORT_PINS.json').read_text())
for name,h in old.items():ck(hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name+' immutable original')
report={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'actual_export_meshes':len(actual),'triangles':ntri,'floor_areas':floors,'sill_receiving':witnesses,'retained_native_export_files':len(old),'shared_floor_cuts_unapplied':p['required_shared_floor_cuts'],'limits':'Additive source floor and lap contacts only. No load capacity, destination/main-world integration, live tram, species or final visual acceptance.'}
(W/'ACTUAL_RECEIVING_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],checks,'checks;',ntri,'triangles;',len(old),'immutable originals');assert not errors,errors
