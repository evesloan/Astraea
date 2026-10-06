#!/usr/bin/env python3
"""Scratch-only exact-source triangle ray/angle screen. No engine, import or live writes."""
import json,hashlib,math,collections
from pathlib import Path
import numpy as np
D=Path(__file__).parent
K=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/court_A_completion004/runtime_export002')
R=D.parents[2]/'runtime_stage01/exports_run005'
G=Path('/workspace/shared/astraea-godot-production-20261003/data/architecture/THEATER_RUNTIME_STAGE001.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.load(open(K/'qa/EXPORT_RECEIPT.json'));n=np.load(K/'witnesses/source_triangle_attributes.npz');s=json.load(open(R/'EXPORT_RECEIPT.json'));w=np.load(R/'source_triangle_attributes.npz')
assert sha(K/'witnesses/source_triangle_attributes.npz')==r['source_attribute_archive_sha256']
assert sha(R/'source_triangle_attributes.npz')==s['source_attribute_archive_sha256']
g=json.load(open(G));f=next(f for f in g['fixtures'] if f['id']=='FP2_D11_BANK_0');assert s['source_sha256']==g['source_sha256']
o=np.array(f['position_world']);source_hashes={str(p):sha(p) for p in [G,K/'qa/EXPORT_RECEIPT.json',K/'witnesses/source_triangle_attributes.npz',R/'EXPORT_RECEIPT.json',R/'source_triangle_attributes.npz']}
ct=[];cn=[];ids=[];batchids=[];tribatch=[];mats=[];scope=[]
def add(t,no,sem,b,material,domain):
 ct.extend(t);cn.extend(no);ids.extend(sem);batchids.extend([b]*len(t));tribatch.extend(range(len(t)));mats.extend([material]*len(t));scope.extend([domain]*len(t))
for b in r['batches']:
 t=n[b['name']+'_xyz']; no=n[b['name']+'_normal'];sem=[]
 # Dict order is Counter insertion order from contiguous object loop in retained exporter.
 for name,c in b['semantic_triangle_counts'].items():sem.extend([name]*c)
 assert len(sem)==len(t)
 if b['kind']=='authored':add(t,no,sem,b['name'],b['material'],'new_court')
 else:
  for inst in r['instances']:
   if inst['definition']!=b['definition']:continue
   M=np.array(inst['native_matrix']);add(t@M[:3,:3].T+M[:3,3],no@np.linalg.inv(M[:3,:3]),[inst['id']+'/'+v for v in sem],b['name']+'@'+inst['id'],b['material'],'new_court')
new_count=len(ct)
for b in s['batches']:
 if b['kind']!='static':continue
 t=w[b['name']+'_xyz']; no=w[b['name']+'_normal'];j=0
 for name,c in b['semantic_triangle_runs']:
  if name.startswith('FP2_D11_COURT_A_'):add(t[j:j+c],no[j:j+c],[name]*c,b['name']+'#'+name,b['material'],'retained_court_architecture')
  j+=c
ct=np.array(ct);cn=np.array(cn);centers=ct.mean(1);norms=cn.mean(1);norms/=np.maximum(np.linalg.norm(norms,axis=1)[:,None],1e-20)
ids=np.array(ids);batchids=np.array(batchids);tribatch=np.array(tribatch);mats=np.array(mats);scope=np.array(scope)
fixture=np.array(['FP2_D11_COURT_A_LIGHT_1_' in s for s in ids])
e1=ct[:,1]-ct[:,0];e2=ct[:,2]-ct[:,0];tv=o-ct[:,0];q=np.cross(tv,e1)
def ray(p):
 d=p-o;dist=float(np.linalg.norm(d));d/=dist
 h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);valid=abs(det)>1e-12
 inv=np.divide(1,det,out=np.zeros_like(det),where=valid);u=np.einsum('ij,ij->i',tv,h)*inv;v=(q@d)*inv;tt=np.einsum('ij,ij->i',e2,q)*inv
 hits=np.flatnonzero(valid&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(tt>1e-6)&(tt<dist-1e-5))
 if not len(hits):return None
 z=hits[np.argmin(tt[hits])];return {'semantic':str(ids[z]),'batch':str(batchids[z]),'triangle':int(tribatch[z]),'distance_m':float(tt[z]),'domain':str(scope[z]),'point':(o+d*tt[z]).tolist(),'is_fixture':bool(fixture[z])}
configs={'current_75':{'aim':f['aim_world'],'fullcone':75},'pitch40_75':{'aim':[0,-math.sin(math.radians(40)),-math.cos(math.radians(40))],'fullcone':75},'pitch45_75':{'aim':[0,-2**-.5,-2**-.5],'fullcone':75},'pitch40_90':{'aim':[0,-math.sin(math.radians(40)),-math.cos(math.radians(40))],'fullcone':90}}
samples=[]
def sample(group,j,bc):
 p=bc@ct[j];nv=bc@cn[j];nv/=max(np.linalg.norm(nv),1e-20);vec=p-o;distance=np.linalg.norm(vec);unit=vec/distance
 angles={k:float(np.degrees(np.arccos(np.clip(unit@np.array(v['aim']),-1,1)))) for k,v in configs.items()}
 samples.append({'group':group,'batch':str(batchids[j]),'triangle':int(tribatch[j]),'semantic':str(ids[j]),'barycentric':bc.tolist(),'point':p.tolist(),'normal':nv.tolist(),'distance_m':float(distance),'incidence_cosine':float(nv@-unit),'blocker':ray(p),'angles_degrees':angles,'inside_cone':{k:angles[k]<=v['fullcone']/2 for k,v in configs.items()},'in_range':bool(distance<7.9)})
leaf=np.flatnonzero(np.array(['CA4_crown' in s and '_leaf' in s for s in ids]))
# Every source leaf triangle centroid is retained, not a proxy patch.
for j in leaf:sample('crown_front' if centers[j,2]>=-143.1 else 'crown_rear',j,np.array([1/3]*3))
for j in np.flatnonzero((mats=='court_A_printed_paper')|(mats=='court_A_original_programme')):
 group='wall_programme' if mats[j]=='court_A_original_programme' else 'reception_programmes' if 'reception' in ids[j] else 'side_table_programmes'
 # 66 points per face, a triangular barycentric grid including exact perimeter.
 for a in range(11):
  for b in range(11-a):sample(group,j,np.array([a/10,b/10,(10-a-b)/10]))
for j in np.flatnonzero(np.array(['A4_reception/AST-CUL-002::' in s and ('counter' in s or 'writing' in s or 'usher_mark' in s) for s in ids])):
 if norms[j,1]>.7:
  group='main_counter_top' if ids[j].endswith('::main_rounded_usher_counter') else 'low_writing_top' if ids[j].endswith('::low_rounded_writing_stone') else 'reception_other_upward_faces'
 elif norms[j,2]>.7:
  group='usher_mark_public_face' if ids[j].endswith('::original_usher_mark') else 'reception_public_front_other'
 else:continue
 sample(group,j,np.array([1/3]*3))
summary={}
for group in sorted(set(x['group'] for x in samples)):
 rows=[x for x in samples if x['group']==group];summary[group]={'count':len(rows),'distance_m':[min(x['distance_m'] for x in rows),max(x['distance_m'] for x in rows)],'unblocked':sum(x['blocker'] is None for x in rows),'blockers':dict(collections.Counter(x['blocker']['semantic'] for x in rows if x['blocker'])),'in_range':sum(x['in_range'] for x in rows),'configurations':{}}
 for k,v in configs.items():
  clear=[x for x in rows if x['blocker'] is None and x['in_range']];ang=[x['angles_degrees'][k] for x in rows]
  summary[group]['configurations'][k]={'angle_min_max_degrees':[min(ang),max(ang)],'inside_cone':sum(x['inside_cone'][k] for x in rows),'clear_in_range_inside':sum(x['inside_cone'][k] for x in clear),'clear_receiver_max_angle_degrees':max([x['angles_degrees'][k] for x in clear],default=None)}
out={'status':'SCRATCH_GEOMETRIC_SCREEN_ONLY_NO_ENGINE_OR_LIVE_PATCH','source_hashes':source_hashes,'fixture':f,'configs':configs,'new_court_triangle_count':new_count,'retained_court_architecture_triangles':len(ct)-new_count,'fixture_triangles':int(fixture.sum()),'method':{'triangles':'Exact native-world Court authored NPZ triangles, prototypes transformed using receipt native_matrix; retained FP2_D11_COURT_A architecture from source witness with semantic_triangle_runs. Authored/prototype semantic Counter insertion order follows each contiguous object loop; witness triangle index remains definitive.','samples':'All 1440 authored crown broadleaf triangle centroids, a barycentric 0.1-step grid including perimeter on all 8 printed programme triangles, and relevant reception top/public-facing triangle centroids. crown_front uses centroid native z>=-143.1 (crown stem plane); reports rear too.','rays':'Two-sided Moller-Trumbore exact triangles, segment epsilon source1e-6m and receiver1e-5m. All Court geometry blocks; retained architecture includes opal lens. Incidence is source authored corner-normal interpolation; negative faces may be double sided.','limits':'Not rendered luminance, photometry, light-selector residence, shadow bias, raster visibility, or whole current ship occlusion. Retained Court architectural subset plus complete newCourt only. Edge samples intentionally include possible grazing hits. No engine/import or shared writes.'},'summary':summary,'samples':samples}
(D/'SOURCE_RECEIVER_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['samples','source_hashes','fixture','method']},indent=2))
assert all(sha(p)==h for p,h in source_hashes.items())
