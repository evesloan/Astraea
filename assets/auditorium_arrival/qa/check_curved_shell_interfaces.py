"""Exact convex material versus actual shell face patches; complete linear LP envelope screen."""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
B=Path(__file__).resolve().parents[1];S=json.loads((B/'qa/source_geometry.json').read_text())['AST-CUL-002'];P=S['parts'];R=json.loads((B/'AST-CUL-002.manifest.json').read_text());EPS=2e-6
# Actual triangulated rear-facing shell surface patches define the bowed inner envelope.
patches=[]
for name,p in P.items():
 if not name.startswith('curved_public_shell_segment_'):continue
 v=np.array(p['vertices'],float)
 outer_c=None
 for ff in p['triangles']:
  tt=v[ff];nn=np.cross(tt[1]-tt[0],tt[2]-tt[0]);nn/=np.linalg.norm(nn)
  if nn[1]<-.8:outer_c=float(np.dot(nn,tt[0])/nn[1]);break
 assert outer_c is not None
 for f in p['triangles']:
  t=v[f];n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)
  if n[1]<.8:continue
  # y_inner = c + ax*x + az*z; matching outer-plane intercept is also measured from actual triangles.
  ax,az=-n[0]/n[1],-n[2]/n[1];c=np.dot(n,t[0])/n[1]
  tri=t[:,[0,2]];cent=tri.mean(0);A=[];b=[]
  for a,z in zip(tri,np.roll(tri,-1,axis=0)):
   e=z-a;normal=np.array([e[1],-e[0]]);val=np.dot(normal,a)
   if np.dot(normal,cent)>val:normal=-normal;val=-val
   A.append([normal[0],0,normal[1]]);b.append(val)
  patches.append({'part':name,'A':np.array(A),'b':np.array(b),'objective':np.array([-ax,1,-az]),'c':c,'actual_depth_y':float(c-outer_c)})
exception={
'recessed_stone_counter_plinth':'Deliberate full floor plinth and toe return',
'low_wing_left_cheek':'Actual perimeter structural end return, forms left public shell termination',
'right_full_height_cheek':'Actual perimeter structural end return, forms right public shell termination',
'low_rounded_writing_stone':'Intended lower stone writing surface with public overhang',
'main_rounded_usher_counter':'Intended upper stone working surface with public overhang',
'usher_mark_timber_bearing':'Deliberate planar sign plaque supported across central public shell; its returned ends remain visible',
'original_usher_mark':'Original public-facing graphic on real supported plaque',
'low_public_amber_insert':'Deliberate public-facing textile insert supported by complete horizontal carrier rails',
'amber_insert_carrier_0.3':'Deliberate public-facing insert frame/carrier, supported across bowed shell',
'amber_insert_carrier_0.65':'Deliberate public-facing insert frame/carrier, supported across bowed shell'}
rows=[]
for name,p in P.items():
 if name.startswith('curved_public_shell_segment_')or name in exception:continue
 vs=np.array(p['vertices'],float);h=ConvexHull(vs);travel=.28 if p['owner']=='USHER_DRAWER'else 0
 states=[]
 for state,dy in [('closed',0),('first_millimetre',min(.001,travel)),('access',travel)]:
  minima=[]
  for patch in patches:
   A=np.vstack([h.equations[:,:3],patch['A']]);rhs=np.r_[-h.equations[:,3]+h.equations[:,1]*dy,patch['b']]
   r=linprog(patch['objective'],A_ub=A,b_ub=rhs,bounds=[(None,None)]*3,method='highs')
   if r.success:minima.append((r.fun-patch['c'],r.x.tolist(),patch['part'],patch['actual_depth_y']))
  if minima:
   worst=min(minima,key=lambda r:r[0]);inner=worst[0];outer=inner+worst[3]
   states.append({'state':state,'translation_source_y_m':dy,'minimum_clearance_to_actual_inner_shell_plane_m':inner,'minimum_clearance_to_actual_public_outer_shell_plane_m':outer,'worst_witness_source_m':worst[1],'actual_shell_patch':worst[2],'actual_shell_depth_y_m':worst[3],'public_face_material_breach':bool(outer<-EPS),'inside_shell_bearing_penetration_m':max(0,-inner)})
  else:states.append({'state':state,'translation_source_y_m':dy,'overlaps_shell_xz_domain':False,'public_face_material_breach':False})
 expected_bearing=name=='counter_central_divider';passed=all(not q['public_face_material_breach'] and (expected_bearing or q.get('minimum_clearance_to_actual_inner_shell_plane_m',1)>=-EPS)for q in states)
 rows.append({'part':name,'owner':p['owner'],'method':'Convex hull of all actual source mesh vertices; LP clips its complete volume against each actual inner-shell triangle XZ domain, not rectangular bounds','allowed_bearing':'Central divider intentionally bears within43mm shell thickness; no external public projection'if expected_bearing else None,'states':states,'whole_translation_interval':'All moving parts translate only +Y, so signed shell clearances increase monotonically over [0,.28]; exact closed minimum proves complete interval including first millimetre','passed':passed})
r={'asset':'AST-CUL-002','source_sha256':S['source_sha256'],'manifest_sha256':hashlib.sha256((B/'AST-CUL-002.manifest.json').read_bytes()).hexdigest(),'generator_sha256':R['generator_sha256'],'scope':'Every actual interior shelf, divider, fixed bearing, drawer wall/back/floor/runner and grip compared with true bowed inner/public shell planes over complete closed/access translation. Exterior trim exceptions are explicit.','actual_shell_triangle_patches':len(patches),'external_or_perimeter_exceptions':[{'part':n,'reason':why}for n,why in exception.items()],'interior_parts':rows,'absent_redundant_backing':'open_cubby_rear_of_public_shell'not in P,'all_passed':all(r['passed']for r in rows)};(B/'qa/curved_shell_interface_screen.json').write_text(json.dumps(r,indent=2,default=lambda x:x.item()));print('WHOLE_INTERFACE',r['all_passed'],'parts',len(rows),'patches',len(patches));print([(x['part'],x['passed'])for x in rows if not x['passed']])
