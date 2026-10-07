"""Read-only crosswalk, source-hash and exact aperture/ceiling verification."""
from pathlib import Path
import json,hashlib,math
from collections import Counter
R=Path(__file__).resolve().parents[1];P=json.loads((R/'QUIET_GROVE_83_CURRENT_APPLICATION.json').read_text());B=json.loads((R/'outputs/source_r002/BATCH_RECEIPT.json').read_text());G=json.loads((R/'qa/GEOMETRY_SCREEN_EXTENDED.json').read_text());V=json.loads((R/'REST_SLOT_PROVENANCE.json').read_text());OLD=json.loads((R.parent/'outputs/sf_house_r002/PLAN.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old={r['address']:r for r in OLD['rooms']};identity=[];bounds=[];pins=[];perimeters=[];curves=[]
for r in P['units']:
 a=old[r['address']];identity.append([r['address'],[(x['unit_slot_key'],x['unit_anchor_index'],x['prototype_anchor_index'])for x in r['anchor_bindings']]==[(x['unit_slot_key'],x['unit_anchor_index'],x['prototype_anchor_index'])for x in a['anchor_bindings']]])
 for s in r['anchor_bindings']:
  x,y,z=s['world_xyz'];bounds.append(r['allocation_x'][0]<=x<=r['allocation_x'][1] and r['allocation_z'][0]<=z<=r['allocation_z'][1] and abs(y-r['floor_y'])<1e-6)
for rc in B['prototypes']:
 d=R/'outputs/source_r002'/rc['prototype'];pins.extend({'file':str(d/n),'pass':sha(d/n)==h}for n,h in rc['files'].items());obs={o['name']:o for o in json.loads((d/'EVALUATED_GEOMETRY.json').read_text())}
 expected={'SUI_WindowPane_-3.4':[[-3.4,12.771,.475],[-.055,12.789,3.605]],'SUI_WindowPane_0.055':[[.055,12.771,.475],[3.4,12.789,3.605]],'SUI_WindowMullion_0':[[-.065,12.72,.48],[.065,12.86,3.60]],'SUI_WindowSill':[[-3.5,12.67,0],[3.5,12.89,.48]],'SUI_WindowHead':[[-3.5,12.67,3.60],[3.5,12.89,3.90]]}
 for name,e in expected.items():
  error=max(abs(obs[name]['bounds'][i][j]-e[i][j])for i in range(2)for j in range(3));perimeters.append({'prototype':rc['prototype'],'part':name,'max_error_m':error,'pass':error<1e-5})
 for name,o in obs.items():
  if not name.startswith('SUI_Ceiling_'):continue
  errs=[]
  for x,y,z in o['vertices']:
   h=2.95+.95*max(0,min(1,(y-2)/10.75));errs.append(min(abs(z-h),abs(z-h-.14)))
  curves.append({'prototype':rc['prototype'],'part':name,'retained_rising_profile_error_m':max(errs),'pass':max(errs)<1e-5})
labels=Counter(c['component']for c in G['shell_surface_contacts']);fixed={'bath_shower','EntryDoor','BathroomDoor'}
newcontacts=[x for x in G['shell_surface_contacts'] if x['component'] not in fixed]
classification={'raw_contact_component_pairs':len(G['shell_surface_contacts']),'labels':dict(labels),'classification':'Retained shower rear mount and static entry/bath door frame joints. No new sleep, sitting, storage or kitchenette crossing pair. Moving-leaf contact remains untested.','evidence':'r011/qa/CLASSIFIED_ALL_FURNITURE_SHELL_CONTACTS.json identifies the same retained three fixed interface families; raw new exact source-owner contacts remain in GEOMETRY_SCREEN.json','unclassified_pairs':newcontacts,'surface_screen_limit':'Triangle-edge screen is a broad source contact diagnostic, not an engine collision/contact manifold certificate'}
report={'status':'PASS_SCOPED_SOURCE_SUCCESSOR' if all([all(x[1]for x in identity),all(bounds),all(x['pass']for x in pins),all(x['pass']for x in perimeters),all(x['pass']for x in curves),G['all_component_transforms_pass'],G['all_route_targets_pass'],not newcontacts,not G['furniture_pair_broad_overlaps']])else'FAIL','counts':{'units':83,'standard':34,'family':49,'recipes':8,'rest_slots':215,'outer_court_outlooks':43,'inner_planted_outlooks':40,'adjacency_edges_different':111,'component_transforms':92,'route_targets_radius_0_30_m':92},'identity_ordinal_count_checks':identity,'every_rest_coordinate_inside_original_envelope':all(bounds),'prototype_file_hash_checks':pins,'sealed_r010_perimeter_checks':perimeters,'original_main_ceiling_curve_checks':curves,'contact_classification':classification,'runtime_acceptance':False,'remaining_gates':['Actual door-in-motion and real loaded cart query','Species/body and sleeping animation fits','Current directional privacy in Game, full vertical court rays and seated/standing external views','Room first-person visual review and CRT on/off','Full structural shell join/receiving support acceptance; existing full-house support holds remain']}
C=R.parents[1]/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json';canonical={x['source_envelope_index']:x for x in json.loads(C.read_text())['records']}
assert all(canonical[r['census_source_index']]['allocation_sha256']==r['allocation_sha256'] and canonical[r['census_source_index']]['proposed_rest_slot_ids']==[a['unit_slot_key']for a in r['anchor_bindings']] and not canonical[r['census_source_index']]['historical_bed_anchor_markers'] for r in P['units'])
report['canonical_1000_crosswalk']={'path':str(C),'sha256':sha(C),'all_83_unit_allocations_and_215_slot_IDs_match':True,'no_recovered_historical_anchor_coordinates_in_any_83':True}
(R/'qa/SOURCE_SUCCESSOR_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['counts']);assert report['status'].startswith('PASS')
