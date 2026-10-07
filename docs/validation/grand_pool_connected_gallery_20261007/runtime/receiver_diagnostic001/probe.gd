extends SceneTree
const S="/workspace/scratch/375c2e438292/pool-connected-gallery-curved001/runtime_draft001/receiver_diagnostic001/"
func _initialize():call_deferred("run")
func vec(v):return [v.x,v.y,v.z]
func v3(a):return Vector3(a[0],a[1],a[2])
func trace(a,b,actor):
 var q=PhysicsRayQueryParameters3D.create(a,b)
 q.exclude=[actor.get_rid()]
 var rows=[]
 for crossing in range(6):
  var hit=actor.get_world_3d().direct_space_state.intersect_ray(q)
  if hit.is_empty():return {"clear":true,"hits":rows}
  var body=hit.collider
  var transparent=body is RigidBody3D or body is CharacterBody3D
  var mesh=body.get_parent() as MeshInstance3D
  var material=null
  if mesh!=null:
   material=mesh.get_active_material(0)
   if material is ShaderMaterial and material.shader!=null and "glass" in material.shader.resource_path:transparent=true
   elif material is StandardMaterial3D and material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED:transparent=true
  rows.append({"collider":str(body.get_path()),"mesh":str(mesh.name)if mesh!=null else null,"position":vec(hit.position),"normal":vec(hit.normal),"distance_m":a.distance_to(hit.position),"transparent_by_existing_policy":transparent,"material_name":str(material.resource_name)if material!=null else null})
  if not transparent:return {"clear":false,"hits":rows}
  var excluded=q.exclude;excluded.append(body.get_rid());q.exclude=excluded
 return {"clear":false,"hits":rows,"six_crossing_limit":true}
func run():
 var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for frame in range(30):await physics_frame
 var ship=main.get_node("World360/Astraea")
 var actor=ship.get_node("ShipSpace/PersistentActors/Player")
 var budget=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 actor.set_physics_process(false);budget.set_process(false)
 var contract=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json"))
 var proof=JSON.parse_string(FileAccess.get_file_as_string(S+"SOURCE_RECEIVER_PROOF.json"))
 var area=ship.find_child(str(contract.root_name),true,false)
 var result={"scope":"Read-only current installed ray diagnosis; no imports or saved changes","fixtures":[],"natural_selection":[]}
 for fixture in contract.fixtures:
  var light=area.get_node(NodePath(str(fixture.name)))
  var a=light.global_position
  var receiver=v3(fixture.receiver_xyz)
  var marker=str(fixture.marker_name)
  var row={"name":fixture.name,"position":vec(a),"actual_axis":vec(-light.global_basis.z),"receiver":fixture.receiver_xyz,"receiver_source_part":fixture.receiver_source_part,"anchor":fixture.visibility_sample_xyz,"anchor_clear_by_existing_selector":budget._clear_sample(a,v3(fixture.visibility_sample_xyz)),"anchor_trace":trace(a,v3(fixture.visibility_sample_xyz),actor),"extended_receiver_trace":trace(a,receiver+(receiver-a).normalized()*.02,actor),"source_alternatives":[]}
  for p in proof.fixtures:
   if str(p.name)!=marker:continue
   for candidate in p.receivers:
    var target=v3(candidate.point_xyz);var anchor=target+(a-target).normalized()*.06
    row.source_alternatives.append({"source_part":candidate.part,"source_point":candidate.point_xyz,"anchor":vec(anchor),"range_m":a.distance_to(target),"within_range_cone":a.distance_to(target)<light.spot_range and (target-a).normalized().dot(-light.global_basis.z)>cos(deg_to_rad(light.spot_angle)),"anchor_trace":trace(a,anchor,actor),"extended_target_trace":trace(a,target+(target-a).normalized()*.02,actor)})
  result.fixtures.append(row)
 for pose in [[-14,54.15,-443.2],[-13.1,54.15,-449.8],contract.seated_views[0].eye_xyz,[-11.05,54.15,-458],[-11.5,54.15,-438.4],[-9,54.15,-438.8]]:
  actor.global_position=v3(pose)-Vector3.UP*1.5
  budget.refresh();budget.refresh()
  var selected=[];var all_selected=[]
  for fixture in contract.fixtures:
   var light=area.get_node(NodePath(str(fixture.name)))
   if light.visible:selected.append(str(light.name))
  for light in budget.sources:
   if light.visible and light.shadow_enabled:all_selected.append(str(light.name))
  result.natural_selection.append({"pose":pose,"gallery_selected":selected,"all_active":all_selected})
 var f=FileAccess.open(S+"RESULT.json",FileAccess.WRITE);assert(f!=null);f.store_string(JSON.stringify(result,"  "));f.close()
 print("PASS: receiver diagnostic complete; ",result.fixtures.size()," fixtures")
 main.queue_free();await process_frame;quit()
