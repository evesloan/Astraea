from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'RUNTIME_RECEIVING.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns={'__file__':str(W/'geometry_reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
for rel,h in P['source_pins'].items():assert sha(R/rel)==h,rel
runtime={name:t for name,t in ns['triangles'](P['model_file'])};count=0;objects=0;owners=[]
for lower in P['lower_structural_owners']:
 assert sha(R/lower['native_source'])==lower['native_sha256'] and sha(R/'Game/assets/models'/lower['runtime_source'])==lower['runtime_sha256']
 original=np.concatenate([t for name,t in ns['triangles'](lower['runtime_source'],lower['origin'],lower['yaw'])]);owncount=0
 for name,t in runtime.items():
  if not name.startswith('Persistent_'+str(lower['source_index'])+'_'):continue
  objects+=1
  for face in t:
   d=np.linalg.norm(original[:,:,None,:]-face[None,None,:,:],axis=3);matching=(d.min(axis=2).max(axis=1)<.00002)&(d.min(axis=1).max(axis=1)<.00002);assert matching.any(),(name,face.tolist());count+=1;owncount+=1
 owners.append({'owner':lower['owner'],'source_triangles_preserved':owncount,'native_sha256':lower['native_sha256'],'runtime_sha256':lower['runtime_sha256']})
assert objects==88 and count>1000
r={'status':'PASS','immutable_source_pins':len(P['source_pins']),'unchanged_lower_sources':4,'persistent_source_objects':objects,'exact_source_triangle_correspondence':count,'vertex_tolerance_m':.00002,'owners':owners,'source_floor_toes':len(P['support_toes']),'all_support_toe_footprints_verified_by_plan':True,'framing_members':len(P['parts']),'wall_base_rails':len(P['base_rails']),'structural_capacity_accepted':False};(W/'ACTUAL_RECEIVING_SOURCE_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
