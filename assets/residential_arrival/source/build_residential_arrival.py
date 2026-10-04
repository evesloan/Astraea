"""Original fitted D13 quiet-arrival ceiling and floor family within the existing street."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[];material_contract=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil','oatmeal_weave','clay_weave']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=material_contract.get(role,{}).get('roughness',.82);b.inputs['Metallic'].default_value=material_contract.get(role,{}).get('metallic',0);m['meters_per_tile_uv']=material_contract.get(role,{}).get('meters_per_tile_uv',[1,1])
 path=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 return o

def extrusion(name,outline,bottom,top,role):
 n=len(outline);v=[(x,y,z)for z in [bottom,top]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role)

def beam(name,points,width,depth,role):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0));up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p

# Local X crosses the 4.1m street, Y runs along it, Z is height.
# Section rises away from the suite door; the opposing frontage remains open
# until its actual addressed unit is fitted. No invented window or room.
profile=[(0,2.91),(.24,2.91),(.58,3.12),(1.02,3.50),(1.34,3.64),(3.02,3.64),(3.46,3.48),(3.86,3.24),(4.1,3.24),(4.1,3.34),(3.86,3.34),(3.49,3.58),(3.05,3.74),(1.31,3.74),(.95,3.59),(.50,3.20),(.20,3.01),(0,3.01)]
n=len(profile)
mesh('ARR_ProfiledAcousticCeiling',[(x,y,z)for y in [-3.6,3.6]for x,z in profile],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'oatmeal_weave')
for j,y in enumerate([-3.45,3.45]):
 points=[(x,y,z-.022)for x,z in profile[:9]]
 beam('ARR_EndRib_'+str(j),points,.065,.07,'warm_walnut')
# Continuous door-side timber cornice and recessed light exits.
extrusion('ARR_DoorCornice',[(.04,-3.6),(.20,-3.6),(.20,3.6),(.04,3.6)],2.73,2.90,'warm_walnut')
for j,y in enumerate([-2.45,0,2.45]):
 extrusion('ARR_Recess_'+str(j),[(.26,y-.26),(.46,y-.26),(.46,y+.26),(.26,y+.26)],2.96,3.04,'champagne_metal')
 extrusion('ARR_Lens_'+str(j),[(.29,y-.22),(.43,y-.22),(.43,y+.22),(.29,y+.22)],2.950,2.957,'lens')
 datum('arrival_light_'+str(j),(.36,y,2.94))
# A bordered runner widens at the suite approach, with purposeful fine inlays.
outline=[(.46,-3.6),(3.50,-3.6),(3.50,-1.9),(3.65,-.9),(3.65,.9),(3.50,1.9),(3.50,3.6),(.46,3.6),(.46,1.9),(.25,.95),(.25,-.95),(.46,-1.9)]
extrusion('ARR_RunnerBorder',outline,.001,.008,'clay_weave')
extrusion('ARR_RunnerField',[(x+.08 if x<2 else x-.08,y)for x,y in outline],.008,.010,'teal_weave')
for j,y in enumerate([-2.5,-1.9,1.9,2.5]):
 extrusion('ARR_WovenWaymark_'+str(j),[(1.30,y-.055),(2.85,y-.055),(2.99,y+.055),(1.44,y+.055)],.010,.011,'oatmeal_weave')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();source=ROOT/'source/AST-ARR-001.blend';export=ROOT/'exports/AST-ARR-001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role,material in mats.items():
 selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='ARR_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-ARR-001.manifest.json').write_text(json.dumps({'catalogue_id':'AST-ARR-001','name':'Quiet suite arrival with rising acoustic ceiling and woven runner','source':'source/AST-ARR-001.blend','export':'exports/AST-ARR-001.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Source drafted; runtime and architectural review pending'},indent=2)+'\n')
