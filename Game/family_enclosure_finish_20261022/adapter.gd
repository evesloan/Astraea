extends RefCounted
const P:="res://family_enclosure_finish_20261022/"
static func build(ship:Node3D)->void:
 assert(FileAccess.get_sha256("res://family_reading_garden_20261022/adapter.gd")=="5c17ac6250fe1fafe3b7245e59c291aac7d89466d6be0adc741ec18ffa51d90b")
 assert(FileAccess.get_sha256(P+"PLAN.json")=="f8b0df7f1afe3da17d0e8cd2a7b02aeda6acead4aa4cd03e480899b9146d8de4")
 assert(FileAccess.get_sha256(P+"runtime/FamilyEnclosure_r001.scn")=="a69da8a37fabfe10e3fd6ecd5b472ed8ef05518b65e4398caa053e707f5d3897")
 load("res://family_reading_garden_20261022/adapter.gd").build(ship)
 var house:Node3D=ship.get_node("ShipSpace/Districts/FamilyTerraceReceivingCandidate")
 assert(not house.has_meta("family_enclosure_finish_20261022"))
 var enclosure:Node3D=load(P+"runtime/FamilyEnclosure_r001.scn").instantiate();enclosure.name="FamilyEnclosureFinish20261022";house.add_child(enclosure)
 assert(enclosure.find_children("*","SpotLight3D",true,false).size()==2)
 # Improve the real canopy illumination, preserving positions, power ownership and selection budget.
 var reading:Node3D=house.get_node("FamilyForwardCourt20261022")
 for light:OmniLight3D in reading.find_children("*","OmniLight3D",true,false):
  assert(is_equal_approx(light.light_energy,1.1) and is_equal_approx(light.omni_range,30))
  light.light_energy=2.0;light.omni_range=38
 house.set_meta("family_enclosure_finish_20261022",{"arches":2,"retained_piers":3,"elevated_planters":6,"added_plants":78,"additional_wash_lights":2,"global_light_budget":8,"visual_accepted":false})
