extends SceneTree
class Probe:
 extends "res://scripts/lighting_budget.gd"
 var sampled:int=0
 func _has_visible_sample(light:Light3D)->bool:
  sampled+=1
  return light.get_meta("actual_local_fixture",false)
func _initialize()->void:call_deferred("run")
func run()->void:
 var room:=Node3D.new();root.add_child(room);var actor:=Node3D.new();room.add_child(actor);var b:=Probe.new();room.add_child(b);b.set_process(false)
 # Reproduce the received-source failure:32 distant imported sources with
 # effectively unbounded ranges,crowding every human-scale local fixture out.
 var far:Array=[];var local:Array=[]
 for i in range(40):
  var lamp:=OmniLight3D.new();room.add_child(lamp);lamp.position=Vector3(140+i,2,0);lamp.omni_range=1000;lamp.shadow_enabled=true;far.append(lamp)
 for i in range(8):
  var lamp:=OmniLight3D.new();room.add_child(lamp);lamp.position=Vector3(4+i*.25,2,0);lamp.omni_range=10;lamp.shadow_enabled=true;lamp.set_meta("actual_local_fixture",true);local.append(lamp)
 b.configure(room,actor)
 for lamp in local:assert(lamp.visible and lamp.shadow_enabled)
 for lamp in far:assert(not lamp.visible and not lamp.shadow_enabled and lamp.omni_range==1000)
 assert(b.previously_active.size()==8 and b.sampled==8 and b.MAX_VISIBILITY_CANDIDATES==32)
 # At the far-source destination,the old local lights cannot remain unshadowed.
 actor.position=Vector3(140,0,0);b.sampled=0;b.refresh()
 for lamp in local:assert(not lamp.visible and not lamp.shadow_enabled)
 for lamp in far:assert(not lamp.visible and not lamp.shadow_enabled)
 assert(b.previously_active.is_empty()and b.sampled<=32)
 var out={"status":"PASS","far_sources":40,"local_sources":8,"unbounded_original_ranges_preserved":true,"near_local_shadow_sources":8,"far_pose_shadow_sources":0,"visibility_sample_limit":32,"source_range_ranking_bound_m":32,"test_scope":"Behavioral regression for actual distant unbounded-range starvation and initial unshadowed-source leak;no image or performance acceptance"}
 FileAccess.open("res://artifacts/lighting_unbounded_range.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "));print(JSON.stringify(out));quit(0)
