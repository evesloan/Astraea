"""New-only editable home approach and four-part retained-wall derivative.
Parent must grant the source-engine slot. Never saves an original or edits Game.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');D=json.loads((R/'source/HOME_SPEC.json').read_text());PINS=json.loads((R/'source/INPUT_PINS.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE_OWNER='AST-STF-010'
for p,h in PINS.items():assert sha(p)==h,p
F=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]

def gv(v):return Vector((v[0],-v[2],v[1]))
def empty(name,parent=None,position=(0,0,0)):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;o.location=gv(position);return o

def material(role):
 for m in bpy.data.materials:
  if m.get('astraea_material_role')==role:return m
 data=json.loads((C/'materials/staff/manifest.json').read_text());row=data['materials'][role];m=bpy.data.materials.new('ASTRAEA_'+role);m.use_nodes=True;m['astraea_material_role']=role;m['material_revision']=data['revision'];m['meters_per_tile_uv']=row['meters_per_tile_uv'];m['intended_context']='staff_only';m.diffuse_color=tuple(c/255 for c in row['colour_srgb_8bit'])+(1,)
 n=m.node_tree.nodes;n.clear();bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic'];t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(C/'materials/staff'/row['file']),check_existing=True);t.image.pack();t.extension='REPEAT';t.interpolation='Linear';out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);return m

def uv_project(me,mat):
 uv=me.uv_layers.active or me.uv_layers.new(name='MetreScaled');uv.name='MetreScaled';scale=mat.get('meters_per_tile_uv',[1,1])
 for p in me.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in p.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])

def mesh(name,vertices,faces,role,parent=None,collision='static_surface'):
 me=bpy.data.meshes.new(name);me.from_pydata([gv(v)for v in vertices],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;mat=material(role);me.materials.append(mat);uv_project(me,mat);o['catalogue_id']=SOURCE_OWNER;o['collision_contract']=collision;o['source_kind']='home_approach_derivative';return o

def box(name,b,role,parent=None,collision='static_surface'):
 x0,x1,y0,y1,z0,z1=b;assert x1>x0 and y1>y0 and z1>z0
 return mesh(name,[(x,y,z)for y in[y0,y1]for x,z in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],F,role,parent,collision)

def prism(name,profile,depth,role,parent,collision):
 n=len(profile);vs=[(x,y,z)for z in depth for x,y in profile];faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,vs,faces,role,parent,collision)

def tube(name,a,b,radius,role,parent,collision='static_surface',segments=12):
 a=Vector(a);b=Vector(b);w=(b-a).normalized();ref=Vector((0,1,0))if abs(w.y)<.9 else Vector((1,0,0));u=w.cross(ref).normalized();v=w.cross(u).normalized();vs=[tuple(p+radius*(math.cos(2*math.pi*i/segments)*u+math.sin(2*math.pi*i/segments)*v))for p in[a,b]for i in range(segments)];faces=[tuple(reversed(range(segments))),tuple(range(segments,segments*2))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments)for i in range(segments)];return mesh(name,vs,faces,role,parent,collision)

def signature(o):
 if o.type!='MESH':return {'type':o.type,'matrix':[list(row)for row in o.matrix_world]}
 return {'matrix':[list(row)for row in o.matrix_world],'vertices':[list(v.co)for v in o.data.vertices],'polygons':[list(p.vertices)for p in o.data.polygons],'uvs':[[list(q.uv)for q in layer.data]for layer in o.data.uv_layers],'materials':[m.name for m in o.data.materials]}

def signature_hash(o):return hashlib.sha256(json.dumps(signature(o),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def save_export(stem,owner):
 src=R/'source'/(stem+'.blend');dst=R/'exports'/(stem+'.glb');assert not src.exists()and not dst.exists();bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(src));sources=[o for o in bpy.context.scene.objects if o.type=='MESH'];triangles=0;groups={}
 for o in sources:
  o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles);vv=[o.matrix_world@v.co for v in o.data.vertices];centre=sum(vv,Vector())/len(vv);key=(o.parent.name if o.parent else '',o.data.materials[0].name,str(o.get('collision_contract','static_surface')),math.floor(centre.x/20),math.floor(-centre.y/20),math.floor(centre.z/8.5));groups.setdefault(key,[]).append(o)
 for i,(key,objects)in enumerate(sorted(groups.items())):
  members=[o.name for o in objects];bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=sorted(objects,key=lambda o:o.name)[0]
  if len(objects)>1:bpy.ops.object.join()
  o=bpy.context.view_layer.objects.active;o.name='HOME_BATCH_%03d_%s'%(i,key[1]);o['source_members_json']=json.dumps(members);o['collision_contract']=key[2];o['catalogue_id']=owner
 bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False)
 record={'catalogue_id':owner,'representation':stem,'source_sha256':sha(src),'export_sha256':sha(dst),'editable_meshes':len(sources),'triangles':triangles,'export_batches':len(groups),'new_floor_owners':0,'runtime_adopted':False,'first_pass_accepted':False};(R/'qa'/(stem+'_BUILD.json')).write_text(json.dumps(record,indent=2)+'\n');return record

if '--wall-only' not in sys.argv:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 names=tuple([p['name']for p in D['retained_home_parts']]+D['fixtures'][0]['donor_part_names'])
 with bpy.data.libraries.load(str(C/'assets/crew_service_platform/source/AST-STF-010.blend'),link=False)as(src,dst):
  assert set(names)<=set(src.objects);dst.objects=list(names)
 loaded=tuple(dst.objects);assert len(loaded)==len(names)and all(o is not None for o in loaded)
 for o in loaded:bpy.context.collection.objects.link(o)
 before={o.name:signature_hash(o)for o in loaded if o.name in names[:85]};assert len(before)==85
 root=empty('AST_STF_010_HOME_DOGLEG');root['derivative_id']=D['derivative_id'];root['floor_owner']='Existing compiler records only';root['first_pass_accepted']=False
 for name in names[:85]:
  o=bpy.data.objects[name];world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
 door=empty('HOME_DOOR_FITTING',root,D['door']['root_xyz']);door.rotation_euler.z=D['door']['yaw_radians'];door['open_fraction']=0.0;door['persistent_id_proposal']=D['door']['persistent_id_proposal'];door['controller_owner']='Unchanged service_door.gd state logic; local source fitting only'
 parents={'STATIC':door}
 for i,side in enumerate(['LEFT','RIGHT']):
  h=empty('HOME_HINGE_'+side,door,(D['door']['hinge_local_x'][i],0,0));parents[h.name]=h;driver=h.driver_add('rotation_euler',2).driver;driver.type='SCRIPTED';var=driver.variables.new();var.name='f';var.targets[0].id=door;var.targets[0].data_path='["open_fraction"]';driver.expression='min(max(f/0.85,0),1)*pi/2'if side=='LEFT'else'-min(max((f-0.15)/0.85,0),1)*pi/2'
 for p in D['new_parts']:
  if p['shape']=='door_prism':prism(p['name'],p['profile_x_y'],p['depth_z'],p['role'],parents[p['parent']],p['collision_contract'])
  else:box(p['name'],p['world_aabb'],p['role'],root,p['collision_contract'])
 # Source-visible pivot fittings; small hardware is excluded from actor contact,
 # while leaf/push/seal source profiles remain the runtime collision contract.
 for side,hx in zip(['LEFT','RIGHT'],D['door']['hinge_local_x']):
  sign=1 if side=='LEFT'else-1
  for j,y in enumerate([.42,1.32,2.28]):
   tube('HOME_Hinge_%s_%d'%(side,j),(hx,y-.09,0),(hx,y+.09,0),.04,'staff_zinc',door,'none')
   lo,hi=sorted([hx-sign*.11,hx+sign*.035]);box('HOME_HingeMount_%s_%d'%(side,j),[lo,hi,y-.035,y+.035,-.015,.015],'staff_zinc',door,'none')
   lo,hi=sorted([-.02*sign,.14*sign]);box('HOME_HingeStrap_%s_%d'%(side,j),[lo,hi,y-.035,y+.035,.033,.047],'staff_zinc',parents['HOME_HINGE_'+side],'none')
 for f in D['fixtures']:
  for oldname in f['donor_part_names']:
   old=bpy.data.objects[oldname];o=old.copy();o.data=old.data.copy();o.name=f['name']+'_'+oldname.rsplit('_',1)[-1];bpy.context.collection.objects.link(o);o.parent=root;o.matrix_world=Matrix.Translation(gv(f['translation_godot_xyz']))@old.matrix_world;o['source_donor']=oldname;o['collision_contract']='static_surface'
  marker=empty(f['name']+'_EMITTER',root,f['emitter_xyz']);marker['world_direction_godot_xyz']=[0,-1,0];marker['physical_lower_opal_y']=15.015;marker['exit_offset_below_opal_m']=.015
 for n in D['fixtures'][0]['donor_part_names']:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 for run in D['utility_paths']:
  for j,(a,b)in enumerate(zip(run['points_xyz'],run['points_xyz'][1:])):
   tube(run['name']+'_%02d'%j,a,b,run['radius_m'],run['role'],root)
   length=(Vector(b)-Vector(a)).length;count=max(1,math.ceil(length/2))
   for k in range(count+1):
    q=Vector(a).lerp(Vector(b),k/count);r=max(run['radius_m']+.012,.025)
    box(run['name']+'_CLIP_%d_%d'%(j,k),[q.x-r,q.x+r,q.y-.012,15.21,q.z-r,q.z+r],'staff_zinc',root)
 # Text is real editable source geometry with no actor collider.
 font_path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');assert font_path.is_file();font=bpy.data.fonts.load(str(font_path))
 for label in D['labels']:
  cu=bpy.data.curves.new(label['name'],'FONT');cu.body=label['text'];cu.font=font;cu.size=label['height_m'];cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.001;cu.resolution_u=3;o=bpy.data.objects.new(label['name'],cu);bpy.context.collection.objects.link(o);o.parent=parents[label['parent']]if 'parent'in label else root;n=gv(label['normal_xyz']).normalized();up=Vector((0,0,1));right=up.cross(n);o.matrix_basis=Matrix.Translation(gv(label['position_xyz']))@Matrix((right,up,n)).transposed().to_4x4();cu.materials.append(material('staff_white_paint'));bpy.context.view_layer.update();assert o.dimensions.length>0
  if o.dimensions.dot(Vector(tuple(abs(v)for v in right)))>label['width_m']:o.scale*=label['width_m']/o.dimensions.dot(Vector(tuple(abs(v)for v in right)))
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;uv_project(o.data,o.data.materials[0]);o['collision_contract']='none';o['label_text']=label['text'];o['backing_part']=label['backing']
 bpy.context.view_layer.update();after={name:signature_hash(bpy.data.objects[name])for name in names[:85]};assert before==after
 (R/'qa/HOME_RETAINED_85_SIGNATURES.json').write_text(json.dumps({'before':before,'after':after,'exact':True,'font_sha256':sha(font_path)},indent=2)+'\n')
 print(save_export('AST-STF-010_home_dogleg','AST-STF-010'))

if '--home-only' not in sys.argv:
 SOURCE_OWNER='AST-STF-009'
 bpy.ops.wm.open_mainfile(filepath=str(C/'assets/grand_pool_orchard_section/source/AST-STF-009_pool_market.blend'))
 changed={p['original_name']for p in D['wall_opening']};assert len(changed)==4 and all(n in bpy.data.objects for n in changed)
 before={o.name:signature_hash(o)for o in bpy.context.scene.objects if o.name not in changed}
 for p in D['wall_opening']:
  old=bpy.data.objects[p['original_name']];assert old.type=='MESH';bpy.data.objects.remove(old,do_unlink=True)
  for i,b in enumerate(p['replacement_boxes']):box(p['original_name']+'_HOME_OPEN_%d'%i,b,p['role'])
 for n,h in before.items():assert signature_hash(bpy.data.objects[n])==h,n
 (R/'qa/WALL_RETAINED_SIGNATURES.json').write_text(json.dumps({'unchanged_count':len(before),'unchanged':before,'changed_original_names':sorted(changed),'replacement_parts':8,'floor_or_lift_change':False},indent=2)+'\n')
 print(save_export('AST-STF-009_pool_market_home','AST-STF-009'))
for p,h in PINS.items():assert sha(p)==h,p
print('SOURCE CANDIDATES BUILT; NO GAME ADOPTION OR VISUAL ACCEPTANCE')
