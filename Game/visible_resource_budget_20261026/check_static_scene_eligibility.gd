extends SceneTree
var output:String
func _initialize()->void:
 for a:String in OS.get_cmdline_user_args():
  if a.begins_with("--output="):output=a.substr(9)
 call_deferred("run")
func run()->void:
 var visual:Node3D=load("res://assets/models/SunsetSpecialty_104.0_r002.scn").instantiate();root.add_child(visual)
 var rows:Dictionary={};var samples:Array=[]
 for n:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  if n.mesh==null:continue
  var material:Material=n.get_active_material(0)
  var data:Dictionary={"material_class":material.get_class() if material!=null else "none","shader":material.shader.resource_path if material is ShaderMaterial else "","skeleton":str(n.skeleton),"skin":n.skin!=null,"surfaces":n.mesh.get_surface_count(),"extras_keys":str(n.get_meta("extras",{}).keys()),"scale":str(load("res://spatial_instance_cells_20261026/ship_rules.gd").pose(n,visual).basis.get_scale()),"mesh_class":n.mesh.get_class(),"children":str(n.get_children().map(func(c):return c.get_class())),"eligible":load("res://spatial_instance_cells_20261026/ship_rules.gd").eligible(n,visual)}
  var key:=JSON.stringify(data);rows[key]=int(rows.get(key,0))+1
  if not data.eligible and samples.size()<3:samples.append({"name":str(n.name),"metadata":n.get_meta("extras",{}),"details":data})
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"counts":rows,"samples":samples},"\t"));f.close();visual.free();quit()
