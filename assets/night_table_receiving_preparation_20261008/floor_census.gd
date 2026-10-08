extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
 for i in range(30):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var rows:Array=[]
 for row in [["interior",Vector3(-31,60.88,216),Vector3(46-.0004,.24-.0004,68-.0004)],["external_link",Vector3(-6,60.88,216),Vector3(4-.0004,.24-.0004,4-.0004)]]:
  var shape:=BoxShape3D.new();shape.size=row[2];var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,row[1]);q.collision_mask=1;q.margin=0
  var hits:Array=[]
  for h in ship.get_world_3d().direct_space_state.intersect_shape(q,256):hits.append(str(h.collider.get_path()))
  rows.append({"region":row[0],"contacts":hits})
 var f:=FileAccess.open("/workspace/scratch/375c2e438292/night_table_receiving_20261008/FLOOR_CENSUS.json",FileAccess.WRITE);f.store_string(JSON.stringify({"existing_world_queries":rows,"slab_y":[60.76,61],"boundary_inset_for_exact_touching_seams_m":.0002,"candidate_installed":false},"  "))
 if rows[0].contacts.is_empty() and rows[1].contacts.is_empty():print("NIGHT TABLE PROPOSED FLOOR FIT PASS")
 else:print("NIGHT TABLE PROPOSED FLOOR CONTACT HOLD: ",JSON.stringify(rows))
 main.queue_free();await process_frame;quit()
