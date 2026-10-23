extends SceneTree
var failures:=0
func require(ok:bool,label:String)->void:
 if not ok:failures+=1;push_error(label)
func texture(color:Color)->ImageTexture:
 var image:=Image.create(4,4,false,Image.FORMAT_RGBA8);image.fill(color)
 return ImageTexture.create_from_image(image)
func cycle(script:Script)->Dictionary:
 var cache=script.new()
 var a:Texture2D=texture(Color.RED);var b:Texture2D=texture(Color.RED)
 var wa:WeakRef=weakref(a);var wb:WeakRef=weakref(b)
 var first:Texture2D=cache.intern_texture(a);var second:Texture2D=cache.intern_texture(b)
 require(first==second,"Identical live payload must share original texture")
 var owner:=StandardMaterial3D.new();owner.albedo_texture=second
 a=null;b=null;first=null;second=null
 require(wa.get_ref()!=null,"Live material must retain shared texture")
 require(wb.get_ref()==null,"Duplicate original must be released")
 owner.albedo_texture=null;owner=null;cache.prune_expired_references()
 return {"remaining":wa.get_ref()!=null,"canonical_entries":cache.canonical.size(),"lookup_entries":cache.textures.size()}
func _initialize()->void:
 var root_path:="/workspace/Astraea-recovered-e6274e77-20261021/"
 var original:Script=load(root_path+"Game/scripts/startup_residency_20261020/exact_texture_intern.gd")
 var fixed:Script=load(root_path+"recovery/texture_lifetime_fix_20261023/payload/Game/scripts/startup_residency_20261020/exact_texture_intern.gd")
 var before:=cycle(original);var after:=cycle(fixed)
 require(before.remaining and before.canonical_entries==1,"Original strong retention reproduced")
 require(not after.remaining and after.canonical_entries==0 and after.lookup_entries==0,"Successor releases unowned canonical and lookup entries")
 var cache=fixed.new()
 for i in range(100):
  var t:Texture2D=texture(Color(float(i)/100.0,.2,.7));var w:WeakRef=weakref(t)
  var shared:Texture2D=cache.intern_texture(t);shared=null;t=null
  require(w.get_ref()==null,"Cycle has no cache-owned resource")
  cache.prune_expired_references()
 require(cache.canonical.is_empty() and cache.textures.is_empty(),"Repeated payload churn leaves no cache entries")
 var red:Texture2D=texture(Color.RED);var blue:Texture2D=texture(Color.BLUE)
 require(cache.intern_texture(red)!=cache.intern_texture(blue),"Different complete payloads remain distinct")
 red=null;blue=null;cache.prune_expired_references()
 var report:={"failures":failures,"original":before,"successor":after,"cycles":100,"geometry_or_material_values_changed":false,"laptop_crash_causality":"UNPROVEN"}
 print("TEXTURE_LIFETIME_RESULT ",JSON.stringify(report));quit(1 if failures else 0)
