"""Original profiled hospitality column with integrated downward task lenses."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
TARGET_HEIGHT=float(globals().get('TARGET_HEIGHT',8.13));ASSET_SUFFIX=globals().get('ASSET_SUFFIX','');AID='AST-STR-001'+ASSET_SUFFIX
assert 3.5<=TARGET_HEIGHT<=9.0
def upper_height(z):return z+TARGET_HEIGHT-8.13
def upper_profile(profile):return [(upper_height(z) if z>=6.4 else z,r) for z,r in profile]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal','dark_rubber']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.65
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('diffused_lens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.95,.88,.7,1);b.inputs['Emission Color'].default_value=(1,.82,.6,1);b.inputs['Emission Strength'].default_value=1.4;mats['diffused_lens']=m
parts=[]
def lathe(name,profile,role,segments=12):
 verts=[];uv=[]
 for h,r in profile:
  for i in range(segments):
   t=2*math.pi*i/segments;verts.append((r*math.cos(t),r*math.sin(t),h));uv.append((i/segments*2*math.pi*r*.5,h*.5))
 faces=[tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))]
 for j in range(len(profile)-1):
  for i in range(segments):k=(i+1)%segments;faces.append((j*segments+i,j*segments+k,(j+1)*segments+k,(j+1)*segments+i))
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);layer=d.uv_layers.new(name='MetreScaled')
 for f in d.polygons:
  for li in f.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
 return o
lathe('STR_StoneFoot',[(0,.78),(.10,.78),(.22,.69),(.35,.58),(.5,.53)],'warm_stone')
lathe('STR_BaseReveal',[(.49,.535),(.55,.535)],'dark_rubber')
lathe('STR_TaperedShaft',upper_profile([(.54,.51),(1.2,.46),(6.4,.38),(7,.5)]),'ivory_enamel')
lathe('STR_LowerMetalBand',[(.55,.515),(.62,.515)],'champagne_metal')
lathe('STR_Capital',upper_profile([(6.96,.5),(7.14,.58),(7.38,.7),(7.58,.7),(7.58,1.12),(7.86,1.24),(8.10,1.27)]),'ivory_enamel')
lathe('STR_CapitalShadow',upper_profile([(7.92,1.278),(7.97,1.278)]),'dark_rubber')
lathe('STR_CeilingBearing',upper_profile([(8.10,1.32),(8.13,1.32)]),'champagne_metal')
for i in range(4):
 t=i*math.pi/2+math.pi/4;x,y=.9*math.cos(t),.9*math.sin(t)
 ob=lathe('STR_LightLens_'+str(i),[(0,.10),(.018,.10)],'diffused_lens',8);ob.location=(x,y,upper_height(7.56))
 marker=bpy.data.objects.new('DATUM_light_'+str(i),None);bpy.context.collection.objects.link(marker);marker.location=(x,y,upper_height(7.55))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();blend=ROOT/'source'/(AID+'.blend');glb=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/(AID+'.manifest.json')).write_text(json.dumps({'catalogue_id':'AST-STR-001','name':'Garden bearing column with lantern capital','status':'Draft; fixture exposure, normals and gameplay view pending','height_m':TARGET_HEIGHT,'bearing_radius_m':1.32,'foot_radius_m':.78,'triangles':tri,'fits_deck_pitch_m':TARGET_HEIGHT+.24,'source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n')
print('COLUMN_CREATED',tri)
