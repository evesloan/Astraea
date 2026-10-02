"""Original joined planted-seat architecture; reproducible intentional profile design.
Blender 4.3, metres, floor Z0, front -Y. No existing ship or room is modified.
Shared textures are packed, authored semantic meshes stay editable; GLBs consolidate
only evaluated copies by material role after preserving and normalizing metric UVs.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]; CAT=ROOT.parents[1]
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
MATS=load('guest_materials',CAT/'standards/materials.py').materials()
MATS['botanical_soil']=load('botanical_materials',CAT/'standards/botanical_materials.py').materials()['botanical_soil']
R=1.4; SEAM=.001; SEAT=.470; SOIL=.390
# Positive depth points toward the sitter. Sculpted stone walls actually bound a
# hollow basin rather than a closed block under the entire planted opening.
FRONT=[(-.150,.095),(-.150,.402),(-.115,.413),(-.032,.413),(.004,.381),(.018,.177),(.084,.105),(.084,0),(-.090,0),(-.129,.045)]
BACK=[(-.880,.095),(-.880,.402),(-.925,.415),(-.984,.415),(-1.019,.375),(-1.014,.092),(-.975,0),(-.865,0),(-.840,.060),(-.840,.095)]
BASE=[(-.880,.075),(-.130,.075),(-.130,.105),(-.880,.105)]
FRONT_CAP=[(-.177,.413),(-.163,.430),(.043,.430),(.058,.417),(.053,.396),(-.164,.396)]
BACK_CAP=[(-1.037,.414),(-1.024,.430),(-.868,.430),(-.854,.417),(-.861,.396),(-1.024,.396)]
BRACKET=[(-.033,.065),(.227,.065),(.247,.091),(.280,.218),(.420,.355),(.442,.394),(.442,.415),(-.032,.415),(-.063,.370),(-.063,.107)]
FOOT=[(-.075,0),(.240,0),(.252,.019),(.244,.065),(-.058,.065)]

def wipe():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def path(kind,a=None,b=None):
 length=R*math.pi/2 if kind=='quarter_turn' else .24 if kind=='closed_end' else 2.4
 a=SEAM if a is None else a;b=length-SEAM if b is None else b
 if kind!='quarter_turn':return [(a,0,1,0,a),(b,0,1,0,b)]
 t0=a/R;t1=b/R;n=max(1,math.ceil((t1-t0)/math.radians(5)))
 arr=[(R*math.sin(t),R*(1-math.cos(t)),math.cos(t),math.sin(t),R*t) for t in [t0+(t1-t0)*i/n for i in range(n+1)]]
 # Exact seam planes across the full wide profile, not radial-angle seam gaps.
 if abs(a-SEAM)<1e-8:arr[0]=(SEAM,0,1,0,a)
 if abs(b-(length-SEAM))<1e-8:arr[-1]=(R,R-SEAM,0,1,b)
 return arr

def sweep(name,stations,profile,role,bevel=.0007,grain='length'):
 verts=[(x+ty*d,y-tx*d,z) for x,y,tx,ty,s in stations for d,z in profile];n=len(profile)
 faces=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(stations)-1) for j in range(n)]
 faces += [tuple(reversed(range(n))),tuple((len(stations)-1)*n+j for j in range(n))]
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role])
 ob['material_role']=role;ob['profile_depth_height_m']=json.dumps(profile);ob['uv_grain']='V follows '+grain
 ob['design_method']='Original intentional metric profile sweep, script-assisted editable mesh'
 uv=me.uv_layers.new(name='metric_material_uv');scale=tuple(MATS[role].get('meters_per_tile_uv',[1,1]))
 perimeter=[0]
 for p,q in zip(profile,profile[1:]):perimeter.append(perimeter[-1]+math.dist(p,q))
 total=perimeter[-1]+math.dist(profile[-1],profile[0])
 for p in me.polygons:
  edge=p.index%n
  for li in p.loop_indices:
   k,j=divmod(me.loops[li].vertex_index,n);d,z=profile[j];s=stations[k][4]
   if p.index>=len(faces)-2:pair=(d/scale[0],z/scale[1])
   elif grain=='vertical':pair=(s/scale[0],(z if abs(profile[(edge+1)%n][1]-profile[edge][1])>.01 else d)/scale[1])
   else:pair=((total if edge==n-1 and j==0 else perimeter[j])/scale[0],s/scale[1])
   uv.data[li].uv=pair
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if bevel:
  m=ob.modifiers.new('Editable eased arris','BEVEL');m.width=bevel;m.segments=1;m.limit_method='ANGLE';m.angle_limit=math.radians(42)
  m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True;m.weight=30
 return ob

def slab_profile(a,b):
 # Three separate thick timber ribbons have a broad flat contact top, eased
 # profile edges, and a dropped rounded-looking outer nose on the front ribbon.
 return [(a,.415),(a,.465),(a+.004,.470),(b-.008,.470),(b,.464),(b,.431),(b-.014,.415)]

def collision(name,stations,profile):
 # Convex wedges follow actual walls / ribbons individually. Never one whole
 # planter convex blocker: above soil the usable cavity remains open.
 return {'semantic_part':name,'solids':[{'type':'convex_hull_points','points_m':[[x+ty*d,y-tx*d,z] for x,y,tx,ty,s in (a,b) for d,z in profile]} for a,b in zip(stations,stations[1:])]}

def create(kind):
 parts=[];coll=[];stations=path(kind);supports=[]
 for name,profile,role in [('sculpted_front_basin_wall',FRONT,'warm_stone'),('sloped_rear_basin_wall',BACK,'warm_stone'),('recessed_cavity_bottom',BASE,'warm_stone'),('enamel_seat_root_coping',FRONT_CAP,'ivory_enamel'),('enamel_rear_coping',BACK_CAP,'ivory_enamel')]:
  parts.append(sweep(name,stations,profile,role));coll.append(collision(name,stations,profile))
 # Soil has real depth down to the basin base and is inset from coping. End cap
 # is intentionally shortened by the terminal wall, so no buried soil/stone overlap.
 soilpath=path(kind,b=.160) if kind=='closed_end' else stations
 profile=[(-.880,.105),(-.150,.105),(-.150,SOIL),(-.880,SOIL)]
 parts.append(sweep('soil_volume_with_usable_planting_surface',soilpath,profile,'botanical_soil',0));coll.append(collision('soil_support_volume_optional',soilpath,profile))
 ribbons=[(.020,.166),(.174,.326),(.334,.490)]
 for i,(a,b) in enumerate(ribbons):
  p=slab_profile(a,b);parts.append(sweep(f'timber_sitting_ribbon_{i+1:02}',stations,p,'warm_walnut',.0006));coll.append(collision(f'timber_seat_ribbon_{i+1:02}',stations,[(a,.415),(b,.415),(b,.470),(a,.470)]))
 for i,(a,b) in enumerate([(.080,.120),(.350,.390)]):
  p=[(a,.381),(b,.381),(b,.415),(a,.415)];parts.append(sweep(f'timber_underseat_bearing_rail_{i+1:02}',stations,p,'warm_walnut'))
 # Small metallic shadow stringer is a continuous inset, not a glowing outline.
 p=[(.021,.198),(.026,.198),(.026,.211),(.021,.211)]
 parts.append(sweep('recessed_front_shadow_stringer',stations,p,'champagne_metal',0))
 if kind=='straight':centers=[.220,1.200,2.180]
 elif kind=='quarter_turn':centers=[R*math.radians(t) for t in (7,32,58,83)]
 else:centers=[.179]
 for i,c in enumerate(centers):
  pp=path(kind,max(SEAM,c-.043),min((R*math.pi/2 if kind=='quarter_turn' else .24 if kind=='closed_end' else 2.4)-SEAM,c+.043))
  for key,p,role in [('seat_load_bracket',BRACKET,'ivory_enamel'),('floor_contact_bracket_shoe',FOOT,'warm_stone')]:
   name=f'{key}_{i+1:02}';parts.append(sweep(name,pp,p,role,.0005,'vertical'));coll.append(collision(name,pp,p))
  x,y,tx,ty,s=path(kind,c,c+.00001)[0]
  supports.append({'along_path_m':c,'center_xy_m':[x,y],'width_m':.086,'foot_z_m':0,'bracket_bottom_z_m':.065,'shoe_top_z_m':.065,'bracket_top_z_m':.415,'timber_underside_z_m':.415,'seat_top_z_m':SEAT,'front_projection_m':.442,'front_seat_overhang_m':.048,'load_path':'timber ribbons + two rails > flared enamel bracket > stone shoe > floor; rear ribbon also nests 15mm into coping'})
 if kind=='closed_end':
  endwall=[(-.880,.105),(-.150,.105),(-.150,.413),(-.880,.413)]
  cap=[(-1.024,.396),(.043,.396),(.058,.417),(.043,.430),(-1.024,.430),(-1.037,.414)]
  for name,pp,p,role in [('closed_end_basin_return',path(kind,.160,.239),endwall,'warm_stone'),('closed_end_enamel_return_coping',path(kind,.160,.239),cap,'ivory_enamel')]:
   parts.append(sweep(name,pp,p,role));coll.append(collision(name,pp,p))
  # Raised horizontal end-grain bar belongs to the joined seat, supported by
  # the final bracket; replaces the last 30mm of ribbon only visually as a join.
  # No added overlay is necessary: three solid ribbon end caps are real ends.
 return parts,coll,supports

def measured(obs):
 dg=bpy.context.evaluated_depsgraph_get();verts=[];tri=0
 for ob in obs:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);verts += [ob.matrix_world@v.co for v in me.vertices];eo.to_mesh_clear()
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 return lo,hi,[b-a for a,b in zip(lo,hi)],tri

def export(obs,p):
 dg=bpy.context.evaluated_depsgraph_get();groups={};repairs=0
 for src in obs:
  me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
  for other in list(me.uv_layers):
   if other!=active:me.uv_layers.remove(other)
  active.name='metric_material_uv';active.active_render=True
  me.calc_loop_triangles();repair=set();sc=tuple(MATS[src['material_role']].get('meters_per_tile_uv',[1,1]))
  for tr in me.loop_triangles:
   a,b,c=[active.data[i].uv for i in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:repair.add(tr.polygon_index)
  for idx in repair:
   face=me.polygons[idx];axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in face.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(v[axes[0]]/sc[0],v[axes[1]]/sc[1])
  repairs+=len(repair)
  ob=bpy.data.objects.new('runtime_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
 runtime=[]
 for role,parts in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in parts:ob.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name='ASTRAEA_planted_seat_'+role;ob['material_role']=role;ob['semantic_parts']=json.dumps([o.name for o in obs if o['material_role']==role]);runtime.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in runtime:ob.select_set(True)
 bpy.context.view_layer.objects.active=runtime[0]
 bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)
 return repairs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 records=[];collision_records={}
 for cid,kind in [('AST-BOT-004','straight'),('AST-BOT-005','quarter_turn'),('AST-BOT-006','closed_end')]:
  wipe();obs,coll,supports=create(kind);bpy.context.view_layer.update()
  sc=bpy.context.scene;sc['catalogue_id']=cid;sc['scope']='Blender component only; room, engine, actor fit and physical behavior untested'
  joins=[{'id':'start','position_m':[0,0,0],'rotation_z_degrees':0,'outward_normal':[-1,0,0],'profile':'planted_seat_470_soil_390'}]
  if kind!='closed_end':joins.append({'id':'end','position_m':[2.4,0,0] if kind=='straight' else [R,R,0],'rotation_z_degrees':0 if kind=='straight' else 90,'outward_normal':[1,0,0] if kind=='straight' else [0,1,0],'profile':'planted_seat_470_soil_390'})
  for ob in obs:ob['catalogue_id']=cid;ob['source_pivot']='Nominal start seam, floor Z0';ob['seams']=json.dumps(joins)
  blend=ROOT/(cid+'.blend');glb=ROOT/(cid+'.glb')
  bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);repair_count=export(obs,glb)
  lo,hi,dims,tris=measured(obs)
  opening={'soil_top_z_m':SOIL,'cavity_base_top_z_m':.105,'soil_depth_m':.285,'coping_top_z_m':.430,'soil_to_coping_clearance_m':.040,'width_m':.730,'front_local_y_m':.150,'rear_local_y_m':.880,'seat_back_y_m':-.020,'seat_to_soil_horizontal_gap_m':.170}
  if kind=='quarter_turn':opening.update({'shape':'quarter annulus','center_xy_m':[0,R],'inner_radius_m':.520,'outer_radius_m':1.250,'start_angle_deg':-90,'end_angle_deg':0,'maximum_facet_angle_deg':5})
  else:opening.update({'shape':'rectangle','min_xy_m':[.001,.150],'max_xy_m':[.160 if kind=='closed_end' else 2.399,.880]})
  meta={'catalogue_id':cid,'name':{'straight':'Joined straight planted-seat edge','quarter_turn':'Joined quarter-turn planted-seat edge','closed_end':'Closed planted-seat terminal'}[kind],'kind':kind,'source_blend':blend.name,'runtime_glb':glb.name,'dimensions_m':dims,'min_m':lo,'max_m':hi,'triangles':tris,'source_parts':len(obs),'editable_semantic_parts':[o.name for o in obs],'material_roles':sorted(set(o['material_role'] for o in obs)),'pivot_m':[0,0,0],'units':'metres; Blender Z up; front -Y','seams':joins,'nominal_seam_gap_m':.002,'seat_top_z_m':SEAT,'seat_underside_z_m':.415,'seat_depth_m':.470,'seat_ribbon_gap_m':.008,'planting_opening':opening,'support_relationships':supports,'closed_cavity_end':kind=='closed_end','front_approach_proposal':{'min_clear_depth_from_seat_nose_m':1.2,'local_y_front_of_straight_module_m':[-1.690,-.490],'scope':'Unoccupied design envelope only, not actor/path certification'},'foliage_separation':'Keep low foliage behind Y +0.15 in straight modules; larger crowns require deliberate plant offsets; no universal all-species contact claim','construction_joints':{'shoe_bracket_z_gap_m':0,'bracket_seat_z_gap_m':0,'rail_seat_z_gap_m':0,'rear_ribbon_coping_vertical_overlap_m':.015,'soil_base_z_gap_m':0,'soil_frontwall_gap_m':0,'soil_backwall_gap_m':0,'nominal_mating_air_gap_m':.002},'collision_proposal_file':'collision_proposals.json','source_method':'Original script-assisted intentional profiles; editable named mesh parts with retained bevel/normal modifiers','export':{'format':'GLB','y_up':True,'scale_applied':True,'consolidation':'One mesh per semantic role','UV':'metric_material_uv normalized before evaluated role joins; degenerate bevel/cap UV repaired using dominant-plane metric projection','repaired_polygons':repair_count,'packed_textures':True},'limitations':['Blender component geometry only; no game integration or room/ceiling claim','Seat contact/load relationships geometric only, not structural engineering or actor-rig validation','Collision solids are separate numeric proposals; do not use a single basin/canopy hull'],'hashes':{'blend_sha256':sha(blend),'glb_sha256':sha(glb)}}
  (ROOT/(cid+'.manifest.json')).write_text(json.dumps(meta,indent=2)+'\n');records.append(meta);collision_records[cid]={'status':'Numeric simplified collision proposal; pending engine adoption','parts':coll}
 (ROOT/'collision_proposals.json').write_text(json.dumps(collision_records,indent=2)+'\n')
 manifest={'family':'AST-BOT planted-seat architecture','unique_assets':3,'assets':records,'reference_pixels_inspected':json.loads((CAT/'batches/batch04/reference_manifest.json').read_text()),'shared_datums':{'soil_z_m':SOIL,'seat_z_m':SEAT,'floor_z_m':0},'assembly_instances':[{'asset_id':'AST-BOT-004','translation_m':[0,0,0],'rotation_z_degrees':0},{'asset_id':'AST-BOT-005','translation_m':[2.4,0,0],'rotation_z_degrees':0},{'asset_id':'AST-BOT-006','translation_m':[3.8,1.4,0],'rotation_z_degrees':90}],'scope':'Original independent component catalogue only','dependency_sha256':{str(p.relative_to(CAT)):sha(p) for p in [Path(__file__),CAT/'standards/materials.py',CAT/'standards/botanical_materials.py',CAT/'materials/material_manifest.json',CAT/'materials/botanical/manifest.json']}}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PLANTED_SEAT_COMPLETE',json.dumps({m['catalogue_id']:{'dimensions_m':m['dimensions_m'],'triangles':m['triangles']} for m in records}))
if __name__=='__main__':main()
