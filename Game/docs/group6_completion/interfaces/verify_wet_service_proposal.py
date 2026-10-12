"""Reproduce the scoped retained compiler receiving survey, including edges."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[4]
P=Path(__file__).with_name('WET_SERVICE_RECEIVING_PROPOSAL001.json')
spec=json.loads(P.read_text());regions=[]
for path,digest in spec['input_sha256'].items():
 p=R/path;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,path
 for r in json.loads(p.read_text())['regions']:
  if 42<r['floor_y']<47:regions.append((path,r))
def contained(p,t):
 x,z=p;sign=[(b[0]-a[0])*(z-a[1])-(b[1]-a[1])*(x-a[0]) for a,b in zip(t,t[1:]+t[:1])]
 return min(sign)>=-1e-7 or max(sign)<=1e-7
for point in spec['sampled_points']:
 xyz=point['xyz'];owners=[{'input':path,'region':r['id'],'floor_y':r['floor_y']} for path,r in regions if any(contained([xyz[0],xyz[2]],t) for t in r['triangles'])]
 assert owners==point['floor_owners_in_retained_compiler_inputs'],point
print('PASS: 7 exact receiving samples/3 pinned retained inputs; boundary is inclusive. No exterior construction or current-root acceptance.')
