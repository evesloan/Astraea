extends RefCounted
const P := "res://orchard_tram_interior_20261025/r003/"

static func raw(path: String) -> Node3D:
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	if document.append_from_file(ProjectSettings.globalize_path(path),state)!=OK:return null
	return document.generate_scene(state)

static func apply(ship: Node3D) -> bool:
	var districts:=ship.get_node("ShipSpace/Districts")
	var specs: Array = [
		["D09_D10_OrchardExchange_WIP","OrchardExchangeArchitecture","Orchard_receiving_exact.glb","DATUM_light_1"],
		["D09_ThreadAndShell_WIP","ThreadShellArchitecture","Retail_receiving_exact.glb","DATUM_light_public_0"]]
	for spec: Array in specs:
		var room: Node3D=districts.get_node(spec[0])
		var wrapper: Node3D=room.get_node(spec[1])
		if wrapper.has_meta("orchard_route_receiving"):push_error("Duplicate Orchard receiving");return false
		var prior: Node3D=wrapper.find_child(spec[3],true,false)
		if prior==null:push_error("Original physical light marker absent");return false
		var old_position:=prior.global_position
		var overrides: Dictionary={}
		for mesh: MeshInstance3D in wrapper.find_children("*","MeshInstance3D",true,false):
			if mesh.material_override!=null:overrides[str(mesh.name)]=mesh.material_override
		var successor:=raw(P+spec[2])
		if successor==null:return false
		# Preserve the wrapper, room identities, original doors, stock and lifts.
		for child: Node in wrapper.get_children():child.free()
		wrapper.add_child(successor)
		for mesh: MeshInstance3D in successor.find_children("*","MeshInstance3D",true,false):
			if overrides.has(str(mesh.name)):mesh.material_override=overrides[str(mesh.name)]
		ship._static_contacts(successor)
		var marker: Node3D=successor.find_child(spec[3],true,false)
		if marker==null:return false
		var moved:=0
		for light: SpotLight3D in room.find_children("*","SpotLight3D",true,false):
			if light.global_position.distance_to(old_position)<.0001:
				light.global_position=marker.global_position
				light.spot_range=9 if spec[0]=="D09_D10_OrchardExchange_WIP" else 10
				light.set_meta("source_fixture_marker",spec[3]);moved+=1
			if spec[0]=="D09_ThreadAndShell_WIP" and str(light.name)=="ThreadShellCeilingWash_DATUM_bounce_public_0":
				var bounce: Node3D=successor.find_child("DATUM_bounce_public_0",true,false)
				var receiver: Node3D=successor.find_child("DATUM_receiver_public_0",true,false)
				if bounce==null or receiver==null:return false
				light.global_position=bounce.global_position
				light.set_meta("illumination_anchor",receiver.global_position)
		if moved!=1:push_error("Expected exactly one matching retained fixture light");return false
		wrapper.set_meta("orchard_route_receiving",true)
	return true
