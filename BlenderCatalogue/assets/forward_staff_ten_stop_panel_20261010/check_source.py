from pathlib import Path
import json,hashlib,struct,numpy as np
from source_geometry import triangles
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'INTERFACE_SURVEY.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=dict(triangles('AST-CIR-003_five_stop.glb'));new=dict(triangles('AST-CIR-003_ten_stop.glb'));retained=0
allnew=np.array([sorted(map(tuple,x))for t in new.values()for x in t])
for name,t in old.items():
 for triangle in t:
  lo=triangle.min(axis=0);hi=triangle.max(axis=0)
  inside=np.all(lo>=np.array([1.75,1.1,-1.72])-1e-5)and np.all(hi<=np.array([1.88,1.56,-.32])+1e-5)
  if inside:continue
  assert np.min(np.max(abs(allnew-np.array(sorted(map(tuple,triangle)))),axis=(1,2)))<1e-5,name
  retained+=1
panel=new['CAB_TenStopControlPanel'];assert np.max(abs(panel.min(axis=(0,1))-[1.75,1.1,-1.72]))<1e-5;assert np.max(abs(panel.max(axis=(0,1))-[1.88,1.9,-.32]))<1e-5
for path,h in P['source_pins'].items():
 q=W/'predecessors'/Path(path).name if path in ['Game/scripts/commons_lift.gd','Game/scripts/star_atlas_fitted_receiving.gd']else R/path
 assert sha(q)==h,path
assert sha(R/'Game/assets/models/AST-CIR-003_ten_stop.glb')==N['export_sha256']
def nodes(file):
 b=(R/'Game/assets/models'/file).read_bytes();d=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);return {n['name']:n.get('translation',[0,0,0])for n in d['nodes']if'mesh'not in n}
o=nodes('AST-CIR-003_five_stop.glb');n=nodes('AST-CIR-003_ten_stop.glb')
assert len([k for k in n if k.startswith('DATUM_floor_button_')])==10
for i in range(5):assert n['DATUM_floor_button_'+str(i)]==o['DATUM_floor_button_'+str(i)]
for i in range(5):assert np.max(abs(np.array(n['DATUM_floor_button_'+str(i+5)])-[1.73,1.73,-(.46+.28*i)]))<1e-5
candidates=[]
for name,t in triangles('AST-STF-009_pool_market_home_equipment.glb'):
 lo=t.min(axis=1);hi=t.max(axis=1);mask=(lo[:,1]>=55.5999)&(hi[:,1]<=55.7401)&(hi[:,0]>=-27.12)&(lo[:,0]<=-22.84)&(hi[:,2]>=-492.2)&(lo[:,2]<=-487.8)
 if mask.any():candidates.append({'batch':name,'triangles_aabb_intersecting_cap_region':int(mask.sum())})
result={'status':'PASS','original_export_triangle_point_sets_unchanged':retained,'original_native_meshes_unchanged':N['unchanged_native_meshes'],'original_five_marker_positions_unchanged':True,'new_markers':5,'backing_native_bounds_matched':True,'preimage_pins_verified':len(P['source_pins']),'cap_region_candidate_map':candidates,'cap_map_scope':'Spatial AABB candidates only; exact source clipping/deletion map still blocked; no geometry changed','upper_operation_enabled':False,'original_five_stop_binding_unchanged':True}
(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
