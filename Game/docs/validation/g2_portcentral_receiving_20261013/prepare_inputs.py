from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).parent;O=P.parent/'g2_remaining_five_pairs_20261013';T=P/'import/Game';G=Path('/workspace/astraea-protected-integration-20261012/Game');key='port_central_upper_house'
for rel in ['assets/group2_completion/'+key+'.glb','assets/group2_care_programmes/CARE_'+key+'_r001.glb','data/group2_completion/contracts/'+key+'.json','data/group2_completion/LIGHTING_ADDENDUM.json','data/group2_care_programmes/FITTINGS_r001.json','scripts/group2_care_programmes/package.gd']:
 q=T/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(O/'inputs/Game'/rel,q)
shutil.copyfile(O/'native'/f'{key}.blend',P/'native'/f'{key}.blend')
shutil.copyfile(O/'guard_window_successor.gd',P/'guard_window_successor.gd')
plan=json.loads((P/'PORTCENTRAL_FRAME_PLAN.json').read_text());plan['receiver_root']='D15_D17_StarAtlasUpper_WIP';plan['receiver_model']=plan['source_model'];plan['receiver_sha256']=hashlib.sha256((G/'assets/models'/plan['source_model']).read_bytes()).hexdigest();plan['mask']=plan['guard_mask'];plan['fixtures']=next(r for r in json.loads((T/'data/group2_completion/LIGHTING_ADDENDUM.json').read_text())['rows']if r['key']==key)['fixtures'];plan['care']=next(r for r in json.loads((T/'data/group2_care_programmes/FITTINGS_r001.json').read_text())['rows']if r['key']==key);plan['model_pins']={str(q.relative_to(T)):hashlib.sha256(q.read_bytes()).hexdigest()for q in(T/'assets').rglob('*.glb')};q=T/'data/group2_portcentral_receiving_20261013/PLAN.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(plan,indent=2)+'\n')
(T/'project.godot').write_text('[application]\nconfig/name="New portcentral sourcepair/frame import"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\nrenderer/rendering_method.mobile="gl_compatibility"\n')
print('PASS_SELECTED_ORIGINAL_PORTCENTRAL_PAIR_STAGED')
