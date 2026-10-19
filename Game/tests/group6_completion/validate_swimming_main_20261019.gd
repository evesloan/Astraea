extends "res://tests/group6_completion/validate_swimming_20261019.gd"
func run()->void:
 output_name="MAIN"
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(20):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 await exercise(ship,actor)
func extra_checks(host:Node3D,actor:CharacterBody3D)->void:
 var floats:Node3D=host.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP/OccupiedSourceFloats")
 var body:RigidBody3D=floats.get_node("south_board")
 record("verified_arrival_from_swimming_package",host.arrive_at(body.seat.exit_world_position(),0))
 var approach:Dictionary=await walk_to(actor,body.seat.exit_world_position()+Vector3.LEFT*.3)
 record("river_remains_wading",approach.reached and actor.water_state=="wading" and not actor.swimming)
 await aim(actor,body.seat.global_position+Vector3.UP*.25);await key_e()
 record("source_float_mount_retained",actor.seated and body.seat.occupant==actor and is_equal_approx(body.mass,87) and actor.body_collider.rotation.is_zero_approx())
 for i in range(300):await physics_frame
 key(KEY_SPACE,true);await physics_frame;key(KEY_SPACE,false)
 for i in range(20):await physics_frame
 record("space_safe_exit_load_cleanup",not actor.seated and body.seat.occupant==null and is_equal_approx(body.mass,12) and actor.water_state=="wading")
 var leave:Dictionary=await walk_to(actor,vec(body.entry.dry_approach_xyz))
 record("river_ramp_returns_dry",leave.reached and leave.floor_contact and actor.water_state=="dry" and not actor.swimming)
