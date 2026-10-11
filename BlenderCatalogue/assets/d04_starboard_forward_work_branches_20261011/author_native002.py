from pathlib import Path
import bpy,bmesh,json,hashlib,sys,numpy as np,math,collections
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
bpy.ops.wm.read_factory_settings(use_empty=True)
for file in sorted({q['source_model']for q in P['cuts']+P['moves']}):bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/file))
pre={q['name']:q for q in P['runtime_preimages']};audit=[];keep=[]
def split(poly,a,s,b):
 I=[];O=[]
 for i,A in enumerate(poly):
  B=poly[(i+1)%len(poly)];da=s*(A[0][a]-b);db=s*(B[0][a]-b);(I if da>=0 else O).append(A)
  if (da<0)!=(db<0):t=da/(da-db);v=(A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t);I.append(v);O.append(v)
 return I,O
area=lambda p:sum(np.linalg.norm(np.cross(p[i][0]-p[0][0],p[i+1][0]-p[0][0]))/2 for i in range(1,len(p)-1))
for row in P['cuts']+P['moves']:
 ob=bpy.data.objects[row['name']];ob.data.calc_loop_triangles();uv=ob.data.uv_layers.active;ts=[]
 for tri in ob.data.loop_triangles:ts.append(([(np.array(ob.matrix_world@ob.data.vertices[ob.data.loops[k].vertex_index].co,dtype=np.float64),np.array(uv.data[k].uv,dtype=np.float64))for k in tri.loops],tri.material_index))
 expected=np.array([(v[0],-v[2],v[1])for v in pre[row['name']]['world_triangle_vertices']]);actual=np.array([v for q,m in ts for v,u in q]);assert len(expected)==len(actual);dist=np.linalg.norm(expected[:,None,:]-actual[None,:,:],axis=2);err=max(float(dist.min(0).max()),float(dist.min(1).max()));bound=float(np.ptp(actual,axis=0).max())/65535+.000005;
 if 'delta'in row:
  proof=json.load(open(W/'FRESH_IMPORT_FACES001.json'));assert proof['source_sha256']==P['source_pins']['Game/assets/models/'+row['source_model']];fresh=np.array([(v[0],-v[2],v[1])for v in proof['faces'][row['name']]]);assert collections.Counter(tuple(sorted(map(tuple,fresh[i:i+3])))for i in range(0,len(fresh),3))==collections.Counter(tuple(sorted(map(tuple,expected[i:i+3])))for i in range(0,len(expected),3)),ob.name+' fresh Godot import triangle multiset differs';raw=np.array([(v[0],-v[2],v[1])for v in json.load(open(W/'RAW_SOURCE_VERTICES.json'))[row['name']]]);rawdist=np.linalg.norm(raw[:,None,:]-actual[None,:,:],axis=2);raw_error=max(float(rawdist.min(0).max()),float(rawdist.min(1).max()));assert raw_error<.00001,(ob.name,raw_error);measured=np.linalg.norm(raw[:,None,:]-expected[None,:,:],axis=2);bound=max(float(measured.min(0).max()),float(measured.min(1).max()))+.00001
 assert err<=bound,(ob.name,err,bound)
 if 'delta'in row:
  d=row['delta'];ob.parent=None;ob.location+=Vector((d[0],-d[2],d[1]));keep.append(ob.name);audit.append({'name':ob.name,'translation_only':d,'runtime_coordinate_error_m':err,'import_quantization_bound_m':bound});continue
 vertices=[];faces=[];uvs=[];mats=[];lost_area=0.;exact=0
 for triangle,material in ts:
  pieces=[triangle];lost=0
  for box in row['boxes']:
   lo=box['min'];hi=box['max'];lo=(lo[0],-hi[2],lo[1]);hi=(hi[0],-box['min'][2],hi[1]);nextpieces=[]
   for q in pieces:
    current=q;outpieces=[]
    for a in range(3):
     for s,b in [(1,lo[a]),(-1,hi[a])]:
      if not current:break
      current,out=split(current,a,s,b)
      if len(out)>=3 and area(out)>1e-9:outpieces.append(out)
    removed=area(current)if len(current)>=3 else 0
    if removed<1e-9:outpieces=[q]
    assert abs(sum(area(x)for x in outpieces)+removed-area(q))<1e-7
    lost+=removed;nextpieces+=outpieces
   pieces=nextpieces
  if lost<1e-9:exact+=1
  lost_area+=lost
  for q in pieces:
   for i in range(1,len(q)-1):
    tri=[q[0],q[i],q[i+1]];start=len(vertices);vertices.extend(tuple(v)for v,u in tri);uvs.extend(tuple(u)for v,u in tri);faces.append((start,start+1,start+2));mats.append(material)
 me=bpy.data.meshes.new(ob.name+'_bounded_apertures');me.from_pydata(vertices,[],faces);me.update()
 for m in ob.data.materials:me.materials.append(m)
 layer=me.uv_layers.new(name='RetainedSourceUV')
 for i,u in enumerate(uvs):layer.data[i].uv=u
 for i,poly in enumerate(me.polygons):poly.material_index=mats[i]
 ob.data=me;ob.parent=None;ob.matrix_world.identity();ob['role']=row['preimage']['role'];ob['category']=row['preimage']['category'];ob['runtime_collision']=row['preimage']['runtime_collision'];keep.append(ob.name);audit.append({'name':ob.name,'input_triangles':len(ts),'exact_unchanged_triangles':exact,'removed_area_m2':lost_area,'output_triangles':len(faces),'runtime_coordinate_error_m':err,'import_quantization_bound_m':bound,'strict_area_conservation_and_UV_interpolation':True})
for ob in list(bpy.data.objects):
 if ob.name not in keep:bpy.data.objects.remove(ob,do_unlink=True)
patch=json.load(open(W/'PARTIAL_NATIVE_PATCH_RECEIPT001.json'));assert sha(W/patch['native'])==patch['native_sha256']and sha(W/patch['export'])==patch['export_sha256'];bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
def mat(role):
 if role in materials:return materials[role]
 m=bpy.data.materials.new('SFW_'+role);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.78;im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/('staff/staff_opal.png'if role=='opal_glow'else role+'.png')));im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Closest';m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 if role=='opal_glow':m.node_tree.links.new(n.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.6
 materials[role]=m;return m
for p in P['parts']:
 me=bpy.data.meshes.new(p['name']);me.from_pydata([(x,-z,y)for x,y,z in p['verts']],[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(mat(p['role']));layer=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in poly.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;layer.data[k].uv=(q.dot(u),q.dot(v))
 for k in ['category','role','runtime_collision']:ob[k]=p[k]
source=R/P['gate_source']['native'];owned_before=set(bpy.data.objects)
with bpy.data.libraries.load(str(source),link=False)as(src,dst):dst.objects=src.objects
source_objects={o.name:o for o in dst.objects if o};s=P['gate_source']['source_pivot'];s=Vector((s[0],-s[2],s[1]));mapping_records=[]
for i,g in enumerate(P['gates']):
 t=g['pivot'];T=Matrix.Translation(Vector((t[0],-t[2],t[1])))@Matrix.Rotation(math.radians(g['source_rotation_y_degrees']),4,'Z')@Matrix.Translation(-s)
 for name in P['gate_source']['members']+P['gate_source']['control_members']:
  old=source_objects[name];ob=old.copy();ob.data=old.data.copy();ob.name='SFW_G'+str(i)+'_'+name;bpy.context.collection.objects.link(ob);ob.parent=None;ob.matrix_world=T@old.matrix_world
  if name.endswith('_Control')and i>=4:
   d=g['fixed_control_delta'];ob.location+=Vector((d[0],-d[2],d[1]))
  mapping_records.append({'name':ob.name,'source':name,'rotation_godot_y_degrees':g['source_rotation_y_degrees'],'new_pivot':g['pivot'],'geometry_UVs_materials_unchanged':True})
for name in P['closed_staging_source_members']:
 old=source_objects[name];ob=old.copy();ob.data=old.data.copy();ob.name='SFW_ClosedDock_'+name;bpy.context.collection.objects.link(ob);ob.parent=None;d=P['closed_staging_translation'];ob.matrix_world=Matrix.Translation(Vector((d[0],-d[2],d[1])))@old.matrix_world
for ob in dst.objects:
 if ob:bpy.data.objects.remove(ob,do_unlink=True)
owned=export_native(bpy,W,R,'D04StarboardForwardWorkBranches_r002.blend',P['structure_file']);P['patch']=patch;P['structure']=owned;P['native_export_records']=[patch,owned];P['model_pins']={q['export']:q['export_sha256']for q in P['native_export_records']}
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_STARBOARD_FORWARD_WORK_BRANCHES.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'native_records':P['native_export_records'],'local_source_clip_audit':audit,'rigid_original_gate_mappings':mapping_records,'original_native_exports_unchanged':4351},indent=2)+'\n');print('Court links immutable native exports complete')
