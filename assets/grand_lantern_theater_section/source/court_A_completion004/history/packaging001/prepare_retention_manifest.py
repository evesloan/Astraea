"""Prepare this one bounded retention handoff; writes only new metadata beside itself."""
from pathlib import Path
import ast, collections, datetime, hashlib, json, re
P=Path(__file__).resolve().parent;R=P.parent;W=Path('/workspace/scratch/375c2e438292')
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003')
T=C/'assets/grand_lantern_theater_section/source/court_A_completion004'
assert not T.exists() and not T.is_symlink()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(name,d):
 with (P/name).open('x') as f:
  if isinstance(d,str):f.write(d)
  else:json.dump(d,f,indent=2,sort_keys=True);f.write('\n')
def pin(p,**extra):
 p=Path(p);assert p.is_file() and not p.is_symlink(),p
 return {'source':str(p),'sha256':sha(p),'bytes':p.stat().st_size,**extra}
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for k,v in x.items():yield str(k);yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)
def keep(p):
 rel=p.relative_to(R)
 return 'retention_package001' not in rel.parts and not any(x.startswith('.') or x in {'__pycache__','cache','config','data'} for x in rel.parts) and not re.search(r'\.blend\d+$',p.name) and not p.name.endswith(('~','.pyc','.pyo'))
files=sorted(p for p in R.rglob('*')if p.is_file()and keep(p))
excluded=[str(p.relative_to(R))for p in R.rglob('*')if p.is_file()and not keep(p)and P not in p.parents]
refs=collections.defaultdict(set)
for p in files:
 if p.suffix=='.json':ss=strings(json.loads(p.read_text()))
 elif p.suffix=='.py':ss=(n.value for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.Constant)and isinstance(n.value,str))
 else:continue
 for s in ss:
  if s.startswith(('/workspace/','/usr/share/fonts/')) and '\n' not in s and len(s)<600:
   q=Path(s)
   if q.is_file() and R not in q.parents:refs[q].add(str(p.relative_to(R)))
scratch_extra='''theater_resume/first_pass_plan/RETAINED_MODULE_MEASUREMENTS.json
theater_resume/first_pass_plan/arrival_revision02/RETAINED_FOCAL_ASSET_BOUNDS.json
theater_resume/first_pass_plan/arrival_revision02/FURNITURE_ARCHITECTURE_STANCE_SCREEN.json'''.splitlines()
for s in scratch_extra:refs[W/s].add('Read-only independent recipe dependency audit: parent measurement/stance input')
external_extra='''assets/grand_lantern_theater_section/source/AST-CUL-005.blend
assets/grand_lantern_theater_section/source/firstpass_001/build_mechanism_package_compact.py
assets/grand_lantern_theater_section/source/firstpass_003/exports_run005/AST-CUL-005_static_003.glb
assets/grand_lantern_theater_section/source/firstpass_003/exports_run005/AST-CUL-005_prototype_003.glb
assets/botanical_cluster/AST-BOT-009.manifest.json'''.splitlines()
for s in external_extra:refs[C/s].add('Independent recipe audit or protected original-source reference')
for s in ['assets/textures/warm_stone.png','assets/textures/ivory_enamel.png']:
 refs[G/s].add('render_court_A_composition001.py dynamic floor texture path')
for s in ['Astraea_Master_Game_Design_v0_3_authoritative.docx','MASTER_CURRENT_APPLICATION.json','MASTER_FULL_CONTENT_INDEX.json','README.md']:
 refs[G/'docs/master_source'/s].add('Reference context for recorded master chapters 4, 14, 21 and current overlay; no new design acceptance')
for manifest in [C/'materials/material_manifest.json',C/'materials/botanical/manifest.json']:
 refs[manifest].add('build_geometry_contract.py reads all material records')
 for spec in json.loads(manifest.read_text())['materials'].values():
  q=manifest.parent/(spec.get('file')or spec['base_color_file']);assert sha(q)==spec['sha256']
  refs[q].add('build_geometry_contract.py hashes all textures in '+str(manifest))
for s in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf','/usr/share/doc/fonts-dejavu-core/copyright']:
 refs[Path(s)].add('Retained artwork/plan typeface and redistribution notice')
# Preserve the reviewed identities exactly before constructing any output manifest.
identities={
 'authoritative_standalone':('reopen_qa001/winding_repair001/authored_source001/AST-CUL-005_arrival_court_A_004_winding001.blend','7456c069315f3ed1f74c327ba0af53a90942cd1549b6905d3abe58ba76633c49'),
 'authoritative_reopen':('reopen_qa001/winding_repair001/authored_source001/REOPEN_REPORT.json','38634822a5e671e04d72d927132a996ccb99bafa623e8ea5d1854d96c907187e'),
 'failed_winding_source_history':('printed_materials001/authored_preview001/AST-CUL-005_arrival_court_A_004.blend','54433eb9a9efba6509e79e783deaf9a5fe27c43d449ee63ad1e1bad257c2be72'),
 'composed_review_source':('composed_review001/AST-CUL-005_court_A_composed_review_004.blend','13c38d104b722938e01d01a8c67939db0874ffefc48f16f6c5ee804c217e46da'),
 'composition_preview':('composition_view001/D11_Court_A_composition.png','00f84dd3900ae5ab08503395edf5ec5212718bf8530ec7fb04aa586464784e1f')}
for role,(rel,h)in identities.items():assert sha(R/rel)==h,(role,rel)
protected_originals={str(C/'assets/grand_lantern_theater_section/source/AST-CUL-005.blend'):'c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5',str(C/'assets/grand_lantern_theater_section/source/firstpass_003/source_repair003/AST-CUL-005_firstpass_003.blend'):'dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'}
for s,h in protected_originals.items():assert sha(s)==h
copied_deps=[];retained_refs=[];system_deps=[]
for q,why in sorted(refs.items()):
 if q.is_relative_to(W):
  copied_deps.append(pin(q,destination_relative='dependencies/scratch/'+str(q.relative_to(W)),used_by=sorted(why),classification='Copied exact scratch input or provenance evidence'))
 elif q.is_relative_to(C)or q.is_relative_to(G):
  retained_refs.append(pin(q,used_by=sorted(why),classification='Existing retained Catalogue/Game reference; read-only; not copied or modified'))
 else:
  system_deps.append(pin(q,destination_relative='dependencies/typefaces/'+q.name,used_by=sorted(why),classification='Copied artwork font or license; binary engine environment not bundled'))
# Current recipes close exactly. Earlier snapshots retain their observed hash gaps.
checks=[];historical_gaps=[]
for name in ['COURT_A_GEOMETRY_CONTRACT.json','COURT_A_GEOMETRY_CONTRACT_v001.json','COURT_A_GEOMETRY_CONTRACT_v002.json','COURT_A_GEOMETRY_CONTRACT_v003.json','FULLER_REAR_MASS_CANDIDATE.json']:
 d=json.loads((R/name).read_text());pins=d.get('input_sha256',d.get('source_method_pins',{}))
 for s,h in pins.items():
  actual=sha(s);row={'record':name,'source':s,'recorded_sha256':h,'current_sha256':actual,'matches':h==actual}
  (checks if h==actual else historical_gaps).append(row)
assert all(r['record'].startswith('COURT_A_GEOMETRY_CONTRACT_v') and r['source']==str(R/'build_geometry_contract.py')for r in historical_gaps)
assert len(copied_deps)==14,(len(copied_deps),[d['source']for d in copied_deps])
limits=[
 'Architecture direction reviewed by the parent for source retention only: facing curved sofas, dark floor zone, planted backdrop, reception and shaped ceiling.',
 'Lighting remains unaccepted. The source Cycles image is a composition study; its darkness must not be used to raise native light energy or infer native photometry.',
 'Retaining the source candidate does not accept finished art, native visuals, physics/collision, six-species circulation/reach, continuous contact/load capacity, or acoustics.',
 'No runtime export/adoption, catalogue ID/registry change, Game mutation, Git action, engine launch or backup publication is performed by this retention tool.',
 'Historical gate JSONs and prior approvals are evidence only; they do not grant permission or a resource slot for a future source job.',
 'Recipes are historical, path-bound and not runnable unchanged after relocation. Editable packed Blender sources preserve the approved source result.']
qa={
 'winding':'Initial printed source failed closed_opposite_directed_edges on A4_W_crowned_cushion. Only its 56 face orders and corresponding UV-loop orders were reversed; vertices, UV-to-vertex associations, all other geometry and all 24 retained instance rows remain unchanged.',
 'material_provenance':'Read-only diagnosis found exact native graph matches for all 30 retained materials. The narrow successor freezes requested source labels before Blender mutates library load bindings; node/value/link/image equality remains enforced.',
 'paper_graph':'Canonical JSON digest normalizes tuple/list representation in material link sequences without dropping graph data.',
 'retained_modifiers':'An overstrict no-modifier retained-library assertion rejected an original table shelf. The final QA independently compares all authored modifier/constraint/animation state and evaluated viewport geometry at the saved frame (133 authored objects, 120 evaluated objects), while keeping new-mesh no-modifier gates.',
 'final_reopen':'PASS_SOURCE_ONLY, 69 architecture pieces + 10 printed solids + 78 fuller parts, 24 retained instances. Native libraries here mean original Blender source libraries, not Godot/native visual acceptance.',
 'composition':'The composed source report preserves the full base snapshot and all 2200 audience chairs. Existing source light/camera/exposure state was unchanged in the saved composed Blend. Review-only renderer adjustments were temporary and never saved/exported.'}
readme='''# Court A completion004: retained source candidate

This is an additive AST-CUL-005 source candidate, not finished-art or native-lighting acceptance. The parent reviewed the facing curved sofas, contrasting floor zone, dense planting, reception and shaped ceiling as the architectural direction worth preserving. Lighting remains unaccepted. Never use the dark Cycles preview to increase native energy.

## Authoritative files

- Editable standalone: court/reopen_qa001/winding_repair001/authored_source001/AST-CUL-005_arrival_court_A_004_winding001.blend
- Actual build and successful independent reopen: BUILD_REPORT.json and REOPEN_REPORT.json beside that Blend
- Full composed editable review: court/composed_review001/AST-CUL-005_court_A_composed_review_004.blend, with COMPOSITION_REPORT.json
- Reviewed source-only image and exact temporary settings: court/composition_view001/
- Failed-winding predecessor: court/printed_materials001/authored_preview001/; retain as history, never substitute as authoritative

The standalone and composed Blends are self-contained editable artifacts for their authored contents. Packed artwork/material image bytes and original source-library fidelity were checked in the retained reports. The compiler-owned review floor is deliberately temporary render geometry and is not a missing source floor to recreate or install.

## Structure and protection

court/ preserves the exact reviewed geometry-contract directory, including current/frozen and historical geometry/plant/print contracts, both SVG/PNG variants, original/corrected winding evidence, source/library/prototype QA, diagnosis, scripts, receipts and logs. dependencies/scratch/ preserves the 14 named outside inputs and method evidence, including both parent measurement files. dependencies/typefaces/ holds both exact DejaVu faces and their license notice. DEPENDENCY_INDEX.json pins the already-retained Catalogue/Game libraries, exports, helper modules, textures, design sources and actual image references; these are read-only references, not duplicated/adopted models. All copies are byte-identical.

RETENTION_MANIFEST.json maps each source to its exact new destination and hash. The guarded copier defaults to read-only preflight and requires --copy for the authorized retention action. It refuses any existing target, file, directory or symlink, including a partial prior attempt. It never merges, overwrites, retries a different destination, launches an engine, changes registry data, runs Git or publishes backups. It verifies input hashes before and after copying and verifies every output. A failed attempt preserves its partial new directory for investigation; do not remove or reuse it automatically.

Original AST-CUL-005 c91193af... and firstpass003 dfb09483... remain protected. Old source material/geometry state and all 2200 audience chairs remain preserved. Game stays frozen for full117; this package is source retention only.

## Status chronology

Earlier HANDOFF/status/gate files are unmodified historical evidence; later successful source/reopen/composition receipts supersede their pending source stages only. ACCEPTANCE_AND_LIMITS.json states the current scope without falsifying old reports. The initial winding failure, material-label false failure, paper tuple/list comparison fix and retained-modifier/evaluated-state fix are preserved in full. No source resave was performed during the successful final reopen or this packaging step.

## Relocation and future rebuild

These recipes are historical and are not portable/rerunnable unchanged. They contain original absolute scratch/Catalogue/Game roots, parent-relative measurements, historical output paths, fixed hashes, and guards requiring new output directories. One older unprinted output directory and the failed predecessor's successful reopen report never existed. Three early contract snapshots name older builder hashes whose exact old script bytes are not present; these are history-only provenance gaps, not missing dependencies of the current verified candidate.

For continued editing, copy the authoritative standalone Blend into a newly authorized scratch location, preserve the retained original, edit there, and reopen/verify the successor. For a recipe rebuild: create a fresh separate workspace; reconstruct the court and parent measurement layout from DEPENDENCY_INDEX.json; point reviewed successor scripts at exact retained helper/library and plant-method inputs; change only path/output/gate handling in new scripts; keep frozen input contracts and the precise winding/UV correction; obtain the current source-job slot; rerun bounded build and independent source QA before a new composition review. The printed pure validator and historical launchers contain pre-build-only assertions and cannot just be replayed in the retained directory. A future generator successor must enforce directed-edge winding validation and preserve face UV associations.

Historical source logs record Blender 4.3.2. Pure recipes require NumPy, Shapely, Pillow and jsonschema. Shapely was absent from the currently inspected default/system Python environments; select a compatible existing environment or separately authorized dependency setup before regeneration. No software was installed. Inkscape/font renderer versions were not pinned by the original recipe, so editable SVG preservation does not guarantee byte-identical raster regeneration. Current approved PNG bytes and exact fonts are retained.

No further input omission blocks retention. Native same-pose/seated/service review, lighting acceptance, runtime/contact/six-species checks and eventual additive adoption remain later gates, outside this package.
'''
write('README.md',readme)
write('ACCEPTANCE_AND_LIMITS.json',{'status':'REVIEWED_ARCHITECTURAL_SOURCE_CANDIDATE_READY_FOR_NEW_ONLY_RETENTION','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'retained_or_installed_by_preparation':False,'identities':{k:{'path':'court/'+r,'sha256':h}for k,(r,h)in identities.items()},'protected_originals':protected_originals,'acceptance_limits':limits,'qa_chronology':qa,'omissions_requiring_decision':[]})
write('DEPENDENCY_INDEX.json',{'scope':'Current Court recipes and evidence closure; imports audited without running engines','scratch_inputs_copied':copied_deps,'artwork_system_inputs_copied':system_deps,'existing_retained_references':retained_refs,'current_and_historical_matching_pin_observations':checks,'historical_builder_versions_not_present':historical_gaps,'historical_outputs_intentionally_absent':['court/authored_preview001/','court/printed_materials001/authored_preview001/REOPEN_REPORT.json'],'unused_pool_and_mechanism_paths':'Pool-specific main routines and mechanism perforated_roof() are not used by the Court imported functions. Their unrelated plans/prototypes/export trees are not part of the Court dependency closure. Existing pool method QA is lineage evidence only.','runtime_environment':'Historical Blender 4.3.2. Pure Python dependencies: NumPy, Shapely, Pillow, jsonschema; Shapely absent currently. Inkscape/font rasterization is not version-locked. No dependency installation authorized or performed.','excluded_files':excluded,'excluded_directories':['cache/config/data XDG job folders','.renderer_home','.renderer_cache','.renderer_config','__pycache__'],'all_essential_inputs_present':True,'portable_or_replayable_unchanged':False,'reference_use_record':'court/REFERENCE_AND_FAMILY_AUDIT.json and dependencies/scratch/theater_resume/first_pass_plan/arrival_revision02/court_A_completion004/REFERENCE_USE.json','game_preservation_snapshot':'court/source_build_run001/INPUT_PINS.json stores the historical observational Game before/after inventory; it is not a generated-geometry dependency set.'})
rows=[]
for p in files:rows.append(pin(p,destination_relative='court/'+str(p.relative_to(R)),classification='Unchanged reviewed Court artifact or historical evidence'))
for d in copied_deps+system_deps:rows.append({k:v for k,v in d.items()if k!='used_by'})
for name in ['README.md','ACCEPTANCE_AND_LIMITS.json','DEPENDENCY_INDEX.json','retain_new_only.py','test_retainer.py','COPIER_TEST_REPORT.json','prepare_retention_manifest.py']:
 rows.append(pin(P/name,destination_relative=name,classification='New retention metadata or bounded copier tooling'))
for row in rows:row['destination']=str(T/row['destination_relative'])
rows.sort(key=lambda r:r['destination_relative'])
protected=[]
for row in rows+retained_refs:
 if not any(p['source']==row['source']for p in protected):protected.append({k:row[k]for k in ['source','bytes','sha256']})
protected.sort(key=lambda r:r['source'])
manifest={'schema':'astraea.court_a.source_retention.v1','target':str(T),'status':'PREPARED_NOT_COPIED','payload_file_count':len(rows),'payload_bytes':sum(r['bytes']for r in rows),'files':rows,'protected_inputs':protected,'acceptance_limits':limits,'identities':{k:{'destination_relative':'court/'+r,'sha256':h}for k,(r,h)in identities.items()},'manifest_copy_policy':'Copy this exact manifest additionally as RETENTION_MANIFEST.json, verified by caller-supplied SHA-256. A final receipt is created new-only after all input/output verification.','expected_final_file_count_including_manifest_and_receipt':len(rows)+2,'no_external_mutation':True}
write('RETENTION_MANIFEST.json',manifest)
summary={'status':'PREPARED_NEW_ONLY_NOT_COPIED','manifest_sha256':sha(P/'RETENTION_MANIFEST.json'),'manifest_bytes':(P/'RETENTION_MANIFEST.json').stat().st_size,'wrapper_sha256':sha(P/'retain_new_only.py'),'wrapper_bytes':(P/'retain_new_only.py').stat().st_size,'payload_file_count':len(rows),'payload_bytes':manifest['payload_bytes'],'expected_final_file_count':len(rows)+2,'bytes_before_generated_receipt':manifest['payload_bytes']+(P/'RETENTION_MANIFEST.json').stat().st_size,'court_artifact_files':len(files),'copied_scratch_dependency_files':len(copied_deps),'copied_typeface_and_license_files':len(system_deps),'existing_retained_reference_files':len(retained_refs),'protected_inputs':len(protected),'historical_builder_hash_gaps':len(historical_gaps),'omissions_requiring_parent_decision':[]}
write('PREPARATION_SUMMARY.json',summary)
print(json.dumps(summary,indent=2))
