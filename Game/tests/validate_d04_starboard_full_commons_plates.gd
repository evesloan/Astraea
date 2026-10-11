extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FULL_COMMONS.json"));var space:=ship.get_world_3d().direct_space_state;var commons:Node3D=load("res://scripts/d04_starboard_full_commons.gd").build(ship,true)
 for i in range(5):await physics_frame
 var own:Array[RID]=[]
 for body:StaticBody3D in commons.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
 var conflicts:Array=[];var triangles:=0
 for part in p.parts:
  if part.category not in ["floor","staff_floor","roof","staff_roof"]:continue
  var bottom:=INF;var top:=-INF
  for v in part.verts:bottom=minf(bottom,v[1]);top=maxf(top,v[1])
  for face in part.faces:
   if face.size()!=3:continue
   var top_face:=true;var centroid:=Vector3.ZERO
   for index in face:top_face=top_face and absf(part.verts[index][1]-top)<.00001;centroid+=vec(part.verts[index])/3
   if not top_face:continue
   var vertices:=PackedVector3Array()
   for index in face:
    var v:=vec(part.verts[index]);v+=(centroid-v).normalized()*.003;vertices.append(Vector3(v.x,bottom+.003,v.z));vertices.append(Vector3(v.x,top-.003,v.z))
   var shape:=ConvexPolygonShape3D.new();shape.points=vertices;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.exclude=own;var hits:=space.intersect_shape(q,32);record("actual_plate_triangle_"+str(triangles),hits.is_empty());triangles+=1
   for h in hits:conflicts.append({"part":part.name,"owner":str(h.collider.get_path())})
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"baseline_conflicts":conflicts,"model_pins":p.model_pins,"source_geometry":"Actual isolated triangular plate prisms, not enclosing hulls across purposeful stair void","engineering_accepted":false}
 FileAccess.open("res://artifacts/d04_starboard_full_commons_plates.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
