"""Version explicit local texture paths without changing any visual master bytes."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile,ast
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'assets/library_contents';OUT=ROOT/'qa/batch08/library_texture_path_revision';OLD=OUT/'original_inputs'
assert not OLD.exists(),'Preserve the prior revision evidence; do not rerun this patch blindly'
OLD.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[F/'texture_manifest.json',F/'make_book_textures.py',F/'build_library_contents.py',F/'dependency_manifest.json',F/'family_summary.json',F/'LIBRARY_CONTENTS_SHA256SUMS.txt',F/'README.md',*sorted(F.glob('AST-LIB-*.manifest.json'))]
initial={}
for p in files:
 initial[p.name]=sha(p);shutil.copy2(p,OLD/p.name)
visuals={str(p.relative_to(ROOT)):sha(p) for p in F.rglob('*') if p.is_file() and p.suffix in ('.blend','.glb','.png') and 'qa' not in p.parts}
old_texture_gen=sha(F/'make_book_textures.py');old_source_gen=sha(F/'build_library_contents.py')
p=F/'make_book_textures.py';s=p.read_text();old="{'resolution_px':[256,256],'provenance':"
new="{'interface_revision':'library-texture-paths-02','texture_root':'textures','path_base':'directory_containing_this_manifest','base_color_file_resolution':'texture_root/base_color_file','resolution_px':[256,256],'provenance':"
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
with tempfile.TemporaryDirectory(prefix='astraea-book-texture-reproduction-') as tmp:
 t=Path(tmp);shutil.copy2(p,t/p.name);subprocess.run([sys.executable,str(t/p.name)],check=True)
 generated=json.loads((t/'texture_manifest.json').read_text());assert generated['texture_root']=='textures'
 comparisons=[]
 for role,row in generated['materials'].items():
  old_file=F/'textures'/row['base_color_file'];new_file=t/'textures'/row['base_color_file'];assert old_file.read_bytes()==new_file.read_bytes(),role
  comparisons.append({'role':role,'file':str(old_file.relative_to(ROOT)),'sha256':sha(old_file),'generator_output_byte_identical':True})
 (F/'texture_manifest.json').write_bytes((t/'texture_manifest.json').read_bytes())
p=F/'build_library_contents.py';s=p.read_text();a=" for role,r in json.loads((ROOT/'texture_manifest.json').read_text())['materials'].items():";b=" texture_info=json.loads((ROOT/'texture_manifest.json').read_text())\n texture_root=ROOT/texture_info.get('texture_root','textures')\n for role,r in texture_info['materials'].items():";assert s.count(a)==1;s=s.replace(a,b)
a="ROOT/'textures'/r['base_color_file']";assert s.count(a)==1;s=s.replace(a,"texture_root/r['base_color_file']")
a="'texture_generator_sha256':hashlib.sha256((ROOT/'make_book_textures.py').read_bytes()).hexdigest()})"
b="'texture_generator_sha256':hashlib.sha256((ROOT/'make_book_textures.py').read_bytes()).hexdigest(),'texture_manifest_interface_revision':json.loads((ROOT/'texture_manifest.json').read_text()).get('interface_revision','legacy-implicit-paths'),'texture_manifest_sha256':hashlib.sha256((ROOT/'texture_manifest.json').read_bytes()).hexdigest()})";assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
old_ast=ast.parse((OLD/p.name).read_text());new_ast=ast.parse(s)
old_funcs={n.name:ast.dump(n,include_attributes=False) for n in old_ast.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))};new_funcs={n.name:ast.dump(n,include_attributes=False) for n in new_ast.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert old_funcs.keys()==new_funcs.keys();unchanged=[name for name in old_funcs if old_funcs[name]==new_funcs[name]];assert set(old_funcs)-set(unchanged)=={'reset','finish'}
new_source_gen=sha(p);new_texture_gen=sha(F/'make_book_textures.py');tm_hash=sha(F/'texture_manifest.json')
def update(row):
 if 'texture_generator_sha256' in row:
  assert row['texture_generator_sha256']==old_texture_gen
  row['texture_generator_sha256_at_original_export']=row['texture_generator_sha256'];row['texture_generator_sha256']=new_texture_gen
 if row.get('source_generator_sha256')==old_source_gen:
  row['source_generator_sha256_at_original_export']=row['source_generator_sha256'];row['source_generator_sha256']=new_source_gen
 row['texture_manifest_interface_revision']='library-texture-paths-02';row['texture_manifest_sha256']=tm_hash
 row['dependency_metadata_revision_note']='Batch08 explicit texture path metadata; existing Blender, GLB and texture pixels remain unchanged. Captured generator hashes are retained separately.'
for p in sorted(F.glob('AST-LIB-*.manifest.json')):
 m=json.loads(p.read_text());update(m);p.write_text(json.dumps(m,indent=2))
p=F/'family_summary.json';m=json.loads(p.read_text())
for row in m:update(row)
p.write_text(json.dumps(m,indent=2))
p=F/'dependency_manifest.json';m=json.loads(p.read_text());m['local_path_contract']={'revision':'library-texture-paths-02','manifest':'assets/library_contents/texture_manifest.json','relative_to':'directory containing texture_manifest.json','texture_root':'textures','filename_field':'materials.*.base_color_file','files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [F/'texture_manifest.json',F/'make_book_textures.py',F/'build_library_contents.py',*sorted((F/'textures').glob('*.png'))]]};p.write_text(json.dumps(m,indent=2))
p=F/'README.md';p.write_text(p.read_text()+'\n## Explicit texture path revision\n\nBatch08 adds `library-texture-paths-02`: each `base_color_file` resolves under `texture_root` (`textures/`) relative to the texture manifest directory. The loader honors that declared root, with the former folder as a backward-compatible default. All eight regenerated PNGs are byte-identical; editable masters and exported GLBs are unchanged. Current generator/manifest dependencies are versioned, while original export generator hashes remain separate provenance records.\n')
p=F/'LIBRARY_CONTENTS_SHA256SUMS.txt';lines=[]
for line in (OLD/p.name).read_text().splitlines():
 if not line.strip():continue
 before,name=line.split('  ',1);assert (F/name).is_file();lines.append(sha(F/name)+'  '+name)
p.write_text('\n'.join(lines)+'\n')
for rel,digest in visuals.items():assert sha(ROOT/rel)==digest,rel
resolved=[]
for role,row in generated['materials'].items():
 q=F/generated['texture_root']/row['base_color_file'];assert q.is_relative_to(F) and q.is_file() and sha(q)==row['sha256'];resolved.append(str(q.relative_to(ROOT)))
report={'passed':True,'scope':'Explicit local texture paths and reproducible metadata; no original model/texture/export mutation','revision':'library-texture-paths-02','old_texture_generator_sha256':old_texture_gen,'new_texture_generator_sha256':new_texture_gen,'old_source_generator_sha256':old_source_gen,'new_source_generator_sha256':new_source_gen,'texture_reproduction':comparisons,'explicit_paths_resolved':resolved,'unchanged_geometry_functions':unchanged,'functions_changed_only_for_path_loading_or_metadata':['reset','finish'],'visual_master_files_unchanged':visuals,'changed_files':[{'path':str(p.relative_to(ROOT)),'old_sha256':initial[p.name],'new_sha256':sha(p)} for p in files if initial[p.name]!=sha(p)],'isolated_blender_regeneration':'Pending separate bounded reproduction check'}
(OUT/'revision_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'textures_identical':len(comparisons),'visual_files_unchanged':len(visuals),'changed_metadata_code_files':len(report['changed_files'])},indent=2))
