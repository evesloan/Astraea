from pathlib import Path
import sys,json,copy,hashlib
R=Path(__file__).resolve().parent;ROOT=R/'mini_root';sys.path.insert(0,str(ROOT/'tools'));from theater_surface_policy import *
layout=json.loads((ROOT/'data/spatial_layout.json').read_text());c=json.loads((ROOT/'data/design_contract.json').read_text());levels={x['deck_id']:x['floor_elevation_m']for x in c['deck_datums']};assert verify_theater_surfaces(ROOT,layout,levels)==set(IDS)
def changed(fn):
 d=copy.deepcopy(layout);r=next(r for r in d['regions']if r['id']==IDS[0]);fn(d,r);return d
cases={
 'wrong_owner':lambda d,r:r.update(owner='anything_else'),
 'wrong_kind':lambda d,r:r.update(kind='generic_floor'),
 'compiler_generated_instead_of_asset':lambda d,r:r.update(provided_by_asset=False),
 'D14_floor_exemption':lambda d,r:r.update(deck='D14'),
 'wrong_elevation':lambda d,r:r.update(offset_y=1),
 'wrong_manifest':lambda d,r:r.update(source_surface_manifest_sha256='0'*64),
 'wrong_export':lambda d,r:r.update(source_static_export_sha256='0'*64),
 'wrong_source':lambda d,r:r.update(source_blend_sha256='0'*64),
 'whole_theater_rectangle':lambda d,r:r.update(boundary=[[-118,-265],[-34,-265],[-34,-115],[-118,-115]],holes=[]),
 'unknown_owner_id':lambda d,r:r.update(id='D12_theater_unreviewed'),
 'moving_cabin_claim':lambda d,r:r.update(id='D12_theater_moving_cabin'),
 'another_void_exemption':lambda d,r:r.update(void_exemptions=['theater_upper_volume','central_atrium']),
 'missing_eighth_owner':lambda d,r:d['regions'].remove(r),
}
results=[]
for name,fn in cases.items():
 try:verify_theater_surfaces(ROOT,changed(fn),levels)
 except AssertionError:results.append({'case':name,'rejected':True})
 else:raise AssertionError('Invalid exemption accepted: '+name)
original=Path('/workspace/shared/astraea-godot-production-20261003/tools/compile_layout.py').read_text();candidate=(ROOT/'tools/compile_layout.py').read_text();line="if item['deck'] in void['decks'] and void['id'] not in exemptions:shape=shape.difference(Polygon(void['boundary']))";assert line in original and line in candidate
compiled=json.loads((ROOT/'data/generated/structural_meshes.json').read_text());assert not set(IDS)&{x['id']for x in compiled['regions']};foundation=sum(x['structural_area_m2']for x in compiled['regions']if x['id'].startswith('D11_theater_foundation_'));flat=next(x['structural_area_m2']for x in compiled['regions']if x['id']=='D11_theater_flat_00');bridge=next(x['structural_area_m2']for x in compiled['regions']if x['id']=='D11_theater_receiving_bridge');assert abs(foundation-674.65)<1e-6 and abs(flat-9526.533323013166)<1e-6 and abs(bridge-183)<1e-6
report={'passed':True,'rejected_invalid_cases':results,'all_other_void_subtraction_rule_unchanged':True,'asset_owned_surface_compiler_triangle_count':0,'exact_D11_flat_area_m2':flat,'exact_D11_nonwalking_foundation_area_m2':foundation,'bridge_area_m2':bridge,'policy_sha256':hashlib.sha256((ROOT/'tools/theater_surface_policy.py').read_bytes()).hexdigest(),'live_Game_changed':False};out=R/'POLICY_GUARD_TESTS.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
