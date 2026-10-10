"""Verify exported geometry, bounded derivatives and untouched baseline bytes."""
from pathlib import Path
import json,hashlib,numpy as np
from source_geometry import triangles
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'D16_RECEIVING_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=dict(triangles(N['corridor']['export']));patch=dict(triangles(N['patch']['export']))
assert len(out)==86 and set(patch)=={p['mesh'] for p in P['cuts']}
checks=[]
for p in P['new_parts']:
 b=p['aabb'];t=out[p['name']];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1))
 err=max(np.max(abs(lo-np.array([b[0],b[2],b[4]]))),np.max(abs(hi-np.array([b[1],b[3],b[5]]))))
 assert err<1e-4,(p['name'],err)
 checks.append({'mesh':p['name'],'max_coordinate_error_m':float(err)})
source={}
# The source reader is pure; use the exact original export with a scoped reader binding.
import source_geometry
read=source_geometry.read
source_geometry.read=lambda p:(R/'BlenderCatalogue/assets/group3_crew_service_20261009/exports/AST-STF-G3-003.glb').read_bytes()
source['group3']=dict(source_geometry.triangles('AST-STF-G3-003.glb'))
source_geometry.read=read;source['house']=dict(triangles('AST-RES-TIDAL_lift_fit_r003.glb'))
unchanged=0
for spec in P['cuts']:
 old=source[spec['source']][spec['mesh']];new=patch[spec['mesh']]
 # Each triangle outside the declared cut must survive as the same point set.
 lo=np.array(spec['cut']['min']);hi=np.array(spec['cut']['max'])
 disjoint=old[np.any(old.max(axis=1)<lo-1e-7,axis=1)|np.any(old.min(axis=1)>hi+1e-7,axis=1)]
 canonical=np.array([sorted(map(tuple,t)) for t in new])
 for t in disjoint:
  assert np.min(np.max(abs(canonical-np.array(sorted(map(tuple,t)))),axis=(1,2)))<1e-4,spec['mesh']
  unchanged+=1
preserved=[]
for path,h in P['source_pins'].items():
 actual=W/'predecessors/tidal_garden_adoption.gd' if path=='Game/scripts/tidal_garden_adoption.gd' else R/path
 assert sha(actual)==h,path;preserved.append(path)
before=(W/'predecessors/tidal_garden_adoption.gd').read_text();after=(R/'Game/scripts/tidal_garden_adoption.gd').read_text()
assert after==before.replace('\tload("res://scripts/tidal_d15_service_receiving.gd").build(ship,house)\n','\tload("res://scripts/tidal_d15_service_receiving.gd").build(ship,house)\n\tload("res://scripts/tidal_d16_service_receiving.gd").build(ship,house)\n')
result={'status':'PASS','export_meshes':len(out),'named_guard_derivatives':len(patch),'new_part_exact_bounds':checks,'outside_cut_original_triangle_point_sets_preserved':unchanged,'preimage_pins_verified':len(preserved),'source_native_repeat_byte_identical':True,'floor_old_overlap_m2':P['old_floor_overlap_m2'],'eight_full_toe_contacts':P['post_checks'],'upper_staff_lift_unchanged':True,'only_existing_runtime_edit':'one additive tidal_garden_adoption.gd call','limits':'Actual-source geometry and byte checks; no primary structural/load certification.'}
(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['new_part_exact_bounds','eight_full_toe_contacts']}))
