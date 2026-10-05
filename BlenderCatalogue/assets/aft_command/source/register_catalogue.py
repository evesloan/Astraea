"""Register the new aft kit and only the explicitly authorized central endcap revision."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
protected=json.loads((R/'qa/protected_prior_assets.json').read_text())
for row in protected['assets']:assert sha(C/row['path'])==row['sha256'],row['path']
catalogue_path=C/'catalogue_manifest.json';catalogue=json.loads(catalogue_path.read_text());entries=catalogue['assets']
for old in protected['protected_other_entries']:
    assert [entry for entry in entries if entry['catalogue_id']==old['catalogue_id']]==[old],old['catalogue_id']
review=json.loads((R/'qa/independent_aft_construction_review.json').read_text())
assert review['status']=='PASS_SOURCE_GEOMETRY_PENDING_PARENT_RUNTIME' and not review['findings']
assert review['files']['assets/aft_command/source/AST-CMD-002.blend']==sha(R/'source/AST-CMD-002.blend')
assert review['files']['assets/aft_command/exports/AST-CMD-002.glb']==sha(R/'exports/AST-CMD-002.glb')
materials=json.loads((R/'qa/material_fidelity.json').read_text())
for family,aid,batch in [('central_crown','AST-CMD-001','66'),('aft_command','AST-CMD-002','67')]:
    root=C/'assets'/family;path=root/(aid+'.manifest.json');manifest=json.loads(path.read_text());qa=json.loads((root/'qa/source_export_validation.json').read_text())
    assert manifest['source_sha256']==qa['source_sha256']==sha(root/manifest['source'])==materials[aid]['source_sha256']
    assert manifest['export_sha256']==qa['export_sha256']==sha(root/manifest['export'])==materials[aid]['export_sha256']
    matches=[entry for entry in entries if entry['catalogue_id']==aid]
    assert not matches or(len(matches)==1 and matches[0]['family']==family)
    manifest.update(status='Source/export geometry, UV, materials, actual shared-door sweeps, fixture exits and independent contact review pass; runtime and visual acceptance remain integration-owned.',validation='qa/source_export_validation.json',material_validation='../aft_command/qa/material_fidelity.json',independent_construction_review='../aft_command/qa/independent_aft_construction_review.json',runtime_batch_extent_blender_xyz_m=qa['max_runtime_dimensions_blender_xyz_m'],protected_other_design_count=159)
    if aid=='AST-CMD-001':
        manifest['aft_endcap_interface_revision']={'baseline_commit':'5918f89a9ff913bd6077f2a7464f4bef66292dac','prior_export_sha256':'fd23668ccfe850409708b6e18a1a483f28ba4f7091e4c417069fc9f0e182b604','scope':'Two fitted endcap apertures and two door markers only','diff':'qa/aft_endcap_interface_diff.json'}
    else:
        manifest.update(floor_policy='No duplicate source slabs; parent owns1408m2 compiled extension',support_certification='Geometric contact expression only; not structural load certification',source_parts='source/geometry_parts.json')
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    entry={'catalogue_id':aid,'name':manifest['name'],'family':family,'source':str((root/manifest['source']).relative_to(C)),'export':str((root/manifest['export']).relative_to(C)),'manifest':str(path.relative_to(C)),'source_sha256':manifest['source_sha256'],'export_sha256':manifest['export_sha256'],'evaluated_triangles':manifest['triangles'],'batch':batch,'adopted_game_instances':matches[0].get('adopted_game_instances',0)if matches else 0,'status':manifest['status']}
    if matches:entries[entries.index(matches[0])]=entry
    else:entries.append(entry)
assert len({entry['catalogue_id']for entry in entries})==len(entries)==161
catalogue.update(unique_authored_asset_count=161,status='161 registered designs; presence is not room completion or final art')
catalogue_path.write_text(json.dumps(catalogue,indent=2)+'\n')
print('Registered161 designs with159 prior entries/files unchanged and only authorized AST-CMD-001 interface revision')
