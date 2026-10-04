"""Original editable audience/backstage fittings. Blender 4.3.2. Metres Z-up/front -Y.
Rebuild: python source/draw_markings.py; blender -b -t 2 --python-exit-code 1 --python source/build_auditorium_use.py
"""
import bpy,bmesh,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for p in ('source','exports','qa'):(BASE/p).mkdir(parents=True,exist_ok=True)
MATS={}
for helper in ('auditorium_materials','staff_materials'):
 spec=importlib.util.spec_from_file_location(helper,CAT/'standards'/f'{helper}.py');mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm);MATS.update(mm.materials())
WOOD='warm_walnut';METAL='champagne_metal';CLOTH='auditorium_amber_velvet';NAVY='auditorium_navy_fibre'
W='staff_white_paint';B='staff_bluegrey_paint';Z='staff_zinc';R='staff_rubber';L='staff_label';O='staff_opal'
MOVES={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gl(p):return [p[0],p[2],-p[1]]
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,VOIDS,COLL,MOVE
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident
 PARTS=[];MARKERS=[];JOINS=[];VOIDS=[];COLL=[];MOVE=None;MOVES.clear()
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident;sc['scope']='Original audience/backstage component, no host placement, additional capacity, working controls or six-species fit'
def uv_assign(me,role):
 uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True;sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3)if i!=axis]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/sx,v[axes[1]]/sy)
 return uv
def mesh(name,verts,faces,role=W,bevel=0,parent=None):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=parent or ROOT;me.materials.append(MATS[role]);uv_assign(me,role);ob['material_role']=role;ob['authorship']='Original script-assisted personal auditorium fitting, 2026-10-03';ob['movement_group']=parent.name if parent and parent!=ROOT else 'static'
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
 bpy.context.view_layer.update(); world=ob.matrix_world.translation; row={'name':name,'kind':kind,'source_m':list(world),'gltf_m':gl(world),'parent_local_source_m':list(p),'physical_part':part,'parent_root':ob.parent.name,'description':description}
 if normal:row.update(direction_source=normal,direction_gltf=gl(normal));ob['direction_source']=normal;ob['direction_gltf']=gl(normal)
 ob['marker_kind']=kind;ob['physical_part']=part or '';ob['source_position_m']=p;ob['gltf_position_m']=gl(p);MARKERS.append(row)
def joint(name,a,b,p,na=None,nb=None,kind='opposing_boundary_contact',group='static'):
 q={'name':name,'parts':[a,b],'probe_source_m':p,'probe_gltf_m':gl(p),'kind':kind,'movement_group':group}
 if na:q.update(normal_a_source=na,normal_b_source=nb,normal_a_gltf=gl(na),normal_b_gltf=gl(nb))
 JOINS.append(q)
def void(name,lo,hi,purpose,state='all'):
 VOIDS.append({'name':name,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':purpose,'state':state})
def hull(ob,others=None,note='Convex authored profile, conservative retained easing <= 2 mm'):
 obs=[ob]+(others or []);COLL.append({'name':ob.name+'_structural_profile','type':'convex_hull_points','points_source_m':[list(o.matrix_world@v.co)for o in obs for v in o.data.vertices],'points_gltf_m':[gl(o.matrix_world@v.co)for o in obs for v in o.data.vertices],'covered_parts':[o.name for o in obs],'parent_root':ob.parent.name,'movement_group':ob['movement_group'],'approximation_note':note})
def pivot(name,p,kind,travel):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob.location=p;ob['motion_type']=kind;ob['axis_source']=[1,0,0]if kind=='rotation'else[0,1,0];ob['axis_gltf']=gl(ob['axis_source']);ob['travel_degrees_or_m']=travel;ob['runtime_status']='unimplemented geometric proposal';MOVES[name]=ob;return ob
def convex(name,verts,role,parent=None):
 from mathutils.geometry import tessellate_polygon
 # Authored ring lofts below supply deliberate faces; generic convex helper uses bmesh hull.
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],[]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=parent or ROOT;me.materials.append(MATS[role]);me.update();uv_assign(me,role);ob['material_role']=role;ob['movement_group']=parent.name if parent else'static';ob['authorship']='Original explicitly shaped audience/backstage component';PARTS.append(ob);return ob
def pillow(name,outline,axis,depths,scales,role,parent=None,lean=0):
 axes=[i for i in range(3)if i!=axis];cx=sum(p[0]for p in outline)/len(outline);cy=sum(p[1]for p in outline)/len(outline);v=[]
 for d,sc in zip(depths,scales):
  for px,py in outline:
   q=[0.,0.,0.];q[axes[0]]=cx+(px-cx)*sc;q[axes[1]]=cy+(py-cy)*sc;q[axis]=d+lean*q[axes[1]];v.append(q)
 return convex(name,v,role,parent)
def cshape(ob,others=None,note='Exact convex authored shape; no added clearance inflation or omitted faces'):
 bpy.context.view_layer.update();hull(ob,others,note)
def seat():
 global MOVE
 # The side/end silhouettes are full depth load-path proposals; no isolated decorative ribs.
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.326,-.282)if s<0 else(.282,.326)
  foot=extrude(tag+'_continuous_floor_runner',clipped(lo-.013,hi+.013,-.325,.325,.011),2,0,.035,METAL);cshape(foot)
  side=extrude(tag+'_shaped_timber_end',[(-.29,.035),(.29,.035),(.255,.705),(-.16,.705),(-.265,.62)],0,lo,hi,WOOD);cshape(side)
  joint(tag+'_end_to_floor_runner',side.name,foot.name,[s*.304,0,.035],[0,0,-1],[0,0,1])
  arm=extrude(tag+'_rounded_arm_cap',clipped(lo-.018,hi+.018,-.30,.273,.022),2,.705,.735,WOOD);cshape(arm)
  joint(tag+'_arm_end_support',arm.name,side.name,[s*.304,0,.705],[0,0,-1],[0,0,1]);marker(tag.upper()+'_ARM_REST',[s*.304,-.10,.735],'physical_arm_contact',arm.name,[0,0,1])
  marker(tag.upper()+'_FLOOR_CONTACT',[s*.304,0,0],'physical_floor_contact',foot.name,[0,0,-1])
  # Thin fibre return terminates on side surface, never shares an exposed same-facing plane.
  elo,ehi=(-.329,-.326)if s<0 else(.326,.329)
  inset=extrude(tag+'_navy_fibre_end_return',[(-.20,.16),(.21,.16),(.185,.63),(-.12,.63)],0,elo,ehi,NAVY);cshape(inset)
  joint(tag+'_fibre_to_end',inset.name,side.name,[s*.326,0,.4],[-s,0,0],[s,0,0])
  # Bearing stubs reach the actual end-face pan pivots at ±.265.
  a,b=([-.282,.10,.44],[-.265,.10,.44])if s<0 else([.265,.10,.44],[.282,.10,.44])
  stub=rod(tag+'_fixed_pivot_stub',a,b,.030,METAL,12);cshape(stub)
  joint(tag+'_stub_end_bearing',stub.name,side.name,[s*.282,.10,.44],[s,0,0],[-s,0,0])
  marker(tag.upper()+'_FIXED_HINGE_BEARING',[s*.265,.10,.44],'physical_fixed_hinge_contact',stub.name,[-s,0,0])
 rail=box('lower_rear_cross_tie',[-.282,.23,.12],[.282,.27,.17],WOOD);cshape(rail)
 for s,tag in[(-1,'left'),(1,'right')]:joint(tag+'_rear_tie_end',rail.name,tag+'_shaped_timber_end',[s*.282,.25,.145],[s,0,0],[-s,0,0])
 back_outline=[(-.232,.54),(.232,.54),(.282,.64),(.282,.98),(.240,1.10),(-.240,1.10),(-.282,.98),(-.282,.64)]
 # y=0.104+0.15*z is the front; silhouette bows gently across crown/corners.
 shell=pillow('swept_crown_back_shell',back_outline,1,[.104,.154],[1,1],WOOD,lean=.15);cshape(shell)
 for s,tag in[(-1,'left'),(1,'right')]:joint(tag+'_back_to_end',shell.name,tag+'_shaped_timber_end',[s*.282,.223,.665],kind='boundary_contact')
 cushion_outline=[(-.204,.595),(.204,.595),(.243,.67),(.243,.967),(.210,1.065),(-.210,1.065),(-.243,.967),(-.243,.67)]
 back=pillow('contoured_amber_back_pad',cushion_outline,1,[.104,.059,.049],[1,1,.89],CLOTH,lean=.15);cshape(back)
 joint('back_pad_to_shell',back.name,shell.name,[0,.104+.15*.82,.82],kind='boundary_contact')
 marker('BACK_SUPPORT_SURFACE',[0,.049+.15*.82,.82],'physical_back_contact',back.name,[0,-1/math.sqrt(1+.15**2),.15/math.sqrt(1+.15**2)])
 MOVE=pivot('PAN_HINGE_X',[0,.10,.44],'rotation',-78)
 pan=extrude('folding_timber_pan',clipped(-.245,.245,-.56,0,.032),2,-.032,0,WOOD,0,MOVE);cshape(pan)
 for s,tag in[(-1,'left'),(1,'right')]:
  a,b=([-.265,0,0],[-.235,0,0])if s<0 else([.235,0,0],[.265,0,0])
  ear=rod(tag+'_moving_hinge_ear',a,b,.030,WOOD,12,MOVE);cshape(ear)
  joint(tag+'_pan_to_hinge_ear',ear.name,pan.name,[s*.240,.086,.425],kind='buried_structural_overlap',group='PAN_HINGE_X')
  joint(tag+'_rotating_bearing_contact',ear.name,tag+'_fixed_pivot_stub',[s*.265,.10,.44],[s,0,0],[-s,0,0],kind='rotating_endface_bearing',group='PAN_HINGE_X_to_fixed')
  marker(tag.upper()+'_MOVING_HINGE_BEARING',[s*.265,0,0],'physical_moving_hinge_contact',ear.name,[s,0,0],MOVE)
 panpad=pillow('shaped_amber_seat_pad',clipped(-.232,.232,-.54,-.028,.04),2,[0,.039,.052],[1,1,.90],CLOTH,MOVE);cshape(panpad)
 joint('seat_pad_pan_support',panpad.name,pan.name,[0,-.18,.44],[0,0,-1],[0,0,1],group='PAN_HINGE_X')
 marker('SEAT_REST_SURFACE',[0,-.27,.052],'physical_seat_contact',panpad.name,[0,0,1],MOVE)
 marker('PAN_LIFT_FRONT_EDGE',[0,-.56,-.016],'physical_pan_lift_proposal',pan.name,[0,-1,0],MOVE,'Geometric front edge, no live interaction')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',description='Floor between runners; not a physical central support')
 for s,tag in[(-1,'LEFT'),(1,'RIGHT')]:marker('OPTIONAL_ROW_MATE_'+tag,[s*.37,0,0],'nonphysical_proposed_row_mating_datum',description='Proposed 0.74m centre spacing QA only; actual row pitch, curvature and species transfer unknown')
 void('under_pan_open_space',[-.24,-.40,.06],[.24,.16,.37],'Actual underpan void in closed state, not a body/foot clearance certificate','closed')
 void('folded_front_recovery_volume',[-.24,-.47,.47],[.24,-.12,.95],'Space recovered ahead of raised pan, bounded proposal only','folded')
 void('dry_seat_use_reservation',[-.23,-.38,.52],[.23,.03,.93],'Useful geometric reservation above pan, no anatomy or species fit','closed')
 return 'Lantern audience fold-up seat/end module',{'budget':{'max_triangles':900,'max_material_roles':4,'max_export_mesh_groups':6},'pan_motion':{'root':'PAN_HINGE_X','pivot_source_m':[0,.10,.44],'pivot_gltf_m':[0,.44,-.10],'axis_source':[1,0,0],'axis_gltf':[1,0,0],'closed_degrees':0,'folded_degrees':-78},'adjacent_QA_only':{'translation_source_m':[.74,0,0],'translation_gltf_m':[.74,0,0],'no_host_row_assignment':True},'full_load_mechanism':'Supported geometric end-face bearings only; locks, damping, spring, fatigue, fasteners and load approval remain unimplemented/unverified','no_new_capacity':True}
def workstand():
 global MOVE
 for x in(-.28,.28):
  for y in(-.22,.22):
   tag=('left'if x<0 else'right')+('_front'if y<0 else'_rear')
   foot=box(tag+'_rubber_sole',[x-.045,y-.045,0],[x+.045,y+.045,.018],R);cshape(foot)
   marker(tag.upper()+'_FLOOR',[x,y,0],'physical_floor_contact',foot.name,[0,0,-1]);joint(tag+'_sole_base',foot.name,'clipped_ballast_base',[x,y,.018],[0,0,1],[0,0,-1])
 base=extrude('clipped_ballast_base',clipped(-.36,.36,-.31,.31,.065),2,.018,.060,B);cshape(base)
 # Open-backed fabricated column: three convex walls, real hollow service route.
 front=box('service_column_front_web',[-.049,.075,.06],[.049,.095,1.40],Z);cshape(front);joint('column_front_base',front.name,base.name,[0,.085,.06],[0,0,-1],[0,0,1])
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.049,-.035)if s<0 else(.035,.049)
  side=box('service_column_'+tag+'_wall',[lo,.095,.06],[hi,.175,1.40],B);cshape(side);joint(tag+'_column_base',side.name,base.name,[s*.042,.13,.06],[0,0,-1],[0,0,1]);joint(tag+'_column_front_web',side.name,front.name,[s*.042,.095,.8],[0,-1,0],[0,1,0])
 cable=rod('protected_internal_cable_proposal',[0,.137,.12],[0,.137,1.33],.006,R,8);cshape(cable)
 for z in(.18,.70,1.28):
  clamp=box('cable_retention_'+str(z),[-.035,.122,z-.012],[.035,.143,z+.012],R);cshape(clamp)
  joint('cable_clamp_'+str(z),clamp.name,cable.name,[0,.137,z],kind='buried_structural_overlap')
  for s,tag in[(-1,'left'),(1,'right')]:joint('clamp_'+str(z)+'_'+tag,clamp.name,'service_column_'+tag+'_wall',[s*.035,.13,z],[s,0,0],[-s,0,0])
 service=pivot('REAR_COVER_REMOVE',[0,0,0],'translation',.22)
 cover=box('removable_rear_service_cover',[-.049,.175,.09],[.049,.187,1.36],B,0,service);cshape(cover)
 for s,tag in[(-1,'left'),(1,'right')]:joint(tag+'_cover_support',cover.name,'service_column_'+tag+'_wall',[s*.042,.175,.70],[0,-1,0],[0,1,0],group='REAR_COVER_REMOVE_to_fixed')
 grip=box('rear_cover_pull_bridge',[-.018,.213,.69],[.018,.226,.73],Z,0,service);cshape(grip)
 for x,tag in[(-.012,'left'),(.012,'right')]:
  ret=box('rear_pull_'+tag+'_return',[x-.006,.187,.69],[x+.006,.213,.73],Z,0,service);cshape(ret);joint('rear_pull_'+tag+'_cover',ret.name,cover.name,[x,.187,.71],[0,-1,0],[0,1,0],group='REAR_COVER_REMOVE');joint('rear_pull_'+tag+'_bridge',ret.name,grip.name,[x,.213,.71],[0,1,0],[0,-1,0],group='REAR_COVER_REMOVE')
 marker('REAR_SERVICE_GRIP',[0,.226,.71],'physical_service_grip',grip.name,[0,1,0],service)
 marker('SERVICE_INSPECTION_DATUM',[0,.15,.94],'nonphysical_service_route_datum',description='Open backed channel behind cover; proposed cable only, no powered system')
 tray=extrude('supported_clipped_work_tray',clipped(-.29,.29,-.33,.075,.035),2,.94,.962,B);cshape(tray)
 joint('tray_column_web',tray.name,front.name,[0,.075,.951],[0,1,0],[0,-1,0])
 for x,tag in[(-.041,'left'),(.041,'right')]:
  gus=extrude(tag+'_tray_gusset',[(-.255,.94),(.075,.94),(.075,.75)],0,x-.007,x+.007,Z);cshape(gus);joint(tag+'_gusset_tray',gus.name,tray.name,[x,-.08,.94],[0,0,1],[0,0,-1]);joint(tag+'_gusset_web',gus.name,front.name,[x,.075,.86],[0,1,0],[0,-1,0])
 lip=box('front_paper_retaining_lip',[-.255,-.33,.962],[.255,-.316,.985],Z);cshape(lip);joint('paper_lip_tray',lip.name,tray.name,[0,-.323,.962],[0,0,-1],[0,0,1])
 marker('WORK_SURFACE',[0,-.11,.962],'physical_work_surface',tray.name,[0,0,1])
 board=extrude('clipped_cue_notes_backer',clipped(-.225,.225,1.01,1.30,.025),1,.045,.075,B);cshape(board);joint('notes_backer_column',board.name,front.name,[0,.075,1.15],[0,1,0],[0,-1,0])
 face=box('inactive_rehearsal_notes_face',[-.205,.040,1.03],[.205,.045,1.28],'original_rehearsal_notes');cshape(face);joint('notes_face_backer',face.name,board.name,[0,.045,1.15],[0,1,0],[0,-1,0])
 # Explicit rectangular graphic UV, source front -Y; only frontal surface carries whole card.
 uv=face.data.uv_layers.active
 for po in face.data.polygons:
  if abs(po.normal.y)<.9:continue
  for li in po.loop_indices:
   co=face.data.vertices[face.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.205)/.410,(co.z-1.03)/.250)
 marker('INACTIVE_CUE_NOTES_FACE',[0,.04,1.16],'physical_notes_surface',face.name,[0,-1,0])
 bar=box('light_yoke_crossbar',[-.226,.075,1.40],[.226,.155,1.425],Z);cshape(bar);joint('yoke_column_top',bar.name,front.name,[0,.085,1.40],[0,0,-1],[0,0,1])
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.226,-.204)if s<0 else(.204,.226)
  pr=extrude(tag+'_light_yoke_upright',[(.075,1.425),(.155,1.425),(.155,1.56),(.115,1.58),(.075,1.56)],0,lo,hi,Z);cshape(pr);joint(tag+'_yoke_bar',pr.name,bar.name,[s*.215,.115,1.425],[0,0,-1],[0,0,1])
  a,b=([-.204,.115,1.54],[-.180,.115,1.54])if s<0 else([.180,.115,1.54],[.204,.115,1.54])
  stub=rod(tag+'_fixed_aim_stub',a,b,.023,Z,12);cshape(stub);joint(tag+'_aim_stub_yoke',stub.name,pr.name,[s*.204,.115,1.54],[s,0,0],[-s,0,0])
 MOVE=pivot('LIGHT_AIM_X',[0,.115,1.54],'rotation',-25)
 hood=extrude('formed_light_hood',[(-.255,.035),(-.215,.085),(.035,.085),(.065,.050),(.065,.022),(-.255,.022)],0,-.180,.180,B,0,MOVE);cshape(hood)
 rear=box('light_rear_spine',[-.18,.035,-.050],[.18,.065,.022],B,0,MOVE);cshape(rear);joint('hood_rear_spine',hood.name,rear.name,[0,.16,1.562],[0,0,-1],[0,0,1],group='LIGHT_AIM_X')
 for s,tag in[(-1,'left'),(1,'right')]:
  lo,hi=(-.180,-.164)if s<0 else(.164,.180)
  cheek=extrude(tag+'_light_end_shield',[(-.255,-.050),(.065,-.050),(.065,.022),(-.255,.022)],0,lo,hi,B,0,MOVE);cshape(cheek)
  joint(tag+'_shield_hood',cheek.name,hood.name,[s*.172,0,1.562],[0,0,1],[0,0,-1],group='LIGHT_AIM_X')
  joint(tag+'_aim_bearing',cheek.name,tag+'_fixed_aim_stub',[s*.18,.115,1.54],[s,0,0],[-s,0,0],kind='rotating_endface_bearing',group='LIGHT_AIM_X_to_fixed')
  marker(tag.upper()+'_MOVING_AIM_BEARING',[s*.18,0,0],'physical_aim_bearing',cheek.name,[s,0,0],MOVE)
 frontshield=box('downturned_glare_shield',[-.164,-.255,-.060],[.164,-.237,.022],B,0,MOVE);cshape(frontshield);joint('front_shield_hood',frontshield.name,hood.name,[0,-.13,1.562],[0,0,1],[0,0,-1],group='LIGHT_AIM_X')
 diff=box('recessed_opal_diffuser',[-.147,-.223,.010],[.147,.023,.022],O,0,MOVE);cshape(diff);joint('diffuser_hood',diff.name,hood.name,[0,.015,1.562],[0,0,1],[0,0,-1],group='LIGHT_AIM_X')
 marker('PROPOSED_EMITTER_SURFACE',[0,-.10,.010],'physical_proposed_emitter_surface',diff.name,[0,0,-1],MOVE,'Opal art surface; material emission zero and no real light object')
 marker('PROPOSED_LIGHT_AIM',[0,-.10,.010],'nonphysical_light_aim',None,[0,0,-1],MOVE,'Proposed downward direction; separate from runtime light/photometry')
 control=box('inactive_local_control_pad',[.09,.065,-.032],[.135,.075,.003],R,0,MOVE);cshape(control);joint('control_rear_spine',control.name,rear.name,[.1125,.18,1.5255],[0,-1,0],[0,1,0],group='LIGHT_AIM_X')
 marker('PROPOSED_LOCAL_CONTROL',[.1125,.075,-.014],'physical_inactive_control_proposal',control.name,[0,1,0],MOVE,'No working cue protocol, lamp input or electrical state')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',description='Floor between soles; ballasted-base appearance, no stability/load certification')
 void('work_surface_clear_use',[-.25,-.30,.993],[.25,.010,1.25],'Useful front work/retrieval reservation, separate from notes card and lip')
 void('rear_cover_grip_opening',[-.005,.191,.695],[.005,.210,.725],'Small central pull opening; not a certified hand envelope','cover_local')
 void('service_channel_upper_clearance',[-.028,.149,.99],[.028,.171,1.20],'Bounded open service volume behind removable cover; remaining internal cable intentionally outside this reserved strip')
 void('rear_service_approach',[-.25,.42,.12],[.25,.75,1.36],'Proposed complete removal/retrieval approach behind translated cover, host route unknown')
 return 'Backstage shielded cue and work-light stand',{'context':'Separate D11_service workshop use proposal; no inferred physical connection to theatre wings','aim_motion':{'root':'LIGHT_AIM_X','pivot_source_m':[0,.115,1.54],'pivot_gltf_m':[0,1.54,-.115],'axis_source':[1,0,0],'axis_gltf':[1,0,0],'range_degrees':[0,-25]},'service_motion':{'root':'REAR_COVER_REMOVE','translation_source_m':[0,.22,0],'translation_gltf_m':[0,0,-.22],'type':'Supported at closed boundary; complete lift-off cover translation as a handling proposal, no retained hinge'},'work_surface_height_m':.962,'inactive_marking':'WORK / REHEARSAL / CUE NOTES / INACTIVE','electrical_scope':'Protected proposed cable and non-emissive diffuser, no outlet assignment, powered cable, flexible joint wiring, active cue/control, photometry or stage certification','light_material_emission_strength':0}
def original_material():
 im=bpy.data.images.load(str(BASE/'source/rehearsal_notes.png'));im.pack();mat=bpy.data.materials.new('ASTRAEA_original_rehearsal_notes');mat.use_nodes=True;mat['astraea_material_role']='original_rehearsal_notes';mat['meters_per_tile_uv']=[.410,.250];bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.88;tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);MATS['original_rehearsal_notes']=mat

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
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+(parent+'__'if parent!=ROOT.name else'static__')+role;world=ob.matrix_world.copy();ob.parent=bpy.data.objects[parent];ob.matrix_world=world;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in PARTS if s.parent.name==parent and s['material_role']==role]);out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for move in MOVES.values():move.select_set(True)
 for ob in out:ob.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT;bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}{suffix}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)
def main():
 bpy.context.preferences.filepaths.save_version=0;original_material();rows=[];coll={};api={}
 for ident,fn in[('AST-CUL-003',seat),('AST-CUL-004',workstand)]:
  reset(ident);title,details=fn();bpy.context.view_layer.update();bb,tri=bounds()
  # Capture the true closed local/source transforms before terminal-state derivatives.
  motion_records=[]
  for name,move in MOVES.items():
   parts=[o.name for o in PARTS if o.parent==move];motion_records.append({'root':name,'kind':move['motion_type'],'pivot_source_m':list(move.location),'pivot_gltf_m':gl(move.location),'axis_source':list(move['axis_source']),'axis_gltf':list(move['axis_gltf']),'travel':move['travel_degrees_or_m'],'semantic_parts':parts,'contact_allowance_m':0,'initial_pose':0})
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  states=[]
  for name,move in MOVES.items():
   kind=move['motion_type'];travel=move['travel_degrees_or_m'];original=move.location.copy()
   if kind=='rotation':move.rotation_euler.x=math.radians(travel)
   else:move.location.y+=travel
   bpy.context.view_layer.update();sb,st=bounds();suffix='_folded'if ident.endswith('003')else('_aimed'if kind=='rotation'else'_service_open');export(ident,suffix)
   states.append({'name':name+' terminal','export':f'exports/{ident}{suffix}.glb','root':name,'kind':kind,'travel':travel,'bounds_source':sb,'glb_sha256':sha(BASE/'exports'/f'{ident}{suffix}.glb')})
   move.rotation_euler.x=0;move.location=original;bpy.context.view_layer.update()
  lo,hi=bb['min_m'],bb['max_m'];glo=[lo[0],lo[2],-hi[1]];ghi=[hi[0],hi[2],-lo[1]]
  groups=sorted({(o.parent.name,o['material_role'])for o in PARTS});roles=sorted({o['material_role']for o in PARTS})
  rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_auditorium_use.py','source_frame':'metres Blender XYZ Z-up front -Y','exchange_frame':'metres native GLB Y-up source(x,y,z)->(x,z,-y)','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'floor between supported soles, not a physical centre support'},'bounds_blender_z_up':bb,'bounds_gltf_y_up':{'min_m':glo,'max_m':ghi,'dimensions_m':[b-a for a,b in zip(glo,ghi)]},'dimensions_blender_xyz_m':bb['dimensions_m'],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':roles,'export_mesh_groups':len(groups),'export_group_ownership':groups,'physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'motion_records':motion_records,'state_derivatives':states,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Original host absent; no placement, row assignment, stage connection or capacity addition','All six-species body/support/reach, room/route/crowd, collision adoption and target-PC performance acceptance pending','No runtime mechanical, cue/control, electrical, lighting/acoustic, stability/load or stage certification']}
  if ident.endswith('003'):assert tri<=900 and len(roles)<=4 and len(groups)<=6,(tri,roles,groups)
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
  for shape in COLL:shape.update(allowed_inflation_m=0,allowed_omission_m=0,approximation='Authored convex visual solids without bevel modifiers; exact static/owned convex profile proposal. Rotating transforms required for moving groups.')
  coll[ident]={'source_frame':'metres Blender Z-up closed asset source frame; owned shapes transform about declared actual pivot','exchange_frame':'metres native GLB Y-up closed asset native frame','status':'Unimplemented component collision proposals','shapes':COLL,'preserve_voids':VOIDS,'motion_records':motion_records,'omitted_semantic_parts':[],'limits':'Separate purpose solids preserve actual pan fold, underseat, work and cable/service spaces; no enclosing asset hull; finite triangulated visual geometry only'};api[ident]=MARKERS
 (BASE/'manifest.json').write_text(json.dumps({'family':'auditorium_use','revision':'auditorium-use-01','unique_designs':2,'assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n')
 deps=[Path(__file__),BASE/'source/draw_markings.py',BASE/'source/rehearsal_notes.png']+[CAT/'standards'/f'{x}.py'for x in('materials','auditorium_materials','staff_materials')]
 for p,key in[(CAT/'materials/material_manifest.json','base_color_file'),(CAT/'materials/auditorium/manifest.json','file'),(CAT/'materials/staff/manifest.json','file')]:deps.append(p);deps.extend(p.parent/v[key]for v in json.loads(p.read_text())['materials'].values())
 (BASE/'dependency_manifest.json').write_text(json.dumps({'schema':'auditorium_use_source_only_inputs_v1','inputs':[{'path_from_catalogue_root':str(p.relative_to(CAT)),'sha256':sha(p)}for p in deps],'count':len(deps),'closure_note':'Includes every loaded common, auditorium and staff texture, even unused roles; graphic is regenerated from original glyph source. No source generator reads prior outputs or QA inputs.'},indent=2)+'\n')
 print('AUDITORIUM_USE_BUILT',[(r['catalogue_id'],r['evaluated_triangles'],r['export_mesh_groups'],r['dimensions_blender_xyz_m'])for r in rows])
if __name__=='__main__':main()
