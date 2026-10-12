extends SceneTree
func _initialize()->void:call_deferred("run")
func model(world:Node3D,file:String,at:Vector3,yaw:float=0)->Node3D:
 var node:Node3D=load("res://assets/models/"+file).instantiate();world.add_child(node);node.position=at;node.rotation.y=yaw
 for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name).begins_with("RTL_finish_"):continue
  load("res://scripts/static_contact_cache.gd").attach(mesh)
 return node
func run()->void:
 var world:=Node3D.new();root.add_child(world)
 model(world,"AST-RTL-006.glb",Vector3(46,52.5,230.4))
 model(world,"AST-BOT-001.glb",Vector3(48.3,52.865,232.4))
 model(world,"AST-BOT-009.glb",Vector3(47.1,53.015,240),.42)
 model(world,"AST-BOT-009.glb",Vector3(47.1,53.315,241.15),.84)
 model(world,"AST-BOT-003.glb",Vector3(47.25,53.115,233.1),1.26)
 model(world,"AST-RTL-001.glb",Vector3(53,52.5,232.7),-PI/2)
 model(world,"AST-RTL-003.glb",Vector3(48.9,52.5,239.6))
 model(world,"AST-STR-001.glb",Vector3(50,52.5,244))
 for i in range(5):await physics_frame
 var hits:Array=[];var space:=world.get_world_3d().direct_space_state
 for plane_x in [47.6]:
  var pose:=Transform3D(Basis(Vector3.UP,-PI/2),Vector3(plane_x,52.5,236.1));var width:=3.78
  for j in range(4):
   var centers:Array=[-3*width/8,-width/8,3*width/8,width/8];var travels:Array=[-(width/4+.05),-(width/2+.05),width/4+.05,width/2+.05]
   for frame in range(21):
    var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(width/4,2.8,.044);box.margin=.0001;q.shape=box;q.transform=pose*Transform3D(Basis.IDENTITY,Vector3(centers[j]+travels[j]*float(frame)/20,1.425,-.12*(j%2)))
    for hit in space.intersect_shape(q,64):hits.append({"plane_x":plane_x,"panel":j,"fraction":float(frame)/20,"old":str(hit.collider.get_parent().get_path())})
 for j in range(4):
  var centers:Array=[-.75,-.25,.75,.25];var travel:Array=[-.55,-1.05,-2.05,-1.55];var depth:Array=[0,-.12,-.36,-.24]
  for frame in range(21):
   var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(.5,2.95,.044);box.margin=.0001;q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(52.4+centers[j]+travel[j]*float(frame)/20,54,242.9+depth[j]))
   for hit in space.intersect_shape(q,64):hits.append({"service":true,"panel":j,"fraction":float(frame)/20,"old":str(hit.collider.get_parent().get_path())})
 FileAccess.open("/workspace/group5-checkpoints/LIVING_DOOR_REVISED_POSE_PROBE.json",FileAccess.WRITE).store_string(JSON.stringify({"scope":"Preliminary actual export triangle contacts for old architecture/flora/display/workbench/aquatic column;not fullmain/controller/fixtures/floor or acceptance","hits":hits},"  "))
 print("LIVING_POSE_PROBE ",JSON.stringify(hits));quit()
