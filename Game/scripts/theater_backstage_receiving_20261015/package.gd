extends RefCounted
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/theater_backstage_receiving_20261015/BACKSTAGE_CONFIG.json"));assert(ship.get_node_or_null("ShipSpace/Districts/TheaterBackstageReceiving20261015")==null)
 for file in p.source_pins:assert(FileAccess.get_sha256("res://"+str(file))==str(p.source_pins[file]),"Exact source preimage "+str(file))
 # Sourcefloor triangles areavailable beforethefirstphysics sync duringdefault startup.
 var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 for row in p.required_end_preimages:
  var point:Vector3=v(row.at);var present:=false
  for region in floors.regions:
   if str(region.id)!=str(row.floor):continue
   assert(absf(float(region.floor_y)-point.y)<.002 and ship.has_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/"+str(row.floor)))
   for triangle in region.triangles:
    var polygon:=PackedVector2Array([Vector2(triangle[0][0],triangle[0][1]),Vector2(triangle[1][0],triangle[1][1]),Vector2(triangle[2][0],triangle[2][1])])
    if Geometry2D.is_point_in_polygon(Vector2(point.x,point.z),polygon):present=true;break
  assert(present,"Exact retained source floor preimage "+str(point))
 var file:String="res://assets/theater_backstage_receiving_20261015/"+str(p.file);assert(FileAccess.get_sha256(file)==str(p.model_sha256));var group:=Node3D.new();group.name="TheaterBackstageReceiving20261015";ship.get_node("ShipSpace/Districts").add_child(group);var model:Node3D=(load(file)as PackedScene).instantiate();model.name="RetainedFamilyBackstageReceiver";group.add_child(model);var meshes:Array[Node]=model.find_children("*","MeshInstance3D",true,false);assert(meshes.size()==int(p.meshes));load("res://scripts/static_contact_cache.gd").attach_group(model,meshes)
 var lights:Array[Light3D]=[]
 for row in p.lights:
  var lens:MeshInstance3D=model.find_child(str(row.lens),true,false);assert(lens!=null and (lens.global_transform*lens.get_aabb()).grow(.03).has_point(v(row.at)));var light:=SpotLight3D.new();light.name=str(row.name);group.add_child(light);light.position=v(row.at);light.rotation.x=-PI/2;light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range_m);light.spot_angle=float(row.spot_angle);light.visible=false;light.shadow_enabled=true;lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship);group.set_meta("default_main_adoption",true);group.set_meta("new_missing_only_floor_m2",float(p.policy.floor_area_m2));group.set_meta("new_room_ids_capacity_or_compiled_floor_changes",0);group.set_meta("source_door_closed_inactive",true);group.set_meta("primary_load_cart_venue_operation_or_final_art_accepted",false);return group
