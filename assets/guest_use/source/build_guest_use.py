"""Astraea original script-assisted guest-use components, Blender 4.3.2.

Rebuild from source plus explicit shared material dependencies; no QA files read.
blender --background --threads 2 --python-exit-code 1 --python source/build_guest_use.py
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parents[1]; CAT=BASE.parents[1]
for name in ('source','exports','qa'): (BASE/name).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('guest_shared_materials',CAT/'standards/materials.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod); MATS=mod.materials()
PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[]
def glb(p):return [p[0],p[2],-p[1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reset(ident):
 global PARTS,MARKERS,JOINS,COLL,VOIDS,ROOT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident
 ROOT['scope']='Static original catalogue component; no engine lighting, physics, species or fit claim'
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc['catalogue_id']=ident
def mesh(name,verts,faces,role='warm_walnut',bevel=0,grain=2):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=ROOT
 ob['material_role']=role;ob['grain_source_axis']=grain;ob['provenance']='Original script-assisted shaped guest component'
 me.materials.append(MATS[role]);uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True
 sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  normal=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=normal]
  if role=='warm_walnut' and grain in axes: axes=[a for a in axes if a!=grain]+[grain]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)
 if bevel:
  m=ob.modifiers.new('Editable edge easing','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m.angle_limit=math.radians(35)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 PARTS.append(ob);return ob
def box(name,c,d,role='warm_walnut',bevel=.003,grain=2):
 x,y,z=c;a,b,h=[v/2 for v in d]
 return mesh(name,[(x+i*a,y+j*b,z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,grain)
def extrude(name,profile,axis,a,b,role='warm_walnut',bevel=.003,grain=2):
 axes=[k for k in range(3) if k!=axis];vs=[]
 for dep in (a,b):
  for p in profile:
   v=[0,0,0];v[axis]=dep;v[axes[0]]=p[0];v[axes[1]]=p[1];vs.append(v)
 n=len(profile);fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,role,bevel,grain)
def rod(name,a,b,r,role='champagne_metal',n=12):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();seed=Vector((1,0,0)) if abs(d.x)<.9 else Vector((0,1,0));u=d.cross(seed).normalized();v=d.cross(u)
 vs=[p+r*(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n)) for p in(a,b) for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,0)
def rounded(w,d,r):
 out=[]
 for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for i in range(4):
   t=math.radians(start+i*30);out.append((cx+r*math.cos(t),cy+r*math.sin(t)))
 return out
def tray(name,c,w,d,h,role='ivory_enamel',r=.028):
 p=rounded(w,d,min(r,w/3,d/3));return extrude(name,[(c[0]+x,c[1]+y)for x,y in p],2,c[2]-h/2,c[2]+h/2,role,.001,0)
def marker(name,p,kind,part=None,direction=None,description=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o.location=p;o.empty_display_size=.025;o['marker_kind']=kind;o['frame']='Blender source metres Z-up; actual GLB node transform is exchange authority'
 row={'name':name,'kind':kind,'source_m':list(p),'gltf_m':glb(p),'physical_part':part,'description':description}
 if direction:row.update(direction_source=direction,direction_gltf=glb(direction));o['direction_source']=direction;o['direction_gltf']=glb(direction)
 o['source_position_m']=list(p);o['gltf_position_m']=glb(p);o['physical_part']=part or '';MARKERS.append(row);return o
def join(name,a,b,p):
 marker('JOIN_'+name,p,'physical_joint',description=a+' bears into '+b)
 JOINS.append({'name':name,'parts':[a,b],'probe_source_m':list(p),'probe_gltf_m':glb(p),'check':'Probe lies on or within both evaluated meshes; nearest-boundary distances are evidence, not assumed AABB contact'})
def collision_box(name,lo,hi):
 COLL.append({'name':name,'type':'box','min_source_m':lo,'max_source_m':hi,'min_gltf_m':[lo[0],lo[2],-hi[1]],'max_gltf_m':[hi[0],hi[2],-lo[1]]})
def collision_hull(name,points):
 COLL.append({'name':name,'type':'convex_hull_points','points_source_m':points,'points_gltf_m':[glb(p)for p in points]})
def shade(name,x,y,z,w,d,h):
 # Hollow faceted hood: sloped crown and offset mouth, closed thin top, open rim.
 rings=[(w,d,y-.028,z),(w*.81,d*.76,y-.012,z+h*.58),(w*.44,d*.38,y,z+h)]
 verts=[]
 for inner in (False,True):
  for rw,rd,cy,zz in rings:
   if inner:rw-=.012;rd-=.012;zz-=.006 if zz>z else 0
   verts.extend((x+px,cy+py,zz)for px,py in rounded(rw,rd,min(.033,rw/5,rd/5)))
 n=16;fs=[]
 for off in(0,48):
  for row in range(2):fs.extend((off+row*n+i,off+row*n+(i+1)%n,off+(row+1)*n+(i+1)%n,off+(row+1)*n+i)for i in range(n))
 fs.extend((i,(i+1)%n,48+(i+1)%n,48+i)for i in range(n));fs.extend([tuple(32+i for i in range(n)),tuple(80+i for i in range(n))])
 shell=mesh(name+'_hollow_shield',verts,fs,'ivory_enamel',0)
 # Recessed opaque diffuser is geometry/material only, no emission or runtime light.
 lens=tray(name+'_recessed_diffuser',(x,y-.023,z+.025),w*.90,d*.87,.008,'oatmeal_weave',.027)
 rim=tray(name+'_crown_fixing_cap',(x,y,z+h+.002),w*.48,d*.43,.012,'champagne_metal',.018)
 for sign in(-1,1):
  xx=x+sign*w*.34
  clip=box(name+'_diffuser_retaining_clip_'+str(sign),(xx,y-.022,z+.023),(.018,d*.46,.013),'champagne_metal',.001)
  marker(name.upper()+'_DIFFUSER_CLIP_'+str(sign),(xx,y-.022,z+.0165),'physical_service_fastener',clip.name,[0,0,-1],'Static retaining clip; diffuser service withdrawal direction is downward; no animation or electrical behavior')
 marker(name.upper()+'_DIFFUSER',(x,y-.023,z+.021),'physical_receiver',lens.name,[0,0,-1],'Opaque recessed diffuser underside, not light output')
 marker(name.upper()+'_READING_AIM',(x,y-.19,z-.45),'nonphysical_direction_target',None,[0,-.35,-.93675],'Proposed reading aim only; no photometry or species-fit claim')
 return shell,lens,rim
def floor_lamp():
 for x in(-.128,.128):
  box('floor_pad_'+str(x),(x,-.032,.006),(.066,.382,.012),'dark_rubber',.002)
  extrude('tapered_runner_'+str(x),[(-.223,.012),(.159,.012),(.159,.041),(.112,.067),(-.165,.041),(-.223,.031)],0,x-.037,x+.037,'warm_walnut',.003,1)
  marker('FLOOR_CONTACT_'+str(x),(x,-.032,0),'physical_floor_contact','floor_pad_'+str(x),[0,0,-1])
  collision_box('runner_'+str(x),[x-.037,-.223,0],[x+.037,.159,.067])
 base=box('rear_cross_foot',(0,.096,.050),(.286,.075,.054),'warm_walnut',.003,0)
 stem=extrude('swept_tapered_walnut_blade',[(.066,.057),(.128,.057),(.119,.60),(.096,1.11),(.047,1.356),(.002,1.345),(.044,1.095),(.064,.60)],0,-.031,.031,'warm_walnut',.003,2)
 join('blade_to_crossfoot',stem.name,base.name,[0,.093,.066])
 rod('neck_structural_arm',(0,.030,1.335),(0,-.078,1.405),.018)
 rod('neck_end_collar',(0,-.047,1.385),(0,-.082,1.410),.024)
 sh,di,cap=shade('floor',0,-.141,1.325,.348,.248,.156)
 join('neck_to_blade','neck_structural_arm',stem.name,[0,.024,1.337])
 join('neck_to_shield','neck_end_collar',sh.name,[0,-.060,1.394])
 rod('rear_concealed_power_gland',(0,.126,.049),(0,.147,.049),.010,'dark_rubber',10)
 marker('FLOOR_POWER_ENTRY',(0,.147,.049),'physical_service_power_entry','rear_concealed_power_gland',[0,1,0],'Concealed rear base cable-entry proposal; no cable, voltage or electrical behavior defined')
 box('switch_mount_inset',(0,.047,.99),(.044,.023,.074),'champagne_metal',.003)
 box('raised_switch_rocker',(0,.030,.991),(.026,.014,.044),'dark_rubber',.002)
 box('switch_locator_bar',(0,.0225,1.000),(.013,.002,.004),'ivory_enamel',.0003)
 marker('READING_SWITCH',(0,.023,.991),'physical_switch_surface','raised_switch_rocker',[0,-1,0],'Static rocker geometry; no electrical action')
 join('switch_to_blade','switch_mount_inset',stem.name,[0,.052,.99])
 marker('FLOOR_DATUM',(0,0,0),'placement_origin',None,[0,0,1])
 # Cross foot remains separate: no collider fills the open front of this U base.
 collision_box('crossfoot',[-.143,.0585,.023],[.143,.1335,.077])
 collision_hull('slender_blade',[[x,y,z]for x in(-.032,.032)for y,z in[(.063,.06),(.129,.06),(.097,1.12),(.047,1.36),(.001,1.35),(.043,1.10)]])
 collision_box('hood_only',[-.176,-.295,1.32],[.176,-.018,1.495])
 VOIDS.append({'name':'open_front_between_base_runners','min_source_m':[-.08,-.20,.014],'max_source_m':[.08,.035,.055],'purpose':'Keep the front base split; no whole-asset convex collider'})
 return 'Bent-blade reading floor lamp','Floor Z0; reading front -Y',{'intended_use':'Companion to day chair, aimed reading hood and a narrow open base. Stability/electrical output untested.'}
def sconce():
 # Source datum is wall plane Y0, local mount centre Z0; projecting front is -Y.
 plate=extrude('shaped_wall_backplate',[(-.070,-.170),(.070,-.170),(.090,-.136),(.090,.135),(.061,.168),(-.061,.168),(-.090,.135),(-.090,-.136)],1,-.023,0,'warm_walnut',.003,2)
 box('inset_metal_mount_plate',(0,-.026,0),(.118,.010,.274),'champagne_metal',.002)
 for z in(-.11,.11):
  rod('visible_fixing_boss_'+str(z),(0,-.036,z),(0,-.027,z),.010,'champagne_metal',10)
  box('fixing_slot_'+str(z),(0,-.0365,z),(.010,.001,.002),'dark_rubber',0)
  marker('WALL_FIXING_'+str(z),(0,0,z),'physical_wall_mount','shaped_wall_backplate',[0,1,0],'Backplate rear plane; substrate, screws and wiring unverified')
 arm=extrude('braced_sconce_arm',[(-.027,-.020),(-.156,.050),(-.181,.059),(-.191,.086),(-.160,.087),(-.025,.026)],0,-.024,.024,'champagne_metal',.002,1)
 sh,di,cap=shade('wall',0,-.192,.047,.258,.192,.120)
 rod('wall_hood_hub',(0,-.172,.080),(0,-.151,.137),.019)
 join('arm_to_mount',arm.name,'inset_metal_mount_plate',[0,-.028,.010])
 join('arm_to_hub',arm.name,'wall_hood_hub',[0,-.172,.083])
 join('hub_to_shield','wall_hood_hub',sh.name,[0,-.143,.133])
 marker('WALL_CONCEALED_POWER_ENTRY',(0,0,.032),'physical_service_power_entry','shaped_wall_backplate',[0,1,0],'Concealed supply entry datum behind mounting plate; no electrical behavior or drilled wall asserted')
 box('sconce_switch_bezel',(0,-.038,-.085),(.052,.014,.058),'ivory_enamel',.003)
 box('sconce_switch_rocker',(0,-.048,-.085),(.030,.014,.037),'dark_rubber',.002)
 box('sconce_switch_locator',(0,-.0555,-.078),(.014,.002,.004),'ivory_enamel',.0003)
 marker('WALL_READING_SWITCH',(0,-.055,-.085),'physical_switch_surface','sconce_switch_rocker',[0,-1,0],'Readable separate static rocker on backplate')
 marker('WALL_MOUNT_DATUM',(0,0,0),'placement_origin',None,[0,1,0],'Place wall plane Y0; illustrative QA datum is 1.36 m above floor')
 collision_box('wall_plate',[-.090,-.032,-.170],[.090,0,.168]);collision_box('hood',[-.130,-.316,.041],[.130,-.095,.180])
 collision_hull('arm',[[x,y,z]for x in(-.025,.025)for y,z in[(-.033,-.02),(-.03,.026),(-.16,.089),(-.194,.089)]])
 VOIDS.append({'name':'space_below_projecting_shield','min_source_m':[-.11,-.31,-.14],'max_source_m':[.11,-.10,.02],'purpose':'Do not fill space below short arm/hood with a plate-to-mouth convex collider'})
 return 'Shielded wall reading sconce','Wall plane Y0; local centre Z0; front -Y',{'intended_use':'A local reading fitting with shaped shield, real rear mounting plane and visible switch. Wall support and illumination remain unverified.'}
def console():
 # Left open landing and taller right personal pod: deliberately unequal functions.
 for x,label in[(-.552,'left'),(.192,'divider'),(.554,'right')]:
  foot=box(label+'_floor_shoe',(x,.0,.012),(.076,.462,.024),'dark_rubber',.003)
  height=.445 if label=='left' else .818
  prof=[(-.226,.024),(.226,.024),(.212,.16),(.202,height),(-.189,height),(-.214,.16)]
  cheek=extrude(label+'_tapered_structural_cheek',prof,0,x-.029,x+.029,'warm_walnut',.004,2)
  marker(label.upper()+'_FLOOR_CONTACT',(x,0,0),'physical_floor_contact',foot.name,[0,0,-1])
  collision_box(label+'_upright',[x-.038,-.231,0],[x+.038,.231,height])
 for y in(-.182,.182):
  box('luggage_bearing_rail_'+str(y),(-.18,y,.278),(.79,.046,.050),'warm_walnut',.003,0)
 for i,y in enumerate((-.183,-.061,.061,.183)):
  sl=tray('luggage_support_slat_'+str(i),(-.18,y,.315),.786,.088,.028,'warm_walnut',.013)
  sl['grain_source_axis']=0
  # Assign lengthwise grain on the broad top face.
  uv=sl.data.uv_layers.active
  for f in sl.data.polygons:
   if abs(f.normal.z)>.5:
    for li in f.loop_indices:
     p=sl.data.vertices[sl.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/.65,p.x/1.3)
  pad=tray('slat_soft_contact_strip_'+str(i),(-.18,y,.332),.704,.047,.006,'dark_rubber',.010)
  marker('LUGGAGE_BEARING_'+str(i),(-.18,y,.335),'physical_luggage_support',pad.name,[0,0,1],'Open slat support plane; load rating unverified')
  collision_box('support_slat_'+str(i),[-.573,y-.044,.301],[.213,y+.044,.335])
 back=extrude('luggage_rear_guard',[(.202,.286),(.230,.286),(.230,.654),(.212,.694),(.202,.694)],0,-.566,.221,'warm_walnut',.003,0)
 box('rear_guard_ivory_inset',(-.182,.197,.564),(.683,.016,.185),'ivory_enamel',.003)
 # Three purposeful open-pod elements, with toe void and useful shelf mouth.
 shelf=tray('personal_open_shelf',(.373,.002,.486),.332,.394,.026,'warm_walnut',.018)
 box('personal_pod_rear',(.373,.212,.649),(.336,.026,.339),'warm_walnut',.003)
 top=tray('personal_tray_stone_surface',(.374,-.003,.828),.398,.478,.025,'warm_stone',.037)
 for x in(.197,.551):box('personal_tray_side_rim_'+str(x),(x,.032,.850),(.015,.408,.022),'champagne_metal',.002,1)
 box('personal_tray_back_rim',(.374,.236,.850),(.367,.016,.022),'champagne_metal',.002,0)
 # A inset catch dish is distinct from the large usable top, no moving drawer.
 tray('small_personal_catch_dish',(.383,.104,.846),.176,.141,.012,'ivory_enamel',.020)
 marker('PERSONAL_SURFACE',(.374,-.112,.8405),'physical_personal_support',top.name,[0,0,1])
 marker('PERSONAL_SHELF',(.373,-.045,.499),'physical_storage_support',shelf.name,[0,0,1])
 marker('LUGGAGE_RECEIVER',(-.18,-.012,.500),'nonphysical_receiver_volume',None,[0,-1,0],'Proposed open landing centre above slats; do not treat as contact')
 marker('PERSONAL_SHELF_MOUTH',(.373,-.197,.642),'nonphysical_receiver_volume',None,[0,-1,0],'Open compartment centre; species hand fit unverified')
 marker('CONSOLE_FLOOR_DATUM',(0,0,0),'placement_origin',None,[0,0,1])
 join('shelf_divider',shelf.name,'divider_tapered_structural_cheek',[.213,.0,.487])
 join('shelf_right',shelf.name,'right_tapered_structural_cheek',[.534,.0,.487])
 join('top_divider',top.name,'divider_tapered_structural_cheek',[.203,.0,.817])
 join('top_right',top.name,'right_tapered_structural_cheek',[.554,.0,.817])
 collision_box('rear_guard',[-.566,.195,.286],[.221,.230,.694]);collision_box('pod_rear',[.205,.199,.479],[.541,.225,.818])
 collision_box('pod_shelf',[.207,-.195,.473],[.539,.199,.499]);collision_box('pod_top',[.175,-.242,.8155],[.573,.244,.861])
 VOIDS.extend([{'name':'luggage_open_landing','min_source_m':[-.49,-.23,.350],'max_source_m':[.14,.170,.920],'purpose':'Uncovered luggage landing, accessible from the front; not a species-specific luggage guarantee'}, {'name':'personal_open_storage','min_source_m':[.235,-.230,.520],'max_source_m':[.510,.185,.790],'purpose':'Open front shelf, no drawer and no moving parts'}, {'name':'lower_luggage_open_space','min_source_m':[-.49,-.23,.050],'max_source_m':[.14,.15,.245],'purpose':'Preserve open lower apron and floor space'}])
 return 'Split-level luggage and personal console','Floor Z0, front -Y',{'intended_use':'Low open luggage slats, raised personal tray and open storage shelf, without a decorative or unnecessary drawer','luggage_support_plane_source_z_m':.335,'personal_surface_source_z_m':.8405,'open_personal_shelf_plane_source_z_m':.499}
def measure():
 dg=bpy.context.evaluated_depsgraph_get();points=[];tri=0
 for o in PARTS:
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);points.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in points)for i in range(3)];hi=[max(p[i]for p in points)for i in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri
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
   p=me.polygons[pi];normal=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3)if i!=normal];grain=int(src['grain_source_axis'])
   if src['material_role']=='warm_walnut'and grain in axes:axes=[i for i in axes if i!=grain]+[grain]
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/sx,co[axes[1]]/sy)
  o=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(o)
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=obs[0];o.name=ident+'__'+role;o.parent=ROOT;o['material_role']=role;o['semantic_parts']=json.dumps([s.name for s in PARTS if s['material_role']==role]);out.append(o)
 bpy.ops.object.select_all(action='DESELECT');ROOT.select_set(True)
 for o in out:o.select_set(True)
 for row in MARKERS:bpy.data.objects[row['name']].select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];coll={};api={}
 for ident,fn in [('AST-GST-001',floor_lamp),('AST-GST-002',sconce),('AST-GST-003',console)]:
  reset(ident);title,datum,details=fn();bpy.context.view_layer.update();bounds,tri=measure()
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(ident)
  rec={'catalogue_id':ident,'title':title,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_guest_use.py','source_frame':'metres Blender Z-up, +X right, -Y front','exchange_frame':'metres GLB Y-up, source(x,y,z) -> (x,z,-y); resolve actual native GLB node transforms','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':datum},'bounds_blender_z_up':bounds,'evaluated_source_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role']for o in PARTS)),'runtime_consolidation':'Static evaluated copies consolidated per distinct semantic material role; active UV normalized; native marker hierarchy retained','physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'interaction_status':'Static visible switches/receivers are proposals only; no animation, runtime light, engine collider or interaction','collision_proposal_file':'collision_proposals.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'limitations':['Separate catalogue, no original ship integration','No active electrical lighting or photometric validation','No load/stability/structural engineering rating','No species-fit or accessibility claim','No target engine/physics/performance validation']}
  rec.update(name=title,dimensions_blender_xyz_m=bounds['dimensions_m'],evaluated_triangles=tri,marker_api_file='marker_api.json')
  rows.append(rec);(BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');coll[ident]={'source_frame':'metres Blender Z-up','exchange_frame':'metres glTF Y-up; records explicitly converted','status':'Economical separate static collider proposals only; no active physics','shapes':COLL,'preserve_voids':VOIDS};api[ident]=MARKERS
 (BASE/'manifest.json').write_text(json.dumps({'family':'guest_use','revision':'guest-use-01','assets':rows},indent=2)+'\n')
 (BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n')
 print('BUILT',[(r['catalogue_id'],r['evaluated_source_triangles'],r['bounds_blender_z_up']['dimensions_m'])for r in rows])
if __name__=='__main__':main()
