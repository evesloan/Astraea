extends RefCounted
# Exact physics payload only. Bodies, transforms and render resources stay independent.
static var entries:Dictionary={}
static var hits:=0
static var misses:=0
static func digest(faces:PackedVector3Array)->String:
 var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(faces.to_byte_array())
 return hash.finish().hex_encode()
static func prune()->void:
 for key:String in entries.keys():
  if entries[key].ref.get_ref()==null:entries.erase(key)
static func invalidate(key:String,reference:WeakRef)->void:
 if not entries.has(key) or entries[key].ref!=reference:return
 var shape:ConcavePolygonShape3D=reference.get_ref()
 if shape==null or shape.backface_collision or shape.get_script()!=null or shape.resource_local_to_scene or shape.margin!=float(PackedFloat32Array([.04])[0]) or digest(shape.get_faces())!=key:
  entries.erase(key)
static func intern(faces:PackedVector3Array)->ConcavePolygonShape3D:
 assert(not faces.is_empty() and faces.size()%3==0)
 var payload:=faces.to_byte_array()
 var key:=digest(faces)
 var shape:ConcavePolygonShape3D=null
 if entries.has(key):
  invalidate(key,entries[key].ref)
 if entries.has(key):
  shape=entries[key].ref.get_ref() as ConcavePolygonShape3D
  if shape!=null:
   assert(shape.get_faces().to_byte_array()==payload,"Contact digest collision or changed canonical triangles")
   assert(not shape.backface_collision and shape.get_script()==null and not shape.resource_local_to_scene)
 if shape==null:
  shape=ConcavePolygonShape3D.new();shape.set_faces(faces)
  var reference:WeakRef=weakref(shape);entries[key]={"ref":reference}
  shape.changed.connect(func()->void:invalidate(key,reference))
  misses+=1
 else:hits+=1
 return shape
