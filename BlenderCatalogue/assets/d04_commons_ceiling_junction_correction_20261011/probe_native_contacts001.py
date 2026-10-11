from pathlib import Path
import bpy,json
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));old=json.load(open(R/'Game/data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json'));bpy.ops.wm.read_factory_settings(use_empty=True)
for f in sorted({q['source_model']for q in old['moves']+old['cuts']}):bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/f))
for q in old['runtime_preimages']:
 ob=next(o for o in bpy.data.objects if o.name.replace('.','_')==q['name']);bpy.data.objects.remove(ob,do_unlink=True)
for rec in old['native_export_records']:
 with bpy.data.libraries.load(str(R/'BlenderCatalogue/assets/d04_port_central_commons_recomposition_20261011'/rec['native']),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update();parts=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];vv=[[v.x,v.z,-v.y]for v in vs];lo=[min(v[i]for v in vv)for i in range(3)];hi=[max(v[i]for v in vv)for i in range(3)];parts.append({'name':ob.name,'bounds':[lo,hi],'axis_aligned_box':all(all(min(abs(v[i]-lo[i]),abs(v[i]-hi[i]))<.00005 for i in range(3))for v in vv)})
rows=[]
for q in P['parts']:
 lo,hi=q['expected_bounds']
 for s in parts:
  a,b=s['bounds'];l=[max(lo[i],a[i])for i in range(3)];h=[min(hi[i],b[i])for i in range(3)];dims=[h[i]-l[i]for i in range(3)]
  if min(dims)>.0001:rows.append({'cap':q['name'],'source':s,'positive_overlap_bounds':[l,h]})
(W/'SOURCE_CAP_OVERLAPS001.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
