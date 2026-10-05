"""Register only the verified new family; all prior catalogue entries remain byte-equivalent data."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-CMD-001';FAMILY='central_crown';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=R/(AID+'.manifest.json');m=json.loads(mp.read_text());qa=json.loads((R/'qa/source_export_validation.json').read_text());assert qa['source_sha256']==m['source_sha256']==sha(R/m['source']);assert qa['export_sha256']==m['export_sha256']==sha(R/m['export'])
m.update({'status':'Source/export, fitted door sweeps, source lens exits and architectural contact checks pass; runtime adoption and visual acceptance remain integration-owned.','validation':'qa/source_export_validation.json','independent_construction_review':'qa/independent_crown_construction_review.json','tie_source_interfaces':'qa/crown_tie_source_interfaces.json','runtime_batch_extent_blender_xyz_m':qa['max_runtime_dimensions_blender_xyz_m'],'protected_prior_design_count':159})
mp.write_text(json.dumps(m,indent=2)+'\n');p=C/'catalogue_manifest.json';d=json.loads(p.read_text());entries=d['assets'];old=[a for a in entries if a['catalogue_id']==AID];assert not old or(len(old)==1 and old[0]['family']==FAMILY)
entry={'catalogue_id':AID,'name':m['name'],'family':FAMILY,'source':str((R/m['source']).relative_to(C)),'export':str((R/m['export']).relative_to(C)),'manifest':str(mp.relative_to(C)),'source_sha256':m['source_sha256'],'export_sha256':m['export_sha256'],'evaluated_triangles':m['triangles'],'batch':'66','adopted_game_instances':old[0].get('adopted_game_instances',0)if old else 0,'status':m['status']}
if old:entries[entries.index(old[0])]=entry
else:entries.append(entry)
assert len({a['catalogue_id']for a in entries})==len(entries);d['unique_authored_asset_count']=len(entries);d['status']=f"{len(entries)} registered designs; presence is not room completion or final art";p.write_text(json.dumps(d,indent=2)+'\n');print('Registered',AID,'catalogue designs',len(entries))
