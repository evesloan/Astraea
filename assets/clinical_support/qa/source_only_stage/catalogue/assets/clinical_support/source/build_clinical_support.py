"""Original editable D05 support furnishings, script-assisted Blender 4.3.2 authoring.
Rebuild from source-only dependency closure: blender -b -t 2 --python-exit-code 1 --python this_file
No host room, clinical behavior, species/load/transfer fit, engine adoption or certification.
"""
import bpy,bmesh,math,json,hashlib,importlib.util,random
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for sub in ('source','exports','textures','qa'): (BASE/sub).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('clinical_shared_materials',CAT/'standards/materials.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);MATS=mod.materials()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
spec=importlib.util.spec_from_file_location('clinical_care_materials',CAT/'standards/care_materials.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);MATS.update(mod.materials())
for mat in MATS.values():
 if isinstance(mat['meters_per_tile_uv'],(int,float)):mat['meters_per_tile_uv']=[mat['meters_per_tile_uv'],mat['meters_per_tile_uv']]
def reset(ident):
 global PARTS,MARKERS,JOINS,COLL,VOIDS,ROOT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident;ROOT['scope']='D05 fictional fixed support furnishing; body/load/transfer fit unverified'
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident

def mesh(name,verts,faces,role='ivory_enamel',bevel=0):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob['material_role']=role;ob['provenance']='Original script-assisted clinical support design';me.materials.append(MATS[role])
 uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True;sx,sy=MATS[role]['meters_per_tile_uv'];grain=max(range(3),key=lambda i:max(v.co[i]for v in me.vertices)-min(v.co[i]for v in me.vertices));ob['grain_source_axis']=grain
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=axis]
  if role=='care_brushed_metal'and grain in axes:axes=[i for i in axes if i!=grain]+[grain]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)
 if bevel:
  m=ob.modifiers.new('Editable contact edge easing','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=math.radians(35)
  m=ob.modifiers.new('Editable weighted surface normals','WEIGHTED_NORMAL');m.keep_sharp=True
 PARTS.append(ob);return ob

def box(name,c,d,role='ivory_enamel',bevel=.003):
 x,y,z=c;a,b,h=[v/2 for v in d]
 return mesh(name,[(x+i*a,y+j*b,z+k*h)for i,j,k in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)
def extrude(name,profile,axis,a,b,role='ivory_enamel',bevel=0):
 axes=[i for i in range(3)if i!=axis];vs=[]
 for dep in(a,b):
  for p in profile:
   v=[0,0,0];v[axis]=dep;v[axes[0]]=p[0];v[axes[1]]=p[1];vs.append(v)
 n=len(profile);return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,bevel)
def clipped(w,d,c=.06,x=0,y=0):return [(x-w/2+c,y-d/2),(x+w/2-c,y-d/2),(x+w/2,y-d/2+c),(x+w/2,y+d/2-c),(x+w/2-c,y+d/2),(x-w/2+c,y+d/2),(x-w/2,y+d/2-c),(x-w/2,y-d/2+c)]
def rod(name,a,b,r,role='care_brushed_metal',n=12,phase=0):
 a,b=Vector(a),Vector(b);di=(b-a).normalized();seed=Vector((1,0,0))if abs(di.x)<.9 else Vector((0,1,0));u=di.cross(seed).normalized();v=di.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n+phase)+v*math.sin(2*math.pi*i/n+phase))for p in(a,b)for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role)
def marker(name,p,kind,part=None,normal=None,description=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o.location=p;o.empty_display_size=.022
 row={'name':name,'kind':kind,'source_m':p,'gltf_m':glb(p),'physical_part':part,'description':description}
 if normal:row.update(direction_source=normal,direction_gltf=glb(normal));o['direction_source']=normal;o['direction_gltf']=glb(normal)
 o['marker_kind']=kind;o['source_position_m']=p;o['gltf_position_m']=glb(p);o['physical_part']=part or '';MARKERS.append(row)
def joint(name,a,b,p,na=None,nb=None,kind='opposing_boundary_contact'):
 row={'name':name,'parts':[a,b],'probe_source_m':p,'probe_gltf_m':glb(p),'kind':kind}
 if na:row.update(normal_a_source=na,normal_b_source=nb,normal_a_gltf=glb(na),normal_b_gltf=glb(nb))
 JOINS.append(row)
def bounds_pair(lo,hi):return {'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]}
def void(name,lo,hi,purpose):VOIDS.append(dict(name=name,purpose=purpose,**bounds_pair(lo,hi)))
def hull(name,vs,parts,limit):COLL.append({'name':name,'type':'convex_hull_points','points_source_m':[list(p)for p in vs],'points_gltf_m':[glb(p)for p in vs],'covered_parts':parts,'approximation_note':limit})
def part_hull(ob,others=None,note='Convex source profile before small retained edge easing; no whole-furniture hull'):
 obs=[ob]+(others or []);hull(ob.name+'_structural_hull',[o.matrix_world@v.co for o in obs for v in o.data.vertices],[o.name for o in obs],note)
def pad(name,y):
 rings=[]
 for w,d,z,c in[(1.005,.655,.70,.065),(1.045,.695,.714,.07),(1.015,.665,.742,.068),(.985,.635,.75,.06)]:rings +=[(x,yy,z)for x,yy in clipped(w,d,c,y=y)]
 faces=[tuple(reversed(range(8)))]+[(r*8+i,r*8+(i+1)%8,(r+1)*8+(i+1)%8,(r+1)*8+i)for r in range(3)for i in range(8)]+[tuple(24+i for i in range(8))]
 return mesh(name,rings,faces,'care_soft_pad')

def support():
 # Symmetric along depth: the three equal modules imply no head/foot anatomy.
 deck=extrude('clipped_neutral_support_deck',clipped(1.18,2.20,.12),2,.665,.70,'ivory_enamel',.002)
 part_hull(deck)
 for i,y in enumerate((-.715,0,.715),1):
  ob=pad('removable_equal_support_pad_'+str(i),y);part_hull(ob)
  marker('PAD_'+str(i)+'_PHYSICAL_CONTACT',[0,y,.75],'physical_support_contact',ob.name,[0,0,1],'Flat pad plateau only; species posture, safe loading and transfer fit unverified')
  joint('pad_'+str(i)+'_to_deck',ob.name,deck.name,[0,y,.70],[0,0,-1],[0,0,1])
 for y,tag in[(-.68,'forward'),(.68,'rear')]:
  for s,side in[(-1,'left'),(1,'right')]:
   xp=[(.35,.025),(.52,.025),(.52,.07),(.47,.575),(.39,.61),(.33,.575)]
   leg=extrude(tag+'_'+side+'_splayed_trestle',[(s*x,z)for x,z in xp],1,y-.095,y+.095,'ivory_enamel',.002)
   shoe=extrude(tag+'_'+side+'_floor_isolation',clipped(.20,.24,.035,x=s*.43,y=y),2,0,.025,'dark_rubber')
   part_hull(leg,[shoe],note='Leg plus local sole; finite overreach measured, bevel loss <=2mm; useful central opening excluded')
   marker(tag.upper()+'_'+side.upper()+'_FLOOR',[s*.43,y,0],'physical_floor_contact',shoe.name,[0,0,-1])
   joint(tag+'_'+side+'_shoe_contact',shoe.name,leg.name,[s*.43,y,.025],[0,0,1],[0,0,-1])
  beam=extrude(tag+'_tapered_trestle_header',[(-.47,.575),(.47,.575),(.49,.625),(.49,.665),(-.49,.665),(-.49,.625)],1,y-.095,y+.095,'ivory_enamel',.002);part_hull(beam)
  joint(tag+'_header_deck',beam.name,deck.name,[0,y,.665],[0,0,1],[0,0,-1])
  for s,side in[(-1,'left'),(1,'right')]:joint(tag+'_'+side+'_leg_header',tag+'_'+side+'_splayed_trestle',beam.name,[s*.40,y,.59],kind='buried_structural_overlap')
 spine=box('underdeck_longitudinal_tie',(0,0,.608),(.16,1.17,.08),'care_brushed_metal',.003);part_hull(spine)
 for y,tag in[(-.68,'forward'),(.68,'rear')]:joint('tie_into_'+tag,spine.name,tag+'_tapered_trestle_header',[0,y+(.095 if y<0 else -.095),.608],kind='buried_structural_overlap')
 for s,side in[(-1,'left'),(1,'right')]:
  rail=box(side+'_recessed_attachment_rail',(s*.5675,0,.623),(.045,1.60,.044),'care_brushed_metal',.003)
  blocks=[]
  for y,tag in[(-.64,'forward'),(.64,'rear')]:
   block=box(side+'_'+tag+'_attachment_bearing',(s*.5675,y,.655),(.045,.11,.02),'ivory_enamel',0);blocks.append(block)
   joint(side+'_'+tag+'_rail_bearing',rail.name,block.name,[s*.5675,y,.645],[0,0,1],[0,0,-1]);joint(side+'_'+tag+'_deck_bearing',block.name,deck.name,[s*.555,y,.665],[0,0,1],[0,0,-1])
  part_hull(rail,blocks,note='Rail and two small bearing lands grouped; fills only 20mm high gap between local mounting lands, outside declared underdeck void')
  marker(side.upper()+'_OPTIONAL_ATTACHMENT_FACE',[s*.59,0,.623],'physical_optional_attachment_face',rail.name,[s,0,0],'Real mounting face only; attachment absent, no latch, standard, Mindo port or load capacity assigned')
  marker(side.upper()+'_STAFF_APPROACH',[s*1.25,0,0],'nonphysical_approach_proposal',description='Optional staff/transfer-side reservation only; no actor or transfer acceptance')
 marker('BARE_DECK_END_CONTACT',[0,-1.06,.70],'physical_support_contact',deck.name,[0,0,1],'Exposed deck surface beyond equal removable pad footprint')
 void('central_underdeck_space',[-.28,-1.04,.045],[.28,1.04,.54],'Continuous clear space under fixed deck; no body-access or transfer guarantee')
 void('side_underdeck_approach',[.325,-.49,.04],[.52,.49,.57],'Between trestles below rail, profile-following unoccupied space')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',description='Floor datum, not a physical point at centre')
 return 'Neutral modular examination-support platform',{'fixed_default':True,'nominal_support_height_m':.75,'supported_source_contacts':'Three equal flat removable pad plateaux, bare deck end, and four floor shoes','removable_option':'Three equal modules are separate editable parts; no removal animation or clinical pose','attachment_reserves':'Two actual under-edge rail faces with bearing lands; no installed attachment, standard or treatment interface','unverified':['species posture','body fit','support load','transfer method','Baelin aquatic/dry suitability','Mindo interfaces','chemistry'],'not_allocated':'No bed, clinical capacity, powered lift or tilt'}

def trolley():
 # Dedicated clean-supply staging and retrieval: closed cases, no cleaning-cart tooling.
 base=extrude('protected_clipped_lower_retrieval_shelf',clipped(.68,.80,.06),2,.235,.275,'ivory_enamel',.003);part_hull(base)
 for x,side in[(-.265,'left'),(.265,'right')]:
  for y,tag in[(-.32,'front'),(.32,'rear')]:
   stem=rod(side+'_'+tag+'_vertical_caster_stem',[x,y,.195],[x,y,.235],.021)
   wheel=rod(side+'_'+tag+'_solid_wheel',[x-.027,y,.075],[x+.027,y,.075],.075/math.cos(math.pi/16),'dark_rubber',16,math.pi/16)
   axle=rod(side+'_'+tag+'_axle',[x-.052,y,.075],[x+.052,y,.075],.014)
   cap=box(side+'_'+tag+'_fork_bridge',(x,y,.185),(.105,.085,.020),'care_brushed_metal',.001)
   forks=[]
   for s,n in[(-1,'inner'),(1,'outer')]:
    fork=extrude(side+'_'+tag+'_'+n+'_wheel_fork',[(y-.042,.068),(y+.042,.068),(y+.042,.175),(y-.042,.175)],0,x+s*.0475-.0075,x+s*.0475+.0075,'care_brushed_metal',.001);forks.append(fork)
    joint(side+'_'+tag+'_'+n+'_fork_to_bridge',fork.name,cap.name,[x+s*.0475,y,.175],[0,0,1],[0,0,-1])
    joint(side+'_'+tag+'_'+n+'_axle_bearing',axle.name,fork.name,[x+s*.0475,y,.075],kind='buried_axle_bearing')
   joint(side+'_'+tag+'_wheel_axle',wheel.name,axle.name,[x,y,.075],kind='buried_axle_bearing')
   joint(side+'_'+tag+'_stem_to_fork',stem.name,cap.name,[x,y,.195],[0,0,-1],[0,0,1])
   joint(side+'_'+tag+'_stem_to_base',stem.name,base.name,[x,y,.235],[0,0,1],[0,0,-1])
   marker(side.upper()+'_'+tag.upper()+'_WHEEL_FLOOR',[x,y,0],'physical_floor_contact',wheel.name,[0,0,-1])
   marker(side.upper()+'_'+tag.upper()+'_AXLE_CENTRE',[x,y,.075],'physical_bearing_centre',description='Pivot datum inside actual wheel/axle assembly; fixed visual assembly, no rigid-body dynamics')
   # Deliberately grouped fork/axle/caster support around one small wheel; preserves global under-shelf opening.
   part_hull(wheel,note='Exact sixteen-sided wheel prism, floor support Z0')
   part_hull(cap,[stem,axle]+forks,note='Caster support compound fills small fork interior around axle; finite gap/profile overreach measured; no wheel turning simulation')
 for x,side in[(-.295,'left'),(.295,'right')]:
  for y,tag in[(-.31,'front'),(.31,'rear')]:
   post=box(side+'_'+tag+'_structural_upright',(x,y,.5725),(.055,.055,.595),'ivory_enamel',.005);part_hull(post)
   joint(side+'_'+tag+'_post_base',post.name,base.name,[x,y,.275],[0,0,-1],[0,0,1])
 mid=extrude('closed_supply_case_bearing_shelf',clipped(.59,.65,.035),2,.515,.55,'warm_stone',.001);part_hull(mid)
 # Shelf returns land in the uprights, evidenced as supported buried edge bearings.
 for x,side in[(-.295,'left'),(.295,'right')]:
  for y,tag in[(-.31,'front'),(.31,'rear')]:joint(side+'_'+tag+'_middle_shelf_bearing',mid.name,side+'_'+tag+'_structural_upright',[x-(-.023 if x<0 else .023),y,.535],kind='buried_structural_overlap')
 for x,label in[(-.1425,'A'),(.1425,'B')]:
  case=extrude('closed_supply_case_'+label,clipped(.255,.535,.03,x=x,y=.005),2,.55,.779,'ivory_enamel',.003)
  lid=extrude('lift_off_case_'+label+'_lid',clipped(.261,.541,.032,x=x,y=.005),2,.779,.806,'care_bluegreen_resin',.002)
  # Pull is a real bridge, with empty fingerspace behind it, separate from original closed container.
  pull=rod('case_'+label+'_front_pull',[x-.060,-.307,.69],[x+.060,-.307,.69],.012/math.cos(math.pi/12),'care_brushed_metal',12,math.pi/12)
  bearings=[]
  for dx,tag in[(-.06,'left'),(.06,'right')]:
   b=rod('case_'+label+'_'+tag+'_pull_bearing',[x+dx,-.307,.69],[x+dx,-.2625,.69],.012);bearings.append(b)
   joint('case_'+label+'_'+tag+'_pull_join',b.name,pull.name,[x+dx,-.307,.69],kind='buried_structural_overlap')
   joint('case_'+label+'_'+tag+'_case_join',b.name,case.name,[x+dx,-.2625,.69],[0,1,0],[0,-1,0])
  joint('case_'+label+'_base_contact',case.name,mid.name,[x,.005,.55],[0,0,-1],[0,0,1])
  joint('case_'+label+'_lid_contact',lid.name,case.name,[x,.005,.779],[0,0,-1],[0,0,1])
  part_hull(case,[lid],note='Closed original integrated supply case and closed lift-off lid; no contents or medicine identity')
  part_hull(pull,note='Narrow pull bridge follows twelve-sided section; fingerspace remains excluded')
  for bearing in bearings:part_hull(bearing,note='Local pull end bearing only, preserving useful midpoint fingerspace')
  marker('CASE_'+label+'_PULL_CONTACT',[x,-.319,.69],'physical_hand_contact',pull.name,[0,-1,0],'Closed case retrieval grip; hand size, retention, removal path/load unverified')
  void('case_'+label+'_pull_fingerspace',[x-.04,-.291,.682],[x+.04,-.273,.698],'Open space behind central pull, kept clear of case face and bearing ends')
 top=extrude('shaped_staff_staging_worktop',clipped(.70,.84,.065),2,.87,.9,'warm_stone',.002);part_hull(top)
 for x,side in[(-.295,'left'),(.295,'right')]:
  for y,tag in[(-.31,'front'),(.31,'rear')]:joint(side+'_'+tag+'_post_top',side+'_'+tag+'_structural_upright',top.name,[x,y,.87],[0,0,1],[0,0,-1])
 for x,side in[(-.33,'left'),(.33,'right')]:
  lip=box(side+'_protected_staging_rim',(x,0,.9275),(.04,.69,.055),'care_bluegreen_resin',.006);part_hull(lip);joint(side+'_rim_top',lip.name,top.name,[x,0,.90],[0,0,-1],[0,0,1])
 for y,tag,h in[(-.39,'front',.02),(.39,'rear',.055)]:
  lip=box(tag+'_staging_stop',(0,y,.90+h/2),(.53,.04,h),'care_bluegreen_resin',.004);part_hull(lip);joint(tag+'_stop_top',lip.name,top.name,[0,y,.90],[0,0,-1],[0,0,1])
 for x,side in[(-.255,'left'),(.255,'right')]:
  leg=rod(side+'_swept_push_handle_support',[x,.34,.90],[x,.475,1.045],.022,'care_brushed_metal');part_hull(leg)
  joint(side+'_push_support_top',leg.name,top.name,[x,.34,.90],kind='boundary_to_angled_end')
 bar=rod('broad_staff_push_handbar',[-.277,.475,1.045],[.277,.475,1.045],.025/math.cos(math.pi/12),'care_soft_pad',12,math.pi/12);part_hull(bar)
 for x,side in[(-.255,'left'),(.255,'right')]:joint(side+'_push_support_bar',side+'_swept_push_handle_support',bar.name,[x,.475,1.045],kind='buried_structural_overlap')
 marker('PUSH_CONTACT',[0,.475,1.070],'physical_hand_contact',bar.name,[0,0,1],'Broad padded staff push contact; no force/load/ergonomic or species claim')
 marker('TOP_STAGING_CONTACT',[0,0,.9],'physical_supply_surface',top.name,[0,0,1],'Bounded useful staging surface; no sterile-field or treatment claim')
 marker('LOWER_RETRIEVAL_CONTACT',[0,-.18,.275],'physical_retrieval_surface',base.name,[0,0,1],'Separate open retrieval shelf; no specific contents')
 marker('FRONT_RETRIEVAL_APPROACH',[0,-.85,0],'nonphysical_approach_proposal',description='Proposed staff access; actual host aisle and hand/body fit unknown')
 marker('REAR_PUSH_APPROACH',[0,.90,0],'nonphysical_approach_proposal',description='Proposed staff push position; no rig or animation')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',description='Datum at wheel contact floor, centre is empty')
 void('lower_retrieval_opening',[-.25,-.395,.29],[.25,.28,.50],'Actual open shelf between uprights, below closed supply shelf')
 void('under_trolley_clear_space',[-.18,-.27,.02],[.18,.27,.225],'Open between four discrete caster assemblies under bottom shelf')
 void('worktop_staging_air',[-.285,-.34,.915],[.285,.30,1.02],'Useful open staging region above real top, bounded by local rim')
 return 'Closed-supply and retrieval clinical trolley',{'fixed_default':True,'actual_contents':'Two closed integrated original supply cases; contents unspecified','regions':['Upper staff staging tray','Closed supply cases','Open lower retrieval shelf'],'movement':'Four fixed visual wheel/fork/axle assemblies; no dynamics, steering or brake behavior','not_player_cleaning_cart':True,'unverified':['handling force','load capacity','sterility','species or staff hand fit','host aisle clearance']}

def measure():
 dg=bpy.context.evaluated_depsgraph_get();points=[];tri=0
 for ob in PARTS:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);points.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in points)for i in range(3)];hi=[max(p[i]for p in points)for i in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

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
   p=me.polygons[pi];axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=axis];grain=int(src['grain_source_axis'])
   if src['material_role']=='care_brushed_metal'and grain in axes:axes=[i for i in axes if i!=grain]+[grain]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
  ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+role;ob.parent=ROOT;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in PARTS if s['material_role']==role]);out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for ob in out:ob.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)

def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];coll={};api={}
 for ident,fn in[('AST-MED-003',support),('AST-MED-004',trolley)]:
  reset(ident);title,details=fn();bpy.context.view_layer.update();bounds,tri=measure()
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  lo,hi=bounds['min_m'],bounds['max_m'];glo=[lo[0],lo[2],-hi[1]];ghi=[hi[0],hi[2],-lo[1]]
  rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_clinical_support.py','source_frame':'metres Blender X width Y depth Z up, front -Y','exchange_frame':'metres GLB Y-up; source(x,y,z)->(x,z,-y), actual node hierarchy authoritative','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'Local floor-contact datum, host deck support unknown'},'bounds_blender_z_up':bounds,'bounds_gltf_y_up':{'min_m':glo,'max_m':ghi,'dimensions_m':[b-a for a,b in zip(glo,ghi)]},'dimensions_blender_xyz_m':bounds['dimensions_m'],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[ob.name for ob in PARTS],'material_roles':sorted(set(ob['material_role']for ob in PARTS)),'runtime_consolidation':'Evaluated static copies by semantic material role; UV layers normalized; source parts editable','physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Original game/host absent; no game implementation or catalogue promotion','Adjustable dimensions only; no room, bed, patient or population allocation','All body/load/transfer/species fit remains unverified','No treatment behavior, active fluids, chemistry or clinical certification','No performance, collision-engine or dynamics claims']}
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');coll[ident]={'source_frame':'metres Blender Z-up','exchange_frame':'metres native glTF Y-up','status':'Separate profile-following structural proposals; no engine physics','shapes':COLL,'preserve_voids':VOIDS,'approximation_limits':'Finite measured source samples only; convex compounds approximate small grouped details, not complete physical bounds'};api[ident]=MARKERS
 (BASE/'manifest.json').write_text(json.dumps({'family':'clinical_support','revision':'clinical-support-01','assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n')
 print('BUILT',[(r['catalogue_id'],r['evaluated_source_triangles'],r['dimensions_blender_xyz_m'])for r in rows])
if __name__=='__main__':main()
