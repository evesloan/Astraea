"""Actual graphic orientation, including a deliberately rotated-UV negative control."""
from pathlib import Path
import json,hashlib,numpy as np
B=Path(__file__).resolve().parents[1];ns={'__file__':str(B/'qa/validate_glb.py')};exec((B/'qa/validate_glb.py').read_text().split('records=[validate')[0],ns)
rows=[]
def orientation(v,uv,indices):
 checks=[]
 for triangle in indices:
  for a,b in zip(triangle,np.roll(triangle,-1)):
   delta=v[b]-v[a];duv=uv[b]-uv[a]
   if abs(delta[0])>.001 and abs(delta[1])<1e-7:checks.append(abs(duv[1])<1e-7 and delta[0]*duv[0]>0)
   if abs(delta[1])>.001 and abs(delta[0])<1e-7:checks.append(abs(duv[0])<1e-7 and delta[1]*duv[1]<0)
 return bool(checks)and all(checks)
for path in sorted((B/'exports').glob('*.glb')):
 d,b=ns['read'](path)
 for m in d['meshes']:
  for p in m['primitives']:
   if 'hospitality_station_graphics'not in d['materials'][p['material']]['name']:continue
   v=ns['accessor'](d,b,p['attributes']['POSITION']);uv=ns['accessor'](d,b,p['attributes']['TEXCOORD_0']);i=ns['accessor'](d,b,p['indices']).reshape(-1,3);good=orientation(v,uv,i);bad=orientation(v,uv[:,::-1],i)
   rows.append({'file':path.name,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'graphic_mesh':m['name'],'horizontal_U_and_vertical_inverted_V':good,'rotated_uv_negative_control_rejected':not bad,'passes':good and not bad})
(B/'qa/graphic_uv_orientation.json').write_text(json.dumps({'results':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n');print([(r['file'],r['passes'])for r in rows])
