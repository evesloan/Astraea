extends RefCounted
const P:="res://family_aft_court_20261024/"
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func require_ok(ok:bool,message:String)->bool:
 if not ok:push_error("Family aft court: "+message)
 return ok
static func build(ship:Node3D)->Node3D:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 for path:String in plan.source_pins:
  if path.begins_with("Game/"):
   if not require_ok(FileAccess.get_sha256("res://"+path.trim_prefix("Game/"))==plan.source_pins[path],"Exact retained source differs: "+path):return null
 var house:=ship.get_node_or_null("ShipSpace/Districts/FamilyTerraceReceivingCandidate")as Node3D
 if not require_ok(house!=null and not house.has_node("FamilyAftCourt20261024"),"Expected unique Family owner"):return null
 var mats:={};var old_meshes:={}
 for mesh:MeshInstance3D in house.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  old_meshes[str(mesh.get_path())]={"mesh":mesh.mesh,"pose":mesh.global_transform}
  for si in range(mesh.mesh.get_surface_count()):
   var material:=mesh.get_active_material(si)
   if material!=null and str(material.resource_name).begins_with("COURT_"):mats[str(material.resource_name).trim_prefix("COURT_")]=material
 for row:Dictionary in plan.parts:
  if not require_ok(mats.has(row.role),"Retained material absent: "+str(row.role)):return null
 for row:Dictionary in plan.lights:
  var lamp:=house.get_node_or_null(row.original)as OmniLight3D
  if not require_ok(lamp!=null and lamp.position.distance_to(vec(row.position))<.001,"Original lantern owner differs"):return null
 var district:=Node3D.new();district.name="FamilyAftCourt20261024";house.add_child(district)
 var groups:={}
 for row:Dictionary in plan.parts:
  var centre:=Vector3.ZERO
  for v:Array in row.verts:centre+=vec(v)
  centre/=row.verts.size()
  var key:=str(row.role)+"_"+str(floori(centre.z/8))+"_"+str(floori(centre.y/4.5))
  if not groups.has(key):groups[key]={"rows":[],"role":row.role,"origin":Vector3(floorf(centre.x/8)*8,floorf(centre.y/4.5)*4.5,floorf(centre.z/8)*8)}
  groups[key].rows.append(row)
 var batches:=0
 for key:String in groups:
  var data:Dictionary=groups[key];var origin:Vector3=data.origin;var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES);var names:Array=[]
  for row:Dictionary in data.rows:
   names.append(row.name)
   for face:Array in row.faces:
    for i in range(1,face.size()-1):
     var a:=vec(row.verts[int(face[0])]);var b:=vec(row.verts[int(face[i])]);var c:=vec(row.verts[int(face[i+1])]);var normal:=(b-a).cross(c-a).normalized()
     for index in [face[0],face[i+1],face[i]]:
      var v:=vec(row.verts[int(index)]);st.set_normal(normal)
      if absf(normal.y)>.7:st.set_uv(Vector2(v.x,v.z)*.35)
      elif absf(normal.x)>.7:st.set_uv(Vector2(v.z,v.y)*.35)
      else:st.set_uv(Vector2(v.x,v.y)*.35)
      st.add_vertex(v-origin)
  st.set_material(mats[data.role]);var mesh:=MeshInstance3D.new();mesh.name="Architecture_%03d"%batches;mesh.mesh=st.commit();district.add_child(mesh);mesh.position=origin;mesh.set_meta("authored_part_names",names);mesh.set_meta("retained_material_role",data.role)
  var shape:=mesh.mesh.create_trimesh_shape();var body:=StaticBody3D.new();body.name="AuthoredContact";mesh.add_child(body);var contact:=CollisionShape3D.new();contact.shape=shape;body.add_child(contact);batches+=1
 var templates:={};var source_meshes:={};var plant_groups:={}
 for source:Dictionary in plan.sources:
  var template:Node3D=load("res://assets/models/"+source.catalogue_id+".glb").instantiate();templates[source.catalogue_id]=template
  source_meshes[source.catalogue_id]=template.find_children("*","MeshInstance3D",true,false)
  if not require_ok(source_meshes[source.catalogue_id].size()==source.runtime_mesh_count,"Retained plant family changed"):district.queue_free();return null
 for row:Dictionary in plan.plants:
  var key:=str(row.catalogue_id)+"_"+str(row.cell)
  if not plant_groups.has(key):plant_groups[key]=[]
  plant_groups[key].append(row)
 var plant_batches:=0
 for key:String in plant_groups:
  var rows:Array=plant_groups[key];var id:String=rows[0].catalogue_id
  for original:MeshInstance3D in source_meshes[id]:
   var source_pose:=original.transform;var parent:=original.get_parent()
   while parent!=templates[id]:source_pose=(parent as Node3D).transform*source_pose;parent=parent.get_parent()
   var multi:=MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D;multi.mesh=original.mesh;multi.instance_count=rows.size()
   for i in range(rows.size()):
    var row:Dictionary=rows[i];multi.set_instance_transform(i,Transform3D(Basis(Vector3.UP,row.yaw).scaled(Vector3.ONE*row.scale),vec(row.position))*source_pose)
   var mesh:=MultiMeshInstance3D.new();mesh.name="PlantBatch_%03d"%plant_batches;mesh.multimesh=multi;mesh.material_override=original.material_override;mesh.set_meta("source_catalogue_id",id);mesh.set_meta("source_instance_count",rows.size());district.add_child(mesh);plant_batches+=1
 for template:Node3D in templates.values():template.free()
 for row:Dictionary in plan.lights:
  var old:OmniLight3D=house.get_node(row.original);old.set_meta("fixture_powered",false);old.visible=false;old.shadow_enabled=false;old.set_meta("aft_court_directional_successor",row.name)
  var lamp:=SpotLight3D.new();lamp.name=row.name;district.add_child(lamp);lamp.position=vec(row.position);lamp.look_at(vec(row.target),Vector3.RIGHT);lamp.light_color=Color(row.color[0],row.color[1],row.color[2]);lamp.light_energy=row.energy;lamp.spot_range=row.range;lamp.spot_angle=row.angle;lamp.shadow_enabled=true;lamp.visible=false;lamp.set_meta("fixture_powered",true);lamp.set_meta("illumination_anchor",vec(row.anchor));lamp.set_meta("retained_fixture",row.original)
 for path:String in old_meshes:
  var original:=ship.get_node(path)as MeshInstance3D;var before:Dictionary=old_meshes[path]
  if not require_ok(original!=null and original.mesh==before.mesh and original.global_transform.is_equal_approx(before.pose),"Original mesh/pose changed: "+path):return null
 # Keep a count receipt, not an extra permanent strong-reference mesh cache.
 district.set_meta("original_meshes_preserved",old_meshes.size());district.set_meta("architecture_parts",plan.parts.size());district.set_meta("architecture_batches",batches);district.set_meta("plant_placements",plan.plants.size());district.set_meta("plant_batches",plant_batches);district.set_meta("new_floor_area_m2",0);district.set_meta("new_capacity",0);district.set_meta("finished",false)
 return district
