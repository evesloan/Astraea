"""Original Vesper upper dining, crosswise stair and fitted local lift architecture."""
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



AID='AST-DIN-006'
def lathe(name,profile,x,z,n,role):
 v=[(x+r*math.cos(2*math.pi*j/n),-z+r*math.sin(2*math.pi*j/n),h)for r,h in profile for j in range(n)]
 f=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j)for k in range(len(profile)-1)for j in range(n)]
 return mesh(name,v,f,role)
lathe('DIN_ShallowRimPlate',[(0,0),(.13,0),(.155,.009),(.17,.024),(.162,.028),(.13,.013),(0,.009)],0,0,24,'ivory_enamel')
lathe('DIN_OpenGuestCup',[(0,0),(.045,0),(.055,.006),(.060,.11),(.058,.12),(.048,.12),(.05,.11),(.038,.015),(0,.015)],-.20,.14,16,'ivory_enamel')
# Folded cloth has a shaped fold rather than a flat texture decal.
v=[(.15,-.10,0),(.25,-.10,0),(.25,.10,0),(.15,.10,0),(.15,-.10,.008),(.25,-.10,.008),(.25,.10,.008),(.15,.10,.008),(.20,-.10,.022),(.20,.10,.022)]
mesh('DIN_FoldedNapkin',v,[(3,2,1,0),(0,1,5,8,4),(3,7,9,6,2),(0,4,7,3),(1,2,6,5),(4,8,9,7),(8,5,6,9)],'teal_weave')
# Economical cutlery silhouette sits alongside the plate, on the napkin.
beam('DIN_CutleryHandle',[(.202,.07,.025),(.202,-.048,.025)],.012,.007,'champagne_metal')
lathe('DIN_SpoonBowl',[(0,0),(.016,0),(.022,.005),(.020,.008),(0,.004)],.202,.069,12,'champagne_metal').location.z=.023
# Source support points are used to verify all placements against actual tabletops.
for i,(x,z)in enumerate([(0,0),(.13,0),(-.13,0),(0,.13),(0,-.13),(-.20,.14),(.15,-.10),(.25,-.10),(.25,.10),(.15,.10)]):datum('support_'+str(i),(x,-z,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
for o in parts:o.data.calc_loop_triangles()
triangles=sum(len(o.data.loop_triangles)for o in parts)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Vesper rimmed plate, open cup and folded-cloth setting','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':triangles,'status':'Original editable static table setting; contact and visual review pending. No pickup/food simulation claim.'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
