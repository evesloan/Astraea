"""Original Astraea aquatic coping and compact entry, script-assisted editable source.
Blender 4.3.2; metres/Z up. Coping seam origin and deck top Z0, dry -Y/wet +Y.
Run: blender -b --threads 2 --python assets/aquatic_edges/source/build_aquatic_edges.py
This is a component catalogue, not a district, water system, safety approval or game.
"""
import bpy, bmesh, math, json, hashlib, importlib.util, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]; CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('aquatic_materials',CAT/'standards/aquatic_materials.py')
mm=importlib.util.module_from_spec(spec);spec.loader.exec_module(mm)
MATS=mm.materials()
spec0=importlib.util.spec_from_file_location('base_materials',CAT/'standards/materials.py')
base=importlib.util.module_from_spec(spec0);spec0.loader.exec_module(base);MATS.update(base.materials())
PARTS=[]; JOINTS=[]; CONTACTS=[]; ASSET=''
UV='metric_material_uv'; TILE='aquatic_edge_tile'; METAL='aquatic_satin_alloy'; GRIP='aquatic_dark_grip'; IVORY='ivory_enamel'; WARM='warm_stone'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new_asset(ident):
 global ASSET,PARTS,JOINTS,CONTACTS
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 ASSET=ident;PARTS=[];JOINTS=[];CONTACTS=[]
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 sc['asset_scope']='Original aquatic leisure component; no game, water physics or safety certification'
 sc['authorship']='Intentionally authored script-assisted geometry; no literal hand-GUI modelling claim'

def uv_map(me,role):
 active=me.uv_layers.active or me.uv_layers.new(name=UV)
 for layer in list(me.uv_layers):
  if layer!=active:me.uv_layers.remove(layer)
 active.name=UV;active.active_render=True
 scale=MATS[role].get('meters_per_tile_uv',(.24,.24))
 if isinstance(scale,(int,float)):scale=(scale,scale)
 for p in me.polygons:
  ax=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=ax]
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co
   active.data[li].uv=(co[axes[0]]/scale[0],co[axes[1]]/scale[1])

def mesh(name,verts,faces,role,kind,bevel=0):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[role]);uv_map(me,role)
 ob['catalogue_id']=ASSET;ob['material_role']=role;ob['semantic_kind']=kind
 if bevel:
  mod=ob.modifiers.new('Editable restrained formed-edge bevel','BEVEL');mod.width=bevel;mod.segments=2;mod.limit_method='ANGLE'
  mod=ob.modifiers.new('Weighted face normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
 PARTS.append(ob);return ob

def coord(s,y,z,R=None):
 if R is None:return(s,y,z)
 a=s/R;return((R-y)*math.sin(a),R-(R-y)*math.cos(a),z)

def sweep(name,profile,start,end,role,kind,R=None,segments=None,bevel=0):
 n=segments or (max(1,math.ceil((end-start)/.06)) if R else 1);p=len(profile)
 v=[coord(start+(end-start)*i/n,y,z,R) for i in range(n+1) for y,z in profile]
 f=[tuple(reversed(range(p))),tuple(n*p+j for j in range(p))]
 for i in range(n):
  for j in range(p):f.append((i*p+j,i*p+(j+1)%p,(i+1)*p+(j+1)%p,(i+1)*p+j))
 return mesh(name,v,f,role,kind,bevel)

def rect(name,s0,s1,y0,y1,z0,z1,role,kind,R=None,bevel=0):
 return sweep(name,[(y0,z0),(y1,z0),(y1,z1),(y0,z1)],s0,s1,role,kind,R,bevel=bevel)

def tube(name,points,radius,role,kind,sides=12):
 ps=[Vector(p) for p in points];verts=[]
 for i,p in enumerate(ps):
  d=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized()
  ref=Vector((1,0,0)) if abs(d.x)<.8 else Vector((0,1,0))
  u=(ref-d*d.dot(ref)).normalized();v=d.cross(u).normalized()
  for j in range(sides):verts.append(tuple(p+radius*(u*math.cos(j*2*math.pi/sides)+v*math.sin(j*2*math.pi/sides))))
 faces=[tuple(reversed(range(sides))),tuple((len(ps)-1)*sides+j for j in range(sides))]
 for i in range(len(ps)-1):
  for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 ob=mesh(name,verts,faces,role,kind)
 for p in ob.data.polygons:
  if len(p.vertices)==4:p.use_smooth=True
 ob['centerline_m']=json.dumps(points);ob['radius_m']=radius;return ob

def fillet_poly(points,d=.07,n=5):
 ps=[Vector(p) for p in points];out=[tuple(ps[0])]
 for i in range(1,len(ps)-1):
  p=ps[i];a=p+(ps[i-1]-p).normalized()*min(d,(ps[i-1]-p).length*.33);b=p+(ps[i+1]-p).normalized()*min(d,(ps[i+1]-p).length*.33)
  out.append(tuple(a))
  for j in range(1,n+1):
   t=j/n;out.append(tuple((1-t)**2*a+2*(1-t)*t*p+t*t*b))
 out.append(tuple(ps[-1]));return out

def cylinder(name,center,radius,depth,role,kind,sides=16):
 x,y,z=center;return tube(name,[(x,y,z-depth/2),(x,y,z+depth/2)],radius,role,kind,sides)

def evaluated(ob):
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
 uv_map(me,ob['material_role']);return me

def bounds(obs):
 vs=[];tris=0
 for ob in obs:
  me=evaluated(ob);me.calc_loop_triangles();tris+=len(me.loop_triangles);vs += [ob.matrix_world@v.co for v in me.vertices];bpy.data.meshes.remove(me)
 lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
 return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[k]-lo[k] for k in range(3)],'triangles':tris}

def save_asset(ident,description,details,collision,derived=False):
 folder=ROOT/'derived' if derived else ROOT;folder.mkdir(exist_ok=True)
 data=bounds(PARTS);hostpads=[]
 for ob in PARTS:
  if ob['semantic_kind'] in ['deck_receiving_structure_anchor','upper_host_receiving_shelf_anchor','lower_host_floor_anchor']:
   bb=bounds([ob]);hostpads.append({'name':ob.name,'bounds_min_m':bb['min_m'],'bounds_max_m':bb['max_m'],'receiving_z_m':bb['min_m'][2],'rule':'Neutral inspection support may meet underside only; support ownership/anchorage remains a host proposal'})
 details['host_contact_pads']=hostpads
 sourceparts=[{'name':o.name,'material_role':o['material_role'],'semantic_kind':o['semantic_kind']} for o in PARTS]
 source=folder/(ident+'.blend');glb=folder/(ident+'.glb')
 bpy.context.scene['catalogue_id']=ident;bpy.context.scene['deck_surface_z_m']=0
 bpy.context.scene['reference_response']='Warm ivory formed pool edges, slender satin rails and orange/teal resort context from actual aquatic reference pixels; source architecture, population and pool physics not copied'
 bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
 groups={}
 for src in PARTS:
  me=evaluated(src);ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
 exports=[]
 for role,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=ident+'__'+role
  ob['catalogue_id']=ident;ob['material_role']=role;ob['semantic_parts']=json.dumps([o['name'] for o in sourceparts if o['material_role']==role]);exports.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in exports:ob.select_set(True)
 bpy.context.view_layer.objects.active=exports[0]
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 data.update({'catalogue_id':ident,'design':description,'authorship':'Original script-assisted intentional design, 2026-10-02','source':str(source.relative_to(ROOT)),'exchange':str(glb.relative_to(ROOT)),'generator':'source/build_aquatic_edges.py','units':'metres','source_axes':'Z up, dry/arrival side -Y; GLB standard Y-up conversion','pivot_m':[0,0,0],'source_parts':sourceparts,'source_object_count':len(sourceparts),'material_roles':sorted(groups),'material_count':len(groups),'role_consolidated_export_mesh_count':len(exports),'source_sha256':sha(source),'glb_sha256':sha(glb),'source_dependencies':['standards/aquatic_materials.py','standards/materials.py','materials/aquatic/','materials/ivory_enamel.png','materials/warm_stone.png'],'support_contacts':CONTACTS,'connections':JOINTS,'collision_proposal':ident+'.collision_proposal.json','export':'Evaluated meshes consolidated by material role; all active UV names normalized to metric_material_uv before joins; ordinary embedded color texture maps','limitations':['Proposed component interfaces only; no recovered engine, water physics, actor rigs, load or slip tests','Not an all-species fit, accessibility route or safety-code certification','QA floors/lights/cameras excluded from source and GLB'],'derived_same_profile_not_new_design':derived,**details})
 (folder/(ident+'.manifest.json')).write_text(json.dumps(data,indent=2)+'\n')
 (folder/(ident+'.collision_proposal.json')).write_text(json.dumps({'status':'PROPOSAL, not runtime-tested','coordinate_system':'source metres Z up','do_not_use_whole_assembly_convex_hull':True,'preserve_openings':['Every 22 mm drain slot and drain throat','Open stair underside and spaces between handrails and support posts'],'parts':collision,'limits':'Exact authored section hulls and narrow rail capsules need host-engine evaluation; no physics or actor test is asserted'},indent=2)+'\n')
 print('SAVED',ident,json.dumps({k:data[k] for k in ['dimensions_m','triangles','source_object_count','material_count']}));return data

COPING_PROFILE=[(-.16,0),(.105,0)]+[(.105+.055*math.cos(a),-.055+.055*math.sin(a)) for a in [math.pi/2-j*math.pi/8 for j in range(1,9)]]+[(-.16,-.11)]
BRACKET_PROFILE=[(-.54,-.08),(-.36,-.08),(-.36,-.19),(-.16,-.19),(-.16,-.11),(.105,-.11),(.105,-.148),(-.20,-.235),(-.54,-.235)]

def coping(ident,R=None):
 new_asset(ident);collision=[];length=1.2
 sweep('01_formed_bullnose_coping',COPING_PROFILE,0,length,WARM,'formed_closed_bullnose',R)
 rect('02_dry_apron',0,length,-.56,-.36,-.08,0,TILE,'flush_dry_deck_apron',R)
 # Drain walls, bearing ledges and a genuinely open downward outlet.
 for name,y0,y1 in [('dry',-.36,-.344),('wet',-.176,-.16)]:
  rect('10_drain_'+name+'_wall',0,length,y0,y1,-.165,-.020,IVORY,'closed_drain_trough_wall',R)
  rect('11_grate_'+name+'_bearing',0,length,y0 if name=='wet' else y0,y1 if name=='dry' else y1,-.027,-.020,METAL,'continuous_slat_bearing_ledge',R)
 for i,(s0,s1,y0,y1) in enumerate([(0,.54,-.36,-.16),(.66,1.2,-.36,-.16),(.54,.66,-.36,-.30),(.54,.66,-.22,-.16)]):
  rect(f'12_open_outlet_trough_floor_{i+1}',s0,s1,y0,y1,-.165,-.145,GRIP,'drain_floor_leaving_120x80_open_throat',R)
 # Outlet throat is four separate closed wall strips around an open rectangle.
 for i,(s0,s1,y0,y1) in enumerate([(.53,.54,-.31,-.21),(.66,.67,-.31,-.21),(.54,.66,-.31,-.30),(.54,.66,-.22,-.21)]):
  rect(f'13_open_drain_throat_wall_{i+1}',s0,s1,y0,y1,-.23,-.145,IVORY,'open_underside_drain_throat_wall',R)
 for i in range(20):
  a=i*.06+.011;b=a+.038
  rect(f'20_removable_grate_slat_{i+1:02d}',a,b,-.35,-.17,-.02,0,METAL,'transverse_grate_slat_22mm_slot',R,bevel=.0012)
  collision.append({'name':f'grate_slat_{i+1:02d}','shape':'swept_box','along_seam_m':[a,b],'profile_yz_m':[[-.35,-.02],[-.17,-.02],[-.17,0],[-.35,0]],'radius_m':R})
  CONTACTS.append({'part':f'20_removable_grate_slat_{i+1:02d}','parent':'both continuous grate bearings','top_m':0,'underside_m':-.02,'bearing_top_m':-.02,'nominal_face_gap_m':0,'bearing_overlap_y_m':.006,'slot_after_m':.022})
 for i,s in enumerate([.12,1.08]):
  sweep(f'30_shaped_cantilever_bearing_{i+1}',BRACKET_PROFILE,s-.035,s+.035,IVORY,'closed_formed_under_edge_bracket',R,bevel=.003)
  for j,(y0,y1) in enumerate([(-.34,-.305),(-.215,-.18)]):rect(f'31_trough_spacer_{i+1}_{j+1}',s-.031,s+.031,y0,y1,-.194,-.157,GRIP,'trough_bearing_pad',R,bevel=.001)
  rect(f'32_host_deck_anchor_plate_{i+1}',s-.065,s+.065,-.525,-.405,-.25,-.233,METAL,'deck_receiving_structure_anchor',R,bevel=.004)
  for j,yy in enumerate([-.50,-.43]):
   p=coord(s,yy,-.232,R);cylinder(f'33_anchor_head_{i+1}_{j+1}',p,.009,.009,METAL,'visible_host_anchor_head',12)
  CONTACTS.extend([{'part':f'30_shaped_cantilever_bearing_{i+1}','parent':'02_dry_apron','contact_z_m':-.08,'nominal_face_gap_m':0,'interface_width_m':.07}, {'part':f'30_shaped_cantilever_bearing_{i+1}','parent':'01_formed_bullnose_coping','contact_z_m':-.11,'nominal_face_gap_m':0,'interface_width_m':.07}, {'part':f'31_trough_spacers_{i+1}','parent':'trough floor and bracket','overlap_with_trough_m':.008,'overlap_with_bracket_m':.004}, {'part':f'32_host_deck_anchor_plate_{i+1}','parent':'bracket','overlap_z_m':.002,'host_receiving_datum_z_m':-.25}])
 # The coupling tongues are below the dry apron. They overlap the next module's
 # matching open underside and are kept out of the drain channel and wet nose.
 for j,yy in enumerate([-.50,-.41]):
  rect(f'40_end_alignment_tongue_{j+1}',1.165,1.223,yy-.009,yy+.009,-.097,-.080,METAL,'underside_alignment_tongue',R,bevel=.001)
 end=coord(length,0,0,R);yaw=math.degrees(length/R) if R else 0
 JOINTS.extend([{'name':'start_profile_seam','position_m':[0,0,0],'tangent_yaw_degrees':0,'mate':'previous module end seam','nominal_surface_gap_m':0}, {'name':'end_profile_seam','position_m':end,'tangent_yaw_degrees':yaw,'mate':'next module start profile','nominal_surface_gap_m':0,'tongue_extension_m':.023,'tongue_receiver':'next apron underside Z−0.08; no above-deck protrusion'}])
 collision[:0]=[{'name':'formed_coping','shape':'swept_profile','profile_yz_m':COPING_PROFILE,'along_seam_m':[0,1.2],'radius_m':R},{'name':'dry_apron','shape':'swept_box','profile_yz_m':[[-.56,-.08],[-.36,-.08],[-.36,0],[-.56,0]],'along_seam_m':[0,1.2],'radius_m':R}]
 collision.append({'name':'structure_and_trough','shape':'per_semantic_closed_part_hulls','source_prefixes':['10_','11_','12_','13_','30_','31_','32_'],'rule':'One hull per named simple solid; retain outlet hole and drain channel. Subdivide curved parts along 60 mm arc chords.'})
 return save_asset(ident,'Compatible curved coping and slotted drain' if R else 'Straight formed coping and slotted drain',{'pivot_meaning':'First seam at deck surface, tangent +X, dry -Y/wet +Y','profile_dry_wet_limits_y_m':[-.56,.16],'deck_datum_z_m':0,'seam_pitch_m':1.2,'curve_centerline_radius_m':R,'curve_angle_degrees':yaw,'curve_center_m':[0,R,0] if R else None,'profile_yz_m':COPING_PROFILE,'bullnose_radius_m':.055,'drain_clear_width_m':.168,'grate_slat_count':20,'slot_clear_length_along_centerline_m':.022,'grate_slat_pitch_m':.06,'open_outlet_m':[.12,.08],'support_anchor_datum_z_m':-.25,'profile_dimension_excludes_below_deck_alignment_tongues':True,'connection_recipe':'Place next origin at current end_profile_seam and rotate about Z by end tangent yaw. Deck upper surfaces and wet nose meet at zero nominal gap. Below-deck tongues overlap only dry apron underside. See terminal derivative for chain closure.'},collision)

def terminal(start=False):
 ident='AST-AQU-003_START' if start else 'AST-AQU-003_END';new_asset(ident)
 # A thin continuation of the exact shared cross-section, plus channel end wall.
 sweep('01_same_profile_terminal_bullnose',COPING_PROFILE,0,.028,WARM,'same_profile_terminal')
 rect('02_same_profile_terminal_apron',0,.028,-.56,-.36,-.08,0,TILE,'same_profile_terminal')
 rect('03_closed_drain_end_wall',0,.020,-.36,-.16,-.165,-.008,IVORY,'closed_drain_terminal_wall')
 rect('04_terminal_grate_crossbar',0,.028,-.35,-.17,-.020,0,METAL,'end_grate_crossbar')
 # Flush strip hides the construction thickness while keeping the 55 mm wet nose.
 sweep('05_terminal_under_edge_return',[(-.56,-.08),(-.36,-.08),(-.36,-.165),(-.16,-.165),(-.16,-.11),(.105,-.11),(.105,-.19),(-.56,-.19)],.016,.028,IVORY,'closed_shaped_end_fascia')
 JOINTS.append({'name':'closure_seam','position_m':[0,0,0],'tangent_yaw_degrees':0,'mate':'straight or curved end_profile_seam after matching tangent transform','nominal_surface_gap_m':0,'alignment_tongue_note':'The final 23 mm tongue extension is contained by this 28 mm closure; no below-deck tongue protrudes past the return'})
 if start:
  for ob in PARTS:
   for v in ob.data.vertices:v.co.x=-v.co.x
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();uv_map(ob.data,ob['material_role'])
  JOINTS[0]['mate']='straight or curved start_profile_seam; this start derivative is already mirrored, so do not add negative scale'
 save_asset(ident,'28 mm same-profile closed terminal recipe',{'pivot_meaning':'Closure start seam at deck surface','design_count':0,'terminal_direction':'negative local X' if start else 'positive local X','same_profile_parent_ids':['AST-AQU-003','AST-AQU-004'],'assembly_rule':'At final seam, use seam position and tangent rotation. At a start seam, mirror terminal across local X. The 23 mm below-apron alignment tongue ends inside the 28 mm closure; no cutting or omitted parts are required.'},[{'name':'terminal_solids','shape':'one_convex_hull_per_semantic_part','preserve_drain_before_terminal':True}],True)

def tread_profile(y0,y1,top):
 # Recess is real: dark grip infill sits flush in a 4 mm formed rebate.
 p=[(y0,top),(y1-.115,top),(y1-.115,top-.004),(y1-.06,top-.004),(y1-.06,top),(y1-.025,top)]
 p += [(y1-.025+.025*math.cos(a),top-.025+.025*math.sin(a)) for a in [math.pi/2-j*math.pi/8 for j in range(1,9)]]
 return p+[(y0,top-.05)]

def stairs():
 ident='AST-AQU-005';new_asset(ident);collision=[]
 # Arrival and landing, individually editable architectural surfaces.
 rect('01_upper_arrival_tile',-.7,.7,-.64,.006,-.070,0,WARM,'dry_arrival_landing',bevel=.006)
 rect('02_upper_arrival_tray',-.68,.68,-.625,.012,-.12,-.068,IVORY,'upper_landing_closed_tray',bevel=.006)
 rect('03_lower_landing_tile',-.7,.7,.952,1.58,-.775,-.72,WARM,'lower_landing_surface',bevel=.007)
 rect('04_lower_landing_tray',-.68,.68,.952,1.565,-.825,-.771,IVORY,'lower_landing_closed_tray',bevel=.007)
 for i in range(3):
  y0=i*.32-.012;y1=(i+1)*.32+.010;z=-.18*(i+1)
  sweep(f'10_step_{i+1}_formed_tread',tread_profile(y0,y1,z),-.7,.7,WARM,'rounded_tread_with_true_grip_rebate')
  rect(f'11_step_{i+1}_flush_grip',-.675,.675,y1-.114,y1-.061,z-.004,z,GRIP,'flush_dark_grip_insert_in_recess',bevel=.001)
  rect(f'12_step_{i+1}_undertray',-.68,.68,y0+.01,y1-.035,z-.095,z-.048,IVORY,'closed_tread_load_tray',bevel=.005)
  collision.append({'name':f'tread_{i+1}','shape':'box','min_m':[-.7,y0,z-.095],'max_m':[.7,y1,z],'grip_insert_top_z_m':z})
 for i in range(4):
  yy=i*.32;upper=-i*.18;lower=-(i+1)*.18
  # Recessed riser below each upper nose joins both treads, not floating cladding.
  rect(f'20_riser_{i+1}_formed_fascia',-.675,.675,yy-.024,yy+.015,lower-.008,upper-.028,IVORY,'closed_riser_joining_adjacent_trays',bevel=.003)
  CONTACTS.append({'part':f'20_riser_{i+1}','parents':['upper tread/tray','lower tread or landing'],'lower_surface_overlap_z_m':.008,'upper_tread_overlap_z_m':.022,'front_clear_tread_depth_m':.281})
  collision.append({'name':f'riser_{i+1}','shape':'box','min_m':[-.675,yy-.024,lower-.008],'max_m':[.675,yy+.015,upper-.028]})
 # Two tapered closed stringers follow the tread underside and land on bolted pads.
 profile=[(-.54,-.119),(-.05,-.119),(.015,-.225),(.285,-.225),(.320,-.405),(.605,-.405),(.640,-.585),(.925,-.585),(.960,-.778),(1.43,-.778),(1.43,-.827),(1.00,-.827),(-.16,-.265),(-.54,-.185)]
 for side,xx in [('left',-.53),('right',.53)]:
  sweep('30_'+side+'_tapered_stringer',profile,xx-.038,xx+.038,IVORY,'closed_stepped_top_sloping_underside_stringer',bevel=.004)
  for i,yy in enumerate([.15,.47,.79]):
   top=-.18*(i+1)-.088
   # Short saddles resolve the intentional clearance between step trays and stringers.
   rect(f'31_{side}_step_saddle_{i+1}',xx-.045,xx+.045,yy-.09,yy+.09,top-.043,top+.006,METAL,'tread_to_stringer_bearing_saddle',bevel=.002)
   CONTACTS.append({'part':f'31_{side}_step_saddle_{i+1}','parents':[f'12_step_{i+1}_undertray',f'30_{side}_tapered_stringer'],'tray_overlap_z_m':.013,'stringer_overlap_z_m':.049,'fit_note':'Stringer plateaus overlap the full 47 mm tread-tray thickness; small visible side saddles share the load connection'})
  rect('32_'+side+'_upper_host_anchor',xx-.082,xx+.082,-.565,-.405,-.18,-.163,METAL,'upper_host_receiving_shelf_anchor',bevel=.004)
  rect('33_'+side+'_lower_floor_anchor',xx-.095,xx+.095,1.26,1.49,-.86,-.825,METAL,'lower_host_floor_anchor',bevel=.005)
  for j,yy in enumerate([1.30,1.45]):cylinder(f'34_{side}_lower_anchor_head_{j+1}',(xx,yy,-.82),.012,.012,METAL,'lower_host_bolt_head',12)
  CONTACTS.extend([{'part':'32_'+side+'_upper_host_anchor','parent':'upper stringer','overlap_z_m':.017,'host_receiving_z_m':-.18},{'part':'33_'+side+'_lower_floor_anchor','parent':'lower stringer and landing tray','overlap_z_m':.002,'host_receiving_z_m':-.86}])
 # Thin formed side closures follow the stair edge while preserving the open underside.
 sideprofile=[(-.64,-.069),(.004,-.069),(.004,-.181),(.324,-.181),(.324,-.361),(.644,-.361),(.644,-.541),(.964,-.541),(.964,-.722),(1.575,-.722),(1.575,-.82),(1.005,-.82),(.952,-.78),(-.008,-.24),(-.64,-.122)]
 for side,a,b in [('left',-.698,-.678),('right',.678,.698)]:
  sweep('35_'+side+'_formed_side_closure',sideprofile,a,b,TILE,'thin_stepped_side_closure_open_below',bevel=.001)
  CONTACTS.append({'part':'35_'+side+'_formed_side_closure','parents':['tread tray edges','upper and lower landing trays'],'transverse_overlap_m':.002,'construction':'Stepped formed cheek closes exposed tray ends but does not bridge the open underside'})
 # Continuous rounded rail with return ends and one narrow mid support each side.
 railpts=[]
 for side,xx in [('left',-.612),('right',.612)]:
  points=[(xx,-.48,.007),(xx,-.48,.80),(xx,-.38,.90),(xx,-.14,.90),(xx,.04,.865),(xx,1.05,.165),(xx,1.23,.165),(xx,1.34,.055),(xx,1.34,-.713)]
  smooth=fillet_poly(points,.07,5);tube('40_'+side+'_continuous_return_handrail',smooth,.022,METAL,'closed_continuous_44mm_handrail')
  midz=.865+(.46-.04)*(.165-.865)/(1.05-.04)
  tube('41_'+side+'_mid_rail_stanchion',[(xx,.46,-.354),(xx,.46,midz)],.017,METAL,'rail_stanchion_joined_to_centerline')
  for name,yy,z in [('upper',-.48,0),('mid',.46,-.36),('lower',1.34,-.72)]:
   cylinder('42_'+side+'_'+name+'_anchor_flange',(xx,yy,z+.004),.064,.010,METAL,'anchored_rail_flange')
   for j,dx in enumerate([-.043,.043]):cylinder(f'43_{side}_{name}_anchor_head_{j+1}',(xx+dx,yy,z+.012),.006,.008,METAL,'rail_flange_anchor_head',10)
   CONTACTS.append({'part':'42_'+side+'_'+name+'_anchor_flange','parent':name+' landing/tread','surface_z_m':z,'flange_bottom_z_m':z-.001,'surface_overlap_m':.001,'rail_end_overlap_m':.002 if name!='mid' else .003})
  railpts.append({'side':side,'diameter_m':.044,'centerline_m':smooth})
  CONTACTS.append({'part':'41_'+side+'_mid_rail_stanchion','parent':'continuous handrail','centerline_meeting_m':[xx,.46,midz],'radial_overlap_m':.039})
  collision.append({'name':side+'_handrail','shape':'capsules_per_centerline_segment','centerline_m':smooth,'radius_m':.022,'do_not_fill_hand_space':True})
  collision.append({'name':side+'_mid_stanchion','shape':'capsule','endpoints_m':[[xx,.46,-.354],[xx,.46,midz]],'radius_m':.017})
 # Collision proposals preserve the open underside and hand spaces.
 collision.extend([{'name':'upper_arrival','shape':'box','min_m':[-.7,-.64,-.12],'max_m':[.7,.006,0]}, {'name':'lower_landing','shape':'box','min_m':[-.7,.952,-.825],'max_m':[.7,1.58,-.72]}, {'name':'stringers_and_anchors','shape':'per_part_convex_decomposition','source_prefixes':['30_','31_','32_','33_'],'preserve_open_underside':True}])
 JOINTS.extend([{'name':'dry_deck_arrival','surface_z_m':0,'edge_y_m':-.64,'width_m':1.4,'receiving_support_z_m':-.18,'host_note':'Host dry deck must meet the rear arrival edge and provide the two upper bearing shelves; do not overlap the coping drain'}, {'name':'lower_pool_floor_landing','surface_z_m':-.72,'toe_y_m':1.58,'width_m':1.4,'receiving_support_z_m':-.86,'host_note':'Host floor/curb must accept lower pads and meet landing top or provide a 140 mm support recess'}])
 return save_asset(ident,'Four-riser compact pool entry with returned rails',{'pivot_meaning':'Top deck level at first descent line; arrival -Y, descent +Y','level_change_m':.72,'riser_count':4,'riser_height_m':.18,'tread_going_m':.32,'clear_tread_going_between_riser_faces_m':.281,'tread_width_m':1.4,'dry_arrival_length_m':.64,'lower_landing_length_m':.62,'lower_landing_top_z_m':-.72,'rail_diameter_m':.044,'clear_between_rails_m':1.18,'rail_top_height_proposal_m':.90,'rail_centerlines':railpts,'top_anchor_receiving_z_m':-.18,'bottom_anchor_receiving_z_m':-.86,'intended_fit':'Compact upright/humanoid-scale entry proposal. Not a ladder, accessible route, all-species fixture or code-certified assembly. Four 180 mm descents including lower landing; three intervening 320 mm treads. Rails continue over arrival and landing and return to anchored flanges. Nominal host dry-deck opening 1.40 m, matching outer closure planes X±0.70; construction tolerance is a host-adoption decision, evaluate species foot/hand envelopes separately.','coping_relationship':'Use coping chains outside the 1.40 m nominal entry opening. Place straight dry rear apron on host deck beside arrival; terminate both drain runs with same-profile closure before stair opening. No automatic coping-to-stair watertight seal or support is asserted.'},collision)

if __name__=='__main__':
 if '--only-entry' in sys.argv:stairs()
 else:coping('AST-AQU-003');coping('AST-AQU-004',3.0);terminal();terminal(True);stairs()
 print('AQUATIC_EDGES_BUILD_COMPLETE')
