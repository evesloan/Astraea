extends RefCounted
# Authenticate 303 actual records/current source, then expose only the exact pinned
# 300-owner state to D12's unchanged four-owner projection down to 296.
# This does not certify runtime geometry or operational/design acceptance by itself.
const PROOF := "res://data/architecture/packages/botanical_pair_runtime/RUNTIME_PROOF.json"
const PROOF_SHA := "e076f8f8ac8aa6433d75d1670bc5b4d4fa18815bc5210f59377097a0a9525774"
static var checked := false
static var checking := false
static var proof:Dictionary={}
static var old_text:Dictionary={}
static var current_compiled:Dictionary={}
static var prior_compiled:Dictionary={}

static func ensure()->void:
 if checked:return
 assert(not checking,"Recursive botanical projection would bypass source authentication")
 checking=true
 assert(PROOF_SHA.length()==64 and FileAccess.get_sha256(PROOF)==PROOF_SHA,"Exact D06 successor proof required")
 proof=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
 assert(proof.schema==1 and proof.predecessor_compiled_owners==300 and proof.current_compiled_owners==303)
 var self_text:=FileAccess.get_file_as_string("res://tests/botanical_pair_successor_guard.gd")
 assert(self_text.count(PROOF_SHA)==1)
 assert(self_text.replace(PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(proof.normalized_guard_sha256),"Exact normalized D06 guard code required")
 for path in proof.predecessors:
  var row:Dictionary=proof.predecessors[path]
  var retained:="res://"+str(row.retained_path)
  assert(FileAccess.get_sha256(retained)==str(row.sha256),"Changed fixed 300-owner predecessor: "+str(path))
  if str(row.encoding)=="utf8":old_text[path]=FileAccess.get_file_as_string(retained)
 for path in proof.current_sha256:
  assert(FileAccess.get_sha256("res://"+str(path))==str(proof.current_sha256[path]),"Unreviewed D06 successor source: "+str(path))
 for path in proof.inverse_edits:
  assert(old_text.has(path),"An inverse cannot invent a predecessor")
  var text:=FileAccess.get_file_as_string("res://"+str(path))
  for edit in proof.inverse_edits[path]:
   assert(not str(edit.after).is_empty() and text.count(str(edit.after))==int(edit.count),"Exact D06 source inverse cardinality: "+str(path))
   text=text.replace(str(edit.after),str(edit.before))
  assert(text==str(old_text[path]),"Entire original source must survive D06: "+str(path))
 var compiler_path:="res://data/architecture/packages/botanical_pair_candidate/BOTANICAL_PAIR_COMPILER_PROOF.json"
 assert(FileAccess.get_sha256(compiler_path)==str(proof.compiler_proof_sha256))
 var compiler:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(compiler_path))
 var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
 var prior_layout:Dictionary=JSON.parse_string(str(old_text["data/spatial_layout.json"]))
 current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 prior_compiled=JSON.parse_string(str(old_text["data/generated/structural_meshes.json"]))
 for pair in [[layout,prior_layout,compiler.new_layout_records],[current_compiled,prior_compiled,compiler.new_expected_compiled_records]]:
  assert(pair[2].size()==3)
  var expected:Array=pair[1].regions.duplicate(true);expected.append_array(pair[2])
  assert(pair[0].regions==expected,"All prior complete records/order and exactly three D06 additions required")
  var seen:Dictionary={}
  for row in pair[0].regions:assert(not seen.has(str(row.id)));seen[str(row.id)]=true
 var a:Dictionary=layout.duplicate(true);var b:Dictionary=prior_layout.duplicate(true)
 a.erase("regions");b.erase("regions");assert(a==b,"All source void/global/deck records must survive D06")
 a=current_compiled.duplicate(true);b=prior_compiled.duplicate(true)
 for key in ["regions","source_checks"]:a.erase(key);b.erase(key)
 assert(a==b and current_compiled.regions.size()==303 and prior_compiled.regions.size()==300)
 assert(current_compiled.source_checks==JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json")))
 var current_checks:Dictionary=current_compiled.source_checks.duplicate(true)
 var old_checks:Dictionary=prior_compiled.source_checks.duplicate(true)
 assert(current_checks.has("botanical_pair_additive_preservation"))
 var receipt:Dictionary=current_checks.botanical_pair_additive_preservation
 assert(receipt.retained_compiled_records==300 and receipt.all_prior_records_exact and receipt.new_area_m2==6274.4)
 var ids:Array=[]
 for row in compiler.new_expected_compiled_records:ids.append(str(row.id))
 assert(receipt.new_owners==ids)
 current_checks.erase("botanical_pair_additive_preservation")
 for key in ["source_sha256","regions","triangles"]:current_checks.erase(key);old_checks.erase(key)
 assert(current_checks==old_checks,"Every prior preservation receipt must survive D06")
 assert(str(current_compiled.source_checks.source_sha256)==FileAccess.get_sha256("res://data/spatial_layout.json"))
 assert(current_compiled.source_checks.triangles==prior_compiled.source_checks.triangles+6)
 checking=false;checked=true

static func current_text(path:String)->String:
 ensure();var relative:=path.trim_prefix("res://")
 if proof.predecessors.has(relative):
  assert(old_text.has(relative),"Binary predecessor cannot be projected as UTF-8 text")
  return str(old_text[relative])
 return FileAccess.get_file_as_string("res://"+relative)

static func current_sha256(path:String)->String:
 ensure();var relative:=path.trim_prefix("res://")
 return str(proof.predecessors[relative].sha256) if proof.predecessors.has(relative) else FileAccess.get_sha256("res://"+relative)

static func project_compiled(value:Dictionary)->Dictionary:
 ensure()
 return prior_compiled.duplicate(true) if value==current_compiled else value

static func floor_children(floors:Node)->Array:
 ensure()
 assert(floors!=null and floors.get_child_count()==303,"Complete actual 303-owner scene required")
 var children:=floors.get_children();var retained:Array=[]
 for i in range(children.size()):
  var row:Dictionary=current_compiled.regions[i]
  assert(children[i] is Node3D and str(children[i].name)==str(row.id),"Exact live owner order required")
  # This existing helper is pure geometry/contact verification; it never calls ensure.
  load("res://tests/medical_triage_successor_guard.gd")._botanical_validate_slab(children[i],row)
  if i<300:retained.append(children[i])
 return retained
