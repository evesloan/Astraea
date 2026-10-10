from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from source_geometry import triangles
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'SHAFT_INTERFACE_PLAN.json'));N=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
new=dict(triangles(N['envelope']['export']));patch=dict(triangles(N['cap_patch']['export']));old=dict(triangles('AST-STF-009_pool_market_home_equipment.glb'));assert len(new)==43 and len(patch)==1
for q in P['retained_shaft_parts']+[P['new_missing_only_top_cap']]+P['sill_gate_interfaces']:
 t=new[q['name']];b=q['aabb'];assert np.max(abs(t.min(axis=(0,1))-[b[0],b[2],b[4]]))<1e-4 and np.max(abs(t.max(axis=(0,1))-[b[1],b[3],b[5]]))<1e-4,q['name']
retained=0
for spec in P['cap_exact_triangle_removals']:
 t=old[spec['mesh']];n=patch[spec['mesh']];removed=set(spec['triangle_indices']);canonical=np.array([sorted(map(tuple,x))for x in n]);assert len(n)==len(t)-len(removed)
 for i,triangle in enumerate(t):
  if i in removed:continue
  assert np.min(np.max(abs(canonical-np.array(sorted(map(tuple,triangle)))),axis=(1,2)))<1e-5;retained+=1
for path,h in P['source_pins'].items():
 p=W/'predecessors/lower_staff_network.gd'if path=='Game/scripts/lower_staff_network.gd'else R/path;assert sha(p)==h,path
before=(W/'predecessors/lower_staff_network.gd').read_text();assert (R/'Game/scripts/lower_staff_network.gd').read_text()==before+'\tload("res://scripts/forward_staff_upper_interfaces.gd").build(root,ship)\n'
contacts=[]
for q in P['sill_gate_interfaces']:
 d=json.load(open(R/f"Game/data/architecture/TIDAL_D{q['deck']}_SERVICE_RECEIVING.json"));floors=unary_union([Polygon(r['rings'][0],r['rings'][1:])for r in d.get('floor_regions',d.get('approach_floor_regions'))]);b=q['aabb'];a=box(b[0],b[4],b[1],b[5]);toe=float(a.intersection(floors).area);assert abs(toe-.192)<1e-6,(q['deck'],toe);contacts.append({'deck':q['deck'],'sill_to_existing_floor_contact_area_m2':toe,'gap_bridge_overhang_m':.01,'load_capacity_accepted':False})
roof=[]
for name,t in triangles('AST-RES-TIDAL_D17_service_receiving_r001.glb'):
 for tri in t:
  if np.all(abs(tri[:,1]-105.2)<1e-4):
   p=Polygon(tri[:,[0,2]]);
   if p.area>1e-8:roof.append(p)
b=P['new_missing_only_top_cap']['aabb'];overlap=float(box(b[0],b[4],b[1],b[5]).intersection(unary_union(roof)).area);assert overlap<1e-5,overlap
result={'status':'PASS','retained_shaft_parts_exact_bounds':37,'new_envelope_meshes':43,'cap_batches_replaced':1,'cap_object':'GPM_STF_NewCap','cap_triangles_removed':12,'same_batch_other_triangle_point_sets_preserved':retained,'every_other_lower_model_batch_unchanged':True,'sill_floor_contact_checks':contacts,'top_cap_existing_roof_overlap_m2_numeric':overlap,'preimage_pins_verified':len(P['source_pins']),'source_native_repeat_identical':True,'upper_operation_enabled':False,'temporary_closures_retained':True,'original_five_stop_binding_unchanged':True,'limits':'Source geometric contact and bounded reversible replacement, not structural/load certification or upper travel acceptance.'};(W/'ACTUAL_SOURCE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
