"""Authored Gentle Waters arrival: rising threshold canopy, recessed waiting bench and coordinated wet-edge finish."""
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


AID='AST-AQU-014'
for role,file in [('wet_tile','aquatic_edge_tile.png'),('grip','aquatic_dark_grip.png')]:
 m=bpy.data.materials.new('Arrival_'+role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.83;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials/aquatic'/file));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);m['meters_per_tile_uv']=[.5,.5];mats[role]=m
def xyz(x,y,z):return(x-8,210-z,y-44)
def h(x):return 47.7+.08*(x-8.3)
outline=[(8.3,210.3),(13.8,210.3),(16,211.2),(17.4,213),(17.4,218.8),(15.8,222.2),(12,222.8),(8.3,222)]
v=[xyz(x,h(x)+offset,z)for offset in [0,.22]for x,z in outline];n=len(outline);f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];mesh('ARR_CanopyRisingField',v,f,'ivory_enamel')
# Three supported bearings leave a broad direct pool reveal along Z218.
for i,(x,z)in enumerate([(8.8,211),(8.8,221),(16.4,212)]):
 verts=[];profiles=[(0,.4),(.14,.4),(.28,.31),(h(x)-44-.45,.24),(h(x)-44-.20,.34),(h(x)-44,.42)]
 for k,(height,radius)in enumerate(profiles):
  for j in range(12):
   xx=x+radius*math.cos(j*math.pi/6);zz=z+radius*math.sin(j*math.pi/6);yy=44+height+(h(xx)-h(x)if k==len(profiles)-1 else 0);verts.append(xyz(xx,yy,zz))
 faces=[tuple(reversed(range(12))),tuple(range(60,72))]+[(k*12+j,k*12+(j+1)%12,(k+1)*12+(j+1)%12,(k+1)*12+j)for k in range(5)for j in range(12)];mesh('ARR_ProfiledBearing_'+str(i),verts,faces,'ivory_enamel')
for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):
 beam('ARR_CanopyEdge_'+str(i),[xyz(a[0],h(a[0])-.04,a[1]),xyz(b[0],h(b[0])-.04,b[1])],.13,.10,'champagne_metal')
# Curved low backing and a generous continuous perch create a waiting recess.
def back_panel(name,a,b,ha,hb):
 av=Vector((a[0]-8,210-a[1]));bv=Vector((b[0]-8,210-b[1]));t=(bv-av).normalized();n=Vector((-t.y,t.x))*.09;q=[av+n,bv+n,bv-n,av-n];v=[(p.x,p.y,0)for p in q]+[(p.x,p.y,h)for p,h in zip(q,[ha,hb,hb,ha])]
 mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
 beam(name+'_TopCap',[xyz(a[0],44+ha,a[1]),xyz(b[0],44+hb,b[1])],.20,.045,'champagne_metal')
path=[(9.9,211.8),(10.7,211.1),(12.5,210.8),(14.3,211.1),(15.1,211.8)]
for i,(a,b)in enumerate(zip(path,path[1:])):
 heights=[1.8,1.35,1.15,1.35,1.8];back_panel('ARR_RecessBacking_'+str(i),a,b,heights[i],heights[i+1])
 # Seat surface extends toward the open approach, rather than occupying the through-route.
 beam('ARR_BenchPlinth_'+str(i),[xyz(a[0],44.19,a[1]+.38),xyz(b[0],44.19,b[1]+.38)],.72,.38,'ivory_enamel')
 beam('ARR_LowPerch_'+str(i),[xyz(a[0],44.425,a[1]+.38),xyz(b[0],44.425,b[1]+.38)],.76,.09,'wet_tile')
back_panel('ARR_LeftShelteredReturn',(9.9,211.8),(9.9,212.35),1.8,1.4)
back_panel('ARR_RightShelteredReturn',(15.1,211.8),(15.1,212.35),1.8,1.4)
for i,(x,z)in enumerate([(10.9,211.446667),(12.5,211.18),(14.1,211.446667)]):datum('seat_'+str(i),xyz(x,44.47,z));datum('seat_approach_'+str(i),xyz(x,44,z+1.35))
for label,scale,y,role in [('border',.98,44.003,'grip'),('field',.95,44.005,'wet_tile')]:
 q=[xyz(12.5+(x-12.5)*scale,y,216.5+(z-216.5)*scale)for x,z in outline];o=mesh('ARR_Finish_'+label,q,[tuple(range(len(q)))],role)
 bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
 if down:bmesh.ops.reverse_faces(bm,faces=down)
 bm.to_mesh(o.data);bm.free()
for i,(x,z)in enumerate([(10.5,215),(15.2,218)]):
 cx,cy=x-8,210-z;top=h(x);q=[(cx+.28*math.cos(j*math.pi/8),cy+.28*math.sin(j*math.pi/8))for j in range(16)]
 extrusion('ARR_LightHousing_'+str(i),q,top-44-.17,top-44+.025,'champagne_metal');extrusion('ARR_OpalLens_'+str(i),[(cx+(a-cx)*.87,cy+(b-cy)*.87)for a,b in q],top-44-.20,top-44-.17,'lens');datum('arrival_light_'+str(i),xyz(x,top-.225,z))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles);o['finish_only']=o.name.startswith('ARR_Finish')
for finish in [False,True]:
 for role,m in mats.items():
  selected=[o for o in list(scene.objects)if o.type=='MESH'and o.get('finish_only')==finish and o.data.materials and o.data.materials[0]==m]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=('ARR_finish_'if finish else'ARR_static_')+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Gentle Waters rising arrival and waiting recess','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable arrival architecture; clearances, fixture contacts and normal-view review pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
