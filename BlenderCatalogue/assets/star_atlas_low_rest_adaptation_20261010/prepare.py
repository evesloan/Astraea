from pathlib import Path
import json,hashlib,copy,math
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
H=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'))
F=json.load(open(R/'BlenderCatalogue/assets/star_atlas_eight_habitat_20261010/PHYSICAL_PLAN.json'))
lanes={k:json.load(open(R/f'Game/data/architecture/STAR_ATLAS_SPECIALTY_{k.upper()}.json'))for k in ['first','second']}
author={k:json.load(open(R/f'BlenderCatalogue/assets/star_atlas_specialty_{k}_20261010/PLAN.json'))for k in lanes}
pins={}
for lane in lanes:
 for room in lanes[lane]['rooms']:
  idx=room['allocation']['source_envelope_index']
  if idx in [443,467,491]:
   for p in [R/'Game/assets/models'/room['model_file'],R/f'BlenderCatalogue/assets/star_atlas_specialty_{lane}_20261010'/f'StarAtlasSpecialty_{idx}.blend',R/'BlenderCatalogue/assets/star_atlas_eight_habitat_20261010'/f'StarAtlasHabitatAssembly_{idx}.blend']:
    pins[str(p.relative_to(R))]=sha(p)
for p in [R/'Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json',R/'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',R/'BlenderCatalogue/catalogue_manifest.json',R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json',R/'BlenderCatalogue/references/intimate/image(20261002-000722).png',R/'BlenderCatalogue/references/aquatic/image(20261001-035517).png']:
 pins[str(p.relative_to(R))]=sha(p)
sources={a['catalogue_id']:a for p in author.values()for a in p['sources']}
def at(v,rest):
 cy,sy=math.cos(rest['yaw']),math.sin(rest['yaw']);p=rest['position'];return[p[0]+v[0]*cy+v[2]*sy,p[1]+v[1],p[2]-v[0]*sy+v[2]*cy]
def cube(name,lo,hi,role='ivory_enamel'):
 return dict(name=name,verts=[[x,y,z]for z in [lo[2],hi[2]]for y in [lo[1],hi[1]]for x in [lo[0],hi[0]]],faces=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],role=role,runtime_collision=True,category='habitat_adaptation')
rooms=[];adaptations=[]
for idx,species,key,template in [(443,'Mantelids','AST-RST-QC-001',413),(467,'Baelins','AST-RST-AQ-001',419),(491,'Mantelids','AST-RST-QC-001',413)]:
 lane='first'if idx==443 else'second';old=next(r for r in author[lane]['rooms']if r['allocation']['source_envelope_index']==idx)
 runtime=next(r for r in lanes[lane]['rooms']if r['allocation']['source_envelope_index']==idx)
 # Runtime successors inherit the already guarded production room's authoring parts.
 room=copy.deepcopy(old);room['model_file']=f'StarAtlasSpecialty_{idx}_CanonAdaptation.glb'
 rest=next(b for b in room['components']if b['name']=='ReservedRestSupport');rest['catalogue_id']=key
 h=next(r for r in H['rooms']if r['source_envelope_index']==idx);t=next(r for r in H['rooms']if r['source_envelope_index']==template)
 h.update(rest_source=copy.deepcopy(rest),reference_key=key,proposed_design_species=species,design_species_assignment={'species':species,'status':'local architectural design target only'},design_choice_status='canon-supported alien architectural proposal; no occupant or biological certification',environment_state='alien_specialty_physical_adaptation_pending_witnesses',species_ready=False,alien_body_compatibility_accepted=False)
 ref=next(r for r in H['references']if r['key']==key)
 h['rest_contacts_world']=[at(v,rest)for v in ref['contact_probes']];h['approach_world']=at([0,0,-2.4 if species=='Mantelids'else-2.7],rest)
 if species=='Mantelids':
  delta=[rest['position'][i]-t['rest_source']['position'][i]for i in range(3)]
  for q in F['parts']:
   if q['name'].startswith('SA413_'):
    n=copy.deepcopy(q);n['name']=n['name'].replace('SA413_','SA'+str(idx)+'_');n['verts']=[[v[i]+delta[i]for i in range(3)]for v in n['verts']];n['role']=n.pop('material');n['category']='quiet_cocoon_enclosure';room['parts'].append(n)
  h['privacy_door']=copy.deepcopy(t['privacy_door']);h['privacy_door']['position']=[v+delta[i]for i,v in enumerate(t['privacy_door']['position'])];h['privacy_door']['persistent_id']=h['unit_proposal_id']+':cocoon_privacy'
  h['quiet_zone']=copy.deepcopy(t['quiet_zone']);h['quiet_zone']['center']=[v+delta[i]for i,v in enumerate(t['quiet_zone']['center'])]
  h['architectural_adaptation']='Closed lined cocoon with roof, jambs and reused physical privacy door; retained library/activity edge stays outside the rest enclosure. Acoustic/molt behavior held.'
 else:
  h['wet_cells_local']=copy.deepcopy(t['wet_cells_local']);h['wet_volume_m3']=t['wet_volume_m3'];h['wet_probes_world']=[at(v,rest)for v in [p['verts'][0]for p in next(r for r in F['references']if r['key']==key)['parts']if 'Head'not in p['name']]]
  removed=[q['name']for q in room['parts']if 'LowLibrary'in q['name']or'LowRestBookPrivacyReturn'in q['name']]
  room['parts']=[q for q in room['parts']if q['name']not in removed]
  # Enclosed twin care shelves take the former north low-library footprint.
  room['parts'] += [cube('SA467_CareCabinet_Base',[-76.25,93,53.45],[-74.45,93.12,54]),cube('SA467_CareCabinet_Back',[-76.25,93.12,53.45],[-74.45,94.32,53.51],'warm_walnut'),cube('SA467_CareCabinet_Left',[-76.25,93.12,53.51],[-76.17,94.32,54],'warm_walnut'),cube('SA467_CareCabinet_Right',[-74.53,93.12,53.51],[-74.45,94.32,54],'warm_walnut'),cube('SA467_CareCabinet_Shelf',[-76.17,93.7,53.51],[-74.53,93.76,54],'teal_weave'),cube('SA467_CareCabinet_Top',[-76.25,94.32,53.45],[-74.45,94.38,54]),cube('SA467_WetPrivacyBlade',[-74.3,93,54.02],[-70.8,95.15,54.1],'teal_weave')]
  h['service_stance_world']=[-75.35,93,54.75];h['service_cabinet_status']='Empty physical clean-product/towel staging shelves; exact cleaner compatibility, stock, trail and chemistry operations held'
  h['architectural_adaptation']='Low nest replaced by source-defined immersed rest basin, conservative wet detector, private dry transfer edge, north privacy blade and empty enclosed care shelves.';h['superseded_source_meshes']=removed
 h['assembly_native']=str((W/f'StarAtlasSpecialty_{idx}.blend').relative_to(R));h.pop('assembly_native_sha256',None)
 room['proposed_design_species']=species;room['design_adaptation']=h['architectural_adaptation'];rooms.append(room)
 adaptations.append({'index':idx,'species':species,'rest_catalogue_id':key,'unit_proposal_id':h['unit_proposal_id'],'rest_slot_ids':h['rest_slot_ids'],'allocation_sha256':h['allocation_sha256'],'capacity':1,'old_model':runtime['model_file'],'new_model':room['model_file'],'rest_contacts_world':h['rest_contacts_world'],'approach_world':h['approach_world']})
assert all(a['capacity']==1 and len(a['rest_slot_ids'])==1 for a in adaptations)
H['proposed_choices']=['Mantelid quiet-cocoon design proposals:413,437,443,491','Baelin aquatic-home design proposals:419,461,467,485','Eight existing single reservations preserved; no Human/Mindo target, population quota, new occupant or canonical rig/operations acceptance']
H['implementation_gate']='Current targets are ordinary local construction choices authorized by owner; canonical rigs/body poses and operations remain separate acceptance gates'
H['status']='low_rest_gap_adapted_to_canon_pending_physical_witnesses'
H['low_rest_adaptation']={'base_commit':'e91c6414bd50014324b2487e8f84c447e7d50a35','authority':'MASTER_CURRENT_APPLICATION Species override; full master chapter6 blocks151-156 and chapter8 blocks177-186; existing one-rest specialty proposals; latest owner delegation','quota_change':0,'capacity_change':0,'new_allocations':0,'new_catalogue_ids':0,'ids_changed':0,'canonical_body_rig_animation_accepted':False,'historical_reconciliation_retained':True,'targets':adaptations}
P=dict(schema='astraea.low_rest_canon_adaptation.v1',base_commit=H['low_rest_adaptation']['base_commit'],rooms=rooms,sources=list(sources.values()),protected_source_pins=pins,adaptations=adaptations,habitat_runtime=H)
write(W/'PLAN.json',P);print('PREPARED',len(rooms),'existing single reservations; no new rooms/rests')
