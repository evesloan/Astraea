"""Bounded proposal only. Reads retained geometry; writes exclusively beside this file.
No Blender/Godot engine, rendering, export, repository edits, commit or network.
"""
import sys, ast, json, math, hashlib, importlib.util, datetime
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, Point
from shapely import constrained_delaunay_triangles
OUT=Path(__file__).resolve().parent
assert OUT==Path('/workspace/scratch/375c2e438292/pool-architectural-composition/fixture_crosswash_study002')
G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
P=C/'assets/grand_pool_first_pass';A=P/'architectural_composition';S=A/'export_tooling003';TOL=5e-5
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
def read(p):
 pins[str(p)]=sha(p);return json.loads(p.read_text())
def save(name,d):
 (OUT/name).write_text(json.dumps(d,indent=2)+'\n')
helper=P/'finish_envelope/stock/geometry.py';pins[str(helper)]=sha(helper)
sp=importlib.util.spec_from_file_location('retained_geometry',helper);geo=importlib.util.module_from_spec(sp);sp.loader.exec_module(geo)
for name in dir(geo):
 if not name.startswith('_'):globals()[name]=getattr(geo,name)
helper=P/'finish_envelope/qa/pure_geometry/review_finish.py';pins[str(helper)]=sha(helper)
wanted={'record','triang_face','rayhits','surface_points','on_surface','strict_inside','contact_pair'}
funcs=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in wanted]
assert len(funcs)==len(wanted);exec(compile(ast.Module(body=funcs,type_ignores=[]),str(helper),'exec'))
section=read(G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json');first=read(G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json');finish=read(G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json');arch=read(G/'data/architecture/GRAND_POOL_ARCHITECTURE_RUNTIME.json')
plan=read(A/'source_tooling003/BLOCKIN_PLAN_003.json');actual=read(A/'source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json')
assert len(plan['parts'])==len(actual['parts'])==451 and len(actual['plants'])==12
assert finish['logical_furnishing_count']==arch['preserved_logical_furnishing_count']==126
assert len(section['fixtures'])+len(finish['fixtures'])==39 and first['placements'] and len(arch['fixtures'])==0
for name in ['grand_pool_finish.gd','grand_pool_architecture.gd','lighting_budget.gd','ship.gd']:pins[str(G/'scripts'/name)]=sha(G/'scripts'/name)
profiles=read(G/'data/lighting_profiles.json')
images=read(OUT.parent/'native_capture_run001/CAPTURE_RECEIPT.json')
for r in images:
 if r['effects']==False:
  image_path=Path(r['file']);assert sha(image_path)==r['sha256'];pins[str(image_path)]=sha(image_path)
source=[];source_by={};snapshot_evidence=[]
for kind in ['loggia','focal_end','roof']:
 snap=read(S/(kind+'_snapshot.json'));eq=read(S/(kind+'_EQUIVALENCE.json'))
 assert eq['status']=='PASS' and sha(S/(kind+'_snapshot.json'))==eq['snapshot_sha256']
 assert sha(Path(snap['source']))==snap['source_sha256']==eq['source_sha256'];pins[snap['source']]=snap['source_sha256']
 assert arch['models'][kind]['source_sha256']==snap['source_sha256']
 snapshot_evidence.append(dict(kind=kind,source=snap['source'],source_sha256=snap['source_sha256'],snapshot_sha256=sha(S/(kind+'_snapshot.json')),equivalence_status=eq['status']))
 for o in snap['objects']:
  if o['type']!='MESH':continue
  rec=record(o['name'],[v for t in o['positions']for v in t],o['positions'],meta=o)
  source.append(rec);source_by[rec['name']]=rec
assert len(source)==451
rooted=read(A/'source_tooling003/ROOTED_SUPPORT_003.json')
assert rooted['status']=='PASS_POSITIVE_AREA_ROOTED_CONTACT_GRAPH' and not rooted['unrooted'] and rooted['actual_plan_sha256']==sha(A/'source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json')
# Retained physical-fixture lineage is read; no import of the authoring script's main body.
lineage=read(S/'envelope_snapshot001.json');plan_helper=P/'finish_envelope/source/plan_finish_envelope.py';pins[str(plan_helper)]=sha(plan_helper)
assert sha(Path(lineage['source']))==lineage['source_sha256'];pins[lineage['source']]=lineage['source_sha256']
parts=[];fixtures=[]
def add(name,vertices,faces,role,support,witnesses=None,notes=''):
 row=dict(name=name,world_vertices=[[float(x)for x in v]for v in vertices],faces=[list(f)for f in faces],material_role=role,parent_design_id='AST-AQU-016',support=support,contact_witnesses=witnesses or [],collision_contract='concave_static_surface',notes=notes)
 parts.append(row);return row
funcs=[n for n in ast.parse(plan_helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in {'native_box','beam','fixture'}]
assert len(funcs)==3;exec(compile(ast.Module(body=funcs,type_ignores=[]),str(plan_helper),'exec'))
def prepare(rec):
 rec['ta']=np.asarray(rec['triangles']);rec['tmin']=rec['ta'].min(axis=1);rec['tmax']=rec['ta'].max(axis=1);return rec
source=[prepare(o)for o in source]
def point_record(point,part):
 q=np.array(point);p=source_by[part];out=[]
 for i,t in enumerate(p['ta']):
  b=np.array(t);e=b[1]-b[0];f=b[2]-b[0];n=np.cross(e,f);n/=np.linalg.norm(n);dist=float((q-b[0])@n)
  if abs(dist)>1e-7:continue
  uv=np.linalg.lstsq(np.stack([e,f],axis=1),q-b[0],rcond=None)[0];bc=[1-float(sum(uv)),float(uv[0]),float(uv[1])]
  if min(bc)>=-1e-7:out.append(dict(source_part=part,source_triangle_index=i,source_triangle_xyz=t.tolist(),point_xyz=q.tolist(),barycentric=bc,plane_error_m=abs(dist),triangle_normal_xyz=n.tolist()))
 assert out,(point,part);return out
# Center contacts stay wholly inside one planar underside quad, away from every seam.
for tag,host,receiver,tri_index,anchor_x,target_y in [
 ('ArchTimber_ForeL','LOG_Fore_Vault_Roof_02','LOG_Fore_Vault_LegR',4,-51.5,47.925),
 ('ArchTimber_ForeR','LOG_Fore_Vault_Roof_13','LOG_Fore_Vault_LegL',4,-51.5,47.925),
 ('ArchFocal_Crown','FOCAL_Vault_Roof_08','FOCAL_OrbitalSunRelief',4,-31.52,49.15)]:
 hostrec=source_by[host];t=hostrec['ta'][tri_index]
 n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)
 if n[1]>0:n=-n
 if 'Timber' in tag:
  # Lower roof vertices from triangle4 span the entire support quad.
  zz=float((t[:,2].min()+t[:,2].max())*.5);y=float(t[0,1]-(n[0]*(anchor_x-t[0,0])+n[2]*(zz-t[0,2]))/n[1]);anchor=np.array([anchor_x,y,zz]);p=anchor+n*.42
  rr=source_by[receiver];zz=float(rr['ta'][:,:,2].max()if receiver.endswith('LegL')else rr['ta'][:,:,2].min());target=np.array([anchor_x,target_y,zz])
  # A real across-loggia optical throw, not a ranking-only range increase.
  face_vertices=rr['ta'].reshape(-1,3);face_vertices=face_vertices[np.abs(face_vertices[:,2]-zz)<1e-6]
  max_receiver_distance=max(float(np.linalg.norm(q-p))for q in face_vertices)
  reach=math.ceil((max_receiver_distance+.25)*10)/10;energy=.65
  axis=(target-p)/np.linalg.norm(target-p)
  max_receiver_angle=max(math.degrees(math.acos(float(np.clip(axis@((q-p)/np.linalg.norm(q-p)),-1,1))))for q in face_vertices)
  cone=math.ceil(max_receiver_angle+1.0)

 else:
  zz=-462.25;y=float(t[0,1]-(n[0]*(anchor_x-t[0,0])+n[2]*(zz-t[0,2]))/n[1]);anchor=np.array([anchor_x,y,zz]);p=anchor+n*.36
  target=np.array([-31,49.15,source_by[receiver]['ta'][:,:,2].max()]);energy=.45;reach=6.0;cone=62
 fixture(tag,p,target,anchor,n,host,.52,.32,reach,energy)
 f=fixtures[-1];f['suggested_spot_angle_degrees']=cone;f['profile']='guest_lounge';f['parent_design_id']='AST-AQU-016';f['proposal_only']=True
 f['visibility_sample_xyz']=(target-np.array(f['direction_xyz'])*.02).tolist();f['visibility_sample_scope']='20mm lightward of exact physical receiver, using the retained adapter convention.'
 f['receiver_source_part']=receiver;f['source_support_anchor_xyz']=anchor.tolist();f['source_support_normal_xyz']=n.tolist();f['support_contact']=point_record(anchor,host);f['receiver_contact']=point_record(target,receiver)
 f['retained_lineage']='WetRestWash_444 backplate .38x.40x.07m, arm .11x.10m, housing .52x.32x.22m, lens .42x.25x.020m; same retained fixture function, new orientation and arm length only.'
 f['native_acceptance']='NOT_RUN: pure cross-wash alternative only; source authoring and native trial pending.'
 if 'Timber' in tag:
  f['range_derivation']={'farthest_actual_receiver_vertex_m':max_receiver_distance,'physical_throw_margin_m':.25,'rounded_up_to_m':.1,'maximum_receiver_half_angle_deg':max_receiver_angle,'cone_margin_deg':1.0,'rationale':'Opposite timber return receives the beam across the actual loggia width; this changes source geometry and direction.'}
add=geo.add  # Restore vector addition after the retained authoring functions finish.
NEW=[prepare(record(p['name'],p['world_vertices'],[t for face in p['faces']for t in triang_face(p['world_vertices'],face)],meta=p))for p in parts];NM={p['name']:p for p in NEW}
# Read currently installed native GLB triangle geometry, including all plants/furnishings.
cache={};native=[]
def glb(path):
 if path not in cache:pins[str(path)]=sha(path);cache[path]=geo.read_glb(path)
 return cache[path]
def add_native(file,label,pos=None,yaw=0):
 d=glb(G/'assets/models'/file)
 for m in d['meshes']:
  tri=np.array(m['triangles']);v=np.array(m['vertices'])
  if pos is not None:
   c,s=math.cos(yaw),math.sin(yaw);R=np.array([[c,0,s],[0,1,0],[-s,0,c]]);tri=tri@R.T+pos;v=v@R.T+pos
  rec=prepare(record(label+'::'+m['name'],v.tolist(),tri.tolist(),native_file=file,native_mesh=m['name'],native_primitive=m['primitive']))
  native.append(rec)
add_native('AST-AQU-016.glb','GrandPoolConnectedArchitecture')
for d in [finish,arch]:
 for e in d['assemblies']:add_native(e['model_file'],e['name'])
for e in first['placements']+finish['placements']+arch['plants']:add_native(e['model_file'],e['name'],e['position_xyz'],e['yaw_radians'])
print('Native input loaded',len(native),'mesh instances',sum(len(p['triangles'])for p in native),'triangles',flush=True)
# Pin the relevant installed models against their contracts.
for d in [first,finish,arch]:
 for v in d['models'].values():assert sha(G/'assets/models'/v['file'])==v['sha256'],v['file']
checks=[];issues=[]
for f in fixtures:
 name=f['name'].removeprefix('DATUM_finish_light_');p=np.array(f['position_xyz']);direction=np.array(f['direction_xyz']);target=np.array(f['receiver_xyz']);host=f['host']
 back=NM[name+'_SourceBackplate'];anchor=np.array(f['source_support_anchor_xyz']);normal=np.array(f['source_support_normal_xyz'])
 face=[v for v in back['vertices'] if abs((np.array(v)-anchor)@normal)<1e-7]
 assert len(face)==4
 contacts=[point_record(v,host)for v in face]
 support=[]
 for part in [x for x in NEW if x['name'].startswith(name+'_')]:
  support_host=part['meta']['support'];other=source_by.get(support_host,NM.get(support_host));res=contact_pair(part,other)
  support.append(dict(part=part['name'],support=support_host,**res))
  if not res['touch']:issues.append(['missing_support',part['name']])
 # The marker must exit immediately into free space; lens is behind it.
 exit_hits=rayhits(p,p+direction*.06,native+NEW)
 lens_front=p-direction*.02;exit_from_lens=rayhits(lens_front+direction*.0001,p+direction*.06,native+NEW)
 hits=rayhits(p,target+direction*.001,native+NEW)
 firsthit=hits[0]if hits else None
 if not firsthit or abs(firsthit['distance_m']-np.linalg.norm(target-p))>TOL:issues.append(['receiver_not_first_hit',name,firsthit])
 sample_hits=rayhits(p,f['visibility_sample_xyz'],native+NEW)
 if exit_hits or exit_from_lens or sample_hits:issues.append(['blocked_light_ray',name,exit_hits,exit_from_lens,sample_hits])
 native_triangle=None
 if firsthit:
  hit_part=next(x for x in native+NEW if x['name']==firsthit['part']);native_triangle=dict(native_file=hit_part.get('native_file'),native_mesh=hit_part.get('native_mesh'),native_triangle_index=firsthit['triangle'],native_triangle_xyz=hit_part['triangles'][firsthit['triangle']],point_xyz=firsthit['point_xyz'])
 checks.append(dict(name=f['name'],backplate_full_contact_corners=contacts,support_chain=support,lens_front_center_xyz=lens_front.tolist(),marker_free_space_offset_m=.02,exit_60mm_hits=exit_hits,lens_surface_to_exit_hits=exit_from_lens,receiver_sample_hits=sample_hits,first_native_receiver_hit=native_triangle,receiver_distance_m=float(np.linalg.norm(target-p))))
print('Primary rays checked',len(checks),'issues',len(issues),flush=True)
# Exact proposed-solid vs existing-geometry contact checks. Only backplate-host touch is allowed.
interference=[]
# Batched architectural exports contain disconnected/coincident solids; parity
# on a whole batch is not a solid-inside test. Use verified source decomposition
# for contact tests, while all native batches remain in every optical ray test.
contact_inputs=source+[p for p in native if not p['name'].startswith(('GrandPoolWetLoggias::','GrandPoolFocalEnd::','GrandPoolRoofComposition::'))]
for new in NEW:
 for old in contact_inputs:
  if not overlap(new['bounds'],old['bounds'],TOL):continue
  res=contact_pair(new,old)
  if res['penetration']:interference.append(dict(proposed=new['name'],retained=old['name'],**res))
issues += [['retained_penetration',x]for x in interference]
new_contacts=[]
for ii,a in enumerate(NEW):
 for b in NEW[ii+1:]:
  if not overlap(a['bounds'],b['bounds'],-TOL):continue
  r=contact_pair(a,b)
  if not(r['touch']or r['penetration']):continue
  allowed=a['meta']['support']==b['name']or b['meta']['support']==a['name']
  new_contacts.append(dict(a=a['name'],b=b['name'],declared_mechanical_joint=allowed,**r))
  if not allowed:issues.append(['undeclared_new_contact',new_contacts[-1]])
# Unchanged old source exit and every available receiver ray, including stock fan rays.
preserved=[]
for f in section['fixtures']+finish['fixtures']:
 p=f['position_xyz'];d=f.get('direction_xyz',f.get('direction'))
 tests=[('exit_60mm',add(p,mul(d,.06)))]
 if 'receiver_xyz'in f:tests += [('receiver',f['receiver_xyz']),('visibility_sample',f.get('visibility_sample_xyz',f['receiver_xyz']))]
 for r in f.get('all_source_receiver_rays',[]):tests.append(('stock_'+r['receiver'],r['receiver_world_xyz']))
 for kind,end in tests:
  hits=rayhits(p,end,NEW);preserved.append(dict(fixture=f['name'],kind=kind,hits=hits))
  if hits:issues.append(['retained_fixture_ray',preserved[-1]])
views=[]
for v in arch['preserved_view_probes']:
 hits=rayhits(v['eye_xyz'],v['target_xyz'],NEW);views.append(dict(kind=v['kind'],name=v['name'],hits=hits))
 if hits:issues.append(['retained_view',views[-1]])
for v in arch['seat_approaches']:
 hits=rayhits(v['seated_eye_xyz'],v['pool_view_target_xyz'],NEW);views.append(dict(kind='new_curved_seat_view',name=v['name'],hits=hits))
 if hits:issues.append(['retained_view',views[-1]])
# Conservative continuous route broad phase. A pass proves proposed fixture bounds clear of full route envelope.
paths=[dict(name=p['item'],points=p['points'],r=.30,h=1.80)for p in first['approach_paths']]
paths += [dict(name='wet_main',points=[[-45.9,46.2,-458],[-45.9,46.2,-405]],r=.5,h=2)]
paths += [dict(name='dry_market',points=[[x,52.5,z]for x,z in section['market']['adopted_dry_loop_centreline_xz']],r=.5,h=2)]
paths += [dict(name='stock_'+p['display'],points=p['points_xyz'],r=.3,h=1.8)for p in finish['stock_approach_paths']]
paths += [dict(name='ramp',points=section['accessible_ramp']['route_xyz'],r=.5,h=2),dict(name='lower_lift',points=section['wet_market_link']['lift']['lower_approach_xyz'],r=.5,h=2)]
paths += [dict(name='curved_'+p['name'],points=p['approach_xyz'],r=p['swept_envelope_radius_m'],h=p['standing_height_m'])for p in arch['seat_approaches']]
route_checks=[]
for path in paths:
 found=set()
 for a,b in zip(path['points'],path['points'][1:]):
  lo=[min(a[0],b[0])-path['r'],min(a[1],b[1])+.02,min(a[2],b[2])-path['r']];hi=[max(a[0],b[0])+path['r'],max(a[1],b[1])+path['h'],max(a[2],b[2])+path['r']]
  for new in NEW:
   if overlap([lo,hi],new['bounds'],TOL):found.add(new['name'])
 route_checks.append(dict(name=path['name'],broad_envelope_hits=sorted(found)))
 if found:issues.append(['route_envelope',route_checks[-1]])
# Source-derived receiver fan stays within cone/range, but does not claim native brightness or active selection.
fan=[]
for f in fixtures:
 p=np.array(f['position_xyz']);axis=np.array(f['direction_xyz']);name=f['name']
 targets=[]
 if 'Timber' in name:
  for x in [-52.5,-51.5,-50.5]:
   for y in [47.75,48.15,48.65]:targets.append([x,y,f['receiver_xyz'][2]])
 else:
  # Use exact real source triangle centroids: sun + all three wave rows + terracotta flanks.
  for partname in ['FOCAL_OrbitalSunRelief','FOCAL_Wave_0_05','FOCAL_Wave_1_05','FOCAL_Wave_2_05']:
   rec=source_by[partname]
   front=[(i,t)for i,t in enumerate(rec['ta']) if np.ptp(t[:,2])<1e-6 and t[:,2].mean()>rec['ta'][:,:,2].max()-1e-5]
   for idx,t in front[:2]:targets.append(np.mean(t,axis=0).tolist())
  for xx in [-34,-28]:
   for yy in [48.7,49.5]:
    q=[xx,yy,float(source_by['FOCAL_RecessedTerracotta']['ta'][:,:,2].max())];point_record(q,'FOCAL_RecessedTerracotta');targets.append(q)
 rows=[]
 for q in targets:
  d=np.array(q)-p;dist=float(np.linalg.norm(d));unit=d/dist;angle=math.degrees(math.acos(float(np.clip(axis@unit,-1,1))))
  hits=rayhits(p,np.array(q)+unit*.001,native+NEW);firsthit=hits[0]if hits else None
  cosine=float(axis@unit);lens_exit=p-unit*(.02/cosine)
  lens=NM[name.removeprefix('DATUM_finish_light_')+'_OpalLens'];on_lens=on_surface(lens_exit,lens,1e-7)
  exit_hits=rayhits(lens_exit+unit*.0001,np.array(q)-unit*.02,native+NEW)
  if not on_lens or exit_hits:issues.append(['fan_lens_exit',name,q,on_lens,exit_hits])
  if not(angle<f['suggested_spot_angle_degrees'] and dist<f['suggested_range_m'] and firsthit and abs(firsthit['distance_m']-dist)<TOL):issues.append(['fan_cone_range_or_receiver',name,q,firsthit])
  rows.append(dict(lens_exit_xyz=lens_exit.tolist(),on_physical_lens_front=on_lens,lens_to_receiver_sample_hits=exit_hits,target_xyz=q,distance_m=dist,axis_angle_degrees=angle,within_trial_cone_and_range=angle<f['suggested_spot_angle_degrees']and dist<f['suggested_range_m'],first_hit=firsthit,requested_target_first_hit=bool(firsthit and abs(firsthit['distance_m']-dist)<TOL)))
 fan.append(dict(name=name,receiver_samples=rows))
# Source visibility rays for exact unchanged camera/actor sample offsets: informative only.
visibility=[]
for r in images:
 if r['effects']:continue
 actor=np.array([r['eye'][0],r['actor_foot_y'],r['eye'][2]])
 for f in fixtures:
  for sample_name,o in [('source',f['position_xyz']),('receiver',f['visibility_sample_xyz'])]:
   hits=[]
   for off in [[0,1.5,0],[0,.4,0],[.65,1,0],[-.65,1,0]]:
    hh=rayhits(o,actor+off,native+NEW);hits.append(dict(actor_offset=off,first_hit=hh[0]if hh else None))
   visibility.append(dict(view=r['view'],fixture=f['name'],sample=sample_name,source_triangle_visibility_only=hits,scope='Conservative all-visible-geometry screen; native physics material exemptions and ranked eight-source selection are not emulated.'))
# Confirm read inputs unchanged across analysis. Output itself is the only authorized write target.
changed=[p for p,h in pins.items()if sha(Path(p))!=h]
if changed:issues.append(['input_changed_during_check',changed])
save('PROPOSED_FIXTURE_LAYER.json',dict(schema=1,status='PROPOSAL_SOURCE_NUMERICAL_PASS'if not issues else'PROPOSAL_NEEDS_CORRECTION',coordinate_frame='Godot/glTF XYZ metres',parent_design_id='AST-AQU-016',fixtures=fixtures,proposed_parts=parts,source_geometry=snapshot_evidence,preserved=dict(original_source_fixtures=39,architectural_parts=451,architectural_plants=12,original_programme_furnishings=126,active_source_budget=8),pending=['Parent current numerical checkpoint completion','Explicit source-authoring gate','Actual saved-source reopen and exact exporter equivalence','Native collision and active selection','Native visual side-by-side review and unchanged full regression']))
save('GEOMETRY_CHECKS.json',dict(status='PASS'if not issues else'FAIL',issues=issues,physical_fixture_checks=checks,retained_interference=interference,declared_new_fixture_joints=new_contacts,preserved_fixture_ray_checks=preserved,preserved_view_checks=views,route_checks=route_checks,receiver_fans=fan,source_only_visibility=visibility,contact_method='Actual closed source parts replace only equivalent architecture batch containers in solid-inside tests; all native triangles remain in optical rays.',native_input_mesh_instances=len(native),native_input_triangles=sum(len(p['triangles'])for p in native),source_only=True,limitations=['No engine or renderer run. Proposed solids are mathematical, not authored/reopened sources.','Native activation, illuminance, reflection, visual hierarchy, seated interaction and performance are untested.','Whole-ship objects outside the four existing pool source contracts are not recompiled; later native ray gates remain mandatory.']))
save('INPUT_PINS.json',dict(sha256=pins,inputs_unchanged_at_finish=not changed,checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print(json.dumps(dict(status='PASS'if not issues else'FAIL',issues=issues,fixture_count=len(fixtures),proposed_parts=len(parts),preserved_fixture_rays=len(preserved),preserved_views=len(views),route_checks=len(route_checks)),indent=2),flush=True)
