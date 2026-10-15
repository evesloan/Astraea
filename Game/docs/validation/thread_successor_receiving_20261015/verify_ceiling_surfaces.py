# Compare source surfaces and UV fields; glTF may triangulate the same clipped polygon differently.
from pathlib import Path
import json,struct,hashlib,numpy as np
D=Path(__file__).resolve().parent
# Reuse only byte decoding/face readers; no transfer or authoring code executes.
s=(D/'verify_ceiling_geometry.py').read_text();exec(s[:s.index('old=D/')])
old=D/'retained_source/BlenderCatalogue/assets/group5_completion_20261011/exports/thread_stock/thread_stock_repair_r004.glb';new=D/'import/Game/assets/models/group5/thread_stock/thread_stock_repair_r005.glb';a,ab=load(old);n,nb=load(new);name='Group5VisualFinish_ThreadCeiling';source=faces(a,ab,name);actual=faces(n,nb,name);holes=[(31.63,32.37,-11.29,-10.71),(31.63,32.37,6.71,7.29)];lo=np.min([v['p']for t in source for v in t],axis=0);hi=np.max([v['p']for t in source for v in t],axis=0);eps=.0001
area=lambda t:float(np.linalg.norm(np.cross(t[1]['p']-t[0]['p'],t[2]['p']-t[0]['p']))/2)
def planes(t):return[(axis,bound)for axis in range(3)for bound in[lo[axis],hi[axis]]if all(abs(v['p'][axis]-bound)<eps for v in t)]
src={};dst={};maxuv=0.;maxplane=0.;retained=0;reveals=0
for tri in source:
 ps=planes(tri);assert len(ps)==1;src.setdefault(ps[0],[]).append(tri)
for tri in actual:
 ps=planes(tri)
 if not ps:
  # Only four side faces per declared aperture are permitted as new cut edges.
  assert any(all(abs(v['p'][axis]-bound)<eps for v in tri)for hole in holes for axis,bound in[(0,hole[0]),(0,hole[1]),(2,hole[2]),(2,hole[3])]);reveals+=1;continue
 assert len(ps)==1 or area(tri)<1e-8
 if area(tri)<1e-8:continue
 plane=ps[0];axis,bound=plane;axes=[i for i in range(3)if i!=axis];dst.setdefault(plane,[]).append(tri);retained+=1
 for v in tri:
  assert np.all(v['p']>=lo-eps)and np.all(v['p']<=hi+eps);maxplane=max(maxplane,abs(v['p'][axis]-bound));match=False
  for original in src[plane]:
   p0,p1,p2=[w['p'][axes]for w in original];mat=np.column_stack((p1-p0,p2-p0));uv=np.linalg.solve(mat,v['p'][axes]-p0);w=np.array([1-uv.sum(),uv[0],uv[1]])
   if np.all(w>=-2*float(np.linalg.norm(np.linalg.inv(mat),axis=1).max())*eps):
    expected=sum(wi*sv['uv']for wi,sv in zip(w,original));err=float(np.linalg.norm(expected-v['uv']));assert err<eps,(v,err);maxuv=max(maxuv,err);match=True;break
  assert match,'Candidate ceiling vertex has no retained source surface/UV correspondence'
 if axis==1:
  for x0,x1,z0,z1 in holes:
   poly=tri
   for ax,b,l in[(0,x0+eps,False),(0,x1-eps,True),(2,z0+eps,False),(2,z1-eps,True)]:poly=clip(poly,ax,b,l)
   overlap=sum(area([poly[0],poly[i],poly[i+1]])for i in range(1,len(poly)-1))if len(poly)>=3 else 0.
   assert overlap<1e-10,'New ceiling extends inside retained fixture housing clearance beyond fixed100um tolerance'
areas=[]
for plane,triangles in src.items():
 expected=sum(area(t)for t in triangles)
 if plane[0]==1:expected-=sum((h[1]-h[0])*(h[3]-h[2])for h in holes)
 observed=sum(area(t)for t in dst.get(plane,[]));error=abs(observed-expected);assert error<.0005,(plane,error);areas.append({'axis':plane[0],'coordinate':float(plane[1]),'expected_area_m2':expected,'actual_area_m2':observed,'error_m2':error})
report={'status':'PASS_RETAINED_CEILING_SURFACES_UV_AND_TWO_EXACT_HOUSING_APERTURES','comparison':'Surface coverage and barycentric UV fields; triangle topology may differ under exporter tessellation','coordinate_and_uv_tolerance':eps,'area_roundtrip_tolerance_m2':.0005,'retained_triangles':retained,'painted_cut_edge_triangles':reveals,'maximum_plane_error_m':maxplane,'maximum_uv_error':maxuv,'surfaces':areas,'source_r004_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'r005_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'earlier_triangle_topology_comparison_failed_and_retained':True};(D/'CEILING_SURFACE_GEOMETRY_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],maxplane,maxuv)
