from pathlib import Path
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');p=R/'Game/tests/validate_d04_commons_transition_fore_staff_connection.gd';s=p.read_text();old='await route(player,[[-28.25,14.25,-456.3],[-31.75,14.25,-456.3],[-31.75,14.25,-455.4],[-31.75,12,-446.8],[-34,12,-447],[-34,12,-449],[-53,12,-449],[-57.3,12,-449]],"fore_staff_used_return")';new='''await route(player,[[-28.25,14.25,-456.3],[-31.75,14.25,-456.3],[-31.75,14.25,-455.4],[-31.75,12,-446.8],[-34,12,-447],[-53,12,-447],[-57.3,12,-447]],"fore_staff_return_shared_clean_lane")
 # Independent used-lane fixture. No continuous court-to-used/stair separation claim.
 player.global_position=Vector3(-34,12.03,-449);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 await route(player,[[-53,12,-449],[-57.3,12,-449]],"independent_used_lane_to_original_staff")
 await aim(player,vec(p.fore_new_gates[0].control_at));record("normal_staff_used_control_target",player.interaction_target==used);await key_e()
 for i in range(100):await physics_frame
 record("normal_staff_used_controller_closed",used.open_fraction==0);await key_e()
 for i in range(100):await physics_frame
 record("normal_staff_used_controller_open",used.open_fraction==1)''';assert s.count(old)==1;s=s.replace(old,new).replace('"separate_upstream_clean_used_complete":false,','"separate_upstream_clean_used_complete":false,"used_lane_walk_is_independent_fixture":true,"continuous_court_to_used_return_accepted":false,');p.write_text(s)
