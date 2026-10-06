extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for f in range(50):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");budget.set_process(false)
	var target:=ship.find_child("GrandPoolFinishSource_DATUM_finish_light_RoofWash_451_Aft",true,false)as SpotLight3D
	var space:=ship.get_world_3d().direct_space_state;var chosen:Array=[]
	for lane in [Vector2(-45.9,52.5),Vector2(-45.9,46.2),Vector2(-20.5,46.2)]:
		for z in range(-458,-404,2):
			var p:=Vector3(lane.x,lane.y,z);var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.1,p-Vector3.UP*.2,1);q.exclude=[actor.get_rid()];var support:=space.intersect_ray(q)
			if support.is_empty() or absf(support.position.y-p.y)>.04:continue
			actor.position=p;budget.refresh();var visibility:bool=budget._has_visible_sample(target);var ranked:Array=[]
			for light in budget.sources:
				if not budget.requested_shadow[light.get_instance_id()] or not light.get_meta("fixture_powered",true):continue
				var reach:float=light.spot_range if light is SpotLight3D else(light.omni_range if light is OmniLight3D else120.0)
				ranked.append({"name":str(light.name),"score":p.distance_to(light.global_position)/maxf(reach,1.0)-(0.08 if light.visible else0.0),"selected":light.visible})
			ranked.sort_custom(func(a,b):return a.score<b.score)
			var rank:=-1
			for i in range(ranked.size()):
				if ranked[i].name==str(target.name):rank=i
			print("ROOF_SELECTION ",p," eligible ",visibility," selected ",target.visible," rank ",rank," floor ",support.collider.get_parent().name)
			if target.visible:chosen.append([p.x,p.y,p.z])
			if lane.y>50 and z==-444:
				print("ROOF_RANK_DETAIL ",ranked.slice(0,16))
				for origin in [target.global_position,target.get_meta("illumination_anchor")]:
					for offset in [Vector3(0,1.5,0),Vector3(0,.4,0),Vector3(.65,1,0),Vector3(-.65,1,0)]:
						var ray:=PhysicsRayQueryParameters3D.create(origin,p+offset,1);ray.exclude=[actor.get_rid()];var hit:=space.intersect_ray(ray)
						print("ROOF_VISIBILITY ",origin," toward ",p+offset," hit ","CLEAR"if hit.is_empty()else str(hit.collider.get_parent().get_path()))
	print("ROOF_SELECTED_SUPPORTED_VIEWS ",chosen);main.queue_free();await process_frame;quit(0)
