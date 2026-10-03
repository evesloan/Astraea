"""Original bifurcated garden-path lantern, editable profiled stem and petal hood."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','champagne_metal','dark_rubber']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.55
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('WarmOpal');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.91,.74,1);b.inputs['Emission Color'].default_value=(1,.88,.65,1);b.inputs['Emission Strength'].default_value=1.6;mats['opal']=m
parts=[]
def mesh(name,v,f,role):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(q.x*2,q.z*2)
 return o
def rings(name,profile,role):
 v=[];n=12
 for x,y,z,rx,ry in profile:
  for j in range(n):a=j*2*math.pi/n;v.append((x+rx*math.cos(a),y+ry*math.sin(a),z))
 f=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]+[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(profile)-1) for j in range(n)]
 mesh(name,v,f,role)
rings('LANT_Foot',[(0,0,0,.23,.18),(0,0,.08,.23,.18),(0,0,.17,.13,.10)],'champagne_metal')
rings('LANT_SweptStem',[(0,0,.12,.10,.08),(.03,0,1.5,.07,.06),(.18,0,2.45,.075,.06),(.32,0,2.85,.13,.08)],'ivory_enamel')
for side in [-1,1]:rings('LANT_Fork_'+str(side),[(.20,0,2.50,.09,.06),(.37,side*.17,2.80,.075,.05),(.44,side*.30,3.03,.07,.05)],'champagne_metal')
rings('LANT_ProfiledPetalHood',[(.42,0,3.00,.72,.45),(.42,0,3.13,.78,.50),(.42,0,3.27,.65,.40),(.42,0,3.36,.37,.22),(.42,0,3.39,.08,.08)],'ivory_enamel')
rings('LANT_OpalUnderside',[(.42,0,2.97,.61,.36),(.42,0,3.015,.67,.41)],'opal')
o=bpy.data.objects.new('DATUM_light',None);bpy.context.collection.objects.link(o);o.location=(.86,0,2.88)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-GAR-002.blend';glb=ROOT/'exports/AST-GAR-002.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-GAR-002.manifest.json').write_text(json.dumps({'catalogue_id':'AST-GAR-002','name':'Bifurcated garden path lantern','source':'source/AST-GAR-002.blend','export':'exports/AST-GAR-002.glb','triangles':tri,'status':'Draft; needs in-engine source-light review','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('GARDEN_LANTERN_CREATED',tri)
