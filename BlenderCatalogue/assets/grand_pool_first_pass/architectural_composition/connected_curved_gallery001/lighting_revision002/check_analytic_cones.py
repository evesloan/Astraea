from pathlib import Path
import json,sys,ast,hashlib,numpy as np,math
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'));import check_programme as q
unit=q.unit;TOL=q.TOL;p=q.C/'assets/grand_pool_first_pass/finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='cone_triangle'],type_ignores=[]),str(p),'exec'))
actual=q.read(B/'source_build002/qa/BUILD_EVALUATED_CORE.json');parts=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']])for p in actual['parts']]);cm={p['name']:p for p in parts};rows=[]
for f in actual['fixture_reservations']:
 pos=f['position_xyz'];d=f['direction_xyz'];rad=.06*math.tan(math.radians(55));bb=[q.add(pos,[-rad-.06]*3),q.add(pos,[rad+.06]*3)];hits=[]
 for p in parts:
  if not q.overlap(bb,p['bounds'],-TOL):continue
  for i,t in enumerate(p['triangles']):
   h=cone_triangle(pos,d,55,t)
   if h:hits.append({'part':p['name'],'triangle':i,**h})
 lens=q.rayhits(pos,q.add(pos,q.mul(d,-.1)),[cm[f['physical_lens']]]);rows.append({'name':f['name'],'continuous_cone_triangle_hits':hits,'physical_lens_behind_marker':lens,'half_angle_degrees':55,'forward_length_m':.06})
issues=[r for r in rows if r['continuous_cone_triangle_hits']or not r['physical_lens_behind_marker']]
r={'status':'PASS_ACTUAL_SOURCE_CONTINUOUS_APERTURE_CONES'if not issues else'CORRECTION_REQUIRED','source_sha256':q.read(B/'source_build002/qa/BUILD_RECEIPT.json')['sha256'],'method':'Analytic finite cone/actual evaluated triangle intersection. Slab clipping and quadratic minimization over vertices, edges and triangle interiors, no angular sampling.','supplements':'RECEIVER_PROOF.json sampled cone exits are diagnostics; this report establishes the complete finite cone claim.','fixtures':rows,'issues':issues,'native_brightness_selection_accepted':False};(B/'ANALYTIC_APERTURE_PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'issues':issues},indent=2),flush=True)
