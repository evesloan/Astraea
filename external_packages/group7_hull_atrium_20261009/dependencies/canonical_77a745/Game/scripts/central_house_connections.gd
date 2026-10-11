extends RefCounted
# Missing-only street floors. Support frames, wintergardens and final acceptance remain open.
static func build(ship:Node3D)->Node3D:
	var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_RESIDENTIAL_STREETS.json"))
	for path in d.source_checks:
		assert(FileAccess.get_sha256("res://"+str(path))==str(d.source_checks[path]))
	var floors:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,d.regions,{},"CentralResidentialStreetFloors")
	var guards:=Node3D.new()
	guards.name="CentralResidentialStreetGuards"
	floors.add_child(guards)
	for edge in d.exposed_edge_guards:
		var a:=Vector3(edge.a[0],edge.a[1],edge.a[2])
		var b:=Vector3(edge.b[0],edge.b[1],edge.b[2])
		guard_segment(ship,guards,str(edge.id),a,b)
	floors.set_meta("finished",false)
	ship.set_meta("central_residential_streets_installed",true)
	return floors

static func guard_segment(ship:Node3D,parent:Node3D,label:String,a:Vector3,b:Vector3)->void:
	ship.beam(parent,label+"Rail",a+Vector3.UP*1.1,b+Vector3.UP*1.1,.04,ship.metal)
	var steps:int=maxi(1,ceili(a.distance_to(b)/2.0))
	for i in range(steps+1):
		var point:=a.lerp(b,float(i)/float(steps))
		ship.beam(parent,label+"Post",point,point+Vector3.UP*1.1,.035,ship.metal)
	var body:=StaticBody3D.new()
	body.name=label+"Contact"
	parent.add_child(body)
	body.position=(a+b)*.5+Vector3.UP*.55
	body.rotation.y=-atan2(b.z-a.z,b.x-a.x)
	var collider:=CollisionShape3D.new()
	var shape:=BoxShape3D.new()
	shape.size=Vector3(a.distance_to(b),1.1,.08)
	collider.shape=shape
	body.add_child(collider)
