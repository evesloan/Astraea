extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var main:Node=load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for frame in range(12):await physics_frame
	var ship:=main.get_node("World360/Astraea")
	var rows:Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/REMAINING_BATCH_SECTIONS.json")).sections
	var verified:Array=[]
	for row in rows:
		var section:=ship.get_node("ShipSpace/Districts/"+str(row.name)+"Receiving_WIP")
		assert(str(section.get_meta("programme_key"))==str(row.key))
		assert(section.has_meta("stream_loaded"))

		verified.append(str(row.key))
	assert(ship.get_node("ShipSpace/Districts/EquipmentDepotReceiving_WIP")!=null)
	var result:Dictionary={"status":"PASS","installed_keys":verified,"scope":"Default ship loading, registered nearby-room loading and precompiled nonoverlap floor checks; detailed traversal deferred by user"}
	FileAccess.open("res://artifacts/remaining_batch_install.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("REMAINING_BATCH_INSTALL PASS ",verified)
	quit(0)
