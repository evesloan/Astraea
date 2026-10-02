"""Close two proven compact-source output-directory assumptions."""
from pathlib import Path
import json,hashlib,shutil,ast
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08/source_output_directory_revision';OLD=OUT/'original_inputs';assert not OLD.exists();OLD.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
families={'botanical_canopy':'build_canopy.py','aquatic_lounge':'build_aquatic_lounge.py'};masters={};changes=[]
for family,script in families.items():
 f=ROOT/'assets'/family
 for p in f.rglob('*'):
  if p.is_file() and p.suffix in ('.blend','.glb','.png') and 'qa' not in p.parts:masters[str(p.relative_to(ROOT))]=sha(p)
 selected=[f/'source'/script,f/'README.md']
 if family=='aquatic_lounge':selected += [f/'AST-AQU-001.manifest.json',f/'AST-AQU-002.manifest.json',f/'manifest.json',f/'dependency_manifest.json',f/'SHA256SUMS.txt']
 before={}
 for p in selected:
  dest=OLD/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);before[str(p.relative_to(ROOT))]=sha(p)
 p=f/'source'/script;old=s=p.read_text();old_hash=sha(p)
 if family=='botanical_canopy':
  key='ROOT=Path(__file__).resolve().parents[1]; CAT=ROOT.parents[1]\n';new=key+"(ROOT/'qa').mkdir(parents=True,exist_ok=True)\n"
 else:
  key='ROOT=Path(__file__).resolve().parents[1]\n';new=key+"for output_folder in ('source','exports','qa'):(ROOT/output_folder).mkdir(parents=True,exist_ok=True)\n"
 assert s.count(key)==1;s=s.replace(key,new);p.write_text(s)
 af=lambda t:{n.name:ast.dump(n,include_attributes=False) for n in ast.parse(t).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 assert af(old)==af(s);new_hash=sha(p)
 if family=='aquatic_lounge':
  def refresh(row):
   if row.get('generator_sha256')==old_hash:row['generator_sha256_at_original_export']=old_hash;row['generator_sha256']=new_hash
  for mp in [f/'AST-AQU-001.manifest.json',f/'AST-AQU-002.manifest.json',f/'manifest.json']:
   m=json.loads(mp.read_text())
   if 'assets' in m:
    for row in m['assets']:refresh(row)
   else:refresh(m)
   mp.write_text(json.dumps(m,indent=2)+'\n')
  mp=f/'dependency_manifest.json';m=json.loads(mp.read_text());m['generator_dependency']={'path':str(p.relative_to(ROOT)),'sha256':new_hash,'revision':'creates-source-export-and-qa-output-directories','visual_master_bytes_unchanged':True};mp.write_text(json.dumps(m,indent=2)+'\n')
 mp=f/'README.md';mp.write_text(mp.read_text()+'\n## Compact-source rebuild readiness\n\nBatch08 makes the generator create its own output directories before writing completion evidence. It can complete from source-only staging without a pre-existing review folder. Existing editable masters, exported geometry and texture bytes are unchanged; original generator provenance is retained in the checkpoint evidence.\n')
 if family=='aquatic_lounge':
  mp=f/'SHA256SUMS.txt';rows=[]
  for line in (OLD/mp.relative_to(ROOT)).read_text().splitlines():
   if line.strip():_,name=line.split('  ',1);rows.append(sha(f/name)+'  '+name)
  mp.write_text('\n'.join(rows)+'\n')
 changes.extend({'path':str(p.relative_to(ROOT)),'old_sha256':before[str(p.relative_to(ROOT))],'new_sha256':sha(p)} for p in selected if sha(p)!=before[str(p.relative_to(ROOT))])
for rel,digest in masters.items():assert sha(ROOT/rel)==digest
report={'passed':True,'scope':'Output-directory creation and current dependency/provenance metadata only','function_ASTs_unchanged':True,'master_files_unchanged':masters,'changed_files':changes,'isolated_before_after_rebuild':'Pending separate check'}
(OUT/'revision_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'changed_files':len(changes),'unchanged_master_files':len(masters),'function_ASTs_unchanged':True},indent=2))
