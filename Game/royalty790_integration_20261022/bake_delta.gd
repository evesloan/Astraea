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
func run():
 var old:=raw(P+"source/EXACT_FOUR_PREDECESSOR_MESHES.glb")
 for m:MeshInstance3D in old.find_children("*","MeshInstance3D",true,false):
  var f:=m.mesh.get_faces()
  for i in range(0,f.size(),3):
   var triangle:Array=[m.global_transform*f[i],m.global_transform*f[i+1],m.global_transform*f[i+2]]
   if str(m.name)=="CR_RoyaltyLowerRoof":roof_before.append(triangle)
   else:removed.append({"part":str(m.name),"v":triangle,"found":0})
 var baseline:=raw("res://assets/models/AST-RES-006.glb")
 var patches:Array=[]
 for m:MeshInstance3D in baseline.find_children("*","MeshInstance3D",true,false):
  var replacement:=ArrayMesh.new();var dropped:=0;var before:=m.mesh.get_faces().size()/3
  for surface in range(m.mesh.get_surface_count()):
   var arrays:=m.mesh.surface_get_arrays(surface);var positions:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
   if indices.is_empty():for i in range(positions.size()):indices.append(i)
   var retained:=PackedInt32Array()
   for i in range(0,indices.size(),3):
    var triangle:Array=[m.global_transform*positions[indices[i]],m.global_transform*positions[indices[i+1]],m.global_transform*positions[indices[i+2]]];var drop:=false
    for entry in removed:
     if same(triangle,entry.v):entry.found+=1;drop=true;dropped+=1;break
    if not drop and covered(triangle,roof_before):drop=true;dropped+=1;roof_after.append(triangle)
    if not drop:retained.append_array(indices.slice(i,i+3))
   assert(not retained.is_empty(),"An entire old surface would disappear; review required")
   arrays[Mesh.ARRAY_INDEX]=retained
   replacement.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
   replacement.surface_set_material(surface,m.mesh.surface_get_material(surface))
  if dropped>0:
   assert(not str(m.name).begins_with("CR_Batch_approach_"))
   var file:=P+"runtime/"+str(m.name)+"_remaining_r002.res";assert(not FileAccess.file_exists(file));assert(ResourceSaver.save(replacement,file)==OK)
   patches.append({"name":str(m.name),"before_triangles":before,"removed_triangles":dropped,"path":file,"sha256":FileAccess.get_sha256(file)})
 for entry in removed:assert(entry.found==1,"Each exact predecessor triangle must be removed once: "+str(entry.part)+" / "+str(entry.found))
 for triangle:Array in roof_before:assert(covered(triangle,roof_after),"Roof surface coverage incomplete")
 assert(absf(area(roof_before)-area(roof_after))<.01,"Roof area changed during reconciliation")
 var candidate:=raw("res://royalty_790_completion_20261020/exports/ROYALTY790_upper_candidate_r002.glb")
 var changed:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://royalty_790_completion_20261020/evidence/BUILD_RECEIPT.json"))
 var court:Node3D=candidate.find_child("DATUM_light_CourtView",true,false);var court_at:=court.global_position
 var keep_names:Array=changed.declared_changed_originals.duplicate();keep_names.erase("DATUM_light_CourtView")
 var meshes:=0;var new_count:=0
 for c in candidate.get_children():
  var keep:bool=str(c.name).begins_with("RG_") or str(c.name).begins_with("DATUM_RG_") or str(c.name) in keep_names
  if not keep:c.free();continue
  if c is MeshInstance3D:
   meshes+=1
   if str(c.name).begins_with("RG_"):new_count+=1
   for vertex in c.mesh.get_faces():
    var world:Vector3=c.global_transform*vertex
    assert(world.y>=101.9998 and world.z<51 and world.y<=112.0002,"Protected volume violated")
 assert(new_count==181 and meshes==185)
 candidate.name="Royalty790ExactUpperDelta";own(candidate,candidate)
 var scene:=PackedScene.new();assert(scene.pack(candidate)==OK)
 var path:=P+"runtime/UpperDelta.scn";assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(scene,path)==OK)
 var receipt:={"fixture_predecessor_triangles_removed_once":removed.size(),"roof_preimage_triangles":roof_before.size(),"roof_batched_triangles_removed":roof_after.size(),"roof_surface_area_before":area(roof_before),"roof_surface_area_removed":area(roof_after),"roof_bidirectional_surface_coverage":true,"patches":patches,"delta_scene":path,"delta_sha256":FileAccess.get_sha256(path),"new_meshes":new_count,"changed_source_meshes":4,"court_light_position":[court_at.x,court_at.y,court_at.z],"approach_patches_untouched":true,"no_new_geometry_below_y102":true,"no_new_geometry_at_z51_or_aft":true,"lower_floor_duplicated":false}
 var f:=FileAccess.open(P+"evidence/DELTA.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"  ")+"\n");f.close()
 print("ROYALTY_DELTA ",removed.size()," exact triangles; ",patches.size()," bounded batch edits;185 delta meshes")
 quit()
