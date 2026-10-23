extends SceneTree
var events:Array=[]
func entering(node:Node)->void:
 if node.name=="NearAttach":events.append("near_attached")
func leaving(node:Node)->void:
 if node.name=="OldRelease":events.append("old_released")
func _initialize()->void:call_deferred("run")
func run()->void:
 if not ProjectSettings.load_resource_pack("/tmp/route-activation-overlay.pck"):quit(2);return
 var base:="/workspace/Astraea-recovered-e6274e77-20261021/recovery/route_activation_fix_20261023/"
 OS.set_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE","1")
 var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var actor:=Node3D.new();actor.name="Player";actors.add_child(actor)
 var manager:Node=load("res://scripts/received_homes_20261015/residency.gd").new();host.add_child(manager);manager.host=host;manager.actor=actor;manager.set_physics_process(false)
 var near_room:=Node3D.new();near_room.name="NearAttach"
 var old_room:=Node3D.new();old_room.name="OldRelease";host.add_child(old_room)
 for spec in [{"room":near_room,"at":Vector3.ZERO,"attached":false},{"room":old_room,"at":Vector3(1000,0,0),"attached":true}]:
  var witness:RefCounted=load(base+"witness.gd").new();witness.visible=false
  manager.entries.append({"room":spec.room,"parent":host,"bounds":AABB(spec.at,Vector3.ONE),"witness":witness,"attached":spec.attached,"hidden_seconds":8.0,"meshes":0})
 host.child_entered_tree.connect(entering);host.child_exiting_tree.connect(leaving)
 manager.refresh(.2)
 var ok:bool=events==["old_released","near_attached"]and manager.entries[0].attached and not manager.entries[1].attached and systems.get_child_count()==0
 print("ROUTE_RELEASE_ORDER ",JSON.stringify({"pass":ok,"events":events,"near_preparation_synchronous":true,"visible_content_not_evicted":true}))
 OS.unset_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE");host.free();quit(0 if ok else 1)
