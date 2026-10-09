extends SceneTree
func _initialize()->void:
 var scene:Node3D=(load("res://assets/models/D18_directory_02.glb") as PackedScene).instantiate()
 var m:MeshInstance3D=scene.find_child("A_ForeArchiveBlade",true,false)
 assert(m!=null)
 var a:Array=m.mesh.surface_get_arrays(0)
 var rows:Array=[]
 for i in range(a[Mesh.ARRAY_VERTEX].size()):
  var p:Vector3=a[Mesh.ARRAY_VERTEX][i]
  var n:Vector3=a[Mesh.ARRAY_NORMAL][i]
  var uv:Vector2=a[Mesh.ARRAY_TEX_UV][i]
  rows.append([p.x,p.y,p.z,n.x,n.y,n.z,uv.x,uv.y])
 var f:=FileAccess.open("/workspace/scratch/375c2e438292/crown_live_integration_20261008/first_surface_import.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"mesh":m.name,"rows":rows,"indices":Array(a[Mesh.ARRAY_INDEX]),"material":m.get_active_material(0).resource_name}));f.close()
 scene.free()
 print("PASS: diagnostic export only")
 quit()
