"""Bounded support/retained-fixture successor. No original outputs overwritten."""
import bpy,bmesh,json,hashlib,struct,sys,importlib.util
from pathlib import Path
from mathutils import Vector
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2]; G=R/'Game/orchard_tram_interior_20261025'
D=G/'r007';N=R/'BlenderCatalogue/assets/orchard_tram_interior_20261025/r007'
assert not D.exists() and not N.exists();D.mkdir();N.mkdir()
source=R/'BlenderCatalogue/assets/orchard_tram_interior_20261025/integration/OrchardIntegratedReceiving_r006_faces.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source))
def xyz(v):return (float(v[0]),-float(v[2]),float(v[1]))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geometry(o):return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[[tuple(x.uv) for x in l.data] for l in o.data.uv_layers],list(o.matrix_world))).encode()).hexdigest()
before={o.name:geometry(o) for o in bpy.data.objects if o.type=='MESH'}
spec=importlib.util.spec_from_file_location('author',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
plan=json.loads((G/'r006/PLAN.json').read_text());build=json.loads((G/'r006/BUILD.json').read_text())
row=next(x for x in build['receiver_bindings'] if x['cursor']==228 and x['leg'][0]>19)
old_leg=np.array(row['leg']);leg=old_leg+np.array([.20,0]);pad=np.array(row['pad'])
q,t=a.PathFit(np.array(plan['route_points_xz'])).sample(228);shoe=q+np.array([t[1],-t[0]])*1.48
a.beam('RouteDrop_10_1',[leg[0],55.72,leg[1]],[leg[0],60.5,leg[1]],.08,.08)
a.beam('RouteOverarm_10_1',[leg[0],60.34,leg[1]],[pad[0],60.34,pad[1]],.18,.32)
a.beam('RouteShoe_10_1',[shoe[0],55.60,shoe[1]],[leg[0],55.60,leg[1]],.38,.19)
changed=[]
for part in a.parts:
 o=bpy.data.objects[part['name']];mat=o.data.materials[0];mesh=bpy.data.meshes.new(part['name']+'_r007')
 mesh.from_pydata([xyz(v) for v in part['vertices']],[],part['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 uv=mesh.uv_layers.new(name='MaterialMetres')
 for face in mesh.polygons:
  axis=max(range(3),key=lambda j:abs(face.normal[j]));axes=[j for j in range(3) if j!=axis]
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/.5,v[axes[1]]/.5)
 mesh.materials.append(mat);o.data=mesh;changed.append(o.name)
# Reuse two original station fixtures, not four unchecked additional lights.
# Their new posts extend the existing station pier bearings at x9.9.
lamp_source=R/'Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-020_foremid_north_candidate.glb'
old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(lamp_source));imported=set(bpy.data.objects)-old
keep=[];lamps=[]
for suffix,old_z,new_z in [('-225',-250.,-237.05),('-218',-243.,-234.5)]:
 delta=Vector(xyz([22.72,0,new_z-old_z]))
 for role in ['Backplate','Opal']:
  name='N005_V2__Source_Lamp_'+role+'_'+suffix
  o=next(o for o in imported if o.name==name);o.location+=delta;keep.append(o)
 lamps.append({'name':'N005_V2__Source_Lamp_Opal_'+suffix,'xyz':[9.950000267028808,58.30000114440918,new_z], 'range':8,'energy':.55,'color':[1,.89,.72], 'backplate':'N005_V2__Source_Lamp_Backplate_'+suffix,'source_delta_xyz':[22.72,0,new_z-old_z]})
for o in imported-set(keep):bpy.data.objects.remove(o,do_unlink=True)
metal=bpy.data.objects['RouteDrop_10_1'].data.materials[0]
for i,z in enumerate([-237.05,-234.5]):
 # Post overlaps the protected station pier at the landing; fitting projects east.
 a.parts=[];a.box('StationFixturePost_%d'%i,[9.9,57.3,z],[.18,2.6,.18])
 part=a.parts[0];mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([xyz(v) for v in part['vertices']],[],part['faces']);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 mesh.materials.append(metal);uv=mesh.uv_layers.new(name='MaterialMetres')
 for face in mesh.polygons:
  axis=max(range(3),key=lambda j:abs(face.normal[j]));axes=[j for j in range(3) if j!=axis]
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/.5,v[axes[1]]/.5)
 o=bpy.data.objects.new(part['name'],mesh);bpy.context.collection.objects.link(o);keep.append(o)
bpy.context.view_layer.update()
unchanged=[name for name,h in before.items() if name not in changed and geometry(bpy.data.objects[name])==h]
assert len(unchanged)==len(before)-3
b=(G/'r006/OrchardInteriorReceiving.glb').read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
names={n['name'] for n in doc['nodes'] if 'mesh' in n};assert len(names)==272
bpy.ops.object.select_all(action='DESELECT')
for name in names:bpy.data.objects[name].select_set(True)
for o in keep:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'OrchardReceiving_native_export.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
text=bpy.data.texts.new('R007_AUTHORED_CORRECTION');text.write('RouteDrop_10_1 leg moves +0.20m X; overarm and shoe endpoints follow, original D10 bearing/pad retained. Two exact original lamp fittings on pier-continuous posts, same energy/range/eight-light budget. Unselected; installed and visual acceptance pending.')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(N/'OrchardIntegratedReceiving_r007.blend'))
assert sha(source)==source_hash
receipt={'status':'UNSELECTED','original_native_sha256':source_hash,'original_fixture_sha256':sha(lamp_source),'changed_supports':changed,'unchanged_native_members':unchanged,'old_leg':old_leg.tolist(),'new_leg':leg.tolist(),'unchanged_bearing':row['owner'],'unchanged_pad':pad.tolist(),'fixtures':lamps,'new_posts':['StationFixturePost_0','StationFixturePost_1'],'retired_fixture_count':4,'replacement_fixture_count':2,'physical_contact_policy':'original opal no_collision_detail; original backplate static; new posts static','light_budget_changed':False,'source_references':['Master v0.3 chapters 5,21,30,32,33','Uploaded_46/08/All-Creature-Kitchen-Ingredient-locations.webp','Uploaded_46/06/image(2).png','Uploaded_46/07/image(3).png'],'files':{p.relative_to(R).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in [D/'OrchardReceiving_native_export.glb',N/'OrchardIntegratedReceiving_r007.blend']}}
(D/'BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'changed':changed,'native_unchanged':len(unchanged),'lamps':lamps}))
