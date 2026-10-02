"""Original adjustable D09 threshold/quiet-edge source. Blender 4.3.2.
Run from any cwd: blender -b --threads 2 --python-exit-code 1 --python this_file
This is new script-assisted component design, not recovered ship geometry.
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]; CAT=BASE.parents[1]
for d in ('source','exports','qa'): (BASE/d).mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('salon_shared_materials',CAT/'standards/materials.py')
mm=importlib.util.module_from_spec(sp);sp.loader.exec_module(mm);MATS=mm.materials()
PARAM={'portal_clear_width':4.4,'portal_clear_height':3.1,'portal_depth':1.28,'portal_width':5.28,'portal_height':3.56,'cove_span':2.4,'rise':.43,'quiet_low_underside':2.85,'quiet_width':6.2,'quiet_depth':3.2,'quiet_height':3.74,'seat_height':.47}
OBJECTS=[]; MARKERS=[]; RECORDS=[]; COLLISIONS={}
def C(p):return [p[0],p[2],-p[1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reset():
 global OBJECTS,MARKERS
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);OBJECTS=[];MARKERS=[]
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
def mesh(name,verts,faces,role,bevel=0):
 me=bpy.data.meshes.new(name+'_semantic_mesh');me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);ob['material_role']=role;ob['authorship']='Original adjustable salon section; script-assisted'
 uv=me.uv_layers.new(name='metric_material_uv');s=MATS[role]['meters_per_tile_uv']
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  if role=='warm_walnut' and axis==2:axes=[1,0]
  for li in p.loop_indices:
   pt=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(pt[axes[0]]/s[0],pt[axes[1]]/s[1])
 if bevel:
  m=ob.modifiers.new('Editable restrained arris','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=math.radians(45)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 OBJECTS.append(ob);return ob
def extrude(name,poly,a,b,axis,role,bevel=0):
 n=len(poly); axes=[k for k in range(3) if k!=axis];verts=[]
 for v in (a,b):
  for p in poly:
   x=[0,0,0];x[axis]=v;x[axes[0]],x[axes[1]]=p;verts.append(x)
 faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,role,bevel)
def box(name,c,d,role,bevel=0):
 x,y,z=c;dx,dy,dz=[k/2 for k in d]
 return extrude(name,[(x-dx,y-dy),(x+dx,y-dy),(x+dx,y+dy),(x-dx,y+dy)],z-dz,z+dz,2,role,bevel)
def band(name,outer,inner,a,b,axis,role):return extrude(name,outer+list(reversed(inner)),a,b,axis,role)
def marker(name,p,n,kind,note,**kw):
 ob=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(ob);ob.location=p;ob.empty_display_type='ARROWS';ob.empty_display_size=.09
 ob['datum_kind']=kind;ob['source_position']=p;ob['exchange_position']=C(p);ob['source_normal']=n;ob['exchange_normal']=C(n);ob['meaning']=note
 r={'name':name,'node_name':ob.name,'source_blender_xyz_m':list(p),'exchange_gltf_yup_m':C(p),'normal_source_blender':list(n),'normal_exchange_gltf':C(n),'kind':kind,'meaning':note,**kw};MARKERS.append((ob,r));return r
def arc(cy,cz,r,a,b,n=12):return [(cy+r*math.cos(a+(b-a)*i/n),cz+r*math.sin(a+(b-a)*i/n)) for i in range(n+1)]
def interpolate(a,b,t):return [(x*(1-t)+u*t,z*(1-t)+v*t) for (x,z),(u,v) in zip(a,b)]
def portal():
 W=PARAM['portal_clear_width']/2;H=PARAM['portal_clear_height'];OW=PARAM['portal_width']/2;OH=PARAM['portal_height'];D=PARAM['portal_depth']
 outer=[(-OW,0)]+arc(-OW+.38,OH-.38,.38,math.pi,math.pi/2)+[(OW-.38,OH)]+arc(OW-.38,OH-.38,.38,math.pi/2,0)[1:]+[(OW,0)]
 inner=[(-W,0)]+arc(-W+.14,H,.14,math.pi,math.pi/2)+[(W-.14,H+.14)]+arc(W-.14,H,.14,math.pi/2,0)[1:]+[(W,0)]
 band('portal_deep_ivory_structural_core',outer,interpolate(outer,inner,.82),.04,D,1,'ivory_enamel')
 woodouter=interpolate(outer,inner,.82);woodinner=list(inner)
 for pp in(woodouter,woodinner):pp[0]=(pp[0][0],.27);pp[-1]=(pp[-1][0],.27)
 band('portal_tactile_walnut_inner_soffit_and_jamb',woodouter,woodinner,.16,D-.16,1,'warm_walnut')
 for tag,a,b in [('front',.04,.16),('rear',D-.16,D)]:band('portal_'+tag+'_ivory_inner_return',interpolate(outer,inner,.82),inner,a,b,1,'ivory_enamel')
 for i,(t0,t1,front,role) in enumerate([(0,.16,0,'ivory_enamel'),(.16,.22,.019,'dark_rubber'),(.22,.64,.024,'teal_weave'),(.64,.67,.012,'champagne_metal'),(.67,1,0,'ivory_enamel')]):
  band('portal_front_joined_profile_'+str(i),interpolate(outer,inner,t0),interpolate(outer,inner,t1),front,.04,1,role)
 # Feet are shaped continuous plinths inside the jamb envelope, leaving the opening untouched.
 for s in (-1,1):
  fx=s*(OW+(W-OW)*.82);ix=s*W
  poly=[(fx,0),(ix,0),(ix,.27),(fx,.27)]
  extrude('portal_'+str(s)+'_inner_footing_walnut_socket',poly,.16,D-.16,1,'ivory_enamel')
  box('portal_'+str(s)+'_tactile_jamb_pad',(s*(W+.235),.007,1.05),(.14,.014,.46),'warm_walnut',.01)
  marker('floor_jamb_'+str(s),(s*(W+.22),.64,0),(0,0,-1),'physical_contact','Actual structural jamb underside; floor/substrate attachment remains proposed')
  marker('lower_side_joint_'+str(s),(s*OW,.64,.59),(s,0,0),'physical_surface','Actual outer jamb face; compatible terminal joining shoulder',face_extents_source={'y':[.56,.72],'z':[.08,1.10]})
  marker('header_side_witness_'+str(s),(s*OW,.64,H+.04),(s,0,0),'physical_surface','Actual short straight shoulder below portal outer corner; not a cove joining profile',face_extents_source={'y':[0,D],'z':[H,OH-.38]})
 marker('opening_pose',(0,.64,1.55),(0,-1,0),'empty_pose','Empty inspection opening centre; no actor registration, door leaf or physical contact')
 marker('fixture_soffit_receiver',(0,.64,H+.14),(0,0,-1),'physical_surface','Walnut inner soffit surface; optional fixture receiving datum, no fixture or runtime light')
 return {'clear_opening_exemplar':{'width_m':2*W,'minimum_height_m':H,'full_width_clear_rectangle_source':{'x':[-W,W],'z':[0,H],'interior_is_empty':True},'inner_corner_radius_m':.14,'inner_arc_centres_source_xz':[[-W+.14,H],[W-.14,H]],'raised_inner_crown_z_m':H+.14,'depth_m':D,'status':'Editable empty exemplar; actual moving door widths/heights/strokes/cassettes all unknown'},'unknown_host_reservations':{'public_leaf':None,'service_leaf':None,'cassette_depth':None,'head_reservation':None},'pivot_datum':'Opening floor centre at front face Y0'}
def bridge():
 L=PARAM['cove_span'];D=PARAM['portal_depth'];H=PARAM['quiet_low_underside'];rise=PARAM['rise']
 def z(x):
  t=x/L;return H+rise*(3*t*t-2*t*t*t)
 xs=[L*i/16 for i in range(17)]
 def run(name,profile,role):
  n=len(profile);vv=[(x,y,z(x)+dz) for x in xs for y,dz in profile];ff=[]
  for i in range(len(xs)-1):ff += [(i*n+k,i*n+(k+1)%n,(i+1)*n+(k+1)%n,(i+1)*n+k) for k in range(n)]
  ff += [tuple(reversed(range(n))),tuple((len(xs)-1)*n+k for k in range(n))];return mesh(name,vv,ff,role)
 run('rising_cove_deep_structural_shoulder',[(0,0),(0,.46),(D,.46),(D,0),(1.1,0),(1.1,.065),(.18,.065),(.18,0)],'ivory_enamel')
 run('rising_recessed_walnut_channel',[(.2,.043),(1.08,.043),(1.08,.065),(.2,.065)],'warm_walnut')
 for i,y in enumerate((.188,1.08)):run('limited_channel_join_'+str(i),[(y,.031),(y+.012,.031),(y+.012,.065),(y,.065)],'champagne_metal')
 # Acoustic treatment belongs to the exposed quiet recess; no buried cosmetic strips or coplanar end caps.
 marker('low_join',(0,.64,H+.23),(-1,0,0),'physical_surface','Actual closed low end face at sheltered quiet edge; separate portal is not its mate',face_extents_source={'y':[0,D],'z':[H,H+.46]})
 marker('high_join',(L,.64,H+rise+.23),(1,0,0),'physical_surface','Actual closed high end face; mate quiet front shoulder',face_extents_source={'y':[0,D],'z':[H+rise,H+rise+.46]})
 for x in (.6,1.8):marker('fixture_receiver_'+str(x),(x,.64,z(x)+.043),(0,0,-1),'physical_surface','Walnut underside receiver at actual smooth-rise station; optional fixture, no runtime light')
 marker('rear_shell_join',(1.2,D,3.40),(0,1,0),'physical_surface','Actual rear closed face joins quiet reserved rear-shell boundary at source translation(-3.1,0,0)')
 marker('lower_side_bearing',(0,.08,H),(0,0,-1),'physical_contact','Actual low underside corner bears on quiet outer rib, with matched rising profile')
 marker('below_span_pose',(L/2,.64,1.65),(0,-1,0),'empty_pose','Empty inspection stance under connector; not a seat/contact or an installed route')
 return {'pivot_datum':'Low joining face X0 projected to floor Z0; connector occupies overhead space only','low_underside_m':H,'high_underside_m':H+rise,'rise_curve':'smoothstep, end tangents horizontal','support':'Quiet outer rising rib plus rear-shell and high-face bearing proposals; no structural engineering certification','quiet_local_placement_source_m':[-3.1,0,0],'reserved_envelope_in_quiet_source':{'x':[-3.1,-.7],'y':[0,1.28],'z':[2.85,3.74]}}
def rounded_plan(xa,xb,ya,yb,r=.15,n=5):
 pp=[]
 for cx,cy,a in [(xb-r,yb-r,0),(xa+r,yb-r,math.pi/2),(xa+r,ya+r,math.pi),(xb-r,ya+r,3*math.pi/2)]:
  pp += [(cx+r*math.cos(a+i*math.pi/2/n),cy+r*math.sin(a+i*math.pi/2/n)) for i in range(n+1)]
 return pp
def loft(name,rings,role):
 n=len(rings[0]);vv=[p for ring in rings for p in ring];ff=[]
 for i in range(len(rings)-1):ff += [(i*n+k,i*n+(k+1)%n,(i+1)*n+(k+1)%n,(i+1)*n+k) for k in range(n)]
 ff += [tuple(reversed(range(n))),tuple((len(rings)-1)*n+k for k in range(n))];return mesh(name,vv,ff,role)
def cushion(name,xa,xb,ya,yb,z,role):
 rings=[]
 for inset,zz in [(.045,z-.11),(.0,z-.075),(.014,z-.012),(.045,z)]:rings.append([(x,y,zz) for x,y in rounded_plan(xa+inset,xb-inset,ya+inset,yb-inset,.14)])
 return loft(name,rings,role)
def quiet():
 W=PARAM['quiet_width']/2;H=PARAM['quiet_height'];D=PARAM['quiet_depth'];under=PARAM['quiet_low_underside']+PARAM['rise']
 outer=[(D,0)]+arc(D-.92,H-.92,.92,0,math.pi/2)+[(1.28,H)]
 inner=[(2.98,0)]+arc(2.20,2.50,.78,0,math.pi/2)+[(1.28,under)]
 # Deep shell is a true rear-wall/cove/soffit section, not a floating decorative roof.
 band('quiet_continuous_rear_cove_and_ceiling',outer,inner,-W,W,0,'ivory_enamel')
 box('quiet_front_header_reserved_cove_receiver',(1.20,.64,3.51),(3.8,1.28,.46),'ivory_enamel')
 # Outer structural side rib has an exact smooth-rise top, physically supporting the inserted transition.
 def bearing_height(x):
  step=2.4/16;i=min(15,int(x/step));a=i*step;b=(i+1)*step;za=2.85+.43*(3*(a/2.4)**2-2*(a/2.4)**3);zb=2.85+.43*(3*(b/2.4)**2-2*(b/2.4)**3);return za+(zb-za)*(x-a)/step
 top=[(-3.1+x,bearing_height(x)) for x in(0,.15,.16)]
 extrude('quiet_outer_low_cove_bearing_rib',[(-3.1,0),(-2.94,0)]+list(reversed(top)),.022,.16,1,'ivory_enamel')
 for label,xa,xb in [('left',-3.1,-3.06),('right',-2.98,-2.94)]:
  pp=[(xa,0),(xb,0),(xb,bearing_height(xb+3.1)),(xa,bearing_height(xa+3.1))];extrude('quiet_outer_rib_recess_frame_'+label,pp,0,.022,1,'ivory_enamel')
 box('quiet_outer_rib_recess_frame_lower',(-3.02,.011,.40),(.08,.022,.80),'ivory_enamel')
 pp=[(-3.06,1.64),(-2.98,1.64),(-2.98,bearing_height(.12)),(-3.06,bearing_height(.04))];extrude('quiet_outer_rib_recess_frame_upper',pp,0,.022,1,'ivory_enamel')
 box('quiet_outer_rib_recess_dark_back',(-3.02,.021,1.22),(.08,.002,.84),'dark_rubber')
 box('quiet_outer_rib_to_book_foot',(-3.02,.54,.07),(.16,.92,.14),'ivory_enamel')
 box('quiet_outer_rib_tactile_inset',(-3.02,.016,1.22),(.056,.016,.80),'warm_walnut',.004)
 # Recess fields sit behind the forward ivory ribs. Their front faces remain usable matte material.
 for i,(xa,xb) in enumerate([(-2.88,-1.62),(-1.46,-.08),(.08,1.46),(1.62,2.88)]):
  box('quiet_acoustic_back_field_'+str(i),((xa+xb)/2,2.955,1.90),(xb-xa,.05,1.21),'teal_weave',.01)
  # Curve follows the inside section from the upper back into the soffit.
  p=arc(2.20,2.50,.776,0,math.pi/2)
  pin=arc(2.20,2.50,.752,0,math.pi/2)
  band('quiet_acoustic_cove_field_'+str(i),p,pin,xa,xb,0,'teal_weave')
 # Load-reading rib returns join wall, curve and front plenum. Walnut central inserts repeat the seat rhythm.
 for i,x in enumerate((-3.01,-1.54,0,1.54,3.01)):
  ro=[(2.91,.10)]+arc(2.20,2.50,.71,0,math.pi/2)+[(0,3.21)]
  ri=[(2.79,.10)]+arc(2.20,2.50,.59,0,math.pi/2)+[(0,3.09)]
  # Front rib feet turn up into underside before the end shoulder, preserving the declared joining profile.
  ro[-1]=(1.28,3.21);ri[-1]=(1.28,3.09)
  band('quiet_structural_rib_'+str(i),ro,ri,x-.064,x+.064,0,'ivory_enamel')
  strip=[(2.782,1.35),(2.782,2.48),(2.76,2.48),(2.76,1.35)]
  extrude('quiet_rib_walnut_touch_inlay_'+str(i),strip,x-.036,x+.036,0,'warm_walnut')
 # Shaped bench body and honest recessed toe support, full width interrupted by real storage wings.
 plan=rounded_plan(-2.53,2.53,1.57,2.87,.28,7)
 extrude('quiet_setback_floor_support',rounded_plan(-2.40,2.40,1.76,2.80,.24,7),0,.16,2,'dark_rubber')
 loft('quiet_sculpted_seat_plinth', [[(x,y,.13) for x,y in rounded_plan(-2.42,2.42,1.68,2.82,.25,7)],[(x,y,.29) for x,y in plan],[(x,y,.36) for x,y in plan]],'ivory_enamel')
 extrude('quiet_tactile_seat_landing',rounded_plan(-2.48,2.48,1.59,2.82,.22,7),.352,.374,2,'warm_walnut')
 for i,(a,b,role) in enumerate([(-2.39,-.81,'oatmeal_weave'),(-.78,.78,'clay_weave'),(.81,2.39,'oatmeal_weave')]):
  cushion('quiet_crowned_seat_'+str(i),a,b,1.64,2.53,PARAM['seat_height'],role)
  # Sloped low back joins padded seat and acoustic backing; no detached chair row.
  pp=[(2.48,.40),(2.72,.40),(2.84,1.27),(2.66,1.29)]
  extrude('quiet_reclined_back_'+str(i),pp,a+.012,b-.012,0,role,.035)
 # Purposeful hollow book returns with backed open shelves and walnut rims, left and right.
 for s in (-1,1):
  xa,xb=(2.53,3.02) if s>0 else(-3.02,-2.53)
  poly=[(.72,0),(2.97,0),(2.97,1.52),(1.08,1.52),(.72,1.22)]
  extrude('quiet_book_'+str(s)+'_outer_cheek',poly,xa,xa+.11,0,'ivory_enamel')
  extrude('quiet_book_'+str(s)+'_inner_cheek',poly,xb-.11,xb,0,'ivory_enamel')
  box('quiet_book_'+str(s)+'_back',((xa+xb)/2,2.88,.76),(xb-xa-.22,.13,1.52),'teal_weave')
  for j,z in enumerate((.12,.54,.96,1.38)):
   shelf=rounded_plan(xa+.07,xb-.07,.94,2.87,.04,4)
   extrude('quiet_book_'+str(s)+'_shelf_'+str(j),shelf,z-.044,z,2,'warm_walnut')
  # Waist-height forehand landing grows out of the book return.
  extrude('quiet_book_'+str(s)+'_shaped_arm_landing',rounded_plan(xa-.02,xb+.02,.70,1.49,.12,6),.73,.78,2,'warm_walnut')
  marker('book_landing_'+str(s),((xa+xb)/2,1.83,.96),(0,0,1),'physical_contact','Actual shelf top; empty shelf use point, no book stock included')
  marker('arm_landing_'+str(s),((xa+xb)/2,1.10,.78),(0,0,1),'physical_contact','Actual tactile walnut return top; support/use datum only')
 # Front header undercut, seated lights and book/shell connections share the same channel grammar.
 box('quiet_front_recessed_walnut_soffit',(1.20,.64,3.266),(3.72,.88,.022),'warm_walnut')
 for y in (.188,1.08):box('quiet_front_limited_arris_'+str(y),(1.20,y+.006,3.272),(3.72,.012,.024),'champagne_metal')
 for x in(-1.60,1.60):
  box('quiet_reading_fixture_socket_'+str(x),(x,1.82,3.257),(.30,.20,.046),'champagne_metal',.015)
  box('quiet_reading_fixture_opaque_lens_'+str(x),(x,1.82,3.226),(.25,.15,.016),'oatmeal_weave',.007)
  marker('fixture_lens_'+str(x),(x,1.82,3.218),(0,0,-1),'physical_surface','Actual opaque fixture lens face; nonemitting geometry, illumination unimplemented')
 for s in(-1,1):
  marker('front_header_joint_'+str(s),(-.7 if s<0 else W,.64,3.51),(s,0,0),'physical_surface','Actual closed quiet plenum end face; high cove end joins here',face_extents_source={'y':[0,1.28],'z':[3.28,3.74]})
  marker('floor_support_'+str(s),(s*1.65,2.35,0),(0,0,-1),'physical_contact','Actual recessed plinth floor contact, no floor slab included')
 for x in(-1.60,0,1.60):
  marker('seat_contact_'+str(x),(x,2.08,.47),(0,0,1),'physical_contact','Actual crown top, measured proposal only; no registered seats or universal species fit')
  marker('seated_pose_'+str(x),(x,2.08,.86),(0,-1,0),'empty_pose','Empty seated-body location above seat surface, not physical support or registered actor slot')
 marker('reserved_cove_rear_join',(-1.9,1.28,3.40),(0,-1,0),'physical_surface','Actual rear shell face beside reserved front slot; mates rising cove rear face')
 marker('low_cove_bearing',(-3.1,.08,2.85),(0,0,1),'physical_contact','Actual outer rib top at low sheltered cove start')
 marker('approach_pose',(0,.55,1.0),(0,-1,0),'empty_pose','Open front approach volume between shelves; no universal route certification')
 return {'pivot_datum':'Quiet component front-floor centre X0/Y0/Z0','historical_authoring_maximum_xyz_m':[7.2,5.4,3.8],'seats':'Three visually subdivided useful pads, no registered occupancy/capacity or species assignment','shelf_storage':'Open empty side returns; QA stock reuse can be shown separately','fixture_function':'Opaque physical sockets/lenses only, zero emission and no light nodes','reserved_transition_slot':{'x':[-3.1,-.7],'y':[0,1.28],'z':[2.85,3.74],'mate':'AST-SAL-002','mate_translation_source_m':[-3.1,0,0],'status':'Explicit unbuilt overhead slot in SAL003; combined section requires SAL002, not counted as another design'}}
def bind_physical_parts():
 from mathutils.bvhtree import BVHTree
 dg=bpy.context.evaluated_depsgraph_get();trees=[(o,BVHTree.FromObject(o,dg)) for o in OBJECTS]
 for ob,r in MARKERS:
  if r['kind'] not in ('physical_contact','physical_surface'):continue
  p=Vector(r['source_blender_xyz_m']);near=[]
  for part,tree in trees:
   hit=tree.find_nearest(p)
   if hit[0] is not None:near.append((hit[3],part.name))
  dist,name=min(near);r['physical_part']=name;r['source_surface_distance_m']=dist;ob['physical_part']=name
  if r['name'].startswith('fixture_receiver_'):
   tree=next(t for part,t in trees if part.name==name);normal=list(tree.find_nearest(p)[1]);r['fixture_aim_source']=[0,0,-1];r['fixture_aim_exchange']=[0,-1,0];r['normal_source_blender']=normal;r['normal_exchange_gltf']=C(normal);ob['source_normal']=normal;ob['exchange_normal']=C(normal)
  if dist>1e-4:raise RuntimeError('Physical marker misses source surface '+r['name']+' '+str(dist))
def collision_record(ident):
 # Modest structural-envelope compounds; attached finishes do not get independent hulls.
 out=[]
 def hull(name,pts,part,limit='Primary structural envelope; attached finish layers covered where useful voids remain open'):
  out.append({'name':name,'type':'convex_hull_points','physical_part':part,'points_m':[list(p) for p in pts],'approximation':limit})
 def prism(name,poly,lo,hi,axis,part):
  axes=[k for k in range(3) if k!=axis];pts=[]
  for d in(lo,hi):
   for p in poly:
    v=[0,0,0];v[axis]=d;v[axes[0]],v[axes[1]]=p;pts.append(v)
  hull(name,pts,part)
 def boxh(name,lo,hi,part):hull(name,[[x,y,z] for x in(lo[0],hi[0]) for y in(lo[1],hi[1]) for z in(lo[2],hi[2])],part)
 if ident=='AST-SAL-001':
  W=2.2;OW=2.64;H=3.1;OH=3.56
  outer=[(-OW,0)]+arc(-OW+.38,OH-.38,.38,math.pi,math.pi/2,4)+[(OW-.38,OH)]+arc(OW-.38,OH-.38,.38,math.pi/2,0,4)[1:]+[(OW,0)]
  inner=[(-W,0)]+arc(-W+.14,H,.14,math.pi,math.pi/2,4)+[(W-.14,H+.14)]+arc(W-.14,H,.14,math.pi/2,0,4)[1:]+[(W,0)]
  for i in range(len(outer)-1):prism('portal_structural_segment_'+str(i),[outer[i],outer[i+1],inner[i+1],inner[i]],0,1.28,1,'portal_deep_ivory_structural_core')
 elif ident=='AST-SAL-002':
  def z(x):t=x/2.4;return 2.85+.43*(3*t*t-2*t*t*t)
  for i in range(8):
   xs=[i*.3,i*.3+.15,(i+1)*.3];pts=[(x,y,zz) for x in xs for y in(0,1.28) for zz in(z(x),z(x)+.46)]
   hull('cove_structural_span_'+str(i),pts,'rising_cove_deep_structural_shoulder','Eight short convex section spans; enclosed underside finish channel is covered; preserve all space below the lower profile')
 else:
  boxh('rear_wall_with_rib_and_acoustic_recess_allowance',[-3.1,2.76,0],[3.1,3.2,2.82],'quiet_continuous_rear_cove_and_ceiling')
  outer=arc(2.28,2.82,.92,0,math.pi/2,4);inner=arc(2.20,2.50,.59,0,math.pi/2,4)
  for i in range(4):prism('rear_cove_structural_segment_'+str(i),[outer[i],outer[i+1],inner[i+1],inner[i]],-3.1,3.1,0,'quiet_continuous_rear_cove_and_ceiling')
  prism('rear_ceiling_with_projecting_ribs',[(1.28,3.09),(2.20,3.09),(2.28,3.74),(1.28,3.74)],-3.1,3.1,0,'quiet_continuous_rear_cove_and_ceiling')
  boxh('high_front_header_finish_envelope',[-.7,0,3.255],[3.1,1.28,3.74],'quiet_front_header_reserved_cove_receiver')
  selected=['quiet_outer_low_cove_bearing_rib','quiet_outer_rib_to_book_foot','quiet_setback_floor_support','quiet_sculpted_seat_plinth']
  for name in selected:
   o=next(o for o in OBJECTS if o.name==name);pts=[list(v.co) for v in o.data.vertices]
   if name=='quiet_outer_low_cove_bearing_rib':pts += [[p[0],0,p[2]] for p in pts]
   hull(name+'_envelope',pts,name)
  for prefix in('quiet_crowned_seat_','quiet_reclined_back_'):
   parts=[o for o in OBJECTS if o.name.startswith(prefix)];hull(prefix+'group_envelope',[v.co for o in parts for v in o.data.vertices],','.join(o.name for o in parts),'One useful seat/back envelope; tiny upholstery seams covered, no approach or toe void filled')
  for o in OBJECTS:
   if o.name.startswith('quiet_book_'):hull(o.name+'_structure',[v.co for v in o.data.vertices],o.name,'Distinct storage board/cheek/back/arm hull; actual open shelf volumes retained')
  # Walnut top is within the occupied seat support envelope except its 22mm upper landing.
  o=next(o for o in OBJECTS if o.name=='quiet_tactile_seat_landing');hull('seat_tactile_landing',[v.co for v in o.data.vertices],o.name)
 for h in out:h['points_exchange_gltf_yup_m']=[C(p) for p in h['points_m']]
 voids=[]
 defs={'AST-SAL-001':[('empty_portal_aperture',[-2.15,.025,.02],[2.15,1.255,3.07])],'AST-SAL-002':[('under_rising_section',[.03,.03,.04],[2.37,1.25,2.80])],'AST-SAL-003':[('open_quiet_approach',[-2.48,.04,.02],[2.48,1.45,2.80]),('left_open_book_shelf',[-2.88,1.55,.56],[-2.67,2.70,.90]),('right_open_book_shelf',[2.67,1.55,.56],[2.88,2.70,.90])]}
 for name,lo,hi in defs[ident]:
  corners=[[x,y,z] for x in(lo[0],hi[0]) for y in(lo[1],hi[1]) for z in(lo[2],hi[2])];ex=[C(p) for p in corners];voids.append({'name':name,'type':'finite_box_void','min_source_m':lo,'max_source_m':hi,'min_exchange_gltf_yup_m':[min(p[k] for p in ex) for k in range(3)],'max_exchange_gltf_yup_m':[max(p[k] for p in ex) for k in range(3)],'meaning':'Geometric finite empty component region, not actor/host route approval'})
 COLLISIONS[ident]={'preserved_voids':voids,'frame':'Blender source Z up, metres','type':'separate_convex_proposals','hulls':out,'hull_count':len(out),'superseded_finish_hull_count':{'AST-SAL-001':247,'AST-SAL-002':16,'AST-SAL-003':115}[ident],'active_physics':False,'limits':'Primary occupied structural envelopes cover attached finishes and small recesses. Four-facet corner/cove chords approximate curved profiles; outer curved surfaces can differ by up to18mm. Portal inner corner chords remain above minimum3.10m clear height. Do not use as host/door/actor sweep certification.'}
def measure():
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for ob in OBJECTS:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];return lo,hi,tri
def export(ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={}
 for src in OBJECTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=active:me.uv_layers.remove(layer)
  active.name='metric_material_uv';active.active_render=True;me.calc_loop_triangles();fix=set();s=MATS[src['material_role']]['meters_per_tile_uv']
  for tr in me.loop_triangles:
   a,b,c=[active.data[i].uv for i in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:fix.add(tr.polygon_index)
  for pi in fix:
   p=me.polygons[pi];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in p.loop_indices:
    pt=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(pt[axes[0]]/s[0],pt[axes[1]]/s[1])
  ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);groups.setdefault(src['material_role'],[]).append(ob)
 runtime=[]
 for role,parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in parts:ob.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=ident+'__'+role;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in OBJECTS if s['material_role']==role]);runtime.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in runtime+[p[0] for p in MARKERS]:ob.select_set(True)
 bpy.context.view_layer.objects.active=runtime[0]
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)
def main():
 bpy.context.preferences.filepaths.save_version=0
 for ident,title,fn in [('AST-SAL-001','Deep ivory portal return',portal),('AST-SAL-002','Rising cove and rib transition',bridge),('AST-SAL-003','Acoustic book and seat return',quiet)]:
  reset();extra=fn();bind_physical_parts();collision_record(ident);lo,hi,tri=measure();sc=bpy.context.scene;sc['catalogue_id']=ident;sc['scope']='New adjustable D09 catalogue section, not recovered or installed room';sc['source_axes']='metres; X right, -Y guest front, Z up';sc['editable_parameters']=json.dumps(PARAM)
  for im in bpy.data.images:
   if im.source=='FILE' and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  rec={'catalogue_id':ident,'name':title,'unique_design':True,'source':'source/'+ident+'.blend','export':'exports/'+ident+'.glb','generator':'source/build_salon_threshold.py','dimensions_blender_xyz_m':[hi[i]-lo[i] for i in range(3)],'bounds_blender_z_up':{'min_m':lo,'max_m':hi},'evaluated_triangles':tri,'editable_semantic_parts':len(OBJECTS),'semantic_parts':[o.name for o in OBJECTS],'material_roles':sorted(set(o['material_role'] for o in OBJECTS)),'positions_and_normals':[r for o,r in MARKERS],'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'coordinate_contract':'../../standards/COORDINATE_CONTRACT.md','reference_manifest':'../../batches/batch10/reference_manifest.json','interface_contract':'../../batches/batch10/interface_contract.json','collision_proposal_file':'collision_proposals.json','dependencies':['../../standards/materials.py','../../materials/material_manifest.json']+['../../materials/'+r+'.png' for r in sorted(set(o['material_role'] for o in OBJECTS))],'export_policy':'One evaluated mesh per semantic material role, UV layer normalized before consolidation, ordinary embedded textures, actual named datum empties retained','provenance':'Original deterministic script-assisted design from documented D09 intent and four supplied references. No recovered game mesh.','limitations':['No original final host polygon','All moving-door interfaces and reservations unknown','No installed room, game scene, controller, new shader or room allocation','Proposed contacts/approach/collisions only; no species fit, route or structural rating'],**extra}
  (BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');RECORDS.append(rec)
 (BASE/'manifest.json').write_text(json.dumps({'family':'D09 salon threshold and quiet section','unique_design_count':3,'assets':RECORDS},indent=2)+'\n')
 deps=['standards/materials.py','materials/material_manifest.json']+['materials/'+r['base_color_file'] for r in json.loads((CAT/'materials/material_manifest.json').read_text())['materials'].values()]
 (BASE/'collision_proposals.json').write_text(json.dumps({'schema':'salon-separate-convex-v1','units':'metres','coordinate_frame':'Blender source XYZ, +Z up, −Y use front','assets':COLLISIONS},indent=2)+'\n')
 (BASE/'dependency_manifest.json').write_text(json.dumps({'path_base':'catalogue root','unchanged_shared_dependencies':[{'path':p,'sha256':sha(CAT/p)} for p in deps],'production_generators':[{'path':'assets/salon_threshold/source/build_salon_threshold.py','sha256':sha(Path(__file__))}],'production_reuse':[],'qa_context_reuse':'None in production exports; any later review context declared separately'},indent=2)+'\n')
 print('SALON_THRESHOLD_COMPLETE',[(r['catalogue_id'],r['dimensions_blender_xyz_m'],r['evaluated_triangles']) for r in RECORDS])
if __name__=='__main__':main()
