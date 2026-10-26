extends "res://visible_resource_budget_20261026/check_precompiled_private_tram.gd"
# Stationary actual-ship diagnostic; no movement, boarding or performance claim.
func operate(_assembly:Node3D)->Dictionary:
 var manager:Node=ship.private_detail_residency
 var snapshot:Dictionary=manager.compiled_lighting()
 var sources:Dictionary={}
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light in budget.sources:
  if is_instance_valid(light):sources[light.get_instance_id()]=light
 for id:int in manager.compiled_light_refs:
  var light=manager.compiled_light_refs[id].get_ref()
  if light!=null:sources[id]=light
 var cells:Array=[]
 var source:Node3D
 var source_home:Node3D
 var source_room:String=""
 for entry:Dictionary in manager.entries:
  if str(entry.record.model_file)!="FamilySpecialty_423_r001.tscn":continue
  var row:Dictionary=manager.compiled_records[str(entry.record.model_file)]
  require(FileAccess.get_sha256(row.compiled)==row.sha256,"Exact protected room source")
  source=load(str(row.compiled)).instantiate()
  source_home=entry.home.get_ref();source_room=str(entry.record.room_id)
  break
 require(source!=null and source_home!=null,"Retained actual room owner available")
 if failures>0:return {"diagnostic":"source_owner_missing"}
 for node:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
   if not node.has_meta("precompiled_fallback"):continue
   var records:Array=node.get_meta("precompiled_fallback")
   var box:=AABB();var initialized:=false;var members:Array=[]
   for record:Array in records:
    var bounds:AABB=source_home.global_transform*record[0]*record[1].get_aabb()
    box=box.merge(bounds) if initialized else bounds;initialized=true
    members.append(bounds)
   var overlaps:Array=[]
   for light:Dictionary in snapshot.lights:
    if light.mask&int(records[0][3])==0:continue
    if light.kind!=0 and light.position.distance_squared_to(light.position.clamp(box.position,box.end))>light.reach*light.reach:continue
    var actual:Light3D=sources.get(light.id)
    var covered:=0
    for bounds:AABB in members:
     if light.kind==0 or light.position.distance_squared_to(light.position.clamp(bounds.position,bounds.end))<=light.reach*light.reach:covered+=1
    overlaps.append({"name":str(actual.name),"path":str(actual.get_path()) if actual.is_inside_tree() else "detached/"+str(actual.name),"kind":light.kind,"range":light.reach,"position":str(light.position),"managed_eight":light.managed_eight,"visible":actual.visible,"shadow":actual.shadow_enabled,"fixture_powered":actual.get_meta("fixture_powered",true),"witness":actual.get_meta("retained_source_light_witness",false),"member_overlap_count":covered})
   cells.append({"room_id":source_room,"cell":str(node.name),"members":members.size(),"bounds":str(box),"overlaps":overlaps})
   if cells.size()>=3:break
 source.free()
 require(not cells.is_empty(),"Exact retained fallback cell bounds inspected against actual ship lights")
 return {"scope":"Actual inherited ship light state and exact retained Family423 room pose; off-tree precompiled cells, no activation, tram movement or performance acceptance","cells":cells,"excluded_inert":snapshot.inert_witnesses_excluded,"compiled_loads":manager.compiled_loads}
func finish(data:Dictionary)->void:
 var output:=FileAccess.open(argument("--report"),FileAccess.WRITE)
 output.store_string(JSON.stringify({"status":"DIAGNOSTIC_COMPLETE" if failures==0 else "FAIL","failures":failures,"data":data},"  ")+"\n");output.close()
 release_input()
 if is_instance_valid(presentation):presentation.queue_free();await process_frame;await process_frame
 quit(1 if failures>0 else 0)

