"""Original script-assisted paired landing guest designs. Blender 4.3.2.
Generic mesh/UV/export construction methods follow the existing catalogue conventions;
all new semantic source geometry and orientation artwork are authored here.
Rebuild: blender --background --threads 2 --python-exit-code 1 --python source/build_landing_guest.py
"""
import bpy, bmesh, math, json, hashlib, importlib.util, sys
from pathlib import Path
from mathutils import Vector, Matrix

BASE=Path(__file__).resolve().parents[1]; CAT=BASE.parents[1]
for name in ('source','exports','qa'): (BASE/name).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('landing_shared_materials',CAT/'standards/materials.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod); MATS=mod.materials()
PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[]
def glb(p):return [p[0],p[2],-p[1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reset(ident):
 global PARTS,MARKERS,JOINS,COLL,VOIDS,ROOT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident
 ROOT['scope']='Static original catalogue component; no engine lighting, physics, species or fit claim'
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident
def mesh(name,verts,faces,role='warm_walnut',bevel=0,grain=2):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT
 ob['material_role']=role;ob['grain_source_axis']=grain;ob['provenance']='Original script-assisted shaped guest component'
 me.materials.append(MATS[role]);uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  normal=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=normal]
  if role=='warm_walnut' and grain in axes: axes=[a for a in axes if a!=grain]+[grain]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)
 if bevel:
  m=ob.modifiers.new('Editable edge easing','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=math.radians(35)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 PARTS.append(ob);return ob
def box(name,c,d,role='warm_walnut',bevel=.003,grain=2):
 x,y,z=c;a,b,h=[v/2 for v in d]
 return mesh(name,[(x+i*a,y+j*b,z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,grain)
def extrude(name,profile,axis,a,b,role='warm_walnut',bevel=.003,grain=2):
 axes=[k for k in range(3) if k!=axis];vs=[]
 for dep in (a,b):
  for p in profile:
   v=[0,0,0];v[axis]=dep;v[axes[0]]=p[0];v[axes[1]]=p[1];vs.append(v)
 n=len(profile);fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,role,bevel,grain)
def rod(name,a,b,r,role='champagne_metal',n=12):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();seed=Vector((1,0,0)) if abs(d.x)<.9 else Vector((0,1,0));u=d.cross(seed).normalized();v=d.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n)) for p in(a,b) for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,0)
def rounded(w,d,r):
 out=[]
 for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for i in range(4):
   t=math.radians(start+i*30);out.append((cx+r*math.cos(t),cy+r*math.sin(t)))
 return out
def tray(name,c,w,d,h,role='ivory_enamel',r=.028):
 p=rounded(w,d,min(r,w/3,d/3));return extrude(name,[(c[0]+x,c[1]+y)for x,y in p],2,c[2]-h/2,c[2]+h/2,role,.001,0)
def marker(name,p,kind,part=None,direction=None,description=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o.location=p;o.empty_display_size=.025;o['marker_kind']=kind;o['frame']='Blender source metres Z-up; actual GLB node transform is exchange authority'
 row={'name':name,'kind':kind,'source_m':list(p),'gltf_m':glb(p),'physical_part':part,'description':description}
 if direction:row.update(direction_source=direction,direction_gltf=glb(direction));o['direction_source']=direction;o['direction_gltf']=glb(direction)
 o['source_position_m']=list(p);o['gltf_position_m']=glb(p);o['physical_part']=part or '';MARKERS.append(row);return o
def join(name,a,b,p):
 marker('JOIN_'+name,p,'physical_joint',description=a+' bears into '+b)
 JOINS.append({'name':name,'parts':[a,b],'probe_source_m':list(p),'probe_gltf_m':glb(p),'check':'Probe lies on or within both evaluated meshes; nearest-boundary distances are evidence, not assumed AABB contact'})
def collision_box(name,lo,hi):
 COLL.append({'name':name,'type':'box','min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]})
def collision_hull(name,points):
 COLL.append({'name':name,'type':'convex_hull_points','points_source_m':points,'points_gltf_m':[glb(p)for p in points]})

def art_material():
 mat=bpy.data.materials.new('ASTRAEA_guest_arrival_original');mat.use_nodes=True
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BASE/'textures/guest_arrival_original.png'),check_existing=True);tex.image.pack();tex.interpolation='Linear';tex.extension='EXTEND'
 mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat['astraea_material_role']='guest_arrival_original';mat['meters_per_tile_uv']=[.65,1.28]
 return mat
MATS['guest_arrival_original']=art_material()
def bounds_pair(lo,hi):return {'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]}
def void(name,lo,hi,purpose):VOIDS.append(dict(name=name,purpose=purpose,**bounds_pair(lo,hi)))
def physical_joint(name,a,b,p,normal_a,normal_b):
 JOINS.append({'name':name,'parts':[a,b],'probe_source_m':list(p),'probe_gltf_m':glb(p),'normal_a_source':normal_a,'normal_b_source':normal_b,'normal_a_gltf':glb(normal_a),'normal_b_gltf':glb(normal_b),'check':'Actual evaluated mesh boundary witness; opposing physical normals separately recorded from use/light aim'})
def directory():
 # Rounded plan nose is a full-depth architectural return, not a trim on a box.
 profile=[(-.70,.045),(-.685,.015),(-.65,0),(-.58,0),(-.53,.020),(-.49,.065),(-.49,.49),(-.45,.53),(-.45,.65),(-.70,.65)]
 ret=extrude('rounded_full_depth_arrival_return',profile,2,0,2.55,'ivory_enamel',0,2)
 spine=box('rear_structural_directory_spine',(.125,.59,1.275),(1.15,.12,2.55),'ivory_enamel',0)
 # Floor plinth limited to the supporting wall footprint; central entry stays empty.
 kick=box('recessed_rear_contact_plinth',(.10,.5175,.070),(1.20,.025,.14),'dark_rubber',0,0)
 marker('LEFT_FLOOR_CONTACT',[-.61,.32,0],'physical_floor_contact',ret.name,[0,0,-1])
 marker('REAR_FLOOR_CONTACT',[.10,.59,0],'physical_floor_contact',spine.name,[0,0,-1])
 physical_joint('return_to_spine',ret.name,spine.name,[-.45,.585,1.30],[1,0,0],[-1,0,0])
 # Original directory is inset between timber borders. Field front y=.482; frame y=.455.
 x0,x1=-.405,.305;z0,z1=.94,2.27;t=.043
 for nm,c,d in [('directory_left_stile',(x0+t/2,.494,(z0+z1)/2),(t,.078,z1-z0)),('directory_right_stile',(x1-t/2,.494,(z0+z1)/2),(t,.078,z1-z0)),('directory_upper_rail',((x0+x1)/2,.494,z1-t/2),(x1-x0-2*t,.078,t)),('directory_lower_rail',((x0+x1)/2,.494,z0+t/2),(x1-x0-2*t,.078,t))]:box(nm,c,d,'warm_walnut',.002,2 if 'stile'in nm else 0)
 field=box('inset_original_guest_arrival_field',((x0+x1)/2,.5015,(z0+z1)/2),(x1-x0-2*t,.029,z1-z0-2*t),'ivory_enamel',0)
 art=box('original_guest_arrival_graphic',(-.05,.4845,1.605),(.622,.005,1.242),'guest_arrival_original',0)
 uv=art.data.uv_layers.active
 for f in art.data.polygons:
  if f.normal.y<-.99:
   for li in f.loop_indices:
    co=art.data.vertices[art.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.361)/.622,(co.z-.984)/1.242)
 physical_joint('art_plate_to_backing',art.name,field.name,[-.05,.487,1.55],[0,1,0],[0,-1,0])
 # Cant the entire physical field and frame toward the core-facing +X strip.
 angle=math.radians(20);c,s=math.cos(angle),math.sin(angle)
 def cant(p):return [-.05+(p[0]+.05)*c-(p[1]-.494)*s,.33+(p[0]+.05)*s+(p[1]-.494)*c,p[2]]
 dirparts=[o for o in PARTS if o.name.startswith('directory_') or o.name in ('inset_original_guest_arrival_field','original_guest_arrival_graphic')]
 for ob in dirparts:
  for v in ob.data.vertices:v.co=cant(v.co)
  ob.data.update()
 for jr in JOINS:
  if jr['name']=='art_plate_to_backing':
   jr['probe_source_m']=cant(jr['probe_source_m']);jr['probe_gltf_m']=glb(jr['probe_source_m']);jr['normal_a_source']=[-s,c,0];jr['normal_b_source']=[s,-c,0];jr['normal_a_gltf']=glb(jr['normal_a_source']);jr['normal_b_gltf']=glb(jr['normal_b_source'])
 left=cant([x0,.516,0]);right=cant([x1,.516,0])
 wedge=extrude('canted_directory_structural_wedge',[(left[0],left[1]),(right[0],right[1]),(right[0],.53),(left[0],.53)],2,z0+.006,z1-.006,'ivory_enamel',0,2)
 physical_joint('directory_wedge_to_spine',wedge.name,spine.name,[-.05,.53,1.6],[0,1,0],[0,-1,0])
 physical_joint('directory_field_to_wedge',field.name,wedge.name,cant([-.05,.516,1.55]),[-s,c,0],[s,-c,0])
 marker('DIRECTORY_READING_FIELD',cant([-.05,.482,1.55]),'physical_orientation_field',art.name,[s,-c,0],'Static original abstract arrival artwork; 20 degree inward cant, no live map, actual route or button')
 box('low_walnut_touch_rail',(-.05,.4775,.765),(.81,.105,.065),'warm_walnut',.004,0)
 marker('DIRECTORY_TOUCH_RAIL',[-.05,.425,.765],'physical_contact_surface','low_walnut_touch_rail',[0,-1,0],'Optional steadying edge; no accessibility or loading certification')
 # Broad rolled cove profile: visible lip, recessed soffit, rear bearing and closed end caps.
 cp=[(.53,2.55),(.65,2.55),(.65,2.8),(.315,2.8),(.270,2.78),(.235,2.74),(.220,2.68),(.220,2.645),(.255,2.645),(.270,2.690),(.30,2.725),(.35,2.742),(.53,2.742)]
 cove=extrude('rolled_local_cove_with_finished_ends',cp,0,-.70,.70,'warm_walnut',0,0)
 physical_joint('cove_rear_bearing',cove.name,spine.name,[.12,.585,2.55],[0,0,-1],[0,0,1])
 # Substantial inner liner is recessed inside the trough; no visible duplicate plane.
 liner=box('cove_recessed_opaque_liner',(0,.425,2.735),(1.16,.145,.014),'oatmeal_weave',.001,0)
 marker('COVE_LINER_PHYSICAL_UNDERSIDE',[0,.425,2.728],'physical_diffuser_surface',liner.name,[0,0,-1],'Opaque material geometry only; no emitted light or electrical assembly')
 marker('COVE_PROPOSED_DIRECTORY_AIM',[0,.31,2.62],'nonphysical_light_aim',None,[0,.18,-.983666],'Design aiming proposal only; physical underside normal is stored on its own marker')
 # Reused sconce receives an exact plane on a real backer; fixture remains QA context only.
 recv=extrude('sconce_receiver_walnut_bearing',[(-.10,-.19),(.10,-.19),(.12,-.16),(.12,.16),(.09,.195),(-.09,.195),(-.12,.16),(-.12,-.16)],1,.47,.53,'warm_walnut',.002,2)
 recv.location.x=.49;recv.location.z=1.93
 marker('SCONCE_RECEIVER_CENTER',[.49,.47,1.93],'physical_fixture_receiver',recv.name,[0,-1,0],'AST-GST-002 QA-only translation (.49,.47,1.93); rear wall face Y0 meets this plane')
 for zz in(-.11,.11):marker('SCONCE_RECEIVER_FIXING_'+str(zz),[.49,.47,1.93+zz],'physical_fixture_receiver',recv.name,[0,-1,0])
 physical_joint('receiver_to_spine',recv.name,spine.name,[.49,.53,1.93],[0,1,0],[0,-1,0])
 marker('SCONCE_SERVICE_WITHDRAWAL',[.49,.08,1.93],'nonphysical_service_reservation',None,[0,-1,0],'Front withdrawal and tool approach proposal; sconce clips are reached from below, no electrical isolation or maintainability certification')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',None,[0,0,1])
 collision_hull('rounded_left_return',[[x,y,z]for z in(0,2.55)for x,y in profile])
 collision_box('rear_wall',[-.45,.53,0],[.70,.65,2.55])
 collision_box('touchrail',[-.455,.425,.7325],[.355,.530,.7975])
 collision_hull('canted_directory_assembly',[[x,y,z]for z in(.94,2.27)for x,y in[(left[0]-.020,left[1]-.066),(right[0]+.020,right[1]-.066),(right[0]+.020,.534),(left[0]-.020,.534)]])
 collision_box('fixture_receiver',[.37,.47,1.74],[.61,.53,2.125])
 # Cove approximates structural profile in three components, preserving recessed underside.
 collision_box('cove_rear_bearing',[-.70,.53,2.55],[.70,.65,2.80])
 collision_box('cove_upper_canopy_and_liner',[-.70,.30,2.728],[.70,.53,2.8])
 collision_hull('cove_lower_lip',[[x,y,z]for x in(-.70,.70)for y,z in[(.22,2.645),(.255,2.645),(.27,2.690),(.235,2.74),(.22,2.68)]])
 collision_hull('cove_upper_roll',[[x,y,z]for x in(-.70,.70)for y,z in[(.235,2.74),(.27,2.78),(.315,2.8),(.35,2.742),(.30,2.725),(.27,2.690)]])
 void('directory_front_reading_air',[-.39,.02,.92],[.32,.13,2.30],'Proposed front space inside component envelope; no solid directory panel across approach')
 void('cove_recessed_trough',[-.60,.29,2.57],[.60,.51,2.70],'Keep local cove recess open; excludes actual liner and lips')
 return 'Guest arrival directory and rolled cove return',{'intended_use':'A localized arrival landmark and static directory beside an unknown core; no host door, lintel or route system','reused_fixture_context':{'catalogue_id':'AST-GST-002','path_from_catalogue_root':'assets/guest_use/exports/AST-GST-002.glb','translation_source_m':[.49,.47,1.93],'rotation_z_deg':0,'receiver_normal_source':[0,-1,0],'fixture_rear_mount_normal_source':[0,1,0],'service_access':'Withdraw toward -Y, inspect retained diffuser from below. This is a geometric proposal, not certified service clearance.'}}

def crown_cushion(name,x0,x1,y0,y1,z0,ztop,role):
 # Four rings form real softened shoulders and a gently crowned broad seating surface.
 rings=[(x0+.025,x1-.025,y0+.025,y1-.025,z0),(x0,x1,y0,y1,z0+.032),(x0+.008,x1-.008,y0+.008,y1-.008,ztop-.021),(x0+.045,x1-.045,y0+.045,y1-.045,ztop)]
 vs=[]
 for xa,xb,ya,yb,z in rings:
  vs.extend((x,y,z)for x,y in[(xa+.035,ya),(xb-.035,ya),(xb,ya+.035),(xb,yb-.035),(xb-.035,yb),(xa+.035,yb),(xa,yb-.035),(xa,ya+.035)])
 fs=[tuple(reversed(range(8)))]+[(r*8+i,r*8+(i+1)%8,(r+1)*8+(i+1)%8,(r+1)*8+i)for r in range(3)for i in range(8)]+[tuple(24+i for i in range(8))]
 return mesh(name,vs,fs,role,0)
def waiting():
 # Three shaped structural cheeks support distinct seat and luggage activities.
 for x,name in[(-.66,'left'),(.075,'divider'),(.66,'right')]:
  profile=[(.060,.02),(.700,.02),(.700,.14),(.680,.19),(.660,.39),(.700,.63 if name=='left' else .405),(.64,.65 if name=='left' else .405),(.47,.64 if name=='left' else .405),(.38,.41),(.12,.405),(.04,.35),(.02,.22),(.02,.09)]
  extrude(name+'_swept_structural_cheek',profile,0,x-.04,x+.04,'warm_walnut',0,2)
  box(name+'_floor_isolation_shoe',(x,.355,.01),(.080,.59,.02),'dark_rubber',0,1)
  marker(name.upper()+'_FLOOR_CONTACT',[x,.355,0],'physical_floor_contact',name+'_floor_isolation_shoe',[0,0,-1])
 # Seat deck fitted between cheeks; meaningful open space remains below it.
 deck=extrude('seat_shaped_load_deck',[(-.62,.035),(-.57,0),(-.020,0),(.035,.048),(.035,.615),(-.62,.615)],2,.350,.383,'warm_walnut',.001,0)
 seat=crown_cushion('waiting_crowned_clay_seat',-.613,.024,.014,.60,.383,.46,'clay_weave')
 marker('WAITING_SEAT_CONTACT',[-.29,.30,.46],'physical_seat_contact',seat.name,[0,0,1],'Single proposed waiting contact plane, no actor/universal species fit or load rating')
 physical_joint('seat_to_deck',seat.name,deck.name,[-.30,.29,.383],[0,0,-1],[0,0,1])
 # Broad swept back shell carries reclined upholstery; height is a component target only.
 bp=[(.545,.382),(.598,.383),(.744,1.000),(.750,1.04),(.729,1.05),(.697,1.044),(.659,.968)]
 shell=extrude('reclined_walnut_back_shell',bp,0,-.62,.035,'warm_walnut',0,2)
 cushion=extrude('shaped_teal_waiting_back',[(.500,.463),(.525,.446),(.598,.468),(.724,.992),(.711,1.020),(.672,1.025),(.641,.997),(.517,.515)],0,-.603,.017,'teal_weave',.009,2)
 # Back cushion is intentionally layered on an actual leaned shell, with a real bearing contact.
 join('back_upholstery_to_shell',cushion.name,shell.name,[-.29,.680,.98])
 marker('WAITING_BACK_CONTACT',[-.29,.580,.760],'nonphysical_pose_reference',None,[0,-.979,.204],'Proposed waiting back pose; physical upholstery surface is checked separately by ray witness')
 marker('WAITING_POSITION',[-.29,.12,.70],'nonphysical_pose_reference',None,[0,-1,0])
 for x,nm in[(-.66,'left'),(.075,'divider')]:
  join('seat_deck_to_'+nm,deck.name,nm+'_swept_structural_cheek',[x+(.04 if nm=='left' else -.04),.33,.367])
 # Luggage slab stands beside the seat and is independently supported above an open bay.
 bag=extrude('separate_luggage_rounded_slab',[(.105,.09),(.15,.055),(.58,.055),(.63,.085),(.63,.650),(.585,.680),(.15,.680),(.105,.65)],2,.405,.447,'warm_walnut',.002,0)
 for x in(.205,.49):
  strip=tray('luggage_soft_bearing_'+str(x),(x,.365,.451),.055,.50,.008,'dark_rubber',.018)
  marker('LUGGAGE_CONTACT_'+str(x),[x,.365,.455],'physical_luggage_support',strip.name,[0,0,1])
 # Bay shelf has a front opening, with a real rear stop and no enclosing collider.
 shelf=extrude('lower_retrieval_shelf',[(.115,.13),(.15,.09),(.62,.09),(.62,.66),(.115,.66)],2,.092,.122,'warm_walnut',.001,0)
 marker('RETRIEVAL_SHELF_CONTACT',[.37,.33,.122],'physical_storage_support',shelf.name,[0,0,1])
 box('luggage_rear_stop',(.3675,.671,.29),(.505,.028,.31),'ivory_enamel',.002,0)
 for x,nm in[(.11,'divider'),(.625,'right')]:
  physical_joint('luggage_slab_to_'+nm,bag.name,nm+'_swept_structural_cheek',[x,.50,.405],[0,0,-1],[0,0,1])
  join('shelf_to_'+nm,shelf.name,nm+'_swept_structural_cheek',[.115 if nm=='divider' else .62,.33,.11])
 marker('RETRIEVAL_OPENING',[.37,.095,.26],'nonphysical_receiver_volume',None,[0,-1,0],'Useful fixed lower bag/personal-item shelf mouth; no moving drawer, guaranteed bag or hand fit')
 marker('LUGGAGE_PLACEMENT',[.37,.36,.64],'nonphysical_receiver_volume',None,[0,-1,0])
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',None,[0,0,1])
 for x,nm in[(-.66,'left'),(.075,'divider'),(.66,'right')]:
  lower=[(.06,0),(.65,0),(.70,.02),(.70,.14),(.68,.19),(.66,.39),(.38,.41),(.12,.405),(.04,.35),(.02,.22),(.02,.09),(.06,.02)]
  if nm!='left':lower +=[(.70,.405),(.47,.405)]
  collision_hull(nm+'_profiled_lower_cheek_and_shoe',[[xx,y,z]for xx in(x-.04,x+.04)for y,z in lower])
  if nm=='left':collision_hull('left_raised_swept_arm',[[xx,y,z]for xx in(x-.04,x+.04)for y,z in[(.38,.41),(.66,.39),(.70,.63),(.64,.65),(.47,.64)]])
 collision_box('seat_deck_and_cushion',[-.62,0,.35],[.035,.615,.46])
 collision_hull('reclined_shell_and_upholstery',[[x,y,z]for x in(-.62,.035)for y,z in[(.50,.446),(.598,.383),(.75,1.04),(.729,1.05),(.672,1.025)]])
 collision_box('luggage_slab_and_contact_strips',[.105,.055,.405],[.63,.68,.455])
 collision_box('retrieval_shelf',[.115,.09,.092],[.62,.66,.122])
 collision_box('luggage_rear_stop',[.115,.657,.135],[.62,.685,.445])
 void('lower_retrieval_open_bay',[.14,.03,.14],[.59,.63,.38],'Preserve fixed front-accessible shelf opening between structural cheeks')
 void('waiting_underseat_open_space',[-.58,.03,.035],[0,.48,.32],'Open foot-facing lower space under shaped deck; no whole-furniture hull')
 return 'Fitted single waiting seat and luggage edge',{'intended_use':'A shaped single waiting perch beside a lower luggage slab and a separate fixed retrieval shelf','seat_contact_source_z_m':.46,'luggage_contact_source_z_m':.455,'lower_shelf_source_z_m':.122,'back_shell_top_source_z_m':1.05,'moving_parts':False}

def measure():
 dg=bpy.context.evaluated_depsgraph_get();points=[];tri=0
 for o in PARTS:
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);points.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in points)for i in range(3)];hi=[max(p[i]for p in points)for i in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri
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
   p=me.polygons[pi];normal=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=normal];grain=int(src['grain_source_axis'])
   if src['material_role']=='warm_walnut'and grain in axes:axes=[i for i in axes if i!=grain]+[grain]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
  o=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(o)
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=obs[0];o.name=ident+'__'+role;o.parent=ROOT;o['material_role']=role;o['semantic_parts']=json.dumps([s.name for s in PARTS if s['material_role']==role]);out.append(o)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for o in out:o.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];coll={};api={};contexts={}
 only=sys.argv[sys.argv.index('--only')+1] if '--only'in sys.argv else None
 for ident,fn,ship in [('AST-LND-001',directory,[-39.2,0,-377.15]),('AST-LND-002',waiting,[-34.8,0,-377.05])]:
  if only and ident!=only:
   rec=json.loads((BASE/f'{ident}.manifest.json').read_text());rec['generator_sha256']=sha(Path(__file__));rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
   coll[ident]=json.loads((BASE/'collision_proposals.json').read_text())[ident];api[ident]=json.loads((BASE/'marker_api.json').read_text())[ident];contexts[ident]=json.loads((BASE/'qa_context_placements.json').read_text())[ident];continue
  reset(ident);title,details=fn();bpy.context.view_layer.update();bounds,tri=measure()
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  lo,hi=bounds['min_m'],bounds['max_m'];glo=[lo[0],lo[2],-hi[1]];ghi=[hi[0],hi[2],-lo[1]]
  rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_landing_guest.py','source_frame':'metres Blender Z-up, +X right, -Y front','exchange_frame':'metres GLB Y-up; source(x,y,z) -> (x,z,-y), actual node hierarchy authoritative','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'Component floor Z0, proposed host floor elevation unknown'},'bounds_blender_z_up':bounds,'bounds_gltf_y_up':{'min_m':glo,'max_m':ghi,'dimensions_m':[b-a for a,b in zip(glo,ghi)]},'dimensions_blender_xyz_m':bounds['dimensions_m'],'proposed_ship_placement':{'origin_ship_xyz_m':ship,'source_z_rotation_degrees':0,'ship_axes':'X transverse, Y up relative to unknown finished landing floor, Z longitudinal','source_to_ship_matrix':[[1,0,0,ship[0]],[0,0,1,ship[1]],[0,-1,0,ship[2]],[0,0,0,1]],'status':'Batch11 R3 inspection proposal only, no actual room/door/shaft/headroom authority'},'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role']for o in PARTS)),'runtime_consolidation':'Evaluated static copies by semantic material role; normalized active UV and retained marker hierarchy','physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['New independent catalogue; original ship unavailable','No actual room, actor/cart, game renderer, lift or runtime acceptance','No structural load rating, accessibility or universal species fit','QA fixture reuse is excluded from new exports and asset count','Component heights are proposed targets, not host headroom']}
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');coll[ident]={'source_frame':'metres Blender Z-up','exchange_frame':'metres GLB Y-up, explicitly converted','status':'Modest separate structural compounds only, no engine physics','shapes':COLL,'preserve_voids':VOIDS,'approximation_limits':'Bounds/hulls conservatively cover profile and contact surfaces; they are not triangle-exact or actor-tested. Cove recess, retrieval mouth and under-seat open space remain excluded.'};api[ident]=MARKERS
  if ident=='AST-LND-001':
   contexts[ident]={'fixture':{'catalogue_id':'AST-GST-002','path_from_catalogue_root':'assets/guest_use/exports/AST-GST-002.glb','source_local_transform_4x4':[[1,0,0,.49],[0,1,0,.47],[0,0,1,1.93],[0,0,0,1]],'gltf_local_transform_4x4':[[1,0,0,.49],[0,1,0,1.93],[0,0,1,-.47],[0,0,0,1]],'counted_as_new_asset':False,'included_in_production_export':False,'mount_witnesses':[{'receiver_part':'sconce_receiver_walnut_bearing','receiver_source_m':[.49,.47,1.93+z],'receiver_normal_source':[0,-1,0],'fixture_part':'shaped_wall_backplate','fixture_local_source_m':[0,0,z],'fixture_normal_source':[0,1,0]}for z in(-.11,0,.11)],'service_direction_source':[0,-1,0],'diffuser_service_access':'Proposed withdrawal toward source -Y and tool access from below; wiring and physical service reach are unverified'},'directory_cant_source_z_deg':20}
  else:contexts[ident]={'waiting_eye_proposal':{'source_m':[-.29,.17,1.19],'gltf_m':[-.29,1.19,-.17],'kind':'Nonphysical seated/waiting eye-height proposal, no actor or species fit'},'waiting_seat_contact':{'source_m':[-.29,.30,.46],'gltf_m':[-.29,.46,-.30],'part':'waiting_crowned_clay_seat','physical_normal_source':[0,0,1],'physical_normal_gltf':[0,1,0]}}
 (BASE/'manifest.json').write_text(json.dumps({'family':'landing_guest','revision':'landing-guest-01','assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n');(BASE/'qa_context_placements.json').write_text(json.dumps(contexts,indent=2)+'\n')
 print('BUILT',[(r['catalogue_id'],r['evaluated_source_triangles'],r['bounds_blender_z_up']['dimensions_m'])for r in rows])
if __name__=='__main__':main()
