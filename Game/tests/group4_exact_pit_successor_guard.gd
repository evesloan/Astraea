extends RefCounted
# Exact source013 receiving transform; original D06 predicates and live slab triangle checks remain.
const PROOF:="res://data/architecture/group4_pit_receiving/EXACT_SOURCE_SUCCESSOR_PROOF.json"
const PROOF_SHA:="a732cdd20896329400d9ed6696b05b570bd29f25e8fc8eda7beb8d0df08c8f7b"
static var checked:=false
static var before:Dictionary={}
static var current:Dictionary={}
static var changed_before:Dictionary={}
static var changed_after:Dictionary={}
static func ensure()->void:
 if checked:return
 assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Exact later pit proof required")
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
 assert(p.schema==1 and p.replaced_owners==3 and p.total_removed_m2==24.8)
 assert(FileAccess.get_sha256(str(p.before_path))==str(p.before_sha256))
 assert(FileAccess.get_sha256(str(p.patch_path))==str(p.patch_sha256))
 assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(p.current_compiled_sha256))
 before=JSON.parse_string(FileAccess.get_file_as_string(str(p.before_path)))
 current=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var patch:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(str(p.patch_path)))
 assert(before.regions.size()==303 and current.regions.size()==303 and patch.replacements.size()==3)
 var expected:Dictionary=before.duplicate(true)
 for row in patch.replacements:
  var id:=str(row.owner_id);assert(id in ["D09_fore_route","D09_aft_route","D09_atrium_circulation"] and not changed_after.has(id))
  var matches:=0
  for i in range(before.regions.size()):
   if str(before.regions[i].id)!=id:continue
   assert(str(row.replacement.id)==id and float(row.replacement.floor_y)==float(before.regions[i].floor_y))
   changed_before[id]=before.regions[i];changed_after[id]=row.replacement;expected.regions[i]=row.replacement;matches+=1
  assert(matches==1)
 assert(changed_after.size()==3 and current==expected,"Exactly three supplied replacements;every other complete owner/order/global remains exact")
 checked=true
static func validated_before_pits(value:Dictionary)->Dictionary:
 ensure();assert(value==current,"Only the exact current source may be projected to its retained D06 predecessor")
 return before.duplicate(true)
static func actual_slab_record(record:Dictionary)->Dictionary:
 ensure();var id:=str(record.id)
 if not changed_after.has(id):return record
 assert(record==changed_before[id] or record==changed_after[id],"Only exact prior or current named pit records may be resolved")
 return changed_after[id].duplicate(true)
