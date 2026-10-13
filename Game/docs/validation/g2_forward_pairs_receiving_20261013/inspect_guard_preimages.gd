extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/g2_remaining_five_pairs_20261013/CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_forward_receiving_20261013/FORWARD.json"));var ship:=Node3D.new();root.add_child(ship);var ss:=Node3D.new();ss.name="ShipSpace";ship.add_child(ss);var ds:=Node3D.new();ds.name="Districts";ss.add_child(ds);var records:Array=[]
 for site in p.sites:
  var r:=Node3D.new();r.name=site.receiver_root;ds.add_child(r);var visual:Node3D=(load("res://assets/models/"+str(site.receiver_model))as PackedScene).instantiate();r.add_child(visual);var rows:Array=[]
  for name in site.guard_batches:
   var mesh:MeshInstance3D=visual.find_child(str(name),true,false);assert(mesh!=null);var extra:Dictionary=mesh.get_meta("extras",{});assert(extra.category in ["guard","public_glass"]);load("res://scripts/static_contact_cache.gd").attach(mesh);rows.append({"name":name,"faces_sha256":digest(mesh.mesh.get_faces().to_byte_array()),"faces_vertices":mesh.mesh.get_faces().size(),"category":extra.category})
  site['guard_preimages']=rows;records.append(site)
 for i in range(3):await physics_frame
 var space:=ship.get_world_3d().direct_space_state;var old:Array=[]
 for site in records:
  for x in [site.centre-1.2,site.centre+1.2]:old.append({"x":x,"hit":not space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,102.7,-384.3),Vector3(x,102.7,-383.7))).is_empty()})
  var owner:=Node3D.new();ship.add_child(owner);load("res://scripts/group2_forward_receiving_20261013/guard_window_successor.gd").apply(ship,owner,site)
 for i in range(3):await physics_frame
 for site in records:assert(space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(site.centre,102.7,-384.3),Vector3(site.centre,102.7,-383.7))).is_empty())
 for row in old:assert(row.hit==not space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(row.x,102.7,-384.3),Vector3(row.x,102.7,-383.7))).is_empty())
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_remaining_five_pairs_20261013/EXACT_FORWARD_GUARD_PREIMAGES.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_FORWARD_GUARD_PREIMAGES_AND_SCOPED_WINDOWS","sites":records,"outside_guard_probe_states_unchanged":true},"  "));print("FORWARD_GUARD_PREIMAGES_PASS");quit(0)
