extends RefCounted
const P:="res://star_atlas_living_commons_20261022/"
static func build(ship:Node3D)->void:
 assert(FileAccess.get_sha256(P+"PLAN.json")=="3c9225595fa4330d1c9743adeef350d16ff197879d6b39599effa3b1c3fa2f0f")
 assert(FileAccess.get_sha256(P+"runtime/StarAtlasLivingCommons_r001.scn")=="9d27213d63318d3f994c6f21aaea57f56c9e204f83ebdf337f2afa6726e987fc")
 assert(FileAccess.get_sha256("res://data/architecture/STAR_ATLAS_UPPER_COMMONS.json")=="c44c78c86c0a851bcde33699330ebb303d35d26b4114c3ada868d01843c0bc8d")
 var upper:Node3D=ship.get_node("ShipSpace/Districts/D15_D17_StarAtlasUpper_WIP")
 assert(upper.get_meta("source_part_count")==514 and upper.has_node("VIPDryClub_Source"))
 assert(not upper.has_meta("star_atlas_living_commons_20261022"))
 var addition:Node3D=load(P+"runtime/StarAtlasLivingCommons_r001.scn").instantiate();upper.add_child(addition)
 # Rebind the twelve existing upper fixtures to the unchanged shadow-source selector.
 var rebound:=0
 for light in upper.get_children():
  if light is SpotLight3D and str(light.name).begins_with("SA_D"):
   light.shadow_enabled=true;light.visible=false;rebound+=1
 assert(rebound==12)
 upper.set_meta("star_atlas_living_commons_20261022",{"study_groups":4,"window_lounges":2,"planted_edges":4,"shared_asset_placements":98,"source_fixtures_rebound":12,"added_lights":0,"new_guest_units":0,"new_reserved_rests":0,"visual_accepted":false})
