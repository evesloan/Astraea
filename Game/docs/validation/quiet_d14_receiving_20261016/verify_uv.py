from pathlib import Path
import json,numpy as np
D=Path('/workspace/Astraea/BlenderCatalogue/assets/quiet_d14_staff_receiving_20261016');rows=json.loads((D/'PATCH_TRIANGLES.json').read_text());report=[]
for row in rows:
 old=np.array([[q['p']for q in t]for t in row['before']]);uv=np.array([[q['uv']for q in t]for t in row['before']]);a=old[:,0];u=old[:,1]-a;v=old[:,2]-a;uu=(u*u).sum(1);vv=(v*v).sum(1);uvdot=(u*v).sum(1);den=uu*vv-uvdot*uvdot;normal=np.cross(u,v);length=np.linalg.norm(normal,axis=1);valid=(abs(den)>1e-14)&(length>1e-9);count=0;maxerr=0
 for t in row['after']:
  for q in t:
   w=np.array(q['p'])-a;wu=(w*u).sum(1);wv=(w*v).sum(1);b=np.divide(wu*vv-wv*uvdot,den,out=np.zeros_like(den),where=valid);c=np.divide(wv*uu-wu*uvdot,den,out=np.zeros_like(den),where=valid);dist=np.divide(abs((w*normal).sum(1)),length,out=np.full_like(length,1e9),where=valid);inside=valid&(dist<.0001)&(b>=-.0001)&(c>=-.0001)&(b+c<=1.0001);expected=uv[:,0]+b[:,None]*(uv[:,1]-uv[:,0])+c[:,None]*(uv[:,2]-uv[:,0]);err=np.linalg.norm(expected-np.array(q['uv']),axis=1);matches=list(err[inside])
   for ia,ib in [(0,1),(1,2),(2,0)]:
    edge=old[:,ib]-old[:,ia];ll=(edge*edge).sum(1);t=np.clip(np.divide(((np.array(q['p'])-old[:,ia])*edge).sum(1),ll,out=np.zeros_like(ll),where=ll>1e-14),0,1);closest=old[:,ia]+t[:,None]*edge;near=np.linalg.norm(closest-np.array(q['p']),axis=1)<.0001;edge_uv=uv[:,ia]+t[:,None]*(uv[:,ib]-uv[:,ia]);matches.extend(np.linalg.norm(edge_uv-np.array(q['uv']),axis=1)[near])
   assert matches and min(matches)<.0001,(row['name'],q,min(matches)if matches else None);maxerr=max(maxerr,float(min(matches)));count+=1
 report.append({'name':row['name'],'verified_vertices':count,'max_uv_error':maxerr})
(D/'UV_VERIFICATION.json').write_text(json.dumps({'status':'PASS','position_tolerance_m':.0001,'uv_tolerance':.0001,'rows':report},indent=2)+'\n');print(report)
