"""Fitted aquatic balcony guard family with supported plinths and local soffit fixtures."""
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


D=json.loads((ROOT/'source/edge_contract.json').read_text());AID='AST-AQU-013'
m=bpy.data.materials.new('AquaticGuardGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.39,.42,.28);b.inputs['Alpha'].default_value=.28;mats['glass']=m
def xyz(x,y,z):return(x-8,182-z,y-44)
def wall(name,a,b,lo,hi,width,role):
 a=Vector((a[0]-8,182-a[1]));b=Vector((b[0]-8,182-b[1]));t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo-44,hi-44,role)
for deck in D['decks']:
 y=deck['floor_y'];ring=deck['boundary'];label=deck['deck']
 for i,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
  wall('AQU_'+label+'_Plinth_'+str(i),a,b,y-.35,y+.12,.22,'ivory_enamel')
  wall('AQU_'+label+'_BaseReveal_'+str(i),a,b,y+.12,y+.17,.13,'champagne_metal')
  wall('AQU_'+label+'_GlazedInfill_'+str(i),a,b,y+.17,y+1.10,.03,'glass')
  # A profiled six-sided top rail is one coherent construction detail.
  av=Vector(xyz(a[0],y,a[1]));bv=Vector(xyz(b[0],y,b[1]));t=(bv-av).normalized();side=Vector((-t.y,t.x,0));verts=[]
  for center in [av,bv]:
   for w,h in [(-.055,1.08),(-.055,1.125),(-.033,1.15),(.033,1.15),(.055,1.125),(.055,1.08)]:verts.append(tuple(center+side*w+Vector((0,0,h))))
  mesh('AQU_'+label+'_ProfiledRail_'+str(i),verts,[tuple(reversed(range(6))),tuple(range(6,12))]+[(j,(j+1)%6,(j+1)%6+6,j+6)for j in range(6)],'champagne_metal')
  count=max(1,math.ceil((bv-av).length/3))
  for j in range(count):
   p=av.lerp(bv,j/count);q=[(p.x+.045*math.cos(k*math.pi/4),p.y+.045*math.sin(k*math.pi/4))for k in range(8)];extrusion('AQU_'+label+'_Post_%s_%s'%(i,j),q,y-44+.1,y-44+1.10,'champagne_metal')
 for i,light in enumerate(deck['lights']):
  x,sy,z=light['source_xyz'];cx,cy=x-8,182-z;q=[(cx+.23*math.cos(j*math.pi/8),cy+.23*math.sin(j*math.pi/8))for j in range(16)]
  extrusion('AQU_'+label+'_SoffitHousing_'+str(i),q,y-44-.57,y-44-.38,'ivory_enamel')
  extrusion('AQU_'+label+'_SoffitLens_'+str(i),[(cx+(a-cx)*.86,cy+(b-cy)*.86)for a,b in q],y-44-.60,y-44-.57,'lens')
  datum(label+'_light_'+str(i),xyz(x,sy,z));rx,ry,rz=light['receiver_xyz'];datum(label+'_receiver_'+str(i),xyz(rx,ry,rz))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Separate terrace groups retain sensible culling rather than one ship-wide mesh.
for deck in D['decks']:
 for role,m in mats.items():
  selected=[o for o in list(scene.objects)if o.type=='MESH'and o.name.startswith('AQU_'+deck['deck']+'_')and o.data.materials and o.data.materials[0]==m]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='AQU_'+deck['deck']+'_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Aquatic profiled balcony guards and soffit fixtures','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable guard family; contacts, lower-level illumination and visual acceptance pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
