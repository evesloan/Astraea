"""Exported-triangle mounting, end profile, and service-support probes."""
from pathlib import Path
import sys,json,numpy as np,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa/batch02'))
from geometry_checks import triangles,contains_xy
api=json.loads((ROOT/'assets/staff_overhead/mounting_api.json').read_text());rows=[]
for ident in ['AST-STF-004','AST-STF-005','AST-STF-006']:
 path=ROOT/'assets/staff_overhead/exports'/f'{ident}.glb';geo=triangles(path);alltri=np.concatenate([r['triangles'] for r in geo]);cross=np.cross(alltri[:,1]-alltri[:,0],alltri[:,2]-alltri[:,0]);probes=[]
 lo=alltri.reshape(-1,3).min(0);hi=alltri.reshape(-1,3).max(0)
 for anchor in api['assets'][ident]['ceiling_anchors']:
  atzero=(np.abs(alltri[:,:,2])<1e-7).all(1)&(cross[:,2]>1e-14);ok=bool(contains_xy([anchor['position_m']],alltri[atzero])[0]);probes.append({'kind':'ceiling_anchor_on_actual_top_face','name':anchor['name'],'passes':ok,'z_m':0})
 if ident!='AST-STF-006':
  kind='straight' if ident.endswith('004') else 'turn';radius=.6;total=1.2 if kind=='straight' else radius*np.pi/2
  def station(s):
   if kind=='straight':return np.array([s,0]),np.array([1,0])
   a=s/radius;return np.array([radius*np.sin(a),radius*(1-np.cos(a))]),np.array([np.cos(a),np.sin(a)])
  for s in ([.24,.96] if kind=='straight' else [total*.25,total*.75]):
   xy,tan=station(s);nor=np.array([-tan[1],tan[0]])
   up=(np.abs(alltri[:,:,2]+.398)<1e-7).all(1)&(cross[:,2]>1e-14);down=(np.abs(alltri[:,:,2]+.398)<1e-7).all(1)&(cross[:,2]<-1e-14)
   for d in [-.279,.279]:
    p=xy+nor*d;u=bool(contains_xy([p],alltri[up])[0]);v=bool(contains_xy([p],alltri[down])[0]);probes.append({'kind':'crossbeam_top_meets_rail_bottom','station_m':s,'offset_m':d,'z_m':-.398,'upward_contact':u,'downward_contact':v,'passes':u and v})
  rungstations=[.09,.34,.6,.86,1.11] if kind=='straight' else [total*t for t in [.06,.27,.5,.73,.94]]
  for s in rungstations:
   xy,tan=station(s)
   for name,role,z,d in [('cable_A','staff_cable_blue',-.388,-.08),('cable_B','staff_rubber',-.388,-.119),('cable_C','staff_cable_red',-.388,-.165),('large_conduit','staff_zinc',-.381,.16),('small_conduit','staff_zinc',-.381,.032)]:
    rt=np.concatenate([r['triangles'] for r in geo if r['role'].endswith(role)]);edges=np.concatenate([rt[:,[0,1]],rt[:,[1,2]],rt[:,[2,0]]]);edges=edges[(np.abs(edges[:,:,2]-z)<1e-7).all(1)]
    a=(edges[:,0,:2]-xy)@tan;b=(edges[:,1,:2]-xy)@tan;mask=(a*b<=1e-12)&(np.abs(a-b)>1e-8);e=edges[mask];u=a[mask]/(a[mask]-b[mask]);points=e[:,0,:2]+u[:,None]*(e[:,1,:2]-e[:,0,:2]);nor=np.array([-tan[1],tan[0]])
    points=points[np.abs((points-xy)@nor-d)<.003]
    support=(np.abs(alltri[:,:,2]-z)<1e-7).all(1)&(cross[:,2]>1e-14)
    covered=contains_xy(points,alltri[support]);probes.append({'kind':'service_base_over_actual_support','service':name,'station_m':s,'z_m':z,'bottom_edge_intersection_points':len(points),'unsupported_points':int((~covered).sum()),'passes':len(points)>0 and bool(covered.all())})
 result={'asset':ident,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actual_lowest_z_m':float(lo[2]),'actual_highest_z_m':float(hi[2]),'declared_lowest_matches':bool(abs(lo[2]-api['assets'][ident]['lowest_geometry_z_m'])<1e-7),'at_3_3m_mount_lowest_world_z_m':float(3.3+lo[2]),'minimum_mount_for_2_65_clearance_m':float(2.65-lo[2]),'probes':probes,'passes':all(p['passes'] for p in probes)}
 rows.append(result)
out={'results':rows,'scope':'Static visual contacts and ceiling datum from exported triangles; excludes engineering load, electrical, real ship route and runtime acceptance.'};(ROOT/'qa/batch03/independent_overhead_support.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{'asset':r['asset'],'passes':r['passes'],'failed':[p for p in r['probes'] if not p['passes']]} for r in rows],indent=2))
