extends SceneTree
const P := "res://tidal_d14_landing_20261023/"
func _initialize()->void: call_deferred("run")
func demand(ok:bool, message:String)->void:
 if not ok: push_error(message);quit(1);assert(false,message)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func raw(path:String)->Node3D:
 var doc:=GLTFDocument.new();var state:=GLTFState.new()
 state.handle_binary_image=GLTFState.HANDLE_BINARY_EMBED_AS_UNCOMPRESSED
 var err:=doc.append_from_buffer(FileAccess.get_file_as_bytes(path),path.get_base_dir(),state)
 demand(err==OK,"fresh GLTF failed: "+path)
 var node:Node3D=doc.generate_scene(state);demand(node!=null,"missing GLTF scene");return node
func own(n:Node,r:Node)->void:
 for c in n.get_children():c.scene_file_path="";c.owner=r;own(c,r)
func merge_meshes(source:Node3D, destination:Node3D, prefix:String)->Dictionary:
 var groups:={};var triangles:=0;var identity:=[]
 for m:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  var xf:Transform3D=source.global_transform.affine_inverse()*m.global_transform
  identity.append({"name":str(m.name),"triangles":m.mesh.get_faces().size()/3})
  for s in m.mesh.get_surface_count():
   var material:Material=m.get_active_material(s);var key:=str(material.get_instance_id())
   if not groups.has(key):
    var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES);tool.set_material(material);groups[key]=tool
   groups[key].append_from(m.mesh,s,xf)
  triangles+=m.mesh.get_faces().size()/3
 for key in groups:
  var m:=MeshInstance3D.new();m.name=prefix+str(destination.get_child_count());m.mesh=groups[key].commit();destination.add_child(m)
 return {"batches":groups.size(),"triangles":triangles,"source_parts":identity}
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 demand(FileAccess.get_sha256(P+"TidalD14Landing_r001.glb")==plan.glb_sha256,"new native export changed")
 var def:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json"))
 var src:=raw(P+"TidalD14Landing_r001.glb");root.add_child(src)
 var holder:=Node3D.new();holder.name="TidalD14Landing_r001";root.add_child(holder)
 var report:=merge_meshes(src,holder,"ArchitectureMaterial_")
 demand(report.source_parts.size()==71,"71 native architecture parts required")
 var contact_faces:=PackedVector3Array();var contacts:=0
 for m:MeshInstance3D in src.find_children("*","MeshInstance3D",true,false):
  var meta:Dictionary=m.get_meta("extras",{})
  if bool(meta.get("runtime_collision",false)):
   var xf:Transform3D=src.global_transform.affine_inverse()*m.global_transform
   for point in m.mesh.get_faces():contact_faces.append(xf*point)
   contacts+=1
 var shape:=ConcavePolygonShape3D.new();shape.set_faces(contact_faces);shape.margin=.001
 var body:=StaticBody3D.new();body.name="AuthoredArchitectureContacts";holder.add_child(body)
 var collider:=CollisionShape3D.new();collider.shape=shape;body.add_child(collider)
 src.free()
 var templates:={};var plant_stats:={}
 for id:String in ["AST-BOT-002","AST-BOT-003"]:
  var path:String="res://assets/models/"+str(def.retained_asset_definitions[id].model_file)
  demand(FileAccess.get_sha256(path)==str(def.retained_asset_definitions[id].sha256),"plant source changed")
  var native:=raw(path);root.add_child(native)
  var combined:=Node3D.new();combined.name="RetainedBotanical";root.add_child(combined)
  plant_stats[id]=merge_meshes(native,combined,"RetainedMaterial_");native.free()
  templates[id]=combined
 for i in plan.plants.size():
  var row:Dictionary=plan.plants[i];var placed:Node3D=templates[row.catalogue_id].duplicate()
  placed.name="RetainedPlant_%02d"%i;placed.position=v(row.position);placed.rotation.y=row.yaw;placed.scale=Vector3.ONE*float(row.scale);placed.set_meta("catalogue_id",row.catalogue_id);holder.add_child(placed)
 for template in templates.values():template.free()
 for row in plan.lights:
  var light:=OmniLight3D.new();light.name=row.name;light.position=v(row.position);light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy;light.omni_range=row.range;light.shadow_enabled=true;light.visible=false;light.set_meta("fixture_powered",true);holder.add_child(light)
 holder.set_meta("native_source_parts",report.source_parts);holder.set_meta("visual_accepted",false)
 own(holder,holder);var packed:=PackedScene.new();var err:=packed.pack(holder);demand(err==OK,"pack failed")
 var out:=P+"runtime/TidalD14Landing_r001.scn";demand(not FileAccess.file_exists(out),"refuse overwrite runtime")
 err=ResourceSaver.save(packed,out);demand(err==OK,"save failed")
 report.merge({"status":"PASS","fresh_glb_parse":true,"contacts":contacts,"contact_triangles":contact_faces.size()/3,"plants":plant_stats,"plant_placements":6,"lights":2,"runtime_sha256":FileAccess.get_sha256(out),"runtime_bytes":FileAccess.get_file_as_bytes(out).size(),"full_import_or_ship_test":false})
 var f:=FileAccess.open(P+"evidence/BAKE.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t")+"\n");f.close()
 print("TIDAL_LANDING_BAKE parts=71 batches=",report.batches," contacts=",contacts," runtime_bytes=",report.runtime_bytes," plant_batches=",plant_stats["AST-BOT-002"].batches,"/",plant_stats["AST-BOT-003"].batches)
 holder.free();quit()
