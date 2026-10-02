"""Read-only Blender state audit. Does not save, export, rebuild or render."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12'
args=sys.argv[sys.argv.index('--')+1:];prefix='independent_'
if args and args[0]=='--prefix':prefix=args[1];args=args[2:]
path=Path(args[0]).resolve();extra_frames=[float(x)for x in args[1:]]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(path)
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
scene=bpy.context.scene;actions=[];frames=set(extra_frames)
for act in bpy.data.actions:
 channels=[]
 for fc in act.fcurves:
  points=[{'frame':float(k.co[0]),'value':float(k.co[1]),'interpolation':k.interpolation}for k in fc.keyframe_points];frames.update(k['frame']for k in points)
  channels.append({'data_path':fc.data_path,'array_index':fc.array_index,'keyframes':points})
 actions.append({'name':act.name,'channels':channels})
frames=sorted(frames or {float(scene.frame_current)});states=[]
for frame in frames:
 scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();triangles=[];labels=[];materials=[];objects=[]
 for o in scene.objects:
  rec={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'world_matrix':np.asarray(o.matrix_world).tolist(),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
  if o.type in {'MESH','CURVE','FONT'}:
   e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();vs=np.asarray([e.matrix_world@v.co for v in m.vertices]);t=np.asarray([x.vertices for x in m.loop_triangles],int)
   if len(vs)and len(t):
    triangles.extend(vs[t]);labels.extend([o.name]*len(t));materials.extend([m.materials[x.material_index].name for x in m.loop_triangles]);rec.update(bounds_min_m=vs.min(axis=0).tolist(),bounds_max_m=vs.max(axis=0).tolist(),triangles=len(t))
   e.to_mesh_clear()
  objects.append(rec)
 tag=str(frame).replace('.','p');cache=OUT/f'{prefix}state_geometry_{path.stem}_{tag}.npz';np.savez_compressed(cache,triangles=np.asarray(triangles),object_names=np.asarray(labels),material_names=np.asarray(materials));v=np.asarray(triangles).reshape(-1,3)
 states.append({'frame':frame,'geometry_cache':str(cache.relative_to(ROOT)),'geometry_cache_sha256':sha(cache),'bounds_min_m':v.min(axis=0).tolist(),'bounds_max_m':v.max(axis=0).tolist(),'objects':objects})
row={'source':str(path.relative_to(ROOT)),'source_sha256':before,'source_unchanged':before==sha(path),'executed_script_sha256':sha(Path(__file__)),'blender_version':bpy.app.version_string,'timeline_range':[scene.frame_start,scene.frame_end],'actions':actions,'states':states}
(OUT/f'{prefix}source_states_{path.stem}.json').write_text(json.dumps(row,indent=2)+'\n');print(path.name,'read-only frames',frames,'unchanged',row['source_unchanged'])
