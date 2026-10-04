"""Original court-facing conversation edge with a swept shelter, integrated planting and flush finish."""
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



AID='AST-RES-003'
assert all(a['catalogue_id']!=AID or a['family']=='residential_conversation_edge' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x,-z,y)
def box(name,x0,x1,y0,y1,z0,z1,role):
 v=[xyz(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
# A lower central back supports quiet conversation, while full-height ends carry
# the returning overhead form. The court-facing side remains broadly open.
back=[(.12,.08),(.65,.16),(1.45,.26),(4.75,.26),(5.55,.16),(6.08,.08)]
for i,((xa,za),(xb,zb))in enumerate(zip(back,back[1:])):
 h=2.45 if i in [1,2,3] else 2.05
 outline=[(xa,za),(xb,zb),(xb,zb+.12),(xa,za+.12)]
 extrusion('TALK_FacetedBack_'+str(i),outline,0,h,'oatmeal_weave')
 extrusion('TALK_BackDado_'+str(i),outline,0,.72,'warm_walnut')
# Tapered end bearings and shallow curved canopy section frame the inward view.
for i,x in enumerate([.12,6.08]):
 profile=[(-.08,0),(-.65,0),(-.48,2.62),(-.90,2.94),(-2.55,3.08),(-2.55,3.25),(-.08,3.35)]
 n=len(profile);v=[xyz(x+dx,y,z)for dx in [-.12,.12]for z,y in profile]
 mesh('TALK_EndBearing_'+str(i),v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)],'ivory_enamel')
outline=[(.24,.10),(5.96,.10),(5.96,2.48),(5.48,2.76),(4.6,2.92),(1.6,2.92),(.72,2.76),(.24,2.48)]
extrusion('TALK_SweptCanopy',outline,3.08,3.25,'warm_walnut')
extrusion('TALK_SoftSoffit',[(x,depth-.03)for x,depth in outline],3.055,3.08,'oatmeal_weave')
# A thin visible floor treatment owns no collision; the existing deck remains sole support.
floor=[(.03,.03),(6.17,.03),(6.17,2.55),(5.65,3.0),(.55,3.0),(.03,2.55)]
extrusion('TALK_VisualFloor',floor,.002,.008,'warm_walnut')
for i,x in enumerate([.65,5.55]):
 outline=[(x-.27,.32),(x+.27,.32),(x+.33,.82),(x+.18,1.0),(x-.18,1.0),(x-.33,.82)]
 extrusion('TALK_PlantedEnd_'+str(i),outline,0,.58,'warm_stone')
 extrusion('TALK_Soil_'+str(i),[(x-.20,.42),(x+.20,.42),(x+.25,.80),(x-.25,.80)],.57,.59,'botanical_soil')
 datum('plant_'+str(i),xyz(x,.59,-.63))
for i,x in enumerate([1.55,4.65]):
 datum('chair_'+str(i),xyz(x,0,-1.0))
 box('TALK_LampHousing_'+str(i),x-.26,x+.26,2.93,3.055,-1.58,-1.18,'champagne_metal')
 box('TALK_LampLens_'+str(i),x-.22,x+.22,2.915,2.93,-1.54,-1.22,'lens')
 datum('light_'+str(i),xyz(x,2.89,-1.38))
datum('table',xyz(3.10,0,-2.0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Court-facing sheltered conversation and planted edge','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Original fitted shelter; runtime access and art review pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
