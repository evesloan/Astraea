from pathlib import Path
import shutil,re,json
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'recovery/release_operations_fix_20261023';P.mkdir(exist_ok=False);out=P/'payload';prior=R/'recovery/quiet_d14_chain_fix/payload';shutil.copytree(prior,out)
H='res://scripts/release_operations_20261023/guard.gd';helper=out/'Game/scripts/release_operations_20261023/guard.gd';helper.parent.mkdir(parents=True)
helper.write_text('''extends RefCounted
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
''')
changed=[]
def read(rel):
 p=out/'Game'/rel
 return p.read_text()if p.exists()else(R/'Game'/rel).read_text()
def write(rel,s):
 p=out/'Game'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s);changed.append(rel)
guard='load("'+H+'")'
# Actual receiving raw-path branches, including all eight already reconciled Quiet/Family packages.
for rel in [f'scripts/{bank}_d{deck}_receiving_20261016/package.gd'for bank in ['quiet','family']for deck in [13,14,15,16]]+['scripts/d17_starboard_standard_20261019/package.gd']:
 s=read(rel)
 pattern=r'  var doc:=GLTFDocument.new\(\);var state:=GLTFState.new\(\);assert\(doc.append_from_file\(file,state(,64)?\)==OK\);model=doc.generate_scene\(state\)'
 def sub(m):return '  model='+guard+'.load_gltf(file'+(',64'if m[1]else'')+')\n  if model==null:return null'
 s,n=re.subn(pattern,sub,s);assert n==1,rel;write(rel,s)
rel='royalty790_integration_20261022/package.gd';s=read(rel);s=s.replace(' var d:=GLTFDocument.new();var s:=GLTFState.new();assert(d.append_from_file(file,s)==OK);return d.generate_scene(s)',' return '+guard+'.load_gltf(file)');s=s.replace(' var preserved:=0',' if expected==null:return null\n var preserved:=0');write(rel,s)
rel='scripts/night_garden_residency_20261022/source_visual.gd';s=read(rel);s=s.replace('\tvar document:=GLTFDocument.new();var state:=GLTFState.new()\n\tassert(document.append_from_file("res://assets/models/"+file,state)==OK)\n\tvar visual:Node3D=document.generate_scene(state)','\tvar visual:Node3D='+guard+'.load_gltf("res://assets/models/"+file)\n\tif visual==null:return null');write(rel,s)
# Do not remove preserved commons walls before the replacement has loaded successfully.
rel='scripts/night_garden_residency_20261022/district.gd';s=read(rel);line='\tfor patch in receiving.commons_patch:commons.find_child(patch.source_mesh,true,false).free()\n';assert line in s;s=s.replace(line,'');s=s.replace('\thelper.contact_visual(street,receiving.model_file)','\tvar receiving_visual:Node3D=helper.contact_visual(street,receiving.model_file)\n\tif receiving_visual==null:\n\t\tstreet.free();return null\n'+line.rstrip());write(rel,s)
rel='scripts/star_atlas_fitted_receiving.gd';s=read(rel);a=s.index('\tvar hash: HashingContext=HashingContext.new()');b=s.index('\n\nstatic func value_state',a);s=s[:a]+'\treturn '+guard+'.sha256_bytes(var_to_bytes(value))'+s[b:];write(rel,s)
rel='scripts/group2_family_meal/package.gd';s=read(rel);old='\t\tvar hash:=HashingContext.new();assert(hash.start(HashingContext.HASH_SHA256)==OK);hash.update(floats.to_byte_array());assert(hash.finish().hex_encode()==str(row.imported_vertex_sha256))';assert old in s;s=s.replace(old,'\t\tvar actual_hash:String='+guard+'.sha256_bytes(floats.to_byte_array())\n\t\tif not '+guard+'.require_ok(actual_hash==str(row.imported_vertex_sha256),"Family meal exact vertex preimage differs"):return null');write(rel,s)
# Import-configuration loads and their immediately dependent policy gates.
for rel in ['scripts/movement_studio_receiving.gd','scripts/sports_care_receiving.gd','scripts/court_a_increment004.gd','scripts/crew_home_approach.gd','scripts/medical_welcome.gd','scripts/engineering_cell_signage.gd']:
 s=read(rel);lines=s.splitlines();result=[];active=False
 returning='null'if 'court_a' in rel else ('false'if 'movement_studio' in rel or 'sports_care' in rel else '')
 for line in lines:
  m=re.match(r'(\s*)assert\((\w+)\.load\((.*)\)\s*==\s*OK\)',line)
  if m:
   indent,var,path=m.groups();result.append(indent+'if not '+guard+'.load_config('+path+','+var+'):return'+(' '+returning if returning else ''));active=True;continue
  if active and line.strip().startswith('assert(') and '.get_value('in line:
   expr=line.strip()[7:-1]
   # Existing message remains the second require_ok argument, if supplied.
   text=expr if re.search(r',\s*"[^"\n]*"\s*(?:\+[^\n]+)?$',expr) else expr+',"Retained import policy differs: '+rel+'"'
   result.append(line[:len(line)-len(line.lstrip())]+'if not '+guard+'.require_ok('+text+'):return'+(' '+returning if returning else ''));continue
  if active and line.strip()and not line.strip().startswith('var expected:')and not line.strip().startswith('var policy:'):active=False
  result.append(line)
 s='\n'.join(result)+'\n'
 if returning=='false':
  s=s.replace('static func model_ready(filename: String, expected: String) -> void:', 'static func model_ready(filename: String, expected: String) -> bool:')
  pos=s.index('\nstatic func build(');s=s[:pos].rstrip()+'\n\treturn true\n'+s[pos:]
  s=re.sub(r'\tmodel_ready\(([^\n]+)\)',r'\tif not model_ready(\1):return',s)
 if 'court_a' in rel:s=s.replace('\tvar prototype := load_template(data.files.prototype)','\tif source==null:return\n\tvar prototype := load_template(data.files.prototype)\n\tif prototype==null:\n\t\tsource.free();return')
 write(rel,s)
(P/'EDITED_OPERATIONS.json').write_text(json.dumps({'changed_scripts':changed,'original_geometry_unchanged':True,'release_execution_pending':True},indent=2)+'\n')
print('changed_runtime_scripts',len(changed))
