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
 assert(hits.is_empty(),"Entry obstruction remains")
 var actor:CharacterBody3D=load("res://scripts/player.gd").new()
 actor.spawn_position=Vector3(-6,6.1,432);actor.position=actor.spawn_position;world.add_child(actor)
 for frame in range(20):await physics_frame
 var walking_frames:=0
 var support_samples:=0
 for target_x in [-18.0,-6.0]:
  actor.rotation.y=PI/2 if target_x<actor.position.x else -PI/2
  var down:=InputEventKey.new();down.physical_keycode=KEY_W;down.keycode=KEY_W;down.pressed=true;Input.parse_input_event(down)
  var reached:=false
  for frame in range(320):
   var before:Vector3=actor.position
   await physics_frame
   walking_frames+=1
   assert(actor.position.distance_to(before)<.15 and absf(actor.position.y-6)<.08,"Unchanged player left supported floor")
   var ray:=PhysicsRayQueryParameters3D.create(actor.position+Vector3.UP*.15,actor.position-Vector3.UP*.2)
   ray.exclude=[actor.get_rid()]
   var support:=physics.intersect_ray(ray)
   assert(not support.is_empty() and absf(support.position.y-6)<.02)
   support_samples+=1
   if absf(actor.position.x-target_x)<.08:reached=true;break
  var up:=InputEventKey.new();up.physical_keycode=KEY_W;up.keycode=KEY_W;up.pressed=false;Input.parse_input_event(up)
  if not reached: print("ENTRY_WALK_FAILED ",actor.position," target ",target_x);quit(1);return
  for frame in range(12):await physics_frame
 var result:={"status":"PASS","section":"D02_directory_09","scope":"Focused production-source core aperture and Solar entry/return with unchanged player; full default scene and visual review separate","walking_frames":walking_frames,"support_samples":support_samples,"capsule_samples":33,"new_core_aperture_m":[4,2.65],"post_start_teleports":0}
 var receipt:=FileAccess.open("res://artifacts/solar_entry_walk.json",FileAccess.WRITE);receipt.store_string(JSON.stringify(result,"  "))
 print("PASS: ",JSON.stringify(result))
 helper.free();quit()
