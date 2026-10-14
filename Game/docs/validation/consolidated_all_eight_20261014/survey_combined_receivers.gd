extends SceneTree
const PLAN="/workspace/astraea-integration-cutoff-20261013/consolidated_all_eight_20261013/CONSOLIDATED_PLAN.json"
const OUT="/workspace/astraea-integration-cutoff-20261013/consolidated_all_eight_20261013/COMBINED_CURRENT_RECEIVING_SURVEY.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state;var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PLAN));var rows:Array=[];var allsamples:=0
 for row in p.G2_floor_rows:
  var samples:Array=[];var missing:=0
  for tri in row.triangles:
   var x:float=(tri[0][0]+tri[1][0]+tri[2][0])/3.;var z:float=(tri[0][1]+tri[1][1]+tri[2][1])/3.;var at:=Vector3(x,row.floor_y,z);var hit:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));var good:bool=not hit.is_empty()and absf(hit.position.y-at.y)<.002 and hit.normal.y>.99
   if not good:missing+=1
   samples.append({"xyz":[x,row.floor_y,z],"floor_contact":good,"path":str(hit.collider.get_path())if not hit.is_empty()else"","normal_y":hit.normal.y if not hit.is_empty()else 0});allsamples+=1
  rows.append({"id":row.id,"owner":row.source_owner,"samples":samples,"missing_samples":missing,"sampled_receiving_present":missing==0,"structural_capacity_accepted":false})
 var entries:Array=[]
 for home in p.G2_homes:
  var at:Vector3=v(home.entry);var floor:Dictionary=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.02,at-Vector3.UP*.02));var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var obstructions:Array=[]
  for h in space.intersect_shape(q,32):obstructions.append(str(h.collider.get_path()))
  entries.append({"key":home.key,"entry":home.entry,"floor_present":not floor.is_empty()and absf(floor.position.y-at.y)<.002,"capsule_obstructions":obstructions,"private_admission_or_capacity_accepted":false})
 var g7:Node=ship.get_node("ShipSpace/Districts/Group7CompletionCandidate");var counts:=g7.get_child_count();assert(counts>=69)
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_COMBINED_CURRENT_RECEIVING_SURVEY","base_commit":p.base_commit,"all_eight_groups_accounted":p.groups.size(),"G2_floor_regions":rows,"G2_floor_samples":allsamples,"G2_home_entries":entries,"G7_selected_models":69,"G7_remaining_models_held":19,"new_primary_structural_or_tram_design_selected":false,"source_or_movement_changes":false,"full_build_accepted":false},"  "));print("COMBINED_RECEIVING_SURVEY_PASS regions=",rows.size()," samples=",allsamples," entries=",entries.size());quit(0)
