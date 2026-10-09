extends RefCounted
# Fail closed: authenticate current bytes and exactly four additions, then expose
# the byte-exact 296-owner predecessor to unchanged older regression assertions.
const PROOF="res://data/architecture/packages/d12_pair_runtime/RUNTIME_PROOF.json"
const PROOF_SHA="fe42e7b1712a373552e590359ba68d93e721119dec73e74802e18009ebd79b36"
static var checked:=false
static var old:Dictionary={}
static var current_compiled:Dictionary={}
static func ensure()->void:
 if checked:return
 assert(FileAccess.get_sha256(PROOF)==PROOF_SHA)
 var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
 for path in proof.predecessors:
  var row:Dictionary=proof.predecessors[path]
  assert(FileAccess.get_sha256("res://"+str(row.retained_path))==str(row.sha256))
  old[path]=FileAccess.get_file_as_string("res://"+str(row.retained_path))
 for path in proof.current_sha256:
  assert(FileAccess.get_sha256("res://"+str(path))==str(proof.current_sha256[path]),"Unreviewed D12 successor source: "+str(path))
 for path in proof.inverse_edits:
  var text:=FileAccess.get_file_as_string("res://"+str(path))
  for edit in proof.inverse_edits[path]:
   assert(text.count(str(edit.after))==int(edit.count));text=text.replace(str(edit.after),str(edit.before))
  assert(text==str(old[path]),"Byte-exact prior guard must survive")
 var compiler_path:="res://data/architecture/packages/d12_pair_candidate/D12_PAIR_COMPILER_PROOF.json"
 assert(FileAccess.get_sha256(compiler_path)==str(proof.compiler_proof_sha256))
 var compiler:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(compiler_path))
 var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
 current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var old_layout:Dictionary=JSON.parse_string(str(old["data/spatial_layout.json"]))
 var old_compiled:Dictionary=JSON.parse_string(str(old["data/generated/structural_meshes.json"]))
 for pair in [[layout,old_layout,compiler.new_layout_records],[current_compiled,old_compiled,compiler.new_expected_compiled_records]]:
  var wanted:Array=pair[1].regions.duplicate(true);wanted.append_array(pair[2])
  assert(pair[2].size()==4 and pair[0].regions==wanted,"All prior records/order and four exact D12 additions required")
  var ids:Dictionary={}
  for row in pair[0].regions:assert(not ids.has(row.id));ids[row.id]=true
 var a:Dictionary=layout.duplicate(true);var b:Dictionary=old_layout.duplicate(true)
 a.erase("regions");b.erase("regions");assert(a==b)
 a=current_compiled.duplicate(true);b=old_compiled.duplicate(true)
 for key in ["regions","source_checks"]:a.erase(key);b.erase(key)
 assert(a==b and old_compiled.regions.size()==296 and current_compiled.regions.size()==300)
 assert(current_compiled.source_checks==JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json")))
 checked=true
static func project_compiled(value:Dictionary)->Dictionary:
 ensure()
 return JSON.parse_string(str(old["data/generated/structural_meshes.json"])) if value==current_compiled else value
static func current_text(path:String)->String:
 ensure();var key:=path.trim_prefix("res://")
 return str(old[key]) if old.has(key) else FileAccess.get_file_as_string(path)
static func current_sha256(path:String)->String:
 ensure();var key:=path.trim_prefix("res://")
 return str(old[key]).sha256_text() if old.has(key) else FileAccess.get_sha256(path)
static func floor_children(floors:Node)->Array:
 ensure();assert(floors!=null and floors.get_child_count()==300)
 var children:=floors.get_children();var retained:Array=[]
 for i in range(children.size()):
  var row:Dictionary=current_compiled.regions[i]
  assert(str(children[i].name)==str(row.id))
  load("res://tests/medical_triage_successor_guard.gd")._botanical_validate_slab(children[i],row)
  if i<296:retained.append(children[i])
 return retained
