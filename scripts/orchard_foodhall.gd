extends RefCounted
# The reserved240 places are real candidate chair positions, not a service/NPC claim.
static func build(parent:Node3D,ship:Node3D)->void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D10_orchard_foodhall.json"))
	var root:=Node3D.new()
	root.name="D10_OrchardFoodHall_WIP"
	root.set_meta("programme_key","D10_directory_04")
	root.set_meta("historical_room_id","D10_banquet3")
	root.set_meta("candidate_places",240)
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-DIN-008.glb","OrchardFoodHallArchitecture",Vector3(8,61,-250))
	for marker in architecture.find_children("DATUM_light_*","Node3D",true,false):
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="OrchardFoodLight_"+str(marker.name)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		var staff:bool="work_" in str(marker.name) or "staff_" in str(marker.name)
		light.light_color=Color(.85,.92,1)if staff else Color(1,.96,.91)
		light.light_energy=1.05 if staff else 1.35
		light.spot_range=5 if staff else 8
		light.spot_angle=70
		light.shadow_enabled=true
	for g in data.candidate_groups:
		var file:String="AST-DIN-007.glb"if g.kind=="communal10"else"AST-DIN-001_six.glb"
		var table:Node3D=ship.model(root,file,"OrchardTable_"+str(g.index),Vector3(g.x,61,g.z))
		table.set_meta("persistent_id",str(g.id))
		for seat in range(int(g.seats)):
			var marker:=table.find_child("DATUM_seat_anchor_"+str(seat),true,false)as Node3D
			assert(marker!=null)
			var direction:Vector3=table.global_position-marker.global_position
			var chair:Node3D=ship.model(root,"AST-DIN-002.glb","OrchardChair_%s_%s"%[g.index,seat],marker.global_position,atan2(direction.x,direction.z))
			chair.set_meta("persistent_id",str(g.id)+"_seat_%02d"%seat)
			load("res://scripts/dining_chair_visual.gd").apply(chair)
	for key in ["staff_door","pavilion_door_0","pavilion_door_1"]:
		var marker:=architecture.find_child("DATUM_"+key,true,false)as Node3D
		var door:Node3D=load("res://scripts/service_door.gd").new()
		door.name="OrchardFood_"+key
		door.persistent_id=StringName("D10_banquet3_"+key)
		door.desired_open=false
		door.open_fraction=0
		door.position=marker.global_position
		door.rotation.y=-PI/2
		root.add_child(door)
	for i in range(2):
		var beverage:=architecture.find_child("DATUM_beverage_"+str(i),true,false)as Node3D
		var machine:Node3D=ship.model(root,"AST-HSP-003.glb","OrchardBeverage_"+str(i),beverage.global_position,-PI/2)
		machine.set_meta("interaction_status","Static serving fixture; dispensing and guest service pending")
		var storage:=architecture.find_child("DATUM_serviceware_"+str(i),true,false)as Node3D
		ship.model(root,"AST-HSP-005.glb","OrchardServiceware_"+str(i),storage.global_position,-PI/2)

	# Fitted perimeter dining edges reuse the authored acoustic family, aligned
	# to actual small-table groups rather than enclosing a new generic box.
	var bays: Array = []
	for x in [27.8,34.0,40.2,46.0]:bays.append({"p":Vector3(x-2.7,61,-249.87),"yaw":0.0})
	for x in [29.0,36.0,43.0]:bays.append({"p":Vector3(x+2.7,61,-182.13),"yaw":PI})
	for z in [-229.0,-205.0,-199.0,-193.0,-187.0]:bays.append({"p":Vector3(8.13,61,z+2.7),"yaw":PI/2})
	for i in range(bays.size()):
		var bay:Node3D=ship.model(root,"AST-DIN-005.glb","OrchardAcousticBay_%02d"%i,bays[i].p,bays[i].yaw)
		var source:=bay.find_child("DATUM_wash_source",true,false)as Node3D
		var receiver:=bay.find_child("DATUM_wall_receiver",true,false)as Node3D
		var wash:=SpotLight3D.new()
		root.add_child(wash)
		wash.name="OrchardPerimeterWash_%02d"%i
		wash.global_position=source.global_position
		wash.look_at(receiver.global_position)
		wash.set_meta("illumination_anchor",receiver.global_position)
		wash.spot_range=3.5
		wash.spot_angle=65
		wash.light_energy=.8
		wash.light_color=Color(1,.95,.9)
		wash.shadow_enabled=true
