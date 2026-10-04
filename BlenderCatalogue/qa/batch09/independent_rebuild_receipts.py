"""Review/bind lead's isolated source-only runs; do not rerun or overwrite authoring."""
from pathlib import Path
import json,hashlib,ast
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
aggregate=OUT/'source_only_rebuild/report.json';agg=json.loads(aggregate.read_text());assert agg['passed'] and agg['byte_identical_glb_count']==6 and agg['byte_identical_texture_count']==15
mm=json.loads((ROOT/'materials/material_manifest.json').read_text());common={'standards/materials.py','materials/material_manifest.json'}|{'materials/'+v['base_color_file']for v in mm['materials'].values()}
rows=[]
for b in agg['families']:
 p=ROOT/b['path'];assert sha(p)==b['sha256'];r=json.loads(p.read_text());assert r['passed'] and not r['preexisting_new_source_or_export_outputs'] and not r['qa_render_inputs'];family=r['family'];actual={a['path']for a in r['input_files']}
 needed=common|{'assets/'+family+'/source/build_'+family+'.py'}
 if family=='library_use':
  needed|={'assets/library_use/source/make_use_art.py','assets/library_contents/texture_manifest.json'}
  book=json.loads((ROOT/'assets/library_contents/texture_manifest.json').read_text())
  needed|={'assets/library_contents/'+book['texture_root']+'/'+book['materials'][role]['base_color_file']for role in ['book_cover_teal','book_cover_clay','book_cover_ochre','book_paper_edges']}
 assert needed==actual,(family,needed-actual,actual-needed)
 for a in r['input_files']+r['exports']+r['textures']:assert sha(ROOT/a['path'])==a['sha256'],a['path']
 for name,h in r['current_bound_files_unchanged'].items():assert sha(ROOT/name)==h,name
 assert all(a['generated_bytes_identical']for a in r['exports']+r['textures']);assert len(r['exports'])==3 and r['editable_blend_outputs_created']==3
 assert all(a['returncode']==0 for a in r['commands'])
 for c in r['commands']:assert (ROOT/c['log']).is_file()
 gp=ROOT/'assets'/family/'source'/('build_'+family+'.py');tree=ast.parse(gp.read_text());mkdir=[ast.unparse(x)for x in ast.walk(tree)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=='mkdir'];assert mkdir
 rows.append({'family':family,'lead_execution_receipt':{'path':str(p.relative_to(ROOT)),'sha256':sha(p)},'input_scope_exactly_matches_reviewed_source_reads':True,'current_input_hash_count':len(actual),'all_inputs_outputs_and_protected_masters_current':True,'byte_identical_glbs':len(r['exports']),'byte_identical_textures':len(r['textures']),'generator_creates_output_parents':mkdir,'lead_runs_not_duplicated':True,'pass':True})
res={'passed':True,'lead_aggregate':{'path':str(aggregate.relative_to(ROOT)),'sha256':sha(aggregate)},'families':rows,'limits':'Independent review of the lead execution harness, declared dependency closure and exact current bindings. The reviewer did not repeat the already successful isolated runs. Byte-identical GLBs and textures plus created editable sources establish this bounded rebuild, not a complete game restore.'}
(OUT/'independent_rebuild_receipts.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
