"""Exact aperture feet after removing wall-owned faces from physical-floor evidence."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import shapely
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();write=lambda f,q:f.write_text(json.dumps(q,indent=2)+'\n')
p=json.load(open(HERE/'source/CROSSING_PREIMAGES_AND_CONTRACT.json'));pins={q['input_path']:q['sha256']for q in p['source_files'].values()}
regions=[]
for path in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/REMAINING_BATCH_FLOORS.json']:
 regions+=json.load(open(HERE/'inputs'/path))['regions']
current=unary_union([Polygon(t)for q in regions if q['deck']=='D03'for t in q['triangles']])
f=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009/extensions/d03_remaining_streets_physical_batch023/source/RETAINED_PHYSICAL_FLOOR_SURVEY.json';pins[str(f.relative_to(ROOT))]=sha(f);physical=json.load(open(f));wall_names={q['runtime_name']for q in p['preimage_meshes']};kept=[];excluded=[]
for owner in physical['owners']:
 if any('/'+n+'/'in owner['collider']for n in wall_names):excluded.append(owner);continue
 kept.extend(Polygon(t)for t in owner['triangles'])
physical_floor=unary_union(kept);old_g3=[]
for folder,file in [('d03_remaining_receivers_batch013','MISSING_ONLY_FLOOR_PATCH.json'),('labelled_crew_bank_batch014','BANK_MISSING_ONLY_FLOOR.json'),('d03_service_receivers_physical_batch021','D03_SERVICE_MISSING_FLOOR.json'),('d03_port2_live_connection_batch022','D03_PORT2_MISSING_FLOOR.json'),('d03_remaining_streets_physical_batch023','REMAINING_STREET_MISSING_FLOOR.json')]:
 f=HERE.parent/folder/'source'/file;pins[str(f.relative_to(ROOT))]=sha(f)
 for q in json.load(open(f))['parts']:
  y=q['y']if'y'in q else q['aabb'][2:4]
  if y[1]!=12:continue
  a=q.get('aabb');old_g3.append(Polygon(q['boundary'],q['holes'])if'boundary'in q else box(a[0],a[4],a[1],a[5]))
prior_floor=unary_union(old_g3);existing=current.union(physical_floor).union(prior_floor)
requests=[];witnesses=[]
for q in p['door_bindings']:
 x,y,z=q['position'];r=box(x-1.38001,z-.24001,x+1.38001,z+.24001);requests.append(r);gap=r.difference(existing);witnesses.append(dict(name=q['name'],requested_footprint_xz=list(r.exterior.coords)[:-1],missing_area_m2=gap.area,retained_supported_area_m2=r.intersection(existing).area))
missing=unary_union(requests).difference(existing);parts=[]
for i,g in enumerate(shapely.get_parts(shapely.set_precision(missing,grid_size=.000001))):
 if g.geom_type!='Polygon'or g.area<1e-10:continue
 parts.append(dict(name='CrossingMissingThreshold_'+str(i),boundary=list(g.exterior.coords)[:-1],holes=[list(r.coords)[:-1]for r in g.interiors],triangles=[list(t.exterior.coords)[:3]for t in shapely.constrained_delaunay_triangles(g).geoms],y=[11.76,12],role='staff_floor',category='floor',batch_cell='six_crossings'))
assert missing.intersection(existing.buffer(-.001)).area<1e-8
base=dict(schema=1,family='group3_crew_service_20261009',material_contract='retained_lower_staff_network',source_pins=pins,catalogue_id='AST-STF-G3-063',parts=parts,fixtures=[],new_floor_m2=missing.area,existing_or_prior_floor_overlay_m2=0,original_wall_owned_faces_excluded_from_support=True,physical_snapshot_is_staged_prior_source_not_current_installed_Group3=True,current_integrator_floor_recheck_required=True,structural_or_capacity_acceptance=False)
write(HERE/'source/CROSSING_MISSING_THRESHOLDS.json',base)
q=dict(status='PASS_SOURCE_THRESHOLD_PLAN_NOT_INSTALLED',current_integration_commit=p['integration_source_commit'],wall_owned_floor_faces_excluded=[dict(collider=q['collider'],triangles=len(q['triangles']))for q in excluded],aperture_witnesses=witnesses,new_threshold_floor_m2=missing.area,zero_source_floor_overlay=True,source_pins=pins,original_13_criteria_preserved=True,actual_combined_walk_ray_or_floor_capacity_acceptance=False)
write(HERE/'qa/THRESHOLD_SOURCE_RECONCILIATION.json',q);print(json.dumps({k:q[k]for k in['status','wall_owned_floor_faces_excluded','aperture_witnesses','new_threshold_floor_m2']}))
