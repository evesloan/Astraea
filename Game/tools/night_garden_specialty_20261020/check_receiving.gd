extends SceneTree
var world:Node3D
var checks:Array=[]
func _initialize()->void:call_deferred("run")
func load_raw(file:String)->Node3D:
 var doc:=GLTFDocument.new();var state:=GLTFState.new()
 assert(doc.append_from_file("res://assets/models/"+file,state)==OK)
 var visual:Node3D=doc.generate_scene(state);world.add_child(visual)
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  if mesh.get_meta("extras",{}).get("runtime_collision",false):mesh.create_trimesh_collision()
 return visual
func ray(a:Vector3,b:Vector3)->Dictionary:
 return world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
func check(label:String,ok:bool)->void:checks.append({"name":label,"pass":ok})
func run()->void:
 world=Node3D.new();root.add_child(world)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE.json"))
 load_raw(p.receiving.model_file)
 for r in p.rooms:load_raw(r.model_file)
 await physics_frame;await physics_frame
 for sign in [-1,1]:
  for z in [14.2,19,25.9,28,30.1,38.5,42,56.8,71.6,86.4,94,97.1]:
   var x:=90.5 if z<26 else (87.0 if z==28 else 84.0)
   check("avenue_floor_%s_%s"%[sign,z],not ray(Vector3(x,93.2,z*sign),Vector3(x,92.8,z*sign)).is_empty())
  check("portal_clear_%s"%sign,ray(Vector3(90.5,94.5,sign*13.8),Vector3(90.5,94.5,sign*14.3)).is_empty())
 for r in p.rooms:
  var a:Dictionary=r.allocation;var z:float=(a.allocation_z[0]+a.allocation_z[1])/2.0
  var x:float=80.5 if a.allocation_x[0]<82 else 87.5
  check("room_floor_%s"%a.source_envelope_index,not ray(Vector3(x,93.2,z),Vector3(x,92.8,z)).is_empty())
  check("threshold_clear_%s"%a.source_envelope_index,ray(Vector3(84,94,z),Vector3(x,94,z)).is_empty())
 var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8
 for r in p.rooms:
  for slot in r.construction_statistics.rest_bounds:
   var b:Array=r.construction_statistics.rest_bounds[slot];var candidates:Array[Vector3]=[]
   for t in [.2,.5,.8]:
    var x:float=lerpf(b[0][0],b[1][0],t);var z:float=lerpf(b[0][2],b[1][2],t)
    candidates.append(Vector3(b[0][0]-.45,93.92,z));candidates.append(Vector3(b[1][0]+.45,93.92,z));candidates.append(Vector3(x,93.92,b[0][2]-.45));candidates.append(Vector3(x,93.92,b[1][2]+.45))
   var available:=false
   for point in candidates:
    if point.x<r.allocation.allocation_x[0]+.35 or point.x>r.allocation.allocation_x[1]-.35 or point.z<r.allocation.allocation_z[0]+.35 or point.z>r.allocation.allocation_z[1]-.35:continue
    var query:=PhysicsShapeQueryParameters3D.new();query.shape=capsule;query.transform=Transform3D(Basis.IDENTITY,point)
    if world.get_world_3d().direct_space_state.intersect_shape(query,1).is_empty() and not ray(Vector3(point.x,93.2,point.z),Vector3(point.x,92.8,point.z)).is_empty():available=true;break
   check("rest_local_stance_"+str(slot),available)
 var failed:=checks.filter(func(c):return not c.pass)
 var result:Dictionary={"scope":"Isolated regenerated geometry actual triangle contacts: avenue/room floor support, room thresholds, successor portals, and 0.6 m diameter / 1.8 m high local rest-access stances (not connected walks). No main hook, occupied traversal, door controllers or species acceptance.","checks":checks,"count":checks.size(),"failures":failed.size()}
 var f:=FileAccess.open("res://docs/validation/night_garden_specialty_20261020/FOCUSED_R002.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();print(JSON.stringify(result));quit(0 if failed.is_empty() else 1)
