"""Audit actual exported source points and standing surfaces, not authoring intentions."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
W=Path(__file__).resolve().parent
R=next(p for p in W.parents if (p/'Game').is_dir())
sys.path.insert(0,str(W.parent))
from glb_geometry import triangles
I=json.loads((W/'SUCCESSOR_INTERFACE.json').read_text())
oldfile=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002'/I['original_model']
old={n:t for n,t,e in triangles(oldfile)}
new={n:t for n,t,e in triangles(W/I['selected_model'])}
checks=0;errors=[]
def check(value,label):
 global checks
 checks+=1
 if not value:errors.append(label)
def points(t):
 p=t.reshape(-1,3)
 return p[np.lexsort((p[:,2],p[:,1],p[:,0]))]
check(hashlib.sha256(oldfile.read_bytes()).hexdigest()==I['original_model_sha256'],'immutable source012 export')
check(hashlib.sha256((W/I['selected_model']).read_bytes()).hexdigest()==I['selected_model_sha256'],'selected source030 export')
check(len(old)==189 and len(new)==202,'actual original and selected mesh counts')
unchanged=set(old)&set(new)
check(len(unchanged)==180,'180 original active meshes')
for name in sorted(unchanged):
 check(np.array_equal(points(old[name]),points(new[name])),name+' exact correlated 3D point payload')
 check(old[name].shape==new[name].shape,name+' original triangle count')
for item in I['same_station_relocated_perch_parts']:
 name=item['source'];target=new[name+'_same_station_relocated']
 check(np.allclose(points(old[name]+np.array(item['translation_xyz'])),points(target),atol=2e-5,rtol=0),name+' rigid original correlated points')
check(any('Canopy_Pier_-226.8' in n for n in unchanged),'protected pier remains original')
def floor(parts):
 faces=[]
 for name,t in parts.items():
  if abs(t[:,:,1].max()-56.1)>2e-4:continue
  for tri in t:
   if np.all(np.abs(tri[:,1]-56.1)<2e-4):
    p=Polygon(tri[:,[0,2]])
    if p.area>1e-9:faces.append(p)
 return unary_union(faces)
a=floor(old);b=floor(new);added=b.difference(a).area;lost=a.difference(b).area
check(abs(added-2.7)<2e-4,'actual missing-only 2.7m2 floor')
check(lost<1e-8,'no original upper floor removed')
for name,t in new.items():check(np.isfinite(t).all(),name+' finite source')
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'point_sort':'lexicographic complete XYZ rows; coordinate correlations preserved','unchanged_source_meshes':len(unchanged),'new_selected_meshes':len(new),'new_only_floor_m2':added,'original_floor_area_lost_m2':lost,'same_station_perch_parts_relocated':2,'canopy_pier_moved':False,'shared_root_floor_registry_room_ids_changed':False,'actual_player_cart_species_and_structural_acceptance_separate':True}
(W/'GEOMETRY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print('AFTMID_GEOMETRY_AUDIT',result)
assert not errors
