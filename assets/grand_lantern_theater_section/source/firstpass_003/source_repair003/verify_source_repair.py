"""Independent reopen: all unaffected source records and materials stay exact."""
import bpy,sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import *
report=json.loads((R/'BUILD_REPORT.json').read_text());source=Path(report['source']);expected=report['source_sha256'];assert sha(source)==expected and not (R/'REOPEN_REPORT.json').exists();bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();failures=compare_subset(report['preserved_snapshot'],baseline_snapshot(bpy));assert not failures,failures[:20];rows=[]
for rec in report['records']:
 ob=bpy.data.objects[rec['name']];me=ob.data;me.calc_loop_triangles();points=[ob.matrix_world@v.co for v in me.vertices];lo,hi=rec['old_world_bounds_blender'];error=max([abs(min(p[k]for p in points)-lo[k])for k in range(3)]+[abs(max(p[k]for p in points)-hi[k])for k in range(3)]);assert error<1e-5
 counts={}
 for f in me.polygons:
  ids=list(f.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
 assert all(c==2 for c in counts.values());opposed=0;minarea=1e9
 for tri in me.loop_triangles:
  a,b,c=[me.vertices[i].co for i in tri.vertices];cross=(b-a).cross(c-a);minarea=min(minarea,cross.length/2);avg=sum((me.corner_normals[i].vector for i in tri.loops),a*0)/3
  if cross.dot(avg)<-1e-10:opposed+=1
 assert opposed==0 and minarea>1e-8;rows.append({'name':ob.name,'triangles':len(me.loop_triangles),'bounds_error_m':error,'opposed_normals':opposed,'minimum_triangle_area_m2':minarea,'manifold':True})
assert len([o for o in bpy.context.scene.objects if o.get('existing_family')=='AST-CUL-003'])==2200 and sha(source)==expected
out={'passed':True,'source_sha256':expected,'unchanged_object_records':len(report['preserved_snapshot']['objects']),'unchanged_material_records':len(report['preserved_snapshot']['materials']),'unchanged_original_part_records':len(report['preserved_snapshot']['parts']),'chairs':2200,'repaired_parts':rows,'source_saved':False};(R/'REOPEN_REPORT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='repaired_parts'}))
