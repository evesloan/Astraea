"""Read-only GLB transforms/triangles and numerical source contract; no engine/import."""
import json,struct,hashlib,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent
DT={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}
def glb(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);b=raw[28+n:];out=[]
 def acc(k):
  a=d['accessors'][k];v=d['bufferViews'][a['bufferView']];w={'SCALAR':1,'VEC3':3}[a['type']];dt=np.dtype(DT[a['componentType']]);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',w*dt.itemsize)
  return np.ndarray((a['count'],w),dt,b,off,(stride,dt.itemsize)).copy()
 def visit(i,parent):
  nd=d['nodes'][i]
  if 'matrix' in nd:m=np.array(nd['matrix']).reshape(4,4).T
  else:
   x,y,z,w=nd.get('rotation',[0,0,0,1]);q=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
   m=np.eye(4);m[:3,:3]=q@np.diag(nd.get('scale',[1,1,1]));m[:3,3]=nd.get('translation',[0,0,0])
  m=parent@m
  if 'mesh' in nd:
   for p in d['meshes'][nd['mesh']]['primitives']:
    if p.get('mode',4)!=4:continue
    a=acc(p['attributes']['POSITION']);a=(np.column_stack([a,np.ones(len(a))])@m.T)[:,:3];idx=acc(p['indices']).flatten() if 'indices' in p else np.arange(len(a));out.append((nd.get('name',str(i)),a,idx.reshape(-1,3)))
  for c in nd.get('children',[]):visit(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return out
# Conservative triangle-AABB exclusion: no candidate overlap => rigorous no contact.
boxlo=np.array([-118.5,74.5,-250]);boxhi=np.array([-117.7,87.5,-160])
files=['AST-HUL-001','AST-ATR-001','AST-CMD-001','AST-CMD-002','AST-CMD-003','AST-CMD-004','AST-CMD-005','AST-CMD-006','AST-RES-006','AST-AQU-016','AST-STF-009_pool_market']
reports=[]
for name in files:
 p=R/'assets/models'/f'{name}.glb';meshes=glb(p);v=np.concatenate([a for n,a,i in meshes]);candidates=[]
 for n,a,i in meshes:
  t=a[i];hit=np.all(t.max(1)>=boxlo,axis=1)&np.all(t.min(1)<=boxhi,axis=1)
  if hit.any():candidates.append({'node':n,'triangles':int(hit.sum())})
 reports.append({'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'vertices':len(v),'bounds_world':{'min':v.min(0).tolist(),'max':v.max(0).tolist()},'production_panel_triangle_aabb_candidates':candidates})
# Commons is local source, correctly transformed by current installation contract.
p=R/'assets/models/AST-COM-003.glb';v=np.concatenate([a for n,a,i in glb(p)])+np.array([63,84,0]);reports.append({'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bounds_world':{'min':v.min(0).tolist(),'max':v.max(0).tolist()},'translation':[63,84,0],'production_panel_aabb_overlap':bool(np.all(v.max(0)>=boxlo)&np.all(v.min(0)<=boxhi))})
slabs=[]
for r in json.loads((R/'data/generated/structural_meshes.json').read_text())['regions']:
 if r['floor_y']<boxlo[1] or r['floor_y']-r['thickness']>boxhi[1]:continue
 for i,t in enumerate(r['triangles']):
  a=np.array(t)
  if np.all(a.max(0)>=boxlo[[0,2]]) and np.all(a.min(0)<=boxhi[[0,2]]):slabs.append({'id':r['id'],'triangle':i})
# Finite end ramps: each station ring is piecewise linear. Solid is a band inward normal.
knotsY=[61,69.5,87.5,92];W=[120,118.5,118.5,109.6]
contract={'status':'Numeric source-authoring candidate; parent acceptance and catalogue identity still required; not runtime geometry','bounded_production_package':{'name':'Theater west vertical shell pilot','outer_quad_world':[[-118.5,74.5,-250],[-118.5,87.5,-250],[-118.5,87.5,-160],[-118.5,74.5,-160]],'normal_inward':[1,0,0],'shell_skin_thickness_normal_m':.18,'frame_depth_normal_m':.22,'panel_service_access_reservation_normal_m':.4,'total_inward_reservation_normal_m':.8,'inner_exclusion_x':-117.7,'framing':'Embedded ribs only inside0.22 frame band. No posts/slabs/fixtures outside0.8 reservation. Frame spacing proposed5m inZ; end seams detachable, no claim of load certification.','service':'0.4m is component withdrawal/inspection clearance reached from interior removable panels; NOT a walkable maintenance corridor. Existing3.4m theater cart return remains inward atX[-117,-113.6].','apertures':'No invented window/door cuts in pilot; full theater west wall is acoustic boundary. No new floor/cap or seated audience geometry. Pilot is an explicitly incomplete open-edged source fragment.','ownership':'New upper hull source package only; do not modify AST-HUL-001 or theater/home/core sources; parent reserves catalogue identity before registration.','contact_screen':'No triangle-AABB candidates among listed world-mapped architecture sources; no compiled slab candidates. Unlisted dynamic/procedural fixtures require pre-adoption runtime census.'},'theater_longitudinal_return_contract':{'central_plateau_z':[-265,-115],'fore_return_z':[-275,-265],'aft_return_z':[-115,-105],'outer_west_halfbeam_y_knots':list(zip(knotsY,W)),'return_rule':'For eachY knot, interpolate west-halfbeam linearly inZ between general tapered halfbeam at−275 and shoulder at−265; maintain shoulder through−115; interpolate to general taper at−105. Split quads into triangles with shared diagonals. No symmetry-generated east shoulder.','normal_rule':'For each oriented triangle outer plane n·p=c with inward unit normal n, skin inner plane n·p=c+0.18; frame/service inner boundary n·p=c+0.80. At joined facets use intersection of shifted inward halfspaces (miter), not X-only offset. Reject triangle orientation/self-intersection; no thickness beyond maximum240m outer beam.','upper_return':'West shoulder tapers inward87.5–92. Actual occupied footprints must be screened against all shifted facet planes, including end returns. An X-only1m audit cannot accept sloping normal reserve.'},'installed_geometry_screen':reports,'compiled_slab_candidates':slabs,'method_limits':['Direct GLB triangle positions include every scene-node TRS/matrix','Pilot conservative triangle AABB test proves exclusion when candidate list empty, not acceptance where overlap exists','Listed architecture placed atworldZERO verified in current build scripts; local commons offset from current runtime contract','Core envelopes separately constrained nearcentreline; moving cabins/dynamic doors and procedural instanced props are not decoded here','No source privately proposed upper pavilion mesh exists in this audit: explicit polygon envelopes used instead','Full sloped shell must pass normal-plane occupied/body screening before authoring beyond pilot']}
(O/'UPPER_SHELL_PRODUCTION_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
print([(r['file'],r['bounds_world'],r.get('production_panel_triangle_aabb_candidates')) for r in reports]);print('slab candidates',slabs)
# Exact inward-normal halfspace test of theater occupied prisms in plateau Z district.
T=json.loads((R/'data/architecture/packages/theater/THEATER_SECTION_PROPOSAL.json').read_text());C=json.loads((R/'data/architecture/packages/theater/CHAIR_FOOTPRINT_SCREENING.json').read_text());lo=C['chair_bounds_local_gltf_m']['min_m'];hi=C['chair_bounds_local_gltf_m']['max_m']
normalreserve=.8;slope=(118.5-109.6)/(92-87.5)
def normal_clearance(x,y,z):
 # Positive distances inward to flat wall and sloped wall, miter intersection.
 return min(x+118.5,(x+118.5-slope*(y-87.5))/math.sqrt(1+slope*slope))-.8
chairs=[]
for s in T['seat_proposals']:
 x,y,z=s['position'];a=s['orientation_yaw_radians'];w=[]
 for u,v in [(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]:
  xx=x+u*math.cos(a)+v*math.sin(a);zz=z-u*math.sin(a)+v*math.cos(a);w.append(normal_clearance(xx,y+hi[1],zz))
 chairs.append({'id':s['id'],'minimum_normal_clearance_after_0_8m_band':min(w),'fits':min(w)>=-1e-8})
ty={'stalls':69.5,'first_gallery':78,'crown_gallery':84};aisles=[]
for a in C['aisle_reservations']:
 y=ty[a['tier']]+3;w=[normal_clearance(x,y,z) for x,z in a['boundary']];aisles.append({'id':a['id'],'top_y':y,'minimum_normal_clearance_after_0_8m_band':min(w),'fits':min(w)>=-1e-8})
normal={'status':'Normal-direction miter test; stage/chairs/routes in plateau are separate from return cells. No anatomy/support/door test.','thickness_normal':{'skin':.18,'frame':.22,'service_withdrawal':.4,'total':.8},'top_slope':slope,'sloped_total_equivalent_transverse_m':normalreserve*math.sqrt(1+slope*slope),'chair_failures':[s for s in chairs if not s['fits']],'aisle_failures':[s for s in aisles if not s['fits']],'minimum_chair_remaining_normal_clearance_m':min(s['minimum_normal_clearance_after_0_8m_band'] for s in chairs),'minimum_aisle_remaining_normal_clearance_m':min(s['minimum_normal_clearance_after_0_8m_band'] for s in aisles),'aisles':aisles,'longitudinal_return_safety':'Actual aisle/chair tests are plateau-only; cart-return nearest end distance12m. Foyer allocation reachesZ−116 only1m from the aft plateau end and backstage reachesZ−263 only2m from the fore end. Future authored foyer/backstage contents and exact return triangles need a separate normal-miter contact check; the pilot excludes end returns.'}
(O/'THEATER_NORMAL_RESERVATION_SCREEN.json').write_text(json.dumps(normal,indent=2)+'\n');print('normal',normal['chair_failures'],normal['aisle_failures'],normal['minimum_aisle_remaining_normal_clearance_m'])
# Authoring-only house envelope: source extents protected, roofs owned by current sources.
U=json.loads((R/'data/architecture/UPPER_SECTION_COORDINATION.json').read_text())
house={'status':'Sidewall-bound targets, not adopted enclosures or permitted room relocations','installed_starboard_central_royalty790':{'protected_mesh':'AST-RES-006.glb','actual_x_max':118.08000183105469,'actual_y_max':106.30000305175781,'wall_outer_x':119.5,'inward_normal_total_m':.8,'inner_x':118.7,'minimum_transverse_remaining_clearance':118.7-118.08000183105469,'longitudinal_hold':'Exact outer side wall Z[28.2,51.88] protects installed boundaryZ[29,51.08] with0.8m normal band. Faceted nose follows original790 floor polygon; do not enclose public approach atX78.5–94 as private space. Endreturns may not cut receiving/entry paths.','roof':'Retain source roof ownership, top106.3; no added0.8m-band roof at106.5. Roof pressure-surface/interface requires bounded derivative review, not duplicate canopy.'},'pavilion_boundaries':[],'crown':'Existing AST-CMD-001…006 sources own roof/enclosures. Max decodedroof114.45; keep114.5global. Do not place a new skin over existing roof. Central X±52 structural roof shoulders and exact source windows are protected. Crown roof sharing requires actual source-owner interfaces.'}
for p in U['private_upper_pavilions']:
 poly=p['boundary'];area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2
 edges=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  dx=b[0]-a[0];dz=b[1]-a[1];ll=math.hypot(dx,dz);out=np.array([dz,-dx])/ll*(1 if area>0 else -1);c=float(out@np.array(a))
  edges.append({'outward_unit_normal_xz':out.tolist(),'occupied_limit_dot':c,'proposed_outer_plane_dot':c+1.5,'inner_band_limit_dot':c+.7})
 house['pavilion_boundaries'].append({'identity':p['unit_proposal_key'],'protected_occupied_polygon':poly,'wall_planes':edges,'outer_normal_offset_m':1.5,'skin_frame_service_total_inward_normal_m':.8,'roof_limit':p['external_roof_limit_y'],'roof_occupied_clear_ceiling_candidate':p['external_roof_limit_y']-.8,'note':'Intersect outer shifted halfspaces with calibrated maximum outline. If any protected corner fails with true offset, hold; never crop occupied polygon. No authored pavilion mesh identified here; roof/headroom/private lift remain reserved, not fitted.'})
(O/'HOUSE_CROWN_BOUNDARY_CONTRACT.json').write_text(json.dumps(house,indent=2)+'\n')
H=json.loads((R/'data/hull_envelope.json').read_text())['plan_xz_m'];stations=sorted({(z,abs(x)) for x,z in H if x>=0})
def hullhalf(z):
 for (za,wa),(zb,wb) in zip(stations,stations[1:]):
  if za<=z<=zb:return wa+(wb-wa)*(z-za)/(zb-za)
 return -1e6
for p in house['pavilion_boundaries']:
 es=p['wall_planes'];verts=[]
 for prev,cur in zip(es[-1:]+es[:-1],es):
  v=np.linalg.solve(np.array([prev['outward_unit_normal_xz'],cur['outward_unit_normal_xz']]),[prev['proposed_outer_plane_dot'],cur['proposed_outer_plane_dot']]);verts.append(v.tolist())
 witnesses=[]
 for a,b in zip(verts,verts[1:]+verts[:1]):
  ts=[0,1]+[(z-a[1])/(b[1]-a[1]) for z,w in stations if abs(b[1]-a[1])>1e-8 and 0<(z-a[1])/(b[1]-a[1])<1]
  for t in ts:
   x=a[0]+t*(b[0]-a[0]);z=a[1]+t*(b[1]-a[1]);witnesses.append({'x':x,'z':z,'remaining_max_outline_m':hullhalf(z)-abs(x)})
 p['outer_miter_polygon']=verts;p['minimum_remaining_calibrated_max_outline_m']=min(w['remaining_max_outline_m'] for w in witnesses);p['outer_plan_fits']=p['minimum_remaining_calibrated_max_outline_m']>=-1e-8
 p['wall_ownership_limit']='Outer plane polygon is an enclosure-bound target, not a mandate to place new walls on every edge. Court/entry sides retain existing source ownership and apertures; only exterior-facing sides/returns may be authored after source reconciliation.'
(O/'HOUSE_CROWN_BOUNDARY_CONTRACT.json').write_text(json.dumps(house,indent=2)+'\n');print('pavilion offsets',[(p['identity'],p['minimum_remaining_calibrated_max_outline_m']) for p in house['pavilion_boundaries']])
cores=[]
for name in ['PRIMARY_ATRIUM_CORE','FORWARD_PUBLIC_CORE','FORE_MIDSHIP_PUBLIC_CORE','AFT_MIDSHIP_PUBLIC_CORE','AFT_PUBLIC_CORE','AFT_CROWN_LINK']:
 cfgp=R/f'data/architecture/{name}.json';d=json.loads(cfgp.read_text());pp=R/'assets/models'/d.get('enclosure_file','AST-CIR-005.glb');vs=np.concatenate([a for n,a,i in glb(pp)])+np.array(d['origin']);bb={'min':vs.min(0).tolist(),'max':vs.max(0).tolist()};cores.append({'id':d['id'],'source':str(pp.relative_to(R)),'origin':d['origin'],'actual_enclosure_bounds_world':bb,'production_panel_aabb_overlap':bool(np.all(vs.max(0)>=boxlo)&np.all(vs.min(0)<=boxhi)),'source_sha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'cfg_sha256':hashlib.sha256(cfgp.read_bytes()).hexdigest()})
contract['installed_core_enclosure_screen']=cores
contract['theater_longitudinal_return_contract']['ring_vertices_world']=[{'y':y,'west_station_xz':[[-120*({61:1,69.5:.985,87.5:.9283333333333333,92:.9133333333333333}[y]),-275],[-w,-265],[-w,-115],[-120*({61:1,69.5:.985,87.5:.9283333333333333,92:.9133333333333333}[y]),-105]]} for y,w in zip(knotsY,W)]
(O/'UPPER_SHELL_PRODUCTION_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n');print('core overlaps',[c['id'] for c in cores if c['production_panel_aabb_overlap']])
