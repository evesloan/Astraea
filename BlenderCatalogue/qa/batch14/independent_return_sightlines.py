"""Finite ordinary-eye screen through the receiver mouth, explicitly not room privacy."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
base=ROOT/'assets/aquatic_towel_use';mp=base/'AST-AQU-008.manifest.json';m=json.loads(mp.read_text());mouth=next(x for x in m['clear_volumes']if x['name']=='guest_mouth_aperture');lo=np.asarray(mouth['min_m']);hi=np.asarray(mouth['max_m']);eyes=[[x,y,z]for x,y,z in itertools.product([-.8,-.4,0,.4,.8],[-1.,-1.5,-2.],[1.10,1.65])];targets=[[x,.65,z]for x,z in itertools.product([-.28,-.14,0,.14,.28],[.15,.3,.45,.6,.75,.9,1.05,1.20,1.4,1.65])]
for suffix in ['', '_withdrawn']:
 gp=base/'exports'/('AST-AQU-008'+suffix+'.glb');n=Native(gp);t=n.tris@C;checked=[]
 for eye,target in itertools.product(eyes,targets):
  a=np.asarray(eye);b=np.asarray(target);frac=(hi[1]-a[1])/(b[1]-a[1]);p=a+frac*(b-a)
  if not(lo[0]+.002<p[0]<hi[0]-.002 and lo[2]+.002<p[2]<hi[2]-.002):continue
  hits=segment_triangles(a,b,t);checked.append({'eye_source_m':eye,'service_target_source_m':target,'mouth_plane_crossing_source_m':p.tolist(),'blocked':bool(hits)})
 above=[[[0,-1.2,1.65],[0,.65,1.65]],[[.75,-1.2,1.65],[.75,.65,1.65]]];bypass=[{'segment_source_m':[a,b],'clear_as_expected':not bool(segment_triangles(a,b,t))}for a,b in above];solid=bool(segment_triangles([0,-1.2,.60],[0,.65,.60],t));row={'state':'closed'if not suffix else'withdrawn','export_sha256':sha(gp),'export_path':str(gp.relative_to(ROOT)),'bounded_mouth_eye_rays':checked,'blocked_count':sum(x['blocked']for x in checked),'tested_count':len(checked),'above_or_around_housing_negative_controls':bypass,'solid_front_guard_positive_control':solid,'pass':len(checked)>20 and all(x['blocked']for x in checked)and all(x['clear_as_expected']for x in bypass)and solid};rows.append(row);print(row['state'],row['pass'],row['blocked_count'],'/',row['tested_count'],flush=True)
r={'passed':all(x['pass']for x in rows),'manifest_sha256':sha(mp),'states':rows,'scope':'Finite ordinary/seated-height example rays crossing the actual guest mouth rectangle toward nearby service-side targets. Does not certify continuous sightline occlusion, privacy, species eyes or any room. Rays above and beside the1.22m component deliberately remain clear; the return is not a privacy wall.','executed_script_sha256':sha(Path(__file__))};(OUT/'independent_return_sightlines.json').write_text(json.dumps(r,indent=2)+'\n')
