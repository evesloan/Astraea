extends SceneTree
# Standalone scoped fixture test and callable static validator. Never loads world.tscn,
# invokes candidate build(), changes activation, creates import maps, or writes receipts.
const HELPER := "res://tests/medical_triage_successor_guard.gd"
const STATIC_CONTACT_SHA256 := "4ebe68081d5bf1d0b433ce93c4cb2d9c8bca0192a301fa11a0c2b58d5a86b049"
const ASSETS := {
 "AST-RCV-D06-CLOUD-LINK-001.glb":{"sha256":"1750017ec2302c8ed36d300b20996917487a04585f42725b2217af3826a24003","nodes":44,"mesh_nodes":44,"surfaces":44,"triangles":528,"placement":[0,0,0]},
 "AST-ATR-001_botanical_nursery_open001.glb":{"sha256":"0b5777db94e1f035bf36cc7afb85fece8a734e4ac22c759a2c83711c6ed68573","nodes":120,"mesh_nodes":120,"surfaces":120,"triangles":9392,"placement":[0,0,0]},
 "WP04_botanical_nursery.glb":{"sha256":"d34662e5f1579e9f025f5dacf4967184ef1a71c7ecd5f23826bed74820e551fb","nodes":1040,"mesh_nodes":1011,"surfaces":1614,"triangles":423648,"placement":[8,27,-216]},
 "WP03_cloud_conservatory.glb":{"sha256":"c42eeed67653c9171c32c47813168342d43a1705744fcf8b31d8acdcdbf7c7c1","nodes":760,"mesh_nodes":655,"surfaces":2298,"triangles":806548,"placement":[0,0,0]}
}
const COURT_ALIASES := {
 "BOTCOURT_port_PORTAL_CLOSURE_Bracket_-217.2":"BOTCOURT_port_PORTAL_CLOSURE_Bracket_-217_2",
 "BOTCOURT_port_PORTAL_CLOSURE_Bracket_-214.8":"BOTCOURT_port_PORTAL_CLOSURE_Bracket_-214_8",
 "BOTCOURT_port_PORTAL_CLOSURE_Label.001":"BOTCOURT_port_PORTAL_CLOSURE_Label_001"
}
const ROOM_MAP_FILES := {
 "WP04_botanical_nursery.glb":"res://data/architecture/botanical_pair/WP04_IMPORT_IDENTITY_MAP.json",
 "WP03_cloud_conservatory.glb":"res://data/architecture/botanical_pair/WP03_IMPORT_IDENTITY_MAP.json"
}
# Intentionally empty: only a separately authorized, observed scoped import can supply
# these maps. Empty hashes are a hard failed gate, never an identity-map fallback.
const ROOM_MAP_SHA256 := {"WP04_botanical_nursery.glb": "9919793ea872630b8853b0c06b7de47f467199bf65b1aa4492b8785fa194c389", "WP03_cloud_conservatory.glb": "c6176110e66bf56cf450d1b4489e14795f2b44afddbe2415f2d34aabffceee73"}
static var _validation_failed := false
static var _validation_completed := false

func _initialize() -> void:
 call_deferred("_run")

func _run() -> void:
 if not OS.is_debug_build():
  push_error("Geometry assertion test requires a debug Godot build")
  quit(1)
  return
 var args := OS.get_cmdline_user_args()
 if args.is_empty():
  for filename in ASSETS:
   if not asset_inputs_ready(str(filename)):
    quit(1)
    return
  validate_pair_sources()
 else:
  if args.size()!=1 or not str(args[0]).begins_with("--asset="):
   push_error("Expected no arguments or --asset=<one exact pinned GLB filename>")
   quit(1)
   return
  var filename := str(args[0]).trim_prefix("--asset=")
  if not asset_inputs_ready(filename):
   quit(1)
   return
  _validate_scoped_fixture(filename)
 if not validation_succeeded():
  push_error("Scoped botanical imported-source validation failed; no pass receipt")
  quit(1)
  return
 print("PASS: scoped botanical raw-GLB/import geometry and exact static-contact fidelity; no runtime traversal or design acceptance")
 quit(0)

static func _require(condition: bool, message: String = "Botanical imported-source invariant failed") -> void:
 if not condition:
  _validation_failed=true
  push_error(message)
  var tree := Engine.get_main_loop() as SceneTree
  if tree!=null: tree.quit(1)
  assert(condition,message)

static func validation_succeeded() -> bool:
 return _validation_completed and not _validation_failed

static func asset_inputs_ready(filename: String) -> bool:
 if not OS.is_debug_build() or not ASSETS.has(filename):
  push_error("Unsupported asset or non-debug geometry test: "+filename)
  return false
 var path := "res://assets/models/"+filename
 if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=str(ASSETS[filename].sha256):
  push_error("Missing or changed pinned raw source: "+filename)
  return false
 if not ResourceLoader.exists(path,"PackedScene"):
  push_error("Actual scoped import has not produced a PackedScene: "+filename)
  return false
 if not FileAccess.file_exists(HELPER) or not FileAccess.file_exists("res://scripts/static_contact_cache.gd") or FileAccess.get_sha256("res://scripts/static_contact_cache.gd")!=STATIC_CONTACT_SHA256:
  push_error("Retained medical geometry/static-contact helper is missing")
  return false
 if ROOM_MAP_FILES.has(filename):
  var pin := str(ROOM_MAP_SHA256[filename])
  var map_file := str(ROOM_MAP_FILES[filename])
  if pin.length()!=64 or not FileAccess.file_exists(map_file) or FileAccess.get_sha256(map_file)!=pin:
   push_error("Actual room import identity discovery and a pinned complete map are still required: "+filename)
   return false
 return true

static func validate_pair_sources() -> void:
 _validation_completed=false
 # Callers may use this before their own access fixture, without a full-world build.
 for filename in ASSETS:
  if not asset_inputs_ready(str(filename)):
   _validation_failed=true
   push_error("Botanical imported-source validation is blocked; no acceptance is granted")
   var tree := Engine.get_main_loop() as SceneTree
   if tree!=null: tree.quit(1)
   _require(false,"Scoped imported-source inputs/identity gate failed")
   return
 for filename in ASSETS:
  _validate_scoped_fixture(str(filename))

static func _validate_scoped_fixture(filename: String) -> void:
 var ship: Node3D=load("res://scripts/ship.gd").new()
 var fixture := Node3D.new()
 # Neither object enters the SceneTree, so ship._ready() and full build never run.
 var placement := _vector(ASSETS[filename].placement)
 var wrapper: Node3D=ship.model(fixture,filename,"ScopedSource",placement)
 validate_imported_asset(wrapper,filename)
 fixture.free()
 ship.free()
 if validation_succeeded(): print("BOTANICAL_SCOPED_GEOMETRY_PASS "+filename)

static func _vector(values: Array) -> Vector3:
 return Vector3(float(values[0]),float(values[1]),float(values[2]))

static func _source_transform(record: Dictionary) -> Transform3D:
 if record.has("matrix"):
  var m: Array=record.matrix
  _require(m.size()==16 and float(m[3])==0.0 and float(m[7])==0.0 and float(m[11])==0.0 and float(m[15])==1.0)
  return Transform3D(Basis(Vector3(m[0],m[1],m[2]),Vector3(m[4],m[5],m[6]),Vector3(m[8],m[9],m[10])),Vector3(m[12],m[13],m[14]))
 var q: Array=record.get("rotation",[0,0,0,1])
 var scale_data := _vector(record.get("scale",[1,1,1]))
 var basis := Basis(Quaternion(float(q[0]),float(q[1]),float(q[2]),float(q[3])))
 # Exact Godot 4.6 GLTFDocument TRS setter order: set_rotation, then
 # GLTFNode.set_scale orthonormalizes before multiplying Basis.from_scale.
 # Derive solely from raw source values; retain exact Transform3D equality.
 # https://github.com/godotengine/godot/blob/4.6/modules/gltf/structures/gltf_node.cpp
 if record.has("scale"):
  basis=basis.orthonormalized()*Basis.from_scale(scale_data)
 return Transform3D(basis,_vector(record.get("translation",[0,0,0])))

static func _name_map(filename: String, document: Dictionary) -> Dictionary:
 var result: Dictionary={}
 if ROOM_MAP_FILES.has(filename):
  _require(str(ROOM_MAP_SHA256[filename]).length()==64,"No invented room identity receipt")
  var map_file := str(ROOM_MAP_FILES[filename])
  _require(FileAccess.get_sha256(map_file)==str(ROOM_MAP_SHA256[filename]))
  var observed: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(map_file))
  _require(int(observed.schema)==1 and str(observed.source_sha256)==str(ASSETS[filename].sha256))
  _require(str(observed.godot_version)==str(Engine.get_version_info().string))
  var import_file := "res://assets/models/"+filename+".import"
  _require(FileAccess.file_exists(import_file) and str(observed.import_settings_sha256)==FileAccess.get_sha256(import_file))
  result=observed.source_to_runtime
  _require(result.size()==document.nodes.size(),"Room discovery must map every raw node explicitly")
 else:
  for record in document.nodes:
   var source_name := str(record.name)
   result[source_name]=str(COURT_ALIASES.get(source_name,source_name)) if filename=="AST-ATR-001_botanical_nursery_open001.glb" else source_name
 var used: Dictionary={}
 for record in document.nodes:
  var source_name := str(record.name)
  _require(result.has(source_name),"Missing exact source identity: "+source_name)
  var imported_name := str(result[source_name])
  _require(not imported_name.is_empty() and not used.has(imported_name),"Name map must be bijective")
  used[imported_name]=true
 _require(result.size()==document.nodes.size())
 return result

static func validate_imported_asset(wrapper: Node3D, filename: String) -> void:
 _validation_completed=false
 _require(asset_inputs_ready(filename),"No scoped validation without all source/import gates")
 _require(wrapper!=null and wrapper.get_child_count()==1)
 _require(wrapper.transform==Transform3D(Basis.IDENTITY,_vector(ASSETS[filename].placement)),"Exact source-room placement required")
 _require(str(wrapper.get_meta("catalogue_file",""))==filename)
 var helper=load(HELPER)
 # This calls only the retained mesh-exact contact validator, not its predecessor
 # preservation/full-runtime entry points.
 helper._crew_validate_model(wrapper,filename,int(ASSETS[filename].mesh_nodes))
 var source: Node3D=wrapper.get_child(0)
 _require(source.transform==Transform3D.IDENTITY,"No hidden imported-root placement or axis conversion is allowed")
 var raw: Dictionary=helper._sports_sign_glb(filename)
 var document: Dictionary=raw.document
 var binary: PackedByteArray=raw.binary
 var aliases := _name_map(filename,document)
 var reverse: Dictionary={}
 for key in aliases: reverse[str(aliases[key])]=str(key)
 var actual: Dictionary={}
 for node in source.find_children("*","Node3D",true,false):
  # Only the exact two children introduced by the already-checked production
  # contact helper are excluded; no source-name sanitization or generic pruning.
  if node is StaticBody3D and str(node.name)=="StaticContact" and node.get_parent() is MeshInstance3D:
   _require(node.get_child_count()==1 and node.has_node("SharedShape"))
   continue
  if node is CollisionShape3D and str(node.name)=="SharedShape" and node.get_parent() is StaticBody3D and str(node.get_parent().name)=="StaticContact" and node.get_parent().get_parent() is MeshInstance3D:
   continue
  _require(reverse.has(str(node.name)),"Unexpected imported identity: "+filename+"/"+str(node.name))
  var source_name := str(reverse[str(node.name)])
  _require(not actual.has(source_name),"Duplicate imported source identity")
  actual[source_name]=node
 _require(document.nodes.size()==int(ASSETS[filename].nodes) and actual.size()==document.nodes.size())
 var parents: Dictionary={}
 for index in range(document.nodes.size()):
  for child in document.nodes[index].get("children",[]):
   _require(not parents.has(int(child)),"Raw source must retain unique parentage")
   parents[int(child)]=index
 var mesh_count := 0
 var surface_count := 0
 var triangle_count := 0
 var material_seen: Dictionary={}
 for index in range(document.nodes.size()):
  var record: Dictionary=document.nodes[index]
  var name_key := str(record.name)
  _require(actual.has(name_key),"Missing raw named node: "+name_key)
  var node: Node3D=actual[name_key]
  var expected_parent: Node=source if not parents.has(index) else actual[str(document.nodes[int(parents[index])].name)]
  _require(node.get_parent()==expected_parent,"Exact source parentage changed")
  _require(node.transform==_source_transform(record),"Raw local transform changed: "+filename+"/"+name_key)
  if not record.has("mesh"): continue
  _require(node is MeshInstance3D)
  var visual := node as MeshInstance3D
  _require(visual.material_override==null and visual.visible)
  var body: StaticBody3D=visual.get_node_or_null("StaticContact") as StaticBody3D
  _require(body!=null and body.transform==Transform3D.IDENTITY)
  var collision: CollisionShape3D=body.get_node_or_null("SharedShape") as CollisionShape3D
  _require(collision!=null and collision.transform==Transform3D.IDENTITY and collision.shape is ConcavePolygonShape3D)
  _require(collision.shape.get_faces()==visual.mesh.create_trimesh_shape().get_faces(),"Actual production contact shape differs from its visible mesh")
  var primitives: Array=document.meshes[int(record.mesh)].primitives
  _require(visual.mesh.get_surface_count()==primitives.size())
  mesh_count+=1
  for surface in range(primitives.size()):
   var primitive: Dictionary=primitives[surface]
   _require(int(primitive.get("mode",4))==4)
   _require(primitive.attributes.has("POSITION") and primitive.attributes.has("NORMAL") and primitive.attributes.has("TEXCOORD_0"))
   var pa: Dictionary=helper._team_lounge_accessor(document,binary,int(primitive.attributes.POSITION))
   var na: Dictionary=helper._team_lounge_accessor(document,binary,int(primitive.attributes.NORMAL))
   var ua: Dictionary=helper._team_lounge_accessor(document,binary,int(primitive.attributes.TEXCOORD_0))
   _require(pa.type=="VEC3" and na.type=="VEC3" and ua.type=="VEC2")
   _require(int(pa.component_type)==5126 and int(na.component_type)==5126 and int(ua.component_type)==5126)
   _require(int(pa.count)==int(na.count) and int(pa.count)==int(ua.count))
   var pv: PackedFloat32Array=pa.bytes.to_float32_array()
   var nv: PackedFloat32Array=na.bytes.to_float32_array()
   var uv: PackedFloat32Array=ua.bytes.to_float32_array()
   var positions := PackedVector3Array()
   var normals := PackedVector3Array()
   var uvs := PackedVector2Array()
   var keys: Array[String]=[]
   for vertex in range(int(pa.count)):
    positions.append(Vector3(pv[vertex*3],pv[vertex*3+1],pv[vertex*3+2]))
    normals.append(Vector3(nv[vertex*3],nv[vertex*3+1],nv[vertex*3+2]))
    uvs.append(Vector2(uv[vertex*2],uv[vertex*2+1]))
    keys.append(helper._team_lounge_corner_key(positions[vertex],uvs[vertex]))
   var order: PackedInt32Array=helper._team_lounge_source_indices(document,binary,primitive,int(pa.count))
   _require(order.size()%3==0)
   var expected_triangles: Dictionary={}
   for start in range(0,order.size(),3):
    var swap := int(order[start+1])
    order[start+1]=order[start+2]
    order[start+2]=swap
    # glTF CCW becomes Godot CW; only cyclic permutations are equivalent.
    var corners: Array[String]=[keys[order[start]],keys[order[start+1]],keys[order[start+2]]]
    var key: String=helper._team_lounge_oriented_triangle(corners)
    expected_triangles[key]=int(expected_triangles.get(key,0))+1
   _require(helper._team_lounge_import_surface(visual.mesh,surface)==expected_triangles,"Exact raw position/UV/winding/multiplicity mismatch: "+filename+"/"+name_key)
   # Includes the two unchanged court text meshes and their degenerate triangles.
   # No degenerate-face exemption or fabricated imported acceptance is allowed.
   var arrays: Array=[]
   arrays.resize(Mesh.ARRAY_MAX)
   arrays[Mesh.ARRAY_VERTEX]=positions
   arrays[Mesh.ARRAY_NORMAL]=normals
   arrays[Mesh.ARRAY_TEX_UV]=uvs
   arrays[Mesh.ARRAY_INDEX]=order
   var expected := ArrayMesh.new()
   expected.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
   _require(_normal_keys(visual.mesh,surface)==_normal_keys(expected,0),"Raw normal storage-equivalence mismatch: "+filename+"/"+name_key)
   var material_index := int(primitive.material)
   var material: Material=visual.get_active_material(surface)
   _require(visual.get_surface_override_material(surface)==null)
   _require(material!=null and material.resource_name==str(document.materials[material_index].name),"Exact source material assignment required")
   if material_seen.has(material_index):
    _require(material_seen[material_index]==material,"Source material sharing changed")
   else:
    _validate_material(material,document.materials[material_index])
    material_seen[material_index]=material
   surface_count+=1
   triangle_count+=int(order.size()/3)
 _require(mesh_count==int(ASSETS[filename].mesh_nodes))
 _require(surface_count==int(ASSETS[filename].surfaces))
 _require(triangle_count==int(ASSETS[filename].triangles))
 _validation_completed=not _validation_failed

static func _normal_keys(mesh: Mesh, surface: int) -> Dictionary:
 var arrays: Array=mesh.surface_get_arrays(surface)
 var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
 var normals: PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
 var uvs: PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV]
 _require(vertices.size()==normals.size() and vertices.size()==uvs.size())
 var order := PackedInt32Array()
 if arrays[Mesh.ARRAY_INDEX]!=null: order=arrays[Mesh.ARRAY_INDEX]
 if order.is_empty():
  for index in range(vertices.size()): order.append(index)
 _require(order.size()%3==0)
 var keys: Array[String]=[]
 for index in range(vertices.size()):
  keys.append(var_to_bytes(vertices[index]).hex_encode()+":"+var_to_bytes(normals[index]).hex_encode()+":"+var_to_bytes(uvs[index]).hex_encode())
 var result: Dictionary={}
 var helper=load(HELPER)
 for start in range(0,order.size(),3):
  var corners: Array[String]=[keys[order[start]],keys[order[start+1]],keys[order[start+2]]]
  var key: String=helper._team_lounge_oriented_triangle(corners)
  result[key]=int(result.get(key,0))+1
 return result

static func _validate_material(material: Material, record: Dictionary) -> void:
 _require(material is BaseMaterial3D,"Raw glTF PBR material requires a real imported PBR resource")
 var imported := material as BaseMaterial3D
 var pbr: Dictionary=record.get("pbrMetallicRoughness",{})
 _require(absf(imported.metallic-float(pbr.get("metallicFactor",1)))<0.000001)
 _require(absf(imported.roughness-float(pbr.get("roughnessFactor",1)))<0.000001)
 _require((imported.albedo_texture!=null)==pbr.has("baseColorTexture"),"Base-color texture presence changed")
 _require((imported.normal_texture!=null)==record.has("normalTexture"),"Normal texture presence changed")
 _require((imported.emission_texture!=null)==record.has("emissiveTexture"),"Emission texture presence changed")
 if bool(record.get("doubleSided",false)):
  _require(imported.cull_mode==BaseMaterial3D.CULL_DISABLED)
 else:
  _require(imported.cull_mode==BaseMaterial3D.CULL_BACK)
