from pathlib import Path
import bpy,math,json,hashlib
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[2];ID='AST-RST-LN-001'
d=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));assert not any(a.get('catalogue_id')==ID and a.get('family')!=O.name for a in d['assets'])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
mats={}
for name,c in [('warm_walnut',(.24,.12,.065,1)),('teal_weave',(.09,.26,.26,1)),('ivory_enamel',(.74,.70,.62,1)),('champagne_metal',(.43,.35,.2,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=c;bs.inputs['Roughness'].default_value=.75
 files=sorted((R/'Game/assets/models').glob('*_'+name+'.png'))
 if files:
  im=bpy.data.images.load(str(files[0]),check_existing=True);im.pack();tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 mats[name]=m
parts=[]
def mesh(name,vs,fs,mat,policy='static_concave_candidate'):
 me=bpy.data.meshes.new(name);me.from_pydata([(v[0],-v[2],v[1])for v in vs],[],fs);me.update();me.materials.append(mats[mat]);uv=me.uv_layers.new(name='MetreScale')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['catalogue_id']=ID;ob['collision_policy']=policy;parts.append(ob);return ob
# Each elliptical layered profile closes at top and bottom; no convex hull spanning a hollow support.
def profile(name,rings,mat):
 n=48;vs=[]
 for rx,rz,y,cz in rings:
  for i in range(n):a=2*math.pi*i/n;vs.append([rx*math.cos(a),y,cz+rz*math.sin(a)])
 fs=[]
 for j in range(len(rings)-1):
  for i in range(n):k=(i+1)%n;fs.append([j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i])
 # Orientation corrected below by signed volume.
 fs.append(list(reversed(range(n))));fs.append([(len(rings)-1)*n+i for i in range(n)])
 ob=mesh(name,vs,fs,mat);return ob
profile('NestWeightedPlinth',[(1.19,1.51,0,0),(1.29,1.62,.09,0),(1.29,1.62,.18,0),(1.23,1.55,.23,0)],'warm_walnut')
profile('NestEnamelRim',[(1.23,1.55,.20,0),(1.28,1.60,.25,0),(1.25,1.57,.31,0)],'ivory_enamel')
# Curved padded support: low centre, raised outer perimeter, short front lip. Nested rings form actual cushion surface.
profile('NestContouredSupport',[(1.18,1.48,.285,0),(1.21,1.51,.385,0),(1.10,1.39,.455,0),(.84,1.10,.375,0),(.35,.48,.34,0),(.08,.10,.335,0)],'teal_weave')
def box(name,c,s,mat,policy='static_concave_candidate'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(c[0],-c[2],c[1]));o=bpy.context.object;o.name=name;o.dimensions=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);be=o.modifiers.new('Soft profile','BEVEL');be.width=min(s)*.23;be.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=be.name);o['catalogue_id']=ID;o['collision_policy']=policy;parts.append(o)
box('LowTransferStep',(0,.075,-1.62),(1.45,.15,.48),'warm_walnut')
box('TransferStepPad',(0,.163,-1.64),(1.32,.026,.40),'teal_weave')
# Authored rear and side bolster arcs leave the front approach open.
for i in range(13):
 a=math.pi*i/12; x=1.035*math.cos(a);z=1.27*math.sin(a)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(x,-z,.49));o=bpy.context.object;o.name='NestBolster_%02d'%i;o.scale=(.22,.29,.20);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats['teal_weave']);o['catalogue_id']=ID;o['collision_policy']='static_concave_candidate';parts.append(o)
box('EnvironmentServicePedestal',(1.43,.31,.72),(.28,.62,.48),'ivory_enamel')
box('EnvironmentControlMount',(1.43,.65,.72),(.32,.08,.42),'champagne_metal')
box('EnvironmentServiceInset',(1.578,.34,.72),(.016,.26,.25),'warm_walnut','no_collision_detail')
# Validate closed meshes and correct orientation consistently.
import bmesh
receipts=[]
for ob in parts:
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
 if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
 assert vol>0 and all(e.is_manifold for e in bm.edges),(ob.name,vol)
 bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles();receipts.append({'name':ob.name,'triangles':len(ob.data.loop_triangles),'volume_m3':vol,'collision_policy':ob['collision_policy']})
bpy.ops.wm.save_as_mainfile(filepath=str(O/(ID+'.blend')),compress=True)
bpy.ops.export_scene.gltf(filepath=str(O/(ID+'.glb')),export_format='GLB',export_extras=True)
meta={'catalogue_id':ID,'name':'Low nesting rest platform','front':'Godot -Z','support_contact':[0,.335,0],'approach':{'min':[-.7,0,-2.95],'max':[.7,1.75,-1.87]},'service':{'min':[1.62,0,.25],'max':[2.52,1.75,1.2]},'reserved_rest_places':1,'species_assignment':None,'parts':receipts,'limits':['New low nesting construction component, no biological/body pose acceptance','Decorative service mount, no functional atmosphere/temperature controls','Final in-engine/CRT review remains open']}
(O/'component_metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print('LOW_NEST_SOURCE',len(parts),sum(q['triangles']for q in receipts),flush=True)
