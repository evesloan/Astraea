"""R070 site-specific approach guard assembly; not counted as a separate unique design."""
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
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
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
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));side=(side-t*t.dot(side)).normalized();up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p

D=json.loads((ROOT/'source/room_contract.json').read_text())
m=bpy.data.materials.new('ApproachSmokedGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.24,.42,.43,.32);b.inputs['Alpha'].default_value=.32;mats['glass']=m
for i,(a,b)in enumerate(D['approach_guard_segments_xz']):
 a=Vector((236-a[1],72-a[0]));b=Vector((236-b[1],72-b[0]));v=(b-a).normalized();n=Vector((-v.y,v.x))
 for label,z0,z1,width,role in [('foot',0,.24,.14,'ivory_enamel'),('glass',.24,1.01,.024,'glass'),('rail',1.01,1.10,.09,'champagne_metal')]:
  w=n*width/2;extrusion('APP_%s_%03d'%(label,i),[tuple(a+w),tuple(b+w),tuple(b-w),tuple(a-w)],z0,z1,role)
 if (b-a).length>1.0:
  for k in range(math.ceil((b-a).length/1.8)+1):
   p=a+(b-a)*k/math.ceil((b-a).length/1.8);q=[(p.x-.026,p.y-.026),(p.x+.026,p.y-.026),(p.x+.026,p.y+.026),(p.x-.026,p.y+.026)];extrusion('APP_post_%d_%d'%(i,k),q,.24,1.02,'champagne_metal')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-RTL-005_approach.blend';export=ROOT/'exports/AST-RTL-005_approach.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
# Room-sized material groups keep the derived assembly inexpensive to submit.
for role in ['ivory_enamel','glass','champagne_metal']:
 selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==mats[role]]
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='APP_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
print('Authored approach boundary assembly exported:',len(D['approach_guard_segments_xz']),'segments')
