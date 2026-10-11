"""Save once. Re-export only in disposable staging; final revision bytes are immutable."""
from pathlib import Path
import hashlib, json, shutil, struct, tempfile

def require_new(paths):
 paths=[Path(p) for p in paths]
 if len({str(p.absolute()) for p in paths}) != len(paths):raise ValueError('Duplicate revision output path')
 for p in paths:
  if p.exists() or p.is_symlink():raise FileExistsError('Immutable revision already exists: '+str(p))
 return paths

def copy_exclusive(source, target):
 target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
 with open(source,'rb') as src,open(target,'xb') as dst:shutil.copyfileobj(src,dst)

def export_native(bpy, work, repo, native, filename, exclude_structure=False):
 work,repo=Path(work),Path(repo)
 if Path(native).name!=native or Path(filename).name!=filename:raise ValueError('Revision filenames must be basenames')
 final_native,final_glb,final_runtime=require_new([work/native,work/filename,repo/'Game/assets/models'/filename])
 stage=Path(tempfile.mkdtemp(prefix='astraea_immutable_native_'))
 first,repeat,screen=stage/'first',stage/'repeat',stage/'screen'
 for p in [first,repeat,screen]:p.mkdir()
 bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(stage/native),compress=True)
 def write(dest):
  bpy.ops.object.select_all(action='DESELECT')
  for ob in bpy.data.objects:
   if ob.type in ['MESH','EMPTY'] and not(exclude_structure and ob.get('category','') in ['floor','frame','truss_brace']):ob.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',export_extras=True,use_selection=True,export_apply=True)
 write(first/filename);bpy.ops.wm.open_mainfile(filepath=str(stage/native));write(repeat/filename)
 raw=(first/filename).read_bytes();h=hashlib.sha256(raw).hexdigest()
 if raw!=(repeat/filename).read_bytes():raise AssertionError('Fresh native repeat export differs; final revision not saved')
 import sys
 sys.path.insert(0,str(repo/'Game/tools'));from validate_production_glb import validate_and_copy
 validate_and_copy(first/filename,screen/filename)
 require_new([final_native,final_glb,final_runtime])
 copy_exclusive(stage/native,final_native);copy_exclusive(first/filename,final_glb);copy_exclusive(screen/filename,final_runtime)
 n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);policy={q['name'].replace('.','_'):{'collide':q.get('extras',{}).get('runtime_collision',True),'opaque':q.get('extras',{}).get('role','')not in ['water','hospitality_glass'],'role':q.get('extras',{}).get('role',''),'category':q.get('extras',{}).get('category','')}for q in doc['nodes']if 'mesh'in q}
 return {'native':native,'native_sha256':hashlib.sha256(final_native.read_bytes()).hexdigest(),'export':filename,'export_sha256':h,'mesh_count':len(policy),'collision_policy':policy,'fresh_native_repeat_identical':True,'immutable_revision':True,'disposable_repeat_export_staging':str(stage)}
