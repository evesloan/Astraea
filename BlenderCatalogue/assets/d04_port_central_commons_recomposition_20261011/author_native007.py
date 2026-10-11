from pathlib import Path
import bpy,bmesh,json,hashlib,sys,math,numpy as np
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
bpy.ops.wm.read_factory_settings(use_empty=True);audit=[]
def split(poly,a,s,b):
 I=[];O=[]
 for i,A in enumerate(poly):
  B=poly[(i+1)%len(poly)];da=s*(A[0][a]-b);db=s*(B[0][a]-b);(I if da>=0 else O).append(A)
  if (da<0)!=(db<0):t=da/(da-db);v=(A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t);I.append(v);O.append(v)
 return I,O
area=lambda p:sum(np.linalg.norm(np.cross(p[i][0]-p[0][0],p[i+1][0]-p[0][0]))/2 for i in range(1,len(p)-1))
def clip(ob,boxes):
 ob.data.calc_loop_triangles();uv=ob.data.uv_layers.active;vs=[];fs=[];us=[];ms=[];lost=0;unchanged=0
 for tri in ob.data.loop_triangles:
  triangle=[(np.array(ob.matrix_world@ob.data.vertices[ob.data.loops[k].vertex_index].co,dtype=np.float64),np.array(uv.data[k].uv,dtype=np.float64))for k in tri.loops];pieces=[triangle];removed=0
  for box in boxes:
   lo=box['min'];hi=box['max'];lo=(lo[0],-hi[2],lo[1]);hi=(hi[0],-box['min'][2],hi[1]);nxt=[]
   for q in pieces:
    current=q;outside=[]
    for a in range(3):
     for s,b in [(1,lo[a]),(-1,hi[a])]:
      if not current:break
      current,out=split(current,a,s,b)
      if len(out)>=3 and area(out)>1e-9:outside.append(out)
    drop=area(current)if len(current)>=3 else 0
    if drop<1e-9:outside=[q]
    assert abs(sum(area(x)for x in outside)+drop-area(q))<1e-7
    removed+=drop;nxt+=outside
   pieces=nxt
  lost+=removed;unchanged+=removed<1e-9
  for q in pieces:
   for i in range(1,len(q)-1):
    t=[q[0],q[i],q[i+1]];start=len(vs);vs.extend(tuple(v)for v,u in t);us.extend(tuple(u)for v,u in t);fs.append((start,start+1,start+2));ms.append(tri.material_index)
 old=ob.data;me=bpy.data.meshes.new(ob.name+'_bounded_successor');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 lay=me.uv_layers.new(name=uv.name)
 for i,u in enumerate(us):lay.data[i].uv=u
 for i,poly in enumerate(me.polygons):poly.material_index=ms[i]
 ob.data=me;ob.parent=None;ob.matrix_world=Matrix.Identity(4);audit.append({'name':ob.name,'removed_area_m2':lost,'exact_unchanged_triangles':int(unchanged),'output_triangles':len(fs),'strict_area_conservation_UV_interpolation':True})
for file in sorted({q['source_model']for q in P['cuts']}):bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/file))
keep=[]
for q in P['cuts']:
 ob=bpy.data.objects[q['name']];clip(ob,q['boxes']);ob['role']=q['collision_policy']['role'];ob['category']=q['collision_policy']['category'];ob['runtime_collision']=q['collision_policy']['collide'];keep.append(ob.name)
for ob in list(bpy.data.objects):
 if ob.name not in keep:bpy.data.objects.remove(ob,do_unlink=True)
with bpy.data.libraries.load(str(R/P['source_co_native']),link=False)as(src,dst):dst.objects=src.objects
for source_ob in dst.objects:
 if source_ob:bpy.context.collection.objects.link(source_ob)
bpy.context.view_layer.update()
objs={o.name.replace('.','_'):o for o in dst.objects if o}; moved_copies=[]
for q in P['moves']:
 source=objs[q['name']];ob=source.copy();ob.data=source.data.copy();ob.name=q['name'];bpy.context.collection.objects.link(ob);ob.parent=None;d=q['delta'];ob.matrix_world=Matrix.Translation(Vector((d[0],-d[2],d[1])))@source.matrix_world
 if q['name']in P['front_clip_boxes']:clip(ob,[P['front_clip_boxes'][q['name']]])
 ob['role']=q['collision_policy']['role'];ob['category']=q['collision_policy']['category'];ob['runtime_collision']=q['collision_policy']['collide']
 moved_copies.append((ob,q['name']))
for ob in dst.objects:
 if ob:bpy.data.objects.remove(ob,do_unlink=True)
for ob,name in moved_copies:ob.name=name
patch=export_native(bpy,W,R,'D04PortCentralCommonsPatch_r003.blend',P['patch_file']);bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
def mat(role):
 if role in materials:return materials[role]
 m=bpy.data.materials.new('PCR_'+role);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.78;im=bpy.data.images.load(str(R/'BlenderCatalogue/materials'/('staff/staff_opal.png'if role=='opal_glow'else('staff/'+role+'.png'if role.startswith('staff_')else role+'.png'))));im.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;node.interpolation='Closest';m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 if role=='opal_glow':m.node_tree.links.new(node.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.6
 materials[role]=m;return m
for q in P['parts']:
 me=bpy.data.meshes.new(q['name']);me.from_pydata([(x,-z,y)for x,y,z in q['verts']],[],q['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(q['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(mat(q['role']));uv=me.uv_layers.new(name='MetreScaled')
 for poly in me.polygons:
  n=poly.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for k in poly.loop_indices:at=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(at.dot(u),at.dot(v))
 for k in ['category','role','runtime_collision']:ob[k]=q[k]
with bpy.data.libraries.load(str(R/P['gate_source']['native']),link=False)as(src,dst):dst.objects=src.objects
for source_ob in dst.objects:
 if source_ob:bpy.context.collection.objects.link(source_ob)
bpy.context.view_layer.update()
objs={o.name.replace('.','_'):o for o in dst.objects if o};s=P['gate_source']['source_pivot'];s=Vector((s[0],-s[2],s[1]));mapping=[]
for i,g in enumerate(P['gates']):
 t=g['pivot'];T=Matrix.Translation(Vector((t[0],-t[2],t[1])))@Matrix.Rotation(math.radians(g['source_rotation_y_degrees']),4,'Z')@Matrix.Translation(-s)
 for name in P['gate_source']['members']+P['gate_source']['control_members']:
  old=objs[name];ob=old.copy();ob.data=old.data.copy();ob.name='PCR_G'+str(i)+'_'+name;bpy.context.collection.objects.link(ob);ob.parent=None;ob.matrix_world=T@old.matrix_world;mapping.append({'name':ob.name,'source':name,'rigid_copy_exact_geometry_UV_materials':True})
for ob in dst.objects:
 if ob:bpy.data.objects.remove(ob,do_unlink=True)
owned=export_native(bpy,W,R,'D04PortCentralCommonsRearRoute_r005.blend',P['structure_file']);P.update(patch=patch,structure=owned,native_export_records=[patch,owned],model_pins={q['export']:q['export_sha256']for q in[patch,owned]})
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
for f in[W/'PLAN.json',W/'RUNTIME_PLAN.json',R/'Game/data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json']:f.write_text(json.dumps(P,indent=2)+'\n')
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'native_records':P['native_export_records'],'clip_audit':audit,'mapping':mapping,'original_native_exports_unchanged':len(P['source_protected_native_exports'])},indent=2)+'\n');print('Commons immutable native exports complete')
