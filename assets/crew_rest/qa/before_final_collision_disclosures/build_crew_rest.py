"""Original editable Astraea crew rest/curtain; source-only deterministic builder.
Only configured single-place dimensions are checked. No room/berth/species assignment.
Curtain is an authored constant-developed-width pleat model, not simulated cloth.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for d in('source','exports','qa'):(BASE/d).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('staff_materials',CAT/'standards/staff_materials.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib);M=lib.materials()
cloth=json.loads((BASE/'textures/manifest.json').read_text())
for role,row in cloth['materials'].items():
 mat=bpy.data.materials.new('ASTRAEA_'+role);mat.use_nodes=True;mat['astraea_material_role']=role;mat['material_revision']=cloth['revision'];mat['meters_per_tile_uv']=row['meters_per_tile_uv'];mat['intended_context']='crew_rest_original_cloth';mat.diffuse_color=tuple(v/255 for v in row['colour_srgb_8bit'])+(1,)
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=row['roughness'];tex=mat.node_tree.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(BASE/'textures'/row['file']),check_existing=True);im.pack();tex.image=im;tex.extension='REPEAT';mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);M[role]=mat
R={'paint':'staff_white_paint','frame':'staff_bluegrey_paint','metal':'staff_zinc','dark':'staff_rubber','label':'staff_label','sheet':'crew_ecru_sheet','blanket':'crew_terracotta_blanket','curtain':'crew_sage_privacy'}
ASSETS=[];API={};COLL={};POSES={}
# Exported configuration summary, not automated dimension controls.
# Change semantic meshes/coordinates and their interfaces together to resize; only this configuration is checked.
PARAM={'frame_width':1.08,'frame_length':2.20,'head_height':1.10,'rest_height':.534,'curtain_x':.68,'closed_leading_y':.02,'closed_span':2.16,'gathered_span':.36,'pleat_count':24,'closed_half_amplitude':.025,'fabric_bottom':.28,'fabric_top':2.015}
LSEG=math.sqrt((2.16/24)**2+.05**2);AOPEN=math.sqrt(LSEG**2-(.36/24)**2)/2
EXPR='(sqrt('+repr(LSEG**2)+'-((2.16-1.8*t)/24)**2)/2-.025)/'+repr(AOPEN-.025)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 bpy.context.scene['scope']='Independent editable components only; no original host, actor/species fit, structural loads or runtime controls';bpy.context.scene['design_parameters_json']=json.dumps(PARAM)
def uv(me,role):
 layer=me.uv_layers.active or me.uv_layers.new(name='metric_material_uv');layer.name='metric_material_uv';layer.active_render=True;s=M[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=axis]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(p[axes[0]]/s[0],p[axes[1]]/s[1])
def mesh(name,vs,fs,role='paint',bevel=0,parent=None):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;o['material_role']=R[role];o['authoring']='Original editable geometric construction';me.materials.append(M[R[role]]);uv(me,R[role])
 if bevel:
  b=o.modifiers.new('Editable edge easing','BEVEL');b.width=bevel;b.segments=2;b.limit_method='ANGLE';n=o.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');n.keep_sharp=True
 return o
def box(name,lo,hi,role='paint',bevel=0,parent=None):
 x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,parent)
def cyl(name,a,b,r,role='metal',n=12,parent=None):
 a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((1,0,0))if abs(v.x)<.9 else Vector((0,1,0))).normalized();w=v.cross(u);vs=[p+r*(u*math.cos(i*2*math.pi/n)+w*math.sin(i*2*math.pi/n))for p in(a,b)for i in range(n)];return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i)for i in range(n)],role,parent=parent)
def empty(name,parent=None,loc=(0,0,0)):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;o.location=loc;o.empty_display_size=.025;return o
def surf(name,obj,p,n,purpose,parent=None,local=None):
 row={'name':name,'physical_object':obj,'point_source_m':p,'normal_source':n,'point_glb_m':glb(p),'normal_glb':glb(n),'kind':'physical_surface','purpose':purpose};e=empty('MARKER_'+name,parent,local if local is not None else p);e['surface_record']=json.dumps(row);return row,e
def cb(name,lo,hi,why,gap=0):return {'name':name,'type':'box','min_source_m':lo,'max_source_m':hi,'reason':why,'conservative_empty_corner_limit_m':gap}
def bounds(obs):
 dg=bpy.context.evaluated_depsgraph_get();ps=[];tri=0
 for o in obs:
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);ps.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[k]for p in ps)for k in range(3)];hi=[max(p[k]for p in ps)for k in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[k]-lo[k]for k in range(3)]},tri
def export(obs,ident,path):
 dg=bpy.context.evaluated_depsgraph_get();groups={}
 for src in obs:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for l in list(me.uv_layers):
   if l!=active:me.uv_layers.remove(l)
  # Preserve developed fabric UVs. Reproject evaluated bevel faces for ordinary solids.
  if not src.get('developed_cloth_uv'):uv(me,src['material_role'])
  else:
   layer=me.uv_layers.active
   for f in me.polygons:
    coords=[layer.data[li].uv.copy()for li in f.loop_indices]
    area=abs(sum(coords[j].x*coords[(j+1)%len(coords)].y-coords[(j+1)%len(coords)].x*coords[j].y for j in range(len(coords))))/2
    if area<1e-12:
     axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=axis]
     for li in f.loop_indices:
      v=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(v[axes[0]]/.4,v[axes[1]]/.4)
  o=bpy.data.objects.new('evaluated_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy();key=(src.parent.name if src.parent else '',src['material_role']);groups.setdefault(key,[]).append((o,src.name))
 out=[]
 for (parent,role),parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o,_ in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0][0];bpy.ops.object.join();o=parts[0][0];o.name=ident+'__'+('MOVING_'if 'MOTION'in parent else 'STATIC_')+role;o['asset_id']=ident;o['semantic_parts']=json.dumps([n for _,n in parts]);mw=o.matrix_world.copy();o.parent=bpy.data.objects.get(parent);o.matrix_world=mw;out.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in out:o.select_set(True)
 for o in bpy.context.scene.objects:
  if o.type=='EMPTY':o.select_set(True)
 bpy.context.view_layer.objects.active=out[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
def finish(ident,title,obs,api,coll,root,states=None):
 bpy.context.view_layer.update();bd,tri=bounds(obs);source=BASE/'source'/f'{ident}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False);export(obs,ident,BASE/'exports'/f'{ident}.glb')
 statefiles=[]
 if states:
  motion=states['root']
  for name,t in [('gathered',1.0)]:
   motion['gather']=t;motion.update_tag();bpy.context.scene.frame_set(2);bpy.context.view_layer.update();export(obs,ident,BASE/'exports'/f'{ident}__{name}.glb');sbd,st=bounds(obs);statefiles.append({'state':name,'gather':t,'export':f'exports/{ident}__{name}.glb','sha256':sha(BASE/'exports'/f'{ident}__{name}.glb'),'bounds_blender_z_up':sbd})
  motion['gather']=0.;motion.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 row={'catalogue_id':ident,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_crew_rest.py','dimension_adjustment':'Editable semantic meshes and generator coordinates; summary fields are not live dimension controls. Resizing requires coordinated interface/collision review.','source_coordinates':{'units':'metres','right':'+X','depth':'+Y','up':'+Z','front':'-Y (foot end); long-side access +X','pivot_m':[0,0,0],'pivot_datum':'floor/foot-end centre, NOT centred footprint'},'glb_coordinates':{'up':'+Y','source_to_glb':'(x,y,z)->(x,z,-y)'},'bounds_blender_z_up':bd,'bounds_gltf_y_up':{'min_m':[bd['min_m'][0],bd['min_m'][2],-bd['max_m'][1]],'max_m':[bd['max_m'][0],bd['max_m'][2],-bd['min_m'][1]]},'editable_semantic_parts':len(obs),'semantic_parts':[o.name for o in obs],'evaluated_triangles':tri,'material_roles':sorted(set(o['material_role']for o in obs)),'runtime_consolidation':'Evaluated meshes grouped by material and static/moving parent; semantic source preserved, moving roots and physical markers retained','interface_api':'interface_api.json','collision_proposal_file':'collision_proposals.json','source_sha256':sha(source),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'state_derivatives':statefiles,'limitations':['Single-place dry prototype; no registered berth/person/room allocation','Only configured source size checked; six-species fit, sleeping poses and loads unverified','No stacked configuration, original host fit, cloth simulation, gameplay, acoustics or lighting performance','Collision compounds are proposals preserving declared voids; not runtime physics certification']}
 (BASE/f'{ident}.manifest.json').write_text(json.dumps(row,indent=2));ASSETS.append(row);API[ident]=api;COLL[ident]={'frame':'Blender source metres +Z; native GLB mapping (x,z,-y)','shapes':coll,'status':'Geometric component proposal only, excludes use voids'}
# Editable semantic source; resizing is explicit geometric authoring, not dictionary/runtime adjustment.
reset();root=empty('AST-CRW-001_floor_foot_end_datum');root['catalogue_id']='AST-CRW-001';root['datum']='floor at centre of foot end; footprint y0..2.20';O=[];S=[];C=[]
def add(o):O.append(o);o.parent=root;return o
for sx in(-1,1):
 x=sx*.49
 for i,y in enumerate((.13,1.10,2.07)):
  add(box(f'001_floor_pad_{sx}_{i}',[x-.041,y-.055,0],[x+.041,y+.055,.018],'dark',.002));add(box(f'001_folded_leg_{sx}_{i}',[x-.033,y-.040,.018],[x+.033,y+.040,.347],'frame',.003));C.append(cb(f'leg_{sx}_{i}',[x-.041,y-.055,0],[x+.041,y+.055,.347],'Leg and pad compound',.011))
  r,e=surf(f'floor_contact_{sx}_{i}',f'001_floor_pad_{sx}_{i}',[x,y,0],[0,0,-1],'Actual supported foot; floor/load unknown',root);S.append(r)
 # Folded side rail keeps an honest open under-frame bay.
 lo=sorted([sx*.47,sx*.54]);add(box(f'001_side_rail_{sx}',[lo[0],.045,.322],[lo[1],2.155,.414],'frame',.003));C.append(cb(f'side_rail_{sx}',[lo[0],.045,.322],[lo[1],2.155,.414],'Vertical folded side rail; separate thin bearing-lip profile',.003))
 add(box(f'001_inward_bearing_lip_{sx}',[min(sx*.445,sx*.53),.065,.414],[max(sx*.445,sx*.53),2.135,.425],'metal',.001));C.append(cb(f'bearing_lip_{sx}',[min(sx*.445,sx*.53),.065,.414],[max(sx*.445,sx*.53),2.135,.425],'Thin inward bearing lip, separate from vertical rail so the inner under-frame bay stays open',.001))
for i,y in enumerate([.16+i*.235 for i in range(9)]):
 add(box(f'001_breathable_support_slat_{i}',[-.47,y-.044,.401],[.47,y+.044,.425],'metal',.002));C.append(cb(f'slat_{i}',[-.47,y-.044,.401],[.47,y+.044,.425],'Separate load slat; actual ventilation openings preserved',.002))
for tag,y in [('foot',.025),('head',2.135)]:add(box('001_'+tag+'_crossrail',[-.50,y,.322],[.50,y+.04,.414],'frame',.002));C.append(cb(tag+'_crossrail',[-.5,y,.322],[.5,y+.04,.414],'End rail below bedding',.002))
# Deliberately crowned padded mattress and pillow, layered rounded-rectangle rings.
def cushion(name,cy,rings,role):
 vs=[];N=48
 for hw,hl,z in rings:
  for i in range(N):
   a=i*math.tau/N;vs.append((hw*math.copysign(abs(math.cos(a))**.30,math.cos(a)),cy+hl*math.copysign(abs(math.sin(a))**.24,math.sin(a)),z))
 fs=[tuple(reversed(range(N))),tuple((len(rings)-1)*N+i for i in range(N))]
 for j in range(len(rings)-1):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 o=add(mesh(name,vs,fs,role));return o
cushion('001_shaped_single_mattress',1.09,[(.452,.965,.425),(.484,.99,.443),(.489,.990,.486),(.476,.978,.519),(.442,.946,.534)],'sheet');C.append({'name':'mattress','type':'convex_hull','vertices_source_m':[list(v.co)for v in O[-1].data.vertices],'reason':'Crowned rounded mattress hull from actual outer support rings; no underbed volume','conservative_empty_corner_limit_m':0})
cushion('001_shaped_head_pillow',1.80,[(.302,.215,.534),(.344,.244,.559),(.331,.235,.622),(.270,.193,.652),(.19,.13,.657)],'sheet');C.append({'name':'pillow','type':'convex_hull','vertices_source_m':[list(v.co)for v in O[-1].data.vertices],'reason':'Rounded crowned pillow outer support rings; concave/compression behavior unimplemented','conservative_empty_corner_limit_m':0})
# Draped blanket with shaped lateral drop and folded head-side return, no pasted flat box.
xs=[-.508,-.499,-.482,-.455,-.35,0,.35,.455,.482,.499,.508];zs=[.433,.480,.520,.535,.536,.536,.536,.535,.520,.480,.433];vs=[];rows=19
for j in range(rows):
 v=j/(rows-1);y=.15+v*1.32
 for i,(x,z)in enumerate(zip(xs,zs)):
  fold=.016*math.exp(-((v-.93)/.047)**2);ripple=.001*(1+math.sin(v*math.pi*7+x*8));vs.append((x,y+.015*math.sin(x*6)*v,z+fold+ripple))
fs=[]
for j in range(rows-1):
 for i in range(len(xs)-1):a=j*len(xs)+i;fs.append((a,a+1,a+len(xs)+1,a+len(xs)))
o=add(mesh('001_draped_folded_blanket',vs,fs,'blanket'));so=o.modifiers.new('Editable textile thickness','SOLIDIFY');so.thickness=.004;so.offset=0;C.append({'name':'blanket','type':'flexible_surface_no_independent_collision','source_object':'001_draped_folded_blanket','reason':'Integrated soft blanket is visual only. Mattress hull supplies underlying rest collision; lateral drape/turned fold conservatively up to .080m outside mattress hull is deliberately omitted. No flexible cloth response.','maximum_declared_visual_detail_omission_m':.080})
# Bed end structure: a genuine headboard with flat mounting patch and a low protected foot rail.
add(box('001_flat_headboard',[-.50,2.14,.414],[.50,2.20,1.10],'paint',.007));C.append(cb('headboard',[-.50,2.14,.414],[.50,2.20,1.10],'Solid economical headboard; 7mm eased perimeter',.007))
for sx in(-1,1):add(box(f'001_headboard_support_{sx}',[sx*.45-.035,2.14,0],[sx*.45+.035,2.20,.414],'frame',.002));C.append(cb(f'headboard_support_{sx}',[sx*.45-.035,2.14,0],[sx*.45+.035,2.20,.414],'Headboard supported down to floor pad elevation',.002))
add(box('001_low_foot_guard',[-.48,0,.342],[.48,.05,.49],'paint',.005));C.append(cb('foot_guard',[-.48,0,.342],[.48,.05,.49],'Low foot keeper leaves entry open',.005))
for name,obj,p,n,why in [('rest_contact','001_shaped_single_mattress',[0,1.52,.534],[0,0,1],'Actual exposed mattress crown between blanket and pillow; blanket contact is a separate surface'),('head_contact','001_shaped_head_pillow',[0,1.80,.657],[0,0,1],'Actual pillow central crown'),('foot_contact','001_low_foot_guard',[0,0,.416],[0,-1,0],'Actual outward foot guard face'),('headboard_mount','001_flat_headboard',[-.26,2.14,.88],[0,-1,0],'Real receiving face for AST-CRW-004')]:r,e=surf(name,obj,p,n,why,root);S.append(r)
for x in(-.37,-.15):
 for z in(.76,1.00):r,e=surf(f'light_mount_{x}_{z}','001_flat_headboard',[x,2.14,z],[0,-1,0],'Opposing physical mount witness for AST-CRW-004',root);S.append(r)
api={'surfaces':S,'joins':[{'a':'001_shaped_single_mattress','b':'001_breathable_support_slat_4','witness_source_m':[0,1.10,.425],'type':'opposing bearing contact','designed_gap_m':0},{'a':'001_shaped_head_pillow','b':'001_shaped_single_mattress','witness_source_m':[0,1.80,.534],'type':'padded bearing','designed_gap_m':0},{'a':'001_draped_folded_blanket','b':'001_shaped_single_mattress','witness_source_m':[0,.81,.534],'type':'textile underside bearing','designed_gap_m':0}],'reserved_voids':[{'name':'central_rest_use','min_source_m':[-.40,.30,.565],'max_source_m':[.40,1.52,1.10],'scope':'Unverified use reservation only, no actor fit'},{'name':'under_frame_cleaning','min_source_m':[-.42,.20,.025],'max_source_m':[.42,2.0,.315],'scope':'Geometric clear prism only, no body/cart fit'},{'name':'side_approach_below_curtain','min_source_m':[.56,.20,0],'max_source_m':[1.25,1.75,.26],'scope':'Low approach floor strip; privacy curtain begins .28'}],'mount_contract':{'mated_asset':'AST-CRW-004','module_to_frame_translation_source_m':[-.26,2.14,.88],'module_to_frame_rotation_degrees':[0,0,0],'module_mount_normal':[0,1,0],'frame_mount_normal':[0,-1,0],'witnesses_source_m':[[x,2.14,z]for x in(-.37,-.15)for z in(.76,1.00)],'physical_receiver':'001_flat_headboard','head_pillow_max_z':.657,'module_shelf_min_z':.735,'vertical_pillow_shelf_gap_m':.078},'rest_status':'No rest/game IDs, body poses or species fit; values are proposed physical components'}
finish('AST-CRW-001','Single-place crew rest frame with fitted bedding',O,api,C,root)
# Curtain assembly, independent grounded posts with proper rod-bearing ring hangers.
reset();root=empty('AST-CRW-002_floor_foot_end_datum');root['catalogue_id']='AST-CRW-002';motion=empty('AST-CRW-002_CURTAIN_MOTION',root,(0,.02,0));motion['gather']=0.;motion['motion_type']='Authored accordion span and pleat depth, no simulation';motion['parameter_interval']=[0.,1.];motion['native_moving_ownership']='Fabric, top straps, all supported rings, grip and grip marker';O=[];S=[];C=[]
def add(o):O.append(o);o.parent=o.parent or root;return o
def driver(target,path,index,expr):
 f=target.driver_add(path,index)if index is not None else target.driver_add(path);d=f.driver;d.type='SCRIPTED';v=d.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=motion;v.targets[0].data_path='["gather"]';d.expression=expr
# t changes both leading-edge position and fabric width; trailing edge remains y2.18 exactly.
driver(motion,'location',1,'.02+1.8*t')
for name,y in [('foot',-.06),('head',2.26)]:
 add(box('002_'+name+'_floor_shoe',[.584,y-.09,0],[.776,y+.09,.035],'frame',.009));add(box('002_'+name+'_post',[.660,y-.023,.035],[.700,y+.023,2.12],'paint',.003));C.append(cb(name+'_shoe',[.584,y-.09,0],[.776,y+.09,.035],'Independent floor support, not frame attachment',.009));C.append(cb(name+'_post',[.660,y-.023,.035],[.700,y+.023,2.12],'Actual slender post, does not fill approach',.003));r,e=surf(name+'_floor_contact','002_'+name+'_floor_shoe',[.68,y,0],[0,0,-1],'Real independent floor shoe',root);S.append(r)
 for z in(.085,2.04):add(cyl(f'002_{name}_assembly_fastener_{z}',[.652,y,z],[.708,y,z],.009,'metal',8))
add(cyl('002_continuous_round_track',[.68,-.078,2.079],[.68,2.278,2.079],.018,'metal',16));C.append({'name':'continuous_track','type':'capsule','a_source_m':[.68,-.078,2.079],'b_source_m':[.68,2.278,2.079],'radius_m':.018,'reason':'Circular track visual/collision; hemispherical ends conservative by18mm'})
for y in(-.006,2.206):add(cyl('002_track_end_stop_'+str(y),[.68,y-.006,2.079],[.68,y+.006,2.079],.028,'dark',16));C.append(cb('endstop_'+str(y),[.652,y-.006,2.051],[.708,y+.006,2.107],'Deliberate end-stop disc, box corner inflation 11.6mm',.0116))
# 24 equal developed pleats. Both shape keys have exact deterministic drivers.
N=24;Z=[.28,.30,.65,1.05,1.45,1.97,2.015];vs=[]
for z in Z:
 for i in range(N+1):vs.append((.68+(-1 if i%2==0 else 1)*.025,2.16*i/N,z))
fs=[]
for j in range(len(Z)-1):
 for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
fab=add(mesh('002_accordion_privacy_fabric',vs,fs,'curtain',parent=motion));fab['developed_cloth_uv']=True;fab['developed_width_m']=N*LSEG;fab['panel_segment_length_m']=LSEG;fab.shape_key_add(name='Basis');span=fab.shape_key_add(name='GatherSpan');pleat=fab.shape_key_add(name='PleatDepth')
for i,v in enumerate(vs):
 vi=i%(N+1);span.data[i].co.y=.36*vi/N;pleat.data[i].co.x=.68+(-1 if vi%2==0 else 1)*AOPEN
for key,expr in[(span,'t'),(pleat,EXPR)]:driver(key,'value',None,expr)
# UV is developed material distance, unchanged during gather. Thickness side UVs assigned after solidify export.
layer=fab.data.uv_layers.active
for f in fab.data.polygons:
 for li in f.loop_indices:
  idx=fab.data.loops[li].vertex_index;i=idx%(N+1);j=idx//(N+1);layer.data[li].uv=(i*LSEG/.4,Z[j]/.4)
solid=fab.modifiers.new('Editable 3mm textile thickness','SOLIDIFY');solid.thickness=.003;solid.offset=0
# Rings have a real central hole. Their inner upper face contacts the rod top at z2.097.
for i in range(N+1):
 y=2.16*i/N;v=[];steps=16
 for yy in(-.004,.004):
  for rx,rz in[(.033,.029),(.026,.022)]:
   for j in range(steps):a=math.tau*j/steps;v.append((.68+rx*math.cos(a),yy,2.075+rz*math.sin(a)))
 f=[]
 for j in range(steps):
  k=(j+1)%steps;f += [(j,k,32+k,32+j),(16+j,48+j,48+k,16+k),(j,16+j,16+k,k),(32+j,32+k,48+k,48+j)]
 o=add(mesh(f'002_supported_ring_{i:02}',v,f,'metal',parent=motion));o.location.y=y;driver(o,'location',1,f'(2.16-1.8*t)*{i}/24')
 # Diagonal fabric suspension tape, fixed at ring bottom and keyed to exact pleat amplitude.
 x=.68+(-1 if i%2==0 else 1)*.025;v=[(x-.004,-.004,2.015),(x+.004,-.004,2.015),(.684,-.004,2.047),(.676,-.004,2.047),(x-.004,.004,2.015),(x+.004,.004,2.015),(.684,.004,2.047),(.676,.004,2.047)]
 v=[(px,py*.75,pz)for px,py,pz in v];o=add(mesh(f'002_suspension_tape_{i:02}',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'curtain',parent=motion));o.location.y=y;driver(o,'location',1,f'(2.16-1.8*t)*{i}/24');o.shape_key_add(name='Basis');k=o.shape_key_add(name='PleatDepth');delta=(-1 if i%2==0 else 1)*(AOPEN-.025)
 for j in(0,1,4,5):k.data[j].co.x+=delta
 driver(k,'value',None,EXPR)
# Leading sewn grip is a supported physical strap; its marker follows motion and pleat depth.
grip=add(box('002_leading_pull_grip',[.643,-.012,.97],[.663,.006,1.13],'dark',.003,parent=motion));driver(grip,'location',0,'-('+EXPR+')*'+repr(AOPEN-.025));r,e=surf('curtain_pull','002_leading_pull_grip',[.643,.02-.003,1.05],[-1,0,0],'Real outer leading grip face; marker follows root and pleat depth',motion,[.643,-.003,1.05]);driver(e,'location',0,'.643-('+EXPR+')*'+repr(AOPEN-.025));S.append(r)
r,e=surf('track_top_contact','002_continuous_round_track',[.68+.009*math.sin(math.pi/8),1.10,2.079+.009*(1+math.cos(math.pi/8))],[math.sin(math.pi/16),0,math.cos(math.pi/16)],'Actual upper rod facet; distinct from ring edge bearing at z2.097',root);S.append(r)
formula={'parameter':'CURTAIN_MOTION["gather"]','range':[0,1],'leading_y_m':'.02+1.8*t','span_m':'2.16-1.8*t','pleat_segments':24,'segment_developed_length_m':LSEG,'developed_fabric_width_m':24*LSEG,'half_pleat_amplitude_m':'0.5*sqrt(segment_length^2-(span/24)^2)','half_amplitude_closed_m':.025,'half_amplitude_gathered_m':AOPEN,'trailing_y_m':2.18,'fabric_height_m':1.735,'fabric_thickness_m':.003,'shape_keys':['GatherSpan linear t','PleatDepth exact nonlinear sqrt driver'],'texture_intent':'U is immutable developed pleat distance / .4m; V is vertical distance /.4m. No material stretching during gather.','native_derivatives':'Closed and gathered static geometric poses under the same named motion root. Parametric driver is source-only, no GLB runtime animation or cloth simulation.'}
api={'surfaces':S,'motion':formula,'declared_states':[{'name':'closed','gather':0},{'name':'gathered','gather':1}],'continuous_geometric_envelope':{'min_source_m':[.68-AOPEN-.014,.004,.28],'max_source_m':[.68+AOPEN+.004,2.188,2.104],'scope':'Complete t0..1 bound from monotone span/amplitude; includes textile/grip/rings/straps. Does not model real flexible cloth dynamics.'},'fixed_clearance':{'bed_rail_max_x':.54,'fabric_min_x':.68-AOPEN-.0015,'fabric_to_bed_rail_min_m':.68-AOPEN-.0015-.54,'leading_moving_min_y':.008,'foot_stop_max_y':0.,'foot_stop_to_leading_grip_min_m':.008,'trailing_ring_max_y':2.184,'head_stop_min_y':2.2,'trailing_ring_stop_gap_m':.016,'fabric_bottom_floor_gap_m':.28},'ring_support':{'count':25,'inner_ring_top_z':2.097,'track_top_z':2.097,'normal_pair':[[0,-0.,-1],[0,0,1]],'witnesses_closed_source_m':[[.68,.02+2.16*i/24,2.097]for i in range(25)],'statement':'Ring inner upper rim bears on rod upper surface; rings remain around rod at every authored t; tolerance numeric, no structural load proof'},'privacy_field':{'closed_tests':[{'eye_source_m':[2.0,y,1.15],'target_source_m':[0,y,.59]}for y in(.45,.9,1.4)],'open_negative_controls':[{'eye_source_m':[2.0,.9,1.15],'target_source_m':[0,.9,.59]}],'limits':'Only those side segments/height range. Top, ends, under-hem, foot/head oblique views and whole room privacy are unprotected/unverified; no acoustic claim'},'reserved_voids':[{'name':'floor_clear_below_fabric','min_source_m':[.56,.20,.04],'max_source_m':[.8,2.0,.26],'scope':'Open under-hem region, no body clearance claim'}]}
C += [dict(name='moving_fabric_profile',type='per_pose_thin_convex_pleat_panels',source_object='002_accordion_privacy_fabric',segments=24,half_thickness_m=.0015,parameter_formula=formula,reason='24 thin panel prisms follow pleats; no broad berth-filling box',max_profile_error_m=.003),dict(name='moving_hangers_and_grip',type='visual_detail_exclusion',reason='Small hangers and pull grip lie within stated sweep; no independent actor collision proposed, not a claim they are absent')]
finish('AST-CRW-002','Supported individual crew privacy curtain and track',O,api,C,root,{'root':motion});POSES['AST-CRW-002']=formula
(BASE/'manifest.json').write_text(json.dumps({'batch':'15','family':'crew_rest','unique_asset_count':2,'assets':ASSETS,'scope':'Original component prototypes; zero registered people or berths','exported_configuration_summary':PARAM,'dimension_adjustment':'Manual editing of semantic source geometry and coordinated interface/collision coordinates. PARAM is a summary, not a live size rig; only the exported configuration is checked.'},indent=2))
(BASE/'interface_api.json').write_text(json.dumps({'units':'metres','source_basis':'X across,Y depth,Z up; floor/foot-end origin','glb_basis':'X across,Y up,Z=-sourceY','assets':API},indent=2));(BASE/'collision_proposals.json').write_text(json.dumps({'assets':COLL},indent=2));(BASE/'pose_contract.json').write_text(json.dumps(POSES,indent=2))
inputs=[Path(__file__),BASE/'textures/draw_crew_cloth.py',BASE/'textures/manifest.json']+[BASE/'textures'/r['file']for r in cloth['materials'].values()]+[CAT/'standards/staff_materials.py',CAT/'materials/staff/manifest.json']+[CAT/'materials/staff'/r['file']for r in json.loads((CAT/'materials/staff/manifest.json').read_text())['materials'].values()]
(BASE/'dependency_manifest.json').write_text(json.dumps({'source_only_inputs':[{'path':str(p.relative_to(CAT)),'sha256':sha(p)}for p in inputs],'source_only_excludes':'No previous blend/GLB/QA or sibling asset input opened','all_loaded_roles_closed':True,'reference_dependencies':'Reference pixels guide original design only; never loaded by builder or copied to texture'},indent=2));print('CREW_REST_BUILD_OK')
