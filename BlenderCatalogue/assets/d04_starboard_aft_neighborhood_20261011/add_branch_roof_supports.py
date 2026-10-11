from pathlib import Path
import json,copy,ast,hashlib
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_starboard_aft_neighborhood_20261011';P=json.load(open(W/'RUNTIME_PLAN.json'));raw=(W/'RUNTIME_PLAN.json').read_bytes();(W/'RECEIVING_REVISION002_PREIMAGE.json').write_bytes(raw)
parts=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];text=(R/'BlenderCatalogue/assets/d04_port_forward_receiving_20261010/prepare.py').read_text()
for n in ast.parse(text).body:
 if isinstance(n,ast.FunctionDef)and n.name in ['add','cube']:exec(compile(ast.get_source_segment(text,n),'<reviewed original box helper>','exec'))
for z in [403.65,406.75]:
 cube(f'SA_PublicArrivalRoofBeam_{z}',[4,20.18,z-.12],[44,20.48,z+.12])
 for i,x in enumerate([8.5,20,32]):cube(f'SA_PublicArrivalRoofPier_{z}_{i}',[x-.12,16.5,z-.12],[x+.12,20.48,z+.12],'warm_walnut','roof_pier')
for z in [367.35,372.45]:
 cube(f'SA_CommonsLinkRoofBeam_{z}',[44,20.18,z-.12],[63,20.48,z+.12])
 for i,x in enumerate([50,56,62.6]):cube(f'SA_CommonsLinkRoofPier_{z}_{i}',[x-.12,16.5,z-.12],[x+.12,20.48,z+.12],'warm_walnut','roof_pier')
P['assemblies']['CombinedStructure']+=parts
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'RECEIVING_ROOF_SUPPORT_INPUT.json').write_text(json.dumps({'prior_runtime_sha256':hashlib.sha256(raw).hexdigest(),'new_owned_roof_support_members':parts,'original110_bearing_sites_unchanged':True,'new_roof_piers_aligned_above_original_verified_candidate_bearings':12,'native_revision':'CombinedStructure_r002','homes_and_corrected_commons_unchanged':True,'load_certificate_accepted':False},indent=2)+'\n')
print('Added roof members',len(parts))
