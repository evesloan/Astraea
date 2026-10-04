"""Curated sealed SunCorp machinery display, mounted on a central axis."""
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

for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets']:
 if a['catalogue_id']=='AST-ENG-007':assert a['source']=='assets/fusion_exhibit/source/AST-ENG-007.blend','Identity already belongs elsewhere'
m=bpy.data.materials.new('ContainedInstrumentEmission');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.025,.19,.24,1);p.inputs['Emission Color'].default_value=(.05,.65,.80,1);p.inputs['Emission Strength'].default_value=1.4;mats['energy']=m
m=bpy.data.materials.new('DeepCeramicRecess');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.055,.095,.11,1);p.inputs['Roughness'].default_value=.7;mats['recess']=m

def axial(name,rings,role,n=24):
 v=[(x,r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n))for x,r in rings for i in range(n)];f=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
 for j in range(len(rings)-1):
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 return mesh(name,v,f,role)

def hoop(name,x,radius,section,role,n=24,m=6):
 v=[]
 for i in range(n):
  a=2*math.pi*i/n
  for j in range(m):
   b=2*math.pi*j/m;v.append((x+section*math.cos(b),(radius+section*math.sin(b))*math.cos(a),(radius+section*math.sin(b))*math.sin(a)))
 f=[(i*m+j,i*m+(j+1)%m,((i+1)%n)*m+(j+1)%m,((i+1)%n)*m+j)for i in range(n)for j in range(m)];return mesh(name,v,f,role)
# Clean profiled end housings flank a contained illuminated instrument sleeve.
axial('FUS_SealedInstrumentSleeve',[(-4.4,1.35),(-3.7,1.48),(3.7,1.48),(4.4,1.35)],'energy')
for side in [-1,1]:
 rings=[(side*x,r)for x,r in [(3.7,1.52),(4.0,1.73),(5.8,1.73),(6.5,1.42),(7.8,1.12),(8.15,.80)]]
 if side<0:rings.reverse()
 axial('FUS_ProfiledEndHousing_'+str(side),rings,'ivory_enamel')
 for x in [4.15,5.6,6.4,7.7]:hoop('FUS_ShoulderTrim_%s_%s'%(side,x),side*x,1.77 if x<6 else(1.47 if x<7 else 1.16),.045,'champagne_metal')
 axial('FUS_EndRecess_'+str(side),[(side*8.14,.65),(side*8.24,.65)],'recess')
 for i in range(8):
  a=2*math.pi*i/8;q=[(side*8.28,.15*math.cos(a-.25),.15*math.sin(a-.25)),(side*8.28,.55*math.cos(a-.14),.55*math.sin(a-.14)),(side*8.28,.55*math.cos(a+.14),.55*math.sin(a+.14)),(side*8.28,.15*math.cos(a+.25),.15*math.sin(a+.25))];mesh('FUS_IrisPetal_%s_%s'%(side,i),q,[(0,1,2,3)],'champagne_metal')
# Precisely repeated induction rings are machine construction, not exposed
# maintenance walkways. Covers and manifolds remain curated exhibit geometry.
for i,x in enumerate([-3.5,-2.1,-.7,.7,2.1,3.5]):
 hoop('FUS_InductionBand_'+str(i),x,1.57,.09,'ivory_enamel')
 hoop('FUS_InductionAccent_'+str(i),x+.11,1.54,.025,'champagne_metal')
for j in range(4):
 a=math.pi/4+j*math.pi/2;y=1.79*math.cos(a);z=1.79*math.sin(a)
 beam('FUS_ContainedCoolantSpine_'+str(j),[(-6.1,y*.8,z*.8),(-5.5,y,z),(5.5,y,z),(6.1,y*.8,z*.8)],.12,.12,'champagne_metal')
# Designed suspension yokes meet the corresponding gallery frame cross-beams.
for x in [-5.5,5.5]:
 beam('FUS_SuspensionYoke_'+str(x),[(x,-1.25,.95),(x,-.75,1.9),(x,-.35,2.16),(x,.35,2.16),(x,.75,1.9),(x,1.25,.95)],.18,.18,'ivory_enamel')
 datum('mount_'+str(x),(x,0,2.25))
for i,x in enumerate([-2.5,2.5]):datum('transmitted_light_'+str(i),(x,0,-2.20))
datum('axis_origin',(0,0,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-ENG-007.blend';export=ROOT/'exports/AST-ENG-007.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role in ['ivory_enamel','energy','recess','champagne_metal']:
 selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==mats[role]]
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='FUS_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':'AST-ENG-007','name':'Curated contained fusion-gallery instrument','source':'source/AST-ENG-007.blend','export':'exports/AST-ENG-007.glb','pivot':'Mount-axis centre; not floor origin','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Original fictional machinery exhibit; source/placement/lighting and screening checks pending; no reactor engineering claim'};(ROOT/'AST-ENG-007.manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
