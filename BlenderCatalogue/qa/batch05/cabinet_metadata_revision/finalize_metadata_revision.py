from pathlib import Path
import json,hashlib,struct
base=Path(__file__).resolve().parents[3];a=base/'assets/staff_workbay';q=base/'qa/batch05/cabinet_metadata_revision';slug='AST-STF-007_supply_work_cabinet'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readglb(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return b,json.loads(b[20:20+n]),b[28+n:]
r=json.loads((q/'source_preservation_report.json').read_text());g=json.loads((q/'glb_preservation_report.json').read_text());props=r['current_hinge_custom_properties'];meta={k:v for k,v in props.items() if k.startswith('hinge_') or k=='coordinate_metadata_revision'}
gp=q/'generator_sandbox/assets/staff_workbay';current,j,bin=readglb(a/(slug+'.glb'));rebuilt,j2,bin2=readglb(gp/(slug+'.glb'))
smoke={'revision':'hinge-frame-metadata-02','command':'blender -b -t 1 --python qa/batch05/cabinet_metadata_revision/generator_sandbox/assets/staff_workbay/build_staff_workbay.py','scope':'Isolated reconstruction with copies of required shared dependencies; no rebuilt geometry replaced reviewed asset files.','generator_sha256':sha(a/'build_staff_workbay.py'),'isolated_generator_sha256':sha(gp/'build_staff_workbay.py'),'dependencies':[{'path':p,'sha256':sha(base/p),'isolated_sha256':sha(q/'generator_sandbox'/p)} for p in ['standards/staff_materials.py','materials/staff/manifest.json','batches/batch03/reference_manifest.json']],'current_glb_sha256':sha(a/(slug+'.glb')),'rebuilt_glb_sha256':sha(gp/(slug+'.glb')),'glb_json_values_identical':j==j2,'bin_chunk_byte_identical':bin==bin2,'bin_sha256':hashlib.sha256(bin).hexdigest(),'glb_byte_difference_explanation':'Only JSON object member ordering differs; every parsed JSON value and the complete BIN chunk match.','reconstructed_triangles':json.loads((gp/(slug+'.manifest.json')).read_text())['triangles_evaluated'],'pass':j==j2 and bin==bin2}
assert smoke['pass'];(q/'generator_smoke_report.json').write_text(json.dumps(smoke,indent=2)+'\n')
r['serialization_note']='Blender data-block library write preserves all asset data including five otherwise orphaned packed staff tiles. Editor session WindowManager/Screen/WorkSpace blocks are excluded; this check does not certify preservation of editor window/layout state. Runtime session IDs and empty renderer-initialized custom-property groups are excluded from semantic comparison.'
(q/'source_preservation_report.json').write_text(json.dumps(r,indent=2)+'\n')
(q/'source_after_snapshot.json').unlink(missing_ok=True)
report_rel='../../qa/batch05/cabinet_metadata_revision/verification_report.json'
manifest_path=a/(slug+'.manifest.json');m=json.loads(manifest_path.read_text());m['door']['node_coordinate_metadata']=meta
for ext in ['blend','glb']:
 p=a/(slug+'.'+ext);m[ext+'_sha256']=sha(p);m[ext+'_bytes']=p.stat().st_size
m['source_generator_sha256']=sha(a/'build_staff_workbay.py')
m['metadata_revision']={'revision':'hinge-frame-metadata-02','scope':'Hinge custom-property coordinate clarification only; asset geometry, material graphs and object transforms unchanged. GLB BIN unchanged. Editor session layout is outside preservation scope.','previous_blend_sha256':r['source_before_sha256'],'previous_glb_sha256':g['old_glb_sha256'],'original_inputs':'../../qa/batch05/cabinet_metadata_revision/original_inputs/','verification':report_rel}
m['component_qa']['metadata_revision_verification']=report_rel
m['component_qa']['historical_evidence_scope']='Existing source/export validation, sweep and render reports bind the pre-revision hashes preserved in original_inputs. They have not been rewritten or rerun. Their geometry remains applicable through the new exact semantic source and byte-identical GLB BIN/non-extras JSON comparisons; metadata fields are checked on the current actual files.'
m['component_qa']['status']='Historical component checks pass; current metadata-only revision preservation passes; original engine/rig/scene integration pending'
manifest_path.write_text(json.dumps(m,indent=2)+'\n')
p=a/'integration_api.json';d=json.loads(p.read_text());d['door']['node_coordinate_metadata']=meta;d['metadata_revision']='hinge-frame-metadata-02';d['metadata_revision_verification']=report_rel;p.write_text(json.dumps(d,indent=2)+'\n')
p=a/'README.md';s=p.read_text();s=s.replace('blender --background --threads 4','blender --background --threads 1')
if '## Coordinate metadata revision 02' not in s:
 s+='''
## Coordinate metadata revision 02

The current `.blend` and `.glb` use **hinge-frame-metadata-02**. Their actual hinge node has no unqualified `axis` field. `hinge_axis_blender_source` is `[0, 0, 1]`, and `hinge_axis_gltf_yup` is `[0, 1, 0]`. Each frame has its own numeric pivot and explicit opening hint. The signed opening remains 0° through −105° about its stated positive axis. Exported extras are copied verbatim, so their names identify the frame of each value.

The generator writes the same fields. An isolated reconstruction with copied shared dependencies produces exactly equal GLB JSON values and a byte-identical BIN chunk. The reviewed production geometry was retained; the current GLB was changed only by replacing the hinge extras in its JSON chunk.

Exact pre-revision source, export, generator, manifests and checksums are preserved under `../../qa/batch05/cabinet_metadata_revision/original_inputs/`. Existing Batch03 sweep, render and validation records retain those historical hashes and were not rerendered or rewritten. `../../qa/batch05/cabinet_metadata_revision/verification_report.json` records the current source reload comparison, GLB invariants and generator check. All 63 base/evaluated meshes, 65 objects and their hierarchy/transforms/modifiers, four material graphs, all nine packed images and scene units match. Blender editor window/layout state is outside that asset-data comparison.
'''
p.write_text(s)
p=a/'STAFF_WORKBAY_SHA256SUMS.txt';rels=[line.split('  ',1)[1] for line in p.read_text().splitlines() if line.strip()]
p.write_text(''.join(sha(a/rel)+'  '+rel+'\n' for rel in rels))
old=json.loads((q/'original_inputs_manifest.json').read_text());changed=[];unchanged=[]
for row in old['files']:
 p=base/row['path'];out={**row,'current_sha256':sha(p),'current_bytes':p.stat().st_size}
 (unchanged if out['sha256']==out['current_sha256'] else changed).append(out)
report={'revision':'hinge-frame-metadata-02','catalogue_id':'AST-STF-007','change':'Replace ambiguous source-only hinge axis text in actual source/export with explicit source-frame and native-GLB-frame numeric axes/pivots and opening hints.','geometry_rebuilt_in_production':False,'source_preservation':'source_preservation_report.json','glb_preservation':'glb_preservation_report.json','isolated_generator_verification':'generator_smoke_report.json','original_inputs_manifest':'original_inputs_manifest.json','changed_existing_files':changed,'unchanged_existing_top_level_files':unchanged,'current_hinge_custom_properties':props,'prior_qa_scope':'Existing asset/Batch03 source, sweep and render evidence remains bound to original hashes. This revision provides new actual-file metadata checks and semantic/byte invariants; it does not rerun rendering, collision sweep or engine behavior.','passed':r['all_invariants_unchanged'] and smoke['pass'] and g['non_json_chunks_byte_identical'] and g['all_json_outside_hinge_extras_identical']}
(q/'verification_report.json').write_text(json.dumps(report,indent=2)+'\n')
(q/'README.md').write_text('''# Staff cabinet hinge coordinate metadata revision 02

This folder preserves the exact eight original top-level inputs and the evidence for a metadata-only asset-content correction. The GLB edit changes hinge extras only, with its complete BIN payload and every JSON value outside those extras unchanged. The editable source is reserialized after changing only hinge properties; all recorded asset geometry/material/hierarchy/transform/texture invariants pass after reload. Blender window/layout state is outside this preservation claim.

- `verification_report.json`: current hashes, changed file list and evidence index
- `original_inputs_manifest.json` and `original_inputs/`: exact historical inputs
- `source_preservation_report.json`, `source_before_snapshot.json`, `revise_source_metadata.py`, `source_revision.log`: source comparisons and procedure
- `glb_preservation_report.json`, `revise_glb_metadata.py`: surgical GLB update and byte/JSON checks
- `generator_smoke_report.json`, `generator_smoke.log`, `generator_sandbox/`: isolated reproduction using copied shared dependencies; parsed JSON and BIN exactly match the current GLB

Existing asset and Batch03 render/sweep/validation reports were not rewritten or rerun. Their old hashes refer to the preserved original inputs. No render, engine scene, gameplay or new unique asset was created.
''')
print('Changed existing files:',*[x['path'] for x in changed],sep='\n')
print('All checks passed:',report['passed'])
