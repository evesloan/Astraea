"""Pending source-slot approval: dark, measured readable glyphs only; original candidate is immutable."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];BASE=R.parent;D=json.loads((BASE/'source/HOME_SPEC.json').read_text());INPUT=BASE/'source/AST-STF-010_home_dogleg.blend';PIN='886f35ff29f66a4d644b15781e386dba728756bbdf82125d72ae2dd52522a764'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cv(v):return Vector((v[0],-v[2],v[1]))
def signature(o):
 if o.type!='MESH':return {'type':o.type,'matrix':[list(row)for row in o.matrix_world]}
 return {'matrix':[list(row)for row in o.matrix_world],'vertices':[list(v.co)for v in o.data.vertices],'polygons':[list(p.vertices)for p in o.data.polygons],'uvs':[[list(q.uv)for q in layer.data]for layer in o.data.uv_layers],'materials':[m.name for m in o.data.materials]}
def sig(o):return hashlib.sha256(json.dumps(signature(o),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def uv_project(me,mat):
 uv=me.uv_layers.active or me.uv_layers.new(name='MetreScaled');scale=mat.get('meters_per_tile_uv',[1,1])
 for p in me.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in p.loop_indices:q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
assert sha(INPUT)==PIN;out=R/'source/AST-STF-010_home_dogleg_labels002.blend';export=R/'exports/AST-STF-010_home_dogleg_labels002.glb';assert not out.exists()and not export.exists();bpy.ops.wm.open_mainfile(filepath=str(INPUT));bpy.context.view_layer.update();names={r['name']for r in D['labels']};before={o.name:sig(o)for o in bpy.context.scene.objects if o.name not in names};old_labels={n:sig(bpy.data.objects[n])for n in names};mat=next(m for m in bpy.data.materials if m.get('astraea_material_role')=='staff_rubber');font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');measured=[]
for label in D['labels']:
 old=bpy.data.objects[label['name']];parent=old.parent;basis=old.matrix_basis.copy();bpy.data.objects.remove(old,do_unlink=True)
 cu=bpy.data.curves.new(label['name'],'FONT');cu.body=label['text'];cu.font=font;cu.size=1;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.001;cu.resolution_u=3;o=bpy.data.objects.new(label['name'],cu);bpy.context.collection.objects.link(o);o.parent=parent;n=cv(label['normal_xyz']).normalized();up=Vector((0,0,1));right=up.cross(n);o.matrix_basis=Matrix.Translation(cv(label['position_xyz']))@Matrix((right,up,n)).transposed().to_4x4();cu.materials.append(mat);bpy.context.view_layer.update();bb=[Vector(p)for p in o.bound_box];width=max(v.x for v in bb)-min(v.x for v in bb);height=max(v.y for v in bb)-min(v.y for v in bb);target=.15 if label['name']in ['HOME_Header_Text','HOME_Service_Directions']else .095;scale=min(target/height,label['width_m']/width);o.scale*=scale;bpy.context.view_layer.update();assert height*scale>=target*.90
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;uv_project(o.data,mat);o['collision_contract']='none';o['label_text']=label['text'];o['backing_part']=label['backing'];o['actual_ink_height_m']=height*scale;measured.append({'name':o.name,'text':label['text'],'width_m':width*scale,'height_m':height*scale,'material_role':'staff_rubber','backing':label['backing']})
for n,h in before.items():assert sig(bpy.data.objects[n])==h,n
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];groups={};triangles=0
for o in meshes:
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles);vs=[o.matrix_world@v.co for v in o.data.vertices];c=sum(vs,Vector())/len(vs);k=(o.parent.name if o.parent else'',o.data.materials[0].name,str(o.get('collision_contract','static_surface')),math.floor(c.x/20),math.floor(-c.y/20),math.floor(c.z/8.5));groups.setdefault(k,[]).append(o)
for i,(key,objs)in enumerate(sorted(groups.items())):
 members=[o.name for o in objs];bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=sorted(objs,key=lambda o:o.name)[0]
 if len(objs)>1:bpy.ops.object.join()
 o=bpy.context.view_layer.objects.active;o.name='HOME_BATCH_%03d_%s'%(i,key[1]);o['source_members_json']=json.dumps(members);o['collision_contract']=key[2];o['catalogue_id']='AST-STF-010'
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False);assert sha(INPUT)==PIN
receipt={'scope':'Only four collision-free label meshes replaced; all other source objects exact; current old candidate immutable','input_source_sha256':PIN,'source_sha256':sha(out),'export_sha256':sha(export),'unchanged_objects':before,'old_label_signatures':old_labels,'labels':measured,'editable_meshes':len(meshes),'triangles':triangles,'export_batches':len(groups),'visual_acceptance':False};(R/'qa/LABEL_CORRECTION_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in['unchanged_objects','old_label_signatures']},indent=2))
