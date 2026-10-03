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

# Roof loft varies in section and plan; side leaves taper toward their ends.
ys=[-4.8,-3.6,-1.4,1.2,3.3,4.5];xs=[-3.5,-2.6,-1.2,.3,1.9]
heights=[3.72,4.47,5.08,5.34,5.16]
v=[]
for j,y in enumerate(ys):
 taper=[.68,.95,1,1,.94,.65][j]
 for i,x in enumerate(xs):v.append((-1.2+(x+1.2)*taper,y,heights[i]-.22*abs(y)/4.8))
for j in range(len(ys)-1):
 for i in range(len(xs)-1):
  q=[v[j*5+i],v[j*5+i+1],v[(j+1)*5+i+1],v[(j+1)*5+i]]
  mesh('OVL_RoofPanel_%d_%d'%(j,i),q+[(x,y,z+.16)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel' if i==4 or j in [0,4] else 'warm_walnut')
for index,y in enumerate([-3.6,-.2,3.3]):
 points=[(-3.18,y,0),(-3.18,y,2.8),(-3.06,y,3.83),(-2.55,y,4.20),(-1.2,y,4.86),(.3,y,5.10),(1.64,y,4.97)]
 beam('OVL_BranchFrame_'+str(index),points,.22,.30,'champagne_metal')
 extrusion('OVL_ColumnFoot_'+str(index),[(-3.45,y-.30),(-2.91,y-.30),(-2.91,y+.30),(-3.45,y+.30)],0,.10,'warm_stone')
# Two distinct built-in rests: a long shared perch and shorter private seat.
for index,(a,b) in enumerate([(-2.95,-.55),(.45,2.95)]):
 outline=[(-3.12,a),(-2.08,a+.12),(-1.92,a+.35),(-1.94,b-.25),(-2.10,b),(-3.12,b)]
 extrusion('OVL_SeatPlinth_'+str(index),outline,0,.36,'ivory_enamel')
 for slat in range(5):
  x=-2.90+slat*.17
  extrusion('OVL_SeatTimber_%d_%d'%(index,slat),[(x,a+.14),(x+.14,a+.14),(x+.14,b-.12),(x,b-.12)],.36,.46,'warm_walnut')
 extrusion('OVL_BackSupport_'+str(index),[(-3.20,a),(-2.98,a),(-2.98,b),(-3.20,b)],.35,1.34 if index==0 else 1.65,'ivory_enamel')
 extrusion('OVL_BackPad_'+str(index),[(-2.97,a+.15),(-2.88,a+.15),(-2.88,b-.15),(-2.97,b-.15)],.55,1.16,'teal_weave')
 datum('seat_'+str(index),(-2.43,(a+b)/2,.46))
# End planting masses enclose the resting pockets, not the circulation face.
for index,(cy,rx,ry) in enumerate([(-4.05,1.0,.64),(3.85,1.2,.56)]):
 outline=[(-1.9+rx*math.cos(i*math.tau/16),cy+ry*math.sin(i*math.tau/16))for i in range(16)]
 extrusion('OVL_Planter_'+str(index),outline,0,.62,'warm_stone')
 inner=[(-1.9+rx*.88*math.cos(i*math.tau/16),cy+ry*.84*math.sin(i*math.tau/16))for i in range(16)]
 extrusion('OVL_Soil_'+str(index),inner,.62,.66,'botanical_soil')
 datum('plant_'+str(index),(-1.9,cy,.66))
for index,y in enumerate([-1.8,1.8]):
 extrusion('OVL_RecessedLightHousing_'+str(index),[(-1.35,y-.30),(-.92,y-.30),(-.92,y+.30),(-1.35,y+.30)],4.69,5.12,'champagne_metal')
 extrusion('OVL_OpalLight_'+str(index),[(-1.31,y-.25),(-.96,y-.25),(-.96,y+.25),(-1.31,y+.25)],4.675,4.69,'lens')
 datum('light_'+str(index),(-1.135,y,4.65))
datum('clear_approach',(.3,0,0));datum('court_view',(1.6,0,1.65))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-GAR-003.blend';glb=ROOT/'exports/AST-GAR-003.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Keep semantic pieces editable in .blend; batch only the exported static visual by material.
for role,material in mats.items():
 selected=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='OVL_Runtime_'+role
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-GAR-003.manifest.json').write_text(json.dumps({'catalogue_id':'AST-GAR-003','name':'Asymmetric botanical overlook canopy and resting bay','source':'source/AST-GAR-003.blend','export':'exports/AST-GAR-003.glb','triangles':tri,'status':'Draft; integration/contact/visual review pending','usage':'D06 port atrium terrace, court-facing edge local +X; not a complete room','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('GARDEN_OVERLOOK_CREATED',tri)
