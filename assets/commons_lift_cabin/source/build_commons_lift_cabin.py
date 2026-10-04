"""Original Night garden: four planted resting courts, sheltered thresholds and atrium views."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys,argparse
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
args=argparse.ArgumentParser();args.add_argument('--stops',type=int,choices=[2,3],default=2);options=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);variant='AST-CIR-003' if options.stops==2 else 'AST-CIR-003_three_stop'
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

# Editable cabin fitted to a4m width x3.6m depth moving platform.
# BlenderX is door width; BlenderY points into cabin from its threshold.
outline=[(-2,0),(2,0),(2,3.25),(1.65,3.6),(-1.65,3.6),(-2,3.25)]
extrusion('CAB_Platform',outline,-.18,0,'warm_stone')
extrusion('CAB_Roof',outline,2.8,2.94,'ivory_enamel')
for side in [-1,1]:
 a,b=sorted([side*1.88,side*2])
 extrusion('CAB_Side_'+str(side),[(a,.14),(b,.14),(b,3.25),(a,3.25)],0,2.8,'ivory_enamel')
 extrusion('CAB_SeatBase_'+str(side),[(side*1.9,2.6),(side*1.4,2.6),(side*1.4,3.15),(side*1.9,3.15)],0,.42,'warm_walnut')
 extrusion('CAB_SeatPad_'+str(side),[(side*1.9,2.6),(side*1.4,2.6),(side*1.4,3.15),(side*1.9,3.15)],.42,.49,'teal_weave')
extrusion('CAB_RearPanel',[(-1.65,3.47),(1.65,3.47),(1.65,3.6),(-1.65,3.6)],0,2.8,'warm_walnut')
for side in [-1,1]:
 q=[(side*2,3.25),(side*1.65,3.6),(side*1.60,3.47),(side*1.88,3.19)]
 extrusion('CAB_FacetedRear_'+str(side),q,0,2.8,'ivory_enamel')
 for h in [.12,1.0,2.65]:extrusion('CAB_RearTrim_%s_%s'%(side,h),q,h,h+.055,'champagne_metal')
# Recessed backrest and handrail, inset light wells, non-flat tiled floor inlay.
extrusion('CAB_RecessedBackrest',[(-1.25,3.44),(1.25,3.44),(1.25,3.47),(-1.25,3.47)],.8,1.65,'oatmeal_weave')
for side in [-1,1]:
 x=side*1.70
 extrusion('CAB_CeilingWell_'+str(side),[(x-.11,.55),(x+.11,.55),(x+.11,2.9),(x-.11,2.9)],2.64,2.8,'warm_walnut')
 extrusion('CAB_OpalLens_'+str(side),[(x-.07,.65),(x+.07,.65),(x+.07,2.8),(x-.07,2.8)],2.63,2.64,'lens')
 datum('light_'+str(side),(x,1.7,2.60))
extrusion('CAB_FloorInlay',[(-1.20,.25),(1.20,.25),(1.20,2.90),(.85,3.2),(-.85,3.2),(-1.20,2.9)],.001,.004,'oatmeal_weave')
# Physical two-button panel on the right, separate controls in runtime.
if options.stops==2:
 extrusion('CAB_ControlPanel',[(1.75,.50),(1.88,.50),(1.88,.88),(1.75,.88)],.98,1.55,'champagne_metal')
 for i,h in enumerate([1.17,1.40]):datum('floor_button_'+str(i),(1.73,.69,h))
else:
 extrusion('CAB_ThreeStopControlPanel',[(1.75,.43),(1.88,.43),(1.88,1.25),(1.75,1.25)],1.10,1.56,'champagne_metal')
 for i,y in enumerate([.55,.84,1.13]):datum('floor_button_'+str(i),(1.73,y,1.27))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(variant+'.blend');export=ROOT/'exports'/(variant+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
for role,material in mats.items():
 selected=[o for o in list(scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='CAB_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/(variant+'.manifest.json')).write_text(json.dumps({'catalogue_id':'AST-CIR-003','name':'Starboard commons fitted lift cabin','source':'source/'+variant+'.blend','export':'exports/'+variant+'.glb','floor_button_count':options.stops,'representation':variant,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Authored draft; physics/controller integration pending'},indent=2)+'\n')
