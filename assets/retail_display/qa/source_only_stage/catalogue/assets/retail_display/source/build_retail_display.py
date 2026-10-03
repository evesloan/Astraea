"""Original Batch18 recessed retail bay and stepped display island.
Blender 4.3.2; metres/source XYZ Z-up front -Y. No host scene, stock or new mechanisms.
Input closure: this file, standards/{materials,retail_materials}.py and every
image/manifest those helpers load. All geometry and metric UVs authored here.
No exporter-only UV repair, font or third-party artwork dependency.
"""
import bpy,bmesh,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]; CAT=BASE.parents[1]
for p in ('source','exports','qa','actor_proxies'):(BASE/p).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('retail_materials',CAT/'standards/retail_materials.py'); mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm);MATS=mm.materials()
W='ivory_enamel'; T='retail_terracotta_enamel'; D='dark_rubber'; O='warm_walnut'; M='champagne_metal'
ALL=[]; COLL={}; BODIES={}; MARKER_API={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gl(p):return [float(p[0]),float(p[2]),-float(p[1])]
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,VOIDS,PATCHES,PROFILES,BODY
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident;ROOT['source_frame']='metres XYZ Z-up front -Y';ROOT['exchange_frame']='metres native GLB Y-up; source(x,y,z)->(x,z,-y)'
 PARTS=[];MARKERS=[];JOINS=[];VOIDS=[];PATCHES=[];PROFILES=[];BODY=[]
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident;sc['scope']='Original unplaced public-retail component; no host adoption, goods inventory, activity slot, payment or species fit'
def mesh(name,verts,faces,role,body=True,desc=''):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT;me.materials.append(MATS[role]);ob['material_role']=role;ob['movement_group']='static';ob['body_candidate_keep']=body;ob['authorship']='Original Batch18 retail display design';ob['part_purpose']=desc
 uv=me.uv_layers.new(name='metric_material_uv');sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3)if i!=axis]
  # Top wood follows longitudinal X in V. End grain uses vertical Z in V.
  if role==O and axis==2:axes=[1,0]
  for li in f.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
 PARTS.append(ob)
 if body:BODY.append({'role':'body','type':'convex_hull_points','semantic_parts':[name],'points_source_m':[list(v)for v in verts],'approximation':'Exact authored convex solid','max_outward_approximation_m':0,'max_omitted_detail_distance_m':0})
 return ob
def ex(n,p,axis,a,b,r,body=True,desc=''):
 axes=[i for i in range(3)if i!=axis];v=[]
 for d in (a,b):
  for q in p:
   z=[0,0,0];z[axis]=d;z[axes[0]]=q[0];z[axes[1]]=q[1];v.append(z)
 N=len(p);ob=mesh(n,v,[tuple(reversed(range(N))),tuple(N+i for i in range(N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)],r,body,desc)
 ob['profile_axis_source']=axis;ob['profile_coordinates_m']=json.dumps(p);ob['extrusion_range_m']=[a,b]
 PROFILES.append({'part':n,'profile_axis_source':axis,'polygon_m':p,'extrusion_range_m':[a,b]})
 return ob
def box(n,lo,hi,r,body=True,desc=''):
 return ex(n,[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])],2,lo[2],hi[2],r,body,desc)
def clip(x,X,y,Y,c):return[(x+c,y),(X-c,y),(X,y+c),(X,Y-c),(X-c,Y),(x+c,Y),(x,Y-c),(x,y+c)]
def marker(n,p,kind,part=None,normal=None,desc=''):
 ob=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(ob);ob.parent=ROOT;ob.location=p;ob.empty_display_size=.015;ob['marker_kind']=kind;ob['physical_part']=part.name if hasattr(part,'name')else part or '';ob['source_position_m']=p;ob['gltf_position_m']=gl(p)
 row={'name':n,'kind':kind,'source_m':list(p),'gltf_m':gl(p),'physical_part':ob['physical_part']or None,'description':desc}
 if normal:row.update(direction_source=normal,direction_gltf=gl(normal));ob['direction_source']=normal;ob['direction_gltf']=gl(normal)
 MARKERS.append(row)
def joint(n,a,b,p,kind='boundary_contact'):
 JOINS.append({'name':n,'parts':[a.name if hasattr(a,'name')else a,b.name if hasattr(b,'name')else b],'probe_source_m':p,'probe_gltf_m':gl(p),'kind':kind})
def void(n,lo,hi,purpose):
 VOIDS.append({'name':n,'min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]],'purpose':purpose,'state':'fixed'})
def patch(n,part,xy,z,purpose):
 PATCHES.append({'name':n,'physical_part':part.name,'polygon_source_m':[[x,y,z]for x,y in xy],'polygon_gltf_m':[gl([x,y,z])for x,y in xy],'normal_source':[0,0,1],'normal_gltf':[0,1,0],'purpose':purpose,'load_or_reach_claim':False})
 marker(n.upper()+'_CONTACT',[sum(x for x,y in xy)/len(xy),sum(y for x,y in xy)/len(xy),z],'physical_display_support',part,[0,0,1])

def bay():
 # An asymmetric, rising arch in front elevation. The left pylon is hollowed on
 # its entry-facing -X end, so its display purpose survives the +90 degree placement.
 sole=ex('recessed_faceted_floor_sole',clip(-1.65,1.65,-.35,.39,.09),2,0,.04,D)
 base=ex('continuous_shaped_pale_plinth',clip(-1.70,1.70,-.45,.43,.11),2,.04,.18,W)
 joint('plinth_on_floor_sole',base,sole,[0,0,.04])
 marker('FLOOR_CONTACT',[0,0,0],'physical_floor_contact',sole,[0,0,-1])
 outer=[(-1.70,.18),(-1.70,2.18),(-1.58,2.53),(-1.27,2.78),(-.82,2.90),(.98,2.90),(1.40,2.78),(1.62,2.56),(1.70,2.25),(1.70,.18)]
 inner=[(-1.29,.18),(-1.29,2.12),(-1.19,2.33),(-.99,2.49),(-.67,2.57),(.96,2.57),(1.20,2.50),(1.34,2.36),(1.38,2.16),(1.38,.18)]
 inset=[(-1.22,.18),(-1.22,2.10),(-1.12,2.28),(-.95,2.42),(-.64,2.495),(.945,2.495),(1.16,2.43),(1.27,2.31),(1.31,2.15),(1.31,.18)]
 shell=[];liners=[]
 # Lowermost left segment is a real side-facing recess, not an applied dark rectangle.
 lower=box('entry_pylon_lower_pier',[-1.70,-.40,.18],[-1.29,.43,1.00],W)
 upper=ex('entry_pylon_upper_pier',[(-1.70,1.88),(-1.29,1.88),inner[1],outer[1]],1,-.40,.43,W)
 cheekf=box('entry_pylon_forward_return',[-1.70,-.40,1.00],[-1.29,-.23,1.88],W)
 cheekb=box('entry_pylon_rear_return',[-1.70,.24,1.00],[-1.29,.43,1.88],W)
 rear=box('entry_recess_structural_back',[-1.40,-.23,1.00],[-1.29,.24,1.88],W)
 shell.append(upper)
 for i in range(1,len(outer)-1):
  ob=ex('pale_rising_surround_'+str(i).zfill(2),[outer[i],outer[i+1],inner[i+1],inner[i]],1,-.40,.43,W,False);shell.append(ob)
  # Compound body integrates the terracotta material return with its matching pale wedge.
  points=[[x,y,z]for y in(-.40,.43)for x,z in[outer[i],outer[i+1],inset[i+1],inset[i]]]
  BODY.append({'role':'body','type':'convex_hull_points','semantic_parts':[ob.name,'recessed_terracotta_return_'+str(i).zfill(2)],'points_source_m':points,'approximation':'Pale profile plus nested material return; fills only the 90mm shallow finish setback, preserves the true opening','max_outward_approximation_m':.09,'max_omitted_detail_distance_m':0})
 for i in range(len(inner)-1):
  ob=ex('recessed_terracotta_return_'+str(i).zfill(2),[inner[i],inner[i+1],inset[i+1],inset[i]],1,-.31,.40,T,i==0);liners.append(ob)
  p=[(inner[i][0]+inner[i+1][0])/2,0,(inner[i][1]+inner[i+1][1])/2]
  joint('nested_pale_terracotta_contact_'+str(i),rear if i==0 else shell[i],ob,p)
 # Dark arch back remains 90mm behind the recessed terracotta front return.
 back=ex('dark_inset_display_back',inset,1,.31,.40,D)
 joint('dark_back_lower_plinth',back,base,[0,.35,.18])
 for i in range(len(inset)-1):
  p=[(inset[i][0]+inset[i+1][0])/2,.35,(inset[i][1]+inset[i+1][1])/2];joint('dark_back_arch_contact_'+str(i),back,liners[i],p)
 # Explicit fitted wall contact pads are proposals, not drilled host anchors.
 for x,t in[(-1.50,'left'),(1.53,'right')]:
  pad=box(t+'_rear_wall_mount_pad',[x-.045,.43,1.92],[x+.045,.45,2.02],M)
  joint(t+'_mount_to_structure',pad,upper if x<0 else shell[-1],[x,.43,1.97])
  marker(t.upper()+'_WALL_MOUNT',[x,.45,1.97],'proposed_wall_contact',pad,[0,1,0],desc='Actual pad face; host anchorage/wall/support unknown')
 # Entry-facing recess has 20mm orange returns and a real dark back at x=-1.425.
 for y,t in[(-.23,'front'),(.22,'rear')]:
  rail=box('entry_recess_'+t+'_terracotta_return',[-1.70,y,1.00],[-1.425,y+.02,1.88],T)
  joint('entry_'+t+'_lining',rail,cheekf if y<0 else cheekb,[-1.55,-.23 if y<0 else .24,1.40])
 erback=box('entry_recess_dark_back',[-1.425,-.21,1.03],[-1.40,.22,1.85],D)
 etop=box('entry_recess_terracotta_head',[-1.70,-.21,1.85],[-1.40,.22,1.88],T)
 efloor=box('entry_recess_tactile_display_sill',[-1.70,-.21,1.00],[-1.40,.22,1.03],O)
 joint('entry_sill_pier',efloor,lower,[-1.55,0,1.00]);joint('entry_head_pier',etop,upper,[-1.55,0,1.88]);joint('entry_back_structure',erback,rear,[-1.40,0,1.4])
 marker('ENTRY_FACING_REVEAL_BACK',[-1.425,0,1.44],'physical_entry_reveal_back',erback,[-1,0,0])
 void('entry_facing_display_recess',[-1.695,-.205,1.035],[-1.43,.215,1.845],'Side-facing useful display/retrieval recess; no inventory or hand-fit claim')
 # Open lower storage and tactile main surface remain useful empty volumes.
 floor=box('lower_storage_tactile_floor',[-1.22,-.34,.18],[1.31,.31,.23],O)
 joint('storage_floor_plinth',floor,base,[0,0,.18])
 dividers=[]
 for x,t in[(-.41,'left'),(.43,'right')]:
  ob=box(t+'_open_storage_divider',[x,-.32,.23],[x+.04,.31,.83],W);dividers.append(ob);joint(t+'_divider_floor',ob,floor,[x+.02,0,.23])
 top=ex('main_display_work_slab',clip(-1.22,1.31,-.447,.31,.065),2,.83,.95,O)
 for ob in dividers:joint(ob.name+'_slab',ob,top,[ob.data.vertices[0].co.x+.02,0,.83])
 for x,t in[(-1.22,'left'),(1.31,'right')]:joint(t+'_work_slab_return',top,liners[0 if x<0 else -1],[x,0,.90])
 # Fine inset metal edge belongs to the front face below the primary support plane.
 band=box('main_slab_recessed_edge_strip',[-1.12,-.450,.867],[1.21,-.447,.885],M,False)
 joint('edge_strip_slab',band,top,[0,-.447,.876])
 upright=box('upper_timber_display_mullion',[.40,.01,.95],[.47,.31,2.495],O)
 joint('mullion_main_top',upright,top,[.435,.16,.95]);joint('mullion_arch_head',upright,liners[4],[.435,.16,2.495])
 shelfA=box('left_supported_display_shelf',[-1.22,-.16,1.46],[.40,.31,1.52],O)
 shelfB=box('right_supported_display_shelf',[.47,-.08,1.88],[1.31,.31,1.94],O)
 for name,ob,a,b,z in[('left',shelfA,-1.22,.40,1.49),('right',shelfB,.47,1.31,1.91)]:
  joint(name+'_shelf_mullion',ob,upright,[b if name=='left'else a,.16,z]);joint(name+'_shelf_side_return',ob,liners[0 if name=='left'else -1],[a if name=='left'else b,.16,z]);joint(name+'_shelf_back',ob,back,[(a+b)/2,.31,z])
 # First and last shelves deliberately terminate at the inner opening faces.
 patch('main_display_left_patch',top,[(-1.08,-.36),(.28,-.36),(.28,.23),(-1.08,.23)],.95,'Primary bare display/work surface; prospective container support')
 patch('main_display_right_patch',top,[(.55,-.34),(1.17,-.34),(1.17,.22),(.55,.22)],.95,'Secondary clear parcel/display surface')
 patch('left_shelf_patch',shelfA,[(-1.12,-.13),(.30,-.13),(.30,.26),(-1.12,.26)],1.52,'True supported display shelf; prospective small container patch')
 patch('right_shelf_patch',shelfB,[(.53,-.05),(1.25,-.05),(1.25,.26),(.53,.26)],1.94,'Narrower upper surface; container footprint must be independently tested')
 patch('entry_sill_patch',efloor,[(-1.68,-.19),(-1.44,-.19),(-1.44,.20),(-1.68,.20)],1.03,'Small entry-facing display surface, distinct from main front')
 for lo,hi,t in[([-1.20,-.33,.235],[-.42,.30,.825],'left'),([-.36,-.33,.235],[.42,.30,.825],'middle'),([.48,-.33,.235],[1.29,.30,.825],'right')]:void('lower_open_storage_'+t,lo,hi,'Useful open lower storage/retrieval; no door sweep or capacity assignment')
 void('left_main_display_void',[-1.20,-.155,.955],[.39,.30,1.455],'Open display volume above primary top and below left shelf')
 void('left_upper_display_void',[-1.15,-.13,1.525],[.38,.30,2.20],'Open upper alcove below rising profile')
 void('right_tall_display_void',[.48,-.075,.955],[1.29,.30,1.875],'Tall display alcove beside timber mullion')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',desc='Floor source pivot within supported plinth')
 return 'Rising recessed retail display bay',{'outer_elevation_profile_source_xz_m':outer,'pale_opening_profile_source_xz_m':inner,'terracotta_opening_profile_source_xz_m':inset,'entry_facing_end':'source -X; becomes arrangement -Y under yaw +90 degrees','front_source':'-Y','wall_plane_proposal_source_y_m':.45,'floor_plane_source_z_m':0,'junction_proposal':'Self-contained fitted floor/wall module; host wall, local ceiling, anchors and adjacent junctions unverified','mechanism':'None; permanently open display and storage','fixture':'No powered fixture or runtime illumination'}

def island():
 sole=ex('inset_faceted_floor_sole',clip(-.81,.81,-.56,.56,.12),2,0,.035,D)
 base=ex('grounded_octagonal_pale_plinth',clip(-.86,.86,-.61,.61,.14),2,.035,.18,W)
 joint('plinth_floor_sole',base,sole,[0,0,.035]);marker('FLOOR_CONTACT',[0,0,0],'physical_floor_contact',sole,[0,0,-1])
 # Side cheeks and rear structural core leave a genuine front storage pocket.
 left=ex('left_faceted_support_cheek',[(-.78,-.46),(-.68,-.56),(-.55,-.56),(-.55,.52),(-.66,.52),(-.78,.40)],2,.18,.63,W)
 right=ex('right_faceted_support_cheek',[(.55,-.56),(.68,-.56),(.78,-.46),(.78,.40),(.66,.52),(.55,.52)],2,.18,.63,W)
 core=box('rear_display_support_core',[-.55,-.015,.18],[.55,.52,.63],W)
 floor=box('front_retrieval_tactile_floor',[-.55,-.54,.18],[.55,-.015,.225],O)
 back=box('front_retrieval_dark_back',[-.55,-.030,.225],[.55,-.015,.63],D)
 for t,ob,p in[('left',left,[-.64,0,.18]),('right',right,[.64,0,.18]),('rear',core,[0,.25,.18]),('floor',floor,[0,-.25,.18])]:joint(t+'_to_plinth',ob,base,p)
 low=ex('broad_low_display_terrace',clip(-.95,.95,-.70,.70,.20),2,.63,.69,O)
 for t,ob,p in[('left',left,[-.65,0,.63]),('right',right,[.65,0,.63]),('rear',core,[0,.25,.63])]:joint(t+'_terrace_support',ob,low,p)
 # Raised rear mass is smaller and offset, exposing the long low front terrace.
 lip=ex('raised_tier_pale_foot',clip(-.57,.85,-.005,.64,.11),2,.69,.73,W)
 tier=ex('raised_terracotta_facet_support',clip(-.53,.81,.035,.60,.105),2,.73,.99,T)
 high=ex('offset_high_display_tablet',clip(-.59,.87,-.025,.66,.13),2,.99,1.05,O)
 joint('raised_foot_low_terrace',lip,low,[.1,.3,.69]);joint('terracotta_support_foot',tier,lip,[.1,.3,.73]);joint('high_tablet_support',high,tier,[.1,.3,.99])
 # A recessed metal line emphasizes the step without pretending to be controls.
 line=box('raised_front_recessed_metal_datum',[-.38,.030,.815],[.66,.035,.832],M,False)
 joint('step_datum_support',line,tier,[.10,.035,.8235])
 patch('low_front_display_patch',low,[(-.72,-.58),(.72,-.58),(.72,-.07),(-.72,-.07)],.69,'Broad low approach-facing terrace; container support must fit this exact patch')
 patch('high_display_patch',high,[(-.42,.07),(.70,.07),(.70,.53),(-.42,.53)],1.05,'Raised stepped display patch with lower circumferential retrieval edge')
 patch('front_retrieval_floor_patch',floor,[(-.49,-.49),(.49,-.49),(.49,-.06),(-.49,-.06)],.225,'Open storage floor; no inventory or capacity claim')
 void('front_retrieval_pocket',[-.54,-.535,.230],[.54,-.035,.625],'Actual lower front pocket preserved by detailed and body collision proposal')
 void('low_terrace_clear_volume',[-.70,-.57,.695],[.70,-.07,1.20],'True open volume above the low tier; no body/reach claim')
 void('high_terrace_clear_volume',[-.42,.07,1.055],[.70,.53,1.55],'Open display volume over raised tablet, no stock content included')
 marker('FRONT_RETRIEVAL_BACK',[0,-.030,.42],'physical_recess_back',back,[0,-1,0]);marker('FLOOR_ORIGIN',[0,0,0],'placement_origin',desc='Floor pivot inside grounded plinth')
 return 'Offset stepped merchandise island',{'levels_source_z_m':[.69,1.05],'appearance':'Faceted continuous low wood terrace, offset terracotta upper tier and grounded pale open-pocket pedestal','public_approach_source':'front -Y and side edges','mechanism':'None; fixed tiers and open retrieval pocket','mount':'Floor-supported proposal; no host anchorage or structural rating'}

def bounds(parts):
 points=[ob.matrix_world@v.co for ob in parts for v in ob.data.vertices];lo=[min(p[i]for p in points)for i in range(3)];hi=[max(p[i]for p in points)for i in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]}
def export(ident,markers):
 grouped={};runtime=[]
 for ob in PARTS:
  cp=bpy.data.objects.new('runtime_'+ob.name,ob.data.copy());bpy.context.collection.objects.link(cp);cp.matrix_world=ob.matrix_world.copy();grouped.setdefault(ob['material_role'],[]).append(cp)
 for role,items in grouped.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in items:ob.select_set(True)
  bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();ob=items[0];ob.name=ident+'__'+role;ob.parent=ROOT;ob['material_role']=role;ob['semantic_parts']=json.dumps([x.name for x in PARTS if x['material_role']==role]);runtime.append(ob)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for ob in runtime:ob.select_set(True)
 for ob in markers:ob.select_set(True)
 bpy.context.view_layer.objects.active=runtime[0]
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)
 return len(grouped)
def finish(ident,title,details):
 bpy.context.view_layer.update();bb=bounds(PARTS);markers=[ob for ob in ROOT.children if ob.type=='EMPTY'];tri=0
 for ob in PARTS:ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles)
 # Pack all loaded images, including unused material roles; source-only closure is broader than exported palette.
 for im in bpy.data.images:
  if im.source=='FILE':im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'))
 groups=export(ident,markers);bbg={'min_m':[bb['min_m'][0],bb['min_m'][2],-bb['max_m'][1]],'max_m':[bb['max_m'][0],bb['max_m'][2],-bb['min_m'][1]],'dimensions_m':[bb['dimensions_m'][0],bb['dimensions_m'][2],bb['dimensions_m'][1]]}
 record={'catalogue_id':ident,'name':title,'title':title,'unique_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_retail_display.py','source_frame':'metres Blender XYZ Z-up front -Y','exchange_frame':'metres native GLB Y-up source(x,y,z)->(x,z,-y)','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'floor origin'},'bounds_blender_z_up':bb,'bounds_gltf_y_up':bbg,'dimensions_blender_xyz_m':bb['dimensions_m'],'evaluated_source_triangles':tri,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[ob.name for ob in PARTS],'material_roles':sorted(set(ob['material_role']for ob in PARTS)),'export_mesh_groups':groups,'physical_and_proposal_markers':MARKERS,'joins':JOINS,'useful_voids':VOIDS,'support_patches':PATCHES,'whole_profile_records':PROFILES,'mechanisms':[],'state_derivatives':[],'collision_proposal_file':'collision_proposals.json','body_candidate_file':'actor_proxies/body_collision_subset.json','marker_api_file':'marker_api.json','used_textures_packed':True,'export_uv_repair':'None: authored per-face metric UVs are carried unchanged into grouped evaluated export','source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Proposed catalogue component only; R070 is a historical allocation, not a recovered finished shop','No actual host support, ceiling, door mechanism, activity slot, quantity, species fit, load, stability or operating certification','Optional detail/body collision proposals are not measured engine performance or runtime adoption']}
 (BASE/f'{ident}.manifest.json').write_text(json.dumps(record,indent=2)+'\n');ALL.append(record)
 detail=[{'role':'detail','type':'convex_hull_points','semantic_part':ob.name,'material_role':ob['material_role'],'points_source_m':[list(ob.matrix_world@v.co)for v in ob.data.vertices],'source_material_thickness_scope':'See actual full profile/extrusion; not an omitted-detail distance'}for ob in PARTS]
 COLL[ident]={'frame':'metres Blender XYZ Z-up; front -Y','role':'detail','shapes':detail,'shape_count':len(detail),'mechanisms':[],'limits':'Exact convex authored prisms; primary openings preserved. Engineering/runtime adoption unverified.'}
 BODIES[ident]={'role':'body','optional':True,'frame':'metres Blender XYZ Z-up; front -Y','shapes':BODY,'shape_count':len(BODY),'detailed_shape_count':len(detail),'omitted_detail':[{'semantic_part':ob.name,'maximum_distance_from_retained_body_m':.003 if ident.endswith('001')else .005,'material_thickness_m':.003 if ident.endswith('001')else .005,'reason':'Thin recessed ornamental metal datum; no grip or support role'}for ob in PARTS if not ob['body_candidate_keep'] and ob['material_role']==M],'performance':'Unmeasured engine-side selection; no target-PC claim','useful_voids_must_remain_open':[v['name']for v in VOIDS]}
 MARKER_API[ident]={'frame_source':'XYZ Z-up metres','frame_native':'GLB Y-up metres','markers':MARKERS,'support_patches':PATCHES}

for ident,build in [('AST-RTL-001',bay),('AST-RTL-002',island)]:reset(ident);title,details=build();finish(ident,title,details)
(BASE/'manifest.json').write_text(json.dumps({'family':'retail_display','batch':'18','revision':'retail-display-01','unique_design_count':2,'assets':[{'catalogue_id':r['catalogue_id'],'manifest':r['catalogue_id']+'.manifest.json','source':r['source'],'export':r['export']}for r in ALL],'reference':'batches/batch18/reference_manifest.json','prior_assets_changed':False},indent=2)+'\n')
(BASE/'collision_proposals.json').write_text(json.dumps({'frame':'Blender XYZ Z-up metres','assets':COLL},indent=2)+'\n')
(BASE/'actor_proxies/body_collision_subset.json').write_text(json.dumps({'scope':'Optional reduced body roles alongside exact detail roles','assets':BODIES},indent=2)+'\n')
(BASE/'marker_api.json').write_text(json.dumps(MARKER_API,indent=2)+'\n')
print('RETAIL_DISPLAY_BUILD_COMPLETE',[(r['catalogue_id'],r['editable_semantic_parts'],r['evaluated_triangles'],r['export_mesh_groups'])for r in ALL])
