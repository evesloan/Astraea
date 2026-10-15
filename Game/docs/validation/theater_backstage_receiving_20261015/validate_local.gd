extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/theater_backstage_receiving_20261015/"
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",true));assert(ProjectSettings.load_resource_pack(D+"CANDIDATE_OVERLAY.zip",true));call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var ship:=Node3D.new();root.add_child(ship);var ss:=Node3D.new();ss.name="ShipSpace";ship.add_child(ss);var districts:=Node3D.new();districts.name="Districts";ss.add_child(districts);var systems:=Node.new();systems.name="ShipSystems";ship.add_child(systems)
 for spec in[["AST-CUL-005_static_003.glb",Vector3.ZERO],["AST-CUL-005_moving_003.glb",Vector3.ZERO],["AST-CIR-005_fore_midship_cinema2_d11.glb",Vector3(0,0,-272)]]:
  var model:Node3D=(load("res://assets/models/"+str(spec[0]))as PackedScene).instantiate();districts.add_child(model);model.position=spec[1]
  for mesh:MeshInstance3D in model.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
 var floors:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"));var regions:Array=[]
 for row in floors.regions:
  if str(row.deck)=="D11":regions.append(row)
 load("res://scripts/structural_floor_builder.gd").build_regions(ss,StandardMaterial3D.new(),StandardMaterial3D.new(),regions)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 var player:CharacterBody3D=load("res://scripts/player.gd").new();player.position=Vector3(-2.5,69.53,-249);ss.add_child(player);budget.configure(ship,player);await frames(3)
 var group:Node3D=load("res://scripts/theater_backstage_receiving_20261015/package.gd").build(ship);await frames(3);var space:=ship.get_world_3d().direct_space_state;var legs:Array=[]
 for goal:Vector3 in[Vector3(-6,69.5,-249),Vector3(-11.8,69.5,-249),Vector3(-11.8,69.5,-257),Vector3(-20,69.5,-257),Vector3(-30,69.5,-257),Vector3(-34.1,69.5,-257),Vector3(-30,69.5,-257),Vector3(-20,69.5,-257),Vector3(-11.8,69.5,-257),Vector3(-11.8,69.5,-249),Vector3(-6,69.5,-249),Vector3(-2.5,69.5,-249)]:
  var leg:Dictionary=await walk_to(player,goal);legs.append(leg)
  if not leg.reached or not leg.floor_contact:break
 var ok:bool=legs.size()==12 and legs.all(func(a):return a.reached and a.floor_contact);FileAccess.open(D+"LOCAL_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","limited_context":true,"actual_controller_legs":legs,"new_floor_m2":group.get_meta("new_missing_only_floor_m2"),"door_operation_accepted":false},"  "));print("PASS_BACKSTAGE_LOCAL_ORIGINAL_CONTROLLER"if ok else"FAIL_BACKSTAGE_LOCAL_ORIGINAL_CONTROLLER");quit(0 if ok else 1)
