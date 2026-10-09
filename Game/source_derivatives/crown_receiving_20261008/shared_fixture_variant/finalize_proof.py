from pathlib import Path
import json,hashlib,struct
B=Path(__file__).resolve().parent;P=B.parent;R=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=json.loads((B/'BATCH_SPLIT_PROOF.json').read_text());p=json.loads((B/'BINARY_EDIT_PROOF.json').read_text())
originals={str(R/'Game/assets/models/AST-CMD-001.glb'):p['original_runtime_sha256'],str(R/'BlenderCatalogue/assets/central_crown/exports/AST-CMD-001.glb'):p['original_runtime_sha256'],p['source_native']:p['source_native_sha256'],str(R/'Game/data/architecture/CENTRAL_CROWN_RUNTIME.json'):p['original_runtime_manifest_sha256']}
for r in json.loads((P/'RECEIVING_AUDIT.json').read_text()):
 if r['programme_key'] not in ['D18_directory_02','D18_directory_04','D18_directory_06']:continue
 originals[str(P/'fixture_fit_candidates'/r['folder']/'source/native.blend')]=r['native_sha256']
 for base in [P/r['folder'],P/'fixture_fit_candidates'/r['folder']]:originals[str(base/'exports'/f"{r['programme_key']}.glb")]=r['glb_sha256']
assert all(sha(Path(k))==v for k,v in originals.items());(B/'ORIGINALS_PRESERVED.json').write_text(json.dumps(originals,indent=2))
checks=json.loads((B/'GEOMETRY_CHECKS.json').read_text());(B/'GEOMETRY_PROVENANCE.json').write_text(json.dumps({'measured_geometry_variant':p['variant'],'measured_runtime_sha256':p['variant_runtime_sha256'],'active_variant':s['variant'],'active_runtime_sha256':s['runtime_sha256'],'transfer_basis':'BATCH_SPLIT_PROOF establishes identical oriented per-triangle POSITION/NORMAL/TEXCOORD/material values in world coordinates; every runtime mesh node has identity transform. Roof contacts, housing clearance, lens paths and broad-cone interceptions therefore apply unchanged to the split successor. No photometric changes.','roof_contact_rays':sum(x['roof_contact_rays']for x in checks),'clear_shared_and_incoming_lens_rays':sum(x['full_shared_and_incoming_lens_footprint_clear_rays_to_y108_8']for x in checks),'max_contact_error_m':max(x['roof_contact_max_error_m']for x in checks)},indent=2))
def doc(path):
 raw=path.read_bytes();return json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
ja=doc(R/'Game/assets/models/AST-CMD-001.glb');jb=doc(B/(s['variant']+'.glb'));na={x['name']:x for x in ja['nodes']};nb={x['name']:x for x in jb['nodes']};q=json.loads((P/'fixture_fit_candidates/MOUNTED_FIXTURE_RELOCATION_PROPOSALS.json').read_text());rows=[]
for x in q:
 name=x['existing_marker'];expected=[na[name]['translation'][i]+x['translation'][i]for i in range(3)];assert nb[name]['translation']==expected;assert {k:v for k,v in na[name].items()if k!='translation'}=={k:v for k,v in nb[name].items()if k!='translation'};rows.append({'name':name,'actual':expected,'intended_manifest':x['proposed_marker_position'],'unchanged_identity_and_extras':True})
(B/'MARKER_TRANSFORM_PROOF.json').write_text(json.dumps(rows,indent=2))
