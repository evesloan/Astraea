extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	paused=true
	var checks:Dictionary={}
	var wall:Node3D=ship.find_child("SA_D17_SouthWall_0",true,false)
	checks["original_main_wall_exists"]=wall!=null
	var space:=ship.get_world_3d().direct_space_state
	var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-65,103.2,13.3),Vector3(-65,103.2,14.4)))
	checks["main_exit_still_sealed_exact_source_owner"]=wall!=null and not h.is_empty() and wall.is_ancestor_of(h.collider)
	var gap:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-65,102.1,14.2),Vector3(-65,101.7,14.2)))
	checks["onward_floor_still_missing"]=gap.is_empty()
	checks["candidate_not_installed"]=ship.find_child("D17_StandardPortal_WestRetainedWall",true,false)==null
	var homes:Node3D=ship.find_child("StarAtlasRoomCandidates",true,false)
	checks["original_85_homes_preserved"]=homes!=null and int(homes.get_meta("source_candidate_units",0))==85
	checks["original_221_rest_slots_preserved"]=homes!=null and int(homes.get_meta("source_rest_slots",0))==221
	checks["residency_stays_enabled"]=ship.get_node("ShipSystems/ReceivedRoomResidency").enabled
	var errors:Array=[]
	for k in checks:if not checks[k]:errors.append(k)
	var report={"status":"PASS"if errors.is_empty()else"FAIL","scope":"Actual-main bounded preservation, candidate held","checks":checks,"errors":errors,"ray_exclude_count":0,"source_wall_changed":false,"D17_standard_adopted":0,"D17_VIP_adopted":0,"whole_Group1_complete":false,"limits":"Full-suite historical Botanical sealed proof pins and final graphical/hardware acceptance remain open"}
	FileAccess.open("res://artifacts/d17_standard_portal_preservation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print(JSON.stringify(report));quit(0 if errors.is_empty()else 1)
