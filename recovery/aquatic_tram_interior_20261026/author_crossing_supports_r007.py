"""Continuous guideway successor and source-owned aquatic receiving frames."""
from pathlib import Path
import json,importlib.util,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r007'
spec=importlib.util.spec_from_file_location('author',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
plan=json.loads((D/'PLAN.json').read_text());points=np.array(plan['route_points_xz']);fit=a.PathFit(points)
# Retained running datums and gauge copied from the selected Orchard guideway.
source=json.loads((R/'Game/orchard_tram_interior_20261025/r007/BUILD.json').read_text())
layout=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());floors=[r for r in layout['regions'] if r['floor_y']==61]
def exact_local_owners(xz,regions):
 x,z=xz;owners=[]
 for region in regions:
  area=0.
  for triangle in region['triangles']:
   if max(p[0] for p in triangle)<x-.12 or min(p[0] for p in triangle)>x+.12 or max(p[1] for p in triangle)<z-.18 or min(p[1] for p in triangle)>z+.18:continue
   poly=[list(p) for p in triangle]
   for axis,value,above in [(0,x-.12,True),(0,x+.12,False),(1,z-.18,True),(1,z+.18,False)]:poly=a.screen.clip(poly,axis,value,above) if poly else []
   if len(poly)>2:area+=abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1])))*.5
  if area>1e-9:owners.append({'owner':region['id'],'overlap_m2':round(area,9),'underside_y':region['floor_y']-region['thickness']})
 return owners
a.screen.footprint_owners=exact_local_owners
poses=np.array(json.loads((D/'POSE_KNOTS.json').read_text()));poses=poses[(poses[:,0]>=plan['aquatic_interval_m'][0]-3)&(poses[:,0]<=plan['aquatic_interval_m'][1]+3)]
def clear(p):
 delta=p-poses[:,1:3];c=np.cos(poses[:,3]);s=np.sin(poses[:,3]);side=abs(delta[:,0]*c-delta[:,1]*s);forward=abs(delta[:,0]*s+delta[:,1]*c)
 if np.any((side<2.13)&(forward<2.83)):return False
 # Original aquatic shaft, public core, protected bypass and newly authored
 # platform/stair/relaxation footprints remain unoccupied by guideway legs.
 # Suspended drops bottom at55.72 leave3.22m above the D09 bypass floor;
 # no floor-standing pier is placed in that route. The tall original shaft
 # and occupied upper station remain excluded throughout the drop height.
 if any(abs(p[1]-z)<2.5 and abs(p[0])>3.7 for z in [145,301]):return False
 reserved=[(11.5,16.1,232.5,237.5),(-8,8,252,292),(18.7,21.3,184.7,187.3),(20.5,35.4,182,205.3)]
 return not any(x0<p[0]<x1 and z0<p[1]<z1 for x0,x1,z0,z1 in reserved)
receivers=[];unresolved=[]
for i,at in enumerate(np.arange(plan['aquatic_interval_m'][0]+2,plan['aquatic_interval_m'][1]-2,7.5)):
 q,t=fit.sample(at);normal=np.array([t[1],-t[0]])
 # Outside these tangent limits the route exactly rejoins retained guideway.
 # Its original supports remain; do not add duplicate frames through the core.
 if not 118<=q[1]<=318.34:continue
 if 255<q[1]<289:
  leg=np.array([-7.8,q[1]]);pad=np.array([-7.8,min(291.,max(260.,q[1]))])
  columns=[v for name,v in a.screen.glb_vertices('AST-CIR-005_aft_midship_d04_port_threshold_r001.glb',[0,0,272]) if name=='CORE_OuterWall_08_-1']
  assert len(columns)==1
  vertices=np.unique(columns[0],axis=0);lo=vertices.min(0);hi=vertices.max(0)
  assert len(vertices)==8 and abs(hi[1]-60.76)<.0001 and lo[0]<pad[0]-.06 and hi[0]>pad[0]+.06 and lo[2]<pad[1]-.12 and hi[2]>pad[1]+.12
  owner={'source':'AST-CIR-005_aft_midship_d04_port_threshold_r001.glb','member':'CORE_OuterWall_08_-1','bearing_y':float(hi[1]),'footprint_m':[.12,.24],'source_bounds':[lo.tolist(),hi.tolist()]}
  a.box('AquaticCoreBearing_'+str(i),[pad[0],60.80,pad[1]],[.12,.08,.24])
  a.beam('AquaticCoreDrop_'+str(i),[leg[0],55.72,leg[1]],[leg[0],60.34,leg[1]],.08,.08)
  if np.linalg.norm(pad-leg)>1e-6:a.beam('AquaticCoreOverarm_'+str(i),[leg[0],60.34,leg[1]],[pad[0],60.34,pad[1]],.18,.32)
  a.beam('AquaticCoreStub_'+str(i),[pad[0],60.34,pad[1]],[pad[0],60.8,pad[1]],.08,.08)
  a.beam('AquaticCoreCantilever_'+str(i),[leg[0],55.6,leg[1]],[q[0]+1.48,55.6,q[1]],.38,.19)
  receivers.append({'cursor':float(at),'leg':leg.tolist(),'pad':pad.tolist(),'owner':owner})
  continue
 for side in [-1,1]:
  if side==1 and 196<q[1]<205:
   pad=np.array([21.1,203.9]);shoe=q+normal*1.48
   a.beam('StationSharedRouteShoe',[shoe[0],55.60,shoe[1]],[pad[0],55.60,pad[1]],.38,.19)
   receivers.append({'cursor':float(at),'leg':pad.tolist(),'pad':pad.tolist(),'owner':{'authored_member':'BoardingTailHanger_0','receipt':'RECEIVERS.json','shared_existing_source_bearing':True}})
   continue
  candidates=[]
  for distance in [2.4,2.8,3.2,3.6,4.0]:
   for along in [0,-1,1,-2,2,-3,3]:
    leg=q+normal*side*distance+t*along
    if not clear(leg):continue
    for dx,dz in [(0,0)]+[(x,z) for x in [-8,-4,0,4,8] for z in [-8,-4,0,4,8]]:
     pad=leg+np.array([dx,dz]);owners=a.screen.footprint_owners(pad,floors)
     if len(owners)==1 and abs(owners[0]['overlap_m2']-.0864)<1e-6:candidates.append(((distance-2.4)**2+along**2+dx*dx+dz*dz,leg,pad,owners[0]))
  if not candidates:unresolved.append({'cursor':float(at),'side':side,'reason':'No clear source-owned receiving frame'});continue
  _,leg,pad,owner=min(candidates,key=lambda v:v[0]);name='%02d_%s'%(i,side)
  a.box('AquaticRouteBearing_'+name,[pad[0],60.79,pad[1]],[.24,.08,.36])
  a.beam('AquaticRouteDrop_'+name,[leg[0],55.72,leg[1]],[leg[0],60.5,leg[1]],.08,.08)
  if np.linalg.norm(pad-leg)>1e-6:a.beam('AquaticRouteOverarm_'+name,[leg[0],60.34,leg[1]],[pad[0],60.34,pad[1]],.18,.32)
  a.beam('AquaticRouteStub_'+name,[pad[0],60.34,pad[1]],[pad[0],60.79,pad[1]],.08,.08)
  shoe=q+normal*side*1.48;a.beam('AquaticRouteShoe_'+name,[shoe[0],55.60,shoe[1]],[leg[0],55.60,leg[1]],.38,.19)
  receivers.append({'cursor':float(at),'leg':leg.tolist(),'pad':pad.tolist(),'owner':owner})
# These precise datums are checked against the retained author before use.
retained=(R/'recovery/orchard_tram_interior_20261025/build_native_r006.py').read_text()
for line in retained.splitlines():
 if 'a.ribbon(' in line:print('RETAINED_GUIDEWAY',line.strip())
for name,offset,width,bottom,top in [('Aquatic_ContinuousWeb',0,.22,55.55,55.68),('Aquatic_Rail_-1',-.39,.10,55.68,55.74),('Aquatic_Rail_1',.39,.10,55.68,55.74)]:a.ribbon(name,points,offset,width,bottom,top)
out=D/'ROUTE_SUPPORTS.json';assert not out.exists()
out.write_bytes((json.dumps({'parts':a.parts,'receivers':receivers,'unresolved':unresolved,'selected':False},separators=(',',':'))+'\n').encode())
print(json.dumps({'parts':len(a.parts),'receivers':len(receivers),'unresolved':unresolved}))
