extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var core:Node3D=ship.find_child("AftMidshipPublicCore_WIP",true,false);var meshes:Array=[]
 for m:MeshInstance3D in core.get_node("PrimaryCoreEnclosure").find_children("*","MeshInstance3D",true,false):
  var verts:Array=[]
  for i in range(m.mesh.get_surface_count()):
   for local in m.mesh.surface_get_arrays(i)[Mesh.ARRAY_VERTEX]:
    var v:Vector3=m.global_transform*local
    if v.y>=15.9 and v.y<=21.01 and v.x< -7.5:verts.append([v.x,v.y,v.z])
  if not verts.is_empty():meshes.append({"name":str(m.get_path()),"vertices":verts})
 var samples:Array=[];var space:=ship.get_world_3d().direct_space_state
 for x in [-8.3,-8.1,-8.0,-7.7,-4.2,-3.5,0.0]:
  for z in [288.7,293.5,405.2]:
   var at:=Vector3(x,16.5,z);var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.03);samples.append({"at":[x,16.5,z],"capsule_clear":capsule_clear(space,at),"floor":str(h.collider.get_path())if not h.is_empty()else"none"})
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_neighborhood_20261011/CORE_BOUNDARY_PROBE.json",FileAccess.WRITE).store_string(JSON.stringify({"meshes":meshes,"samples":samples},"  "));quit()
