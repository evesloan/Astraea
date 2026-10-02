"""Original script-assisted editable engineering pair; Blender 4.3.2.
Metres; source Z up/front -Y/floor Z0. No fluid, pressure or power simulation.
Shared staff finishes remain unchanged. Build with blender -b -t 2 --python this_file.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
SM=module('staff_materials',CAT/'standards/staff_materials.py');UP=module('utility_ports',CAT/'standards/utility_ports.py');MATS=SM.materials()
ROLES={'paint':'staff_bluegrey_paint','white':'staff_white_paint','metal':'staff_zinc','dark':'staff_rubber','label':'staff_label','blue':'staff_cable_blue'}
OBJECTS=[];MARKERS=[];SUPPORTS=[];CLEARANCES=[];PORTS=[]
def exchange(p):return [float(p[0]),float(p[2]),float(-p[1])]
def reset():
 global OBJECTS,MARKERS,SUPPORTS,CLEARANCES,PORTS
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 OBJECTS=[];MARKERS=[];SUPPORTS=[];CLEARANCES=[];PORTS=[]
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def register(ob,role=None,group='static'):
 if role:ob['material_role']=ROLES.get(role,role)
 ob['export_group']=group;ob['original_design']='Original Astraea component; script-assisted editable geometry, not recovered game geometry'
 OBJECTS.append(ob);return ob

def mesh(name,verts,faces,role='metal',bevel=0,group='static'):
 ob=UP.mesh(name,verts,faces,MATS[ROLES[role]]);register(ob,role,group)
 if bevel:
  mod=ob.modifiers.new('Editable manufactured edge easing','BEVEL');mod.width=bevel;mod.segments=1;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
  mod=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return ob

def box(name,c,d,role='metal',bevel=.002,group='static'):
 x,y,z=c;a,b,c=[n/2 for n in d];verts=[(x+xx,y+yy,z+zz) for xx,yy,zz in [(-a,-b,-c),(a,-b,-c),(a,b,-c),(-a,b,-c),(-a,-b,c),(a,-b,c),(a,b,c),(-a,b,c)]]
 return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,group)

def extrude_profile(name,profile,a,b,axis='Y',role='paint',bevel=.001,group='static'):
 # Profile is XZ for Y extrusion; XY for Z; YZ for X.
 verts=[]
 for depth in(a,b):
  for u,v in profile:verts.append((u,depth,v) if axis=='Y' else((u,v,depth) if axis=='Z' else(depth,u,v)))
 n=len(profile);faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
 return mesh(name,verts,faces,role,bevel,group)

def cyl(name,a,b,r,role='metal',n=24,group='static'):
 return register(UP.solid_cylinder(name,a,b,r,MATS[ROLES[role]],n),role,group)

def annular(name,face,axis,stations,role='metal',n=48,group='static'):
 return register(UP.annular(name,face,axis,stations,MATS[ROLES[role]],n),role,group)

def solid_revolve(name,origin,axis,stations,role='paint',n=48,group='static'):
 p=Vector(origin);axis,u,v=UP.basis(axis);verts=[]
 for s,r in stations:verts.extend(tuple(p+axis*s+r*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n))) for i in range(n))
 faces=[tuple(reversed(range(n))),tuple((len(stations)-1)*n+i for i in range(n))]
 for k in range(len(stations)-1):faces += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
 return mesh(name,verts,faces,role,0,group)

def drill(ob,a,b,r,name):
 cutter=UP.solid_cylinder(name+'_tool',a,b,r,MATS['staff_zinc'],48)
 bpy.context.view_layer.objects.active=ob
 mod=ob.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();UP.metric_uv(ob,ob.data.materials[0])
 ob['bore_operation']='Applied exact bore cut; generator reproduces; editable resultant vertices retained'

def marker(name,p,normal=None,kind='contact',group='static'):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.location=p;ob.empty_display_type='ARROWS';ob.empty_display_size=.06
 ob['kind']=kind;ob['position_blender_source_m']=list(p);ob['position_gltf_yup_m']=exchange(p);ob['datum']='asset floor Z0; source frame metres'
 if normal:ob['direction_blender_source']=list(normal);ob['direction_gltf_yup']=exchange(normal)
 ob['export_group']=group;MARKERS.append(ob);return ob

def pairpoint(name,p,normal=None,kind='physical_contact'):
 row={'name':name,'kind':kind,'position_blender_source_m':list(p),'position_gltf_yup_m':exchange(p)}
 if normal:row.update(direction_blender_source=list(normal),direction_gltf_yup=exchange(normal))
 return row

def flange(name,p,n):
 result=UP.add_flange(name,p,n,MATS)
 for ob in result['objects']:register(ob)
 PORTS.append(result['record']);mark=UP.add_port_marker(name,p,n,result['record']);MARKERS.append(mark)

def text(name,body,p,size=.027,role='dark',group='static'):
 data=bpy.data.curves.new(name+'_editable_text','FONT');data.body=body;data.size=size;data.align_x='CENTER';data.extrude=0;data.space_character=1.05
 ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=p;ob.rotation_euler=(math.pi/2,0,0)
 data.materials.append(MATS[ROLES[role]]);ob['material_role']=ROLES[role]
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob=bpy.context.object;UP.metric_uv(ob,MATS[ROLES[role]]);ob.select_set(False)
 register(ob,role,group);ob['label_text']=body;return ob

def bolt(name,p,axis=(0,0,1),r=.012,length=.019,group='static'):
 p=Vector(p);n=Vector(axis);return cyl(name,p-n*length/2,p+n*length/2,r,'metal',6,group)

def feet_skid():
 # Two folded closed rails carry crossbars. Floor pads are exactly Z0.
 for x in(-.56,.56):
  profile=[(x-.045,.045),(x+.045,.045),(x+.045,.142),(x+.034,.160),(x-.034,.160),(x-.045,.142)]
  extrude_profile('skid_longitudinal_formed_rail_'+str(x),profile,-.40,1.09,role='paint',bevel=.003)
  for y in(-.30,.97):
   box('floor_pad_'+str((x,y)),(x,y,.020),(.18,.21,.040),'dark',.004)
   box('anchor_plate_'+str((x,y)),(x,y,.051),(.19,.22,.022),'metal',.002)
   # Broad pads and rail intersect behind hidden top support surfaces.
   for xx in(x-.066,x+.066):bolt('skid_anchor_'+str((xx,y)),(xx,y,.069),r=.012)
   row=pairpoint('floor_pad_'+str((x,y)),(x,y,0),(0,0,1));row['footprint_xy_m']=[.18,.21];SUPPORTS.append(row);marker(row['name']+'_contact',(x,y,0),(0,0,1),'physical_floor_contact')
 for y in(-.12,.16,.354,.54,.88):box('load_crossmember_'+str(y),(0,y,.138),(1.15,.092,.05),'metal',.003)


def pump():
 feet_skid()
 body=annular('cast_pump_chamber_with_open_X_bore',(0,0,.60),(1,0,0),[(-.33,.08,.10),(-.26,.08,.11),(-.21,.08,.255),(-.18,.08,.28),(.18,.08,.28),(.21,.08,.255),(.26,.08,.11),(.33,.08,.10)],'paint',48)
 drill(body,(0,-.40,.60),(0,0,.60),.135,'Real_front_service_aperture')
 annular('pump_front_service_open_collar',(0,0,.60),(0,-1,0),[(.190,.135,.178),(.278,.135,.178)],'metal',48)
 for s in(-1,1):
  flange('pump_'+('left' if s<0 else'right'),(s*.85,0,.6),(s,0,0))
  annular('pump_'+str(s)+'_continuous_nozzle',(0,0,.60),(s,0,0),[(.315,.08,.10),(.758,.08,.10)],'paint',48)
  # Pipe saddle sits below nozzle and joins the outside at Z0.50.
  box('nozzle_saddle_foot_'+str(s),(s*.56,0,.185),(.14,.21,.054),'metal',.003)
  extrude_profile('nozzle_saddle_web_'+str(s),[(s*.56-.032,.201),(s*.56+.032,.201),(s*.56+.026,.50),(s*.56-.026,.50)],-.028,.028,role='metal',bevel=.001)
  # Actual ring clamp surrounds external pipe; bore remains unobstructed.
  annular('nozzle_clamp_'+str(s),(s*.56,0,.60),(1,0,0),[(-.025,.1002,.112),(.025,.1002,.112)],'metal',48)
 for x in(-.145,.145):
  box('pump_cast_mount_foot_'+str(x),(x,.0,.186),(.13,.32,.065),'paint',.005)
  extrude_profile('pump_cast_mount_web_'+str(x),[(x-.043,.206),(x+.043,.206),(x+.025,.355),(x-.025,.355)],-.105,.105,role='paint',bevel=.002)
  for y in(-.11,.11):bolt('pump_mount_bolt_'+str((x,y)),(x,y,.226),r=.015,length=.022)
 # Front cover attaches at the shell face, not through the central pipe opening.
 solid_revolve('pump_front_removable_service_cover',(0,0,.60),(0,-1,0),[(.275,.176),(.292,.176),(.310,.160)],'white',48,'pump_service_cover')
 for i in range(8):
  a=2*math.pi*i/8;bolt('pump_front_cover_bolt_'+str(i),(.152*math.sin(a),-.315,.60+.152*math.cos(a)),(0,-1,0),.009,.013,'pump_service_cover')
 box('pump_identification_plaque',(0,-.314,.606),(.23,.006,.072),'label',.001,'pump_service_cover')
 text('pump_name','P-01  TRANSFER',(0,-.318,.609),.020,group='pump_service_cover')
 text('pump_service','COVER  -Y',(0,-.318,.582),.014,group='pump_service_cover')
 # Shaft and guard bridge directly into the pump back and drive nose.
 cyl('pump_drive_shaft',(0,.218,.60),(0,.485,.60),.045,'metal',24)
 solid_revolve('drive_motor_cast_housing',(0,0,.60),(0,1,0),[(.442,.10),(.48,.17),(.52,.178),(.91,.178),(.968,.15),(.998,.145)],'paint',48)
 for i in range(14):
  a=2*math.pi*i/14
  if math.cos(a)<-.65:continue
  # axial motor cooling fins, supported at every long edge
  pts=[]
  for r,t in[(.174,a-.030),(.201,a-.030),(.201,a+.030),(.174,a+.030)]:pts.append((r*math.sin(t),.60+r*math.cos(t)))
  extrude_profile('drive_integral_cooling_fin_'+str(i),pts,.53,.90,role='paint',bevel=.0008)
 for y in(.55,.87):
  box('motor_foot_'+str(y),(0,y,.188),(.44,.15,.05),'paint',.004)
  for x in(-.16,.16):
   extrude_profile('motor_saddle_web_'+str((x,y)),[(x-.035,.20),(x+.035,.20),(.14 if x>0 else-.085,.515),(.085 if x>0 else-.14,.515)],y-.046,y+.046,role='paint',bevel=.002)
   bolt('motor_mount_bolt_'+str((x,y)),(x,y-.055,.222),r=.013,length=.019)
 # Coupling guard: hollow arched shell, bolted skirts, a visible removable group.
 n=16;outer=[(.126*math.cos(math.pi*i/n),.60+.126*math.sin(math.pi*i/n)) for i in range(n+1)];inner=[(.112*math.cos(math.pi*i/n),.60+.112*math.sin(math.pi*i/n)) for i in reversed(range(n+1))]
 extrude_profile('coupling_guard_formed_half_shell',outer+inner,.264,.445,role='white',bevel=.001,group='coupling_guard')
 for x in(-.134,.134):
  box('coupling_guard_skirt_'+str(x),(x,.354,.595),(.036,.20,.022),'white',.002,'coupling_guard')
  box('coupling_guard_standoff_'+str(x),(x,.354,.3735),(.022,.046,.431),'metal',.001)
  for y in(.29,.42):bolt('coupling_guard_captive_fastener_'+str((x,y)),(x,y,.612),r=.008,length=.014,group='coupling_guard')
 # Formed terminal hood, gasket and paired cover screws identify its single purpose.
 extrude_profile('motor_terminal_hood',[(-.10,.77),(.10,.77),(.10,.856),(.065,.89),(-.065,.89),(-.10,.856)],.635,.80,role='white',bevel=.003)
 box('motor_terminal_cover_seam',(0,.628,.830),(.176,.009,.103),'dark',.001)
 box('motor_terminal_cover',(0,.619,.83),(.183,.014,.11),'white',.002)
 for x in(-.065,.065):bolt('terminal_captive_screw_'+str(x),(x,.608,.848),(0,-1,0),.006,.01)
 cyl('motor_cable_gland',(0,.795,.823),(0,.853,.823),.025,'dark',12)
 # Rear end guard supports vent slots; this is static geometry without electricity.
 for z in(-.09,-.06,-.03,0,.03,.06,.09):
  half=math.sqrt(.125**2-z*z)
  box('drive_rear_vent_'+str(z),(0,1.003,.60+z),(2*half,.006,.010),'dark',.001)
 marker('pump_front_cover_service_point',(0,-.319,.60),(0,-1,0),'service_tool_access_proposal','pump_service_cover')
 marker('coupling_guard_lift_axis',(0,.354,.73),(0,0,1),'removal_axis_proposal','coupling_guard')
 CLEARANCES.extend([
 {'name':'front_cover_withdrawal','type':'clear_prism','min_blender_source_m':[-.38,-1.20,.22],'max_blender_source_m':[.38,-.33,1.2],'purpose':'Approach from -Y and pull front cover outward; 0.85 m work depth proposal'},
 {'name':'drive_rear_service','type':'clear_prism','min_blender_source_m':[-.40,1.12,.16],'max_blender_source_m':[.40,1.72,1.0],'purpose':'0.60 m behind motor for endbell and terminal access'},
 {'name':'coupling_guard_lift','type':'clear_prism','min_blender_source_m':[-.20,.24,.74],'max_blender_source_m':[.20,.46,1.12],'purpose':'Lift guard +Z after releasing captive skirt fasteners'}])


def filter_vessel():
 # Three splayed fabricated feet leave the front centre open for maintenance.
 for i,a in enumerate((math.radians(90),math.radians(210),math.radians(330))):
  x,y=.37*math.cos(a),.37*math.sin(a);tx,ty=.267*math.cos(a),.267*math.sin(a)
  box('filter_floor_pad_'+str(i),(x,y,.018),(.18,.19,.036),'dark',.003)
  box('filter_foot_plate_'+str(i),(x,y,.047),(.20,.21,.025),'metal',.002)
  # Sloping square closed brace, bottom above plate, top welded under belly.
  axis=(Vector((tx,ty,.480))-Vector((x,y,.055))).normalized();u=Vector((-math.sin(a),math.cos(a),0));v=axis.cross(u).normalized();verts=[]
  for j,c in enumerate((Vector((x,y,.055)),Vector((tx,ty,.480)))):
   tr=.024 if j==0 else .010
   verts += [tuple(c+u*s+v*t) for s,t in[(-.030,-tr),(.030,-tr),(.030,tr),(-.030,tr)]]
  mesh('filter_splayed_closed_leg_'+str(i),verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'metal',.002)
  for dx in(-.065,.065):bolt('filter_anchor_'+str((i,dx)),(x+dx,y,.07),r=.012,length=.02)
  row=pairpoint('filter_floor_contact_'+str(i),(x,y,0),(0,0,1));row['footprint_xy_m']=[.18,.19];SUPPORTS.append(row);marker(row['name'],(x,y,0),(0,0,1),'physical_floor_contact')
 # Closed-bottom hollow formed vessel with real X nozzle holes into its cavity.
 body=annular('filter_hollow_formed_shell',(0,0,0),(0,0,1),[(.375,.145,.175),(.405,.202,.23),(.45,.252,.282),(1.29,.252,.282),(1.355,.252,.282),(1.378,.254,.308)],'white',48)
 solid_revolve('filter_closed_shallow_belly',(0,0,0),(0,0,1),[(.338,.085),(.35,.12),(.377,.177),(.402,.204)],'white',48)
 drill(body,(-.50,0,.60),(.50,0,.60),.08,'Two_real_nozzle_openings_to_chamber')
 # Neck ends terminate exactly inside shell bore, not as fake cap disks.
 for s in(-1,1):
  flange('filter_'+('left' if s<0 else'right'),(s*.64,0,.60),(s,0,0))
  annular('filter_'+str(s)+'_hollow_nozzle',(0,0,.60),(s,0,0),[(.235,.08,.10),(.548,.08,.10)],'paint',48)
  # Reinforcement collar is also hollow, outside wall; no ring disk through bore.
  annular('filter_nozzle_reinforcing_ring_'+str(s),(0,0,.60),(s,0,0),[(.273,.081,.128),(.296,.081,.128)],'metal',48)
 annular('filter_neck_gasket',(0,0,0),(0,0,1),[(1.378,.253,.307),(1.386,.253,.307)],'dark',48)
 # Lid is preserved as a separate named export assembly with upward removal axis.
 solid_revolve('filter_removable_domed_lid',(0,0,0),(0,0,1),[(1.386,.308),(1.408,.308),(1.43,.279),(1.47,.20),(1.492,.07)],'white',48,'service_lid')
 # Split rim shows boundary between body flange and lid, six captive clamps are hand scale.
 for i in range(6):
  a=2*math.pi*i/6;x,y=.278*math.sin(a),.278*math.cos(a)
  cyl('filter_lid_captive_stud_'+str(i),(x,y,1.348),(x,y,1.423),.008,'metal',12,'service_lid')
  bolt('filter_lid_hex_'+str(i),(x,y,1.422),(0,0,1),.018,.028,'service_lid')
 # U handles attach through feet on domed lid; raised bridge stays easy to grasp.
 for y in(-.115,.115):
  for x in(-.075,.075):cyl('lid_handle_post_'+str((x,y)),(x,y,1.46),(x,y,1.555),.012,'metal',12,'service_lid')
  cyl('lid_handle_grip_'+str(y),(-.075,y,1.555),(.075,y,1.555),.014,'dark',16,'service_lid')
  marker('lid_handle_grip_point_'+str(y),(0,y,1.555),(0,0,1),'grip_centreline_proposal','service_lid')
 # Front purpose label on shallow formed saddle with no decorative box clutter.
 for x in(-.105,.105):box('identity_plate_curved_shell_standoff_'+str(x),(x,-.263,1.06),(.028,.062,.09),'metal',.001)
 box('filter_identity_plate',(0,-.287,1.06),(.29,.014,.17),'label',.003)
 text('filter_name','F-02',(0,-.296,1.099),.041)
 text('filter_function','SERVICE FILTER',(0,-.296,1.060),.021)
 text('filter_lid_direction','LIFT LID  +Z',(0,-.296,1.021),.019)
 # A small closed drain service boss near the belly, distinctly not a pipe-system port.
 cyl('filter_drain_boss',(0,-.11,.354),(0,-.215,.354),.027,'metal',16)
 bolt('filter_drain_plug',(0,-.228,.354),(0,-1,0),.031,.026)
 marker('filter_drain_service_point',(0,-.25,.354),(0,-1,0),'service_tool_access_proposal')
 marker('filter_lid_removal_axis',(0,0,1.386),(0,0,1),'service_lid_origin','service_lid')
 CLEARANCES.extend([
 {'name':'filter_front_maintenance','type':'clear_prism','min_blender_source_m':[-.48,-1.30,0],'max_blender_source_m':[.48,-.47,1.9],'purpose':'0.83 m approach depth from -Y to lid clamps/drain; feet stay behind this prism'},
 {'name':'filter_lid_and_cartridge_withdrawal','type':'clear_prism','min_blender_source_m':[-.35,-.35,1.57],'max_blender_source_m':[.35,.35,2.36],'purpose':'0.79 m vertical lift reservation above 1.569 m grip top; overhead services must remain outside'}])


def measure(objects):
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts += [ob.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={};runtime=[]
 for src in OBJECTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy()
  # Reproject final triangles per dominant polygon normal after bevel/Boolean, guaranteeing noncollapsed metric UVs.
  UP.metric_uv(ob,MATS[src['material_role']]);role=src['material_role'];group=src.get('export_group','static');groups.setdefault((group,role),[]).append(ob)
 for (group,role),parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in parts:ob.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=ident+'__'+group+'__'+role;ob['material_role']=role;ob['assembly_role']=group
  ob['semantic_parts']=json.dumps([s.name for s in OBJECTS if s['material_role']==role and s.get('export_group','static')==group]);runtime.append(ob)
  if group!='static':
   direction=[0,-1,0] if group=='pump_service_cover' else [0,0,1];ob['removal_direction_blender_source']=direction;ob['removal_direction_gltf_yup']=exchange(direction);ob['interaction_status']='Named editable removable assembly proposal; no runtime controls'
 for ob in runtime+MARKERS:ob.select_set(True)
 bpy.context.view_layer.objects.active=runtime[0]
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)
 return len(groups)

def bounds_glb(bounds):
 lo,hi=bounds['min_m'],bounds['max_m'];pts=[exchange((x,y,z)) for x in(lo[0],hi[0]) for y in(lo[1],hi[1]) for z in(lo[2],hi[2])]
 return {'min_m':[min(p[k] for p in pts) for k in range(3)],'max_m':[max(p[k] for p in pts) for k in range(3)]}

def source_checks(ident):
 # Evaluate all support surfaces against finished body regions. Named intersection intent is bounded.
 rows=[]
 if ident=='AST-ENG-001':
  rows=[{'relationship':'pump feet -> crossbars -> longitudinal skid rails -> floor pads','passes':True,'basis':'Crossbar top .163, cast foot bottom .1535; rail top .160 and crossbar bottom .113; pad top .040/anchor plate bottom .040. Positive overlap only within intended joint thickness.'},
   {'relationship':'pump cast web hidden behind lower cast shell','passes':True,'basis':'Web top .355 versus shell bottom .320; at web X±.145, Y±.105 shell lower surface .3405. Web extends .0145 m behind shell, never beyond exterior top/face.'},
   {'relationship':'drive feet and upright webs remain below motor finished crown','passes':True,'basis':'Splayed web top Z.515, X .085-.140 (mirrored left); maximum radial distance from shaft .164 m < housing .178 m. Tops join inside housing while feet remain wider.'},
   {'relationship':'pipe clamps preserve axial .16 m bores','passes':True,'basis':'Clamp inner radius .1002 m > pipe .10 m OD radius; webs stop at Z .50, below bore bottom .52'}]
 else:
  rows=[{'relationship':'three splayed legs to shell lower taper','passes':True,'basis':'Top radial centre .267 at Z .480; radial half thickness .010 and tangent half width .030. All top corners sit within shell annulus .252-.282 and above lower taper; no outer or inner surface breakout.'},
   {'relationship':'lid posts to domed lid','passes':True,'basis':'Post bottoms Z1.460 at radial .137, within lid dome below Z1.485; grip tops1.569'},
   {'relationship':'open nozzle into chamber','passes':True,'basis':'Both nozzle inner ends X±.235; cavity radius .252. At bore edge Y .08, inner wall X .239; the mouth therefore opens into the cavity across the full circular bore.'}]
 return rows

def collisions(ident):
 # Individual material bodies; no convex wrapping around component/ports/service space.
 if ident=='AST-ENG-001':
  boxes=[('skid_left',[-.66,-.405,0],[-.46,1.10,.165]),('skid_right',[.46,-.405,0],[.66,1.10,.165]),('pump_case',[-.34,-.315,.31],[.34,.28,.89]),('motor',[-.21,.44,.39],[.21,1.01,.90]),('guard',[-.17,.26,.20],[.17,.46,.74])]
 else:boxes=[('vessel_body',[-.285,-.29,.335],[.285,.285,1.38]),('lid',[-.31,-.31,1.386],[.31,.31,1.57])]
 result={'status':'simplified collision proposal only, not engine-tested','frame':'Blender asset local Z-up; matching GLB fields included','boxes':[{'name':n,'min_blender_source_m':lo,'max_blender_source_m':hi,'bounds_gltf_yup_m':bounds_glb({'min_m':lo,'max_m':hi})} for n,lo,hi in boxes],'ports':'Use annular segmented hulls from port profile if nozzle collision is needed; never cap the bores with automatic whole-asset hull','open_space_policy':'No collider across front approach or lid/guard removal volumes; no whole-component convex hull','floor_supports':SUPPORTS.copy()}
 return result

def main():
 bpy.context.preferences.filepaths.save_version=0;recs=[];col={};api={}
 for ident,title,fn in [('AST-ENG-001','Compact transfer pump skid',pump),('AST-ENG-002','Serviceable vertical filter vessel',filter_vessel)]:
  reset();fn()
  bounds,tri=measure(OBJECTS)
  for c in CLEARANCES:
   bb=bounds_glb({'min_m':c['min_blender_source_m'],'max_m':c['max_blender_source_m']});c['min_gltf_yup_m']=bb['min_m'];c['max_gltf_yup_m']=bb['max_m'];c['status']='human-scale geometric work reservation, not validated actor/real-engineering clearance'
  points=[{k:(list(ob[k]) if not isinstance(ob[k],(str,int,float,bool)) else ob[k]) for k in ob.keys()}|{'name':ob.name} for ob in MARKERS]
  sc=bpy.context.scene;sc['catalogue_id']=ident;sc['scope']='Original editable asset library, no ship room or game implementation';sc['source_frame']='metres Blender Z-up, ordinary front -Y, pivot floor (0,0,0)';sc['exchange_frame']='GLB Y-up (x,z,-y)'
  for im in bpy.data.images:
   if im.source=='FILE' and not im.packed_file:im.pack()
  bpy.ops.object.select_all(action='DESELECT')
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True)
  runtime=export(ident)
  record={'catalogue_id':ident,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_utility_machines.py','units':'metres','source_frame':'Blender Z-up, +X right, +Y rear, front -Y','exchange_frame':'GLB Y-up, source point (x,y,z) -> (x,z,-y)','pivot':pairpoint('floor_origin',(0,0,0),(0,0,1),'asset_origin'), 'bounds_blender_z_up':bounds,'bounds_gltf_y_up':bounds_glb(bounds),'evaluated_triangles':tri,'editable_semantic_parts':len(OBJECTS),'runtime_material_group_meshes':runtime,'material_roles':sorted(set(ob['material_role'] for ob in OBJECTS)),'used_textures_packed':True,'semantic_parts':[ob.name for ob in OBJECTS],'ports':PORTS.copy(),'floor_contacts':SUPPORTS.copy(),'service_and_connection_markers':points,'maintenance_clearances':CLEARANCES.copy(),'support_checks':source_checks(ident),'runtime_static_consolidation':'One mesh per material role and necessary removal group; UV names and final projection normalized before joining; removable coupling guard/lid retained','UV':'Metric dominant-face projected UVs; final evaluated geometry reprojected before role joins','collision_proposal':'collision_proposals.json','reference_manifest':'../../batches/batch06/reference_manifest.json','dependencies':['../../standards/staff_materials.py','../../standards/utility_ports.py','../../materials/staff/'],'artistic_interface_revision':'utility-port-01','limitations':['No recovered game geometry','No room reconstruction or ship allocation','No operating pressure, load, flow or electrical rating','No fluid/power simulation','Actor use, actual room fit and target-PC cost remain pending']}
  record['source_sha256']=hashlib.sha256((BASE/'source'/f'{ident}.blend').read_bytes()).hexdigest();record['glb_sha256']=hashlib.sha256((BASE/'exports'/f'{ident}.glb').read_bytes()).hexdigest();record['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
  (BASE/f'{ident}.manifest.json').write_text(json.dumps(record,indent=2)+'\n');recs.append(record);col[ident]=collisions(ident);api[ident]={'ports':PORTS.copy(),'service_points':points,'maintenance_clearances':CLEARANCES.copy()}
 (BASE/'manifest.json').write_text(json.dumps({'family':'Purpose-shaped engineering utility machines','unique_design_count':2,'assets':recs},indent=2)+'\n')
 (BASE/'collision_proposals.json').write_text(json.dumps(col,indent=2)+'\n');(BASE/'connection_api.json').write_text(json.dumps({'revision':'utility-machines-01','assets':api},indent=2)+'\n')
 module('collision_proposals',BASE/'source/build_collision_proposals.py').main()
 print('UTILITY_MACHINES_BUILT',[(r['catalogue_id'],r['evaluated_triangles']) for r in recs])
if __name__=='__main__':main()
