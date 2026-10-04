extends Node3D
# Single moving physics cabin with independently positioned gates. Dynamic
# passengers and loose objects are never reparented to the moving platform.
var floor_heights:Array[float]=[84.0,88.5]
var deck_numbers:Array[int]=[13,14]
var gate_origin_xz:=Vector2(92.2,0)
var identity_prefix:="commons"
var district_label:="Commons"
var persistent_id:StringName=&"starboard_commons_lift_001"
var cabin:AnimatableBody3D
var cabin_gate:Node3D
var landing_gates:Array[Node3D]=[]
var current_floor:=0
var destination_floor:=0
var queued_floor:=-1
var phase:="opening"
var travel_velocity:=0.0
var maximum_speed:=1.1
var acceleration:=.65
var button_script=preload("res://scripts/lift_button.gd")
func _ready() -> void:
	assert(floor_heights.size()==2 and deck_numbers.size()==2,"This cabin has two authored floor-button positions")
	assert(floor_heights[1]>floor_heights[0])
	process_physics_priority=-20
	for i in range(2):
		var gate:Node3D=load("res://scripts/lift_gate.gd").new()
		gate.name="LandingGate_D"+str(deck_numbers[i])
		gate.persistent_id=StringName("D%d_%s_lift_gate"%[deck_numbers[i],identity_prefix])
		gate.position=Vector3(gate_origin_xz.x-.12,floor_heights[i],gate_origin_xz.y)
		gate.rotation.y=PI/2
		add_child(gate)
		landing_gates.append(gate)
		_button(self,Vector3(gate_origin_xz.x-.34,floor_heights[i]+1.3,gate_origin_xz.y+1.65),i,"D%d_%s_lift_call"%[deck_numbers[i],identity_prefix])
		_box(self,Vector3(gate_origin_xz.x-.055,floor_heights[i]-.055,gate_origin_xz.y),Vector3(.09,.11,2.4),"FixedSill_D"+str(deck_numbers[i]))
	cabin=AnimatableBody3D.new()
	cabin.name="Moving"+district_label+"Cabin"
	cabin.set_meta("persistent_id",identity_prefix+"_lift_cabin_001")
	cabin.sync_to_physics=false
	cabin.position=Vector3(gate_origin_xz.x,floor_heights[0],gate_origin_xz.y)
	cabin.rotation.y=-PI/2
	add_child(cabin)
	var visual:Node3D=(load("res://assets/models/AST-CIR-003.glb")as PackedScene).instantiate()
	visual.set_meta("catalogue_file","AST-CIR-003.glb")
	cabin.add_child(visual)
	# Simple convex platform follows the actual faceted platform perimeter.
	var points:=PackedVector3Array()
	for y in [-.18,0.0]:
		for p in [Vector2(-2,0),Vector2(2,0),Vector2(2,3.25),Vector2(1.65,3.6),Vector2(-1.65,3.6),Vector2(-2,3.25)]:points.append(Vector3(p.x,y,-p.y))
	var contact:=CollisionShape3D.new()
	var floor_shape:=ConvexPolygonShape3D.new()
	floor_shape.points=points
	floor_shape.margin=.001
	contact.shape=floor_shape
	cabin.add_child(contact)
	for side in [-1,1]:
		_box(cabin,Vector3(side*1.94,1.4,-1.695),Vector3(.12,2.8,3.11),"CabinSide")
		_box(cabin,Vector3(side*1.65,.245,-2.875),Vector3(.5,.49,.55),"CabinSeat")
		var corner_points:=PackedVector3Array()
		for h in [0.0,2.8]:
			for p in [Vector2(side*2,3.25),Vector2(side*1.65,3.6),Vector2(side*1.60,3.47),Vector2(side*1.88,3.19)]:corner_points.append(Vector3(p.x,h,-p.y))
		var corner_contact:=CollisionShape3D.new()
		var corner_shape:=ConvexPolygonShape3D.new()
		corner_shape.points=corner_points
		corner_shape.margin=.001
		corner_contact.shape=corner_shape
		cabin.add_child(corner_contact)
		# Actual pocket skins, not a solid box across moving leaf travel.
		_box(cabin,Vector3(side*1.55,1.325,-.205),Vector3(.70,2.65,.020),"CabinGateFrontSkin")
		_box(cabin,Vector3(side*1.55,1.325,-.0475),Vector3(.70,2.65,.025),"CabinGateBackSkin")
		_box(cabin,Vector3(side*1.89,1.405,-.125),Vector3(.02,2.81,.18),"CabinGatePocketEnd")
	_box(cabin,Vector3(0,2.75,-.125),Vector3(3.84,.20,.20),"CabinGateHeader")
	_box(cabin,Vector3(0,1.4,-3.535),Vector3(3.3,2.8,.13),"CabinRear")
	_box(cabin,Vector3(0,2.87,-1.8),Vector3(4,.14,3.6),"CabinRoof")
	for i in range(2):
		var marker:=visual.find_child("DATUM_floor_button_"+str(i),true,false)as Node3D
		_button(cabin,marker.position,i,identity_prefix+"_cabin_D"+str(deck_numbers[i]))
	for side in [-1,1]:
		var marker:=visual.find_child("DATUM_light_"+str(side),true,false)as Node3D
		var light:=SpotLight3D.new()
		cabin.add_child(light)
		light.position=marker.position
		light.rotation.x=-PI/2
		light.spot_angle=70
		light.spot_range=4
		light.light_energy=.7
		light.shadow_enabled=true
		light.light_color=Color(1,.95,.87)
	cabin_gate=load("res://scripts/lift_gate.gd").new()
	cabin_gate.name="CabinGate"
	cabin_gate.persistent_id=StringName(identity_prefix+"_cabin_gate")
	cabin_gate.position=Vector3(gate_origin_xz.x+.12,floor_heights[0],gate_origin_xz.y)
	cabin_gate.rotation.y=PI/2
	add_child(cabin_gate)
	# Cabin-gate fixed-frame contacts must move with the cabin as well.
	# Disable the frame's static contacts; body-owned fitted side walls protect it.
	for node in cabin_gate.find_children("StaticContact","StaticBody3D",true,false):node.queue_free()
	cabin.sync_to_physics=true
	_set_present()
func _box(parent:Node3D,pos:Vector3,size:Vector3,label:String) -> void:
	var contact:=CollisionShape3D.new()
	contact.name=label
	var shape:=BoxShape3D.new()
	shape.size=size
	shape.margin=.001
	contact.shape=shape
	contact.position=pos
	if parent is CollisionObject3D:parent.add_child(contact)
	else:
		var body:=StaticBody3D.new()
		parent.add_child(body)
		body.add_child(contact)
func _button(parent:Node3D,pos:Vector3,index:int,identity:String) -> void:
	var button:Node3D=button_script.new()
	button.controller=self
	button.floor_index=index
	button.display_deck=deck_numbers[index]
	button.district_label=district_label
	button.persistent_id=StringName(identity)
	button.name=identity
	button.position=pos
	button.rotation.y=-PI/2
	parent.add_child(button)
func request_floor(index:int) -> bool:
	if index<0 or index>=floor_heights.size():return false
	if phase=="moving":
		queued_floor=index
		return true
	destination_floor=index
	if index==current_floor:
		phase="opening"
		_set_present()
	else:
		phase="closing"
		cabin_gate.request_close()
		for gate in landing_gates:gate.request_close()
	return true
func _set_present() -> void:
	cabin_gate.cabin_present_and_stopped=true
	cabin_gate.request_open()
	for i in range(2):
		landing_gates[i].cabin_present_and_stopped=(i==current_floor)
		if i==current_floor:landing_gates[i].request_open()
		else:landing_gates[i].request_close()
func _physics_process(delta:float) -> void:
	if phase=="opening":
		if cabin_gate.open_fraction>.999 and landing_gates[current_floor].open_fraction>.999:
			phase="idle"
			if queued_floor>=0:
				var next:=queued_floor
				queued_floor=-1
				request_floor(next)
	elif phase=="closing":
		if not cabin_gate.is_closed_and_clear():return
		for gate in landing_gates:
			if not gate.is_closed_and_clear():return
		cabin_gate.cabin_present_and_stopped=false
		for gate in landing_gates:gate.cabin_present_and_stopped=false
		phase="moving"
	elif phase=="moving":
		var remaining:float=floor_heights[destination_floor]-cabin.position.y
		var wanted:float=sign(remaining)*min(maximum_speed,sqrt(2*acceleration*abs(remaining)))
		travel_velocity=move_toward(travel_velocity,wanted,acceleration*delta)
		if abs(remaining)<=abs(travel_velocity*delta)+.0001:
			cabin.position.y=floor_heights[destination_floor]
			travel_velocity=0
			current_floor=destination_floor
			phase="opening"
			_set_present()
		else:cabin.position.y+=travel_velocity*delta
		cabin_gate.position.y=cabin.position.y
