extends SceneTree
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"SOURCE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var reports:Array=[]
 for kit in["TIDAL","QUIET"]:
  var origin:=Vector3(-80 if kit=="TIDAL"else 80,102,-370);var model:Node3D=(load("res://assets/group2_vip_pavilions/VIP_"+kit+"_r003.glb")as PackedScene).instantiate();ship.add_child(model);model.global_position=origin
  var collisions:Array=[];var meshes:=0
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if "Water_Illustrative"in str(mesh.name):continue
   var original_bounds:AABB=mesh.global_transform*mesh.get_aabb()
   if original_bounds.end.z > -374.0:continue
   mesh.position.z+=18.0
   meshes+=1
   var shape:ConvexPolygonShape3D=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=mesh.global_transform;q.margin=0.
   var hits:Array=space.intersect_shape(q,256)
   if not hits.is_empty():
    var contacts:Array=[]
    for hit in hits:contacts.append(str(hit.collider.get_path()).trim_prefix(str(ship.get_path())+"/"))
    var bounds:AABB=mesh.global_transform*mesh.get_aabb();collisions.append({"part":str(mesh.name),"min":[bounds.position.x,bounds.position.y,bounds.position.z],"max":[bounds.end.x,bounds.end.y,bounds.end.z],"contacts":contacts,"hit_limit_reached":hits.size()==256})
  var receiver:Node3D=ship.get_node("ShipSpace/Districts/"+("TidalGardenReceivingCandidate"if kit=="TIDAL"else"QuietGroveReceivingCandidate"))
  var loose:Array=[]
  for node:Node3D in receiver.get_node("RetainedLandscapeAndSeating").get_children():
   var bounds:=AABB();var first:=true
   for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
    var b:AABB=mesh.global_transform*mesh.get_aabb();bounds=b if first else bounds.merge(b);first=false
   if bounds.intersects(AABB(origin+Vector3(-15.8,0,-13.7),Vector3(31.6,.12,7.75))):loose.append({"path":str(receiver.get_path_to(node)),"position":[node.position.x,node.position.y,node.position.z],"min":[bounds.position.x,bounds.position.y,bounds.position.z],"max":[bounds.end.x,bounds.end.y,bounds.end.z]})
  reports.append({"kit":kit,"footprint_m2":952,"meshes_checked":meshes,"collisions":collisions,"loose_furniture":loose});model.queue_free();await physics_frame
 FileAccess.open(D+"AFT_WET_PAVILION_CURRENT_CONTACTS.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"CURRENT_SCOPED_CONVEX_CONTACT_INVENTORY_REQUIRES_INTERPRETATION_NOT_ACCEPTANCE","sites":reports},"  "));print("PASS_AFT_PAVILION_CONTACT_INVENTORY");quit(0)
