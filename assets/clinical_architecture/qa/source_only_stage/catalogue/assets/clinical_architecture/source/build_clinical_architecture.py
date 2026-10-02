"""Original editable D05 clinical architecture proposals. Blender 4.3.2, metres.
All authored geometry and motion in this file; textures are original deterministic sources.
Usage: python source/make_clinical_textures.py; blender -b -t 2 --python-exit-code 1 --python source/build_clinical_architecture.py
"""
import bpy,bmesh,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
for name in ('source','exports','qa'):(BASE/name).mkdir(parents=True,exist_ok=True)
CAT=BASE.parents[1]
MATS={}
for helper in ('materials','care_materials'):
 spec=importlib.util.spec_from_file_location('clinical_'+helper,CAT/'standards'/f'{helper}.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);MATS.update(mod.materials())
MM=json.loads((BASE/'material_manifest.json').read_text())['materials']
for role,r in MM.items():
 m=bpy.data.materials.new('ASTRAEA_'+role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=r['roughness'];bs.inputs['Metallic'].default_value=r['metallic']
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BASE/r['base_color_file']),check_existing=True);tex.image.pack();tex.interpolation='Linear';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m['astraea_material_role']=role;m['meters_per_tile_uv']=r['meters_per_tile_uv'];MATS[role]=m

def glb(p):return [p[0],p[2],-p[1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds_pair(lo,hi):return {'min_source_m':list(lo),'max_source_m':list(hi),'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]}
def reset(ident):
 global PARTS,MARKERS,JOINS,COLL,VOIDS,ROOT,MOTION,PARENT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[];MOTION=None
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);PARENT=ROOT
 ROOT['catalogue_id']=ident;ROOT['scope']='Fictional care component; no active treatment, species fit, host fit or load approval'
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.frame_set(1);sc['catalogue_id']=ident

def uvmap(me,role):
 uv=me.uv_layers.active or me.uv_layers.new(name='metric_material_uv');uv.name='metric_material_uv';uv.active_render=True;scale=MATS[role]['meters_per_tile_uv'];sx,sy=(scale,scale)if isinstance(scale,(float,int))else scale
 for f in me.polygons:
  n=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3)if i!=n]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)

def mesh(name,vs,fs,role='ivory_enamel',bevel=0):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=PARENT;ob['material_role']=role;ob['provenance']='Original D05 script-assisted care form';me.materials.append(MATS[role]);uvmap(me,role)
 if bevel:
  mo=ob.modifiers.new('Editable edge easing','BEVEL');mo.width=bevel;mo.segments=2;mo.limit_method='ANGLE';mo.angle_limit=math.radians(35)
  mo=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');mo.keep_sharp=True
 PARTS.append(ob);return ob

def box(name,c,d,role='ivory_enamel',bevel=.003):
 x,y,z=c;a,b,h=[v/2 for v in d]
 return mesh(name,[(x+i*a,y+j*b,z+k*h)for i,j,k in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)

def extrude(name,profile,axis,a,b,role='ivory_enamel',bevel=0):
 axes=[i for i in range(3)if i!=axis];vs=[]
 for d in(a,b):
  for p in profile:
   v=[0,0,0];v[axis]=d;v[axes[0]]=p[0];v[axes[1]]=p[1];vs.append(v)
 n=len(profile);return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,bevel)

def rounded(w,d,r,cx=0,cy=0):
 out=[]
 for x,y,s in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for i in range(4):
   t=math.radians(s+i*30);out.append((cx+x+r*math.cos(t),cy+y+r*math.sin(t)))
 return out

def rod(name,a,b,r,role='care_brushed_metal',n=12):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();s=Vector((1,0,0))if abs(d.x)<.9 else Vector((0,1,0));u=d.cross(s).normalized();v=d.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n))for p in(a,b)for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role)

def ring_x(name,c,length,rin,rout):
 x,y,z=c;vs=[];n=16
 for xx,rad in[(x-length/2,rout),(x+length/2,rout),(x-length/2,rin),(x+length/2,rin)]:
  vs.extend((xx,y+rad*math.cos(i*2*math.pi/n),z+rad*math.sin(i*2*math.pi/n))for i in range(n))
 fs=[]
 for i in range(n):
  j=(i+1)%n;fs.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
 return mesh(name,vs,fs,'dark_rubber')

def label(name,text,c,size,role='clinical_ink'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0015;cu.resolution_u=2
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.location=c;ob.rotation_euler=(math.pi/2,0,0);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.parent=PARENT
 # Bake local transform into vertices; text is intentional raised solid with rear bearing.
 for v in ob.data.vertices:v.co=ob.matrix_basis@v.co
 ob.matrix_basis.identity();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob.data.materials.append(MATS[role]);ob['material_role']=role;uvmap(ob.data,role);PARTS.append(ob);ob.select_set(False);return ob

def marker(name,p,kind,part=None,normal=None,desc='',moving=False):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=MOTION if moving else ROOT;o.location=p;o.empty_display_size=.025;o['marker_kind']=kind;o['frame']='source metres XYZ Z-up'
 row={'name':name,'kind':kind,'source_m':list(p),'gltf_m':glb(p),'physical_part':part,'description':desc,'moving_with_screen':moving}
 if normal:row.update(normal_source=list(normal),normal_gltf=glb(normal));o['normal_source']=normal;o['normal_gltf']=glb(normal)
 if moving:row.update(open_source_m=[p[0]-1.16,p[1],p[2]],open_gltf_m=glb([p[0]-1.16,p[1],p[2]]))
 o['source_position_m']=p;o['gltf_position_m']=glb(p);o['physical_part']=part or '';MARKERS.append(row);return o

def joint(name,a,b,p,na,nb):JOINS.append({'name':name,'parts':[a,b],'probe_source_m':p,'probe_gltf_m':glb(p),'normal_a_source':na,'normal_b_source':nb,'normal_a_gltf':glb(na),'normal_b_gltf':glb(nb),'kind':'opposed physical surface witness'})
def cbox(name,lo,hi,moving=False):COLL.append(dict(name=name,type='box',moving_with_screen=moving,**bounds_pair(lo,hi)))
def chull(name,pts,moving=False):COLL.append({'name':name,'type':'convex_hull_points','points_source_m':pts,'points_gltf_m':[glb(p)for p in pts],'moving_with_screen':moving})
def void(name,lo,hi,purpose,state='all'):VOIDS.append(dict(name=name,state=state,purpose=purpose,**bounds_pair(lo,hi)))

def privacy():
 global PARENT,MOTION
 for x,s in[(-1.32,'left'),(1.32,'right')]:
  foot=extrude(s+'_splayed_contact_foot',rounded(.10,.80,.045,x,.05),2,0,.045,'dark_rubber')
  post=extrude(s+'_rounded_support_post',[(x-.04,.045),(x+.04,.045),(x+.04,2.30),(x+.022,2.36),(x-.022,2.36),(x-.04,2.30)],1,.055,.155,'ivory_enamel')
  marker(s.upper()+'_FLOOR_CONTACT',[x,.05,0],'physical_floor_contact',foot.name,[0,0,-1])
  joint(s+'_post_to_foot',post.name,foot.name,[x,.10,.045],[0,0,-1],[0,0,1])
  cbox(s+'_foot',[x-.05,-.35,0],[x+.05,.45,.045]);cbox(s+'_post',[x-.04,.055,.045],[x+.04,.155,2.36])
 # Fixed wall is behind the parallel sliding field; narrow return nose remains outside full stroke.
 ret=extrude('fixed_quiet_arrival_return',rounded(1.220,2.06,.055,-.635,1.19),1,.235,.300,'care_bluegreen_resin')
 nose=box('left_rounded_return_nose',(-1.2625,.095,1.19),(.035,.41,2.06),'ivory_enamel',.009)
 for z,s in[(.30,'lower'),(2.10,'upper')]:
  box(s+'_return_support_bracket',(-1.30,.20,z),(.12,.09,.09),'ivory_enamel',.002)
 # Coarse direction and care title are on a physically terminated relief plaque, not coplanar decals.
 plaque=box('care_arrival_relief_plaque',(-.65,.224,1.62),(.73,.022,.33),'ivory_enamel',.005)
 label('care_title','CARE',(-.65,.2115,1.66),.125)
 label('care_quiet_subtitle','QUIET',(-.65,.2115,1.53),.054)
 joint('plaque_to_fixed_return',plaque.name,ret.name,[-.65,.235,1.62],[0,1,0],[0,-1,0])
 cbox('fixed_return',[-1.245,.235,.16],[-.025,.30,2.22]);cbox('fixed_return_nose',[-1.28,-.11,.16],[-1.245,.30,2.22]);cbox('arrival_plaque',[-1.015,.208,1.455],[-.285,.235,1.785])
 rail=rod('continuous_exposed_slider_rod',(-1.28,.095,2.29),(1.28,.095,2.29),.020,'care_brushed_metal',16)
 for x,s in[(-1.26,'left'),(1.26,'right')]:
  # Stop collars lie outside the total moving sleeve span.
  rod(s+'_rod_stop',(x-.012,.095,2.29),(x+.012,.095,2.29),.028,'dark_rubber',16)
  marker(s.upper()+'_ROD_END_BEARING',[(-1.28 if x<0 else 1.28),.095,2.29],'physical_bearing_axis',rail.name,[(-1 if x<0 else 1),0,0],desc='End bearing into actual post, no load rating')
 cbox('overhead_rod_and_stops',[-1.28,.067,2.262],[1.28,.123,2.318])
 MOTION=bpy.data.objects.new('SCREEN_TRANSLATION',None);bpy.context.collection.objects.link(MOTION);MOTION.parent=ROOT;MOTION['joint_type']='bounded prismatic visual proposal';MOTION['axis_source']=[1,0,0];MOTION['axis_gltf']=[1,0,0];MOTION['closed_translation_source']=[0,0,0];MOTION['open_translation_source']=[-1.16,0,0];MOTION['open_translation_gltf']=[-1.16,0,0];PARENT=MOTION
 slab=extrude('opaque_sliding_privacy_field',rounded(1.20,2.0,.036,.54,1.18),1,.055,.115,'privacy_sage')
 for x,s in[(.08,'left'),(1.00,'right')]:
  ring_x(s+'_annular_slider_sleeve',(x,.095,2.29),.075,.0215,.034)
  box(s+'_screen_hanger',(x,.095,2.221),(.043,.037,.086),'care_brushed_metal',.003)
  marker(s.upper()+'_SLIDER_AXIS',[x,.095,2.29],'nonphysical_joint_axis_center',None,[1,0,0],'Centre lies inside actual sleeve bore; separate from bearing surface',True)
  marker(s.upper()+'_SLEEVE_INNER_BEARING',[x,.09911382,2.2693185],'physical_inner_bearing_surface',s+'_annular_slider_sleeve',[0,-.195090322,.980785280],'Declared 1.5mm radial design gap to rod, no solved mechanical bearing',True)
  cbox(s+'_hanger',[x-.022,.0765,2.178],[x+.022,.1135,2.264],True)
  cbox(s+'_sleeve',[x-.0375,.061,2.256],[x+.0375,.129,2.324],True)
 # A low and high return on one grasp rail allow a visible open space behind the grip.
 for z,s in[(1.07,'lower'),(1.34,'upper')]:
  rod('handle_'+s+'_standoff',(1.045,.055,z),(1.045,-.024,z),.018,'care_brushed_metal')
 grip=rod('privacy_continuous_pull_grip',(1.045,-.024,1.07),(1.045,-.024,1.34),.020,'dark_rubber')
 marker('PRIVACY_PULL_CONTACT',[1.040,-.042660254,1.20],'physical_grip_surface',grip.name,[-.258819045,-.965925826,0],'Static contact proposal; no specified hand size or accessibility certification',True)
 marker('SCREEN_CONTROL_PROPOSAL',[.54,-.25,1.2],'nonphysical_interaction_proposal',None,[0,-1,0],'Candidate interaction location separate from physical grip; no engine action implemented',True)
 box('privacy_raised_semantic_band',(.47,.043,1.68),(.62,.024,.16),'ivory_enamel',.009)
 label('privacy_label','PRIVACY',(.47,.0295,1.68),.078)
 joint('moving_band_to_screen','privacy_raised_semantic_band',slab.name,[.47,.055,1.68],[0,1,0],[0,-1,0])
 cbox('sliding_opaque_field',[-.06,.055,.18],[1.14,.115,2.18],True);cbox('pull_assembly',[1.025,-.044,1.05],[1.065,.055,1.36],True);cbox('moving_semantic_band',[.16,.027,1.60],[.78,.055,1.76],True)
 PARENT=ROOT
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',None,[0,0,1])
 marker('APPROACH_EYE_STANDING',[.55,-1.25,1.60],'nonphysical_eye_proposal',None,[0,1,0],'Component test camera/eye only, no actor/species standard')
 marker('APPROACH_EYE_SEATED',[.55,-1.25,1.12],'nonphysical_eye_proposal',None,[0,1,0],'Component test camera/eye only, no actor/species standard')
 void('front_approach_air',[-1.15,-.33,.05],[1.15,-.08,2.15],'Unoccupied strip in front of screen/grip, no reserved host route')
 void('open_right_field',[.06,.01,.22],[1.17,.22,2.14],'Open-state field at right; feet/posts remain outside this finite proposal','open')
 void('fixed_to_moving_parallel_clearance',[-1.20,.14,.22],[-.04,.205,2.15],'Real nesting air between parallel screen and fixed return','all')
 MOTION.location=(0,0,0);MOTION.keyframe_insert('location',frame=1);MOTION.location=(-1.16,0,0);MOTION.keyframe_insert('location',frame=117)
 for fc in MOTION.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 bpy.context.scene.frame_end=117;bpy.context.scene.frame_set(1)
 return 'Controllable opaque privacy and arrival return',{'purpose':'Lateral privacy field beside an approach, never an inferred host door','mechanism':'Two annular sleeves on one exposed supported rod, rigid hanging screen slides left in front of the fixed arrival return','motion':{'node':'SCREEN_TRANSLATION','source_axis':[1,0,0],'gltf_axis':[1,0,0],'closed_translation_source_m':[0,0,0],'open_translation_source_m':[-1.16,0,0],'closed_translation_gltf_m':[0,0,0],'open_translation_gltf_m':[-1.16,0,0],'frames':{'1':'closed','117':'open'},'travel_m':1.16,'derivatives_count_as_designs':False,'mechanical_status':'Visual kinematic proposal only; bearings, locks, end damping and load remain unsolved'},'privacy_limit':'Only finite declared frontal and oblique component rays are tested; open edges and top prevent whole-room confidentiality claims'}

def basin_counter():
 outer=rounded(1.60,.76,.085,0,0);inner=rounded(.78,.46,.10,-.31,-.045);bottom=rounded(.56,.29,.080,-.31,-.045);under=rounded(.62,.35,.088,-.31,-.045);underlip=rounded(.84,.52,.10,-.31,-.045);n=len(outer)
 vs=[(x,y,z)for loop,z in[(outer,.94),(inner,.94),(bottom,.755),(under,.724),(outer,.88),(underlip,.88)]for x,y in loop]
 fs=[]
 for a,b in[(0,1),(1,2),(3,5),(5,4),(4,0)]:
  for i in range(n):j=(i+1)%n;fs.append((a*n+i,a*n+j,b*n+j,b*n+i))
 fs += [tuple(2*n+i for i in range(n)),tuple(reversed([3*n+i for i in range(n)]))]
 return mesh('continuous_shaped_basin_and_dry_work_rim',vs,fs,'ivory_enamel')

def wash():
 # Sculpted side cheeks support the rim and delineate actual service/retrieval spaces.
 for x,s in[(-.75,'left'),(.75,'right')]:
  prof=[(-.27,.04),(.29,.04),(.35,.11),(.35,.88),(-.31,.88),(-.34,.78),(-.28,.70),(-.24,.18)]
  o=extrude(s+'_swept_basin_support_cheek',prof,0,x-.035,x+.035,'care_bluegreen_resin')
  shoe=box(s+'_floor_isolation_shoe',(x,.02,.02),(.075,.54,.04),'dark_rubber',.003)
  marker(s.upper()+'_FLOOR_CONTACT',[x,.02,0],'physical_floor_contact',shoe.name,[0,0,-1])
  joint(s+'_cheek_to_shoe',o.name,shoe.name,[x,.02,.04],[0,0,-1],[0,0,1])
  chull(s+'_profiled_cheek',[[xx,y,z]for xx in(x-.0375,x+.0375)for y,z in prof]);cbox(s+'_shoe',[x-.0375,-.25,0],[x+.0375,.29,.04])
 back=box('rear_service_bearing_wall',(0,.325,.48),(1.43,.05,.80),'care_bluegreen_resin',.003)
 lower=box('lower_service_and_supply_floor',(0,.015,.125),(1.43,.57,.05),'ivory_enamel',.003)
 divide=box('basin_service_supply_divider',(.205,.01,.495),(.045,.58,.69),'care_bluegreen_resin',.003)
 rim=basin_counter()
 joint('rim_to_left_cheek',rim.name,'left_swept_basin_support_cheek',[-.75,.10,.88],[0,0,-1],[0,0,1]);joint('rim_to_right_cheek',rim.name,'right_swept_basin_support_cheek',[.75,.10,.88],[0,0,-1],[0,0,1]);joint('rim_to_rear_bearing',rim.name,back.name,[.50,.325,.88],[0,0,-1],[0,0,1])
 cbox('rear_service_bearing',[-.715,.30,.08],[.715,.35,.88]);cbox('lower_floor',[-.715,-.27,.10],[.715,.30,.15]);cbox('service_supply_divider',[.1825,-.28,.15],[.2275,.30,.84])
 # Unimplemented front-removable service cover, intentionally proud and bounded by a reveal.
 cover=box('front_removable_service_cover',(-.2675,-.2775,.43),(.865,.025,.49),'ivory_enamel',.012)
 for x in(-.65,.10):
  for z in(.235,.625):rod('service_cover_retainer_'+str(x)+'_'+str(z),(x,-.290,z),(x,-.296,z),.009,'care_brushed_metal',10)
 handle=box('service_cover_recess_grip',(-.2675,-.295,.58),(.17,.010,.031),'dark_rubber',.004)
 label('service_cover_semantics','SERVICE',(-.2675,-.2915,.36),.067)
 marker('SERVICE_COVER_CONTACT',[-.2675,-.300,.58],'physical_grip_surface',handle.name,[0,-1,0],'Cover requires removal before interior access; no hinge/sweep or opening behavior implemented')
 marker('SERVICE_WITHDRAWAL',[-.27,-.58,.44],'nonphysical_service_approach',None,[0,-1,0],'Proposed front cover removal, no actual maintenance/tool or isolation acceptance')
 cbox('front_service_cover',[-.70,-.301,.185],[.165,-.265,.675])
 # Small supply bay underneath the dry landing: no collider fills either actual mouth.
 shelf=box('lower_clean_supply_shelf',(.4725,.025,.47),(.49,.51,.038),'ivory_enamel',.003)
 cbox('lower_supply_shelf',[.2275,-.23,.451],[.7175,.28,.489])
 void('lower_supply_retrieval_low',[.255,-.30,.17],[.68,.27,.43],'Finite actual lower front-access shelf volume')
 void('lower_supply_retrieval_high',[.255,-.30,.515],[.68,.26,.80],'Finite actual upper front-access shelf volume')
 # Tower is intentionally right of the wet bowl: two open shelves, finished angled canopy.
 for x,s in[(.28,'inner'),(.75,'outer')]:
  p=[(.08,.94),(.36,.94),(.36,1.61),(.144,1.61),(.104,1.555),(.08,1.555)]
  extrude('clean_supply_'+s+'_tower_cheek',p,0,x-.018,x+.018,'care_bluegreen_resin')
  chull('clean_supply_'+s+'_cheek',[[xx,y,z]for xx in(x-.018,x+.018)for y,z in p])
 box('clean_supply_tower_back',(.515,.345,1.275),(.434,.03,.67),'care_bluegreen_resin',.002)
 cbox('clean_tower_back',[.298,.33,.94],[.732,.36,1.61])
 for z,s in[(.985,'lower'),(1.235,'middle')]:
  o=box('clean_supply_'+s+'_shelf',(.515,.215,z),(.434,.23,.030),'ivory_enamel',.003)
  cbox('clean_supply_'+s+'_shelf',[.298,.10,z-.015],[.732,.33,z+.015])
  marker('CLEAN_'+s.upper()+'_SUPPORT',[.515,.215,z+.015],'physical_storage_surface',o.name,[0,0,1],'Clean supply designation is fictional organization; no contents or sterility claim')
 cap=extrude('clean_supply_shelter_cap',[(.08,1.57),(.13,1.64),(.36,1.64),(.36,1.61),(.144,1.61),(.104,1.555)],0,.262,.768,'ivory_enamel')
 chull('clean_supply_cap',[[x,y,z]for x in(.262,.768)for y,z in[(.08,1.57),(.13,1.64),(.36,1.64),(.36,1.61),(.144,1.61),(.104,1.555)]])
 band=box('clean_supply_label_band',(.515,.091,1.507),(.434,.018,.096),'ivory_enamel',.003)
 label('clean_supply_semantics','CLEAN',(.515,.0805,1.507),.064)
 cbox('clean_supply_label',[.298,.078,1.459],[.732,.10,1.555])
 void('clean_upper_retrieval',[.32,.025,1.27],[.71,.315,1.44],'Upper open supply shelf mouth, finite component clearance')
 void('clean_lower_retrieval',[.32,.025,1.015],[.71,.315,1.21],'Lower open supply shelf mouth, finite component clearance')
 void('basin_working_recess',[-.535,-.145,.800],[-.085,.055,.93],'Finite actual central bowl void, no virtual liquid or treatment assignment')
 marker('DRY_WORK_CONTACT',[.48,-.16,.94],'physical_work_surface',rim.name,[0,0,1],'Flat dry landing separate from recessed bowl; no reach certification')
 # Stout supported tap assembly: continuous solid visual stem and elbow, closed outlet.
 rod('tap_deck_mount',(-.32,.265,.940),(-.32,.265,.957),.047,'care_brushed_metal',16)
 rod('tap_vertical_stem',(-.32,.265,.957),(-.32,.265,1.185),.029,'care_brushed_metal',12)
 elbow=extrude('tap_forward_elbow',[(.294,1.156),(.294,1.205),(.25,1.235),(-.075,1.235),(-.106,1.205),(-.106,1.16),(-.058,1.16),(-.058,1.181),(.242,1.181),(.242,1.156)],0,-.349,-.291,'care_brushed_metal')
 rod('tap_closed_outlet_cap',(-.32,-.082,1.158),(-.32,-.082,1.151),.020,'dark_rubber',12)
 marker('TAP_DECK_BEARING',[-.32,.265,.94],'physical_mount_face','tap_deck_mount',[0,0,-1],'Physical counter bearing, no installed water system')
 marker('UNIMPLEMENTED_WATER_OUTLET',[-.32,-.082,1.151],'physical_closed_port','tap_closed_outlet_cap',[0,0,-1],'Opaque blank nozzle face; no liquid, plumbing or species compatibility implemented')
 cbox('tap_stem',[-.367,.218,.94],[-.273,.312,1.205]);cbox('tap_bridge',[-.349,-.106,1.181],[-.291,.294,1.235]);cbox('tap_tip',[-.349,-.106,1.151],[-.291,-.058,1.205])
 for x,s in[(-.59,'water'),(-.07,'control')]:
  rod(s+'_control_mount',(x,.267,.94),(x,.267,.957),.037,'care_brushed_metal',12)
  box(s+'_inactive_paddle',(x,.246,.979),(.075,.09,.044),'privacy_sage',.010)
  marker('UNIMPLEMENTED_'+s.upper()+'_CONTROL',[x,.246,1.001],'physical_control_face',s+'_inactive_paddle',[0,0,1],'Static inactive interface; no temperature, dosing, chemistry or treatment behavior assigned')
  cbox(s+'_control',[x-.0375,.201,.94],[x+.0375,.304,1.001])
 # Drain face is a closed cap standing on the real bowl floor, not a textured illusion.
 rod('basin_closed_drain_cap',(-.31,-.045,.755),(-.31,-.045,.761),.030,'care_brushed_metal',16)
 marker('UNIMPLEMENTED_DRAIN_FACE',[-.31,-.045,.761],'physical_closed_port','basin_closed_drain_cap',[0,0,1],'Blank drain cap only; drain route and fluid are unimplemented')
 # Explicit separate physical supply/drain/control rear interfaces; blank caps with support collars.
 for x,z,r,s in[(-.53,.42,.023,'water_supply'),(-.34,.32,.038,'drain'),(-.10,.49,.018,'control')]:
  rod(s+'_rear_collar',(x,.350,z),(x,.372,z),r+.010,'care_brushed_metal',12)
  rod(s+'_rear_blank_cap',(x,.372,z),(x,.379,z),r,'dark_rubber',12)
  marker('UNIMPLEMENTED_REAR_'+s.upper(),[x,.379,z],'physical_closed_port',s+'_rear_blank_cap',[0,1,0],'Distinct static blank interface; no host connection or flow/control function')
  cbox(s+'_rear_port',[x-r-.01,.35,z-r-.01],[x+r+.01,.379,z+r+.01])
 # Conservative basin compounds preserve the explicitly declared cavity and dry landing.
 cbox('basin_left_rim',[-.8,-.38,.88],[-.70,.38,.94]);cbox('basin_right_dry_landing',[.08,-.38,.88],[.8,.38,.94]);cbox('basin_front_rim',[-.70,-.38,.88],[.08,-.275,.94]);cbox('basin_back_rim',[-.70,.185,.88],[.08,.38,.94])
 chull('basin_left_sloped_wall',[[x,y,z]for y in(-.275,.185)for x,z in[(-.70,.94),(-.70,.88),(-.62,.724),(-.59,.755)]])
 chull('basin_right_sloped_wall',[[x,y,z]for y in(-.275,.185)for x,z in[(.08,.94),(.08,.88),(0,.724),(-.03,.755)]])
 chull('basin_front_sloped_wall',[[x,y,z]for x in(-.59,-.03)for y,z in[(-.275,.94),(-.275,.88),(-.22,.724),(-.19,.755)]])
 chull('basin_back_sloped_wall',[[x,y,z]for x in(-.59,-.03)for y,z in[(.185,.94),(.185,.88),(.13,.724),(.10,.755)]])
 cbox('basin_floor_and_drain',[-.62,-.22,.724],[0,.13,.761])
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',None,[0,0,1])
 marker('FRONT_WORK_APPROACH',[0,-.77,1.20],'nonphysical_approach_proposal',None,[0,1,0],'No body, tool, wheelchair or universal species fit')
 return 'Shaped clinical wash and clean-supply bay',{'purpose':'Separate recessed wash bowl, supported static tap/control interfaces, dry work landing, clean-supply retrieval and service access','basin_floor_source_z_m':.755,'work_surface_source_z_m':.94,'clean_shelf_source_z_m':[1.0,1.25],'service_cover':'Removable static cover; withdrawal proposal only, no moving service state','functional_limit':'No active fluids, medicine, chemistry, treatment guidance, powered actions or sterility claim','species_limit':'Adjustable component proposal; shape does not demonstrate suitability for any species'}

def measure():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for o in PARTS:
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in pts)for i in range(3)];hi=[max(p[i]for p in pts)for i in range(3)]
 return dict(bounds_pair(lo,hi),dimensions_source_m=[b-a for a,b in zip(lo,hi)],dimensions_gltf_m=[hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]],triangles=tri)

def export(ident,state):
 dg=bpy.context.evaluated_depsgraph_get();copies=[]
 for src in PARTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=active:me.uv_layers.remove(layer)
  # Reproject evaluated faces when a bevel/text cap introduced a degenerate UV.
  uvmap(me,src['material_role'])
  o=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy();o.parent=ROOT;o['source_part']=src.name;o['material_role']=src['material_role'];o['state']=state;o['moving_part']=src.parent==MOTION;copies.append(o)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 if MOTION:MOTION.select_set(True)
 for o in copies:o.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 path=BASE/'exports'/(ident+(''if state=='closed'else'__'+state)+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_animations=False,export_current_frame=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in copies:bpy.data.objects.remove(o,do_unlink=True)
 return path

def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];collisions={};api={}
 for ident,fn in[('AST-MED-001',privacy),('AST-MED-002',wash)]:
  reset(ident);title,details=fn();bpy.context.view_layer.update();closed=measure();states={}
  for state,frame in([('closed',1),('open',117)]if MOTION else [('closed',1)]):
   bpy.context.scene.frame_set(frame);bounds=measure();path=export(ident,state);states[state]={'export':str(path.relative_to(BASE)),'sha256':sha(path),'bounds':bounds}
  bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True)
  row={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_clinical_architecture.py','source_frame':'metres Blender Xwidth/Ydepth/Zup, front-Y','exchange_frame':'native GLB Y-up, source(x,y,z)->(x,z,-y), actual hierarchy authoritative','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'kind':'floor origin; actual host support unknown'},'bounds':closed,'bounds_blender_z_up':{'min_m':closed['min_source_m'],'max_m':closed['max_source_m'],'dimensions_m':closed['dimensions_source_m']},'bounds_gltf_y_up':{'min_m':closed['min_gltf_m'],'max_m':closed['max_gltf_m'],'dimensions_m':closed['dimensions_gltf_m']},'dimensions_blender_xyz_m':closed['dimensions_source_m'],'evaluated_source_triangles':closed['triangles'],'evaluated_triangles':closed['triangles'],'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role']for o in PARTS)),'physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'states':states,'details':details,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_editability':'Named original solids, retained bevels, separate materials and parts, screen prismatic hierarchy/keyframes; evaluated export copies only','limitations':['Original game unavailable; no host room polygon, walls, door, usable ceiling or support recovered','No patient capacity, rooms, beds or population added','No actual body/cart, actor, treatment, engineering load or universal species suitability validation','Inspection component only; no Godot integration, clinical implementation or runtime performance claim']}
  rows.append(row);(BASE/f'{ident}.manifest.json').write_text(json.dumps(row,indent=2)+'\n');api[ident]=MARKERS;collisions[ident]={'source_frame':'Blender Z-up metres','exchange_frame':'GLB Y-up metres','status':'Structural compound proposals, not engine collision or mechanics','shapes':COLL,'preserve_voids':VOIDS,'approximation_limits':'Conservative boxes/convex hulls can extend outside rounded corners and details. Quantified finite profile evidence follows in qa; no universal surface or actor guarantee.'}
 (BASE/'manifest.json').write_text(json.dumps({'family':'clinical_architecture','revision':'clinical-architecture-01','new_design_count':2,'state_derivatives_are_new_designs':False,'assets':rows},indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(collisions,indent=2)+'\n')
 print('BUILT',[(r['catalogue_id'],r['bounds']['dimensions_source_m'],r['evaluated_triangles'])for r in rows])
if __name__=='__main__':main()
