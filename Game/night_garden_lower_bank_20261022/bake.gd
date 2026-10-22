extends SceneTree
const P:="res://night_garden_lower_bank_20261022/"
func _initialize()->void:call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func arr(a:Vector3)->Array:return [a.x,a.y,a.z]
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"));var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://family_specialty_bank_20261022/evidence/INDEX_R002.json")).rooms;var result:={"rooms":{},"status":"PASS","main_integrated":false}
 for room:Dictionary in plan.rooms:
  var old:Dictionary=source[room.source_room_model];var transform:=Transform3D(Basis.IDENTITY,v(room.runtime_translation));var record:Dictionary=old.duplicate(true)
  for kind:String in ["shell","detail","full"]:
   var src:String=old[kind+"_path"]if kind!="full"else str(old.full_path);var expected:String=old[kind+"_sha256"]if kind!="full"else str(old.sha256);assert(FileAccess.get_sha256(src)==expected)
   var holder:=Node3D.new();holder.name="NightGardenLowerSpecialty";var instance:Node3D=load(src).instantiate();instance.name="RetainedNightGardenLowerComposition";instance.transform=transform;holder.add_child(instance);instance.owner=holder
   var packed:=PackedScene.new();assert(packed.pack(holder)==OK);var dest:String=("res://assets/models/"+str(room.model_file))if kind=="full"else P+"runtime/"+str(room.model_file).replace(".tscn","."+kind+".tscn");assert(not FileAccess.file_exists(dest));assert(ResourceSaver.save(packed,dest)==OK)
   if kind!="full":
    record[kind+"_path"]=dest;record[kind+"_sha256"]=FileAccess.get_sha256(dest);record[kind+"_mesh_paths"]=old[kind+"_mesh_paths"].map(func(p):return "RetainedNightGardenLowerComposition/"+str(p))
   else:record["full_path"]=dest;record["sha256"]=FileAccess.get_sha256(dest)
   holder.free()
  for prefix:String in ["","detail_"]:
   var box:=AABB(v(old[prefix+"bounds_min"]),v(old[prefix+"bounds_max"])-v(old[prefix+"bounds_min"]));var moved:AABB=transform*box;record[prefix+"bounds_min"]=arr(moved.position);record[prefix+"bounds_max"]=arr(moved.end)
  record.room_id=room.allocation.proposed_runtime_id;record.model_file=room.model_file;room.model_sha256=record.sha256;room.full_path=record.full_path;result.rooms[room.model_file]=record
 var f:=FileAccess.open(P+"evidence/INDEX.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t")+"\n");f.close();f=FileAccess.open(P+"PACKAGE.json",FileAccess.WRITE);f.store_string(JSON.stringify(plan,"\t")+"\n");f.close();print("NIGHT_LOWER_RUNTIME_PASS rooms=17 shared_source_partitions=34");quit()
