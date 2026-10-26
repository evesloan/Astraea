extends RefCounted
static func build(parent:Node3D,top:Material,side:Material,materials:Dictionary={})->Node3D:
 var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://grand_arrivals_tram_20261026/integration_r001/WORLD_RECEIVING.json"))
 assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==proof.compiled_source_sha256)
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var count:=0
 for i in source.regions.size():
  for change:Dictionary in proof.floor_changes:
   if source.regions[i].id==change.before.id:
    assert(source.regions[i]==change.before,"Exact original floor receiver required")
    source.regions[i]=change.after;count+=1
 assert(count==6)
 var group:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(parent,top,side,source.regions,materials)
 group.set_meta("lower_arrivals_exact_floor_changes",count)
 return group
