from pathlib import Path
import bpy,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
bpy.ops.wm.read_factory_settings(use_empty=True);source={}
for file in sorted({q['material_native']for q in P['closure_sites']}):
 with bpy.data.libraries.load(str(R/file),link=False)as(src,dst):dst.objects=[q['source_name']for q in P['closure_sites']if q['material_native']==file]
 for ob in dst.objects:
  assert ob is not None
  bpy.context.collection.objects.link(ob);source[ob.name]=ob
bpy.context.view_layer.update();P['parts']=[];F=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
for i,row in enumerate(P['closure_sites']):
 ob=source[row['source_name']];vs=[ob.matrix_world@v.co for v in ob.data.vertices];assert vs;xs=[v.x for v in vs];zs=[-v.y for v in vs];ys=[v.z for v in vs];assert abs(max(ys)-row['bottom'])<.0001,(ob.name,max(ys),row['bottom']);lo=[min(xs),row['bottom'],min(zs)];hi=[max(xs),row['top'],max(zs)];x,y,z=lo;X,Y,Z=hi;assert X>x and Y>y and Z>z
 verts=[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]];name='CCJ_Cap'+str(i)+'_'+row['source_name'];me=bpy.data.meshes.new(name);me.from_pydata([(v[0],-v[2],v[1])for v in verts],[],F);me.update()
 for m in ob.data.materials:me.materials.append(m)
 uv=me.uv_layers.new(name='SourceScaleWorldProjection')
 for face in me.polygons:
  axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3)if a!=axis]
  for k in face.loop_indices:
   v=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(v[axes[0]],v[axes[1]])
 new=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(new);new['role']=row['source']['role'];new['category']='wall_ceiling_closure';new['runtime_collision']=True;P['parts'].append({'name':name,'verts':verts,'faces':F,'role':row['source']['role'],'category':'wall_ceiling_closure','runtime_collision':True,'source_name':row['source_name'],'source_root':row['source_root'],'bottom':row['bottom'],'top':row['top'],'expected_bounds':[lo,hi],'material_native':row['material_native'],'source_materials_exact':True})
for ob in source.values():bpy.data.objects.remove(ob,do_unlink=True)
rec=export_native(bpy,W,R,'D04CommonsCeilingJunctions_r001.blend','D04_COMMONS_CEILING_JUNCTIONS_r001.glb');P['structure_file']=rec['export'];P['structure']=rec;P['native_export_records']=[rec];P['model_pins']={rec['export']:rec['export_sha256']}
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_COMMONS_CEILING_JUNCTIONS.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('Immutable additive ceiling closures:',len(P['parts']))
