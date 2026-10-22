extends SceneTree
func _initialize()->void:call_deferred("run")
func own(n:Node,r:Node)->void:
	for c in n.get_children():c.owner=r;own(c,r)
func run()->void:
	var p:="res://sunset_specialty_bank_20261022/"
	var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(p+"evidence/RECEIVING_BUILD_R002.json"))
	assert(FileAccess.get_sha256("res://"+str(receipt.export))==receipt.export_sha256)
	var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://"+str(receipt.export),state)==OK)
	var node:Node3D=doc.generate_scene(state);root.add_child(node);own(node,node)
	var pack:=PackedScene.new();assert(pack.pack(node)==OK);var dest:=p+"runtime/Sunset47Receiving_r002.scn";assert(not FileAccess.file_exists(dest));assert(ResourceSaver.save(pack,dest,ResourceSaver.FLAG_COMPRESS)==OK)
	print("RECEIVING_BAKED ",node.find_children("*","MeshInstance3D",true,false).size()," meshes")
	quit()
