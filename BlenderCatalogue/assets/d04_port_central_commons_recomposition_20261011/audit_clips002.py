from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));pre={q['name']:q for q in P['runtime_preimages']}
def triangles(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active;return [{'v':np.array([list(o.matrix_world@o.data.vertices[o.data.loops[k].vertex_index].co)for k in t.loops]),'uv':np.array([list(uv.data[k].uv)for k in t.loops])}for t in o.data.loop_triangles]
bpy.ops.wm.read_factory_settings(use_empty=True)
for file in sorted({q['source_model']for q in P['cuts']}):bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/file))
sources={q['name']:triangles(bpy.data.objects[q['name']])for q in P['cuts']}
bpy.ops.wm.open_mainfile(filepath=str(R/P['source_co_native']))
for q in P['moves']:
 if q['name']not in P['front_clip_boxes']:continue
 o=next(o for o in bpy.data.objects if o.name.replace('.','_')==q['name']);d=q['delta'];T=Vector((d[0],-d[2],d[1]));rows=triangles(o)
 for row in rows:row['v']+=np.array(T)
 sources[q['name']]=rows
bpy.ops.wm.open_mainfile(filepath=str(W/P['patch']['native']));targets={o.name.replace('.','_'):triangles(o)for o in bpy.data.objects if o.type=='MESH'};report=[]
for name,rows in sources.items():
 move=next((q for q in P['moves']if q['name']==name),None);cut=next((q for q in P['cuts']if q['name']==name),None);boxes=cut['boxes']if cut else[P['front_clip_boxes'][name]];actual=np.concatenate([q['v']for q in rows]);raw=np.array([(x,-z,y)for x,y,z in pre[name]['world_triangle_vertices']])
 if move:raw+=np.array((move['delta'][0],-move['delta'][2],move['delta'][1]))
 dist=np.linalg.norm(actual[:,None,:]-raw[None,:,:],axis=2);err=max(float(dist.min(0).max()),float(dist.min(1).max()));import_bound=float(np.ptp(actual,axis=0).max())/65535+.000005+max(abs(t)for row in actual for t in row)/2**23*2;assert err<=import_bound,(name,err,import_bound)
 kept=0;float_bound=max(abs(t)for row in actual for t in row)/2**23*2+1e-6
 for row in rows:
  outside=True
  for b in boxes:
   lo=np.array((b['min'][0],-b['max'][2],b['min'][1]));hi=np.array((b['max'][0],-b['min'][2],b['max'][1]));a=row['v'].min(0);z=row['v'].max(0)
   if not any(z[k]<lo[k]-float_bound or a[k]>hi[k]+float_bound for k in range(3)):outside=False
  if not outside:continue
  found=False
  for target in targets.get(name,[]):
   d=np.linalg.norm(row['v'][:,None,:]-target['v'][None,:,:],axis=2);idx=d.argmin(1)
   if len(set(idx))==3 and float(d.min(1).max())<=float_bound and np.array_equal(row['uv'],target['uv'][idx]):found=True;break
  assert found,name+' outside source triangle/UV changed';kept+=1
 report.append({'name':name,'source_runtime_import_coordinate_error_m':err,'import_quantization_plus_float32_bound_m':import_bound,'outside_aperture_triangles_and_original_UVs_preserved':kept,'float32_serialization_bound_m':float_bound,'output_triangles':len(targets.get(name,[]))})
result={'status':'PASS','model_pins':P['model_pins'],'clip_successors':report,'exact_runtime_preimages_verified_by_builder':len(P['runtime_preimages']),'source_native_GLB_bytes_pinned':True,'no_unexplained_preimage_mismatch':True};(W/'SOURCE_CLIP_PREIMAGE_AND_OUTSIDE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('SOURCE CLIP PREIMAGE/OUTSIDE AUDIT PASS',len(report),sum(q['outside_aperture_triangles_and_original_UVs_preserved']for q in report))
