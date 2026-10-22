extends RefCounted
const P:="res://atrium_ceiling_completion_20261022/"
static func finish(ship:Node3D)->Node3D:
 var pre:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/PREREQUISITES.json"))
 for path in pre.source_pins:assert(FileAccess.get_sha256("res://"+str(path))==str(pre.source_pins[path]))
 var parent:Node3D=ship.get_node("ShipSpace/Districts")
 assert(not parent.has_node("AtriumLanternCeiling20261022"),"Do not duplicate architectural owner")
 var cap:Node3D=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D18_atrium_structural_cap")
 var prior:MeshInstance3D=cap.find_children("*","MeshInstance3D",true,false)[0]
 var original:=prior.mesh
 var before:=var_to_bytes(original.surface_get_arrays(0)).hex_encode().sha256_text()+var_to_bytes(original.surface_get_arrays(1)).hex_encode().sha256_text()
 var bodies:=cap.find_children("*","StaticBody3D",true,false)
 var baked:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BAKE.json"))
 assert(FileAccess.get_sha256(str(baked.scene))==str(baked.sha256))
 var scene:Node3D=load(str(baked.scene)).instantiate();parent.add_child(scene)
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD.json"))
 for row in d.lights:
  var light:=SpotLight3D.new();light.name=str(row.name);scene.add_child(light)
  light.position=Vector3(row.position[0],row.position[1],row.position[2]);light.look_at(Vector3(row.target[0],row.target[1],row.target[2]),Vector3.RIGHT)
  light.light_color=Color(1,.80,.57);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=float(row.angle);light.shadow_enabled=true
  light.set_meta("illumination_anchor",Vector3(row.anchor[0],row.anchor[1],row.anchor[2]))
 # Extend the already integrated upper-gallery palette to D17; never replace its mesh/contact.
 var court:Node3D=parent.get_node("NightGardenReceivingCourts20261022")
 var stone:MeshInstance3D=court.find_child("Base_*",true,false)
 var wood:MeshInstance3D=court.find_child("Fore_CrownBeam_*",true,false)
 assert(stone!=null and wood!=null)
 var records:Array=[]
 for id in ["D17_atrium_circulation","D13_authored_atrium_terrace","D14_authored_atrium_terrace","D15_authored_atrium_terrace","D16_authored_atrium_terrace","D17_authored_atrium_terrace"]:
  var gallery:Node3D=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/"+id)
  var contacts:=gallery.find_children("*","StaticBody3D",true,false)
  for mesh:MeshInstance3D in gallery.find_children("*","MeshInstance3D",true,false):
   var unchanged:=mesh.mesh;var count:=unchanged.get_surface_count()
   assert(count==2 if id=="D17_atrium_circulation" else count==1)
   var digest:=""
   for surface in range(count):
    digest+=var_to_bytes(unchanged.surface_get_arrays(surface)).hex_encode().sha256_text()
    var side:bool=surface==1 or str(mesh.name)=="StructuralSidesAndUnderside"
    mesh.set_surface_override_material(surface,wood.get_active_material(0) if side else stone.get_active_material(0))
   assert(mesh.mesh==unchanged)
   records.append({"owner":id,"mesh":str(mesh.name),"geometry_sha256":digest})
  assert(contacts==gallery.find_children("*","StaticBody3D",true,false))
 assert(prior.mesh==original and bodies==cap.find_children("*","StaticBody3D",true,false))
 scene.set_meta("terrace_finish_records",records)
 scene.set_meta("cap_geometry_sha256",before);scene.set_meta("cap_contacts_unchanged",true);scene.set_meta("finished",false)
 return scene
