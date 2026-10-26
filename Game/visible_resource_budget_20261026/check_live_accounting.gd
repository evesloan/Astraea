extends "res://tram_live_route_20261026/check_ownership.gd"
var accounting_started:=false
var counts:Dictionary={}
var resources_seen:Dictionary={}
var totals:Dictionary={"nodes":0,"mesh_buffer_bytes":0,"contact_face_bytes":0,"texture_pixels":0,"unique_resources":0}
func _process(delta:float)->bool:
 var result:bool=super._process(delta)
 if recording and route_motor!=null and route_motor.distance_travelled>=2.0 and not accounting_started:
  accounting_started=true;capture_accounting.call_deferred()
 return result
func resource_once(value:Resource,kind:String,row:Dictionary)->bool:
 if value==null:return false
 var id:=value.get_instance_id()
 if resources_seen.has(id):return false
 resources_seen[id]=true;totals.unique_resources+=1
 row[kind]=int(row.get(kind,0))+1
 return true
func visit(node:Node,row:Dictionary)->void:
 totals.nodes+=1;row.nodes+=1
 var kind:=node.get_class();row.classes[kind]=int(row.classes.get(kind,0))+1
 if node is MeshInstance3D:
  if node.mesh==null:row.null_mesh_nodes+=1
  else:
   var mesh:Mesh=node.mesh
   if resource_once(mesh,"unique_meshes",row) and mesh is ArrayMesh:
    for surface:Dictionary in mesh.get("_surfaces"):
     for key:String in ["vertex_data","attribute_data","skin_data","index_data"]:
      if surface.has(key):row.mesh_buffer_bytes+=surface[key].size()
   for i in mesh.get_surface_count():
    var mat:Material=node.get_active_material(i)
    if resource_once(mat,"unique_materials",row) and mat is BaseMaterial3D:
     for slot in BaseMaterial3D.TEXTURE_MAX:
      var texture:Texture2D=mat.get_texture(slot)
      if resource_once(texture,"unique_textures",row):row.texture_pixels+=texture.get_width()*texture.get_height()
 elif node is CollisionShape3D:
  if resource_once(node.shape,"unique_shapes",row):
   if node.shape is ConcavePolygonShape3D:row.contact_face_bytes+=node.shape.get_faces().size()*12
 for child in node.get_children():visit(child,row)
func capture_accounting()->void:
 release_input()
 var started:=Time.get_ticks_usec()
 var initial:=OS.get_static_memory_usage()
 var roots:Array[Node]=[ship]
 # Traverse live ship with attributed district owners, plus detached cached rooms.
 var districts:Node=ship.get_node("ShipSpace/Districts")
 var detached:Array[Node]=[]
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for entry:Dictionary in residency.entries:
  if not entry.room.is_inside_tree():detached.append(entry.room)
 var owners:Array[Node]=districts.get_children()
 for child in ship.get_children():
  if child.name!="ShipSpace":owners.append(child)
 for child in ship.get_node("ShipSpace").get_children():
  if child!=districts:owners.append(child)
 owners.append_array(detached)
 var rows:Array=[]
 for owner:Node in owners:
  var row:Dictionary={"owner":str(owner.get_path()) if owner.is_inside_tree() else "DETACHED/"+str(owner.name),"nodes":0,"null_mesh_nodes":0,"classes":{},"mesh_buffer_bytes":0,"contact_face_bytes":0,"texture_pixels":0}
  visit(owner,row);rows.append(row)
  totals.mesh_buffer_bytes+=row.mesh_buffer_bytes;totals.contact_face_bytes+=row.contact_face_bytes;totals.texture_pixels+=row.texture_pixels
 var data:Dictionary={"scope":"Actual selected ship at >=2m original-player tram movement; exclusive first-owner resource attribution, shared resources counted once. Raw payload bytes are not process RAM. Detached room state included. No content changed.","revision":"142a45f0cb3586321ff694efaa21612689509147","elapsed_us":Time.get_ticks_usec()-started,"static_before":initial,"static_after":OS.get_static_memory_usage(),"video_bytes":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),"texture_video_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),"buffer_video_bytes":Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED),"distance_m":route_motor.distance_travelled,"totals":totals,"owners":rows}
 var output:=argument("--report").get_base_dir().path_join("accounting.json")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(data,"\t"));f.close()
 print("ACCOUNTING_CAPTURE_COMPLETE ",JSON.stringify(totals)," duration_us=",data.elapsed_us)
 recording=false;quit(0)
