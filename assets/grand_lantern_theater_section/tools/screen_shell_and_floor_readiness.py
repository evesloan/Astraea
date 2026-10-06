#!/usr/bin/env python3
"""Pure package-only evidence. No Blender/Godot and no live floor adoption.
The miter band is an explicit conservative *proposal* for the unbuilt shell.
Its clearance is not a claim that pressure enclosure or structural loads exist.
"""
import argparse, hashlib, itertools, json, math
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import shapely

P=argparse.ArgumentParser();P.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1]);args=P.parse_args();R=args.package
G=Path('/workspace/shared/astraea-godot-production-20261003')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(rel,d):(R/rel).write_text(json.dumps(d,indent=2)+'\n')
def polygons(shape):
 out=[]
 for p in shapely.get_parts(shape):
  if p.geom_type=='Polygon' and p.area>1e-10:out.append({'boundary':[list(v)for v in list(p.exterior.coords)[:-1]],'holes':[[list(v)for v in list(q.coords)[:-1]]for q in p.interiors]})
 return out
geometry=read(R/'source/geometry.json');objects=[o for o in geometry['objects']if o['role']!='preview_only'];source_hash=sha(R/'source/geometry.json')
contract_path=G/'data/architecture/packages/upper_hull/UPPER_SHELL_PRODUCTION_CONTRACT.json';h=read(contract_path)['theater_longitudinal_return_contract']
outer=np.array([[[x,ring['y'],z]for x,z in ring['west_station_xz']]for ring in h['ring_vertices_world']]).reshape(-1,3)
triangles=[]
for iy in range(3):
 for iz in range(3):
  a,b,c,d=iy*4+iz,(iy+1)*4+iz,(iy+1)*4+iz+1,iy*4+iz+1
  triangles.extend([(a,b,c),(a,c,d)])
normals=[]
for ids in triangles:
 a,b,c=outer[list(ids)];n=np.cross(b-a,c-a);n/=np.linalg.norm(n)
 if n[0]<0:n=-n
 normals.append(n)
normals=np.array(normals)
# Minimum-norm simultaneous shifted-halfspace intersection at every seam vertex.
# An X-only offset is NOT used. Active-set enumeration covers the convex QP in3D.
inner=[];miter_witnesses=[]
for vi,v in enumerate(outer):
 incidence=[j for j,tri in enumerate(triangles)if vi in tri];N=np.unique(np.round(normals[incidence],12),axis=0);solutions=[]
 for k in range(1,min(len(N),3)+1):
  for idx in itertools.combinations(range(len(N)),k):
   A=N[list(idx)]
   if np.linalg.matrix_rank(A,tol=1e-10)<k:continue
   d=A.T@np.linalg.solve(A@A.T,np.full(k,.8))
   if np.all(N@d>=.8-1e-8):solutions.append(d)
 assert solutions,('miter missing',vi)
 d=min(solutions,key=np.linalg.norm);inner.append(v+d);miter_witnesses.append({'vertex':vi,'outer':v.tolist(),'inner':(v+d).tolist(),'normal_reserve_per_incident_facet_m':(N@d).tolist(),'displacement':d.tolist()})
inner=np.array(inner)
# Each convex hull contains its entire triangulated outer-to-inner band, including
# nonplanar seam caps. Thus a separating plane for a tested convex object proves
# no contact conservatively; no sampling and no source-centre-only acceptance.
volumes=[]
for i,ids in enumerate(triangles):
 ids=list(ids);points=np.concatenate([outer[ids],inner[ids]]);hull=ConvexHull(points)
 cross=np.cross(inner[ids[1]]-inner[ids[0]],inner[ids[2]]-inner[ids[0]])
 assert np.dot(cross,np.cross(outer[ids[1]]-outer[ids[0]],outer[ids[2]]-outer[ids[0]]))>0
 assert min((inner[ids]-outer[ids[0]])@normals[i])>=.8-1e-8
 volumes.append((points,hull))
clouds=[(o['name'],np.array(o['vertices_world']))for o in objects]
for p in read(R/'contracts/place_instances.json')['places']:
 x,y,z=p['position'];a=p['orientation_yaw_radians'];c,s=math.cos(a),math.sin(a)
 verts=[[x+u*c+w*s,y+dy,z-u*s+w*c]for dy in [0,1.1]for u,w in [(-.344,-.325),(.344,-.325),(.344,.460),(-.344,.460)]]
 clouds.append((p['id']+'__closed_chair',np.array(verts)))
for route in read(R/'contracts/route_reservations.json')['routes']:
 lo,hi=route['floor_y_range'];clouds.append((route['id']+'__3m_route_volume',np.array([[x,y,z]for y in [lo,hi+3]for x,z in route['boundary']])))
fail=[];candidates=[]
for label,q in clouds:
 for vi,(v,hull)in enumerate(volumes):
  if not np.all(q.max(0)>=v.min(0)-1e-9)or not np.all(v.max(0)>=q.min(0)-1e-9):continue
  candidates.append({'object':label,'reservation_facet':vi})
  separated=[{'plane':j,'margin_m':float(np.min(q@eq[:3]+eq[3]))}for j,eq in enumerate(hull.equations)if np.min(q@eq[:3]+eq[3])>1e-8]
  if not separated:fail.append({'object':label,'reservation_facet':vi,'status':'Unresolved conservative convex-band contact; requires exact source repair or narrower proof'})
  else:candidates[-1]['separating_plane']=max(separated,key=lambda x:x['margin_m'])
write('contracts/END_RETURN_MITER_RESERVATION.json',{'status':'Explicit unbuilt normal-reservation candidate, not pressure-shell geometry; upper-hull owner must preserve this band or rerun','source_contract_sha256':sha(contract_path),'outer_vertices_world':outer.tolist(),'inner_vertices_world':inner.tolist(),'triangles':triangles,'normal_reserve_m':.8,'method':'Adjacent-facet shifted halfspaces; minimum-norm feasible miter vertex; conservative convex band per outer triangle. Full vertices, edges and faces covered by separating plane/AABB exclusions.','miter_witnesses':miter_witnesses,'not_claimed':['Structural certification','Pressure enclosure','Unlisted future hull joints or mountings']})
write('qa/end_return_miter_screen.json',{'geometry_sha256':source_hash,'objects_checked':len(objects),'closed_chairs_checked':2200,'route_volumes_checked':len(clouds)-len(objects)-2200,'normal_band_facets':18,'conservative_contacts':fail,'AABB_candidates_resolved_by_plane':candidates,'source_min_z':min(float(v[:,2].min())for _,v in clouds[:len(objects)]),'source_max_z':max(float(v[:,2].max())for _,v in clouds[:len(objects)]),'fore_end_band_max_z':max(float(volumes[j][0][:,2].max())for j in [0,1,6,7,12,13]),'aft_end_band_min_z':min(float(volumes[j][0][:,2].min())for j in [4,5,10,11,16,17]),'shell_owner_adoption_required':True,'engine_run':False})

part=read(R/'contracts/D11_COMPILER_PARTITION.json');base=unary_union([box(*part['base_rectangle'])]+[box(*r)for r in part['compiler_union_threshold_extensions']]);holes=unary_union([box(*r)for r in part['full_holes']]);source=unary_union([Polygon(p['boundary_xz'])for p in part['source_owned_lower_parts']]);flat=base.difference(unary_union([holes,source]));assert flat.is_valid
floortris=shapely.constrained_delaunay_triangles(flat);assert abs(sum(t.area for t in floortris.geoms)-flat.area)<1e-6
assert all(flat.covers(t)for t in floortris.geoms)
write('contracts/D11_FLAT_FLOOR_CANDIDATE.json',{'status':'Compiler input candidate only; not added to spatial_layout or current runtime','source_partition_sha256':sha(R/'contracts/D11_COMPILER_PARTITION.json'),'source_geometry_sha256':source_hash,'floor_y':69.5,'thickness':.24,'structural_area_m2':flat.area,'polygons':polygons(flat),'triangles':[[list(v)for v in list(t.exterior.coords)[:3]]for t in floortris.geoms],'source_owned_lower_projection_m2':source.area,'full_holes_m2':holes.area,'source_lower_floor_overlap_m2':flat.intersection(source).area,'full_hole_overlap_m2':flat.intersection(holes).area,'existing_compiler_unchanged':True})
# Ground full-bearing audit catches architectural bases outside the flat rectangle.
# Propose separately owned foundations below Y69.5; no source triangles changed,
# no walkable floor extension, and no positive-area entry into moving cabin.
base_failures=[];proposal_parts=[];base_witnesses=[]
for o in objects:
 vs=np.array(o['vertices_world']);lo=float(vs[:,1].min())
 if abs(lo-69.5)>1e-8:continue
 footprint=Polygon(vs[np.abs(vs[:,1]-lo)<1e-8][:,[0,2]]).convex_hull if int(np.sum(np.abs(vs[:,1]-lo)<1e-8))>=3 else None
 if footprint is None or footprint.area<1e-9:continue
 missing=footprint.difference(flat)
 if missing.area<=1e-7:continue
 base_failures.append({'object':o['name'],'missing_bearing_area_m2':missing.area,'base_area_m2':footprint.area,'min_y':lo})
 x0,z0,x1,z1=footprint.bounds
 if o['name']=='west_acoustic_vertical_boundary':candidate=box(x0,z0,-117,z1)
 elif (o['name'].startswith('east_acoustic_wall_')or o['name'].startswith('D11_door_pocket_')):candidate=box(-35,z0,x1,z1)
 else:candidate=footprint
 proposal_parts.append((o['name'],candidate))
foundation=unary_union([p for _,p in proposal_parts]).difference(flat)
cabin=box(-44,-123.5,-39,-118.5);assert foundation.intersection(cabin).area<1e-8
for row in base_failures:
 o=next(o for o in objects if o['name']==row['object']);v=np.array(o['vertices_world']);p=Polygon(v[np.abs(v[:,1]-69.5)<1e-8][:,[0,2]]).convex_hull
 base_witnesses.append({**row,'candidate_support_area_m2':p.intersection(foundation).area,'uncovered_after_proposal_m2':p.difference(unary_union([flat,foundation])).area})
assert not any(w['uncovered_after_proposal_m2']>1e-7 for w in base_witnesses)
write('contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json',{'status':'PARENT SOURCE REVIEW REQUIRED; non-walkable structural foundation proposal, no adoption','source_geometry_sha256':source_hash,'source_partition_sha256':sha(R/'contracts/D11_COMPILER_PARTITION.json'),'datum_top_y':69.5,'datum_bottom_y':69.26,'additional_non_walkable_foundation_area_m2':foundation.area,'source_owned_stage_foundation_area_m2':dict(proposal_parts)['stage_36x14'].area,'perimeter_shaft_bearing_area_m2':foundation.area-dict(proposal_parts)['stage_36x14'].area,'compiler_walking_floor_area_unchanged_m2':flat.area,'polygons':polygons(foundation),'named_basis':[{'object':n,'polygon':polygons(p)}for n,p in proposal_parts],'base_contact_witnesses':base_witnesses,'moving_cabin_positive_area_overlap_m2':foundation.intersection(cabin).area,'walkable_flat_overlap_m2':foundation.intersection(flat).area,'policy':'Separately owned structural substrate, below actual static bases and bridge to adjacent flat slab; not a walking-floor broadening or exemption. Static shaft feet only: whole 5x5 moving cabin remains absent. No existing retained compiler slab may be overwritten.','limits':['Ground-bearing footprint proof only, not span/load certification','Other floors/stairs/ceiling/hangers need their source attachment and runtime checks','Parent must reconcile retained slabs/void permissions before live adoption']})
places=[]
for s in read(R/'contracts/place_instances.json')['places']:
 if s['tier']!='stalls'or s['kind']!='rear_transfer_replaceable_place':continue
 x,y,z=s['position'];a=s['orientation_yaw_radians'];c,t=math.cos(a),math.sin(a);p=Polygon([[x+u*c+w*t,z-u*t+w*c]for u,w in [(-.344,-.325),(.344,-.325),(.344,.460),(-.344,.460)]])
 places.append({'id':s['id'],'floor_y':y,'unsupported_area_m2':p.difference(flat).area})
thresholds=[{'rectangle':r,'unsupported_area_m2':box(*r).difference(flat).area}for r in part['compiler_union_threshold_extensions']]
assert all(p['unsupported_area_m2']<1e-7 for p in places+thresholds)
write('qa/compiler_floor_source_screen.json',{'status':'SOURCE CANDIDATE PASS; live compiler implementation remains required','source_geometry_sha256':source_hash,'flat_floor_area_m2':flat.area,'flat_triangles':len(floortris.geoms),'triangle_area_conservation':True,'source_owned_projection_overlap_m2':flat.intersection(source).area,'shaft_stair_hole_overlap_m2':flat.intersection(holes).area,'lower_rear_place_witnesses':places,'threshold_witnesses':thresholds,'new_foundation_parent_review_required':True,'foundation_bearing_witnesses':base_witnesses,'exact_upper_surface_ids':[s['region_id']for s in read(R/'contracts/surface_manifest.json')['surfaces']],'shared_compiler_edited':False,'engine_run':False})
assert not fail,fail
print(json.dumps({'shell_source_contacts':len(fail),'shell_candidates_resolved':len(candidates),'flat_floor_area_m2':flat.area,'triangles':len(floortris.geoms),'conditional_rear_places_now_supported_in_candidate':len(places),'foundation_proposal_area_m2':foundation.area,'foundation_ground_bases':len(base_witnesses),'foundation_stage_m2':504,'remaining_requires_parent_source_approval':True},indent=2))
