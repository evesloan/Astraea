extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var selector=load("res://retained_lod_cells_20261026/selector.gd")
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://precompiled_bank_cells_20261026/COMPILED_SOURCES.json"))
 var report:Array=[]
 for key:String in index:
  var descriptor:Dictionary=index[key];assert(FileAccess.get_sha256(descriptor.path)==descriptor.sha256)
  var bank:Node3D=load(str(descriptor.path)).instantiate();root.add_child(bank)
  var before_contacts:Array=[]
  for c:CollisionShape3D in bank.find_children("*","CollisionShape3D",true,false):before_contacts.append([c.get_instance_id(),c.shape,c.transform])
  selector.preserve_lods=false
  var selected:Dictionary=selector.apply(bank,[])
  assert(selected.lod_cells>0,"Actual retained imported LOD records required")
  var switched:Dictionary=selector.switch_to_original_lods();assert(switched.cells>0)
  var actual:=0;var refs:Array=[]
  for w:WeakRef in switched.owners:
   var owner:Node3D=w.get_ref();assert(owner.instances.size()==owner.records.size())
   for row:Array in owner.records:
    assert(row.size()==11 and row[1] is Mesh and row[2] is Material);actual+=1
   refs.append(weakref(owner))
  assert(actual==switched.original_instances)
  var after_contacts:Array=[]
  for c:CollisionShape3D in bank.find_children("*","CollisionShape3D",true,false):after_contacts.append([c.get_instance_id(),c.shape,c.transform])
  assert(before_contacts==after_contacts,"Original contact IDs/shapes/poses unchanged")
  var row:Dictionary={"source":key,"baseline":selected,"cells":switched.cells,"original_instances":actual,"contact_bindings_unchanged":before_contacts.size()};report.append(row)
  bank.free()
  for w:WeakRef in refs:assert(w.get_ref()==null,"Original renderer owners released with room")
  await process_frame
 print("RETAINED_LOD_CHECK ",JSON.stringify(report));quit()
