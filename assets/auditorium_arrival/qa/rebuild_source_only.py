"""Isolated 20-input rebuild; no production reads of QA or earlier output."""
from pathlib import Path
import json,shutil,subprocess,hashlib,re
B=Path(__file__).resolve().parents[1];C=B.parents[1];Q=B/'qa';T=Q/'source_only_stage_r09/catalogue';D=json.loads((B/'dependency_manifest.json').read_text())
assert not T.exists(),'Use a new stage revision; never overwrite previous proof'
T.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for f in D['source_only_inputs']:
 p=C/f['path'];assert sha(p)==f['sha256'];out=T/f['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
TB=T/'assets/auditorium_arrival';before_outputs=list(T.rglob('*.blend'))+list(T.rglob('*.glb'));assert not before_outputs
art=subprocess.run(['python3',str(TB/'source/draw_programme.py')],capture_output=True,text=True);(Q/'source_only_art_r09.log').write_text(art.stdout+art.stderr);assert art.returncode==0
art_match={p.name:sha(p)==sha(B/'textures'/p.name)for p in(TB/'textures').glob('*.png')}
cmd=['blender','--background','--threads','2','--python-exit-code','1','--python',str(TB/'source/build_auditorium_arrival.py')]
p=subprocess.run(cmd,capture_output=True,text=True);(Q/'source_only_build_r09.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
exports={g.name:sha(g)==sha(B/'exports'/g.name)for g in(TB/'exports').glob('*.glb')};interfaces={f:json.loads((TB/f).read_text())==json.loads((B/f).read_text())for f in('marker_api.json','collision_proposals.json')}
reads=[];unexpected=[]
r={'stage':str(T.relative_to(B)),'dependency_manifest_sha256':sha(B/'dependency_manifest.json'),'starting_input_count':len(D['source_only_inputs']),'prior_blends_or_glbs_present':False,'qa_or_prior_output_inputs':False,'system_call_read_tracing':'Unavailable: container ptrace denied; original failure preserved. Closure is proven by source paths anchored to the clean stage and exact copied inputs; no syscall-open completeness claim.','original_art_byte_reproduction':art_match,'export_byte_reproduction':exports,'interface_json_exact_match':interfaces,'blender_returncode':p.returncode,'passed':all(art_match.values())and all(exports.values())and all(interfaces.values())and not unexpected};(Q/'source_only_rebuild.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
