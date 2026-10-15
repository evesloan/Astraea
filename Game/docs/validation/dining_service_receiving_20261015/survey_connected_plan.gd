extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/dining_service_receiving_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func volume(space:PhysicsDirectSpaceState3D,x0:float,x1:float,z0:float,z1:float)->Array:
 var q:=PhysicsShapeQueryParameters3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(x1-x0,4.06,z1-z0);shape.margin=0.;q.shape=shape;q.margin=0.;q.transform.origin=Vector3((x0+x1)/2,62.57,(z0+z1)/2);var result:Array=[]
 for hit in space.intersect_shape(q,1024):result.append(str(hit.collider.get_path()))
 return result
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30);var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.set_physics_process(false);var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var rows:Array=[]
 for spec in[["D10_directory_01",-1.,-457.,-417.,-470.],["D10_directory_02",1.,-457.,-417.,-470.],["D10_directory_03",-1.,-241.,-201.,-176.]]:
  player.global_position=Vector3(spec[1]*50,61.03,(spec[2]+spec[3])/2);stream.prepare_position(player.global_position);await frames(4);player.global_position=Vector3(0,0,0);await frames(2);var side:float=spec[1];var clean:float=spec[2];var used:float=spec[3];var join:float=spec[4];var zlo:float=minf(join,clean-5.);var zhi:float=maxf(join,used+5.);var boxes:Array=[]
  for rect in[[54.001,66.,clean-5.,clean+7.],[54.001,66.,used-7.,used+5.],[66.,70.,zlo-2.15,zhi+2.15],[4.001,70.,join-2.15,join+2.15]]:
   var a:float=minf(side*rect[0],side*rect[1]);var b:float=maxf(side*rect[0],side*rect[1]);boxes.append({"rect":[a,b,rect[2],rect[3]],"old_contacts":volume(space,a,b,rect[2],rect[3])})
  var probes:Array=[]
  for z in[clean,used,join]:
   for x in[0.,3.5,4.5,8.,16.,24.,32.,40.,48.,53.5,54.5,56.,60.,64.,68.]:
    var point:=Vector3(side*x,61,z);var h:=ray(space,point+Vector3.UP*.02,point-Vector3.UP*.02);var under:=ray(space,point-Vector3.UP*.25,point-Vector3.UP*.65);probes.append({"at":[point.x,point.y,point.z],"capsule_clear":capsule_clear(space,point),"floor":str(h.collider.get_path())if not h.is_empty()else"","underframe_contact":str(under.collider.get_path())if not under.is_empty()else"","underframe_y":under.position.y if not under.is_empty()else null})
  rows.append({"programme_key":spec[0],"side":side,"clean_z":clean,"used_z":used,"axial_join_z":join,"volumes":boxes,"probes":probes})
 FileAccess.open(D+"PROPOSED_SERVICE_PREIMAGES.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"CURRENT_CONNECTED_D10_SERVICE_PLAN_PREIMAGES","production_changed":false,"sites":rows},"  "));print("PASS_D10_CONNECTED_SERVICE_PREIMAGE_SURVEY");quit(0)
