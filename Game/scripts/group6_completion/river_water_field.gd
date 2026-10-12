extends RefCounted
# Geometry-backed flat river and prescribed game current; not a fluid simulation.
var outer:PackedVector2Array
var island:PackedVector2Array
var points:PackedVector3Array
var cumulative:PackedFloat64Array
var length_m:=0.0
var water_y:=0.0
var bed_y:=0.0
var flow_speed:=0.6
func _init()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/FLOAT_WATER_CONTRACT.json"))
	assert(FileAccess.get_sha256("res://data/architecture/AQUATIC_ANNEX_PLAN.json")==str(p.source_sha256))
	for q in p.outer_xz:outer.append(Vector2(q[0],q[1]))
	for q in p.island_xz:island.append(Vector2(q[0],q[1]))
	for q in p.centerline_xyz:points.append(Vector3(q[0],q[1],q[2]))
	assert(points[0].is_equal_approx(points[-1]));cumulative.append(0.0)
	for i in range(points.size()-1):length_m+=points[i].distance_to(points[i+1]);cumulative.append(length_m)
	assert(absf(length_m-float(p.length_m))<.0001)
	water_y=float(p.water_y);bed_y=float(p.bed_y);flow_speed=float(p.proposed_current_m_s)
func contains_xz(p:Vector3)->bool:
	var q:=Vector2(p.x,p.z)
	return Geometry2D.is_point_in_polygon(q,outer) and not Geometry2D.is_point_in_polygon(q,island)
func project(p:Vector3)->Dictionary:
	var flat:=Vector3(p.x,water_y,p.z);var best:=INF;var answer:Dictionary={}
	for i in range(points.size()-1):
		var d:=points[i+1]-points[i];var t:=clampf((flat-points[i]).dot(d)/d.length_squared(),0.0,1.0);var q:=points[i]+d*t;var distance:=flat.distance_squared_to(q)
		if distance<best:
			best=distance;answer={"point":q,"tangent":d.normalized(),"arc_m":cumulative[i]+d.length()*t,"lateral_m":sqrt(distance)}
	return answer
func sample(p:Vector3)->Dictionary:
	if not contains_xz(p) or p.y<bed_y-.02:return {"wet":false}
	var nearest:=project(p);var drift:Vector3=nearest.point-Vector3(p.x,water_y,p.z)
	# Bounded transverse flow closes the prescribed loop without position writes.
	var correction:=drift.limit_length(.4)*.7
	return {"wet":p.y<water_y,"surface_y":water_y,"depth_m":maxf(0.0,water_y-p.y),"water_velocity":nearest.tangent*flow_speed+correction,"arc_m":nearest.arc_m,"lateral_m":nearest.lateral_m}
