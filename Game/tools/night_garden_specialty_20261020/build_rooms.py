"""Run in Blender4.3.2. Bake mirrored fit and exact recovered rest anchors."""
import bpy,bmesh,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
G=Path(__file__).resolve().parents[2];B=G.parent/'BlenderCatalogue';N=B/'assets/night_garden_specialty_d15_20261020';N.mkdir(exist_ok=True)
pth=G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE.json';p=json.loads(pth.read_text());records=[]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for r in p['rooms']:
 i=r['allocation']['source_envelope_index']
 if args and str(i) not in args:continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(G/'assets/models'/r['source_model_file']))
 transforms={o.name:o.matrix_world.copy() for o in bpy.context.scene.objects}
 mirror=Matrix.Diagonal((-1,1,1,1));stats={'meshes':0,'triangles':0,'rest_component_meshes':{},'rest_bounds':{}}
 for o in list(bpy.context.scene.objects):
  oldname=o.name;mat=mirror@transforms[oldname]
  adjustment=next((a for a in r['rest_adjustments'] if a['component_name'] in oldname),None)
  if adjustment:
   d=adjustment['mirrored_delta'];mat=Matrix.Translation((d[0],-d[2],d[1]))@mat
   o['reserved_rest_slot_id']=adjustment['slot_id']
  elif '_Cocoon' in oldname and 'ReservedRestSupport' not in oldname:
   import re
   match=re.search(r'_Cocoon(\d*)_',oldname)
   if match:
    idx=int(match.group(1) or '1')-1;d=r['rest_adjustments'][idx]['mirrored_delta'];mat=Matrix.Translation((d[0],-d[2],d[1]))@mat
  else:
   fit=next((a for a in r.get('component_adjustments',[]) if a['component_name']+'__' in oldname),None)
   if fit:
    d=fit['mirrored_delta'];mat=Matrix.Translation((d[0],-d[2],d[1]))@mat
  o.parent=None
  if o.type=='MESH':
   o.data=o.data.copy();o.data.transform(mat)
   if mat.determinant()<0:
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   o.matrix_world=Matrix.Identity(4);o.data.update();o.data.calc_loop_triangles();stats['meshes']+=1;stats['triangles']+=len(o.data.loop_triangles)
   if adjustment:
    k=adjustment['slot_id'];stats['rest_component_meshes'][k]=stats['rest_component_meshes'].get(k,0)+1
    if bool(o.get('runtime_collision',False)):
     points=[(v.co.x,v.co.z,-v.co.y) for v in o.data.vertices];bounds=stats['rest_bounds'].setdefault(k,[[1e9]*3,[-1e9]*3])
     for pt in points:
      for ax in range(3):bounds[0][ax]=min(bounds[0][ax],pt[ax]);bounds[1][ax]=max(bounds[1][ax],pt[ax])
  else:o.matrix_world=mat
  o.name=oldname.replace('SA'+str(i-3),'NG'+str(i));o['fitted_target_allocation']=i;o['authorship']='new_night_garden_derivative_20261020'
 for a in r['rest_adjustments']:assert stats['rest_component_meshes'].get(a['slot_id'],0)>0,a
 for bounds in stats['rest_bounds'].values():
  a=r['allocation'];assert bounds[0][0]>=a['allocation_x'][0]-.03 and bounds[1][0]<=a['allocation_x'][1]+.03 and bounds[0][2]>=a['allocation_z'][0]-.03 and bounds[1][2]<=a['allocation_z'][1]+.03,(i,bounds)
 bpy.context.preferences.filepaths.save_version=0
 native=N/f'NightGardenD15Specialty_{i}_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 # Compact immutable runtime batches; native source above retains individual authored objects.
 groups={}
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  key=(tuple(m.name if m else '' for m in o.data.materials),bool(o.get('runtime_collision',False)),str(o.get('collision_policy','')),str(o.get('material_role','')),str(o.get('reserved_rest_slot_id','')))
  groups.setdefault(key,[]).append(o)
 for idx,(key,objects) in enumerate(groups.items()):
  if len(objects)<2:continue
  names=[o.name for o in objects];bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'NG{i}_RuntimeBatch_{idx:03d}';o['source_object_names']=names
 stats['runtime_mesh_batches']=sum(o.type=='MESH' for o in bpy.context.scene.objects)
 out=G/'assets/models'/r['model_file'];bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_cameras=False,export_lights=False)
 r['model_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();r['native_source']=str(native.relative_to(B));r['native_source_sha256']=hashlib.sha256(native.read_bytes()).hexdigest();r['construction_statistics']=stats
 pth.write_text(json.dumps(p,indent=2)+'\n');print('NEW_FIT_COMPLETE',i,stats['meshes'],flush=True)
print('ROOM_BATCH_COMPLETE',flush=True)
