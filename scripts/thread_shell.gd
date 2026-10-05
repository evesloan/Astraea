extends RefCounted
# Partial real fore retail destination; no checkout, NPC use or final-art claim.
static func build(parent:Node3D,ship:Node3D) -> void:
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D09_thread_shell.json"))
	var root:=Node3D.new()
	root.name="D09_ThreadAndShell_WIP"
	root.set_meta("programme_key",data.programme_key)
	root.set_meta("historical_room_id",data.historical_room_id)
	parent.add_child(root)
	var architecture:Node3D=ship.model(root,"AST-RTL-007.glb","ThreadShellArchitecture",Vector3(8,52.5,-216))
	var glass:=ShaderMaterial.new()
	glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for part in architecture.find_children("*","MeshInstance3D",true,false):
		if "glass" in str(part.name).to_lower():part.material_override=glass
	for marker in architecture.find_children("DATUM_light_*","Node3D",true,false):
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="ThreadShellLight_"+str(marker.name)
		light.global_position=marker.global_position
		light.rotation.x=-PI/2
		var staff:bool="staff" in str(marker.name)
		light.light_color=Color(.86,.93,1) if staff else Color(1,.95,.88)
		light.light_energy=.85 if "private" in str(marker.name) else 1.10
		light.spot_range=5 if staff or "private" in str(marker.name) else 10
		light.spot_angle=75
		light.shadow_enabled=true
	for marker in architecture.find_children("DATUM_bounce_*","Node3D",true,false):
		var light:=SpotLight3D.new()
		root.add_child(light)
		light.name="ThreadShellCeilingWash_"+str(marker.name)
		light.global_position=marker.global_position
		light.rotation.x=PI/2
		light.light_color=Color(1,.96,.90)
		light.light_energy=2.4
		light.spot_range=7
		light.spot_angle=75
		light.shadow_enabled=true
	for index in range(data.columns.size()):
		var p:Array=data.columns[index]
		var column:Node3D=ship.model(root,"AST-STR-001-H826.glb","ThreadShellBearing_"+str(index),Vector3(p[0],52.5,p[1]))
		for i in [1,2]:
			var marker:=column.find_child("DATUM_light_"+str(i),true,false)as Node3D
			var light:=SpotLight3D.new()
			root.add_child(light)
			light.name="ThreadShellBearingLight_%s_%s"%[index,i]
			light.global_position=marker.global_position
			light.rotation.x=-PI/2
			light.light_color=Color(1,.95,.88)
			light.light_energy=.85
			light.spot_angle=65
			light.spot_range=10
			light.shadow_enabled=i==1
	for pod in data.fitting_pods:
		var door:Node3D=load("res://scripts/guest_entry_door.gd").new()
		door.name=str(pod.id)+"_Door"
		door.persistent_id=StringName(str(pod.id)+"_door")
		door.visual_file="AST-DOR-002_wide.glb"
		door.leaf_width=1.18
		door.leaf_travel=1.24
		door.enclosure_width=5.16
		door.door_description="fitting-room door"
		door.desired_open=false
		door.open_fraction=0
		door.position=Vector3(pod.front_x,52.5,pod.center_z)
		door.rotation.y=-PI/2
		root.add_child(door)
	for key in ["service_door","staff_entry_door"]:
		var marker:=architecture.find_child("DATUM_"+key,true,false)as Node3D
		var door:Node3D=load("res://scripts/service_door.gd").new()
		door.name="ThreadShell_"+key
		door.persistent_id=StringName("D09_tailor3_"+key)
		door.desired_open=false
		door.open_fraction=0
		door.position=marker.global_position
		door.rotation.y=-PI/2
		root.add_child(door)
	var count:=0
	var variants:Array[String]=["AST-RTL-008.glb","AST-RTL-008_teal_weave.glb","AST-RTL-008_oatmeal_weave.glb"]
	for bank in range(2):
		for index in [2,4,6,8,10]:
			var marker:=architecture.find_child("DATUM_fabric_%s_%s"%[bank,index],true,false)as Node3D
			var center:=Vector2(19,-226 if bank==0 else -206)
			var yaw:float=atan2(marker.global_position.x-center.x,marker.global_position.z-center.y)
			var stock:Node3D=ship.model(root,variants[count%3],"ThreadShellTextile_"+str(count),marker.global_position,yaw)
			stock.set_meta("persistent_id","D09_tailor3_textile_%02d"%count)
			stock.set_meta("interaction_status","Static hanging sample; cloth simulation, pickup, inventory and sale pending")
			count+=1
