extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var world:=Node3D.new();root.add_child(world);var base:Node3D=load("res://scripts/group4_completion.gd").build(world,true,true)
 for i in range(10):await physics_frame
 var rows:Array=[]
 for bridge:Node3D in base.get_children():
  if not "Group4Bridge_" in str(bridge.name):continue
  var moving:AnimatableBody3D=bridge.moving
  var before:=moving.global_transform;var authoritative:Transform3D=PhysicsServer3D.body_get_state(moving.get_rid(),PhysicsServer3D.BODY_STATE_TRANSFORM)
  moving.sync_to_physics=false;moving.rotation.z=(1.0-bridge.fraction)*PI/2
  for i in range(3):await physics_frame
  var after:Transform3D=PhysicsServer3D.body_get_state(moving.get_rid(),PhysicsServer3D.BODY_STATE_TRANSFORM)
  rows.append({"bridge":str(bridge.name),"fraction":bridge.fraction,"before_node":str(before),"before_physics":str(authoritative),"after_unsynced_expected_stow_node":str(moving.global_transform),"after_unsynced_expected_stow_physics":str(after)})
 var f:=FileAccess.open("res://artifacts/group4_bridge_pose_diagnostic.json",FileAccess.WRITE);f.store_string(JSON.stringify({"purpose":"Diagnostic only; not travel acceptance","rows":rows}," "));f.close();print("GROUP4 BRIDGE PHYSICS DIAGNOSTIC",rows);quit()
