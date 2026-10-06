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

# Local +Y goes from access street toward the real atrium-facing window.
# The outer allocation remains7.2x12.9m; offset wet-room privacy, swept living
# walls and a rising ceiling shape the experience inside it.
glass=bpy.data.materials.new('SuiteHospitalityGlass');glass.use_nodes=True;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.25,.46,.49,.38);bs.inputs['Alpha'].default_value=.38;bs.inputs['Roughness'].default_value=.3;mats['glass']=glass
extrusion('SUI_Floor',[(-3.6,0),(3.6,0),(3.6,12.9),(-3.6,12.9)],-.22,0,'warm_stone')
left=[(-3.50,.12),(-3.50,4.0),(-3.18,4.55),(-2.95,5.2),(-2.95,6.2),(-3.20,7.05),(-3.50,7.8),(-3.50,12.75)]
right=[(3.50,.12),(3.50,2.8),(3.30,3.5),(3.20,4.2),(3.20,5.1),(3.20,6.2),(3.40,7.25),(3.50,8),(3.50,12.75)]
def height(y):return 2.95+.95*max(0,min(1,(y-2)/10.75))
def wall(name,a,b,lo,ha,hb,role,thickness=.12):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();n=Vector((-t.y,t.x))*thickness/2;ring=[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)]
 return mesh(name,[(x,y,lo)for x,y in ring]+[(x,y,z)for (x,y),z in zip(ring,[ha,hb,hb,ha])],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
for side,path in [('L',left),('R',right)]:
 for i in range(len(path)-1):
  a,b=path[i:i+2];ha,hb=height(a[1]),height(b[1]);wall('SUI_Base_'+side+str(i),a,b,0,.24,.24,'warm_walnut');wall('SUI_Wall_'+side+str(i),a,b,.24,ha,hb,'ivory_enamel');wall('SUI_Crown_'+side+str(i),a,b,ha-.045,ha+.045,hb+.045,'warm_walnut',.16)
# Soft finishes and curved acoustic panels belong to the room profile, not
# a stronger display filter. The bathroom keeps its washable stone surface.
carpet=[(-.55,1.4),(2.45,1.4),(2.45,2.7),(3.25,3.5),(2.85,4.2),(2.65,5.1),(2.80,6.2),(3.25,7.25),(3.40,8),(3.40,12.65),(-3.40,12.65),(-3.40,7.8),(-3.05,7.2),(-2.75,6.3),(-2.90,5.5),(-3.30,4.8),(-3.40,4.1),(-.55,4.1)]
extrusion('SUI_FittedCarpet',carpet,.001,.012,'oatmeal_weave')
for i,a in enumerate(carpet):
 b=carpet[(i+1)%len(carpet)];wall('SUI_CarpetBinding_'+str(i),a,b,.012,.017,.017,'clay_weave',.065)
for side,path in [('L',left),('R',right)]:
 for i in range(len(path)-1):
  a,b=path[i:i+2]
  wall('SUI_TimberWainscot_'+side+str(i),a,b,.24,1.05,1.05,'warm_walnut',.15)
  if a[1]>=4 and b[1]<=8:wall('SUI_AcousticLiving_'+side+str(i),a,b,1.12,2.18,2.18,'clay_weave',.15)
# A broad woven colour field distinguishes the occupied lounge at gameplay
# resolution; the restrained bound edge stays flush and does not obstruct feet.
lounge=[(-3.15,4.35),(-.60,4.35),(0,4.10),(2.78,4.35),(2.60,5.20),(2.70,6.35),(3.20,7.35),(-3.00,7.35),(-2.65,6.30),(-2.82,5.50)]
extrusion('SUI_LoungeCarpet',lounge,.013,.018,'clay_weave')
for i,a in enumerate(lounge):
 b=lounge[(i+1)%len(lounge)];wall('SUI_LoungeCarpetBinding_'+str(i),a,b,.018,.020,.020,'oatmeal_weave',.05)
datum('window_view_target',(0,12.7,1.4))
# Front entrance remains centred on its historical marker; the wet room
# has an offset side entrance so the bathroom is not exposed to the street.
for a,b in [((-3.5,.12),(-.80,.12)),((.80,.12),(3.5,.12))]:wall('SUI_EntryJamb_'+str(a[0]),a,b,0,2.95,2.95,'ivory_enamel',.18)
wall('SUI_EntryHeader',(-.8,.12),(.8,.12),2.55,2.95,2.95,'warm_walnut',.18)
wall('SUI_BathPrivacyReturn',(-3.44,4.0),(-.70,4.0),0,2.60,2.60,'ivory_enamel')
wall('SUI_BathInnerForward',(-.7,.12),(-.7,2.35),0,2.60,2.60,'ivory_enamel')
wall('SUI_BathInnerRear',(-.7,3.45),(-.7,4.0),0,2.60,2.60,'ivory_enamel')
wall('SUI_BathDoorHeader',(-.7,2.35),(-.7,3.45),2.25,2.60,2.60,'warm_walnut')
extrusion('SUI_BathCeiling',[(-3.44,.16),(-.70,.16),(-.70,4),(-3.44,4)],2.60,2.74,'ivory_enamel')
# Main ceiling follows the side contours at several sections; the sheltered
# entrance gradually gives way to the taller sleeping/viewing zone.
ys=[.12,2,4,6,8,10,12.75]
def at(path,y):
 for a,b in zip(path,path[1:]):
  if a[1]<=y<=b[1]:return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
 return path[-1][0]
for i in range(len(ys)-1):
 a,b=ys[i:i+2];q=[(at(left,a),a,height(a)),(at(right,a),a,height(a)),(at(right,b),b,height(b)),(at(left,b),b,height(b))]
 mesh('SUI_Ceiling_'+str(i),q+[(x,y,z+.14)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
# Low screened wings and a shaped overhead threshold distinguish the lounge
# from sleeping without taking away the long view or the central cart route.
for side in [-1,1]:
 profile=[(side*3.43,7.63),(side*1.70,7.63),(side*1.35,7.84),(side*1.50,8.04),(side*3.43,8.04)]
 h=1.20 if side<0 else 1.50
 if side<0:
  extrusion('SUI_LivingCasePlinth',profile,0,.34,'warm_walnut')
  extrusion('SUI_LivingCaseBack',[(-3.43,7.98),(-1.5,7.98),(-1.5,8.04),(-3.43,8.04)],.34,h,'ivory_enamel')
  for a,b in [(-3.43,-3.31),(-1.70,-1.58)]:extrusion('SUI_LivingCaseReturn_'+str(a),[(a,7.63),(b,7.63),(b,8.04),(a,8.04)],.34,h,'warm_walnut')
  extrusion('SUI_LivingCaseShelf',profile,.73,.78,'warm_walnut')
 else:extrusion('SUI_SleepThresholdWing_'+str(side),profile,0,h,'ivory_enamel')
 extrusion('SUI_ThresholdTimberCap_'+str(side),profile,h,h+.065,'warm_walnut')
section=[(-3.45,3.0),(-2.8,3.0),(-1.2,3.20),(1.2,3.20),(2.8,3.0),(3.45,3.0),(3.45,3.60),(-3.45,3.60)]
v=[(x,y,z)for y in [7.65,7.98]for x,z in section];n=len(section)
mesh('SUI_SleepingValance',v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],'ivory_enamel')
# A fitted writing/reading position gives the second lounge edge a different
# purpose from the shared bench. Its kneehole is left genuinely open.
extrusion('SUI_WritingTop',[(1.48,7.12),(3.22,7.12),(3.27,7.57),(1.66,7.57),(1.40,7.36)],.73,.79,'warm_walnut')
for x in [1.58,3.1]:extrusion('SUI_WritingSupport_'+str(x),[(x-.045,7.16),(x+.045,7.16),(x+.045,7.53),(x-.045,7.53)],0,.735,'champagne_metal')
datum('writing_chair',(2.22,6.25,0))
# Two sleeping alcoves replace the original single open sleeping area.
# Their open approaches split around a slender screened spine; each keeps its
# own half of the actual inward glazing and one existing bed anchor.
spine=[(-.07,8.78),(0,8.60),(.07,8.78),(.07,12.66),(-.07,12.66)]
extrusion('SUI_TwinRetreatSpine',spine,0,2.40,'teal_weave')
extrusion('SUI_TwinRetreatSpineCap',spine,2.40,2.47,'warm_walnut')
for side in [-1,1]:
 # Each canopy is a segmented vault, open above the actual approach aisle.
 centre=side*1.90
 section=[(centre-1.30,2.90),(centre-.95,3.10),(centre-.45,3.22),(centre+.45,3.22),(centre+.95,3.10),(centre+1.30,2.90)]
 for j in range(len(section)-1):
  a,b=section[j:j+2]
  q=[(a[0],9.12,a[1]),(b[0],9.12,b[1]),(b[0],12.52,b[1]),(a[0],12.52,a[1])]
  mesh('SUI_RetreatVault_%d_%d'%(side,j),q+[(x,y,z+.07)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'oatmeal_weave')
 # End returns carry the ceiling into the existing side-wall language.
 for y in [9.12,12.45]:
  wall('SUI_RetreatVaultSupport_%d_%s'%(side,y),(side*3.20,y),(side*3.44,y),0,2.93,2.93,'warm_walnut',.12)
# A real inward-facing window; separate glass batch gets the existing Godot shader.
wall('SUI_WindowSill',(-3.5,12.78),(3.5,12.78),0,.48,.48,'warm_walnut',.22)
wall('SUI_WindowHead',(-3.5,12.78),(3.5,12.78),3.60,3.90,3.90,'warm_walnut',.22)
for x in [-3.45,0,3.45]:wall('SUI_WindowMullion_'+str(x),(x,12.72),(x,12.86),.48,3.60,3.60,'champagne_metal',.09)
for a,b in [(-3.40,-.055),(.055,3.40)]:wall('SUI_WindowPane_'+str(a),(a,12.78),(b,12.78),.49,3.59,3.59,'glass',.018)
# A built-in entry storage volume remains visibly closed; no inventory claim.
extrusion('SUI_EntryStorage',[(2.55,.30),(3.42,.30),(3.42,2.5),(2.85,2.5),(2.55,2.20)],0,2.35,'warm_walnut')
wall('SUI_StorageFront',(2.53,.45),(2.53,2.1),.22,2.15,2.15,'teal_weave',.025)
for i,(x,y) in enumerate([(1.35,2.7),(0,6.4),(0,8.2)]):
 h=height(y)-.18
 extrusion('SUI_RecessedFixture_'+str(i),[(x-.25,y-.18),(x+.25,y-.18),(x+.25,y+.18),(x-.25,y+.18)],h,h+.22,'champagne_metal')
 extrusion('SUI_OpalLens_'+str(i),[(x-.21,y-.14),(x+.21,y-.14),(x+.21,y+.14),(x-.21,y+.14)],h-.015,h,'lens')
 datum('light_'+str(i),(x,y,h-.035))
for i,side in enumerate([-1,1]):
 x=side*3.36
 extrusion('SUI_BedSconceHousing_'+str(i),[(x-.08,10.6),(x+.08,10.6),(x+.08,11.0),(x-.08,11.0)],1.16,1.72,'champagne_metal')
 x=side*3.26
 extrusion('SUI_BedSconceOpal_'+str(i),[(x-.035,10.66),(x+.035,10.66),(x+.035,10.94),(x-.035,10.94)],1.24,1.64,'lens')
 datum('bed_light_'+str(i),(side*3.20,10.8,1.44))
 datum('bed_table_'+str(i),(side*2.83,11.7,0))
for i,x in enumerate([-1.65,1.65]):datum('bed_'+str(i),(x,10.25,0))
datum('living_bench',(-1.50,5.8,0));datum('living_table',(-.85,6.75,0));datum('door',(0,0,0));datum('bath_entry',(-.65,2.9,0))
datum('bath_vanity',(-3.44,3.1,0));datum('bath_wc',(-2.8,.90,0));datum('bath_shower',(-1.38,.905,0))
extrusion('SUI_BathFixture',[(-2.3,2.2),(-1.7,2.2),(-1.7,2.6),(-2.3,2.6)],2.47,2.63,'champagne_metal')
extrusion('SUI_BathLens',[(-2.26,2.24),(-1.74,2.24),(-1.74,2.56),(-2.26,2.56)],2.455,2.47,'lens')
datum('bath_light',(-2.0,2.4,2.43))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();blend=ROOT/'source/AST-SUI-002.blend';glb=ROOT/'exports/AST-SUI-002.glb';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Keep semantic pieces editable in .blend; batch only the exported static visual by material.
for role,material in mats.items():
 selected=[o for o in list(bpy.context.scene.objects) if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
 if not selected:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='SUI_Runtime_'+role
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True)
(ROOT/'AST-SUI-002.manifest.json').write_text(json.dumps({'catalogue_id':'AST-SUI-002','name':'Twin-retreat suite with bifurcated sleeping alcoves and a shared salon','source':'source/AST-SUI-002.blend','export':'exports/AST-SUI-002.glb','triangles':tri,'status':'Authored twin-retreat variation; integration/contact/visual review pending','usage':'D13 address13041 allocation; dry standard twin profile, incomplete bathroom fitout','source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()},indent=2)+'\n');print('GARDEN_OVERLOOK_CREATED',tri)
