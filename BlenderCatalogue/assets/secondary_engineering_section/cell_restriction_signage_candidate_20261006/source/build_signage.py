from pathlib import Path
import bpy,bmesh,json,math,hashlib,resource,numpy as np
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];P=json.loads((R/'source/sign_plan.json').read_text());OUT=R/'source/AST-ENG-008_cell_restriction_signage.blend';EXPORT=R/'exports/AST-ENG-008_cell_restriction_signage.glb';assert not OUT.exists()and not EXPORT.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cv(p):return Vector((p[0],-p[2],p[1]))
def xyz(p):return [p.x,p.z,-p.y]
for p,h in P['immutable_inputs'].items():assert sha(p)==h
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(P['source_blend'],link=False)as(a,b):b.materials=[n for n in a.materials if n in ['ASTRAEA_staff_label','ASTRAEA_staff_rubber']]
mats={m.get('astraea_material_role'):m for m in b.materials};assert set(mats)=={'staff_label','staff_rubber'}
font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf');objects=[];textrows=[]
def uv(mesh):
 layer=mesh.uv_layers.new(name='MetreScaled')
 for f in mesh.polygons:
  normal=f.normal;axes=[k for k in range(3)if k!=max(range(3),key=lambda k:abs(normal[k]))]
  for li in f.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;layer.data[li].uv=(v[axes[0]],v[axes[1]])
def box(name,bounds,role):
 x,y,z,X,Y,Z=bounds;vs=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];m=bpy.data.meshes.new(name);m.from_pydata([cv(v)for v in vs],[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();uv(m);o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);m.materials.append(mats[role]);o['sign_group']='SIGN_FIXED_EAST_HEADER';objects.append(o);return o
box('HeaderBackedEnamelPlate',P['header']['plate_bounds_xyz'],'staff_label')
def text(name,body,center,normal,cap,width,role,group):
 d=bpy.data.curves.new(name,'FONT');d.body=body;d.font=font;d.size=1;d.align_x='CENTER';d.resolution_u=3;d.extrude=.00004;d.bevel_depth=0;d.materials.append(mats[role]);o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update();bb=np.array(o.bound_box);size=bb.max(0)-bb.min(0);s=min(cap/size[1],width/size[0]);o.scale=(s,s,s);rot=Matrix(((0,0,1),(1,0,0),(0,1,0)))if normal[0]>0 else Matrix(((0,0,-1),(-1,0,0),(0,1,0)));o.rotation_euler=rot.to_euler();mid=(Vector(bb.min(0))+Vector(bb.max(0)))*.5;o.location=cv(center)-rot@(mid*s);o['sign_group']=group;o['canonical_text']=body;o['collision_contract']='none';o['backing_source_sha256']=P['model_sha256'];objects.append(o);bpy.context.view_layer.update();world=np.array([xyz(o.matrix_world@Vector(v))for v in o.bound_box]);row={'name':name,'text':body,'bounds_xyz':world.min(0).tolist()+world.max(0).tolist(),'actual_cap_height_m':float(size[1]*s),'requested_cap_height_m':cap,'group':group};textrows.append(row);return o
h=P['header'];text('HeaderRestrictionText',h['text'],h['text_center_xyz'],h['normal_xyz'],h['cap_height_m'],h['max_width_m'],h['text_role'],h['name'])
l=P['leaf_print']
for i,(body,center)in enumerate(zip(l['lines'],l['line_centers_xyz'])):text('PrintedGateLine_'+str(i),body,center,l['normal_xyz'],l['cap_height_m'],l['max_width_m'],l['material_role'],l['name'])
for o in objects:o['catalogue_id']='AST-ENG-008';o['catalogue_derivative']='restricted_cell_signage';o['collision_contract']='none'
bpy.context.scene['scope']=P['scope'];bpy.context.scene['runtime_adopted']=False;bpy.context.scene['source_backing_model_sha256']=P['model_sha256'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
# Export duplicates only. Editable fonts and original role graphs remain saved untouched.
dg=bpy.context.evaluated_depsgraph_get();groups={};tri=[];material_ids=[];material_names=[]
for o in objects:
 me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));me.transform(o.matrix_world);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.calc_loop_triangles()
 if not me.uv_layers:uv(me)
 for t in me.loop_triangles:
  tri.append([xyz(me.vertices[i].co)for i in t.vertices]);mat=me.materials[t.material_index].name
  if mat not in material_names:material_names.append(mat)
  material_ids.append(material_names.index(mat))
 e=bpy.data.objects.new('Export_'+o.name,me);bpy.context.scene.collection.objects.link(e);groups.setdefault(o['sign_group'],[]).append(e)
exportobs=[]
for group,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 o=obs[0];o.name=group;o['collision_contract']='none';o['catalogue_id']='AST-ENG-008';o['source_backing_model_sha256']=P['model_sha256'];o['bind_source_owner']='LEAF_WORKBAY_CELL'if group==l['name']else'SectionStatic_0_WORKBAY';o['moving_with_existing_leaf']=group==l['name'];exportobs.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in exportobs:o.select_set(True)
bpy.context.view_layer.objects.active=exportobs[0];bpy.ops.export_scene.gltf(filepath=str(EXPORT),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
np.savez_compressed(R/'qa/expected_export_triangles.npz',triangles=np.array(tri),material_ids=np.array(material_ids),material_names=np.array(material_names),source_sha256=np.array(sha(OUT)))
for p,h in P['immutable_inputs'].items():assert sha(p)==h
report={'source_sha256':sha(OUT),'export_sha256':sha(EXPORT),'editable_fonts':4,'editable_backing_plates':1,'mesh_groups':len(exportobs),'triangles':len(tri),'text_rows':textrows,'materials':material_names,'all_new_collision_contracts':'none','old_source_unchanged':True,'new_lights':0,'new_emission_or_shader_graphs':0,'runtime_adopted':False,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/BUILD.json').write_text(json.dumps(report,indent=2)+'\n');print('SIGN_SOURCE_BUILT',json.dumps(report),flush=True)
