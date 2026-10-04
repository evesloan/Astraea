extends SceneTree
var counts: Dictionary = {}
var static_stock_groups := 0
func _initialize() -> void: call_deferred("run")
func visit(node: Node) -> void:
	if node.has_meta("stock_groups"): static_stock_groups += int(node.get_meta("stock_groups"))
	if node.has_meta("catalogue_file"):
		var key := str(node.get_meta("catalogue_file"))
		counts[key] = int(counts.get(key,0))+1
	for child in node.get_children():visit(child)
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(20):await physics_frame
	visit(main)
	var total := 0
	for count in counts.values():total+=int(count)
	var output := FileAccess.open("res://artifacts/asset_adoption.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"by_file":counts,"instances":total,"static_stock_groups":static_stock_groups,"scope":"Actual main-scene model presence; not completed rooms or final art"},"  ")+"\n")
	output.close()
	print("ADOPTION INVENTORY:",total,"model instances")
	quit()
