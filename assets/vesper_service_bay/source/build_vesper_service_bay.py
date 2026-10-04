"""Original Vesper finishing bay with distinct clean and dirty service faces."""
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


AID='AST-DIN-003'
def wall(name,a,b,z0,z1,width,role):
 a=Vector((a[0],-a[1]));b=Vector((b[0],-b[1]));v=(b-a).normalized();n=Vector((-v.y,v.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],z0,z1,role)
outline=[(0,.35),(.35,0),(4.05,0),(4.4,.35),(4.4,7.45),(4.05,7.8),(.35,7.8),(0,7.45)]
for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):
 if a[0]==b[0]==0:continue
 wall('DIN_ServiceShell_'+str(i),a,b,0,3.3,.14,'ivory_enamel')
 wall('DIN_ServiceSkirting_'+str(i),a,b,.02,.20,.17,'warm_stone')
# The west frontage has actual pass-throughs, not a label pasted on a wall.
for a,b in [(.35,.5),(2.1,2.6),(5.4,5.6),(7.1,7.45)]:wall('DIN_ServiceWestPier_'+str(a),(0,a),(0,b),0,3.3,.18,'ivory_enamel')
for a,b in [(.5,2.1),(5.6,7.1)]:
 wall('DIN_ServiceWindowBase_'+str(a),(0,a),(0,b),0,.92,.18,'warm_walnut')
 wall('DIN_ServiceWindowHeader_'+str(a),(0,a),(0,b),2.15,3.3,.18,'ivory_enamel')
 q=[(-.07,-a),(.66,-a),(.66,-b),(-.07,-b)];extrusion('DIN_ServiceLanding_'+str(a),q,.88,.92,'warm_stone')
 wall('DIN_ServiceLandingLip_'+str(a),(-.07,a),(-.07,b),.90,.95,.05,'champagne_metal')
# Existing framed service doors own the2.8m-wide opening at local Z2.6..5.4.
wall('DIN_DoorHeader',(0,2.6),(0,5.4),2.83,3.3,.18,'ivory_enamel')
# Supported ceiling varies in profile while keeping the central working aisle clear.
q=[(x,-z)for x,z in outline];extrusion('DIN_ServiceCeiling',q,3.3,3.48,'ivory_enamel')
for a,b in zip(outline,outline[1:]+outline[:1]):wall('DIN_ServiceCeilingReveal',a,b,3.20,3.3,.12,'warm_walnut')
# A clean washable inset and coordinated edging distinguish the staff work surface.
q=[(.32,-.3),(4.02,-.3),(4.08,-7.45),(.32,-7.45)];extrusion('DIN_VisualFloor_ServiceInset',q,.003,.008,'warm_stone')
for i,z in enumerate([2.25,5.65]):
 x=2.9;y=-z;h=3.12;q=[(x+.22*math.cos(2*math.pi*j/16),y+.22*math.sin(2*math.pi*j/16))for j in range(16)]
 extrusion('DIN_ServiceFixtureBody_'+str(i),q,h,h+.12,'champagne_metal');extrusion('DIN_ServiceFixtureLens_'+str(i),q,h-.025,h,'lens');datum('light_'+str(i),(x,y,h-.05))
 beam('DIN_ServiceFixtureMount_'+str(i),[(x,y,h+.12),(x,y,3.3)],.05,.05,'champagne_metal')
for i,z in enumerate([3,5.6]):datum('counter_'+str(i),(3.88,-z,0))
datum('credenza',(3.88,-6.85,0));datum('dish_return',(1.11,-6.5,0));datum('door',(0,-4,0));datum('clean_landing',(.35,-1.3,.92));datum('dirty_landing',(.35,-6.35,.92))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Vesper clean and dirty finishing-service bay','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable fitted service bay; runtime access, moving-door, support, optical and visual checks pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
