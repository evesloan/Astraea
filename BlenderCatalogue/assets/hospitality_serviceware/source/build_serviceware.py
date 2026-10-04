"""Original script-assisted AST-HSP-005/006 service furnishings. Blender 4.3.2.
Editable named shaped parts and non-destructive edge modifiers. No game behavior.
Run: blender -b -t 2 --python-exit-code 1 --python source/build_serviceware.py
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
MATS={**module('guest',CAT/'standards/materials.py').materials(),**module('staff',CAT/'standards/staff_materials.py').materials()}
PARTS=[];GROUPS=[];MARKERS=[];JOINS=[];ROOT=None;ID=''
def mapped(p):return [p[0],p[2],-p[1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def group(name,loc=(0,0,0),parent=None,**props):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=loc;o.parent=parent;o.empty_display_size=.04
 for k,v in props.items():o[k]=v
 GROUPS.append(o);bpy.context.view_layer.update();return o

def uv_metric(me,role):
 uv=me.uv_layers.new(name='metric_material_uv') if not me.uv_layers else me.uv_layers.active;uv.name='metric_material_uv';scale=MATS[role]['meters_per_tile_uv']
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  if role=='warm_walnut':axes=([axes[0],2] if 2 in axes else [1,0])
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/scale[0],co[axes[1]]/scale[1])

def mesh(name,verts,faces,role,par=None,smooth=False,bevel=0):
 par=par or ROOT;bpy.context.view_layer.update();inv=par.matrix_world.inverted();verts=[inv@Vector(p) for p in verts]
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=par;me.materials.append(MATS[role]);o['material_role']=role;o['authoring']='Original script-assisted intentional shape';o['functional_group']=par.name
 for p in me.polygons:p.use_smooth=smooth
 uv_metric(me,role)
 if bevel:
  mod=o.modifiers.new('Editable small eased construction edges','BEVEL');mod.width=bevel;mod.segments=2
  mod=o.modifiers.new('Weighted hard-surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 PARTS.append(o);return o

def rect(w,d,r,n=6):
 out=[]
 for cx,cy,start in[(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for j in range(n+1):
   a=math.radians(start+j*90/n);out.append((cx+r*math.cos(a),cy+r*math.sin(a)))
 return out

def loft(name,rings,role,par=None,smooth=False,caps=True):
 n=len(rings[0]);v=[p for r in rings for p in r];f=[]
 for i in range(len(rings)-1):
  for j in range(n):f.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 if caps:f.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))])
 return mesh(name,v,f,role,par,smooth)

def slab(name,w,d,z0,z1,role,xy=(0,0),r=.04,par=None):
 edge=min(.004,(z1-z0)/3);rings=[]
 for z,sh in[(z0,.003),(z0+edge,0),(z1-edge,0),(z1,.003)]:rings.append([(x+xy[0],y+xy[1],z) for x,y in rect(w-2*sh,d-2*sh,max(.006,r-sh))])
 return loft(name,rings,role,par)

def prism(name,poly,axis,a,b,role,par=None,bevel=0):
 others=[k for k in range(3) if k!=axis];v=[]
 for q in[a,b]:
  for p in poly:
   co=[0,0,0];co[axis]=q;co[others[0]]=p[0];co[others[1]]=p[1];v.append(co)
 n=len(poly);f=[tuple(reversed(range(n))),tuple(n+j for j in range(n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 return mesh(name,v,f,role,par,False,bevel)

def tube(name,pts,r,role,par=None,sides=10):
 pts=list(map(Vector,pts));v=[];previous_t=None;previous_u=None
 for i,p in enumerate(pts):
  t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
  if previous_t is None:
   seed=Vector((0,0,1)) if abs(t.z)<.95 else Vector((1,0,0));u=t.cross(seed).normalized()
  else:u=(previous_t.rotation_difference(t)@previous_u).normalized()
  q=t.cross(u);previous_t=t;previous_u=u
  v.extend(p+r*(u*math.cos(2*math.pi*j/sides)+q*math.sin(2*math.pi*j/sides)) for j in range(sides))
 f=[]
 for i in range(len(pts)-1):
  for j in range(sides):f.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 f.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+j for j in range(sides))]);o=mesh(name,v,f,role,par,True)
 for p in o.data.polygons[-2:]:p.use_smooth=False
 return o

def lathe(name,profile,center,role,axis='Z',par=None,n=32):
 # Profile includes nonzero radial inner/outer closed cross-section; exact centre disks use separate caps.
 v=[]
 for r,h in profile:
  for j in range(n):
   a=2*math.pi*j/n;co=(r*math.cos(a),r*math.sin(a),h) if axis=='Z' else(h,r*math.cos(a),r*math.sin(a));v.append(Vector(center)+Vector(co))
 f=[]
 for i in range(len(profile)-1):
  for j in range(n):f.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 f.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+j for j in range(n))]);return mesh(name,v,f,role,par,True)

def marker(name,p,normal=None,kind='physical contact',**props):
 o=group(name,p,ROOT,coordinate_frame='Blender Z-up metres',point_blender=list(p),point_gltf_yup=mapped(p),kind=kind,**props)
 if normal:o['normal_blender']=normal;o['normal_gltf_yup']=mapped(normal)
 MARKERS.append({'node':name,'position_blender_m':list(p),'position_gltf_yup_m':mapped(p),'kind':kind,**props});return o

def tray(name,center,z,par):
 # Closed pressed tray with actual shallow well, flared rim and integrated lip. Envelope .45 x .32 m.
 rings=[]
 for w,d,r,h in[(.430,.300,.036,0),(.450,.320,.043,.015),(.450,.320,.043,.021),(.428,.298,.033,.021),(.403,.273,.023,.004)]:rings.append([(x+center[0],y+center[1],z+h) for x,y in rect(w,d,r)])
 return loft(name,rings,'staff_zinc',par)

def plate(name,x,y,z,par):
 # Closed coupe plate; flat contact foot, concave serving centre, raised lip.
 return lathe(name,[(.080,0),(.090,.004),(.139,.020),(.143,.025),(.141,.030),(.133,.030),(.096,.012),(.035,.010)],(x,y,z),'ivory_enamel','Z',par)

def storage():
 global ROOT,ID
 ID='AST-HSP-005';ROOT=group(ID,datum='floor origin at centre',guest_front_blender=[0,-1,0],guest_front_gltf_yup=[0,0,1]);static=group('005_fixed_carcass',(0,0,0),ROOT)
 slab('005_rounded_warm_stone_worktop',1.10,.78,.852,.900,'warm_stone',r=.080,par=static)
 slab('005_lower_ivory_continuous_plinth',1.055,.710,.128,.181,'ivory_enamel',r=.085,par=static)
 # Deliberate side cheek outline: toe setback, raked upper edge and rounded guest return.
 profile=[(-.310,.177),(-.349,.207),(-.351,.750),(-.335,.822),(-.297,.852),(.318,.852),(.346,.827),(.346,.200),(.310,.177)]
 for x,side in[(-.527,'left'),(.483,'right')]:prism('005_'+side+'_shaped_ivory_end_cheek',profile,0,x,x+.044,'ivory_enamel',static,.007)
 # Bowed and raked warm timber front with real return depth; 17 broad flutes, not luminous decoration.
 n=24;xs=[-.487+.974*i/n for i in range(n+1)];rings=[]
 for z,shift in[(.180,.012),(.230,0),(.790,0),(.838,.012)]:
  outer=[(x,-.337-.022*(1-(x/.487)**2)+shift,z) for x in xs];inner=[(x,y+.022,z) for x,y,_ in reversed(outer)];rings.append(outer+inner)
 loft('005_bowed_walnut_guest_fascia',rings,'warm_walnut',static)
 for i in range(17):
  x=-.449+i*.0561;y=-.337-.022*(1-(x/.487)**2)-.005
  # Rounded slender ribs are broad enough to read as joinery, taper at top and foot.
  tube('005_guest_walnut_flute_%02d'%i,[(x,y+.009,.225),(x,y,.260),(x,y,.765),(x,y+.009,.807)],.009,'warm_walnut',static,8)
 tube('005_champagne_upper_reveal',[(x,-.337-.022*(1-(x/.487)**2)-.002,.825) for x in xs],.005,'champagne_metal',static,8)
 # Inside panels and reachable rear-open divided storage; all staff metal scoped to stock surfaces.
 prism('005_central_structural_divider',[(-.309,.180),(.345,.180),(.345,.840),(-.309,.840)],0,.040,.064,'ivory_enamel',static,.004)
 shelflevels=[.245,.473,.701]
 for i,z in enumerate(shelflevels):slab('005_tray_shelf_%d'%i,.501,.620,z-.020,z,'staff_zinc',xy=(-.222,.016),r=.015,par=static)
 for i,z in enumerate([.245,.535]):slab('005_plate_shelf_%d'%i,.402,.620,z-.020,z,'staff_zinc',xy=(.274,.016),r=.015,par=static)
 # Folded cleats bear every shelf onto the side cheeks and central divider.
 for kind,zs,pairs in[('tray',shelflevels,[(-.490,-.456),(.020,.048)]),('plate',[.245,.535],[(.056,.086),(.460,.491)])]:
  for i,z in enumerate(zs):
   for k,(a,b) in enumerate(pairs):
    poly=[(a,z-.048),(a+.004,z-.048),(a+.004,z-.030),(b,z-.030),(b,z-.020),(a,z-.020)] if k==0 else [(a,z-.030),(b-.004,z-.030),(b-.004,z-.048),(b,z-.048),(b,z-.020),(a,z-.020)]
    prism('005_'+kind+'_shelf_'+str(i)+'_folded_cleat_'+str(k),poly,1,-.285,.306,'staff_zinc',static)
 for side,x in[('left',-.441),('right',.441)]:
  for end,y in[('front',-.257),('rear',.257)]:
   lathe('005_'+side+'_'+end+'_leveling_foot',[(.044,0),(.047,.008),(.039,.018),(.033,.091),(.040,.128)],(x,y,0),'dark_rubber',par=static,n=16)
   marker('005_'+side+'_'+end+'_floor_contact',(x,y,0),[0,0,1],foot_mesh='005_'+side+'_'+end+'_leveling_foot')
 stocks=[]
 for i,z in enumerate(shelflevels):
  g=group('005_tray_stock_%d'%i,(-.222,.064,z),ROOT,stock_derivative=True,removable=True,nominal_envelope_m=[.45,.32,.021])
  for k in range(2):tray('005_tray_stock_%d_piece_%d'%(i,k),(-.222,.064),z+k*.021,g)
  marker('005_tray_support_%d'%i,(-.222,.064,z),[0,0,1],support_mesh='005_tray_shelf_%d'%i)
  stocks.append({'node':g.name,'support_z_m':z,'piece_count':2,'tray_envelope_m':[.45,.32,.021],'withdrawal_axis_blender':[0,1,0],'withdrawal_axis_gltf_yup':[0,0,-1],'proposed_translation_m':.72,'clear_opening_width_m':.501,'clear_above_shelf_m':shelflevels[i+1]-z-.020 if i<2 else .852-z})
 for i,z in enumerate([.245,.535]):
  g=group('005_plate_stock_%d'%i,(.274,.092,z),ROOT,stock_derivative=True,removable=True)
  for k in range(4):plate('005_plate_stock_%d_piece_%d'%(i,k),.274,.092,z+k*(.010+(.080-.035)*(.002/(.096-.035))),g)
  marker('005_plate_support_%d'%i,(.274,.092,z),[0,0,1],support_mesh='005_plate_shelf_%d'%i)
  stocks.append({'node':g.name,'support_z_m':z,'piece_count':4,'plate_diameter_m':.286,'stack_height_m':.030+3*(.010+(.080-.035)*(.002/(.096-.035))),'open_approach_blender':[0,1,0]})
 marker('005_top_work_contact',(0,.050,.900),[0,0,1],support_mesh='005_rounded_warm_stone_worktop')
 return {'title':'Aster plate and tray service credenza','stock_groups':stocks,'approach':{'staff_rear_positive_y':True,'proposed_clear_zone_source_m':{'min':[-.60,.39,0],'max':[.60,1.24,1.80]},'guest_front_finish':'Bowed walnut ribs with shaped ivory cheeks and warm-stone worktop'},'collision':{'frame':'Blender Z-up metres','strategy':'Use separate side cheek, guest fascia, divider, worktop, each shelf and four feet; do not use a full cabinet convex hull','openings':'Rear stock compartments and staff approach stay open','stock':'Tray/plate derivative groups are optional static context; removable proxy dynamics remain unimplemented'}}

def trolley():
 global ROOT,ID
 ID='AST-HSP-006';ROOT=group(ID,datum='floor origin at centre',guest_front_blender=[0,-1,0],guest_front_gltf_yup=[0,0,1]);static=group('006_fixed_chassis',(0,0,0),ROOT)
 for tier,z in[('lower',.225),('upper',.785)]:
  slab('006_'+tier+'_ivory_formed_tier',.680,.540,z-.038,z,'ivory_enamel',r=.090,par=static)
  # Walnut apron deliberately follows continuous round outline.
  rings=[[(x,y,zz) for x,y in rect(w,d,r)] for w,d,r,zz in[(.665,.525,.084,z-.041),(.665,.525,.084,z-.021),(.643,.503,.073,z-.021),(.643,.503,.073,z-.041)]]
  loft('006_'+tier+'_walnut_perimeter_apron',rings,'warm_walnut',static,caps=False)
  slab('006_'+tier+'_washable_inset',.577,.437,z,z+.006,'staff_zinc',r=.048,par=static)
  # Low lips on guest front and side edges, open rear grip approach.
  pts=[(-.297,.150,z+.032),(-.302,-.140,z+.032),(-.280,-.192,z+.032),(-.235,-.215,z+.032),(.235,-.215,z+.032),(.280,-.192,z+.032),(.302,-.140,z+.032),(.297,.150,z+.032)]
  tube('006_'+tier+'_three_sided_retention_rail',pts,.008,'champagne_metal',static,8)
  marker('006_'+tier+'_tray_support',(0,0,z+.006),[0,0,1],support_mesh='006_'+tier+'_washable_inset')
 # Load path: four struts reach chassis above caster bearing and both tier undersides.
 for x,side in[(-.272,'left'),(.272,'right')]:
  for y,end in[(-.184,'front'),(.184,'rear')]:
   tube('006_'+side+'_'+end+'_continuous_support',[(x,y,.128),(x,y,.220),(x,y,.745),(x*.96,y*.94,.780)],.016,'champagne_metal',static,10)
  # Arc supporting the rear grip, swept rather than detached handle box.
  tube('006_'+side+'_swept_push_stanchion',[(x,.184,.737),(x,.190,.824),(x*.97,.240,.889),(x*.92,.302,.923),(x*.90,.355,.925)],.016,'champagne_metal',static,10)
 grip=tube('006_rear_dark_push_grip',[(-.2448,.355,.925),(.2448,.355,.925)],.019,'dark_rubber',static,12)
 marker('006_push_grip_contact',(0,.355,.944),[0,0,1],handle_center_source=[0,.355,.925],handle_axis_source=[1,0,0],handle_axis_gltf=[1,0,0],diameter_m=.038,free_palm_span_m=.40)
 # Explicit real hierarchy for proposed wheels; swivel +Z, axle +X. No controller/rolling implementation.
 wheelrecords=[]
 for x,side in[(-.267,'left'),(.267,'right')]:
  for y,end in[(-.179,'front'),(.179,'rear')]:
   tag=side+'_'+end;sw=group('006_'+tag+'_swivel',(x,y,.126),ROOT,axis_blender=[0,0,1],axis_gltf_yup=[0,1,0],pivot_blender=[x,y,.126],pivot_gltf_yup=mapped((x,y,.126)),proposed_motion='swivel rotation only; no solver');ax=group('006_'+tag+'_axle',(0,-.020,-.071),sw,axis_blender=[1,0,0],axis_gltf_yup=[1,0,0],proposed_motion='wheel rotation only; no rolling implementation')
   # fork arm pair leaves air around central wheel and uses deliberate bent side profile.
   poly=[(y-.061,.054),(y-.058,.096),(y-.026,.127),(y+.022,.127),(y+.025,.109),(y-.018,.088),(y-.012,.052)]
   for sign in[-1,1]:prism('006_'+tag+'_fork_'+str(sign),poly,0,x+sign*.030-.005,x+sign*.030+.005,'staff_zinc',sw,.002)
   lathe('006_'+tag+'_swivel_bearing',[(.027,0),(.029,.006),(.026,.016)],(x,y,.120),'staff_zinc',par=sw,n=16)
   center=(x,y-.020,.055)
   lathe('006_'+tag+'_rubber_wheel',[(.020,-.019),(.047,-.019),(.055,-.012),(.055,.012),(.047,.019),(.020,.019)],center,'dark_rubber','X',ax,n=24)
   lathe('006_'+tag+'_wheel_hub',[(.008,-.024),(.022,-.023),(.022,.023),(.008,.024)],center,'champagne_metal','X',ax,n=16)
   marker('006_'+tag+'_floor_contact',(x,y-.020,0),[0,0,1],wheel_mesh='006_'+tag+'_rubber_wheel')
   wheelrecords.append({'tag':tag,'swivel_node':sw.name,'axle_node':ax.name,'swivel_pivot_blender_m':[x,y,.126],'swivel_pivot_gltf_yup_m':mapped((x,y,.126)),'wheel_center_blender_m':list(center),'wheel_center_gltf_yup_m':mapped(center),'swivel_axis_blender':[0,0,1],'swivel_axis_gltf_yup':[0,1,0],'axle_axis_blender':[1,0,0],'axle_axis_gltf_yup':[1,0,0],'wheel_radius_m':.055,'geometry_floor_contact_m':[x,y-.020,0]})
 # One proposed tray on lower tier emphasizes clear use without hiding top inset.
 stock=group('006_context_lower_tray',(0,0,.231),ROOT,stock_derivative=True,removable=True);tray('006_context_lower_tray_piece',(0,0),.231,stock)
 return {'title':'Aster two-tier dining service trolley','wheels':wheelrecords,'stock_groups':[{'node':stock.name,'support_z_m':.231,'piece_count':1,'envelope_m':[.45,.32,.021],'status':'Contextual tray derivative, not an extra design'}],'upper_support_z_m':.791,'lower_support_z_m':.231,'clear_height_above_lower_inset_m':.516,'approach':{'staff_rear_positive_y':True,'push_direction_source':[0,-1,0],'proposed_clear_zone_source_m':{'min':[-.50,.390,0],'max':[.50,1.15,1.80]}},'collision':{'frame':'Blender Z-up metres','strategy':'Split shallow tier shells, narrow support/grip capsules, wheel cylinders and fork shapes. Preserve tier access and space under grip. No whole trolley convex box.','sweep':'Four swivel assemblies proposed full-turn swept radius0.091 m each about named pivots, validated separately; excludes cargo/controller/rolling','status':'Geometry/contact proposal only; not the original player cart'}}

def measured_bounds():
 dg=bpy.context.evaluated_depsgraph_get();pts=[];tri=0
 for o in PARTS:
  e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);pts.extend(o.matrix_world@v.co for v in me.vertices);e.to_mesh_clear()
 lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(path):
 dg=bpy.context.evaluated_depsgraph_get();copies={};out=[]
 for src in GROUPS:
  o=bpy.data.objects.new('EXPORT_'+src.name,None);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy()
  for k in src.keys():o[k]=src[k]
  copies[src.name]=o;out.append(o)
 for src in GROUPS:
  if src.parent:
   o=copies[src.name];world=o.matrix_world.copy();o.parent=copies[src.parent.name];o.matrix_world=world
 grouped={}
 for src in PARTS:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=active:me.uv_layers.remove(layer)
  active.name='metric_material_uv';active.active_render=True
  # Reproject evaluated geometry per face to preserve noncollapsed metric UV after bevels.
  uv_metric(me,src['material_role'])
  o=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(o);o.matrix_world=src.matrix_world.copy();grouped.setdefault((src.parent.name,src['material_role']),[]).append(o)
 for (parent,role),obs in grouped.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=obs[0];o.name='EXPORT_'+parent+'__'+role;world=o.matrix_world.copy();o.parent=copies[parent];o.matrix_world=world;o['functional_group']=parent;o['material_role']=role;o['source_parts']=json.dumps([s.name for s in PARTS if s.parent.name==parent and s['material_role']==role]);out.append(o)
 # Keep runtime names matching documented markers/hierarchy; source objects temporarily renamed.
 old=[]
 for src in list(GROUPS)+list(PARTS):old.append((src,src.name));src.name='SOURCE_HIDDEN_'+src.name
 for o in out:o.name=o.name.removeprefix('EXPORT_')
 bpy.ops.object.select_all(action='DESELECT')
 for o in out:o.select_set(True)
 bpy.context.view_layer.objects.active=out[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
 for src,name in old:src.name=name

def main():
 global PARTS,GROUPS,MARKERS,JOINS
 manifests=[]
 for build in[storage,trolley]:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);PARTS=[];GROUPS=[];MARKERS=[];JOINS=[];scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
  design=build();bpy.context.view_layer.update();bounds,tri=measured_bounds();scene['catalogue_id']=ID;scene['authoring']='Original script-assisted editable Blender shapes';scene['not_game']=True
  source=BASE/'source'/f'{ID}.blend';glb=BASE/'exports'/f'{ID}.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));export(glb)
  m={'catalogue_id':ID,'unique_design':True,**design,'name':design['title'],'dimensions_blender_xyz_m':bounds['dimensions_m'],'evaluated_triangles':tri,'source':str(source.relative_to(BASE)),'export':str(glb.relative_to(BASE)),'generator':'source/build_serviceware.py','units':'metres','coordinates':{'source':'Blender Z-up; guest −Y; staff +Y','exchange':'GLB Y-up; guest +Z; staff −Z','mapping':'(x,y,z) → (x,z,−y)','datum':'Floor origin at design XY centre'},'bounds_blender_z_up':bounds,'editable_semantic_parts':len(PARTS),'source_evaluated_triangle_count':tri,'material_roles':sorted(set(o['material_role']for o in PARTS)),'semantic_parts':[o.name for o in PARTS],'native_marker_records':MARKERS,'export_consolidation':'Evaluated static geometry by semantic material within functional group. Stock/castor groups preserved, active metric UV normalized. Markers exported as actual named hierarchy nodes.','material_intent':'Shared frozen guest ivory/walnut/stone/champagne/rubber. Neutral staff_zinc only on stock trays, inner shelf liners, forks and bearings.','provenance':'Original new script-assisted shaped service furnishings, guided by actual reference images; no external kit or recovered-game source.','references':['../../references/hospitality/public_reference.png','../../references/hospitality/vibe_dining_edge.jpg'],'limitations':['No room/game/controller/cargo/rolling implementation','No species reach, load-bearing, food-service, accessibility or physical certification','Component QA and conservative geometric proposals only'],'source_sha256':sha(source),'glb_sha256':sha(glb),'generator_sha256':sha(Path(__file__))}
  (BASE/f'{ID}.manifest.json').write_text(json.dumps(m,indent=2)+'\n');manifests.append(m);print('BUILT',ID,len(PARTS),tri,bounds)
 (BASE/'manifest.json').write_text(json.dumps({'batch':'batch07','asset_count':2,'assets':manifests},indent=2)+'\n')
 module('collision_shapes',BASE/'source/collision_shapes.py').build()
if __name__=='__main__':main()
