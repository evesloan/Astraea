"""Original editable AST-HSK-003/004. Source-only deterministic Blender 4.3.2 build.
Static proposed textile workplace furnishings; no hygiene, rolling/load or species certification.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for sub in('source','exports','textures','qa'):(BASE/sub).mkdir(parents=True,exist_ok=True)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
load('original_handling_art',BASE/'textures/draw_handling_art.py').build()
M=load('unchanged_staff_materials',CAT/'standards/staff_materials.py').materials()
ART=json.loads((BASE/'textures/manifest.json').read_text())['materials']
for role,row in ART.items():
 mat=bpy.data.materials.new('ASTRAEA_'+role);mat.use_nodes=True;mat['astraea_material_role']=role;mat['meters_per_tile_uv']=row['meters_per_tile_uv'];mat['provenance']='Original generated handling art, no external font';nd=mat.node_tree.nodes;nd.clear();bs=nd.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic'];tx=nd.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(BASE/'textures'/row['file']),check_existing=True);tx.image.pack();tx.interpolation='Linear';tx.extension='REPEAT';out=nd.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);M[role]=mat
ALIASES={'white':'staff_white_paint','metal':'staff_zinc','dark':'staff_rubber','frame':'staff_bluegrey_paint','canvas':'handling_canvas','linen':'handling_linen','clean':'handling_clean_graphic','used':'handling_used_graphic'}
def reset(ident):
 global PARTS,MARKERS,JOINS,VOIDS,COLL,ROOT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);PARTS=[];MARKERS=[];JOINS=[];VOIDS=[];COLL=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident;ROOT['handling_scope']='Static fictional workplace form; no operating, hygiene, species, load or rolling acceptance'
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident

def uv_mesh(me,role,graphic=False):
 uv=me.uv_layers.active or me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 sx,sy=M[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[i for i in range(3)if i!=axis]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)

def mesh(name,verts,faces,role='white',bevel=0,body=True):
 role=ALIASES.get(role,role);me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob['material_role']=role;ob['body_candidate_retained']=body;ob['motion_group']='fixed';me.materials.append(M[role]);uv_mesh(me,role)
 if bevel:
  mo=ob.modifiers.new('Editable eased manufacturing edge','BEVEL');mo.width=bevel;mo.segments=2;mo.limit_method='ANGLE';mo.angle_limit=math.radians(35)
  mo=ob.modifiers.new('Editable weighted face normals','WEIGHTED_NORMAL');mo.keep_sharp=True
 PARTS.append(ob)
 # All shapes are individually convex as authored. Body candidate is literal subset of this reference list.
 COLL.append({'name':name,'kind':'convex_hull_points','points_source_m':[list(v)for v in verts],'points_gltf_m':[glb(v)for v in verts],'source_part':name,'body_candidate_retained':body,'edge_easing_max_m':bevel,'scope':'Original convex semantic part before editable bevel; no assembled enclosing hull'})
 return ob

def box(name,lo,hi,role='white',bevel=.0015,body=True):
 return mesh(name,[(lo[0]if i==0 else hi[0],lo[1]if j==0 else hi[1],lo[2]if k==0 else hi[2])for i,j,k in[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,body)
def prism(name,poly,z0,z1,role='white',bevel=.0015,body=True):
 n=len(poly);return mesh(name,[(x,y,z)for z in(z0,z1)for x,y in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,bevel,body)
def clipped(x0,x1,y0,y1,c=.03):return[(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1-c),(x1-c,y1),(x0+c,y1),(x0,y1-c),(x0,y0+c)]
def rod(name,a,b,r,role='metal',n=12,phase=0,body=True):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();seed=Vector((1,0,0))if abs(d.x)<.9 else Vector((0,1,0));u=d.cross(seed).normalized();v=d.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n+phase)+v*math.sin(2*math.pi*i/n+phase))for p in(a,b)for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,0,body)
def marker(name,p,kind,part=None,normal=None,note=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o.location=p;o.empty_display_size=.025;row={'name':name,'kind':kind,'source_m':p,'gltf_m':glb(p),'physical_part':part,'description':note}
 if normal:row.update(normal_source=normal,normal_gltf=glb(normal));o['normal_source']=normal;o['normal_gltf']=glb(normal)
 o['marker_kind']=kind;o['physical_part']=part or '';o['source_position_m']=p;o['gltf_position_m']=glb(p);MARKERS.append(row)
def joint(name,a,b,p,kind='opposing_boundary_contact'):
 JOINS.append({'name':name,'parts':[a,b],'probe_source_m':p,'probe_gltf_m':glb(p),'kind':kind})
def void(name,lo,hi,note):VOIDS.append({'name':name,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':note})
def label(name,x0,x1,y,z0,z1,word,support):
 ob=box(name,[x0,y-.005,z0],[x1,y,z1],'metal',0,False);ob.data.materials.append(M[ALIASES[word]]);uv=ob.data.uv_layers.active
 for f in ob.data.polygons:
  if f.normal.y<-.999:
   f.material_index=1
   for li in f.loop_indices:
    p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x-x0)/(x1-x0),(p.z-z0)/(z1-z0))
 ob['graphic_bounds']=json.dumps([x0,x1,z0,z1]);ob['graphic_role']=ALIASES[word];joint(name+'_backing',name,support,[(x0+x1)/2,y,(z0+z1)/2]);marker(name+'_FACE',[(x0+x1)/2,y-.005,(z0+z1)/2],'physical_identification_surface',name,[0,-1,0],word.upper()+' handling intent only; not hygiene certification');return ob

def cloth(name,x0,x1,y0,y1,z0,z1):
 return prism(name,clipped(x0,x1,y0,y1,.025),z0,z1,'linen',.005)

def bench():
 top=prism('bench_folded_work_deck',clipped(-.90,.90,-.43,.43,.055),.866,.90,'white',.002)
 # Two pairs of open square tubular legs support headers, distinct from guest desks.
 for side,x in[('left',-.77),('right',.77)]:
  for end,y in[('front',-.30),('rear',.30)]:
   tag=side+'_'+end;shoe=box(tag+'_floor_shoe',[x-.042,y-.042,0],[x+.042,y+.042,.025],'dark',0)
   leg=box(tag+'_square_leg',[x-.028,y-.028,.025],[x+.028,y+.028,.815],'frame',.0015)
   joint(tag+'_shoe_to_leg',shoe.name,leg.name,[x,y,.025]);marker(tag.upper()+'_FLOOR',[x,y,0],'physical_floor_contact',shoe.name,[0,0,-1])
  header=box(side+'_top_header',[x-.039,-.355,.815],[x+.039,.355,.866],'metal',.001)
  for end,y in[('front',-.30),('rear',.30)]:joint(side+'_'+end+'_leg_header',side+'_'+end+'_square_leg',header.name,[x,y,.815])
  joint(side+'_header_to_worktop',header.name,top.name,[x,0,.866])
  beam=box(side+'_shelf_bearing',[x-.027,-.324,.265],[x+.027,.324,.295],'metal',.001)
  for y,end in[(-.30,'front'),(.30,'rear')]:joint(side+'_'+end+'_shelf_bearing_to_leg',beam.name,side+'_'+end+'_square_leg',[x,y,.28],'buried_structural_overlap')
 # Exposed cross ties end into leg sides and stay behind retrieval face.
 rear=box('rear_upper_cross_tie',[-.742,.274,.756],[.742,.326,.811],'frame',.001)
 for side,x in[('left',-.742),('right',.742)]:joint(side+'_rear_cross_tie_to_leg',rear.name,side+'_rear_square_leg',[x,.30,.78])
 shelf=prism('open_lower_textile_shelf',clipped(-.791,.791,-.327,.327,.02),.295,.321,'white',.0015)
 for side,x in[('left',-.77),('right',.77)]:joint(side+'_shelf_to_bearing',shelf.name,side+'_shelf_bearing',[x,0,.295])
 lip=box('lower_shelf_backstop',[-.72,.302,.321],[.72,.327,.37],'frame',.001);joint('shelf_backstop_support',lip.name,shelf.name,[0,.313,.321])
 # Front folded nose ends at top corner cuts; downturned support and labels are real plates.
 nose=box('work_deck_front_downturn',[-.839,-.425,.811],[.839,-.395,.866],'metal',.001)
 joint('front_fold_to_deck',nose.name,top.name,[0,-.407,.866])
 # Central separation/return edge is fixed; it does not turn intent into a hygiene barrier.
 divider=box('central_fixed_separation_return',[.092,-.355,.90],[.115,.40,1.017],'metal',.001)
 back=box('rear_retention_return',[-.835,.395,.90],[.835,.423,1.017],'white',.001)
 joint('central_return_worktop',divider.name,top.name,[.103,0,.90]);joint('rear_return_worktop',back.name,top.name,[0,.408,.90]);joint('central_to_rear_return',divider.name,back.name,[.103,.398,.98],'buried_structural_overlap')
 # Used right has a shorter side return; left remains broad folding approach.
 right=box('used_outer_return',[.837,-.13,.90],[.86,.395,.972],'metal',.001);joint('used_return_worktop',right.name,top.name,[.848,0,.90]);joint('used_return_back',right.name,back.name,[.837,.395,.95])
 label('clean_zone_plate',-.735,-.235,-.425,.812,.865,'clean',nose.name);label('used_zone_plate',.225,.725,-.425,.812,.865,'used',nose.name)
 # Two integrated anonymous folded pieces, supported and kept off the active folding contact.
 a=cloth('clean_folded_linen_lower',-.755,-.325,.11,.345,.90,.94);joint('clean_folded_stock_on_worktop',a.name,top.name,[-.54,.22,.90])
 b=cloth('clean_folded_linen_upper',-.74,-.34,.12,.332,.94,.973);joint('clean_folded_stock_stack',b.name,a.name,[-.54,.22,.94])
 # Low open storage contains one bundle to communicate textile use, not inventory.
 c=cloth('lower_folded_bundle',-.63,-.19,.005,.27,.321,.391);joint('lower_bundle_shelf',c.name,shelf.name,[-.41,.15,.321])
 marker('CLEAN_FOLDING_SURFACE',[-.35,-.16,.90],'physical_work_surface',top.name,[0,0,1],'Clean-zone geometric work face; no hygienic separation claim')
 marker('USED_SORTING_SURFACE',[.49,0,.90],'physical_work_surface',top.name,[0,0,1],'Used-zone geometric work face; procedure unassigned')
 marker('LOWER_RETRIEVAL_SURFACE',[.40,0,.321],'physical_load_surface',shelf.name,[0,0,1])
 marker('FRONT_STAFF_APPROACH',[0,-.85,0],'nonphysical_approach_proposal',note='Actual species/reach/room and carrier clearances unverified')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',note='Empty centre floor datum, not a physical centre contact')
 void('open_lower_retrieval_mouth',[-.69,-.50,.403],[.69,.26,.74],'Real unoccupied lower storage approach above shelf and bundle')
 void('front_toe_space',[-.67,-.42,.035],[.67,.22,.25],'Open between legs beneath shelf; no body fitting claim')
 void('clean_work_air',[-.76,-.34,.912],[.07,.08,1.15],'Open folding area over actual top, excludes anonymous stock')
 void('used_work_air',[.13,-.34,.912],[.82,.36,1.15],'Open used sorting area within fixed returns')
 return 'Separated textile sorting and folding workbench',{'handling_intent':'Left CLEAN, right USED; procedural/hygienic separation unassigned','nominal_worktop_height_m':.90,'closed_static_configuration':True,'articulation':'None; open storage deliberately avoids unnecessary doors','integrated_stock':'Three original anonymous folded textile forms, not inventory or new designs','proposed_access':{'front_approach_source_m':{'min':[-.95,-1.05,0],'max':[.95,-.45,1.8]}}}

def carrier():
 # Single-role USED-only deep bulk space, not a guest-return receiver or service trolley.
 deck=prism('carrier_lower_load_cradle',clipped(-.39,.39,-.32,.32,.045),.205,.237,'frame',.002)
 for side,x in[('left',-.315),('right',.315)]:
  for end,y in[('front',-.245),('rear',.245)]:
   tag=side+'_'+end
   # Sixteen-sided tread with exactly flat floor sector at Z0.
   wheel=rod(tag+'_wheel_tread',[x-.027,y,.07],[x+.027,y,.07],.07/math.cos(math.pi/16),'dark',16,math.pi/16)
   axle=rod(tag+'_retained_axle',[x-.052,y,.07],[x+.052,y,.07],.012,'metal',12,0,False)
   bridge=box(tag+'_caster_fork_bridge',[x-.055,y-.045,.153],[x+.055,y+.045,.175],'metal',.001)
   stem=rod(tag+'_caster_stem',[x,y,.175],[x,y,.205],.020,'metal',12)
   for s,term in[(-1,'inner'),(1,'outer')]:
    fork=box(tag+'_'+term+'_fork',[x+s*.045-.008,y-.039,.058],[x+s*.045+.008,y+.039,.153],'metal',.001,False)
    joint(tag+'_'+term+'_fork_bridge',fork.name,bridge.name,[x+s*.045,y,.153]);joint(tag+'_'+term+'_axle_retention',fork.name,axle.name,[x+s*.045,y,.07],'buried_axle_bearing')
   joint(tag+'_wheel_axle',wheel.name,axle.name,[x,y,.07],'buried_axle_bearing');joint(tag+'_stem_bridge',stem.name,bridge.name,[x,y,.175]);joint(tag+'_stem_cradle',stem.name,deck.name,[x,y,.205]);marker(tag.upper()+'_WHEEL_FLOOR',[x,y,0],'physical_floor_contact',wheel.name,[0,0,-1]);marker(tag.upper()+'_AXLE_CENTRE',[x,y,.07],'nonphysical_bearing_axis_datum',note='Fixed retained caster construction, no steering, traction or rolling animation')
 # Liner bottom physically rests on continuous cradle. Tall tapered walls do not fill the load space.
 bottom=prism('liner_supported_bottom',clipped(-.286,.286,-.236,.236,.035),.237,.252,'canvas',0)
 joint('liner_bottom_cradle',bottom.name,deck.name,[0,0,.237]);marker('LINER_LOAD_FLOOR',[0,0,.252],'physical_load_surface',bottom.name,[0,0,1],'Geometric bulk space only; no load mass/capacity acceptance')
 # Eight separated, thick faceted wall panels; matching edge joints, no curved-shell dividers.
 low=clipped(-.286,.286,-.236,.236,.035);high=clipped(-.36,.36,-.29,.29,.045)
 ztop=[.765,.765,.795,.925,.94,.94,.925,.795]
 # Offset toward cavity by 8mm in XY, giving closed prism thickness per panel.
 for i in range(8):
  j=(i+1)%8;a=Vector(low[i]+(.245,));b=Vector(low[j]+(.245,));c=Vector(high[j]+(ztop[j],));d=Vector(high[i]+(ztop[i],));edge=(b-a).normalized();n=Vector((-edge.y,edge.x,0))*.008
  vs=[a,b,c,d,a+n,b+n,c+n,d+n];ob=mesh('liner_faceted_wall_'+str(i),vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'canvas',0)
  mid=(a+b)/2+n/2;joint('liner_wall_'+str(i)+'_bottom',ob.name,bottom.name,list(mid),'buried_structural_overlap')
 # Frame posts end into cradle and retain the top rail. High rear, low front form gives clear retrieval.
 for side,x in[('left',-.375),('right',.375)]:
  for end,y,z in[('front',-.285,.80),('rear',.285,.967)]:
   tag=side+'_'+end;post=rod(tag+'_hoop_post',[x,y,.237],[x,y,z],.018,'metal');joint(tag+'_post_cradle',post.name,deck.name,[x,y,.237]);
  sideRail=rod(side+'_sloping_retained_side_hoop',[x,-.285,.80],[x,.285,.967],.018,'metal')
  for end,y,z in[('front',-.285,.80),('rear',.285,.967)]:joint(side+'_'+end+'_post_hoop',side+'_'+end+'_hoop_post',sideRail.name,[x,y,z],'buried_structural_overlap')
  # Broad woven straps overlap actual wall and wrap around side hoop; decorative small straps omitted from body candidate.
  for y,z in[(-.17,.834),(.18,.936)]:
   strap=box(side+'_liner_retention_strap_'+str(y),[x-.021,y-.028,z-.078],[x+.021,y+.028,z+.025],'linen',.001,False)
   joint(side+'_strap_'+str(y)+'_hoop',strap.name,sideRail.name,[x,y,z],'buried_structural_overlap')
 front=rod('lowered_front_retrieval_hoop',[-.393,-.285,.80],[.393,-.285,.80],.018,'metal')
 rear=rod('high_rear_hoop',[-.393,.285,.967],[.393,.285,.967],.018,'metal')
 for side,x in[('left',-.375),('right',.375)]:
  joint(side+'_front_cross_hoop',side+'_front_hoop_post',front.name,[x,-.285,.80],'buried_structural_overlap');joint(side+'_rear_cross_hoop',side+'_rear_hoop_post',rear.name,[x,.285,.967],'buried_structural_overlap')
 # Rear grip clear of liner rim. Real supports intersect retained back posts, not end-face hovering.
 for side,x in[('left',-.275),('right',.275)]:
  support=rod(side+'_grip_standoff',[x,.285,.967],[x,.39,1.055],.018,'metal');joint(side+'_grip_to_hoop',support.name,rear.name,[x,.285,.967],'buried_structural_overlap')
 grip=box('broad_rear_staff_grip',[-.302,.373,1.037],[.302,.415,1.077],'dark',.008)
 for side,x in[('left',-.275),('right',.275)]:joint(side+'_grip_standoff_retained',side+'_grip_standoff',grip.name,[x,.39,1.055],'buried_structural_overlap')
 marker('REAR_STAFF_GRIP',[0,.415,1.055],'physical_hand_contact',grip.name,[0,1,0],'Used-only carrier grip; force, hand sizes and turning space unverified')
 marker('FRONT_RETRIEVAL_RAIL',[0,-.303,.80],'physical_hand_contact',front.name,[0,-1,0],'Lower front textile retrieval edge; not a restraint or guest chute')
 # Dedicated rigid hanging identity plaque supported from the low rail, deliberately outside load cavity.
 hanger=box('used_label_hanger',[-.24,-.305,.647],[.24,-.287,.80],'metal',.001,False);joint('label_hanger_rail',hanger.name,front.name,[0,-.296,.80],'buried_structural_overlap')
 label('used_only_identification_plate',-.232,.232,-.305,.661,.776,'used',hanger.name)
 marker('FRONT_RETRIEVAL_APPROACH',[0,-.85,0],'nonphysical_approach_proposal',note='Proposed textile transfer approach; actual room/body path unknown');marker('REAR_PUSH_APPROACH',[0,.90,0],'nonphysical_approach_proposal',note='Proposed staff grip-side position; no driving controller or cart identity');marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',note='Empty centre floor datum')
 void('deep_bulk_linen_space',[-.245,-.19,.267],[.245,.19,.745],'True empty tapered liner core; geometric capacity only, no item or mass count')
 void('open_top_retrieval',[-.29,-.23,.819],[.29,.23,1.22],'Open retrieval above lowered front and liner; bounded core, not reach/collision acceptance')
 void('rear_grip_fingerspace',[-.235,.318,.997],[.235,.368,1.072],'Real opening in front of grip, behind high rear hoop')
 void('under_cradle_clear_space',[-.20,-.17,.02],[.20,.17,.19],'Real open floor gap between discrete fixed casters')
 return 'Used-textile bulk linen carrier',{'handling_intent':'USED ONLY; no mixed clean/used loading','purpose_distinction':'Deep open bulk-textile transfer volume with lowered front rail; not AQU-008 removable towel receiver, HSP-006 dining trolley, MED-004 supply trolley or player cart','movement':'Static retained caster geometry only. No caster swivel, rolling, liner removal or rigid-body state','liner':'Eight thick faceted walls and load bottom supported by cradle; stitched/retained top straps are geometric intent only','proposed_access':{'front_transfer_source_m':{'min':[-.6,-1.0,0],'max':[.6,-.38,1.7]},'rear_grip_source_m':{'min':[-.6,.45,0],'max':[.6,1.05,1.7]}}}

def evaluated(ob):
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));uv_mesh(me,ob['material_role'])
 if 'graphic_bounds'in ob:
  x0,x1,z0,z1=json.loads(ob['graphic_bounds']);uv=me.uv_layers.active
  for f in me.polygons:
   if f.material_index==1:
    for li in f.loop_indices:
     p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((p.x-x0)/(x1-x0),(p.z-z0)/(z1-z0))
 return me

def export(ident):
 groups={};out=[]
 for ob in PARTS:
  me=evaluated(ob);e=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(e);e.matrix_world=ob.matrix_world.copy();key=ob['material_role']+('__graphic'if'graphic_bounds'in ob else'');groups.setdefault(key,[]).append(e)
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+role;ob.parent=ROOT;ob['motion_group']='fixed';ob['material_group']=role;out.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for ob in out:ob.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT;bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)
 return len(groups)

def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];collision={};api={}
 for ident,fn in[('AST-HSK-003',bench),('AST-HSK-004',carrier)]:
  reset(ident);title,details=fn();bpy.context.view_layer.update();vertices=[];tri=0;parts=[]
  for ob in PARTS:
   me=evaluated(ob);me.calc_loop_triangles();tri+=len(me.loop_triangles);vertices.extend(ob.matrix_world@v.co for v in me.vertices);parts.append({'name':ob.name,'material_role':ob['material_role'],'body_candidate_retained':ob['body_candidate_retained'],'evaluated_triangles':len(me.loop_triangles),'editable_modifiers':[m.type for m in ob.modifiers]});bpy.data.meshes.remove(me)
  lo=[min(p[i]for p in vertices)for i in range(3)];hi=[max(p[i]for p in vertices)for i in range(3)]
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);group_count=export(ident)
  rec={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'design_count':1,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_handling.py','units':'metres','source_frame':'Blender XYZ Z-up front -Y','exchange_frame':'native glTF (x,z,-y); actual node hierarchy authoritative','datum':'Floor Z0, centre origin may be in empty space','pivot_source_m':[0,0,0],'bounds_blender_z_up':{'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i]for i in range(3)]},'bounds_gltf_y_up':{'min_m':[lo[0],lo[2],-hi[1]],'max_m':[hi[0],hi[2],-lo[1]]},'dimensions_blender_xyz_m':[hi[i]-lo[i]for i in range(3)],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'parts':parts,'runtime_mesh_groups':group_count,'runtime_consolidation':'Static evaluated copies grouped by material role and actual graphic submaterials, not per fastener or glyph','material_roles':sorted(set(ob['material_role']for ob in PARTS)),'physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','state_derivatives':[],'used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Proposed source configuration only; original host game and finished rooms absent','No species/reach/transfer/cart/door fitting, load/mass, hygiene or cleaning compatibility acceptance','No roll, traction, mechanism dynamics, operator or chore loop','Body candidate is optional geometric subset, engine acceptance pending']}
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');api[ident]={'markers':MARKERS,'joins':JOINS,'voids':VOIDS,'proposed_access':details['proposed_access']};collision[ident]={'source_frame':'Blender Z-up metres','native_frame':'GLB Y-up metres','precise_reference':COLL,'optional_body_candidate':{'derivation':'Literal subset of author-declared convex semantic reference shapes, authored from outset','retained_shape_names':[r['name']for r in COLL if r['body_candidate_retained']],'omitted_shape_names':[r['name']for r in COLL if not r['body_candidate_retained']],'new_enclosing_hulls':False,'contacts_and_service_markers_retained_separately':True,'engine_adoption':'Pending','fine_detail_distance':'Measured separately by QA; distinct from material wall thickness'},'preserved_voids':VOIDS}
 (BASE/'manifest.json').write_text(json.dumps({'batch':'17','family':'housekeeping_handling','unique_asset_count':2,'assets':rows},indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(collision,indent=2)+'\n')
 staff=json.loads((CAT/'materials/staff/manifest.json').read_text());inputs=[Path(__file__),BASE/'textures/draw_handling_art.py',CAT/'standards/staff_materials.py',CAT/'materials/staff/manifest.json']+[CAT/'materials/staff'/r['file']for r in staff['materials'].values()]
 (BASE/'dependency_manifest.json').write_text(json.dumps({'source_only_inputs':[{'path':str(p.relative_to(CAT)),'sha256':sha(p)}for p in inputs],'generated_original_art':[str((BASE/'textures'/r['file']).relative_to(CAT))for r in ART.values()]+[str((BASE/'textures/manifest.json').relative_to(CAT))],'original_art_regenerated_by_builder':True,'all_loaded_staff_roles_declared':True,'font_dependency':'None; original encoded glyphs in draw_handling_art.py','excluded_inputs':'No prior .blend, GLB, render, QA report or generated original graphic is used as a seed'},indent=2)+'\n')
 print('HANDLING_BUILD_OK',[(r['catalogue_id'],r['evaluated_triangles'],r['dimensions_blender_xyz_m'])for r in rows])
if __name__=='__main__':main()
