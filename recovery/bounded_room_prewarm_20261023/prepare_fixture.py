#!/usr/bin/env python3
"""Resolve portable Git/PCK receipts and compose maps. No Godot or production main.
Retained Git sources must be materialized at --repo; only needed PCK entries extract.
"""
from pathlib import Path
import hashlib,json,argparse,os
import pck_inputs
S=Path(__file__).resolve().parent;R=S.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def file_hash(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(16*1024*1024),b''):h.update(block)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['baseline','candidate'],required=True)
 p.add_argument('--repo',type=Path,default=Path(os.environ.get('ASTRAEA_FIXTURE_REPO',str(R/'retained'))))
 p.add_argument('--base-pack',type=Path,default=Path(os.environ.get('ASTRAEA_FIXTURE_BASE_PACK',str(R/'library/latest/extracted/Astraea-e3af0334.pck'))))
 a=p.parse_args();repo=a.repo.resolve();pack=a.base_pack.resolve();contract=json.loads((S/'FIXTURE_INPUTS.json').read_text())
 assert file_hash(pack)==contract['pack_sha256'],'Retained PCK mismatch'
 pack_index=pck_inputs.index(pack)['entries'];mapping={}
 for row in json.loads((S/'PREIMAGE_CONTRACTS.json').read_text()):
  assert sha((repo/row['repository_path']).read_bytes())==row['sha256'],row['target']
 for row in contract['inputs']:
  source=repo/row['repository_path'] if 'repository_path' in row else None
  if source is None or not source.is_file():
   assert 'pack_entry' in row,'Missing exact Git input '+row['uri']
   source=S/'focused-inputs'/row['pack_entry']
   if not source.exists():pck_inputs.extract(pack,pack_index[row['pack_entry']],source,row['sha256'])
  data=source.read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'],row['uri']
  mapping[row['uri']]={'path':row['uri'],'source':str(source),'sha256':row['sha256']}
 if a.mode=='candidate':
  for path in (S/'payload/Game').rglob('*'):
   if path.is_file():
    uri='res://'+str(path.relative_to(S/'payload/Game'));mapping[uri]={'path':uri,'source':str(path),'sha256':sha(path.read_bytes())}
 project=S/'focused-project';project.mkdir(exist_ok=True)
 (project/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Astraea bounded room fixture"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
 out=S/'evidence';out.mkdir(exist_ok=True)
 (out/f'{a.mode}-source-map.json').write_text(json.dumps(sorted(mapping.values(),key=lambda x:x['path']),indent=2)+'\n')
 print(out/f'{a.mode}-source-map.json')
if __name__=='__main__':main()
