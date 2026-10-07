"""Write terminal source receipts after externally observed successful test stages."""
import argparse,json,hashlib,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--observed-utc',required=True);ap.add_argument('--stages',required=True);a=ap.parse_args()
P=Path(a.package).resolve();BASE=Path(__file__).resolve().parents[1];assert P.is_relative_to(BASE);Q=P/'qa/receiving_source_review';inp=json.loads((Q/'INPUT_HASH_RECEIPT.json').read_text());origin=Path(inp['original_directory']);assert origin.is_relative_to(BASE)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert all(sha(origin/r)==h for r,h in inp['files'].items())
assert sha(Path(inp['archive']['path']))==inp['archive']['sha256']
map=json.loads((P/'dependency_map.json').read_text())['dependencies'];CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
assert all(sha(P/r['package_relative_path'])==sha(CAT/r['catalogue_relative_path'])==r['sha256'] for r in map)
changed=[r for r,h in inp['files'].items() if sha(P/r)!=h]
immutable=[r for r in inp['files'] if r.startswith(('source/','assets/','dependencies/')) or (r.startswith('tests/') and r.endswith('.py')) or r in ['root_review.json','EVIDENCE_SUMMARY.json','dependency_map.json','copy_dependencies.py']]
assert all(sha(P/r)==inp['files'][r] for r in immutable),'Unexpected immutable input mutation'
closure=json.loads((Q/'NATIVE_RESOURCE_CLOSURE.json').read_text());assert closure['pass']
glbs=list((P/'exports').glob('*.glb'));natives=list((P/'source').glob('*.blend'));assert len(glbs)==len(natives)==1
checks=[]
for rel in ['qa/native_check.json','qa/export_check.json','tests/reload_export_receipt.json','qa/source_checks.json','qa/receiving_source_review/ACTUAL_GLB_VERTEX_CHECK.json','qa/receiving_source_review/NATIVE_BOUNDS_CHECK.json']:
 f=P/rel
 if not f.exists():continue
 d=json.loads(f.read_text());success=d.get('pass',d.get('status') in ['pass','PASS_SOURCE_SCREENS']);assert success,(rel,d);checks.append({'file':rel,'sha256':sha(f),'pass':True})
logs={f.name:[line for line in f.read_text().splitlines() if any(t in line.lower() for t in ['warning','error','traceback','assert'])] for f in Q.glob('*.log')}
outputs=[natives[0],glbs[0],Q/'NATIVE_RESOURCE_CLOSURE.json']+[P/r['file'] for r in checks]
for rel in ['manifest.json','exports/manifest.json','qa/build_manifest.json']:
 if (P/rel).is_file():outputs.append(P/rel)
historical=json.loads((P/'root_review.json').read_text());stages=json.loads(a.stages);assert all(v==0 for v in stages.values())
r={'scope':'Source-only reconstructed candidate, no renders or receiving-engine adoption','observed_terminal_utc':a.observed_utc,'blender':'4.3.2','thread_limit':2,'stage_exit_codes':stages,'original_extracted_tree_unchanged':True,'original_archive_unchanged':True,'catalogue_dependencies_unchanged':True,'immutable_working_inputs_unchanged':True,'changed_generated_metadata_from_original':changed,'input_receipt_sha256':sha(Q/'INPUT_HASH_RECEIPT.json'),'outputs':{str(f.relative_to(P)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in outputs},'checks':checks,'decoded_native_images':len(closure['images']),'embedded_glb_images':closure['export_embedded_images'],'punctual_lights':closure['export_punctual_lights'],'native_fonts_survive':len(closure['native_fonts']),'log_warning_lines':logs,'historical_root_review_note_retained':historical.get('note'),'visual_review_of_rebuilt_outputs':False,'historical_patch_run':False,'game_catalogue_modified':False}
(Q/'TERMINAL_RECEIPT.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['log_warning_lines','historical_root_review_note_retained','outputs']},indent=2))
