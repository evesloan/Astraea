"""Original adjustable D09 edge junctions, Blender 4.3.2.
Rebuild from this script + listed shared material inputs. No QA/context inputs.
blender --background --threads 2 --python-exit-code 1 --python assets/salon_edges/source/build_salon_edges.py
"""
import bpy,bmesh,math,json,hashlib,importlib.util,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for directory in ('source','exports','qa'):(BASE/directory).mkdir(parents=True,exist_ok=True)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
MATS=load('salon_existing_materials',CAT/'standards/materials.py').materials()
MATS.update(load('salon_existing_botanical_materials',CAT/'standards/botanical_materials.py').materials())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,COLL,VOIDS,INTERFACES
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[];INTERFACES=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT)
 ROOT['catalogue_id']=ident;ROOT['scope']='New adjustable static D09 component, not recovered host or accepted ship installation'
 ROOT['source_frame']='metres Blender Z-up; +X across, -Y guest front';ROOT['exchange_frame']='glTF Y-up; source(x,y,z)->(x,z,-y)'
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident
 sc['moving_door_interfaces']='UNKNOWN: real clear spans, heights, leaf stroke, cassette depth and head reservations'
def mesh(name,vs,fs,role='ivory_enamel',bevel=.006,grain=2):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(vs,[],fs);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob['material_role']=role;ob['grain_source_axis']=grain;ob['provenance']='Original script-assisted purpose-built salon junction'
 me.materials.append(MATS[role]);uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True;sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  normal=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=normal]
  if role=='warm_walnut'and grain in axes:axes=[k for k in axes if k!=grain]+[grain]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)
 if bevel:
  m=ob.modifiers.new('Editable restrained eased arris','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=math.radians(35)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 PARTS.append(ob);return ob
BOX_FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,c,d,role='ivory_enamel',bevel=.006,grain=2):
 x,y,z=c;a,b,h=[v/2 for v in d];return mesh(name,[(x+i*a,y+j*b,z+k*h)for i,j,k in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],BOX_FACES,role,bevel,grain)
def extrude(name,poly,axis,a,b,role='ivory_enamel',bevel=.006,grain=2):
 axes=[k for k in range(3)if k!=axis];vs=[]
 for d in (a,b):
  for p in poly:
   v=[0,0,0];v[axis]=d;v[axes[0]]=p[0];v[axes[1]]=p[1];vs.append(v)
 n=len(poly);fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 return mesh(name,vs,fs,role,bevel,grain)
def rounded_rect(x0,x1,y0,y1,r=.07,n=4):
 vs=[]
 for x,y,a in [(x1-r,y1-r,0),(x0+r,y1-r,90),(x0+r,y0+r,180),(x1-r,y0+r,270)]:
  for i in range(n+1):
   t=math.radians(a+i*90/n);vs.append((x+r*math.cos(t),y+r*math.sin(t)))
 return vs
def marker(name,p,kind,part=None,normal=None,description=''):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob.location=p;ob.empty_display_size=.05
 ob['marker_kind']=kind;ob['source_position_m']=list(p);ob['gltf_position_m']=glb(p);ob['physical_part']=part or '';ob['description']=description
 row={'name':name,'kind':kind,'source_m':list(p),'gltf_m':glb(p),'physical_part':part,'description':description}
 if normal:row.update(normal_source=normal,normal_gltf=glb(normal));ob['normal_source']=normal;ob['normal_gltf']=glb(normal)
 MARKERS.append(row);return ob

def join(name,a,b,p):
 marker('JOIN_'+name,p,'physical_joint',description=a+' bears into '+b)
 JOINS.append({'name':name,'parts':[a,b],'probe_source_m':list(p),'probe_gltf_m':glb(p),'check':'Probe on or within both actual evaluated meshes'})
def interface(name,p,normal,part,extents,description):
 marker(name,p,'physical_join_face',part,normal,description)
 INTERFACES.append({'name':name,'centre_source_m':list(p),'centre_gltf_m':glb(p),'normal_source':normal,'normal_gltf':glb(normal),'physical_part':part,'face_extent_source_m':extents,'description':description,'profile_m':{'structural_depth':.16,'wood_inset':.022,'reveal':.012,'arris':.012}})
def cb(name,lo,hi):COLL.append({'name':name,'type':'box','min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]})
def ch(name,poly,axis,a,b):
 axes=[k for k in range(3)if k!=axis];pts=[]
 for v in (a,b):
  for p in poly:
   row=[0,0,0];row[axis]=v;row[axes[0]]=p[0];row[axes[1]]=p[1];pts.append(row)
 COLL.append({'name':name,'type':'convex_hull_points','points_source_m':pts,'points_gltf_m':[glb(p)for p in pts]})
def void(name,lo,hi,purpose):VOIDS.append({'name':name,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':purpose})

def court():
 # A seat/plant/structural junction, not a freestanding generic planter.
 # Three tapered piers carry the broad useful seat; rear spine carries soil tray.
 for i,x in enumerate((-1.32,-.27,.72)):
  shoe=box(f'seat_pier_{i}_floor_shoe',(x,.455,.02),(.18,.57,.04),'dark_rubber',.003)
  poly=[(.17,.04),(.74,.04),(.74,.414),(.12,.414)]
  pier=extrude(f'seat_pier_{i}_tapered_load_cheek',poly,0,x-.08,x+.08,'ivory_enamel',.005)
  marker(f'SEAT_PIER_{i}_FLOOR',(x,.455,0),'physical_floor_contact',shoe.name,[0,0,-1])
  join(f'seat_pier_{i}_shoe',shoe.name,pier.name,[x,.45,.04]);cb(f'seat_pier_{i}',[x-.09,.17,0],[x+.09,.74,.414])
 seat_poly=rounded_rect(-1.64,.91,0,.744,.10,4)
 seat=extrude('sculpted_walnut_seat_contact',seat_poly,2,.41,.47,'warm_walnut',.007,0)
 for i,x in enumerate((-1.32,-.27,.72)):
  join(f'seat_to_pier_{i}',seat.name,f'seat_pier_{i}_tapered_load_cheek',[x,.48,.412])
 for i,x in enumerate((-1.00,.18)):
  marker(f'SEAT_CONTACT_{i}',(x,.34,.47),'physical_seat_contact',seat.name,[0,0,1],'Actual planar walnut seat top; body/species/comfort testing pending')
 ch('seat_contact_only',seat_poly,2,.41,.47)
 # Low sculpted fascia rises towards a supported arm/plant return at right.
 face=[(-1.64,.19),(-1.23,.12),(-.43,.12),(.35,.19),(.89,.34),(.94,.41),(-1.64,.41)]
 fascia=extrude('swept_ivory_front_fascia',face,1,.18,.34,'ivory_enamel',.009,0)
 for i,x in enumerate((-1.32,-.27,.72)):join(f'fascia_to_pier_{i}',fascia.name,f'seat_pier_{i}_tapered_load_cheek',[x,.25,.35])
 # This broad inset is vertical/recessed, not a luminous trim line.
 inset=[(-1.19,.19),(-.46,.19),(.26,.245),(.64,.347),(-1.19,.347)]
 extrude('fascia_recessed_teal_field',inset,1,.167,.180,'teal_weave',.003,0)
 box('fascia_teal_left_recess_joint',(-1.205,.173,.270),(.012,.012,.166),'dark_rubber',0)
 # Flat side shoulder is compatible with new salon lower-profile family.
 leftpoly=[(0.56,.08),(.72,.08),(.72,.86),(.56,.80)]
 left=extrude('low_left_structural_join_shoulder',leftpoly,0,-1.80,-1.64,'ivory_enamel',0)
 box('left_shoulder_floor_shoe',(-1.72,.64,.04),(.16,.16,.08),'dark_rubber',.003)
 cap=box('left_shoulder_walnut_touch_inset',(-1.72,.55,.715),(.12,.022,.15),'warm_walnut',.002,2)
 join('left_shoulder_seat',left.name,seat.name,[-1.64,.64,.45])
 interface('COURT_LOW_LEFT_JOIN',[-1.80,.64,.44],[-1,0,0],left.name,{'x':[-1.8,-1.8],'y':[.56,.72],'z':[.08,.80]},'Real flat left side of low0.16m structural shoulder; adjustable lower portal/seat-return mate, no host placement implied')
 cb('left_low_shoulder',[-1.80,.56,0],[-1.64,.72,.86])
 # Structural back plinth supports the whole soil tray, reaching the real floor.
 back=box('plant_rear_load_spine',(0,1.54,.35),(3.04,.16,.70),'ivory_enamel',.006,0)
 box('rear_spine_floor_shoe',(0,1.54,.014),(2.98,.16,.028),'dark_rubber',.003)
 marker('COURT_REAR_FLOOR',(0,1.54,0),'physical_floor_contact','rear_spine_floor_shoe',[0,0,-1])
 soilpoly=[(-1.33,.88),(1.28,.88),(1.40,1.00),(1.40,1.47),(-1.33,1.47)]
 traypoly=[(-1.48,.88),(1.42,.88),(1.54,1.0),(1.54,1.50),(-1.48,1.50)]
 tray=extrude('supported_integral_plant_tray',traypoly,2,.32,.38,'ivory_enamel',.005,0)
 # Rim does not falsely fill planting void. Soil is a shallow visible cap over reserved depth.
 soil=extrude('actual_soil_contact_surface',soilpoly,2,.60,.62,'botanical_soil',0,0)
 box('plant_front_retaining_wall',(.035,.82,.51),(2.89,.12,.38),'ivory_enamel',.006,0)
 box('plant_left_retaining_wall',(-1.41,1.13,.51),(.16,.62,.38),'ivory_enamel',.006)
 box('plant_right_retaining_wall',(1.48,1.13,.51),(.16,.62,.38),'ivory_enamel',.006)
 for x,label in[(-1.41,'left'),(1.48,'right')]:
  box(f'plant_{label}_support_to_floor',(x,1.17,.16),(.16,.50,.32),'ivory_enamel',.005)
  marker(f'PLANT_{label.upper()}_FLOOR',(x,1.17,0),'physical_floor_contact',f'plant_{label}_support_to_floor',[0,0,-1])
  join(f'plant_{label}_support_tray',f'plant_{label}_support_to_floor',tray.name,[x,1.17,.32])
 join('plant_tray_rear_spine',tray.name,back.name,[0,1.465,.35])
 box('plant_front_walnut_touch_cap',(.035,.825,.715),(2.91,.166,.030),'warm_walnut',.006,0)
 box('plant_front_cap_limited_champagne_arris',(.035,.747,.701),(2.78,.012,.012),'champagne_metal',.002,0)
 for i,x in enumerate((-.72,.50)):
  marker(f'PLANT_SOIL_CONTACT_{i}',(x,1.18,.62),'physical_plant_soil_contact',soil.name,[0,0,1],'Actual soil top. Existing AST-BOT-002 may be placed here as QA context, not a source dependency or new asset')
  marker(f'PLANT_ROOT_DEPTH_{i}',(x,1.18,.49),'nonphysical_root_volume_receiver',None,[0,0,1],'Reserved substrate depth0.22m fromZ.38 to.60; no horticultural/irrigation verification')
 # A low, broad end return is also a useful hand/drink perch, structurally folded to floor.
 rightpoly=[(.91,.04),(1.80,.04),(1.80,.73),(1.60,.86),(1.24,.86),(.94,.67)]
 right=extrude('rising_court_end_return',rightpoly,1,.57,.73,'ivory_enamel',.009,0)
 box('right_return_floor_shoe',(1.365,.65,.02),(.85,.16,.04),'dark_rubber',.003)
 top_poly=[(.96,.10),(1.58,.10),(1.80,.28),(1.80,.60),(1.64,.73),(.96,.73)]
 perch=extrude('raised_walnut_end_perch',top_poly,2,.718,.740,'warm_walnut',.005,0)
 box('end_perch_front_structural_bearing',(1.36,.33,.365),(.16,.44,.73),'ivory_enamel',.006)
 join('perch_structural_bearing',perch.name,'end_perch_front_structural_bearing',[1.36,.33,.725])
 join('perch_folded_return',perch.name,right.name,[1.36,.65,.73])
 marker('COURT_PERCH_FLOOR',[1.36,.33,0],'physical_floor_contact','end_perch_front_structural_bearing',[0,0,-1],'Real floor-supported perch pier')
 marker('COURT_PERCH_CONTACT',(1.36,.32,.740),'physical_tactile_surface',perch.name,[0,0,1],'Small supported end perch, not an extra seat')
 marker('COURT_FLOOR_DATUM',[0,0,0],'placement_origin',None,[0,0,1])
 cb('plant_rear_spine',[-1.52,1.46,0],[1.52,1.62,.70]);cb('plant_tray',[-1.48,.88,.32],[1.54,1.50,.38]);cb('plant_front_wall',[-1.41,.76,.32],[1.48,.88,.70]);cb('plant_left_wall',[-1.49,.82,0],[-1.33,1.44,.70]);cb('plant_right_wall',[1.40,.82,0],[1.56,1.44,.70]);ch('right_folded_return',rightpoly,1,.57,.73);ch('right_perch',top_poly,2,.718,.740);cb('perch_bearing',[1.28,.11,0],[1.44,.55,.73])
 void('seat_front_leg_approach',[-1.20,-.52,.02],[.57,.105,.38],'Open in front of seat: deliberately not wrapped in a whole-component convex collider')
 void('seat_under_middle_left',[-1.12,.36,.03],[-.40,.70,.39],'Useful under-seat gap between true load piers')
 void('open_above_seat',[-1.48,.04,.49],[.71,.70,1.08],'Low open social edge; plant leaves in QA remain behind this contact/approach zone')
 return 'Low court seat, planted fascia and structural return',{'seat_surface_z_m':.47,'soil_surface_z_m':.62,'root_depth_proposal_m':.22,'maximum_height_m':.86,'character':'Asymmetric low open seat supports and shaped fascia joined to integral supported plant tray and useful end perch','no_giant_tree':True}

def balcony():
 # Continuous heavy top profile with two explicit open infill receiver fields.
 for i,x in enumerate((-1.32,0,1.32)):
  shoe=box(f'edge_floor_shoe_{i}',(x,.24,.026),(.16,.48,.052),'dark_rubber',.003)
  foot=box(f'edge_anchor_foot_{i}',(x,.24,.076),(.16,.42,.068),'ivory_enamel',.005)
  post=box(f'edge_structural_post_{i}',(x,.24,.566),(.16,.16,1.068),'ivory_enamel',0)
  marker(f'EDGE_FLOOR_CONTACT_{i}',(x,.24,0),'physical_floor_contact',shoe.name,[0,0,-1])
  join(f'edge_post_to_foot_{i}',post.name,foot.name,[x,.24,.08]);join(f'edge_foot_to_shoe_{i}',foot.name,shoe.name,[x,.24,.05])
  for j,y in enumerate((.075,.405)):
   box(f'edge_anchor_fastener_{i}_{j}',(x,y,.114),(.030,.030,.008),'champagne_metal',.001)
   marker(f'EDGE_ANCHOR_{i}_{j}',(x,y,.118),'physical_host_anchor_surface',f'edge_anchor_fastener_{i}_{j}',[0,0,1],'Visible fixing head only; host bolt/substrate/load rating unverified')
  cb(f'edge_post_{i}',[x-.08,.16,0],[x+.08,.32,1.10]);cb(f'edge_foot_{i}',[x-.08,0,0],[x+.08,.48,.114])
 bottom=box('continuous_ivory_edge_sill',(0,.24,.235),(2.80,.16,.17),'ivory_enamel',0,0)
 beam=box('continuous_ivory_top_structural_profile',(0,.24,.993),(2.80,.16,.214),'ivory_enamel',0,0)
 cap=box('continuous_walnut_tactile_top',(0,.24,1.116),(2.80,.28,.068),'warm_walnut',.008,0)
 for i,x in enumerate((-1.32,0,1.32)):
  join(f'edge_top_to_post_{i}',beam.name,f'edge_structural_post_{i}',[x,.24,1.04]);join(f'edge_sill_to_post_{i}',bottom.name,f'edge_structural_post_{i}',[x,.24,.235])
 join('edge_cap_to_beam',cap.name,beam.name,[0,.24,1.09])
 # Deliberate shadow recess/wood/metal construction hierarchy, no broken rods.
 box('edge_front_recessed_walnut_inset',(0,.149,.986),(2.46,.022,.128),'warm_walnut',.003,0)
 box('edge_front_joint_shadow',(0,.135,.907),(2.48,.012,.012),'dark_rubber',.001,0)
 box('edge_front_limited_arris',(0,.099,1.095),(2.72,.012,.012),'champagne_metal',.002,0)
 for i,(xa,xb) in enumerate(((-1.24,-.08),(.08,1.24))):
  # Thin gasket lips belong to real sill, reveal ends explicit empty receivers.
  for y in (.205,.275):box(f'infill_seat_gasket_{i}_{y}',((xa+xb)/2,y,.324),(xb-xa,.012,.012),'dark_rubber',.001,0)
  marker(f'INFILL_LOWER_CONTACT_{i}',((xa+xb)/2,.24,.32),'physical_infill_bottom_support',bottom.name,[0,0,1],'Actual sill top; pane/panel is absent. This component alone is not a completed safety barrier')
  marker(f'INFILL_RECEIVER_{i}',((xa+xb)/2,.24,.60),'nonphysical_infill_receiver',None,[0,1,0],'Empty0.048m depth panel receiver; fieldZ.33.. .88; infill and host connections remain required')
  void(f'infill_open_field_{i}',[xa+.014,.218,.336],[xb-.014,.262,.872],'Explicitly absent infill; preserve opening in collider. No completed barrier or safety compliance claim')
  marker(f'INFILL_UPPER_CONTACT_{i}',((xa+xb)/2,.24,.886),'physical_infill_upper_interface',beam.name,[0,0,-1],'Underside of substantial structural top; host-selected panel retention unresolved')
 for sign,label in[(-1,'CONTINUATION'),(1,'PORTAL')]:
  part=f'edge_structural_post_{0 if sign<0 else 2}'
  interface('BALCONY_'+label+'_LOW_JOIN',[sign*1.40,.24,.55],[sign,0,0],part,{'x':[sign*1.4,sign*1.4],'y':[.16,.32],'z':[.08,1.10]},'Physical full-depth terminal face. Portal mate uses SAL001 outside jamb face with0.40m depth-axis translation; no invented host door or full guard')
 marker('BALCONY_HAND_REST',[0,.24,1.15],'physical_hand_rest',cap.name,[0,0,1],'Actual continuous walnut top; height proposed, safety/ergonomics unverified')
 marker('BALCONY_FLOOR_DATUM',[0,0,0],'placement_origin',None,[0,0,1])
 cb('edge_sill',[-1.4,.16,.15],[1.4,.32,.32]);cb('edge_top_beam',[-1.4,.16,.886],[1.4,.32,1.10]);cb('edge_walnut_cap',[-1.4,.10,1.082],[1.4,.38,1.15]);cb('edge_front_inset',[-1.23,.138,.922],[1.23,.16,1.05])
 void('guest_side_clear_strip',[-1.24,-.60,.02],[1.24,-.02,1.45],'Open approach to hand rest; no whole-envelope barrier collision')
 return 'Continuous balcony edge with portal terminal',{'top_height_proposal_m':1.15,'infill_status':'Two open receiver fields; no panel or glass included and no completed barrier claim','runtime_glass_shader':'Absent; original runtime shader remains unavailable','host_interface':'Source right endX+1.40 can butt SAL001 left or right jamb face with explicit chosen placement; floor substrate/structural engineering pending'}

def service():
 # Fixed two-faced assembly. Guest wall/ledge and rear open storage are one constructed return.
 spine=box('service_guest_structural_spine',(0,.24,1.185),(2.8,.16,2.33),'ivory_enamel',.008,2)
 for i,x in enumerate((-1.32,1.32)):
  shoe=box(f'service_floor_shoe_{i}',(x,.72,.02),(.16,1.28,.04),'dark_rubber',.003)
  sidepoly=[(.16,.04),(.92,.04),(.92,2.08),(.81,2.27),(.32,2.35),(.16,2.35)]
  side=extrude(f'service_tapered_side_cheek_{i}',sidepoly,0,x-.08,x+.08,'ivory_enamel',.006,2)
  marker(f'SERVICE_FLOOR_CONTACT_{i}',(x,.72,0),'physical_floor_contact',shoe.name,[0,0,-1])
  join(f'service_side_spine_{i}',side.name,spine.name,[x,.24,1.50]);join(f'service_side_shoe_{i}',side.name,shoe.name,[x,.50,.04]);cb(f'service_side_{i}',[x-.08,.16,0],[x+.08,.92,2.27]);cb(f'service_floor_shoe_{i}',[x-.08,.08,0],[x+.08,1.36,.04])
 # Recessed vertical guest fields: framed and interrupted by actual ledge.
 for i,(a,b) in enumerate(((-1.16,-.45),(-.29,.43),(.59,1.16))):
  field=box(f'guest_recessed_teal_field_{i}',((a+b)/2,.143,1.603),(b-a,.026,1.02),'teal_weave',.008,2)
  for x in(a-.015,b+.015):box(f'guest_field_{i}_ivory_side_frame_{x}',(x,.112,1.603),(.030,.064,1.07),'ivory_enamel',.004,2)
  box(f'guest_field_{i}_walnut_lower_inset',((a+b)/2,.106,1.07),(b-a,.022,.102),'warm_walnut',.003,0)
  box(f'guest_field_{i}_top_shadow_reveal',((a+b)/2,.120,2.128),(b-a,.012,.012),'dark_rubber',.001,0)
 box('guest_walnut_ledge_bearing',(0,.175,.896),(2.50,.25,.10),'ivory_enamel',.006,0)
 ledgepoly=rounded_rect(-1.32,1.40,0,.32,.10,4)
 ledge=extrude('guest_continuous_tactile_serving_ledge',ledgepoly,2,.936,.958,'warm_walnut',.006,0)
 join('guest_ledge_to_bearing',ledge.name,'guest_walnut_ledge_bearing',[0,.17,.941])
 marker('GUEST_LEDGE_CONTACT',[-.55,.17,.958],'physical_guest_surface',ledge.name,[0,0,1],'Actual serving/setting surface; no transaction or active service mechanism')
 # Fine framed lower panel keeps guest finish composed without fake drawer seams.
 extrude('guest_lower_shaped_ivory_fascia',[(-1.18,.24),(1.18,.24),(1.26,.42),(1.26,.875),(-1.26,.875),(-1.26,.42)],1,.085,.16,'ivory_enamel',.006,0)
 box('guest_lower_walnut_kick_recess',(0,.074,.37),(2.34,.022,.15),'warm_walnut',.003,0)
 box('guest_lower_limited_champagne_joint',(0,.056,.462),(2.35,.012,.012),'champagne_metal',.001,0)
 # Reachable shelves open to +Y; separate top/bottom, side and rear contacts.
 for i,z in enumerate((.26,.70,1.17,1.65)):
  shelf=box(f'service_open_shelf_{i}',(0,.592,z-.018),(2.48,.556,.036),'warm_walnut',.004,0)
  support=box(f'service_shelf_back_bearing_{i}',(0,.341,z-.057),(2.48,.06,.06),'ivory_enamel',.004,0)
  join(f'service_shelf_{i}_back_support',shelf.name,support.name,[0,.341,z-.033])
  for j,x in enumerate((-1.32,1.32)):join(f'service_shelf_{i}_side_{j}',shelf.name,f'service_tapered_side_cheek_{j}',[x+(.08 if j==0 else -.08),.60,z-.018])
  marker(f'SERVICE_SHELF_CONTACT_{i}',[0,.69,z],'physical_storage_support',shelf.name,[0,0,1],'Actual open shelf top,0.556m deep; reach/load rating unverified')
  marker(f'SERVICE_SHELF_MOUTH_{i}',[0,.88,z+.18],'nonphysical_service_receiver',None,[0,1,0],'Open compartment/approach centre, not a contact')
  cb(f'service_shelf_{i}',[-1.24,.314,z-.036],[1.24,.87,z]);cb(f'service_shelf_bearing_{i}',[-1.24,.311,z-.087],[1.24,.371,z-.027])
  if i<3:void(f'open_service_storage_{i}',[-1.20,.384,z+.025],[.88 if i<2 else 1.20,.88,(.70,1.17,1.65)[i]-.10],'Open service-side shelf mouth; lower two reserve the right corner support, with2.08m unobstructed width. No doors/covers or whole-cabinet collider')
 # The counter turns at the right, ending at a genuine service threshold edge.
 returnpoly=[(.92,.30),(1.40,.30),(1.40,1.36),(1.06,1.36),(.92,1.22)]
 returntop=extrude('turned_service_work_surface',returnpoly,2,.936,.958,'warm_walnut',.006,1)
 return_support=box('turned_service_low_structural_return',(1.32,1.13,.488),(.16,.46,.896),'ivory_enamel',.006,2)
 return_front=box('turn_inner_supported_cheek',(1.00,1.05,.49),(.16,.38,.90),'ivory_enamel',.006,2)
 join('turn_top_outer_support',returntop.name,return_support.name,[1.32,1.13,.936]);join('turn_top_inner_support',returntop.name,return_front.name,[1.00,1.05,.938])
 marker('SERVICE_TURN_WORK_CONTACT',[1.17,1.10,.958],'physical_service_surface',returntop.name,[0,0,1],'Actual low worktop at the corner between finished guest and practical service sides')
 # The requested motion is explicitly fixed. Nothing is a removable cover or leaf.
 ROOT['motion_contract']='Entire assembly fixed; open shelving; no cover, door, hinge, slide or removal operation'
 interface('SERVICE_RIGHT_THRESHOLD_JOIN',[1.40,1.12,.55],[1,0,0],return_support.name,{'x':[1.4,1.4],'y':[.98,1.28],'z':[.08,.90]},'Physical fixed right return face adjacent to reserved service turn. This is not a door jamb cassette or host opening size')
 interface('SERVICE_LEFT_PROFILE_JOIN',[-1.40,.64,.55],[-1,0,0],'service_tapered_side_cheek_0',{'x':[-1.4,-1.4],'y':[.56,.72],'z':[.08,1.10]},'Physical0.16m structural side profile for lower portal-compatible join; top of this piece stays below quiet cove')
 marker('SERVICE_TURN_APPROACH',[1.82,1.08,0],'nonphysical_turn_datum',None,[1,0,0],'Proposed approach outside component: no real door, passage width, actor/cart fit or threshold floor asserted')
 marker('SERVICE_FLOOR_DATUM',[0,0,0],'placement_origin',None,[0,0,1])
 cb('service_spine',[-1.4,.16,.02],[1.4,.32,2.35]);cb('guest_ledge',[-1.32,0,.936],[1.4,.32,.958]);cb('guest_ledge_bearing',[-1.25,.05,.846],[1.25,.30,.946]);cb('guest_lower_fascia',[-1.26,.085,.24],[1.26,.16,.875]);cb('return_outer_support',[1.24,.90,.04],[1.40,1.36,.936]);cb('return_inner_support',[.92,.86,.04],[1.08,1.24,.94]);ch('turn_worktop',returnpoly,2,.936,.958)
 void('service_turn_outside_fixed_end',[1.43,.50,.02],[2.18,1.34,2.00],'Proposed open turn beside actual low service return. No door motion or recovered passage width is certified')
 void('service_rear_approach',[-1.15,.96,.06],[.84,1.76,1.96],'Open rear shelf approach, not filled by a cabinet convex hull; right return remains occupied')
 return 'Two-faced fixed service storage and threshold return',{'fixed_assembly':True,'shelf_planes_z_m':[.26,.70,1.17,1.65],'guest_and_service_surface_z_m':.958,'service_side':'+Y','guest_side':'-Y','motion':'No leaf/cover/door mechanism; all parts fixed','threshold_relationship':'Actual low right return ends beside explicitly nonphysical outside turn datum; real host door interfaces unknown'}

def measure():
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for ob in PARTS:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in pts)for i in range(3)];hi=[max(p[i]for p in pts)for i in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={};out=[]
 for src in PARTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));uv=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=uv:me.uv_layers.remove(layer)
  uv.name='metric_material_uv';uv.active_render=True;me.calc_loop_triangles();fix=set()
  for tr in me.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:fix.add(tr.polygon_index)
  sx,sy=MATS[src['material_role']]['meters_per_tile_uv']
  for pi in fix:
   p=me.polygons[pi];normal=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3)if k!=normal];grain=int(src['grain_source_axis'])
   if src['material_role']=='warm_walnut'and grain in axes:axes=[k for k in axes if k!=grain]+[grain]
   for li in p.loop_indices:
    c=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(c[axes[0]]/sx,c[axes[1]]/sy)
  o=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(o)
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=obs[0];o.name=ident+'__'+role;o.parent=ROOT;o['material_role']=role;o['semantic_parts']=json.dumps([p.name for p in PARTS if p['material_role']==role]);out.append(o)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for o in out:o.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)
def main():
 bpy.context.preferences.filepaths.save_version=0
 only=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else None
 rows=[r for r in json.loads((BASE/'manifest.json').read_text())['assets']if r['catalogue_id']!=only]if only and(BASE/'manifest.json').exists()else[]
 coll=json.loads((BASE/'collision_proposals.json').read_text())if only and(BASE/'collision_proposals.json').exists()else{}
 api=json.loads((BASE/'marker_api.json').read_text())if only and(BASE/'marker_api.json').exists()else{}
 for ident,fn in [('AST-SAL-004',court),('AST-SAL-005',balcony),('AST-SAL-006',service)]:
  if only and ident!=only:continue
  reset(ident);name,details=fn();bpy.context.view_layer.update();bounds,tri=measure()
  for image in bpy.data.images:
   if image.source=='FILE'and not image.packed_file:image.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  rec={'catalogue_id':ident,'name':name,'title':name,'unique_design':True,'original_script_assisted_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_salon_edges.py','source_frame':'metres Blender +Z up,+X across,-Y guest front','exchange_frame':'metres glTF +Y up; source(x,y,z)->(x,z,-y); native node transforms authoritative','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'Source floor Z0, component centre acrossX; depth origin at guest edgeY0'},'dimensions_blender_xyz_m':bounds['dimensions_m'],'bounds_blender_z_up':bounds,'evaluated_triangles':tri,'evaluated_source_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role']for o in PARTS)),'physical_and_proposal_markers':MARKERS,'joins':JOINS,'physical_join_interfaces':INTERFACES,'receiver_voids':VOIDS,'marker_api_file':'marker_api.json','collision_proposal_file':'collision_proposals.json','runtime_consolidation':'Evaluated static copies by semantic material role; native semantic marker nodes retained; editable meshes and modifiers in source','details':details,'moving_host_door_interfaces':{'public_clear_width_m':None,'public_clear_height_m':None,'service_clear_width_m':None,'service_clear_height_m':None,'leaf_stroke_m':None,'cassette_depth_m':None,'head_reservation_m':None},'reference_manifest':'../../batches/batch10/reference_manifest.json','profile_contract':'../../batches/batch10/interface_contract.json','context_dependencies':'None for production rebuild. QA plant/other components are separate existing context, separately hashed.','source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'limitations':['New adjustable source work; original final host polygon and game remain unavailable','No recovered-host or installed-room claim','No door motion, real door dimensions or cassette/head fit asserted','No load rating, guard safety compliance, species ergonomics or engine collision acceptance','Host arrival/service axis, terrace relation, X35..45 tram reserve and D09_salon5 identity remain governed by historical records; local QA layouts are hypotheses only']}
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');api[ident]=MARKERS;coll[ident]={'source_frame':'metres Blender Z-up','exchange_frame':'metres glTF Y-up; explicitly converted records','status':'Separate modest static collision proposals only, preserving use/infill/storage voids; no runtime physics','shapes':COLL,'preserve_voids':VOIDS}
 rows.sort(key=lambda r:r['catalogue_id'])
 for r in rows:
  r['generator_sha256']=sha(Path(__file__));(BASE/(r['catalogue_id']+'.manifest.json')).write_text(json.dumps(r,indent=2)+'\n')
 (BASE/'manifest.json').write_text(json.dumps({'family':'salon_edges','revision':'salon-edge-junctions-01','assets':rows},indent=2)+'\n')
 (BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n')
 print('BUILT_SALON_EDGES',[(r['catalogue_id'],r['dimensions_blender_xyz_m'],r['evaluated_triangles'])for r in rows])
if __name__=='__main__':main()
