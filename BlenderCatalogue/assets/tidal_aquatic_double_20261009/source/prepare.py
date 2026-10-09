from pathlib import Path
import json,copy,hashlib
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');B=R/'BlenderCatalogue/assets/tidal_aquatic_singles_20261009';O=R/'BlenderCatalogue/assets/tidal_aquatic_double_20261009';(O/'source').mkdir(parents=True,exist_ok=True);u=O/'units/394';u.mkdir(parents=True,exist_ok=True);(u/'source').mkdir(exist_ok=True)
p=json.load(open(B/'units/364/PLAN.json'));row=next(q for q in json.load(open(R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json'))['records']if q['source_envelope_index']==394);dz=-18.8
for part in p['parts']:
 part['name']=part['name'].replace('TA364','TA394')
 for v in part['verts']:v[2]+=dz
# Fit existing indexed editable shell parts into bespoke double layout.
def reshape(part,lo,hi):
 oldlo=[min(v[i]for v in part['verts'])for i in range(3)];oldhi=[max(v[i]for v in part['verts'])for i in range(3)]
 for v in part['verts']:
  for i in range(3):v[i]=lo[i]+(v[i]-oldlo[i])/(oldhi[i]-oldlo[i])*(hi[i]-lo[i])
for part in p['parts']:
 n=part['name']
 if n.endswith('WashWest'):reshape(part,[-38.5,88.5,-493.38],[-38.28,91.9,-491.1])
 elif n.endswith('WashSouth_0'):reshape(part,[-39.325,88.5,-491.25],[-38.5,91.9,-491.05])
 elif n.endswith('WashSouth_1'):reshape(part,[-41.7,88.5,-491.25],[-40.675,91.9,-491.05])
 elif n.endswith('WashLintel'):reshape(part,[-40.675,90.78,-491.25],[-39.325,91.9,-491.05])
 elif 'PrivacyScreen' in n:reshape(part,[-40.3,88.5,-488.9],[-39.4,90.1,-487.6])
 elif 'Storage' in n:
  for v in part['verts']:v[0]-=4.25;v[2]-=.0
 elif 'Activity' in n:
  for v in part['verts']:v[0]+=2.65;v[2]-=3.4
 elif 'WindowSeat' in n:
  for v in part['verts']:v[2]-=3.95
p['allocation']=row;p['composition_variant']='paired_aquatic_cradles_with_north_dry_activity_and_west_wet_service';p['components']=[{'catalogue_id':'AST-RST-AQ-001','name':'AquaticRestCradle'+str(i+1),'world_origin':[x,88.5,-488.75],'godot_yaw':0,'rest_slot_id':row['proposed_rest_slot_ids'][i]}for i,x in enumerate([-36.6,-32.3])]
for d in p['doors']:
 d['world_origin'][2]+=dz;d['identity']=row['proposed_runtime_id']+(':entry'if d['name']=='EntryDoor'else':wash')
 if d['name']=='WashDoor':d['world_origin']=[-40,88.5,-491.15]
p['source_fixtures']=[{'catalogue_id':'AST-SAN-001','origin':[-38.6,88.5,-491.85],'yaw':3.141592653589793},{'catalogue_id':'AST-SAN-002','origin':[-39.75,88.5,-492.9],'yaw':0},{'catalogue_id':'AST-SAN-003','origin':[-40.85,88.5,-492.6],'yaw':0}]
for q in p['lights']:q['position'][2]+=dz;q['name']=q['name'].replace('TQ102','TA394')
for k in ['min','max']:p['guard_opening_world'][k][2]+=dz
p['limits'][1]='Two retained proposed rest reservation IDs; no additional guest unit or capacity change.'
p['reference_review']='Master v0.3 chapters6,7,21,32 and current overlays re-read; Luxury_single_space_view_8079.jpg pixels inspected. Fitted activity/storage and privacy principles, court view retained.'
(u/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
old=json.load(open(B/'BATCH_PLAN.json'));cuts=old['entry_cuts_including_retained_102']+[p['guard_opening_world']];plan={'schema':'astraea.tidal_aquatic_double.v1','source_house_sha256':old['source_house_sha256'],'rooms':[{'source_index':394,'runtime_id':row['proposed_runtime_id'],'plan':'units/394/PLAN.json'}],'entry_cuts_including_retained_102':cuts,'limits':p['limits']};(O/'BATCH_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');(O/'source/prepare.py').write_text(Path(__file__).read_text());(O/'source/build.py').write_text((B/'source/build.py').read_text());print('Prepared bespoke double394 source plan')
