"""Original script-assisted editable hospitality counters, Blender 4.3.2.
No game geometry or external mesh assets. Frozen shared material helpers reused.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
MATS={}
for name in ['materials','staff_materials']:
 spec=importlib.util.spec_from_file_location(name,CAT/'standards'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);MATS.update(m.materials())
R=.620;P=2.400;GAP=.002
TOP=[(-.378,.852),(.378,.852),(.39,.864),(.39,.888),(.378,.90),(-.378,.90),(-.39,.888),(-.39,.869),(-.386,.860)]
FACE=[(-.304,.164),(-.343,.201),(-.359,.275),(-.351,.490),(-.342,.580),(-.354,.696),(-.367,.770),(-.345,.807)]
FACIA=FACE+[(d+.024,z) for d,z in reversed(FACE)]
UPPER=[(-.345,.795),(-.365,.809),(-.368,.840),(-.352,.852),(-.308,.852),(-.308,.795)]
LOWER=[(-.283,.124),(-.316,.144),(-.345,.185),(-.334,.205),(-.309,.186),(-.285,.168)]
END=[(-.282,0),(.280,0),(.280,.124),(.350,.145),(.350,.852),(-.349,.852),(-.367,.770),(-.354,.696),(-.342,.58),(-.351,.49),(-.359,.275),(-.343,.201),(-.304,.164),(-.282,.124)]
COLLISIONS={};RECORDS=[]
CURVED_SERVICE_ACCESS={'type': 'geometric_inner_curve_service_access_proposal', 'frame_source': 'Blender source +Z up', 'frame_glb': 'native glTF +Y up', 'access_from': 'Concave inner side of return, toward larger radius', 'inner_curve_center_source_m': [0, 0.62, 0], 'inner_curve_center_glb_m': [0, 0, -0.62], 'nominal_inner_worktop_radius_m': 0.23, 'lower_usable_vertical_interval_source_z_m': [0.2, 0.42], 'upper_usable_vertical_interval_source_z_m': [0.505, 0.8], 'sampled_approach_rays': [{'source_start_m': [0.02377026264271346, 0.522866202514797, 0.26], 'source_direction': [0.23770262642713458, -0.9713379748520297, 0], 'glb_start_m': [0.02377026264271346, 0.26, -0.522866202514797], 'glb_direction': [0.23770262642713458, 0, 0.9713379748520297], 'ray_length_m': 0.63}, {'source_start_m': [0.02377026264271346, 0.522866202514797, 0.38], 'source_direction': [0.23770262642713458, -0.9713379748520297, 0], 'glb_start_m': [0.02377026264271346, 0.38, -0.522866202514797], 'glb_direction': [0.23770262642713458, 0, 0.9713379748520297], 'ray_length_m': 0.63}, {'source_start_m': [0.02377026264271346, 0.522866202514797, 0.55], 'source_direction': [0.23770262642713458, -0.9713379748520297, 0], 'glb_start_m': [0.02377026264271346, 0.55, -0.522866202514797], 'glb_direction': [0.23770262642713458, 0, 0.9713379748520297], 'ray_length_m': 0.63}, {'source_start_m': [0.02377026264271346, 0.522866202514797, 0.73], 'source_direction': [0.23770262642713458, -0.9713379748520297, 0], 'glb_start_m': [0.02377026264271346, 0.73, -0.522866202514797], 'glb_direction': [0.23770262642713458, 0, 0.9713379748520297], 'ray_length_m': 0.63}, {'source_start_m': [0.0706825181105366, 0.54926117308328, 0.26], 'source_direction': [0.706825181105366, -0.7073882691671998, 0], 'glb_start_m': [0.0706825181105366, 0.26, -0.54926117308328], 'glb_direction': [0.706825181105366, 0, 0.7073882691671998], 'ray_length_m': 0.63}, {'source_start_m': [0.0706825181105366, 0.54926117308328, 0.38], 'source_direction': [0.706825181105366, -0.7073882691671998, 0], 'glb_start_m': [0.0706825181105366, 0.38, -0.54926117308328], 'glb_direction': [0.706825181105366, 0, 0.7073882691671998], 'ray_length_m': 0.63}, {'source_start_m': [0.0706825181105366, 0.54926117308328, 0.55], 'source_direction': [0.706825181105366, -0.7073882691671998, 0], 'glb_start_m': [0.0706825181105366, 0.55, -0.54926117308328], 'glb_direction': [0.706825181105366, 0, 0.7073882691671998], 'ray_length_m': 0.63}, {'source_start_m': [0.0706825181105366, 0.54926117308328, 0.73], 'source_direction': [0.706825181105366, -0.7073882691671998, 0], 'glb_start_m': [0.0706825181105366, 0.73, -0.54926117308328], 'glb_direction': [0.706825181105366, 0, 0.7073882691671998], 'ray_length_m': 0.63}, {'source_start_m': [0.09711483779210446, 0.5961523946566277, 0.26], 'source_direction': [0.9711483779210446, -0.23847605343372313, 0], 'glb_start_m': [0.09711483779210446, 0.26, -0.5961523946566277], 'glb_direction': [0.9711483779210446, 0, 0.23847605343372313], 'ray_length_m': 0.63}, {'source_start_m': [0.09711483779210446, 0.5961523946566277, 0.38], 'source_direction': [0.9711483779210446, -0.23847605343372313, 0], 'glb_start_m': [0.09711483779210446, 0.38, -0.5961523946566277], 'glb_direction': [0.9711483779210446, 0, 0.23847605343372313], 'ray_length_m': 0.63}, {'source_start_m': [0.09711483779210446, 0.5961523946566277, 0.55], 'source_direction': [0.9711483779210446, -0.23847605343372313, 0], 'glb_start_m': [0.09711483779210446, 0.55, -0.5961523946566277], 'glb_direction': [0.9711483779210446, 0, 0.23847605343372313], 'ray_length_m': 0.63}, {'source_start_m': [0.09711483779210446, 0.5961523946566277, 0.73], 'source_direction': [0.9711483779210446, -0.23847605343372313, 0], 'glb_start_m': [0.09711483779210446, 0.73, -0.5961523946566277], 'glb_direction': [0.9711483779210446, 0, 0.23847605343372313], 'ray_length_m': 0.63}], 'actual_check_file': 'qa/interface_checks.json', 'scope': 'Actual GLB triangle rays at 3 angular bays and 4 service heights clear to radius .73m. Rays demonstrate sampled openings only, not universal actor/body/hand envelope, food hygiene or implemented interaction. Radial shelf supports and closed end bulkheads are excluded from access rays.'}
def conv(p):return[p[0],p[2],-p[1]]
def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1

def mesh(name,verts,faces,role,bevel=0,group='static',grain='vertical'):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);ob['material_role']=role;ob['functional_group']=group;ob['original_authoring']='Original Python-assisted profile and joinery construction';ob['uv_grain']=grain
 uv=me.uv_layers.new(name='metric_material_uv');s=MATS[role]['meters_per_tile_uv']
 for face in me.polygons:
  axis=max(range(3),key=lambda k:abs(face.normal[k]));ax=[k for k in range(3) if k!=axis]
  for li in face.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;u,v=p[ax[0]],p[ax[1]];uv.data[li].uv=(u/s[0],v/s[1])
 if bevel:
  mod=ob.modifiers.new('Editable edge easing','BEVEL');mod.width=bevel;mod.segments=1;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
  mod=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 return ob

def box(name,center,size,role,bevel=.001,group='static'):
 x,y,z=center;a,b,c=[t/2 for t in size];v=[(x+dx,y+dy,z+dz) for dx,dy,dz in[(-a,-b,-c),(a,-b,-c),(a,b,-c),(-a,b,-c),(-a,-b,c),(a,-b,c),(a,b,c),(-a,b,c)]]
 return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,group)

def st(kind,s):
 if kind=='straight':return(s,0,1,0,s)
 t=s/R;return(R*math.sin(t),R*(1-math.cos(t)),math.cos(t),math.sin(t),s)
def total(kind):return P if kind=='straight' else R*math.pi/2

def rows(kind,a=None,b=None,n=None):
 a=.001 if a is None else a;b=total(kind)-.001 if b is None else b;n=(1 if kind=='straight' else max(1,math.ceil((b-a)/total(kind)*24))) if n is None else n
 out=[st(kind,a+(b-a)*i/n) for i in range(n+1)]
 if kind=='turn':
  # Exact planar seam faces: +X entry and +Y exit, with 1mm inset.
  if abs(a-.001)<1e-8:out[0]=(.001,0,1,0,a)
  if abs(b-(total(kind)-.001))<1e-8:out[-1]=(R,R-.001,0,1,b)
 return out

def sweep(name,rs,profile,role,bevel=0,group='static'):
 n=len(profile);verts=[(x-ty*d,y+tx*d,z) for x,y,tx,ty,s in rs for d,z in profile];faces=[]
 for k in range(len(rs)-1):faces.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
 faces += [tuple(reversed(range(n))),tuple((len(rs)-1)*n+j for j in range(n))]
 ob=mesh(name,verts,faces,role,bevel,group);uv=ob.data.uv_layers.active;scale=MATS[role]['meters_per_tile_uv']
 for face in ob.data.polygons:
  cap=face.index>=len(faces)-2
  for li in face.loop_indices:
   k,j=divmod(ob.data.loops[li].vertex_index,n);d,z=profile[j]
   # Vertical grain on walnut/ivory profile, useful planar UV on horizontal shelves.
   if cap:u,v=d,z
   elif abs(face.normal.z)>.8:u,v=rs[k][4],d
   else:u,v=rs[k][4],z
   uv.data[li].uv=(u/scale[0],v/scale[1])
 ob['profile_depth_height_m']=json.dumps(profile);return ob

def panel(name,kind,a,b,d0,d1,z0,z1,role='staff_zinc',group='static'):
 return sweep(name,rows(kind,a,b),[(d0,z0),(d1,z0),(d1,z1),(d0,z1)],role,.0008,group)

def build(kind,ident):
 reset();obs=[];L=total(kind);rs=rows(kind)
 def add(ob):obs.append(ob);return ob
 add(sweep('continuous_eased_stone_worktop',rs,TOP,'warm_stone'))
 add(sweep('bowed_guest_walnut_shell',rs,FACIA,'warm_walnut'))
 add(sweep('upper_ivory_bullnose_rail',rs,UPPER,'ivory_enamel'))
 add(sweep('lower_ivory_swept_rail',rs,LOWER,'ivory_enamel'))
 add(sweep('single_champagne_shadow_reveal',rs,[(-.370,.823),(-.372,.823),(-.372,.837),(-.370,.837)],'champagne_metal'))
 add(panel('recessed_front_floor_plinth',kind,.001,L-.001,-.282,-.250,0,.142,'dark_rubber'))
 add(panel('rear_recessed_floor_plinth',kind,.001,L-.001,.238,.268,0,.142,'dark_rubber'))
 add(panel('load_bearing_base_shelf',kind,.022,L-.022,-.310,.350,.142,.164,'staff_zinc'))
 add(panel('rear_top_support_rail',kind,.022,L-.022,.303,.350,.816,.852,'ivory_enamel'))
 for s0,s1,label in[(.001,.027,'entry'),(L-.027,L-.001,'exit')]:add(sweep(label+'_closed_shaped_terminal_bulkhead',rows(kind,s0,s1),END,'ivory_enamel'))
 # Broad economical timber ribs echo the reference's continuous joinery rhythm.
 count=26 if kind=='straight' else 16
 for i in range(count):
  center=.065+(L-.130)*i/(count-1);w=.026 if kind=='straight' else .017
  outer=[(d-.008,z) for d,z in FACE[1:-1]];inner=[(d+.002,z) for d,z in reversed(FACE[1:-1])]
  add(sweep(f'vertical_walnut_rib_{i+1:02d}',rows(kind,center-w/2,center+w/2,1),outer+inner,'warm_walnut'))
 if kind=='straight':
  for i,x in enumerate((.80,1.60)):
   add(box(f'load_bearing_bay_divider_{i+1}',(x,.026,.492),(.024,.634,.656),'ivory_enamel'))
  for name,a,b in [('left',.027,.788),('right',1.612,2.373)]:
   add(panel(name+'_open_service_shelf',kind,a,b,-.301,.340,.447,.466,'staff_zinc',name+'_removable_shelf'))
   add(panel(name+'_shelf_rear_retaining_upstand',kind,a,b,-.301,-.288,.466,.496,'staff_zinc',name+'_removable_shelf'))
   add(panel(name+'_shelf_front_rolled_lip',kind,a,b,.328,.343,.447,.476,'staff_zinc',name+'_removable_shelf'))
  add(panel('centre_lower_service_shelf',kind,.812,1.588,-.301,.340,.447,.466,'staff_zinc','centre_removable_shelf'))
  # Usable 0.690 x 0.535 internal drawer below worktop, separately named moving group.
  group='proposed_linen_drawer';add(box('drawer_open_pan_bottom',(1.2,.040,.655),(.724,.600,.018),'staff_zinc',.001,group))
  for label,x in [('left',.842),('right',1.558)]:add(box('drawer_'+label+'_side',(x,.040,.727),(.012,.600,.144),'staff_zinc',.001,group))
  add(box('drawer_rear_wall',(1.2,-.252,.727),(.704,.016,.144),'staff_zinc',.001,group))
  add(box('drawer_ivory_front',(1.2,.354,.728),(.746,.030,.170),'ivory_enamel',.005,group))
  # U-shaped grip with actual finger gap, no invisible spanning plate.
  for x in(1.040,1.360):add(box('drawer_grip_standoff_'+str(x),(x,.388,.750),(.018,.040,.020),'champagne_metal',.003,group))
  add(box('drawer_grip_horizontal',(1.2,.411,.750),(.342,.016,.020),'champagne_metal',.003,group))
  for x in(.830,1.570):add(box('fixed_drawer_runner_'+str(x),(x,.030,.635),(.030,.594,.022),'staff_zinc'))
  # Guide and identity metadata remain in source and actual export functional groups.
  grip=[1.2,.411,.750]
 else:
  add(panel('curved_open_service_shelf',kind,.028,L-.028,-.304,.337,.447,.466,'staff_zinc','curved_removable_shelf'))
  add(panel('curved_shelf_inner_rolled_lip',kind,.028,L-.028,.325,.341,.447,.476,'staff_zinc','curved_removable_shelf'))
  add(panel('curved_shelf_outer_retaining_upstand',kind,.028,L-.028,-.304,-.290,.466,.492,'staff_zinc','curved_removable_shelf'))
  # Two slim radial shelf supports preserve the open inner service arc.
  for i,s in enumerate((L*.31,L*.69)):
   add(panel(f'curved_shelf_radial_support_{i+1}',kind,s-.010,s+.010,-.296,.317,.164,.447,'ivory_enamel'))
  grip=None
 bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get();points=[];tri=0
 for o in obs:
  e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);points += [o.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
 lo=[min(p[k] for p in points) for k in range(3)];hi=[max(p[k] for p in points) for k in range(3)]
 sources=BASE/'source'/f'{ident}.blend';dest=BASE/'exports'/f'{ident}.glb'
 # Explicit source markers are data properties, not visual or collision geometry.
 bpy.context.scene['catalogue_id']=ident;bpy.context.scene['source_frame']='Blender metres +Z up, guest -Y at entry; entry floor seam datum';bpy.context.scene['original_script_assisted']=True
 bpy.ops.wm.save_as_mainfile(filepath=str(sources),compress=True)
 export(obs,dest,ident)
 end=[P,0,0] if kind=='straight' else[R,R,0]
 joints=[{'name':'entry','origin_source_m':[0,0,0],'outward_tangent_source':[-1,0,0],'origin_glb_m':[0,0,0],'outward_tangent_glb':[-1,0,0]}, {'name':'exit','origin_source_m':end,'outward_tangent_source':[1,0,0] if kind=='straight' else[0,1,0],'origin_glb_m':conv(end),'outward_tangent_glb':[1,0,0] if kind=='straight' else[0,0,-1]}]
 physical=[{'name':'floor_front_plinth','source_m':[.25,-.265,0] if kind=='straight' else list(worldpoint(kind,L*.5,-.265,0)),'surface':'recessed_front_floor_plinth','kind':'physical_contact'}, {'name':'host_worktop_support','source_m':[.70,0,.90] if kind=='straight' else list(worldpoint(kind,L*.5,0,.90)),'surface':'continuous_eased_stone_worktop','kind':'physical_contact'}]
 for p in physical:p['glb_m']=conv(p['source_m'])
 rec={'catalogue_id':ident,'name':'Fitted hospitality pantry counter' if kind=='straight' else'Compatible curved hospitality return','dimensions_blender_xyz_m':[hi[k]-lo[k] for k in range(3)],'title':'Fitted hospitality pantry counter' if kind=='straight' else'Compatible curved hospitality return','unique_design':True,'units':'metres','source':str(sources.relative_to(BASE)),'export':str(dest.relative_to(BASE)),'generator':'source/build_hospitality_counters.py','script_assisted_original_design':True,'provenance':'Original intentionally shaped geometry and script; actual hospitality reference pixels inspected. Frozen shared original material helpers reused. No imported game meshes or recovered-source claim.','source_frame':'Blender +Z up, guest front -Y at entry, staff +Y, entry floor seam datum','glb_frame':'Native glTF +Y up, source (x,y,z)->(x,z,-y); actual node hierarchy authoritative','pivot_source_m':[0,0,0],'pivot_glb_m':[0,0,0],'bounds_blender_z_up':{'min_m':lo,'max_m':hi,'dimensions_m':[hi[k]-lo[k] for k in range(3)]},'evaluated_triangles':tri,'editable_semantic_parts':len(obs),'semantic_parts':[o.name for o in obs],'material_roles':sorted(set(o['material_role'] for o in obs)),'runtime_consolidation':'By semantic material role within functional group; removable shelves and proposed drawer remain distinct','joints':joints,'mating_section_file':'counter_interface.json','physical_contacts':physical,'nominal_worktop_z_m':.90,'nominal_depth_m':.78,'closed_terminal_treatment':'Entry and exit shaped ivory end bulkheads are fully closed meshes and support the stone slab. They remain in adjoining modules; no missing terminal cap is required.','staff_use':'Rear-open service shelving with raised retaining lip. Pan drawer translates +Y as proposal only.' if kind=='straight' else'Inside-curve open shelving with radial supports; countertop return surface; no door or appliance function.','drawer_proposal':{'source_axis':[0,1,0],'glb_axis':[0,0,-1],'travel_m':.32,'grip_source_m':grip,'grip_glb_m':conv(grip),'internal_clear_envelope_source_m':{'min':[.848,-.244,.664],'max':[1.552,.339,.798]},'external_proposed_sweep_source_m':{'min':[.827,-.260,.645],'max':[1.573,.739,.817]},'status':'named geometry and proposed linear slide only; no animation, physics or load claim'} if grip else None,'limitations':['Independent component catalogue only','No original game, room, physics, food hygiene, electrical, structural, species/accessibility or target-PC certification'],'source_sha256':hashlib.sha256(sources.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
 if kind=='turn':rec['staff_shelf_access']=CURVED_SERVICE_ACCESS
 (BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');RECORDS.append(rec)
 COLLISIONS[ident]=collisions(kind,obs)

def worldpoint(kind,s,d,z):
 x,y,tx,ty,_=st(kind,s);return(x-ty*d,y+tx*d,z)
def export(obs,path,ident):
 dg=bpy.context.evaluated_depsgraph_get();groups={}
 for src in obs:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));uv=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=uv:me.uv_layers.remove(layer)
  uv.name='metric_material_uv';uv.active_render=True;me.calc_loop_triangles();fix=set();scale=MATS[src['material_role']]['meters_per_tile_uv']
  for tr in me.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:fix.add(tr.polygon_index)
  for pi in fix:
   p=me.polygons[pi];axis=max(range(3),key=lambda k:abs(p.normal[k]));ax=[k for k in range(3) if k!=axis]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[ax[0]]/scale[0],co[ax[1]]/scale[1])
  ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault((src['functional_group'],src['material_role']),[]).append(ob)
 out=[]
 for (group,role),parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for p in parts:p.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=ident+'__'+group+'__'+role;ob['material_role']=role;ob['functional_group']=group;ob['semantic_parts']=json.dumps([s.name for s in obs if s['functional_group']==group and s['material_role']==role])
  if group=='proposed_linen_drawer':ob['translation_axis_blender_source']=[0,1,0];ob['translation_axis_gltf_yup']=[0,0,-1];ob['travel_proposal_m']=.32
  out.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in out:ob.select_set(True)
 bpy.context.view_layer.objects.active=out[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in out:bpy.data.objects.remove(ob,do_unlink=True)

def collisions(kind,obs):
 proposals=[]
 # Small per-part boxes for straight joinery; actual mesh vertices in segmented
 # convex profiles for curved shell/top preserve the concave staff-side opening.
 for ob in obs:
  if ob.name.startswith('vertical_walnut_rib') or 'champagne_shadow' in ob.name or 'grip' in ob.name:continue
  profile=json.loads(ob['profile_depth_height_m']) if 'profile_depth_height_m' in ob else None
  points=[list(v.co) for v in ob.data.vertices]
  if profile and kind=='turn' and len(points)>2*len(profile):
   n=len(profile)
   for k in range(len(points)//n-1):
    p=points[k*n:(k+2)*n];proposals.append({'semantic_part':ob.name,'segment':k,'type':'convex_hull_points','source_points_m':p,'glb_points_m':[conv(x) for x in p],'functional_group':ob['functional_group']})
  else:
   proposals.append({'semantic_part':ob.name,'type':'convex_hull_points','source_points_m':points,'glb_points_m':[conv(x) for x in points],'functional_group':ob['functional_group']})
 return{'source_frame':'Blender source metres +Z up','glb_frame':'Native glTF metres +Y up, converted from source point once','status':'Conservative offline convex piece proposals. Not assigned to any engine. Excludes thin ornament; retains shelf and drawer solids without filling open rear compartments. Concave curved pieces split by arc station.','proposals':proposals}

if __name__=='__main__':
 build('straight','AST-HSP-001');build('turn','AST-HSP-002')
 interface={'version':'hospitality-counter-interface-01','units':'metres','source_frame':'Blender +Z up, local seam travel +X, depth d toward staff +Y','glb_frame':'(x,y,z)->(x,z,-y), native glTF +Y up','profile_coordinates':'Pairs [d,z] in local travel frame; identical at both ends and both designs','profiles':{'stone_top':TOP,'walnut_shell':FACIA,'ivory_upper_rail':UPPER,'ivory_lower_rail':LOWER,'closed_terminal_bulkhead':END},'seam':'Nominal planes at each entry/exit, all main mesh inset 0.001 m. 0.002 m physical joint between adjacent matching modules. Each module remains closed.','AST-HSP-001':{'entry_source_m':[0,0,0],'exit_source_m':[P,0,0],'exit_tangent_source':[1,0,0],'usable_host_worktop_source_m':{'min':[.06,-.34,.90],'max':[2.34,.34,.90]},'proposed_beverage_origin_source_m':[.70,0,.90],'host_plane_normal_source':[0,0,1],'host_plane_normal_glb':[0,1,0]},'AST-HSP-002':{'entry_source_m':[0,0,0],'exit_source_m':[R,R,0],'exit_tangent_source':[0,1,0],'centerline_radius_m':R,'turn_degrees':90},'inspection_pair_placement_source':[{'id':'AST-HSP-001','translation_m':[0,0,0],'yaw_degrees':0},{'id':'AST-HSP-002','translation_m':[P,0,0],'yaw_degrees':0}],'closure':'Built-in closed shaped terminal bulkheads at both ends; no optional missing closure derivative','scope':'Component-only placement proposal, no approved room fit or installation'}
 for ident in['AST-HSP-001','AST-HSP-002']:
  for key,val in list(interface[ident].items()):
   if key.endswith('_source_m') and isinstance(val,list):interface[ident][key.replace('_source_m','_glb_m')]=conv(val)
 interface['AST-HSP-002']['staff_shelf_access']=CURVED_SERVICE_ACCESS
 (BASE/'counter_interface.json').write_text(json.dumps(interface,indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(COLLISIONS,indent=2)+'\n');(BASE/'manifest.json').write_text(json.dumps({'family':'Hospitality counters','unique_design_count':2,'assets':RECORDS},indent=2)+'\n')
 print('BUILD_COMPLETE',[(r['catalogue_id'],r['evaluated_triangles'],r['editable_semantic_parts']) for r in RECORDS])
