"""Actual before/after source-only generation for the two directory fixes."""
from pathlib import Path
import json,hashlib,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08/source_output_directory_revision';OLD=OUT/'original_inputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=[('botanical_canopy','build_canopy.py','support_contacts.json',['AST-BOT-001.glb']),('aquatic_lounge','build_aquatic_lounge.py','join_checks.json',['exports/AST-AQU-001.glb','exports/AST-AQU-002.glb'])];rows=[]
masters=json.loads((OUT/'revision_report.json').read_text())['master_files_unchanged']
for family,script,qa_name,exports in cases:
 pair=[]
 for phase in ('before','after'):
  with tempfile.TemporaryDirectory(prefix='astraea-output-dir-'+phase+'-') as tmp:
   t=Path(tmp);f=t/'assets'/family;(f/'source').mkdir(parents=True);shutil.copytree(ROOT/'materials',t/'materials');shutil.copytree(ROOT/'standards',t/'standards')
   source=(OLD/'assets'/family/'source'/script) if phase=='before' else (ROOT/'assets'/family/'source'/script);shutil.copy2(source,f/'source'/script)
   # Source packages contain exports already. Empty that existing directory in
   # the negative control to isolate the missing QA parent, not absent outputs.
   if phase=='before' and family=='aquatic_lounge':(f/'exports').mkdir()
   cmd=['blender','--background','--threads','1','--python-exit-code','1','--python',str(f/'source'/script)]
   done=subprocess.run(cmd,cwd=t,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);log=OUT/(family+'_'+phase+'.log');log.write_text(done.stdout)
   if phase=='before':
    assert done.returncode!=0 and 'FileNotFoundError' in done.stdout and qa_name in done.stdout,(family,done.returncode,done.stdout[-1600:])
    pair.append({'phase':phase,'exit_code':done.returncode,'expected_missing_qa_parent_failure':True,'source_sha256':sha(source),'log':str(log.relative_to(ROOT))})
   else:
    assert done.returncode==0 and (f/'qa'/qa_name).is_file(),(family,done.returncode,done.stdout[-1600:]);same=[]
    for rel in exports:
     generated=f/rel;existing=ROOT/'assets'/family/rel;assert generated.is_file() and generated.read_bytes()==existing.read_bytes(),(family,rel)
     same.append({'path':str(existing.relative_to(ROOT)),'sha256':sha(existing),'generated_bytes_identical':True})
    pair.append({'phase':phase,'exit_code':done.returncode,'source_sha256':sha(source),'qa_output_created':True,'empty_output_directories_required_before_run':False,'exports':same,'log':str(log.relative_to(ROOT))})
 rows.append({'family':family,'results':pair})
for rel,digest in masters.items():assert sha(ROOT/rel)==digest,rel
report={'passed':True,'scope':'Original missing-parent failures and corrected fresh source generation. No current master overwritten, no render/network.','cases':rows,'unchanged_current_master_files':masters}
(OUT/'isolated_rebuild_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'fixed_generators':2,'byte_identical_exports':3,'unchanged_master_files':len(masters)},indent=2))
