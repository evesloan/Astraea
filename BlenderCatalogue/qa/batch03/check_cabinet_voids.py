"""Inspect clear volumes against exported triangles and separate collision boxes."""
from pathlib import Path
import json,sys,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa/batch02'))
from geometry_checks import triangles,triangles_intersect_box
p=ROOT/'assets/staff_workbay/AST-STF-007_supply_work_cabinet.glb';m=json.loads(p.with_suffix('.manifest.json').read_text());c=json.loads(p.with_suffix('.collision_proposal.json').read_text());geo=triangles(p)
rows=[]
for key in ['right_open_bays_m','left_locker_clear_volumes_m']:
 for i,v in enumerate(m['storage_openings'][key]):
  hits=triangles_intersect_box(geo,v['min'],v['max']);ch=[]
  for part in c['compound_parts']:
   ctr=np.array(part['centre_m']);size=np.array(part['size_m']);lo=ctr-size/2;hi=ctr+size/2
   overlap=np.minimum(hi,v['max'])-np.maximum(lo,v['min'])
   if (overlap>1e-6).all():ch.append({'part':part['source_part'],'overlap_m':overlap.tolist()})
  rows.append({'volume_group':key,'index':i,'volume':v,'visual_triangle_intersections':hits,'collision_proposal_intersections':ch})
out={'export_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'results':rows,'passes':not any(r['visual_triangle_intersections'] or r['collision_proposal_intersections'] for r in rows),'scope':'Four declared storage interiors remain geometrically hollow in the initial closed state; the door occludes left access until rotated. Separate simplified collision data checked only for clear-volume intrusion, not physics or controller acceptance.'}
(ROOT/'qa/batch03/independent_cabinet_voids.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
