extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 var helper:Node3D=load("res://scripts/ship.gd").new()
 var core:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_PUBLIC_CORE.json"))
 helper.model(world,str(core.enclosure_file),"ExistingAftCore",Vector3(0,0,432))
 helper.model(world,"SOL_D02_directory_09_source001.glb","Solar",Vector3(-8,6,398))
 var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var extra:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/received_structural_meshes.json"))
 var rows:Array=extra.regions.duplicate(true)
 for row in base.regions:
  if str(row.id)=="D02_aft_public_core_floor":rows.append(row)
 var mat:=StandardMaterial3D.new()
 load("res://scripts/structural_floor_builder.gd").build_regions(world,mat,mat,rows)
 for frame in range(4):await physics_frame
 var physics:=world.get_world_3d().direct_space_state
 var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
 var hits:Array=[]
 for step in range(33):
  var p:=Vector3(-6.0-step*.25,6,432)
  var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform=Transform3D(Basis.IDENTITY,p+Vector3.UP*.925)
  for hit in physics.intersect_shape(query,32):hits.append({"xyz":[p.x,p.y,p.z],"collider":str(hit.collider.get_path())})
 var file:=FileAccess.open("res://artifacts/solar_entry_obstructions.json",FileAccess.WRITE);file.store_string(JSON.stringify(hits,"  "))
 print("SOLAR_ENTRY_DIAGNOSTIC ",JSON.stringify(hits))
 helper.free();quit()
