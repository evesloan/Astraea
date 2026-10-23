from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
sources=['Game/scripts/group4_integrated_receiving.gd','Game/scripts/group4_boarding_safety.gd','Game/scripts/group4_cart_restraint.gd','Game/scripts/group4_tram_source_actuator.gd','Game/scripts/group4_loaded_tram_actuator.gd','Game/scripts/group4_tram_operating_controls.gd','Game/scripts/startup_residency_20261020/private_detail_residency.gd','Game/scripts/received_homes_20261015/residency.gd','Game/scripts/static_contact_cache.gd','Game/tests/validate_atrium_supports.gd','Game/data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json','Game/data/architecture/GROUP4_BOARDING_SAFETY_CANDIDATE.json']
rows=[]
for file in sources:
 b=(R/file).read_bytes();retained=subprocess.check_output(['git','show','47dbba2b8d57bf8b8a6e66a4af40c8974a3a16ca:'+file],cwd=R)
 assert b==retained,file
 rows.append({'path':file,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
text=(P/'route_profile.gd').read_text()
for forbidden in [r'\.global_position\s*=',r'\.global_transform\s*=',r'\.position\s*=',r'\.set_meta\(\s*"integration_',r'\.apply_pose\(',r'passenger\.set_physics_process\(',r'passenger\.set_controls_enabled\(']:assert not re.search(forbidden,text),forbidden
route=json.loads(re.search(r'const ROUTE := (\[[^\n]+\])',text)[1]);plan=json.loads((R/sources[-2]).read_text());stops={x['station']:x for x in plan['stops']}
assert len(stops)==len(plan['stops'])
for name in route:
 assert name in stops,name
 assert plan['safe_body_cursor_range_m'][0]<=stops[name]['distance_m']<=plan['safe_body_cursor_range_m'][1]
assert route==['AFT_MIDSHIP','CENTRAL','FORE_MIDSHIP','CENTRAL']
assert text.index('if int(safety.stationary_frames)<STATIONARY_FRAMES:return')<text.index('if not safety._physical_dock_matches("CENTRAL")')
assert not re.search(r'find_children\(',text),'No recurring whole-tree scan'
(P/'SOURCE_PINS.json').write_text(json.dumps({'protected_source_commit':'47dbba2b8d57bf8b8a6e66a4af40c8974a3a16ca','files':rows},indent=2)+'\n')
result={'source_check':'PASS','production_preimages_unchanged':len(rows),'route_targets_in_original_safe_range':len(route),'no_actor_car_pose_admission_or_physics_override':True,'stationary_witness_order':'existing safety15 frames before docking call','no_whole_tree_scan':True,'godot_protocol_parse':'PENDING_ENGINE_OWNER','actual_passenger_route':'HELD_BY_EXISTING_OPERATION_ADMISSION','physical_geometry_authored':False,'target_hardware_performance':'NOT_MEASURED'}
(P/'SOURCE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
