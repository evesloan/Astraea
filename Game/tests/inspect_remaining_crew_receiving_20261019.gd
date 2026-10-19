extends SceneTree
var floor_parts:Array=[]
var obstacles:Array=[]
var checked:=0
func _initialize()->void:call_deferred("run")
func scan(n:Node)->void:
 if n is MeshInstance3D and n.mesh!=null:
  var b:AABB=n.global_transform*n.get_aabb()
  if b.end.y>=11.759 and b.position.y<=15.35 and b.end.x>=-107 and b.position.x<=107 and b.end.z>=-346 and b.position.z<=346 and (b.position.x<=-65 or b.end.x>=65):
   checked+=1
   var path:String=str(n.get_path())
   if b.end.y>12.02 and b.position.y<15.2:obstacles.append({"path":path,"bounds":[b.position.x,b.position.y,b.position.z,b.end.x,b.end.y,b.end.z]})
   if b.position.y<=12.002 and b.end.y>=11.998:
    var tops:Array=[]
    for s in n.mesh.get_surface_count():
     var arrays:Array=n.mesh.surface_get_arrays(s)
     var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
     var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
     var count:int=indices.size() if not indices.is_empty() else vertices.size()
     for i in range(0,count,3):
      var a:Vector3=n.global_transform*vertices[indices[i] if not indices.is_empty() else i]
      var c:Vector3=n.global_transform*vertices[indices[i+1] if not indices.is_empty() else i+1]
      var d:Vector3=n.global_transform*vertices[indices[i+2] if not indices.is_empty() else i+2]
      if max(abs(a.y-12),max(abs(c.y-12),abs(d.y-12)))>.002:continue
      # Godot imported triangle winding is clockwise when viewed from the front.
      if (c-a).cross(d-a).y>=-.0000001:continue
      tops.append([[a.x,a.z],[c.x,c.z],[d.x,d.z]])
    if not tops.is_empty():floor_parts.append({"path":path,"triangles_xz":tops})
 for c in n.get_children():scan(c)
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node=main.get_node("World360/Astraea")
 scan(ship)
 var out:Dictionary={"base_commit":"042c4bb2f2d0e6ac11ac0eee8ac6738e48d163b6","checked_meshes":checked,"floor_parts":floor_parts,"obstacle_aabbs":obstacles,"scope":"Current actual main D03 receiving band. AABB conflicts are conservative screening candidates, not exact penetration verdicts."}
 FileAccess.open("/workspace/crew-bank-receiving-20261019/ACTUAL_D03_RECEIVING.json",FileAccess.WRITE).store_string(JSON.stringify(out))
 print("D03_RECEIVING meshes=",checked," floor_parts=",floor_parts.size()," obstacles=",obstacles.size())
 quit()
