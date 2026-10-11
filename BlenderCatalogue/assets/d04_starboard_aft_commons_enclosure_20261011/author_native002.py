from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
bpy.ops.wm.read_factory_settings(use_empty=True);source={}
for file in sorted({q['material_native']for q in P['fit_sites']}):
 with bpy.data.libraries.load(str(R/file),link=False)as(src,dst):dst.objects=sorted({q['source_name']for q in P['fit_sites']if q['material_native']==file})
 for ob in dst.objects:
  assert ob is not None
  bpy.context.collection.objects.link(ob);source[ob.name]=ob
bpy.context.view_layer.update()
for row in P['parts']:
 ob=source[row['source_name']];verts=row['verts'];name=row['name'];me=bpy.data.meshes.new(name);me.from_pydata([(v[0],-v[2],v[1])for v in verts],[],row['faces']);me.update()
 for m in ob.data.materials:me.materials.append(m)
 uv=me.uv_layers.new(name='SourceScaleWorldProjection')
 for face in me.polygons:
  axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3)if a!=axis]
  for k in face.loop_indices:
   v=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(v[axes[0]],v[axes[1]])
 new=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(new);new['role']=row['role'];new['category']=row['category'];new['runtime_collision']=True
for ob in source.values():bpy.data.objects.remove(ob,do_unlink=True)
rec=export_native(bpy,W,R,'D04StarboardAftCommonsEnclosure_r001.blend','D04_STARBOARD_AFT_COMMONS_ENCLOSURE_r001.glb');P['structure_file']=rec['export'];P['structure']=rec;P['native_export_records']=[rec];P['model_pins']={rec['export']:rec['export_sha256']}
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_STARBOARD_AFT_COMMONS_ENCLOSURE.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('Immutable additive ceiling closures:',len(P['parts']))
