"""Three original tabletop keepsake designs for the addressed Kind Curios shop."""
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

def lathe(name,rings,role,n=16):
 v=[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z)for z,r in rings for i in range(n)];f=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
 for j in range(len(rings)-1):
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 return mesh(name,v,f,role)
def ring(name,center,radius,tube,tilt,role,n=24,m=5):
 v=[]
 for i in range(n):
  a=2*math.pi*i/n
  for j in range(m):
   b=2*math.pi*j/m;x=(radius+tube*math.cos(b))*math.cos(a);y=(radius+tube*math.cos(b))*math.sin(a);z=tube*math.sin(b)
   v.append((center[0]+x,center[1]+y*math.cos(tilt)-z*math.sin(tilt),center[2]+y*math.sin(tilt)+z*math.cos(tilt)))
 f=[(i*m+j,i*m+(j+1)%m,((i+1)%n)*m+(j+1)%m,((i+1)%n)*m+j)for i in range(n)for j in range(m)];return mesh(name,v,f,role)
records=[]
for index,title in [(1,'Orbit keepsake'),(2,'Coiled ceramic specimen'),(3,'Folded stellar sculpture')]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[]
 aid='AST-CUR-%03d'%index
 lathe('CURIO_WeightedFoot',[(0,.12),(.02,.15),(.04,.15),(.06,.11)],'warm_walnut',12)
 lathe('CURIO_BrassCollar',[(.04,.115),(.06,.115)],'champagne_metal',12)
 if index==1:
  lathe('CURIO_Stem',[(.06,.025),(.22,.025)],'champagne_metal',8)
  ring('CURIO_InclinedOrbitA',(0,0,.31),.22,.009,.85,'champagne_metal')
  ring('CURIO_InclinedOrbitB',(0,0,.31),.19,.008,-.55,'ivory_enamel')
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.09,location=(0,0,.31));o=bpy.context.object;o.name='CURIO_CeramicWorld';o.data.materials.append(mats['teal_weave']);parts.append(o)
  for a in [0,2.1,4.2]:
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.022,location=(.22*math.cos(a),.22*math.sin(a)*math.cos(.85),.31+.22*math.sin(a)*math.sin(.85)));o=bpy.context.object;o.name='CURIO_Satellite';o.data.materials.append(mats['warm_stone']);parts.append(o)
 elif index==2:
  v=[];N=36;M=8
  for i in range(N):
   t=i/(N-1);a=t*math.pi*3.8;radius=.13*(1-t)+.025;cx=radius*math.cos(a);cy=radius*math.sin(a);cz=.11+t*.34;thick=.07*(1-t)+.012
   for j in range(M):
    b=2*math.pi*j/M;v.append((cx+thick*math.cos(b)*math.cos(a),cy+thick*math.cos(b)*math.sin(a),cz+thick*math.sin(b)))
  f=[tuple(reversed(range(M))),tuple(range((N-1)*M,N*M))]+[(i*M+j,i*M+(j+1)%M,(i+1)*M+(j+1)%M,(i+1)*M+j)for i in range(N-1)for j in range(M)]
  mesh('CURIO_SpiralCeramic',v,f,'ivory_enamel')
  ring('CURIO_SpecimenTrim',(0,0,.085),.105,.012,0,'champagne_metal',16)
 else:
  lathe('CURIO_DisplayStem',[(.06,.035),(.26,.025)],'champagne_metal',8)
  for i in range(5):
   a=2*math.pi*i/5;r=.23;v=[(0,0,.33),(.075*math.cos(a-.5),.075*math.sin(a-.5),.26),(r*math.cos(a),r*math.sin(a),.43),(.075*math.cos(a+.5),.075*math.sin(a+.5),.26),(0,0,.22)]
   mesh('CURIO_FoldedRay_'+str(i),v,[(0,1,2),(0,2,3),(4,2,1),(4,3,2),(0,4,1),(0,3,4)],'champagne_metal'if i%2 else'clay_weave')
 for o in parts:
  if not o.data.uv_layers:
   uv=o.data.uv_layers.new(name='AuthoredScale')
   for poly in o.data.polygons:
    for li in poly.loop_indices:
     q=o.data.vertices[o.data.loops[li].vertex_index].co
     uv.data[li].uv=(q.x*2+.5,q.z*2+.5)
 datum('support',(0,0,0));datum('grasp',(0,0,.22))
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(aid+'.blend');export=ROOT/'exports'/(aid+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
 for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
 record={'catalogue_id':aid,'name':title,'source':'source/'+aid+'.blend','export':'exports/'+aid+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable original draft; scale, support, UV and runtime review pending; not yet a sale/pickup system'};(ROOT/(aid+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');records.append(record)
print(records)
