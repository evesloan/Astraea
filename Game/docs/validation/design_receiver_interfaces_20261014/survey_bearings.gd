extends SceneTree
const P="/workspace/astraea-integration-cutoff-20261013/design_connections_20261014/"
func _initialize()->void:
 for p in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"DESIGN_RECEIVER_PLAN.json"));var floors:Array=[];var kits:Array=[]
 for row in plan.floor_rows:
  var samples:Array=[]
  for tri in row.triangles:
   var x:float=(tri[0][0]+tri[1][0]+tri[2][0])/3.;var z:float=(tri[0][1]+tri[1][1]+tri[2][1])/3.;var y:float=row.floor_y-row.thickness;var at:=Vector3(x,y,z);var exact:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));var lower:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.1,at-Vector3.UP*18.));samples.append({"xyz":[x,y,z],"exact_bottom_bearing":not exact.is_empty(),"exact_path":str(exact.collider.get_path())if not exact.is_empty()else"","first_lower_y":lower.position.y if not lower.is_empty()else null,"first_lower_path":str(lower.collider.get_path())if not lower.is_empty()else""})
  floors.append({"id":row.id,"owner":row.source_owner,"samples":samples})
 for kit in plan.wet:
  var origin:Vector3=v(kit.candidate.world_xyz);var parts:Array=[]
  for part in kit.parts:
   var lo:Vector3=v(part.min)+origin;var hi:Vector3=v(part.max)+origin;var shape:=BoxShape3D.new();shape.size=hi-lo;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,(hi+lo)/2);var contacts:Array=[]
   for hit in space.intersect_shape(q,128):contacts.append(str(hit.collider.get_path()))
   parts.append({"part":part.name,"world_min":[lo.x,lo.y,lo.z],"world_max":[hi.x,hi.y,hi.z],"retained_contacts":contacts})
  kits.append({"kit":kit.kit,"parts":parts})
 FileAccess.open(P+"EXACT_CURRENT_BEARINGS_AND_WET_CONFLICTS.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_DESIGN_RECEIVER_SURVEY","base":plan.base,"floors":floors,"wet":kits,"source_geometry_changed":false,"new_primary_design_selected":false},"  "));print("DESIGN_RECEIVER_SURVEY_PASS floors=",floors.size()," wet=",kits.size());quit(0)
