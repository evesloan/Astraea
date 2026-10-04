"""Fitted aquatic lift enclosure; editable source, closed pit and controlled landing apertures."""
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


D=json.loads((ROOT/'source/section_contract.json').read_text());AID='AST-CIR-004'
def xy(p):return(p[0]-12,235-p[1])
def wall(name,a,b,lo,hi,width,role):
 a=Vector(xy(a));b=Vector(xy(b));t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo-44,hi-44,role)
def slab(name,x0,x1,z0,z1,lo,hi,role):return extrusion(name,[xy(p)for p in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],lo-44,hi-44,role)
# The shaft is hollow. Contact follows each actual wall, never a enclosing hull.
for side in [-1,1]:wall('AQU_ShaftSide_'+str(side),(11.82,235+side*2.10),(15.76,235+side*2.10),43.76,64.35,.12,'ivory_enamel')
wall('AQU_ShaftRear',(15.76,232.90),(15.76,237.10),43.76,64.35,.12,'ivory_enamel')
for lo,hi in [(46.86,52.5),(55.36,61),(63.86,64.35)]:wall('AQU_FrontSpandrel_'+str(lo),(11.90,232.96),(11.90,237.04),lo,hi,.12,'ivory_enamel')
slab('AQU_PitPan',11.98,15.62,232.98,237.02,43.76,43.80,'warm_stone')
slab('AQU_ClosedCap',11.82,15.82,232.84,237.16,64.23,64.35,'ivory_enamel')
# Thin profiled collars make each stop readable without entering the approach or cabin sweep.
for level in D['floor_heights']:
 for side in [-1,1]:
  z=235+side*2.10
  wall('AQU_LevelCollar_%s_%s'%(level,side),(11.82,z),(15.76,z),level+3.10,level+3.22,.12,'champagne_metal')
 # Recessed header is entirely above the existing gate frame; its optical face points toward the forecourt.
 slab('AQU_LandingHeader_'+str(level),11.825,11.91,233.15,236.85,level+2.93,level+3.05,'warm_walnut')
 slab('AQU_HeaderLens_'+str(level),11.82,11.825,234.25,235.75,level+2.94,level+3.01,'lens')
 datum('arrival_light_'+str(level),(-.19,0,level-44+2.97))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role,m in mats.items():
 selected=[o for o in list(scene.objects)if o.type=='MESH' and o.data.materials and o.data.materials[0]==m]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='AQU_Lift_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Aquatic three-stop fitted lift enclosure','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable construction component; full sweep, landing contacts and visual review pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
