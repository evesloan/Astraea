"""Original oval book-lined reading alcove with level entry and an integrated cushioned retreat."""
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



AID='AST-RES-004'
assert all(a['catalogue_id']!=AID or a['family']=='residential_quiet_alcove' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x,-z,y)
def box(name,x0,x1,y0,y1,z0,z1,role):
 v=[xyz(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
# The bottom of the oval is deliberately open: no raised sill blocks access.
angles=[math.radians(-125+250*i/24)for i in range(25)]
for i,(a,b)in enumerate(zip(angles,angles[1:])):
 for label,z0,z1,role in [('FrontRim',-.13,.08,'warm_walnut'),('Vault',-2.96,-.13,'oatmeal_weave')]:
  ring=[(1.75*math.sin(a),1.6+1.6*math.cos(a)),(1.75*math.sin(b),1.6+1.6*math.cos(b)),(1.50*math.sin(b),1.6+1.37*math.cos(b)),(1.50*math.sin(a),1.6+1.37*math.cos(a))]
  v=[xyz(x,y,z)for z in [z0,z1]for x,y in ring]
  mesh('QUIET_'+label+'_'+str(i),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
for side in [-1,1]:
 x=side*1.39
 box('QUIET_ContinuousBearing_'+str(side),x-.125,x+.125,0,.90,-2.98,.10,'warm_walnut')
 # Fitted horizontal shelf surfaces remain level despite the curved enclosure.
 for level,y in enumerate([.65,1.05,1.45,1.85]):
  x0,x1=(1.0,1.53)if side>0 else(-1.53,-1.0)
  box('QUIET_BookShelf_%s_%s'%(side,level),x0,x1,y-.045,y,-2.56,-.52,'warm_walnut')
  for row,z in enumerate([-1.05,-1.92]):datum('book_%s_%s_%s'%(side,level,row),xyz(side*(1.13 if level==0 else 1.20),y,z))
# An actual opaque back supports the upholstered seating rather than showing a void.
profile=[(-1.5,0)]+[(1.5*math.sin(math.radians(-90+180*i/18)),1.6+1.37*math.cos(math.radians(-90+180*i/18)))for i in range(19)]+[(1.5,0)]
n=len(profile);v=[xyz(x,y,z)for z in [-3.08,-2.96]for x,y in profile]
mesh('QUIET_Back',v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'teal_weave')
box('QUIET_SeatBase',-.99,.99,0,.43,-2.82,-1.70,'warm_walnut')
for i,x in enumerate([-.49,.49]):
 o=box('QUIET_SeatCushion_'+str(i),x-.475,x+.475,.43,.52,-2.72,-1.73,'oatmeal_weave')
 mod=o.modifiers.new('Soft authored cushion corners','BEVEL');mod.width=.035;mod.segments=2
 v=[xyz(xx,y,z)for xx in [x-.475,x+.475]for z,y in [(-2.66,.52),(-2.80,1.28),(-2.94,1.28),(-2.80,.52)]]
 o=mesh('QUIET_ReclinedBack_'+str(i),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
 mod=o.modifiers.new('Soft authored back corners','BEVEL');mod.width=.025;mod.segments=2
 datum('seat_'+str(i),xyz(x,.52,-2.15));datum('approach_'+str(i),xyz(x,0,-1.18))
# One softly crowned accent cushion rests on the left seat and leans into its back.
outline=[]
for cx,cy,start in [(.20,.23,0),(-.20,.23,90),(-.20,-.23,180),(.20,-.23,270)]:
 for k in range(4):
  a=math.radians(start+k*30);outline.append((cx+.10*math.cos(a),cy+.10*math.sin(a)))
v=[]
for scale,depth in [(.86,-.10),(1.0,0.0),(.90,.13)]:
 for x,h in outline:v.append(xyz(-.49+x*scale,.85+h*scale,-2.60-h*scale*.18+depth))
n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(layer*n+j,layer*n+(j+1)%n,(layer+1)*n+(j+1)%n,(layer+1)*n+j)for layer in range(2)for j in range(n)]
mesh('QUIET_CrownedAccentCushion',v,faces,'clay_weave')
for side in [-1,1]:box('QUIET_SeatArm_'+str(side),side*.94-.045,side*.94+.045,.49,.72,-2.65,-1.72,'warm_walnut')
box('QUIET_LampHousing',-.35,.35,2.77,2.92,-1.56,-1.10,'champagne_metal')
box('QUIET_LampLens',-.30,.30,2.745,2.77,-1.51,-1.15,'lens')
box('QUIET_LampMount',-.03,.03,2.92,2.98,-1.36,-1.30,'champagne_metal')
datum('light',xyz(0,2.72,-1.33))
box('QUIET_SwitchPlinth',.89,.985,.72,.75,-1.94,-1.78,'champagne_metal')
box('QUIET_SwitchCap',.914,.961,.75,.77,-1.897,-1.823,'ivory_enamel')
datum('toggle',xyz(.9375,.785,-1.86))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Level-entry oval book-lined reading alcove','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original authored quiet retreat; actual fit, access and art review pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
