extends SceneTree
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"FITTED_CANDIDATE_OVERLAY_r006.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func digest(b:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(b);return h.finish().hex_encode()
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var group:Node3D=load("res://scripts/fitted_wet_pavilions_20261015/package.gd").build(ship)
 for i in range(4):await physics_frame
 var space:=ship.get_world_3d().direct_space_state;var excludes:Array[RID]=[]
 for body:CollisionObject3D in group.find_children("*","CollisionObject3D",true,false):excludes.append(body.get_rid())
 var sites:Array=[];var main_hits:Array=[];var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r006.json"))
 for kit in["TIDAL","QUIET"]:
  var model:Node3D=group.get_node(kit);var contacts:Array=[];var footpins:Array=[];var checked:=0
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if str(mesh.name).contains("Water_Illustrative"):continue
   checked+=1;var b:AABB=mesh.global_transform*mesh.get_aabb();var shape:ConvexPolygonShape3D=mesh.mesh.create_convex_shape(true,false);shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=mesh.global_transform;q.exclude=excludes
   var hits:Array=space.intersect_shape(q,256)
   if not hits.is_empty():
    var paths:Array=[]
    for hit in hits:paths.append(str(hit.collider.get_path()).trim_prefix(str(ship.get_path())+"/"))
    contacts.append({"part":str(mesh.name),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"contacts":paths,"saturated":hits.size()==256})
   if str(mesh.name).contains("ColumnBase") or str(mesh.name).ends_with("_Foot"):
    var centre:Vector3=b.get_center();var ray:=PhysicsRayQueryParameters3D.create(Vector3(centre.x,102.05,centre.z),Vector3(centre.x,101.95,centre.z));ray.exclude=excludes;var hit:Dictionary=space.intersect_ray(ray);footpins.append({"column":str(mesh.name),"at":[centre.x,102,centre.z],"old_floor":str(hit.collider.get_path())if not hit.is_empty()else"","floor_y":hit.position.y if not hit.is_empty()else null})
  sites.append({"kit":kit,"meshes_checked":checked,"contacts":contacts,"column_floor_preimages":footpins})
  var box:=BoxShape3D.new();box.size=Vector3(34,3.98,8);box.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.margin=0.;q.transform=Transform3D(Basis.IDENTITY,Vector3(-80 if kit=="TIDAL"else 80,104.0,-370));var hits:Array=space.intersect_shape(q,8192);assert(hits.size()<8192)
  for hit in hits:
   if group.is_ancestor_of(hit.collider):main_hits.append({"kit":kit,"new_contact":str(hit.collider.get_path())})
 var roof_preservation:Array=[]
 for row in config.roofs:
  var old:Mesh=group.get_meta(str(row.kit)+"_original_roof_mesh");var node:MeshInstance3D=ship.get_node("ShipSpace/Districts/"+str(row.receiver_root)).find_child(str(row.node),true,false);var faces:PackedVector3Array=node.mesh.get_faces();var keys:Dictionary={}
  for i in range(0,faces.size(),3):keys[digest(PackedVector3Array([faces[i],faces[i+1],faces[i+2]]).to_byte_array())]=true
  var original:PackedVector3Array=old.get_faces();var untouched:=0;var missing:=0;var hole:=AABB(Vector3(row.mask[0],row.mask[2],row.mask[4]),Vector3(row.mask[1]-row.mask[0],row.mask[3]-row.mask[2],row.mask[5]-row.mask[4]))
  for i in range(0,original.size(),3):
   var bounds:=AABB(original[i],Vector3.ZERO);bounds=bounds.expand(original[i+1]);bounds=bounds.expand(original[i+2])
   if not bounds.intersects(hole):
    if keys.has(digest(PackedVector3Array([original[i],original[i+1],original[i+2]]).to_byte_array())):untouched+=1
    else:missing+=1
  roof_preservation.append({"kit":row.kit,"untouched_original_triangles_exact":untouched,"unmatched_outside_triangles":missing,"original_source_file_unchanged":FileAccess.get_sha256("res://assets/models/"+str(row.model))==str(row.source_sha256)})
 FileAccess.open(D+"FITTED_CURRENT_CONTACTS_r006.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"FITTED_R006_CURRENT_CONTACT_INVENTORY_REQUIRES_INTERPRETATION","sites":sites,"new_contacts_in_original_eight_metre_main_lanes":main_hits,"roof_outside_preservation":roof_preservation,"retained_loose_models_moved":group.get_meta("exact_loose_furniture_successors").size(),"production_changed":false},"  "));print("PASS_FITTED_R006_CURRENT_CONTACT_INVENTORY");quit(0)
