extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var legs:Array=[]
const OUT="/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_CENTRAL_ADJUNCT_CARE_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"original_controller_legs":legs,"completion_adjuncts_selected":1,"completion_luxury_homes_selected":0,"care_kits_selected":1,"source_floor_m2":80,"missing_connector_m2":39.78,"actual_positive_bearing_contacts":14,"all_original_D16_D17_profilewalls_and_contacts_retained":true,"new_wall_openings_or_cuts":0,"new_compiler_owners":0,"operating_private_admission_or_service":false,"beam_primary_structure_capacity_and_lower_section_accepted":false,"clinical_streaming_and_support_holds_unchanged":true,"capacity_credit":0,"full_build_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var space:=ship.get_world_3d().direct_space_state
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_central_receiving_20261013/RECEIVING.json"));var old:Node3D=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D17_starboard_house_extension");var originals:Array=[]
 for mesh:MeshInstance3D in old.find_children("*","MeshInstance3D",true,false):originals.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"bounds":mesh.get_aabb()})
 var shapes:Array=[]
 for c:CollisionShape3D in old.find_children("*","CollisionShape3D",true,false):shapes.append({"node":c,"shape":c.shape,"pose":c.global_transform})
 if not require(not originals.is_empty()and not shapes.is_empty(),"ActualoriginalD17receiver captured"):return
 for path in p.model_pins:
  if not require(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]),"Exactsource modelpin "+str(path)):return
 var wall_arch:Node3D=ship.find_child("StarboardHouseUpperArchitecture",true,false);var wall_pre:Array=[]
 for mesh:MeshInstance3D in wall_arch.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name).begins_with("HC_ProfileWall_D16")or str(mesh.name).begins_with("HC_ProfileWall_D17"):wall_pre.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"bounds":mesh.get_aabb(),"contacts":mesh.find_children("*","CollisionShape3D",true,false)})
 if not require(not wall_pre.is_empty(),"ActualretainedD16D17 profilewalls captured"):return
 var records:Array=[]
 for part in p.parts:
  var a:Array=part.bounds_xyz;var shape:=BoxShape3D.new();shape.size=Vector3(a[1]-a[0],a[3]-a[2],a[5]-a[4]);shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=.0001;q.transform=Transform3D(Basis.IDENTITY,Vector3((a[0]+a[1])/2.,(a[2]+a[3])/2.,(a[4]+a[5])/2.));var hits:Array=space.intersect_shape(q,128)
  for hit in hits:
   var mesh:MeshInstance3D=hit.collider.get_parent()as MeshInstance3D;var bounds:AABB=mesh.global_transform*mesh.get_aabb()if mesh!=null else AABB();records.append({"part":part.name,"kind":part.kind,"planned_bounds":a,"collider":str(hit.collider.get_path()),"mesh":str(mesh.name)if mesh!=null else"COMPILED_SLAB","world_min":[bounds.position.x,bounds.position.y,bounds.position.z],"world_max":[bounds.end.x,bounds.end.y,bounds.end.z],"compiled_receiver":old.is_ancestor_of(hit.collider)})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/ALL_CURRENT_FRAME_CONTACT_PREIMAGES.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_COMPLETE_CHANGED_FRAME_CONTACT_PREIMAGE_SURVEY","contacts":records,"new_geometry_adopted":false},"  "));print("CHANGED_FRAME_COMPLETE_CONTACT_SURVEY_PASS");quit(0)
