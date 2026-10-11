extends RefCounted
# Source-only geometry probe. Never installs a care task or production contacts.
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func point(a:Vector3)->Array:return [a.x,a.y,a.z]
static func ray(space:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3)->Dictionary:return space.intersect_ray(PhysicsRayQueryParameters3D.create(a,b))
static func setup(owner:Node3D,p:Dictionary)->Dictionary:
 var out:Dictionary={"poles":[],"terminal":[],"spec":p.reach_tool.angled_terminal}
 for group in ["poles","terminal"]:
  var spec:Dictionary=p.reach_tool if group=="poles" else p.reach_tool.angled_terminal
  var model:Node3D=load("res://assets/models/"+str(spec.model)).instantiate();owner.add_child(model);model.visible=false
  for member in spec.members:
   var mesh:MeshInstance3D=model.find_child(str(member.name),true,false);assert(mesh!=null);var shape:=mesh.mesh.create_convex_shape();shape.margin=.0001;out[group].append({"name":str(member.name),"shape":shape,"native_pose":mesh.global_transform})
 return out
static func capsule_clear(space:PhysicsDirectSpaceState3D,at:Vector3)->bool:
 var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925)
 return space.intersect_shape(q,64).is_empty() and not ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty()
static func probe(space:PhysicsDirectSpaceState3D,ship:Node3D,tool:Dictionary,name:String,height:float)->Dictionary:
 var mesh:MeshInstance3D=ship.find_child(name,true,false);var bounds:AABB=mesh.global_transform*mesh.get_aabb();var spec:Dictionary=tool.spec;var offset:float=spec.offset_length_m;var tip_length:float=spec.terminal_length_m;var pivot:=v(spec.terminal_pivot);var blockers:Dictionary={};var stance_cache:Dictionary={}
 var z:float=bounds.get_center().z
 var zs:Array=[z];var sample_z:float=bounds.position.z+.04
 while sample_z<bounds.end.z-.039:zs.append(sample_z);sample_z+=.025
 for target_z in zs:
  var hit:=ray(space,Vector3(-58.99,height,target_z),Vector3(bounds.position.x-.01,height,target_z))
  if hit.is_empty() or str(hit.collider.get_parent().name)!=name:continue
  for roll in [180.0,0.0]:
   var base:=Basis.looking_at(Vector3.RIGHT,Vector3.UP)*Basis(Vector3.BACK,deg_to_rad(roll))
   for pitch in [-90.0,-85.0,-80.0,-75.0,-70.0,70.0,75.0,80.0,85.0,90.0]:
    var tip_rot:=Basis(Vector3.RIGHT,deg_to_rad(pitch));var direction:=base*(tip_rot*Vector3.BACK);var tip_start:Vector3=hit.position-direction*tip_length;var shaft_end:Vector3=tip_start-base*Vector3(offset,0,0)
    if shaft_end.y<17.05 or shaft_end.y>18.05:continue
    for x in [-57.55,-57.35,-57.15,-56.95,-56.75]:
     var at:=Vector3(x,16.5,shaft_end.z);var hand:=Vector3(x-.45,shaft_end.y,shaft_end.z);var length:float=hand.x-shaft_end.x
     if length<1.2 or length+offset+tip_length>3.4:continue
     var key:=str(at)
     if not stance_cache.has(key):stance_cache[key]=capsule_clear(space,at)
     if not stance_cache[key]:continue
     var clear:=true
     for side in [Vector3.UP*.012,-Vector3.UP*.012,Vector3.FORWARD*.012,Vector3.BACK*.012]:
      var h:=ray(space,hand+side,shaft_end+side)
      if not h.is_empty():clear=false
     if not clear:continue
     var slide:float=(length-1.2)/2;var poses:Array=[];var head_pose:=Transform3D(base,shaft_end);var shaft_pose:=Transform3D(base,hand)
     for k in range(tool.poles.size()):poses.append({"part":tool.poles[k],"pose":shaft_pose*Transform3D(Basis.IDENTITY,Vector3(0,0,k*slide))*tool.poles[k].native_pose,"tip":false})
     for part in tool.terminal:
      var pose:Transform3D=head_pose
      if part.name=="D04PC_CareTerminalTip":pose=pose*Transform3D(Basis.IDENTITY,pivot)*Transform3D(tip_rot,Vector3.ZERO)*Transform3D(Basis.IDENTITY,-pivot)
      poses.append({"part":part,"pose":pose*part.native_pose,"tip":part.name=="D04PC_CareTerminalTip"})
     var pose_records:Array=[]
     for row in poses:
      var query:=PhysicsShapeQueryParameters3D.new();query.shape=row.part.shape;query.transform=row.pose;var contacts:=space.intersect_shape(query,64)
      if contacts.size()>=64:clear=false
      for contact in contacts:
       var cn:=str(contact.collider.get_parent().name)
       if not(row.tip and cn==name):clear=false;blockers[cn]=int(blockers.get(cn,0))+1
      var t:Transform3D=row.pose;pose_records.append({"name":row.part.name,"basis":[point(t.basis.x),point(t.basis.y),point(t.basis.z)],"origin":point(t.origin),"contacts":contacts.size()})
     if clear:return {"passed":true,"plant":name,"height":height,"worker_stance":point(at),"hand":point(hand),"first_contact":point(hit.position),"shaft_end":point(shaft_end),"joint_slide":slide,"shaft_length_m":length,"total_native_path_length_m":length+offset+tip_length,"shaft_axial_roll_deg":roll,"terminal_pitch_deg":pitch,"exact_native_convex_shapes_checked":poses.size(),"native_part_poses":pose_records,"hand_extension_m":.45,"person_access":false,"terminal_native_foliage_contact_test_only":true,"no_rescaling":true,"angled_terminal_used":true}
 return {"passed":false,"plant":name,"height":height,"blockers":blockers}
