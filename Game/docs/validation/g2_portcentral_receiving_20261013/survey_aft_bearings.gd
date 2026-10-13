extends SceneTree
const OUT="/workspace/astraea-integration-cutoff-20261013/g2_last_three_pairs_20261013/AFT_CURRENT_LOWER_BEARINGS_AND_CLEARANCE.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 for sign_x in[-1,1]:
  for xabs in[63.5,65.,67.,69.,71.,73.]:
   for z in[326.5,330.,334.,338.,342.,344.5,346.,349.,352.,355.5,356.5]:
    var x:float=sign_x*xabs;var q:=PhysicsRayQueryParameters3D.create(Vector3(x,101.5,z),Vector3(x,83.9,z));var hit:Dictionary=space.intersect_ray(q);var row:Dictionary={"x":x,"z":z,"first_lower_hit":{}}
    if not hit.is_empty():
     row.first_lower_hit={"at":[hit.position.x,hit.position.y,hit.position.z],"normal":[hit.normal.x,hit.normal.y,hit.normal.z],"path":str(hit.collider.get_path())}
     var shape:=BoxShape3D.new();shape.size=Vector3(.18,maxf(.01,101.84-hit.position.y),.18);var sweep:=PhysicsShapeQueryParameters3D.new();sweep.shape=shape;sweep.transform=Transform3D(Basis.IDENTITY,Vector3(x,(101.84+hit.position.y)/2.,z));sweep.margin=.001;var contacts:Array=[]
     for contact in space.intersect_shape(sweep,128):contacts.append(str(contact.collider.get_path()))
     row.proposed_column_contacts=contacts
    rows.append(row)
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_AFT_BEARING_AND_COLUMN_CONTACT_SURVEY","rows":rows,"samples":rows.size(),"new_geometry_adopted":false,"engineering_or_lower_room_accepted":false},"  "));print("AFT_CURRENT_BEARING_SURVEY_PASS ",rows.size());quit(0)
