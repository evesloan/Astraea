"""Original AST-RTL-003/004: editable public-retail wrapping station and reusable case.
All geometry/art authored here; no previous outputs are read. Blender 4.3.2.
"""
import bpy,bmesh,math,json,hashlib,importlib.util,runpy
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for sub in ('source','exports','qa'):(BASE/sub).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [float(p[0]),float(p[2]),float(-p[1])]
runpy.run_path(str(CAT/'materials/retail/draw_textures.py'),run_name='__main__')
spec=importlib.util.spec_from_file_location('retail_palette',CAT/'standards/retail_materials.py');palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
ALIASES={'pale':'ivory_enamel','wood':'warm_walnut','dark':'dark_rubber','metal':'champagne_metal','clay':'retail_terracotta_enamel','stone':'warm_stone'}
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,VOIDS,COLL,GROUPS,SUPPORTS
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];MARKERS=[];JOINS=[];VOIDS=[];COLL=[];SUPPORTS=[];GROUPS={}
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident;ROOT['scope']='Proposed component geometry only; not actual shop ownership, species fit, payment or load acceptance'
 for group in ('fixed','lid','carrier'):
  o=bpy.data.objects.new(ident+'__ownership_'+group,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o['motion_group']=group;o['pivot_source_m']=[0.,0.,0.];o['pivot_gltf_m']=[0.,0.,0.];o['attachment']='fixed'if group=='fixed'else'detachable manual handling; no retained joint or automatic motion';GROUPS[group]=o
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.context.scene['catalogue_id']=ident

def uv(me,role):
 layer=me.uv_layers.active or me.uv_layers.new(name='metric_material_uv');layer.active_render=True;sx,sy=M[role]['meters_per_tile_uv']
 for f in me.polygons:
  ax=max(range(3),key=lambda i:abs(f.normal[i]));ij=[i for i in range(3)if i!=ax]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(p[ij[0]]/sx,p[ij[1]]/sy)

def mesh(name,verts,faces,role='pale',bevel=0,body=True,group='fixed'):
 role=ALIASES.get(role,role);verts=[list(v)for v in verts];me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=GROUPS[group];ob['material_role']=role;ob['body_candidate_retained']=body;ob['motion_group']=group;me.materials.append(M[role]);uv(me,role)
 if bevel:
  m=ob.modifiers.new('Small editable edge easing','BEVEL');m.width=bevel;m.segments=1;m.limit_method='ANGLE';m.angle_limit=math.radians(35)
  m=ob.modifiers.new('Editable weighted face normals','WEIGHTED_NORMAL');m.keep_sharp=True
 PARTS.append(ob);COLL.append({'name':name,'kind':'convex_hull_points','points_source_m':verts,'points_gltf_m':[glb(v)for v in verts],'source_part':name,'motion_group':group,'body_candidate_retained':body,'edge_easing_max_m':bevel,'scope':'Convex semantic component before small edge easing; no hull enclosing an assembled opening'})
 return ob
FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(n,lo,hi,r='pale',b=0,body=True,g='fixed'):
 return mesh(n,[(lo[0]if i==0 else hi[0],lo[1]if j==0 else hi[1],lo[2]if k==0 else hi[2])for i,j,k in[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]],FACES,r,b,body,g)
def prism(n,poly,z0,z1,r='pale',b=0,body=True,g='fixed'):
 N=len(poly);return mesh(n,[(x,y,z)for z in(z0,z1)for x,y in poly],[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)],r,b,body,g)
def clipped(x0,x1,y0,y1,c=.025):return[(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1-c),(x1-c,y1),(x0+c,y1),(x0,y1-c),(x0,y0+c)]
def ring(n,outer,inner,z0,z1,r,g='fixed',body=True):
 out=[]
 for i in range(len(outer)):
  j=(i+1)%len(outer);poly=[outer[i],outer[j],inner[j],inner[i]];out.append(prism(n+'_'+str(i),poly,z0,z1,r,0,body,g))
 return out

def marker(n,p,kind,part=None,normal=None,note='',g='fixed'):
 o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.parent=GROUPS[g];o.location=p;o.empty_display_size=.012;o['marker_kind']=kind;o['physical_part']=part or '';o['source_position_m']=p;o['gltf_position_m']=glb(p);row={'name':n,'kind':kind,'source_m':list(p),'gltf_m':glb(p),'physical_part':part,'motion_group':g,'description':note}
 if normal:row.update(normal_source=list(normal),normal_gltf=glb(normal));o['normal_source']=normal;o['normal_gltf']=glb(normal)
 MARKERS.append(row)
def join(n,a,b,p,kind='opposing_boundary_contact'):JOINS.append({'name':n,'parts':[a,b],'probe_source_m':list(p),'probe_gltf_m':glb(p),'kind':kind})
def void(n,lo,hi,note,states=None,g='fixed'):
 if states is None:states=['closed','open_lid_parked','handling']if ROOT.name=='AST-RTL-004'else['closed']
 VOIDS.append({'name':n,'motion_group':g,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':note,'valid_states':states})
def support(n,poly,z,part,note=''):
 SUPPORTS.append({'name':n,'polygon_source_m':[[x,y,z]for x,y in poly],'polygon_gltf_m':[glb([x,y,z])for x,y in poly],'normal_source':[0,0,1],'normal_gltf':[0,1,0],'physical_part':part,'motion_group':next(o['motion_group']for o in PARTS if o.name==part),'description':note})
def glyphbar(n,a,b,y,width=.009):
 # Original parcel pictogram is encoded vector geometry; no fonts, graphic assets or licensed marks.
 d=Vector((b[0]-a[0],b[1]-a[1]));q=Vector((-d.y,d.x)).normalized()*width/2
 verts=[(p[0],yy,p[1])for yy in(y-.003,y)for p in[Vector(a)+q,Vector(b)+q,Vector(b)-q,Vector(a)-q]]
 return mesh(n,verts,FACES,'metal',0,False)

def bench():
 # Asymmetric guest-rest pylon is separate from the lower broad staff wrapping wing.
 pl=prism('parcel_pylon_floor_plinth',clipped(-.89,-.23,-.405,.395,.055),0,.055,'dark')
 for name,x0,x1 in [('outer',-.875,-.790),('inner',-.315,-.230)]:
  ob=box('parcel_pylon_'+name+'_return',[x0,-.37,.055],[x1,.37,1.025],'pale',.002)
  join(name+'_return_on_plinth',ob.name,pl.name,[(x0+x1)/2,0,.055])
  marker(name.upper()+'_FLOOR',[(x0+x1)/2,0,0],'physical_floor_contact',pl.name,[0,0,-1])
 front=box('parcel_pylon_recessed_terracotta_front',[-.790,-.37,.055],[-.315,-.235,1.025],'clay')
 join('front_on_plinth',front.name,pl.name,[-.55,-.30,.055])
 top=prism('guest_parcel_rest',clipped(-.90,-.20,-.45,.40,.065),1.025,1.075,'wood',.002)
 for name,x in [('outer',-.83),('inner',-.27)]:join(name+'_return_to_parcel_rest','parcel_pylon_'+name+'_return',top.name,[x,0,1.025])
 for z,tag in[(.175,'lower'),(.555,'upper')]:
  sh=box('paper_stock_'+tag+'_shelf',[-.790,-.235,z-.027],[-.315,.345,z],'wood')
  for name,x in [('outer',-.790),('inner',-.315)]:join(tag+'_'+name+'_shelf_return',sh.name,'parcel_pylon_'+name+'_return',[x,.10,z-.014])
  support('PAPER_'+tag.upper()+'_PATCH',clipped(-.765,-.34,-.21,.31,.01),z,sh.name,'Empty supported sheet/stock access; no inventory or paper material specification')
 # Quiet raised side cheek gives a purposeful rear-paper tuck and public silhouette.
 cheek=box('parcel_rest_outer_raised_cheek',[-.875,-.33,1.075],[-.825,.335,1.15],'pale',.002)
 join('cheek_on_rest',cheek.name,top.name,[-.85,0,1.075])
 # Wrapping work wing: broad empty plane at 0.95m with rear staff approach.
 wing=prism('clear_wrapping_worktop',clipped(-.23,.90,-.43,.43,.045),.915,.95,'wood',.002)
 join('wing_into_inner_return',wing.name,'parcel_pylon_inner_return',[-.23,0,.933])
 shoe=prism('work_wing_floor_shoe',clipped(.76,.885,-.32,.35,.025),0,.045,'dark')
 fin=box('work_wing_outer_support_fin',[.775,-.30,.045],[.86,.33,.915],'pale',.002)
 join('fin_on_floor_shoe',fin.name,shoe.name,[.815,0,.045]);join('fin_under_worktop',fin.name,wing.name,[.815,0,.915]);marker('WING_FLOOR',[.815,0,0],'physical_floor_contact',shoe.name,[0,0,-1])
 sill=box('staff_open_stock_sill',[-.23,-.285,.29],[.775,.33,.322],'pale')
 join('sill_into_pylon',sill.name,'parcel_pylon_inner_return',[-.23,0,.306]);join('sill_into_wing_fin',sill.name,fin.name,[.775,0,.306])
 apron=box('wrapping_front_recessed_return',[-.23,-.375,.735],[.775,-.325,.915],'clay')
 join('apron_into_worktop',apron.name,wing.name,[.2,-.35,.915])
 # Fixed open paper cradles belong under worktop, keep wrapping and guest patches clear.
 divider=box('open_stock_short_divider',[.20,-.235,.322],[.222,.28,.59],'wood')
 join('stock_divider_on_sill',divider.name,sill.name,[.211,0,.322])
 support('STAFF_STOCK_PATCH',clipped(.26,.735,-.25,.29,.018),.322,sill.name,'Empty open stock compartment; no drawer or mechanism')
 # Recessed inactive service face on public pylon; small paired marks on staff edge are not a payment device.
 panel=box('original_parcel_service_face',[-.716,-.378,.60],[-.389,-.37,.926],'dark',.002,False)
 join('service_face_on_pylon',panel.name,front.name,[-.55,-.37,.76])
 q=[(-.645,.705),(-.460,.705),(-.460,.850),(-.645,.850),(-.645,.705)]
 for i in range(4):glyphbar('original_parcel_outline_'+str(i),q[i],q[i+1],-.378)
 glyphbar('original_parcel_fold_left',(-.645,.85),(-.5525,.80),-.378);glyphbar('original_parcel_fold_right',(-.46,.85),(-.5525,.80),-.378);glyphbar('original_parcel_wrap_seam',(-.5525,.80),(-.5525,.706),-.378)
 control=box('inactive_staff_control_face',[-.68,.355,.818],[-.42,.371,.965],'dark',.002,False)
 join('inactive_face_to_shelf_return_left',control.name,'paper_stock_upper_shelf',[-.55,.355,.86],'fixed bracket documented below')
 # Real back plate supports the quiet control face, rather than floating signage.
 bracket=box('inactive_face_fixed_backing',[-.69,.34,.795],[-.41,.355,1.025],'pale')
 join('control_backing_into_parcel_rest',bracket.name,top.name,[-.55,.348,1.025]);join('inactive_face_backing',control.name,bracket.name,[-.55,.355,.87])
 for i,x in enumerate([-.595,-.505]):
  btn=box('inactive_staff_recess_mark_'+str(i),[x-.023,.371,.867],[x+.023,.374,.891],'clay',0,False);join('inactive_mark_'+str(i),btn.name,control.name,[x,.371,.879])
 marker('PARCEL_REST',[-.54,-.02,1.075],'physical_guest_parcel_surface',top.name,[0,0,1])
 marker('WRAPPING_SURFACE',[.28,0,.95],'physical_staff_work_surface',wing.name,[0,0,1])
 marker('SERVICE_IDENTITY_FACE',[-.55,-.378,.76],'physical_inactive_identity_surface',panel.name,[0,-1,0],'Original parcel pictogram; no price, payment, reader, screen interaction or personal data')
 marker('STAFF_APPROACH',[.28,.90,0],'nonphysical_approach_proposal',note='Room/body/reach/route and real host slots unverified')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',note='Empty centre floor datum, not physical support')
 support('GUEST_PARCEL_PATCH',clipped(-.805,-.25,-.38,.28,.025),1.075,top.name,'Bounded useful rest for a small parcel; left raised cheek excluded')
 support('CLEAR_WRAPPING_PATCH',clipped(-.18,.74,-.37,.37,.025),.95,wing.name,'Clear staff wrapping work area 0.92x0.74m inside perimeter easing')
 void('guest_parcel_air',[-.79,-.36,1.079],[-.27,.25,1.43],'Empty volume over actual guest rest')
 void('staff_wrapping_air',[-.17,-.35,.954],[.73,.35,1.30],'Clear staff work above actual top')
 void('upper_paper_stock_access',[-.75,-.19,.565],[-.35,.325,.79],'Rear-open stock cavity above actual shelf, below inactive face backing')
 void('lower_paper_stock_access',[-.75,-.19,.185],[-.35,.325,.515],'Rear-open lower sheet-stock cavity')
 void('staff_stock_access',[.25,-.23,.332],[.73,.55,.70],'Rear-open shelf compartment; extends through actual rear retrieval face')
 void('staff_toe_gap',[-.16,-.20,.025],[.71,.42,.28],'Open beneath staff wing, not actor-body acceptance')
 # Remove deliberately nonphysical documentary link; actual support is the fixed backing.
 JOINS[:]=[j for j in JOINS if j['name']!='inactive_face_to_shelf_return_left']
 return 'Parcel wrapping and service workbench',{'articulation':'None; static open stock access avoids unnecessary drawer motion','front_source':'-Y guest rest and original parcel identity','staff_source':'+Y open stock and clear wrapping plane','inactive_control':'Abstract two-mark face only; no payment flow, prices, card reader, runtime screen, transaction or personal-data behavior','proposed_access':{'guest_source_m':{'min':[-.95,-1.05,0],'max':[-.15,-.46,1.8]},'staff_source_m':{'min':[-.88,.44,0],'max':[.90,1.20,1.8]}},'original_art':'Seven encoded vector bars form parcel-fold pictogram; original geometry, no font or external artwork'},{}

def container():
 outer=clipped(-.23,.23,-.165,.165,.034);inner=clipped(-.214,.214,-.149,.149,.026)
 footpoly=clipped(-.205,.205,-.14,.14,.024)
 foot=prism('case_grounded_foot',footpoly,0,.012,'dark')
 bottom=prism('case_load_floor',outer,.012,.026,'clay')
 join('load_floor_on_foot',bottom.name,foot.name,[0,0,.012])
 walls=ring('case_faceted_shell',outer,inner,.026,.25,'clay')
 for i,ob in enumerate(walls):
  p=[(outer[i][0]+inner[i][0]+outer[(i+1)%8][0]+inner[(i+1)%8][0])/4,(outer[i][1]+inner[i][1]+outer[(i+1)%8][1]+inner[(i+1)%8][1])/4,.026];join('shell_'+str(i)+'_floor',ob.name,bottom.name,p)
 # Eight ribs have real rear contact to the long flat shell faces and stop below its closure seat.
 for side,y0,y1 in [('front',-.171,-.165),('rear',.165,.171)]:
  for i,x in enumerate([-.15,-.05,.05,.15]):
   rib=box('case_'+side+'_vertical_rib_'+str(i),[x-.007,y0,.045],[x+.007,y1,.219],'pale',.001,False)
   join(side+'_rib_'+str(i)+'_on_shell',rib.name,'case_faceted_shell_'+('0'if side=='front'else'4'),[x,-.165 if side=='front'else.165,.13])
 # Tray bears on two real narrow side shelves at 0.119m, with entire boundary inside the eight-sided shell.
 for side,x0,x1 in [('left',-.214,-.174),('right',.174,.214)]:
  rail=box('carrier_'+side+'_bearing',[x0,-.118,.107],[x1,.118,.119],'metal')
  join(side+'_bearing_to_shell',rail.name,'case_faceted_shell_'+('6'if side=='left'else'2'),[x0 if side=='left'else x1,0,.112])
 traypoly=clipped(-.190,.190,-.124,.124,.020);trayinner=clipped(-.178,.178,-.112,.112,.013)
 tray=prism('nested_carrier_floor',traypoly,.119,.131,'wood',0,True,'carrier')
 for side,x in [('left',-.184),('right',.184)]:join(side+'_carrier_bearing_seat',tray.name,'carrier_'+side+'_bearing',[x,0,.119])
 tw=ring('nested_carrier_wall',traypoly,trayinner,.131,.192,'wood','carrier')
 for i,ob in enumerate(tw):
  j=(i+1)%8;join('carrier_wall_'+str(i)+'_floor',ob.name,tray.name,[(traypoly[i][0]+traypoly[j][0]+trayinner[i][0]+trayinner[j][0])/4,(traypoly[i][1]+traypoly[j][1]+trayinner[i][1]+trayinner[j][1])/4,.131])
 divider=box('nested_carrier_central_partition',[-.006,-.112,.131],[.006,.112,.178],'wood',0,True,'carrier');join('carrier_partition_floor',divider.name,tray.name,[0,0,.131])
 # Raised carrier bridges leave useful finger openings. They are below closed lid seat.
 for side,y in [('front',-.118),('rear',.118)]:
  for hand,x in [('left',-.062),('right',.062)]:
   st=box('carrier_'+side+'_'+hand+'_grip_standoff',[x-.008,y-.006,.192],[x+.008,y+.006,.222],'metal',0,True,'carrier');join(side+'_'+hand+'_grip_to_tray',st.name,'nested_carrier_wall_'+('0'if side=='front'else'4'),[x,y,.192])
  grip=box('carrier_'+side+'_lift_grip',[-.070,y-.009,.222],[.070,y+.009,.234],'metal',.001,True,'carrier')
  for hand,x in [('left',-.062),('right',.062)]:join(side+'_'+hand+'_grip_to_standoff',grip.name,'carrier_'+side+'_'+hand+'_grip_standoff',[x,y,.222])
  marker('CARRIER_'+side.upper()+'_GRIP',[0,y,.234],'physical_hand_contact',grip.name,[0,0,1],'Manual detached tray handling; fingers/body/forces unverified',g='carrier')
  void('carrier_'+side+'_finger_gap',[-.052,y-.005,.198],[.052,y+.005,.218],'Actual under-bridge opening; full hand fit not claimed',['closed','open_lid_parked','handling'],g='carrier')
 # Lift-off closure: cap rests on shell seat. A recessed locator skirt has 6mm radial clearance.
 lidpoly=clipped(-.234,.234,-.169,.169,.036)
 cap=prism('removable_lid_cap',lidpoly,.25,.272,'pale',.001,True,'lid')
 lo=clipped(-.208,.208,-.143,.143,.028);li=clipped(-.196,.196,-.131,.131,.022)
 loc=ring('lid_recessed_locator',lo,li,.235,.25,'dark','lid')
 for i,ob in enumerate(loc):
  j=(i+1)%8;join('locator_'+str(i)+'_cap',ob.name,cap.name,[(lo[i][0]+lo[j][0]+li[i][0]+li[j][0])/4,(lo[i][1]+lo[j][1]+li[i][1]+li[j][1])/4,.25])
 for i,ob in enumerate(walls):
  j=(i+1)%8;join('closed_lid_seat_'+str(i),cap.name,ob.name,[(outer[i][0]+outer[j][0]+inner[i][0]+inner[j][0])/4,(outer[i][1]+outer[j][1]+inner[i][1]+inner[j][1])/4,.25])
 for side,x in [('left',-.07),('right',.07)]:
  st=box('lid_'+side+'_grip_pillar',[x-.013,-.018,.272],[x+.013,.018,.298],'metal',0,True,'lid');join(side+'_lid_grip_pillar_cap',st.name,cap.name,[x,0,.272])
 handle=box('lid_broad_lift_grip',[-.083,-.018,.298],[.083,.018,.316],'wood',.002,True,'lid')
 for side,x in [('left',-.07),('right',.07)]:join(side+'_lid_grip_pillar_bridge',handle.name,'lid_'+side+'_grip_pillar',[x,0,.298])
 marker('CASE_FLOOR',[0,0,0],'physical_support_surface',foot.name,[0,0,-1],'Full chamfered foot contact patch; no load rating')
 marker('CASE_LOAD_FLOOR',[0,0,.026],'physical_load_surface',bottom.name,[0,0,1])
 marker('LID_LIFT_GRIP',[0,0,.316],'physical_hand_contact',handle.name,[0,0,1],'Lid is detached after axial lift; no hinge/latch',g='lid')
 marker('CARRIER_LEFT_LOAD',[-.08,0,.131],'physical_load_surface',tray.name,[0,0,1],g='carrier')
 marker('CARRIER_RIGHT_LOAD',[.08,0,.131],'physical_load_surface',tray.name,[0,0,1],g='carrier')
 marker('CLOSED_LID_SEAT',[0,-.157,.25],'physical_closed_seating_contact','case_faceted_shell_0',[0,0,1])
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',note='Coincides with actual foot support')
 support('CASE_FLOOR_PATCH',footpoly,0,foot.name,'Down-facing source surface; polygon winding/normal corrected in support record below')
 SUPPORTS[-1]['normal_source']=[0,0,-1];SUPPORTS[-1]['normal_gltf']=[0,-1,0];SUPPORTS[-1]['polygon_source_m'].reverse();SUPPORTS[-1]['polygon_gltf_m'].reverse()
 support('CARRIER_LEFT_PATCH',clipped(-.17,-.017,-.102,.102,.008),.131,tray.name,'Left empty small-goods compartment')
 support('CARRIER_RIGHT_PATCH',clipped(.017,.17,-.102,.102,.008),.131,tray.name,'Right empty small-goods compartment')
 void('case_lower_goods_space',[-.163,-.118,.032],[.163,.118,.101],'True lower cavity beneath carrier, not filled by body hull')
 void('carrier_left_goods_space',[-.167,-.098,.136],[-.014,.098,.176],'Empty left tray compartment',['closed','open_lid_parked','handling'],g='carrier')
 void('carrier_right_goods_space',[.014,-.098,.136],[.167,.098,.176],'Empty right tray compartment',['closed','open_lid_parked','handling'],g='carrier')
 void('lid_finger_gap',[-.052,-.015,.277],[.052,.015,.295],'Actual under-grip opening, not hand fit',g='lid')
 void('open_case_retrieval',[-.17,-.10,.241],[.17,.10,.48],'Opening cleared by detached lid',['open_lid_parked'])
 states={'closed':{'fixed':[0,0,0],'lid':[0,0,0],'carrier':[0,0,0]},'open_lid_parked':{'fixed':[0,0,0],'lid':[.58,0,-.235],'carrier':[0,0,0]},'handling':{'fixed':[0,0,0],'lid':[.58,0,-.235],'carrier':[0,0,.30]}}
 details={'design_identity':'One reusable faceted small-goods case with detachable lid and nested divided carrier; repeated instances/states are not additional designs','closure':'Lift-off cap seated on shell rim, locator skirt clearance. No operating latch, hinge, lock or sealing claim','manual_path':{'lid':{'frame':'source XYZ m','waypoints':[[0,0,0],[0,0,.09],[.58,0,.09],[.58,0,-.235]],'interpretation':'Manual detached handling. Parked locator bottom reaches inspection support datum Z0; not a retained mechanism or solved dynamics'},'carrier':{'precondition':'lid parked','waypoints':[[0,0,0],[0,0,.30]],'interpretation':'Detached, externally held state; deliberately unsupported in handling pose'}},'profile':{'outer_polygon_source_xy_m':outer,'inner_polygon_source_xy_m':inner,'carrier_outer_polygon_source_xy_m':traypoly,'lid_locator_outer_polygon_source_xy_m':lo,'shell_inner_height_m':[.026,.25],'whole_profile_rule':'All carrier/locator projected boundary points must lie within every halfspace of full eight-sided inner profile; checked independently, not only AABB'},'proposed_access':{'manual_handling_source_m':{'min':[-.30,-.30,0],'max':[.85,.30,.62]}},'contents':'Empty. No biological/food compatibility, quantity, contents, load rating or inventory implied','states':states}
 return 'Reusable small-goods case with nested carrier',details,states

def evaluated(ob):
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));uv(me,ob['material_role']);return me

def export(ident,suffix='',poses=None):
 poses=poses or {'fixed':[0,0,0],'lid':[0,0,0],'carrier':[0,0,0]}
 for g,p in poses.items():GROUPS[g].location=p
 bpy.context.view_layer.update();groups={};out=[]
 for ob in PARTS:
  me=evaluated(ob);e=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(e);e.matrix_world=ob.matrix_world.copy();key=(ob['motion_group'],ob['material_role']);groups.setdefault(key,[]).append(e)
 for (g,role),obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+g+'__'+role;world=ob.matrix_world.copy();ob.parent=GROUPS[g];ob.matrix_world=world;ob['motion_group']=g;ob['material_group']=role;out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for ob in out+list(GROUPS.values()):ob.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/(ident+suffix+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)
 for ob in GROUPS.values():ob.location=(0,0,0)
 bpy.context.view_layer.update();return len(groups)

def main():
 bpy.context.preferences.filepaths.save_version=0;assets=[];api={};collision={}
 for ident,fn in [('AST-RTL-003',bench),('AST-RTL-004',container)]:
  reset(ident);title,details,states=fn();bpy.context.view_layer.update();verts=[];tri=0;parts=[]
  for ob in PARTS:
   me=evaluated(ob);me.calc_loop_triangles();tri+=len(me.loop_triangles);verts.extend(ob.matrix_world@v.co for v in me.vertices);parts.append({'name':ob.name,'material_role':ob['material_role'],'motion_group':ob['motion_group'],'body_candidate_retained':ob['body_candidate_retained'],'evaluated_triangles':len(me.loop_triangles),'editable_modifiers':[m.type for m in ob.modifiers]});bpy.data.meshes.remove(me)
  lo=[min(v[i]for v in verts)for i in range(3)];hi=[max(v[i]for v in verts)for i in range(3)]
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/(ident+'.blend')),compress=True);count=export(ident);derivatives=[]
  for name,pose in states.items():
   if name=='closed':continue
   export(ident,'__'+name,pose);p=BASE/'exports'/(ident+'__'+name+'.glb');derivatives.append({'state':name,'export':str(p.relative_to(BASE)),'glb_sha256':sha(p),'ownership_translations_source_m':pose,'ownership_translations_gltf_m':{g:glb(v)for g,v in pose.items()},'design_count':0,'support':'Lid locator parked at Z0; carrier remains seated'if name=='open_lid_parked'else'Lid parked at Z0; carrier is explicitly detached and externally held, no physical support claim'})
  row={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'design_count':1,'source':'source/'+ident+'.blend','export':'exports/'+ident+'.glb','generator':'source/build_retail_work.py','units':'metres','source_frame':'Blender XYZ Z-up front -Y','exchange_frame':'Native GLB (x,z,-y), actual hierarchy authoritative','pivot_source_m':[0,0,0],'pivot_gltf_m':[0,0,0],'bounds_blender_z_up':{'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i]for i in range(3)]},'bounds_gltf_y_up':{'min_m':[lo[0],lo[2],-hi[1]],'max_m':[hi[0],hi[2],-lo[1]]},'dimensions_blender_xyz_m':[hi[i]-lo[i]for i in range(3)],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'parts':parts,'runtime_mesh_groups':count,'runtime_consolidation':'Evaluated copies grouped by common material role and actual fixed/lid/carrier ownership; no per-rib or glyph node inflation','material_roles':sorted(set(p['material_role']for p in parts)),'physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'support_patches':SUPPORTS,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','state_derivatives':derivatives,'uv_policy':{'editable_source':'Metric projection on raw semantic faces before edge modifiers; modifier-created UVs remain interpolated in the editable source','evaluated_export':'Reproject each evaluated face using its dominant absolute normal axis; omit that axis and divide the other two source-local coordinates by unchanged material meters_per_tile_uv; then group by ownership/material','export_reprojects_after_modifiers':True,'consequence':'Bevel-face native UVs can differ from direct modifier-interpolated source UVs. Export normals and geometry are evaluated source values; independent expected-export corner comparison uses this declared projection.'},'used_textures_packed':True,'source_sha256':sha(BASE/'source'/(ident+'.blend')),'glb_sha256':sha(BASE/'exports'/(ident+'.glb')),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Proposed source component only; real shop ownership, finished polygon, door/pockets/support and host activity slots remain unknown','No payment, inventory, load, closure seal, food/biological, species/body/reach or runtime-performance acceptance','Detailed and optional body shapes are proposals; omission distances measured separately from material thickness','Inspection states do not implement a game mechanism or retained hinge']}
  assets.append(row);write(BASE/(ident+'.manifest.json'),row);api[ident]={'markers':MARKERS,'joins':JOINS,'voids':VOIDS,'support_patches':SUPPORTS,'proposed_access':details['proposed_access'],'state_transforms_source_m':states};collision[ident]={'source_frame':'Blender Z-up metres','native_frame':'GLB Y-up metres','precise_reference':COLL,'optional_body_candidate':{'derivation':'Literal outset-authored subset of convex semantic structural parts','retained_shape_names':[x['name']for x in COLL if x['body_candidate_retained']],'omitted_shape_names':[x['name']for x in COLL if not x['body_candidate_retained']],'new_enclosing_hulls':False,'fine_detail_distance':'QA measures separately; not material thickness','engine_adoption':'Pending'},'preserved_voids':VOIDS,'state_transforms_source_m':states}
 write(BASE/'manifest.json',{'batch':'18','family':'retail_work','unique_asset_count':2,'assets':assets});write(BASE/'marker_api.json',api);write(BASE/'collision_proposals.json',collision)
 cm=json.loads((CAT/'materials/material_manifest.json').read_text());rm=json.loads((CAT/'materials/retail/manifest.json').read_text());inputs=[Path(__file__),CAT/'standards/materials.py',CAT/'standards/retail_materials.py',CAT/'materials/material_manifest.json',CAT/'materials/retail/draw_textures.py']+[CAT/'materials'/r['base_color_file']for r in cm['materials'].values()]
 write(BASE/'dependency_manifest.json',{'source_only_inputs':[{'path':str(p.relative_to(CAT)),'sha256':sha(p)}for p in inputs],'all_helper_loaded_roles_included':True,'new_enamel_regenerated_from_original_source':True,'generated_materials':['materials/retail/manifest.json','materials/retail/retail_terracotta_enamel.png'],'original_art':'Encoded original vector parcel glyph in builder, no external font/art input','excluded_inputs':'No existing .blend, GLB, QA, render or generated interface file is an input seed'})
 print('RETAIL_WORK_BUILD_OK',[(a['catalogue_id'],a['evaluated_triangles'],a['runtime_mesh_groups'])for a in assets])
if __name__=='__main__':main()
