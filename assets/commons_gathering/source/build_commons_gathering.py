"""Authored communal planting island and sheltered conversation canopy."""
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

# Anchor ship(79,84,4). Planting remains beneath the real upper opening;
# a lower canopy frames the existing southern conversation edge.
N=32
levels=[(3.02,1.18,.02),(3.25,1.38,.14),(3.40,1.48,.46),(3.38,1.46,.59),(3.16,1.24,.64)]
vertices=[]
for rx,ry,z in levels:
 for i in range(N):
  a=2*math.pi*i/N;scallop=1+.035*math.sin(3*a)
  vertices.append((rx*math.cos(a)*scallop,ry*math.sin(a),z))
faces=[tuple(reversed(range(N)))]
for ring in range(len(levels)-1):
 for i in range(N):faces.append((ring*N+i,ring*N+(i+1)%N,(ring+1)*N+(i+1)%N,(ring+1)*N+i))
faces.append(tuple(range((len(levels)-1)*N,len(levels)*N)))
mesh('GATHER_ProfiledIslandBasin',vertices,faces,'warm_stone')
inner=[(3.05*math.cos(2*math.pi*i/N)*(1+.035*math.sin(6*math.pi*i/N)),1.14*math.sin(2*math.pi*i/N))for i in range(N)]
extrusion('GATHER_Soil',inner,.64,.665,'botanical_soil')
# Slender, continuous recessed bronze bands follow the actual bowl profile.
for z,rx,ry in [(.13,3.255,1.385),(.48,3.395,1.475)]:
 v=[]
 for dz in [0,.024]:
  for i in range(N):
   a=2*math.pi*i/N;v.append((rx*math.cos(a)*(1+.035*math.sin(3*a)),ry*math.sin(a),z+dz))
 mesh('GATHER_ProfileBand_'+str(z),v,[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)],'champagne_metal')
for i,p in enumerate([(-1.5,-.08,.665),(1.35,.05,.665)]):datum('canopy_plant_'+str(i),p)
for i in range(12):
 a=2*math.pi*i/12;datum('underplant_'+str(i),(2.45*math.cos(a),.78*math.sin(a),.665))
# A fan of low acoustic ceiling petals around the existing conversation seats.
# Outer ring is lowered; centre lifted, with actual supports at its back edge.
for i in range(12):
 a=2*math.pi*i/12;b=a+2*math.pi/12*.96
 q=[(.8*math.cos(a),-6+.6*math.sin(a),3.87),(4.15*math.cos(a),-6+2.85*math.sin(a),3.44),(4.15*math.cos(b),-6+2.85*math.sin(b),3.44),(.8*math.cos(b),-6+.6*math.sin(b),3.87)]
 mesh('GATHER_AcousticPetal_'+str(i),q+[(x,y,z+.10)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
for i,x in enumerate([-3.8,3.8]):
 # Fanned support profile grows into canopy rather than a floating lid.
 profile=[(x-.09,-7.55),(x+.09,-7.55),(x+.09,-7.35),(x-.09,-7.35)]
 extrusion('GATHER_CanopySupport_'+str(i),profile,0,3.48,'warm_walnut')
 beam('GATHER_CanopyBranch_'+str(i),[(x,-7.45,3.35),(x*.60,-7.45,3.70),(x*.25,-7.45,3.82)],.14,.14,'warm_walnut')
for i,(x,y,h)in enumerate([(-2.1,-6,3.56),(2.1,-6,3.56)]):
 extrusion('GATHER_LightHousing_'+str(i),[(x-.42,y-.18),(x+.42,y-.18),(x+.42,y+.18),(x-.42,y+.18)],h,h+.10,'champagne_metal')
 extrusion('GATHER_LightLens_'+str(i),[(x-.37,y-.14),(x+.37,y-.14),(x+.37,y+.14),(x-.37,y+.14)],h-.012,h,'lens')
 datum('light_'+str(i),(x,y,h-.03))
# A real pendant above the planted island uses the existing two-storey opening.
# Its stem meets the commons roof; it does not float beneath an absent ceiling.
ring_count=16;v=[]
for radius,h in [(.42,7.77),(.60,7.63),(.86,7.40),(.82,7.34)]:
 for i in range(ring_count):
  a=2*math.pi*i/ring_count;v.append((radius*math.cos(a),radius*math.sin(a),h))
f=[]
for k in range(3):
 for i in range(ring_count):f.append((k*ring_count+i,k*ring_count+(i+1)%ring_count,(k+1)*ring_count+(i+1)%ring_count,(k+1)*ring_count+i))
mesh('GATHER_IslandPendantShade',v,f,'champagne_metal')
extrusion('GATHER_IslandOpalLens',[(.80*math.cos(2*math.pi*i/16),.80*math.sin(2*math.pi*i/16))for i in range(16)],7.325,7.34,'lens')
extrusion('GATHER_IslandPendantStem',[(-.035,-.035),(.035,-.035),(.035,.035),(-.035,.035)],7.76,8.16,'warm_walnut')
datum('light_2',(0,0,7.29))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-COM-002.blend';export=ROOT/'exports/AST-COM-002.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
for role,material in mats.items():
 selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='GATHER_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-COM-002.manifest.json').write_text(json.dumps({'catalogue_id':'AST-COM-002','name':'Commons planting island and sheltered gathering canopy','source':'source/AST-COM-002.blend','export':'exports/AST-COM-002.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Authored draft; source, route and visual acceptance pending'},indent=2)+'\n')
