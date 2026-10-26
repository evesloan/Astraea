extends RefCounted
static func install(manager:Node)->Dictionary:
 assert(manager.get_script().resource_path=="res://scripts/night_garden_residency_20261022/manager.gd","Only exact current manager type may adopt opt-in successor")
 var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://precompiled_private_cells_20261026/FAMILY_COMPILE.json"))
 assert(FileAccess.get_sha256(report.index)==report.index_sha256)
 var preimages:Dictionary={}
 for property:Dictionary in manager.get_property_list():
  if int(property.usage)&PROPERTY_USAGE_SCRIPT_VARIABLE:preimages[property.name]=manager.get(property.name)
 var identity:=manager.get_instance_id()
 manager.set_script(load("res://precompiled_private_cells_20261026/manager.gd"))
 for key:StringName in preimages:manager.set(key,preimages[key])
 assert(manager.get_instance_id()==identity)
 for key:StringName in preimages:assert(manager.get(key)==preimages[key],"Original manager state changed")
 for row:Dictionary in report.rows:manager.compiled_records[row.model_file]=row
 for light:Light3D in manager.host.find_children("*","Light3D",true,false):manager.compiled_light_refs[light.get_instance_id()]=weakref(light)
 manager.get_tree().node_added.connect(manager.compiled_node_added)
 return {"manager_identity":identity,"preserved_state_fields":preimages.size(),"candidate_rooms":report.rows.size(),"policy":"Existing live details remain untouched; successor applies on next genuine load. Original near/visible admission, pending queues, release timing and shell/door/light IDs remain inherited."}
