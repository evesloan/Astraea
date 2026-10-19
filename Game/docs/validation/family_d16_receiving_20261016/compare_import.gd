extends SceneTree
func _initialize()->void:
 var f="res://assets/family_d16_receiving_20261016/FAMILY_D16_STAFF_RECEIVING_r001.glb";var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(f,state,64)==OK);var raw:Node=doc.generate_scene(state);var imported:Node=load(f).instantiate();var rows:Array=[]
 for a:MeshInstance3D in raw.find_children("*","MeshInstance3D",true,false):
  var b:MeshInstance3D=imported.find_child(a.name,true,false);assert(b!=null);var av:=a.mesh.get_faces();var bv:=b.mesh.get_faces();var amap:Dictionary={};var bmap:Dictionary={}
  for v in av:amap[v]=amap.get(v,0)+1
  for v in bv:bmap[v]=bmap.get(v,0)+1
  var maxerr:float=0;var different:int=0
  for v in bv:
   if not amap.has(v):
    different+=1;var best:float=INF
    for w in amap:best=minf(best,v.distance_to(w))
    maxerr=maxf(maxerr,best)
  rows.append({"name":str(a.name),"raw_format":a.mesh.surface_get_format(0),"import_format":b.mesh.surface_get_format(0),"compress_flag":Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES,"raw_faces":av.size()/3,"import_faces":bv.size()/3,"different_vertices":different,"max_error_m":maxerr,"same_pose":a.transform.is_equal_approx(b.transform),"raw_bounds":str(a.get_aabb()),"import_bounds":str(b.get_aabb())})
 FileAccess.open("/workspace/family-d16-integration/IMPORT_COMPARISON.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));raw.free();imported.free();quit()
