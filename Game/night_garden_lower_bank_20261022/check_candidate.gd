extends SceneTree
const P:="res://night_garden_lower_bank_20261022/"
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var host:=Node3D.new();host.name="IsolatedCandidateNotMain";root.add_child(host)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);manager.set_physics_process(false)
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PACKAGE.json"));var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/INDEX.json")).rooms
 var checks:=0;var rest_ids:={};var door_ids:={};var records:Array=[]
 for room:Dictionary in package.rooms:
  var record:Dictionary=index[room.model_file];assert(not manager.index.has(room.model_file));assert(record.room_id==room.allocation.proposed_runtime_id);checks+=2
  manager.index[room.model_file]=record;manager.night_files[room.model_file]=true
  var home:=Node3D.new();home.name=record.room_id;host.add_child(home)
  var shell:Node3D=manager.register_room(home,room.model_file);load("res://quiet_grove_bank_20261022/adapter.gd").decorate_shell(shell,room)
  for id:String in room.allocation.proposed_rest_slot_ids:assert(not rest_ids.has(id));rest_ids[id]=true;checks+=1
  for door:Dictionary in room.doors:assert(not door_ids.has(door.persistent_id));door_ids[door.persistent_id]=true;checks+=1
  var entry:Dictionary=manager.entries[-1];var shell_id:int=shell.get_instance_id();manager._load_entry(entry);assert(is_instance_valid(entry.detail));checks+=1
  var meshes:int=entry.detail.find_children("*","MeshInstance3D",true,false).size();manager._release_entry(entry);assert(not is_instance_valid(entry.detail) and is_instance_valid(shell) and shell.get_instance_id()==shell_id);checks+=1
  records.append({"room_id":record.room_id,"detail_nodes":meshes,"load_release_pass":true,"shell_persistent":true})
 assert(manager.entries.size()==17 and rest_ids.size()==19 and door_ids.size()==53);checks+=3
 var report:={"status":"PASS isolated source candidate","checks":checks,"rooms":17,"reserved_rests":19,"door_ids":53,"load_release_cycles":17,"source_private_manager_unchanged":true,"records":records,"main_integrated":false,"receiving_contacts_tested":false,"hull_outlook_validated":false,"full_startup":false}
 var f:=FileAccess.open(P+"evidence/CANDIDATE_RUNTIME.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t")+"\n");f.close();print("NIGHT_LOWER_CANDIDATE ",checks," PASS; receiving held");host.free();await process_frame;quit()
