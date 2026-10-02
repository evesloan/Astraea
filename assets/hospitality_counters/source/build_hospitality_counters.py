"""Original script-assisted editable hospitality counters, Blender 4.3.2.
No game geometry or external mesh assets. Frozen shared material helpers reused.
"""
import bpy,bmesh,math,json,hashlib,importlib.util,sys
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
 COLLISIONS[ident]=collisions(kind,obs)
 rec['collision_proposal']=collision_manifest_record(ident,COLLISIONS[ident])
 (BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');RECORDS.append(rec)

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

# Batch08 collision revision: consolidate actual source rows, never rebuild visuals
# in --collision-only mode. Profile bands retain the real bowed fascia instead
# of the prior whole-profile infill. A radial chord bound chooses the arc span.
COLLISION_REVISION='hospitality-static-compound-03'
COLLISION_CHORD_LIMIT_M=.005

def profile_overreach_bound(profile):
 """Exact depth-axis bound of a 2D convex profile at every input height.
 Piecewise-linear source/envelope differences attain maxima at these knots.
 """
 outer=profile;pts=sorted(set(tuple(p) for p in outer+[(d+.024,z) for d,z in outer]))
 def cross(o,a,b):return(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[]
 for p in pts:
  while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
  lower.append(p)
 upper=[]
 for p in reversed(pts):
  while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
  upper.append(p)
 hull=lower[:-1]+upper[:-1];error=0.
 for d,z in outer:
  depths=[]
  for a,b in zip(hull,hull[1:]+hull[:1]):
   if min(a[1],b[1])-1e-10<=z<=max(a[1],b[1])+1e-10:
    if abs(a[1]-b[1])<1e-10:depths.extend([a[0],b[0]])
    else:depths.append(a[0]+(b[0]-a[0])*(z-a[1])/(b[1]-a[1]))
  error=max(error,d-min(depths),max(depths)-d-.024)
 return max(0.,error)

def collision_sections(kind,parts):
 """Pure data operation, shared by normal builds and read-only source reloads.

 Each part supplies source-frame raw vertices in profile-row order plus its
 2D profile. Bounds are
 derived from those actual points, including the special planar seam rows.
 """
 parts={p['name']:p.copy() for p in parts}
 # The old whole-fascia hull filled genuine lower-shelf depth. Split its bowed
 # profile first. Only adjacent spans with <=5mm exact depth infill can combine.
 fascia=parts.pop('bowed_guest_walnut_shell');profile=fascia['profile'];half=len(profile)//2
 outer=profile[:half];first=0;band=0
 while first<half-1:
  last=first+1
  while last+1<half and profile_overreach_bound(outer[first:last+2])<=.005+1e-12:last+=1
  inds=list(range(first,last+1))+[len(profile)-1-j for j in reversed(range(first,last+1))]
  pts=fascia['points'];sub=fascia.copy();sub['points']=[pts[k+j] for k in range(0,len(pts),len(profile)) for j in inds]
  sub['profile_size']=len(inds);sub['semantic_parts']=['bowed_guest_walnut_shell'];sub['semantic_name']='bowed_guest_walnut_shell'
  sub['profile_vertex_interval']=[first,last];sub['profile_depth_overreach_bound_m']=profile_overreach_bound(outer[first:last+1])
  parts[f'bowed_guest_walnut_shell__profile_band_{band}']=sub;first=last;band+=1
 # Follow the actual toe step and changes in guest-facing terminal curvature.
 # Four height pieces remove both the toe void fill and old guest-side bulges.
 def clip_height(poly,z,above):
  out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=a[2]>=z if above else a[2]<=z;ib=b[2]>=z if above else b[2]<=z
   if ia:out.append(a)
   if ia!=ib:
    t=(z-a[2])/(b[2]-a[2]);out.append([a[k]+t*(b[k]-a[k]) for k in range(3)])
  return out
 for terminal in ['entry_closed_shaped_terminal_bulkhead','exit_closed_shaped_terminal_bulkhead']:
  part=parts.pop(terminal);n=part['profile_size'];points=part['points']
  for label,lo,hi in [('foot',0.,.124),('lower_return',.124,.164),
                      ('middle_body',.164,.58),('upper_return',.58,.852)]:
   rows=[clip_height(clip_height(points[k:k+n],lo,True),hi,False) for k in range(0,len(points),n)]
   assert all(len(row)==len(rows[0]) for row in rows)
   sub=part.copy();sub['points']=[v for row in rows for v in row];sub['profile_size']=len(rows[0])
   sub['semantic_parts']=[terminal];sub['semantic_name']=terminal
   sub['profile_source_z_interval_m']=[lo,hi];parts[terminal+'__'+label]=sub
 # The small rolled front lip shares its shelf's row stations and lower face.
 # Keep the higher rear upstand separate, avoiding a wedge across shelf access.
 pairs=([('left_open_service_shelf','left_shelf_front_rolled_lip'),
         ('right_open_service_shelf','right_shelf_front_rolled_lip')]
        if kind=='straight' else
        [('curved_open_service_shelf','curved_shelf_inner_rolled_lip')])
 for shelf,lip in pairs:
  a=parts[shelf];b=parts.pop(lip);na=a['profile_size'];nb=b['profile_size']
  assert len(a['points'])//na==len(b['points'])//nb
  aa=a['points'];bb=b['points'];a['points']=[]
  for i in range(len(aa)//na):a['points']+=aa[i*na:(i+1)*na]+bb[i*nb:(i+1)*nb]
  a['profile_size']=na+nb;a['semantic_parts']=[shelf,lip]
 proposals=[]
 for name,p in sorted(parts.items()):
  points=p['points'];n=p['profile_size'];nrows=len(points)//n if n else 1
  # Upper rear rail has only 4mm source clearance to the deep shelf endpoint.
  # Limit its chord to2.5mm, preserving that real thin clearance.
  chord_limit=min(COLLISION_CHORD_LIMIT_M,.0025) if name=='upper_ivory_bullnose_rail' else COLLISION_CHORD_LIMIT_M
  start=0
  while start < (nrows-1 if kind=='turn' and nrows>2 else 1):
   stop=start+1
   if kind=='turn' and nrows>2:
    while stop+1<nrows:
     trial=points[start*n:(stop+2)*n]
     radii=[math.hypot(x,R-y) for x,y,z in trial]
     angles=[math.atan2(x,R-y) for x,y,z in trial]
     bound=max(radii)*(1-math.cos((max(angles)-min(angles))/2))
     if bound>chord_limit+1e-12:break
     stop+=1
    chosen=points[start*n:(stop+1)*n]
   else:chosen=points
   angles=[math.atan2(x,R-y) for x,y,z in chosen] if kind=='turn' else []
   chord=max(math.hypot(x,R-y) for x,y,z in chosen)*(1-math.cos((max(angles)-min(angles))/2)) if angles else 0.
   semantic_name=p.get('semantic_name',name)
   rec={'semantic_part':semantic_name,'semantic_parts':p.get('semantic_parts',[name]),
        'section':sum(q['semantic_part']==semantic_name for q in proposals),
        'type':'convex_hull_points','source_points_m':chosen,
        'glb_points_m':[conv(x) for x in chosen],
        'functional_group':p['functional_group'],
        'source_row_interval':[start,stop] if nrows>2 and kind=='turn' else [0,max(0,nrows-1)],
        'maximum_radial_chord_bound_m':chord,'radial_chord_limit_m':chord_limit}
   if 'profile_vertex_interval' in p:rec['profile_vertex_interval']=p['profile_vertex_interval'];rec['profile_depth_overreach_bound_m']=p['profile_depth_overreach_bound_m']
   if 'profile_source_z_interval_m' in p:rec['profile_source_z_interval_m']=p['profile_source_z_interval_m']
   proposals.append(rec)
   start=stop if kind=='turn' and nrows>2 else 1
 return {'source_frame':'Blender source metres +Z up',
         'glb_frame':'Native glTF metres +Y up, source (x,y,z) converted once to (x,z,-y)',
         'revision':COLLISION_REVISION,'maximum_radial_chord_limit_m':COLLISION_CHORD_LIMIT_M,
         'status':f'Offline static compound proposal. Continuous source profile rows consolidated within a {COLLISION_CHORD_LIMIT_M*1000:g} mm radial chord bound. Bowed fascia split into source-backed vertical bands with at most 5 mm profile-depth infill; rails, slab, floor plinths, base shelf, higher shelf upstands, end bulkheads and radial supports remain distinct. Front rolled lips join their own shelf; drawer stays separate. Thin decorative ribs, reveal and drawer grip remain omitted. No engine physics or performance certification.',
         'approximation_note':'All represented source triangles remain covered. Prior whole-fascia convexification is intentionally removed because it blocked real lower shelf depth. Arc consolidation and shelf/lip convexification can occupy nearby empty space; measured two-sided source-surface error and bounded access evidence are in qa/batch08/counter_collision_revision/validation_report.json.',
         'proposals':proposals}

def collisions(kind,obs):
 parts=[]
 for ob in obs:
  if ob.name.startswith('vertical_walnut_rib') or 'champagne_shadow' in ob.name or 'grip' in ob.name:continue
  profile=json.loads(ob['profile_depth_height_m']) if 'profile_depth_height_m' in ob else None
  parts.append({'name':ob.name,'profile_size':len(profile) if profile else 0,'profile':profile,
                'points':[list(ob.matrix_world@v.co) for v in ob.data.vertices],
                'functional_group':ob['functional_group']})
 return collision_sections(kind,parts)

def collision_manifest_record(ident,data):
 return {'path':'collision_proposals.json','revision':data['revision'],
         'shape_count':len(data['proposals']),
         'baseline_batch07_shape_count':26 if ident=='AST-HSP-001' else 263,
         'maximum_radial_chord_limit_m':data['maximum_radial_chord_limit_m'],
         'maximum_fascia_profile_depth_limit_m':.005,
         'maximum_upper_rail_radial_chord_limit_m':min(data['maximum_radial_chord_limit_m'],.0025),
         'terminal_profile_height_cuts_source_z_m':[.124,.164,.58],
         'drawer_separate_convex_piece_count':sum(p['functional_group']=='proposed_linen_drawer' for p in data['proposals']),
         'source_frame':data['source_frame'],'glb_frame':data['glb_frame'],
         'validation_catalogue_relative_path':'qa/batch08/counter_collision_revision/validation_report.json',
         'status':'Offline compound proposal only; no engine setup or performance certification'}

def collision_only(output_path=None):
 """Read existing masters; write only collision_proposals.json. Never save/export."""
 protected=[BASE/'source'/f'{ident}.blend' for ident in ['AST-HSP-001','AST-HSP-002']]
 protected += [BASE/'exports'/f'{ident}.glb' for ident in ['AST-HSP-001','AST-HSP-002']]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
 result={}
 for kind,ident in [('straight','AST-HSP-001'),('turn','AST-HSP-002')]:
  bpy.ops.wm.open_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'))
  obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
  result[ident]=collisions(kind,obs)
 after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
 assert before==after,'Read-only collision generation changed a protected visual/source'
 output_path=BASE/'collision_proposals.json' if output_path is None else Path(output_path)
 if output_path.suffix!='.json':raise ValueError('Collision output must be a JSON file')
 output_path.write_text(json.dumps(result,indent=2)+'\n')
 print('COLLISION_ONLY_COMPLETE',[(k,len(v['proposals'])) for k,v in result.items()])

if __name__=='__main__':
 if '--collision-chord-limit-m' in sys.argv:
  COLLISION_CHORD_LIMIT_M=float(sys.argv[sys.argv.index('--collision-chord-limit-m')+1])
  if not 0<COLLISION_CHORD_LIMIT_M<=.010:raise ValueError('Chord limit must be positive and at most 0.010 m')
 if '--collision-only' in sys.argv:
  collision_only(sys.argv[sys.argv.index('--collision-output')+1] if '--collision-output' in sys.argv else None);sys.exit(0)
 build('straight','AST-HSP-001');build('turn','AST-HSP-002')
 interface={'version':'hospitality-counter-interface-01','units':'metres','source_frame':'Blender +Z up, local seam travel +X, depth d toward staff +Y','glb_frame':'(x,y,z)->(x,z,-y), native glTF +Y up','profile_coordinates':'Pairs [d,z] in local travel frame; identical at both ends and both designs','profiles':{'stone_top':TOP,'walnut_shell':FACIA,'ivory_upper_rail':UPPER,'ivory_lower_rail':LOWER,'closed_terminal_bulkhead':END},'seam':'Nominal planes at each entry/exit, all main mesh inset 0.001 m. 0.002 m physical joint between adjacent matching modules. Each module remains closed.','AST-HSP-001':{'entry_source_m':[0,0,0],'exit_source_m':[P,0,0],'exit_tangent_source':[1,0,0],'usable_host_worktop_source_m':{'min':[.06,-.34,.90],'max':[2.34,.34,.90]},'proposed_beverage_origin_source_m':[.70,0,.90],'host_plane_normal_source':[0,0,1],'host_plane_normal_glb':[0,1,0]},'AST-HSP-002':{'entry_source_m':[0,0,0],'exit_source_m':[R,R,0],'exit_tangent_source':[0,1,0],'centerline_radius_m':R,'turn_degrees':90},'inspection_pair_placement_source':[{'id':'AST-HSP-001','translation_m':[0,0,0],'yaw_degrees':0},{'id':'AST-HSP-002','translation_m':[P,0,0],'yaw_degrees':0}],'closure':'Built-in closed shaped terminal bulkheads at both ends; no optional missing closure derivative','scope':'Component-only placement proposal, no approved room fit or installation'}
 for ident in['AST-HSP-001','AST-HSP-002']:
  for key,val in list(interface[ident].items()):
   if key.endswith('_source_m') and isinstance(val,list):interface[ident][key.replace('_source_m','_glb_m')]=conv(val)
 interface['AST-HSP-002']['staff_shelf_access']=CURVED_SERVICE_ACCESS
 (BASE/'counter_interface.json').write_text(json.dumps(interface,indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(COLLISIONS,indent=2)+'\n');(BASE/'manifest.json').write_text(json.dumps({'family':'Hospitality counters','unique_design_count':2,'collision_revision':COLLISION_REVISION,'collision_piece_count':sum(len(a['proposals']) for a in COLLISIONS.values()),'assets':RECORDS},indent=2)+'\n')
 print('BUILD_COMPLETE',[(r['catalogue_id'],r['evaluated_triangles'],r['editable_semantic_parts']) for r in RECORDS])
