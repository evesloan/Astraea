extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 for x in [-8.3,-8.01,-7.99,-7.9,-7.81,-7.79,-7.5]:
  for z in [287.0,287.1,288.7,290.3,290.4]:
   var record:Dictionary={"x":x,"z":z}
   for spec in [["floor",Vector3(x,16.55,z),Vector3(x,16.1,z)],["underside",Vector3(x,16.1,z),Vector3(x,16.55,z)],["roof",Vector3(x,20.3,z),Vector3(x,21.1,z)]]:
    var q:=PhysicsRayQueryParameters3D.create(spec[1],spec[2]);q.hit_back_faces=true;var h:=space.intersect_ray(q);record[spec[0]]={"owner":str(h.collider.get_path()),"point":[h.position.x,h.position.y,h.position.z],"normal":[h.normal.x,h.normal.y,h.normal.z]}if not h.is_empty()else{}
   rows.append(record)
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_core_threshold_20261011/INTERFACE_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify({"baseline_only":true,"rows":rows},"  "));print("Interface preflight complete");quit()
