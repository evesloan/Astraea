"""Original Vesper dining furniture, profiled for fitted table groups."""
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


def rings(name,rows,role,n=24,cap_top=True):
 v=[(cx+rx*math.cos(2*math.pi*i/n),cy+ry*math.sin(2*math.pi*i/n),h)for cx,cy,rx,ry,h in rows for i in range(n)]
 f=[tuple(reversed(range(n)))]+([tuple(range((len(rows)-1)*n,len(rows)*n))]if cap_top else[])+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for j in range(len(rows)-1)for i in range(n)]
 return mesh(name,v,f,role)
AID='AST-DIN-007'
assert all(a['catalogue_id']!=AID or a['family']=='orchard_communal_table'for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
for cx in [-1.65,1.65]:
 rings('ORCH_TablePedestal_'+str(cx),[(cx,0,.42,.32,0),(cx,0,.44,.34,.035),(cx,0,.35,.25,.09),(cx,0,.14,.12,.17),(cx,0,.11,.105,.52),(cx,0,.23,.18,.66),(cx,0,.42,.29,.725)],'warm_walnut',16)
 rings('ORCH_FootBand_'+str(cx),[(cx,0,.44,.34,.03),(cx,0,.44,.34,.045)],'champagne_metal',16)
beam('ORCH_LowStretcher',[(-1.65,0,.28),(-.8,0,.23),(.8,0,.23),(1.65,0,.28)],.09,.11,'warm_walnut')
def outline(rx,ry,r):
 out=[]
 for cx,cy,start in [(rx-r,ry-r,0),(-rx+r,ry-r,90),(-rx+r,-ry+r,180),(rx-r,-ry+r,270)]:
  for i in range(5):
   a=math.radians(start+i*22.5);out.append((cx+r*math.cos(a),cy+r*math.sin(a)))
 return out
profiles=[(2.71,.76,.22,.725),(2.75,.80,.26,.744),(2.75,.80,.26,.773),(2.72,.77,.23,.79)]
v=[(x,y,h)for rx,ry,r,h in profiles for x,y in outline(rx,ry,r)];n=20
f=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for j in range(3)for i in range(n)]
mesh('ORCH_ProfiledCommunalRim',v,f,'warm_walnut')
outer=outline(2.72,.77,.23);inner=outline(2.67,.72,.20)
mesh('ORCH_TopInlay',[(x,y,.79)for x,y in outer+inner],[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'warm_walnut')
extrusion('ORCH_InsetStoneSurface',inner,.779,.787,'warm_stone')
for i,x in enumerate([-2.1,-1.05,0,1.05,2.1]):
 datum('seat_anchor_'+str(i),(x,-1.15,0));datum('seat_anchor_'+str(i+5),(x,1.15,0))
datum('table_surface',(0,0,.79));datum('floor_contact',(0,0,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Orchard long communal table with profiled soft corners and paired pedestals','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'candidate_seat_anchors':10,'status':'Original editable communal table; fitted seating, roundtrip and art checks pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
