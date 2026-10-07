"""Fresh evaluated native vertices, ignoring source-preview context. Read-only."""
import bpy,json,hashlib,sys,argparse,math
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--native',required=True);ap.add_argument('--bounds',required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
P=Path(a.package).resolve();assert P.is_relative_to(Path(__file__).resolve().parents[1]);f=(P/a.native).resolve();assert f.is_relative_to(P);limits=json.loads(a.bounds);bpy.ops.wm.open_mainfile(filepath=str(f))
deps=bpy.context.evaluated_depsgraph_get();lo=[float('inf')]*3;hi=[-float('inf')]*3;bad=[];count=0;verts=0
for inst in deps.object_instances:
 obj=inst.object;orig=obj.original
 if obj.type not in {'MESH','CURVE','FONT'}:continue
 if orig.get('SOURCE_PREVIEW_ONLY') or orig.get('exclude_architecture_export') or orig.get('export_excluded') or 'SOURCE_PREVIEW_ONLY' in obj.name:continue
 me=bpy.data.meshes.new_from_object(obj,depsgraph=deps);count+=1
 for v in me.vertices:
  p=inst.matrix_world@v.co;g=(float(p.x),float(p.z),-float(p.y));verts+=1
  assert all(math.isfinite(c) for c in g)
  for k in range(3):lo[k]=min(lo[k],g[k]);hi[k]=max(hi[k],g[k])
  if any(g[k]<limits[0][k]-.003 or g[k]>limits[1][k]+.003 for k in range(3)) and len(bad)<30:bad.append({'object':obj.name,'vertex':g})
 bpy.data.meshes.remove(me)
export=json.loads((P/'qa/receiving_source_review/ACTUAL_GLB_VERTEX_CHECK.json').read_text());eb=export['actual_vertex_bounds_glb'];delta=max(abs(a-b) for x,y in zip([lo,hi],eb) for a,b in zip(x,y))
r={'scope':'Fresh evaluated native vertices and overall bound correspondence to actual GLB; no render or receiving-engine acceptance','pass':not bad and delta<.003,'native_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'native_evaluated_objects':count,'native_vertex_samples':verts,'native_local_gltf_bounds':[lo,hi],'export_local_gltf_bounds':eb,'aabb_max_delta_m':delta,'out_of_bounds':bad}
(P/'qa/receiving_source_review/NATIVE_BOUNDS_CHECK.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert r['pass']
