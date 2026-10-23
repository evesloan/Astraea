extends SceneTree
const H=preload("res://d04_surface_cells_20261023/batcher.gd")
func _initialize()->void:call_deferred("run")
func make_room()->Node3D:
 var room:=Node3D.new();root.add_child(room)
 var st:=SurfaceTool.new();st.create_from(BoxMesh.new(),0);var mesh:=st.commit();mesh.surface_set_material(0,StandardMaterial3D.new())
 for i in 3:
  var n:=MeshInstance3D.new();n.name="Part"+str(i);n.mesh=mesh;n.skeleton=NodePath("");n.position=Vector3(i*.3,0,0);room.add_child(n)
 return room
func run()->void:
 var checks:Array=[]
 var room:=make_room();var r:Dictionary=H.build(room,[]);assert(r.saved_submissions==2)
 H.set_enabled(room,true)
 for group:Dictionary in r.groups:
  for row:Dictionary in group.members:assert(row.node.visible and row.node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY)
 H.set_enabled(room,false);checks.append("Exact opaque positive case and original shadow passes restored");room.free()
 room=make_room();var material:StandardMaterial3D=room.get_child(0).get_active_material(0);material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
 assert(H.build(room,[]).saved_submissions==0);checks.append("Alpha blending rejected");room.free()
 room=make_room();var lights:Array=[]
 for i in 9:
  var light:=OmniLight3D.new();light.omni_range=10;root.add_child(light);lights.append(light)
 assert(H.build(room,lights).saved_submissions==0);checks.append("Per-object light limit rejected")
 for light in lights:light.free()
 room.free();room=make_room();room.get_child(1).position=Vector3(9,0,0);room.get_child(2).position=Vector3(18,0,0)
 assert(H.build(room,[]).saved_submissions==0);checks.append("Separated cells not merged");room.free()
 room=make_room();room.get_child(1).visibility_range_end=4;room.get_child(2).cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED
 assert(H.build(room,[]).saved_submissions==0);checks.append("Visibility-range and double-sided shadow semantics excluded");room.free()
 var f:=FileAccess.open("/tmp/d04_surface_guards.json",FileAccess.WRITE);f.store_string(JSON.stringify({"status":"PASS","checks":checks},"  "));f.close();print("SURFACE_GUARDS_PASS ",checks.size());quit()
