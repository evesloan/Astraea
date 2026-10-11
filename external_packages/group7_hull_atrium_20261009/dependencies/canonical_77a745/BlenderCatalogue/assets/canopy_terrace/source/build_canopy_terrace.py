"""Original D06 garden overlook: sheltered back, rising roof and open court-facing edge."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[]
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.82
 path=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.x*.8,q.y*.8) if abs(p.normal.z)>.5 else ((q.x+q.y)*.8,q.z*.8)
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

# Entry narrows to a sheltered throat, then opens around two planted resting
# pockets. The view back to the atrium remains a straight accessible centreline.
outline=[(0,-3),(-4,-3),(-6,-8),(-10,-13),(-17,-15),(-23,-13),(-27,-8),(-28,0),(-27,8),(-23,13),(-17,15),(-10,13),(-6,8),(-4,3),(0,3)]
extrusion('CAN_Floor',outline,-.24,0,'warm_stone')
# Wall/ceiling profile is designed together: low sheltered perimeter, tall
# central crown, recessed threshold. Real occupied D07 above stays untouched.
for i in range(len(outline)-1):
 a=Vector(outline[i]);b=Vector(outline[i+1]);t=(b-a).normalized();n=Vector((-t.y,t.x));h=3.7 if i in [0,13] else 4.8
 ring=[tuple(a),tuple(b),tuple(b+n*.24),tuple(a+n*.24)]
 extrusion('CAN_WallPlinth_'+str(i),ring,0,.62,'warm_stone')
 ha=3.7 if i in [0,1,13,14] else 4.8;hb=3.7 if i+1 in [0,1,13,14] else 4.8
 mesh('CAN_ProfileWall_'+str(i),[(x,y,.62)for x,y in ring]+[(x,y,z) for (x,y),z in zip(ring,[ha,hb,hb,ha])],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
 # A deep timber inner reveal gives the perimeter material depth.
 if 2<=i<=11:
  for j in range(3):
   q=a.lerp(b,(j+.5)/3)-n*.13
   extrusion('CAN_Reveal_%d_%d'%(i,j),[tuple(q+t*u+n*v) for u,v in [(-.09,-.10),(.09,-.10),(.09,.10),(-.09,.10)]],.62,h,'warm_walnut')
# Selected wall bays have deep, coordinated acoustic returns, rather than
# repeating the same vertical baton on every face. Low tables can face these
# quieter edges while the centre remains an understandable through route.
for i in [3,5,8,10]:
 a=Vector(outline[i]);b=Vector(outline[i+1]);t=(b-a).normalized();n=Vector((-t.y,t.x));c=(a+b)/2-n*.16;half=min((b-a).length*.32,1.7)
 def quad(u0,u1,v0,v1):return [tuple(c+t*u+n*v)for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
 extrusion('CAN_AcousticInset_'+str(i),quad(-half,half,-.03,.03),1.05,3.12,'teal_weave')
 for j,sign in enumerate([-1,1]):
  extrusion('CAN_DeepReturn_%d_%d'%(i,j),quad(sign*half-.09,sign*half+.09,-.20,.12),.62,3.52,'warm_walnut')
 extrusion('CAN_LowDisplayShelf_'+str(i),quad(-half-.12,half+.12,-.32,.09),.80,.91,'warm_stone')
 extrusion('CAN_RecessedHeader_'+str(i),quad(-half-.16,half+.16,-.27,.15),3.35,3.52,'ivory_enamel')
# Two tailored floor islands support the social groups; no raised platform
# blocks the accessible central route or the perimeter niche approaches.
for i,(cx,cy,rx,ry) in enumerate([(-15,3.2,3.0,1.5),(-8.5,-5.0,2.2,2.0)]):
 extrusion('CAN_GatheringFloor_'+str(i),[(cx+rx*math.cos(j*math.tau/24),cy+ry*math.sin(j*math.tau/24))for j in range(24)],.001,.009,'warm_walnut')
# A broad raised ceiling field replaces the single-point tent. The offset
# inner ring creates a low perimeter and a legible high central gathering space.
inner=[(-15+(x+15)*.62,y*.60) for x,y in outline]
for i in range(len(outline)):
 j=(i+1)%len(outline);a=outline[i];b=outline[j];c=inner[j];d=inner[i]
 ha=3.7 if i in [0,1,13,14] else 4.8;hb=3.7 if j in [0,1,13,14] else 4.8
 q=[(a[0],a[1],ha),(b[0],b[1],hb),(c[0],c[1],6.5),(d[0],d[1],6.5)]
 mesh('CAN_RoofShoulder_'+str(i),q+[(x,y,z+.18)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut' if i in [3,4,9,10] else 'ivory_enamel')
extrusion('CAN_CentralCeiling',inner,6.5,6.68,'ivory_enamel')
# Substantial paired arch shoulders bear at the perimeter and frame each
# garden pocket without a knot of floating spokes at the centre.
for i in [2,4,6,8,10,12]:
 x,y=outline[i];ix,iy=inner[i]
 beam('CAN_RoofRib_'+str(i),[(x,y,.1),(x,y,4.45),((x+ix)/2,(y+iy)/2,5.25),(ix,iy,6.35)],.38,.34,'champagne_metal')
for y in [-3,3]:
 beam('CAN_CeilingLongitudinal_'+str(y),[(-22,y,6.35),(-16,y,6.35),(-10,y,6.35)],.14,.18,'warm_walnut')
# Two unequal garden pockets leave a broad accessible loop and an open centre.
for index,(cx,cy,rx,ry) in enumerate([(-17,-7.5,5.0,2.3),(-20,6.0,3.6,2.2)]):
 poly=[(cx+rx*math.cos(i*math.tau/20),cy+ry*math.sin(i*math.tau/20)) for i in range(20)]
 extrusion('CAN_PlantingPocket_'+str(index),poly,0,.56,'warm_stone')
 inner=[(cx+(rx-.18)*math.cos(i*math.tau/20),cy+(ry-.18)*math.sin(i*math.tau/20)) for i in range(20)]
 extrusion('CAN_PlantingSoil_'+str(index),inner,.56,.59,'botanical_soil')
 for j in range(5):
  datum('plant_%d_%d'%(index,j),(cx+(j-2)*rx*.32,cy,.59))
 # Built-in timber resting shelf faces the centre rather than the wall.
 side=1 if cy<0 else -1
 for j in range(8):
  angle=(.20+j*.12)*math.pi*side
  a=(cx+(rx+.25)*math.cos(angle),cy+(ry+.28)*math.sin(angle));b=(cx+(rx+.25)*math.cos(angle+.10*side),cy+(ry+.28)*math.sin(angle+.10*side))
  v=Vector(b)-Vector(a);t=v.normalized();n=Vector((-t.y,t.x));q=[tuple(Vector(a)+n*.25),tuple(Vector(b)+n*.25),tuple(Vector(b)-n*.25),tuple(Vector(a)-n*.25)]
  extrusion('CAN_IntegratedRest_%d_%d'%(index,j),q,.36,.46,'warm_walnut')
def roof_at(x,y):
 # All four source-positioned pendants lie inside the raised central field.
 return 6.5
for index,cy in enumerate([-11.8,11.8]):
 side=-1 if cy<0 else 1
 for j in range(4):
  x=-17.8+j*.65
  extrusion('CAN_NicheBack_%d_%d'%(index,j),[(x,cy-.12),(x+.55,cy-.12),(x+.55,cy+.12),(x,cy+.12)],.2,2.0,'warm_walnut')
 extrusion('CAN_NicheRest_'+str(index),[(-18.1,cy-side*.25),(-15.3,cy-side*.25),(-15.3,cy-side*1.0),(-18.1,cy-side*1.0)],.1,.43,'teal_weave')
 beam('CAN_NicheSoffit_'+str(index),[(-18.2,cy,3.25),(-16.7,cy-side*.75,3.55),(-15.1,cy,3.25)],.55,.18,'warm_walnut')
for i,(x,y,h) in enumerate([(-7,0,4.8),(-15,-4,5.6),(-19,4,5.6),(-24,0,4.8)]):
 extrusion('CAN_PendantStem_'+str(i),[(x-.035,y-.035),(x+.035,y-.035),(x+.035,y+.035),(x-.035,y+.035)],h,roof_at(x,y)-.02,'champagne_metal')
 extrusion('CAN_OpalLantern_'+str(i),[(x+.36*math.cos(j*math.tau/12),y+.36*math.sin(j*math.tau/12))for j in range(12)],h-.28,h,'lens')
 datum('light_'+str(i),(x,y,h-.31))
datum('arrival',(0,0,0));datum('gathering',(-13,0,0));datum('quiet_rest',(-24,0,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-GAR-004.blend';glb=ROOT/'exports/AST-GAR-004.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Keep semantic pieces editable in .blend; batch only the exported static visual by material.
for role,material in mats.items():
 selected=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='CAN_Runtime_'+role
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-GAR-004.manifest.json').write_text(json.dumps({'catalogue_id':'AST-GAR-004','name':'Canopy terrace branching arrival and garden room','source':'source/AST-GAR-004.blend','export':'exports/AST-GAR-004.glb','triangles':tri,'status':'Draft; integration/contact/visual review pending','usage':'D06_directory_05 eastern subset, origin X-52 Y27 Z0; unfinished surrounding allocation','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('GARDEN_OVERLOOK_CREATED',tri)
