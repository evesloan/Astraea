extends RefCounted
var river:RefCounted
var volumes:Array=[]
func _init()->void:
 river=load("res://scripts/group6_completion/river_water_field.gd").new()
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_swimming_20261019/WATER_VOLUMES.json"))
 var verified:Dictionary={}
 for volume in p.volumes:
  if not verified.has(volume.source_file):
   assert(FileAccess.get_sha256("res://"+str(volume.source_file))==str(volume.source_sha256));verified[volume.source_file]=true
  var triangles:Array=[];var bounds:=Rect2();var first:=true
  for row in volume.triangles_xz:
   var triangle:=PackedVector2Array()
   for q in row:
    var point:=Vector2(q[0],q[1]);triangle.append(point)
    if first:bounds=Rect2(point,Vector2.ZERO);first=false
    else:bounds=bounds.expand(point)
   triangles.append(triangle)
  volumes.append({"id":volume.id,"surface_y":float(volume.water_y),"bed_y":float(volume.bed_y),"bounds":bounds.grow(.001),"triangles":triangles})
func sample(p:Vector3)->Dictionary:
 if p.y>=river.bed_y-.02 and p.y<river.water_y+2 and river.contains_xz(p):
  var answer:Dictionary=river.sample(p);answer["id"]="aquatic_river_001";answer["bed_y"]=river.bed_y;return answer
 var flat:=Vector2(p.x,p.z)
 for volume in volumes:
  if p.y<volume.bed_y-.02 or p.y>volume.surface_y+2 or not volume.bounds.has_point(flat):continue
  for triangle in volume.triangles:
   if Geometry2D.is_point_in_polygon(flat,triangle):
    return {"id":volume.id,"wet":p.y<volume.surface_y,"surface_y":volume.surface_y,"bed_y":volume.bed_y,"depth_m":maxf(0,volume.surface_y-p.y),"water_velocity":Vector3.ZERO}
 return {"wet":false}
