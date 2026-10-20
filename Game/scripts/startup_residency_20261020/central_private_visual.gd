extends RefCounted
static func contact_visual(parent: Node3D,file: String) -> Node3D:
 var ship: Node=parent
 while ship!=null and not ship.has_method("register_private_interior"):ship=ship.get_parent()
 assert(ship!=null,"Private interior successor requires the explicit startup owner")
 if ship.private_detail_residency.accepts(file):return ship.register_private_interior(parent,file)
 return load("res://scripts/star_atlas_specialty_first.gd").contact_visual(parent,file)
