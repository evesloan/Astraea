"""Authored2.4m-clear derivative of the existing paired sliding guest door; unchanged hollow-pocket principle."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
assert any(a['catalogue_id']=='AST-DOR-002' and a['family']=='guest_entry_door' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
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

# Enclosed surface-mounted pockets sit on the street side of the existing
# wall. The leaves travel in actual empty cavities, never through solid walls.
for side in [-1,1]:
 a,b=sorted([side*1.20,side*2.56])
 for face,(y0,y1)in enumerate([(-.11,-.055),(.055,.11)]):
  extrusion('ENTRY_PocketSkin_%d_%d'%(side,face),[(a,y0),(b,y0),(b,y1),(a,y1)],.025,2.50,'ivory_enamel')
 x=side*2.54
 extrusion('ENTRY_ClosedPocketEnd_'+str(side),[(x-.02,-.11),(x+.02,-.11),(x+.02,.11),(x-.02,.11)],0,2.64,'warm_walnut')
 extrusion('ENTRY_PocketBase_'+str(side),[(a,-.11),(b,-.11),(b,.11),(a,.11)],0,.025,'champagne_metal')
 # Long narrow trim describes a finished casing without filling its cavity.
 extrusion('ENTRY_FrontTrim_'+str(side),[(a,-.13),(b,-.13),(b,-.11),(a,-.11)],2.32,2.50,'warm_walnut')
extrusion('ENTRY_Header',[(-2.58,-.13),(2.58,-.13),(2.58,.13),(-2.58,.13)],2.50,2.66,'warm_walnut')
leaves=[]
for side,label in [(-1,'LEFT'),(1,'RIGHT')]:
 root=bpy.data.objects.new('LEAF_'+label,None);bpy.context.collection.objects.link(root);root.location=(side*.60,0,0);leaves.append(root)
 outline=[(-.55,.035),(.55,.035),(.59,.075),(.59,2.445),(.55,2.485),(-.55,2.485),(-.59,2.445),(-.59,.075)];n=len(outline)
 o=mesh('ENTRY_MovingPanel_'+label,[(x,y,z)for y in [-.025,.025]for x,z in outline],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'ivory_enamel');o.parent=root
 for face in [-1,1]:
  o=extrusion('ENTRY_TimberInset_%s_%d'%(label,face),[(-.50,face*.028-.002),(.50,face*.028-.002),(.50,face*.028+.002),(-.50,face*.028+.002)],.22,2.25,'warm_walnut');o.parent=root
 if side<0:
  o=extrusion('ENTRY_OverlappingMeetingSeal',[(.582,-.045),(.622,-.045),(.622,-.030),(.582,-.030)],.035,2.485,'champagne_metal');o.parent=root
# A physical call plate, rather than another UI interaction system.
extrusion('ENTRY_CallPlate',[(-2.50,-.165),(-2.28,-.165),(-2.28,-.13),(-2.50,-.13)],1.02,1.42,'champagne_metal')
extrusion('ENTRY_CallLens',[(-2.46,-.175),(-2.32,-.175),(-2.32,-.165),(-2.46,-.165)],1.12,1.30,'lens')
datum('call_button',(-2.39,-.18,1.21))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-DOR-002_wide.blend';export=ROOT/'exports/AST-DOR-002_wide.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for parent in [None]+leaves:
 for role,material in mats.items():
  selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH'and o.parent==parent and o.data.materials and o.data.materials[0]==material]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='ENTRY_'+('moving_'if parent else 'fixed_')+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-DOR-002_wide.manifest.json').write_text(json.dumps({'catalogue_id':'AST-DOR-002','name':'Wide enclosed paired sliding guest entry','source':'source/AST-DOR-002_wide.blend','export':'exports/AST-DOR-002_wide.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'variant':'wide240','travel_m':1.24,'leaf_width_m':1.18,'clear_opening_m':2.40,'status':'Actual hollow pocket geometry; runtime clipping and interaction checks pending'},indent=2)+'\n');print('GUEST_ENTRY_AUTHORED',tri)
