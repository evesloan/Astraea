from pathlib import Path
import json,hashlib
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));U=json.load(open(R/'Game/data/architecture/STAR_ATLAS_UNITS.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parts=[];supports=[];lower=[]
def cube(name,lo,hi,category):
 vs=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]];parts.append({'name':name,'verts':vs,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'category':category,'runtime_collision':True})
regions=[]
for file in ['CENTRAL_RESIDENTIAL_STREETS.json']:
 regions+=json.load(open(R/'Game/data/architecture'/file))['regions']
for file in ['structural_meshes.json','received_structural_meshes.json']:regions+=json.load(open(R/'Game/data/generated'/file))['regions']
def owner(toe):
 matches=[r for r in regions if float(r['floor_y'])==88.5 and unary_union([Polygon(t)for t in r['triangles']]).buffer(1e-7).covers(toe)];assert len(matches)==1,(toe.bounds,[r['id']for r in matches]);return matches[0]['id']
for side,sign in [('North',-1),('South',1)]:
 lo,hi=sorted([82.6*sign,90*sign]);cube(f'SA_D15_{side}_FourthStreetFloor',[-86.05,92.76,lo],[-81.95,93,hi],'D15_street_extension_floor')
 for x in [-85.8,-82.2]:cube(f'SA_D15_{side}_FourthLongitudinal_{x}',[x-.1,92.6,lo],[x+.1,92.76,hi],'D15_bridge_longitudinal_frame')
 end=90*sign;cube(f'SA_D15_{side}_FourthTerminalGuard',[-86.05,93,end-.035],[-81.95,94.1,end+.035],'guard')
 a,b=sorted([82.6*sign,82.8*sign])
 # Both banks are now fitted; guards only at the0.2m source gap, never across entries.
 for edge in ['East','West']:
  xx=-82.02 if edge=='East'else-86.05;cube(f'SA_D15_{side}_Fourth{edge}GapGuard',[xx,93,a],[xx+.07,94.1,b],'guard')
 for n,d in enumerate([83.1,86.4,89.7]):
  zz=d*sign;xx=-85.8;toe=box(xx-.1,zz-.1,xx+.1,zz+.1);o=owner(toe);cube(f'SA_D15_{side}_SharedBankPier_{n}',[xx-.1,88.5,zz-.1],[xx+.1,92.6,zz+.1],'D14_street_to_D15_shared_bank_pier');supports.append({'name':parts[-1]['name'],'position':[xx,88.5,zz],'full_toe_area_m2':.04,'owner':o,'deck':'D14'})
  cube(f'SA_D15_{side}_SharedBankCrossbeam_{n}',[-98.95,92.6,zz-.1],[-69.05,92.76,zz+.1],'D15_both_bank_room_and_street_crossbeam')
for room in P['rooms']:
 idx=room['allocation']['source_envelope_index'];row=room['allocation'];z=sum(row['allocation_z'])/2;xlo,xhi=row['allocation_x'];u=room['below_unit'];proto=next(p for p in U['prototypes']if p['key']==u['source_recipe_key']);assert sha(R/proto['editable_source'])==proto['editable_source_sha256'];lower.append({'source_index':idx,'owner':u['rebuild_identity'],'allocation_sha256':u['allocation_sha256'],'native_source':proto['editable_source'],'native_sha256':proto['editable_source_sha256'],'runtime_source':proto['model_file'],'runtime_sha256':proto['sha256'],'origin':u['source_origin_world_xyz'],'yaw':u['source_yaw_godot'],'persistent_structure_only':True,'rendering_policy':'Persistent hidden duplicate structural contacts; original rendering remains residency managed','selected_prefixes':['SUI_Floor','SUI_Ceiling_','SUI_Wall_'],'contacts':room['receiving_contacts']})
 for v in [-3.35,-1.7,0,1.7,3.35]:cube(f'SA{idx}_D15FloorJoist_{v}',[xlo,92.6,z+v-.08],[xhi,92.76,z+v+.08],'D15_room_floor_joist')
 for x in [xlo+.1,(xlo+xhi)/2,xhi-.1]:cube(f'SA{idx}_D15RoomTie_{x}',[x-.1,92.6,z-3.5],[x+.1,92.76,z+3.5],'D15_room_transverse_tie')
Q={'schema':'astraea.star_atlas_specialty_receiving.v1','base_commit':'ff420d2838f4cb02ba5d99adef28035c888beab2','model_file':'StarAtlasSpecialtyFourthReceiving.glb','parts':parts,'support_toes':supports,'lower_structural_owners':lower,'source_pins':{f:sha(R/f)for f in ['Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']},'culling_preserved':True,'new_units':0,'new_source_ids':0,'structural_capacity_accepted':False,'removed_terminal_guard_names':['SA_D15_North_ThirdTerminalGuard','SA_D15_South_ThirdTerminalGuard'],'receiving_model_preimage_sha256':sha(R/'Game/assets/models/StarAtlasSpecialtyThirdReceiving.glb'),'new_street_floor_area_m2':60.68,'geometric_load_path':'Six shared full-toe piers on existing D14 street -> crossbeams over both room banks and street -> joists/room floors.16 new posts also touch exact preserved lower roofs.88 lower source structural objects remain persistent with60 exact wall-base rails. No invented D13 floor, duplicate bank piers or structural capacity certificate.'};(W/'RECEIVING_PLAN.json').write_text(json.dumps(Q,indent=2)+'\n');print('Prepared',len(parts),'frame members with',len(supports),'shared D14 floor toes')
