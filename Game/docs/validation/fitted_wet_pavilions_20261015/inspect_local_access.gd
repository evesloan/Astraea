extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"FITTED_CANDIDATE_OVERLAY_r006.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var ship:=Node3D.new();root.add_child(ship);var ss:=Node3D.new();ss.name="ShipSpace";ship.add_child(ss);var districts:=Node3D.new();districts.name="Districts";ss.add_child(districts)
 for spec in[["TidalGardenReceivingCandidate","AST-RES-TIDAL_lift_fit_r003.glb"],["QuietGroveReceivingCandidate","QUIET_GROVE_ARCHITECTURE_lift_r003.glb"]]:
  var site:=Node3D.new();site.name=spec[0];districts.add_child(site);var model:Node3D=(load("res://assets/models/"+spec[1])as PackedScene).instantiate();site.add_child(model)
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if mesh.get_meta("extras",{}).get("runtime_collision",false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 for i in range(3):await physics_frame
 var space:=ship.get_world_3d().direct_space_state;var floor_samples:Array=[]
 for x in[-97.,-96.6,-96.1,-95.7,-95.4]:
  for z in[-370.,-366.,-364.,-360.,-357.2,-356.3]:
   var point:=Vector3(x,102,z);var h:=ray(space,point+Vector3.UP*.03,point-Vector3.UP*.03);floor_samples.append({"at":str(point),"floor":str(h.collider.get_path())if not h.is_empty()else"","clear":capsule_clear(space,point)})
 var group:=Node3D.new();group.name="LocalWet";ss.add_child(group);var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(D+"FITTED_CONFIG_r006.json"));load("res://scripts/fitted_wet_pavilions_20261015/roof_successor.gd").apply(ship,group,p.roofs)
 for row in p.models:
  var model:Node3D=(load("res://assets/fitted_wet_pavilions_20261015/"+str(row.file))as PackedScene).instantiate();model.name=row.kit;group.add_child(model);var contacts:Array[Node]=[]
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):
   if not str(mesh.name).contains("Water_Illustrative"):contacts.append(mesh)
  load("res://scripts/static_contact_cache.gd").attach_group(model,contacts)
 for i in range(3):await physics_frame
 var entries:Array=[]
 for point:Vector3 in[Vector3(-96.1,102,-357.2),Vector3(-95.4,102,-357.2),Vector3(64.25,102,-382.7),Vector3(77.35,103.5,-375.6),Vector3(77.35,103.5,-375.8),Vector3(77.2,103.5,-375.6)]:
  var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,point+Vector3.UP*.925);var hits:Array=[]
  for hit in space.intersect_shape(q,32):hits.append(str(hit.collider.get_path()))
  entries.append({"at":str(point),"contacts":hits})
 FileAccess.open(D+"LOCAL_ACCESS_DIAGNOSTIC_r006.json",FileAccess.WRITE).store_string(JSON.stringify({"original_floor_samples":floor_samples,"fitted_entry_samples":entries,"limited_context":true},"  "));print("PASS_LOCAL_SOURCE_ACCESS_INVENTORY");quit(0)
