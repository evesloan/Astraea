"""Read retained inputs; copy only to this bounded package. No host Git mutation."""
from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
P=Path(__file__).resolve().parents[1];HOST=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
files=[]
for base in ['Game/docs/master_source','Game/data','Game/scripts','BlenderCatalogue/references/retail','DesignArchive/Planning/Supporting_Analyses/d09-retail-handoff','BlenderCatalogue/standards','BlenderCatalogue/materials']:
 for f in (HOST/base).rglob('*'):
  if f.is_file() and f.suffix in ['.json','.gd','.md','.py','.png','.jpg','.webp','.docx'] and '.godot' not in f.parts:files.append(f)
for n in ['Game/AGENTS.md','Game/docs/ARCHITECTURAL_DELIVERY_RULES.md','Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md','Game/docs/THREAD_SHELL_PROGRESS.md','Game/docs/CURRENT_STATUS.md','Game/docs/GITHUB_BACKUPS.md','Game/docs/AUTOMATED_BACKUPS.md']:
 if (HOST/n).exists():files.append(HOST/n)
for base in ['retail_curios_room','retail_display','retail_work','retail_textile_display','orchard_exchange']:
 for f in (HOST/'BlenderCatalogue/assets'/base).rglob('*'):
  if f.is_file() and f.suffix in ['.blend','.glb','.json','.py'] and 'qa' not in f.parts:files.append(f)
hashes={str(f.relative_to(HOST)).replace('\\','/'):sha(f) for f in sorted(set(files))}
for rel,h in hashes.items():
 f=HOST/rel;t=P/'dependencies'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,t);assert sha(t)==h==sha(f)
write('qa/retained_input_hashes.json',hashes)
aq=HOST/'external_packages/aquatic_district_20261009/RESOURCE_HASHES.json'
write('qa/aquatic_retention.json',{'manifest_sha256':sha(aq),'files':{n:sha(aq.parent/n) for n in json.loads(aq.read_text())['files']},'scope':'Read-only baseline; leave aquatic package unchanged'})
def git(*a):return subprocess.run(['git','-C',str(HOST),*a],capture_output=True,text=True,check=True).stdout.strip()
write('qa/retention_baseline.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'origin_pushurl':git('remote','get-url','--push','origin'),'status_lines':len(git('status','--porcelain').splitlines()),'main_remote':git('ls-remote','https://github.com/evesloan/Astraea.git','refs/heads/main'),'aquatic_remote':git('ls-remote','https://github.com/evesloan/Astraea.git','refs/heads/handoff/aquatic-district-20261009'),'model_effort':'Actual runtime model/effort not exposed; requested Sol High is not verification'})
print('RETAINED_INPUTS_PROTECTED',len(hashes))
