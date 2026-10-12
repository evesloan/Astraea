"""Evidence-derived reversible plan contours, not adopted walls or roof caps."""
import json,sys,hashlib
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
from check_retained_exports import read,acc,nodes
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_77a745';L=P/'dependencies/canonical_9d6f85'
outline=Polygon(json.loads((D/'Game/data/hull_envelope.json').read_text())['plan_xz_m']);floors=[]
for f in [D/'Game/data/generated/structural_meshes.json',D/'Game/data/architecture/REMAINING_BATCH_FLOORS.json',L/'Game/data/generated/received_structural_meshes.json']:
 floors.extend(json.loads(f.read_text())['regions'])
sources=[]
for r in json.loads((P/'qa/upper_source_placements_unconfirmed.json').read_text()):
 if r['key'] in ['AST-RES-001','AST-RES-002','AST-RES-003','AST-RES-004']:continue
 path=L/r['path'];h=hashlib.sha256(path.read_bytes()).hexdigest()
 if r['expected_sha256']:assert h==r['expected_sha256']
 d,b=read(path);pts=[];yaw=r['yaw'];rot=np.array([[np.cos(yaw),0,np.sin(yaw)],[0,1,0],[-np.sin(yaw),0,np.cos(yaw)]]);origin=np.array(r['origin'])
 for n,m in nodes(d):
  for q in d['meshes'][n['mesh']]['primitives']:
   a=acc(d,b,q['attributes']['POSITION']);pts.extend(((np.c_[a,np.ones(len(a))]@m.T)[:,:3]@rot.T)+origin)
 a=np.array(pts);sources.append({'id':r['key'],'path':r['path'],'sha256':h,'vertices':a,'bounds':[a.min(axis=0).tolist(),a.max(axis=0).tolist()],'placement':'Recorded runtime registry translation for WP sections; Vector3.ZERO crown/connected-house scripts for CMD/RES006. RES005 world-platform datum corroborated by source bounds, proposal evidence only.'})
datums=[61,69.5,78,84,88.5,93,97.5,102,106.5];rings=[]
for y0,y1 in zip(datums,datums[1:]):
 rows=[r for r in floors if r['floor_y']==y0];polys=[Polygon(t) for r in rows for t in r['triangles']];owners=[r['id'] for r in rows];witnesses=[]
 for s in sources:
  a=s['vertices'];q=a[(a[:,1]>=y0-1e-4)&(a[:,1]<=y1+1e-4)]
  if len(q)>2:polys.append(MultiPoint(q[:,[0,2]]).convex_hull);witnesses.append(s['id'])
 protected=unary_union(polys).convex_hull;candidate=protected.buffer(1.5,join_style='mitre');normal=1.5
 if candidate.difference(outline).area>1e-6:candidate=protected.buffer(.8,join_style='mitre');normal=.8
 spill=candidate.difference(outline).area
 rings.append({'id':'G7_UpperSeam_Y'+str(y0).replace('.','_'),'datum_y':y0,'next_datum_y':y1,'source_floor_owners':owners,'source_mesh_witnesses':witnesses,'protected_plan_convex_hull_xz':list(protected.exterior.coords)[:-1],'proposal_outer_contour_xz':list(candidate.exterior.coords)[:-1],'normal_offset_outside_protected_plan_m':normal,'skin_frame_withdrawal_reservation_m':.8,'maximum_outline_outside_area_m2':spill,'status':'Reversible plan-bound evidence proposal; reject/hold any spill without cropping protected sources','proposal_bounds_xz':list(candidate.bounds),'architectural_limit':'Convex plan witnesses do not select roof transitions, source wall aperture ownership, occupied clear ceilings or private/pavilion seams. No cap, slab, post or general-body tapered wall is built from this guide.'})
contract=json.loads((D/'Game/data/architecture/packages/upper_hull/HOUSE_CROWN_BOUNDARY_CONTRACT.json').read_text())
out={'baseline':'9d6f8518f9ddbe5892711ca4eb4849a46fbd32be','status':'Reversible source-backed upper perimeter/terminal proposals, not adopted general hull geometry','rings':rings,'retained_source_bounds':[{k:v for k,v in s.items() if k!='vertices'} for s in sources],'private_pavilion_boundary_targets':contract['pavilion_boundaries'],'retained_connected_house_side_target':contract['installed_starboard_central_royalty790'],'upper_height_budget':{'general_boundary_max_y':106.5,'retained_crown_max_y':114.44999694824219,'global_max_y':114.5,'keel_min_y':-3.5,'duplicate_roof_skin_permitted':False},'theater_join':{'retained_owner':'AST-HUL-002','y_stations':[61,69.5,87.5,92],'z_stations':[-275,-265,-115,-105],'status':'Retained complete west shoulder; adjacent upper contours must yield to its actual face planes, not overlay it'},'terminal_source_obligation':'Contours expose exact longitudinal occupied witnesses for step/cutback review. An inter-level loft may cut the protected source vertices even where each individual ring fits. Therefore do not loft these contours into a production wall/roof without fitting intermediate source geometry. Future root/Group2 house/pavilion sources must be added before closing their seams.','root_adoption_decisions':['Pressure-surface ownership of room walls/windows and retained roof faces','Exact source-side receiver/collar and panel withdrawal access','Final Group2 private pavilion/window/lift interfaces','Intermediate-height perimeter and terminal soffit/roof shape around occupied witnesses','All source regions not in this bounded10-model upper census; actual legacy procedural placements are not accepted by this proposal']}
(P/'docs/UPPER_PERIMETER_AND_TERMINAL_PROPOSALS.json').write_text(json.dumps(out,indent=2)+'\n');print('UPPER_REVERSIBLE_PROPOSALS',len(rings),'rings',len(sources),'models',[(r['datum_y'],r['maximum_outline_outside_area_m2']) for r in rings])
