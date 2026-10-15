from pathlib import Path
import json,struct,hashlib
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');r=json.loads((D/'CANDIDATE_RUNTIME.json').read_text());accepted=[];bad=[];raw=(G/'assets/models/AST-CUL-005_static_003.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);nodes={x.get('name'):x for x in j['nodes']}
for row in r['old_contact_inventory']:
 part=row['part'];expected=set();reason=''
 if part=='Backstage_PositiveHeaderTieCanopy':
  expected={'C005_S_0424','C005_S_0426','C005_S_0428'};reason='200mm positive overlap into exact retained fixed east acoustic wall/header'
  for node in expected:
   x=nodes[node]['extras'];assert x['source_role']=='static_structure'and x['source_owner']=='east'and not x['unpowered_closed_preview'];assert all(k.startswith('east_acoustic_wall_')for k in json.loads(x['source_semantic_ids']))
 elif part=='Backstage_WestLegStringer0_TopFlange':expected={'D11_theater_foundation_05'};reason='Original nonwalking foundation receives the new upper flange'
 elif part=='Backstage_WestLegStringer1_TopFlange':expected={'D11_theater_foundation_06'};reason='Original nonwalking foundation receives the new upper flange'
 elif part in['Backstage_AxialLegStringer0_TopFlange','Backstage_AxialLegStringer1_TopFlange','Backstage_AxialCross1','Backstage_CanopyFoot15','Backstage_CanopyFoot16']or part.startswith('Backstage_AxialFloorUnderlap'):expected={'D11_fore_route'};reason='Bounded below-floor orbaseplate bearing into retained axial slab'
 elif part in['Backstage_CanopyFoot0','Backstage_CanopyFoot1']or part.startswith('Backstage_OriginalFloorUnderlap'):expected={'D11_theater_flat_00'};reason='Bounded below-floor orbaseplate bearing into retained backstage floor'
 for target in row['old_contacts']:
  ok=any('/'+x+'/'in target for x in expected);item={'part':part,'target':target,'meaning':reason}
  (accepted if ok else bad).append(item)
report={'status':'PASS_EXACT_BEARINGS_AND_FIXED_HEADER_TIE'if not bad else'FAIL_UNEXPLAINED_CONTACTS','classified_contacts':accepted,'unexplained_contacts':bad,'source_door_motion_or_compiled_geometry_changed':False,'whole_venue_or_primary_capacity_accepted':False};(D/'CONTACT_CLASSIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(accepted),len(bad));assert not bad,bad
