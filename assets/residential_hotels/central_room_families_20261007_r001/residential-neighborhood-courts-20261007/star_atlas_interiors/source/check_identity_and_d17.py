"""Broad source identity/profile and truthful D17 spatial fit screen, no engine."""
from pathlib import Path
import json,hashlib,math,sys
import numpy as np
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
B=W/'residential-batch-neighborhood-20261006/scale_domestic_r011';G=Path('/workspace/shared/astraea-godot-production-20261003');P=json.loads((R/'STAR_ATLAS_85_PLACEMENT_MAP.json').read_text());old={r['census_source_index']:r for r in json.loads((B/'assemblies/GODOT_BATCH_INSTANCE_MAP.json').read_text())['instances']};cw={r['source_envelope_index']:r for r in json.loads((W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json').read_text())['records']};pins=json.loads((R/'qa/REFERENCE_INSPECTION.json').read_text())['owners_read_and_protected'];owner_checks={p:sha(p)==h for p,h in pins.items()};assert all(owner_checks.values())
proto={p['address']:p for p in P['prototypes']};source={};profile=[];hash_checks=[]
for key,cfg in proto.items():
 D=R/'outputs/source_r002'/key;rec=json.loads((D/'SOURCE_RECEIPT.json').read_text());objects=json.loads((D/'EVALUATED_GEOMETRY.json').read_text());markers=json.loads((D/'DATUMS.json').read_text());source[key]={'objects':objects,'markers':markers,'rec':rec}
 for n,h in rec['files'].items():hash_checks.append({'file':str(D/n),'matches':sha(D/n)==h})
 for o in objects:
  if o['name'].startswith('SUI_WindowPane'):
   lo,hi=o['bounds'];profile.append({'prototype':key,'name':o['name'],'low_z':lo[2],'high_z':hi[2],'glass_y':[lo[1],hi[1]],'pass':abs(lo[2]-.475)<1e-6 and abs(hi[2]-3.605)<1e-6 and abs(lo[1]-12.771)<1e-5 and abs(hi[1]-12.789)<1e-5})
  if o['name'].startswith('SUI_WindowMullion'):
   lo,hi=o['bounds'];profile.append({'prototype':key,'name':o['name'],'width_x':hi[0]-lo[0],'pass':abs(hi[0]-lo[0]-.13)<1e-5})
 assert sum(o['name'].startswith('SUI_Ceiling_')for o in objects)==6
 checks=[]
 for a in cfg['bed_anchors']:assert np.max(np.abs(np.array(markers['datums']['DATUM_bed_'+str(a['historical_anchor_index'])])-np.array(a['source_xyz'])))<1e-5
slots=[];world_fixtures=[];row_checks=[]
for r in P['units']:
 o=old[r['census_source_index']];c=cw[r['census_source_index']]
 unchanged=all(r[k]==o[k]for k in ['address','rebuild_identity','allocation_sha256','allocation_x','allocation_z','floor_y','source_origin_world_xyz','source_yaw_godot','historical_door_marker_xz','entry_persistent_id','bath_persistent_id','view_target_family','view_target_id','aperture_contract'])
 assert unchanged and c['house']==P['house_id'] and c['historical_bed_anchor_markers']==[]
 assert [x['unit_slot_key']for x in r['anchor_bindings']]==c['proposed_rest_slot_ids']
 for i,b in enumerate(r['anchor_bindings']):
  assert b['unit_anchor_index']==b['prototype_anchor_index']==i
  q=np.array(source[r['source_recipe_key']]['markers']['datums'][b['prototype_marker_name']]);a=r['source_yaw_godot'];ox,oy,oz=r['source_origin_world_xyz'];world=[ox+q[0]*math.cos(a)-q[1]*math.sin(a),oy+q[2],oz-q[0]*math.sin(a)-q[1]*math.cos(a)];err=float(np.max(np.abs(np.array(world)-b['world_xyz'])));assert err<1e-5;slots.append({'unit':r['address'],'slot':b['unit_slot_key'],'ordinal':i,'evaluated_world_error_m':err})
 for f in source[r['source_recipe_key']]['markers']['fixture_positions']:
  x,y,z=f['source_xyz'];fy=r['floor_y']+z;assert fy>r['floor_y']+1.4;world_fixtures.append({'unit':r['address'],'fixture':f['datum'],'local':f['source_xyz'],'world_y':fy,'pass':True})
 row_checks.append({'source_index':r['census_source_index'],'unit':r['address'],'all_identity_allocation_view_fields_unchanged':unchanged})
assert len(slots)==221 and len({s['slot']for s in slots})==221
assert all(p['pass']for p in profile)and all(h['matches']for h in hash_checks)
report={'status':'PASS_SOURCE_IDENTITIES_AND_PROFILE','units':85,'rest_slots':221,'prototype_count':8,'adjacency_edges':len(P['adjacency_edges']),'adjacency_pass':P['adjacency_pass'],'row_checks':row_checks,'slots':slots,'fixture_world_elevations':world_fixtures,'profile_checks':profile,'saved_file_hash_checks':hash_checks,'preserved_existing_owners':owner_checks,'historical_coordinates_changed':0,'main_ceiling_segments_preserved':48,'runtime_acceptance':False,'whole_house_scope':P['whole_house_scope']}
(R/'qa/IDENTITY_PROFILE_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
# D17 retained polygons are a different proposal. Never use the historical floor
# rectangle or invent a new court opening to make a fitted room appear possible.
d17path=R.parent/'inputs/D17_LUXURY_HOUSES_PROPOSAL.json';d17=json.loads(d17path.read_text());d17units=[r for r in d17['replanned_standard_units']if r['house']==P['house_id']];vips=[r for r in d17['replacements']if r['house']==P['house_id']];rows=[]
standard=[p for p in P['prototypes']if p['historical_class']=='standard']
for n,d in enumerate(d17units):
 c=cw[d['source_envelope_index']];poly=Polygon(d['proposed_floor_boundary']);minx,minz,maxx,maxz=poly.bounds;cfg=standard[n%len(standard)];objects=source[cfg['address']]['objects'];origin=[maxx-.05,102,(minz+maxz)/2];yaw=math.pi/2
 def xz(v):return[origin[0]-v[1],origin[2]-v[0]]
 allverts=np.concatenate([o['vertices']for o in objects]);allpoints=[xz(v)for v in allverts]
 from shapely.geometry import MultiPoint
 footprint=MultiPoint(allpoints).convex_hull;outside=footprint.difference(poly).area
 guest_footprint=unary_union([MultiPoint([xz(v)for v in o['vertices']]).convex_hull for o in objects if o['assembly_member']not in ['EntryDoor']])
 # A prior 18m-wide central court intent does not constitute built receiving
 # enclosure. Test the available westward strip without claiming it is a void.
 aperture=[origin[0]-12.78,origin[2]];ray=LineString([aperture,[minx-17.9,origin[2]]]);obstacles=[]
 for v in vips:
  q=Polygon(v['proposed_floor_boundary']);a=ray.intersection(q).length
  if a>1e-5:obstacles.append({'proposal_key':v['proposal_key'],'intersection_length_m':a})
 other_overlap=[]
 for other in d17units:
  if other is d:continue
  ar=footprint.intersection(Polygon(other['proposed_floor_boundary'])).area
  if ar>1e-6:other_overlap.append({'source_index':other['source_envelope_index'],'area_m2':ar})
 slots17=[]
 for i,a in enumerate(cfg['bed_anchors']):
  x,y,z=a['source_xyz'];slots17.append({'slot_id':c['proposed_rest_slot_ids'][i],'ordinal':i,'old_historical_world_xyz':None,'old_coordinate_evidence':'No recovered historical coordinate or earlier fitted D17 rest coordinate','new_proposed_source_xyz':a['source_xyz'],'new_proposed_world_xyz':[origin[0]-y,102+z,origin[2]-x],'new_source_yaw':a['source_yaw'],'status':'Unbuilt conditional fit only; not current registered or 85-unit production placement'})
 rows.append({'source_index':d['source_envelope_index'],'unit_id':c['proposed_runtime_id'],'historical_stable_id':c['historical_persistent_id'],'source_allocation':d['source_allocation'],'exact_proposed_floor_boundary':d['proposed_floor_boundary'],'floor_y':102,'trial_prototype':cfg['address'],'trial_origin_world_xyz':origin,'trial_yaw_godot':yaw,'full_source_convex_hull_outside_polygon_m2':outside,'excluding_entry_door_outside_polygon_m2':guest_footprint.difference(poly).area,'neighbor_standard_overlaps':other_overlap,'westward_reserved_strip_ray_blockers':obstacles,'trial_aperture_world_xz':aperture,'trial_window_view':'Westward 18m-wide central court intent; receiving garden/enclosure/route is unbuilt and unverified','fit_status':'HOLD_NO_ADOPTION','blocking_conditions':['Full source footprint and retained door/interface must fit its exact polygon or explicit receiving access easement','D17 receiving garden, ceiling/roof, service/access and privacy geometry are not authored or verified','Built Star Atlas D12-D14 court and lift do not authorize any D15-D17 void extension'],'proposed_rest_slot_bindings':slots17})
assert len(rows)==10
(R/'D17_STANDARD_FIT_REPORT.json').write_text(json.dumps({'status':'SEPARATE_CONDITIONAL_FIT_REPORT_ALL_10_HELD','source_sha256':sha(d17path),'exact_units':10,'proposed_rest_slots':20,'adopted_or_added_to85':0,'rows':rows,'full_house_totals_unchanged':{'standard':44,'family':51,'specialty':46,'VIP':7,'total':148},'opening_through_D15_D17_created':False},indent=2)+'\n')
print('IDENTITY_PROFILE_PASS',len(slots),len(world_fixtures),'D17_HELD',len(rows),'D17_outside',[(r['source_index'],round(r['full_source_convex_hull_outside_polygon_m2'],4),round(r['excluding_entry_door_outside_polygon_m2'],4))for r in rows])
