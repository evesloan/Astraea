extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/Astraea/BlenderCatalogue/assets/sound_receiving_20261016/"
const E="/workspace/sound-evidence/"
func _initialize()->void:call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func query_box(space:PhysicsDirectSpaceState3D,lo:Vector3,hi:Vector3,exclude:Array[RID])->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var b:=BoxShape3D.new();b.size=(hi-lo-Vector3.ONE*.0004).max(Vector3.ONE*.00001);b.margin=0;q.shape=b;q.margin=0;q.transform.origin=(lo+hi)/2;q.exclude=exclude;var result:Array=[]
 for h in space.intersect_shape(q,128):result.append(str(h.collider.get_path()))
 return result
func expected_surface(at:Vector3)->float:
 if at.x> -23.0 and at.x< -21.0:
  var z:float=650.8-at.z
  if z>=184.15 and z<184.55:return 69.503+(z-184.15)*.025/.4
  if z>=184.55 and z<184.95:return 69.528
  if z>=184.95 and z<=185.35:return 69.528-(z-184.95)*.025/.4
 return 69.5
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_PLAN.json"));var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(60)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(-2.0,69.53,467.55);actor.velocity=Vector3.ZERO
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(-22.0,69.53,463.8));ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(Vector3(-22.0,69.53,463.8));await frames(8)
 var cafe:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections/D11_directory_12");var original:Dictionary={}
 for m:MeshInstance3D in cafe.find_children("*","MeshInstance3D",true,false):original[m]={"mesh":m.mesh,"pose":m.global_transform}
 record("original_cafe_mesh_count",original.size()==212)
 for file in plan.source_pins:record("pin_"+str(file),FileAccess.get_sha256("res://"+str(file))==str(plan.source_pins[file]))
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[actor.get_rid()];var preflight:Array=[]
 for row in p.bounds:
  if row.name in["ISR_MissingOnlyFloor","ISR_SourceJoinedRoof"]:continue
  var hits:Array=query_box(space,vec(row.min),vec(row.max),excludes);var tie:bool=str(row.name).contains("Embedded")or str(row.name)in["ISR_AxialCross0_Web","ISR_AxialCross0_Upper"];var good:=hits.is_empty()
  if tie:
   good=hits.size()==1 and ((str(row.name).contains("Axial")and str(hits[0]).contains("/D11_aft_route/"))or(str(row.name).contains("Room")and str(hits[0]).contains("/D11_directory_12_authored_floor/")))
  if str(row.name).contains("Threshold"):
   good=true
   for hit in hits:
    if not (str(hit).contains("/E_outer_north/")or str(hit).contains("/D11_directory_12_authored_floor/")):good=false
  if str(row.name).begins_with("ISR_SourceWallJoin")or str(row.name)=="ISR_SourceRoofJoin":
   good=true
   for hit in hits:
    if not str(hit).contains("/E_outer_north/"):good=false
  record("old_contacts_"+str(row.name),good)
  if not hits.is_empty():preflight.append({"part":row.name,"contacts":hits,"classified":good})
 var floor_points:Array[Vector3]=[]
 for rect in plan.floor_rectangles:
  var x:float=rect[0]+.4
  while x<float(rect[1])-.2:
   var z:float=rect[2]+.4
   while z<float(rect[3])-.2:
    var at:=Vector3(x,69.5,z);floor_points.append(at);record("missing_before_"+str(floor_points.size()),ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty());z+=2.
   x+=2.
  for level in [[69.26,69.5],[73.3,73.48]]:
   var hits:Array=query_box(space,Vector3(rect[0],level[0],rect[2]),Vector3(rect[1],level[1],rect[3]),excludes);record("rect_volume_"+str(rect)+str(level),hits.is_empty())
 var doc:=GLTFDocument.new();var state:=GLTFState.new();record("candidate_raw_glb_read",doc.append_from_file(D+"exports/SOUND_SERVICE_RECEIVER_r001.glb",state)==OK)
 var model:Node3D=doc.generate_scene(state);model.name="SoundReceivingCandidate";ship.get_node("ShipSpace").add_child(model);var contacts:Array[Node]=[]
 var changed_walls:Array[MeshInstance3D]=[]
 for wallrow in p.walls:
  var oldwall:MeshInstance3D=cafe.find_child(str(wallrow.source_name),true,false);changed_walls.append(oldwall);var replacement:MeshInstance3D=model.find_child(str(wallrow.replacement_name),true,false)
  record("wall_source_pose_"+str(wallrow.source_name),oldwall.transform.origin.distance_to(vec(wallrow.source_local_translation))<.0001)
  record("wall_source_triangles_"+str(wallrow.source_name),oldwall.mesh.get_faces().size()==int(wallrow.source_triangles)*3)
  record("wall_source_bounds_"+str(wallrow.source_name),oldwall.mesh.get_aabb().position.distance_to(vec(wallrow.input_bounds_local[0]))<.0001 and oldwall.mesh.get_aabb().end.distance_to(vec(wallrow.input_bounds_local[1]))<.0001)
  var edited:Mesh=replacement.mesh.duplicate()
  for i in range(edited.get_surface_count()):edited.surface_set_material(i,oldwall.mesh.surface_get_material(i))
  oldwall.mesh=edited;var shape:CollisionShape3D=oldwall.find_children("*","CollisionShape3D",true,false)[0];var prior:Shape3D=shape.shape;shape.shape=edited.create_trimesh_shape();shape.shape.margin=prior.margin;replacement.free()
 for row in p.batches:
  var m:MeshInstance3D=model.find_child(str(row.name),true,false);record("batch_"+str(row.name),m!=null)
  if m!=null and row.collide:contacts.append(m)
 load("res://scripts/static_contact_cache.gd").attach_group(model,contacts);await frames(5)
 for at in floor_points:
  var h:=ray(space,at+Vector3.UP*.06,at-Vector3.UP*.02);record("floor_after_"+str(at),not h.is_empty()and str(h.collider.get_path()).contains("SoundReceivingCandidate")and absf(h.position.y-expected_surface(at))<.0002)
 var mounts:Array=[]
 for row in p.bounds:
  if not str(row.name).contains("CanopyTie"):continue
  var at:Vector3=(vec(row.min)+vec(row.max))/2;at.y=73.29;var h:=ray(space,at,at+Vector3.UP*.03);var good:bool=not h.is_empty()and str(h.collider.get_path()).contains("SoundReceivingCandidate")and absf(h.position.y-73.3)<.0002;record("fixture_roof_"+str(row.name),good);mounts.append({"name":row.name,"at":str(at),"passed":good})
 for row in p.lights:
  var at:=vec(row.at);var h:=ray(space,at,at-Vector3.UP*4);record("emitter_to_new_floor_"+str(row.name),not h.is_empty()and str(h.collider.get_path()).contains("SoundReceivingCandidate")and absf(h.position.y-69.5)<.0002)
 var legs:Array=[];var route:Array[Vector3]=[Vector3(-6,69.5,467.55),Vector3(-22,69.5,467.55),Vector3(-22,69.5,466.8),Vector3(-22,69.5,464),Vector3(-22,69.5,459.5),Vector3(-11,69.5,459.5),Vector3(-12,69.5,461.4),Vector3(-11,69.5,459.5),Vector3(-22,69.5,459.5),Vector3(-36,69.5,459.5),Vector3(-36,69.5,461.2),Vector3(-45,69.5,461.2),Vector3(-36,69.5,461.2),Vector3(-36,69.5,459.5),Vector3(-22,69.5,459.5),Vector3(-22,69.5,464),Vector3(-22,69.5,466.8),Vector3(-22,69.5,467.55),Vector3(-6,69.5,467.55),Vector3(-2,69.5,467.55)]
 var proceed:bool=errors.is_empty();actor.set_controls_enabled(true);actor.set_physics_process(true);await frames(20)
 for goal in route:
  if not proceed:break
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg);record("walk_out_"+str(legs.size()),leg.reached and leg.floor_contact);proceed=leg.reached and leg.floor_contact
 var preserved:=true
 for m in original:
  if not is_instance_valid(m)or (m not in changed_walls and m.mesh!=original[m].mesh) or not m.global_transform.is_equal_approx(original[m].pose):preserved=false
 record("all_original_cafe_meshes_unchanged",preserved);record("continuous_route_complete",proceed and legs.size()==20)
 var report:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","scope":"Candidate receiving only; unchanged original controller and sources; no operational/cart/species/primary/final-art acceptance","checks":checks,"errors":errors,"original_cafe_meshes":original.size(),"old_geometry_contacts":preflight,"missing_only_floor_samples":floor_points.size(),"fixture_roof_mounts":mounts,"original_controller_legs":legs,"route_teleports":0,"candidate_only":true}
 FileAccess.open(E+"SOUND_CANDIDATE_MAIN_r001.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("SOUND_CANDIDATE ",report.status," ",checks.size()," checks ",legs.size()," legs errors=",errors);quit(0 if errors.is_empty()else 1)
