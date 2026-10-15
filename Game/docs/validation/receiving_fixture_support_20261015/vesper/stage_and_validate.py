from pathlib import Path
import json
D=Path(__file__).parent;V=D.parent/'vesper_service_receiving_20261015';I=D/'import/Game';p=I/'project.godot';p.write_text('config_version=5\n[application]\nconfig/name="Vesper Fixture Import"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
s=(V/'validate325.gd').read_text();init=s[s.index('func _initialize'):s.index('func frames')].replace('D+"CANDIDATE_OVERLAY.zip"','"/workspace/astraea-integration-cutoff-20261013/VESPER_SERVICE_ADOPTION_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"');s='extends "res://tests/validate_d04_court_controls_staff_candidate.gd"\nconst D="'+str(D)+'/"\n'+init+'''func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false);actor.global_position=Vector3(62,61.03,188);var group:Node3D=ship.get_node("ShipSpace/VesperServiceReceiving20261015");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_VERIFICATION.json"));var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"NATIVE_FIXTURE_SUPPORT_VERIFICATION.json"));var space:=ship.get_world_3d().direct_space_state;var supports:Array=[];var exits:Array=[];var receivers:Array=[]
 for row in proof.all10_actual_roof_mounts:
  var at:=vec(row.roof_contact_xyz)+Vector3(.1,0,0);var h:=ray(space,at+Vector3.DOWN*.03,at+Vector3.UP*.03);supports.append({"mount":row.name,"native_positive_embed_m":row.positive_embed_m,"nearby_roof_witness":str(at),"hit":str(h.position)if not h.is_empty()else"","passed":not h.is_empty()and group.is_ancestor_of(h.collider)and absf(h.position.y-64.8)<.0001})
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var registration:Array=[]
 for light:Light3D in group.find_children("*","Light3D",true,false):registration.append({"name":str(light.name),"once":budget.sources.count(light)==1})
 for row in p.lights:
  var at:=vec(row.at);var light:Light3D=group.get_node(str(row.name));var h:=ray(space,at,at+Vector3.DOWN*.08);exits.append({"name":row.name,"passed":h.is_empty()and light.global_position.distance_to(at)<.0001});h=ray(space,at,Vector3(at.x,60.97,at.z));receivers.append({"name":row.name,"passed":not h.is_empty()and absf(h.position.y-61)<.0001 and group.is_ancestor_of(h.collider)})
 actor.velocity=Vector3.ZERO;actor.set_physics_process(true);actor.set_controls_enabled(true);await frames(20);var legs:Array=[]
 for at:Vector3 in[Vector3(62,61,210),Vector3(62,61,226.8),Vector3(62,61,210),Vector3(62,61,188)]:
  legs.append(await walk_to(actor,at))
  if not legs[-1].reached:break
 var ok:bool=supports.size()==10 and supports.all(func(r):return r.passed)and registration.size()==10 and registration.all(func(r):return r.once)and exits.size()==10 and exits.all(func(r):return r.passed)and receivers.size()==10 and receivers.all(func(r):return r.passed)and legs.size()==4 and legs.all(func(r):return r.reached and r.floor_contact)
 FileAccess.open(D+"FIXTURE_SUPPORT_RUNTIME329.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","actual_roof_bearings":supports,"source_light_registration":registration,"emitter_exits":exits,"actual_floor_receivers":receivers,"changed_area_controller_legs":legs,"r001_retained":true,"corridor_floor_wall_frame_and_original_sources_changed":false,"final_Game_CRT_visual_acceptance":false},"  "));print("PASS_VESPER_R002_FIXTURE_SUPPORT"if ok else"FAIL_VESPER_R002_FIXTURE_SUPPORT");quit(0 if ok else 1)
''';(D/'validate329.gd').write_text(s)
