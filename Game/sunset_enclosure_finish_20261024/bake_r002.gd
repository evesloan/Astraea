extends SceneTree
const P:="res://sunset_enclosure_finish_20261024/"
func _initialize()->void:call_deferred("run")
func own(n:Node,r:Node)->void:
 for c in n.get_children():c.scene_file_path="";c.owner=r;own(c,r)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func fail(message:String)->void:push_error(message);quit(1)
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_r002.json"))
 if FileAccess.get_sha256(P+"SunsetEnclosure_r002.glb")!=plan.glb_sha256:fail("Native GLB mismatch");return
 var target:=P+"runtime/SunsetEnclosure_r002.scn"
 if FileAccess.file_exists(target):fail("Immutable runtime exists");return
 var doc:=GLTFDocument.new();var state:=GLTFState.new();state.handle_binary_image=GLTFState.HANDLE_BINARY_EMBED_AS_UNCOMPRESSED
 var err:=doc.append_from_buffer(FileAccess.get_file_as_bytes(P+"SunsetEnclosure_r002.glb"),P,state)
 if err!=OK:fail("Native load failed");return
 var src:Node3D=doc.generate_scene(state);root.add_child(src)
 var holder:=Node3D.new();holder.name="SunsetEnclosure_r002";root.add_child(holder)
 var groups:={};var contacts:={};var materials:={};var count:=0;var triangles:=0
 for m:MeshInstance3D in src.find_children("*","MeshInstance3D",true,false):
  var e:Dictionary=m.get_meta("extras",{});var xf:Transform3D=src.global_transform.affine_inverse()*m.global_transform
  for s in m.mesh.get_surface_count():
   var mat:Material=m.get_active_material(s);materials[str(e.role)]=mat
   var key:=str(e.cell)+":"+str(e.role)
   if not groups.has(key):
    var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES);tool.set_material(mat);groups[key]={"tool":tool,"cell":e.cell,"role":e.role,"owner":e.retained_owner,"deck":e.deck}
   groups[key].tool.append_from(m.mesh,s,xf)
  if bool(e.runtime_collision):
   var key:=str(e.retained_owner)
   if not contacts.has(key):contacts[key]=PackedVector3Array()
   var faces:PackedVector3Array=contacts[key];faces.append_array(xf*m.mesh.get_faces());contacts[key]=faces
  count+=1;triangles+=m.mesh.get_faces().size()/3
 if count!=plan.parts.size():fail("Native part identity count differs");return
 for role in materials:
  err=ResourceSaver.save(materials[role],P+"runtime/r002_"+role+".tres")
  if err!=OK:fail("Material save failed");return
 for key in groups:
  var row:Dictionary=groups[key];var m:=MeshInstance3D.new();m.name="Surface_%03d"%holder.get_child_count();m.mesh=row.tool.commit();m.set_meta("cell",row.cell);m.set_meta("retained_owner",row.owner);m.set_meta("role",row.role);m.set_meta("deck",row.deck);holder.add_child(m)
 for key in contacts:
  var body:=StaticBody3D.new();body.name=key+"_FinishContact";holder.add_child(body)
  var col:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.set_faces(contacts[key]);shape.margin=.001;col.shape=shape;body.add_child(col)
 for row in plan.lights:
  var light:=SpotLight3D.new();light.name=row.name;holder.add_child(light);light.position=v(row.position);light.look_at(v(row.target))
  light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy;light.spot_range=row.range;light.spot_angle=row.angle;light.spot_attenuation=row.attenuation;light.shadow_enabled=true;light.visible=false;light.set_meta("source_fixture",row.source_fixture);light.set_meta("fixture_powered",true);light.set_meta("deck",row.deck)
 holder.set_meta("source_parts",count);holder.set_meta("new_capacity",0);holder.set_meta("visual_accepted",false)
 own(holder,holder);var pack:=PackedScene.new();err=pack.pack(holder)
 if err!=OK:fail("Pack failed");return
 err=ResourceSaver.save(pack,target)
 if err!=OK:fail("Save failed");return
 var report:={"status":"PASS","source_parts":count,"triangles":triangles,"spatial_material_batches":groups.size(),"wall_contact_groups":contacts.size(),"fixture_lights":plan.lights.size(),"runtime_sha256":FileAccess.get_sha256(target),"runtime_bytes":FileAccess.get_file_as_bytes(target).size(),"full_import":false}
 var f:=FileAccess.open(P+"evidence_r002/BAKE.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close();print(JSON.stringify(report));src.free();holder.free();quit(0)
