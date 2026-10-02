"""Whole wash assembly support-path audit, not a force/fastener/load calculation."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];ident='AST-MED-002';path=BASE/'source'/f'{ident}.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path));obs={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'and'material_role'in o};data={}
for name,o in obs.items():
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices)for t in me.loop_triangles];data[name]={'tree':BVHTree.FromPolygons(v,f,all_triangles=True),'samples':v+[sum((v[i]for i in ids),Vector())/3 for ids in f]};ev.to_mesh_clear()
paths={}
for side in('left','right'):
 paths[side+'_floor_isolation_shoe']=[];paths[side+'_swept_basin_support_cheek']=[side+'_floor_isolation_shoe']
paths.update({
'rear_service_bearing_wall':['left_swept_basin_support_cheek','right_swept_basin_support_cheek'],
'lower_service_and_supply_floor':['left_swept_basin_support_cheek','right_swept_basin_support_cheek'],
'basin_service_supply_divider':['lower_service_and_supply_floor'],
'continuous_shaped_basin_and_dry_work_rim':['left_swept_basin_support_cheek','right_swept_basin_support_cheek','rear_service_bearing_wall'],
'front_removable_service_cover':['lower_service_cover_receiver','upper_service_cover_receiver'],
'lower_service_cover_receiver':['left_swept_basin_support_cheek','basin_service_supply_divider'],
'upper_service_cover_receiver':['left_swept_basin_support_cheek','basin_service_supply_divider'],
'service_cover_recess_grip':['front_removable_service_cover'],
'service_cover_semantics':['front_removable_service_cover'],
'lower_clean_supply_shelf':['basin_service_supply_divider','right_swept_basin_support_cheek'],
'clean_supply_inner_tower_cheek':['continuous_shaped_basin_and_dry_work_rim'],
'clean_supply_outer_tower_cheek':['continuous_shaped_basin_and_dry_work_rim'],
'clean_supply_tower_back':['clean_supply_inner_tower_cheek','clean_supply_outer_tower_cheek'],
'clean_supply_lower_shelf':['clean_supply_inner_tower_cheek','clean_supply_outer_tower_cheek','clean_supply_tower_back'],
'clean_supply_middle_shelf':['clean_supply_inner_tower_cheek','clean_supply_outer_tower_cheek','clean_supply_tower_back'],
'clean_supply_shelter_cap':['clean_supply_inner_tower_cheek','clean_supply_outer_tower_cheek','clean_supply_tower_back'],
'clean_supply_label_band':['clean_supply_inner_tower_cheek','clean_supply_outer_tower_cheek'],
'clean_supply_semantics':['clean_supply_label_band'],
'tap_deck_mount':['continuous_shaped_basin_and_dry_work_rim'],
'tap_vertical_stem':['tap_deck_mount'],
'tap_forward_elbow':['tap_vertical_stem'],
'tap_closed_outlet_cap':['tap_forward_elbow'],
'basin_closed_drain_cap':['continuous_shaped_basin_and_dry_work_rim']})
for n in obs:
 if n.startswith('service_cover_retainer_'):paths[n]=['front_removable_service_cover']
for what in('water','control'):
 paths[what+'_control_mount']=['continuous_shaped_basin_and_dry_work_rim'];paths[what+'_inactive_paddle']=[what+'_control_mount']
for what in('water_supply','drain','control'):
 paths[what+'_rear_collar']=['rear_service_bearing_wall'];paths[what+'_rear_blank_cap']=[what+'_rear_collar']
assert set(paths)==set(obs),(set(obs)-set(paths),set(paths)-set(obs))
results=[]
for child,parents in paths.items():
 for parent in parents:
  a,b=data[child],data[parent];cross=len(a['tree'].overlap(b['tree']));best=1e10;wp=None
  for first,second in[(a,b),(b,a)]:
   for p in first['samples']:
    h=second['tree'].find_nearest(p)
    if h[3]<best:best=h[3];wp={'sample':list(p),'nearest_surface':list(h[0]),'nearest_normal':list(h[1])}
  results.append({'part':child,'supported_by':parent,'nearest_sample_surface_distance_m':best,'surface_intersection_pairs':cross,'witness':wp,'passed':best<.00003 or cross>0,'interpretation':'Geometric boundary bearing or intentional joined solid. Not a load, fastener, weld, cleaning or mechanical-certification claim.'})
roots=['left_floor_isolation_shoe','right_floor_isolation_shoe']
def reaches(n,seen=None):
 if n in roots:return True
 seen=set()if seen is None else seen
 if n in seen:return False
 return any(reaches(p,seen|{n})for p in paths[n])
report={'catalogue_id':ident,'source_sha256':before,'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'coverage':'Every named semantic mesh including all controls, caps, covers, shelves, labels and retainers has a declared support chain to the two floor contact shoes','paths':paths,'pair_checks':results,'all_parts_reach_floor_shoe':all(reaches(n)for n in obs),'source_unchanged':before==sha(path),'scope':'Assembly adjacency/support-path geometry only. End caps and cover receivers are joined static visual parts; no forces, actual removal, tools, fastening or load performance simulated.','passed':all(r['passed']for r in results)and all(reaches(n)for n in obs)and before==sha(path)}
(BASE/'qa/wash_assembly_support_paths.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'failures':[r for r in results if not r['passed']]},indent=2))
