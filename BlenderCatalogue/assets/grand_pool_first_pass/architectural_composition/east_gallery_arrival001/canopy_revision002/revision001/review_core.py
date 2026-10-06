"""Planned actual-solid/contact/reservation/route/view review. No engine/build/export."""
import sys,ast,json,math,hashlib,collections,importlib.util,argparse
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely import constrained_delaunay_triangles,union_all
S=Path(__file__).resolve().parent;P=Path("/workspace/scratch/375c2e438292/pool-opposite-gallery-proposal001");C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');TOL=5e-5
helper=C/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py';sp=importlib.util.spec_from_file_location('geo',helper);geo=importlib.util.module_from_spec(sp);sp.loader.exec_module(geo)
for name in dir(geo):
    if not name.startswith('_'):globals()[name]=getattr(geo,name)
helper=C/'assets/grand_pool_first_pass/finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(helper.read_text());wanted={'record','triang_face','rayhits','surface_points','on_surface','strict_inside','contact_pair','topology'};exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in wanted],type_ignores=[]),str(helper),'exec'))
# Concave swept caps need a polygon-wide normal. The audited helper's first
# corner normal can reverse a concave cap even when its edge loop is correct.
# Preserve its constrained triangulation but resolve orientation with Newell.
def triang_face(v,face):
    q=np.array([v[i]for i in face]);local=q-q[0];normal=np.sum(np.cross(local,np.roll(local,-1,axis=0)),axis=0);assert np.linalg.norm(normal)>1e-12
    if len(face)==3:return [tuple(tuple(x)for x in q)]
    axis=int(np.argmax(np.abs(normal)));proj=np.delete(q,axis,1);poly=Polygon(proj);assert poly.is_valid,(face,q.tolist());out=[]
    for t in constrained_delaunay_triangles(poly).geoms:
        vv=[]
        for a in list(t.exterior.coords)[:3]:
            ix=np.argmin(np.linalg.norm(proj-a,axis=1));assert np.linalg.norm(proj[ix]-a)<1e-7;vv.append(tuple(q[ix]))
        if np.dot(np.cross(np.array(vv[1])-vv[0],np.array(vv[2])-vv[0]),normal)<0:vv.reverse()
        out.append(tuple(vv))
    return out
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
parser=argparse.ArgumentParser();parser.add_argument('--plan',type=Path,default=S/'CORE_PLAN.json');parser.add_argument('--output',type=Path,default=S/'CORE_REVIEW.json');args=parser.parse_args()
output=args.output.resolve();allowed_output_roots=[S.resolve(),(P/'combined_source001/qa').resolve(),(P/'combined_source002/qa').resolve()]
assert any(output.is_relative_to(root)for root in allowed_output_roots),'Output must remain in core scratch or combined scratch QA'
if not output.is_relative_to(S.resolve()):assert not output.exists(),'Preserve prior combined QA evidence'
plan=read(args.plan);pins=plan['input_sha256']
for p,h in pins.items():assert sha(p)==h,p
def part_triangles(p):
    if 'evaluated_triangles'in p:
        assert p['evaluated_triangles'],(p['name'],'Empty evaluated triangle array')
        assert all(len(t)==3 and len(set(t))==3 and all(isinstance(i,int)and 0<=i<len(p['vertices_xyz'])for i in t)for t in p['evaluated_triangles']),(p['name'],'Invalid evaluated triangle indices')
        return [tuple(tuple(p['vertices_xyz'][i])for i in t)for t in p['evaluated_triangles']]
    return [t for f in p['faces']for t in triang_face(p['vertices_xyz'],f)]
parts=[record(p['name'],p['vertices_xyz'],part_triangles(p),meta=p)for p in plan['parts']];new={p['name']:p for p in parts} 
# Exact retained shell triangle ownership comes from the independently pinned
# source/installed vertex mapping, not source AABBs acting as host geometry.
glb=read_glb(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');old=[]
for p in read(P/'geometry/RETAINED_PART_BOUNDS.json')['parts']:
    tr=[glb['triangles'][i]for i in p['global_triangle_indices']];old.append(record(p['source_name'],[v for t in tr for v in t],tr,meta=p))
oldmap={p['name']:p for p in old};floors=[]
for f in read(P/'geometry/FLOOR_POLYGONS.json')['floor_regions']:
    tr=[];vv=[]
    for face in f['triangles']:
        v=[(x,y,z)for y in [f['floor_y']-f['thickness'],f['floor_y']]for x,z in face];fs=[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)];vv+=v;tr += [t for ff in fs for t in triang_face(v,ff)]
    floors.append(record('COMPILER_FLOOR_'+f['id'],vv,tr,meta=f))
fm={p['name']:p for p in floors};allmap=oldmap|fm|new
for p in parts+old+floors:p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
issues=[];topos=[topology(p)for p in parts]
for row in topos:
    if row['degenerate_triangles']or row['nonmanifold_edges']or row['inconsistent_winding_edges']:issues.append(dict(kind='topology',row=row))
# Every vertex stays inside the proper approved free-volume reservation.
boxes={p['id']:p['bounds_xyz']for p in read(P/'geometry/ADDITIVE_RESERVATIONS.json')['candidates']};reservation_rows=[]
for p in parts:
    lo,hi=boxes[p['meta']['reservation']];bad=[i for i,v in enumerate(p['vertices'])if any(v[k]<lo[k]-TOL or v[k]>hi[k]+TOL for k in range(3))]
    reservation_rows.append(dict(name=p['name'],reservation=p['meta']['reservation'],outside_vertices=bad,bounds_xyz=p['bounds']))
    if bad:issues.append(dict(kind='outside_reservation',name=p['name'],vertices=bad))
# Existing finishes, props and routes had no overlap with whole reservations.
# Recheck actual core bounds against each retained finish/prop/sign snapshot.
broad=[]
for p in parts:
    for q in read(P/'geometry/RETAINED_FINISH_BOUNDS.json'):
        if overlap(p['bounds'],q['bounds_xyz'],TOL):broad.append([p['name'],q['source_name']])
if broad:issues.append(dict(kind='retained_finish_broad_hits',rows=broad))
retained=[]
for p in parts:
    for q in old+floors:
        if not overlap(p['bounds'],q['bounds'],TOL):continue
        r=contact_pair(p,q)
        if r['penetration']:retained.append(dict(new=p['name'],retained=q['name'],**r))
if retained:issues.append(dict(kind='retained_interpenetration',rows=retained))
contacts=[];graph={}
for p in parts:
    rr=[]
    for name in p['meta']['support']:
        assert name in allmap,name
        r=contact_pair(p,allmap[name]);rr.append(dict(support=name,**r))
    good=[r['support']for r in rr if r['touch']and not r['penetration']];graph[p['name']]=good
    contacts.append(dict(name=p['name'],contact_rows=rr,verified_supports=good))
    if not good:issues.append(dict(kind='missing_true_contact',name=p['name'],rows=rr))
retained_root_paths={}
for row in read(P/'geometry/RETAINED_SUPPORT_PATHS.json')['paths']:
    path=row['path_to_retained_keel']
    for i,name in enumerate(path):retained_root_paths.setdefault(name,path[i:])
def root_path(name,visited=None):
    if name in oldmap or name in fm:return retained_root_paths.get(name)
    visited=set()if visited is None else visited
    if name in visited:return None
    for target in graph.get(name,[]):
        path=root_path(target,visited|{name})
        if path:return [name]+path
    return None
rooted={p['name']:root_path(p['name'])for p in parts}
for name,path in rooted.items():
    if not path:issues.append(dict(kind='unrooted_support',name=name))
newnew=[]
for i,p in enumerate(parts):
    for q in parts[i+1:]:
        if not overlap(p['bounds'],q['bounds'],TOL):continue
        r=contact_pair(p,q)
        if r['penetration']:newnew.append(dict(a=p['name'],b=q['name'],**r))
if newnew:issues.append(dict(kind='new_new_interpenetration',rows=newnew))
# True plan footprint against protected extruded routes, with positive height.
protected=read(P/'geometry/PROTECTED_RESERVATIONS.json');route_rows=[]
for r in protected['routes']:
    poly=union_all([Polygon(v)for v in r['plan_polygon_union_xz']]);hits=[]
    for p in parts:
        lo,hi=p['bounds']
        if min(hi[1],r['y_m'][1])-max(lo[1],r['y_m'][0])<=TOL:continue
        footprint=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if Polygon([(v[0],v[2])for v in t]).area>1e-12])
        if footprint.intersection(poly).area>1e-8:hits.append(p['name'])
    route_rows.append(dict(name=r['id'],hits=hits))
    if hits:issues.append(dict(kind='protected_route',route=r['id'],hits=hits))
for r in plan['approach_paths']:
    region=LineString([(p[0],p[2])for p in r['points_xyz']]).buffer(r['radius_m']);loy=r['points_xyz'][0][1]+.02;hiy=loy+r['height_m'];hits=[]
    for p in parts:
        lo,hi=p['bounds']
        if min(hi[1],hiy)-max(lo[1],loy)<=TOL:continue
        footprint=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if Polygon([(v[0],v[2])for v in t]).area>1e-12])
        if footprint.intersection(region).area>1e-8:hits.append(p['name'])
    route_rows.append(dict(name=r['name'],radius_m=r['radius_m'],height_m=r['height_m'],hits=hits))
    if hits:issues.append(dict(kind='new_approach',route=r['name'],hits=hits))
# The 3.2 m apron is deliberately unoccupied at standing/cart heights.
apron=Polygon([(-14.4,-454),(-11.2,-454),(-11.2,-445),(-14.4,-445)])
for p in parts:
    if p['bounds'][0][1]>=54.5:continue
    footprint=Polygon([(p['bounds'][0][0],p['bounds'][0][2]),(p['bounds'][1][0],p['bounds'][0][2]),(p['bounds'][1][0],p['bounds'][1][2]),(p['bounds'][0][0],p['bounds'][1][2])])
    if footprint.intersection(apron).area>1e-8:issues.append(dict(kind='apron_intrusion',name=p['name']))
views=[]
for v in read(P/'geometry/PRESERVED_VIEWS.json'):
    hits=rayhits(v['eye_xyz'],v['target_xyz'],parts)
    if hits:issues.append(dict(kind='retained_view_occlusion',name=v['name'],hits=hits))
for v in plan['seated_views']:
    ray=rayhits(v['eye_xyz'],v['market_target_xyz'],parts);d=sub(v['media_target_xyz'],v['eye_xyz']);elev=math.degrees(math.atan2(d[1],math.hypot(d[0],d[2])));yaw=math.degrees(math.atan2(abs(d[2]),-d[0]));mhits=rayhits(v['eye_xyz'],v['media_target_xyz'],[p for p in parts if p['name']!='EAST_Display_AngledReceiver'])
    row=dict(name=v['name'],market_new_core_hits=ray,media_elevation_degrees=elev,media_head_turn_degrees=yaw,media_core_hits=mhits,water_surface_floor_blocked=True,full_scene_visibility_not_yet_claimed=True);views.append(row)
    if ray or mhits:issues.append(dict(kind='new_seated_view',row=row))
# Standing eyes are tied to actual floor; knee/foot boxes use exact triangle
# contact after broad phase, and cleaning reach ends on the named real surface.
use_rows=[]
for r in plan.get('use_envelopes',[]):
    lo,hi=r['bounds_xyz'];x,y,z=lo;X,Y,Z=hi;v=[[x,y,z],[X,y,z],[X,y,Z],[x,y,Z],[x,Y,z],[X,Y,z],[X,Y,Z],[x,Y,Z]];fs=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];q=record(r['name'],v,[t for f in fs for t in triang_face(v,f)]);q['ta']=np.array(q['triangles']);q['tmin']=q['ta'].min(axis=1);q['tmax']=q['ta'].max(axis=1);hits=[]
    for p in parts:
        if overlap(q['bounds'],p['bounds'],TOL)and contact_pair(q,p)['penetration']:hits.append(p['name'])
    use_rows.append(dict(name=r['name'],hits=hits))
    if hits:issues.append(dict(kind='knee_foot_volume',name=r['name'],hits=hits))
clean_rows=[]
for r in plan.get('cleaning_reaches',[]):
    hits=rayhits(r['eye_xyz'],r['target_xyz'],parts);distance=length(sub(r['target_xyz'],r['eye_xyz']));target_on_surface=on_surface(r['target_xyz'],new[r['target_part']]);clean_rows.append(dict(name=r['name'],distance_m=distance,maximum_segment_m=r['maximum_segment_m'],hits=hits,target_on_surface=target_on_surface,scope='Static operator stance and short reach only; no cart/controller operation claim'))
    if hits or distance>r['maximum_segment_m'] or not target_on_surface:issues.append(dict(kind='cleaning_reach',row=clean_rows[-1]))
for r in plan.get('standing_views',[]):
    if 'floor_owner'not in r:continue
    floor=fm['COMPILER_FLOOR_'+r['floor_owner']];q=[r['eye_xyz'][0],floor['meta']['floor_y'],r['eye_xyz'][2]]
    if not on_surface(q,floor):issues.append(dict(kind='standing_eye_floor',name=r['name']))
# Preserve every original source light's first 60 mm and its saved receiver ray.
section=read(C/'assets/grand_pool_orchard_section/source/connected_contract.json');lightrows=[]
for f in section['fixtures']:
    pos=f['position_xyz'];d=f.get('direction_xyz',f.get('direction'));hits=rayhits(pos,add(pos,mul(d,.06)),parts)
    if 'receiver_xyz'in f:hits+=rayhits(pos,f['receiver_xyz'],parts)
    if hits:issues.append(dict(kind='retained_fixture_ray',name=f['name'],hits=hits))
for f in plan['fixture_reservations']:
    hits=rayhits(f['position_xyz'],add(f['position_xyz'],mul(f['direction_xyz'],.06)),parts);lightrows.append(dict(name=f['name'],exit_60mm_hits=hits))
    if hits:issues.append(dict(kind='new_fixture_exit',name=f['name'],hits=hits))
# Floor contact area is actual bottom polygons against the exact compiler union.
f=fm['COMPILER_FLOOR_D09_orchard_market_gallery']['meta'];surface=union_all([Polygon(t)for t in f['triangles']]);floorrows=[]
for p in parts:
    if 'COMPILER_FLOOR_D09_orchard_market_gallery'not in p['meta']['support']:continue
    base=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if max(abs(v[1]-52.5)for v in t)<TOL]);area=base.area;covered=base.intersection(surface).area
    floorrows.append(dict(name=p['name'],bearing_area_m2=area,covered_m2=covered,uncovered_m2=area-covered))
    if area<1e-5 or area-covered>1e-7:issues.append(dict(kind='floor_coverage',name=p['name'],area=area,covered=covered))
for p,h in pins.items():assert sha(p)==h,p
report=dict(status='PASS_CORE_PURE_GEOMETRY'if not issues else'CORE_REQUIRES_CORRECTION',scope='Actual planned core solids only. Not saved source, retained programme integration, load certification or engine validation.',plan_sha256=sha(args.plan),semantic_objects=len(parts),geometry_basis={p['name']:('evaluated_triangle_indices'if 'evaluated_triangles'in p['meta']else'planned_face_triangulation')for p in parts},triangles=sum(len(p['triangles'])for p in parts),issues=issues,topology=topos,reservation_checks=reservation_rows,support_contacts=contacts,rooted_support_paths=rooted,floor_bearing=floorrows,routes=route_rows,seated_views=views,use_envelopes=use_rows,cleaning_reaches=clean_rows,fixture_exits=lightrows,new_new_intersections=newnew,retained_intersections=retained,input_sha256=pins,excluded_from_this_gate=['exact retained botanical meshes','retained housed display geometry and all image-corner rays','two retained RES-001 signs and route arrows','actual source reopen and material UV checks','native lighting selection and performance'])
args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','semantic_objects','triangles','issues','seated_views']},indent=2));sys.exit(bool(issues))
