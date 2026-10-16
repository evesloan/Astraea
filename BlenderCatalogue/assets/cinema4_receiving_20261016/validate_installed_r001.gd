extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/cinema4_receiving_20261016/"
const E="/workspace/cinema4-evidence/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func query_box(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);b.margin=0;q.shape=b;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func expected_surface(at:Vector3)->float:
 if at.z> 159.0 and at.z< 161.0:
  if at.x>=10.8 and at.x<11.2:return 69.503+(at.x-10.8)*.025/.4
  if at.x>=11.2 and at.x<11.6:return 69.528
  if at.x>=11.6 and at.x<=12:return 69.528-(at.x-11.6)*.025/.4
 return 69.5
func opening_occlusion_clear(ship:Node3D)->bool:
 var root:Node3D=ship.get_node("VerifiedStaticOpaqueFaceOccluders");var cells:=root.find_children("*","OccluderInstance3D",true,false)
 if cells.is_empty():return false
 var region:=AABB(Vector3(11.2,69.9,158.7),Vector3(.5,2.2,2.6))
 for cell:OccluderInstance3D in cells:
  var vs:PackedVector3Array=cell.occluder.get_vertices();var ix:PackedInt32Array=cell.occluder.get_indices()
  for i in range(0,ix.size(),3):
   var a:Vector3=cell.global_transform*vs[ix[i]];var b:Vector3=cell.global_transform*vs[ix[i+1]];var c:Vector3=cell.global_transform*vs[ix[i+2]];var lo:Vector3=a.min(b).min(c);var hi:Vector3=a.max(b).max(c)
   if not AABB(lo,hi-lo).grow(.0001).intersects(region):continue
   for z in [159.2,160.0,160.8]:
    for y in [70.,71.,72.]:
     if Geometry3D.segment_intersects_triangle(Vector3(11.2,y,z),Vector3(11.7,y,z),a,b,c)!=null:return false
 return true
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(2,69.53,160.0);actor.velocity=Vector3.ZERO
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(16,69.53,160.0));ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(Vector3(16,69.53,160.0));await frames(8)
 var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D11_directory_05");var original:Node3D=cafe.get_child(0);var baseline:Node3D=load("res://assets/models/SOL_D11_directory_05_source001.glb").instantiate();var preserved:=true;var count:=0
 for m:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):
  var before:MeshInstance3D=baseline.get_node(original.get_path_to(m));count+=1
  if not m.transform.is_equal_approx(before.transform)or(m.name not in["E_outer_west1"]and m.mesh!=before.mesh):preserved=false
 record("source_poses_and_unrelated_meshes_preserved",preserved and count==1468);baseline.free()
 var model:Node3D=ship.get_node("ShipSpace/Cinema4ServiceReceiving20261016");record("only_one_receiving_root",ship.get_node("ShipSpace").find_children("Cinema4ServiceReceiving20261016","",false,false).size()==1);record("two_source_lamps",model.find_children("*","Light3D",true,false).size()==2)
 for wall in p.walls:
  var key:String=str(wall.source_name).replace("-","_");record("retained_original_resources_"+key,model.has_meta(key+"_retained_mesh")and model.has_meta(key+"_retained_shape"))
 record("installed_opening_occlusion_clear",opening_occlusion_clear(ship))
 var space:=ship.get_world_3d().direct_space_state;var floor_points:Array[Vector3]=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.4
  while x<float(rect[1])-.2:
   var z:float=rect[2]+.4
   while z<float(rect[3])-.2:
    floor_points.append(Vector3(x,69.5,z));z+=2.
   x+=2.
 for at in floor_points:
  var h:=ray(space,at+Vector3.UP*.06,at-Vector3.UP*.02);record("new_floor_"+str(at),not h.is_empty()and str(h.collider.get_path()).contains("Cinema4ServiceReceiving20261016")and absf(h.position.y-expected_surface(at))<.0002)
 for x in [11.25,11.4,11.55]:
  var h:=ray(space,Vector3(x,69.6,160.0),Vector3(x,69.49,160.0));record("positive_threshold_"+str(x),not h.is_empty()and h.position.y>69.505 and h.position.y<69.54)
 var mounts:Array=[]
 for row in p.bounds:
  if not str(row.name).contains("CanopyTie"):continue
  var at:Vector3=(vec(row.min)+vec(row.max))/2;at.y=73.29;var h:=ray(space,at,at+Vector3.UP*.03);var good:bool=not h.is_empty()and str(h.collider.get_path()).contains("Cinema4ServiceReceiving20261016")and absf(h.position.y-73.3)<.0002;record("fixture_roof_"+str(row.name),good);mounts.append({"name":row.name,"at":str(at),"passed":good})
 for row in p.lights:
  var at:=vec(row.at);var h:=ray(space,at,at-Vector3.UP*4);record("emitter_to_new_floor_"+str(row.name),not h.is_empty()and str(h.collider.get_path()).contains("Cinema4ServiceReceiving20261016")and absf(h.position.y-69.5)<.0002)
 var legs:Array=[];var route:Array[Vector3]=[Vector3(6,69.5,160.0),Vector3(10.5,69.5,160.0),Vector3(12.2,69.5,160.0),Vector3(16,69.5,160.0),Vector3(29,69.5,160.0),Vector3(29,69.5,152.0),Vector3(36,69.5,152.0),Vector3(36,69.5,155.0),Vector3(36,69.5,152.0),Vector3(44,69.5,152.0),Vector3(56,69.5,152.0),Vector3(56,69.5,157.5),Vector3(56,69.5,152.0),Vector3(44,69.5,152.0),Vector3(36,69.5,152.0),Vector3(29,69.5,152.0),Vector3(29,69.5,160.0),Vector3(16,69.5,160.0),Vector3(12.2,69.5,160.0),Vector3(10.5,69.5,160.0),Vector3(6,69.5,160.0),Vector3(2,69.5,160.0)]
 var proceed:bool=errors.is_empty();actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_out_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 record("continuous_route_complete",proceed and legs.size()==22)
 actor.set_physics_process(false);var saved_position:=actor.global_position;var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");actor.global_position=Vector3(5000.0,61.0,0.0);residency.refresh(9.);record("normal_cached_detach",not cafe.is_inside_tree());actor.global_position=saved_position;residency.prepare_position(saved_position);await frames(8);record("normal_cached_reattach",cafe.is_inside_tree());record("one_preserved_source_set",model.find_children("*","Light3D",true,false).size()==2)
 record("cached_west_opening_clear",capsule_clear(space,Vector3(11.45,69.54,160.0)))
 record("cached_opening_occlusion_clear",opening_occlusion_clear(ship))
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","scope":"Physical care receiving only; unchanged original controller and sources; no operational/cart/species/primary/final-art acceptance","checks":checks,"errors":errors,"original_cafe_meshes":count,"missing_only_floor_samples":floor_points.size(),"fixture_roof_mounts":mounts,"original_controller_legs":legs,"route_teleports":0,"default_installed":true,"separate_stream_lifecycle_test_after_route":true}
 FileAccess.open(E+"CINEMA4_INSTALLED_MAIN_r001.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("CINEMA4_INSTALLED ",report.status," ",checks.size()," checks ",legs.size()," legs errors=",errors);quit(0 if errors.is_empty()else 1)
