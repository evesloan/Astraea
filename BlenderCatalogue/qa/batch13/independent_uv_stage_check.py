import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/botanical_transition/source/AST-BOT-010.blend'),load_ui=False);dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 for mode in ['evaluated_to_mesh','new_from_object']:
  ev=o.evaluated_get(dg);me=ev.to_mesh()if mode=='evaluated_to_mesh'else bpy.data.meshes.new_from_object(ev);me.calc_loop_triangles();uv=me.uv_layers.active;bad=[]
  for t in me.loop_triangles:
   a,b,c=[uv.data[i].uv for i in t.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:bad.append({'tri':t.index,'poly':t.polygon_index})
  if bad:rows.append({'part':o.name,'mode':mode,'collapsed_triangles':len(bad),'repaired_polygons':len(set(t['poly']for t in bad)),'bad':bad})
  if mode=='evaluated_to_mesh':ev.to_mesh_clear()
  else:bpy.data.meshes.remove(me)
(OUT/'independent_uv_stage_check.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
