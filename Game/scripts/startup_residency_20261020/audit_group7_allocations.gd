extends SceneTree
func _initialize()->void:
 call_deferred("run")
func run()->void:
 var interner=load("res://scripts/startup_residency_20261020/exact_texture_intern.gd").new()
 node_added.connect(interner.observe)
 var parent:=Node3D.new();root.add_child(parent)
 var baseline:=OS.get_static_memory_usage()
 var visuals_bytes:=0;var contacts_bytes:=0
 for file in ["res://data/architecture/GROUP7_COMPLETION.json","res://data/consolidated_all_eight_20261013/G7_ADDITIONAL.json"]:
  var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(file))
  for row in data.models:
   var before:=OS.get_static_memory_usage()
   var scene:PackedScene=load("res://assets/models/"+str(row.file))
   var visual:Node3D=scene.instantiate();parent.add_child(visual);scene=null
   interner.flush()
   var after_visual:=OS.get_static_memory_usage()
   var triangles:=0
   for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
    var category:=str(mesh.get_meta("extras",{}).get("contact_category",""))
    if category.begins_with("solid_"):
     triangles+=mesh.mesh.get_faces().size()/3
     load("res://scripts/static_contact_cache.gd").attach(mesh)
   var after_contact:=OS.get_static_memory_usage()
   visuals_bytes+=after_visual-before;contacts_bytes+=after_contact-after_visual
   print("G7_ALLOCATION ",JSON.stringify({"file":row.file,"visual_bytes":after_visual-before,"contact_bytes":after_contact-after_visual,"contact_triangles":triangles}))
 print("G7_TOTAL ",JSON.stringify({"visual_bytes":visuals_bytes,"contact_bytes":contacts_bytes,"total_bytes":OS.get_static_memory_usage()-baseline,"textures":interner.statistics()}))
 parent.free();quit()
