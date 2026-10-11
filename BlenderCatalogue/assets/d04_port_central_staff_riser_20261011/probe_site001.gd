extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var routes:Array=[];var feet:Array=[];var portal:Array=[];var blockers:Array=[]
 var points:Array=[]
 for y in [0.0,16.5]:
  for x in [-54.8,-50,-40,-30,-21]:
   for z in [-100.6,-97.8]:points.append(Vector3(x,y,z))
  for z in [-96,-93.5,-90,-86.5,-84.5]:points.append(Vector3(-21,y,z))
 for x in [-63.2,-60.4]:
  for z in [-94,-85,-76,-67,-58,-49,-40,-38.5]:points.append(Vector3(x,16.5,z))
 for at in points:
  var shape:=CapsuleShape3D.new();shape.radius=.5;shape.height=2.4;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*1.25);var hits:Array=[]
  for h in space.intersect_shape(q,64):hits.append(str(h.collider.get_path()))
  var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.4));routes.append({"at":[at.x,at.y,at.z],"volume_blockers":hits,"floor_owner":str(h.collider.get_path())if not h.is_empty()else"NO_FLOOR","floor_y":h.position.y if not h.is_empty()else null})
 var shaft_shape:=BoxShape3D.new();shaft_shape.size=Vector3(3.9,19.7,4);var sq:=PhysicsShapeQueryParameters3D.new();sq.shape=shaft_shape;sq.transform=Transform3D(Basis.IDENTITY,Vector3(-25,9.85,-90))
 for h in space.intersect_shape(sq,64):blockers.append(str(h.collider.get_path()))
 var shape:=BoxShape3D.new();shape.size=Vector3(.5,2.85,5.6);var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,Vector3(-55.2,1.425,-99.2));var names:Dictionary={}
 for h in space.intersect_shape(q,64):
  var mesh:Node=h.collider.get_parent()
  if mesh is MeshInstance3D and "LowerStaffNetwork_WIP"in str(mesh.get_path()):
   if names.has(str(mesh.name)):continue
   names[str(mesh.name)]=true;var verts:Array=[]
   for v in mesh.mesh.get_faces():var at:Vector3=mesh.global_transform*v;verts.append([at.x,at.y,at.z])
   portal.append({"name":str(mesh.name),"path":str(mesh.get_path()),"world_triangle_vertices":verts})
 var rawfeet:Array=[]
 for x in [-60.5,-51.5,-42.5,-33.5,-23.5]:
  for z in [-101.84,-96.56]:rawfeet.append(Vector3(x,16.26,z))
 for x in [-64.44,-59.16]:
  for z in [-90,-81,-72,-63,-54,-45,-38.5]:rawfeet.append(Vector3(x,16.26,z))
 for x in [-27.05,-22.95]:
  for z in [-92.05,-87.95]:rawfeet.append(Vector3(x,19.7,z))
 for x in [-51.5,-42.5,-33.5,-23.5]:
  for z in [-101.84,-96.56]:rawfeet.append(Vector3(x,-.24,z))
 for at in rawfeet:
  var corners:Array=[];var owner:="";var accepted:=true;var hit_y:=-INF
  for dx in [-.12,.12]:
   for dz in [-.12,.12]:
    var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(at.x+dx,at.y-.005,at.z+dz),Vector3(at.x+dx,-5,at.z+dz)));var path:=str(h.collider.get_path())if not h.is_empty()else"NO_CONTACT";var ok:bool=not h.is_empty()and h.normal.y>.15 and ("HUL_KeelPan"in path or"HUL_LowerBand"in path or "CompiledStructuralFloors"in path);accepted=accepted and ok
    if owner=="":owner=path
    else:accepted=accepted and path==owner
    if not h.is_empty():hit_y=maxf(hit_y,h.position.y);corners.append([h.position.x,h.position.y,h.position.z])
  var vol:=BoxShape3D.new();vol.size=Vector3(.235,at.y-hit_y-.09,.235);var vq:=PhysicsShapeQueryParameters3D.new();vq.shape=vol;vq.transform=Transform3D(Basis.IDENTITY,Vector3(at.x,(at.y+hit_y+.09)/2,at.z));var volume_blockers:Array=[]
  for hh in space.intersect_shape(vq,64):volume_blockers.append(str(hh.collider.get_path()))
  feet.append({"volume_blockers":volume_blockers,"top":[at.x,at.y,at.z],"source_owner":owner,"corners":corners,"accepted":accepted,"source_max_y":hit_y})
 var result={"routes":routes,"shaft_volume_blockers":blockers,"portal_preimage_meshes":portal,"support_feet":feet};FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_staff_riser_20261011/SITE_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("Staff site preflight complete");quit()
