"""Original reusable guard/fascia profile fitted to the real sixteen-level atrium.
One construction family, not sixteen newly counted designs. Editable source retains parts.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1];paths=json.loads((ROOT/'source/atrium_paths.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for role in ['ivory_enamel','warm_walnut','champagne_metal','dark_rubber']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.65
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('gallery_glass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.23,.49,.51,1);b.inputs['Alpha'].default_value=.23;b.inputs['Roughness'].default_value=.22;m.diffuse_color=(.23,.49,.51,.23);m.surface_render_method='DITHERED';mats['gallery_glass']=m
parts=[]
def mesh(name,vertices,faces,role,uvs=None):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o)
 uv=d.uv_layers.new(name='MetreScaled')
 for f in d.polygons:
  for li in f.loop_indices:
   vi=d.loops[li].vertex_index;v=d.vertices[vi].co;uv.data[li].uv=uvs[vi] if uvs else (v.x*.5,v.z*.5)
 return o
for deck in paths['decks']:
 name=deck['deck'];base=deck['floor_y'];source=[Vector(p) for p in deck['boundary']];points=[]
 for i,a in enumerate(source):
  b=source[(i+1)%len(source)];steps=max(1,math.ceil((b-a).length/2))
  points.extend(a.lerp(b,j/steps) for j in range(steps))
 def frames(path):
  normals=[];distance=[0.0]
  for i,p in enumerate(path):
   previous=(p-path[i-1]).normalized();following=(path[(i+1)%len(path)]-p).normalized()
   n1=Vector((previous.y,-previous.x));n2=Vector((following.y,-following.x));n=(n1+n2).normalized();n/=max(.5,n.dot(n2));normals.append(n)
   if i:distance.append(distance[-1]+(p-path[i-1]).length)
  return normals,distance
 normals,distance=frames(points)
 coarse_normals,coarse_distance=frames(source)
 def sweep(label,profile,role):
  verts=[];uv=[];n=len(profile)
  for i,p in enumerate(source):
   for depth,z in profile:
    q=p+coarse_normals[i]*depth;verts.append((q.x,-q.y,base+z));uv.append((coarse_distance[i]*.5,z*.5+depth*.5))
  faces=[]
  for i in range(len(source)):
   k=(i+1)%len(source)
   for j in range(n):l=(j+1)%n;faces.append((i*n+j,i*n+l,k*n+l,k*n+j))
  return mesh(name+'_'+label,verts,faces,role,uv)
 drop=.66 if deck['major'] else .32
 sweep('Fascia',[(0,0),(.34,0),(.34,-drop+.16),(.25,-drop),(.08,-drop),(0,-drop+.15)],'ivory_enamel')
 sweep('GuardPlinth',[(.01,0),(.43,0),(.43,.14),(.32,.21),(.1,.21),(.01,.13)],'ivory_enamel')
 sweep('Handrail',[(.115,1.10),(.14,1.08),(.29,1.08),(.315,1.10),(.315,1.13),(.29,1.15),(.14,1.15),(.115,1.13)],'warm_walnut')
 sweep('RailSeat',[(.17,1.055),(.26,1.055),(.26,1.08),(.17,1.08)],'champagne_metal')
 for i,p in enumerate(points):
  k=(i+1)%len(points);q=points[k]
  start=p.lerp(q,.025);end=p.lerp(q,.975);v=[]
  for point,normal in [(start,normals[i]),(end,normals[k])]:
   for depth,z in [(.218,.235),(.236,.235),(.236,1.055),(.218,1.055)]:
    loc=point+normal*depth;v.append((loc.x,-loc.y,base+z))
  mesh(name+f'_Glass_{i:03}',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'gallery_glass')
  loc=p+normals[i]*.225;v=[]
  for z,r in [(.16,.05),(.24,.035),(1.10,.035)]:
   for j in range(6):a=2*math.pi*j/6;v.append((loc.x+r*math.cos(a),-loc.y+r*math.sin(a),base+z))
  f=[tuple(reversed(range(6))),tuple(range(12,18))]+[(h*6+j,h*6+(j+1)%6,(h+1)*6+(j+1)%6,(h+1)*6+j) for h in range(2) for j in range(6)]
  mesh(name+f'_Post_{i:03}',v,f,'champagne_metal')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();blend=ROOT/'source/AST-ATR-001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Compact export by deck/material, not a ship-wide combined mesh. Source remains editable.
for deck in paths['decks']:
 for role,material in mats.items():
  objects=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.name.startswith(deck['deck']+'_') and o.data.materials[0]==material]
  if not objects:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name=deck['deck']+'_'+role
bpy.ops.object.select_all(action='SELECT');glb=ROOT/'exports/AST-ATR-001.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-ATR-001.manifest.json').write_text(json.dumps({'catalogue_id':'AST-ATR-001','name':'Profiled atrium guard and fascia network','unique_design':True,'design_count_note':'One construction profile family fitted to sixteen decks; deck copies and fitted paths are not additional designs','status':'Draft; path/physics/visual checks pending','source':'source/AST-ATR-001.blend','export':'exports/AST-ATR-001.glb','support_files':['source/atrium_paths.json'],'decks':16,'major_bands':['D06','D09','D12','D16'],'triangles':tri,'source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'coordinates':'Source Blender XYZ=(shipX,-shipZ,shipY); origin is ship datum. GLB is already ship-local.','collision_policy':'Static guard/fascia contacts, no moving leaf physics. Do not combine into one convex hull.'},indent=2)+'\n')
print('ATRIUM_GUARDS_CREATED',tri)
