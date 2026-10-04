extends RefCounted
# Fitted first dining groups within the retained Vesper programme. No service or NPC claim.
static func build(parent:Node3D,ship:Node3D) -> void:
	var root:=Node3D.new()
	root.name="D10_VesperDining_FirstGroups_WIP"
	root.set_meta("programme_key","D10_directory_08")
	root.set_meta("historical_room_id","D10_banquet7")
	root.set_meta("fitted_seats",54)
	root.set_meta("required_capacity",240)
	parent.add_child(root)
	var definitions:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D10_vesper_dining_subset.json"))
	for item in definitions.groups:
		var index:int=item.index
		var table:Node3D=ship.model(root,item.model,"VesperTable_"+str(index),Vector3(item.x,61,item.z))
		table.set_meta("persistent_id","D10_banquet7_table_%02d"%index)
		for seat in range(int(item.seats)):
			var marker:=table.find_child("DATUM_seat_anchor_"+str(seat),true,false)as Node3D
			assert(marker!=null)
			var direction:Vector3=table.global_position-marker.global_position
			var chair:Node3D=ship.model(root,"AST-DIN-002.glb","VesperChair_%d_%d"%[index,seat],marker.global_position,atan2(direction.x,direction.z))
			chair.set_meta("persistent_id","D10_banquet7_table_%02d_seat_%d"%[index,seat])
