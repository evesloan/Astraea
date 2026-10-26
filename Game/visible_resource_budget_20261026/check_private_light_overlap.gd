extends "res://visible_resource_budget_20261026/check_precompiled_private_tram.gd"
# Stationary actual-ship diagnostic; no movement, boarding or performance claim.
func operate(_assembly:Node3D)->Dictionary:
 var manager:Node=ship.private_detail_residency
 var started:=Time.get_ticks_msec()
 while manager.compiled_loads==0 and Time.get_ticks_msec()-started<20000:await process_frame
 require(manager.compiled_loads>0,"Actual private activation available for light ownership diagnosis")
 if failures>0:return {"diagnostic":"no_actual_activation"}
 var snapshot:Dictionary=manager.compiled_lighting()
 var sources:Dictionary={}
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for light in budget.sources:
  if is_instance_valid(light):sources[light.get_instance_id()]=light
 for id:int in manager.compiled_light_refs:
  var light=manager.compiled_light_refs[id].get_ref()
  if light!=null:sources[id]=light
 var cells:Array=[]
 for entry:Dictionary in manager.entries:
  if not is_instance_valid(entry.detail):continue
  for node:Node in entry.detail.find_children("*","Node3D",true,false):
   if node.get_script()==null or node.get_script().resource_path!="res://static_bank_cells_20261026/render_owner.gd":continue
   var box:=AABB();var initialized:=false;var members:Array=[]
   for record:Array in node.records:
    var bounds:AABB=node.global_transform*record[0]*record[1].get_aabb()
    box=box.merge(bounds) if initialized else bounds;initialized=true
    members.append(bounds)
   var overlaps:Array=[]
   for light:Dictionary in snapshot.lights:
    if light.mask&int(node.records[0][3])==0:continue
    if light.kind!=0 and light.position.distance_squared_to(light.position.clamp(box.position,box.end))>light.reach*light.reach:continue
    var actual:Light3D=sources.get(light.id)
    var covered:=0
    for bounds:AABB in members:
     if light.kind==0 or light.position.distance_squared_to(light.position.clamp(bounds.position,bounds.end))<=light.reach*light.reach:covered+=1
    overlaps.append({"name":str(actual.name),"path":str(actual.get_path()) if actual.is_inside_tree() else "detached/"+str(actual.name),"kind":light.kind,"range":light.reach,"position":str(light.position),"managed_eight":light.managed_eight,"visible":actual.visible,"shadow":actual.shadow_enabled,"fixture_powered":actual.get_meta("fixture_powered",true),"witness":actual.get_meta("retained_source_light_witness",false),"member_overlap_count":covered})
   cells.append({"room_id":entry.record.room_id,"cell":str(node.name),"members":members.size(),"bounds":str(box),"overlaps":overlaps})
   if cells.size()>=3:break
  if cells.size()>=3:break
 require(not cells.is_empty(),"Actual fallback cells inspected")
 return {"scope":"Stationary actual inherited ship; no tram movement or performance acceptance","cells":cells,"excluded_inert":snapshot.inert_witnesses_excluded,"compiled_loads":manager.compiled_loads}
func finish(data:Dictionary)->void:
 var output:=FileAccess.open(argument("--report"),FileAccess.WRITE)
 output.store_string(JSON.stringify({"status":"DIAGNOSTIC_COMPLETE" if failures==0 else "FAIL","failures":failures,"data":data},"  ")+"\n");output.close()
 release_input()
 if is_instance_valid(presentation):presentation.queue_free();await process_frame;await process_frame
 quit(1 if failures>0 else 0)
