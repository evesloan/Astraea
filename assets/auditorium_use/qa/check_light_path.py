"""Finite source-geometry aperture/working-target ray checks, no photometry claim."""
from pathlib import Path
import numpy as np,json,math,hashlib
BASE=Path(__file__).resolve().parents[1];ident='AST-CUL-004';rec=json.loads((BASE/f'{ident}.manifest.json').read_text());data=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text())[ident];pivot=np.array([0,.115,1.54]);origin=np.array([0,.015,1.55]);rows=[]
def rotation(a):
 c=math.cos(math.radians(a));s=math.sin(math.radians(a));return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def hits(p,d,tris):
 e1=tris[:,1]-tris[:,0];e2=tris[:,2]-tris[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);ok=np.abs(a)>1e-10;f=np.divide(1,a,out=np.zeros_like(a),where=ok);s=p-tris[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*np.einsum('j,ij->i',d,q);t=f*np.einsum('ij,ij->i',e2,q);mask=ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-5);return t[mask]
for angle in(0,-12.5,-25):
 R=rotation(angle);meshes={}
 for part in data['parts']:
  v=np.array(part['vertices']);v=(v-pivot)@R.T+pivot if part['movement_group']=='LIGHT_AIM_X'else v;meshes[part['name']]=v[np.array(part['triangles'])]
 for dx,dy in[(0,0),(-.025,0),(.025,0),(0,-.015),(0,.015)]:
  p=R@(origin+[dx,dy,0]-pivot)+pivot;d=R@np.array([0,0,-1]);allhits=[]
  for name,tris in meshes.items():
   ts=hits(p,d,tris)
   if len(ts):allhits.append((float(ts.min()),name))
  allhits.sort();first=allhits[0]if allhits else None;target=(p+d*first[0]).tolist()if first else None
  rows.append({'aim_angle_degrees':angle,'emitter_sample_offset_source_closed_m':[dx,dy,0],'origin_source_m':p.tolist(),'direction_source':d.tolist(),'first_hit':first[1]if first else None,'hit_source_m':target,'distance_m':first[0]if first else None,'passes':first is not None and first[1]=='supported_clipped_work_tray'})
# Positive control inserts a small solid plane in the ray 30mm below emitter.
p=origin;d=np.array([0,0,-1]);tri=np.array([[[-.1,-.1,1.52],[.1,-.1,1.52],[0,.1,1.52]]]);control=hits(p,d,tri);out={'source_sha256':rec['source_sha256'],'scope':'15 finite central-aperture rays at three supported aiming states; full real housing/yoke/column/notes/tray triangle intersections; not full aperture illumination, glare, photometry or runtime light','samples':rows,'occluder_positive_control_detected':bool(len(control)),'all_passed':all(x['passes']for x in rows)and bool(len(control))};(BASE/'qa/light_aperture_paths.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
