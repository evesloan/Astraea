"""Original editable AST-CRW-003/004 personal crew fittings. Blender 4.3.2.
Source-only: blender -b -t 2 --python-exit-code 1 --python build_crew_personal.py
Metres, source Z up/front -Y; GLB maps (x,y,z)->(x,z,-y).
"""
import bpy,bmesh,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for p in ('source','exports','qa'): (BASE/p).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('crew_staff_materials',CAT/'standards/staff_materials.py');mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm);MATS=mm.materials()
W='staff_white_paint';B='staff_bluegrey_paint';Z='staff_zinc';R='staff_rubber';L='staff_label';O='staff_opal'
DRAWER_TRAVEL=.24
MOUNT={'source_asset':'AST-CRW-004','receiver_asset':'AST-CRW-001','source_frame':'metres Blender XYZ, Z-up','module_mount_plane':'local Y=0','module_normal_source':[0,1,0],'receiver_front_plane':'rest frame source Y=2.14','receiver_normal_source':[0,-1,0],'module_to_frame_translation_source_m':[-.26,2.14,.88],'module_to_frame_rotation_degrees_xyz':[0,0,0],'module_to_frame_translation_gltf_m':[-.26,.88,-2.14],'receiver_physical_part':'continuous headboard slab (receiver author supplies exact source name)','contact_witnesses':[{'module_source_m':[x,0,z],'frame_source_m':[x-.26,2.14,z+.88]}for x in(-.11,.11)for z in(-.12,.12)],'mounting_scope':'Real opposing flat surfaces in proposed frame/module pair; receiver and light/shelf load capacity, fastener engineering and host certification remain unverified. No external wall is invented.'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gl(p):return [p[0],p[2],-p[1]]
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,VOIDS,COLL,MOVE
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident
 PARTS=[];MARKERS=[];JOINS=[];VOIDS=[];COLL=[];MOVE=None
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident;sc['scope']='Original crew-use component, no game room allocation, occupancy or six-species fit'
def uv_assign(me,role):
 uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True;sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3)if i!=axis]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/sx,v[axes[1]]/sy)
 return uv
def mesh(name,verts,faces,role=W,bevel=0,parent=None):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=parent or ROOT;me.materials.append(MATS[role]);uv_assign(me,role);ob['material_role']=role;ob['authorship']='Original script-assisted personal crew fitting, 2026-10-03';ob['movement_group']='drawer'if parent==MOVE and MOVE else 'static'
 if bevel:
  mod=ob.modifiers.new('Editable formed edge easing','BEVEL');mod.width=bevel;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
  mod=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 PARTS.append(ob);return ob
def box(name,lo,hi,role=W,bevel=0,parent=None):
 x0,y0,z0=lo;x1,y1,z1=hi
 return mesh(name,[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,parent)
def extrude(name,profile,axis,lo,hi,role=W,bevel=0,parent=None):
 axes=[i for i in range(3)if i!=axis];v=[]
 for d in(lo,hi):
  for p in profile:
   q=[0,0,0];q[axis]=d;q[axes[0]]=p[0];q[axes[1]]=p[1];v.append(q)
 n=len(profile);return mesh(name,v,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,bevel,parent)
def clipped(x0,x1,y0,y1,c):return [(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1-c),(x1-c,y1),(x0+c,y1),(x0,y1-c),(x0,y0+c)]
def rod(name,a,b,r,role=Z,n=12,parent=None):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();seed=Vector((1,0,0))if abs(d.x)<.9 else Vector((0,1,0));u=d.cross(seed).normalized();v=d.cross(u)
 vv=[p+r*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n))for p in(a,b)for i in range(n)]
 return mesh(name,vv,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,0,parent)
def marker(name,p,kind,part=None,normal=None,parent=None,description=''):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.parent=parent or ROOT;ob.location=p;ob.empty_display_size=.018
 row={'name':name,'kind':kind,'source_m':p,'gltf_m':gl(p),'physical_part':part,'parent_root':ob.parent.name,'description':description}
 if normal:row.update(direction_source=normal,direction_gltf=gl(normal));ob['direction_source']=normal;ob['direction_gltf']=gl(normal)
 ob['marker_kind']=kind;ob['physical_part']=part or '';ob['source_position_m']=p;ob['gltf_position_m']=gl(p);MARKERS.append(row)
def joint(name,a,b,p,na=None,nb=None,kind='opposing_boundary_contact',group='static'):
 q={'name':name,'parts':[a,b],'probe_source_m':p,'probe_gltf_m':gl(p),'kind':kind,'movement_group':group}
 if na:q.update(normal_a_source=na,normal_b_source=nb,normal_a_gltf=gl(na),normal_b_gltf=gl(nb))
 JOINS.append(q)
def void(name,lo,hi,purpose,state='all'):
 VOIDS.append({'name':name,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':purpose,'state':state})
def hull(ob,others=None,note='Convex authored profile, conservative retained easing <= 2 mm'):
 obs=[ob]+(others or []);COLL.append({'name':ob.name+'_structural_profile','type':'convex_hull_points','points_source_m':[list(v.co)for o in obs for v in o.data.vertices],'points_gltf_m':[gl(v.co)for o in obs for v in o.data.vertices],'covered_parts':[o.name for o in obs],'parent_root':ob.parent.name,'movement_group':ob['movement_group'],'approximation_note':note})
def storage():
 global MOVE
 for x,side in[(-.26,'left'),(.26,'right')]:
  for y,end in[(-.16,'front'),(.16,'back')]:
   sole=box(side+'_'+end+'_floor_sole',[x-.040,y-.040,0],[x+.040,y+.040,.018],R,.001)
   foot=box(side+'_'+end+'_short_support',[x-.032,y-.032,.018],[x+.032,y+.032,.08],Z,.001)
   hull(sole,[foot],note='One local foot/sole compound; fills only hidden bevel and shoulder volume <=8 mm, preserves open space between feet')
   marker(side.upper()+'_'+end.upper()+'_FLOOR',[x,y,0],'physical_floor_contact',sole.name,[0,0,-1]);joint(side+'_'+end+'_sole_support',sole.name,foot.name,[x,y,.018],[0,0,1],[0,0,-1]);joint(side+'_'+end+'_support_plinth',foot.name,'protected_plinth',[x,y,.08],[0,0,1],[0,0,-1])
 plinth=extrude('protected_plinth',clipped(-.32,.32,-.21,.235,.018),2,.08,.16,B,.001);hull(plinth)
 sideprofile=[(-.21,.16),(.235,.16),(.235,1.34),(-.17,1.34),(-.21,1.28)]
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.32,-.30)if s<0 else(.30,.32)
  side=extrude(tag+'_formed_cheek',sideprofile,0,lo,hi,W,.001);hull(side)
  joint(tag+'_cheek_plinth',side.name,plinth.name,[s*.31,0,.16],[0,0,-1],[0,0,1]);joint(tag+'_cheek_cap',side.name,'protected_top_cap',[s*.31,0,1.34],[0,0,1],[0,0,-1])
 back=box('recessed_bluegrey_back',[-.30,.215,.16],[.30,.235,1.34],B,.001);hull(back)
 joint('back_plinth',back.name,plinth.name,[0,.225,.16],[0,0,-1],[0,0,1])
 for z0,z1,tag in[(.49,.52,'lower_open_shelf'),(.89,.91,'upper_open_shelf')]:
  shelf=box(tag,[-.30,-.205,z0],[.30,.215,z1],W,.001);hull(shelf)
  for s,side in[(-1,'left'),(1,'right')]:joint(tag+'_'+side+'_bearing',shelf.name,side+'_formed_cheek',[s*.30,0,(z0+z1)/2],[s,0,0],[-s,0,0])
  joint(tag+'_back_bearing',shelf.name,back.name,[0,.215,(z0+z1)/2],[0,1,0],[0,-1,0])
  liner=extrude(tag+'_replaceable_liner',clipped(-.285,.285,-.186,.20,.010),2,z1,z1+.005,L,.0006);hull(liner)
  joint(tag+'_liner_contact',liner.name,shelf.name,[0,0,z1],[0,0,-1],[0,0,1]);marker(tag.upper()+'_RESTING_SURFACE',[0,-.05,z1+.005],'physical_storage_contact',liner.name,[0,0,1],'',description='Useful open personal storage; no item, identity or ownership assignment')
 cap=extrude('protected_top_cap',clipped(-.32,.32,-.21,.235,.018),2,1.34,1.38,W,.002);hull(cap)
 joint('back_to_cap',back.name,cap.name,[0,.225,1.34],[0,0,1],[0,0,-1])
 # Stationary and drawer rails touch at their broad vertical bearing face. Their remaining overlap is 155 mm at full extension.
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.30,-.283)if s<0 else(.283,.30)
  rail=box(tag+'_fixed_drawer_runner',[lo,-.195,.25],[hi,.20,.278],Z);hull(rail)
  joint(tag+'_runner_cheek',rail.name,tag+'_formed_cheek',[s*.30,0,.264],[s,0,0],[-s,0,0])
 MOVE=bpy.data.objects.new('DRAWER_TRANSLATE',None);bpy.context.collection.objects.link(MOVE);MOVE.parent=ROOT;MOVE['motion_type']='bounded linear geometric proposal';MOVE['translation_source_axis']=[0,-1,0];MOVE['translation_gltf_axis']=[0,0,1];MOVE['travel_m']=DRAWER_TRAVEL;MOVE['runtime_interaction']='Unimplemented'
 bot=box('drawer_inner_base',[-.277,-.214,.195],[.277,.195,.213],B,0,MOVE);hull(bot)
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.277,-.261)if s<0 else(.261,.277)
  wall=box('drawer_'+tag+'_wall',[lo,-.214,.213],[hi,.195,.445],W,0,MOVE);hull(wall)
  joint('drawer_'+tag+'_base_contact',wall.name,bot.name,[s*.269,0,.213],[0,0,-1],[0,0,1],group='drawer')
  lo,hi=(-.283,-.277)if s<0 else(.277,.283)
  rail=box('drawer_'+tag+'_sliding_runner',[lo,-.195,.25],[hi,.20,.278],Z,0,MOVE);hull(rail)
  joint('drawer_'+tag+'_rail_wall',rail.name,wall.name,[s*.277,0,.264],[-s,0,0],[s,0,0],group='drawer')
  joint('drawer_'+tag+'_runner_bearing',rail.name,tag+'_fixed_drawer_runner',[s*.283,0,.264],[s,0,0],[-s,0,0],kind='sliding_boundary_contact',group='drawer_to_fixed')
 rear=box('drawer_back_wall',[-.261,.179,.213],[.261,.195,.445],W,0,MOVE);hull(rear);joint('drawer_rear_base',rear.name,bot.name,[0,.187,.213],[0,0,-1],[0,0,1],group='drawer')
 front=extrude('drawer_protected_front',[(-.296,.185),(.296,.185),(.296,.450),(.281,.465),(-.281,.465),(-.296,.450)],1,-.234,-.214,B,.001,MOVE);hull(front)
 joint('drawer_front_base',front.name,bot.name,[0,-.214,.203],[0,1,0],[0,-1,0],group='drawer')
 pull=box('drawer_pull_bridge',[-.11,-.296,.346],[.11,-.280,.364],Z,.003,MOVE);hull(pull)
 for x,tag in[(-.10,'left'),(.10,'right')]:
  bearing=box('drawer_'+tag+'_pull_return',[x-.010,-.280,.346],[x+.010,-.234,.364],Z,.001,MOVE);hull(bearing)
  joint('drawer_'+tag+'_pull_contact',bearing.name,pull.name,[x,-.280,.355],[0,-1,0],[0,1,0],group='drawer');joint('drawer_'+tag+'_pull_front',bearing.name,front.name,[x,-.234,.355],[0,1,0],[0,-1,0],group='drawer')
 marker('DRAWER_GRIP',[0,-.296,.355],'physical_hand_contact',pull.name,[0,-1,0],MOVE,'Grip moves with complete drawer root; no live interaction')
 marker('DRAWER_INNER_STORAGE',[0,0,.213],'physical_storage_contact',bot.name,[0,0,1],MOVE)
 marker('FLOOR_DATUM',[0,0,0],'placement_origin',description='Origin between four soles, not a physical centre floor contact')
 void('lower_open_retrieval_volume',[-.278,-.45,.54],[.278,.194,.875],'Full unobstructed front approach through useful lower opening, not anatomy/reach certification')
 void('upper_open_retrieval_volume',[-.278,-.45,.93],[.278,.194,1.31],'Full unobstructed front approach through useful upper opening')
 void('drawer_inner_useful_volume',[-.25,-.20,.224],[.25,.168,.43],'Actual hollow drawer interior in closed local pose; translates with drawer','drawer_local')
 void('pull_fingerspace',[-.075,-.274,.343],[.075,-.241,.366],'Empty central grip clearance; hand/body fit unknown','drawer_local')
 void('between_feet_underplinth',[-.20,-.20,.008],[.20,.20,.068],'Real open space between supported feet')
 return 'Personal open storage with controlled lower drawer',{'dimensions_proposed':True,'drawer_translation_source_m':[0,-DRAWER_TRAVEL,0],'drawer_translation_gltf_m':[0,0,DRAWER_TRAVEL],'useful_drawer_inner_dimensions_m':[.50,.368,.206],'runner_overlap_full_open_m':.155,'storage_use':'Two open personal-scale shelves and one hollow lower drawer; anonymous empty receiver volumes','motion_scope':'Geometric authored states and whole-part translation only; no live control, lock, ownership, item persistence or mechanism/load certification'}
def reading():
 plate=extrude('headboard_mount_backplate',clipped(-.14,.14,-.16,.18,.012),1,-.012,0,W,0);hull(plate)
 for x in(-.11,.11):
  for z in(-.12,.12):
   tag=('L'if x<0 else'R')+('_LOW'if z<0 else'_HIGH')
   marker('HEADBOARD_CONTACT_'+tag,[x,0,z],'physical_mount_contact',plate.name,[0,1,0],description='Opposes actual AST-CRW-001 headboard face after declared placement')
   bolt=rod('recessed_mount_washer_'+tag,[x,-.012,z],[x,-.016,z],.0075,Z);hull(bolt)
   joint('washer_'+tag+'_plate',bolt.name,plate.name,[x,-.012,z],[0,1,0],[0,-1,0])
 shelf=extrude('clipped_personal_shelf',clipped(-.17,.17,-.26,-.012,.018),2,-.145,-.125,W,.001);hull(shelf)
 joint('shelf_backplate',shelf.name,plate.name,[0,-.012,-.135],[0,1,0],[0,-1,0])
 for x,tag in[(-.155,'left'),(.155,'right')]:
  gus=extrude(tag+'_triangular_shelf_gusset',[(-.012,-.125),(-.218,-.125),(-.012,-.025)],0,x-.007,x+.007,Z,0);hull(gus)
  joint(tag+'_gusset_shelf',gus.name,shelf.name,[x,-.11,-.125],[0,0,-1],[0,0,1]);joint(tag+'_gusset_plate',gus.name,plate.name,[x,-.012,-.10],[0,1,0],[0,-1,0])
 liner=extrude('replaceable_small_shelf_liner',clipped(-.147,.147,-.239,-.032,.012),2,-.125,-.120,L,.0005);hull(liner)
 joint('liner_shelf',liner.name,shelf.name,[0,-.13,-.125],[0,0,-1],[0,0,1]);marker('PERSONAL_SHELF_SURFACE',[0,-.13,-.120],'physical_resting_surface',liner.name,[0,0,1])
 arm=box('supported_light_return_arm',[-.025,-.09,.1525],[.025,-.012,.1775],Z,.001);hull(arm);joint('light_arm_plate',arm.name,plate.name,[0,-.012,.165],[0,1,0],[0,-1,0])
 hood=extrude('formed_shield_top',[(-.19,.170),(-.17,.20),(-.060,.20),(-.040,.18),(-.055,.170)],0,-.14,.14,W,.001);hull(hood)
 joint('light_arm_hood',arm.name,hood.name,[0,-.075,.174],kind='buried_structural_overlap')
 front=extrude('lowered_front_glare_shield',[(-.19,.13),(-.176,.13),(-.166,.17),(-.19,.17)],0,-.14,.14,B,.0006);hull(front);joint('front_shield_hood',front.name,hood.name,[0,-.18,.17],[0,0,1],[0,0,-1])
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.14,-.126)if s<0 else(.126,.14)
  side=extrude(tag+'_light_end_shield',[(-.176,.13),(-.055,.148),(-.055,.17),(-.166,.17)],0,lo,hi,B,.0006);hull(side);joint(tag+'_shield_hood',side.name,hood.name,[s*.133,-.10,.17],[0,0,1],[0,0,-1])
 diffuser=extrude('recessed_task_light_diffuser',clipped(-.116,.116,-.158,-.065,.010),2,.160,.170,O,.0005);hull(diffuser);joint('diffuser_hood_support',diffuser.name,hood.name,[0,-.10,.17],[0,0,1],[0,0,-1])
 marker('PROPOSED_EMITTER_SURFACE',[0,-.11,.160],'physical_proposed_emitter_surface',diffuser.name,[0,0,-1],description='Opal art surface and proposed local emitter position; material emits no light and actual runtime light/photometry are unimplemented')
 marker('PROPOSED_LIGHT_AIM',[0,-.11,.160],'nonphysical_light_aim',description='Suggested local down/forward aim (0,-.22,-.98), distinct from physical diffuser normal (0,0,-1)')
 control=box('proposed_local_control_pad',[.080,-.020,.018],[.114,-.012,.046],R,.003);hull(control);joint('control_pad_backplate',control.name,plate.name,[.097,-.012,.032],[0,1,0],[0,-1,0]);marker('PROPOSED_LIGHT_CONTROL',[.097,-.020,.032],'physical_control_proposal',control.name,[0,-1,0],description='Physical proposed button face; no game input or implemented electrical control')
 marker('MOUNT_DATUM',[0,0,0],'physical_mount_origin',plate.name,[0,1,0]);void('shelf_useful_retrieval_volume',[-.132,-.40,-.105],[.132,-.037,.04],'Open supported small personal resting area and front retrieval; no item or occupant identity')
 return 'Headboard-mounted individual reading light and shelf',{'mount_contract':'mount_contract.json','envelope_relative_to_mount_datum_m':[.34,.26,.36],'proposed_emitter_position_source_m':[0,-.11,.16],'proposed_light_aim_source':[0,-.22,-.98],'material_emission_strength':0,'light_scope':'Visible shaped opal diffuser and local aim/control interfaces only, no light objects, active emitter, working input, electrical/load design or runtime photometry','shelf_source_top_m':-.120,'shelf_world_proposed_top_m':.760}
def bounds():
 p=[];tri=0;dg=bpy.context.evaluated_depsgraph_get()
 for o in PARTS:
  e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);p.extend(o.matrix_world@v.co for v in me.vertices);e.to_mesh_clear()
 lo=[min(q[i]for q in p)for i in range(3)];hi=[max(q[i]for q in p)for i in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i]for i in range(3)]},tri
def export(ident,suffix=''):
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
   p=me.polygons[pi];axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=axis]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
  ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault((src.parent.name,src['material_role']),[]).append(ob)
 for (parent,role),obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+('drawer__'if parent=='DRAWER_TRANSLATE'else'static__')+role;world=ob.matrix_world.copy();ob.parent=bpy.data.objects[parent];ob.matrix_world=world;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in PARTS if s.parent.name==parent and s['material_role']==role]);out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 if MOVE:MOVE.select_set(True)
 for ob in out:ob.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT;bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}{suffix}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)
def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];coll={};api={}
 for ident,fn in[('AST-CRW-003',storage),('AST-CRW-004',reading)]:
  reset(ident);title,details=fn();bpy.context.view_layer.update();bb,tri=bounds()
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  states=[]
  if MOVE:
   MOVE.location.y=-DRAWER_TRAVEL;bpy.context.view_layer.update();ob,ot=bounds();export(ident,'_open');states.append({'name':'drawer_fully_open','export':f'exports/{ident}_open.glb','root':'DRAWER_TRANSLATE','translation_source_m':[0,-DRAWER_TRAVEL,0],'translation_gltf_m':[0,0,DRAWER_TRAVEL],'bounds_source':ob,'glb_sha256':sha(BASE/'exports'/f'{ident}_open.glb')});MOVE.location.y=0;bpy.context.view_layer.update()
  lo,hi=bb['min_m'],bb['max_m'];glo=[lo[0],lo[2],-hi[1]];ghi=[hi[0],hi[2],-lo[1]]
  rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_crew_personal.py','source_frame':'metres Blender X width Y depth Z-up, front -Y','exchange_frame':'metres native GLB Y-up source(x,y,z)->(x,z,-y)','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'floor origin'if ident.endswith('003')else'rear mounting plane centre'},'bounds_blender_z_up':bb,'bounds_gltf_y_up':{'min_m':glo,'max_m':ghi,'dimensions_m':[b-a for a,b in zip(glo,ghi)]},'dimensions_blender_xyz_m':bb['dimensions_m'],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted({o['material_role']for o in PARTS}),'runtime_consolidation':'Static evaluated copies consolidated by material; drawer copies consolidated by material under sole actual moving root; physical moving markers parented to it','physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'state_derivatives':states,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Proposed component dimensions only; no final host room, berth keys, roommate identity or story','Zero new people and zero registered berths; shared-player programme remains within 400 crew','No species fitting, loading, anatomy/reach, runtime controls, illumination, engine collision or performance acceptance']}
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');coll[ident]={'source_frame':'metres Blender Z-up','exchange_frame':'metres native GLB Y-up','status':'Profile-following compound proposals only; not game collision','shapes':COLL,'preserve_voids':VOIDS,'limits':'Purposeful separate convex parts preserve shelves, drawer interior, grip gap and support spaces; bevel/profile approximation measured by QA, no whole-asset enclosing hull'};api[ident]=MARKERS
 (BASE/'manifest.json').write_text(json.dumps({'family':'crew_personal','revision':'crew-personal-01','unique_designs':2,'assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n');(BASE/'mount_contract.json').write_text(json.dumps(MOUNT,indent=2)+'\n')
 deps=[Path(__file__),CAT/'standards/staff_materials.py',CAT/'materials/staff/manifest.json']+[CAT/'materials/staff'/v['file']for v in json.loads((CAT/'materials/staff/manifest.json').read_text())['materials'].values()]
 (BASE/'dependency_manifest.json').write_text(json.dumps({'schema':'crew_personal_source_only_inputs_v1','inputs':[{'path_from_catalogue_root':str(p.relative_to(CAT)),'sha256':sha(p)}for p in deps],'count':len(deps),'closure_note':'All nine staff textures included because helper loads every role, including roles not used by these assets; references and QA images never read by generator'},indent=2)+'\n')
 print('CREW_PERSONAL_BUILT',[(r['catalogue_id'],r['evaluated_triangles'],r['dimensions_blender_xyz_m'])for r in rows])
if __name__=='__main__':main()
