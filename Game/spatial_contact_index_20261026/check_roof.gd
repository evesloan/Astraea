extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var host=load("res://scripts/runtime_contracts_20261022/fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var actors:=Node3D.new();actors.name="PersistentActors";space.add_child(actors)
 var player:=Node3D.new();player.name="Player";actors.add_child(player);player.position=Vector3(10000,10000,10000)
 var manager=load("res://scripts/startup_contact_residency_20261022/manager.gd").new();host.add_child(manager);manager.setup(host);host.tidal_contacts=manager
 var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r010.json"))
 var nodes:Array=[]
 for row:Dictionary in config.roofs:
  var source:Node3D=load("res://assets/models/"+str(row.model)).instantiate()
  var original:MeshInstance3D=source.find_child(str(row.node),true,false);assert(original!=null)
  var mesh:=MeshInstance3D.new();mesh.name=str(row.node);mesh.mesh=original.mesh
  var site:=Node3D.new();site.name=str(row.receiver_root);districts.add_child(site);site.add_child(mesh);source.free()
  var body:=StaticBody3D.new();body.name="StaticContact";mesh.add_child(body)
  var collider:=CollisionShape3D.new();collider.name="SharedShape";collider.shape=mesh.mesh.create_trimesh_shape();collider.shape.margin=.031;body.add_child(collider)
  assert(manager._digest(mesh.mesh.get_faces())==str(row.faces_sha256))
  if str(row.receiver_root)=="TidalGardenReceivingCandidate":manager.adopt(site)
  nodes.append({"mesh":mesh,"collider":collider,"original":mesh.mesh})
 assert(manager.entries.size()==1)
 manager.refresh();assert(nodes[0].collider.shape==null,"Reproduce original distant roof release")
 var handoff:Dictionary=load("res://scripts/runtime_contracts_20261022/roof_handoff.gd").prepare(host)
 assert(manager.entries.is_empty() and nodes[0].collider.shape!=null)
 var owner:=Node3D.new();host.add_child(owner)
 load("res://scripts/fitted_wet_pavilions_20261015/roof_successor.gd").apply(host,owner,config.roofs)
 manager.refresh()
 for row:Dictionary in nodes:
  assert(row.mesh.mesh!=row.original and row.collider.shape!=null)
  assert(is_equal_approx(row.collider.shape.margin,.031))
  assert(manager._digest(row.collider.shape.get_faces())==manager._digest(row.mesh.mesh.get_faces()))
 var f:=FileAccess.open("C:/Users/cered/Documents/Codex/2026-10-22/task/Astraea-resume-20261025/spatial-contact-roof-001/result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"original_null_reproduced":true,"exact_roofs_cut":2,"original_margins_preserved":true,"stale_entries":manager.entries.size(),"handoff":handoff},"  "));f.close()
 host.free();print("ROOF_HANDOFF_PASS");quit()
