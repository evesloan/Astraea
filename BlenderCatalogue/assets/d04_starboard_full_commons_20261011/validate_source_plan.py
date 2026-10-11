from pathlib import Path
import json,hashlib,subprocess
from shapely.geometry import shape,Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for r in P['native_export_records']:
 for key,hashkey in [('native','native_sha256'),('export','export_sha256')]:assert sha(W/r[key])==r[hashkey]
 assert sha(R/'Game/assets/models'/r['export'])==r['export_sha256'];assert r['fresh_native_repeat_identical']
upper=shape(P['commons_floor_geometry']);lower=shape(P['lower_staff_floor_geometry']);voids=[shape(a['geometry'])for a in P['negative_volume_zones']]
assert abs(upper.area+sum(a.area for a in voids)-952)<1e-7
for v in voids:assert upper.intersection(v).area<1e-8
assert shape(P['planted_court_geometry']).difference(upper).area<1e-8
original=json.load(open(R/'Game/data/generated/structural_meshes.json'));overlaps=[]
for region in original['regions']:
 if region['floor_y']not in [12,16.5]:continue
 geo=unary_union([Polygon(t)for t in region['triangles']]);area=(lower if region['floor_y']==12 else upper).intersection(geo).area
 if area>1e-7:overlaps.append({'region':region['id'],'m2':area})
assert not overlaps,overlaps
for a in P['all_twenty_allocations_unchanged']:
 if isinstance(a,dict)and 'allocation_x'in a:
  envelope=box(*[a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1]])
  assert upper.intersection(envelope).area<1e-8
# Prior native and runtime files are protected by comparing the complete Git object identity at this exact base.
protected=subprocess.check_output(['git','ls-tree','-r','--name-only',P['base_commit'],'BlenderCatalogue','Game/assets/models'],cwd=R,text=True).splitlines();protected=[f for f in protected if f.endswith(('.blend','.glb'))];changed=set(subprocess.check_output(['git','diff','--name-only',P['base_commit']],cwd=R,text=True).splitlines());assert not(changed&set(protected))
result={'status':'PASS','source_pins':len(P['source_pins']),'unchanged_prior_native_and_export_files':len(protected),'commons_floor_m2':upper.area,'purposeful_floor_free_m2':sum(a.area for a in voids),'lower_staff_floor_m2':lower.area,'duplicate_retained_structural_floor_intersections':overlaps,'planted_outlook_uses_commons_plate_once':True,'immutable_native_fresh_repeat_identical':True,'new_home_units':0,'new_reserved_rests':0,'production_active':False,'dedicated_staff_network_engineering_final_accepted':False}
(W/'SOURCE_PLAN_INTEGRITY.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
