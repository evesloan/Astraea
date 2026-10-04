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



AID='AST-RES-001'
registered=json.loads((CAT/'catalogue_manifest.json').read_text())['assets']
assert all(a['catalogue_id']!=AID or a['family']=='residential_wayfinding_bay' for a in registered),'Catalogue ID already belongs to another family'
def xyz(x,y,z):return(x,-z,y)
def box(name,x0,x1,y0,y1,z0,z1,role):
 v=[xyz(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
box('RES_SolidBack',0,5.4,0,3.55,-.15,-.03,'ivory_enamel')
box('RES_StoneBase',0,5.4,0,.16,-.24,-.15,'warm_stone')
# Rolled side profiles join the overhead return to the floor.
profile=[(-.03,0),(-.35,0),(-.35,.28),(-.24,2.62),(-.30,2.88),(-.56,3.13),(-1.15,3.25),(-1.15,3.48),(-.03,3.55)]
for i,x in enumerate([.16,5.24]):
 n=len(profile);v=[xyz(x+dx,y,z)for dx in [-.16,.16]for z,y in profile]
 mesh('RES_RolledSide_'+str(i),v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)],'ivory_enamel')
box('RES_Canopy',.32,5.08,3.25,3.48,-1.15,-.15,'warm_walnut')
box('RES_AcousticCeiling',.42,4.98,3.23,3.25,-1.08,-.22,'oatmeal_weave')
# Two-place perch integrated into the bay, with useful approaches outside it.
box('RES_SeatFrame',1.20,4.20,.34,.43,-.95,-.24,'warm_walnut')
box('RES_SeatCushion',1.27,4.13,.43,.50,-.91,-.28,'clay_weave')
v=[xyz(x,y,z)for x in [1.23,4.17]for z,y in [(-.34,.50),(-.25,1.05),(-.14,1.05),(-.23,.50)]]
mesh('RES_SlopedBenchBack',v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'clay_weave')
for x in [1.43,3.97]:box('RES_BenchBearing_'+str(x),x-.10,x+.10,0,.34,-.78,-.35,'champagne_metal')
for x in [1.20,4.10]:box('RES_ReturnedArm_'+str(x),x,x+.10,.47,.66,-.92,-.25,'warm_walnut')
for i,x in enumerate([2.05,3.35]):
 datum('seat_'+str(i),xyz(x,.50,-.59));datum('approach_'+str(i),xyz(x,0,-1.42))
# Side plant plinths give the resting edge a living end without using the route.
for i,x in enumerate([.68,4.72]):
 box('RES_PlantPlinth_'+str(i),x-.24,x+.24,0,.56,-.86,-.38,'warm_stone')
 datum('plant_'+str(i),xyz(x,.56,-.62))
box('RES_MapFrame',1.14,4.26,1.23,2.68,-.23,-.15,'warm_walnut')
box('RES_MapBacking',1.24,4.16,1.33,2.58,-.245,-.23,'ivory_enamel')
datum('map_center',xyz(2.7,1.955,-.251))
for i,x in enumerate([1.45,3.95]):
 box('RES_FixtureHousing_'+str(i),x-.22,x+.22,3.10,3.23,-.79,-.43,'champagne_metal')
 box('RES_FixtureLens_'+str(i),x-.19,x+.19,3.085,3.10,-.76,-.46,'lens')
 datum('light_'+str(i),xyz(x,3.06,-.61))
# A flush material threshold marks the resting edge without adding a trip lip.
outline=[(.03,.03),(5.37,.03),(5.37,1.20),(5.10,1.70),(.30,1.70),(.03,1.20)]
extrusion('RES_VisualFloorBorder',outline,.001,.006,'champagne_metal')
inner=[(.10,.10),(5.30,.10),(5.30,1.18),(5.05,1.63),(.35,1.63),(.10,1.18)]
extrusion('RES_VisualFloorWalnut',inner,.006,.008,'warm_walnut')
for name in ['RES_SeatCushion','RES_SlopedBenchBack']:
 o=bpy.data.objects[name];modifier=o.modifiers.new('AuthoredSoftEdges','BEVEL');modifier.width=.018;modifier.segments=2
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
for o in parts:o.data.calc_loop_triangles()
triangles=sum(len(o.data.loop_triangles)for o in parts)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Residential resting bay with recessed local directory and planted ends','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':triangles,'status':'Original editable alcove for verified D13 street; runtime access and visual acceptance pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
