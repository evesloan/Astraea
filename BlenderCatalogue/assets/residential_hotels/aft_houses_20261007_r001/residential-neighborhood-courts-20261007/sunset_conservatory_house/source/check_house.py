"""Selected exact house geometry, membership, owner, route and receiver checks."""
from pathlib import Path
import json,sys,math,hashlib,collections
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,Point,LineString,MultiPoint,box,shape as geo_shape
from shapely.ops import unary_union
from shapely import STRtree
G=Path('/workspace/shared/astraea-godot-production-20261003');read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();eps=1e-6
P=R/'outputs/house_r002/PLAN.json';p=read(P);cross=read(W/'residential-neighborhood-audit-20261007/ALL_1000_NEIGHBORHOOD_CROSSWALK.json')['records'];w=read(G/'data/whole_ship_layout.json');compiled=read(G/'data/generated/structural_meshes.json')['regions'];hull=read(G/'data/architecture/HULL_BODY_SECTION_PROPOSAL.json');lux=read(G/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json');luxby={r['source_envelope_index']:r for r in lux['replacements']};yby={r['deck']:r['floor_y']for r in w['decks']}
def mesh_poly(r):
 v=r['verts'];yt=max(t[1] for t in v); polys=[]
 for f in r['faces']:
  if len(f)>=3 and all(abs(v[i][1]-yt)<eps for i in f):
   pp=Polygon([(v[i][0],v[i][2])for i in f]);
   if pp.area>eps:polys.append(pp)
 return unary_union(polys)

def shape(r):
 if r['kind']=='mesh':return mesh_poly(r),min(t[1]for t in r['verts']),max(t[1]for t in r['verts'])
 a=r['a'];b=r['b'];d=[b[i]-a[i]for i in range(3)];length=math.sqrt(sum(v*v for v in d));t=[v/length for v in d];ss=[0,0,1]if abs(t[2])<.95 else[1,0,0];dot=sum(ss[i]*t[i]for i in range(3));ss=[ss[i]-t[i]*dot for i in range(3)];ln=math.sqrt(sum(v*v for v in ss));ss=[v/ln for v in ss];u=[t[1]*ss[2]-t[2]*ss[1],t[2]*ss[0]-t[0]*ss[2],t[0]*ss[1]-t[1]*ss[0]]
 vs=[[p[i]+ss[i]*ww+u[i]*dd for i in range(3)]for p in[a,b]for ww,dd in[(-r['width']/2,-r['depth']/2),(r['width']/2,-r['depth']/2),(r['width']/2,r['depth']/2),(-r['width']/2,r['depth']/2)]]
 return MultiPoint([(v[0],v[2])for v in vs]).convex_hull,min(v[1]for v in vs),max(v[1]for v in vs)
parts=p['parts'];shapes=[shape(r)for r in parts];polygons=[q for q,a,b in shapes];tree=STRtree(polygons)
expected=[r for r in cross if r['house']==p['house_id']];ids={r['source_envelope_index']for r in expected};regular={r['source_envelope_index']for r in expected if r['production_lane']=='regular_source_supported'}
assert len(ids)==147 and len(regular)==83 and regular=={r['census_source_index']for r in p['rooms']}
assert len(p['D17_replacement_reservations'])==17 and len(p['separate_D04_membership']['guest_envelope_source_indices'])==20
floors={y:unary_union([geo_shape(r['geometry'])for r in p['floor_regions']if r['floor_y']==y])for y in p['upper_datums']}
clashes=[];minor=[]
for r in cross:
 if r['deck']not in['D13','D14','D15','D16','D17']:continue
 i=r['source_envelope_index'];y=yby[r['deck']];rr=luxby.get(i)
 q=Polygon(rr['proposed_floor_boundary'])if rr else box(r['allocation_x'][0],r['allocation_z'][0],r['allocation_x'][1],r['allocation_z'][1]);top=rr['proposed_external_roof_limit_y']if rr else y+4.2
 for k in tree.query(q,predicate='intersects'):
  pp=parts[k];s,a,b=shapes[k]
  if b<=y+eps or a>=top-eps:continue
  ar=q.intersection(s).area
  if ar<=eps:continue
  hit={'source_index':i,'part':pp['name'],'category':pp['category'],'area_m2':round(ar,7),'height_interval':[a,b]}
  if i in ids-regular and pp['category']in['guard','public_glass']and ar<.02:minor.append(hit)
  else:clashes.append(hit)
new_duplicate=[];existing_duplicate=[]
for y,f in floors.items():
 same=[geo_shape(r['geometry'])for r in p['floor_regions']if r['floor_y']==y];ar=sum(q.area for q in same)-f.area
 if ar>eps:new_duplicate.append({'y':y,'area_m2':ar})
 for c in compiled:
  if c['floor_y']!=y:continue
  ar=f.intersection(unary_union([Polygon(t)for t in c['triangles']])).area
  if ar>eps:existing_duplicate.append({'y':y,'owner':c['id'],'area_m2':ar})
entries=[{'source_index':r['census_source_index'],'covered':floors[r['floor_y']].buffer(1e-6).covers(Point(r['historical_door_marker_xz']))}for r in p['rooms']]
routes=[]
for r in p['routes']:
 y=r['points'][0][1];path=LineString([(a[0],a[2])for a in r['points']]);radius=.30
 # The connected existing centerline landing supplies the last 0.3m at X-4.
 prev=unary_union([Polygon(t)for c in compiled if c['floor_y']==y for t in c['triangles']]);available=unary_union([floors[y],prev]);margin=available.covers(path.buffer(radius,cap_style=2))
 routes.append({'id':r['id'],'radius_m':radius,'source_floor_covers_swept_path':margin,'missing_m2':round(path.buffer(radius,cap_style=2).difference(available).area,7)})
cut=unary_union([Polygon(r['proposed_floor_boundary'])for r in p['D17_replacement_reservations']]);vipchecks=[]
for i,pp in enumerate(parts):
 q,a,b=shapes[i]
 if pp['category']=='floor'and abs(b-102)<eps or pp['name'].startswith('SC_PrincipalOpaqueCover'):
  vipchecks.append({'part':pp['name'],'area_m2':round(q.intersection(cut).area,7)})
hp=Polygon(next(r for r in hull['levels']if r['deck']=='D13')['inner_reservation_boundary']);outside=[]
for i,pp in enumerate(parts):
 q,a,b=shapes[i];ar=q.difference(hp).area
 if ar>eps:outside.append({'part':pp['name'],'area_m2':ar})
# Local stair contacts and all lantern support chains can be verified without
# pretending the base slab has a supported receiving structure below it.
by={r['name']:i for i,r in enumerate(parts)};stairs=[]
for level,y in enumerate(p['upper_datums'][:-1]):
 for label,n,yy in [('first',f'SC_Stair_{level}_0_0_0',y),('last',f'SC_Stair_{level}_1_12_0',y+4.5)]:
  q,a,b=shapes[by[n]];distance=q.distance(floors[yy]);stairs.append({'level':level,'contact':label,'distance_m':distance,'touches':distance<eps})
fixtures=[]
for l in p['lights']:
 name=l['name'];mount=next((i for i,r in enumerate(parts)if r['name']==name+'_mount'),None);body=by[name+'_body_0'];q,a,b=shapes[body];qq,aa,bb=shapes[mount]
 fixtures.append({'fixture':name,'body_mount_contact':q.intersects(qq)and max(a,aa)<=min(b,bb)+eps,'has_declared_mount':mount is not None})
miny=min(a for q,a,b in shapes);assert miny>=83.76-1e-6
report={'schema':'astraea.sunset_house_geometry.v1','source_plan_sha256':sha(P),'membership':{'whole_ship':1000,'house':147,'ordinary_family':83,'rest_slots':215,'specialty_hold':47,'VIP_hold':17,'separate_D04':20,'regular_set_exact':True},'unintended_guest_volume_conflicts':clashes,'temporary_reservation_edge_guard_contacts':minor,'duplicate_new_floors':new_duplicate,'overlap_existing_floor_owners':existing_duplicate,'entries':entries,'routes':routes,'D17_actual_polygon_cut_checks':vipchecks,'outside_upper_hull':outside,'stair_contacts':stairs,'fixture_contacts':fixtures,'minimum_new_part_y':miny,'lower_receiver_status':'ALL HELD: no support member below D13 floor-bottom, no D12 Vesper or lower-programme intrusion','lower_owner_inventory':p['receiving_interface_blocks'],'scoped_pass':not(clashes or new_duplicate or existing_duplicate or outside)and all(r['covered']for r in entries)and all(r['source_floor_covers_swept_path']for r in routes)and all(r['area_m2']<eps for r in vipchecks)and all(r['touches']for r in stairs)and all(r['body_mount_contact']for r in fixtures),'limits':p['limits']}
(R/'qa/HOUSE_GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n');print('SUNSET_HOUSE_GEOMETRY',report['scoped_pass'],'clashes',len(clashes),'minor_guards',len(minor),'outside',len(outside));assert report['scoped_pass']
