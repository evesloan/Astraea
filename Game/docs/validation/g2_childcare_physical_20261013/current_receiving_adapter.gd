# Physical consumer; source fixture/admission guard above remains unchanged.
static func build_on_current_receiver(ship:Node3D)->Node3D:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_family_childcare/COMPONENT_r001.json"))
 assert(FileAccess.get_sha256("res://assets/models/FAMILY_TERRACE_ARCHITECTURE_lift_r003.glb")==str(data.source_receiver_sha256))
 assert(FileAccess.get_sha256("res://assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb")==str(data.export_sha256))
 assert(FileAccess.get_sha256("res://assets/models/"+str(data.door.file))==str(data.door.sha256))
 var packed:PackedScene=load("res://assets/group2_family_childcare/FAMILY_CHILDCARE_r001.glb");var fitting:PackedScene=load("res://assets/models/"+str(data.door.file));assert(packed!=null and fitting!=null)
 var house:Node3D=ship.get_node_or_null("ShipSpace/Districts/FamilyTerraceReceivingCandidate");assert(house!=null and house.global_transform.is_equal_approx(Transform3D.IDENTITY))
 assert(house.get_node_or_null("Group2ChildcarePhysicalReceiving")==null)
 var root:=Node3D.new();root.name="Group2ChildcarePhysicalReceiving";house.add_child(root)
 var visual:Node3D=packed.instantiate();visual.name="FAMILY_CHILDCARE_r001";root.add_child(visual)
 load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
 var closed:Node3D=fitting.instantiate();closed.name="CareEntry_StaticClosedSource";closed.position=Vector3(data.door.world_xyz[0],data.door.world_xyz[1],data.door.world_xyz[2]);root.add_child(closed)
 load("res://scripts/static_contact_cache.gd").attach_group(closed,closed.find_children("*","MeshInstance3D",true,false))
 assert(closed.find_child("LEAF_LEFT",true,false).position.is_equal_approx(Vector3(-.6,0,0))and closed.find_child("LEAF_RIGHT",true,false).position.is_equal_approx(Vector3(.6,0,0)))
 var lights:Array[Light3D]=[]
 for row in data.lights:
  assert(visual.find_child(str(row.source_mesh),true,false)!=null)
  var light:=OmniLight3D.new();light.name=str(row.source_mesh)+"_PhysicalSource";root.add_child(light);light.position=Vector3(row.world_xyz[0],row.world_xyz[1],row.world_xyz[2]);light.omni_range=row.range;light.light_energy=row.energy;light.light_color=Color(1,.86,.68);light.shadow_enabled=false;light.visible=false;light.set_meta("fixture_powered",true);lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 root.set_meta("default_main_adoption",false);root.set_meta("new_floor_owners",0);root.set_meta("new_registered_rooms_beds_or_capacity",0);root.set_meta("proposed_day_rest_fittings",4);root.set_meta("guardian_supervision_admission_or_child_programme_accepted",false);root.set_meta("entry_or_inside_egress_operation_admitted",false);root.set_meta("food_hygiene_or_staff_services_admitted",false);root.set_meta("source_fixture_id_bound_to_production",false)
 return root
