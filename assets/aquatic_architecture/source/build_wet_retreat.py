"""Original open crescent wet-rest retreat: authored wall, soffit and light locations."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','warm_stone','champagne_metal','dark_rubber','aquatic/aquatic_edge_tile']:
 m=bpy.data.materials.new(role.split('/')[-1]);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.7
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('alcove_diffuser');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.91,.76,1);b.inputs['Emission Color'].default_value=(1,.85,.67,1);b.inputs['Emission Strength'].default_value=1.2;mats['alcove_diffuser']=m
parts=[]
def sweep(name,profile,role,start=-math.pi/2,end=math.pi/2,steps=20):
 verts=[];uv=[];n=len(profile);arc=0;previous=None
 for i in range(steps+1):
  t=start+(end-start)*i/steps;center=Vector((3.4*math.sin(t),2.7*math.cos(t)))
  if previous is not None:arc+=(center-previous).length
  previous=center
  for depth,z in profile:verts.append(((3.4-depth)*math.sin(t),(2.7-depth)*math.cos(t),z));uv.append((arc*.5,z*.5+depth*.5))
 faces=[tuple(reversed(range(n))),tuple(steps*n+j for j in range(n))]
 for i in range(steps):
  for j in range(n):k=(j+1)%n;faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 ob=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(ob);d.materials.append(mats[role]);parts.append(ob);layer=d.uv_layers.new(name='MetreScaled')
 for f in d.polygons:
  for li in f.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
 return ob
sweep('AQR_WetWall',[(0,0),(.22,0),(.22,1.36),(0,1.36)],'aquatic/aquatic_edge_tile')
sweep('AQR_UpperWall',[(0,1.39),(.20,1.39),(.20,3.2),(0,3.2)],'ivory_enamel')
sweep('AQR_WashableFoot',[(.20,0),(.30,0),(.30,.12),(.26,.19),(.20,.19)],'warm_stone')
sweep('AQR_BeltReveal',[(0,1.355),(.215,1.355),(.215,1.40),(0,1.40)],'dark_rubber')
sweep('AQR_BeltTrim',[(.215,1.40),(.23,1.40),(.23,1.44),(.215,1.44)],'champagne_metal')
sweep('AQR_ShelteringSoffit',[(0,3.20),(1.02,3.20),(1.02,3.05),(.9,2.94),(.2,2.94),(0,3.04)],'ivory_enamel')
sweep('AQR_RecessedCeilingInlay',[(.24,2.939),(.85,2.939),(.85,2.91),(.24,2.91)],'aquatic/aquatic_edge_tile')
for i,t in enumerate([-.62,.62]):
 sweep(f'AQR_Lens_{i}',[(.44,2.902),(.61,2.902),(.61,2.91),(.44,2.91)],'alcove_diffuser',t-.07,t+.07,2)
 o=bpy.data.objects.new('DATUM_light_'+str(i),None);bpy.context.collection.objects.link(o);o.location=((3.4-.525)*math.sin(t),(2.7-.525)*math.cos(t),2.89)
for name,loc in [('ENTRY',(0,-.4,0)),('LOUNGER_LEFT',(-1.1,.8,0)),('LOUNGER_RIGHT',(1.1,.8,0)),('TRAY',(0,.6,0))]:
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=loc
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();blend=ROOT/'source/AST-AQU-011.blend';glb=ROOT/'exports/AST-AQU-011.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-AQU-011.manifest.json').write_text(json.dumps({'catalogue_id':'AST-AQU-011','name':'Sheltered crescent wet-rest retreat','status':'Draft, not a complete room; visual and interaction fit review pending','design_dimensions_m':[6.8,2.7,3.2],'open_front':True,'floor_included':False,'triangles':tri,'source':'source/AST-AQU-011.blend','export':'exports/AST-AQU-011.glb','lounger_recipe':'AST-AQU-001 at source datums; tray AST-AQU-002 at tray datum; no assumptions about all-species body compatibility','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n')
print('RETREAT_CREATED',tri)
