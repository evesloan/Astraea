from pathlib import Path
import json,math,hashlib,numpy as np
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');S=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002';W=Path(__file__).resolve().parent;D=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());M=json.loads((S/'SUCCESSOR_INTERFACE.json').read_text());P=np.array(M['guideway']['route_points_xz']);dl=np.linalg.norm(np.diff(P,axis=0),axis=1);ss=np.r_[0,np.cumsum(dl)]
def at(k):
 i=min(len(dl)-1,max(0,int(np.searchsorted(ss,k,side='right')-1)));v=(P[i+1]-P[i])/dl[i];q=P[i]+(k-ss[i])*v;return q,v
# Exact triangle/axis-aligned rectangle clipping, positive planar area, independent of point-boundary labels.
def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly))))/2 if len(poly)>2 else 0
def clip(poly,axis,value,gt):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  aa=(a[axis]>=value-1e-10) if gt else (a[axis]<=value+1e-10);bb=(b[axis]>=value-1e-10) if gt else (b[axis]<=value+1e-10)
  if aa:out.append(a)
  if aa!=bb:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
 return out
def owners(q):
 a,c=q[0]-.12,q[1]-.18;b,d=q[0]+.12,q[1]+.18;out=[]
 for r in D['regions']:
  if r['floor_y']!=61:continue
  ar=0
  for t in r['triangles']:
   if max(p[0] for p in t)<a or min(p[0] for p in t)>b or max(p[1] for p in t)<c or min(p[1] for p in t)>d:continue
   poly=[list(p) for p in t]
   for axis,val,gt in [(0,a,True),(0,b,False),(1,c,True),(1,d,False)]:poly=clip(poly,axis,val,gt) if poly else []
   ar+=area(poly)
  if ar>1e-9:out.append({'owner':r['id'],'overlap_m2':ar,'slab_underside_y':61-r['thickness']})
 return out
# Receiver identity choices are bounded adjustments within the existing core floor, no floor/crossbeam change.
ends=[]
for z,key in [(-412,'D10_forward_public_core_floor'),(-252,'D10_fore_midship_public_core_floor'),(292,'D10_aft_midship_public_core_floor'),(452,'D10_aft_public_core_floor')]:
 q=np.array([-3.9,z-1.0]);o=owners(q);assert len(o)==1 and o[0]['owner']==key and abs(o[0]['overlap_m2']-.0864)<1e-6,(q,o)
 ends.append({'old_ambiguous_point':[-3.9,60.76,z],'new_receiver_center':[-3.9,60.76,z-1],'positive_footprint_xz':[-4.02,z-1.18,-3.78,z-.82],'contacts':o,'resolution':'1m inside existing core, complete positive-area0.0864m² pad on named core slab; no point-boundary inference'})
# Hangers for both ties and central bypass. Corner6m exclusion avoids upright/end-body congestion.
start=float(ss[np.argmin(np.linalg.norm(P-np.array([-5.6,-85.3]),axis=1))]);end=float(ss[np.argmin(np.linalg.norm(P-np.array([-5.6,92]),axis=1))]);sites=[];held=[]
corners=np.array([[0,-56],[40,-52],[40,52],[0,56]])
for k0 in np.arange(start+1,end,8):
 q,v=at(k0)
 if np.min(np.linalg.norm(corners-q,axis=1))<6:continue
 found=None
 for dk in [0,.5,-.5,1,-1]:
  k=k0+dk;q,v=at(k);n=np.array([v[1],-v[0]]);legs=[q+n*h for h in [-1.70,1.70]];oo=[owners(l) for l in legs]
  if all(len(o)==1 and abs(o[0]['overlap_m2']-.0864)<1e-6 and abs(o[0]['slab_underside_y']-60.76)<1e-6 for o in oo):found={'path_station_m':float(k),'center_xz':q.tolist(),'tangent_xz':v.tolist(),'leg_receivers':[{'center_xz':l.tolist(),'contacts':o} for l,o in zip(legs,oo)]};break
 if found:sites.append(found)
 else:held.append({'nominal_path_station_m':float(k0),'center_xz':q.tolist(),'receiver_contacts':oo,'reason':'no unique full-area receiver within bounded±1m adjustment'})
rep={'schema':'astraea.group4.receiving_module.v1','source_only':True,'frozen_successor_receipt_sha256':hashlib.sha256((S/'FROZEN_SUCCESSOR_BATCH.json').read_bytes()).hexdigest(),'slab_sha256':hashlib.sha256((R/'Game/data/generated/structural_meshes.json').read_bytes()).hexdigest(),'core_end_resolutions':ends,'central_tie_header_sites':sites,'held_sites':held,'profile':{'rod_radius_m':.04,'rod_bottom_y':55.72,'rod_top_y':60.75,'upper_header_bottom_y':60.18,'upper_header_top_y':60.50,'positive_bearing_xyz':[.24,.08,.36],'rail_side_shoe_lower_y':55.60,'rail_side_shoe_upper_y':55.79,'underweb_girders_y':[55.55,55.71]},'limits':['Positive-area source contact only, no structural load/capacity/engineering proof.','Headers remain above reserved running clearance60.1; floor underside60.76.','Corner uprights deliberately omitted within6m of four protected corner vertices, longitudinal underweb transfers bridge those source spans.','Frozen station/rail exports unchanged; new members additive only.']}
W.mkdir(exist_ok=True);(W/'RECEIVING_PLAN.json').write_text(json.dumps(rep,indent=2)+'\n');print('FOUR_ENDS',[e['contacts'][0]['owner'] for e in ends]);print('SITES',len(sites),'HELD',len(held));print('OWNERS',sorted(set(o['contacts'][0]['owner'] for s in sites for o in s['leg_receivers'])))
