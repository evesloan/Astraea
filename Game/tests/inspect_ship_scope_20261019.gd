extends SceneTree
# Read-only receiving survey; includes cached/detached rooms without forcing them all resident.
var rows:Array=[]
var visited:Dictionary={}
func _initialize()->void:call_deferred("run")
func scan(node:Node,path:String)->void:
	if visited.has(node.get_instance_id()):return
	visited[node.get_instance_id()]=true
	var meta:Dictionary={}
	for key in node.get_meta_list():
		var value:Variant=node.get_meta(key)
		if typeof(value) in [TYPE_STRING,TYPE_STRING_NAME,TYPE_INT,TYPE_FLOAT,TYPE_BOOL,TYPE_ARRAY,TYPE_DICTIONARY,TYPE_PACKED_STRING_ARRAY]:
			if str(value).length()<4000:meta[str(key)]=value
	var source:String=node.scene_file_path
	if not meta.is_empty() or not source.is_empty() or path.count("/")<3:
		rows.append({"path":path,"class":node.get_class(),"scene_source":source,"metadata":meta,"attached":node.is_inside_tree()})
	for child in node.get_children():scan(child,path+"/"+str(child.name))
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(60):await physics_frame
	var ship:Node=main.get_node("World360/Astraea")
	assert(ship.get_node("ReceivedSectionInstallation").get_meta("installation_ready",false))
	scan(ship,"")
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	for entry in residency.entries:
		scan(entry.room,str(ship.get_path_to(entry.parent))+"/"+str(entry.room.name))
	var report:Dictionary={"base_commit":"3833e6897e66420814a51f7b2c0c3a425f9967a1","scope":"Read-only actual main-scene resource and metadata survey including cached rooms. Presence is not complete interior, route, capacity or visual acceptance.","rows":rows,"visited_nodes":visited.size(),"residency":residency.statistics()}
	FileAccess.open("/workspace/ship-scope-reconciliation-20261019/RUNTIME_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("SHIP_SCOPE_SURVEY nodes=",visited.size()," evidence_rows=",rows.size())
	quit()
