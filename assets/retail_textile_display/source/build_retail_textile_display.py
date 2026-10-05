"""Original draped textile display sample with authored folds and supported hanging rail."""
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



AID='AST-RTL-008'
assert all(a['catalogue_id']!=AID or a['family']=='retail_textile_display' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x,-z,y)
vertices=[];nx=12;ny=18
for side in [-1,1]:
 for j in range(ny+1):
  t=j/ny;y=-.045-1.24*t
  for i in range(nx+1):
   u=i/nx;x=(u-.5)*(.54+.05*t);depth=.055*math.sin(u*math.pi*5+t*.6)*(.25+.75*t)+.025*math.sin(t*math.pi)+side*.003
   vertices.append(xyz(x,y+.018*math.sin(u*math.pi)*t,depth))
stride=nx+1;layer=stride*(ny+1);faces=[]
for side in range(2):
 for j in range(ny):
  for i in range(nx):
   a=side*layer+j*stride+i;q=(a,a+1,a+1+stride,a+stride);faces.append(q if side else tuple(reversed(q)))
for i in range(nx):
 faces.append((i,i+1,layer+i+1,layer+i));a=ny*stride+i;faces.append((a,a+layer,a+layer+1,a+1))
for j in range(ny):
 a=j*stride;b=(j+1)*stride;faces.append((a,a+layer,b+layer,b));a+=nx;b+=nx;faces.append((a,b,b+layer,a+layer))
cloth=mesh('TEXTILE_AuthoredFoldedPanel',vertices,faces,'clay_weave')
beam('TEXTILE_SupportBar',[xyz(-.285,-.04,0),xyz(.285,-.04,0)],.025,.025,'champagne_metal')
beam('TEXTILE_HangingNeck',[xyz(0,-.04,0),xyz(0,-.04,.065),xyz(0,.079,.065),xyz(0,.109,.045),xyz(0,.109,-.045),xyz(0,.079,-.065),xyz(0,.02,-.065)],.018,.018,'champagne_metal')
datum('hanging_contact',xyz(0,.10,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Draped textile display with authored folds and hanging support','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original static retail sample; no cloth simulation, inventory or sale interaction'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n')
for role in ['teal_weave','oatmeal_weave']:
 cloth.data.materials[0]=mats[role];path=ROOT/'exports'/(AID+'_'+role+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_yup=True,export_extras=True)
print(record)
