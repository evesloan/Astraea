extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/theater_backstage_receiving_20261015/"
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",true));call_deferred("run")
func run()->void:
 var host:=Node3D.new();root.add_child(host)
 for spec in[["AST-CUL-005_static_003.glb",Vector3.ZERO],["AST-CUL-005_moving_003.glb",Vector3.ZERO],["AST-CIR-005_fore_midship_cinema2_d11.glb",Vector3(0,0,-272)]]:
  var model:Node3D=(load("res://assets/models/"+str(spec[0]))as PackedScene).instantiate();host.add_child(model);model.position=spec[1]
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"));var regions:Array=[]
 for row in data.regions:
  if str(row.deck)=="D11":regions.append(row)
 load("res://scripts/structural_floor_builder.gd").build_regions(host,StandardMaterial3D.new(),StandardMaterial3D.new(),regions)
 for i in range(3):await physics_frame
 var space:=host.get_world_3d().direct_space_state;var floor_samples:Array=[];var clearance:Array=[]
 for x in[-36.,-35.4,-35.,-34.8,-34.,-30.,-20.,-12.,-8.,-4.,-3.]:
  for z in[-258.4,-257.,-255.6,-252.,-250.,-249.]:
   var point:=Vector3(x,69.5,z);var h:=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02);floor_samples.append({"at":[x,69.5,z],"floor":str(h.collider.get_path())if not h.is_empty()else"","capsule_clear":capsule_clear(space,point)})
 for row in[["leg1",Vector3(-34.7,69.51,-258.5),Vector3(-11.8,73,-255.5)],["leg2",Vector3(-13.3,69.51,-257),Vector3(-10.3,73,-249)],["leg3",Vector3(-11.8,69.51,-250.5),Vector3(-3.85,73,-247.5)]]:
  var lo:Vector3=row[1];var hi:Vector3=row[2];var shape:=BoxShape3D.new();shape.size=hi-lo;shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=Transform3D(Basis.IDENTITY,(hi+lo)/2);var hits:Array=[]
  for h in space.intersect_shape(q,256):hits.append(str(h.collider.get_path()))
  clearance.append({"leg":row[0],"contacts":hits})
 FileAccess.open(D+"LOCAL_EXISTING_RECEIVING.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"LOCAL_EXACT_SOURCE_AND_D11_FLOOR_INVENTORY","limited_context":true,"floor_samples":floor_samples,"occupied_approach_contacts":clearance,"source_changed":false},"  "));print("PASS_BACKSTAGE_LOCAL_RECEIVING_INVENTORY");quit(0)
