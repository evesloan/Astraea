"""Original wide telescoping lift gate with two real depth channels per side."""
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

CLEAR_WIDTH=2.4
CLEAR_HEIGHT=2.65
leaf_roots=[];leaf_specs=[]
glass=bpy.data.materials.new('LiftGateTintedGlass');glass.use_nodes=True;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.25,.46,.49,.38);bs.inputs['Alpha'].default_value=.38;bs.inputs['Roughness'].default_value=.3;mats['glass']=glass
# Two panel ranks gather inside genuine hollow pockets; skins never cross travel.
for side in [-1,1]:
 a,b=sorted([side*1.20,side*1.90])
 for face,(y0,y1)in enumerate([(-.095,-.075),(.060,.085)]):
  extrusion('LIFT_PocketSkin_%d_%d'%(side,face),[(a,y0),(b,y0),(b,y1),(a,y1)],0,CLEAR_HEIGHT,'ivory_enamel')
 x=side*1.89
 extrusion('LIFT_PocketEnd_'+str(side),[(x-.01,-.095),(x+.01,-.095),(x+.01,.085),(x-.01,.085)],0,CLEAR_HEIGHT+.16,'champagne_metal')
 extrusion('LIFT_PocketBase_'+str(side),[(a,-.095),(b,-.095),(b,.085),(a,.085)],0,.020,'champagne_metal')
extrusion('LIFT_Header',[(-1.92,-.105),(1.92,-.105),(1.92,.095),(-1.92,.095)],CLEAR_HEIGHT,CLEAR_HEIGHT+.20,'warm_walnut')
for side,label in [(-1,'LEFT'),(1,'RIGHT')]:
 for rank in ['INNER','OUTER']:
  width=.595 if rank=='INNER'else .615
  x=side*(.30 if rank=='INNER'else .90)
  y=-.030 if rank=='INNER'else .025
  root=bpy.data.objects.new('LEAF_'+label+'_'+rank,None);bpy.context.collection.objects.link(root);root.location=(x,y,0);leaf_roots.append(root)
  start=len(parts)
  # Actual glazed opening within a framed moving panel, not glass over solid paint.
  w=width/2
  for a,b in [(-w,-.20),(.20,w)]:extrusion('LIFT_LeafStile_'+label+rank+str(a),[(a,-.008),(b,-.008),(b,.008),(a,.008)],.03,CLEAR_HEIGHT-.02,'ivory_enamel')
  for lo,hi in [(.03,.70),(2.16,CLEAR_HEIGHT-.02)]:extrusion('LIFT_LeafRail_'+label+rank+str(lo),[(-.20,-.008),(.20,-.008),(.20,.008),(-.20,.008)],lo,hi,'ivory_enamel')
  extrusion('LIFT_MovingGlass_'+label+rank,[(-.199,-.005),(.199,-.005),(.199,.005),(-.199,.005)],.70,2.16,'glass')
  for z in [.67,2.16]:extrusion('LIFT_GlassBead_'+label+rank+str(z),[(-.205,-.012),(.205,-.012),(.205,-.008),(-.205,-.008)],z,z+.03,'champagne_metal')
  if side<0 and rank=='INNER':extrusion('LIFT_MeetingSeal',[(.2875,-.026),(.3275,-.026),(.3275,-.017),(.2875,-.017)],.03,CLEAR_HEIGHT-.02,'champagne_metal')
  for o in parts[start:]:o.parent=root
  leaf_specs.append({'node':root.name,'width_m':width,'height_m':CLEAR_HEIGHT-.05,'center_y_m':(CLEAR_HEIGHT+.01)/2,'travel_x_m':side*(1.21 if rank=='INNER'else .61),'closed_source_xyz_m':[x,y,0],'meeting_seal':side<0 and rank=='INNER'})
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-DOR-003.blend';export=ROOT/'exports/AST-DOR-003.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for parent in [None]+leaf_roots:
 for role,material in mats.items():
  selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH'and o.parent==parent and o.data.materials and o.data.materials[0]==material]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='LIFT_'+('moving_'if parent else 'fixed_')+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-DOR-003.manifest.json').write_text(json.dumps({'catalogue_id':'AST-DOR-003','name':'Wide glazed telescoping lift gate','source':'source/AST-DOR-003.blend','export':'exports/AST-DOR-003.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'clear_opening_m':CLEAR_WIDTH,'clear_height_m':CLEAR_HEIGHT,'leaf_specs':leaf_specs,'status':'Authored source; motion, controller and architectural integration checks pending'},indent=2)+'\n')
