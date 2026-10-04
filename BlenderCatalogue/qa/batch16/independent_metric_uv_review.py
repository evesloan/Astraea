"""Read-only actual source UV scaling checks, separate from native exact corner equality."""
import bpy,json,hashlib,sys,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
for family in ['auditorium_arrival','auditorium_use']:
 for p in sorted((ROOT/'assets'/family/'source').glob('AST-*.blend')):
  before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);parts=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   me=ob.data;uv=me.uv_layers.active;v=np.array([list(x.co)for x in me.vertices]);lo=v.min(0);hi=v.max(0);role=ob.get('material_role','');errs=[];graphic=role.startswith('original_')or role.endswith('_original');grain=ob.get('grain_axis');scales=list(me.materials[0].get('meters_per_tile_uv',[1,1]));graphic_faces=0
   for face in me.polygons:
    axis=int(np.argmax(abs(np.array(face.normal))));axes=[x for x in range(3)if x!=axis]
    if role=='warm_walnut'and grain in axes:axes=[x for x in axes if x!=grain]+[grain]
    special=graphic and ((family=='auditorium_arrival'and face.normal.y<-.99)or(family=='auditorium_use'and abs(face.normal.y)>.9))
    if special:graphic_faces+=1
    for li in face.loop_indices:
     q=me.vertices[me.loops[li].vertex_index].co;expect=[(q.x-lo[0])/(hi[0]-lo[0]),(q.z-lo[2])/(hi[2]-lo[2])]if special else[q[axes[0]]/scales[0],q[axes[1]]/scales[1]];errs.append(float(np.max(abs(np.array(uv.data[li].uv)-expect))))
   parts.append({'part':ob.name,'material_role':role,'meters_per_tile_uv':scales,'grain_axis':grain,'graphic_rectangular_whole_face_count':graphic_faces,'max_uv_component_error':max(errs),'passed':max(errs)<2e-6})
  row={'catalogue_id':p.stem,'source_sha256':before,'parts':parts,'source_unmodified':before==sha(p),'passed':all(x['passed']for x in parts)and before==sha(p)};rows.append(row);print(p.stem,row['passed'],[x['part']for x in parts if not x['passed']],flush=True)
(OUT/'independent_metric_uv_review.json').write_text(json.dumps({'passed':all(x['passed']for x in rows),'assets':rows,'method':'Read actual editable mesh material tile dimensions and corner UVs. Compare deliberate dominant local-plane metric projection, arrival walnut grain-axis ordering, and bounded whole-face original graphics. Native exact position/UV/normal corner equality is separate. Dominant projection on sloped solids is a documented planar-projection intent, not a distortion-free developed surface.','executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
