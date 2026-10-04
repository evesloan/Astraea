"""Original Night garden: four planted resting courts, sheltered thresholds and atrium views."""
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

# Existing D12 Night garden allocation: worldX52..98,Z-34..34, floor78.
# Local source X points starboard across the allocation, Y becomes negative worldZ.
outline=[(0,-34),(37,-34),(43,-30),(46,-21),(46,21),(43,30),(37,34),(0,34)]
resin=bpy.data.materials.new('NightGardenMatteResin');resin.use_nodes=True;resin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.065,.10,.115,1);resin.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.86;mats['night_resin']=resin
extrusion('NG_Floor',outline,-.24,0,'night_resin')
finish=json.loads((ROOT/'source/floor_finish.json').read_text());vertices=[];faces=[]
for triangle in finish['triangles']:
 n=len(vertices);vertices.extend((x,y,.006)for x,y in triangle);faces.append((n,n+1,n+2))
mesh('NG_StoneWalkingLoop',vertices,faces,'warm_stone')
for i,(x,y)in enumerate(finish['loop_points']):datum('walk_loop_%03d'%i,(x,y,0))
def wall(name,a,b,lo,hi,role,thickness=.16):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();n=Vector((-t.y,t.x))*thickness/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo,hi,role)
# Deep side walls collect the intimate courts. The atrium side has real glazing
# beside its central entry; no exterior window is invented through another room.
for i,(a,b) in enumerate(zip(outline[1:],outline[2:]+[outline[0]])):
 if a[0]==0 and b[0]==0:continue
 # Pull structural thickness inward from the allocation edge.
 a=(a[0]-.12 if a[0]>0 else .12,a[1]-.12 if a[1]>0 else a[1]+.12)
 b=(b[0]-.12 if b[0]>0 else .12,b[1]-.12 if b[1]>0 else b[1]+.12)
 wall('NG_Side_'+str(i),a,b,0,5.20,'ivory_enamel')
 wall('NG_Dado_'+str(i),a,b,0,.70,'warm_walnut',.20)
wall('NG_NorthSide',(.12,-33.88),(36.88,-33.88),0,5.2,'ivory_enamel')
glass=bpy.data.materials.new('NightGardenGlass');glass.use_nodes=True;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.25,.46,.49,.38);bs.inputs['Alpha'].default_value=.38;bs.inputs['Roughness'].default_value=.3;mats['glass']=glass
for a,b in [(-33.8,-6),(6,33.8)]:
 wall('NG_ViewSill_'+str(a),(.12,a),(.12,b),0,.65,'warm_walnut',.20)
 wall('NG_ViewHead_'+str(a),(.12,a),(.12,b),4.40,5.20,'warm_walnut',.20)
 for y in [a,a+(b-a)/3,a+2*(b-a)/3,b]:wall('NG_ViewMullion_'+str(y),(.06,y),(.22,y),.65,4.4,'champagne_metal',.10)
 wall('NG_RealAtriumGlazing_'+str(a),(.12,a),(.12,b),.67,4.38,'glass',.016)
# Opaque roof stays below the actual occupied deck above. Six fitted soffit
# planes form a higher central arrival and lower garden edges.
extrusion('NG_OpaqueRoof',outline,5.20,5.38,'ivory_enamel')
for side in [-1,1]:
 pts=[(0,side*6,4.55),(8,side*7,4.85),(16,side*9,4.85),(24,side*12,4.60),(34,side*16,4.15),(44,side*19,3.8)]
 beam('NG_BranchingSoffit_'+str(side),pts,.55,.24,'warm_walnut')
 # Portal-bearing posts make the canopy visibly attached to architecture.
 for x,y,z in [pts[1],pts[4]]:
  extrusion('NG_CanopyBearing_%s_%s'%(side,x),[(x-.13,y-.16),(x+.13,y-.16),(x+.13,y+.16),(x-.13,y+.16)],0,z,'champagne_metal')
# Deep ceiling shoulders shape the whole room in section, rather than leaving
# its height as a uniform flat box around three decorative canopies.
for side in [-1,1]:
 stations=[(22,5.12),(26,4.86),(30,4.28),(33.75,3.48)]
 for j,((ya,za),(yb,zb))in enumerate(zip(stations,stations[1:])):
  q=[(.25,side*ya,za),(37,side*ya,za),(37,side*yb,zb),(.25,side*yb,zb)]
  mesh('NG_SideCeilingShoulder_%d_%d'%(side,j),q+[(x,y,z+.10)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
for j,((xa,za),(xb,zb))in enumerate(zip([(32,5.12),(37,4.80),(41,4.18)],[(37,4.80),(41,4.18),(45.70,3.48)])):
 q=[(xa,-20,za),(xb,-20,zb),(xb,20,zb),(xa,20,za)]
 mesh('NG_RearCeilingShoulder_'+str(j),q+[(x,y,z+.10)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
# Unequal planted courts interrupt the long box envelope with activity
# edges, while the main cross-route and a longitudinal spine remain clear.
courts=[(22,-20,6.4,4.2),(32,15,7.5,5.6),(12,24,4.8,3.5),(18,0,8,4.5)]
for k,(cx,cy,rx,ry) in enumerate(courts):
 ring=[(cx+rx*math.cos(2*math.pi*i/24),cy+ry*math.sin(2*math.pi*i/24))for i in range(24)]
 inner=[(cx+(rx-.23)*math.cos(2*math.pi*i/24),cy+(ry-.23)*math.sin(2*math.pi*i/24))for i in range(24)]
 extrusion('NG_PlanterShell_'+str(k),ring,0,.55,'warm_walnut')
 extrusion('NG_Soil_'+str(k),inner,.55,.58,'botanical_soil')
 for j in range(7):
  a=2*math.pi*j/7;datum('plant_%d_%d'%(k,j),(cx+(rx-1.10)*math.cos(a),cy+(ry-1.0)*math.sin(a),.58))
 # Low underplanting fills the bed in deliberately nested groups instead of
 # leaving seven isolated specimens around a largely empty soil plane.
 for j in range(16):
  a=2*math.pi*j/16;datum('underplant_%d_%d'%(k,j),(cx+(rx-1.8)*.64*math.cos(a),cy+(ry-1.6)*.64*math.sin(a),.58))
 for j in range(8):
  a=2*math.pi*j/8;datum('flower_%d_%d'%(k,j),(cx+(rx-.65)*math.cos(a),cy+(ry-.55)*math.sin(a),.58))
 # A broad low canopy over each resting edge lowers its intimate scale.
 arc=[]
 for j in range(13):
  a=math.pi*.05+math.pi*.9*j/12
  arc.append((cx+(rx+1.10)*math.cos(a),cy+(ry+1.10)*math.sin(a),3.30+.30*math.sin(a)))
 beam('NG_RestingCanopy_'+str(k),arc,1.25,.14,'oatmeal_weave')
 for j in [0,12]:
  x,y,z=arc[j];extrusion('NG_RestPost_%d_%d'%(k,j),[(x-.09,y-.09),(x+.09,y-.09),(x+.09,y+.09),(x-.09,y+.09)],0,z,'warm_walnut')
 # Segmented integrated seating follows the bed's edge, facing out to the room.
 for j in range(8):
  a=.12*math.pi+j*.10*math.pi;b=a+.085*math.pi
  q=[(cx+(rx+.25)*math.cos(a),cy+(ry+.25)*math.sin(a)),(cx+(rx+.88)*math.cos(a),cy+(ry+.88)*math.sin(a)),(cx+(rx+.88)*math.cos(b),cy+(ry+.88)*math.sin(b)),(cx+(rx+.25)*math.cos(b),cy+(ry+.25)*math.sin(b))]
  extrusion('NG_BuiltInBench_%d_%d'%(k,j),q,.08,.41,'warm_walnut');extrusion('NG_Seat_%d_%d'%(k,j),q,.41,.48,'teal_weave')
# The entrance is compressed under an acoustic lid, opening onto the central
# planted court. Its two routes reveal the quieter rooms obliquely.
extrusion('NG_EntryAcousticLid',[(0,-5.8),(7,-5.8),(9,-4.8),(9,4.8),(7,5.8),(0,5.8)],3.62,3.82,'oatmeal_weave')
for y in [-5.8,5.8]:
 beam('NG_EntryProfile_'+str(y),[(0,y,3.60),(7,y,3.60),(9,y*.827,3.85)],.16,.12,'warm_walnut')
# Side screens define each quiet court without severing its accessible route.
for k,(x,y,angle) in enumerate([(30,-26,.30),(39,4,-.3),(19,28,.15)]):
 points=[(x-3,y-1.2),(x-1.8,y),(x,y+.55),(x+2,y),(x+3,y-1.2)]
 for j,(a,b)in enumerate(zip(points,points[1:])):
  wall('NG_QuietScreen_%d_%d'%(k,j),a,b,0,2.25,'oatmeal_weave',.20)
  wall('NG_ScreenCap_%d_%d'%(k,j),a,b,2.25,2.32,'warm_walnut',.24)
# Tall wall bays give the longer enclosure a legible rhythm and material depth.
for y in [-27,-18,-9,0,9,18,27]:
 x=45.65 if abs(y)<22 else 43.4
 extrusion('NG_RearWallPilaster_'+str(y),[(x-.18,y-.32),(x+.10,y-.32),(x+.10,y+.32),(x-.18,y+.32)],0,5.18,'warm_walnut')
# A low shared refreshment/repose destination at the rear does not need a monument.
for j,(x,y) in enumerate([(10,-20),(18,0),(35,-8),(38,24),(20,18),(8,10)]):
 h=3.82 if j==1 else (4.20 if j<3 else 3.90)
 extrusion('NG_LightHousing_'+str(j),[(x-.44,y-.32),(x+.44,y-.32),(x+.44,y+.32),(x-.44,y+.32)],h,h+.16,'champagne_metal')
 extrusion('NG_OpalExit_'+str(j),[(x-.39,y-.27),(x+.39,y-.27),(x+.39,y+.27),(x-.39,y+.27)],h-.012,h,'lens')
 beam('NG_LightStem_'+str(j),[(x,y,h+.16),(x,y,5.22)],.055,.055,'champagne_metal')
 datum('light_'+str(j),(x,y,h-.04))
for j,(x,y) in enumerate([(5,-10),(5,10),(40,0)]):datum('conversation_'+str(j),(x,y,0))
for i,(x,y)in enumerate([(22,-23.8),(32,10)]):
 extrusion('NG_PlanterUplightHousing_'+str(i),[(x-.13,y-.13),(x+.13,y-.13),(x+.13,y+.13),(x-.13,y+.13)],.49,.64,'champagne_metal')
 extrusion('NG_PlanterUplightLens_'+str(i),[(x-.10,y-.10),(x+.10,y-.10),(x+.10,y+.10),(x-.10,y+.10)],.64,.648,'lens')
 datum('uplight_'+str(i),(x,y,.66))
# Coordinated occupied-ceiling interfaces for the upper commons piers.
# Each opening is filled by its explicit matching shaft and profiled collar;
# the garden floor and deck elevations remain intact.
interfaces=[(19,12),(12,-12),(42,11.5),(42,-11.5),(8,17)]
for index,(cx,cy)in enumerate(interfaces):
 targets=[o for o in parts if o.name=='NG_OpaqueRoof' or (cx>41 and o.name=='NG_RearCeilingShoulder_2')]
 for target in targets:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,cy,4.5));cutter=bpy.context.object;cutter.name='TEMP_PierAperture';cutter.dimensions=(.72,.72,4)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bpy.context.view_layer.objects.active=target
  mod=target.modifiers.new('CoordinatedPierAperture_'+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
  rear=target.name.startswith('NG_Rear')
  def plane(x):return 4.18-(x-41)*.70/4.70 if rear else 5.20
  # Inner contour mates with the octagonal 640mm pier; the outer ring covers
  # the720mm clearance opening. Sloped shoulder collar follows its plane.
  half=.32;ch=.075
  inner=[(-half+ch,-half),(half-ch,-half),(half,-half+ch),(half,half-ch),(half-ch,half),(-half+ch,half),(-half,half-ch),(-half,-half+ch)]
  outer=[(-.42,-.42),(.42,-.42),(.42,-.20),(.42,.20),(.42,.42),(-.42,.42),(-.42,.20),(-.42,-.20)]
  vertices=[]
  for dz in [-.035,.035]:
   for ring in [outer,inner]:vertices.extend((cx+x,cy+y,plane(cx+x)+dz)for x,y in ring)
  faces=[]
  for k in range(8):
   j=(k+1)%8
   faces.extend([(k,j,j+8,k+8),(k+16,k+24,j+24,j+16),(k,k+16,j+16,j),(k+8,j+8,j+24,k+24)])
  mesh('NG_CoordinatedPierCollar_%d_%s'%(index,rear),vertices,faces,'champagne_metal')

scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();source=ROOT/'source/AST-GAR-006.blend';export=ROOT/'exports/AST-GAR-006.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
for role,material in mats.items():
 selected=[o for o in list(bpy.context.scene.objects)if o.type=='MESH'and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='NG_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-GAR-006.manifest.json').write_text(json.dumps({'catalogue_id':'AST-GAR-006','name':'Night garden with four planted resting courts and branching soffits','source':'source/AST-GAR-006.blend','export':'exports/AST-GAR-006.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Authored draft; route, contact, visual and programme checks pending'},indent=2)+'\n')
