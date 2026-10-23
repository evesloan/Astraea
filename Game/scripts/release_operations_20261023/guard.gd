extends RefCounted
# Required work and failure handling execute in both debug and release builds.
static func require_ok(condition:bool,message:String)->bool:
 if condition:return true
 push_error("ASTRAEA_RELEASE_GUARD: "+message)
 var loop:MainLoop=Engine.get_main_loop()
 if loop is SceneTree:
  loop.root.set_meta("astraea_release_guard_failure",message)
  loop.paused=true
  loop.quit(2)
 return false
static func load_gltf(path:String,flags:int=-1)->Node3D:
 var document:=GLTFDocument.new();var state:=GLTFState.new()
 var status:int=document.append_from_file(path,state) if flags<0 else document.append_from_file(path,state,flags)
 if not require_ok(status==OK,"GLTF append failed (%s): %s"%[status,path]):return null
 var result:Node=document.generate_scene(state)
 if not require_ok(result is Node3D and result.get_child_count()>0,"Empty or invalid GLTF scene: "+path):
  if result!=null:result.free()
  return null
 return result as Node3D
static func load_config(path:String,target:ConfigFile)->bool:
 var status:int=target.load(path)
 return require_ok(status==OK,"Import config load failed (%s): %s"%[status,path])
static func sha256_bytes(bytes:PackedByteArray)->String:
 var context:=HashingContext.new()
 var status:int=context.start(HashingContext.HASH_SHA256)
 if not require_ok(status==OK,"SHA256 initialization failed"):return ""
 status=context.update(bytes)
 if not require_ok(status==OK,"SHA256 update failed"):return ""
 var result:PackedByteArray=context.finish()
 if not require_ok(result.size()==32,"SHA256 result length differs"):return ""
 return result.hex_encode()
