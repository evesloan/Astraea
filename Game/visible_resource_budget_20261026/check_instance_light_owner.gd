extends SceneTree
const PACKAGE=preload("res://spatial_instance_cells_20261026/package.gd")
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var parent:=Node3D.new();parent.position=Vector3(80,56,-240);parent.rotation.y=.4;root.add_child(parent)
 var room:=Node3D.new();room.position=Vector3(7,3,-2);parent.add_child(room)
 var light:=OmniLight3D.new();light.position=Vector3(2,4,1);light.omni_range=8;room.add_child(light)
 var original:=light.global_position;var box:=AABB(original-Vector3.ONE,Vector3.ONE*2)
 var signature:=RULES.light_signature(box,1,[light])
 parent.remove_child(room)
 var parents:Dictionary={room.get_instance_id():parent};var recovered:Variant=PACKAGE.retained_position(light,parents)
 assert(recovered!=null and original.is_equal_approx(recovered))
 var descriptor:={"id":light.get_instance_id(),"kind":1,"mask":light.light_cull_mask,"reach":light.omni_range,"position":recovered}
 assert(RULES.light_signature(box,1,[descriptor])==signature)
 assert(PACKAGE.retained_position(light,{})==null,"Unknown detached owner must fail closed")
 parent.add_child(room);assert(light.global_position.is_equal_approx(original))
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"checks":4,"original_position":str(original),"recovered_position":str(recovered),"scope":"Detached potential light retains exact room-parent transform and light signature across reattachment; unknown owner refused"},"\t"));f.close()
 parent.free();await process_frame;quit()
