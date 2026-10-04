"""Original Batch16 cultural arrival designs. Deterministic Blender 4.3.2 generator.
Run blender --background --threads 2 --python-exit-code 1 --python source/build_auditorium_arrival.py
Source-only inputs: this file, auditorium/common helpers and all loaded role textures/manifests,
and local original programme/usher PNG sources. QA and prior outputs are never read.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,importlib.util
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
for p in ('source','exports'):(BASE/p).mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('auditorium_materials',CAT/'standards/auditorium_materials.py');mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm);MATS=mm.materials()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):return [p[0],p[2],-p[1]]
def art(role,file,size):
 m=bpy.data.materials.new('ASTRAEA_'+role);m.use_nodes=True;m['astraea_material_role']=role;m['meters_per_tile_uv']=size
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.84
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(BASE/'textures'/file));t.image.pack();t.extension='EXTEND';t.interpolation='Linear';m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);MATS[role]=m
art('programme_original','programme_original.png',[.70,1.18]);art('usher_original','usher_original.png',[.56,.187])
def reset(ident):
 global ROOT,PARTS,MARKERS,JOINS,COLL,VOIDS,MOVES,MOVEROOTS
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 PARTS=[];MARKERS=[];JOINS=[];COLL=[];VOIDS=[];MOVES=[];MOVEROOTS=[]
 ROOT=bpy.data.objects.new(ident,None);bpy.context.collection.objects.link(ROOT);ROOT['catalogue_id']=ident
 ROOT['scope']='Original unplaced D11 cultural component; no added capacity or room; host absent'
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 bpy.context.scene['catalogue_id']=ident

def mesh(name,vs,fs,role='warm_walnut',parent=None,grain=2):
 me=bpy.data.meshes.new(name+'_editable');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=parent or ROOT;me.materials.append(MATS[role]);ob['material_role']=role;ob['grain_axis']=grain
 uv=me.uv_layers.new(name='metric_material_uv');uv.active_render=True;sx,sy=MATS[role]['meters_per_tile_uv']
 for f in me.polygons:
  norm=max(range(3),key=lambda a:abs(f.normal[a]));axes=[a for a in range(3)if a!=norm]
  if role=='warm_walnut'and grain in axes:axes=[a for a in axes if a!=grain]+[grain]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/sx,p[axes[1]]/sy)
 PARTS.append(ob);return ob

def box(name,lo,hi,role='warm_walnut',parent=None,coll=True):
 vs=[(x,y,z)for x,y,z in [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),(lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]]
 ob=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,parent)
 if coll:COLL.append({'name':name,'type':'box','min_source_m':lo,'max_source_m':hi,'owner':(parent or ROOT).name,'maximum_outward_inflation_m':0,'omission_m':0})
 return ob

def prism(name,profile,axis,a,b,role='warm_walnut',parent=None,coll=True):
 axes=[i for i in range(3)if i!=axis];vs=[]
 for v in (a,b):
  for p in profile:
   q=[0,0,0];q[axis]=v;q[axes[0]]=p[0];q[axes[1]]=p[1];vs.append(q)
 n=len(profile);ob=mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,parent)
 if coll:COLL.append({'name':name,'type':'convex_hull_points','points_source_m':vs,'owner':(parent or ROOT).name,'maximum_outward_inflation_m':0,'omission_m':0})
 return ob

def rounded(w,d,r,c=(0,0)):
 ps=[]
 for x,y,t in[(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
  for j in range(4):a=math.radians(t+j*30);ps.append((c[0]+x+r*math.cos(a),c[1]+y+r*math.sin(a)))
 return ps

def rod(name,a,b,r,role='champagne_metal',parent=None):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();v=d.cross(Vector((1,0,0))if abs(d.x)<.9 else Vector((0,1,0))).normalized();u=d.cross(v);n=8
 vs=[list(p+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)))for p in (a,b)for i in range(n)]
 o=mesh(name,vs,[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role,parent)
 COLL.append({'name':name,'type':'convex_hull_points','points_source_m':vs,'owner':(parent or ROOT).name,'maximum_outward_inflation_m':0,'omission_m':0});return o

def marker(name,p,kind,part=None,normal=None,parent=None,note=''):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent or ROOT;o.location=p;o.empty_display_size=.02;o['marker_kind']=kind;o['physical_part']=part or '';o['frame']='source Z-up metres; native GLB node hierarchy authoritative'
 row={'name':name,'kind':kind,'source_m':p,'gltf_m':glb(p),'physical_part':part,'owner':o.parent.name,'description':note}
 if normal:row.update(direction_source=normal,direction_gltf=glb(normal));o['direction_source']=normal;o['direction_gltf']=glb(normal)
 MARKERS.append(row);return o

def join(name,a,b,p,na=None,nb=None):
 JOINS.append({'name':name,'parts':[a,b],'probe_source_m':p,'probe_gltf_m':glb(p),'normal_a_source':na,'normal_b_source':nb,'method':'Actual evaluated boundary or shared buried bearing probe; finite source/native witness check'})
def void(name,lo,hi,note,pose='closed'):
 VOIDS.append({'name':name,'min_source_m':lo,'max_source_m':hi,'pose':pose,'purpose':note})
def moving(name,travel,note):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=ROOT;o['translation_axis_source']=[0,1,0];o['translation_axis_gltf']=[0,0,-1];o['closed_translation_m']=0.;o['access_translation_m']=travel;o['scope']=note;MOVEROOTS.append(o)
 MOVES.append({'root':name,'type':'translation','axis_source':[0,1,0],'axis_gltf':[0,0,-1],'closed_m':0,'access_m':travel,'motion_includes_handle_and_all_owned_parts':True,'claim':note});return o

def map_art(ob,lo,hi,front=-1):
 uv=ob.data.uv_layers.active
 for f in ob.data.polygons:
  if f.normal.y*front>.99:
   for li in f.loop_indices:
    p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x-lo[0])/(hi[0]-lo[0]),(p.z-lo[2])/(hi[2]-lo[2]))

def display():
 base=prism('stone_elliptic_floor_plinth',rounded(1.20,.64,.14),2,0,.085,'warm_stone')
 marker('FLOOR_CONTACT',[0,0,0],'physical_floor_contact',base.name,[0,0,-1])
 # Two gently swept timber uprights; thick surfaces return around the display and rear cassette.
 left=[(-.40,.085),(-.40,.71),(-.405,1.50),(-.42,1.98),(-.47,2.23),(-.54,2.30),(-.59,2.28),(-.59,.085)]
 L=prism('swept_tall_walnut_left_stile',left,1,-.12,.14,coll=False)
 # Piecewise quadrilateral structural collision following the actual thin sweep, no all-wing hull.
 from mathutils.geometry import tessellate_polygon
 for i,tri in enumerate(tessellate_polygon([[Vector((x,z,0))for x,z in left]])):
  ps=[[left[v][0],y,left[v][1]]for y in(-.12,.14)for v in tri]
  COLL.append({'name':'left_stile_section_'+str(i),'type':'convex_hull_points','points_source_m':ps,'owner':ROOT.name,'covered_parts':[L.name],'maximum_outward_inflation_m':0,'omission_m':0,'note':'Exact triangle-prism decomposition of the concave structural stile, preserving its authored inner profile'})
 R=prism('short_tapered_right_stile',[(.40,.085),(.54,.085),(.53,.75),(.51,1.82),(.47,2.08),(.40,2.11)],1,-.12,.14)
 lower=prism('lower_sculpted_cross_web',[(-.40,.085),(.40,.085),(.40,.70),(-.40,.70)],1,-.09,.13)
 cap=prism('sloping_crown_lintel',[(-.54,2.20),(.46,2.025),(.47,2.08),(-.54,2.30)],1,-.113,.133)
 for ob,x,z in[(L,-.48,.085),(R,.46,.085),(lower,0,.085)]:join(ob.name+'_to_plinth',ob.name,base.name,[x,0,z],[0,0,-1],[0,0,1])
 join('left_crown_bearing',cap.name,L.name,[-.53,0,2.23]);join('right_crown_bearing',cap.name,R.name,[.435,0,2.07])
 shelf=box('cassette_lower_bearing',[-.40,-.12,.70],[.40,.14,.745])
 substrate=box('programme_front_rigid_backing',[-.40,-.12,.745],[.40,-.065,2.025],'warm_walnut')
 artob=box('replaceable_original_programme_face',[-.35,-.125,.785],[.35,-.12,1.965],'programme_original')
 map_art(artob,[-.35,0,.785],[.35,0,1.965]);join('graphic_to_rigid_backing',artob.name,substrate.name,[0,-.12,1.3],[0,1,0],[0,-1,0])
 marker('PROGRAMME_FACE',[0,-.125,1.4],'physical_programme_surface',artob.name,[0,-1,0],note='Original programme study; no current performance or showtime asserted')
 # Navy removable rear cassette is genuinely open behind the front poster; amber lower insert is fixed.
 mov=moving('REAR_SERVICE_PANEL',.32,'Geometric removal along +Y from true closed state; tool release/hand support and installed service reach pending')
 panel=box('rear_navy_absorptive_cassette',[-.385,.093,.765],[.385,.119,2.005],'auditorium_navy_fibre',mov)
 for x in(-.38,.38):
  ob=box('cassette_rear_edge_'+str(x),[x-.01,.119,.765],[x+.01,.137,2.005],'warm_walnut',mov);join('cassette_edge_support_'+str(x),ob.name,panel.name,[x,.119,1.4],[0,-1,0],[0,1,0])
 # Real closed retaining ledges and panel seat. They stop short of the removal path.
 for x in(-.39,.39):
  ledge=box('fixed_panel_seat_'+str(x),[x-.03,.063,.765],[x+.03,.093,2.005],'champagne_metal')
  join('rear_cassette_closed_bearing_'+str(x),panel.name,ledge.name,[x+(.015 if x<0 else -.015),.093,1.4],[0,-1,0],[0,1,0])
 for x in(-.09,.09):
  h=rod('rear_handle_boss_'+str(x),[x,.119,1.39],[x,.173,1.39],.012,parent=mov);join('handle_boss_to_panel_'+str(x),h.name,panel.name,[x,.119,1.39],[0,-1,0],[0,1,0])
 handle=box('rear_cassette_pull',[-.09,.161,1.378],[.09,.185,1.402],'champagne_metal',mov)
 marker('PANEL_PULL',[0,.185,1.39],'physical_grip',handle.name,[0,1,0],mov)
 marker('REAR_ABSORPTIVE_FACE',[.20,.119,1.5],'physical_material_surface',panel.name,[0,1,0],mov,note='Navy fibre proposal; acoustic effect is unmeasured')
 amber=box('lower_amber_return_insert',[-.30,.13,.23],[.30,.15,.61],'auditorium_amber_velvet')
 join('amber_backing_contact',amber.name,lower.name,[0,.13,.4],[0,-1,0],[0,1,0])
 for z in(.21,.615):box('lower_insert_walnut_rail_'+str(z),[-.32,.13,z],[.32,.163,z+.015])
 marker('REAR_SERVICE_APPROACH',[0,.76,1.36],'nonphysical_service_reservation',None,[0,-1,0])
 void('closed_programme_cassette_air',[-.36,-.055,.78],[.36,.060,1.98],'Useful access cavity behind replaceable front graphic, bounded away from support')
 void('rear_panel_hand_gap',[-.065,.14,1.374],[.065,.155,1.405],'Clear pocket below real pull bar; not a hand-fit certificate')
 void('rear_service_reach',[-.37,.53,.77],[.37,.82,1.99],'External handling proposal, not a room allocation','access')
 marker('FLOOR_ORIGIN',[0,0,0],'placement_origin')
 return 'Acoustic programme wing and removable cultural cassette',{'programme':'A Thousand Small Worlds','programme_state':'Historically original title used in original static programme study','acoustic_status':'Absorptive material/design intent only','front':'source -Y','service_side':'source +Y','envelope_is_component_only':True}

def station():
 # Swept public front and two work heights; actual open staff face is +Y.
 footprint=rounded(1.43,.65,.12,(0,-.045));base=prism('recessed_stone_counter_plinth',footprint,2,0,.105,'warm_stone')
 marker('FLOOR_CONTACT',[0,0,0],'physical_floor_contact',base.name,[0,0,-1])
 xs=[-.665,-.55,-.35,-.19,.05,.29,.51,.665]
 ys=[-.25,-.30,-.35,-.367,-.37,-.35,-.30,-.25]
 fronts=[]
 for i in range(len(xs)-1):
  x0,x1=xs[i:i+2];y0,y1=ys[i:i+2];zt=.76 if x1<=-.19 else 1.015
  ob=prism('curved_public_shell_segment_'+str(i),[(x0,y0),(x1,y1),(x1,y1+.043),(x0,y0+.043)],2,.105,zt,'warm_walnut');fronts.append(ob)
  join('front_shell_to_floor_'+str(i),ob.name,base.name,[(x0+x1)/2,(y0+y1)/2+.025,.105],[0,0,-1],[0,0,1])
 # Lower writing wing supported at left by a sculpted cheek and on the central cabinet divider.
 left=prism('low_wing_left_cheek',[(-.25,.105),(.26,.105),(.26,.68),(.18,.765),(-.25,.765)],0,-.71,-.665)
 mid=box('counter_central_divider',[-.235,-.325,.105],[-.19,.28,1.015])
 right=prism('right_full_height_cheek',[(-.25,.105),(.28,.105),(.28,.93),(.20,1.015),(-.25,1.015)],0,.665,.71)
 for ob,x in[(left,-.69),(mid,-.21),(right,.685)]:join(ob.name+'_plinth',ob.name,base.name,[x,0,.105],[0,0,-1],[0,0,1])
 low=prism('low_rounded_writing_stone',rounded(.57,.74,.08,(-.47,-.03)),2,.765,.805,'warm_stone')
 high=prism('main_rounded_usher_counter',rounded(.97,.78,.10,(.27,-.015)),2,1.015,1.065,'warm_stone')
 join('lower_writing_to_cheek',low.name,left.name,[-.69,0,.765],[0,0,-1],[0,0,1]);join('upper_counter_to_right',high.name,right.name,[.685,0,1.015],[0,0,-1],[0,0,1]);join('upper_counter_to_divider',high.name,mid.name,[-.20,0,1.015],[0,0,-1],[0,0,1])
 marker('LOW_WRITING_SURFACE',[-.47,-.04,.805],'physical_work_surface',low.name,[0,0,1],note='Proposed lower writing/retrieval height; six-species reach pending')
 marker('USHER_WORK_SURFACE',[.27,0,1.065],'physical_work_surface',high.name,[0,0,1])
 shelf=prism('open_programme_cubby_floor',[(-.19,-.324),(.05,-.327),(.29,-.307),(.51,-.257),(.665,-.207),(.665,.28),(-.19,.28)],2,.235,.267,'warm_walnut')
 # The continuous walnut public shell is also the real cubby backing; no independent flat liner crosses its bow.
 top=box('drawer_separation_shelf',[-.19,-.29,.655],[.665,.28,.683],'warm_walnut')
 for ob,z in[(shelf,.25),(top,.67)]:
  join(ob.name+'_left_support',ob.name,mid.name,[-.19,0,z],[ -1,0,0],[1,0,0]);join(ob.name+'_right_support',ob.name,right.name,[.665,0,z],[1,0,0],[-1,0,0])
 marker('CUBBY_SUPPORT',[.23,0,.267],'physical_storage_surface',shelf.name,[0,0,1])
 # Drawer uses supported long runners. Whole pull, fascia, floor, sides and back share one moving root.
 mov=moving('USHER_DRAWER',.28,'Complete shallow drawer +Y translation; real runner bearing overlap 0.15 m at access pose; not an implemented mechanism')
 for x,n in[(-.165,'left'),(.64,'right')]:
  fixed=box(n+'_fixed_slide_bearing',[x-.025,-.19,.715],[x+.025,.24,.731],'champagne_metal')
  movingrail=box(n+'_drawer_slide',[x-.011,-.19,.731],[x+.011,.235,.744],'champagne_metal',mov)
  join(n+'_slide_closed_support',movingrail.name,fixed.name,[x,0,.731],[0,0,-1],[0,0,1])
 floor=box('drawer_tray_floor',[-.176,-.19,.744],[.651,.245,.761],'warm_walnut',mov)
 for x,n in[(-.176,'left'),(.629,'right')]:
  ob=box('drawer_'+n+'_wall',[x,-.19,.761],[x+.022,.245,.916],'warm_walnut',mov);join(n+'_tray_to_floor',ob.name,floor.name,[x+.011,0,.761],[0,0,-1],[0,0,1])
 ob=box('drawer_inner_back',[-.154,-.19,.761],[.629,-.17,.916],'warm_walnut',mov)
 face=box('drawer_walnut_fascia',[-.178,.245,.710],[.653,.274,.940],'warm_walnut',mov)
 join('fascia_floor_bearing',face.name,floor.name,[.24,.245,.75],[0,-1,0],[0,1,0])
 for x in(.145,.325):rod('drawer_pull_boss_'+str(x),[x,.274,.826],[x,.327,.826],.012,parent=mov)
 handle=box('drawer_brass_pull',[.145,.315,.814],[.325,.339,.838],'champagne_metal',mov)
 marker('DRAWER_PULL',[.235,.339,.826],'physical_grip',handle.name,[0,1,0],mov)
 marker('DRAWER_STOW_FLOOR',[.235,0,.761],'physical_storage_surface',floor.name,[0,0,1],mov)
 # Original usher mark on supported shallow plaque, above curved public shell in a legible planar island.
 plaque=box('usher_mark_timber_bearing',[-.04,-.392,.42],[.54,-.333,.64],'warm_walnut')
 artob=box('original_usher_mark',[-.03,-.397,.431],[.53,-.392,.618],'usher_original');map_art(artob,[-.03,0,.431],[.53,0,.618])
 join('usher_mark_backing',artob.name,plaque.name,[.25,-.392,.5],[0,1,0],[0,-1,0])
 marker('PUBLIC_USHER_MARK',[.25,-.397,.52],'physical_orientation_surface',artob.name,[0,-1,0])
 # Amber inset echoes the auditorium textile, mechanically backed by the low wing front.
 amber=box('low_public_amber_insert',[-.62,-.342,.31],[-.30,-.325,.65],'auditorium_amber_velvet')
 # Top and bottom carrier bridges reach the real curved timber shell at both ends.
 for z in(.30,.65):box('amber_insert_carrier_'+str(z),[-.64,-.347,z],[-.28,-.294,z+.017])
 void('staff_open_programme_cubby',[-.16,-.19,.285],[.63,.50,.635],'Whole actual open storage mouth, continues outside counter to staff side')
 void('drawer_closed_useful_tray',[-.13,-.15,.78],[.60,.22,.90],'Real open-top drawer stow, not a solid block')
 void('lower_wing_staff_knee_proposal',[-.64,-.19,.15],[-.27,.40,.735],'Open staff-side lower writing bay, finite furniture void only')
 void('drawer_access_tray',[-.13,.13,.78],[.60,.50,.90],'Translated useful storage well in access pose','access')
 void('staff_service_approach',[-.14,.63,.10],[.61,1.10,1.00],'External staff reach reservation, host placement pending','access')
 marker('STAFF_APPROACH',[.25,.82,.5],'nonphysical_service_reservation',None,[0,-1,0]);marker('PUBLIC_APPROACH',[.1,-.85,.5],'nonphysical_use_reservation',None,[0,1,0]);marker('FLOOR_ORIGIN',[0,0,0],'placement_origin')
 return 'Curved usher counter with lower writing wing and programme storage',{'front':'source -Y','staff_side':'source +Y','work_heights_m':[.805,1.065],'drawer_translation_m':.28,'runtime_ticketing':False,'six_species_fit':'pending','utility':'Original usher mark, lower writing edge, fixed programme cubby, shallow pull-out tray'}

def measure():
 dg=bpy.context.evaluated_depsgraph_get();vs=[];tris=0
 for ob in PARTS:
  ev=ob.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);vs.extend(ob.matrix_world@v.co for v in m.vertices);ev.to_mesh_clear()
 lo=[min(p[i]for p in vs)for i in range(3)];hi=[max(p[i]for p in vs)for i in range(3)];return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tris

def export(ident):
 groups={};out=[];dg=bpy.context.evaluated_depsgraph_get()
 for ob in PARTS:
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));o=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(o);o.matrix_world=ob.matrix_world.copy();groups.setdefault((ob.parent.name,ob['material_role']),[]).append(o)
 for (parent,role),obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=obs[0];o.name=ident+'__'+parent+'__'+role;world=o.matrix_world.copy();o.parent=bpy.data.objects[parent];o.matrix_world=world;o['material_role']=role;o['semantic_parts']=json.dumps([p.name for p in PARTS if p.parent.name==parent and p['material_role']==role]);out.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in [ROOT]+MOVEROOTS+out+[bpy.data.objects[m['name']]for m in MARKERS]:o.select_set(True)
 bpy.context.view_layer.objects.active=ROOT
 bpy.context.view_layer.update()
 bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in out:bpy.data.objects.remove(o,do_unlink=True)
 return len(groups)

def main():
 bpy.context.preferences.filepaths.save_version=0;rows=[];coll={};api={}
 for ident,fn in [('AST-CUL-001',display),('AST-CUL-002',station)]:
  reset(ident);name,details=fn();bpy.context.view_layer.update();bounds,tris=measure()
  for o in PARTS:o['original_authorship']='Original Batch16 authored cultural component; generic mesh/export methods follow catalogue conventions'
  for im in bpy.data.images:
   if im.source=='FILE'and not im.packed_file:im.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);groups=export(ident)
  derivatives=[]
  for mov in MOVEROOTS:mov.location.y=float(mov['access_translation_m'])
  bpy.context.view_layer.update();access_bounds,unused=measure();export(ident+'_access')
  derivatives.append({'name':'access','export':f'exports/{ident}_access.glb','glb_sha256':sha(BASE/'exports'/f'{ident}_access.glb'),'bounds_blender_z_up':access_bounds,'motion_roots':MOVES,'counted_as_new_design':False})
  for mov in MOVEROOTS:mov.location.y=0
  bpy.context.view_layer.update()
  lo,hi=bounds['min_m'],bounds['max_m'];gl=[lo[0],lo[2],-hi[1]];gh=[hi[0],hi[2],-lo[1]]
  r={'catalogue_id':ident,'name':name,'title':name,'unique_design':True,'script_assisted_original_design':True,'source':f'source/{ident}.blend','export':f'exports/{ident}.glb','generator':'source/build_auditorium_arrival.py','source_frame':'metres, Blender source Z-up; -Y public front; +Y staff/service','exchange_frame':'metres GLB Y-up; source(x,y,z)->(x,z,-y); actual node hierarchy authoritative','pivot':{'source_m':[0,0,0],'gltf_m':[0,0,0],'datum':'floor plane Z0; unplaced component'},'bounds_blender_z_up':bounds,'bounds_gltf_y_up':{'min_m':gl,'max_m':gh,'dimensions_m':[b-a for a,b in zip(gl,gh)]},'dimensions_blender_xyz_m':bounds['dimensions_m'],'evaluated_source_triangles':tris,'evaluated_triangles':tris,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role']for o in PARTS)),'export_mesh_groups':groups,'runtime_consolidation':'Evaluated semantic copies consolidated by material role and genuine fixed/removable/drawer ownership','physical_and_proposal_markers':MARKERS,'joins':JOINS,'receiver_voids':VOIDS,'motions':MOVES,'collision_proposal_file':'collision_proposals.json','marker_api_file':'marker_api.json','used_textures_packed':True,'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'glb_sha256':sha(BASE/'exports'/f'{ident}.glb'),'generator_sha256':sha(Path(__file__)),'details':details,'state_derivatives':derivatives,'limitations':['Original host absent; no room adjacency, fit, registered place or capacity added','Physical host support, access/egress, body/cart routes and all six species fit remain pending','No acoustic, load, moving mechanism, lighting, electrical, transaction or game performance certification','Removal pose needs hand support and tool release; animation is a geometric proposal only']}
  rows.append(r);(BASE/f'{ident}.manifest.json').write_text(json.dumps(r,indent=2)+'\n')
  for c in COLL:
   c.setdefault('covered_parts',[c['name']]);c.setdefault('omitted_parts',[])
   if 'points_source_m'in c:c['points_gltf_m']=[glb(p)for p in c['points_source_m']]
   else:c['min_gltf_m']=[c['min_source_m'][0],c['min_source_m'][2],-c['max_source_m'][1]];c['max_gltf_m']=[c['max_source_m'][0],c['max_source_m'][2],-c['min_source_m'][1]]
  coll[ident]={'frame':'Blender Z-up metres with explicit GLB Y-up conversion','status':'Uninstalled structural collision proposal; no runtime behavior','shapes':COLL,'shape_count':len(COLL),'preserve_voids':VOIDS,'motion_roots':MOVES,'omitted_parts':[],'limits':'Finite geometric proposal; exposed artwork thickness included; component movement path must be reserved separately, not filled by a collision box'};api[ident]=MARKERS
 (BASE/'manifest.json').write_text(json.dumps({'family':'auditorium_arrival','revision':'auditorium-arrival-02','assets':rows},indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');(BASE/'marker_api.json').write_text(json.dumps(api,indent=2)+'\n')
 print('BUILT',[(r['catalogue_id'],r['evaluated_triangles'],r['dimensions_blender_xyz_m'],r['export_mesh_groups'])for r in rows])
if __name__=='__main__':main()
