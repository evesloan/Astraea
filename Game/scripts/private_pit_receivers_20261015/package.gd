extends RefCounted
static func build(ship:Node3D)->Node3D:
 assert(ship.get_node_or_null("ShipSpace/ApprovedSixHouseReceiving")!=null)
 var root:=Node3D.new();root.name="PrivatePitReceivingFrames";ship.get_node("ShipSpace").add_child(root)
 var carriers:Node3D=(load("res://assets/private_pit_receivers_20261015/G2_PIT_CARRIERS_r002.glb")as PackedScene).instantiate()
 carriers.name="NewUnderfloorCarriers";root.add_child(carriers)
 load("res://scripts/static_contact_cache.gd").attach_group(carriers,carriers.find_children("*","MeshInstance3D",true,false))
 for key in["787","792","794","795","797"]:
  var slab:Node3D=(load("res://assets/group2_private_vertical/PIT_"+key+"_r001.glb")as PackedScene).instantiate()
  slab.name="RetainedPitReceiver_"+key;root.add_child(slab)
  load("res://scripts/static_contact_cache.gd").attach_group(slab,slab.find_children("*","MeshInstance3D",true,false))
 root.set_meta("source_slabs_preserved",5)
 root.set_meta("new_profiled_underfloor_members",10)
 root.set_meta("capacity_or_operation_admitted",false)
 root.set_meta("structural_capacity_accepted",false)
 root.set_meta("default_main_adoption",true)
 return root
