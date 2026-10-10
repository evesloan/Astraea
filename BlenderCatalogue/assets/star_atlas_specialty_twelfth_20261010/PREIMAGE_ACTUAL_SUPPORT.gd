extends SceneTree
var errors:Array=[]
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(90):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");paused=true;var space:=ship.get_world_3d().direct_space_state;var supports:=0;var missing:=0;var rows:Array=[]
 for sign in [-1,1]:
  var owner:Node3D=ship.get_node("ShipSpace/CentralResidentialStreetFloors/D14_STAR_ATLAS_MISSING_STREET_"+str(0 if sign<0 else 1))
  var bounds:Array=[]
  for z in [sign*98.1,sign*101.2,sign*104.3]:bounds.append([Vector3(-85.9,88.26,z-.1),Vector3(-82.1,88.28,z+.1)])
  for x in [-85.8,-82.2]:
   bounds.append([Vector3(x-.1,88.26,-104.8 if sign<0 else 104.56),Vector3(x+.1,88.28,-104.56 if sign<0 else 104.8)])
   bounds.append([Vector3(x-.1,88.26,sign*104.5-.1),Vector3(x+.1,88.28,sign*104.5+.1)])
  for b in bounds:
   var lo:Vector3=b[0];var hi:Vector3=b[1];var center:Vector3=(lo+hi)*.5;center.y=88.26;var points:Array[Vector3]=[center]
   for x in [lo.x+.001,hi.x-.001]:
    for z in [lo.z+.001,hi.z-.001]:points.append(Vector3(x,88.26,z))
   for at in points:
    var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at-Vector3.UP*.025,at+Vector3.UP*.025))
    var ok:bool=not h.is_empty()and owner.is_ancestor_of(h.collider)and absf(h.position.y-88.26)<.003
    if not ok:errors.append({"kind":"actual_D14_source_slab","point":str(at),"hit":str(h.get("position","none"))})
    rows.append({"point":str(at),"exact_owner":str(owner.name),"matched":ok,"exclude_count":0});supports+=1
 for z in [-101.2,101.2,-108.6,108.6]:
  for x in [-92.5,-84,-75.5]:
   var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,84.05,z),Vector3(x,83.95,z)))
   if not h.is_empty():errors.append({"kind":"unexpected_D13_floor","point":str(Vector3(x,84,z))})
   missing+=1
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");assert(residency.enabled)
 var report={"status":"PASS"if errors.is_empty()else"FAIL","stage":"actual baseline support before D14 production edits","source_slab_witnesses":supports,"D13_datum_clearance_probes":missing,"unrestricted_source_witnesses":rows,"culling_enabled":true,"errors":errors,"limits":"Bounded actual D14 retained street slab witnesses; no underlying D13 foundation assumed, primary engineering/load design held"}
 FileAccess.open("/tmp/astraea_d14_support_preimage.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "));print(JSON.stringify(report));quit(0 if errors.is_empty()else 1)
