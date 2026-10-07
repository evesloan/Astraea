extends SceneTree
const OUT="/workspace/scratch/375c2e438292/pool-connected-gallery-curved001/runtime_draft001/representation_diagnostic001/RESULT.json"
func _initialize():call_deferred("run")
func run():
 var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for frame in range(3):await physics_frame
 var ship=main.get_node("World360/Astraea")
 var files=["AST-AQU-016.glb","AST-STF-009_pool_market.glb","AST-STF-009.glb","AST-CIR-005_forward_pool_market.glb","AST-CIR-005_forward_core.glb","AST-CIR-005_forward_pool_market_engineering_access.glb","AST-STF-009_pool_market_home.glb","AST-CIR-005_forward_pool_market_engineering_medical_access.glb"]
 var rows={}
 for file in files:rows[file]=[]
 for node in ship.find_children("*","Node3D",true,false):
  var file=str(node.get_meta("catalogue_file",""))
  if rows.has(file):rows[file].append({"path":str(node.get_path()),"file":file,"glb_sha256":FileAccess.get_sha256("res://assets/models/"+file)})
 var proof=JSON.parse_string(FileAccess.get_file_as_string("res://docs/MEDICAL_ADDITIVE_SUCCESSOR.json"))
 var guard=load("res://tests/medical_successor_guard.gd")
 var retained=guard.retained_text("res://data/architecture/FORWARD_PUBLIC_CORE.json")
 var current=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
 var result={"status":"PASS_READ_ONLY_ACTUAL_MODEL_REPRESENTATION_INVENTORY","representations":rows,"current_core_enclosure":current.enclosure_file,"authenticated_predecessor_core_enclosure":JSON.parse_string(retained).enclosure_file,"medical_proof_sha256":FileAccess.get_sha256("res://docs/MEDICAL_ADDITIVE_SUCCESSOR.json"),"medical_derivative":proof.core_derivative_file,"no_scene_changes":true}
 var f=FileAccess.open(OUT,FileAccess.WRITE);assert(f!=null);f.store_string(JSON.stringify(result,"  "));f.close();print("PASS: actual model representation inventory complete")
 main.queue_free();await process_frame;quit()
