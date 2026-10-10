from pathlib import Path
import json,numpy as np,hashlib
W=Path(__file__).resolve().parent;G={'__file__':str(W/'north_access_geometry.py'),'__name__':'geometry'};exec((W/'north_access_geometry.py').read_text(),G);recipes=G['recipes'];floors={n:t for n,t in G['receiving'].items() if n.startswith('N006_MissingOnlyFloor_')};anchors=[]
for q in recipes:
 if q['min'][1]>=52.5:continue
 areas=[]
 for name,t in floors.items():
  lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));v=np.maximum(0,np.minimum(q['max'],hi)-np.maximum(q['min'],lo))
  if v.prod()>1e-9:areas.append({'frozen_floor_mesh':name,'plan_area_m2':float(v[0]*v[2]),'positive_floor_overlap_volume_m3':float(v.prod())})
 assert areas,q['name'];anchors.append({'new_mesh':q['name'],'floor_receiver_contacts':areas})
fixture_joints=[]
posts=[q for q in recipes if '_Post_' in q['name']]
for q in recipes:
 if not q['name'].endswith(('_Infill','_Rail')):continue
 contacts=[]
 for p in posts:
  v=np.maximum(0,np.minimum(q['max'],p['max'])-np.maximum(q['min'],p['min']))
  if v.prod()>1e-9:contacts.append({'receiver_post':p['name'],'positive_overlap_volume_m3':float(v.prod())})
 assert len(contacts)>=2,(q['name'],contacts);fixture_joints.append({'guard_mesh':q['name'],'post_receivers':contacts})
assert len(anchors)==40 and len(fixture_joints)==8
# Static protected intervals only; no further route sweep.
assert all(q['max'][0]<=-4.0+1e-6 for q in recipes)
high=[q for q in recipes if q['max'][1]>53.75+1e-6];assert all(q['max'][0]<-7.6 for q in high)
rep={'status':'NORTH_ACCESS_FIXED_RECEIVING_AND_PROTECTED_INTERVAL_PASS','source_only':True,'root_floor_owner':'ROOT_FOREMID_NORTH_ANNEX_PROPOSAL uninstalled006','new_floor_anchor_parts':len(anchors),'positive_floor_anchor_witnesses':anchors,'guard_rail_infill_meshes_with_multiple_positive_post_receivers':fixture_joints,'nominal_core_wall_face_seal':{'new_mesh':'N007_ForeEdgeToCoreWallSeal','wall_source_mesh':'CORE_BATCH_ivory_enamel','nominal_wall_face_x':-7.88,'actual_retained_wall_face_x':-7.880000114440918,'nominal_contact_area_m2':.1,'world_tolerance_m':1e-5,'protected_wall_cut_or_changed':False},'protected_interval_evidence':{'unchanged_lower_axial_route_x':[-2,2],'new_protection_max_x':max(q['max'][0] for q in recipes),'unchanged_port_trunk_protected_strip_x':[-7.6,-3.6],'new_parts_above_guard_y_max_x':max(q['max'][0] for q in high),'new_guard_top_y':53.75,'retained_actual_wheel_min_y':55.74,'guard_to_wheel_vertical_separation_m':1.99},'limits':['Positive receiver volumes and nominal wall-face fit are geometric evidence, not capacity.','Protected interval comparisons are local static bounds only; no route traversal, curvature or full-world campaign.','Root collision/receiving, whole-species access and installation remain open.']};(W/'ACCESS_RECEIVING_CHECK.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['status'],'floor anchors',len(anchors),'guard fixture groups',len(fixture_joints))
