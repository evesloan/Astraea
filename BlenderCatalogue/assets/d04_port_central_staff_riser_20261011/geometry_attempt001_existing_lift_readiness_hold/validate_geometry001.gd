extends SceneTree
var failures:Array=[]
var checks:=0
var rows:Array=[]
func ck(ok:bool,label:String)->void:
 checks+=1
 if not ok:failures.append(label);print("FAIL ",label)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func rids(n:Node)->Array[RID]:
 var a:Array[RID]=[]
 if n is CollisionObject3D:a.append(n.get_rid())
 for c in n.get_children():a.append_array(rids(c))
 return a
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_STAFF_RISER.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var districts:Node3D=ship.get_node("ShipSpace/Districts");var old:Node3D=districts.get_node("LowerStaffNetwork_WIP");var enclosure:Node3D=old.get_node("LowerStaffEnclosure");var untouched:Dictionary={}
 for mesh:MeshInstance3D in enclosure.find_children("*","MeshInstance3D",true,false):
  if not str(mesh.name)in p.wall_patch.modified_cells:untouched[str(mesh.name)]={"faces":mesh.mesh.get_faces(),"transform":mesh.global_transform}
 var original_lift:Node3D=old.get_node("ForwardStaffLift");var stop_numbers:Array=original_lift.deck_numbers.duplicate();var stop_heights:Array=original_lift.floor_heights.duplicate();var old_lights:=old.find_children("*","Light3D",true,false).size()
 var n:Node3D=districts.get_node_or_null("D04PortCentralStaffCatchment")
 if n==null:n=load("res://scripts/d04_port_central_staff_riser.gd").build(ship,true)
 for i in range(120):await physics_frame
 for name in untouched:
  var mesh:MeshInstance3D=enclosure.find_child(name,true,false);ck(mesh!=null,"retained cell "+name)
  if mesh!=null:ck(mesh.mesh.get_faces()==untouched[name].faces and mesh.global_transform==untouched[name].transform,"retained exact cell faces/pose "+name)
 ck(original_lift.deck_numbers==stop_numbers and original_lift.floor_heights==stop_heights and original_lift.persistent_id==&"forward_staff_lift_001" and not original_lift.operation_ready,"old forward staff lift and blank stops unchanged")
 ck(old.find_children("*","Light3D",true,false).size()==old_lights,"old staff fixture lights retained")
 for part in p.parts:
  var m:MeshInstance3D=n.find_child(part.name,true,false);ck(m!=null,"part "+part.name)
  if m==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var a:AABB=m.global_transform*m.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"runtime part bounds "+part.name)
 var lift:Node3D=n.get_node("PortCentralStaffLift");ck(lift.floor_heights==[0.0,16.5]and lift.deck_numbers==[1,4]and lift.landing_gates.size()==2,"actual D01/D04 independent lift")
 for item in p.service_doors:n.get_node(item.name).interact(null)
 for i in range(100):await physics_frame
 for item in p.service_doors:ck(n.get_node(item.name).open_fraction==1.0,"new service door fully open "+item.name)
 var space:=ship.get_world_3d().direct_space_state;var all_new:=rids(n)
 for foot in p.support_preimages:
  for at in foot.corners:
   var v:=vec(at);var q:=PhysicsRayQueryParameters3D.create(v+Vector3.UP*.03,v-Vector3.UP*.03);q.exclude=all_new;q.hit_back_faces=true;var hit:=space.intersect_ray(q)
   ck(not hit.is_empty(),"hull foot corner contact "+str(at))
   if not hit.is_empty():ck(str(hit.collider.get_path())==foot.source_owner and abs(hit.position.y-v.y)<.001,"exact hull contact owner "+str(at))
 # Swept cabin body excludes controller-owned cabin, landing frames and gates.
 var lift_rids:=rids(lift)
 for i in range(34):
  var box:=BoxShape3D.new();box.size=Vector3(3.58,3.11,3.98);box.margin=.001
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(-25,float(i)*.5+1.38,-90));q.exclude=lift_rids
  var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"new cabin swept envelope y="+str(float(i)*.5));rows.append({"cabin_y":float(i)*.5,"blockers":hits.map(func(h):return str(h.collider.get_path()))})
 var samples:Array[Vector3]=[]
 for z in range(-107,-90):samples.append(Vector3(-57,0,z))
 for z in [-100.6,-97.8]:
  for x in range(-57,-20):samples.append(Vector3(x,0,z))
 for z in range(-100,-85):samples.append(Vector3(-21,0,z));samples.append(Vector3(-21,16.5,z))
 for spec in [[-63.2,-100.6],[-60.4,-97.8]]:
  for x in range(int(spec[0]),-20):samples.append(Vector3(x,16.5,spec[1]))
  samples.append(Vector3(spec[0],16.5,spec[1]))
  for z in range(int(spec[1]),-39):samples.append(Vector3(spec[0],16.5,z))
 for v in samples:
  var capsule:=CapsuleShape3D.new();capsule.radius=.5;capsule.height=2.4;capsule.margin=.001
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,v+Vector3.UP*1.24);var hits:=space.intersect_shape(q,64)
  ck(hits.is_empty(),"staff capsule clearance "+str(v));rows.append({"at":[v.x,v.y,v.z],"blockers":hits.map(func(h):return str(h.collider.get_path()))})
  var ray:=PhysicsRayQueryParameters3D.create(v+Vector3.UP*.05,v-Vector3.UP*.08);var hit:=space.intersect_ray(ray);ck(not hit.is_empty(),"staff supported floor "+str(v))
  if not hit.is_empty():ck(abs(hit.position.y-v.y)<.001,"correct staff floor datum "+str(v))
 var report:Dictionary={"status":"PASS"if failures.is_empty()else"HOLD","checks":checks,"failures":failures,"model_pins":p.model_pins,"preserved_original_staff_runtime_cells":untouched.size(),"old_staff_lift_and_lights_retained":true,"feet":p.support_preimages.size(),"four_corner_source_contacts":p.support_preimages.size()*4,"cabin_sweep_samples":34,"route_capsule_samples":samples.size(),"rows":rows,"limits":p.limits}
 FileAccess.open("res://artifacts/d04_port_central_staff_riser_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print("Staff geometry ",report.status," checks=",checks," failures=",failures.size());quit(0 if failures.is_empty()else 1)
