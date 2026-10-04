"""Original faceted hospitality wall lantern with profiled backplate and opal diffuser."""
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

# Fixture backplate sits onY0; front points toward negative sourceY.
N=24;v=[]
for y,scale in [(.015,.92),(-.005,1),(-.035,.92)]:
 for i in range(N):
  a=2*math.pi*i/N;x=.205*math.copysign(abs(math.cos(a))**.72,math.cos(a))*scale;z=.45+.445*math.copysign(abs(math.sin(a))**.72,math.sin(a))*scale
  v.append((x,y,z))
f=[tuple(reversed(range(N))),tuple(range(2*N,3*N))]
for k in range(2):
 for i in range(N):f.append((k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i))
mesh('LANTERN_ProfiledCeramicBackplate',v,f,'ivory_enamel')
# Inset patterned central back surface has a distinct narrow metallic shoulder.
for x in [-.14,.14]:
 beam('LANTERN_VerticalFin_'+str(x),[(x,-.042,.16),(x,-.10,.25),(x,-.10,.68),(x,-.042,.76)],.035,.026,'champagne_metal')
# Faceted opal globe is intentionally economical; silhouette carries the form.
rings=10;segments=16;v=[]
for j in range(rings+1):
 phi=math.pi*j/rings
 for i in range(segments):
  a=2*math.pi*i/segments;v.append((.135*math.sin(phi)*math.cos(a),-.16+.13*math.sin(phi)*math.sin(a),.45+.235*math.cos(phi)))
f=[]
for j in range(rings):
 for i in range(segments):f.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
mesh('LANTERN_OpalDiffuser',v,f,'lens')
for h,label in [(.185,'Lower'),(.685,'Upper')]:
 q=[(.145*math.cos(2*math.pi*i/16),-.16+.14*math.sin(2*math.pi*i/16))for i in range(16)]
 extrusion('LANTERN_'+label+'Collar',q,h,h+.03,'champagne_metal')
for h in [.20,.70]:
 beam('LANTERN_StandOff_'+str(h),[(0,-.02,h),(0,-.11,h)],.07,.045,'champagne_metal')
datum('light_exit',(0,-.31,.45))
datum('wall_mount',(0,0,.45))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-LGT-001.blend';export=ROOT/'exports/AST-LGT-001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role,material in mats.items():
 selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='LANTERN_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-LGT-001.manifest.json').write_text(json.dumps({'catalogue_id':'AST-LGT-001','name':'Profiled opal hospitality wall lantern','source':'source/AST-LGT-001.blend','export':'exports/AST-LGT-001.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Authored draft; source/fixture/collision/visual review pending'},indent=2)+'\n')
