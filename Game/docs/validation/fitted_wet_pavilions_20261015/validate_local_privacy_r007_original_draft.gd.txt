extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"FITTED_CANDIDATE_OVERLAY_r007.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var ship:=Node3D.new();root.add_child(ship);var ss:=Node3D.new();ss.name="ShipSpace";ship.add_child(ss);var districts:=Node3D.new();districts.name="Districts";ss.add_child(districts)
 for spec in[["TidalGardenReceivingCandidate","AST-RES-TIDAL_lift_fit_r003.glb"],["QuietGroveReceivingCandidate","QUIET_GROVE_ARCHITECTURE_lift_r003.glb"]]:
  var site:=Node3D.new();site.name=spec[0];districts.add_child(site);var model:Node3D=(load("res://assets/models/"+spec[1])as PackedScene).instantiate();site.add_child(model)
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if mesh.get_meta("extras",{}).get("runtime_collision",false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for i in range(3):await physics_frame
 var group:=Node3D.new();group.name="LocalWet";ss.add_child(group);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"FITTED_CONFIG_r007.json"));load("res://scripts/fitted_wet_pavilions_20261015/roof_successor.gd").apply(ship,group,p.roofs)
 load("res://scripts/fitted_wet_pavilions_20261015/canopy_successor.gd").apply(ship,group,p.canopies)
 for row in p.models:
  var model:Node3D=(load("res://assets/fitted_wet_pavilions_20261015/"+str(row.file))as PackedScene).instantiate();model.name=row.kit;group.add_child(model);var contacts:Array[Node]=[]
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if not str(mesh.name).contains("Water_Illustrative"):contacts.append(mesh)
  load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 for i in range(3):await physics_frame
 var player:CharacterBody3D=load("res://scripts/player.gd").new();ship.add_child(player);var space:=ship.get_world_3d().direct_space_state;var suites:Array=[]
 var results:Array=[]
 for row in p.doors:
  var door:Node3D=load("res://scripts/group2_vip_pavilions/privacy_door.gd").new();door.name=str(row.kit)+"Privacy"+str(row.source_index);door.position=vec(row.at);door.rotation.y=float(row.yaw);door.persistent_id=StringName(str(row.persistent_id));group.add_child(door)
  var outward:Vector3=Vector3(0,0,1)if row.kit=="TIDAL"else Vector3(0,0,-1);var outside:Vector3=vec(row.at)+outward*1.8;var inside:Vector3=vec(row.at)-outward*1.3;player.global_position=outside+Vector3.UP*.03;player.velocity=Vector3.ZERO;await frames(20)
  var closed_before:bool=not door.desired_open and door.open_fraction==0;door.interact(player);await frames(100);var opened:bool=door.desired_open and door.open_fraction>.999
  var leg:Dictionary=await walk_to(player,inside);var back:Dictionary={}
  if leg.reached:back=await walk_to(player,outside)
  if back.get("reached",false):door.interact(player);await frames(100)
  results.append({"kit":row.kit,"index":row.source_index,"closed_before":closed_before,"opened":opened,"entered":leg,"returned":back,"closed_after":not door.desired_open and door.open_fraction==0})
 var suites:Array=[]
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
 var stances:Array=[]
 for point:Vector3 in[Vector3(-73.9,103.5,-360.8),Vector3(77.35,103.5,-375.6),Vector3(-91.7,102,-374.5),Vector3(-88.3,102,-374.5),Vector3(66.55,102,-363.1),Vector3(71.05,102,-363.1)]:stances.append({"at":str(point),"capsule_clear":capsule_clear(space,point)})
 var ok:bool=results.all(func(a):return a.closed_before and a.opened and a.entered.reached and a.returned.get("reached",false)and a.closed_after)
 FileAccess.open(D+"FITTED_LOCAL_PRIVACY_r007.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","privacy_door_routes":results,"stances":stances,"original_player_controller":true,"limited_context":true,"new_capacity_or_water_operation_admitted":false},"  "));print("PASS_FITTED_R007_PRIVACY_INVENTORY"if ok else"FAIL_FITTED_R007_PRIVACY_INVENTORY");quit(0 if ok else 1)
