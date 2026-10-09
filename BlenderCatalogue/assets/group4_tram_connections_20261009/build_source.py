#!/usr/bin/env python3
"""Group4 source-only station and cart tram. Does not mutate Game or catalogue owners.
blender -b --python build_source.py -- [--no-render]
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,struct,sys
from mathutils import Vector
OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name
assert FAMILY=='group4_tram_connections_20261009'
CAT=R/'BlenderCatalogue/catalogue_manifest.json';cat=json.loads(CAT.read_text())
IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']
def scan(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if isinstance(x,str) and x in IDS:assert any(a.get('catalogue_id')==x and a.get('family')==FAMILY for a in cat['assets']),x+' already owned'
   scan(x)
 elif isinstance(v,list):
  for x in v:scan(x)
scan(cat)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
B=lambda p:(p[0],-p[2],p[1]);G=lambda p:(p[0],p[2],-p[1])
materials={};texture_pins={}
def material(tag,file,color,rough=.7,metal=0):
 m=bpy.data.materials.new(tag);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if file:
  path=R/'BlenderCatalogue/materials'/file;texture_pins[str(path.relative_to(R))]=hashlib.sha256(path.read_bytes()).hexdigest();im=bpy.data.images.load(str(path),check_existing=True);tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Closest';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 materials[tag]=m;return m
stone=material('warm_stone','warm_stone.png',(.55,.49,.39));ivory=material('ivory_enamel','ivory_enamel.png',(.77,.73,.62));metal=material('champagne_metal','champagne_metal.png',(.56,.45,.27),.5,.5);wood=material('warm_walnut','warm_walnut.png',(.26,.14,.07));rubber=material('dark_rubber','dark_rubber.png',(.03,.03,.03));orange=material('original_coral_enamel',None,(.52,.16,.065));glass=material('station_guard_preview',None,(.10,.26,.24),.35)
parts=[];markers=[];current=None
collections={}
for name in ['FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name]=c

def mesh(name,vs,fs,mat,role,policy='static_trimesh_candidate',collection=None):
 co=collection or current;me=bpy.data.meshes.new(name+' mesh');me.from_pydata([B(p) for p in vs],[],fs);me.materials.append(mat);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);co.objects.link(ob)
 ob['construction_family']=FAMILY;ob['role']=role;ob['collision_policy']=policy
 # World-planar metre UVs per face, without subdivisions or generated textures.
 uv=me.uv_layers.new(name='Original_metre_UV')
 for poly in me.polygons:
  n=poly.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*.7,p[axes[1]]*.7)
 if co!=collections['UNEXPORTED_REFERENCE_AND_STUDIO']:parts.append(ob)
 return ob

def box(name,c,s,m,role,policy='static_trimesh_candidate',collection=None):
 x,y,z=c;dx,dy,dz=[a/2 for a in s];vs=[(x+u*dx,y+v*dy,z+w*dz) for u,v,w in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,role,policy,collection)
def tube(name,p,q,r,m,role,policy='static_trimesh_candidate',sides=8):
 p=Vector(p);q=Vector(q);v=(q-p).normalized();guide=Vector((0,1,0)) if abs(v.y)<.9 else Vector((1,0,0));a=v.cross(guide).normalized();b=v.cross(a).normalized();vs=[]
 for o in (p,q):
  for i in range(sides):t=math.tau*i/sides;vs.append(tuple(o+r*(math.cos(t)*a+math.sin(t)*b)))
 fs=[tuple(reversed(range(sides))),tuple(sides+i for i in range(sides))]+[(i,(i+1)%sides,sides+(i+1)%sides,sides+i) for i in range(sides)]
 return mesh(name,vs,fs,m,role,policy)
def marker(name,p,role,collection=None):
 ob=bpy.data.objects.new(name,None);(collection or current).objects.link(ob);ob.location=B(p);ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.15;ob['datum_kind']=role;markers.append(ob);return ob

def guard(name,x,z0,z1,y):
 # Faceted thick parapet infill, not a single convex fill through boarding openings.
 box(name+'_foot',(x,y+.11,(z0+z1)/2),(.10,.22,z1-z0),ivory,'guard base')
 box(name+'_infill',(x,y+.66,(z0+z1)/2),(.06,.82,z1-z0),glass,'guard infill')
 tube(name+'_rail',(x,y+1.13,z0),(x,y+1.13,z1),.055,metal,'handrail')
 for z in [z0,z1]:tube(name+'_post_'+str(z),(x,y,z),(x,y+1.1,z),.06,metal,'guard post')

# Elevated axial 68m study. Running/passenger floor56.1 is separate from wheel rail55.74.
current=collections['FORE_MIDSHIP_STATIC_SOURCE']
for i in range(17):
 z=-248+4*i
 box('Guideway_RibbedDeck_%02d'%i,(0,55.615,z),(4,.13,4),metal,'guideway structural deck')
 for x in [-.86,.86]:
  box('Guide_Rail_%02d_%s'%(i,x),(x,55.71,z),(.09,.06,4),metal,'wheel rail')
 # Parapet is outside4m vehicle clearance, anchored to fixed crossbearers.
for i,z in enumerate([-248,-240,-232,-224,-216,-208,-200,-192,-184]):
 for x in [-2.4,2.4]:
  box('Guideway_CapPad_%02d_%s'%(i,x),(x,52.54,z),(.42,.08,.75),metal,'actual D09 axial slab contact')
  box('Guideway_TaperedPier_%02d_%s'%(i,x),(x,54.12,z),(.30,3.08,.40),ivory,'pier to existing axial slab')
  box('Pier_OuterFascia_%02d_%s'%(i,x),(x,54.12,z+.205),(.22,2.96,.025),orange,'profiled pier fascia','no_collision_detail')
 box('Guideway_Crossbearer_Web_%02d'%i,(0,55.615,z),(5.1,.13,.55),metal,'wheel-channel crossbearer continuous web')
 for j,(a,b) in enumerate([(-2.55,-1.04),(-.68,.68),(1.04,2.55)]):box('Guideway_Crossbearer_Flange_%02d_%s'%(i,j),((a+b)/2,55.765,z),(b-a,.17,.55),metal,'flanges outside actual rolling wheels')
 if -240<=z<=-200:
  box('Platform_Cantilever_%02d'%i,(-5.1,55.7,z),(5.1,.30,.55),metal,'platform cantilever to same crossbearer')
  tube('Platform_Diagonal_%02d'%i,(-2.4,54.65,z),(-6.8,55.55,z),.09,metal,'visible platform brace')
for s,z in [('North',-250),('South',-182)]:marker('GUIDEWAY_INTERFACE_'+s,(0,56.1,z),'held exact guideway join; no line extension')
# Real profiled island deck24m, wider outer circulation, recessed boarding opening.
box('Boarding_Island_24m',(-4.9,55.975,-216),(5.4,.25,24),stone,'station top56.1')
box('Platform_OuterSoffit',(-7.44,55.89,-216),(.30,.34,24),ivory,'thick profiled platform edge')
box('Platform_InnerFascia',(-2.3,55.90,-216),(.2,.30,24),orange,'tram-facing station fascia')
# Opening spans z-217.2..-214.8, matching the vehicle side doorway.
guard('Port_Edge',-7.53,-228,-204,56.1)
guard('Tram_NorthGuard',-2.24,-228,-217.2,56.1);guard('Tram_SouthGuard',-2.24,-214.8,-204,56.1)
for z in [-217.2,-214.8]:
 box('Boarding_Portal_Post_'+str(z),(-2.24,57.35,z),(.18,2.5,.18),ivory,'boarding frame')
 box('Portal_Coral_Reveal_'+str(z),(-2.34,57.35,z),(.035,2.32,.12),orange,'portal reveal','no_collision_detail')
box('Boarding_Portal_Header',(-2.24,58.60,-216),(.20,.18,2.64),metal,'boarding frame')
marker('BOARDING_GATE_CONTROLLER_MOUNT',(-2.24,56.1,-216),'existing lift_gate visual/interaction adapter needed; no gate controller supplied')
marker('BOARDING_BRIDGE_STOW_AXIS',(-2.2,56.1,-216),'bridge0.9m reach to tram port sill-1.3; retract before movement')
# Canopy has layered edges and4m-free interior route between north/south landmark pockets.
for z in [-226.8,-205.2]:
 box('Station_Canopy_Pier_'+str(z),(-7.25,57.55,z),(.28,2.90,.40),ivory,'canopy support')
 box('Station_Canopy_Arm_'+str(z),(-5.0,59.10,z),(4.8,.22,.40),metal,'canopy crossbeam')
box('Canopy_Profiled_Crown',(-4.9,59.30,-216),(5.5,.25,24.3),ivory,'local station roof; independent no borrowed D10 slab')
box('Canopy_Recessed_Coral_Band',(-4.9,59.11,-216),(5.1,.07,23.5),orange,'recessed layered ceiling')
for z in [-225,-218,-211,-205]:
 box('Source_Lamp_Backplate_'+str(z),(-7.32,58.3,z),(.15,.38,.50),metal,'physical lamp fitting')
 box('Source_Lamp_Opal_'+str(z),(-7.22,58.3,z),(.08,.23,.34),ivory,'physical lens','no_collision_detail')
 marker('DATUM_LAMP_'+str(z),(-7.1,58.25,z),'bounded existing lighting manager candidate; source exports no lights')
for z in [-225.8,-206.2]:
 box('Quiet_Perch_Base_'+str(z),(-7.06,56.4,z),(.64,.60,1.2),wood,'local rest perch')
 box('Quiet_Perch_Cushion_'+str(z),(-7.03,56.75,z),(.70,.16,1.2),orange,'rest perch surface')
# Switchback, two12-riser flights, 150mm risers300mm treads;2.4m clear each.
for flight,x,base,direction in [(0,-6.25,52.5,-1),(1,-3.55,54.3,1)]:
 for i in range(12):
  z=-235-.3*(i+.5) if direction==-1 else -238.6+.3*(i+.5);top=base+.15*(i+1)
  box('Emergency_Flight%d_Step%02d'%(flight,i),(x,top-.12,z),(2.4,.24,.30),stone,'stair tread; actual top')
  box('Emergency_Nosing%d_%02d'%(flight,i),(x,top+.009,z+direction*.135),(2.4,.018,.03),metal,'stair nosing','no_collision_detail')
 for xx in [x-1.29,x+1.29]:
  y0=base+1.06;y1=base+1.8+1.06;z0=-235 if direction==-1 else -238.6;z1=-238.6 if direction==-1 else -235
  tube('Emergency_Rail%d_%s'%(flight,xx),(xx,y0,z0),(xx,y1,z1),.05,metal,'stair handrail')
  for t in [0,.5,1]:tube('Emergency_RailPost%d_%s_%s'%(flight,xx,t),(xx,base+1.8*t,z0+(z1-z0)*t),(xx,y0+(y1-y0)*t,z0+(z1-z0)*t),.04,metal,'stair rail post')
 # Sloped stringer is a closed slab under flight, not a solid wedge across walkable headroom.
 z0=-235 if direction==-1 else -238.6;z1=-238.6 if direction==-1 else -235;y0=base+.03;y1=base+1.8
 vs=[(xx,yy,zz) for xx in [x-1.2,x+1.2] for zz,top in [(z0,y0),(z1,y1)] for yy in [top-.28,top]]
 mesh('Emergency_Profiled_Stringer%d'%flight,vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],ivory,'closed inclined stair support')
box('Emergency_MidLanding',(-4.9,54.175,-239.5),(5.4,.25,1.8),stone,'supported switchback half landing')
box('Emergency_UpperLanding',(-3.55,55.975,-233.8),(2.4,.25,2.4),stone,'upper return landing')
box('Emergency_TopApproach',(-4.9,55.975,-230.3),(5.4,.25,4.6),stone,'stair to boarding island')
guard('Upper_Approach_Outer',-7.53,-232.6,-228,56.1);guard('Upper_Approach_Inner',-2.24,-232.6,-228,56.1)
# Guard the exposed switchback landing and descending-flight sides.
for x in [-7.53,-2.27]:guard('Emergency_MidLanding_Side_'+str(x),x,-240.4,-238.6,54.3)
box('Emergency_MidLanding_NorthInfill',(-4.9,54.92,-240.35),(5.3,1.08,.06),glass,'midlanding guarded back')
tube('Emergency_MidLanding_NorthRail',(-7.53,55.43,-240.35),(-2.27,55.43,-240.35),.05,metal,'midlanding rear handrail')
for flight,x,base,direction in [(0,-6.25,52.5,-1),(1,-3.55,54.3,1)]:
 z0=-235 if direction==-1 else -238.6;z1=-238.6 if direction==-1 else -235
 for xx in [x-1.29,x+1.29]:
  vs=[(tx,yy,zz) for tx in [xx-.025,xx+.025] for zz,top in [(z0,base),(z1,base+1.8)] for yy in [top+.08,top+1.02]]
  mesh('Emergency_Inclined_Guard_%s_%s'%(flight,xx),vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],glass,'faithful inclined guard; no open underrail gap')
# No new lower slab/fill is exported. Root must author a missing-only strip and bounded lift pit cut.
marker('LOWER_STAIR_ARRIVAL',(-6.25,52.5,-232.6),'new missing-only lower floor required')
marker('UPPER_STAIR_ARRIVAL',(-3.55,56.1,-232.6),'source supported upper landing')
# New boarding lift housing reuses existing4x3.6m two-stop cabin and entire commons_lift controller.
# Instance origin(-5.6,0,-200), yaw-PI/2, gate_origin_xz=(0,0), heights52.5/56.1.
for x in [-7.7,-3.5]:box('BoardingLift_HousingSide_'+str(x),(x,55.89,-198.2),(.12,7.22,3.72),ivory,'lift enclosure side')
box('BoardingLift_Rear',(-5.6,55.89,-196.3),(4.3,7.22,.12),ivory,'lift enclosure rear')
box('BoardingLift_Header',(-5.6,59.39,-198.2),(4.3,.18,3.92),metal,'lift top cap')
box('BoardingLift_PitPan',(-5.6,52.24,-198.2),(4.3,.08,3.92),metal,'pit source; bounded lower recess required')
box('BoardingLift_UpperLanding',(-5.6,55.975,-202),(4.4,.25,4.0),stone,'level accessible upper landing to platform')
for x in [-7.74,-3.46]:guard('LiftApproach_'+str(x),x,-204,-200,56.1)
marker('REUSE_COMMONS_LIFT_ROOT',(-5.6,0,-200),'yaw-PI/2; two unique local stop IDs; no existing stops changed')
marker('BOARDING_LIFT_LOWER_GATE',(-5.6,52.5,-200),'gate toward north; supported lower4m landing must be installed')
marker('BOARDING_LIFT_UPPER_GATE',(-5.6,56.1,-200),'gate toward north; source4m landing installed in proposal')
# Partial screened NPC waiting pocket, distinct from player tram doorway and controller.
box('Guest_Waiting_Screen',(-7.28,53.5,-211),(0.12,2.0,5.6),ivory,'screened guest vestibule edge')
box('Guest_Waiting_Seat',(-6.93,52.88,-210),(0.64,.76,1.7),wood,'guest waiting edge')
marker('GUEST_ABSTRACT_BOARDING_WAIT',(-5.8,52.5,-210),'separate future abstract transport; no boarding physical tram')
marker('CORE_TRANSFER_D09',(-1,52.5,-252),'existing fore-midship axial aft opening;56m catchment offset')
marker('D09_PEDESTRIAN_AXIS', (0,52.5,-216),'4m X-2..2 remains beneath guideway;3.05m underside headroom')
# Source reference-only plane for missing lower floor. It is explicitly excluded from exports.
ref=collections['UNEXPORTED_REFERENCE_AND_STUDIO']
box('UNEXPORTED_MISSING_LOWER_FLOOR_DIAGRAM',(-5.9,52.38,-218.35),(3.8,.24,44.3),stone,'diagram only; not runtime floor',collection=ref)
box('UNEXPORTED_EXISTING_D09_AXIS', (0,52.38,-216),(8,.24,76),stone,'existing compiled floor reference',collection=ref)

# Original compact player/service cart tram. Physical fittings; no duplicate cart, inventory or controller.
current=collections['TRAM_EDITABLE_COMPONENT']
box('Tram_Floor', (0,-.11,0),(2.6,.22,4.8),metal,'moving vehicle floor','moving_shape_candidate')
box('Tram_AntiSlip_Deck',(0,.009,0),(2.42,.018,4.58),rubber,'standing/docking deck','no_collision_detail')
for z in [-2.26,2.26]:
 box('Tram_End_Bumper_'+str(z),(0,.37,z),(2.7,.35,.36),orange,'vehicle end bumper','moving_shape_candidate')
 box('Tram_End_Sill_'+str(z),(0,1.10,z),(2.6,.20,.20),metal,'end enclosure sill','moving_shape_candidate')
 for x in [-1.25,1.25]:tube('Tram_Corner_'+str((x,z)),(x,.12,z),(x,2.60,z),.10,ivory,'vehicle corner frame','moving_shape_candidate')
 box('Tram_End_Guard_'+str(z),(0,.67,z),(2.4,.6,.08),ivory,'end enclosure','moving_shape_candidate')
 box('Tram_End_Glazing_'+str(z),(0,1.77,z),(2.35,1.18,.05),glass,'end glazing','moving_shape_candidate')
# Port opening2.4m long; no single collision fills this aperture.
for z in [-1.74,1.74]:
 box('Tram_PortPocket_'+str(z),(-1.29,1.12,z),(.11,2.20,1.08),ivory,'port doorway pocket','moving_shape_candidate')
for z in [-1.22,1.22]:tube('Tram_Door_Post_'+str(z),(-1.29,.05,z),(-1.29,2.65,z),.055,metal,'door frame','moving_shape_candidate')
box('Tram_Port_Header',(-1.29,2.61,0),(.15,.20,2.55),metal,'doorway header','moving_shape_candidate')
box('Tram_Starboard_LowerWall',(1.29,.58,0),(.12,1.0,4.50),ivory,'vehicle side enclosure','moving_shape_candidate')
for z in [-1.4,0,1.4]:tube('Tram_Starboard_Rib_'+str(z),(1.28,1.0,z),(1.28,2.60,z),.065,metal,'glazing rib','moving_shape_candidate')
box('Tram_Starboard_Glazing',(1.29,1.80,0),(.06,1.35,4.50),glass,'side glazing','moving_shape_candidate')
box('Tram_Layered_Canopy',(0,2.75,0),(2.65,.24,4.75),ivory,'vehicle roof','moving_shape_candidate')
box('Tram_Coral_Roof_Reveal',(0,2.60,0),(2.47,.055,4.57),orange,'vehicle ceiling','no_collision_detail')
for x in [-.86,.86]:
 for z in [-1.50,1.50]:tube('Tram_Wheel_'+str((x,z)),(x-.09,-.20,z),(x+.09,-.20,z),.16,rubber,'rolling wheel visual','no_collision_detail',sides=12)
# Compact rear-facing operator perch leaves central cart turning/boarding floor open.
box('Tram_Operator_Perch',(0,.42,-1.78),(1.00,.72,.46),wood,'operator perch','moving_shape_candidate')
box('Tram_Operator_Pad',(0,.82,-1.78),(1.04,.14,.48),orange,'operator support','moving_shape_candidate')
box('Tram_Control_Pedestal',(0,1.03,-2.12),(.76,.28,.26),ivory,'control mounting','moving_shape_candidate')
for x in [-.51,.51]:
 box('Cart_Restraint_Rail_'+str(x),(x,.07,.93),(.08,.14,1.52),metal,'cart bay restraint rail','moving_shape_candidate')
 for z in [.26,1.55]:box('Cart_Restraint_Anchor_'+str((x,z)),(x,.17,z),(.15,.2,.10),orange,'future physical clamp mounting','moving_shape_candidate')
marker('TRAM_PORT_DOOR_SILL',(-1.3,0,0),'2.4m opening; bridge gap0.9m at station')
marker('TRAM_PLAYER_STANCE',(0,0,-.65),'actual0.3m-radius player fit candidate')
marker('TRAM_EXISTING_CART_DOCK',(0,0,.93),'retain custodian_cart_001 and existing four product identities')
marker('TRAM_EXISTING_CONTROL_MOUNT',(0,1.13,-2.02),'root-controlled E interface; no new input controller')
marker('TRAM_LAMP_DATUM',(0,2.45,0),'bounded existing light manager')
# Posed vehicle is linked native reference only, actual component remains local pivot0.
for ob in list(current.objects):
 dup=ob.copy();ref.objects.link(dup);dup.name='UNEXPORTED_POSED_'+ob.name;dup.location+=Vector(B((0,56.1,-216)))
current.hide_render=True
# Three individually fitted core/catchment stations. All are source-only candidates.
station_interfaces=[]
D10compiled=json.loads((R/'Game/data/generated/structural_meshes.json').read_text())
def covered(q,r):
 def sg(a,b,c):return (a[0]-c[0])*(b[1]-c[1])-(b[0]-c[0])*(a[1]-c[1])
 for t in r['triangles']:
  v=[sg(q,t[0],t[1]),sg(q,t[1],t[2]),sg(q,t[2],t[0])]
  if not(min(v)<-1e-7 and max(v)>1e-7):return True
 return False

def roof_hanger(prefix,x,z):
 own=[r['id'] for r in D10compiled['regions'] if r['floor_y']==61 and covered((x,z),r)]
 if len(own)!=1:raise AssertionError(('No unique D10 hanger receiver',prefix,x,z,own))
 box(prefix+'_Hanger',(x,58.34,z),(.10,4.98,.10),metal,'source upper floor suspension to actual D10 underside')
 box(prefix+'_CeilingBearing',(x,60.775,z),(.24,.07,.36),metal,'named D10 slab underside receiving pad')
 marker(prefix+'_D10_RECEIVER',(x,60.76,z),'existing D10 slab owner '+own[0]+'; load/capacity not certified')
 return {'xyz':[x,60.76,z],'owner':own[0]}

def copy_emergency(prefix,delta,co):
 for ob in list(collections['FORE_MIDSHIP_STATIC_SOURCE'].objects):
  if ob.type!='MESH' or not ob.name.startswith('Emergency_') or ob.name=='Emergency_TopApproach':continue
  ps=[G(ob.matrix_world@v.co) for v in ob.data.vertices];ps=[(a,b,c+delta) for a,b,c in ps]
  mesh(prefix+ob.name,ps,[tuple(f.vertices) for f in ob.data.polygons],ob.data.materials[0],ob['role'],ob['collision_policy'],collection=co)

def core_station(label,core_z,catch_z,asset,central=False):
 global current
 co=collections[label+'_STATIC_SOURCE'];current=co;pr=label+'__';receivers=[]
 copy_emergency(pr,core_z+208,co)
 # Emergency landing has an actual wide return around the local cabin rear.
 box(pr+'Stair_BroadReturn',(-1.875,55.975,core_z-25.8),(5.75,.25,2.4),stone,'wide emergency stair top return')
 box(pr+'Stair_EastCabin_Bypass',(-1.1,55.975,core_z-20.9),(4.4,.25,7.4),stone,'4m-clear upper return around local boarding lift')
 guard(pr+'Return_Outer',-3.24,core_z-24.6,core_z-17.2,56.1);guard(pr+'Return_Inner',1.04,core_z-24.6,core_z-17.2,56.1)
 box(pr+'Broad_LocalLanding',(-3.4,55.975,core_z-15.1),(8.8,.25,4.2),stone,'level lift/stair turn at core open front')
 # Local cabin is outside existing core footprint. Standard controller/cabin reuse only.
 gz=core_z-17.2
 for x in [-7.7,-3.5]:box(pr+'LiftHousingSide_'+str(x),(x,55.89,gz-1.8),(.12,7.22,3.72),ivory,'lift enclosure side')
 box(pr+'LiftHousingRear',(-5.6,55.89,gz-3.7),(4.3,7.22,.12),ivory,'lift enclosure rear')
 box(pr+'LiftPitPan',(-5.6,52.24,gz-1.8),(4.3,.08,3.92),metal,'pit source; bounded lower recess required')
 box(pr+'LiftCap',(-5.6,59.39,gz-1.8),(4.3,.18,3.92),metal,'boarding lift roof cap')
 marker(pr+'COMMONS_LIFT_ROOT',(-5.6,0,gz),'yaw+PI/2, localgate(0,0); heights52.5/56.1; two distinct G4 local stop IDs')
 marker(pr+'LOWER_LIFT_GATE',(-5.6,52.5,gz),'lower missing-only annex landing required')
 marker(pr+'UPPER_LIFT_GATE',(-5.6,56.1,gz),'source upper broad landing')
 marker(pr+'LOWER_STAIR_ARRIVAL',(-6.25,52.5,core_z-24.6),'lower missing-only annex landing required')
 # Outside-core annex piers bear on already installed8m axial slab, leaving X-2..2 clear.
 for i,z in enumerate([core_z-31,core_z-25,core_z-17]):
  for x in [-2.4,2.4]:
   box(pr+'Annex_Footpad_%s_%s'%(i,x),(x,52.54,z),(.42,.08,.75),metal,'actual D09 axial slab contact')
   box(pr+'Annex_Pier_%s_%s'%(i,x),(x,54.12,z),(.30,3.08,.4),ivory,'pier to existing axial slab')
  box(pr+'AnnexCrossbearer_%s'%i,(-2.6,55.7,z),(10.3,.3,.5),metal,'annex cantilever to actual axial piers')
 # Core-side upper connector uses the existing outward wall as its edge.
 end=catch_z-3 if central else core_z-2
 box(pr+'Upper_Port_CoreConnector',(-5.585,55.975,(core_z-13+end)/2),(4.27,.25,end-(core_z-13)),stone,'4m-clear elevated port connector; existing lower gates/stairs unchanged')
 guard(pr+'Upper_Core_InnerGuard',-3.5,core_z-13,end,56.1)
 for i,z in enumerate([core_z-11,core_z-4,core_z+3]+([core_z+12,core_z+19,catch_z-3] if central else [])):
  for x in [-7.62,-3.6]:receivers.append(roof_hanger(pr+'CoreRoof_%s_%s'%(i,x),x,z))
 if central:
  px=-4.9;edge=-2.2;track_x=0;platformx=(-7.6,-2.2);trackz=(-72,-56)
  box(pr+'Boarding_Pod',(px,55.975,catch_z),(5.4,.25,6),stone,'6m central catchment platform on apron')
  guard(pr+'Platform_OuterGuard',-7.53,catch_z-3,catch_z+3,56.1)
 else:
  px=.8;edge=3.4;track_x=5.6;platformx=(-1.8,3.4);trackz=(core_z-13,core_z+20)
  box(pr+'Boarding_Pod',(px,55.975,catch_z),(5.2,.25,6),stone,'6m station between source shaft and stair intervals')
  box(pr+'Port_TransverseConnector',(-4.7,55.975,core_z),(5.8,.25,4),stone,'level port upper transfer to6m boarding pod')
  guard(pr+'Platform_BackGuard',-1.74,catch_z-3,catch_z-2,56.1);guard(pr+'Platform_BackGuardSouth',-1.74,catch_z+2,catch_z+3,56.1)
 for z0,z1 in [(catch_z-3,catch_z-1.2),(catch_z+1.2,catch_z+3)]:guard(pr+'Boarding_Edge_'+str(z0),edge,z0,z1,56.1)
 for z in [catch_z-1.2,catch_z+1.2]:box(pr+'Boarding_Post_'+str(z),(edge,57.35,z),(.18,2.5,.18),ivory,'deep boarding portal frame')
 box(pr+'Boarding_Header',(edge,58.6,catch_z),(.2,.18,2.64),metal,'deep boarding portal header')
 box(pr+'LocalCanopy',(px,59.3,catch_z),(5.4,.25,6.15),ivory,'profiled6m station canopy')
 box(pr+'Canopy_Recess',(px,59.11,catch_z),(5.1,.07,5.7),orange,'recessed coral station ceiling')
 for x in [platformx[0]+.25,platformx[1]-.25]:
  for z in [catch_z-2.7,catch_z+2.7]:receivers.append(roof_hanger(pr+'PodRoof_'+str((x,z)),x,z))
 marker(pr+'BOARDING_GATE_MOUNT',(edge,56.1,catch_z),'root-controlled gate and interlocked0.9m bridge not supplied')
 marker(pr+'CORE_TRANSFER_D09',(-1,52.5,core_z-13),'existing public-core front axial opening; all current lift/stair travel preserved')
 marker(pr+'CATCHMENT',(track_x,56.1,catch_z),'retained longitudinal catchment; trackX offset unadopted except central protected axis')
 # Short source-only guideway; held joins are separate from installed destinations.
 zz=[trackz[0]+4*i for i in range(int((trackz[1]-trackz[0])/4))]+[trackz[1]]
 for i,(a,b) in enumerate(zip(zz,zz[1:])):
  box(pr+'GuidewayWeb_'+str(i),(track_x,55.615,(a+b)/2),(3.2,.13,b-a),metal,'local guideway web')
  for xx in [-.86,.86]:box(pr+'GuideRail_%s_%s'%(i,xx),(track_x+xx,55.71,(a+b)/2),(.09,.06,b-a),metal,'wheel rail')
 if central:
  for i,z in enumerate([-72,-68,-64]):
   for x in [-2.4,2.4]:
    box(pr+'Tram_Footpad_%s_%s'%(i,x),(x,52.54,z),(.42,.08,.75),metal,'actual D09 apron slab contact')
    box(pr+'Tram_Pier_%s_%s'%(i,x),(x,54.12,z),(.3,3.08,.4),ivory,'actual apron receiving pier')
   box(pr+'Tram_BeamWeb_%s'%i,(0,55.615,z),(5.1,.13,.5),metal,'wheel-channel crossbearer continuous web')
   for j,(a,b) in enumerate([(-2.55,-1.04),(-.68,.68),(1.04,2.55)]):box(pr+'Tram_Flange_%s_%s'%(i,j),((a+b)/2,55.765,z),(b-a,.17,.5),metal,'flanges outside rolling wheels')
 else:
  for i,z in enumerate([core_z-11,core_z-4,core_z+3,core_z+11,core_z+18]):
   for x in [4.08,7.12]:receivers.append(roof_hanger(pr+'GuidewayRoof_%s_%s'%(i,x),x,z))
 # Small screened future NPC waiting edge sits away from physical tram boarding.
 box(pr+'GuestWaitScreen',(-7.3,53.5,core_z-15.5),(.10,2,2.0),ivory,'separate abstract guest waiting screen')
 marker(pr+'GUEST_ABSTRACT_WAIT',(-5.6,52.5,core_z-15),'separate finite-time NPC transit; controller not supplied')
 for z in [catch_z-2.25,catch_z+2.25]:
  box(pr+'Perch_'+str(z),(platformx[0]+.46,56.4,z),(.64,.6,.72),wood,'resting edge outside4m route')
  box(pr+'Lamp_Backplate_'+str(z),(platformx[0]+.12,58.15,z),(.15,.34,.40),metal,'source lamp backplate')
  marker(pr+'LIGHT_DATUM_'+str(z),(platformx[0]+.23,58.15,z),'bounded existing lighting manager candidate')
 for z in trackz:marker(pr+'GUIDEWAY_INTERFACE_'+str(z),(track_x,56.1,z),'HOLD: source-only local span; unadopted full-line joins')
 station_interfaces.append({'label':label,'asset':asset,'catchment_z':catch_z,'actual_core_z':core_z,'source_only':True,'boarding_platform_xz':[platformx[0],catch_z-3,platformx[1],catch_z+3],'guideway_local_x':track_x,'guideway_local_z':list(trackz),'guideway_side_status':'central axis portion retains governing polyline' if central else 'UNADOPTED core-side join candidate; full-line decision held','root_lift_origin':[-5.6,0,gz],'root_lift_yaw_rad':math.pi/2,'reuse_cabin':'AST-CIR-003.glb','reuse_controller':'commons_lift.gd','floor_heights':[52.5,56.1],'stop_ids':['G4_'+label+'_LOWER','G4_'+label+'_BOARDING'],'deck_numbers':[9,9],'local_gate_origin_xz':[0,0],'lower_missing_only_strip_xz':[-7.8,core_z-32.5,-4,core_z-12.9],'lower_lift_recess_xz':[-7.8,gz-3.8,-3.4,gz+.2],'axial_recess_area_m2':2.4,'roof_receivers':receivers,'structural_status':'geometric source receivers only; capacity/floor connections/actual-main fit held','new_lower_floor_exported':False,'boarding_gate_bridge_and_controls':'mounts only; root integration required'})
core_station('FORWARD',-432,-432,'AST-TRM-G4-004_forward_source.glb')
core_station('CENTRAL',-100,-72,'AST-TRM-G4-005_central_source.glb',True)
core_station('AFT',432,432,'AST-TRM-G4-006_aft_source.glb')
# Second independently placed catchment, mirrored axial span only. No whole-line claim.
aft=collections['AFT_MIDSHIP_STATIC_SOURCE']; aft_rows=[]
for ob in list(collections['FORE_MIDSHIP_STATIC_SOURCE'].objects):
 if ob.type=='MESH':
  vs=[G(ob.matrix_world@v.co) for v in ob.data.vertices];vs=[(p[0],p[1],-p[2]) for p in vs];fs=[tuple(reversed(tuple(poly.vertices))) for poly in ob.data.polygons]
  no=mesh('Aftmid_'+ob.name,vs,fs,ob.data.materials[0],ob['role'],ob['collision_policy'],collection=aft);aft_rows.append(no)
 else:
  p=G(ob.location);p=(p[0],p[1],-p[2]);p=(-1,52.5,259) if ob.name=='CORE_TRANSFER_D09' else p
  marker('Aftmid_'+ob.name,p,ob['datum_kind'].replace('aft opening;56m','front opening;56m'),collection=aft)
# Export three compact GLBs, preserve original per-part editable native.
for name,co,file in [('station',collections['FORE_MIDSHIP_STATIC_SOURCE'],'AST-TRM-G4-001_fore_midship_source.glb'),('vehicle',collections['TRAM_EDITABLE_COMPONENT'],'AST-TRM-G4-002_cart_tram_component.glb'),('aftmid',collections['AFT_MIDSHIP_STATIC_SOURCE'],'AST-TRM-G4-003_aft_midship_source.glb'),('forward',collections['FORWARD_STATIC_SOURCE'],'AST-TRM-G4-004_forward_source.glb'),('central',collections['CENTRAL_STATIC_SOURCE'],'AST-TRM-G4-005_central_source.glb'),('aft',collections['AFT_STATIC_SOURCE'],'AST-TRM-G4-006_aft_source.glb')]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in co.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=next(iter(co.objects))
 bpy.ops.export_scene.gltf(filepath=str(OUT/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
# Bounded analytic fit metadata; source-only, controllers/collision are receiving obligations.
meta={'schema':'astraea.group4.source_batch.v1','status':'SOURCE_ONLY_NOT_INSTALLED','scope':'five source-only station candidates, bounded separate local guideway spans and original cart-tram component; no complete line or Group4 completion','family':FAMILY,'ids':IDS,'manifest_baseline_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),'units':'Godot metres XYZ Y-up','datum':{'deck':'D09','lower_y':52.5,'boarding_y':56.1,'guideway_soffit_y':55.55,'rail_head_y':55.74,'vehicle_floor_y':56.1},'station':{'catchment_z':-216,'actual_core_z':-272,'guideway_xz_bounds':[-2,-250,2,-182],'boarding_bounds_xyz':[[-7.6,55.85,-228],[-2.2,56.1,-204]],'canopy_top_y':59.425,'pedestrian_prism':[[-2,52.5,-250],[2,55.55,-182]],'four_m_axis_preserved':True,'source_guideway_joins':[[0,56.1,-250],[0,56.1,-182]],'join_status':'HOLD; upstream core conflict and downstream central curve not solved','emergency_stair':{'rise':3.6,'risers':24,'riser_m':.15,'tread_m':.3,'clear_flight_width':2.4,'midlanding_depth':1.8},'lift':{'reuse_script':'Game/scripts/commons_lift.gd','reuse_cabin':'Game/assets/models/AST-CIR-003.glb','root_origin':[-5.6,0,-200],'root_yaw_rad':-math.pi/2,'local_gate_origin_xz':[0,0],'floor_heights':[52.5,56.1],'deck_numbers':[9,9],'stop_ids':['G4_FOREMID_LOWER','G4_FOREMID_BOARDING'],'stop_names':['D09 promenade','Fore-midship boarding'],'stop_codes':['L','B'],'cabin_roof_top_upper_y':59.04,'cap_underside_y':59.30,'upper_roof_gap_m':.26,'shaft_swept_bounds_xyz':[[-7.601,52.319,-200.001],[-3.599,59.041,-196.399]],'lower_slab_recess_bounds_xz':[-7.8,-200.2,-3.4,-196.2],'existing_axial_slab_overlap_recess_m2':2.4,'status':'NOT_INSTALLED; root must verify rotating reused lift preserves button rays and group carry behavior'},'boarding_bridge':{'vehicle_sill_x':-1.3,'platform_edge_x':-2.2,'reach_m':.9,'width_z_m':2.4,'status':'mount datum only; interlocked moving bridge/controller not supplied'},'lower_floor':{'proposed_missing_strip_xz':[-7.8,-240.5,-4,-196.2],'area_before_lift_recess_m2':168.34,'supplied':False,'reason':'root compiler must compute missing-only fill and bounded pit cut; reference plane excluded from exports'},'support':'guideway source piers terminate on existing D09 axial slab x±2.4; platform cantilevers/braces share them. Lower annex receiving and structural capacity remain held.'},'vehicle':{'body_bounds_xyz':[[-1.35,-.36,-2.44],[1.35,2.87,2.44]],'reserved_straight_sweep_width_m':4,'door_port_opening_z':[-1.2,1.2],'cart_dock_xyz':[0,0,.93],'player_stance_xyz':[0,0,-.65],'controller':'NONE supplied; root owns existing world interactions and eventual transport','state':'cart and loose stock stay persistent actors. No second cart/product meshes exported.'},'source_material_sha256':texture_pins,'reference_application':{'pixels_opened':['DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-1(1).png','DesignArchive/References/Uploaded_46/04/2.png','DesignArchive/References/Historical_Concepts_And_Blueprints/Futuristic Luxury Space Atrium Garden.png'],'lessons':['layered deep boarding portal, thick profiled platform/canopy, integrated lamps and perches','public/source-side movement separate, actual offset-core connection retained','central hero-tree bypass retained; no substitute port line']},'open':['all other four site-specific stations','full line and core detours','vehicle curvature and body-end sweep','new lower floor/receiving foundation/pit','actual controller integration, powered doors and interlocked bridge','all-five normal boarding, cart/stock motion, pause and persistence','guest abstract transit vestibules and finite-time routing','remaining destination/neighborhood access joins','actual-main stationary fit and visual receiving, full-height hull and structural capacity','final materials/lighting/species/user-GPU acceptance']}
meta['aft_midship']={'asset':'AST-TRM-G4-003_aft_midship_source.glb','mirror_method':'source geometry(x,y,z)→(x,y,-z), face winding reversed and normals recomputed','catchment_z':216,'actual_core_z':272,'guideway_xz_bounds':[-2,182,2,250],'platform_bounds_xyz':[[-7.6,55.85,204],[-2.2,56.1,228]],'core_transfer_xyz':[-1,52.5,259],'actual_core_boundary_note':'Aft-midship begins259, not mirrored252; native transfer marker explicitly corrected','lift_root_origin':[-5.6,0,200],'lift_root_yaw_rad':math.pi/2,'floor_heights':[52.5,56.1],'stop_ids':['G4_AFTMID_LOWER','G4_AFTMID_BOARDING'],'local_gate_origin_xz':[0,0],'lower_missing_floor_strip_xz':[-7.8,196.2,-4,240.5],'lower_lift_recess_xz':[-7.8,196.2,-3.4,200.2],'existing_axial_slab_overlap_recess_m2':2.4,'status':'SOURCE_ONLY_NOT_INSTALLED; independent receiving checks required','same_remaining_holds_as_fore_midship':True}
meta['other_three_stations']=station_interfaces
meta['open'][0]='all five station receiving/boarding/normal arrival gates remain open; source candidates are not installed'
(OUT/'BATCH_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
rows=[]
for ob in parts:
 pts=[Vector(G(ob.matrix_world@v.co)) for v in ob.data.vertices];rows.append({'mesh':ob.name,'collection':ob.users_collection[0].name,'role':ob['role'],'policy':ob['collision_policy'],'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'faces':len(ob.data.polygons)})
(OUT/'MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n')
# Native contains actual authored source plus explicitly excluded diagrams and review-only pose.
for ob in list(parts)+markers:
 if ob.type=='MESH':ob.select_set(False)
def mov(ob):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 ref.objects.link(ob)
def look(ob,p):ob.rotation_euler=(Vector(B(p))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=B((12,63,-236)));cam=bpy.context.object;mov(cam);cam.name='SOURCE_REVIEW_EYE';cam.data.lens=35;look(cam,(-3,55.7,-216));scene.camera=cam
for p,power,size in [((-9,65,-219),1300,12),((8,64,-222),1700,15),((-2,60,-194),900,8)]:
 bpy.ops.object.light_add(type='AREA',location=B(p));o=bpy.context.object;mov(o);o.data.energy=power;o.data.size=size;look(o,(-3,55.5,-216))
scene.world.color=(.14,.14,.14);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=880;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
bpy.ops.file.make_paths_relative()
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Group4_Foremid_Tram_Source.blend'),compress=True)
if '--no-render' not in sys.argv:
 scene.render.filepath=str(OUT/'SOURCE_REVIEW_station_overview.png');bpy.ops.render.render(write_still=True)
 cam.location=B((-5.2,57.75,-225));look(cam,(-1.8,57.25,-214));cam.data.lens=24;scene.render.filepath=str(OUT/'SOURCE_REVIEW_station_eye.png');bpy.ops.render.render(write_still=True)
 for ob in collections['FORE_MIDSHIP_STATIC_SOURCE'].objects:
  if any(k in ob.name for k in ['Canopy_Profiled_Crown','Canopy_Recessed_Coral_Band','BoardingLift_Header']):ob.hide_render=True
 cam.location=B((-1,92,-215));look(cam,(-1,52,-215));cam.data.type='ORTHO';cam.data.ortho_scale=76;scene.render.filepath=str(OUT/'SOURCE_REVIEW_station_plan.png');bpy.ops.render.render(write_still=True)
print('GROUP4_SOURCE_BATCH '+json.dumps({'native_members':len(parts),'aft_station_members':len(aft.objects),'station_members':len(collections['FORE_MIDSHIP_STATIC_SOURCE'].objects),'vehicle_members':len(collections['TRAM_EDITABLE_COMPONENT'].objects),'outputs':str(OUT)}))
