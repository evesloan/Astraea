"""Original ceiling-mounted artificial daylight coffer; not an exterior skylight."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','warm_walnut','champagne_metal']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.65
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('diffused_daylight');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.92,.95,.9,1);b.inputs['Emission Color'].default_value=(.98,.97,.91,1);b.inputs['Emission Strength'].default_value=1.8;mats['diffused_daylight']=m
parts=[]
def mesh(name,v,f,role):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.5,q.y*.5)
 return o
def ring(name,profile,role):
 v=[];n=len(profile);steps=48
 for i in range(steps):
  t=2*math.pi*i/steps
  for inset,z in profile:v.append(((6-inset)*math.cos(t),(12-inset)*math.sin(t),z))
 f=[(i*n+j,i*n+(j+1)%n,((i+1)%steps)*n+(j+1)%n,((i+1)%steps)*n+j) for i in range(steps) for j in range(n)]
 mesh(name,v,f,role)
ring('DAY_ProfiledFrame',[(0,0),(0,-.45),(.30,-.65),(.75,-.65),(.95,-.4),(.95,0)],'ivory_enamel')
ring('DAY_RecessedWarmReveal',[(.75,-.63),(.95,-.4),(1.08,-.39),(.89,-.57)],'warm_walnut')
ring('DAY_MetalDiffuserSeat',[(.94,-.42),(1.12,-.42),(1.12,-.37),(.94,-.37)],'champagne_metal')
v=[(0,0,-.39)]+[(4.95*math.cos(i*math.pi/24),10.95*math.sin(i*math.pi/24),-.39) for i in range(48)]
mesh('DAY_Diffuser',v,[(0,1+(i+1)%48,1+i) for i in range(48)],'diffused_daylight')
for y in [-6,0,6]:
 half=4.95*math.sqrt(1-(y/10.95)**2)
 mesh('DAY_Baffle_'+str(y),[(-half,y-.08,-.43),(half,y-.08,-.43),(half,y+.08,-.43),(-half,y+.08,-.43)],[(0,3,2,1)],'champagne_metal')
o=bpy.data.objects.new('DATUM_emitter',None);bpy.context.collection.objects.link(o);o.location=(0,0,-.70)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();blend=ROOT/'source/AST-ATR-002.blend';glb=ROOT/'exports/AST-ATR-002.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-ATR-002.manifest.json').write_text(json.dumps({'catalogue_id':'AST-ATR-002','name':'Artificial daylight ceiling coffer','status':'Draft; in-engine lighting and underside-normal review pending','source':'source/AST-ATR-002.blend','export':'exports/AST-ATR-002.glb','dimensions_m':[12,24,.65],'triangles':tri,'mounting_datum':'LocalZ0 on opaque ceiling underside; hangs down; no exterior aperture implied','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n')
print('DAYLIGHT_COFFER_CREATED',tri)
