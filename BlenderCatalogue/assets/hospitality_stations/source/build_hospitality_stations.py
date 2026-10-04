"""Original script-assisted editable station pair. Blender4.3.2; source metres/Z-up.
No food/fluid/device simulation. Frozen shared material sources are read only.
"""
import bpy,bmesh,math,json,hashlib,importlib.util,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
U=module('utility_ports',CAT/'standards/utility_ports.py')
M=module('guest_materials',CAT/'standards/materials.py').materials();M.update(module('staff_materials',CAT/'standards/staff_materials.py').materials())
R={'ivory':'ivory_enamel','wood':'warm_walnut','stone':'warm_stone','metal':'champagne_metal','dark':'dark_rubber','wash':'staff_zinc','label':'hospitality_station_graphics'}
mat=bpy.data.materials.new('ASTRAEA_hospitality_station_graphics');mat.use_nodes=True;mat['astraea_material_role']='hospitality_station_graphics';mat['meters_per_tile_uv']=[1,1];ns=mat.node_tree.nodes;ns.clear();bs=ns.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.72;tex=ns.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BASE/'textures/station_graphics.png'));tex.image.pack();out=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs[0],out.inputs[0]);M['hospitality_station_graphics']=mat
OBJECTS=[];MARKERS=[];GROUPS={};CONTACTS=[];CLEAR=[];COL=[];FEATURES=[]
def C(p):return [float(p[0]),float(p[2]),float(-p[1])]
def reset():
 global OBJECTS,MARKERS,GROUPS,CONTACTS,CLEAR,COL,FEATURES
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);OBJECTS=[];MARKERS=[];GROUPS={};CONTACTS=[];CLEAR=[];COL=[];FEATURES=[]
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def reg(ob,role,group='static'):
 ob['material_role']=R.get(role,role);ob['export_group']=group;OBJECTS.append(ob);return ob

def mesh(name,v,f,role='ivory',bevel=0,group='static'):
 ob=U.mesh(name,v,f,M[R.get(role,role)]);reg(ob,role,group)
 if bevel:
  mod=ob.modifiers.new('Editable edge radius','BEVEL');mod.width=bevel;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=.55
  mod=ob.modifiers.new('Editable weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return ob

def box(name,c,d,role='ivory',bevel=.003,group='static'):
 x,y,z=c;a,b,e=[q/2 for q in d]
 return mesh(name,[(x+i,y+j,z+k) for i,j,k in[(-a,-b,-e),(a,-b,-e),(a,b,-e),(-a,b,-e),(-a,-b,e),(a,-b,e),(a,b,e),(-a,b,e)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,group)

def profile(name,points,a,b,axis='X',role='ivory',bevel=.002,group='static'):
 v=[]
 for w in(a,b):v.extend((w,u,z) if axis=='X' else(u,w,z) for u,z in points)
 n=len(points);return mesh(name,v,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],role,bevel,group)

def cyl(name,a,b,r,role='metal',n=16,group='static'):return reg(U.solid_cylinder(name,a,b,r,M[R[role]],n),role,group)
def ann(name,p,axis,stations,role='metal',n=24,group='static'):return reg(U.annular(name,p,axis,stations,M[R[role]],n),role,group)
def slab(name,c,w,d,r,th,role='stone',group='static'):
 x,y,z=c;pts=[]
 for cx,cy,start in[(x+w/2-r,y+d/2-r,0),(x-w/2+r,y+d/2-r,90),(x-w/2+r,y-d/2+r,180),(x+w/2-r,y-d/2+r,270)]:
  for j in range(5):
   a=math.radians(start+j*90/4);pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
 n=len(pts);v=[(px,py,z+dz) for dz in(-th/2,th/2) for px,py in pts];return mesh(name,v,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],role,.001,group)

def marker(name,p,kind,d=None,group=None):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.location=p;ob.empty_display_type='ARROWS';ob.empty_display_size=.03
 ob['export_group']=group or 'static';ob['kind']=kind;ob['position_blender_source_m']=list(p);ob['position_gltf_yup_m']=C(p)
 if d:ob['direction_blender_source']=list(d);ob['direction_gltf_yup']=C(d)
 MARKERS.append(ob);return ob

def motion(name,p,d,travel):
 ob=marker(name,p,'proposed_linear_removal_root',d);ob['travel_m']=travel;ob['translation_axis_blender_source']=list(d);ob['translation_axis_gltf_yup']=C(d);ob['status']='Proposal only; no operating motion/controls';GROUPS[name]=ob;return ob

def contact(name,p,size):
 marker(name,p,'physical_support_contact',(0,0,1));CONTACTS.append({'name':name,'source_m':list(p),'gltf_m':C(p),'footprint_xy_m':size})
def bbox(lo,hi):
 pts=[C((x,y,z)) for x in(lo[0],hi[0]) for y in(lo[1],hi[1]) for z in(lo[2],hi[2])];return {'min_m':[min(p[k] for p in pts) for k in range(3)],'max_m':[max(p[k] for p in pts) for k in range(3)]}
def collider(name,lo,hi,group='static'):
 COL.append({'name':name,'type':'box','group':group,'min_source_m':lo,'max_source_m':hi,'bounds_gltf_yup':bbox(lo,hi)})
def clearance(name,lo,hi,purpose):
 CLEAR.append({'name':name,'min_source_m':lo,'max_source_m':hi,'bounds_gltf_yup':bbox(lo,hi),'purpose':purpose,'status':'Geometric proposal; no species/actor/food certification'})

def graphic(name,c,w,h,region,back=False,group='static'):
 x,y,z=c;v=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)]
 if back:v=list(reversed(v))
 ob=mesh(name,v,[(0,1,2,3)],'label',0,group)
 if (ob.data.polygons[0].normal.y>0) != back:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 u0,v0,u1,v1=region;coords=[(u0,1-v1),(u1,1-v1),(u1,1-v0),(u0,1-v0)]
 if back:coords=list(reversed(coords))
 for loop in ob.data.loops:
  co=ob.data.vertices[loop.vertex_index].co
  ob.data.uv_layers[0].data[loop.index].uv=(u0 if co.x<x else u1,1-v1 if co.z<z else 1-v0)
 ob['custom_graphics_uv']=True;return ob

def beverage():
 for x in(-.255,.255):
  for y in(-.157,.157):
   box('counter_contact_pad_'+str((x,y)),(x,y,.010),(.080,.065,.020),'dark',.003);contact('COUNTER_CONTACT_'+str((x,y)),(x,y,0),[.080,.065]);collider('counter_pad_'+str((x,y)),[x-.04,y-.0325,0],[x+.04,y+.0325,.022])
 slab('weighted_rounded_base',(0,0,.032),.65,.45,.045,.040,'ivory')
 collider('station_base',[-.325,-.225,.02],[.325,.225,.052])
 # Profiled cheeks make a rising open arch; enclosed back stops behind cup bay.
 side=[(-.206,.052),(.207,.052),(.207,.497),(.183,.552),(.14,.577),(-.132,.577),(-.186,.550),(-.206,.502)]
 for s in(-1,1):
  profile('shaped_ivory_cheek_'+str(s),side,s*.293-.021,s*.293+.021,'X','ivory',.007)
  profile('warm_wood_inset_cheek_'+str(s),[(-.155,.102),(.186,.102),(.186,.484),(.162,.523),(-.130,.523),(-.171,.498),(-.171,.135)],s*.315-.003,s*.315+.003,'X','wood',.002)
  collider('load_cheek_'+str(s),[s*.293-.023,-.206,.052],[s*.293+.023,.207,.577])
 box('closed_rear_service_body',(0,.142,.295),(.540,.132,.480),'ivory',.013)
 box('recess_washable_rear_face',(0,.068,.252),(.534,.010,.390),'wash',.003)
 collider('rear_enclosure',[-.272,.070,.052],[.272,.211,.535])
 slab('crown_cap',(0,-.010,.552),.60,.396,.042,.046,'ivory')
 box('champagne_control_reveal',(0,-.191,.494),(.520,.014,.114),'metal',.006)
 box('dark_control_fascia',(0,-.201,.494),(.510,.009,.104),'dark',.006)
 collider('overhead_crown',[-.270,-.205,.435],[.270,.195,.577])
 box('ivory_twin_spout_manifold',(0,-.086,.489),(.472,.123,.090),'ivory',.012)
 marker('MANIFOLD_CROWN_JOIN',(0,-.086,.531),'hidden_positive_overlap_join')
 for i,x in enumerate((-.140,.140)):
  graphic('control_label_'+str(i),(x,-.206,.507),.193,.060,[i*.5,0,(i+1)*.5,.5])
  cyl('round_pour_button_'+str(i),(x,-.213,.457),(x,-.205,.457),.013,'metal',20)
  # Short genuine hollow down-facing nozzle; body joins through underside of crown.
  ann('open_hollow_dispense_spout_'+str(i),(x,-.095,.431),(0,0,-1),[(-.018,.008,.019),(0,.008,.019),(.049,.008,.019),(.057,.009,.015)],'wash',24)
  marker('SPOUT_OUTLET_'+str(i),(x,-.095,.374),'physical_open_nozzle_mouth',(0,0,-1))
  marker('CUP_PLACEMENT_'+str(i),(x,-.095,.079),'proposed_cup_pose_centre_not_a_surface',(0,0,1),'DRIP_TRAY')
  ann('cup_base_annular_rest_'+str(i),(x,-.095,.072),(0,0,1),[(0,.052,.058),(.007,.052,.058)],'wash',32,'DRIP_TRAY')
  for j,(dx,dy) in enumerate(((.055,0),(-.055,0),(0,.055),(0,-.055))):marker('CUP_BASE_RING_CONTACT_'+str(i)+'_'+str(j),(x+dx,-.095+dy,.079),'physical_annular_base_contact',(0,0,1),'DRIP_TRAY')
  clearance('cup_receiving_space_'+str(i),[x-.066,-.163,.081],[x+.066,-.025,.362],'Clear cup envelope below real outlet; height .281 m above physical annular base rest')
 # Separate forward-removing open drip tray with support slats, no opaque top cover.
 motion('DRIP_TRAY',(0,-.079,.060),(0,-1,0),.32)
 slab('drip_catch_floor',(0,-.074,.058),.513,.247,.023,.012,'wash','DRIP_TRAY')
 for x in(-.251,.251):box('drip_rim_side_'+str(x),(x,-.074,.067),(.012,.246,.025),'wash',.002,'DRIP_TRAY')
 for y in(-.193,.045):box('drip_rim_end_'+str(y),(0,y,.067),(.501,.010,.025),'wash',.002,'DRIP_TRAY')
 for i in range(13):box('drip_grid_bar_'+str(i),(-.228+i*.038,-.074,.070),(.011,.223,.006),'wash',.001,'DRIP_TRAY')
 box('drip_front_pull',(0,-.207,.061),(.180,.021,.016),'metal',.004,'DRIP_TRAY')
 marker('DRIP_BASE_BEARING',(0,-.074,.052),'physical_drip_floor_to_base_contact',(0,0,1))
 collider('drip_floor',[-.258,-.20,.052],[.258,.052,.065],'DRIP_TRAY')
 for x in(-.251,.251):collider('drip_side_'+str(x),[x-.006,-.20,.063],[x+.006,.052,.080],'DRIP_TRAY')
 # Neutral service panel is restricted to the staff rear.
 box('rear_service_panel_gasket',(0,.213,.305),(.417,.007,.328),'dark',.006)
 box('rear_service_panel',(0,.218,.305),(.405,.010,.316),'wash',.005)
 for x in(-.166,.166):
  for z in(.17,.44):cyl('rear_captive_fastener_'+str((x,z)),(x,.220,z),(x,.227,z),.006,'metal',8)
 clearance('guest_beverage_approach',[-.39,-.92,-.90],[.39,-.41,.76],'Standing guest reservation at proposed counter install offset+0.90 m')
 clearance('above_worktop_guest_reach',[-.33,-.41,.025],[.33,-.205,.58],'Hand reach above host top only; distinct from standing-body reservation')
 clearance('above_worktop_staff_reach',[-.33,.228,.03],[.33,.44,.60],'Rear hand reach above host top only; distinct from standing-body reservation')
 clearance('drip_tray_withdrawal',[-.27,-.53,.048],[.27,-.202,.085],'Forward removable catch tray travel0.32 m; top remains open')
 clearance('staff_rear_service',[-.38,.44,-.90],[.38,1.04,.76],'Proposed rear access, measured from counter component support datum')
 FEATURES.extend([{'name':'double_cup_bay','open_width_m':.54,'outlet_z_m':.374,'cup_base_contact_z_m':.079,'usable_cup_height_m':.281,'pose_centres_are_open':True},{'name':'host_placement','asset':'AST-HSP-001','translation_source_m':[.70,0,.90],'support_plane_source_z_m':0,'host_plane_z_m':.9}])

def dirty_return():
 for x in(-.46,.46):
  for y in(-.30,.30):
   box('floor_pad_'+str((x,y)),(x,y,.025),(.11,.12,.05),'dark',.005);contact('FLOOR_CONTACT_'+str((x,y)),(x,y,0),[.11,.12]);collider('pad_'+str((x,y)),[x-.055,y-.06,0],[x+.055,y+.06,.05])
 slab('inset_rounded_plinth',(0,0,.083),1.03,.704,.075,.09,'ivory')
 collider('plinth',[-.515,-.352,.04],[.515,.352,.128])
 # Continuous curved/raked guest fascia is a solid shallow profile, not an opening decal.
 guest=[(-.383,.128),(-.357,.71),(-.333,.829),(-.310,.847),(-.276,.833),(-.296,.70),(-.322,.128)]
 profile('raked_continuous_walnut_guest_fascia',guest,-.504,.504,'X','wood',.004)
 for i in range(9):
  x=-.438+i*.1095
  profile('broad_walnut_fascia_rib_'+str(i),[(-.390,.16),(-.369,.696),(-.348,.813),(-.333,.813),(-.353,.696),(-.374,.16)],x-.014,x+.014,'X','wood',.002)
 collider('guest_fascia',[-.511,-.39,.12],[.511,-.275,.853])
 # Rounded side shoulders and vertical back corners leave the caddy path open.
 side=[(-.390,.125),(.390,.125),(.390,1.156),(.365,1.195),(.325,1.217),(-.288,1.217),(-.352,1.192),(-.390,1.143)]
 for s in(-1,1):
  profile('load_bearing_ivory_side_'+str(s),side,s*.514-.036,s*.514+.036,'X','ivory',.008)
  collider('side_'+str(s),[s*.514-.037,-.390,.125],[s*.514+.037,.39,1.217])
 box('front_ivory_lower_rail',(0,-.362,.15),(1.025,.075,.07),'ivory',.012)
 box('front_ivory_upper_rail',(0,-.323,.82),(1.02,.092,.065),'ivory',.012)
 box('champagne_reveal',(0,-.371,.858),(1.026,.012,.012),'metal',.003)
 # Front only stone ledge. Rear and centre stay open for loaded caddy removal.
 slab('guest_drop_stone_ledge',(0,-.352,.88),1.10,.096,.029,.040,'stone')
 collider('guest_drop_ledge',[-.55,-.400,.86],[.55,-.304,.9])
 slab('upper_hood_crown',(0,.002,1.188),1.10,.780,.065,.075,'ivory')
 box('hood_front_champagne_reveal',(0,-.381,1.16),(.950,.015,.013),'metal',.003)
 graphic('guest_return_instruction',(0,-.390,1.185),.326,.079,[0,.5,.5,1])
 collider('overhead_hood',[-.55,-.39,1.150],[.55,.39,1.226])
 # Two parallel runners support physical caddy underside and guide extraction +Y.
 for x in(-.421,.421):
  box('caddy_runner_'+str(x),(x,.019,.853),(.042,.650,.042),'wash',.003)
  collider('caddy_runner_'+str(x),[x-.021,-.306,.832],[x+.021,.344,.874])
  box('rail_support_post_'+str(x),(x,.277,.480),(.036,.059,.714),'wash',.003)
  collider('runner_post_'+str(x),[x-.018,.2475,.123],[x+.018,.3065,.837])
 # Lower washable shelf, explicitly open from staff side.
 slab('staff_open_lower_shelf',(0,.023,.283),.924,.614,.025,.035,'wash')
 collider('lower_shelf',[-.462,-.284,.2655],[.462,.33,.3005])
 motion('RECEIVING_CADDY',(0,.015,.880),(0,1,0),.80)
 # Caddy feet bear on the rails; floor top Z.888, side walls leave real clear volume.
 for x in(-.421,.421):box('caddy_rail_contact_'+str(x),(x,.015,.878),(.034,.58,.008),'dark',.001,'RECEIVING_CADDY')
 slab('receiving_caddy_floor',(0,.015,.885),.900,.608,.022,.012,'wash','RECEIVING_CADDY')
 for x in(-.446,.446):box('receiving_caddy_sidewall_'+str(x),(x,.015,.918),(.016,.603,.064),'wash',.003,'RECEIVING_CADDY')
 # Low front roll allows tray sliding. Rear lip has attached hand grip.
 box('caddy_guest_lip',(0,-.282,.903),(.886,.018,.037),'wash',.003,'RECEIVING_CADDY')
 box('caddy_rear_lip',(0,.312,.918),(.886,.018,.064),'wash',.003,'RECEIVING_CADDY')
 for x in(-.128,.128):cyl('caddy_grip_standoff_'+str(x),(x,.318,.922),(x,.377,.922),.010,'metal',12,'RECEIVING_CADDY')
 cyl('caddy_staff_pull_grip',(-.128,.377,.922),(.128,.377,.922),.012,'dark',16,'RECEIVING_CADDY')
 marker('CADDY_STAFF_GRIP',(0,.377,.922),'physical_grip_centreline',(0,1,0),'RECEIVING_CADDY')
 marker('DISH_TRAY_RECEIVING_SURFACE',(0,.015,.891),'physical_receiving_floor',(0,0,1),'RECEIVING_CADDY')
 for x in(-.421,.421):marker('CADDY_RAIL_BEARING_'+str(x),(x,.015,.874),'physical_caddy_runner_contact',(0,0,1))
 collider('caddy_floor',[-.45,-.29,.879],[.45,.319,.891],'RECEIVING_CADDY')
 for x in(-.446,.446):collider('caddy_side_'+str(x),[x-.008,-.2865,.886],[x+.008,.3165,.95],'RECEIVING_CADDY')
 for y in(-.282,.312):collider('caddy_end_'+str(y),[-.443,y-.009,.885],[.443,y+.009,.95 if y>0 else .9215],'RECEIVING_CADDY')
 clearance('guest_tray_approach',[-.57,-1.22,0],[.57,-.41,1.95],'Guest front reservation; .45×.32 m tray enters unobstructed upper opening')
 clearance('staff_caddy_withdrawal',[-.47,.394,.87],[.47,1.20,.965],'Caddy translation +Y0.80 m including rim/grip; no boxed collision over rear opening')
 clearance('staff_service_approach',[-.60,.40,0],[.60,1.45,1.95],'Rear hand/caddy work reservation; staging placement remains untested')
 clearance('tray_receiving_clear_volume',[-.420,-.255,.952],[.420,.280,1.140],'Useful volume above receiving floor excluding low rims; common tray .45×.32 m fits')
 FEATURES.extend([{'name':'receiving_caddy','internal_clear_width_m':.876,'internal_clear_depth_m':.576,'floor_contact_z_m':.891,'common_tray_envelope_m':[.45,.32],'nominal_drop_z_m':.90,'opening_clear_height_above_side_rim_m':.20},{'name':'staff_extraction','node':'RECEIVING_CADDY','direction_source':[0,1,0],'direction_gltf':[0,0,-1],'travel_m':.80}])

def bind_source_groups():
 bpy.context.view_layer.update()
 for ob in OBJECTS+MARKERS:
  gr=ob.get('export_group');root=GROUPS.get(gr)
  if root:
   w=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=w

def measure():
 bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for ob in OBJECTS:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={};out=[]
 for src in OBJECTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0000001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();role=src['material_role'];group=src.get('export_group','static')
  if not src.get('custom_graphics_uv'):U.metric_uv(ob,M[role])
  else:ob.data.uv_layers[0].name='metric_material_uv'
  groups.setdefault((group,role),[]).append(ob)
 for (group,role),parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in parts:ob.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=ident+'__'+group+'__'+role;ob['material_role']=role;ob['functional_group']=group
  ob['semantic_parts']=json.dumps([s.name for s in OBJECTS if s['material_role']==role and s.get('export_group','static')==group]);root=GROUPS.get(group)
  if root:w=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=w
  out.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in out+MARKERS:ob.select_set(True)
 bpy.context.view_layer.objects.active=out[0]
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)
 return len(groups)

def main():
 bpy.context.preferences.filepaths.save_version=0;only=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else None;records=[];collisions={};api={}
 if only:
  records=[r for r in json.loads((BASE/'manifest.json').read_text())['assets']if r['catalogue_id']!=only];collisions=json.loads((BASE/'collision_proposals.json').read_text());api=json.loads((BASE/'service_api.json').read_text())['assets']
 for ident,title,fn in [('AST-HSP-003','Twin-spout countertop beverage station',beverage),('AST-HSP-004','Guest dish return with rear extraction caddy',dirty_return)]:
  if only and ident!=only:continue
  reset();fn();datum=marker('ASSET_DATUM',(0,0,0),'asset_origin');datum['source_frame']='metres Blender Z-up,guest front-Y,staff rear+Y';datum['exchange_frame']='GLB Y-up;(x,y,z) to(x,z,-y)';bind_source_groups();bounds,tri=measure();sc=bpy.context.scene;sc['catalogue_id']=ident;sc['source_frame']='metres Blender Z-up, guest front-Y, staff rear+Y';sc['exchange_frame']='GLB Y-up; (x,y,z)->(x,z,-y)';sc['scope']='Original component; no operating food/device system';sc['pivot']='support plane Z0' if ident.endswith('003') else'floor Z0'
  bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);mesh_count=export(ident)
  raw=(BASE/'exports'/f'{ident}.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);runtime_tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes']for p in m['primitives'])
  record={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_hospitality_stations.py','source_frame':'Metres Blender Z-up; right+X; guest front-Y; staff rear+Y','exchange_frame':'GLB Y-up; source(x,y,z)→(x,z,−y); actual node hierarchy authoritative','pivot':'support plane Z0, proposed host top+0.90 m' if ident.endswith('003') else'floor origin Z0','dimensions_blender_xyz_m':bounds['dimensions_m'],'evaluated_triangles':runtime_tri,'exported_triangles':runtime_tri,'bounds_blender_z_up':bounds,'bounds_gltf_y_up':bbox(bounds['min_m'],bounds['max_m']),'evaluated_source_triangles':tri,'editable_semantic_parts':len(OBJECTS),'runtime_material_group_meshes':mesh_count,'material_roles':sorted({o['material_role'] for o in OBJECTS}),'used_textures_packed':True,'semantic_parts':[o.name for o in OBJECTS],'physical_contacts':CONTACTS.copy(),'clearances':CLEAR.copy(),'functional_features':FEATURES.copy(),'proposed_motion_nodes':[{k:(list(ob[k]) if not isinstance(ob[k],(str,int,float,bool)) else ob[k]) for k in ob.keys()}|{'name':name} for name,ob in GROUPS.items()],'UV':'Metric dominant-face projection on evaluated geometry; UV layer normalized prior joins; walnut grain follows vertical V on facades; original label atlas preserves explicit region UV','consolidation':'Evaluated static meshes consolidated by material within functional group; editable semantic source parts and modifiers retained','collision_proposal':'collision_proposals.json','service_api':'service_api.json','dependencies':['../../standards/materials.py','../../standards/staff_materials.py','../../standards/utility_ports.py','../../materials/','textures/station_graphics.png'],'reference_guidance':['../../references/hospitality/public_reference.png','../../references/hospitality/vibe_dining_edge.jpg','../../references/premium/image(20261002-001347).png'],'limitations':['No original game files or room/controller reconstruction','No working food, fluid or electrical device system','No food hygiene, structural, accessibility or universal species certification','Collision, motion, approach and host placement are geometric proposals pending engine/room adoption']}
  for key,path in [('source_sha256',BASE/record['source']),('glb_sha256',BASE/record['export']),('generator_sha256',Path(__file__))]:record[key]=hashlib.sha256(path.read_bytes()).hexdigest()
  (BASE/f'{ident}.manifest.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record);collisions[ident]={'status':'Physically meaningful per-body box proposals; no automatic whole-body hull','frame':'Blender source Z-up with converted GLB Y-up bounds','openings_policy':'Receiving, cup and staff extraction spaces remain open','boxes':COL.copy()};api[ident]={'contacts':CONTACTS.copy(),'clearances':CLEAR.copy(),'features':FEATURES.copy(),'motion_nodes':record['proposed_motion_nodes']}
 records.sort(key=lambda r:r['catalogue_id'])
 (BASE/'manifest.json').write_text(json.dumps({'family':'Hospitality service stations','unique_design_count':2,'assets':records},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(collisions,indent=2)+'\n');(BASE/'service_api.json').write_text(json.dumps({'revision':'hospitality-stations-01','assets':api},indent=2)+'\n')
 print('STATIONS_BUILT',[(r['catalogue_id'],r['evaluated_source_triangles']) for r in records])
if __name__=='__main__':main()
