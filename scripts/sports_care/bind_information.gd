extends RefCounted
const Information = preload("amenity_information.gd")

## Call only after the imported section has its final world placement.
## Architectural staff access stays with the existing section owner.
static func bind(section: Node3D, manifest: Dictionary) -> Dictionary:
	var bound: Array[String] = []
	var rejected: Array[Dictionary] = []
	var seen: Dictionary = {}
	for spec in manifest.get("candidates", []):
		var identity := str(spec.get("id", ""))
		if spec.get("action", "") != "read_information":
			rejected.append({"id":identity,"reason":"Action requires existing specialized gameplay script"})
			continue
		if seen.has(identity):
			rejected.append({"id":identity,"reason":"Duplicate candidate identity"})
			continue
		seen[identity] = true
		var visual := section.find_child(str(spec.get("visual_node", "")), true, false) as MeshInstance3D
		var target := Information.new()
		section.add_child(target)
		if not target.configure(visual, spec):
			rejected.append({"id":identity,"reason":"Missing visible mesh or invalid fitted target/information"})
			target.free()
			continue
		target.name = identity
		bound.append(identity)
	return {"bound":bound,"rejected":rejected,"scope":"Authored information only; no authority/access, inventory, cleaning or persistent gameplay state"}
