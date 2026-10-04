"""AST-ENG-003 original script-assisted wall control console, Blender 4.3.
Metres, source Z up and front -Y. Source datum: wall contact plane, console centre.
Run: blender -b --threads 2 --python source/build_utility_console.py
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1];ID='AST-ENG-003'
spec=importlib.util.spec_from_file_location('staff_materials',CAT/'standards/staff_materials.py');mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
MATS=mm.materials();PARTS=[];MARKERS=[];CONTROLS=[];CONTACTS=[]
P='staff_white_paint';B='staff_bluegrey_paint';Z='staff_zinc';R='staff_rubber';O='staff_opal';RED='staff_cable_red';BLUE='staff_cable_blue';G='utility_console_original_print'
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
root=bpy.data.objects.new(ID+'_wall_datum',None);bpy.context.collection.objects.link(root)
root['catalogue_id']=ID;root['metadata_revision']='utility-console-frames-01';root['source_frame']='Blender source metres Z-up; front -Y; wall datum at console centre'
root['exchange_frame']='glTF Y-up metres; front +Z; actual node hierarchy authoritative'
root['datum_blender_source_m']=[0.,0.,0.];root['datum_gltf_yup_m']=[0.,0.,0.]
root['proposed_installation_datum_height_above_deck_m']=1.45
root['static_artwork']='Printed circuit mimic and analogue dial; no live telemetry, simulation or operating ratings'
root['scope']='Original independent catalogue asset; no room, fluid simulator, device controller or certified actor fit'
mat=bpy.data.materials.new('ASTRAEA_'+G);mat.use_nodes=True;mat['astraea_material_role']=G;mat['material_revision']='console-print-01';mat['meters_per_tile_uv']=[1.,1.];mat['static_artwork']=True
nodes=mat.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.86;bs.inputs['Metallic'].default_value=0
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/console_graphics.png'),check_existing=True);tex.image.pack();tex.interpolation='Linear';tex.extension='EXTEND'
out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);MATS[G]=mat
ATLAS=json.loads((ROOT/'textures/console_graphics.json').read_text())['zones_pixels_top_left']
def cv(p):return [p[0],p[2],-p[1]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def uv(me,role):
 layer=me.uv_layers.new(name='metric_material_uv');scale=MATS[role]['meters_per_tile_uv']
 for poly in me.polygons:
  axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
def mesh(name,verts,faces,role,bevel=0,keep=False):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=root;me.materials.append(MATS[role]);uv(me,role);ob['material_role']=role;ob['catalogue_id']=ID
 ob['authorship']='Original script-assisted designed construction, 2026-10-02';ob['preserve_named_node']=keep
 if bevel:
  mod=ob.modifiers.new('Editable edge easing','BEVEL');mod.width=bevel;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
  mod=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 PARTS.append(ob);return ob
def box(name,lo,hi,role,bevel=0,keep=False):
 x,y,z=lo;X,Y,Zz=hi
 return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Zz),(X,y,Zz),(X,Y,Zz),(x,Y,Zz)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel,keep)
def profile(w,h,c):return [(-w/2+c,-h/2),(w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]
def slab(name,poly,y0,y1,role,bevel=0,keep=False):
 n=len(poly);v=[(x,y,z) for y in [y0,y1] for x,z in poly];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,role,bevel,keep)
def ring(name,outer,inner,y0,y1,role,bevel=0):
 n=len(outer);v=[(x,y,z) for y in [y0,y1] for p in [outer,inner] for x,z in p];f=[]
 for i in range(n):
  j=(i+1)%n;f.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
 return mesh(name,v,f,role,bevel)
def cylinder(name,center,r,depth,role,n=24,axis='Y',bevel=0,keep=False):
 x,y,z=center;verts=[]
 for dep in [-depth/2,depth/2]:
  for i in range(n):
   a=2*math.pi*i/n
   verts.append((x+r*math.cos(a),y+dep,z+r*math.sin(a)) if axis=='Y' else (x+r*math.cos(a),y+r*math.sin(a),z+dep))
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,f,role,bevel,keep)
def annulus(name,center,outer,inner,depth,role,n=24,bevel=0):
 x,y,z=center
 po=[(x+outer*math.cos(2*math.pi*i/n),z+outer*math.sin(2*math.pi*i/n)) for i in range(n)]
 pi=[(x+inner*math.cos(2*math.pi*i/n),z+inner*math.sin(2*math.pi*i/n)) for i in range(n)]
 return ring(name,po,pi,y-depth/2,y+depth/2,role,bevel)
def move_origin(ob,p):
 ob.data.transform(Matrix.Translation(-Vector(p)));ob.location=p
def marker(name,p,kind,normal=None):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.parent=root;ob.location=p;ob.empty_display_size=.025
 ob['record_kind']=kind;ob['point_blender_source_m']=list(p);ob['point_gltf_yup_m']=cv(p);ob['metadata_revision']='utility-console-frames-01'
 if normal:ob['normal_blender_source']=list(normal);ob['normal_gltf_yup']=cv(normal)
 MARKERS.append(ob);return ob
def fixing(name,x,y,z,r=.007):
 cylinder(name,(x,y+.0009,z),r,.0028,Z,n=12,bevel=.0003)
 box(name+'_slot',(x-r*.46,y-.0006,z-.0006),(x+r*.46,y-.00025,z+.0006),R)
def graphic(name,x,z,w,h,y,zone):
 ob=box(name,(x-w/2,y,z-h/2),(x+w/2,y+.0008,z+h/2),G)
 x0,y0,x1,y1=ATLAS[zone];lay=ob.data.uv_layers.active
 for p in ob.data.polygons:
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   u=(v.x-(x-w/2))/w;vv=(v.z-(z-h/2))/h
   # Nonzero side UV areas retain full coverage on the front print plane.
   if abs(p.normal.y)<.5:
    axis=0 if abs(p.normal.z)>.5 else 2
    u=(v[axis]-(x-w/2 if axis==0 else z-h/2))/(w if axis==0 else h);vv=(v.y-y)/.0008
   lay.data[li].uv=((x0+u*(x1-x0))/1024,1-(y1-vv*(y1-y0))/1024)
 ob['static_artwork']=True;ob['graphic_atlas_zone']=zone;return ob
def graphic_disc(name,x,z,r,y,zone):
 ob=cylinder(name,(x,y+.0004,z),r,.0008,G,n=32)
 x0,y0,x1,y1=ATLAS[zone];lay=ob.data.uv_layers.active
 for p in ob.data.polygons:
  if abs(p.normal.y)<.5:continue
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;u=(v.x-x+r)/(2*r);vv=(v.z-z+r)/(2*r)
   lay.data[li].uv=((x0+u*(x1-x0))/1024,1-(y1-vv*(y1-y0))/1024)
 ob['static_artwork']=True;ob['graphic_atlas_zone']=zone;return ob

# Folded case: octagonal perimeter, stepped front rim and real recessed face.
outer=profile(.82,.68,.06);inner=profile(.768,.628,.052)
slab('formed_rear_closure',outer,-.098,-.079,Z,.0015)
ring('deep_formed_case_returns',outer,inner,-.205,-.088,B,.0017)
ring('pale_front_protection_rim',outer,inner,-.212,-.194,P,.0013)
slab('recessed_control_face',[(-.3825,-.195),(.3825,-.195),(.3825,.263),(.3345,.311),(-.3345,.311),(-.3825,.263)],-.185,-.165,P,.001)
box('lower_face_return',(-.332,-.185,-.312),(.332,-.165,-.294),P,.001)
# Main upper mimic is physically recessed, with its own dark gasket and surround.
box('schematic_recess_gasket',(-.348,-.190,-.052),(.118,-.184,.218),R,.001)
box('schematic_zinc_frame',(-.341,-.195,-.047),(.111,-.188,.211),Z,.003)
graphic('printed_flow_path_mimic',-.115,.082,.434,.244,-.1958,'schematic')
graphic('console_identifier_plate',-.054,.267,.620,.066,-.1858,'header')
# Raised single dial with static physical pointer; no transparent shader.
cylinder('filter_gauge_outer_rim',(.258,-.197,.137),.077,.026,Z,n=32,bevel=.002)
cylinder('filter_gauge_inset',(.258,-.210,.137),.066,.007,R,n=32)
graphic_disc('printed_filter_dial',.258,.137,.062,-.214,'gauge_dial')
pointer=slab('STATIC_filter_gauge_pointer',[(.255,.134),(.217,.166),(.258,.144),(.262,.138)],-.218,-.215,RED,keep=True)
pointer['static_artwork']=True;pointer['not_live_telemetry']=True
cylinder('gauge_pointer_pin',(.258,-.219,.137),.006,.004,Z,n=16)
marker('gauge_static_pointer_datum',(.258,-.219,.137),'Static artwork origin, not a control',[0,-1,0])
# Three individually named tactile buttons. Guard collars remain static by role.
graphic('control_button_legend',-.127,-.076,.425,.040,-.1858,'button_legend')
for name,x,role,purpose in [('START',-.263,BLUE,'Proposed circulate/start action'),('HOLD',-.127,O,'Proposed hold action'),('ISOLATE',.009,RED,'Proposed isolate action; no safety-system claim')]:
 annulus(name+'_guard_collar',(x,-.198,-.133),.029,.021,.029,Z,n=24,bevel=.0005)
 annulus(name+'_dark_socket',(x,-.211,-.133),.023,.021,.010,R,n=24)
 ob=cylinder('CTRL_button_'+name,(x,-.219,-.133),.0195,.015,role,n=24,bevel=.0014,keep=True)
 pivot=[x,-.2115,-.133];touch=[x,-.2265,-.133];move_origin(ob,pivot)
 ob['control_kind']='button';ob['pivot_blender_source_m']=pivot;ob['pivot_gltf_yup_m']=cv(pivot);ob['interaction_blender_source_m']=touch;ob['interaction_gltf_yup_m']=cv(touch)
 ob['press_axis_blender_source']=[0.,1.,0.];ob['press_axis_gltf_yup']=[0.,0.,-1.];ob['proposed_max_travel_m']=.003;ob['purpose']=purpose
 marker(name+'_interaction',touch,'Front cap centre contact proposal',[0,-1,0])
 CONTROLS.append({'node':ob.name,'kind':'button','pivot_blender_source_m':pivot,'pivot_gltf_yup_m':cv(pivot),'interaction_blender_source_m':touch,'interaction_gltf_yup_m':cv(touch),'axis_blender_source':[0,1,0],'axis_gltf_yup':[0,0,-1],'max_travel_proposal_m':.003,'purpose':purpose})
# Three-position selector, distinct grip shape and pivot node, no controller.
graphic('mode_selector_legend',.263,-.101,.181,.143,-.1858,'selector_legend')
annulus('selector_escutcheon',(.263,-.195,-.099),.050,.0285,.024,Z,n=24,bevel=.0007)
annulus('selector_socket',(.263,-.207,-.099),.037,.0285,.016,R,n=24)
knob=cylinder('CTRL_mode_selector',(.263,-.222,-.099),.027,.023,B,n=24,bevel=.001,keep=True)
grip=box('CTRL_mode_selector_grip',(.253,-.247,-.126),(.273,-.226,-.072),R,.003,keep=True)
stripe=box('CTRL_mode_selector_index',(.260,-.248,-.125),(.266,-.247,-.118),O,keep=True)
pivot=[.263,-.2105,-.099];touch=[.263,-.247,-.099]
for ob in [knob,grip,stripe]:move_origin(ob,pivot)
grip.parent=knob;grip.location=(0,0,0);stripe.parent=knob;stripe.location=(0,0,0)
knob['control_kind']='rotary_selector';knob['pivot_blender_source_m']=pivot;knob['pivot_gltf_yup_m']=cv(pivot);knob['interaction_blender_source_m']=touch;knob['interaction_gltf_yup_m']=cv(touch)
knob['rotation_axis_blender_source']=[0.,-1.,0.];knob['rotation_axis_gltf_yup']=[0.,0.,1.];knob['proposed_detents_about_named_axis_deg']=[-90.,0.,90.];knob['static_selected_detent']='OFF artwork; no software state';knob['detent_labels_by_angle_deg_json']=json.dumps({'-90':'LOCAL','0':'OFF','90':'REMOTE'})
marker('MODE_interaction',touch,'Front grip contact proposal',[0,-1,0])
CONTROLS.append({'node':knob.name,'kind':'rotary_selector','pivot_blender_source_m':pivot,'pivot_gltf_yup_m':cv(pivot),'interaction_blender_source_m':touch,'interaction_gltf_yup_m':cv(touch),'axis_blender_source':[0,-1,0],'axis_gltf_yup':[0,0,1],'detent_proposals_deg':[-90,0,90],'parts':[knob.name,grip.name,stripe.name]})
# Removable lower hatch with an inset vent pocket and individually formed fins.
ring('service_hatch_perimeter_gasket',[(-.332,-.292),(.332,-.292),(.332,-.202),(-.332,-.202)],[(-.322,-.282),(.322,-.282),(.322,-.212),(-.322,-.212)],-.189,-.184,R,.0005)
hatch=ring('SERVICE_removable_hatch',[(-.328,-.288),(.328,-.288),(.328,-.206),(-.328,-.206)],[(.014,-.275),(.280,-.275),(.280,-.219),(.014,-.219)],-.197,-.187,B,.0007)
hatch['preserve_named_node']=True
hatch['service_action']='Remove four front fasteners, withdraw hatch toward source -Y / GLB +Z; no animation implemented'
hatch['withdrawal_axis_blender_source']=[0.,-1.,0.];hatch['withdrawal_axis_gltf_yup']=[0.,0.,1.]
graphic('service_hatch_print',-.172,-.247,.234,.049,-.1978,'service_label').parent=hatch
box('vent_dark_rear_baffle',(.014,-.162,-.275),(.280,-.158,-.219),R)
box('vent_left_pocket_wall',(.010,-.190,-.279),(.015,-.158,-.215),Z)
box('vent_right_pocket_wall',(.280,-.190,-.279),(.285,-.158,-.215),Z)
box('vent_bottom_pocket_wall',(.014,-.190,-.279),(.281,-.158,-.275),Z)
box('vent_top_pocket_wall',(.014,-.190,-.219),(.281,-.158,-.215),Z)
for i in range(8):
 x=.027+i*.031
 # Sloping fins have closed sections; positive 10 mm gaps remain between fins.
 q=[(x,-.194),(x+.016,-.205),(x+.020,-.200),(x+.004,-.189)]
 v=[(a,b,z) for z in [-.278,-.216] for a,b in q]
 fin=mesh('vent_formed_louver_%02d'%i,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],Z,.0003)
 fin.parent=hatch
for x in [-.314,.314]:
 for z in [-.220,-.275]:
  before=len(PARTS);fixing('hatch_fastener_%.3f_%.3f'%(x,z),x,-.199,z,.0055)
  for ob in PARTS[before:]:ob.parent=hatch
for x,z in [(-.371,.254),(.371,.254),(-.348,-.286),(.348,-.286)]:fixing('case_fixing_%.3f_%.3f'%(x,z),x,-.213,z)
# Four closed rear standoffs carry the case to a true wall Y=0 mounting face.
for x in [-.305,.305]:
 box('rear_vertical_mount_cleat_%.3f'%x,(x-.028,-.094,-.266),(x+.028,-.060,.266),Z,.001)
 for z in [-.221,.221]:
  name='MOUNT_%s_%s'%('L' if x<0 else 'R','LOW' if z<0 else 'HIGH')
  cylinder(name+'_standoff',(x,-.045,z),.022,.080,Z,n=16,bevel=0)
  cylinder(name+'_wall_pad',(x,-.0025,z),.034,.005,R,n=20)
  marker(name,(x,0,z),'Physical wall pad contact centre',[0,1,0])
  CONTACTS.append({'name':name,'point_blender_source_m':[x,0,z],'point_gltf_yup_m':cv([x,0,z]),'normal_blender_source':[0,1,0],'normal_gltf_yup':[0,0,-1],'wall_pad_radius_m':.034,'physical_support_node':name+'_wall_pad'})
# Two organised glands and a short restrained cable drop remain within the shell
# footprint. Cable entries are design interfaces, not plumbing connectors.
for i,(x,role) in enumerate([(-.154,BLUE),(-.094,R)]):
 cylinder('cable_gland_%d'%i,(x,-.118,-.332),.016,.024,Z,n=12,axis='Z')
 cylinder('cable_gland_grip_%d'%i,(x,-.118,-.348),.012,.016,R,n=12,axis='Z')
 cylinder('rear_cable_drop_%d'%i,(x,-.118,-.388),.0075,.075,role,n=12,axis='Z')
 marker('CABLE_entry_%d'%i,(x,-.118,-.4255),'Cable termination interface; unresolved upstream routing',[0,0,-1])
box('cable_organising_bridge',(-.179,-.132,-.407),(-.067,-.106,-.392),Z,.002)
for x in [-.177,-.069]:
 box('cable_bridge_return_%.3f'%x,(x-.004,-.111,-.400),(x+.004,-.079,-.392),Z,.001)
 box('cable_bridge_case_strap_%.3f'%x,(x-.004,-.089,-.396),(x+.004,-.079,-.330),Z,.001)
marker('wall_datum_origin',[0,0,0],'Asset installation origin, intentionally in rear void',[0,1,0])
marker('standing_use_pose',[0,-.85,.20],'Proposed eye pose at 1.65 m when installed at 1.45 m; not physical contact',[0,1,0])
root['width_blender_X_m']=.82;root['wall_front_direction_blender_source']=[0.,-1.,0.];root['wall_front_direction_gltf_yup']=[0.,0.,1.]
root['mount_records_json']=json.dumps(CONTACTS);root['control_records_json']=json.dumps(CONTROLS)
sc['asset_id']=ID;sc['scope']=root['scope'];sc['datum']='Wall plane Y=0 at case centre; place Z=1.45 m above deck as a human-scale proposal only'
sc['graphics']='Static original base-color bitmap printed labels, schematic and dial; no emission or live telemetry'
for ob in PARTS:ob['source_frame']='Blender source metres Z-up';ob['exchange_frame']='glTF Y-up metres'

def evaluated_summary(obs):
 dg=bpy.context.evaluated_depsgraph_get();v=[];tris=0
 for ob in obs:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);v.extend(ob.matrix_world@q.co for q in me.vertices);eo.to_mesh_clear()
 lo=[min(p[k] for p in v) for k in range(3)];hi=[max(p[k] for p in v) for k in range(3)]
 return {'min_blender_source_m':lo,'max_blender_source_m':hi,'dimensions_blender_source_xyz_m':[hi[k]-lo[k] for k in range(3)],'min_gltf_yup_m':[lo[0],lo[2],-hi[1]],'max_gltf_yup_m':[hi[0],hi[2],-lo[1]],'triangles':tris}
bpy.context.view_layer.update();summary=evaluated_summary(PARTS)
blend=ROOT/'source'/f'{ID}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
# Export evaluated static copies by material role; preserve each actual control,
# selector hierarchy, service hatch and metadata markers. UV name normalised first.
dg=bpy.context.evaluated_depsgraph_get();groups={};runs=[];mapping={}
for src in PARTS:
 me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));act=me.uv_layers.active
 for layer in list(me.uv_layers):
  if layer!=act:me.uv_layers.remove(layer)
 act.name='metric_material_uv';act.active_render=True
 me.calc_loop_triangles();repair=set()
 for tri in me.loop_triangles:
  a,b,c=[act.data[i].uv for i in tri.loops]
  if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-13:repair.add(tri.polygon_index)
 for i in repair:
  p=me.polygons[i];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;act.data[li].uv=(v[axes[0]],v[axes[1]])
 ob=bpy.data.objects.new(src.name+'_EXPORT',me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy()
 for k in src.keys():ob[k]=src[k]
 mapping[src]=ob
 if src['preserve_named_node']:runs.append(ob)
 else:groups.setdefault((src['material_role'],src.parent if src.parent!=root else None),[]).append(ob)
for (role,anchor),obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ID+'_static_'+role+('_hatch' if anchor else '');ob['semantic_parts_json']=json.dumps([s.name for s in PARTS if not s['preserve_named_node'] and s['material_role']==role and (s.parent if s.parent!=root else None)==anchor]);runs.append(ob)
 if anchor:
  matrix=ob.matrix_world.copy();ob.parent=mapping[anchor];ob.matrix_world=matrix
for src,ob in mapping.items():
 if not src['preserve_named_node']:continue
 if src.parent in mapping and src.parent['preserve_named_node']:
  matrix=ob.matrix_world.copy();ob.parent=mapping[src.parent];ob.matrix_world=matrix
 else:
  matrix=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=matrix
for ob in runs:
 if not ob.parent:ob.parent=root
# Temporarily rename editable objects so GLB control node names stay exact.
oldnames={o:o.name for o in PARTS if o['preserve_named_node']}
for src,name in oldnames.items():src.name=name+'_SOURCE';mapping[src].name=name
bpy.ops.object.select_all(action='DESELECT')
for ob in runs+MARKERS+[root]:ob.select_set(True)
bpy.context.view_layer.objects.active=root
glb=ROOT/f'{ID}.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
for ob in runs:bpy.data.objects.remove(ob,do_unlink=True)
for src,name in oldnames.items():src.name=name
record={'catalogue_id':ID,'design':'Wall-mounted water-recovery utility control console','revision':'utility-console-01','unique_designs':1,'authoring':'Original script-assisted intentional design; no original game files changed','source':'source/'+blend.name,'generator':'source/build_utility_console.py','exchange':glb.name,**summary,'units':'metres','source_frame':'Blender source Z-up; front -Y; datum at wall plane/console centre','exchange_frame':'glTF Y-up; front +Z; map (x,y,z)->(x,z,-y)','pivot_blender_source_m':[0,0,0],'pivot_gltf_yup_m':[0,0,0],'proposed_installation':{'datum_height_above_deck_m':1.45,'body_bottom_above_deck_m':1.11,'upper_body_above_deck_m':1.79,'button_contact_height_above_deck_m':1.317,'mode_grip_height_above_deck_m':1.351,'standing_eye_above_deck_m':1.65,'standing_eye_blender_source_m':[0,-.85,.20],'standing_eye_gltf_yup_m':[0,.20,.85],'approach':'From source -Y / native GLB +Z; keep 0.80 m open from foremost control, plus site-specific circulation and access assessment','status':'Human-scale installation proposal only; all-species reach, accessibility codes, load rating and engine actor fit untested'},'mounts':CONTACTS,'controls':CONTROLS,'service':{'hatch_node':'SERVICE_removable_hatch','front_withdrawal_axis_blender_source':[0,-1,0],'front_withdrawal_axis_gltf_yup':[0,0,1],'clearance_proposal_m':.30,'fastener_count':4,'vent_fins':8,'vent_clear_gaps_m':.011,'cable_termination_blender_source_m':[[-.154,-.118,-.4255],[-.094,-.118,-.4255]],'cable_termination_gltf_yup_m':[[-.154,-.4255,.118],[-.094,-.4255,.118]],'notes':'Rear cleats/standoffs carry case against wall; organised cable glands and bridge; hollow shell is closed by rear and recessed face. Site cabling and load bearing remain unresolved.'},'static_artwork':'Original printed flow mimic, control legend and static analogue dial with separate fixed pointer. No live telemetry, fluid simulation, device logic, operating rating or emission.','material_roles':sorted({o['material_role'] for o in PARTS}),'shared_material_revision':'astraea-staff-materials-01 unchanged','local_graphic_sources':['textures/draw_console_graphics.py','textures/console_graphics.png','textures/console_graphics.json'],'source_dependencies':['standards/staff_materials.py','materials/staff/manifest.json','materials/staff/*.png'],'editable_named_parts':[o.name for o in PARTS],'named_export_controls':[c['node'] for c in CONTROLS],'export_settings':'Evaluated static meshes consolidated by staff semantic role, normalised active UV layers and embedded PNG; control/hatch nodes and explicit source/native exchange marker extras preserved','cost':{'triangles':summary['triangles'],'source_mesh_parts':len(PARTS),'source_editable_bevels':sum(any(m.type=='BEVEL' for m in o.modifiers) for o in PARTS),'export_mesh_objects':len(runs),'authored_lods':0,'runtime_drawcalls':'See actual GLB primitive count in qa validation; target-PC performance pending'},'source_sha256':sha(blend),'glb_sha256':sha(glb),'reference_manifest':'batches/batch06/reference_manifest.json','reference_use':'Actual blueprint/staff photographs inspected: maintenance purpose, cool painted metal, practical supported service runs; no reference pixels copied or old deck labels adopted.','limits':['Component-only source/export/visual evidence','No room placement or game engine integration','No live controls, circuitry, fluid dynamics, accessibility or safety certification','Collision proposals need original engine testing']}
(ROOT/f'{ID}.manifest.json').write_text(json.dumps(record,indent=2));(ROOT/'manifest.json').write_text(json.dumps({'unique_designs':1,'asset_ids':[ID],'assets':[record]},indent=2))
import runpy
runpy.run_path(str(ROOT/'source/write_collision_proposals.py'))
print('UTILITY_CONSOLE_BUILD_COMPLETE',summary)
