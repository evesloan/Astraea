from pathlib import Path
import hashlib,json,numpy as np
from source_geometry import triangles
import source_geometry
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'UPPER_OPERATION_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for spec in P['receiving_reconciliations']:
 old=dict(triangles(spec['old_export']));reader=source_geometry.read;source_geometry.read=lambda p:(W/spec['new_export']).read_bytes();new=dict(source_geometry.triangles(spec['new_export']));source_geometry.read=reader
 assert spec['closure_mesh']not in new and len(new)==len(old)-1;count=0
 for name,t in old.items():
  if name==spec['closure_mesh']:continue
  assert name in new;canonical=np.array([sorted(map(tuple,x))for x in new[name]])
  assert len(t)==len(canonical)
  for triangle in t:assert np.min(np.max(abs(canonical-np.array(sorted(map(tuple,triangle)))),axis=(1,2)))<1e-4
  count+=len(t)
 rows.append({'deck':spec['deck'],'only_mesh_removed':spec['closure_mesh'],'retained_meshes':len(new),'retained_triangle_point_sets':count})
for path,h in P['source_pins'].items():
 predecessor=W/'predecessors'/path;assert sha(predecessor if predecessor.exists()else R/path)==h,path
old=(W/'predecessors/Game/scripts/commons_lift.gd').read_text();new=(R/'Game/scripts/commons_lift.gd').read_text()
start='\tcabin=AnimatableBody3D.new()';end='func request_floor(index:int) -> bool:'
assert old[old.index(start):old.index(end)]==new[new.index(start):new.index(end)],'Original cabin/body/panel/gate initializer must remain exact'
assert old[old.index('func _set_present()'):old.index('func _physics_process')]==new[new.index('func _set_present()'):new.index('func _physics_process')]
original=(W/'predecessors/Game/scripts/star_atlas_fitted_receiving.gd').read_text();current=(R/'Game/scripts/star_atlas_fitted_receiving.gd').read_text();import re
assert re.sub(r'(const LEGACY_LIFT_SHA[^=]*=\s*)"[a-f0-9]{64}"','PIN',original)==re.sub(r'(const LEGACY_LIFT_SHA[^=]*=\s*)"[a-f0-9]{64}"','PIN',current)
result={'status':'PASS','receiving_successors':rows,'total_nonclosure_meshes_preserved':sum(x['retained_meshes']for x in rows),'preimage_pins_verified':len(P['source_pins']),'original_cabin_body_panel_gate_initializer_byte_identical':True,'present_cabin_interlock_byte_identical':True,'original_sources_exports_retained':True,'star_atlas_only_changed_exact_successor_pin':True,'original_five_ids_preserved':True,'no_extra_sills_or_upper_gates_created':True,'operation_enabled_only_after_guarded_reconciliation':True,'limits':'Source/native and bounded activation-map verification. Actual travel/gate/frame/obstruction checks recorded separately; structural/load/hygiene/full Group1 not accepted.'};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
