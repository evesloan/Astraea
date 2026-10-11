"""Editable low-poly basin surrounds and central planted island, fitted to D02."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1];plan=json.loads((ROOT/'source/garden_plan.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role,path in [('stone','warm_stone.png'),('ivory','ivory_enamel.png'),('metal','champagne_metal.png'),('wood','warm_walnut.png'),('soil','botanical/botanical_soil.png'),('tile','aquatic/aquatic_edge_tile.png')]:
 m=bpy.data.materials.new('Garden_'+role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.75
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('Garden_opal');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.98,.94,.8,1);b.inputs['Emission Color'].default_value=(1,.90,.70,1);b.inputs['Emission Strength'].default_value=1.5;mats['opal']=m
parts=[]
def mesh(name,v,f,role,uvs=None):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:
   vi=d.loops[li].vertex_index;q=d.vertices[vi].co;uv.data[li].uv=uvs[vi] if uvs else (q.x*.5,q.y*.5)
 return o
def sweep(name,points,profile,role):
 pts=[Vector(q) for q in points];v=[];uv=[];distance=0;n=len(profile)
 for i,p in enumerate(pts):
  a=(p-pts[i-1]).normalized();b=(pts[(i+1)%len(pts)]-p).normalized();normal=Vector((a.y+b.y,-a.x-b.x)).normalized();normal/=max(.5,normal.dot(Vector((b.y,-b.x))))
  if i:distance+=(p-pts[i-1]).length
  for offset,height in profile:
   q=p+normal*offset;v.append((q.x,-q.y,height));uv.append((distance*.5,(height+offset)*.5))
 f=[(i*n+j,i*n+(j+1)%n,((i+1)%len(pts))*n+(j+1)%n,((i+1)%len(pts))*n+j) for i in range(len(pts)) for j in range(n)]
 return mesh(name,v,f,role,uv)
for i,points in enumerate(plan['pools']):
 # Outward normal is corrected by source winding so coping stays dry-side.
 area=sum(points[k][0]*points[(k+1)%len(points)][1]-points[(k+1)%len(points)][0]*points[k][1] for k in range(len(points)))
 if area<0:points=list(reversed(points))
 sweep(f'GAR_Pool_{i}_Coping',points,[(0,-.10),(.46,-.10),(.46,.04),(.35,.11),(.08,.11),(0,.04)],'stone')
 sweep(f'GAR_Pool_{i}_TileWall',points,[(-.025,-.8),(.025,-.8),(.025,.02),(-.025,.02)],'tile')
 sweep(f'GAR_Pool_{i}_MetalInset',points,[(.30,.111),(.33,.111),(.33,.115),(.30,.115)],'metal')
# Low planting island leaves the broad surrounding court traversable.
points=[(-3+8*math.cos(i*math.pi/24),-4+16*math.sin(i*math.pi/24)) for i in range(48)]
sweep('GAR_CentralPlanter',points,[(-.18,0),(.26,0),(.34,.20),(.30,.44),(.18,.51),(-.18,.51)],'ivory')
sweep('GAR_PlanterSeatCap',points,[(.22,.44),(.85,.44),(.85,.52),(.22,.52)],'wood')
v=[(-3,4,.46)]+[(x,-z,.46) for x,z in points];mesh('GAR_PlantingSoil',v,[(0,(i+1)%48+1,i+1) for i in range(48)],'soil')
for name,x,z in [('CANOPY_A',-5,-12),('CANOPY_B',0,5)]:
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=(x,-z,.46)
for i,(x,z) in enumerate([(-8,-12),(2,-12),(-7,5),(2,5)]):
 points=[(x+.22*math.cos(j*math.pi/8),z+.22*math.sin(j*math.pi/8)) for j in range(16)]
 sweep('GAR_UplightFrame_'+str(i),points,[(0,.46),(.06,.46),(.06,.57),(0,.57)],'metal')
 v=[(x,-z,.56)]+[(a,-b,.56) for a,b in points];mesh('GAR_UplightLens_'+str(i),v,[(0,(j+1)%16+1,j+1) for j in range(16)],'opal')
 o=bpy.data.objects.new('DATUM_uplight_'+str(i),None);bpy.context.collection.objects.link(o);o.location=(x,-z,.60)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all()
blend=ROOT/'source/AST-GAR-001.blend';glb=ROOT/'exports/AST-GAR-001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
(ROOT/'AST-GAR-001.manifest.json').write_text(json.dumps({'catalogue_id':'AST-GAR-001','name':'D02 offset garden basin and seated grove island','source':'source/AST-GAR-001.blend','export':'exports/AST-GAR-001.glb','support_files':['source/garden_plan.json'],'triangles':tri,'status':'Draft; needs in-engine route and visual review','coordinates':'Blender=(shipX,-shipZ,height above D02), place GLB at shipY6','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n')
print('GARDEN_BASIN_CREATED',tri)
