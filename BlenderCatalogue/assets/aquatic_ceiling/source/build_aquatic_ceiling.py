"""Authored aquatic ceiling, fitted to the actual upper opening and protected cinema substrate."""
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
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));
 if name in ['AQU_HighCentralField','AQU_MiddleCove','AQU_PeripheralSoffit','AQU_VesperLiftRelief']:
  # Triangulated cap boundary T-junctions can confuse global normal propagation.
  # These level faces have an explicit authored outward direction.
  low=min(v.co.z for v in bm.verts);high=max(v.co.z for v in bm.verts)
  for face in bm.faces:
   zs=[v.co.z for v in face.verts]
   if max(zs)-min(zs)<1e-5:
    want=-1 if abs(zs[0]-low)<1e-5 else 1
    if face.normal.z*want<0:face.normal_flip()
 bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
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


D=json.loads((ROOT/'source/ceiling_contract.json').read_text());AID='AST-AQU-012'
m=bpy.data.materials.new('AquaticTerracottaEnamel');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.76;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials/retail/retail_terracotta_enamel.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);m['meters_per_tile_uv']=[1,1];mats['terracotta']=m
def xyz(x,y,z):return(x-8,182-z,y-61)
def wall(name,a,b,lo,hi,width,role):
 a=Vector((a[0]-8,182-a[1]));b=Vector((b[0]-8,182-b[1]));t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo-61,hi-61,role)
for layer in D['layers']:
 v=[];f=[]
 for tri in layer['triangles']:
  for h,reverse in [(layer['lo'],True),(layer['hi'],False)]:
   start=len(v);v.extend([xyz(p[0],h,p[1])for p in tri]);f.append(tuple(start+i for i in ([2,1,0]if reverse else[0,1,2])))
 for ring in layer['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   start=len(v);v.extend([xyz(a[0],layer['lo'],a[1]),xyz(b[0],layer['lo'],b[1]),xyz(b[0],layer['hi'],b[1]),xyz(a[0],layer['hi'],a[1])]);f.append(tuple(range(start,start+4)))
 mesh('AQU_'+layer['name'],v,f,layer['role'])
for name,edge,lo,hi in [('Inner',D['central_edge'],68.36,68.85),('Outer',D['middle_edge'],67.56,68.2)]:
 segments=D.get('edge_segments',{}).get('central_edge' if name=='Inner' else 'middle_edge',list(zip(edge,edge[1:]+edge[:1])))
 for i,(a,b)in enumerate(segments):
  wall('AQU_'+name+'TerracottaReveal_'+str(i),a,b,lo,hi,.08,'terracotta')
  wall('AQU_'+name+'ChampagneEdge_'+str(i),a,b,lo-.035,lo+.025,.10,'champagne_metal')
if D.get('lift_relief_boundary'):
 edge=D['lift_relief_boundary']
 for i,(a,b)in enumerate(zip(edge,edge[1:]+edge[:1])):wall('AQU_LocalLiftCoveReturn_'+str(i),a,b,67.4,68.2,.06,'ivory_enamel')
for i,(x,z)in enumerate(D['bearing_centers_xz']):
 ring=[(x+1.45*math.cos(j*math.pi/8),z+1.45*math.sin(j*math.pi/8))for j in range(16)]
 for j,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):wall('AQU_BearingCoffer_%s_%s'%(i,j),a,b,67.4,69.1,.06,'warm_walnut')
 # Short transfers join each bearing to the boundary support zone, not across the central field.
 end=(x,182.05)if i==0 else(53.95,z)if i==1 else(8.05,z)
 beam('AQU_PerimeterTransfer_'+str(i),[xyz(x,68.95,z),xyz(end[0],68.95,end[1])],.32,.30,'ivory_enamel')
# Pendant-free surface fixtures fitted to lower peripheral ceiling zones.
for i,(x,z)in enumerate([(15,207),(52,207),(20,246),(43,186)]):
 cx,cy=x-8,182-z;q=[(cx+.42*math.cos(j*math.pi/8),cy+.42*math.sin(j*math.pi/8))for j in range(16)]
 extrusion('AQU_CoveHousing_'+str(i),q,67.27-61,67.4-61,'champagne_metal')
 extrusion('AQU_CoveDiffuser_'+str(i),[(cx+(a-cx)*.88,cy+(b-cy)*.88)for a,b in q],67.245-61,67.27-61,'lens');datum('ceiling_light_'+str(i),(cx,cy,67.22-61))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role,m in mats.items():
 selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==m]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='AQU_Ceiling_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Aquatic stepped ceiling and bearing coffers','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable fitted ceiling; compiled closure, fixture contacts and visual acceptance pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
