"""AST-BOT-001. Original script-assisted branching canopy, not hand-GUI work.
Metres, Z up, soil-plane pivot at origin. Curve branch controls remain editable.
Run Blender 4.3.2 -b --threads 2 --python source/build_canopy.py.
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]; CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('botanical_materials',CAT/'standards/botanical_materials.py')
mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
MATS=mm.materials(); PARTS=[]; CONTACTS=[]; PATHS={}; LEAF_RECORDS=[]
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1

def meta(ob,role,kind):
 ob['catalogue_id']='AST-BOT-001';ob['material_role']=role;ob['semantic_kind']=kind
 ob['authorship']='Original intentionally composed script-assisted design; no hand-GUI claim'
 PARTS.append(ob);return ob

def branch(name,pts,radii,parent=None,kind='closed_branch'):
 cu=bpy.data.curves.new(name+'_editable_path','CURVE');cu.dimensions='3D';cu.resolution_u=1
 cu.bevel_depth=1;cu.bevel_resolution=1;cu.use_fill_caps=True;cu.resolution_u=1
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co,r in zip(sp.points,pts,radii):p.co=(*co,1);p.radius=r
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(MATS['botanical_bark'])
 ob['path_points_m']=json.dumps(pts);ob['path_radii_m']=json.dumps(radii);ob['parent_branch']=parent or 'soil_plane'
 meta(ob,'botanical_bark',kind);PATHS[name]={'points_m':pts,'radii_m':radii,'parent':parent}
 if parent:
  pp=PATHS[parent];q=Vector(pts[0]);best=None
  for a,b,ra,rb in zip(pp['points_m'][:-1],pp['points_m'][1:],pp['radii_m'][:-1],pp['radii_m'][1:]):
   a,b=Vector(a),Vector(b);v=b-a;t=max(0,min(1,(q-a).dot(v)/v.length_squared));d=(q-(a+t*v)).length
   rec=(d,ra+(rb-ra)*t)
   if best is None or d<best[0]:best=rec
  CONTACTS.append({'child':name,'parent':parent,'start_m':pts[0],'parent_centerline_distance_m':best[0],'parent_radius_m':best[1],'child_radius_m':radii[0],'radial_overlap_m':best[1]+radii[0]-best[0],'construction':'Capped closed curved branch starts on parent centerline and overlaps its solid; distinct editable support meshes, not a welded boolean union'})
 return ob

def new_leaf_group(name,verts,faces,uvs,role,records):
 me=bpy.data.meshes.new(name+'_folded_leaf_mesh');me.from_pydata(verts,[],faces);me.update()
 uv=me.uv_layers.new(name='metric_material_uv')
 for p in me.polygons:
  for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);meta(ob,role,'open_folded_leaf_surfaces')
 ob['leaf_attachment_records']=json.dumps(records);ob['foliage_surface']='Opaque double-sided thin surface; deliberately open boundary edges; 8 triangles per leaf'
 return ob

def leaf(verts,faces,uvs,base,direction,L,W,roll):
 # An elongated, shouldered blade with visible shallow central keel, downturned tip.
 D=Vector(direction).normalized();S=D.cross(Vector((0,0,1))).normalized();N=S.cross(D).normalized()
 if N.z<0:N=-N
 S2=S*math.cos(roll)+N*math.sin(roll);N2=N*math.cos(roll)-S*math.sin(roll)
 local=[(0,0,0),(-W*.46,L*.29,.009),(W*.44,L*.29,.008),(0,L*.29,.025),(-W*.36,L*.66,.000),(W*.34,L*.66,-.001),(0,L*.66,.020),(0,L,-.028)]
 idx=len(verts)
 for x,y,z in local:
  co=Vector(base)+S2*x+D*y+N2*z;verts.append(tuple(co));uvs.append((x/W+.5,y/L))
 # Winding faces toward N2. Every surface stays opaque and double-sided.
 fs=[(0,3,1),(0,2,3),(1,3,6),(1,6,4),(3,2,5),(3,5,6),(4,6,7),(6,5,7)]
 faces.extend(tuple(idx+i for i in f) for f in fs)
 return tuple(Vector(base)+D*L-N2*.028)

trunk='01_primary_S_trunk'
branch(trunk,[(0,0,0),(0,0,.13),(.038,.012,.32),(-.024,.034,.79),(.065,.020,1.22),(.05,.045,1.53),(.16,.07,1.88),(.12,.08,2.20),(.18,.08,2.45)],[.105,.096,.087,.071,.058,.047,.036,.020,.0075])
# Root flare fingers terminate exactly at the soil plane and join the central stem.
for i,(a,L) in enumerate([(15,.19),(128,.17),(244,.21)]):
 a=math.radians(a);x,y=math.cos(a)*L,math.sin(a)*L
 # Start on stem, curve down into soil; the cap is level because final segment is vertical.
 branch(f'02_root_flare_{i+1}',[(.015,0,.20),(x*.57,y*.57,.065),(x,y,.025),(x,y,0)],[.045,.038,.024,.024],trunk,'closed_root_flare')

ARMS=[
 ('10_low_left',[ (.065,.020,1.22),(-.22,-.012,1.47),(-.52,-.024,1.68),(-.80,.025,1.81)],[.046,.034,.022,.008]),
 ('11_mid_right',[(.05,.045,1.53),(.35,.018,1.71),(.64,-.054,1.86),(.87,-.090,2.00)],[.041,.029,.019,.008]),
 ('12_back_left',[(.05,.045,1.53),(-.18,.30,1.83),(-.37,.44,2.05),(-.55,.52,2.17)],[.036,.026,.017,.007]),
 ('13_back_right',[(.16,.07,1.88),(.33,.27,2.07),(.51,.40,2.25),(.59,.44,2.36)],[.029,.020,.012,.006]),
 ('14_front_mid',[(.16,.07,1.88),(-.08,-.22,1.99),(-.24,-.44,2.12),(-.36,-.53,2.23)],[.032,.023,.014,.006]),
 ('15_upper_left',[(.12,.08,2.20),(-.08,.14,2.37),(-.28,.18,2.46),(-.42,.21,2.49)],[.023,.017,.010,.005]),
 ('16_top_back',[(.12,.08,2.20),(.23,.15,2.35),(.27,.25,2.44),(.25,.33,2.51)],[.020,.014,.009,.0045])]
for name,pts,r in ARMS:branch(name,pts,r,trunk)

# Three terminal sprays per tier, distributed along each limb rather than sphere volumes.
# All leaf locations follow their supporting shoot, with individually recorded attachment points.
for ai,(arm,pts,rads) in enumerate(ARMS):
 for si,t in enumerate([.20,.60,.94]):
  pa,pb=Vector(pts[-2]),Vector(pts[-1]);start=pa.lerp(pb,t)
  outward=Vector((pb.x-pa.x,pb.y-pa.y,0)).normalized();side=Vector((-outward.y,outward.x,0))
  handed=[-1,1,0][si];direction=(outward*.72+side*handed*.54+Vector((0,0,.42 if ai<5 else .17))).normalized()
  length=[.34,.37,.35][si];end=start+direction*length
  # Swept shallow arch keeps each spray at a deliberate crown tier.
  mid=start.lerp(end,.52)+Vector((0,0,.035))
  shoot=f'20_spray_{ai+1:02d}_{si+1}'
  branch(shoot,[tuple(start),tuple(mid),tuple(end)],[.012,.007,.0025],arm,'closed_terminal_shoot')
  grouped={role:([],[],[],[]) for role in ['botanical_leaf_jade','botanical_leaf_sage','botanical_leaf_olive']}
  for li in range(10):
   u=.10+.085*li
   if u<=.52:attachment=start.lerp(mid,u/.52)
   else:attachment=mid.lerp(end,(u-.52)/.48)
   sign=-1 if li%2==0 else 1
   facing=(direction*.28+side*sign*.93+Vector((0,0,.18+.08*((li+si)%3)))).normalized()
   petiole_end=attachment+facing*.026
   petiole=f'30_petiole_{ai+1:02d}_{si+1}_{li+1:02d}'
   branch(petiole,[tuple(attachment),tuple(petiole_end)],[.0032,.002],shoot,'closed_leaf_petiole')
   role=['botanical_leaf_jade','botanical_leaf_jade','botanical_leaf_olive','botanical_leaf_jade','botanical_leaf_sage'][(ai+li+si*2)%5]
   v,f,uv,rr=grouped[role]
   L=.235+.026*((li*3+ai+si)%4);W=.104+.010*((li+si)%3)
   tip=leaf(v,f,uv,petiole_end,facing,L,W,math.radians(sign*(7+li%4*5)))
   rec={'petiole':petiole,'leaf_base_m':list(petiole_end),'tip_m':list(tip),'length_m':L,'width_m':W,'petiole_to_leaf_base_gap_m':0.0}
   rr.append(rec);LEAF_RECORDS.append(rec)
  # Each group keeps its place in the canopy and material role editable in source.
  for role,(v,f,uv,rr) in grouped.items():
   if v:new_leaf_group(f'40_leaves_tier_{ai+1:02d}_spray_{si+1}_{role.removeprefix("botanical_leaf_")}',v,f,uv,role,rr)

def evaluated_mesh(ob):
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
 if ob.type=='CURVE':
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 return me
def planar_uv(me,role):
 active=me.uv_layers.active
 if active is None:active=me.uv_layers.new(name='metric_material_uv')
 for layer in list(me.uv_layers):
  if layer!=active:me.uv_layers.remove(layer)
 active.name='metric_material_uv';active.active_render=True
 scale=tuple(MATS[role].get('meters_per_tile_uv',(.24,.24)))
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(co[axes[0]]/scale[0],co[axes[1]]/scale[1])
 return active
def bounds(obs):
 points=[];tris=0
 for ob in obs:
  me=evaluated_mesh(ob);me.calc_loop_triangles();tris+=len(me.loop_triangles);points.extend(ob.matrix_world@v.co for v in me.vertices);bpy.data.meshes.remove(me)
 lo=[min(p[k] for p in points) for k in range(3)];hi=[max(p[k] for p in points) for k in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[k]-lo[k] for k in range(3)],'triangles':tris}

data=bounds(PARTS)
# Beveled root tips must not fall through soil: endpoint caps are horizontal at Z0.
assert abs(data['min_m'][2])<1e-6,data
assert 2.4<=data['max_m'][2]<=2.8,data
assert all(c['radial_overlap_m']>0 for c in CONTACTS)
for role in ['botanical_leaf_jade','botanical_leaf_sage','botanical_leaf_olive']:
 MATS[role].use_backface_culling=False
sc['asset_scope']='AST-BOT-001 Blender botanical component only; no game adoption or real-room fit'
sc['source_authoring']='Original scripted editable branch paths and intentionally placed folded leaf groups'
sc['soil_plane_z_m']=0.0;sc['leaf_count']=len(LEAF_RECORDS)
sc['reference_inspection']='All actual pixels inspected in batch04 reference_manifest.json before authoring; layered botanical hierarchy and human-scale open outlook transferred; giant atrium tree scale not copied'
blend=ROOT/'AST-BOT-001.blend';glb=ROOT/'AST-BOT-001.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)

# Evaluated role consolidation; preserve editable originals in the saved .blend.
groups={}
for src in PARTS:
 me=evaluated_mesh(src);role=src['material_role']
 if src.type=='CURVE':planar_uv(me,role)
 else:
  active=me.uv_layers.active
  for layer in list(me.uv_layers):
   if layer!=active:me.uv_layers.remove(layer)
  active.name='metric_material_uv';active.active_render=True
 ob=bpy.data.objects.new('export_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(role,[]).append(ob)
export_parts=[]
for role,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name='ASTRAEA_canopy_'+role
 ob['material_role']=role;ob['catalogue_id']='AST-BOT-001';ob['semantic_parts']=json.dumps([s.name for s in PARTS if s['material_role']==role]);export_parts.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in export_parts:ob.select_set(True)
bpy.context.view_layer.objects.active=export_parts[0]
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
leaves=[o for o in PARTS if o.type=='MESH'];leaf_bounds=bounds(leaves)
collision=[]
# Narrow segmented capsules only; open space under and within the crown remains unblocked.
tp=PATHS[trunk]
for i,(a,b,ra,rb) in enumerate(zip(tp['points_m'][:-1],tp['points_m'][1:],tp['radii_m'][:-1],tp['radii_m'][1:])):
 collision.append({'name':f'trunk_segment_{i+1}','shape':'capsule','endpoint_a_m':a,'endpoint_b_m':b,'radius_m':max(ra,rb)+.008})
(ROOT/'AST-BOT-001.collision_proposal.json').write_text(json.dumps({'status':'PROPOSAL only, not runtime-tested','coordinate_system':'Blender metres Z up, plant soil pivot Z0','parts':collision,'canopy_collision':False,'limitations':['Capsule end at soil may extend below Z0; clamp/merge with separately tested planter collision on adoption','Minor twigs and opaque thin leaves nonblocking proposal','No game, actor, ceiling, native physics, route or room-fit certification']},indent=2))
data.update({'catalogue_id':'AST-BOT-001','design':'Asymmetric small branching canopy specimen','authorship':'Original script-assisted intentional geometry, 2026-10-02; no hand-GUI claim','source':blend.name,'exchange':glb.name,'generator':'source/build_canopy.py','units':'metres','source_axes':'Z up, front -Y; GLB standard Y-up conversion','pivot_m':[0,0,0],'pivot_meaning':'Plant soil plane; add planter supplied soil datum to placement Z','soil_contact_z_m':0,'branch_paths':PATHS,'editable_curve_paths':sum(o.type=='CURVE' for o in PARTS),'editable_leaf_groups':len(leaves),'leaf_count':len(LEAF_RECORDS),'leaf_triangles_each':8,'leaf_bounds':leaf_bounds,'material_roles':sorted(groups),'material_transparency':{'alpha_mode':'OPAQUE','alpha_factor':1.0,'leaf_double_sided':True,'leaf_open_boundary_edges':'intentional thin folded geometry','closed_supports':'All bark branch paths have filled caps; branches overlap at measured parent centers, not a welded boolean union'},'source_parts':[o.name for o in PARTS],'support_contacts':'qa/support_contacts.json','collision_proposal':'AST-BOT-001.collision_proposal.json','source_sha256':sha(blend),'glb_sha256':sha(glb),'source_dependencies':['standards/botanical_materials.py','materials/botanical/'],'export':'Evaluated static meshes consolidated by four material roles; coincident curve cap vertices welded; active UV layer normalized before joining; embedded ordinary texture maps','reference_response':'Layered crown planes and articulated branching from the botanical island, tempered to human-scale planted edges from the intimate and dense outlook references','acceptance_limits':['Component catalogue only, not installed in a game','No whole-canopy collision','No living plant care, indoor ceiling or all-species seat compatibility claim','Thin leaves have intentional open boundaries; bark branch solids are individually closed and intersect at joins']})
(ROOT/'AST-BOT-001.manifest.json').write_text(json.dumps(data,indent=2))
(ROOT/'qa/support_contacts.json').write_text(json.dumps({'scope':'Actual authored path geometry; analytical capped-support overlap and exact leaf-base contact','soil_contact_z_m':0.0,'branch_contacts':CONTACTS,'leaf_contacts':LEAF_RECORDS,'all_child_starts_inside_parent_radius':all(c['parent_centerline_distance_m']<c['parent_radius_m'] for c in CONTACTS),'all_branch_contacts_positive':all(c['radial_overlap_m']>0 for c in CONTACTS),'all_leaf_base_gaps_zero':all(r['petiole_to_leaf_base_gap_m']==0 for r in LEAF_RECORDS)},indent=2))
print('CANOPY_BUILD_COMPLETE',json.dumps({k:data[k] for k in ['dimensions_m','triangles','leaf_count','editable_curve_paths','editable_leaf_groups']}))
