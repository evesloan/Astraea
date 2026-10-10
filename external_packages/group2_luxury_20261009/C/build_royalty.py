"""Royalty household with lower conversation room and private upper rest/viewing gallery.
Source-only, no preview slab, exterior opening, registry or controller adoption.
Run only through heavy.py. Retained furniture is rigid; fitted shapes follow
the actual allocation profile and every saved/exported vertex is checked.
"""
import bpy,bmesh,pathlib,json,hashlib,math,sys,runpy
from mathutils import Matrix,Vector
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from premium_frame import PremiumFrame
from source_paths import section
from editable_label import repair_label
unit=int(sys.argv[sys.argv.index('--')+1]);target_row,target_o,_,_=section(unit)
assert target_row['reservation']['tier']=='royalty' and target_row['identity']['existing_partial_construction'] is None
assert not (target_o/f'{unit}_royalty.blend').exists(),'Preserve existing source candidate'
# Use the already inspected pinned importer/palette/primitives without executing
# its876 architecture, views or output writes. __file__ remains this recipe.
seed=R/'build_first_deluxe.py';seed_sha=hashlib.sha256(seed.read_bytes()).hexdigest()
exec(compile(seed.read_text().split('# Weighted compartment envelope')[0],str(seed),'exec'),globals())
row=target_row;reservation=row['reservation'];O=target_o;O.mkdir(parents=True,exist_ok=True)
assert len(row['identity']['proposed_rest_slot_ids'])==8
screen=next(x for x in json.loads((R/'ALL_81_NEIGHBOUR_SCREEN.json').read_text())['records'] if x['source_envelope_index']==unit)
if screen['screen_status']!='NO_AABB_INTERSECTIONS':
 p=next(x for x in json.loads((R/'PRECISE_RETAINED_TIDAL_INTERSECTIONS.json').read_text())['records'] if x['source_envelope_index']==unit)
 assert p['status']=='AABB_CANDIDATE_CLEARED_BY_ACTUAL_TRIANGLES' and not screen['structural_mesh_aabb_contacts']
frame=PremiumFrame(reservation['proposed_floor_boundary']);assert abs(frame.length-22)<.001
def xyz(u,v,h):return Vector(frame.blender(u,v,h))
def w(u,v,h):return frame.world(u,v,h)
def put(aid,u,v,h=0,yaw=0,label=None):return asset(aid,u,v,h,yaw+frame.angle(v)-math.pi,label)
def rigid_box(name,u,v,du0,du1,dv0,dv1,h0,h1,role,kind='fitted_privacy'):
 points=[frame.inverse(frame.rigid(u,v,du,dv,h)) for h in [h0,h1] for du,dv in [(du0,dv0),(du1,dv0),(du1,dv1),(du0,dv1)]]
 return mesh(name,points,faces,role,kind)
def fixture(name,u,v,h,target,mount,energy=160):
 ob=box(name+'_Bracket',u-.09,u+.09,v-.09,v+.09,h,mount+.025,'champagne_metal','fixture');ob['source_mount_target']=target
 box(name+'_Lens',u-.22,u+.22,v-.22,v+.22,h-.04,h+.015,'lens','fixture')
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=(1,.78,.53);d.shape='DISK';d.size=1.1;ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=xyz(u,v,h-.07);lights.append(ob);marker(name+'_Light',u,v,h-.07,'fixture_light',energy_w=energy)
def profile_band(name,u0,u1,v0,v1,h0,h1,role,kind='architecture'):
 # Include every actual profile knot; custom fitted meshes may follow it.
 vs=sorted({v0,v1,*[(z-frame.start)/frame.vsign for x,z in frame.poly if v0<(z-frame.start)/frame.vsign<v1]})
 polygon=[(u0,v) for v in vs]+[(min(u1,frame.depth(v)-.30),v) for v in reversed(vs)]
 simplified=True
 while simplified and len(polygon)>3:
  simplified=False
  for j in range(len(polygon)):
   a=xyz(*polygon[j-1],0);b=xyz(*polygon[j],0);c=xyz(*polygon[(j+1)%len(polygon)],0)
   if (b-a).cross(c-b).length<.0001 and (b-a).dot(c-b)>=0:
    polygon.pop(j);simplified=True;break
 return prism(name,polygon,h0,h1,role,kind)
# A deep inner threshold opens to a branching household gallery, with three
# separated rest niches and a high outer conversation room.
for label,v0,v1 in [('InnerForePartyReturn',.06,4.85),('InnerAftPartyReturn',8.65,21.94)]:profile_band(label,.06,.30,v0,v1,0,9.05,'ivory_enamel')
profile_band('ArrivalHeader',.06,.30,4.85,8.65,2.80,9.05,'ivory_enamel')
put('AST-DOR-002',1.05,6.80,0,math.pi/2,'PrivateEntry')
box('ArrivalForePocket',.48,1.80,4.72,5.00,0,2.85,'warm_walnut');box('ArrivalAftPocket',.48,1.80,8.50,8.78,0,2.85,'warm_walnut')
box('ArrivalLoweredCrown',.48,2.55,4.72,8.78,2.85,3.12,'ivory_enamel');marker('entry',1.10,6.80,0,'proposed_shared_RMB_focus_E_entry',controller_adoption='Root existing vocabulary only')
for label,v0,v1 in [('ForePartyWall',.06,.30),('AftPartyWall',21.70,21.94)]:profile_band(label,.06,100,v0,v1,0,9.05,'ivory_enamel')
# The outward enclosure is opaque: the atlas is a plan guide, not proof of
# per-height real exterior frontage. Root/Group7 own aperture coordination.
vs=sorted({.30,21.70,*[(z-frame.start)/frame.vsign for x,z in frame.poly if .30<(z-frame.start)/frame.vsign<21.70]})
outer=[(frame.depth(v)-.30,v) for v in vs]+[(frame.depth(v)-.06,v) for v in reversed(vs)];prism('HeldFrontageOpaqueEnclosure',outer,0,9.05,'ivory_enamel')
# Rigid private bath frame fits its assets and actual wall mount plane.
bu,bv=3.70,2.87
bath_shapes=[('BathRear',1.90,5.05,.60,.82),('BathWest',1.90,2.12,.60,3.90),('BathEast',4.83,5.05,.60,3.90),('BathFrontLeft',1.90,2.88,3.68,3.90),('BathFrontRight',4.02,5.05,3.68,3.90)]
for name,a,b,c,d in bath_shapes:rigid_box(name,bu,bv,a-3.48,b-3.48,c-2.27,d-2.27,0,2.88,'ivory_enamel')
rigid_box('BathDoorHead',bu,bv,2.88-3.48,4.02-3.48,3.68-2.27,3.90-2.27,2.29,2.88,'ivory_enamel')
def bath_put(aid,u,v,yaw,label):
 p=frame.inverse(frame.rigid(bu,bv,u-3.48,v-2.27,0));return asset(aid,*p,yaw+frame.angle(bv)-math.pi,label)
bath_put('AST-DOR-001',3.45,3.80,0,'BathPrivacy');bath_put('AST-SAN-001',4.85,2.80,math.pi,'Vanity')
normal=Vector((math.cos(frame.angle(bv)),0,-math.sin(frame.angle(bv))));mount=frame.rigid(bu,bv,4.83-3.48,2.80-2.27,0)
imports[-1]['mount_contact_plane']={'normal_xyz':list(normal),'point_xyz':[mount[0],mount[2],-mount[1]],'support_object':'BathEast'}
bath_put('AST-SAN-002',2.49,2.80,-math.pi/2,'Toilet');bath_put('AST-SAN-003',3.55,1.54,0,'Shower')
rigid_box('ShowerRearServiceFacing',bu,bv,2.91-3.48,4.19-3.48,.82-2.27,.865-2.27,.03,2.38,'ivory_enamel')
rigid_box('BathAcousticCover',bu,bv,1.90-3.48,5.05-3.48,.60-2.27,3.90-2.27,2.88,3.06,'ivory_enamel');fixture('BathOpal',bu,bv,2.75,'BathAcousticCover',2.88,95)
# Fore, outer fore and aft-facing rest branches preserve six proposed IDs.
rest_specs=[(7.30,2.70,1,0),(13.00,3.50,1,0),(11.60,19.20,-1,4.5),(15.60,19.20,-1,4.5)]
for j,(u,v,facing,hbase) in enumerate(rest_specs):
 put('AST-SLP-002',u,v,hbase,math.pi if facing==1 else 0,f'RestAlcove{j+1}')
 dv0,dv1=sorted([-1.65*facing,-1.43*facing]);rigid_box(f'RestHeadBacking{j}',u,v,-1.50,1.50,dv0,dv1,hbase,hbase+2.86,'warm_walnut')
 rigid_box(f'RestSideCheek{j}',u,v,-1.58,-1.36,-1.65,1.62,hbase,hbase+2.72,'ivory_enamel');rigid_box(f'RestCrown{j}',u,v,-1.58,1.50,-1.65,1.62,hbase+2.72,hbase+2.95,'ivory_enamel')
 p=frame.inverse(frame.rigid(u,v,1.63,-1.10*facing,hbase));asset('AST-GST-003',*p,math.pi/2+frame.angle(v)-math.pi,f'PersonalStow{j}')
 for k,du in enumerate([-.46,.46]):
  p=frame.inverse(frame.rigid(u,v,du,0,hbase+.69));marker(f'rest_{j*2+k+1:02}',*p,'proposed_rest_anchor',reservation_id=row['identity']['proposed_rest_slot_ids'][j*2+k])
 fixture(f'RestReading{j}',u,v,hbase+2.60,f'RestCrown{j}',hbase+2.72,85)
# A six-chair private table between the three branches, with a real full
# kitchen along the inner edge and separate preparation/used-return stances.
put('AST-HSP-001',1.70,9.40,0,math.pi/2,'FittedKitchen')
bev=frame.inverse(frame.rigid(1.70,9.40,.02,2.10,.90));asset('AST-HSP-003',*bev,math.pi/2+frame.angle(9.40)-math.pi,'Beverage')
box('KitchenTallColdStorage',.80,1.85,12.30,13.30,0,2.30,'warm_walnut','kitchen');box('ColdStorageDoor',1.86,1.90,12.35,13.25,.12,2.22,'ivory_enamel','kitchen');box('KitchenUsedReturn',.80,1.85,8.30,9.10,0,.90,'warm_walnut','kitchen')
box('KitchenHobTop',1.40,2.10,10.00,10.90,.90,.96,'dark_rubber','kitchen');box('KitchenOvenFront',2.11,2.16,10.00,10.90,.19,.76,'dark_rubber','kitchen');box('KitchenExtraction',1.20,2.20,10.00,10.90,2.30,2.50,'ivory_enamel','kitchen')
oval=[(7.20+1.40*math.cos(2*math.pi*k/28),7.0+math.sin(2*math.pi*k/28)) for k in range(28)];prism('FittedOvalDiningTop',oval,.72,.79,'warm_stone','private_dining')
for j,u in enumerate([6.60,7.80]):box(f'DiningPedestalFoot{j}',u-.36,u+.36,6.60,7.40,0,.075,'warm_walnut','private_dining');box(f'DiningPedestal{j}',u-.22,u+.22,6.65,7.35,.075,.72,'warm_walnut','private_dining')
for name,u,v,yaw in [('N',7.2,5.70,math.pi),('S',7.2,8.30,0),('W1',5.5,6.4,math.pi/2),('W2',5.5,7.6,math.pi/2),('E1',9.1,6.4,-math.pi/2),('E2',9.1,7.6,-math.pi/2)]:put('AST-FUR-002',u,v,0,yaw,'PrivateDiningChair'+name)
arc('CrescentBenchPlinth',(14.80,10.20),1.00,1.86,-1.00,1.00,0,.34,'warm_walnut');arc('CrescentBenchCushion',(14.80,10.20),.96,1.86,-1.00,1.00,.34,.50,'teal_weave');arc('CrescentBenchBack',(14.80,10.20),1.74,1.97,-1.00,1.00,.50,1.18,'oatmeal_weave')
put('AST-FUR-002',11.85,9.00,0,math.pi/2,'ConversationChairA');put('AST-FUR-002',11.85,11.80,0,math.pi/2,'ConversationChairB');put('AST-FUR-003',14.0,10.2,0,0,'ConversationTable')
box('ReadingCounter',9.40,11.25,12.85,13.50,0,.78,'warm_walnut','activity');put('AST-FUR-002',10.35,11.70,0,math.pi,'ReadingChair');put('AST-LIB-006',10.35,13.15,.78,0,'ReadingBooks');box('ReadingBayBacking',9.40,11.25,13.50,13.70,.78,2.90,'warm_walnut','activity')
for j,h in enumerate([1.25,1.83,2.41]):box(f'ReadingShelf{j}',9.40,11.25,13.10,13.50,h,h+.075,'warm_walnut','activity');put('AST-LIB-006',10.25,13.28,h+.075,0,f'ReadingShelfStock{j}')
put('AST-BOT-002',16.70,7.30,.14,0,'PrivatePlant');box('PlantPlinth',16.15,17.25,6.92,7.70,0,.14,'warm_stone')
# Lower private rooms retain human-scaled covers. The outer conversation
# area is a genuinely double-height source volume, with a rear upper gallery.
profile_band('ForeHouseholdCover',.30,100,.30,5.30,3.55,3.73,'ivory_enamel','roof')
profile_band('InnerArrivalCover',.30,10.55,5.30,11.80,3.55,3.73,'ivory_enamel','roof')
profile_band('PavilionRoof',.06,100,.06,21.94,9.05,9.20,'ivory_enamel','roof')
# Cover bearings are at actual enclosure edges and remain inside this unit.
for j,v in enumerate([.40,21.60]):profile_band(f'PavilionRoofBearing{j}',.30,100,v-.09,v+.09,8.88,9.065,'warm_walnut','roof_bearing')
fixture('ArrivalOpal',3.00,6.80,3.34,'InnerArrivalCover',3.55,170)
fixture('PrivateDiningOpal',7.2,7.0,3.34,'InnerArrivalCover',3.55,210)
fixture('KitchenWork',3.1,10.1,3.34,'InnerArrivalCover',3.55,190)
fixture('ConversationOpal',14.8,10.2,8.84,'PavilionRoof',9.05,420)
fixture('UpperGalleryOpal',11.5,14.1,8.84,'PavilionRoof',9.05,230)
# Two flights in a fixed bay. Treads and stringers are editable source
# equipment; Root owns lower/upper receiver slabs and their separate voids.
stair_records=[]
for flight,count,ulo,uhi,vstart,direction,baseh in [(0,13,.70,2.10,15.0,1,0),(1,12,2.65,4.05,18.64,-1,2.34)]:
 for step in range(count):
  lo=min(vstart+direction*step*.28,vstart+direction*(step+1)*.28);hi=max(vstart+direction*step*.28,vstart+direction*(step+1)*.28);h=baseh+(step+1)*.18
  ob=box(f'PrivateStair_F{flight}_Tread_{step:02}',ulo,uhi,lo,hi,h-.08,h,'warm_stone','private_stair')
  stair_records.append({'object':ob.name,'flight':flight,'step':step,'top_h':h,'run_m':.28,'width_m':1.40,'u':[ulo,uhi],'v':[lo,hi]})
box('PrivateStairMidLanding',.70,4.05,18.64,20.05,2.26,2.34,'warm_stone','private_stair')
# Triangulated diagonal stringers bear each flight and the landing.
for flight,ulo,uhi,start,end,h0,h1 in [(0,.73,2.07,15.0,18.64,.08,2.34),(1,2.68,4.02,18.64,15.28,2.34,4.50)]:
 for j,u in enumerate([ulo,uhi-.10]):
  points=[(u,start,h0-.08),(u+.10,start,h0-.08),(u+.10,end,h1-.08),(u,end,h1-.08),(u,start,h0),(u+.10,start,h0),(u+.10,end,h1),(u,end,h1)]
  mesh(f'PrivateStairStringer_F{flight}_{j}',points,faces,'warm_walnut','private_stair')
# Sloping rails follow the flights; posts meet actual tread tops.
for flight,count,ulo,uhi,vstart,direction,baseh in [(0,13,.70,2.10,15.0,1,0),(1,12,2.65,4.05,18.64,-1,2.34)]:
 for step in [0,count//2,count-1]:
  v=vstart+direction*(step+.5)*.28;h=baseh+(step+1)*.18
  box(f'StairRailPost_F{flight}_{step}',ulo-.05,ulo+.05,v-.04,v+.04,h,h+1.0,'champagne_metal','private_stair_guard')
 u=ulo;vs=vstart+direction*.14;ve=vstart+direction*(count-.5)*.28;hs=baseh+.18+1.0;he=baseh+count*.18+1.0
 mesh(f'StairSlopingHandrail_F{flight}',[(x,v,h) for x in [u-.04,u+.04] for v,h in [(vs,hs-.04),(ve,he-.04),(ve,he+.04),(vs,hs+.04)]],faces,'warm_walnut','private_stair_guard')
for flight,count,u,vstart,direction,baseh in [(0,13,2.10,15.0,1,0),(1,12,4.05,18.64,-1,2.34)]:
 for step in [0,count//2,count-1]:
  v=vstart+direction*(step+.5)*.28;h=baseh+(step+1)*.18
  box(f'StairOtherRailPost_F{flight}_{step}',u-.05,u+.05,v-.04,v+.04,h,h+1.0,'champagne_metal','private_stair_guard')
 vs=vstart+direction*.14;ve=vstart+direction*(count-.5)*.28;hs=baseh+.18+1.0;he=baseh+count*.18+1.0
 mesh(f'StairOtherHandrail_F{flight}',[(x,v,h) for x in [u-.04,u+.04] for v,h in [(vs,hs-.04),(ve,he-.04),(ve,he+.04),(vs,hs+.04)]],faces,'warm_walnut','private_stair_guard')
box('StairLandingRearGuard',.65,4.10,20.0,20.08,2.34,3.42,'glass','private_stair_guard')
# Upper bridge meets the proposed floor edge; void guards leave a1.4m exit.
box('PrivateStairUpperLanding',2.65,4.05,14.65,15.28,4.42,4.50,'warm_stone','private_stair')
for name,u0,u1,v0,v1 in [('StairUpperVoidLeft',.57,.65,14.81,20.28),('StairUpperVoidInner',4.16,4.24,14.85,20.28),('StairUpperVoidRear',.60,4.20,20.20,20.28),('StairUpperVoidFore',.60,2.60,14.81,14.89)]:
 box(name+'Panel',u0,u1,v0,v1,4.50,5.58,'glass','upper_guard')
 box(name+'Rail',u0,u1,v0,v1,5.55,5.63,'warm_walnut','upper_guard')
# A front upper balcony protects the overlooking edge, leaving internal
# stair/lift landings separate. These guards bear on a proposed Root slab.
for j,(u0,u1) in enumerate([(.30,12.8),(14.2,17.7)]):
 box(f'UpperViewingGuardFoot{j}',u0,u1,12.06,12.18,4.50,4.60,'warm_walnut','upper_guard')
 box(f'UpperViewingGuardPanel{j}',u0,u1,12.08,12.14,4.60,5.58,'glass','upper_guard')
 box(f'UpperViewingGuardRail{j}',u0,u1,12.04,12.18,5.55,5.63,'warm_walnut','upper_guard')
# The centre interval is filled by a continuous guard, not an unguarded gap.
box('UpperViewingCentreGuard',12.80,14.20,12.08,12.14,4.50,5.58,'glass','upper_guard')
box('UpperViewingCentreRail',12.80,14.20,12.04,12.18,5.55,5.63,'warm_walnut','upper_guard')
# Fitted shaft enclosure starts at lower datum. The retained moving cabin
# is a separately pinned component: its18cm platform pit is explicitly held.
for name,u0,u1,v0,v1 in [('LiftLeft',4.80,4.98,15.86,19.82),('LiftRight',9.02,9.20,15.86,19.82),('LiftRear',4.98,9.02,19.64,19.82)]:
 rigid_box(name,7,16,u0-7,u1-7,v0-16,v1-16,0,7.50,'ivory_enamel','private_lift_shaft')
for j,h0 in enumerate([0,4.5]):
 rigid_box(f'LiftFrontLeft{j}',7,16,-2.0199999999999996,-1.21,-.16,-.02,h0,h0+2.80,'warm_walnut','private_lift_shaft')
 rigid_box(f'LiftFrontRight{j}',7,16,1.2100000000000009,2.0199999999999996,-.16,-.02,h0,h0+2.80,'warm_walnut','private_lift_shaft')
 rigid_box(f'LiftDoorHeader{j}',7,16,-2.0199999999999996,2.0199999999999996,-.16,-.02,h0+2.80,h0+3.00,'warm_walnut','private_lift_shaft')
 marker(f'private_lift_stop_{j}',7.0,15.35,h0,'private_lift_landing_proposal',existing_controller='commons_lift.gd',source_only=True)
rigid_box('LiftShaftCap',7,16,-2.20,2.20,-.14,3.82,7.50,7.70,'ivory_enamel','private_lift_shaft')
put('AST-FUR-002',11.3,14.25,4.5,0,'UpperViewingChairA');put('AST-FUR-002',15.2,14.25,4.5,0,'UpperViewingChairB');put('AST-FUR-003',13.4,14.8,4.5,0,'UpperViewingTable')
box('UpperReadingConsole',9.5,10.15,16.8,20.3,4.5,5.28,'warm_walnut','upper_reading')
put('AST-LIB-006',9.85,18.5,5.28,0,'UpperReadingBooks')
# Floor surfaces are proposals and preview-only; final native/export omit
# every receiver slab. The Root-adopted terrace would rise45cm around the
# lower conversation space, making a pit without cutting belowD17.
upper_floor_proposal={'floor_y':106.5,'boundary':frame.poly,'local_v':[12.0,21.70],'voids':[{'kind':'private_stair','u':[.60,4.20],'v':[14.85,20.20]},{'kind':'private_lift','u':[4.95,9.05],'v':[15.98,19.65]}],'adoption':'Root-owned slab/support/hole proposal only'}
upper_floor_proposal['private_lift_void_world_xz']=[[p[0],-p[1]] for p in [frame.rigid(7,16,du,dv,4.5) for du,dv in [(-2.03,-.02),(2.03,-.02),(2.03,3.65),(-2.03,3.65)]]]
pit_proposal={'base_y':102,'terrace_y':102.45,'pit_local_u':[10.80,17.55],'pit_local_v':[7.80,12.0],'ramp_local_u':[10.80,12.0],'ramp_local_v':[6.0,11.4],'rise_m':.45,'run_m':5.4,'status':'Root floor proposal, no structural or accessibility acceptance'}
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for rec in markers:
 if rec['kind']!='proposed_rest_anchor':continue
 ob=bpy.data.objects[rec['name']];hits=[]
 for part in parts:
  if part.type!='MESH' or 'REST_Quilt' not in part.name or 'seam' in part.name:continue
  ev=part.evaluated_get(dg);inv=ev.matrix_world.inverted();hit,loc,norm,ix=ev.ray_cast(inv@(ob.location+Vector((0,0,1))),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append((ev.matrix_world@loc).z)
 assert hits;ob.location.z=max(hits);rec['world_xyz'][1]=max(hits)
bpy.context.view_layer.update()
curve=bpy.data.curves.new('SmallDoorLabel','FONT');curve.body=f'ROYALTY {unit}';curve.size=.11;curve.extrude=.001;curve.materials.append(mats['champagne_metal']);sign=bpy.data.objects.new('SmallDoorLabel',curve);scene.collection.objects.link(sign);sign.location=xyz(.44,8.45,1.55);sign.rotation_euler=(math.pi/2,0,(math.pi/2 if frame.star else -math.pi/2)+frame.angle(6.8)-(0 if frame.star else math.pi));repair_label(sign);remember(sign,'editable_sign')
for ob in parts:ob['source_scope']=f'Group2/{unit}';ob['source_envelope_index']=unit
scene.cycles.samples=4
preview=profile_band('PREVIEW_COMPILER_FLOOR',.01,100,.01,21.99,-.18,0,'warm_stone','preview_floor');parts.remove(preview)
upper_previews=[]
for j,(u0,u1,v0,v1) in enumerate([(.30,4.65,12.0,14.85),(.30,.60,14.85,20.20),(4.20,4.65,14.85,20.20),(.30,4.65,20.20,21.70),(4.65,9.35,12.0,15.85),(4.65,4.80,15.85,19.82),(9.20,9.35,15.85,19.82),(4.65,9.35,19.82,21.70),(9.35,100,12.0,21.70)]):
 ob=profile_band(f'PREVIEW_UPPER_COMPILER_FLOOR_{j}',u0,u1,v0,v1,4.32,4.50,'warm_stone','preview_floor');parts.remove(ob);upper_previews.append(ob)
context_path=I/'Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb';before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(context_path));context=set(scene.objects)-before
cams=[('arrival',(2.65,6.8,1.65),(13.8,10.2,1.4)),('main_programme',(11.4,8.1,1.65),(15.0,10.2,1.0)),('private_circulation',(4.50,13.0,1.65),(2.4,18.8,3.2)),('sleeping_second',frame.inverse(frame.rigid(15.6,19.2,.45,-3.15,6.15)),frame.inverse(frame.rigid(15.6,19.2,0,.7,5.35))),('kitchen_service',(5.0,9.0,1.65),(1.7,11.0,1.1)),('bath_privacy',frame.inverse(frame.rigid(bu,bv,.05,1.21,1.65)),frame.inverse(frame.rigid(bu,bv,.05,-1.07,1.1)))]
cam=bpy.data.objects.new('QA_EyeLevelCamera',bpy.data.cameras.new('QA_EyeLevelCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.lens=20;cam.data.clip_start=.05;cam.data.clip_end=100;views=[]
for name,pos,target in cams:
 cam.location=xyz(*pos);cam.rotation_euler=(xyz(*target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);views.append({'name':name,'file':name+'.png','sha256':sha(O/(name+'.png')),'camera_world_xyz':w(*pos),'target_world_xyz':w(*target),'height_above_local_floor':1.65,'proposed_local_floor_y':106.5 if pos[2]>4.5 else 102})
for ob in context:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(preview,do_unlink=True);
for ob in upper_previews:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(cam,do_unlink=True);scene.camera=None;bpy.ops.file.pack_all();bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
native=O/f'{unit}_royalty.blend';export=O/f'{unit}_royalty.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_apply=True)
world_routes=[('main_loaded_cart',[w(2.65,6.8,0),w(4.0,6.8,0),w(4.0,9.2,0)],.82),('outer_gallery_body',[w(10.4,6.8,0),w(10.4,10.2,0),w(13.0,10.2,0)],.38),('kitchen_body',[w(3.4,9.2,0),w(3.4,11.0,0)],.38)]
def bath_world(u,v):
 p=frame.rigid(bu,bv,u-3.48,v-2.27,0);return [p[0],p[2],-p[1]]
bath_routes=[('bath_vanity_stance',[bath_world(3.53,3.30),bath_world(3.53,2.80),bath_world(3.84,2.80)],.38),('bath_toilet_stance',[bath_world(3.53,3.30),bath_world(3.45,2.80)],.38),('shower_approach_and_tray',[bath_world(3.53,3.30),bath_world(3.55,2.80),bath_world(3.55,1.85)],.38)]
contract={'schema':'astraea.group2_source_section.v1','status':'BUILT_ROYALTY_PENDING_QA_AND_ACTUAL_PIXELS','identity':row['identity'],'reservation':reservation,'architecture':'Lower household core with double-height crescent conversation room; two-flight private stair and fitted lift enclosure lead to proposed upper balcony and two upper rest branches. Root floors, pit/ramp and moving lift adoption remain explicit proposals.','floor_owner':'Root compiler only; preview floor omitted','floor_proposal':{'boundary':frame.poly,'floor_y':102,'thickness':.24,'status':'HELD Root support/adoption'},'imports':imports,'markers':markers,'source_views':views,'native_sha256':sha(native),'export_sha256':sha(export),'rebuild_source_sha256':sha(pathlib.Path(__file__)),'upper_floor_proposal':upper_floor_proposal,'conversation_pit_floor_proposal':pit_proposal,'private_stair_records':stair_records,'private_lift_proposal':{'cabin_source':'inputs_9311/BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003.blend','cabin_export':'inputs_9311/Game/assets/models/AST-CIR-003.glb','lower_origin_world':w(7.0,16.0,0),'proper_yaw_radians':frame.angle(16),'stops_y':[102,106.5],'platform_bottom_y':101.82,'rigid_shaft_inner_box_cabin_native_xyz':[[-2.02,-.02,0],[2.02,3.64,7.50]],'pit_void_world_xz':upper_floor_proposal['private_lift_void_world_xz'],'body_clear_front_width_m':2.4,'status':'Separate retained cabin dependency; Root pit/support/controller/physical transfer acceptance held'},'additional_source_files':{x:sha(R/x) for x in ['inputs_9311/BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003.blend','inputs_9311/Game/assets/models/AST-CIR-003.glb','inputs_9311/Game/scripts/commons_lift.gd','SPECIAL_COMPONENT_NATIVE_INSPECTION.json']},'geometry_rebuild_dependencies':{'build_royalty.py':sha(pathlib.Path(__file__)),'build_first_deluxe.py':seed_sha,'premium_frame.py':sha(R/'premium_frame.py'),'editable_label.py':sha(R/'editable_label.py')},'source_routes_world':world_routes,'internal_bath_routes_world':bath_routes,'species_assignment':None,'rest_contact_mesh_tokens':['REST_Quilt'],'private_frontage_status':'HELD: no exterior aperture authored; atlas plan vector is not per-height frontage proof. Root/Group7 final enclosing frontage/opening acceptance required.','remaining':['Actual saved-native/export fit and normal-height pixels','Root support/floors, genuine frontage/windows and external connections','Root controller/actor/physical-cart and rest ledger adoption','Installed Godot normal-arrival, streaming, persistence, regression and final art acceptance']}
(O/'SECTION_CONTRACT.json').write_text(json.dumps(contract,indent=2));runpy.run_path(str(R/'verify_first_native.py'),run_name='__main__');runpy.run_path(str(R/'verify_first_export.py'),run_name='__main__');print('ROYALTY SOURCE QA PASS',unit,flush=True)
