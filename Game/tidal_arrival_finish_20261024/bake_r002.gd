extends SceneTree
const P := "res://tidal_arrival_finish_20261024/"
func _initialize()->void: call_deferred("run")
func own(n:Node,r:Node)->void:
 for c in n.get_children():c.scene_file_path="";c.owner=r;own(c,r)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN_r002.json"))
 if FileAccess.get_sha256(P+"TidalArrivalPortals_r002.glb")!=plan.glb_sha256:push_error("Arrival GLB differs");quit(1);return
 var target:=P+"runtime/TidalArrivalPortals_r002.scn"
 if FileAccess.file_exists(target):push_error("Immutable runtime already exists");quit(1);return
 var doc:=GLTFDocument.new();var state:=GLTFState.new();state.handle_binary_image=GLTFState.HANDLE_BINARY_EMBED_AS_UNCOMPRESSED
 var err:=doc.append_from_buffer(FileAccess.get_file_as_bytes(P+"TidalArrivalPortals_r002.glb"),P,state)
 if err!=OK:push_error("Native GLB parse failed");quit(1);return
 var src:Node3D=doc.generate_scene(state);root.add_child(src)
 var holder:=Node3D.new();holder.name="TidalArrivalPortals_r002";root.add_child(holder)
 var groups:={};var contact_groups:={};var parts:=0;var triangles:=0
 for mesh:MeshInstance3D in src.find_children("*","MeshInstance3D",true,false):
  var extras:Dictionary=mesh.get_meta("extras",{});var deck:=int(extras.deck);var xf:Transform3D=src.global_transform.affine_inverse()*mesh.global_transform
  for s in mesh.mesh.get_surface_count():
   var material:Material=mesh.get_active_material(s);var key:=str(deck)+":"+str(material.get_instance_id())
   if not groups.has(key):
    var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES);tool.set_material(material);groups[key]={"tool":tool,"deck":deck}
   groups[key].tool.append_from(mesh.mesh,s,xf)
  if bool(extras.runtime_collision):
   if not contact_groups.has(deck):contact_groups[deck]=PackedVector3Array()
   var faces:PackedVector3Array=contact_groups[deck];faces.append_array(xf*mesh.mesh.get_faces());contact_groups[deck]=faces
  parts+=1;triangles+=mesh.mesh.get_faces().size()/3
 if parts!=plan.parts.size():push_error("Native part count differs");src.free();holder.free();quit(1);return
 for key in groups:
  var row:Dictionary=groups[key];var m:=MeshInstance3D.new();m.name="D%d_Surface_%d"%[row.deck,holder.get_child_count()];m.mesh=row.tool.commit();m.set_meta("deck",row.deck);holder.add_child(m)
 for deck in contact_groups:
  var body:=StaticBody3D.new();body.name="D%d_FixedHeaderContacts"%deck;holder.add_child(body)
  var col:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.set_faces(contact_groups[deck]);shape.margin=.001;col.shape=shape;body.add_child(col)
 for row in plan.lights:
  var light:=SpotLight3D.new();light.name=row.name;holder.add_child(light);light.position=v(row.position);light.look_at(v(row.target))
  light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.light_energy=row.energy;light.spot_range=row.range;light.spot_angle=row.angle;light.spot_attenuation=row.attenuation
  light.shadow_enabled=true;light.visible=false;light.set_meta("fixture_powered",true);light.set_meta("source_fixture",row.source_fixture);light.set_meta("deck",row.deck)
 holder.set_meta("source_native_parts",parts);holder.set_meta("visual_accepted",false);holder.set_meta("preserved_rooms",131)
 own(holder,holder);var pack:=PackedScene.new();err=pack.pack(holder)
 if err!=OK:push_error("Arrival pack failed");src.free();holder.free();quit(1);return
 err=ResourceSaver.save(pack,target)
 if err!=OK:push_error("Arrival save failed");src.free();holder.free();quit(1);return
 var report:={"status":"PASS","native_parts":parts,"triangles":triangles,"spatial_material_batches":groups.size(),"contact_groups":contact_groups.size(),"fixture_lights":plan.lights.size(),"runtime_sha256":FileAccess.get_sha256(target),"runtime_bytes":FileAccess.get_file_as_bytes(target).size(),"engine_full_import":false}
 var f:=FileAccess.open(P+"evidence_r002/BAKE.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  ")+"\n");f.close();print(JSON.stringify(report));src.free();holder.free();quit(0)
