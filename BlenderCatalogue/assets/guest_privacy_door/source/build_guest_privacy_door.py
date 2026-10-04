"""Original D06 garden overlook: sheltered back, rising roof and open court-facing edge."""
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

# Single guest wet-room leaf with honest jamb/reveal clearance and an
# editable hinge. This is opaque privacy joinery, not a recoloured staff door.
for side in [-1,1]:
 x=side*.565
 extrusion('BATH_Jamb_'+str(side),[(x-.025,-.075),(x+.025,-.075),(x+.025,.075),(x-.025,.075)],0,2.28,'warm_walnut')
extrusion('BATH_Header',[(-.59,-.075),(.59,-.075),(.59,.075),(-.59,.075)],2.18,2.28,'warm_walnut')
# The hinge barrel lies beyond the jamb face, so the open leaf does not
# rotate through its own frame. Recessed stops mask the side light gaps.
for side in [-1,1]:
 x=side*.52
 extrusion('BATH_RecessedStop_'+str(side),[(x-.02,.035),(x+.02,.035),(x+.02,.055),(x-.02,.055)],.025,2.18,'warm_walnut')
hinge=bpy.data.objects.new('HINGE_LEFT',None);bpy.context.collection.objects.link(hinge);hinge.location=(-.528,.085,0)
def panel(name,outline,y0,y1,role):
 n=len(outline);o=mesh(name,[(x,y,z)for y in [y0,y1]for x,z in outline],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role);o.parent=hinge;return o
outline=[(.052,.025),(.998,.025),(1.038,.065),(1.038,2.11),(.998,2.15),(.052,2.15),(.012,2.11),(.012,.065)]
panel('BATH_LeafFrame',outline,-.025,.025,'warm_walnut')
inner=[(.13,.17),(.90,.17),(.95,.22),(.95,1.97),(.90,2.03),(.13,2.03),(.09,1.97),(.09,.22)]
for side in [-1,1]:
 panel('BATH_OpaqueInset_'+str(side),inner,side*.026-.004,side*.026+.004,'ivory_enamel')
 panel('BATH_HandleBackplate_'+str(side),[(.865,.99),(.94,.99),(.94,1.20),(.865,1.20)],side*.039-.012,side*.039+.012,'champagne_metal')
 panel('BATH_Lever_'+str(side),[(.85,1.055),(.985,1.055),(1.005,1.075),(.985,1.098),(.85,1.098)],side*.061-.012,side*.061+.012,'champagne_metal')
 o=bpy.data.objects.new('POINT_handle_'+str(side),None);bpy.context.collection.objects.link(o);o.parent=hinge;o.location=(.93,side*.079,1.08)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source/AST-DOR-001.blend';export=ROOT/'exports/AST-DOR-001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Batch within a rig parent only. Never merge the moving leaf into the frame.
for parent in [None,hinge]:
 for role,material in mats.items():
  selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH' and o.parent==parent and o.data.materials and o.data.materials[0]==material]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name=('BATH_Leaf_' if parent else 'BATH_Static_')+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
manifest={'catalogue_id':'AST-DOR-001','name':'Single opaque guest privacy door','source':'source/AST-DOR-001.blend','export':'exports/AST-DOR-001.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'hinge':'HINGE_LEFT','leaf_contact_godot':{'size':[1.026,2.125,.05],'center':[.525,1.0875,0]},'handle_contacts_godot':[{'size':[.17,.23,.035],'center':[.925,1.10,z]}for z in [-.060,.060]],'status':'Authored component; shared controller integration and full motion-clearance tests pending'}
(ROOT/'AST-DOR-001.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('GUEST_PRIVACY_DOOR_AUTHORED',tri)
