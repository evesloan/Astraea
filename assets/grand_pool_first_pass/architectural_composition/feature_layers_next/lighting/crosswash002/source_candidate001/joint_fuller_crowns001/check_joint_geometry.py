"""Pure-geometry comparison only. No engine, source load, export, import or adoption.
Writes exclusively new evidence beside this script. Immutable source snapshots bind
all geometry. Replacement triangles preserve actual evaluated per-part indexing.
"""
import sys
sys.dont_write_bytecode = True
import json, hashlib, math, datetime, importlib.util
from pathlib import Path
OUT = Path(__file__).resolve().parent
C = OUT.parent
ROOT = C.parent
PROTO = ROOT.parent / 'plant_mass_prototype/candidate_v001'
PINS = {}
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def pin(p, expected=None):
    p=Path(p); h=sha(p)
    assert expected is None or h==expected, ('Hash mismatch',str(p),expected,h)
    assert str(p) not in PINS or PINS[str(p)]==h
    PINS[str(p)]=h
    return h
def read(p, expected=None):
    pin(p,expected); return json.loads(Path(p).read_text())
def write(name, data):
    path=OUT/name
    assert path.resolve().parent==OUT
    with path.open('x') as f: json.dump(data,f,indent=2,sort_keys=True,allow_nan=False); f.write('\n')
def log(s): print(s,flush=True)
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sys.version_info[:2] == (3,12)
source_hash=pin(C/'source/AST-AQU-016_pool_feature_lighting.blend','0d02c3e4d11e8b50272a30606a6ef23955a8ef08a9a406993b4f8ee75f77daf8')
receipt=read(C/'qa/reopen001_geometry/REOPEN_RECEIPT.json','ec24fcf8d468bf247dc416b31b93e6ba4c8bbdfea6bcc59e8b23b60a846c692d')
assert receipt['status']=='PASS_SOURCE_ONLY' and receipt['inputs_unchanged_at_finish'] and not receipt['issues']
assert receipt['source_sha256']==source_hash
for p,h in receipt['input_sha256'].items(): pin(p,h)
for name,h in receipt['evidence_sha256'].items(): pin(C/'qa/reopen001_geometry'/name,h)
for name,h in receipt['snapshot_evidence_sha256'].items(): pin(C/'qa/reopen001_snapshot'/name,h)
fixed=read(ROOT/'INPUT_PINS.json')
assert fixed['inputs_unchanged_at_finish']
for p,h in fixed['sha256'].items():pin(p,h)
old=read(C/'qa/reopen001_geometry/REOPEN_GEOMETRY_CHECKS.json')
snapshot=read(C/'qa/reopen001_snapshot/ACTUAL_REOPENED_SOURCE.json')
assert snapshot['source_sha256']==source_hash
proposal=read(ROOT/'PROPOSED_FIXTURE_LAYER.json')
proposal_baseline=read(ROOT/'GEOMETRY_CHECKS.json')
qa=read(PROTO/'qa/SOURCE_QA.json')
assert qa['status']=='PASS_SOURCE_QA_ONLY' and qa['source_files_unchanged_by_qa'] and qa['retained_input_hashes_unchanged']
proto=read(PROTO/'qa/REOPENED_GEOMETRY.json',qa['reopened_geometry_sha256'])
assert 'Blender local (x,y,z) -> glTF (x,z,-y)' in proto['coordinate_mapping']
for row in qa['sources']: pin(row['source'],row['source_sha256'])
for p,h in qa['retained_constraints']['read_only_runtime_input_pins'].items():pin(p,h)
script=C/'reopen_feature_lighting002.py'
pin(script,receipt['script_sha256'])
spec=importlib.util.spec_from_file_location('read_only_reopen_helpers',script)
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
r.PINNED.update(PINS)
helpers=r.geometry_helpers()
np=r.np
retained=r.retained_geometry(helpers)
src,src_by,native,section,first,finish,arch=retained
# Cache the immutable retained scene and reproduce the complete exact baseline first.
r.retained_geometry=lambda _:retained
r.ISSUES.clear()
reproduced=r.geometry_checks(snapshot['meshes'],snapshot['markers'],proposal,proposal_baseline,helpers)
assert not r.ISSUES, r.ISSUES
assert reproduced==old, 'Recomputed actual baseline differs from retained evidence'
write('BASELINE_REPRODUCTION.json',{'status':'EXACT_MATCH','source_geometry_checks_sha256':pin(C/'qa/reopen001_geometry/REOPEN_GEOMETRY_CHECKS.json'),'all_fields_equal':True,'source_receipt_sha256':pin(C/'qa/reopen001_geometry/REOPEN_RECEIPT.json')})
log('Exact retained source-only baseline reproduced.')
plant_by={p['name']:p for p in arch['plants']}
assert len(plant_by)==12
assert len(proto['assets'])==len(proto['retained_basal_instances'])==len(proto['prior_middle_instances'])==6
names={a['replaces_instance'] for a in proto['assets']}
assert names=={p['name'] for p in proto['prior_middle_instances']}
assert all(n.startswith('LOG_') and '_Pocket_' in n and n.endswith('_middle') for n in names)
for p in proto['retained_basal_instances']+proto['prior_middle_instances']:
    oldp=plant_by[p['name']]
    assert all(p[k]==oldp[k] for k in ('position_xyz','yaw_radians','model_file'))
    assert p['scale_xyz']==[1,1,1] and oldp.get('scale_xyz',[1,1,1])==[1,1,1]
fuller=[];mapping=[]
for asset in proto['assets']:
    p=plant_by[asset['replaces_instance']]
    assert asset['position_xyz']==p['position_xyz'] and asset['yaw_radians']==p['yaw_radians'] and asset['scale_xyz']==[1,1,1]
    assert abs(asset['yaw_radians']-math.pi/2)<1e-15
    assert asset['replaces_model_file']==p['model_file']
    c,s=math.cos(asset['yaw_radians']),math.sin(asset['yaw_radians'])
    rot=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    av=[];triangle_count=0
    for part in asset['parts']:
        local=np.asarray(part['vertices'],dtype=float)
        native_local=local[:,[0,2,1]]*np.array([1,1,-1])
        world=native_local@rot.T+np.asarray(asset['position_xyz'])
        ix=np.asarray(part['evaluated_triangle_indices'],dtype=int)
        tris=world[ix]
        g=r.prepare(helpers['record'](asset['replaces_instance']+'::'+part['name'],world.tolist(),tris.tolist(),
             prototype_asset=asset['name'],prototype_source=str(PROTO/asset['source']),
             source_part=part['name'],source_triangle_index_convention='zero-based evaluated_triangle_indices order',
             material_role=part['material_role'],surface_kind=part['surface_kind'],triangle_vertex_indices=ix.tolist()))
        fuller.append(g);av.extend(world.tolist());triangle_count+=len(tris)
    actual_bounds=helpers['bounds'](av)
    assert float(np.max(np.abs(np.asarray(actual_bounds)-asset['bounds_world'])))<1e-12
    sq=next(x for x in qa['sources'] if x['name']==asset['name'])
    assert triangle_count==sq['triangles']==asset['planned_triangle_count']==7066
    assert len(asset['parts'])==sq['parts']==178
    removed=[x for x in native if x['name'].split('::')[0]==asset['replaces_instance']]
    assert removed
    mapping.append({'instance':asset['replaces_instance'],'source':str(PROTO/asset['source']),
        'source_sha256':pin(PROTO/asset['source']),'position_xyz':asset['position_xyz'],'yaw_radians':asset['yaw_radians'],
        'scale_xyz':asset['scale_xyz'],'actual_bounds_xyz':actual_bounds,'parts':len(asset['parts']),'triangles':triangle_count,
        'removed_sparse_mesh_names':[x['name'] for x in removed],'removed_sparse_triangles':sum(len(x['triangles']) for x in removed)})
removed=[p for p in native if p['name'].split('::')[0] in names]
kept=[p for p in native if p['name'].split('::')[0] not in names]
joint_native=kept+fuller
assert set(p['name'].split('::')[0] for p in removed)==names
assert all(any(x['name'].startswith(p['name']+'::') for x in kept) for p in proto['retained_basal_instances'])
write('REPLACEMENT_MAPPING.json',{'coordinate_mapping':proto['coordinate_mapping'],'only_six_middle_instances_replaced':True,
    'all_twelve_transforms_unchanged':True,'six_basal_instances_retained':proto['retained_basal_instances'],
    'retained_geometry_records_unchanged':len(kept),'removed_sparse_records':len(removed),'fuller_parts':len(fuller),
    'fuller_triangles':sum(len(p['triangles']) for p in fuller),'assets':mapping})
r.retained_geometry=lambda _:(src,src_by,joint_native,section,first,finish,arch)
r.ISSUES.clear()
joint=r.geometry_checks(snapshot['meshes'],snapshot['markers'],proposal,proposal_baseline,helpers)
joint_issues=list(r.ISSUES)
joint['method']='Exact reproduced pinned actual fixture-source baseline, replacing only six middle plant GLB instances with hash-bound actual reopened prototype triangles. The prototypes remain uninstalled. All other geometry and transforms are unchanged.'
write('JOINT_GEOMETRY_CHECKS.json',joint)
new=[r.prepare(helpers['record'](m['name'],m['vertices'],m['triangles'])) for m in snapshot['meshes']]
fuller_names={p['name'] for p in fuller}
by_name={p['name']:p for p in fuller}
marker_by={m['name']:m for m in snapshot['markers']}
fan_delta=[];foliage_obstructions=[]
for jf,of in zip(joint['actual_receiver_fans'],old['actual_receiver_fans']):
    assert jf['name']==of['name']
    for i,(j,o) in enumerate(zip(jf['receiver_samples'],of['receiver_samples'])):
        sample_name=jf['name']+f'/receiver_sample_{i:02d}'
        assert j['target_xyz']==o['target_xyz'] and j['actual_lens_exit']==o['actual_lens_exit']
        hits=j['lens_to_receiver_sample_hits']
        foliage=[h for h in hits if h['part'] in fuller_names]
        entry={'fixture':jf['name'],'sample_name':sample_name,'sample_index_zero_based':i,
            'target_xyz':j['target_xyz'],'distance_marker_to_receiver_m':j['distance_m'],
            'actual_lens_exit':j['actual_lens_exit'],'baseline_first_hit':o['first_hit'],
            'joint_first_hit_from_marker':j['first_hit'],'lens_to_20mm_receiver_sample_hits':hits,
            'first_hit_from_lens_exit_plus_0_1mm':hits[0] if hits else None,
            'clear_in_baseline':o['pass'],'clear_in_joint':j['pass'],
            'classification':'FOLIAGE_TRIANGLE_INTERCEPTION_ON_SECONDARY_SAMPLE' if foliage else 'UNCHANGED_CLEAR_RECEIVER_SAMPLE'}
        if foliage:
            hit=foliage[0];part=by_name[hit['part']];ti=hit['triangle']
            entry['first_foliage_hit_detail']={**hit,'distance_reference':'actual lens intersection plus 0.1 mm forward along this sample ray',
                 'prototype_source':part['prototype_source'],'source_part':part['source_part'],
                 'source_triangle_index_zero_based':ti,'source_triangle_vertex_indices':part['triangle_vertex_indices'][ti],
                 'world_triangle_xyz':part['triangles'][ti],'material_role':part['material_role'],'surface_kind':part['surface_kind']}
            foliage_obstructions.append(entry)
        fan_delta.append(entry)
write('RECEIVER_FAN_COMPARISON.json',{'sample_count':len(fan_delta),'foliage_shadow_sample_count':len(foliage_obstructions),
    'distance_conventions':'first_hit_from_marker distances start at saved source marker; lens path distances start 0.1 mm past actual lens intersection; sample segment ends 20 mm before actual receiver.',
    'samples':fan_delta})
write('NEW_FOLIAGE_OBSTRUCTIONS.json',foliage_obstructions)
log(json.dumps({'central_paths_unchanged':joint['actual_primary_light_paths']==old['actual_primary_light_paths'],
    'foliage_shadow_samples':len(foliage_obstructions),'sample_names':[x['sample_name'] for x in foliage_obstructions]}))
# Hardware contact: conservative bounds can establish complete separation without
# interpreting open leaves as closed volumes. If any bounds overlap, inspect real
# triangle surface contact and leaf vertices inside the closed hardware.
hardware=[]
for a in new:
    broad=[b for b in fuller if helpers['overlap'](a['bounds'],b['bounds'],-r.TOL)]
    exact=[]
    for b in broad:
        touch=helpers['contact_pair'](a,b,interior=False)
        inside=[v for v in b['vertices'] if helpers['strict_inside'](v,a)]
        if touch['touch'] or inside: exact.append({'foliage_part':b['name'],'surface_contact':touch,'foliage_vertices_inside_hardware':inside})
    hardware.append({'fixture_part':a['name'],'broad_phase_candidates':[p['name'] for p in broad],'actual_contact_or_inside':exact})
write('HARDWARE_FOLIAGE_CHECKS.json',hardware)
# Recheck retained 91 rays against added actual crown geometry, preserving baseline
# new-hardware-only results and also exposing old sparse vs fuller whole-scene first hits.
ray_rows=[]
rayhits=helpers['rayhits']
sparse_scene=native+new;fuller_scene=joint_native+new
for fixture in section['fixtures']+finish['fixtures']:
    p=np.asarray(fixture['position_xyz']);direction=np.asarray(fixture.get('direction_xyz',fixture.get('direction')))
    rays=[('exit_60mm',p+direction*.06)]
    if 'receiver_xyz' in fixture:rays += [('receiver',fixture['receiver_xyz']),('visibility_sample',fixture.get('visibility_sample_xyz',fixture['receiver_xyz']))]
    rays += [('stock_'+v['receiver'],v['receiver_world_xyz']) for v in fixture.get('all_source_receiver_rays',[])]
    for kind,q in rays:
        crown_hits=rayhits(p,q,fuller);sparse_hits=rayhits(p,q,sparse_scene);joint_hits=rayhits(p,q,fuller_scene)
        ray_rows.append({'fixture':fixture['name'],'kind':kind,'origin_xyz':p.tolist(),'endpoint_xyz':np.asarray(q).tolist(),
             'fuller_foliage_hits':crown_hits,'baseline_first_hit':sparse_hits[0] if sparse_hits else None,
             'joint_first_hit':joint_hits[0] if joint_hits else None,'all_first_hits_equal':(sparse_hits[:1]==joint_hits[:1])})
assert len(ray_rows)==91
write('PRESERVED_FIXTURE_COMPARISON.json',ray_rows)
views=[]
probes=[dict(name=v['name'],kind=v['kind'],eye=v['eye_xyz'],target=v['target_xyz']) for v in arch['preserved_view_probes']]
probes += [dict(name=v['name'],kind='new_curved_seat_view',eye=v['seated_eye_xyz'],target=v['pool_view_target_xyz']) for v in arch['seat_approaches']]
for p in probes:
    crown_hits=rayhits(p['eye'],p['target'],fuller);sparse_hits=rayhits(p['eye'],p['target'],sparse_scene);joint_hits=rayhits(p['eye'],p['target'],fuller_scene)
    views.append({**p,'fuller_foliage_hits':crown_hits,'baseline_first_hit':sparse_hits[0] if sparse_hits else None,
        'joint_first_hit':joint_hits[0] if joint_hits else None,'all_first_hits_equal':sparse_hits[:1]==joint_hits[:1]})
assert len(views)==162
write('PRESERVED_VIEW_COMPARISON.json',views)
paths=[dict(name=p['item'],points=p['points'],r=.3,h=1.8) for p in first['approach_paths']]
paths += [dict(name='wet_main',points=[[-45.9,46.2,-458],[-45.9,46.2,-405]],r=.5,h=2)]
paths += [dict(name='dry_market',points=[[x,52.5,z] for x,z in section['market']['adopted_dry_loop_centreline_xz']],r=.5,h=2)]
paths += [dict(name='stock_'+p['display'],points=p['points_xyz'],r=.3,h=1.8) for p in finish['stock_approach_paths']]
paths += [dict(name='ramp',points=section['accessible_ramp']['route_xyz'],r=.5,h=2),dict(name='lower_lift',points=section['wet_market_link']['lift']['lower_approach_xyz'],r=.5,h=2)]
paths += [dict(name='curved_'+p['name'],points=p['approach_xyz'],r=p['swept_envelope_radius_m'],h=p['standing_height_m']) for p in arch['seat_approaches']]
routes=[]
for path in paths:
    hits=set()
    for a,b in zip(path['points'],path['points'][1:]):
        box=[[min(a[0],b[0])-path['r'],min(a[1],b[1])+.02,min(a[2],b[2])-path['r']],
             [max(a[0],b[0])+path['r'],max(a[1],b[1])+path['h'],max(a[2],b[2])+path['r']]]
        hits.update(p['name'] for p in fuller if helpers['overlap'](box,p['bounds'],r.TOL))
    routes.append({**path,'fuller_continuous_broad_envelope_hits':sorted(hits)})
assert len(routes)==30
write('PRESERVED_ROUTE_COMPARISON.json',routes)
structural_issues=[x for x in joint_issues if x['category']!='actual_receiver_fan']
structural_issues += [{'category':'hardware_foliage_contact','detail':x} for x in hardware if x['actual_contact_or_inside']]
structural_issues += [{'category':'preserved_ray_new_foliage','detail':x} for x in ray_rows if x['fuller_foliage_hits']]
structural_issues += [{'category':'preserved_view_new_foliage','detail':x} for x in views if x['fuller_foliage_hits']]
structural_issues += [{'category':'preserved_route_broad_candidate','detail':x} for x in routes if x['fuller_continuous_broad_envelope_hits']]
# Check exact pin stability after all computation, including any additional read inputs.
for p,h in r.PINNED.items():pin(p,h)
for p,h in list(PINS.items()):assert sha(p)==h, ('Changed input',p)
write('INPUT_PINS.json',{'sha256':PINS,'inputs_unchanged_at_finish':True})
summary={'status':'PASS_STRUCTURAL_WITH_FOLIAGE_INTERCEPTIONS_SOURCE_ONLY' if not structural_issues else 'REVIEW_REQUIRED_SOURCE_ONLY',
    'started_at_utc':started,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_sha256':source_hash,'exact_baseline_reproduced':True,'unchanged_input_count':len(PINS),
    'replacement_instance_count':6,'retained_basal_instance_count':6,'all_12_plant_transforms_unchanged':True,
    'fuller_parts':len(fuller),'fuller_triangles':sum(len(p['triangles']) for p in fuller),
    'central_paths_count':3,'central_paths_exactly_unchanged':joint['actual_primary_light_paths']==old['actual_primary_light_paths'],
    'exit_60mm_obstructions':sum(len(p['exit_60mm_hits'])+len(p['lens_front_to_exit_hits']) for p in joint['actual_primary_light_paths']),
    'finite_cone_obstructions':sum(len(p['finite_forward_cone_hits']) for p in joint['actual_primary_light_paths']),
    'receiver_fan_samples':len(fan_delta),'receiver_fan_clear_samples':sum(x['clear_in_joint'] for x in fan_delta),
    'new_foliage_shadow_samples':len(foliage_obstructions),
    'fan_counts_by_fixture':[{'fixture':f['name'],'total':len(f['receiver_samples']),'clear':sum(p['pass'] for p in f['receiver_samples']),
        'foliage_shadow_samples':[x['sample_name'] for x in foliage_obstructions if x['fixture']==f['name']]} for f in joint['actual_receiver_fans']],
    'fixture_hardware_parts':len(hardware),'hardware_foliage_broad_candidates':sum(len(x['broad_phase_candidates']) for x in hardware),
    'hardware_foliage_contacts':sum(len(x['actual_contact_or_inside']) for x in hardware),
    'preserved_fixture_ray_count':len(ray_rows),'preserved_fixture_new_foliage_hits':sum(bool(x['fuller_foliage_hits']) for x in ray_rows),
    'preserved_fixture_first_hit_changes':sum(not x['all_first_hits_equal'] for x in ray_rows),
    'preserved_view_count':len(views),'preserved_view_new_foliage_hits':sum(bool(x['fuller_foliage_hits']) for x in views),
    'preserved_view_first_hit_changes':sum(not x['all_first_hits_equal'] for x in views),
    'preserved_route_count':len(routes),'preserved_route_broad_candidates':sum(bool(x['fuller_continuous_broad_envelope_hits']) for x in routes),
    'structural_issues':structural_issues,'raw_joint_issues':joint_issues,
    'scope':{'engines_launched':False,'blender_launched':False,'exports_created':False,'native_imports':False,
             'game_or_catalogue_writes':False,'plants_or_fixtures_modified':False,'prototypes_installed':False},
    'pending':['Native import/equivalence','Native light activation','8-active source selection','Matched native A/B','Visible brightness and foliage-shadow appearance'],
    'interpretation':'Actual opaque-triangle foliage interceptions on secondary receiver paths are reported, not suppressed and not automatically structural failures. These botanical instances are visual-only. Source-triangle interception does not prove runtime physics occlusion, selector behavior, native shadows or final visible brightness. Material alpha and native shadow response remain unrun A/B evidence. No unobstructed timber wash or brightness claim follows from clear central rays.'}
write('JOINT_RECEIPT.json',summary)
log(json.dumps(summary))
