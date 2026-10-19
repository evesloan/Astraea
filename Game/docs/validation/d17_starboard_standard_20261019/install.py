from pathlib import Path
import json,hashlib,re,subprocess,shutil
R=Path('/workspace/Astraea');E=Path('/workspace/d17-starboard-integration');D=R/'BlenderCatalogue/assets/d17_starboard_standard_20261019';V=R/'Game/docs/validation/d17_starboard_standard_20261019';p=json.load(open(D/'PLAN.json'));c=json.load(open(E/'CANDIDATE.json'));assert c['status']=='PASS';assert json.load(open(D/'EXACT_NATIVE_AUDIT.json'))['status']=='PASS'
classified=[]
for row in c['preflight_contacts_unclassified']:
 n=row['part'];assert row['category']!='source_bearing_pier'
 if n.startswith('SBS_Floor0_'):reason='New fore plate receives retained below-top rail/post stump at Z-16; source plate ends there. No pre-existing public slab duplicated.';allowed=['ReceivingFrame/RoomStaticContacts']
 elif n.startswith('SBS_Floor1_'):reason='Aft plate receives existing fascia below the bounded1mm sill; original compiler floor begins at X78.5.';allowed=['CR_Batch_approach_ivory_enamel/StaticContact']
 elif n.startswith(('SBS_Fore_Hanger','SBS_Fore_InnerLast')):reason='New fore endpoint frame/guard joins retained rail at Z-16; bounded successors remove only the walking aperture.';allowed=['ReceivingFrame/RoomStaticContacts']
 elif n.startswith('SBS_BranchFloorBeam'):reason='Declared positive slab/fascia receiving overlap at X78.5..78.62 and Y101.76..101.8.';allowed=['D17_connected_house_floor_00/','CR_Batch_approach_ivory_enamel/StaticContact']
 elif n.startswith('SBS_BranchRoofBeam'):reason='Positive contact with retained west commons-rooted roof beam at X78.3..78.42,Y105.98..106.26.';allowed=['CR_Batch_approach_warm_walnut/StaticContact']
 elif n.startswith(('SBS_BranchGuard','SBS_BranchHanger')):reason='Branch terminal joins exact retained approach fascia/guard successor and roof beam; source structural hanger at Z18 remains outside opening.';allowed=['CR_Batch_approach_'+s+'/StaticContact'for s in ['warm_walnut','ivory_enamel','champagne_metal','HouseSmokedGlass']]
 else:raise AssertionError(n)
 assert all(any(t in h for t in allowed)for h in row['hits']),row
 classified.append(dict(row,classification=reason))
(V/'CONTACT_CLASSIFICATION.json').write_text(json.dumps({'status':'CLASSIFIED_RECEIVING_JOINTS','rows':classified,'all_lower_pier_volumes_clear':True,'room_envelopes_clear':9,'scope':'Exact candidate preflight receiving contacts; no primary structural capacity acceptance'},indent=2)+'\n')
for name in ['CANDIDATE.json','PREFLIGHT.json','check.gd','candidate-r002.log','native-audit.log']:shutil.copy2(E/name,V/name)
f=p['structure_file'];dest=R/'Game/assets/models';template=(R/'Game/assets/family_d15_receiving_20261016/FAMILY_D15_STAFF_RECEIVING_r001.glb.import').read_text();old='FAMILY_D15_STAFF_RECEIVING_r001.glb';s=re.sub(r'^uid=.*\n','',template,flags=re.M).replace('assets/family_d15_receiving_20261016/','assets/models/').replace(old,f).replace('8a57d62330ea15507459ed43b4a812de',hashlib.md5(('res://assets/models/'+f).encode()).hexdigest());(dest/(f+'.import')).write_text(s)
project=R/'Game/project.godot';original=project.read_bytes();assert hashlib.sha256(original).hexdigest()=='42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0'
try:
 project.write_bytes(original+b'\n[filesystem]\nimport/blender/enabled=false\n')
 with (E/'import.log').open('w')as log:result=subprocess.run(['godot','--headless','--editor','--path','Game','--import'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0
finally:project.write_bytes(original)
p['active']=True;p['runtime_status']='Installed physical WIP pending installed check; guest routes only, service operations and full acceptance open.'
for path in [D/'PLAN.json',R/'Game/data/architecture/D17_STARBOARD_STANDARD_CANDIDATE_20261019.json']:path.write_text(json.dumps(p,indent=2)+'\n')
ship=R/'Game/scripts/ship.gd';s=ship.read_text();needle='\tload("res://scripts/family_d15_receiving_20261016/package.gd").build(self)';assert s.count(needle)==1 and 'd17_starboard_standard_20261019'not in s;ship.write_text(s.replace(needle,needle+'\n\t# Approved retained D17 starboard reservations, physical receiving only.\n\tload("res://scripts/d17_starboard_standard_20261019/package.gd").build(self)'))
print('Imported r002 and added default-scene hook; installed check required.')
