extends SceneTree
const P := "res://tidal_d14_landing_20261023/"
var checks:=0
var failures:Array[String]=[]
func _initialize()->void:call_deferred("run")
func check(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);push_error(label)
func raw(path:String)->Node3D:
 var doc:=GLTFDocument.new();var state:=GLTFState.new();state.handle_binary_image=GLTFState.HANDLE_BINARY_EMBED_AS_UNCOMPRESSED
 var error:=doc.append_from_buffer(FileAccess.get_file_as_bytes(path),path.get_base_dir(),state)
 check(error==OK,"fresh source GLTF parse "+path)
 return doc.generate_scene(state)
func signature(source:Node3D)->Dictionary:
 var result:={}
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  result[str(source.get_path_to(mesh))]=[mesh.mesh,mesh.global_transform,mesh.get_child_count()]
 return result
func triangle_signature(node:Node3D, architecture_only:bool=false)->Dictionary:
 var groups:={}
 for m:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  if architecture_only and not str(m.name).begins_with("ArchitectureMaterial_"):continue
  for surface in m.mesh.get_surface_count():
   var key:=m.get_active_material(surface).resource_name
   if not groups.has(key):groups[key]=[]
   var arrays:=m.mesh.surface_get_arrays(surface);var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
   for i in (indices if not indices.is_empty() else range(vertices.size())):
    var point:Vector3=m.global_transform*vertices[i]
    groups[key].append("%d,%d,%d"%[roundi(point.x*10000),roundi(point.y*10000),roundi(point.z*10000)])
 for key in groups:groups[key].sort()
 return groups
func run()->void:
 var adapter=load(P+"adapter.gd")
 var ship:=Node3D.new();ship.name="FocusedTidalReceiving";root.add_child(ship)
 check(not adapter.receiving_error(ship).is_empty(),"missing receiving owner rejected")
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var house:=Node3D.new();house.name="TidalGardenReceivingCandidate";districts.add_child(house);house.set_meta("persistent_id","tidal_garden_house_001");house.set_meta("installed_guest_units",131)
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json"))
 var source:=raw("res://assets/models/"+str(definition.model_file));house.add_child(source)
 var original_meshes:=source.find_children("*","MeshInstance3D",true,false)
 check(original_meshes.size()==334,"all retained architecture parts present")
 var source_faces:=PackedVector3Array()
 for mesh:MeshInstance3D in original_meshes:
  if not bool(mesh.get_meta("extras",{}).get("runtime_collision",false)):continue
  for point in mesh.mesh.get_faces():source_faces.append(mesh.global_transform*point)
 var static_body:=StaticBody3D.new();ship.add_child(static_body);var cs:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.set_faces(source_faces);cs.shape=shape;static_body.add_child(cs)
 var seats:=Node3D.new();seats.name="RetainedLandscapeAndSeating";house.add_child(seats)
 for row in definition.retained_asset_instances:
  if not str(row.name) in ["D14_LandingSeat_-89","D14_LandingSeat_-85","D14_LandingTable"]:continue
  var placement:=Node3D.new();placement.name=row.name;seats.add_child(placement);placement.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);placement.rotation.y=deg_to_rad(row.yaw);placement.scale=Vector3.ONE*float(row.scale)
  var asset:Node3D=raw("res://assets/models/"+str(definition.retained_asset_definitions[row.catalogue_id].model_file));placement.add_child(asset)
  for mesh:MeshInstance3D in asset.find_children("*","MeshInstance3D",true,false):mesh.create_trimesh_collision()
 var before:=signature(source);var seats_before:=signature(seats)
 check(adapter.after_step(ship,"quiet_grove_adoption.gd")==null,"unrelated construction step ignored")
 var addition:Node3D=adapter.after_step(ship,"tidal_garden_adoption.gd");check(addition!=null,"receiving adapter installs")
 if addition==null:ship.free();quit(1);return
 check(adapter.build(ship)==addition,"idempotent call returns same addition")
 check(signature(source)==before,"all 334 original meshes and transforms unchanged")
 check(signature(seats)==seats_before,"original landing furnishings and contacts unchanged")
 check(addition.find_children("*","CollisionShape3D",true,false).size()==1,"one prebuilt exact contact shape")
 check(addition.find_children("*","Light3D",true,false).size()==2,"two fixture lights without duplication")
 check(addition.get_meta("native_source_parts").size()==71,"71 original native part identities retained")
 var new_native:=raw(P+"TidalD14Landing_r001.glb");ship.add_child(new_native)
 check(triangle_signature(new_native)==triangle_signature(addition,true),"exact material-grouped native vertex coverage at 0.1mm")
 new_native.free()
 for i in [0,1]:
  var id:String="AST-BOT-002" if i==0 else "AST-BOT-003"
  var retained:=raw("res://assets/models/"+str(definition.retained_asset_definitions[id].model_file));ship.add_child(retained)
  var planted:Node3D=addition.get_node("RetainedPlant_%02d"%i);retained.global_transform=planted.global_transform
  check(triangle_signature(retained)==triangle_signature(planted),"retained botanical material and vertex coverage "+id)
  retained.free()
 var actor:=Node3D.new();actor.position=Vector3(-87,88.5,-387);ship.add_child(actor)
 await physics_frame;await physics_frame
 var state:=ship.get_world_3d().direct_space_state
 for x in [-89.0,-87.0,-85.0]:
  for z in [-385.0,-386.5,-387.7]:
   var floor_hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,88.65,z),Vector3(x,88.3,z)))
   check(not floor_hit.is_empty() and abs(float(floor_hit.position.y)-88.5)<.002,"retained landing floor "+str(Vector2(x,z)))
   var capsule:=CapsuleShape3D.new();capsule.radius=.32;capsule.height=1.8
   var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform.origin=Vector3(x,89.42,z)
   check(state.intersect_shape(query,1).is_empty(),"clear ordinary approach capsule "+str(Vector2(x,z)))
 for z in [-374.0,-372.0,-370.0,-368.0,-366.0]:
  var query:=PhysicsRayQueryParameters3D.create(Vector3(-87,89,z),Vector3(-87,92,z));var hit:=state.intersect_ray(query)
  check(hit.is_empty() or not addition.is_ancestor_of(hit.collider),"new package excludes dry arrival "+str(z))
 for x in [-89.0,-85.0]:
  var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,90,-389.5),Vector3(x,90,-381.5)))
  check(hit.is_empty() or not addition.is_ancestor_of(hit.collider),"new architecture preserves forward seated outlook "+str(x))
 var budget:Node=load("res://scripts/lighting_budget.gd").new();ship.add_child(budget);budget.configure(ship,actor)
 check(budget.shadow_source_budget==8,"retained eight-source selector unchanged")
 check(budget.sources.size()==2,"fixtures enrolled exactly once")
 check(budget.previously_active.size()==2,"both local fixture light samples clear")
 house.set_meta("installed_guest_units",132);check(not adapter.receiving_error(ship).is_empty(),"changed allocation rejected");house.set_meta("installed_guest_units",131)
 var chair:Node3D=seats.get_node("D14_LandingSeat_-89");chair.position.x+=.1;check(not adapter.receiving_error(ship).is_empty(),"moved furniture rejected");chair.position.x-=.1
 var receipt:={"status":"PASS" if failures.is_empty() else "FAIL","checks":checks,"failures":failures,"original_architecture_parts":334,"unchanged_furniture":3,"new_native_parts":71,"new_floors":0,"new_units":0,"new_rests":0,"lights":2,"fixture_type":"fresh raw retained architecture plus three actual landing furnishings; not full ship","ordinary_approach_capsules":9,"final_visual_accepted":false,"full_startup_gameplay_performance":false}
 var f:=FileAccess.open(P+"evidence/CHECK.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("TIDAL_LANDING_CHECK ",JSON.stringify(receipt))
 ship.free();quit(0 if failures.is_empty() else 1)
