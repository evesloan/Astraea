extends "res://tests/group6_completion/validate_thermal_targets.gd"
func run()->void:
 var host:=LocalHost.new();root.add_child(host)
 var floor_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"));var regions:Array=[]
 for r in floor_data.regions:
  if str(r.id).begins_with("D08_directory_02_") or str(r.id).begins_with("D08_directory_03_"):regions.append(r)
 load("res://scripts/structural_floor_builder.gd").build_regions(host,host.stone,host.ivory,regions,{},"RetainedThermalFloors")
 var actor:CharacterBody3D=load("res://scripts/group6_swimming_20261019/player.gd").new();host.add_child(actor)
 var contract:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"))
 for spec in contract.rooms:
  var room:Node3D=load("res://"+str(spec.current_room_runtime).trim_prefix("Game/")).instantiate();room.name=str(spec.programme_key);room.set_meta("programme_key",str(spec.programme_key));host.add_child(room)
  for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
  load("res://scripts/group6_completion/thermal_entries.gd").build(room)
  load("res://scripts/group6_completion/thermal_support.gd").build(room)
  load("res://scripts/group6_completion/thermal_recovery.gd").build(room,false)
  if spec.programme_key=="D08_directory_02":load("res://scripts/group6_completion/tidal_north_room.gd").build(room)
  for entry in spec.entries:
   actor.global_position=vec(entry.dry_xyz)+Vector3.UP*.03;actor.velocity=Vector3.ZERO
   for i in range(20):await physics_frame
   record(str(entry.id)+"_dry",actor.water_state=="dry" and not actor.swimming)
   var into:Dictionary=await walk_to(actor,vec(entry.bed_xyz));record(str(entry.id)+"_walk_into_water",into.reached and into.floor_contact)
   record(str(entry.id)+"_wading_exact_volume",actor.water_state=="wading" and not actor.swimming and actor.water_volume_id==str(entry.id))
   var out:Dictionary=await walk_to(actor,vec(entry.dry_xyz));record(str(entry.id)+"_walk_out_dry",out.reached and out.floor_contact and actor.water_state=="dry")
 var field:RefCounted=actor.water_field
 record("mineral_water_corner_excluded",not field.sample(Vector3(-42.8,44.5,-239.8)).get("wet",false))
 record("river_island_excluded",not field.sample(Vector3(78,44.5,216)).get("wet",false))
 record("upper_deck_not_wet",not field.sample(Vector3(-31,52.5,-432)).get("wet",false))
 record("below_basin_not_wet",not field.sample(Vector3(-31,44,-432)).get("wet",false))
 for at in [Vector3(81.5,44.5,211.5),Vector3(81.5,44.5,223.5)]:record("source_spa_"+str(at),field.sample(at).get("wet",false))
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors}
 FileAccess.open("res://docs/validation/group6_swimming_20261019/TRANSITIONS.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print("WATER TRANSITIONS ",result.status," ",errors);quit(0 if errors.is_empty() else 1)
