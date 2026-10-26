extends SceneTree
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func capture(label:String)->Image:
 for i in 8:await process_frame
 await RenderingServer.frame_post_draw
 var image:=root.get_texture().get_image()
 assert(image.save_png(output.get_base_dir()+"/"+label+".png")==OK)
 return image
func run()->void:
 root.size=Vector2i(1920,1080);root.content_scale_size=root.size;root.content_scale_mode=Window.CONTENT_SCALE_MODE_VIEWPORT
 var host:=Node3D.new();root.add_child(host)
 var environment:=WorldEnvironment.new();environment.environment=Environment.new();environment.environment.background_mode=Environment.BG_COLOR;environment.environment.background_color=Color(.08,.09,.1);environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.environment.ambient_light_color=Color.WHITE;environment.environment.ambient_light_energy=.4;host.add_child(environment)
 var light:=DirectionalLight3D.new();light.rotation=Vector3(-.5,-.7,0);light.light_energy=.8;host.add_child(light)
 var row:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://precompiled_private_cells_20261026/FAMILY_COMPILE.json")).rows[0]
 var original:Node3D=load(str(row.source)).instantiate();host.add_child(original)
 var box:=AABB();var initialized:=false
 for mesh:MeshInstance3D in original.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var bound:AABB=mesh.global_transform*mesh.get_aabb();box=box.merge(bound) if initialized else bound;initialized=true
 var camera:=Camera3D.new();host.add_child(camera);camera.position=box.get_center()+Vector3(5,4,8);camera.look_at(box.get_center());camera.current=true;camera.fov=70
 var before:Image=await capture("original")
 original.free();await process_frame
 var compiled:Node3D=load(str(row.compiled)).instantiate();host.add_child(compiled)
 var selected:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(compiled,[{"id":light.get_instance_id(),"kind":0,"mask":light.light_cull_mask,"reach":0.0,"position":light.global_position,"managed_eight":false}])
 var after:Image=await capture("compiled")
 var a:PackedByteArray=before.get_data();var b:PackedByteArray=after.get_data();assert(a.size()==b.size())
 var changed:=0;var over8:=0;var maximum:=0;var total:=0
 for i in range(0,a.size(),4):
  var delta:=0
  for c in 3:
   var d:=absi(a[i+c]-b[i+c]);delta=maxi(delta,d);total+=d
  if delta>0:changed+=1
  if delta>8:over8+=1
  maximum=maxi(maximum,delta)
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"source":row.source,"compiled":row.compiled,"render_size":str(before.get_size()),"camera":str(camera.global_transform),"selected":selected,"changed_pixels":changed,"pixels_over_8":over8,"maximum_channel_difference":maximum,"mean_channel_difference":float(total)/(before.get_width()*before.get_height()*3),"scope":"Fixed reference-room original versus compiled mirrored full-resolution geometry/material/UV render. Not whole-ship performance or art acceptance."},"\t"));f.close();host.free();quit()
