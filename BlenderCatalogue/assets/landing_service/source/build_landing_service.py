"""Astraea Batch11: two original script-assisted editable staff landing components.
Source-only inputs: this script, standards/staff_materials.py, material manifest and
all nine textures loaded by that helper. No previous source/export/QA is read.
Metres; +Z up; -Y front. Static inspected proposal, no lift/room/game function.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]; CAT=BASE.parents[1]
for sub in ('source','exports','qa'):(BASE/sub).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('staff_materials',CAT/'standards/staff_materials.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib);M=lib.materials()
R={'paint':'staff_white_paint','bluegrey':'staff_bluegrey_paint','metal':'staff_zinc','dark':'staff_rubber','opal':'staff_opal','label':'staff_label','red':'staff_cable_red','blue':'staff_cable_blue'}
GRAPHICS=json.loads((BASE/'textures/manifest.json').read_text())['roles']
for role,row in GRAPHICS.items():
 mat=bpy.data.materials.new('ASTRAEA_'+role);mat.use_nodes=True;mat['astraea_material_role']=role;mat['meters_per_tile_uv']=[1.,1.];mat['intended_context']='landing_service_local_graphic';mat['material_revision']='landing-service-graphics-01';mat.diffuse_color=tuple(c/255 for c in row['colour_srgb_8bit'])+(1,)
 nodes=mat.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=row['roughness'];tex=nodes.new('ShaderNodeTexImage');img=bpy.data.images.load(str(BASE/'textures'/row['file']),check_existing=True);img.pack();tex.image=img;tex.interpolation='Closest';tex.extension='EXTEND';out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);M[role]=mat
GRAPHIC_MAP={'003_attention_request_pad':'landing_service_request_symbol','003_inspection_key_cover':'landing_service_inspection_symbol','003_status_flag_surface':'landing_service_inactive_symbol','003_service_legend_plaque':'landing_service_legend_graphic'}
ASSETS=[]; COLLISIONS={}; API={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s['evidence_scope']='Independent editable component; no original ship or game reconstruction'

def uv_project(me,role):
 uv=me.uv_layers.active or me.uv_layers.new(name='metric_material_uv');uv.name='metric_material_uv';uv.active_render=True
 scale=M[role]['meters_per_tile_uv']
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/scale[0],p[axes[1]]/scale[1])

def graphic_uv(me,record):
 c=Vector(record['centre']);v=Vector(record['vertical']);n=Vector(record['normal']);w,h=record['size'];uv=me.uv_layers.active
 for f in me.polygons:
  if f.material_index==1 and f.normal.dot(n)>.999:
   for li in f.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co-c;uv.data[li].uv=(.5+p.x/w,.5+p.dot(v)/h)

def mesh(name,vs,fs,role='paint',bevel=0):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(M[R[role]]);o['material_role']=R[role];o['authoring']='original script-assisted editable folded component';uv_project(me,R[role])
 if bevel:
  b=o.modifiers.new('Editable formed corner easing','BEVEL');b.width=bevel;b.segments=1;b.limit_method='ANGLE'
  n=o.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');n.keep_sharp=True
 return o

def box(name,lo,hi,role='paint',bevel=0):
 x,y,z=lo;X,Y,Z=hi
 return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)

def extrude(name,poly,a,b,axis,role='paint',bevel=0):
 # Polygon is in the remaining axes, extrusion in named dimension.
 axes=[i for i in range(3) if i!=axis];vs=[]
 for d in (a,b):
  for p in poly:
   q=[0,0,0];q[axis]=d;q[axes[0]]=p[0];q[axes[1]]=p[1];vs.append(q)
 n=len(poly);fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
 return mesh(name,vs,fs,role,bevel)

def chamfer_plan(w,d,y0=0,c=.04):
 return [(-w/2+c,y0),(w/2-c,y0),(w/2,y0+c),(w/2,y0+d-c),(w/2-c,y0+d),(-w/2+c,y0+d),(-w/2,y0+d-c),(-w/2,y0+c)]

def cylinder(name,a,b,r,role='metal',n=12):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((1,0,0)) if abs(axis.x)<.9 else Vector((0,1,0))).normalized();v=axis.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n)) for p in(a,b) for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],role)

def bounds(obs):
 pts=[];nt=0;dg=bpy.context.evaluated_depsgraph_get()
 for o in obs:
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();nt+=len(me.loop_triangles);pts.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},nt

def surface(name,obj,p,n,purpose):
 return {'name':name,'physical_object':obj,'point_source_m':p,'normal_source':n,'point_glb_m':glb(p),'normal_glb':glb(n),'kind':'physical surface','purpose':purpose}

def collbox(name,lo,hi,reason,maxgap=0):return {'name':name,'type':'box','min_source_m':lo,'max_source_m':hi,'reason':reason,'conservative_empty_corner_limit_m':maxgap}
def collpoly(name,poly,a,b,axis,reason,maxgap=0):
 axes=[i for i in range(3) if i!=axis];vs=[]
 for d in (a,b):
  for p in poly:
   q=[0,0,0];q[axis]=d;q[axes[0]]=p[0];q[axes[1]]=p[1];vs.append(q)
 return {'name':name,'type':'convex_prism','vertices_source_m':vs,'section_axis':axis,'section_polygon_m':poly,'extrusion_min_m':a,'extrusion_max_m':b,'reason':reason,'conservative_empty_corner_limit_m':maxgap}

def export(obs,ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={}
 for src in obs:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=active:me.uv_layers.remove(layer)
  uv_project(me,src['material_role'])
  if src.get('graphic_uv_record'):graphic_uv(me,json.loads(src['graphic_uv_record']))
  # Project the evaluated faces so narrow new bevel faces also retain nonzero UVs.
  o=bpy.data.objects.new('evaluated_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy()
  key=src.name if src.get('individual_control') else src['material_role'];groups.setdefault(key,[]).append(o)
 out=[]
 for key,parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name=ident+'__'+key;o['asset_id']=ident;o['semantic_parts']=json.dumps([s.name for s in obs if (s.name if s.get('individual_control') else s['material_role'])==key]);out.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in out:
  o.parent=bpy.data.objects.get(ident+'_floor_datum');o.select_set(True)
 for o in bpy.context.scene.objects:
  if o.type=='EMPTY':o.select_set(True)
 bpy.context.view_layer.objects.active=out[0]
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)

def save(ident,title,obs,api,coll,origin,targets):
 bd,tri=bounds(obs)
 root=bpy.data.objects.new(ident+'_floor_datum',None);bpy.context.collection.objects.link(root);root['pivot_source_m']=[0,0,0];root['front_source']=[0,-1,0];root['front_glb']=[0,0,1];root['catalogue_id']=ident
 for o in obs:o.parent=root
 for row in api['surfaces']:
  e=bpy.data.objects.new('MARKER_'+row['name'],None);bpy.context.collection.objects.link(e);e.location=row['point_source_m'];e.empty_display_size=.035;e['surface_record']=json.dumps(row);e.parent=root
 bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),check_existing=False)
 export(obs,ident)
 corners=[[x,y,z] for x in [bd['min_m'][0],bd['max_m'][0]] for y in [bd['min_m'][1],bd['max_m'][1]] for z in [bd['min_m'][2],bd['max_m'][2]]]
 ship=[[origin[0]+p[1],origin[1]+p[2],origin[2]+p[0]] for p in corners]
 row={'catalogue_id':ident,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_landing_service.py','units':'metres','source_coordinates':{'right':'+X','depth':'+Y','up':'+Z','front':'-Y','pivot_m':[0,0,0],'pivot_datum':'floor at source origin; may lie in intentional open space'},'glb_coordinates':{'up':'+Y','front':'+Z','source_to_glb':'(x,y,z) -> (x,z,-y)','pivot_m':[0,0,0]},'bounds_blender_z_up':bd,'bounds_gltf_y_up':{'min_m':[bd['min_m'][0],bd['min_m'][2],-bd['max_m'][1]],'max_m':[bd['max_m'][0],bd['max_m'][2],-bd['min_m'][1]]},'proposed_ship_placement':{'source_z_rotation_degrees':-90,'origin_ship_xyz_m':origin,'mapping':'ship=(originX+sourceY, originY+sourceZ, originZ+sourceX)','front_ship':[-1,0,0],'bounds_min_ship_m':[min(p[k] for p in ship) for k in range(3)],'bounds_max_ship_m':[max(p[k] for p in ship) for k in range(3)],'candidate_bounds_ship':targets,'authority':'R3 plan proposal only; heights are component targets, unknown host floor/support/head/shaft/door dimensions'},'editable_semantic_parts':len(obs),'semantic_parts':[o.name for o in obs],'evaluated_triangles':tri,'material_roles':sorted(set(m.get('astraea_material_role',m.name) for o in obs for m in o.data.materials)),'runtime_consolidation':'One evaluated mesh per material role except individual control objects preserved as separate meshes; active evaluated UV layers projected and normalized by name','interface_api':'interface_api.json','collision_proposal_file':'collision_proposals.json','collision_shape_count':len(coll),'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'limitations':['Independent component proposal, original ship missing','No room/actor/cart/route, support/load, headroom, lighting, electrical, mechanical or engine acceptance','No lift behavior or moving travel','R3 heights and boxes are proposed reservations only']}
 (BASE/f'{ident}.manifest.json').write_text(json.dumps(row,indent=2));ASSETS.append(row);API[ident]=api;COLLISIONS[ident]={'frame':'Blender source, metres, +Z up; GLB mapping (x,z,-y)','shapes':coll,'status':'Separate structural collision proposal; not exported with visual GLB, no physics acceptance','policy':'No all-enclosing hull; small fasteners and control pads do not add hulls; conservative errors measured against named profiles'}

reset();O=[];S=[];C=[]
# 003: broad economical panel and upper receiver. All finish layers end before return faces.
foot=chamfer_plan(1.30,.45,0,.045);O.append(extrude('003_chamfered_floor_shoe',foot,0,.055,2,'bluegrey',.002));C.append(collpoly('floor_shoe',foot,0,.055,2,'Flat floor shoe; bevel ignored',.002))
O.append(box('003_structural_back_spine',[-.61,.400,.055],[.61,.45,2.47],'bluegrey',.0015));C.append(collbox('back_spine',[-.61,.398,.055],[.61,.45,2.47],'Continuous structural wash-panel core',.002))
# White washable fields separated by real 8 mm vertical service seam.
for suffix,lo,hi in [('lower',[-.568,.382,.105],[.568,.400,1.00]),('upper',[-.568,.382,1.008],[.568,.400,2.285])]:O.append(box('003_'+suffix+'_washable_field',lo,hi,'paint',.0015))
# Side returns have a forward fold and clipped upper termination, protected only where touched.
sidepoly=[(.345,.055),(.45,.055),(.45,2.47),(.401,2.47),(.345,2.38)]
for sign in [-1,1]:
 a,b=sorted([sign*.57,sign*.62]);O.append(extrude(f'003_folded_edge_return_{sign:+d}',sidepoly,a,b,0,'bluegrey',.0015));C.append(collpoly(f'edge_return_{sign:+d}',sidepoly,a,b,0,'Folded outer support; no broad approach hull',.0015))
 O.append(box(f'003_replaceable_corner_guard_{sign:+d}',[a-.008,.319,.075],[b+.008,.343,1.04],'dark',.002))
 for z in(.16,.96):O.append(cylinder(f'003_guard_fastener_{sign:+d}_{z}',[(a+b)/2,.313,z],[(a+b)/2,.33,z],.009,'metal',8))
for z in(.36,.83):
 p=[(-.536,.327),(.536,.327),(.554,.339),(.554,.370),(-.554,.370),(-.554,.339)]
 O.append(extrude(f'003_replaceable_impact_strip_{z}',p,z,z+.073,2,'dark',.0015));C.append(collbox(f'impact_rail_{z}',[-.554,.327,z],[.554,.4,z+.073],'Combined impact rail and concealed backing; 18 mm chamfer corner inflation',.018))
# Console section: front rises 0.05 m while returning 0.44 m upward, no invisible coplanar overlay.
consolepoly=[(.382,1.04),(.282,1.09),(.332,1.53),(.382,1.575)]
O.append(extrude('003_sloped_control_cassette',consolepoly,-.438,.438,0,'metal',.0015));C.append(collpoly('sloped_control_cassette',consolepoly,-.438,.438,0,'Supports actual individual control pads; no simulation',.0015))
v=Vector((0,.05,.44)).normalized();n=Vector((0,-.44,.05)).normalized()
def pad(name,x,z,width,height,role,depth=.014):
 y=.282+(z-1.09)*.05/.44;center=Vector((x,y,z));base=[]
 for dx,dy in[(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]:base.append(center+Vector((dx,0,0))+v*dy)
 vv=[p+n*k for k in(0,depth) for p in base];o=mesh(name,vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,.001);o['individual_control']=True;O.append(o)
 if name in GRAPHIC_MAP:
  o.data.materials.append(M[GRAPHIC_MAP[name]])
  for face in o.data.polygons:
   if face.normal.dot(n)>.999:face.material_index=1
  record={'centre':list(center+n*depth),'vertical':list(v),'normal':list(n),'size':[width,height]};o['graphic_uv_record']=json.dumps(record);o['graphic_role']=GRAPHIC_MAP[name];graphic_uv(o.data,record)
 p=center+n*depth;S.append(surface(name+'_contact',name,list(p),list(n),'Static control affordance; no lift action, wiring, state or interaction implementation'));return p
p=pad('003_attention_request_pad',-.235,1.252,.16,.12,'blue')
pad('003_inspection_key_cover',0,1.252,.14,.12,'dark')
pad('003_status_flag_surface',.235,1.252,.14,.12,'opal',.009)
# Large physical legend field above controls, abstract machine-readable divisions only.
pad('003_service_legend_plaque',0,1.435,.62,.067,'label',.003)
# Service access cover is a separated inset at high left, with a real forward handle.
O.append(box('003_service_access_backing',[-.455,.367,1.606],[.455,.382,1.814],'dark',.001));O.append(box('003_removable_service_cover',[-.441,.353,1.620],[.441,.367,1.800],'paint',.0015))
for x in(-.402,.402):O.append(cylinder(f'003_captive_cover_fastener_{x}',[x,.344,1.71],[x,.356,1.71],.012,'metal',8))
S.append(surface('service_cover_face','003_removable_service_cover',[0,.353,1.71],[0,-1,0],'Removable cover witness only; no animation'))
# Receiver underside at 2.47 meets the unchanged fixture top at 2.47.
roof=chamfer_plan(1.24,.42,.03,.025);O.append(extrude('003_folded_fixture_receiver',roof,2.47,2.50,2,'bluegrey',.001));C.append(collpoly('fixture_receiver',roof,2.47,2.50,2,'Upper receiver, broad underside accepts existing fixture plate',.001))
for x in(-.55,.55):
 gp=[(.382,2.245),(.382,2.47),(.16,2.47)];O.append(extrude(f'003_receiver_gusset_{x}',gp,x-.017,x+.017,0,'metal',.0008));C.append(collpoly(f'fixture_gusset_{x}',gp,x-.017,x+.017,0,'Triangular receiver support',.0008))
for x in(-.36,.36):S.append(surface(f'fixture_receiver_{x}','003_folded_fixture_receiver',[x,.20,2.47],[0,0,-1],'Opposing mount receiver for reused AST-STF-006 top plate'))
S.append(surface('floor_contact','003_chamfered_floor_shoe',[0,.225,0],[0,0,-1],'Actual bottom of component shoe; host support unknown'))
api={'surfaces':S,'joins':[{'a':'003_folded_fixture_receiver','b':'003_structural_back_spine','witness_source_m':[0,.425,2.47],'type':'opposing butt','designed_gap_m':0},{'a':'003_chamfered_floor_shoe','b':'003_structural_back_spine','witness_source_m':[0,.425,.055],'type':'opposing butt','designed_gap_m':0}],'fixture_context':{'asset_id':'AST-STF-006','scope':'Reused original QA fixture only; not copied into new source or production export; no new fixture count','existing_source':'../staff_overhead/source/AST-STF-006.blend','existing_export':'../staff_overhead/exports/AST-STF-006.glb','translation_source_m':[-.6,.20,2.47],'rotation_source_degrees':[0,0,0],'scale':[1,1,1],'anchor_source_m':[[-.36,.20,2.47],[.36,.20,2.47]],'fixture_top_normal_source':[0,0,1],'receiver_surface_normal_source':[0,0,-1],'lens_aim_source':[0,0,-1],'all_context_bounds_source_m':{'min':[-.560000001,.025000003,1.862500043],'max':[.559999967,.372999993,2.47]},'matrix_source_local':[[1,0,0,-.6],[0,1,0,.20],[0,0,1,2.47],[0,0,0,1]],'paired_mount_witnesses':[{'fixture_local_point_m':[.24,0,0],'receiver_source_point_m':[-.36,.20,2.47],'receiver_object':'003_folded_fixture_receiver'},{'fixture_local_point_m':[.96,0,0],'receiver_source_point_m':[.36,.20,2.47],'receiver_object':'003_folded_fixture_receiver'}],'whole_fixture_check_required':True},'reserved_voids':[{'name':'front_approach','min_source_m':[-.50,-.8,0],'max_source_m':[.5,-.02,1.8],'authority':'negative geometry QA only; no actor fit'}],'standing_point_source_m':[0,-.75,0],'standing_point_scope':'Unverified inspection viewpoint only, no actor fit','moving_travel':'None'}
save('AST-LND-003','Protected staff arrival and control return',O,api,C,[-48.55,0,-377.05],{'min':[-48.55,0,-377.7],'max':[-48.10,2.5,-376.4]})

reset();O=[];S=[];C=[]
# 004: clipped folded inspection table; source front Y0. Lower bay stays genuinely open.
top=chamfer_plan(1.50,.75,0,.06);O.append(extrude('004_folded_inspection_top',top,.9,.925,2,'metal',.0015));C.append(collpoly('inspection_top',top,.9,.925,2,'Broad fixed worktop; exact clipped plan',.0015))
# Front nose folds down beneath top, ends before the corner cuts.
O.append(box('004_replaceable_front_nose',[-.675,.017,.866],[.675,.061,.898],'dark',.002));C.append(collbox('front_nose',[-.675,.017,.866],[.675,.061,.9],'Single protected nose; 2 mm reveal below actual top',.002))
# Two load-bearing folded end frames; front setback frees retrieval approach.
leg=[(.085,0),(.69,0),(.69,.9),(.12,.9),(.12,.755),(.27,.535),(.22,.155),(.085,.12)]
# Collision uses exact convex partition for concave folded support, not full side AABB.
for sign in(-1,1):
 a,b=sorted([sign*.61,sign*.70]);O.append(extrude(f'004_folded_end_frame_{sign:+d}',leg,a,b,0,'bluegrey',.0015))
 for k,poly in enumerate([[(.085,0),(.69,0),(.69,.155),(.22,.155),(.085,.12)],[(.22,.155),(.69,.155),(.69,.535),(.27,.535)],[(.27,.535),(.69,.535),(.69,.9),(.12,.9),(.12,.755)]]):C.append(collpoly(f'end_frame_{sign:+d}_{k}',poly,a,b,0,'Exact convex partition of folded frame; preserves front setback',.0015))
 # Floor shoe is integral to frame; protective front corner stops below worktop.
 O.append(box(f'004_terminated_end_guard_{sign:+d}',[a-.004,.081,.045],[b+.004,.111,.118],'dark',.001))
 for y,z in[(.55,.15),(.58,.83)]:O.append(cylinder(f'004_frame_joint_{sign:+d}_{z}',[a-.004,y,z],[b+.004,y,z],.012,'metal',8))
 S.append(surface(f'floor_contact_{sign:+d}',f'004_folded_end_frame_{sign:+d}',[(a+b)/2,.45,0],[0,0,-1],'Actual flat floor-bearing frame face'))
# Retrieval tray with low rolled back lip; 7 mm reveal around sides.
shelf=chamfer_plan(1.202,.435,.255,.022);O.append(extrude('004_fixed_lower_retrieval_tray',shelf,.225,.250,2,'paint',.0015));C.append(collpoly('retrieval_tray',shelf,.225,.250,2,'Fixed lower tray below open retrieval mouth',.0015))
O.append(box('004_retrieval_rear_stop',[-.575,.666,.25],[.575,.689,.312],'paint',.001));C.append(collbox('retrieval_stop',[-.575,.666,.25],[.575,.689,.312],'Tray rear stop below usable void',.001))
for sign in(-1,1):
 a,b=sorted([sign*.585,sign*.627]);O.append(box(f'004_tray_bearing_ledge_{sign:+d}',[a,.285,.205],[b,.665,.225],'metal',.0008));C.append(collbox(f'tray_bearing_{sign:+d}',[a,.285,.205],[b,.665,.225],'Actual side support under tray',.0008))
O.append(box('004_upper_rear_crossbrace',[-.612,.632,.823],[.612,.689,.895],'metal',.0015));C.append(collbox('rear_crossbrace',[-.612,.632,.823],[.612,.689,.9],'Connects end frames; leaves lower bay open',.0015))
# Rear splash strip and return triangles meet top with opposing faces, never coplanar overlapping layers.
O.append(box('004_short_backstop',[-.676,.716,.925],[.676,.744,1.05],'paint',.001));C.append(collbox('work_backstop',[-.676,.716,.925],[.676,.744,1.05],'Stops tools; no wall or host attachment implied',.001))
for sign in(-1,1):
 a,b=sorted([sign*.66,sign*.692]);gp=[(.58,.925),(.716,.925),(.716,1.038)];O.append(extrude(f'004_short_end_backstop_{sign:+d}',gp,a,b,0,'paint',.001));C.append(collpoly(f'backstop_return_{sign:+d}',gp,a,b,0,'Short triangular end fold',.001))
# Physical service tag supported by a folded hanger on the worktop underside.
O.append(box('004_tag_hanger',[-.29,.071,.832],[.29,.084,.900],'metal',.0006))
O.append(box('004_service_identification_plate',[-.28,.066,.834],[.28,.071,.886],'label',.0006));S.append(surface('service_tag','004_service_identification_plate',[0,.066,.86],[0,-1,0],'Physical identification surface, static'))
S += [surface('inspection_contact','004_folded_inspection_top',[0,.375,.925],[0,0,1],'Fixed usable inspection surface'),surface('retrieval_contact','004_fixed_lower_retrieval_tray',[0,.46,.250],[0,0,1],'Actual lower support; open approach from -Y')]
api={'surfaces':S,'joins':[{'a':'004_folded_inspection_top','b':'004_folded_end_frame_-1','witness_source_m':[-.65,.45,.9],'type':'opposing butt','designed_gap_m':0},{'a':'004_fixed_lower_retrieval_tray','b':'004_tray_bearing_ledge_-1','witness_source_m':[-.59,.45,.225],'type':'opposing butt','designed_gap_m':0}],'fixture_context':None,'reserved_voids':[{'name':'lower_retrieval_mouth','min_source_m':[-.56,-.3,.33],'max_source_m':[.56,.625,.80],'authority':'actual geometric bay negative control, not actor/cart fit'},{'name':'below_tray_front_toe_void','min_source_m':[-.54,-.2,.03],'max_source_m':[.54,.24,.19],'authority':'negative geometry QA only'}],'standing_point_source_m':[0,-.65,0],'standing_point_scope':'Unverified service viewpoint only, no actor fit','moving_travel':'None; fixed service furnishing, not player cart'}
save('AST-LND-004','Fixed service stow and inspection edge',O,api,C,[-48.95,0,-375.55],{'min':[-48.95,0,-376.3],'max':[-48.2,1.05,-374.8]})
(BASE/'manifest.json').write_text(json.dumps({'batch':'11','family':'landing_service','unique_asset_count':2,'assets':ASSETS,'scope':'Original independent component catalogue; no recovered ship, game or working lift'},indent=2))
(BASE/'interface_api.json').write_text(json.dumps({'units':'metres','source_basis':'X across, Y depth, Z up, front -Y','glb_basis':'X across, Y up, front +Z','source_to_glb':'(x,y,z)->(x,z,-y)','assets':API},indent=2))
(BASE/'collision_proposals.json').write_text(json.dumps({'assets':COLLISIONS},indent=2))
inputs=[Path(__file__),BASE/'textures/manifest.json',BASE/'textures/draw_service_graphics.py']+[BASE/'textures'/r['file'] for r in GRAPHICS.values()]+[CAT/'standards/staff_materials.py',CAT/'materials/staff/manifest.json']+[CAT/'materials/staff'/r['file'] for r in json.loads((CAT/'materials/staff/manifest.json').read_text())['materials'].values()]
(BASE/'dependency_manifest.json').write_text(json.dumps({'source_only_inputs':[{'path':str(p.relative_to(CAT)),'sha256':sha(p)} for p in inputs],'source_only_excludes':'No previous blend, GLB, QA, fixture or render input is opened by builder','fixture_context_dependency':'../staff_overhead/exports/AST-STF-006.glb is used only by QA render and context validation, never source creation','all_loaded_roles_closed':True},indent=2))
print('LANDING_SERVICE_BUILD_OK')
