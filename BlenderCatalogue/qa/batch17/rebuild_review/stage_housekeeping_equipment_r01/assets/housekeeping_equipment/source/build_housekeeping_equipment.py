"""Original editable D01 housekeeping equipment. Blender 4.3.2, metre Z-up/front -Y.
Inputs: this generator, original draw_controls.py and unchanged staff material helper/textures.
No existing generated geometry, manifest, QA report or host project is opened.
"""
import bpy,bmesh,json,math,hashlib,importlib.util,subprocess,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for p in ('source','exports','qa','actor_proxies'):(BASE/p).mkdir(parents=True,exist_ok=True)
# Draw originals on every production build, using system Python/Pillow; Blender has no Pillow requirement.
subprocess.run(['python3',str(BASE/'source/draw_controls.py')],check=True)
spec=importlib.util.spec_from_file_location('staff_materials',CAT/'standards/staff_materials.py');sm=importlib.util.module_from_spec(spec);spec.loader.exec_module(sm);MATS=sm.materials()
W='staff_white_paint';B='staff_bluegrey_paint';Z='staff_zinc';R='staff_rubber'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gl(p):return [float(p[0]),float(p[2]),-float(p[1])]
def local_material(role,file):
 im=bpy.data.images.load(str(BASE/'source'/file));im.pack();mat=bpy.data.materials.new('ASTRAEA_'+role);mat.use_nodes=True;mat['astraea_material_role']=role;mat['meters_per_tile_uv']=[.40,.10];bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82;tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);MATS[role]=mat
for role in('cloth_controls','rack_controls'):local_material(role,role+'.png')
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,VOIDS,MOVES,BEARINGS
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident
 PARTS=[];MARKERS=[];JOINS=[];VOIDS=[];MOVES={};BEARINGS=[];sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident;sc['scope']='Original unplaced housekeeping component; no operation, species fit, capacity, plumbing or game implementation'
def mesh(name,verts,faces,role=W,parent=None,body=True,omission=0):
 par=parent or ROOT;off=par.location if par!=ROOT else Vector((0,0,0));verts=[Vector(v)-off for v in verts];me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=par;me.materials.append(MATS[role]);ob['material_role']=role;ob['movement_group']=par.name if par!=ROOT else 'static';ob['body_candidate_keep']=body;ob['body_omission_max_distance_m']=omission;ob['authorship']='Original Batch17 folded housekeeping equipment';uv=me.uv_layers.new(name='metric_material_uv');sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3)if i!=axis]
  for li in f.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
 PARTS.append(ob);return ob
def box(n,lo,hi,r=W,parent=None,body=True,omission=0):
 x,y,z=lo;X,Y,Zz=hi;return mesh(n,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Zz),(X,y,Zz),(X,Y,Zz),(x,Y,Zz)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],r,parent,body,omission)
def ex(n,profile,axis,a,b,r=W,parent=None,body=True,omission=0):
 axes=[i for i in range(3)if i!=axis];v=[]
 for d in(a,b):
  for p in profile:
   q=[0,0,0];q[axis]=d;q[axes[0]]=p[0];q[axes[1]]=p[1];v.append(q)
 N=len(profile);return mesh(n,v,[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)],r,parent,body,omission)
def clip(x,X,y,Y,c):return[(x+c,y),(X-c,y),(X,y+c),(X,Y-c),(X-c,Y),(x+c,Y),(x,Y-c),(x,y+c)]
def rod(n,a,b,r,role=Z,N=8,parent=None,body=True,omission=0):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((1,0,0))if abs(d.x)<.9 else Vector((0,1,0))).normalized();v=d.cross(u);verts=[p+r*(u*math.cos(2*math.pi*i/N)+v*math.sin(2*math.pi*i/N))for p in(a,b)for i in range(N)];return mesh(n,verts,[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)],role,parent,body,omission)
def ring(n,cx,cz,ri,ro,y0,y1,role,parent=None,N=8):
 out=[]
 for i in range(N):
  a=2*math.pi*i/N;b=2*math.pi*(i+1)/N;p=[(cx+ri*math.cos(a),cz+ri*math.sin(a)),(cx+ro*math.cos(a),cz+ro*math.sin(a)),(cx+ro*math.cos(b),cz+ro*math.sin(b)),(cx+ri*math.cos(b),cz+ri*math.sin(b))];out.append(ex(n+'_'+str(i).zfill(2),p,1,y0,y1,role,parent))
 return out
def octagon(cx,cz,r):return[(cx+r*math.cos(2*math.pi*i/8),cz+r*math.sin(2*math.pi*i/8))for i in range(8)]
def move(n,p,kind,axis,travel,handling=False):
 ob=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob.location=p;ob['motion_type']=kind;ob['axis_source']=axis;ob['axis_gltf']=gl(axis);ob['travel_degrees_or_m']=travel;ob['support_scope']='detached hand-supported proposal'if handling else'retained geometric support, engineering unverified';MOVES[n]=ob;return ob
def marker(n,p,kind,part=None,normal=None,parent=None,desc=''):
 par=parent or ROOT;ob=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(ob);ob.parent=par;ob.location=Vector(p)-(par.location if par!=ROOT else Vector((0,0,0)));ob.empty_display_size=.012;bpy.context.view_layer.update();row={'name':n,'kind':kind,'source_m':list(p),'gltf_m':gl(p),'parent_local_source_m':list(ob.location),'physical_part':part.name if part else None,'parent_root':par.name,'description':desc}
 if normal:row.update(direction_source=normal,direction_gltf=gl(normal));ob['direction_source']=normal;ob['direction_gltf']=gl(normal)
 ob['marker_kind']=kind;ob['physical_part']=row['physical_part']or'';ob['source_position_m']=p;ob['gltf_position_m']=gl(p);ob['parent_local_source_m']=list(ob.location);ob['position_metadata_state']='true closed pose';MARKERS.append(row)
def joint(n,a,b,p,kind='boundary_contact'):
 JOINS.append({'name':n,'parts':[a.name if hasattr(a,'name')else a,b.name if hasattr(b,'name')else b],'probe_source_m':p,'probe_gltf_m':gl(p),'kind':kind})
def void(n,lo,hi,purpose,state='all'):
 VOIDS.append({'name':n,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':purpose,'state':state})
def label(n,lo,hi,role,parent=None):
 ob=box(n,lo,hi,role,parent);uv=ob.data.uv_layers.active;off=ob.parent.location if ob.parent!=ROOT else Vector((0,0,0))
 for f in ob.data.polygons:
  if f.normal.y<-.9:
   for li in f.loop_indices:
    c=ob.data.vertices[ob.data.loops[li].vertex_index].co+off;uv.data[li].uv=((c.x-lo[0])/(hi[0]-lo[0]),(c.z-lo[2])/(hi[2]-lo[2]))
 return ob
def grip(prefix,x0,x1,yfront,yback,z0,z1,parent=None):
 # Rear return and bridge meet at real boundaries, preserving central finger opening.
 br=box(prefix+'_bridge',[x0,yfront,z0],[x1,yfront+.020,z1],R,parent)
 for x,t in[(x0,'left'),(x1-.022,'right')]:
  ret=box(prefix+'_'+t+'_return',[x,yfront+.020,z0],[x+.022,yback,z1],Z,parent);joint(prefix+'_'+t+'_bridge',ret,br,[x+.011,yfront+.020,(z0+z1)/2])
 marker(prefix.upper()+'_CONTACT',[(x0+x1)/2,yfront,(z0+z1)/2],'physical_grip',br,[0,-1,0],parent)
 return br

def appliance():
 # Broad clipped plinth, cool folded panels and an eight-sided hollow loading chamber.
 for x,t in[(-.47,'left'),(.47,'right')]:
  sole=box(t+'_rubber_floor_runner',[x-.055,-.37,0],[x+.055,.35,.025],R);marker(t.upper()+'_FLOOR',[x,0,0],'physical_floor_contact',sole,[0,0,-1])
 base=ex('clipped_kick_plinth',clip(-.59,.59,-.44,.41,.055),2,.025,.15,B)
 for t,x in[('left',-.47),('right',.47)]:joint(t+'_runner_base',t+'_rubber_floor_runner',base,[x,0,.025])
 sideprofile=[(-.46,.15),(.42,.15),(.42,1.70),(-.31,1.70),(-.46,1.52)]
 sides=[]
 for x0,x1,t in[(-.60,-.57,'left'),(.57,.60,'right')]:
  ob=ex(t+'_folded_casing_side',sideprofile,0,x0,x1,W);sides.append(ob);joint(t+'_case_plinth',ob,base,[(x0+x1)/2,0,.15])
 lower=box('lower_front_pressed_apron',[-.57,-.46,.15],[.57,-.425,.61],W);joint('apron_plinth',lower,base,[0,-.43,.15])
 crown=box('upper_control_crown',[-.57,-.46,1.44],[.57,-.425,1.595],W)
 cap=ex('sloped_upper_fold',[(-.46,1.595),(-.425,1.575),(-.29,1.67),(-.31,1.70)],0,-.57,.57,W)
 roof=box('horizontal_upper_fold',[-.57,-.31,1.67],[.57,.42,1.70],W)
 for s,t in[(-1,'left'),(1,'right')]:joint(t+'_crown_side',crown,t+'_folded_casing_side',[s*.57,-.44,1.50])
 topback=box('rear_upper_structure',[-.57,.39,1.43],[.57,.42,1.67],B)
 bottomback=box('rear_lower_structure',[-.57,.39,.15],[.57,.42,.42],B);joint('rear_lower_plinth',bottomback,base,[0,.40,.15])
 for s,t in[(-1,'left'),(1,'right')]:
  stile=box(t+'_rear_service_stile',[s*.515-.055,.39,.42],[s*.515+.055,.42,1.43],B);joint(t+'_stile_side',stile,t+'_folded_casing_side',[s*.57,.40,.8])
 mouth=ring('formed_octagonal_chamber_mouth',0,1.03,.35,.48,-.48,-.430,Z)
 chamber=ring('real_chamber_wall',0,1.03,.35,.375,-.430,.285,Z)
 back=ex('chamber_back_plate',octagon(0,1.03,.375),1,.285,.310,B)
 for i in range(8):
  a=(i+.5)*math.pi/4;r=.3625*math.cos(math.pi/8);p=[r*math.cos(a),-.430,1.03+r*math.sin(a)];joint('chamber_mouth_'+str(i),chamber[i],mouth[i],p);joint('chamber_back_'+str(i),chamber[i],back,[p[0],.285,p[2]])
 # Rectangular return strips terminate at the outer mouth, without sealing its void.
 for s,t in[(-1,'left'),(1,'right')]:
  stile=box(t+'_front_case_return',[s*.525-.045,-.46,.61],[s*.525+.045,-.425,1.45],W);joint(t+'_front_return_side',stile,t+'_folded_casing_side',[s*.57,-.44,1.0]);joint(t+'_mouth_return',stile,mouth[0 if s>0 else 4],[s*.48,-.44,1.03])
 # Exact lower/upper physical support at centre radial tip, inside substantial overlap with apron/crown.
 joint('mouth_apron_tip',mouth[5],lower,[0,-.44,.55]);joint('mouth_crown_tip',mouth[1],crown,[0,-.44,1.50])
 ctrl=label('original_inactive_control_face',[-.24,-.466,1.475],[.24,-.46,1.575],'cloth_controls');joint('controls_crown',ctrl,crown,[0,-.46,1.50]);marker('INACTIVE_CONTROLS',[0,-.466,1.525],'physical_inactive_controls',ctrl,[0,-1,0])
 # Complete hatch carries its ring, opaque inspection centre, handle, straps and bearing sleeves.
 hatch=move('LOADING_HATCH_Z',[-.47,-.52,1.03],'rotation',[0,0,1],-105)
 rings=ring('hatch_pressed_ring',0,1.03,.295,.395,-.565,-.505,B,hatch)
 window=ex('opaque_inactive_inspection_inset',octagon(0,1.03,.295),1,-.560,-.510,R,hatch)
 for i in range(8):
  a=i*math.pi/4;joint('inspection_inset_ring_'+str(i),window,rings[i],[.295*math.cos(a),-.535,1.03+.295*math.sin(a)])
 pull=grip('hatch_pull',-.12,.12,-.645,-.565,1.330,1.370,hatch)
 for x,t in[(-.109,'left'),(.109,'right')]:joint('hatch_pull_ring_'+t,'hatch_pull_'+t+'_return',rings[2 if x<0 else 1],[x,-.565,1.35])
 for z0,z1,t in[(.680,.740,'lower'),(1.320,1.380,'upper')]:
  zmid=(z0+z1)/2
  bracketz=(.650,.675)if t=='lower'else(1.385,1.410)
  bracket=box(t+'_fixed_hinge_bracket',[-.59,-.55,bracketz[0]],[-.448,-.405,bracketz[1]],Z);joint(t+'_bracket_case',bracket,sides[0],[-.575,-.44,sum(bracketz)/2])
  pin=rod(t+'_retained_hinge_pin',[-.47,-.52,z0-.005],[-.47,-.52,z1+.005],.0105,Z,8,body=False,omission=.075)
  caps=[]
  for zz,tag in[(z0-.005,'lower'),(z1,'upper')]:caps.append(rod(t+'_'+tag+'_pin_retainer',[-.47,-.52,zz],[-.47,-.52,zz+.005],.020,Z,8,body=False,omission=.075))
  sleeves=[]
  for k in range(8):
   a=k*math.pi/4;b=(k+1)*math.pi/4;pr=[(-.47+r*math.cos(q),-.52+r*math.sin(q))for r,q in[(.012,a),(.024,a),(.024,b),(.012,b)]];sleeves.append(ex(t+'_bored_hinge_sleeve_'+str(k),pr,2,z0,z1,Z,hatch,False,.045))
  strap=box(t+'_hatch_retaining_strap',[-.454,-.534,zmid-.017],[-.14,-.506,zmid+.017],Z,hatch)
  joint(t+'_strap_sleeve',strap,sleeves[0],[-.450,-.514,zmid]);joint(t+'_strap_hatch',strap,rings[5 if t=='lower'else 2],[-.16,-.530,zmid])
  marker(t.upper()+'_HINGE_AXIS',[-.47,-.52,zmid],'nonphysical_bored_axis',None,None,hatch,'Axis through actual finite sleeve and retained pin')
  marker(t.upper()+'_AXIAL_BEARING',[-.454,-.518,z0],'physical_axial_bearing',sleeves[0],[0,0,-1],hatch)
  BEARINGS.append({'name':t+'_vertical_hatch_bearing','root':hatch.name,'pin':pin.name,'sleeves':[s.name for s in sleeves],'retainers':[s.name for s in caps],'fixed_support':bracket.name,'axis_source':[0,0,1],'pivot_source_m':[-.47,-.52,zmid],'sleeve_z_range':[z0,z1],'bore_circumradius_m':.012,'bore_inradius_m':.012*math.cos(math.pi/8),'pin_circumradius_m':.0105,'radial_clearance_min_m':.012*math.cos(math.pi/8)-.0105,'axial_retention_clearance_m':0,'status':'geometric retained journal only; no torque, wear, latch or load proof'})
 # Real reverse maintenance face, closed support and complete detached removal proposal.
 coverroot=move('REAR_SERVICE_COVER',[0,0,0],'translation',[0,1,0],.25,True)
 cover=box('removable_rear_service_cover',[-.46,.42,.42],[.46,.442,1.43],W,coverroot)
 for x,t in[(-.460,'left'),(.460,'right')]:joint(t+'_rear_cover_seat',cover,t+'_rear_service_stile',[x,.42,.90])
 # Rear bridge with actual returns; no reversed-use grip helper.
 bridge=box('rear_cover_pull_bridge',[-.10,.487,.85],[.10,.505,.90],R,coverroot)
 for x,t in[(-.10,'left'),(.078,'right')]:
  ret=box('rear_pull_'+t+'_return',[x,.442,.85],[x+.022,.487,.90],Z,coverroot);joint('rear_pull_'+t+'_cover',ret,cover,[x+.011,.442,.875]);joint('rear_pull_'+t+'_bridge',ret,bridge,[x+.011,.487,.875])
 marker('REAR_SERVICE_GRIP',[0,.505,.875],'physical_service_grip',bridge,[0,1,0],coverroot)
 # Original capped interfaces do not assign pipe size, chemical, voltage or pressure.
 for x,z,t in[(-.22,1.55,'left'),(.22,1.55,'right')]:
  cap=rod(t+'_unassigned_utility_cap',[x,.42,z],[x,.455,z],.040,Z,8);joint(t+'_cap_mount',cap,topback,[x,.42,z]);marker(t.upper()+'_CAPPED_UTILITY_FACE',[x,.455,z],'physical_unassigned_capped_utility_face',cap,[0,1,0],desc='Compatibility, plumbing and electrical use unassigned')
 marker('CHAMBER_BACK_SURFACE',[0,.285,1.03],'physical_chamber_back',back,[0,-1,0]);marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',desc='Floor datum between real runners')
 void('useful_loading_chamber',[-.22,-.42,.81],[.22,.28,1.25],'Whole rectangular witness inside actual octagonal chamber, no textile capacity or species fit')
 void('opened_loading_approach',[-.26,-1.05,.79],[.31,-.57,1.29],'Proposed front access after whole hatch opens; room/body fit unknown','LOADING_HATCH_Z_terminal')
 void('rear_service_clear_region',[-.42,.313,.48],[.42,.388,1.39],'Real space between chamber rear and rear service face; no operational equipment')
 void('hatch_grip_void',[-.092,-.620,1.335],[.092,-.570,1.365],'Actual opening behind the moving pull, no hand-fit claim','LOADING_HATCH_Z_local')
 void('rear_service_approach',[-.48,.77,.40],[.48,1.12,1.45],'Empty approach behind complete cover removal swept volume')
 return 'Faceted cloth-treatment appliance housing',{'chamber_inner_circumradius_m':.35,'chamber_inner_inradius_m':.35*math.cos(math.pi/8),'chamber_depth_m':.71,'appearance':'Folded white casing, real octagonal loading throat, opaque inactive inspection inset, supported hatch and separate reverse maintenance face','inactive_marking':'CLOTH / INACTIVE','temperature_airflow_treatment_power':'unimplemented; no substance or species compatibility','bearing_records':BEARINGS,'all_internal_part_containment':'Chamber eight-sided shell explicitly separated from rectangular outer casing; targeted whole-part containment required'}

def rack():
 # Open longitudinal rails and broad shallow hood. Distinct from storage cabinetry.
 for x,t in[(-.54,'left'),(.54,'right')]:
  sole=ex(t+'_floor_runner',clip(x-.06,x+.06,-.38,.38,.020),2,0,.032,R);marker(t.upper()+'_FLOOR',[x,0,0],'physical_floor_contact',sole,[0,0,-1])
  rail=box(t+'_lower_steel_sill',[x-.045,-.34,.032],[x+.045,.34,.095],Z);joint(t+'_sill_sole',rail,sole,[x,0,.032])
  for y,u in[(-.28,'front'),(.29,'rear')]:
   post=box(t+'_'+u+'_upright',[x-.027,y-.027,.095],[x+.027,y+.027,1.785],W);joint(t+'_'+u+'_post_sill',post,rail,[x,y,.095])
  side=box(t+'_upper_hood_tie',[x-.045,-.32,1.785],[x+.045,.34,1.825],Z)
  for y,u in[(-.28,'front'),(.29,'rear')]:joint(t+'_'+u+'_tie_post',side,t+'_'+u+'_upright',[x,y,1.785],'boundary_contact')
 brace=box('rear_lower_cross_tie',[-.54,.267,.20],[.54,.313,.25],Z)
 for x,t in[(-.54,'left'),(.54,'right')]:joint(t+'_rear_cross_tie',brace,t+'_rear_upright',[x,.29,.225],'buried_structural_overlap')
 # Hollow shallow faceted hood. The rear panel really opens the unassigned service volume.
 roof=box('hood_upper_skin',[-.60,-.29,1.960],[.60,.35,1.980],W)
 frontfold=ex('hood_forward_fold',[(-.37,1.915),(-.350,1.900),(-.277,1.960),(-.290,1.980)],0,-.60,.60,W)
 forehead=box('hood_control_forehead',[-.60,-.370,1.825],[.60,-.342,1.915],W)
 reartop=ex('hood_rear_upper_fold',[(.35,1.960),(.38,1.925),(.38,1.940),(.35,1.980)],0,-.60,.60,W)
 cheeks=[]
 for x0,x1,t in[(-.60,-.575,'left'),(.575,.60,'right')]:
  cheek=ex(t+'_hood_end_cheek',[(-.37,1.825),(-.37,1.915),(-.29,1.98),(.35,1.98),(.38,1.94),(.38,1.825)],0,x0,x1,W);cheeks.append(cheek);joint(t+'_hood_support',cheek,t+'_upper_hood_tie',[(-.580 if x0<0 else .580),0,1.825]);joint(t+'_hood_roof',cheek,roof,[(x0+x1)/2,0,1.970])
 rearbottom=box('hood_rear_lower_return',[-.575,.352,1.825],[.575,.380,1.839],Z)
 for x,t in[(-.46,'left'),(.46,'right')]:
  st=box(t+'_hood_service_stile',[x-.024,.352,1.839],[x+.024,.380,1.920],Z);joint(t+'_hood_stile_return',st,rearbottom,[x,.365,1.839])
 fascia=label('original_inactive_rack_control',[-.24,-.377,1.831],[.24,-.370,1.905],'rack_controls');joint('rack_controls_hood',fascia,forehead,[0,-.37,1.87]);marker('INACTIVE_CONTROLS',[0,-.377,1.868],'physical_inactive_controls',fascia,[0,-1,0])
 # Real tier carriers: seven transverse rectangular bars held by side stringers.
 for zz,t in[(.53,'lower'),(1.41,'upper')]:
  for x,s in[(-.51,'left'),(.51,'right')]:
   st=box(t+'_'+s+'_carrier_stringer',[x-.023,-.28,zz],[x+.023,.29,zz+.040],Z)
   for y,u in[(-.28,'front'),(.29,'rear')]:joint(t+'_'+s+'_'+u+'_stringer_post',st,s+'_'+u+'_upright',[x+(-.010 if x<0 else .010),y,zz+.020],'buried_structural_overlap')
  for i,y in enumerate([-.265,-.18,-.095,-.01,.075,.16,.245]):
   bar=box(t+'_textile_support_rail_'+str(i),[-.49,y-.014,zz+.016],[.49,y+.014,zz+.038],Z)
   for x,s in[(-.49,'left'),(.49,'right')]:joint(t+'_rail_'+str(i)+'_'+s,bar,t+'_'+s+'_carrier_stringer',[x,y,zz+.025])
  marker(t.upper()+'_LOAD_SUPPORT',[0,-.01,zz+.038],'physical_rail_support',t+'_textile_support_rail_3' if False else bar,[0,0,1]) if False else None
  marker(t.upper()+'_LOAD_SUPPORT',[0,-.01,zz+.038],'physical_rail_support',bpy.data.objects[t+'_textile_support_rail_3'],[0,0,1])
 # Middle sliding carrier has retained bottom/top guide channel on each side, no tiny bolt colliders.
 trayroot=move('MIDDLE_CARRIER_SLIDE',[0,0,0],'translation',[0,-1,0],.28)
 for x,s in[(-.51,'left'),(.51,'right')]:
  guide=box(s+'_fixed_carrier_bearing',[x-.030,-.28,.945],[x+.030,.32,.965],B)
  wall=box(s+'_fixed_carrier_outer_guide',[x+(.030 if x>0 else-.042),-.28,.965],[x+(.042 if x>0 else-.030),.32,1.038],B)
  top=box(s+'_fixed_carrier_retaining_lip',[x-.030,-.28,1.026],[x+.030,.32,1.038],B)
  for y,u in[(-.28,'front'),(.29,'rear')]:joint(s+'_'+u+'_guide_post',guide,s+'_'+u+'_upright',[x+(-.010 if x<0 else .010),y,.954],'buried_structural_overlap')
  joint(s+'_guide_wall',guide,wall,[x+(.030 if x>0 else-.030),0,.965]);joint(s+'_wall_retaining_lip',wall,top,[x+(.030 if x>0 else-.030),0,1.026])
  mx=x+(.016 if x<0 else-.016)
  runner=box(s+'_moving_carrier_runner',[mx-.011,-.32,.965],[mx+.011,.32,.990],Z,trayroot)
  stringer=box(s+'_moving_carrier_edge',[mx-.014,-.32,.990],[mx+.014,.30,1.010],Z,trayroot);joint(s+'_runner_edge',runner,stringer,[mx,0,.990])
  marker(s.upper()+'_SLIDE_BEARING',[mx,0,.965],'physical_retained_sliding_bearing',runner,[0,0,-1],trayroot)
  BEARINGS.append({'name':s+'_retained_linear_carrier','root':trayroot.name,'runner':runner.name,'bearing':guide.name,'retaining_lip':top.name,'outer_guide':wall.name,'axis_source':[0,-1,0],'travel_m':.28,'closed_runner_y':[-.32,.32],'fixed_bearing_y':[-.28,.32],'terminal_overlap_y':[-.28,.04],'terminal_overlap_m':.32,'minimum_vertical_retaining_clearance_m':.016,'status':'geometric bearing/retention only; no load, latch, stop or sliding-friction validation'})
 for i,y in enumerate([-.300,-.205,-.110,-.015,.080,.175,.270]):
  bar=box('moving_textile_support_rail_'+str(i),[-.492,y-.014,.985],[.492,y+.014,1.007],Z,trayroot)
  for x,s in[(-.492,'left'),(.492,'right')]:joint('moving_rail_'+str(i)+'_'+s,bar,s+'_moving_carrier_edge',[x,y,.998])
 front=box('moving_carrier_front_tie',[-.51,-.338,.965],[.51,-.320,1.020],Z,trayroot)
 for x,s in[(-.51,'left'),(.51,'right')]:joint(s+'_moving_front_tie',front,s+'_moving_carrier_runner',[x+(.016 if x<0 else-.016),-.32,.98])
 br=grip('carrier_pull',-.17,.17,-.430,-.338,.972,1.020,trayroot)
 for x,t in[(-.159,'left'),(.159,'right')]:joint('carrier_pull_'+t+'_tie','carrier_pull_'+t+'_return',front,[x,-.338,.995])
 marker('MIDDLE_LOAD_SUPPORT',[0,-.015,1.007],'physical_rail_support',bpy.data.objects['moving_textile_support_rail_3'],[0,0,1],trayroot)
 # Rear maintenance cassette is already part of hood volume, removed as hand-supported part.
 service=move('HOOD_REAR_SERVICE',[0,0,0],'translation',[0,1,0],.20,True)
 panel=box('hood_rear_removable_panel',[-.46,.380,1.839],[.46,.396,1.935],B,service);joint('hood_service_panel_seat',panel,rearbottom,[0,.380,1.839])
 for x,t in[(-.45,'left'),(.45,'right')]:joint(t+'_hood_panel_stile',panel,t+'_hood_service_stile',[x,.380,1.88])
 marker('HOOD_SERVICE_FACE',[0,.396,1.90],'physical_service_panel',panel,[0,1,0],service)
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',desc='Floor datum between runner soles')
 void('lower_open_textile_zone',[-.46,-.26,.58],[.46,.26,.92],'Actual open volume above lower tier; no drying capacity or cloth compatibility')
 void('middle_open_textile_zone',[-.46,-.26,1.05],[.46,.26,1.39],'Actual open volume above middle carrier; whole sliding root clears this volume')
 void('hood_real_service_volume',[-.42,-.29,1.842],[.42,.375,1.930],'Unassigned hollow service volume opened by the real rear cover; no powered components')
 void('upper_open_textile_zone',[-.46,-.26,1.46],[.46,.26,1.78],'Open volume below supported hood; airflow and heat unimplemented')
 void('carrier_grip_void',[-.140,-.407,.978],[.140,-.343,1.013],'Open volume behind moving grip bridge','MIDDLE_CARRIER_SLIDE_local')
 void('front_retrieval_approach',[-.48,-1.12,.53],[.48,-.73,1.75],'Clear front region beyond complete carrier/pull sweep')
 return 'Open tier drying and conditioning rack',{'appearance':'Open three-tier supported textile rails, shallow faceted hood, one retained sliding carrier','inactive_marking':'RACK / INACTIVE','bearing_records':BEARINGS,'hood_scope':'Hollow proposed housing; no fan, airflow, heat, UV, ventilation or electrical implementation','fabric_support':'No floating cloth; useful rail tops and clear volume only','species_compatibility':'Unassigned for all six species'}

def geometry():
 bpy.context.view_layer.update();parts=[];pts=[];tri=0
 for ob in PARTS:
  me=ob.data;me.calc_loop_triangles();vs=[list(ob.matrix_world@v.co)for v in me.vertices];ts=[list(t.vertices)for t in me.loop_triangles];parts.append({'name':ob.name,'parent':ob.parent.name,'movement_group':ob['movement_group'],'vertices':vs,'triangles':ts,'material_role':ob['material_role'],'body_candidate_keep':ob['body_candidate_keep'],'body_omission_max_distance_m':ob['body_omission_max_distance_m']});pts+=vs;tri+=len(ts)
 lo=[min(p[i]for p in pts)for i in range(3)];hi=[max(p[i]for p in pts)for i in range(3)];return parts,{'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(ident,suffix=''):
 out=[];groups={}
 for ob in PARTS:
  me=ob.data.copy();cp=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(cp);cp.matrix_world=ob.matrix_world.copy();groups.setdefault((ob.parent.name,ob['material_role']),[]).append(cp)
 for (parent,role),obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+('static'if parent==ident else parent)+'__'+role;w=ob.matrix_world.copy();ob.parent=bpy.data.objects[parent];ob.matrix_world=w;ob['material_role']=role;ob['semantic_parts']=json.dumps([o.name for o in PARTS if o.parent.name==parent and o['material_role']==role]);out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for o in list(MOVES.values())+out+[bpy.data.objects[m['name']]for m in MARKERS]:o.select_set(True)
 bpy.context.view_layer.objects.active=ROOT;bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}{suffix}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
def setmotion(ob,t):
 if ob['motion_type']=='rotation':ob.rotation_euler=Vector(ob['axis_source'])*math.radians(t)
 else:ob.location=Vector(ob.get('original_pivot',[0,0,0]))+Vector(ob['axis_source'])*t
 bpy.context.view_layer.update()
def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];collision={};body={};api={};dumps={}
 for ident,fn in[('AST-HSK-001',appliance),('AST-HSK-002',rack)]:
  reset(ident);title,details=fn();parts,bb,tri=geometry();motions=[]
  for name,m in MOVES.items():
   m['original_pivot']=list(m.location);motions.append({'root':name,'kind':m['motion_type'],'pivot_source_m':list(m.location),'pivot_gltf_m':gl(m.location),'axis_source':list(m['axis_source']),'axis_gltf':list(m['axis_gltf']),'travel':m['travel_degrees_or_m'],'initial_pose':0,'support_scope':m['support_scope'],'semantic_parts':[p['name']for p in parts if p['parent']==name]})
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident);states=[]
  for m in MOVES.values():
   setmotion(m,m['travel_degrees_or_m']);_,sb,_=geometry();suffix='_hatch_open'if m.name=='LOADING_HATCH_Z'else('_retrieval'if m.name=='MIDDLE_CARRIER_SLIDE'else'_service_open');export(ident,suffix);states.append({'name':m.name+'_terminal','root':m.name,'export':f'exports/{ident}{suffix}.glb','travel':m['travel_degrees_or_m'],'support_scope':m['support_scope'],'bounds_source':sb,'glb_sha256':sha(BASE/'exports'/f'{ident}{suffix}.glb')});setmotion(m,0)
  # Full occupied sweeps are computed by continuous-bound QA, not mislabelled empty voids.
  roles=sorted({p['material_role']for p in parts});groups=sorted({(p['parent'],p['material_role'])for p in parts});lo,hi=bb['min_m'],bb['max_m'];rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_housekeeping_equipment.py','source_frame':'metres Blender XYZ Z-up front -Y','exchange_frame':'metres native GLB Y-up source(x,y,z)->(x,z,-y)','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'floor between supported runners'},'bounds_blender_z_up':bb,'bounds_gltf_y_up':{'min_m':[lo[0],lo[2],-hi[1]],'max_m':[hi[0],hi[2],-lo[1]],'dimensions_m':[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]},'dimensions_blender_xyz_m':bb['dimensions_m'],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(parts),'semantic_parts':[p['name']for p in parts],'material_roles':roles,'export_mesh_groups':len(groups),'export_group_ownership':groups,'physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'motion_records':motions,'state_derivatives':states,'collision_proposal_file':'collision_proposals.json','body_candidate_file':'actor_proxies/body_collision_subset.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Original host absent; no new room, position, machinery quantity or game implementation','D01 laundry and separate custodial depot remain historical allocation records; no proved connection','No six-species reach, body, textile/substance compatibility, capacity, plumbing, operating cycle or cleaning/drying effectiveness','No load, stability, bearing-life, latch, electrical, heat, hygiene certification or collision-engine/target-PC acceptance']};rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n')
  shapes=[{'name':p['name']+'_precise_profile','type':'convex_hull_points','points_source_m':p['vertices'],'points_gltf_m':[gl(v)for v in p['vertices']],'covered_parts':[p['name']],'parent_root':p['parent'],'movement_group':p['movement_group'],'allowed_inflation_m':0,'allowed_omission_m':0,'status':'Exact convex semantic solid; finite mesh source, unadopted mechanism/reference proposal'}for p in parts]
  collision[ident]={'source_frame':'metres source Z-up true closed pose','exchange_frame':'metres native GLB Y-up','shapes':shapes,'motion_records':motions,'preserve_voids':VOIDS,'omitted_semantic_parts':[],'limits':'Precise reference compound, not claimed economical runtime collision; no enclosing hull'}
  body[ident]={'source_frame':'metres source Z-up true closed pose','exchange_frame':'metres native GLB Y-up','derivation_stage':'literal subset selected during original build; no new enclosing hull','shapes':[s for s,p in zip(shapes,parts)if p['body_candidate_keep']],'omitted_parts':[{'part':p['name'],'maximum_distance_to_retained_body_m':p['body_omission_max_distance_m'],'reason':'Fine retained hinge sleeve/pin/cap stays in precise mechanism set; not a separate broad body hull'}for p in parts if not p['body_candidate_keep']],'added_inflation_m':0,'preserve_voids':VOIDS,'motion_records':motions,'fine_contacts_retained_in':'../collision_proposals.json and ../marker_api.json','status':'Optional conservative geometric candidate; target engine/body tests pending'}
  api[ident]=MARKERS;dumps[ident]={'parts':parts,'markers':MARKERS,'voids':VOIDS,'joins':JOINS,'motion_records':motions}
 (BASE/'manifest.json').write_text(json.dumps({'family':'housekeeping_equipment','revision':'housekeeping-equipment-01','unique_designs':2,'assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(collision,indent=2)+'\n');(BASE/'actor_proxies/body_collision_subset.json').write_text(json.dumps(body,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n');(BASE/'qa/authored_geometry.json').write_text(json.dumps(dumps))
 deps=[Path(__file__),BASE/'source/draw_controls.py',CAT/'standards/staff_materials.py',CAT/'materials/staff/manifest.json'];deps.extend(CAT/'materials/staff'/v['file']for v in json.loads((CAT/'materials/staff/manifest.json').read_text())['materials'].values());(BASE/'dependency_manifest.json').write_text(json.dumps({'schema':'housekeeping_equipment_exact_source_inputs_v1','inputs':[{'path_from_catalogue_root':str(p.relative_to(CAT)),'sha256':sha(p)}for p in deps],'count':len(deps),'regenerated_original_art':['source/cloth_controls.png','source/rack_controls.png'],'closure_note':'Exact source inputs only. Generator always redraws original encoded glyph art, reads unchanged staff helper/manifest and all nine loaded staff textures; no old generated source/export, art or QA seed.'},indent=2)+'\n')
 print('HOUSEKEEPING_EQUIPMENT_BUILT',[(r['catalogue_id'],r['evaluated_triangles'],r['export_mesh_groups'],r['dimensions_blender_xyz_m'])for r in rows])
if __name__=='__main__':main()
