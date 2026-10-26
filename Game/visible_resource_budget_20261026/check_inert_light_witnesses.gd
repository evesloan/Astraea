extends SceneTree
class Residency extends Node:
 var entries:Array=[]
var output:String
func _initialize()->void:
 for a:String in OS.get_cmdline_user_args():
  if a.begins_with("--output="):output=a.substr(9)
 call_deferred("run")
func run()->void:
 var ship:=Node3D.new();root.add_child(ship)
 var systems:=Node.new();systems.name="ShipSystems";ship.add_child(systems)
 var residency:=Residency.new();residency.name="ReceivedRoomResidency";systems.add_child(residency)
 var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 var source:=Node3D.new();ship.add_child(source)
 var witnesses:Array=[]
 for i in 16:
  var light:=OmniLight3D.new();light.omni_range=1000;source.add_child(light);witnesses.append(light)
 var physical:Array[Light3D]=load("res://scripts/receiving_source_lights.gd").normalize(source,16)
 for light:Light3D in physical:budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
 var old:Dictionary=load("res://spatial_instance_cells_20261026/ship_lighting.gd").lighting(ship)
 var fixed:Dictionary=load("res://precompiled_private_cells_20261026/lighting_r002.gd").lighting(ship)
 assert(old.lights.size()==32 and fixed.lights.size()==16 and fixed.inert_witnesses_excluded==16)
 var rules=load("res://spatial_instance_cells_20261026/ship_rules.gd")
 var box:=AABB(Vector3(-1,-1,-1),Vector3(2,2,2))
 assert(rules.light_signature(box,1,old.lights)=="OVER_LIMIT")
 assert(rules.light_signature(box,1,fixed.lights)!="OVER_LIMIT")
 # A source that is functional or has an invalid witness contract must still count.
 var ordinary:Array=[]
 for i in 9:
  var light:=OmniLight3D.new();light.omni_range=8;ship.add_child(light);ordinary.append(light)
 var with_ordinary:Dictionary=load("res://precompiled_private_cells_20261026/lighting_r002.gd").lighting(ship)
 assert(rules.light_signature(box,1,with_ordinary.lights)=="OVER_LIMIT")
 for light:Light3D in ordinary:light.free()
 witnesses[0].visible=true
 var invalid:Dictionary=load("res://precompiled_private_cells_20261026/lighting_r002.gd").lighting(ship)
 assert(invalid.inert_witnesses_excluded==15 and invalid.lights.size()==17)
 assert(rules.light_signature(box,1,invalid.lights)=="OVER_LIMIT")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"status":"PASS","original_normalizer_used":true,"inert_witnesses":16,"functional_sources_preserved":16,"old_overflow":true,"corrected_capacity_pass":true,"nine_ordinary_sources_still_reject":true,"active_witness_still_counts":true,"scope":"Exact normalizer witness semantics, unchanged eight-source limit; actual ship omitted-witness counts and resulting batching remain to be measured."},"\t"));f.close();ship.free();quit()
