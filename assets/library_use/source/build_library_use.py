"""Astraea library use expansion: original script-assisted editable components.
Run: python source/make_use_art.py; blender -b -t 2 --python-exit-code 1 --python source/build_library_use.py
Only writes this family. Rebuild requires source, textures and the explicitly listed unchanged shared dependencies; no QA or rendered images.
"""
from pathlib import Path
import sys,math,json,hashlib
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1]
for p in ['source','exports','qa','textures']:(ROOT/p).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(BASE/'standards'))
from materials import materials
M={};PARTS=[];MARKERS=[];SHAPES=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def C(p):return [p[0],p[2],-p[1]]
def reset():
 global M,PARTS,MARKERS,SHAPES
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 M=materials();PARTS=[];MARKERS=[];SHAPES=[]
 defs=json.loads((ROOT/'texture_manifest.json').read_text())['materials']
 book=json.loads((BASE/'assets/library_contents/texture_manifest.json').read_text())
 for role in ['book_cover_teal','book_cover_clay','book_cover_ochre','book_paper_edges']:
  r=dict(book['materials'][role]);r['file']=str(Path('../library_contents')/book['texture_root']/r['base_color_file']);defs[role]=r
 for role,r in defs.items():
  m=bpy.data.materials.new('ASTRAEA_'+role);m.use_nodes=True;m['astraea_material_role']=role;m['meters_per_tile_uv']=r['meters_per_tile_uv'];m['dependency_path']=r['file']
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.34 if role=='catalogue_screen' else r.get('roughness',.75);bs.inputs['Metallic'].default_value=0
  im=bpy.data.images.load(str(ROOT/r['file']),check_existing=True);im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Linear';n.extension='REPEAT';m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color']);M[role]=m

def metric(me,role,grain='x'):
 uv=me.uv_layers.active or me.uv_layers.new(name='UV_Metric_Metres');uv.name='UV_Metric_Metres';uv.active_render=True;tile=M[role].get('meters_per_tile_uv',[1,1]);g={'x':0,'y':1,'z':2}[grain]
 for p in me.polygons:
  a=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=a]
  if g in axes:axes.remove(g);axes.append(g)
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/tile[0],co[axes[1]]/tile[1])

def mesh(name,verts,faces,role,bevel=0,grain='x',art=False):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(M[role]);ob['semantic_role']=role;ob['grain_axis']=grain;ob['art_uv']=art;metric(me,role,grain)
 if bevel:
  b=ob.modifiers.new('Editable edge easing','BEVEL');b.width=bevel;b.segments=1
  b=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');b.keep_sharp=True
 PARTS.append(ob);return ob

def extrude(name,profile,lo,hi,role,axis='z',bevel=.002,grain='x'):
 n=len(profile)
 if axis=='z':vs=[(a,b,t) for t in [lo,hi] for a,b in profile]
 elif axis=='x':vs=[(t,a,b) for t in [lo,hi] for a,b in profile]
 elif axis=='y':vs=[(a,t,b) for t in [lo,hi] for a,b in profile]
 fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,role,bevel,grain)
def rounded(w,d,r,n=3,center=(0,0)):
 p=[]
 for x,y,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for j in range(n):
   t=math.radians(a+90*j/(n-1));p.append((center[0]+x+r*math.cos(t),center[1]+y+r*math.sin(t)))
 return p
def slab(name,w,d,z0,z1,role,center=(0,0),r=.025,bevel=.002):return extrude(name,rounded(w,d,r,3,center),z0,z1,role,bevel=bevel)
def box(name,lo,hi,role,bevel=.002):return extrude(name,[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])],lo[2],hi[2],role,bevel=bevel)
def ring(name,outer,inner,z0,z1,role,bevel=.001):
 n=len(outer);assert len(inner)==n;vs=[(x,y,z) for z in [z0,z1] for arr in [outer,inner] for x,y in arr];fs=[]
 for i in range(n):
  j=(i+1)%n;fs += [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
 return mesh(name,vs,fs,role,bevel)
def beam(name,a,b,w,d,role,bevel=.002):
 a,b=Vector(a),Vector(b);ob=box(name,(-w/2,-d/2,-(b-a).length/2),(w/2,d/2,(b-a).length/2),role,bevel);ob.location=(a+b)/2;ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob

def basis(center,up=(0,0,1)):
 u=Vector((1,0,0));v=Vector(up).normalized();n=u.cross(v);return Matrix(((u.x,v.x,n.x,center[0]),(u.y,v.y,n.y,center[1]),(u.z,v.z,n.z,center[2]),(0,0,0,1)))
def place(ob,mat):ob.matrix_world=mat;return ob
def art(name,w,h,mat,role):
 ob=mesh(name,[(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)],[(0,1,2,3)],role,art=True)
 for i,li in enumerate(ob.data.polygons[0].loop_indices):ob.data.uv_layers.active.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][i]
 ob.matrix_world=mat;return ob

def marker(name,p,n,kind,meaning):
 ob=bpy.data.objects.new('POINT_'+name,None);bpy.context.collection.objects.link(ob);ob.location=p;ob.empty_display_size=.025
 ob['kind']=kind;ob['source_normal']=list(n);ob['exchange_normal']=C(n);ob['meaning']=meaning
 rec={'name':name,'node_name':ob.name,'kind':kind,'source_blender_zup_m':list(p),'exchange_gltf_yup_m':C(p),'normal_source_blender':list(n),'normal_exchange_gltf':C(n),'meaning':meaning};MARKERS.append((ob,rec));return rec

def collision_box(name,lo,hi,note='Separate fixed component box proposal'):
 SHAPES.append({'name':name,'type':'axis_aligned_box','min_source_m':list(lo),'max_source_m':list(hi),'min_exchange_m':[lo[0],lo[2],-hi[1]],'max_exchange_m':[hi[0],hi[2],-lo[1]],'note':note})
def collision_obb(name,center,size,up):
 mat=basis(center,up);corners=[list(mat@Vector((x*size[0]/2,y*size[1]/2,z*size[2]/2))) for x in [-1,1] for y in [-1,1] for z in [-1,1]]
 SHAPES.append({'name':name,'type':'oriented_box','centre_source_m':[float(v) for v in center],'size_local_xyz_m':list(size),'basis_source_columns':[list(mat.col[i][:3]) for i in range(3)],'vertices_source_m':corners,'vertices_exchange_m':[C(p) for p in corners],'note':'Independent thin shelf/body volume; no hull around front approach or between tiers'})

def lamp():
 # Small actual mating footprint is intentionally entirely inside both existing receiver surfaces.
 slab('LIGHT_mating_shoe',.084,.070,0,.016,'champagne_metal',r=.012,bevel=.0007)
 slab('LIGHT_service_foot',.106,.085,.014,.040,'ivory_enamel',r=.020,bevel=.001)
 for x in [-.032,.032]:slab('LIGHT_retaining_screw_'+str(x),.008,.008,.039,.041,'champagne_metal',(x,.021),r=.003,bevel=.0003)
 # Sculpted backward sweep raises the hood while keeping the receiving plate centre fixed.
 p=[(-.008,.032),(.027,.033),(.036,.099),(.047,.263),(.097,.368),(.097,.437),(.071,.461),(.052,.450),(.068,.422),(.067,.376),(.017,.275),(.006,.113)]
 extrude('LIGHT_swept_housed_spine',p,-.021,.021,'ivory_enamel',axis='x',bevel=.0018,grain='z')
 beam('LIGHT_rear_feed_conduit',(0,.023,.047),(0,.057,.314),.014,.014,'champagne_metal',.0007)
 # Real hollow polygon hood: wall follows an arched section, open below, no black painted outline.
 profile=[(-.200,.403),(-.184,.443),(-.139,.478),(-.060,.490),(.052,.480),(.106,.451),(.120,.414),(.101,.414),(.091,.440),(.044,.461),(-.060,.471),(-.132,.460),(-.168,.434),(-.180,.403)]
 extrude('LIGHT_arched_open_hood_shell',profile,-.282,.282,'warm_walnut',axis='x',bevel=.0018)
 # End cheeks close the lateral edges and seat the reflector.
 cheek=[(-.2,.403),(-.184,.443),(-.139,.478),(-.06,.49),(.052,.48),(.106,.451),(.12,.414),(.07,.400),(-.155,.394)]
 for x,side in [(-.289,'L'),(.280,'R')]:extrude('LIGHT_'+side+'_shaped_end_cheek',cheek,x,x+.009,'ivory_enamel',axis='x',bevel=.0015)
 # Reflector is a bent 3D trough around a replaceable tube receiver.
 rp=[(-.175,.411),(-.146,.449),(-.06,.461),(.055,.451),(.089,.430),(.092,.417),(.082,.418),(.074,.435),(.05,.440),(-.06,.451),(-.14,.440),(-.164,.410)]
 extrude('LIGHT_bent_reflector_bowl',rp,-.272,.272,'reflector',axis='x',bevel=.0006)
 for x,lab in [(-.23,'L'),(.23,'R')]:
  slab('LIGHT_'+lab+'_source_receiver_block',.041,.049,.427,.450,'ivory_enamel',(x,-.048),r=.009,bevel=.0006)
 beam('LIGHT_replaceable_source_carrier',(-.214,-.047,.430),(.214,-.047,.430),.017,.016,'opal_diffuser',.0005)
 # Opal shallow lens is housed in an actual metal gasket ring, not painted onto outer shell.
 ring('LIGHT_lower_diffuser_retaining_ring',rounded(.550,.257,.048),rounded(.514,.220,.038),.398,.410,'champagne_metal',.0005).location.y=-.041
 slab('LIGHT_recessed_opal_diffuser',.514,.220,.401,.411,'opal_diffuser',(0,-.041),r=.038,bevel=.0007)
 # Rear cap and distinct seam: a small service opening beyond the diffuser, with screw bosses.
 art('LIGHT_service_cap_label',.067,.017,basis((0,.1205,.438))@Matrix.Rotation(math.pi,4,'Y'),'label_service')
 box('LIGHT_rear_service_cap',(-.063,.109,.414),(.063,.120,.455),'ivory_enamel',.001)
 for x in [-.048,.048]:
  ob=slab('LIGHT_service_cap_screw_'+str(x),.007,.007,0,.004,'champagne_metal',r=.002,bevel=.0002);ob.matrix_world=basis((x,.121,.436))@Matrix.Rotation(math.pi,4,'Y')
 box('LIGHT_cable_feed_recess',(-.012,.040,.019),(.012,.044,.030),'dark_rubber',.0005)
 slab('LIGHT_toggle_surround',.032,.024,.039,.043,'dark_rubber',(0,-.019),r=.004,bevel=.0005)
 slab('LIGHT_toggle_rocker',.026,.017,.043,.048,'champagne_metal',(0,-.019),r=.004,bevel=.0005)
 marker('mount_contact',(0,0,0),(0,0,-1),'physical_contact','Bottom of mating shoe on existing receiver plate. Support datum, not floor datum')
 marker('source_receiver',(0,-.047,.430),(0,0,-1),'source_receiver','Proposed replaceable light-source centre, inside physical housing; electrical/light operation pending')
 marker('diffuser_face',(0,-.041,.401),(0,0,-1),'physical_surface','Actual lower lens face; proposed light direction -Z. No runtime light exported')
 marker('toggle',(0,-.019,.048),(0,0,1),'interaction_proposal','Physical rocker crown; runtime action and reach pending')
 marker('service_access',(0,.121,.436),(0,1,0),'service_proposal','Rear represented fixed cap faces +Y; .16 m service workspace only, no supplied opening trajectory')
 marker('cable_feed',(0,.044,.024),(0,1,0),'service_proposal','Rear low-voltage feed recess; cable route, supply and safety certification pending')
 collision_box('mount_foot',(-.053,-.0425,0),(.053,.0425,.048))
 spine_points=[(0,.019,.039),(0,.026,.269),(0,.083,.374),(0,.083,.437)]
 for j,(a,b) in enumerate(zip(spine_points,spine_points[1:])):
  a,b=Vector(a),Vector(b);collision_obb('spine_segment_'+str(j),(a+b)/2,(.042,(b-a).length,.030),(b-a).normalized())
 hood_mid=[(-.190,.408),(-.175,.438),(-.136,.469),(-.060,.4805),(.048,.4705),(.0985,.4455),(.1105,.414)]
 for j,(a,b) in enumerate(zip(hood_mid,hood_mid[1:])):
  a,b=Vector((0,*a)),Vector((0,*b));collision_obb('hood_wall_segment_'+str(j),(a+b)/2,(.564,(b-a).length,.019),(b-a).normalized())
 collision_obb('hood_shell_left',(-.284,-.04,.442),(.010,.310,.090),(0,1,0));collision_obb('hood_shell_right',(.284,-.04,.442),(.010,.310,.090),(0,1,0))
 collision_box('diffuser_panel',(-.257,-.151,.401),(.257,.069,.411),'Thin panel preserves service/reflector cavity rather than one enclosing hood hull')
 return {'catalogue_id':'AST-LIB-008','name':'Astraea Housed Study Task Fixture','datum':'Receiver contact plane Z0; not floor origin','intent':'A shaped fixed task fixture for existing study receiver plates; sculpted open hood, bent reflector, source carrier and represented fixed rear service cover','compatible_mounts':[{'asset':'AST-LIB-STUDY-01','receiver_source_m':[0,0,.754],'fixture_translation_source_m':[0,0,.754],'receiver_plate_size_m':[.14,.09],'mating_shoe_size_m':[.084,.070],'edge_clearance_xy_m':[.028,.010]},{'asset':'AST-LIB-STUDY-02','receiver_source_m':[-.433,.286,.756],'fixture_translation_source_m':[-.433,.286,.756],'receiver_plate_size_m':[.09,.12],'mating_shoe_size_m':[.084,.070],'edge_clearance_xy_m':[.003,.025]}],'clear_volumes_source_m':[{'name':'rear_service_workspace','min':[-.075,.122,.410],'max':[.075,.282,.475]}],'runtime_status':'No light object, electrical behavior, switching, animation or material self-emission exported. Fixed housing geometry only'}

def browser():
 for x,lab in [(-.566,'L'),(.566,'R')]:
  for y,tag in [(-.25,'front'),(.205,'rear')]:slab('BROWSER_'+lab+'_'+tag+'_floor_pad',.066,.080,0,.025,'dark_rubber',(x,y),r=.014,bevel=.001)
  # Bifurcated side profile retains an open triangle and broad independent floor bearings.
  p=[(-.286,.018),(-.258,.117),(-.208,.425),(-.060,.717),(.120,1.196),(.169,1.22),(.218,1.208),(.220,1.168),(.075,.675),(-.148,.382),(-.204,.107),(-.231,.018)]
  extrude('BROWSER_'+lab+'_swept_front_bearing',p,x-.034,x+.034,'ivory_enamel',axis='x',grain='z',bevel=0)
  p=[(.178,.018),(.238,.018),(.240,.132),(.203,.451),(.191,.724),(.208,1.205),(.158,1.209),(.132,.721),(.143,.424),(.165,.107)]
  extrude('BROWSER_'+lab+'_rear_bearing',p,x-.032,x+.032,'ivory_enamel',axis='x',grain='z',bevel=.003)
 slab('BROWSER_open_archive_shelf',1.14,.391,.232,.267,'warm_walnut',(0,-.004),r=.035,bevel=.003)
 beam('BROWSER_archive_rear_rail',(-.57,.178,.282),(.57,.178,.282),.040,.051,'ivory_enamel',.002)
 # Three honestly empty lower storage bays, no filled hull.
 for x in [-.18,.18]:box('BROWSER_archive_divider_'+str(x),(x-.009,-.17,.267),(x+.009,.169,.436),'warm_walnut',.0015)
 art('BROWSER_archive_storage_label',.442,.036,basis((0,-.201,.248)),'label_archive')
 up=Vector((0,.438,.899)).normalized();normal=Vector((0,-up.z,up.y))
 for row,center in [('lower',(0,-.143,.678)),('upper',(0,.015,1.032))]:
  mat=basis(center,up)
  place(extrude('BROWSER_'+row+'_sloped_browse_tray',rounded(1.085,.324,.018),-.023,0,'warm_walnut',bevel=.002),mat)
  # Lip projects forward, without obscuring cover title or a hand-size gap between columns.
  place(box('BROWSER_'+row+'_retaining_lip',(-.555,-.167,-.004),(.555,-.147,.031),'champagne_metal',.001),mat)
  for x in [-.545,.545]:place(box('BROWSER_'+row+'_tray_endstop_'+str(x),(x-.009,-.148,0),(x+.009,.140,.024),'ivory_enamel',.001),mat)
  for j,(x,role,cover) in enumerate([(-.365,'book_cover_teal','periodical_orbit'),(0,'book_cover_clay','periodical_terra'),(.365,'book_cover_ochre','periodical_form')]):
   m=mat@Matrix.Translation((x,.008,.012))
   place(box('BROWSER_'+row+'_journal_%s_bound_board'%j,(-.151,-.151,-.009),(.151,.151,.006),role,.0006),m)
   place(box('BROWSER_'+row+'_journal_%s_leaf_block'%j,(-.147,-.146,-.006),(.147,.146,.004),'book_paper_edges',.0003),m)
   art('BROWSER_'+row+'_journal_%s_original_front_cover'%j,.296,.297,m@Matrix.Translation((0,0,.0064)),cover)
   pt=mat@Vector((x,.008,.0184));marker(row+'_journal_'+str(j+1),pt,normal,'interaction_proposal','Face-out title centre; grasp or remove action and species reach pending. Tier centre '+str(round(pt.z,3))+' m')
  collision_obb(row+'_tray',center,(1.085,.324,.025),up)
  for x in [-.51,.51]:
   # Housed short bracket is visible at tray/side-frame contact.
   beam('BROWSER_'+row+'_end_bearing_'+str(x),(x,center[1]+.020,center[2]-.06),(x,center[1]+.126,center[2]+.080),.048,.035,'ivory_enamel',.0015)
 art('BROWSER_current_issue_header',.46,.024,basis((0,.0628,1.223)),'label_current')
 beam('BROWSER_top_header_backing',(-.551,.086,1.223),(.551,.086,1.223),.045,.028,'ivory_enamel',.0015)
 marker('floor_contact_left',(-.566,-.25,0),(0,0,-1),'physical_contact','Actual front floor pad base')
 marker('floor_contact_right',(.566,-.25,0),(0,0,-1),'physical_contact','Actual front floor pad base')
 marker('archive_shelf',(0,-.004,.267),(0,0,1),'physical_surface','Open lower shelf; back issues/storage, no supplied stored content')
 marker('approach',(0,-.90,0),(0,1,0),'pose_proposal','Proposed standing or seated browse approach centre, not a body fit claim')
 collision_box('archive_shelf',(-.57,-.2,.232),(.57,.192,.267))
 for x in [-.18,.18]:collision_box('archive_divider_'+str(x),(x-.009,-.17,.267),(x+.009,.169,.436),'Thin fixed divider; preserves three separate lower storage bays')
 for x in [-.566,.566]:
  for yy in [-.25,.205]:collision_box('floor_pad_'+str(x)+'_'+str(yy),(x-.033,yy-.040,0),(x+.033,yy+.040,.026))
  paths={'front':[(x,-.258,.020),(x,-.232,.115),(x,-.178,.4035),(x,.0075,.696),(x,.170,1.185),(x,.188,1.207)],'rear':[(x,.208,.024),(x,.2025,.12),(x,.173,.438),(x,.1615,.724),(x,.183,1.198)]}
  for side,path in paths.items():
   for j,(a,b) in enumerate(zip(path,path[1:])):
    a,b=Vector(a),Vector(b);collision_obb('end_'+str(x)+'_'+side+'_bearing_'+str(j),(a+b)/2,(.068,(b-a).length+.014,.060),(b-a).normalized())
 return {'catalogue_id':'AST-LIB-009','name':'Astraea Low Periodical Browser','datum':'Floor plane Z0 at centre','intent':'Six readable face-out journal groups on two staggered slopes, lower browsing centre 0.69 m and upper centre 1.047 m; open lower back-issue storage. Fixed stocked visual component, no removable-book interaction yet','stock_titles':['ORBIT / SKY FIELD','TERRA / LIVING SYSTEMS','FORM / CRAFT DESIGN'],'tier_width_m':1.085,'cover_width_m':.296,'intergroup_cover_gap_m':.069,'clear_volumes_source_m':[{'name':'front_browse_approach','min':[-.52,-1.15,0],'max':[.52,-.31,1.35]},{'name':'lower_archive_opening','min':[-.52,-.17,.270],'max':[.52,.145,.430],'qualification':'Two thin dividers at X +/- .18 partition this opening; no general navigation passage'}],'runtime_status':'Fixed visual mesh, no animation; all access/selection behavior pending original game and actor verification'}

def terminal():
 for x,lab in [(-.283,'L'),(.283,'R')]:
  slab('TERM_'+lab+'_floor_pad',.121,.515,0,.026,'dark_rubber',(x,.011),r=.039,bevel=.0015)
  # Shaped ski foot feeds a swept narrow side support. Central foot and knee region stays open.
  p=[(-.250,.024),(-.214,.069),(-.141,.092),(.136,.070),(.232,.038),(.257,.026)]
  extrude('TERM_'+lab+'_sculpted_foot',p,x-.060,x+.060,'ivory_enamel',axis='x',bevel=.003)
  p=[(.074,.059),(.164,.053),(.184,.332),(.159,.609),(.064,.878),(.046,.997),(-.021,1.015),(-.009,.857),(.081,.600),(.105,.327)]
  extrude('TERM_'+lab+'_swept_load_spine',p,x-.031,x+.031,'ivory_enamel',axis='x',grain='z',bevel=.003)
  beam('TERM_'+lab+'_timber_inner_join',(x,.109,.719),(x,-.016,.959),.085,.038,'warm_walnut',.0015)
 # A narrow rear brace, not a panel closing the knees.
 beam('TERM_rear_service_bridge',(-.302,.129,.702),(.302,.129,.702),.071,.041,'warm_walnut',.002)
 box('TERM_rear_fixed_service_case',(-.196,.082,.744),(.196,.158,.944),'ivory_enamel',.004)
 art('TERM_rear_service_label',.151,.026,basis((0,.159,.833))@Matrix.Rotation(math.pi,4,'Y'),'label_service')
 for x in [-.17,.17]:box('TERM_service_fastener_'+str(x),(x-.006,.159,.897),(x+.006,.165,.909),'champagne_metal',.001)
 for x in [-.133,-.098,-.063,-.028,.007,.042,.077,.112]:box('TERM_rear_vent_'+str(x),(x,.1585,.769),(x+.016,.160,.803),'dark_rubber',.0005)
 # Thick framed angled display, recessed glazing and tactile walnut cheeks.
 up=Vector((0,.27,.96286)).normalized();mat=basis((0,.003,1.206),up)
 place(extrude('TERM_shaped_back_shell',rounded(.684,.426,.066),-.081,-.023,'ivory_enamel',bevel=.003),mat)
 place(ring('TERM_walnut_display_frame',rounded(.684,.426,.066),rounded(.584,.326,.023),-.026,.013,'warm_walnut',.002),mat)
 place(ring('TERM_recessed_inner_gasket',rounded(.593,.335,.026),rounded(.560,.303,.013),-.018,.004,'dark_rubber',.0006),mat)
 place(extrude('TERM_recessed_display_glazing',rounded(.562,.306,.014),-.016,-.006,'display_glass',bevel=.0004),mat)
 art('TERM_original_catalogue_display',.554,.296,mat@Matrix.Translation((0,0,-.0054)),'catalogue_screen')
 # Positive lower bearing tongue mates head to control deck/side spars.
 beam('TERM_display_lower_bearing',(-.276,-.045,1.000),(.276,-.045,1.000),.052,.057,'champagne_metal',.0015)
 deckup=Vector((0,.964,.266)).normalized();deck=basis((0,-.114,.959),deckup)
 place(extrude('TERM_control_pod_sculpted_body',rounded(.716,.227,.040),-.061,0,'ivory_enamel',bevel=.0025),deck)
 place(ring('TERM_control_pod_walnut_edge',rounded(.722,.235,.042),rounded(.676,.190,.025),-.012,.009,'warm_walnut',.001),deck)
 # Individual physical buttons are large enough to distinguish in ordinary views.
 for x,role,lab,w in [(-.232,'label_back','BACK',.100),(-.082,'label_search','SEARCH',.151),(.102,'label_map','INDEX',.140)]:
  m=deck@Matrix.Translation((x,0,.009));place(extrude('TERM_'+lab+'_key_surround',rounded(w+.013,.110,.016),0,.004,'dark_rubber',bevel=.0007),m)
  place(extrude('TERM_'+lab+'_physical_key',rounded(w,.096,.013),.003,.014,'champagne_metal',bevel=.0007),m)
  art('TERM_'+lab+'_key_label',w*.84,.022,m@Matrix.Translation((0,0,.0144)),role)
  p=m@Vector((0,0,.0144));marker('control_'+lab.lower(),p,deck.col[2][:3],'interaction_proposal','Distinct physical '+lab+' key crown; input binding and functional result pending')
 # A separate scalloped selection dial with pointer and label.
 p=[(.041*math.cos(i*math.tau/12),.041*math.sin(i*math.tau/12)) for i in range(12)];m=deck@Matrix.Translation((.263,0,.010))
 place(extrude('TERM_selection_dial',p,0,.025,'champagne_metal',bevel=.001),m)
 place(box('TERM_selection_dial_pointer',(-.003,.018,.025),(.003,.032,.026),'dark_rubber',.0001),m)
 art('TERM_select_dial_label',.082,.015,deck@Matrix.Translation((.263,-.081,.011)),'label_select')
 marker('control_select',m@Vector((0,0,.025)),deck.col[2][:3],'interaction_proposal','Physical rotary selector; fixed geometry. No rotation animation or input is implemented')
 marker('display_surface',mat@Vector((0,0,-.0054)),mat.col[2][:3],'physical_surface','Actual catalogue artwork surface within framed display, not a room map or working screen')
 marker('standing_use',(0,-.86,0),(0,1,0),'pose_proposal','Body-scale proposed standing use datum; control heights measured separately; species fit pending')
 marker('seated_use',(0,-.65,0),(0,1,0),'pose_proposal','Candidate seated approach, central foot/knee void retained; accessibility/rig verification pending')
 marker('rear_service',(0,.165,.833),(0,1,0),'service_proposal','Represented fixed back service cover; proposed .30 m workspace, no supplied removal trajectory')
 marker('floor_left',(-.283,.011,0),(0,0,-1),'physical_contact','Actual ski pad bottom at floor plane')
 marker('floor_right',(.283,.011,0),(0,0,-1),'physical_contact','Actual ski pad bottom at floor plane')
 for x in [-.283,.283]:
  collision_box('ski_foot_'+str(x),(x-.061,-.250,0),(x+.061,.268,.095))
  collision_box('side_spine_'+str(x),(x-.032,-.021,.095),(x+.032,.184,.997),'Conservative separate support only; refinement required around sweep, central void preserved')
 collision_obb('head',(0,.003,1.206),(.684,.426,.081),up);collision_obb('control_pod',(0,-.114,.945),(.722,.235,.065),deckup)
 collision_box('rear_service',(-.196,.082,.744),(.196,.158,.944))
 return {'catalogue_id':'AST-LIB-010','name':'Astraea Catalogue Terminal Stand','datum':'Floor plane Z0 at centre','intent':'Sculpted framed catalogue screen with original collection-index art and four individually legible controls; swept side supports preserve central foot/knee opening','screen_content':'Original static FIND A BOOK / BROWSE catalogue with abstract collection index; does not invent missing ship layout','clear_volumes_source_m':[{'name':'central_knee_void','min':[-.220,-.340,.105],'max':[.220,.075,.732]},{'name':'front_approach','min':[-.450,-1.20,0],'max':[.450,-.270,1.75]}],'runtime_status':'Static screen art and fixed physical controls only. Search/index/back/select actions, display updates, actor reach and species fit all pending'}

def stats(obs):
 dg=bpy.context.evaluated_depsgraph_get();pts=[];records=[];tris=0
 for ob in obs:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];pts+=vs;tris+=len(me.loop_triangles)
  records.append({'name':ob.name,'material_role':ob['semantic_role'],'bounds_min_source_m':[min(v[i] for v in vs) for i in range(3)],'bounds_max_source_m':[max(v[i] for v in vs) for i in range(3)],'triangles':len(me.loop_triangles),'retained_modifiers':[m.type for m in ob.modifiers]});eo.to_mesh_clear()
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 return {'bounds_min_source_m':lo,'bounds_max_source_m':hi,'dimensions_blender_xyz_m':[hi[i]-lo[i] for i in range(3)],'evaluated_triangles':tris,'editable_parts':records}

def finish(info):
 cid=info['catalogue_id'];root=bpy.data.objects.new(cid+'_root',None);bpy.context.collection.objects.link(root);root['catalogue_id']=cid;root['datum']=info['datum'];root['interaction_status']='Proposals only; no runtime actions';root['source_axes']='X right, Y depth, Z up, front -Y';root['exchange_axes']='X right, Y up, front +Z'
 for ob in PARTS+[m[0] for m in MARKERS]:ob.parent=root
 bpy.context.view_layer.update();info.update(stats(PARTS));assert abs(info['bounds_min_source_m'][2])<1e-6
 info.update({'source':'source/'+cid+'.blend','export':'exports/'+cid+'.glb','generator':'source/build_library_use.py','texture_generator':'source/make_use_art.py','units':'metres','material_roles':sorted(set(ob['semantic_role'] for ob in PARTS)),'coordinate_contract':{'source':'Blender local Z up, front -Y','exchange':'glTF Y up, front +Z','mapping':'(x,y,z) -> (x,z,-y)','root_source_m':[0,0,0],'root_exchange_m':[0,0,0]},'positions_and_normals':[m[1] for m in MARKERS],'animations':[],'authoring':'Original reproducible script-assisted shaped polygon construction; named semantic editable parts, low-segment edge easing; no downloaded mesh or copied reference pixels','provenance':'Independent catalogue continuation 2026-10-02. All four supplied library references and existing study/structure component images inspected for useful form and restraint. Original ship remains unavailable.','qa_scope':'Imported-GLB Blender component evidence only. No original room recreation, Godot adoption, ship lighting, crowd/species, physics or runtime-performance claim.','generator_sha256':sha(Path(__file__)),'texture_generator_sha256':sha(ROOT/'source/make_use_art.py'),'source_blender_version':bpy.app.version_string,'export_settings':{'format':'GLB','Y_up':True,'semantic_static_meshes':1,'embedded_material_textures':True,'extras':True,'cameras':False,'lights':False,'collision':'Separate modest proposals only','marker_nodes':'Explicit source/exchange record nodes retained in exported hierarchy'}})
 coll={'catalogue_id':cid,'scope':'Numeric proposals only; no runtime collision export or physics testing','coordinates':'Both source Z-up and exchange Y-up explicitly labelled; source oriented-box basis is local X/Y/Z','preserved_openings':info['clear_volumes_source_m'],'shapes':SHAPES};(ROOT/(cid+'.collision_proposals.json')).write_text(json.dumps(coll,indent=2))
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/info['source']),compress=True)
 bpy.ops.object.select_all(action='DESELECT');dg=bpy.context.evaluated_depsgraph_get();copies=[]
 for ob in PARTS:
  eo=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=dg)
  if not ob['art_uv']:metric(me,ob['semantic_role'],ob['grain_axis'])
  active=me.uv_layers.active
  for l in list(me.uv_layers):
   if l!=active:me.uv_layers.remove(l)
  active.name='UV_Metric_Metres';active.active_render=True
  cp=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(cp);cp.matrix_world=ob.matrix_world.copy();cp.select_set(True);copies.append(cp)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();visual=bpy.context.object;visual.name=cid+'_static_visual';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);visual.parent=root;visual['editable_source_part_count']=len(PARTS)
 root.select_set(True)
 for ob,_ in MARKERS:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/info['export']),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False)
 info['source_sha256']=sha(ROOT/info['source']);info['export_sha256']=sha(ROOT/info['export']);info['source_semantic_mesh_count']=len(PARTS)
 (ROOT/(cid+'.manifest.json')).write_text(json.dumps(info,indent=2));return info

if __name__=='__main__':
 records=[]
 for maker in [lamp,browser,terminal]:reset();records.append(finish(maker()))
 deps=[BASE/'standards/materials.py',BASE/'materials/material_manifest.json',BASE/'assets/library_contents/texture_manifest.json']
 roles=set(r for a in records for r in a['material_roles'])
 mm=json.loads((BASE/'materials/material_manifest.json').read_text())['materials'];bm=json.loads((BASE/'assets/library_contents/texture_manifest.json').read_text())
 for record in mm.values():deps.append(BASE/'materials'/record['base_color_file'])
 for role in roles:
  if role in bm['materials']:deps.append(BASE/'assets/library_contents'/bm['texture_root']/bm['materials'][role]['base_color_file'])
 (ROOT/'dependency_manifest.json').write_text(json.dumps({'revision':'library-use-dependencies-01','path_base':'catalogue root','unchanged_shared_dependencies':[{'path':str(p.relative_to(BASE)),'sha256':sha(p)} for p in sorted(set(deps))],'local_dependencies':['source/build_library_use.py','source/make_use_art.py','texture_manifest.json','textures/*.png'],'build_order':['python assets/library_use/source/make_use_art.py','blender --background --threads 2 --python-exit-code 1 --python assets/library_use/source/build_library_use.py'],'qa_render_dependencies_required_for_source_rebuild':False,'runtime':'GLBs embed all geometry and textures; no external paths needed','reference_use':'Four portable library references recorded in batches/batch09/reference_manifest.json; pixels inspected, no pixel or geometry copying'},indent=2))
 (ROOT/'manifest.json').write_text(json.dumps({'family':'library_use','unique_asset_count':3,'asset_ids':[a['catalogue_id'] for a in records],'assets':[{'catalogue_id':a['catalogue_id'],'name':a['name'],'source':a['source'],'export':a['export'],'generator':a['generator'],'dimensions_blender_xyz_m':a['dimensions_blender_xyz_m'],'evaluated_triangles':a['evaluated_triangles'],'material_roles':a['material_roles']} for a in records],'scope':'Independent fixed library-use components; original game absent; integration and behavior pending'},indent=2))
 print('LIBRARY_USE_BUILT',[(r['catalogue_id'],r['evaluated_triangles'],r['dimensions_blender_xyz_m']) for r in records])
