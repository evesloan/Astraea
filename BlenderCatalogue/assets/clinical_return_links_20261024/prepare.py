"""Source-defined clinical through-route detours; original bearings remain intact."""
from pathlib import Path
import json,hashlib,sys,math
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[3];G=R/'Game';P=G/'clinical_return_links_20261024';E=P/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(R/'BlenderCatalogue/assets/group4_completion_20261011'));from glb_geometry import triangles
native='RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/clinical_full_transfer_batch020/source'
source=R/native/'CLINICAL_COMPLETE_ARCHITECTURE.json';legacy=json.loads(source.read_text());clinic=G/'data/architecture/group3_clinical_full_20261011/CLINICAL.json';contract=json.loads(clinic.read_text());pins={str(p.relative_to(R)):sha(p)for p in [source,clinic,G/'assets/models/AST-RES-006.glb',G/'assets/models/AST-AQU-016.glb',G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json',G/'data/architecture/LOWER_HULL_BODY.json',G/'data/hull_envelope.json']}
oldfloor=[]
for rel in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 p=G/rel;pins[str(p.relative_to(R))]=sha(p)
 for row in json.loads(p.read_text())['regions']:
  if abs(row['floor_y']-21)<.00001:oldfloor.extend(Polygon(t)for t in row['triangles'])
for file,digest in contract['model_pins'].items():
 p=G/'assets/models/group3_clinical_full_20261011'/file;assert sha(p)==digest;pins[str(p.relative_to(R))]=digest
 for name,faces,e in triangles(p):
  for face in faces:
   if abs(face[:,1]-21).max()<.00002:
    q=Polygon(face[:,[0,2]])
    if q.area>1e-8:oldfloor.append(q)
floors=unary_union(oldfloor)
parts=[];routes=[];cutboxes=[]
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return[g]
 return[p for p in g.geoms if p.geom_type=='Polygon']
def extrude(g,lo,hi,name,role,zone):
 from shapely.geometry.polygon import orient
 vs=[];fs=[]
 for poly in polys(g):
  if poly.area<1e-8:continue
  poly=orient(poly,sign=1)
  for t in constrained_delaunay_triangles(poly).geoms:
   cs=list(t.exterior.coords)[:3]
   if not t.exterior.is_ccw:cs.reverse()
   k=len(vs);vs += [[x,lo,z]for x,z in cs]+[[x,hi,z]for x,z in cs];fs += [[k,k+1,k+2],[k+5,k+4,k+3]]
  for ring in [poly.exterior,*poly.interiors]:
   for (x,z),(xx,zz)in zip(list(ring.coords),list(ring.coords)[1:]):
    k=len(vs);vs += [[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,zz]];fs.append([k+3,k+2,k+1,k])
 if vs:parts.append(dict(name=name,role=role,zone=zone,verts=vs,faces=fs))
def shape(row):return Polygon(row['boundary'],row['holes'])
def existing_at(lo,hi):return unary_union([shape(q)for q in legacy['parts']if q['y'][0]<hi-1e-6 and q['y'][1]>lo+1e-6])
configs=[('Royalty_return',[[108,22],[110.6,22],[110.6,58],[108,58]],5),('Pool_return',[[-61,-411],[-63.4,-411],[-63.4,-394],[-61,-394]],3),('Pool_clean',[[-57,-408.5],[-57,-395.5]],2)]
for zone,path,count in configs:
 line=LineString(path);foot=line.buffer(1.85,cap_style=3,join_style=2);outer=foot.buffer(.14,join_style=2);missing=outer.difference(floors)
 assert missing.intersection(floors).area<1e-7
 extrude(missing,20.76,21,zone+'_MissingOnlyFloor','staff_floor',zone)
 ceiling=outer.difference(existing_at(25.2,25.38));extrude(ceiling,25.2,25.38,zone+'_Ceiling','staff_white_paint',zone)
 # Open ends connect to the original longitudinal street, not to a new room.
 first,last=path[0],path[-1];openings=box(first[0]-1.851,foot.bounds[1]-.3,first[0]+1.851,foot.bounds[1]+.3).union(box(last[0]-1.851,foot.bounds[3]-.3,last[0]+1.851,foot.bounds[3]+.3))
 wall=outer.difference(foot).difference(openings)
 for suffix,lo,hi,role in [('Dado',21,22.02,'staff_bluegrey_paint'),('Enamel',22.02,25.2,'staff_white_paint')]:
  # Preserve outside originals and avoid coplanar replacement walls.
  existing=existing_at(lo,hi).difference(foot)
  for i,poly in enumerate(polys(wall.difference(existing))):extrude(poly,lo,hi,f'{zone}_{suffix}_{i}',role,zone)
 lamps=[]
 for i in range(count):
  q=line.interpolate(line.length*(i+.5)/count);x,z=q.x,q.y
  extrude(box(x-.45,z-.18,x+.45,z+.18),25.04,25.2,f'{zone}_Fixture{i}_Housing','staff_zinc',zone)
  extrude(box(x-.38,z-.12,x+.38,z+.12),25.035,25.055,f'{zone}_Fixture{i}_Lens','staff_opal',zone)
  lamps.append(dict(name=f'{zone}_TaskLight{i}',position=[x,25.02,z],energy=.8,range=8,color=[.8,.9,1]))
 # The union of square-ended segment rectangles exactly defines this orthogonal
 # corridor footprint for source-wall triangle subtraction.
 boxes=[]
 for (x,z),(xx,zz)in zip(path,path[1:]):boxes.append([min(x,xx)-1.85,min(z,zz)-1.85,max(x,xx)+1.85,max(z,zz)+1.85])
 assert unary_union([box(*q)for q in boxes]).symmetric_difference(foot).area<1e-7
 cutboxes+=boxes;routes.append(dict(id=zone,path=path,clear_width=3.7,required_width=3.6,footprint=[list(q.exterior.coords)for q in polys(foot)],new_floor_m2=missing.area,lights=lamps,required_body_height=3.2,ceiling_underside_y=25.2))
clear=unary_union([box(*q)for q in cutboxes]);walls=[]
# Close only newly exposed ends of the original thin partitions. The existing
# outside skin is clipped at runtime; these faces do not reauthor whole walls.
for index,row in enumerate(legacy['parts']):
 if row['category']!='screen_wall':continue
 poly=shape(row);remaining=poly.difference(clear)
 if remaining.is_empty or not poly.intersects(clear):continue
 edges=remaining.boundary.intersection(clear.boundary)
 lines=[edges]if edges.geom_type=='LineString'else list(edges.geoms)
 for j,line in enumerate(lines):
  if line.geom_type!='LineString' or line.length<1e-7:continue
  cs=list(line.coords)
  for k,((x,z),(xx,zz))in enumerate(zip(cs,cs[1:])):
   lo,hi=row['y'];verts=[[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,z]];dx,dz=xx-x,zz-z;length=math.hypot(dx,dz)
   from shapely.geometry import Point
   normal_inside=clear.covers(Point((x+xx)/2-dz/length*.0001,(z+zz)/2+dx/length*.0001));face=[0,1,2,3]if normal_inside else[3,2,1,0]
   zone=next(r['id']for r in routes if unary_union([Polygon(q)for q in r['footprint']]).distance(line)<1e-6)
   parts.append(dict(name=f'RetainedWallReveal_{index}_{j}_{k}',role=row['role'],zone=zone,verts=verts,faces=[face]))
for name,faces,e in triangles(G/'assets/models/group3_clinical_full_20261011/AST-MED-G3-007.glb'):
 if not name.startswith('screen_wall_'):continue
 lo=faces.min((0,1));hi=faces.max((0,1))
 if hi[1]<21 or lo[1]>25.21:continue
 hit=any(Polygon(face[:,[0,2]]).intersects(clear)for face in faces)
 if hit:walls.append(dict(name=name,source_triangles=len(faces),world_bounds=[lo.tolist(),hi.tolist()]))
assert len(walls)==10,(len(walls),[q['name']for q in walls])
# Real source supports, not the old conservative hold rectangles.
supports=[]
for name,faces,e in triangles(G/'assets/models/AST-RES-006.glb'):
 if 'RoyaltyPier' in name:
  lo=faces.min((0,1));hi=faces.max((0,1));assert box(lo[0],lo[2],hi[0],hi[2]).disjoint(clear);supports.append(dict(owner='D17ConnectedHouse_WIP/D17ConnectedArchitecture/AST-RES-006',name=name,bounds=[lo.tolist(),hi.tolist()]))
pool=box(-61.3,-406.08,-59.9,-403.92);assert pool.disjoint(clear.buffer(.14,join_style=2))
for f in ['AST-MED-G3-007.blend','AST-MED-G3-008.blend']:p=R/native/f;pins[str(p.relative_to(R))]=sha(p)
prior_plan=G/'clinical_room_receiving_20261024/PLAN.json';pins[str(prior_plan.relative_to(R))]=sha(prior_plan);prior=json.loads(prior_plan.read_text());gate_names=[n for n,f,e in triangles(G/'assets/models/group3_clinical_full_20261011/AST-MED-G3-010.glb')];bindings=[]
for i in [3,5,6,7,8]:
 key=f'D05_directory_{i:02d}';port=next(q for q in prior['ports']if q['id']==key+'_soiled');prefix=key+'_crossing_2__';names=[n for n in gate_names if n.startswith(prefix)];assert len(names)==21
 canonical=next(q for q in contract['door_bindings']if q['name']==key+'_crossing_2')['position']
 bindings.append(dict(room=key,receiver=port['id']+'_ClosedSourceCassette',position=port['gate_position'],canonical_mesh_names=names,source_offset_m=round(math.dist(port['gate_position'],canonical),6),canonical_position=canonical))
plan=dict(parent='651c51dbea82ff69c29da6315403478f29b60aeb',status='UNFINISHED_THROUGH_ROUTE_SUCCESSOR',source_pins=pins,native_library=native,retained_gate_bindings=bindings,parts=parts,routes=routes,wall_preimages=walls,cut_boxes_xz=cutboxes,protected_supports=supports,pool_bearing=dict(owner='GrandPoolOrchardSection_WIP/GrandPoolConnectedArchitecture/AST-AQU-016',name='GPM_CELL_-4_-21_2_ASTRAEA_warm_stone_concave_static_surface'),new_floor_m2=sum(q['new_floor_m2']for q in routes),new_rooms=0,new_capacity=0,operating_gate_ids_added=0,clinical_operation=False,holds=['D06 transfer crossing around western Royalty pier remains unaccepted','D01 Pool transfer-gate/cassette redesign remains held','Authoritative clinical dispatch, inside egress, sealed loads, stock and sterility remain held','Primary structure, final visual and whole-gameplay/performance acceptance remain open'])
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('Prepared',len(parts),'parts',len(walls),'wall resources',plan['new_floor_m2'],'new floor m2')
