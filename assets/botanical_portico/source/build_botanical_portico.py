"""Original D06 garden overlook: sheltered back, rising roof and open court-facing edge."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[]
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.82
 path=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.x*.8,q.y*.8) if abs(p.normal.z)>.5 else ((q.x+q.y)*.8,q.z*.8)
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

# The canopy grows outward from the existing six-metre room mouth and
# raises its head toward the atrium. Two forked piers preserve a broad arrival.
rows=[(0,3.0,3.7),(2.0,3.5,4.0),(4.4,4.4,4.5),(6.3,3.8,4.3)]
for i in range(3):
 for j in range(4):
  q=[]
  for k,l in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]:
   x,w,h=rows[k];u=-1+l*.5;q.append((x,u*w,h+.30*(1-u*u)*min(1,x/2)))
  mesh('POR_RoofLeaf_%d_%d'%(i,j),q+[(x,y,z+.18)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut' if j in [1,2] else 'ivory_enamel')
for side in [-1,1]:
 x=5.15;y=side*3.65;levels=[(0,.43),(.17,.47),(.38,.31),(3.25,.24)];v=[(x+r*math.cos(i*math.tau/10),y+r*math.sin(i*math.tau/10),z)for z,r in levels for i in range(10)]
 f=[tuple(reversed(range(10))),tuple(range(30,40))]+[(k*10+i,k*10+(i+1)%10,(k+1)*10+(i+1)%10,(k+1)*10+i)for k in range(3)for i in range(10)]
 mesh('POR_ProfiledPier_'+str(side),v,f,'warm_stone')
 beam('POR_ForkBack_'+str(side),[(x,y,3.15),(4.85,side*3.8,3.85),(4.4,side*4.0,4.48)],.23,.22,'champagne_metal')
 beam('POR_ForkFront_'+str(side),[(x,y,3.15),(5.5,side*3.6,3.95),(6.15,side*3.5,4.32)],.23,.22,'champagne_metal')
 beam('POR_Fascia_'+str(side),[(x,side*w,h+.07)for x,w,h in rows],.18,.25,'ivory_enamel')
for i,x in enumerate([1.0,4.0]):
 h=3.75 if i==0 else 4.45
 extrusion('POR_LightHousing_'+str(i),[(x-.22,-.28),(x+.22,-.28),(x+.22,.28),(x-.22,.28)],h,h+.3,'champagne_metal')
 extrusion('POR_LightLens_'+str(i),[(x-.18,-.24),(x+.18,-.24),(x+.18,.24),(x-.18,.24)],h-.02,h,'lens')
 datum('light_'+str(i),(x,0,h-.04))
datum('room_joint',(0,0,0));datum('atrium_arrival',(6.2,0,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-GAR-005.blend';glb=ROOT/'exports/AST-GAR-005.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Keep semantic pieces editable in .blend; batch only the exported static visual by material.
for role,material in mats.items():
 selected=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='POR_Runtime_'+role
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-GAR-005.manifest.json').write_text(json.dumps({'catalogue_id':'AST-GAR-005','name':'Fanning botanical arrival portico','source':'source/AST-GAR-005.blend','export':'exports/AST-GAR-005.glb','triangles':tri,'status':'Draft; integration/contact/visual review pending','usage':'Shared D06 port forecourt; joins Canopy terrace mouth to existing atrium floor','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('GARDEN_OVERLOOK_CREATED',tri)
