extends "res://tests/group3_fore_starboard_clinical_20261011/validate_fore.gd"
var probe_count:=0
var setups:=0
func moving_doors()->void:
 samples+=1;var state:=package.get_world_3d().direct_space_state
 for s in p.door_bindings:
  var door:Node3D=package.get_node(s.name)
  for leaf in door.leaves:
   for c in leaf.get_children():
    if not c is CollisionShape3D:continue
    var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001;var bad:Array=[]
    for h in state.intersect_shape(q,128):
     if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
    record("continuation_leaf_"+str(samples)+str(c.name),bad.is_empty())
    if not bad.is_empty():print("CONTINUATION_LEAF_CONTACT ",bad)
func line_probe(state:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,label:String)->void:
 var count:int=ceili(a.distance_to(b)/2)
 for j in range(count+1):
  var at:=a.lerp(b,float(j)/maxi(count,1));var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.3)
  probe_count+=1;record("floor_"+label+str(j),not h.is_empty()and absf(h.position.y-12)<.002);record("worker_"+label+str(j),capsule_clear(state,at))
  if not capsule_clear(state,at):print("STREET_WORKER_CONTACT ",label," ",at)
func setup(actor:CharacterBody3D,at:Vector3)->void:
 setups+=1;actor.global_position=at+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
 for i in range(20):await physics_frame
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_streets_20261011/STREETS.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var cart:Node3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart");var cart_id:=cart.get_instance_id()
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");residency.enabled=false;residency.set_physics_process(false)
 for entry in residency.entries:
  var room:Node3D=entry.room
  if str(room.get_meta("programme_key",""))not in["D03_directory_02","D03_directory_04","D03_directory_09"]:continue
  if not entry.attached:entry.parent.add_child(room);entry.attached=true
  load("res://scripts/deferred_home_visual.gd").ensure(room)
 load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(ship)
 load("res://scripts/group3_completion_20261011/labelled_bank.gd").build(ship)
 load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(ship)
 load("res://scripts/group3_d03_services_20261011/physical_package.gd").build(ship)
 var port2:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_port2_clinical_20261011/PHYSICAL.json"));var p2ids:Dictionary={}
 for key in port2.supplied_identity_map_required:p2ids[key]="__validation_only_streets_port2_"+key
 load("res://scripts/group3_port2_clinical_20261011/physical_package.gd").build(ship,p2ids)
 var connection:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CONNECTION.json"));var cids:Dictionary={}
 for q in connection.door_bindings:cids[q.name]="__validation_only_streets_connection_"+q.name
 load("res://scripts/group3_d03_port2_20261011/physical_package.gd").build(ship,cids,true)
 for i in range(15):await physics_frame
 var lower:Node3D=ship.get_node("ShipSpace/Districts/LowerStaffNetwork_WIP/LowerStaffEnclosure");var retained:Dictionary={}
 for mesh in lower.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name)in p.exact_current_meshes_to_replace:continue
  retained[str(mesh.name)]={"node":mesh,"transform":mesh.global_transform,"mesh":mesh.mesh,"faces":mesh.mesh.get_faces()}
 var ids:Dictionary={}
 for q in p.door_bindings:ids[q.name]="__validation_only_remaining_streets_"+q.name
 package=load("res://scripts/group3_d03_streets_20261011/physical_package.gd").build(ship,ids,true)
 for i in range(20):await physics_frame
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 for name in retained:
  var r:Dictionary=retained[name];record("unrelated_current_cell_"+name,is_instance_valid(r.node)and r.node.mesh==r.mesh and r.node.global_transform==r.transform and r.node.mesh.get_faces()==r.faces)
 record("only_exact_four_live_cells_replaced",lower.find_children("*","MeshInstance3D",true,false).size()==retained.size())
 var state:=ship.get_world_3d().direct_space_state
 for zrange in[[-469,-42.5],[42.5,431]]:line_probe(state,Vector3(57,12,zrange[0]),Vector3(57,12,zrange[1]),"starboard_main"+str(zrange))
 for zrange in[[-211,-42.5],[42.5,431]]:line_probe(state,Vector3(-57,12,zrange[0]),Vector3(-57,12,zrange[1]),"port_main"+str(zrange))
 for x in[-86,86]:
  for zrange in[[-342,-40],[40,342]]:line_probe(state,Vector3(x,12,zrange[0]),Vector3(x,12,zrange[1]),"interbank"+str(x)+str(zrange))
 for side in[-1,1]:
  var outer:float=-102 if side==-1 else 103
  line_probe(state,Vector3(side*57,12,-40),Vector3(outer,12,-40),"cross_fore"+str(side));line_probe(state,Vector3(side*57,12,40),Vector3(outer,12,40),"cross_aft"+str(side));line_probe(state,Vector3(outer,12,-40),Vector3(outer,12,40),"existing_outer"+str(side))
 for q in p.fixtures:
  var l:OmniLight3D=package.get_node(str(q.name)+"_PhysicalSource");record("supported_fixture_profile_"+str(q.name),l.global_position.distance_to(vec(q.position))<.0001 and l.shadow_enabled and l.omni_range==8 and is_equal_approx(l.light_energy,.9))
 var contacts:Array=[]
 for at in [Vector3(57,12,-383.3014),Vector3(57,12,379.2),Vector3(57,12,383.1846),Vector3(-57,12,379.2),Vector3(-57,12,383.1846),Vector3(-86,12,-62),Vector3(-86,12,-46),Vector3(-86,12,62),Vector3(86,12,-62),Vector3(86,12,46),Vector3(86,12,62)]:
  var query:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var names:Array=[]
  for hit in state.intersect_shape(query,128):names.append(str(hit.collider.get_path()))
  for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
   var hit:=ray(state,at+Vector3.UP-delta,at+Vector3.UP+delta)
   if not hit.is_empty():names.append(str(hit.collider.get_path()))
  contacts.append({"position":[at.x,at.y,at.z],"colliders":names});print("EXACT_STREET_CONTACT ",at," ",names)
 FileAccess.open("res://artifacts/group3_d03_streets_20261011/contact_survey.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"CONTACT_SURVEY_ONLY","contacts":contacts},"  "));quit()
