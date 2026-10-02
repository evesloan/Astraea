"""Original three-design staff wall catalogue; Blender 4.3, metric Z up.
Script-assisted authored construction. Reads final staff roles only; never edits
prior assets. Run: blender -b --threads 2 --python source/build_staff_wall.py
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT.parents[1]
SPEC=importlib.util.spec_from_file_location('staff_materials',CAT/'standards/staff_materials.py')
MM=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MM)
MATS=MM.materials()
# Final semantic staff material keys are supplied by the common staff helper.
PALE='staff_white_paint'; METAL='staff_zinc'; RUBBER='staff_rubber'
RAIL=[(.045,.765),(.085,.765),(.112,.785),(.120,.802),(.120,.806),(.1185,.806),(.1185,.809),(.120,.809),(.120,.890),(.1185,.890),(.1185,.893),(.120,.893),(.120,.898),(.112,.915),(.085,.935),(.045,.935)]
COVE=[(0,0),(.077,0),(.077,.006),(.058,.015),(.047,.031),(.039,.055),(.035,.082),(.035,.182),(.033,.182),(.033,.082),(.037,.054),(.045,.030),(.056,.013),(.075,.004),(0,.002)]
TOP=[(0,2.598),(.044,2.598),(.044,2.575),(.046,2.575),(.046,2.600),(0,2.600)]
PARTS=[]

def wipe():
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.context.scene.unit_settings.system='METRIC'; bpy.context.scene.unit_settings.scale_length=1
 PARTS.clear()

def material_uv(me,role):
 layer=me.uv_layers.new(name='metric_material_uv')
 scale=tuple(MATS[role]['meters_per_tile_uv'])
 for poly in me.polygons:
  axis=max(range(3),key=lambda k:abs(poly.normal[k])); axes=[k for k in range(3) if k!=axis]
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   layer.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
 return layer

def mesh(name,verts,faces,role,bevel=0):
 me=bpy.data.meshes.new(name+'_mesh'); me.from_pydata(verts,[],faces); me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);material_uv(me,role)
 ob['material_role']=role;ob['authorship']='Original independent script-assisted staff construction, 2026-10-02'
 if bevel:
  mod=ob.modifiers.new('Editable formed edge easing','BEVEL');mod.width=bevel;mod.segments=1;mod.limit_method='ANGLE';mod.angle_limit=math.radians(35)
  mod=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 PARTS.append(ob);return ob

def box(name,lo,hi,role,bevel=0):
 x0,y0,z0=lo;x1,y1,z1=hi
 return mesh(name,[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)

def sweep(name,profile,stations,role,bevel=0):
 # Stations x,y,nx,ny. The miter station's offset vector is deliberately
 # non-unit (1,-1) so both profiles meet on a true 45-degree inner corner.
 verts=[(x+nx*d,y+ny*d,z) for x,y,nx,ny in stations for d,z in profile]
 n=len(profile);faces=[tuple(reversed(range(n))),tuple((len(stations)-1)*n+j for j in range(n))]
 for k in range(len(stations)-1):
  faces.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
 ob=mesh(name,verts,faces,role,bevel);ob['closed_section_depth_height_m']=json.dumps(profile);return ob

def straight(a,b):return [(a,0,0,-1),(b,0,0,-1)]
def corner(length):return [(length,0,0,-1),(0,0,1,-1),(0,-length,1,0)]
def profile_rect(d0,d1,z0,z1):return [(d0,z0),(d1,z0),(d1,z1),(d0,z1)]

def fixing(name,x,y,z,face='A'):
 # Eight-sided raised countersunk washer and recessed slot; both closed.
 r=.0065; dep=.0013
 verts=[]
 for dd,rr in [(0,r),(-dep,.0048)]:
  for i in range(8):
   a=2*math.pi*i/8
   verts.append((x+rr*math.cos(a),y+dd,z+rr*math.sin(a)) if face=='A' else (x-dd,y+rr*math.cos(a),z+rr*math.sin(a)))
 faces=[tuple(reversed(range(8))),tuple(8+i for i in range(8))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 mesh(name,verts,faces,METAL)
 if face=='A':box(name+'_recessed_slot',(x-.0026,y-dep-.00012,z-.00048),(x+.0026,y-dep+.00010,z+.00048),RUBBER)
 else:box(name+'_recessed_slot',(x+dep-.0001,y-.0026,z-.00048),(x+dep+.00012,y+.0026,z+.00048),RUBBER)

def bay():
 # Grounded formed carrier channels reach the true Y0 backing plane.
 for i,x in enumerate([0,.585,1.170]):
  box(f'backing_vertical_carrier_{i+1}',(x,-.029,.004),(x+.030,0,2.598),METAL,.0007)
 for i,z in enumerate([.19,.742,.937,2.565]):box(f'backing_horizontal_fixing_rail_{i+1}',(0,-.030,z),(1.2,-.018,z+.016),METAL,.0005)
 # Shallow opaque reveal seals cover the visible joint without protruding.
 box('continuous_sealed_backing',(0,-.031,.180),(1.2,-.029,2.598),RUBBER)
 for name,z0,z1 in [('washable_lower_replaceable_panel',.180,.758),('washable_upper_replaceable_panel',.942,2.575)]:
  box(name,(.006,-.044,z0),(1.194,-.031,z1),PALE,.0008)
 sweep('folded_continuous_top_return',TOP,straight(0,1.2),METAL)
 sweep('washdown_coved_formed_foot',COVE,straight(0,1.2),METAL)
 sweep('continuous_impact_rail_carrier',profile_rect(.039,.054,.775,.925),straight(0,1.2),METAL)
 sweep('replaceable_closed_rubber_cart_bumper',RAIL,straight(0,1.2),RUBBER)
 for x in [.054,1.146]:
  for z in [.258,.671,1.04,2.48]:fixing(f'panel_fixing_{x:.3f}_{z:.3f}',x,-.044,z)

def inside_corner():
 # Continuous closed L skins form a real inside corner; no intersecting boxes.
 sweep('L_backing_carrier',profile_rect(0,.030,.004,2.598),corner(.300),METAL)
 sweep('L_continuous_reveal_seal',profile_rect(.029,.031,.180,2.598),corner(.300),RUBBER)
 for name,z0,z1 in [('L_washable_lower_corner_skin',.180,.758),('L_washable_upper_corner_skin',.942,2.575)]:
  sweep(name,profile_rect(.031,.044,z0,z1),corner(.294),PALE,.0007)
 sweep('L_folded_top_closure',TOP,corner(.300),METAL)
 sweep('L_continuous_coved_foot',COVE,corner(.300),METAL)
 sweep('L_impact_rail_carrier',profile_rect(.039,.054,.775,.925),corner(.300),METAL)
 sweep('L_mitered_closed_rubber_guard',RAIL,corner(.300),RUBBER)
 for z in [.258,.671,1.04,2.48]:
  fixing(f'A_corner_fixing_{z:.3f}',.240,-.044,z)
  fixing(f'B_corner_fixing_{z:.3f}',.044,-.240,z,'B')
 # A narrow formed seam cover at the concave vertical arris is washable.
 sweep('folded_inside_corner_hygiene_cover',profile_rect(.044,.045,.184,2.575),corner(.059),METAL)

def terminal():
 box('closed_terminal_backplate',(0,-.031,.004),(.090,0,2.598),METAL,.0006)
 box('terminal_sealed_reveal',(0,-.033,.180),(.088,-.031,2.598),RUBBER)
 for name,z0,z1 in [('terminal_lower_washable_face',.180,.758),('terminal_upper_washable_face',.942,2.575)]:
  box(name,(.006,-.044,z0),(.074,-.033,z1),PALE,.0006)
 # A closed 2 mm sheet channel has a 16 mm returned flange.
 box('full_height_closed_folded_end',(.088,-.046,0),(.090,0,2.600),METAL,.0004)
 box('terminal_front_return_flange',(.074,-.046,.182),(.088,-.044,2.598),METAL)
 box('terminal_back_return_flange',(.074,-.002,.002),(.088,0,2.598),METAL)
 sweep('terminal_top_return',TOP,straight(0,.090),METAL)
 sweep('terminal_coved_foot',COVE,straight(0,.088),METAL)
 # Shaped plate closes the entire cove silhouette at its outward end.
 sweep('terminal_cove_end_plate',[(0,0),(.077,0),(.077,.006),(.058,.015),(.047,.031),(.039,.055),(.035,.082),(.035,.182),(0,.182)],straight(.088,.090),METAL)
 sweep('terminal_rail_carrier',profile_rect(.039,.054,.775,.925),straight(0,.068),METAL)
 n=len(RAIL);verts=[]
 for x,scale in [(0,1),(.062,1),(.080,.87),(.090,.65)]:
  verts.extend((x,-(.045+(d-.045)*scale),.850+(z-.850)*scale) for d,z in RAIL)
 faces=[tuple(reversed(range(n))),tuple(3*n+j for j in range(n))]
 for k in range(3):faces.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
 mesh('closed_tapered_rubber_bumper_end',verts,faces,RUBBER)
 for z in [.258,1.04,2.48]:fixing(f'terminal_fixing_{z:.3f}',.037,-.044,z)

def bounds(objects):
 points=[];tris=0;dg=bpy.context.evaluated_depsgraph_get()
 for ob in objects:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles)
  points.extend(ob.matrix_world@v.co for v in me.vertices);eo.to_mesh_clear()
 lo=[min(v[k] for v in points) for k in range(3)];hi=[max(v[k] for v in points) for k in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[k]-lo[k] for k in range(3)],'triangles':tris}

def export(objects,dst):
 dg=bpy.context.evaluated_depsgraph_get();groups={}
 for src in objects:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=active:me.uv_layers.remove(layer)
  active.name='metric_material_uv';active.active_render=True
  # Bevel interpolation may collapse narrow cap triangles; repair only affected
  # polygons by their dominant plane, keeping real metre-scaled coordinates.
  me.calc_loop_triangles();repair=set();scale=tuple(MATS[src['material_role']]['meters_per_tile_uv'])
  for tri in me.loop_triangles:
   a,b,c=[active.data[i].uv for i in tri.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-13:repair.add(tri.polygon_index)
  for pidx in repair:
   p=me.polygons[pidx];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in p.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
  ob=bpy.data.objects.new('export_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
 run=[]
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name='ASTRAEA_staff_wall_'+role
  ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in objects if s['material_role']==role]);run.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in run:ob.select_set(True)
 bpy.context.view_layer.objects.active=run[0]
 bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 for ob in run:bpy.data.objects.remove(ob,do_unlink=True)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

CONNECTIONS={
 'bay':{'origin':'left floor seam','backing_planes':['Y=0'],'mating_seams':[{'name':'left','plane':'X=0','normal':[-1,0,0]},{'name':'right','plane':'X=1.2','normal':[1,0,0]}],'extension_m':[1.2,0,0],'panel_edge_setback_m':.006,'panel_to_panel_gap_m':.012,'maximum_inward_projection_m':.120,'mount':'Fix backing rails to a separately verified wall substrate; carriers rear Y0. Floor cove contacts Z0.'},
 'corner':{'origin':'backing-plane intersection at floor','backing_planes':['Y=0','X=0'],'inside_quadrant':'X>0 and Y<0','mating_seams':[{'name':'A','plane':'X=0.3','normal':[1,0,0],'connect_bay_origin_m':[.3,0,0],'bay_rotation_z_deg':0},{'name':'B','plane':'Y=-0.3','normal':[0,-1,0],'connect_bay_origin_m':[0,-1.5,0],'bay_rotation_z_deg':90}],'leg_length_m':.300,'panel_to_panel_gap_m':.012,'maximum_inward_projection_m':.120,'mount':'Fix both L carrier legs to separately verified orthogonal substrate planes. Continuous cove reaches Z0.'},
 'terminal':{'origin':'inboard floor seam','backing_planes':['Y=0'],'mating_seams':[{'name':'inboard','plane':'X=0','normal':[-1,0,0]}],'place_at_bay_right_m':[1.2,0,0],'extension_m':[.09,0,0],'closed_end_plane':'X=0.09','panel_to_panel_gap_m':.012,'maximum_inward_projection_m':.120,'left_end_variant':'Reuse the same design with reflection across the mating seam; apply transform and correct winding before integration. Not a fourth authored asset.','mount':'Fasten backplate to verified substrate; formed cove and end plate touch Z0.'}}

def collision(kind):
 def aabb(name,lo,hi):return {'semantic_part':name,'type':'box','min_m':lo,'max_m':hi}
 if kind=='bay':parts=[aabb('panel_and_carrier',[0,-.046,0],[1.2,0,2.6]),aabb('bumper',[0,-.120,.765],[1.2,-.046,.935]),aabb('coved_foot',[0,-.077,0],[1.2,-.046,.080])]
 elif kind=='corner':parts=[aabb('A_panel',[0,-.046,0],[.3,0,2.6]),aabb('B_panel',[0,-.3,0],[.046,0,2.6]),aabb('A_bumper',[.046,-.120,.765],[.3,-.046,.935]),aabb('B_bumper',[.046,-.3,.765],[.120,-.120,.935]),aabb('A_cove',[.046,-.077,0],[.3,-.046,.080]),aabb('B_cove',[.046,-.3,0],[.077,-.077,.080])]
 else:parts=[aabb('closed_end',[0,-.046,0],[.09,0,2.6]),aabb('bumper',[0,-.120,.765],[.09,-.046,.935]),aabb('cove',[0,-.077,0],[.09,-.046,.182])]
 return {'status':'Compound collision PROPOSAL only; engine acceptance pending','coordinate_space':'Blender metres Z up','parts':parts,'preserves':'Usable circulation quadrant; no whole-arrangement hull','limitations':'Conservative faceted visual profiles simplified to boxes. Actual cart/body/route clearance must be checked in the unavailable original game.'}

RECORDS=[]
for kind,ident,fn in [('bay','AST-STF-001',bay),('corner','AST-STF-002',inside_corner),('terminal','AST-STF-003',terminal)]:
 wipe();fn();obs=list(PARTS);data=bounds(obs)
 for ob in obs:ob['catalogue_id']=ident
 bpy.context.scene['asset_scope']='Independent staff wall component. Blender evidence only, no room/game proof.'
 bpy.context.scene['join_contract']=json.dumps(CONNECTIONS[kind])
 blend=ROOT/f'{ident}.blend';glb=ROOT/f'{ident}.glb'
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 export(obs,glb)
 data.update({'catalogue_id':ident,'design':kind,'authorship':'New script-assisted authored asset, 2026-10-02; no original game files changed','source':blend.name,'exchange':glb.name,'editable_semantic_parts':[o.name for o in obs],'material_roles':sorted({o['material_role'] for o in obs}),'connection_api':CONNECTIONS[kind],'collision_proposal':f'{ident}.collision_proposal.json','source_sha256':sha(blend),'glb_sha256':sha(glb),'generator':'source/build_staff_wall.py','units':'metres','source_axes':'Z up, front −Y; corner interior +X/−Y','export':'GLB standard Y-up conversion; evaluated static meshes consolidated by material role after active UV normalization; embedded original colour tiles','source_dependencies':['standards/staff_materials.py','materials/staff/'],'visual_intent':'Washable pale panels, practical folded metal, rubber cart protection, restrained surface variation. Deliberately no guest timber/luxury language.','acceptance_limits':['Component source/export checks only','No room shell, doorway, route or actor integration','No game rendering, collision runtime or performance acceptance']})
 (ROOT/f'{ident}.manifest.json').write_text(json.dumps(data,indent=2));(ROOT/f'{ident}.collision_proposal.json').write_text(json.dumps(collision(kind),indent=2));RECORDS.append(data)
(ROOT/'family_summary.json').write_text(json.dumps({'unique_designs':3,'asset_ids':[r['catalogue_id'] for r in RECORDS],'components':RECORDS},indent=2))
print('STAFF_WALL_BUILD_COMPLETE',[(r['catalogue_id'],r['triangles']) for r in RECORDS])
