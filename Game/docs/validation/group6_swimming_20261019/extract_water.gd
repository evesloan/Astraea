extends SceneTree
func _initialize()->void:call_deferred("run")
func extract(model:Node3D,mesh_name:String,water_y:float)->Array:
 var mesh:MeshInstance3D=model.find_child(mesh_name,true,false);assert(mesh!=null)
 var faces:PackedVector3Array=mesh.mesh.get_faces();var triangles:Array=[]
 for i in range(0,faces.size(),3):
  var a:Vector3=mesh.transform*faces[i];var b:Vector3=mesh.transform*faces[i+1];var c:Vector3=mesh.transform*faces[i+2]
  if maxf(absf(a.y-water_y),maxf(absf(b.y-water_y),absf(c.y-water_y)))>.003:continue
  if absf((b-a).cross(c-a).y)<.000001:continue
  triangles.append([[a.x,a.z],[b.x,b.z],[c.x,c.z]])
 assert(not triangles.is_empty());return triangles
func run()->void:
 var rows:Array=[]
 var entries:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/THERMAL_ENTRY_CONTRACT.json"))
 var tidal:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/TIDAL_NORTH_ROOM_CONTRACT.json"))
 for room in entries.rooms:
  var file:String="res://"+str(room.current_room_runtime).trim_prefix("Game/")
  var model:Node3D=load(file).instantiate()
  for i in range(room.entries.size()):
   var entry:Dictionary=room.entries[i];var water_mesh:String=room.water_visual_contact_exclusions[i];var nominal:=44.92;var current:Node3D=model;var source_file:=file
   if room.programme_key=="D08_directory_02" and i==1:
    source_file="res://"+str(tidal.runtime_addition).trim_prefix("Game/");current=load(source_file).instantiate();water_mesh="G6_TIDAL__water_face";nominal=float(tidal.water_nominal_y)
   rows.append({"id":entry.id,"programme_key":room.programme_key,"water_y":nominal,"bed_y":entry.original_bed_top_y,"source_file":source_file.trim_prefix("res://"),"source_sha256":FileAccess.get_sha256(source_file),"source_water_mesh":water_mesh,"triangles_xz":extract(current,water_mesh,nominal)})
   if current!=model:current.free()
  model.free()
 var annex:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AQUATIC_ANNEX_PLAN.json"))
 var visual:Node3D=load("res://assets/models/AquaticCompletion_r019.glb").instantiate()
 var policy:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/COLLISION_POLICY.json"))
 for pool in annex.new_thermal_spa_pools:
  var triangles:Array=[]
  for name in policy:
   if policy[name]!="water_visual":continue
   var mesh:MeshInstance3D=visual.find_child(str(name),true,false);assert(mesh!=null)
   var faces:PackedVector3Array=mesh.mesh.get_faces()
   for i in range(0,faces.size(),3):
    var a:Vector3=mesh.transform*faces[i];var b:Vector3=mesh.transform*faces[i+1];var c:Vector3=mesh.transform*faces[i+2]
    if maxf(absf(a.y-float(pool.water_y)),maxf(absf(b.y-float(pool.water_y)),absf(c.y-float(pool.water_y))))>.003:continue
    if Vector2((a.x+b.x+c.x)/3-pool.center_xz[0],(a.z+b.z+c.z)/3-pool.center_xz[1]).length()>float(pool.radius_m):continue
    if absf((b-a).cross(c-a).y)<.000001:continue
    triangles.append([[a.x,a.z],[b.x,b.z],[c.x,c.z]])
  assert(not triangles.is_empty());rows.append({"id":pool.id,"programme_key":pool.parent_programme,"water_y":pool.water_y,"bed_y":pool.bottom_y,"source_file":"assets/models/AquaticCompletion_r019.glb","source_sha256":FileAccess.get_sha256("res://assets/models/AquaticCompletion_r019.glb"),"triangles_xz":triangles})
 visual.free()
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_SECTION_PLAN.json"));var rect:Array=plan.water.rect
 rows.append({"id":"D08_directory_01","programme_key":"D08_directory_01","water_y":plan.section.water_level_trial_y,"bed_y":plan.section.basin_bottom_y,"source_file":"scripts/grand_pool_section.gd","source_sha256":FileAccess.get_sha256("res://scripts/grand_pool_section.gd"),"source_water_mesh":"GrandPoolTrialWater_VisualOnly_NoSwimming","triangles_xz":[[[rect[0],rect[2]],[rect[1],rect[2]],[rect[1],rect[3]]],[[rect[0],rect[2]],[rect[1],rect[3]],[rect[0],rect[3]]]]})
 FileAccess.open("res://data/architecture/group6_swimming_20261019/WATER_VOLUMES.json",FileAccess.WRITE).store_string(JSON.stringify({"schema":1,"source_extracted":true,"volumes":rows},"  "))
 for row in rows:print(row.id," WATER ",row.water_y," BED ",row.bed_y," TRIANGLES ",row.triangles_xz.size())
 quit()
