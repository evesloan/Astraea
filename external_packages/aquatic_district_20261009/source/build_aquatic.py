"""Editable bounded aquatic assembly. Blender 5.1.2. No host source writes."""
import bpy,math,json,sys,importlib.util,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
P=Path(__file__).resolve().parents[1];D=json.loads((P/'docs/AQUATIC_CONSTRUCTION_PLAN.json').read_text());A=[];F=[];LIGHT=[];M={}
def xyz(p):return Vector((p[0],-p[2],p[1]))
def uv(o):
 me=o.data;me.update();layer=me.uv_layers.get('UV0') or me.uv_layers.new(name='UV0')
 for f in me.polygons:
  drop=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=drop]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(v[axes[0]]*.5,v[axes[1]]*.5)
def finish(o,n,role='ivory_enamel',kind='architecture',support='annex_substrate',bevel=0):
 o.name='AQD__'+n;o['programme_key']='D08_directory_08';o['kind']=kind;o['support_owner']=support;o['construction_status']='source_and_export_only_root_adoption_pending'
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(M[role]);bpy.context.view_layer.objects.active=o
  if bevel:
   mod=o.modifiers.new('Crafted edge','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  uv(o)
  if kind not in ['water_visual','tube_static_visual','fixture_lens']:o['collision_proposal']='static_concave_triangles'
  else:o['collision_proposal']='none; future gameplay owner'
 (F if kind=='compiler_floor_proposal' else A).append(o);return o
def box(n,p,d,role='ivory_enamel',kind='architecture',support='annex_substrate',bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,role,kind,support,min(bevel,min(d)*.22))
def mesh(n,vs,faces,role='warm_stone',kind='architecture',support='annex_substrate'):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(p) for p in vs],[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return finish(o,n,role,kind,support)
def rod(n,a,b,r=.05,role='champagne_metal',kind='architecture',support='annex_substrate'):
 a,b=xyz(a),xyz(b);delta=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=delta.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,role,kind,support)
def prism(n,poly,bottom,top,role='warm_stone',kind='architecture',support='annex_substrate'):
 k=len(poly);vs=[(x,bottom,z) for x,z in poly]+[(x,top,z) for x,z in poly];faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];return mesh(n,vs,faces,role,kind,support)
def slab(n,tris,y,t,role='warm_stone',kind='compiler_floor_proposal'):
 vs=[];fs=[]
 for tri in tris:
  q=len(vs);vs.extend([(x,y,z) for x,z in tri]+[(x,y-t,z) for x,z in tri]);fs.extend([(q,q+1,q+2),(q+5,q+4,q+3),(q,q+3,q+4,q+1),(q+1,q+4,q+5,q+2),(q+2,q+5,q+3,q)])
 return mesh(n,vs,fs,role,kind,n)
def rail(n,points,y):
 for i,(a,b) in enumerate(zip(points,points[1:])):
  rod(n+'_top_'+str(i),(a[0],y+1.1,a[1]),(b[0],y+1.1,b[1]),.035)
  rod(n+'_low_'+str(i),(a[0],y+.5,a[1]),(b[0],y+.5,b[1]),.025)
  rod(n+'_post_'+str(i),(a[0],y,a[1]),(a[0],y+1.1,a[1]),.04)
 a=points[-1];rod(n+'_end',(a[0],y,a[1]),(a[0],y+1.1,a[1]),.04)
def wall(n,a,b,y,h,w=.3,role='ivory_enamel'):
 dx,dz=b[0]-a[0],b[1]-a[1];o=box(n,((a[0]+b[0])/2,y+h/2,(a[1]+b[1])/2),(math.hypot(dx,dz),h,w),role);o.rotation_euler.z=-math.atan2(dz,dx);return o
def ramp(a):
 p,q=a['a'],a['b'];dx,dz=q[0]-p[0],q[2]-p[2];l=math.hypot(dx,dz);nx,nz=-dz/l,dx/l;w=a['clear_width']/2+.10
 pts=[(p[0]+nx*w,p[1],p[2]+nz*w),(q[0]+nx*w,q[1],q[2]+nz*w),(q[0]-nx*w,q[1],q[2]-nz*w),(p[0]-nx*w,p[1],p[2]-nz*w)]
 vs=[(x,y-.20,z) for x,y,z in pts]+pts;mesh(a['id'],vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_stone','ramp_asset',a['id'])
 for side in [-1,1]:
  posts=[]
  for i in range(9):
   t=i/8;x=p[0]+dx*t+nx*w*side;y=p[1]+(q[1]-p[1])*t;z=p[2]+dz*t+nz*w*side
   rod(a['id']+'_bearing_'+str(side)+'_'+str(i),(x,44,z),(x,y-.2,z),.065,'warm_stone') if y>44.21 else None
   rod(a['id']+'_post_'+str(side)+'_'+str(i),(x,y,z),(x,y+1.1,z),.04);posts.append((x,y+1.1,z))
  for i in range(8):rod(a['id']+'_handrail_'+str(side)+'_'+str(i),posts[i],posts[i+1],.035)
 # Actual lower/upper landing contact records, not an unsolved player pose.
 for tag,v in [('LOWER',p if p[1]<q[1] else q),('UPPER',q if p[1]<q[1] else p)]:empty(a['id']+'_'+tag,v)
def empty(n,p):
 o=bpy.data.objects.new('DATUM_'+n,None);bpy.context.collection.objects.link(o);o.location=xyz(p);o.empty_display_size=.12;A.append(o);return o
def circular_pool(n,c,r,bottom,water,rim):
 x,z=c;poly=[(x+r*math.cos(i*2*math.pi/48),z+r*math.sin(i*2*math.pi/48)) for i in range(48)]
 prism(n+'_bottom',poly,bottom-.15,bottom,'warm_stone','basin_asset',n)
 for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):wall(n+'_wall_'+str(i),a,b,bottom,rim-bottom,.16,'warm_stone')
 prism(n+'_water',[(x+(a-x)*.97,z+(b-z)*.97) for a,b in poly],water-.02,water,'water','water_visual',n)
 # Water entry treads on west edge, plus stationary transfer chair/hoist reservation.
 for i in range(4):box(n+'_wet_tread_'+str(i),(x-r+.45+i*.38,rim-.12-.16*i,z),(1.0,.22,1.6),'warm_stone','basin_entry',n)
 pad=box(n+'_transfer_pad',(x-r-.6,rim-.10,z+1.25),(1.1,.2,1.6),'dark_rubber','basin_entry',n)
 rod(n+'_hoist_post',(x-r-.7,rim,z+1.7),(x-r-.7,rim+1.65,z+1.7),.07,'champagne_metal')
 rod(n+'_hoist_arm',(x-r-.7,rim+1.65,z+1.7),(x-.4,rim+1.65,z+.2),.06,'champagne_metal')
 box(n+'_transfer_seat',(x-r-.5,rim+.46,z+.7),(.85,.12,.8),'teal_weave','transfer_fixture',n)
 for side in [-1,1]:rod(n+'_adaptive_handhold_'+str(side),(x+side*r*.8,rim,z-1),(x+side*r*.8,rim+1.35,z+1),.04)
 empty(n+'_GRAVITY_CONTROL_RESERVED',(x-r-.9,rim+1.1,z-1.8))
def tube(n,p,vertical=False):
 bpy.ops.mesh.primitive_torus_add(major_radius=.49,minor_radius=.16,major_segments=24,minor_segments=8,location=xyz(p));o=bpy.context.object
 if vertical:o.rotation_euler.x=math.pi/2
 finish(o,n,'clay_weave','tube_static_visual','tube_rack')
 # Native markers reserve a tube mount, not a buoyant player equilibrium.
 empty(n+'_MOUNT_RESERVED',p)
def fixture(rec):
 x,y,z=rec['xyz'];n=rec['id'];support_y=49.11 if z==196 or (x>=97 and 220<=z<=244) else 51.70
 rod(n+'_drop',(x,support_y,z),(x,y+.2,z),.025,'champagne_metal','fixture_mount','roof_or_gallery')
 box(n+'_hood',(x,y+.18,z),(.55,.16,.55),'champagne_metal','fixture_mount','roof_or_gallery')
 box(n+'_lens',(x,y,z),(.4,.06,.4),'opal','fixture_lens','hood');empty(n,rec['xyz'])
 bpy.ops.object.light_add(type='POINT',location=xyz(rec['xyz']));o=bpy.context.object;o.name='SOURCE_'+n;o.data.energy=220;o.data.color=(1,.87,.69);o.data.shadow_soft_size=.22;LIGHT.append(o)
def build():
 bpy.ops.wm.read_factory_settings(use_empty=True);s=importlib.util.spec_from_file_location('materials',P/'dependencies/Catalogue/standards/materials.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);M.update(m.materials())
 for name,color in [('water',(.035,.30,.34,1)),('opal',(1,.76,.38,1)),('glass',(.29,.54,.52,1))]:
  mat=bpy.data.materials.new('AQD_'+name);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.3
  if name=='opal':bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=.5
  if name=='glass':bs.inputs['Alpha'].default_value=.28;mat.surface_render_method='DITHERED';mat.diffuse_color=(*color[:3],.28)
  M[name]=mat
 # Common horizontal substrates are a separately exported root/ compiler proposal.
 for f in D['floor_records']:
  slab(f['id'],f['triangles_xz'],f['top_y'],f['thickness_m'],'warm_stone','compiler_floor_proposal' if f['owner'].startswith('compiler') else 'basin_asset')
 # Closed plinth skin below the raised deck, excludes dry arrival/ramp opening. No1.45m service crawlway claimed.
 boundary=D['annex_boundary']
 for i,(a,b) in enumerate(zip(boundary,boundary[1:]+boundary[:1])):
  if a[0]==b[0]==56:
   wall('west_threshold_north',(56,188),(56,238),44,7.7,.32);wall('west_threshold_south',(56,242),(56,244),44,7.7,.32)
   box('west_portal_header',(56,47.5,240),(.55,.6,4.5),'warm_walnut');box('portal_canopy',(57,47.8,240),(2.2,.22,4.8),'ivory_enamel')
  elif a[0]==b[0]==100:
   wall('east_boundary_north',(100,188),(100,208.5),44,7.7,.32);wall('east_boundary_south',(100,211.5),(100,244),44,7.7,.32)
   box('service_header',(100,48.35,210),(.45,.4,3.4),'warm_walnut');empty('SERVICE_PORTAL_RESERVED',(100,45.45,210))
  else:wall('enclosure_'+str(i),a,b,44,7.7,.32)
 # Thick ceiling field and shaped bearing ribs. No skylight or D09 opening inferred.
 prism('opaque_roof',boundary,51.7,51.95,'ivory_enamel','roof_asset','perimeter_bearings')
 for i,(x,z) in enumerate([(59,189),(96,189),(59,231),(99.7,231),(63,247.5),(95,247.5)]):
  box('bearing_foot_'+str(i),(x,44.15,z),(.9,.3,.9),'warm_stone');rod('bearing_shaft_'+str(i),(x,44.3,z),(x,51.5,z),.25,'warm_stone')
  box('bearing_cap_'+str(i),(x,51.5,z),(1.35,.4,1.35),'warm_walnut')
 for i,z in enumerate([189,202,216,230,246]):
  rod('roof_rib_left_'+str(i),(58,51.25,z),(78,51.63,z),.17,'warm_walnut');rod('roof_rib_right_'+str(i),(78,51.63,z),(98,51.25,z),.17,'warm_walnut')
 # Layered wall bays with useful opaque acoustic lining and warm alcove reveals.
 for i,z in enumerate([193,205,217,229]):
  box('west_acoustic_bay_'+str(i),(56.4,48.5,z),(.18,4.8,7.5),'teal_weave');box('east_acoustic_bay_'+str(i),(99.6,48.5,z),(.18,4.8,7.5),'clay_weave')
 for f in D['river']['bed_polygons']:
  # Wall loops built from actual buffered, closed contour; no painted channel.
  for side,loop in [('outer',f['boundary']),('inner',f['holes'][0])]:
   points=loop[:-1] if loop[0]==loop[-1] else loop
   for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
    if side=='outer' and abs((a[0]+b[0])/2-78)<1.05 and (((a[1]+b[1])/2)>237.8 or ((a[1]+b[1])/2)<194.2):continue
    wall('river_'+side+'_wall_'+str(i),a,b,44.3,1.15,.12,'warm_stone')
    wall('river_'+side+'_coping_'+str(i),a,b,45.45,.10,.26,'ivory_enamel')
 # River water triangulated from the same shell record.
 slab('river_water_visual',D['floor_records'][-1]['triangles_xz'],45.25,.02,'water','water_visual')
 for a in D['ramps']:ramp(a)
 for i,(a,b) in enumerate(D['plinth_closure_segments_xz']):wall('closed_underdeck_riser_'+str(i),a,b,44,1.21,.12,'warm_stone')
 # Ramp landings, gallery and a purposeful crossing with2.23m water clearance.
 box('launch_ramp_return',(93.8,47.28,219.4),(5.2,.24,2.4),'warm_stone','ramp_asset')
 box('launch_top_landing',(96.3,49.23,243.6),(5.2,.24,2.4),'warm_stone','ramp_asset')
 box('launch_east_gallery',(98.2,49.23,219.3),(2.6,.24,48.6),'warm_stone','ramp_asset')
 rail('upper_east_guard_west',[(96.9,195),(96.9,243.6)],49.35);rail('upper_east_guard_east',[(99.5,195),(99.5,243.6)],49.35)
 box('launch_north_gallery',(80.6,49.23,196.2),(35.2,.24,2.6),'warm_stone','ramp_asset')
 rail('launch_front_guard',[(63,194.9),(69.9,194.9)],49.35);rail('launch_front_guard_middle',[(74.1,194.9),(83.4,194.9)],49.35);rail('launch_front_guard_east',[(87.6,194.9),(98.2,194.9)],49.35)
 rail('launch_rear_guard',[(63,197.5),(98.2,197.5)],49.35)
 for i,cx in enumerate([72,85.5]):
  box('launch_spur_'+str(i),(cx,49.23,193.8),(3.2,.24,2.6),'warm_stone','ramp_asset')
  rail('spur_guard_L_'+str(i),[(cx-1.6,192.6),(cx-1.6,195.0)],49.35);rail('spur_guard_R_'+str(i),[(cx+1.6,192.6),(cx+1.6,195.0)],49.35)
  empty('SLIDE_'+str(i+1)+'_ADMISSION_RESERVED',(cx,49.35,194.4))
 for i,(x,z) in enumerate([(62.9,196.2),(99.35,196.2),(99.35,243.6)]):rod('gallery_bearing_'+str(i),(x,44,z),(x,49.11,z),.17,'warm_stone')
 box('island_bridge',(66.95,47.58,202),(15.7,.24,2.6),'warm_stone','bridge_asset')
 rail('bridge_guard_north',[(59.1,200.7),(74.8,200.7)],47.7);rail('bridge_guard_south',[(59.1,203.3),(74.8,203.3)],47.7)
 for x in [59.4,73.4]:rod('bridge_bearing_'+str(x),(x,44,202),(x,47.46,202),.13,'warm_stone')
 # Two helical open flumes: full cross-section, sidewalls, complete runouts.
 for i,s in enumerate(D['slides']):
  path=s['trajectory_xyz'];vs=[];faces=[];sections=13
  for j,p in enumerate(path):
   q=path[min(j+1,len(path)-1)] if j<len(path)-1 else path[j-1];dx,dz=q[0]-p[0],q[2]-p[2]
   if j==len(path)-1:dx,dz=-dx,-dz
   ll=math.hypot(dx,dz);nx,nz=-dz/ll,dx/ll
   for k in range(sections):
    a=-math.pi/2+k*math.pi/(sections-1);l=.78*math.sin(a);h=.48*(1-math.cos(a));vs.append((p[0]+nx*l,p[1]+h,p[2]+nz*l))
  for j in range(len(path)-1):
   for k in range(sections-1):a=j*sections+k;faces.append((a,a+1,a+1+sections,a+sections))
  o=mesh(s['id'],vs,faces,'ivory_enamel','slide_trough_asset',s['id']);sol=o.modifiers.new('Contained flume thickness','SOLIDIFY');sol.thickness=.12;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sol.name)
  # Supports stay in dedicated north splash zone and clear river water corridor.
  for j in [12,28,44,60,76]:
   v=path[j];rod(s['id']+'_bearing_'+str(j),(v[0],44.3,v[2]),(v[0],v[1]-.13,v[2]),.095,'champagne_metal')
  poly=s['runout_poly'];prism(s['id']+'_runout_pan',poly,44.15,44.3,'warm_stone','basin_asset',s['id'])
  for j,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):wall(s['id']+'_runout_wall_'+str(j),a,b,44.3,1.15,.16,'warm_stone')
  prism(s['id']+'_runout_water',poly,45.28,45.3,'water','water_visual',s['id'])
  empty(s['id']+'_EXIT_RESERVED',s['exit_xyz'])
  x=s['exit_xyz'][0];box(s['id']+'_exit_seat',(x,45.91,190.7),(.9,.12,.8),'teal_weave','transfer_fixture',s['id'])
  for j in range(4):box(s['id']+'_exit_tread_'+str(j),(x,45.25-.15*j,191.15+j*.45),(1.4,.22,.6),'warm_stone','basin_entry',s['id'])
 # Pools5/6 are children, not duplicate bath-room parents.
 for a in D['new_thermal_spa_pools']:circular_pool(a['id'],a['center_xz'],a['radius_m'],a['bottom_y'],a['water_y'],a['rim_y'])
 # Curved planted/ resting edges have real plinth/soil contacts.
 for i,(cx,cz) in enumerate([(75.5,233),(74.5,211),(74.5,222)]):
  poly=[(cx+1.4*math.cos(j*2*math.pi/16),cz+.8*math.sin(j*2*math.pi/16)) for j in range(16)];prism('island_planter_'+str(i),poly,45.45,46.15,'ivory_enamel','planter_asset','island_terrace')
  prism('planter_soil_'+str(i),[(cx+(x-cx)*.9,cz+(z-cz)*.9) for x,z in poly],46.1,46.16,'dark_rubber','planter_asset','planter')
  for j in range(4):
   rod('plant_stem_'+str(i)+'_'+str(j),(cx+.3*math.cos(j),46.16,cz+.2*math.sin(j)),(cx+.4*math.cos(j),47.1,cz+.3*math.sin(j)),.035,'warm_walnut','plant_static','soil')
   for k in range(3):
    a=j*1.5+k*2.1;leaf=[(cx,46.8,cz),(cx+1.1*math.cos(a),47.0,cz+.6*math.sin(a)),(cx+.8*math.cos(a+.3),46.7,cz+.5*math.sin(a+.3))];mesh('plant_leaf_'+str(i)+'_'+str(j)+'_'+str(k),leaf,[(0,1,2),(2,1,0)],'teal_weave','plant_static','stem')
 for i,(xx,z) in enumerate([(58,193),(58,198),(90.2,247)]):
  box('river_lounge_base_'+str(i),(xx,45.65,z),(1.2,.4,3.0),'warm_walnut','lounge_asset','wet_promenade');box('river_lounge_pad_'+str(i),(xx,45.98,z),(1.15,.22,2.8),'oatmeal_weave','lounge_asset','bench_base')
 # Eight physical rings retained as static provision; no mount/ride physics claim.
 for i in range(6):tube('rack_tube_'+str(i),(83+i*.95,46.9,246.5),True)
 box('tube_rack_foot',(85.4,45.65,246.5),(6,.4,1.5),'warm_walnut','tube_rack','wet_promenade');rod('tube_rack_bar',(82.2,47.1,246.5),(88.6,47.1,246.5),.045)
 for i in range(2):tube('boarding_ring_'+str(i),(76+i*2,45.6,240.4))
 for a in D['boarding']:
  empty(a['id']+'_RECOVERY_RESERVED',a['bank_xyz']);empty(a['id']+'_AFK_WATER_RESERVED',a['water_xyz']);x,y,z=a['bank_xyz'];box(a['id']+'_transfer_seat',(x,y+.45,z),(.9,.12,.8),'teal_weave','transfer_fixture','wet_promenade')
  # Grab rail ends and four shallow, permanently supported descent treads.
  for j in range(4):
   zz=(238.02-j*.55) if 'south' in a['id'] else (193.98+j*.55);top=45.3-.2*j;box(a['id']+'_entry_tread_'+str(j),(x,(44.3+top)/2,zz),(1.6,top-44.3,.65),'warm_stone','basin_entry','river_bed')
 # Local dry privacy/rinse assistance alcoves (not another Universal changing parent).
 for i,z in enumerate([231.0,233.6]):
  n='assisted_rinse_'+str(i);wall(n+'_rear',(57.1,z-1.1),(57.1,z+1.1),45.45,2.9,.18,'ivory_enamel');wall(n+'_north',(57.1,z-1.1),(60.1,z-1.1),45.45,2.9,.18,'warm_walnut');wall(n+'_south',(57.1,z+1.1),(60.1,z+1.1),45.45,2.9,.18,'warm_walnut')
  box(n+'_roof',(58.6,48.46,z),(3,.22,2.2),'ivory_enamel');box(n+'_privacy_leaf',(60.1,46.62,z),(.12,2.34,2.2),'teal_weave','privacy_door_proposal','wet_promenade');empty(n+'_PRIVACY_CONTROL_RESERVED',(60.3,46.65,z+.85))
  box(n+'_bench',(58.0,45.93,z),(.7,.22,1.8),'oatmeal_weave','lounge_asset','wet_promenade');rod(n+'_rinse_pipe',(57.5,45.6,z+.6),(57.5,47.75,z+.6),.035);box(n+'_drain',(58.7,45.47,z),(.7,.04,.7),'dark_rubber','drain_reservation','wet_promenade')
 # Care stock/dirty return and refreshments: distinct service use, zero new dining reservations.
 for n,x,z in [('clean_towels',62.5,232),('dirty_return',62.5,234.2)]:
  box(n+'_carcass',(x,46.2,z),(1.3,1.5,1.8),'ivory_enamel','stock_asset','wet_promenade');box(n+'_shelf',(x,46.45,z),(1.45,.12,1.8),'warm_walnut','stock_asset','carcass');box(n+'_stack',(x,46.65,z),(.9,.28,1.2),'oatmeal_weave','stock_asset','shelf');empty(n+'_STOCK_RESERVED',(x-.8,46.5,z))
 box('refreshments_cove',(98.3,46.05,205.5),(2.5,1.2,5),'warm_walnut','stock_asset','wet_promenade');box('refreshments_counter',(98.3,46.72,205.5),(2.8,.14,5.2),'warm_stone','stock_asset','counter');box('refreshments_canopy',(98.3,48.3,205.5),(2.8,.24,5.6),'ivory_enamel')
 for i in range(6):box('refreshment_cup_'+str(i),(97.4,46.9,204+i*.4),(.14,.23,.14),'champagne_metal','stock_asset','counter')
 box('wet_service_cabinet',(98.6,46.45,214.5),(1.9,2,2.6),'ivory_enamel','stock_asset','wet_promenade');empty('WATER_PLANT_RETURN_RESERVED',(99,45.6,214.5));empty('BAELIN_CLEANER_RESERVED',(97.4,46.6,214.5))
 # Existing cascade's maintenance shoulder and east splash/acoustic interface. Original receiver stays untouched.
 box('cascade_maintenance_shoulder',(22,43.88,215),(2,.24,1.4),'warm_stone','maintenance_asset','retained_basin_bottom')
 for x in [21.4,22.6]:rod('cascade_shoulder_bearing_'+str(x),(x,42.8,215),(x,43.76,215),.06,'champagne_metal','maintenance_asset','retained_basin_bottom')
 rail('cascade_shoulder_guard',[(22.9,214.3),(22.9,215.7)],44)
 for i in range(16):
  a=-math.pi/2+i*math.pi/16;b=-math.pi/2+(i+1)*math.pi/16;aa=(25+2.2*math.cos(a),215+2.2*math.sin(a));bb=(25+2.2*math.cos(b),215+2.2*math.sin(b));wall('cascade_splash_'+str(i),aa,bb,42.8,2.6,.07,'glass')
  if i%4==0:rod('cascade_splash_post_'+str(i),(aa[0],42.8,aa[1]),(aa[0],45.4,aa[1]),.035,'champagne_metal','maintenance_asset','retained_basin_bottom')
 box('cascade_acoustic_hood',(22,46.65,215),(2.3,.24,1.8),'teal_weave','maintenance_asset','shoulder_posts');rod('cascade_hood_post',(21.1,44,214.3),(21.1,46.53,214.3),.04,'champagne_metal','maintenance_asset','shoulder')
 empty('CASCADE_PUMP_AND_AUDIO_RETURN_RESERVED',(22,44.8,215))
 for rec in D['lights']:fixture(rec)
 # Upper accessible launch task sources are also supported by real fixtures.
 for i,cx in enumerate([72,85.5]):fixture({'id':'launch_task_'+str(i),'xyz':[cx,51.1,194.4]})
 bpy.context.scene['source_plan_sha256']=hashlib.sha256((P/'docs/AQUATIC_CONSTRUCTION_PLAN.json').read_bytes()).hexdigest();bpy.context.scene['status']='Source architectural assembly only; all gameplay and host integration pending';bpy.context.scene.unit_settings.system='METRIC';bpy.context.view_layer.update()
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file:im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'source/aquatic_district.blend'))
 # World bounds and complete source vertex positions support independent exchange validation.
 evidence={}
 for o in A+F:
  if o.type!='MESH':continue
  dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];wv=[[v.x,v.z,-v.y] for v in vs]
  evidence[o.name]={'kind':o.get('kind'),'bounds_min':[min(v[a] for v in wv) for a in range(3)],'bounds_max':[max(v[a] for v in wv) for a in range(3)],'world_vertices_xyz':wv,'support_owner':o.get('support_owner')};e.to_mesh_clear()
 (P/'qa/source_geometry.json').write_text(json.dumps(evidence,separators=(',',':')))
 for filename,obs in [('AQD_architecture.glb',A),('AQD_floor_proposals.glb',F)]:
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(P/'exports'/filename),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
 (P/'qa/build_receipt.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'source_meshes':len(evidence),'architecture_objects':len(A),'separate_floor_objects':len(F),'native':'source/aquatic_district.blend','exports':['exports/AQD_architecture.glb','exports/AQD_floor_proposals.glb'],'host_writes':0,'origin':[0,0,0],'lights_modeled':len(D['lights'])+2},indent=2))
 print('Aquatic complete source assembly saved and both bounded exports created.')
if __name__=='__main__':build()
