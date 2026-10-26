extends SceneTree
class Budget:
 extends "res://scripts/lighting_budget.gd"
 func _has_visible_sample(_light:Light3D)->bool:return true
func _initialize()->void:call_deferred("run")
func run()->void:
 var ship:=Node3D.new();root.add_child(ship)
 var systems:=Node.new();systems.name="ShipSystems";ship.add_child(systems)
 var budget:=Budget.new();budget.name="LocalShadowSourceBudget";systems.add_child(budget);budget.set_process(false)
 var actor:=Node3D.new();ship.add_child(actor);budget.configure(ship,actor)
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var family:=Node3D.new();family.name="FamilySpecialty47_20261022";districts.add_child(family)
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://family_specialty_bank_20261022/PACKAGE_R002.json"))
 var lights:Array[Light3D]=[]
 for room:Dictionary in package.rooms:
  var home:=Node3D.new();home.name=room.allocation.proposed_runtime_id;family.add_child(home)
  for data:Dictionary in room.lights:
   var light:=SpotLight3D.new();light.name=data.name;home.add_child(light);light.position=Vector3(data.position[0],data.position[1],data.position[2]);light.rotation.x=-PI/2;light.light_color=Color(1,.90,.74);light.light_energy=data.energy;light.spot_range=data.range;light.spot_angle=72;light.shadow_enabled=true;light.visible=false;lights.append(light)
 var owner=load("res://precompiled_private_cells_20261026/fixture_owner.gd")
 var last:SpotLight3D=lights[-1];var range_before:=last.spot_range;last.spot_range+=1
 assert(owner.reconcile(ship).has("failed") and budget.sources.is_empty(),"Mismatch must reject before all writes")
 last.spot_range=range_before
 var first:Dictionary=owner.reconcile(ship);assert(not first.has("failed") and first.newly_registered==lights.size())
 var again:Dictionary=owner.reconcile(ship);assert(not again.has("failed") and again.newly_registered==0)
 var ids:Array=[]
 for light:Light3D in lights:ids.append(light.get_instance_id());assert(budget.sources.count(light)==1 and budget.requested_shadow[light.get_instance_id()])
 var home:Node3D=family.get_child(0);family.remove_child(home);budget.refresh();family.add_child(home)
 assert(owner.reconcile(ship).newly_registered==0)
 for i in lights.size():assert(lights[i].get_instance_id()==ids[i])
 var active:=0
 for light:Light3D in lights:
  if light.visible:active+=1;assert(light.shadow_enabled)
 assert(active<=8 and active>0)
 var output:=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS","first":first,"second":again,"active":active,"mismatch_before_writes":true,"detach_reattach_same_ids":true,"scope":"Actual retained source light records and original budget ranking; visibility predicate stubbed only in focused fixture test"},"  ")+"\n")
 ship.free();quit()
