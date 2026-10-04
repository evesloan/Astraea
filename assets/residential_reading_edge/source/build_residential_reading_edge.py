"""Original sheltered residential reading edge, with shaped writing surfaces and integrated shelving."""
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



AID='AST-RES-002'
assert all(a['catalogue_id']!=AID or a['family']=='residential_reading_edge' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x,-z,y)
def box(name,x0,x1,y0,y1,z0,z1,role):
 v=[xyz(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
box('READ_Back',0,6.4,0,3.32,-.15,-.03,'ivory_enamel')
# Continuous rolled portal makes the ceiling and end supports one spatial frame.
profile=[(-.03,0),(-.42,0),(-.42,.28),(-.28,2.60),(-.42,2.83),(-.73,3.02),(-1.65,3.10),(-1.65,3.30),(-.03,3.32)]
for i,x in enumerate([.16,6.24]):
 n=len(profile);v=[xyz(x+dx,y,z)for dx in [-.16,.16]for z,y in profile]
 mesh('READ_RolledPortal_'+str(i),v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)],'warm_walnut')
box('READ_Canopy',.32,6.08,3.10,3.30,-1.65,-.15,'warm_walnut')
box('READ_AcousticSoffit',.42,5.98,3.075,3.10,-1.55,-.25,'oatmeal_weave')
# Two staggered writing stations, with genuine open knee spaces and a shared shelf.
for i,(x,y)in enumerate([(1.50,.75),(4.65,.78)]):
 outline=[(x-.91,.32),(x+.91,.32),(x+.91,1.05),(x+.70,1.30),(x+.25,1.38),(x-.68,1.24),(x-.91,1.03)]
 extrusion('READ_Desk_'+str(i),outline,y-.07,y,'warm_walnut')
 for side in [-1,1]:box('READ_DeskBearing_%s_%s'%(i,side),x+side*.80-.065,x+side*.80+.065,0,y-.07,-1.05,-.45,'champagne_metal')
 box('READ_TextileBack_'+str(i),x-.95,x+.95,.9,2.50,-.21,-.15,'teal_weave')
 datum('chair_'+str(i),xyz(x,0,-2.02));datum('approach_'+str(i),xyz(x,0,-2.90));datum('work_surface_'+str(i),xyz(x,y,-.82))
 box('READ_TaskHousing_'+str(i),x-.24,x+.24,2.80,3.075,-.98,-.58,'champagne_metal')
 box('READ_TaskLens_'+str(i),x-.20,x+.20,2.78,2.80,-.94,-.62,'lens')
 datum('light_'+str(i),xyz(x,2.75,-.78))
 box('READ_SwitchPlinth_'+str(i),x+.61,x+.79,y,y+.035,-1.04,-.86,'champagne_metal')
 box('READ_SwitchCap_'+str(i),x+.665,x+.735,y+.035,y+.055,-.985,-.915,'ivory_enamel')
 datum('toggle_'+str(i),xyz(x+.70,y+.068,-.95))
# A central book spine separates activities without hiding the court beyond.
box('READ_ShelfBack',2.66,3.55,.12,2.65,-.40,-.24,'warm_walnut')
for x in [2.66,3.49]:box('READ_ShelfSide_'+str(x),x,x+.06,.12,2.65,-.72,-.24,'warm_walnut')
for i,y in enumerate([.18,.66,1.14,1.62,2.10,2.59]):
 box('READ_Shelf_'+str(i),2.72,3.49,y-.05,y,-.72,-.24,'warm_walnut')
 if i<5:datum('shelf_'+str(i),xyz(3.105,y,-.50))
# Shared book/folio ledges sit beside, rather than in, the writing area.
box('READ_LowReturn',.34,.48,0,.76,-1.25,-.20,'warm_walnut')
box('READ_LowReturnOther',5.92,6.06,0,.79,-1.25,-.20,'warm_walnut')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Sheltered residential writing and shared book edge','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original authored reading edge; runtime placement, seating access and art review pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
