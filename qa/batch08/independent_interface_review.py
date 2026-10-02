"""Review per-file interface metadata correction scope and current evidence bindings."""
from pathlib import Path
import ast,json,hashlib,subprocess,tempfile,shutil,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08';BASE='66dcaf10f105958c5cadb421d5aca15b054b98ed';LIB=ROOT/'assets/library_contents'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+str(p.relative_to(ROOT))],cwd=ROOT)
def functions(text):return {f.name:ast.dump(f,include_attributes=False) for f in ast.parse(text).body if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef))}
allowed={'source_generator_sha256','texture_generator_sha256','texture_generator_sha256_at_original_export','source_generator_sha256_at_original_export','texture_manifest_interface_revision','texture_manifest_sha256','dependency_metadata_revision_note'}
def changes(a,b,p=''):
 if isinstance(a,dict) and isinstance(b,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):
   if k not in a or k not in b:out.append(p+'/'+k)
   else:out+=changes(a[k],b[k],p+'/'+k)
  return out
 if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
  return [z for i,(x,y) in enumerate(zip(a,b)) for z in changes(x,y,p+'/'+str(i))]
 return [] if a==b else [p]
manifest_rows=[]
for p in sorted(LIB.glob('*.manifest.json')):
 before=json.loads(old(p));after=json.loads(p.read_text());diff=changes(before,after)
 assert all(k.rsplit('/',1)[-1] in allowed for k in diff),(p,diff)
 assert after['source_generator_sha256_at_original_export']==before['source_generator_sha256']
 assert after['texture_generator_sha256_at_original_export']==before['texture_generator_sha256']
 assert after['texture_manifest_sha256']==sha(LIB/'texture_manifest.json')
 sourcegen='build_stock_variants.py' if any(v in p.name for v in ['reordered','short_flat']) else 'build_library_contents.py'
 assert after['source_generator_sha256']==sha(LIB/sourcegen);assert after['texture_generator_sha256']==sha(LIB/'make_book_textures.py')
 manifest_rows.append({'path':str(p.relative_to(ROOT)),'original_sha256':hashlib.sha256(old(p)).hexdigest(),'current_sha256':sha(p),'changed_json_pointers':diff,'unchanged_all_geometry_contacts_material_parameters_and_dimensions':True,'original_generator_provenance_preserved':True})
f=LIB/'build_library_contents.py';bf=functions(old(f));af=functions(f.read_text());unchanged=[k for k in bf if bf[k]==af[k]];changed=[k for k in bf if bf[k]!=af[k]];assert set(changed)=={'reset','finish'}
v=LIB/'build_stock_variants.py';before=ast.parse(old(v));after=ast.parse(v.read_text());added=[n for n in after.body if ast.dump(n) not in [ast.dump(o) for o in before.body]];assert len(added)==1
assert isinstance(added[0],ast.Expr) and isinstance(added[0].value,ast.Call) and isinstance(added[0].value.func,ast.Attribute) and added[0].value.func.attr=='mkdir'
after.body=[n for n in after.body if n is not added[0]];assert ast.dump(before)==ast.dump(after)
t=LIB/'texture_manifest.json';before=json.loads(old(t));after=json.loads(t.read_text());declared={'interface_revision','texture_root','path_base','base_color_file_resolution'};assert {k:v for k,v in after.items() if k not in declared}==before
assert after['texture_root']=='textures' and after['path_base']=='directory_containing_this_manifest';paths=[]
with tempfile.TemporaryDirectory(prefix='independent_library_metadata_') as tmp:
 tmp=Path(tmp);shutil.copy2(LIB/'make_book_textures.py',tmp/'make_book_textures.py');run=subprocess.run([sys.executable,str(tmp/'make_book_textures.py')],capture_output=True,text=True);assert run.returncode==0,run.stderr
 assert json.loads((tmp/'texture_manifest.json').read_text())==after
 for role,r in after['materials'].items():
  p=LIB/after['texture_root']/r['base_color_file'];assert sha(p)==r['sha256']==sha(tmp/'textures'/r['base_color_file'])
  paths.append({'role':role,'path':str(p.relative_to(ROOT)),'sha256':sha(p),'independent_isolated_generator_bytes_identical':True})
ledger=[]
for line in (LIB/'LIBRARY_CONTENTS_SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split(maxsplit=1);assert sha(LIB/name)==digest,name;ledger.append(name)
rebuild_path=OUT/'library_texture_path_revision/isolated_rebuild_report.json';rebuild=json.loads(rebuild_path.read_text());assert rebuild['passed']
for r in rebuild['inputs']:assert sha(ROOT/r['path'])==r['sha256']
for r in rebuild['byte_identical_glb_rebuilds']:assert r['isolated_generated_bytes_identical'] and sha(ROOT/r['export'])==r['sha256']
index_path=ROOT/sys.argv[1] if len(sys.argv)>1 else ROOT/'standards/catalogue_interface_index.json'
if not index_path.exists():index_path=OUT/'interface_normalized_index_proposed.json'
index=json.loads(index_path.read_text());assert len(index['assets'])==45 and len({r['catalogue_id'] for r in index['assets']})==45
rows=[]
required=['units','datum_and_pivot','source_and_native_frames','connections_and_normals','physical_contact_pose_and_origin','motion_and_hierarchy','dependencies_and_material_roles']
for r in index['assets']:
 for kind,b in r['source_export_manifest_bindings'].items():assert sha(ROOT/b['path'])==b['sha256'],b['path']
 for f in required:assert r[f]['status']
 rows.append({'id':r['catalogue_id'],'applicability_statuses':{f:r[f]['status'] for f in required},'actual_source_export_manifest_bindings_current':True})
summary=json.loads((OUT/'interface_checks_summary.json').read_text())
result={'pass':True,'unique_artistic_design_count':45,'canonical_consumer_index':{'path':str(index_path.relative_to(ROOT)),'sha256':sha(index_path),'promoted_to_standards':str(index_path.relative_to(ROOT)).startswith('standards/')},'per_asset_explicit_statuses':rows,'library_metadata_scoped_corrections':manifest_rows,'library_texture_manifest_existing_material_records_identical':True,'texture_outputs':paths,'library_geometry_functions_ast_unchanged':unchanged,'source_generator_changed_functions':changed,'variant_generator_only_ast_change':ast.unparse(added[0]),'library_hash_ledger_entries_verified':len(ledger),'lead_isolated_four_glb_rebuild_evidence':{'path':str(rebuild_path.relative_to(ROOT)),'sha256':sha(rebuild_path),'current_input_hashes_verified':True,'all_four_current_outputs_match_report':True,'performed_by':'lead; independently reviewed current bindings, not redundantly rerun by reviewer'},'audit_counts_and_failures':summary,'semantic_assessment':['All45 rows distinguish static not-applicable interfaces, existing connections, physical support versus pose/opening/centreline datums, actual parent hierarchy and unspecified removable trajectories. No inferred user interaction point is promoted into a physical anchor.','Legacy Z-up text in eight GLB origin extras is explicitly interpreted as source-description prose; native Y-up geometry is not transformed again. Cabinet hinge corrected metadata remains byte-stable.','Nozzle/pipe/cup/drain centres may occupy intended voids. Live moved markers follow their actual native hierarchy; neutral extras are not live world transforms.','Station export_group=static is a consolidation tag. Actual proposed-motion kind, axis, travel and descendants determine grouping.'],'limits':['This binds the read-only45-asset audit and exact correction diffs. It is not a fresh geometry/contact re-render or source load of all45 designs.','Native engine, physics, controller, whole-room/ship route, species fit and target-PC acceptance remain untested.']}
(OUT/'independent_interface_report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':True,'assets':45,'library_manifest_corrections':len(manifest_rows),'identical_textures':len(paths),'ledger_files':len(ledger),'consumer_index':str(index_path.relative_to(ROOT))},indent=2))
