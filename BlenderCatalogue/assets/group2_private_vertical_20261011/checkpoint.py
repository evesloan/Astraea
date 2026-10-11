"""Preserve the sealed handoff and independently verify every successor byte."""
import argparse,datetime,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
PARENT='75068311728a44aac02732496edf2f810c624841'
OWNED=['BlenderCatalogue/assets/group2_private_vertical_20261011','Game/assets/group2_private_vertical',
       'Game/data/group2_private_vertical','Game/scripts/group2_private_vertical','Game/tests/group2_private_vertical']
def sha(path):
 h=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def only_additions(lines):
 return all(line.startswith('A\t')and any(line[2:].startswith(p+'/')for p in OWNED)for line in lines)

def make():
 assert git('rev-parse','HEAD')==PARENT
 assert only_additions(git('diff','--name-status',PARENT).splitlines())
 prior=ROOT/'BlenderCatalogue/assets/group2_completion_20261011/MANIFEST.json'
 assert sha(prior)=='fd5042631e8801750564025411fb6a62da5d92135120ed3ff461bab903d473f5'
 old=json.loads(prior.read_text())
 for row in old['files']:
  f=ROOT/row['path'];assert f.stat().st_size==row['bytes']and sha(f)==row['sha256'],row['path']
 baseline=json.loads((ROOT/'CHECKPOINT.json').read_text());count=0
 for project in baseline['projects'].values():
  for rel,expected in project['files'].items():
   assert sha(ROOT/project['prefix']/rel)==expected,rel;count+=1
 interfaces=json.loads((ROOT/'Game/data/group2_private_vertical/INTERFACES.json').read_text())
 for rel,expected in interfaces['dependency_pins'].items():assert sha(ROOT/rel)==expected,rel
 for suite in interfaces['suites']:
  key=str(suite['source_index']);assert key!='790'
  receipt=json.loads((ROOT/'BlenderCatalogue/assets/group2_completion_20261011/evidence'/('recovery_'+key+'.json')).read_text())
  assert sha(pathlib.Path(receipt['native_local']))==suite['native_sha256']
  assert sha(ROOT/receipt['runtime_path'])==suite['runtime_sha256']
 for name in ['SOURCE_NATIVE_r002.json','CONVERSATION_NATIVE_r001.json','PRIVATE_FINAL_PASS010.json',
              'CONVERSATION_PASS001.json','LIGHTING_PASS001.json','PRIVATE_CONTEXT_RECEIPT001.json']:
  assert json.loads((P/'evidence'/name).read_text())['pass'],name
 for native,receipt in [('PRIVATE_VERTICAL_KITS_r002.blend','SOURCE_NATIVE_r002.json'),
                        ('CONVERSATION_RECEIVERS_r001.blend','CONVERSATION_NATIVE_r001.json')]:
  j=json.loads((P/'evidence'/receipt).read_text());assert sha(P/'source'/native)==j['native_sha256']
  for row in j.get('pit_receivers',j.get('exports',[])):assert sha(ROOT/row['path'])==row['sha256']
 original_head=subprocess.check_output(['git','-C','/workspace/Astraea','rev-parse','HEAD'],text=True).strip()
 assert original_head=='144ba8cd8d6105c7b1959f25ce88cb5d89185f0b'
 write(P/'evidence/PRESERVATION_AUDIT.json',{'pass':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'sealed_parent':PARENT,'all_parent_manifest_files_unchanged':len(old['files'])+1,
  'baseline_files_unchanged':count,'original_checkout_head_unchanged':original_head,
  'all_five_native_and_runtime_originals_unchanged':True,'registered_dependency_pins_unchanged':True,
  'only_additive_owned_paths':OWNED,'790_excluded':True,'whole_Group2_accepted':False})
 files=[];manifest=P/'MANIFEST.json'
 for prefix in OWNED:
  for path in sorted((ROOT/prefix).rglob('*')):
   if not path.is_file()or path==manifest:continue
   assert not path.is_symlink()and '__pycache__'not in path.parts
   files.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':sha(path)})
 signature=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 write(manifest,{'schema':'astraea.group2_private_successor_manifest.v1','parent':PARENT,'owned_paths':OWNED,
  'files':files,'file_count':len(files),'bytes':sum(r['bytes']for r in files),'signature':signature,
  'signature_algorithm':"SHA256 of UTF-8 json.dumps(files,sort_keys=True,separators=(',',':'))",'self_excluded':True,
  'status':'Scoped source construction verified; shared adoption and whole Group2 unfinished'})
 print(json.dumps({'pass':True,'prior_files_preserved':len(old['files'])+1,'baseline_files_preserved':count,
                  'new_files_including_manifest':len(files)+1,'manifest_sha256':sha(manifest),'signature':signature}))

def verify(output):
 path=P/'MANIFEST.json';m=json.loads(path.read_text());files=m['files']
 assert hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()==m['signature']
 actual={str(p.relative_to(ROOT))for prefix in OWNED for p in (ROOT/prefix).rglob('*')if p.is_file()}
 assert actual=={r['path']for r in files}|{str(path.relative_to(ROOT))}
 for row in files:
  f=ROOT/row['path'];assert f.stat().st_size==row['bytes']and sha(f)==row['sha256'],row['path']
 changed=git('diff','--name-status',PARENT,'HEAD').splitlines();assert len(changed)==len(files)+1 and only_additions(changed)
 assert not git('diff','--name-only','HEAD')
 write(output,{'pass':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remote_url':git('remote','get-url','origin'),
  'commit':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),'parent':git('rev-parse','HEAD^'),
  'downloaded_and_SHA256_verified_successor_files':len(files)+1,'bytes_excluding_manifest':m['bytes'],
  'manifest_sha256':sha(path),'manifest_signature':m['signature'],'all_paths_additive_and_owned':True,
  'method':'Fresh independent GitHub clone, no local object alternates, all owned bytes read back'})
 print(output.read_text())
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--verify-output',type=pathlib.Path);args=parser.parse_args()
 if args.verify_output:verify(args.verify_output)
 else:make()
