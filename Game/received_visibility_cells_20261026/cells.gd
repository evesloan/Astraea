extends RefCounted
# Exact partition of the original conservative volume; no omitted empty cells.
# Cell budget bounds notifier overhead only, never the number of resident rooms.
const TARGET_EXTENT:=12.0
const MAX_CELLS:=32
static func partition(bounds:AABB)->Array[AABB]:
	var cells:Array[AABB]=[bounds]
	while cells.size()<MAX_CELLS:
		var selected:=-1;var longest:=TARGET_EXTENT;var axis:=0
		for i in cells.size():
			var candidate:int=cells[i].size.max_axis_index()
			if cells[i].size[candidate]>longest:
				longest=cells[i].size[candidate];selected=i;axis=candidate
		if selected<0:break
		var left:AABB=cells[selected];var right:AABB=left
		left.size[axis]*=.5;right.position[axis]+=left.size[axis];right.size[axis]-=left.size[axis]
		cells[selected]=left;cells.append(right)
	return cells
static func install(host:Node3D,bounds:AABB,label:String,entered:Callable)->Array[VisibleOnScreenNotifier3D]:
	var witnesses:Array[VisibleOnScreenNotifier3D]=[]
	for box:AABB in partition(bounds):
		var witness:=VisibleOnScreenNotifier3D.new();witness.name=label+"_Cell"+str(witnesses.size())
		witness.aabb=box;host.add_child(witness);witness.screen_entered.connect(entered);witnesses.append(witness)
	return witnesses
static func visible(entry:Dictionary)->bool:
	if not entry.has("visibility_cells"):return entry.witness.is_on_screen()
	for witness:VisibleOnScreenNotifier3D in entry.visibility_cells:
		if not is_instance_valid(witness):return true # Failed witness must not hide content.
		if witness.is_on_screen():return true
	return false
