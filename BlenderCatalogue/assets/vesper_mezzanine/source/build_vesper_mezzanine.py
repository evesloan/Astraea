"""Original Vesper upper dining, crosswise stair and fitted local lift architecture."""
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


D=json.loads((ROOT/'source/section_contract.json').read_text());AID='AST-DIN-004'
def xyz(x,y,z):return(x-21,182-z,y-61)
def xy(p):return(p[0]-21,182-p[1])
def wall(name,a,b,lo,hi,width,role):
 a=Vector(xy(a));b=Vector(xy(b));t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo-61,hi-61,role)
def slab(name,x0,x1,z0,z1,lo,hi,role):return extrusion(name,[xy(p)for p in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],lo-61,hi-61,role)
m=bpy.data.materials.new('MezzanineGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.39,.42,.3);b.inputs['Alpha'].default_value=.3;mats['glass']=m
# The structural plate comes from the existing compiler. These profiles and guards follow it.
edge=D['rail_boundary'];segments=[]
for a,b in zip(edge,edge[1:]+edge[:1]):
 if abs(a[0]-b[0])<.001 and abs(a[0]-16.51)<.02:
  lo,hi=sorted([a[1],b[1]])
  if lo<203.58:segments.append(([a[0],lo],[a[0],min(hi,203.58)]))
  if hi>206.42:segments.append(([a[0],max(lo,206.42)],[a[0],hi]))
 elif abs(a[0]-b[0])<.001 and abs(a[0]-20.21)<.02:
  lo,hi=sorted([a[1],b[1]])
  if lo<190.8:segments.append(([a[0],lo],[a[0],min(hi,190.8)]))
  if hi>193.2:segments.append(([a[0],max(lo,193.2)],[a[0],hi]))
 else:segments.append((a,b))
for i,(a,b)in enumerate(segments):
 if Vector(a).lerp(Vector(b),.5).length<.001:continue
 wall('MEZ_ProfiledEdge_'+str(i),a,b,64.27,64.50,.22,'ivory_enamel')
 wall('MEZ_GuardPlinth_'+str(i),a,b,64.5,64.74,.22,'warm_walnut')
 wall('MEZ_GuardGlass_'+str(i),a,b,64.74,65.58,.024,'glass')
 wall('MEZ_GuardCap_'+str(i),a,b,65.58,65.67,.09,'champagne_metal')
# Authored crosswise flight and sealed structural wedge, leaving the x18 route beneath the landing.
x0,x1=D['stair']['x'];z0,z1=D['stair']['z'];rise=3.5/18
for i in range(18):
 slab('MEZ_Step_'+str(i),x0+i*.3,x0+(i+1)*.3,z0+.22,z1-.22,61+i*rise,61+(i+1)*rise,'warm_stone')
v=[xyz(x,y,z)for z in [z0,z1]for x,y in [(x0,61),(x1,61),(x1,64.5),(x1-.3,64.5)]]
mesh('MEZ_StairCarcass',v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_stone')
for sign,z in [(-1,z0+.11),(1,z1-.11)]:
 beam('MEZ_StairHandrail_'+str(sign),[xyz(x0,62.17,z),xyz(x1,65.67,z)],.09,.09,'champagne_metal')
 v=[xyz(x,y,z+dz)for dz in [-.012,.012]for x,y in [(x0,61.18),(x1,64.68),(x1,65.58),(x0,62.08)]]
 mesh('MEZ_StairGlass_'+str(sign),v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'glass')
 # Explicit return closes the tiny transition to the landing perimeter.
 end=(16.51,203.58)if sign<0 else(16.51,206.31)
 wall('MEZ_StairReturnGlass_'+str(sign),(x1,z),end,64.68,65.58,.024,'glass');wall('MEZ_StairReturnCap_'+str(sign),(x1,z),end,65.58,65.67,.09,'champagne_metal')
# Slender fitted piers respect the reviewed lower seats and routes. No bearing is put in the old stair hole.
for i,(x,z)in enumerate(D['piers_xz']):
 cx,cy=xy((x,z));profile=[(.22,0),(.22,.12),(.16,.22),(.16,2.72),(.22,2.90),(.34,3.13),(.34,3.22)];n=12
 v=[(cx+radius*math.cos(2*math.pi*j/n),cy+radius*math.sin(2*math.pi*j/n),h)for radius,h in profile for j in range(n)];f=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j)for k in range(len(profile)-1)for j in range(n)];mesh('MEZ_ProfiledPier_'+str(i),v,f,'ivory_enamel')
 datum('pier_foot_'+str(i),(cx,cy,0))
# Edge girders remain within the plate depth over the protected lower passage.
for i,(a,b)in enumerate([((26.5,182.7),(53.5,182.7)),((28,195.2),(50,197.55)),((16.35,202),(16.4,205.8)),((16.35,202),(20.8,196.5))]):wall('MEZ_VisibleEdgeGirder_'+str(i),a,b,64.22,64.43,.24,'warm_walnut')
# Fitted two-stop shaft retains the tested cabin dimensions and a closed within-slab pit.
for side in [-1,1]:wall('MEZ_LiftShaftSide_'+str(side),(20.32,192+side*2.10),(24.26,192+side*2.10),60.76,67.85,.12,'ivory_enamel')
wall('MEZ_LiftShaftRear',(24.26,189.9),(24.26,194.1),60.76,67.85,.12,'ivory_enamel')
for lo,hi in [(63.86,64.5),(67.36,67.85)]:wall('MEZ_LiftFrontSpandrel_'+str(lo),(20.4,189.96),(20.4,194.04),lo,hi,.12,'ivory_enamel')
slab('MEZ_LiftPitPan',20.48,24.12,189.98,194.02,60.76,60.8,'warm_stone')
slab('MEZ_LiftClosedCap',20.32,24.32,189.84,194.16,67.73,67.85,'ivory_enamel')
for level in [61,64.5]:
 for side in [-1,1]:wall('MEZ_LiftCollar_'+str(level)+str(side),(20.32,192+side*2.1),(24.26,192+side*2.1),level+3.1,level+3.22,.12,'champagne_metal')
 slab('MEZ_LiftHeader_'+str(level),20.325,20.41,190.15,193.85,level+2.93,level+3.05,'warm_walnut')
# Paired lower and upper dining light fields belong to actual ceiling surfaces.
for index,(x,z,level)in enumerate([(x,z,y)for y in [61,64.5]for x,z in [(29.3,186.8),(40.1,186.8),(34.7,192.6),(45.5,192.6)]]):
 h=63.93 if level==61 else 67.10;mount=64.22 if level==61 else 67.4;cx,cy=xy((x,z));q=[(cx+.25*math.cos(2*math.pi*j/16),cy+.25*math.sin(2*math.pi*j/16))for j in range(16)]
 extrusion('MEZ_FixtureBody_'+str(index),q,h-61,h-61+.14,'champagne_metal');extrusion('MEZ_FixtureLens_'+str(index),q,h-61-.02,h-61,'lens');beam('MEZ_FixtureMount_'+str(index),[(cx,cy,h-61+.14),(cx,cy,mount-61)],.045,.045,'champagne_metal');datum('light_'+str(index),(cx,cy,h-61-.04))
datum('lower_stair_approach',xyz(9.8,61,205));datum('upper_stair_arrival',xyz(17.6,64.5,205));datum('lower_lift_stage',xyz(18.25,61,192));datum('upper_lift_stage',xyz(18.25,64.5,192))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Vesper upper dining and crosswise local circulation architecture','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Authored in verified allocation; runtime stair, headroom, guard, loaded lift and seating acceptance pending; no structural-load certification'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
