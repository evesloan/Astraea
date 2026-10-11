from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
bpy.ops.wm.read_factory_settings(use_empty=True);source={};furn={};loaded=[]
for file in sorted({q['material_native']for q in P['parts']}):
 names=sorted({q['material_source']for q in P['parts']if q['material_native']==file})
 with bpy.data.libraries.load(str(R/file),link=False)as(src,dst):dst.objects=names
 for ob in dst.objects:bpy.context.collection.objects.link(ob);source[ob.name]=ob;loaded.append(ob)
for file in sorted({q['native']for q in P['furniture']}):
 with bpy.data.libraries.load(str(R/file),link=False)as(src,dst):dst.objects=[n for n in src.objects]
 furn[file]=[]
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob);loaded.append(ob);furn[file].append(ob)
bpy.context.view_layer.update();furniture_audit=[]
for q in P['parts']:
 me=bpy.data.meshes.new(q['name']);me.from_pydata([(v[0],-v[2],v[1])for v in q['verts']],[],q['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free()
 for m in source[q['material_source']].data.materials:me.materials.append(m)
 uv=me.uv_layers.new(name='MetricWorldProjection')
 for face in me.polygons:
  axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3)if a!=axis]
  for k in face.loop_indices:v=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(v[axes[0]],v[axes[1]])
 ob=bpy.data.objects.new(q['name'],me);bpy.context.collection.objects.link(ob);ob['role']={'walnut':'warm_walnut','enamel':'ivory_enamel','glass':'hospitality_glass','stone':'warm_stone'}[q['role']];ob['category']=q['category'];ob['runtime_collision']=True
for q in P['furniture']:
 T=Matrix.Translation(Vector((q['at'][0],-q['at'][2],q['at'][1])))@Matrix.Rotation(q['yaw'],4,'Z')
 for original in furn[q['native']]:
  if original.type!='MESH':continue
  ob=original.copy();ob.data=original.data.copy();ob.parent=None;ob.name=q['name']+'__'+original.name;ob.matrix_world=T@original.matrix_world;bpy.context.collection.objects.link(ob);ob['category']='source_furniture';ob['runtime_collision']=True
  furniture_audit.append({'name':ob.name,'source_native':q['native'],'source_name':original.name,'placement':q,'source_world_matrix':[list(row)for row in original.matrix_world]})
for ob in loaded:bpy.data.objects.remove(ob,do_unlink=True)
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
rec=export_native(bpy,W,R,'AftCrownSittingBays_r001.blend',P['structure_file']);P['structure']=rec;P['native_export_records']=[rec];P['model_pins']={rec['export']:rec['export_sha256']};P['furniture_meshes']=furniture_audit
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/AFT_CROWN_SITTING_BAYS.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('PASS immutable bays',len(P['parts']),'enclosure meshes',len(furniture_audit),'exact rigid furniture meshes')
