"""Independent decoded-source review; proposal only, no shared construction edits."""
from pathlib import Path
import gzip
import hashlib,json,sys,itertools
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parents[1];I=P/'qa/star_atlas_review_inputs'
sys.path.insert(0,str(P.parent/'group7_hull_atrium_20261009/source'))
from check_retained_exports import read,acc,nodes
plan=json.loads((I/'PLAN.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
root=R/'Game/assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb'
room=R/'Game/assets/models/STAR_ATLAS_D17_823_FITTED_r001.glb'
frame=I/'STAR_ATLAS_D17_STANDARD823_FRAME_r001.glb'
assert sha(root)==plan['source_pins'][str(root.relative_to(R))]
assert sha(room)==plan['room_model_sha256']
assert sha(frame)==plan['structure']['export_sha256']
def meshes(file):
    d,b=read(file);out={}
    for n,m in nodes(d):
        points=np.vstack([acc(d,b,q['attributes']['POSITION'])for q in d['meshes'][n['mesh']]['primitives']]);points=(np.c_[points,np.ones(len(points))]@m.T)[:,:3]
        low=points.min(0);high=points.max(0)
        corners=np.array(list(itertools.product(*zip(low,high))))
        cuboid=all(np.min(np.linalg.norm(points-q,axis=1))<1e-4 for q in corners)
        out[n['name']]={'bounds':[low.tolist(),high.tolist()],'cuboid_corners_verified':cuboid}
    return out
old=meshes(root);new=meshes(frame);room_meshes=meshes(room)
checks=0
for part in plan['parts']:
    if not part['name'].startswith(('SA823_Transverse','SA823_Longitudinal')):continue
    actual=new[part['name']];assert actual['cuboid_corners_verified']
    assert np.max(np.abs(np.array(actual['bounds'])-part['expected_bounds']))<1e-4;checks+=1
def contact(a,b):
    assert a['cuboid_corners_verified'] and b['cuboid_corners_verified']
    mn=np.maximum(a['bounds'][0],b['bounds'][0]);mx=np.minimum(a['bounds'][1],b['bounds'][1]);overlap=mx-mn
    assert np.all(overlap>1e-5),(a,b,overlap)
    return {'intersection_bounds':[mn.tolist(),mx.tolist()],'overlap_m':overlap.tolist(),'geometry_only':True}
root_contacts=[]
for i in range(4):
    name='SA823_Transverse'+str(i);root_contacts.append({'new_member':name,'retained_receiver':'D17R_FloorLong_0',**contact(new[name],old['D17R_FloorLong_0'])});checks+=1
floor=next(v for k,v in room_meshes.items()if k=='SUI_Floor')
floor_contacts=[]
for i in range(4):
    name='SA823_Transverse'+str(i);floor_contacts.append({'new_member':name,'retained_receiver':'SUI_Floor',**contact(new[name],floor)});checks+=1
for i in range(3):
    name='SA823_Longitudinal'+str(i);floor_contacts.append({'new_member':name,'retained_receiver':'SUI_Floor',**contact(new[name],floor)});checks+=1
upper_contact=contact(old['D17R_Hanger_0_06'],old['D17R_TrussLower_0']);checks+=1
envelope=[[-75.95,100.30,32.96],[-60.09,101.56,39.14]]
census_file=P/'qa/RETAINED_RUNTIME_CENSUS.json'
census=json.loads(census_file.read_bytes() if census_file.exists() else gzip.decompress(census_file.with_suffix('.json.gz').read_bytes()))['meshes']
low=np.array([m['minimum']for m in census]);high=np.array([m['maximum']for m in census]);hits=np.all(high>envelope[0],axis=1)&np.all(low<envelope[1],axis=1)
candidates=[m for m,hit in zip(census,hits)if hit and 'All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE'not in m['path']]
report={'status':'SOURCE_GEOMETRY_REVIEW_PASS_PRIMARY_CAPACITY_HELD','source_commit':'bc731d6d6d54bb2595331ee2f4368558d4d24fda','decoded_geometry_checks':checks,'root_sha256':sha(root),'room_sha256':sha(room),'new_frame_sha256':sha(frame),'original_room_runtime_meshes':len(room_meshes),'four_transverse_root_contacts':root_contacts,'seven_original_floor_contacts':floor_contacts,'retained_hanger_to_lower_truss_contact':upper_contact,'outboard_extent_m':13.2,'current_member_depth_m':.24,'extent_over_depth_geometric_ratio':55.0,'proposed_deep_transfer_clearance_envelope':envelope,'envelope_conservative_baseline_receiver_candidates':candidates,'envelope_clearance_accepted':False,'existing_roof_primary_capacity_accepted':False,'room_and_rest_reservations_modified':False,'runtime_or_shared_sources_modified':False,'limits':'Decoded cuboid geometry confirms positive overlaps, not joint strength, fixity, uplift, buckling, torsion, pressure capacity or owner permission. Deep-transfer volume is a coordination reservation only; conservative AABB candidates require true-face and current-main review.'}
(P/'qa/STAR_ATLAS_SOURCE_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
proposal={'status':'PROPOSED_SOURCE_ROOTED_TRANSFER_LAYOUT_NOT_BUILT','source_review':'qa/STAR_ATLAS_SOURCE_REVIEW.json','receiving_owner':'Group1 via parent 01a10f57-470c-7080-835a-63e3a239700f','structural_scope_owner':'Group7','source_root':'Game/assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb','root_sha256':sha(root),'preserve':['original 405-mesh runtime room','original two rest reservations','seven existing strongbacks and three lanterns unless source-owner revision explicitly replaces members','D17 street and D18 roof/route datums','all luxury roofs and private windows'],
 'transfer_lines':[{'z':33.10,'existing_station':['D17R_FloorCross_05','D17R_Hanger_0_05'],'outboard_floor_x':-75.95,'inboard_return_x':-60.09},{'z':39.00,'existing_station':['D17R_FloorCross_06','D17R_Hanger_0_06'],'outboard_floor_x':-75.95,'inboard_return_x':-60.09}],
 'proposal':'Reserve two deeper transverse underfloor transfer frames at the exact retained hanger/crossmember stations, with a return across both existing street longitudinal frame lines. The three retained outboard longitudinal members can distribute floor loads to these two lines after member/joint design. This layout avoids posts onto absent D16 slabs and preserves original room fit-out; it is not a member-size or load-capacity approval.',
 'receivers':['D17R_FloorLong_0','D17R_FloorLong_1','D17R_FloorCross_05','D17R_FloorCross_06','D17R_Hanger_0_05','D17R_Hanger_0_06','D17R_TrussLower_0','D17R_TrussLower_1','D17R_TrussUpper_0','D17R_TrussUpper_1','D17R_Hanger_1_05','D17R_Hanger_1_06'],
 'load_path_to_prove':'Original room floor -> seven retained underfloor members -> proposed transverse transfer frames -> restrained joints at both street frame lines -> existing hangers -> longitudinal truss lower chords/posts/diagonals/upper chords -> documented primary ship/house receivers. The final receiver capacities and restrained couple are not established by current geometry.',
 'underfloor_envelope':envelope,'envelope_is_reserved_not_accepted':True,
 'required_before_source_build':['Group1 exact underfloor true-face and route/room/roof clearance for the proposed envelope; current-main room and neighbour source pins','Source-owner selection of exact inboard primary receivers and the full connected native member/joint graph beyond the hanging-street frame','Primary load cases, section/joint/material specification, transverse bending/shear, torsion, local buckling and uplift/reaction checks for the 13.2m extension and short inboard return','Owner-reviewed native revision or additive scoped GLB with exact immutable-root pins and no room/roof cropping; rerun source, contact, route and graphical checks'],
 'rejected':'No posts are placed onto absent lower slabs; no room skin, decorative roof or shell glazing is substituted for a primary receiver. No protected luxury roof is changed.',
 'structural_capacity_accepted':False,'shared_patch_applied':False,'new_capacity':0}
proposal['transfer_lines'][0]['inboard_hanger_stagger']='Inboard Hanger_1_05 is at Z35.50, not Z33.10. The Z33.10 return meets FloorCross_05/FloorLong_1; longitudinal transfer to a real inboard hanger and its torsion/uplift restraint require explicit source/joint design.'
proposal['receivers_review_note']='The eight conservative baseline envelope hits are the intended existing street frame/hanger receivers. No unrelated baseline AABB hit was found after guide exclusion, but this is not exact current-main or route clearance acceptance.'
(P/'docs/STAR_ATLAS_SUPPORT_PROPOSAL.json').write_text(json.dumps(proposal,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':checks,'root_contacts':4,'floor_contacts':7,'original_room_meshes':len(room_meshes),'conservative_transfer_envelope_candidates':len(candidates),'built':False,'capacity_accepted':False}))
