"""Original open crescent conversation alcove; coordinated seating, back and canopy."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','warm_walnut','champagne_metal','dark_rubber','teal_weave','oatmeal_weave']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.80 if 'weave' in role else .66
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('OpalConversationLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.93,.82,1);b.inputs['Emission Color'].default_value=(1,.9,.76,1);b.inputs['Emission Strength'].default_value=1.3;mats['lens']=m
parts=[]
def mesh(name,v,f,role):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.x+q.y)*.8,q.z*.8) if abs(p.normal.z)<.5 else (q.x*.8,q.y*.8)
 return o
def arc(name,profile,a,b,role,steps=20):
 n=len(profile);v=[]
 for i in range(steps+1):
  t=math.radians(a+(b-a)*i/steps)
  for r,z in profile:v.append((r*math.cos(t),-r*math.sin(t),z))
 f=[tuple(reversed(range(n))),tuple(range(steps*n,(steps+1)*n))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(steps) for j in range(n)]
 return mesh(name,v,f,role)
arc('ALC_ProfiledSeatBase',[(2.55,0),(3.48,0),(3.53,.20),(3.40,.40),(2.63,.40),(2.55,.30)],-75,75,'ivory_enamel')
arc('ALC_SeatShadowReveal',[(2.58,.30),(2.64,.30),(2.64,.37),(2.58,.37)],-75,75,'dark_rubber')
# Individual cushions keep a relaxed rhythm without fake random variants.
for i in range(8):
 a=-73+i*18.4;b=a+17.4
 arc('ALC_Cushion_'+str(i),[(2.58,.39),(3.30,.39),(3.29,.49),(2.62,.49),(2.56,.44)],a,b,'oatmeal_weave',3)
 arc('ALC_BackCushion_'+str(i),[(3.25,.48),(3.47,.46),(3.57,.94),(3.43,1.04),(3.30,1.00)],a,b,'teal_weave',3)
arc('ALC_AcousticBack',[(3.48,.10),(3.70,.10),(3.76,1.42),(3.64,1.62),(3.49,1.58)],-77,77,'warm_walnut')
arc('ALC_BackCap',[(3.46,1.55),(3.77,1.55),(3.77,1.62),(3.46,1.62)],-77,77,'champagne_metal')
arc('ALC_Canopy',[(2.30,3.15),(3.80,3.15),(3.85,3.40),(3.67,3.56),(2.48,3.56),(2.30,3.36)],-82,82,'ivory_enamel')
arc('ALC_CanopyInset',[(2.56,3.14),(3.50,3.14),(3.50,3.16),(2.56,3.16)],-76,76,'warm_walnut')
# Slender structural returns reach the actual room ceiling, supporting the canopy.
for a in [-78,78]:
 arc('ALC_Rib_'+str(a),[(3.63,0),(3.82,0),(3.82,5.60),(3.63,5.60)],a-1.5,a+1.5,'champagne_metal',1)
for i,a in enumerate([-48,0,48]):
 arc('ALC_Lens_'+str(i),[(2.66,3.12),(2.97,3.12),(2.97,3.14),(2.66,3.14)],a-5,a+5,'lens',3)
 t=math.radians(a);o=bpy.data.objects.new('DATUM_light_'+str(i),None);bpy.context.collection.objects.link(o);o.location=(2.8*math.cos(t),-2.8*math.sin(t),3.02)
for i,a in enumerate([-61,-42,-23,-4,15,34,53]):
 t=math.radians(a);o=bpy.data.objects.new('DATUM_seat_'+str(i),None);bpy.context.collection.objects.link(o);o.location=(2.97*math.cos(t),-2.97*math.sin(t),.49);o['future_use']='Potential seating datum; no NPC seating implementation claimed'
v=[(0,0,.012)]+[(2.2*math.cos(i*math.pi/24),3.0*math.sin(i*math.pi/24),.012) for i in range(48)];mesh('ALC_VisualFloorInlay',v,[(0,i+1,(i+1)%48+1) for i in range(48)],'oatmeal_weave')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-SAL-008.blend';glb=ROOT/'exports/AST-SAL-008.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-SAL-008.manifest.json').write_text(json.dumps({'catalogue_id':'AST-SAL-008','name':'Open crescent conversation alcove','source':'source/AST-SAL-008.blend','export':'exports/AST-SAL-008.glb','triangles':tri,'status':'Draft; requires collision, ceiling fit and visual review','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('CONVERSATION_ALCOVE_CREATED',tri)
