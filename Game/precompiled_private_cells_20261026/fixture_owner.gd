extends RefCounted
# Reconcile only exact authored Family fixtures; preflight every owner before writes.
const PACKAGE="res://family_specialty_bank_20261022/PACKAGE_R002.json"
const SHA="794eb975e3591e7c75acd8d7a5602a7aff89a0c1069212f74d007ad2a70528a0"
static func reconcile(ship:Node3D)->Dictionary:
 if FileAccess.get_sha256(PACKAGE)!=SHA:return {"failed":"Family source differs"}
 var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
 if budget==null or not is_instance_valid(budget.actor) or budget.shadow_source_budget!=8:return {"failed":"Configured original eight-source owner required"}
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PACKAGE))
 var pending:Array[Light3D]=[];var total:=0
 for room:Dictionary in package.rooms:
  var home:Node3D=ship.get_node_or_null("ShipSpace/Districts/FamilySpecialty47_20261022/"+str(room.allocation.proposed_runtime_id))
  if home==null:return {"failed":"Missing exact Family room"}
  for data:Dictionary in room.lights:
   var light:SpotLight3D=home.get_node_or_null(str(data.name)) as SpotLight3D
   if light==null:return {"failed":"Missing exact authored fixture"}
   var pos:=Vector3(data.position[0],data.position[1],data.position[2])
   if not light.position.is_equal_approx(pos) or not is_equal_approx(light.rotation.x,-PI/2) or not is_equal_approx(light.spot_range,float(data.range)) or not is_equal_approx(light.spot_angle,72.0) or not is_equal_approx(light.light_energy,float(data.energy)) or not light.light_color.is_equal_approx(Color(1,.90,.74)):
    return {"failed":"Authored fixture properties differ","name":str(light.name)}
   var id:=light.get_instance_id();var count:int=budget.sources.count(light)
   if count>1:return {"failed":"Duplicate existing light ownership"}
   if count==1:
    if not bool(budget.requested_shadow.get(id,false)):return {"failed":"Existing conflicting light ownership"}
   else:
    if budget.requested_shadow.has(id) or light.visible or not light.shadow_enabled:return {"failed":"Unregistered fixture state differs"}
    pending.append(light)
   total+=1
 for light:Light3D in pending:
  budget.sources.append(light)
  budget.requested_shadow[light.get_instance_id()]=true
 budget.refresh()
 return {"authored_fixtures":total,"newly_registered":pending.size(),"budget":8,"policy":"Original permanent room fixture identities and authored optical properties; exact once-only post-configuration registration"}
