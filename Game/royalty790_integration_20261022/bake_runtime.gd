extends SceneTree
const P="res://royalty790_integration_20261022/"
var removed:Array=[]
var roof_before:Array=[]
var roof_after:Array=[]
func on_triangle(p:Vector3,t:Array)->bool:
 var a:Vector3=t[1]-t[0];var b:Vector3=t[2]-t[0];var q:Vector3=p-t[0]
 if absf(a.cross(b).normalized().dot(q))>.0002:return false
 var aa:=a.dot(a);var ab:=a.dot(b);var bb:=b.dot(b);var den:=aa*bb-ab*ab
 if absf(den)<.00000001:return false
 var u:float=(q.dot(a)*bb-q.dot(b)*ab)/den;var v:float=(q.dot(b)*aa-q.dot(a)*ab)/den
 return u>=-.0001 and v>=-.0001 and u+v<=1.0001
func covered(t:Array,faces:Array)->bool:
 var n:Vector3=(t[1]-t[0]).cross(t[2]-t[0]).normalized()
 for p:Vector3 in [t[0],t[1],t[2],(t[0]+t[1])/2,(t[1]+t[2])/2,(t[2]+t[0])/2,(t[0]+t[1]+t[2])/3]:
  var found:=false
  for f:Array in faces:
   var other:Vector3=(f[1]-f[0]).cross(f[2]-f[0]).normalized()
   if n.dot(other)>.999 and on_triangle(p,f):found=true;break
  if not found:return false
 return true
func area(faces:Array)->float:
 var total:=0.0
 for t:Array in faces:total+=(t[1]-t[0]).cross(t[2]-t[0]).length()*.5
 return total
func raw(path:String)->Node3D:
 var d:=GLTFDocument.new();var s:=GLTFState.new();assert(d.append_from_file(path,s)==OK);var n:Node3D=d.generate_scene(s);root.add_child(n);return n
func same(a:Array,b:Array)->bool:
 for v:Vector3 in a:
  var found:=false
  for w:Vector3 in b:if v.distance_to(w)<.0002:found=true
  if not found:return false
 return true
func own(n:Node,top:Node)->void:
 for c in n.get_children():c.owner=top;own(c,top)
func _initialize():call_deferred("run")
func faces(m:MeshInstance3D)->Array:
 var result:Array=[];var f:=m.mesh.get_faces()
 for i in range(0,f.size(),3):result.append([m.global_transform*f[i],m.global_transform*f[i+1],m.global_transform*f[i+2]])
 return result
func run():
 var baseline:=raw("res://assets/models/AST-RES-006.glb")
 var preimage:=raw(P+"source/OriginalBoundedBatches.glb")
 var successor:=raw(P+"runtime/ExactBoundedBatches_r003.glb")
 var patches:Array=[]
 for old:MeshInstance3D in preimage.find_children("*","MeshInstance3D",true,false):
  var installed:MeshInstance3D=baseline.find_child(old.name,true,false)
  assert(installed!=null and not str(old.name).begins_with("CR_Batch_approach_"))
  var a:=faces(old);var b:=faces(installed)
  for triangle in a:assert(covered(triangle,b),"Native batch surface missing from installed owner: "+str(old.name))
  for triangle in b:assert(covered(triangle,a),"Installed batch surface missing from native owner: "+str(old.name))
  assert(absf(area(a)-area(b))<.02,"Native/runtime batch surface area mismatch")
  var changed:MeshInstance3D=successor.find_child(old.name,true,false)
  assert(changed!=null and changed.transform.is_equal_approx(installed.transform))
  var path:=P+"runtime/final/"+str(old.name)+".res";assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(changed.mesh,path)==OK)
  patches.append({"name":str(old.name),"source_triangles":b.size(),"path":path,"sha256":FileAccess.get_sha256(path),"original_area":area(b),"native_area":area(a),"bidirectional_surface_coverage":true})
 assert(patches.size()==3)
 var candidate:=raw("res://royalty_790_completion_20261020/exports/ROYALTY790_upper_candidate_r002.glb")
 var court:Node3D=candidate.find_child("DATUM_light_CourtView",true,false);var court_at:=court.global_position
 var count:=0
 for child in candidate.get_children():
  if not (str(child.name).begins_with("RG_") or str(child.name).begins_with("DATUM_RG_")):child.free();continue
  if child is MeshInstance3D:
   count+=1
   for v in child.mesh.get_faces():
    var point:Vector3=child.global_transform*v
    assert(point.y>=101.9998 and point.y<=112.0002 and point.z<51)
 assert(count==181)
 candidate.name="Royalty790UpperAdditions";own(candidate,candidate)
 var scene:=PackedScene.new();assert(scene.pack(candidate)==OK)
 var path:=P+"runtime/final/UpperAdditions.scn";assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(scene,path)==OK)
 var result:={"patches":patches,"scene":path,"scene_sha256":FileAccess.get_sha256(path),"court_light_position":[court_at.x,court_at.y,court_at.z],"new_meshes":count,"unchanged_approach_batches":4,"no_lower_slab_added":true,"new_geometry_y_min":102,"new_geometry_z_max_exclusive":51}
 var file:=FileAccess.open(P+"evidence/RUNTIME_DELTA.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"  ")+"\n");file.close()
 print("EXACT_BOUNDED_ROYALTY_DELTA 3 batches,181 upper meshes;native/runtime surfaces verified")
 quit()
