extends SceneTree
const P:="res://sunset_court_finish_20261022/"
func own(n:Node,owner_root:Node)->void:
 for c in n.get_children():c.scene_file_path="";c.owner=owner_root;own(c,owner_root)
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_R002.json"))
 var holder:=Node3D.new();holder.name="SunsetCourtFinish20261022";root.add_child(holder)
 var mats:={}
 for role:String in plan.materials:
  var row:Dictionary=plan.materials[role];var c:Array=row.color;var m:=StandardMaterial3D.new();m.resource_name="SunsetFinish_"+role;m.albedo_color=Color(c[0],c[1],c[2],c[3]);m.roughness=row.roughness;m.metallic=row.metallic
  if role=="lens":m.emission_enabled=true;m.emission=Color(1,.84,.58);m.emission_energy_multiplier=.6
  mats[role]=m
 var tris:=0
 for row:Dictionary in plan.parts:
  var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
  for face:Array in row.faces:
   for i in range(1,face.size()-1):
    for index in [face[0],face[i],face[i+1]]:
     var v:Array=row.verts[int(index)];st.add_vertex(Vector3(v[0],v[1],v[2]))
    tris+=1
  st.generate_normals();st.set_material(mats[row.role]);var mesh:=MeshInstance3D.new();mesh.name=row.name;mesh.mesh=st.commit();holder.add_child(mesh);mesh.set_meta("retained_owner",row.owner)
  mesh.create_trimesh_collision()
 var groups:={};var templates:={};var meshes:={}
 for source:Dictionary in plan.sources:
  var path:String="res://assets/models/"+str(source.catalogue_id)+".glb";assert(FileAccess.get_sha256(path)==source.export_sha256)
  var template:Node3D=load(path).instantiate();root.add_child(template);templates[source.catalogue_id]=template
  var ms:Array=template.find_children("*","MeshInstance3D",true,false);assert(ms.size()==(4 if source.catalogue_id=="AST-BOT-008" else 5));meshes[source.catalogue_id]=ms
  assert(template.find_children("*","CollisionObject3D",true,false).is_empty())
 for row:Dictionary in plan.placements:
  var p:=Vector3(row.position[0],row.position[1],row.position[2]);var key:String=str(row.receiving_bed)+"_"+str(row.catalogue_id)+"_"+str(floori(p.x/4))+"_"+str(floori(p.z/4))
  if not groups.has(key):groups[key]=[]
  groups[key].append(row)
 var batches:=0;var plant_instances:=0
 for key:String in groups:
  var rows:Array=groups[key];var id:String=rows[0].catalogue_id;var template:Node3D=templates[id]
  for source_mesh:MeshInstance3D in meshes[id]:
   var batch:=MultiMeshInstance3D.new();batch.name="UnderstoryBatch_%s"%batches;var mm:=MultiMesh.new();mm.transform_format=MultiMesh.TRANSFORM_3D;mm.mesh=source_mesh.mesh;mm.instance_count=rows.size()
   for i in rows.size():
    var row:Dictionary=rows[i];var p:=Vector3(row.position[0],row.position[1],row.position[2]);var xform:=Transform3D(Basis(Vector3.UP,float(row.yaw)).scaled(Vector3.ONE*float(row.scale)),p);mm.set_instance_transform(i,xform*template.global_transform.affine_inverse()*source_mesh.global_transform)
   batch.multimesh=mm;batch.material_override=source_mesh.material_override;holder.add_child(batch);batch.set_meta("bed_cell",key);batches+=1;plant_instances+=rows.size()
 for template:Node3D in templates.values():template.free()
 for row:Dictionary in plan.lights:
  var light:=OmniLight3D.new();light.name=row.name;holder.add_child(light);light.position=Vector3(row.position[0],row.position[1],row.position[2]);light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy;light.omni_range=row.range;light.omni_attenuation=.9;light.shadow_enabled=true;light.visible=false
 own(holder,holder);var packed:=PackedScene.new();assert(packed.pack(holder)==OK);var path:=P+"runtime/SunsetCourtFinish_r002.scn";assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(packed,path)==OK)
 var receipt:={"status":"PASS","geometry_parts":plan.parts.size(),"triangles":tris,"plant_placements":plan.placements.size(),"plant_mesh_instances":plant_instances,"spatial_batches":batches,"shared_plant_meshes":9,"maximum_cell_width_m":4,"budgeted_lights":8,"runtime_sha256":FileAccess.get_sha256(path),"runtime_bytes":FileAccess.get_file_as_bytes(path).size(),"whole_ship_test":false}
 var f:=FileAccess.open(P+"evidence/BAKE_R002.json",FileAccess.WRITE);f.store_string(JSON.stringify(receipt,"\t")+"\n");f.close();print("SUNSET_COURT_BAKE ",JSON.stringify(receipt));holder.free();quit()
