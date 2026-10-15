extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"FITTED_CANDIDATE_OVERLAY_r010.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
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
 # Exact original loose-model instances in the bounded pavilion context.
 var placed_assets:Array=[]
 for spec in[["TIDAL","TIDAL_GARDEN_RECEIVING_CANDIDATE.json"],["QUIET","QUIET_GROVE_RECEIVING.json"]]:
  var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/"+spec[1]));var scene_cache:Dictionary={}
  for item in definition.retained_asset_instances:
   var xyz:Array=item.world_xyz
   if float(xyz[2])< -386 or float(xyz[2])> -354 or absf(float(xyz[0]))<63 or absf(float(xyz[0]))>98:continue
   var asset:Dictionary=definition.retained_asset_definitions[str(item.catalogue_id)];var path:String="res://assets/models/"+str(asset.model_file);assert(FileAccess.get_sha256(path)==str(asset.sha256))
   if not scene_cache.has(path):scene_cache[path]=load(path)
   var placed:=Node3D.new();placed.name=str(item.name);placed.position=vec(xyz);placed.rotation.y=deg_to_rad(float(item.yaw));placed.scale=Vector3.ONE*float(item.scale);ship.add_child(placed);var visual:Node3D=(scene_cache[path]as PackedScene).instantiate();placed.add_child(visual)
   if not str(item.catalogue_id).begins_with("AST-BOT"):
    for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
   placed_assets.append(placed)
 var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"FITTED_CONFIG_r010.json"))
 for row in config.loose_furniture_moves:
  var node:Node3D=ship.find_child(str(row.name),true,false);assert(node!=null and node.position.distance_to(vec(row.preimage_xyz))<.001);node.position=vec(row.target_xyz)
  for body:CollisionObject3D in node.find_children("*","CollisionObject3D",true,false):body.force_update_transform()
 var group:=Node3D.new();group.name="LocalWet";ss.add_child(group);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"FITTED_CONFIG_r010.json"));load("res://scripts/fitted_wet_pavilions_20261015/roof_successor.gd").apply(ship,group,p.roofs)
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
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
 var stances:Array=[]
 for point:Vector3 in[Vector3(-73.9,103.5,-360.8),Vector3(77.35,103.5,-375.6),Vector3(-91.7,102,-374.5),Vector3(-88.3,102,-374.5),Vector3(66.55,102,-363.1),Vector3(71.05,102,-363.1)]:stances.append({"at":str(point),"capsule_clear":capsule_clear(space,point)})
 var rest_approaches:Array=[]
 for kit in["TIDAL","QUIET"]:
  for i in range(6):
   var chair:MeshInstance3D=group.find_child("F010__G2VIP_"+kit+"_Rest"+str(i)+"_Seat",true,false);assert(chair!=null);var b:AABB=chair.global_transform*chair.get_aabb();var at:=b.get_center();at.y=103.5 if kit=="TIDAL"else 102.;at.x+=1.15 if kit=="TIDAL"or i%2==0 else -1.15;rest_approaches.append({"kit":kit,"chair":i,"at":str(at),"capsule_clear":capsule_clear(space,at)})
 var moved_floor_pins:Array=[]
 var all_excludes:Array[RID]=[]
 for asset:Node3D in placed_assets:
  for body:CollisionObject3D in asset.find_children("*","CollisionObject3D",true,false):all_excludes.append(body.get_rid())
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):all_excludes.append(body.get_rid())
 for row in config.loose_furniture_moves:
  var point:=vec(row.target_xyz);var q:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.02,point-Vector3.UP*.02);q.exclude=all_excludes;var h:=space.intersect_ray(q);moved_floor_pins.append({"name":row.name,"floor":str(h.collider.get_path())if not h.is_empty()else"","supported":not h.is_empty()and absf(h.position.y-102)<.002})
 var group_contacts:Array=[]
 for key in["D17_QuietReading_1","D17_QuietReading_2","D17_SharedTable_1"]:
  var item:Node3D=ship.find_child(key,true,false);var excluded:Array[RID]=[]
  for body:CollisionObject3D in item.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
  for mesh:MeshInstance3D in item.find_children("*","MeshInstance3D",true,false):
   var q:=PhysicsShapeQueryParameters3D.new();q.shape=mesh.mesh.create_convex_shape(true,false);q.shape.margin=0.;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excluded
   for hit in space.intersect_shape(q,128):
    var parent:Node=hit.collider.get_parent()
    if parent.get_meta("extras",{}).get("category","")!="floor":group_contacts.append({"item":key,"mesh":str(mesh.name),"hit":str(hit.collider.get_path())})
 var ok:bool=group_contacts.is_empty()and moved_floor_pins.all(func(a):return a.supported)and rest_approaches.all(func(a):return a.capsule_clear)and results.all(func(a):return a.closed_before and a.opened and a.entered.reached and a.returned.get("reached",false)and a.closed_after)
 FileAccess.open(D+"FITTED_LOCAL_FUNCTION_r010.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","privacy_door_routes":results,"rest_approaches":rest_approaches,"moved_floor_pins":moved_floor_pins,"reading_group_contacts":group_contacts,"retained_loose_context_instances":placed_assets.size(),"stances":stances,"original_player_controller":true,"limited_context":true,"new_capacity_or_water_operation_admitted":false},"  "));print("PASS_FITTED_R010_PRIVACY_INVENTORY"if ok else"FAIL_FITTED_R010_PRIVACY_INVENTORY");quit(0 if ok else 1)
