extends RefCounted
const P="res://night_garden_view_galleries_20261022/"
static func raw(path:String)->Node3D:
 var d:=GLTFDocument.new();var s:=GLTFState.new();assert(d.append_from_file(path,s)==OK);return d.generate_scene(s)
static func build(ship:Node3D)->Node3D:
 var district:Node3D=ship.get_node("ShipSpace/Districts/NightGardenD15SpecialtyReceiving20261020")
 assert(not district.has_node("OuterViewGalleries20261022"))
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
 assert(FileAccess.get_sha256("res://assets/models/"+source.receiving.model_file)==source.receiving.model_sha256)
 var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_r003.json"))
 assert(FileAccess.get_sha256("res://"+receipt.gallery_export)==receipt.gallery_export_sha256)
 var street:Node3D=district.get_node("ConnectedStreetsAndPortalSuccessors").get_child(0)
 var ends:Array[MeshInstance3D]=[]
 for m:MeshInstance3D in street.find_children("*","MeshInstance3D",true,false):
  if str(m.name).ends_with("_StreetEnd"):ends.append(m)
 assert(ends.size()==2,"Exact two original terminal boundaries required")
 var body:StaticBody3D=street.get_node("RoomStaticContacts")
 for m in ends:
  var bounds:AABB=m.global_transform*m.get_aabb();var lo:=bounds.position;var hi:=bounds.end
  assert(lo.x<=82.5 and hi.x>=85.5 and lo.y<93.1 and hi.y>95.8)
  var pieces:Array[AABB]=[AABB(lo,Vector3(82.5-lo.x,hi.y-lo.y,hi.z-lo.z)),AABB(Vector3(85.5,lo.y,lo.z),Vector3(hi.x-85.5,hi.y-lo.y,hi.z-lo.z)),AABB(Vector3(82.5,95.8,lo.z),Vector3(3,hi.y-95.8,hi.z-lo.z))]
  var arrays:Array=[];arrays.resize(Mesh.ARRAY_MAX);var vertices:=PackedVector3Array();var normals:=PackedVector3Array()
  for piece in pieces:
   var cube:=BoxMesh.new();cube.size=piece.size
   var faces:=cube.get_faces()
   for i in range(0,faces.size(),3):
    var normal:Vector3=(faces[i+1]-faces[i]).cross(faces[i+2]-faces[i]).normalized()
    for j in range(3):vertices.append(m.global_transform.affine_inverse()*(faces[i+j]+piece.get_center()));normals.append(m.global_basis.inverse()*normal)
  arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals
  var mesh:=ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays);mesh.surface_set_material(0,m.mesh.surface_get_material(0));m.mesh=mesh
 # Rebuild only the existing opaque aggregate shape; retain its owner and all glass contacts.
 var faces:=PackedVector3Array()
 for m:MeshInstance3D in street.find_children("*","MeshInstance3D",true,false):
  var extra:Dictionary=m.get_meta("extras",{})
  if not bool(extra.get("runtime_collision",false)) or str(extra.get("collision_policy",""))=="no_collision_detail":continue
  if not m.find_children("StaticContact","StaticBody3D",true,false).is_empty():continue
  var transform:Transform3D=street.global_transform.affine_inverse()*m.global_transform
  for point in m.mesh.get_faces():faces.append(transform*point)
 var shape:=ConcavePolygonShape3D.new();shape.set_faces(faces);body.get_node("SharedRoomTriangles").shape=shape
 var gallery:=raw("res://"+receipt.gallery_export);gallery.name="OuterViewGalleries20261022";district.add_child(gallery)
 var solids:Array[Node]=[]
 for m:MeshInstance3D in gallery.find_children("*","MeshInstance3D",true,false):
  if bool(m.get_meta("extras",{}).get("runtime_collision",false)):solids.append(m)
 load("res://scripts/static_contact_cache.gd").attach_group(gallery,solids)
 var lights:Array[Light3D]=[]
 for i in range(receipt.lights.size()):
  var p:Array=receipt.lights[i];var light:=OmniLight3D.new();light.name="GardenSourceLight_"+str(i);light.position=Vector3(p[0],p[1],p[2]);light.light_color=Color(1,.91,.76);light.light_energy=.65;light.omni_range=9;light.shadow_enabled=false;gallery.add_child(light);lights.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lights,ship)
 gallery.set_meta("finished",false);gallery.set_meta("engineering_accepted",false);gallery.set_meta("residential_visual_accepted",false);gallery.set_meta("new_units",0)
 return gallery
