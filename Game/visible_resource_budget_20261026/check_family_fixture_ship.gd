extends "res://visible_resource_budget_20261026/check_private_light_overlap.gd"
func operate(_assembly:Node3D)->Dictionary:
 var manager:Node=ship.private_detail_residency
 var target:Dictionary={}
 for entry:Dictionary in manager.entries:
  if str(entry.record.model_file)=="FamilySpecialty_423_r001.tscn":target=entry;break
 require(not target.is_empty() and not is_instance_valid(target.detail),"Exact initially unloaded Family423 target")
 if failures>0:return {"stage":"target_not_available"}
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var before:=budget.sources.size();var home_id:int=target.home.get_ref().get_instance_id()
 var cycles:Array=[]
 for cycle in 3:
  var saved_before:int=manager.compiled_saved_submissions
  manager._load_entry(target)
  require(is_instance_valid(target.detail),"Actual selected-ship private detail activation")
  if failures>0:break
  var refs:Array[WeakRef]=[]
  for mesh:MeshInstance3D in target.detail.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh!=null:refs.append(weakref(mesh.mesh))
  var saved:int=manager.compiled_saved_submissions-saved_before
  var contacts:int=target.detail.find_children("RoomStaticContacts","StaticBody3D",true,false).size()
  manager._release_entry(target)
  var live:=0
  for ref:WeakRef in refs:
   if ref.get_ref()!=null:live+=1
  var registration:Dictionary=load("res://precompiled_private_cells_20261026/fixture_owner.gd").reconcile(ship)
  require(saved>0,"Actual batch substitutions required")
  require(registration.get("newly_registered",-1)==0 and budget.sources.size()==before,"Detail release/reload must not re-register permanent fixtures")
  require(target.home.get_ref().get_instance_id()==home_id and target.detail==null,"Persistent home preserved; detail released")
  cycles.append({"cycle":cycle,"saved_submissions":saved,"tracked_meshes":refs.size(),"still_live_after_release":live,"contact_owners":contacts,"registration":registration})
  if failures>0:break
 return {"scope":"Stationary selected inherited ship, explicit exact-room activation/release only; not natural movement, visual or FPS acceptance","cycles":cycles,"fixture_registration":private_installed.get("fixture_registration",{}),"home_id":home_id}
