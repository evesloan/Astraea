"""Early editable section study. Source only; never exports a second Game floor.
Load retained equipment source and original context; save a separate proposal .blend.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib,resource
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];D=R.parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');assert str(R)=='/workspace/scratch/375c2e438292/engineering-dense-bays/sectional-proposal'
def cv(p):return Vector((p[0],-p[2],p[1]))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
S=json.loads((R/'source/section_plan.json').read_text());original=D/'source/AST-ENG-008_dense_bays.blend';pins={str(p):sha(p) for p in [original,D/'exports/AST-ENG-008_dense_bays.glb',C/'assets/secondary_engineering_section/exports/AST-ENG-008.glb',D.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb']}
bpy.ops.wm.open_mainfile(filepath=str(original));scene=bpy.context.scene
# Source backing roots stay separate; hide superseded upper west furniture only in proposal copy.
for o in list(scene.objects):
 if o.get('assembly') in S['removed_upper_source_assemblies'] and o.type=='MESH':o.hide_render=True;o.hide_viewport=True;o['proposal_disposition']='Relocated or omitted in section study; original bytes preserved'
# Reuse the original authored drums, collars and upper receiving blocks on the new compact skid.
for j,(oldz,newx) in enumerate([(-404.15,24.30),(-403.38,25.20)]):
 T=Matrix.Translation(cv((newx-20.84,-.45,-405.91-oldz)))
 names=['FilterDrum'+str(j),'FilterBand'+str((j,6.42)),'FilterBand'+str((j,7.83)),'FilterUpperJunction'+str(j),'FilterRiser'+str(j),'FilterTop'+str(j)+'_gland','FilterTop'+str(j)+'_collar','FilterRiserEnd'+str(j)+'_gland','FilterRiserEnd'+str(j)+'_collar']
 for name in names:
  old=bpy.data.objects.get(name)
  if old is None:continue
  ob=old.copy();ob.data=old.data.copy();scene.collection.objects.link(ob);ob.parent=None;ob.matrix_world=T@old.matrix_world;ob.hide_render=False;ob.hide_viewport=False;ob.name='CELL_REUSE_'+name;ob['section_study']=True;ob['retained_donor_name']=name
 # Recreate moved port markers with actual moved receiver ownership.
 for base in ['FilterTop'+str(j),'FilterRiserEnd'+str(j)]:
  old=bpy.data.objects.get('PORT_'+base)
  if old:
   marker=old.copy();marker.data=None;scene.collection.objects.link(marker);marker.parent=None;marker.matrix_world=T@old.matrix_world;marker.name='PORT_CELL_'+base;marker['assembly']='CELL_MACHINE';marker['owner']='CELL_REUSE_'+str(old.get('owner',''));marker['proposal_relocated']=True
# Existing architectural envelopes and the original benchmark kit remain visible.
for p in [C/'assets/secondary_engineering_section/exports/AST-ENG-008.glb',D.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb']:bpy.ops.import_scene.gltf(filepath=str(p))
# Use exact role graphs, including the retained pressure-glass material.
mats={}
for m in bpy.data.materials:
 role=m.get('astraea_material_role')
 if role and role not in mats:mats[role]=m
for role in ['staff_floor']:
 if role not in mats:
  sys.path.insert(0,str(C/'standards'));import staff_materials
  mats.update({k:v for k,v in staff_materials.materials().items() if k not in mats})
glass=next((m for m in bpy.data.materials if m.name.startswith('ASTRAEA_bridge_pressure_glass')),None);assert glass is not None;mats['section_sealed_glass']=glass
new=[]
def make(name,vs,fs,role,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([cv(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);me.materials.append(mats[role]);o['section_proposal_only']=True;o['bay']='WORKBAY';o['kind']=kind;o['collision_contract']=('visual_only_glass' if kind=='glazing' else ('visual_only_stair_tread' if kind in ['stair_structure','stair_nosing'] else ('door_control_only' if kind=='real_door_control' else ('none' if kind in ['open_gate_proposal','lens','nosing_pigment'] else 'static_surface'))));o['not_runtime_floor']=kind.startswith('compiler_');o['floor_owner_proposal']='D02_secondary_engineering_floor revised, lower owner pending';new.append(o)
 uv=me.uv_layers.new(name='MetreScaled');tile=mats[role].get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/tile[0],q.dot(v)/tile[1])
 return o
for p in S['parts']:
 if 'bounds_xyz'in p:
  x,y,z,X,Y,Z=p['bounds_xyz'];vs=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 else:
  a,b=map(Vector,p['endpoints_xyz']);t=(b-a).normalized();u=t.cross(Vector((0,0,1))).normalized();v=t.cross(u);N=10;vs=[tuple(p0+(u*math.cos(i*2*math.pi/N)+v*math.sin(i*2*math.pi/N))*p['radius']) for p0 in [a,b] for i in range(N)];fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 if p['material_role']=='section_sealed_glass':
  b=p['bounds_xyz'];axis=min(range(3),key=lambda k:b[k+3]-b[k]);mid=(b[axis]+b[axis+3])/2
  if axis==0:vs=[(mid,b[1],b[2]),(mid,b[4],b[2]),(mid,b[4],b[5]),(mid,b[1],b[5])]
  else:vs=[(b[0],b[1],mid),(b[3],b[1],mid),(b[3],b[4],mid),(b[0],b[4],mid)]
  fs=[(0,1,2,3)]
  if p['kind']!='open_gate_proposal':
   marker=bpy.data.objects.new('DATUM_CONTACT_PROXY_'+p['name'],None);scene.collection.objects.link(marker);marker.location=cv([(b[i]+b[i+3])/2 for i in range(3)]);marker['kind']='glass_contact_proxy';marker['bounds_xyz']=b;marker['size_xyz']=[b[i+3]-b[i] for i in range(3)];marker['collision_owner']='new pane only';marker['material_unchanged']=True
 ob=make(p['name'],vs,fs,p['material_role'],p['kind'])
 if p['material_role']=='section_sealed_glass' and p['kind']!='open_gate_proposal':
  x,y,z,X,Y,Z=p['bounds_xyz'];pv=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)];pf=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
  proxy=make('CONTACT_PROXY_'+p['name'],pv,pf,'section_sealed_glass','glass_contact_proxy');proxy['collision_contract']='contact_only_glass_26mm';proxy['contact_only']=True;proxy['bounds_xyz']=p['bounds_xyz'];proxy.hide_render=True

 if p['name'].startswith(('CellProfile','CellStepped','CellYoke','CellCapAnchor')):
  m=ob.modifiers.new('Editable stepped-frame corner easing','BEVEL');m.width=.012;m.segments=1

# Short mechanical supports attach reused upper junctions to the new crossbeam, no floating endpoints.
for x in [24.30,25.20]:
 make('CellUpperJunctionStem'+str(x),[(x+dx,y,-405.91+dz) for y in [8.46,8.67] for dx,dz in [(-.022,-.022),(.022,-.022),(.022,.022),(-.022,.022)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'staff_zinc','machinery_support')
# Faithful inclined contact within this exact stair flight, following existing stair convention.
q=[(21.9,6,-405.1),(21.9,6,-403.9),(22.8,5.55,-403.9),(22.8,5.55,-405.1)];vs=q+[(x,y-.12,z) for x,y,z in q]
wedge=make('CONTACT_CellStairFlight',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'staff_zinc','stair_flight_contact');wedge['collision_contract']='stair_flight_contact';wedge['contact_only']=True;wedge.hide_render=True
marker=bpy.data.objects.new('DATUM_CELL_STAIR_FLIGHT',None);scene.collection.objects.link(marker);marker.location=cv((22.35,5.775,-404.5));marker['kind']='stair_flight_contact';marker['quad_xyz_flat']=[v for pt in q for v in pt];marker['thickness_m']=.12
# New source-bound door: canonical closed rest, later rendered in open inspection pose.
door_id='D02_secondary_engineering_workbay_cell_gate';pivot=cv((21.8675,6,-404.5));leafparts=[]
for ob in list(scene.objects):
 if ob.name=='CellDoorOpenLeaf' or ob.name.startswith('CellDoorLeafEdge') or ob.name=='CellDoorLeafTop':
  for v in ob.data.vertices:v.co+=cv((0,0,1.22))-pivot
  ob.location=pivot;ob['door_leaf_id']=door_id;ob['collision_contract']='moving_door_visual';leafparts.append(ob)
for name,pos,kind,extra in [
 ('DATUM_WORKBAY_CELL_GATE',[21.8675,6,-404.5],'door_rest',{'persistent_id':door_id,'travel_xyz':[0,0,-1.22],'aperture_z':[-405.1,-403.9],'clear_width':1.2,'closed_leaf_bounds_xyz':[21.84,6.03,-405.12,21.895,8.36,-403.88]}),
 ('TARGET_CELL_GATE_OUTSIDE',[21.764,7.10,-405.23],'door_control',{'owner':door_id,'approach_xyz':[20.85,6,-405.23]}),
 ('TARGET_CELL_GATE_INSIDE',[22.111,6.86,-403.78],'door_control',{'owner':door_id,'approach_xyz':[23.3,5.55,-404.5]}),
 ('DATUM_CELL_LIGHT',S['source_light']['position'],'fixture_exit',{'aim_xyz':S['source_light']['aim']}),
 ('DATUM_CELL_THRESHOLD_LIGHT',[22.025,8.285,-404.5],'fixture_exit',{'aim_xyz':[22.45,5.8,-404.5]})]:
 ob=bpy.data.objects.new(name,None);scene.collection.objects.link(ob);ob.location=cv(pos);ob['kind']=kind
 for key,value in extra.items():ob[key]=value
# Actual primary view: original rejected camera with all retained room walls/cap visible.
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
lights=[('DATUM_workbay_task',[27,9.145,-405],[26.5,7,-401.4],750,65),('LIGHT_PROPOSAL_north_services',[24.52,8.66,-408],[24.52,7.31,-408.58],420,68),('LIGHT_PROPOSAL_bench_task',[26.43,7.73,-401.45],[26.1,7.18,-401.35],35,55),('PROPOSAL_CellTask',S['source_light']['position'],S['source_light']['aim'],180,58),('PROPOSAL_CellThreshold',[22.025,8.285,-404.5],[22.45,5.8,-404.5],55,52)]
for name,pos,aim,power,cone in lights:
 d=bpy.data.lights.new(name+'_section_trial','SPOT');d.energy=power;d.spot_size=math.radians(cone*2);d.spot_blend=.6;d.shadow_soft_size=.075;o=bpy.data.objects.new(name+'_section_trial',d);scene.collection.objects.link(o);o.location=cv(pos);o.rotation_euler=(cv(aim)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('EXACT_ORDINARY_EYE');cam.sensor_fit='VERTICAL';cam.sensor_height=32;cam.lens=32/(2*math.tan(math.radians(36)));cam.clip_start=.05;cam.clip_end=100;o=bpy.data.objects.new('EXACT_ORDINARY_EYE',cam);scene.collection.objects.link(o);scene.camera=o;o.location=cv(S['ordinary_eye']);o.rotation_euler=(cv([29,S['ordinary_eye'][1],-405])-o.location).to_track_quat('-Z','Y').to_euler()
scene['scope']='Unadopted workbay sectional architecture source study with real proposed compiler-floor cut, not current Game';scene['D01_reserved_underside_y']=5.31;scene['runtime_adopted']=False
bpy.ops.file.pack_all();target=R/'source/AST-ENG-008_workbay_section.blend';assert not target.exists(),'Retain existing study before rebuild';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
# Package contains equipment/section only. Real floor ownership stays with compiler proposal.
sys.path.insert(0,str(R/'source'));from export_section_package import export_package
export_report=export_package(R,target,S['removed_upper_source_assemblies'])
for ob in leafparts:ob.location+=cv((0,0,-1.22))
scene.render.filepath=str(R/'views/workbay_exact_eye_section_refined.png');bpy.ops.render.render(write_still=True)
# Supplemental ordinary-height west-threshold view, explicitly not a substitute camera.
o.location=cv((20.77,7.65,-407.60));o.rotation_euler=(cv((23.1,6.45,-404.6))-o.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(R/'views/workbay_west_threshold_section_refined.png');bpy.ops.render.render(write_still=True)
for p,h in pins.items():assert sha(p)==h,p
record={'scope':scene['scope'],'source_sha256':sha(target),'inputs_unchanged':True,'input_hashes':pins,'plan_sha256':sha(R/'source/section_plan.json'),'new_architecture_meshes':len(new),'floor_cut_is_actual_in_preview':True,'runtime_compiler_changed':False,'primary_eye':S['ordinary_eye'],'vertical_fov':72,'same_exposure':0,'world_strength':0,'retained_room_walls_hidden':False,'lights':lights,'glass_reused_without_edit':glass.name,'five_physical_source_lights_only':True,'export_sha256':export_report['export_sha256'],'new_glazing_single_sheet_with_26mm_contact_proxy':True,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'not_proven':['actual Godot floor compilation/collision','all step capsule paths','lower maintenance access','loaded cart parking/portable-tool workflow','glazing/door interaction','D01 future room fit','visual approval']}
(R/'qa/section_refined_build.json').write_text(json.dumps(record,indent=2)+'\n');print('SECTION_STUDY_READY',record['source_sha256'],'PEAK_RSS_KIB',record['peak_rss_kib'])
