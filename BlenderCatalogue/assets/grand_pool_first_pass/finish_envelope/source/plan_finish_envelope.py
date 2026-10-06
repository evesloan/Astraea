"""Author only new Grand Pool finish geometry contract; no engine or original writes."""
from pathlib import Path
import sys, json, hashlib, math
try: import shapely
except ModuleNotFoundError:
 sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps');import shapely
from shapely.geometry import Polygon,box as planar_box,MultiPoint
from shapely.geometry.polygon import orient
import numpy as np
HERE=Path(__file__).resolve().parents[1];CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002');GAME=Path('/workspace/shared/astraea-godot-production-20261003')
assert shapely.__version__=='2.1.2'
S=json.loads((CAT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text());OLD={p['name']:p for p in S['source_parts']};FLOORS={f['id']:f for f in S['floor_regions']};parts=[];fixtures=[];checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def add(name,vertices,faces,role,support,witnesses=None,notes=''):
 assert name not in {p['name'] for p in parts};assert vertices and faces
 row=dict(name=name,world_vertices=[[float(a) for a in v] for v in vertices],faces=[list(f) for f in faces],material_role=role,parent_design_id='AST-AQU-016',support=support,contact_witnesses=witnesses or [],collision_contract='concave_static_surface',notes=notes)
 parts.append(row);return row

def prism(name,shape,lo,hi,role,support):
 assert shape.is_valid and hi>lo
 result=[]
 for j,p in enumerate(shapely.get_parts(shape)):
  if p.is_empty or p.area<1e-7:continue
  p=orient(p,sign=1);tris=list(shapely.constrained_delaunay_triangles(p).geoms);assert abs(sum(t.area for t in tris)-p.area)<1e-6
  v=[];f=[]
  for t in tris:
   q=list(orient(t,sign=1).exterior.coords)[:3]
   for y,order in [(lo,[0,1,2]),(hi,[2,1,0])]:
    off=len(v);v.extend((x,y,z) for x,z in q);f.append([off+i for i in order])
  for ring in [p.exterior,*p.interiors]:
   q=list(ring.coords)
   for a,b in zip(q,q[1:]):
    off=len(v);v.extend([(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]);f.append([off+i for i in [3,2,1,0]])
  n=name if len(list(shapely.get_parts(shape)))==1 else name+'_%02d'%j
  row=add(n,v,f,role,support);result.append(row)
 return result

def box(name,x0,x1,y0,y1,z0,z1,role,support,witness=None):
 v=[(x,y,z) for y in [y0,y1] for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]
 return add(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,support,witness or [])
def chamfer(x0,x1,z0,z1,c):
 return [(x0+c,z0),(x1-c,z0),(x1,z0+c),(x1,z1-c),(x1-c,z1),(x0+c,z1),(x0,z1-c),(x0,z0+c)]
def ring_profile(name,outer,inner,outer_bottom,outer_top,inner_bottom,inner_top,role,support):
 assert len(outer)==len(inner)
 for i in range(len(outer)):
  j=(i+1)%len(outer);v=[(outer[i][0],outer_bottom,outer[i][1]),(outer[j][0],outer_bottom,outer[j][1]),(inner[j][0],inner_bottom,inner[j][1]),(inner[i][0],inner_bottom,inner[i][1]),(outer[i][0],outer_top,outer[i][1]),(outer[j][0],outer_top,outer[j][1]),(inner[j][0],inner_top,inner[j][1]),(inner[i][0],inner_top,inner[i][1])]
  witness=[dict(point_xyz=[(outer[i][0]+outer[j][0])*.5,outer_top,(outer[i][1]+outer[j][1])*.5],normal_xyz=[0,-1,0],contact='upper attachment to original ceiling underside')]
  add(name+'_%02d'%i,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,support,witness)

def source_footprint(prefix,margin=0):
 out=[]
 for p in S['source_parts']:
  if not p['name'].startswith(prefix):continue
  hull=MultiPoint([(v[0],v[2]) for v in p['world_vertices']]).convex_hull
  out.append(hull.buffer(margin,join_style='mitre'))
 return shapely.union_all(out)

def native_box(name,center,right,up,forward,width,height,depth,role,support):
 c=np.array(center);r=np.array(right)*width/2;u=np.array(up)*height/2;f=np.array(forward)*depth/2
 v=[(c+sx*r+sy*u+sz*f).tolist() for sz in [-1,1] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return add(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,support)

def beam(name,a,b,width,depth,role,support):
 a=np.array(a);b=np.array(b);f=(b-a)/np.linalg.norm(b-a);r=np.cross(f,[0,1,0]);
 if np.linalg.norm(r)<.01:r=np.cross(f,[1,0,0])
 r/=np.linalg.norm(r);u=np.cross(r,f);return native_box(name,(a+b)/2,r,u,f,width,depth,float(np.linalg.norm(b-a)),role,support)

def fixture(name,position,target,wall_anchor,wall_normal,host,width=.95,height=.22,range_m=12,energy=.6):
 # Source marker is 20mm in front of the physical emitting lens, not inside housing.
 p=np.array(position);t=np.array(target);f=(t-p)/np.linalg.norm(t-p);r=np.cross(f,[0,1,0]);r/=np.linalg.norm(r);u=np.cross(r,f)
 anchor=np.array(wall_anchor);n=np.array(wall_normal,dtype=float);ar=np.cross(n,[0,1,0]);ar/=np.linalg.norm(ar);au=np.cross(ar,n)
 back=native_box(name+'_SourceBackplate',anchor+n*.035,ar,au,n,.38,.40,.07,'champagne_metal',host);back['contact_witnesses']=[dict(point_xyz=list(wall_anchor),normal_xyz=list(wall_normal),contact='real fixed host face')]
 beam(name+'_SupportedArm',anchor+n*.04,p-f*.18,.11,.10,'champagne_metal',back['name'])
 body=native_box(name+'_RecessHousing',p-f*.15,r,u,f,width,height,.22,'warm_walnut',name+'_SupportedArm')
 lens=native_box(name+'_OpalLens',p-f*.030,r,u,f,width-.10,height-.07,.020,'lens',body['name']);lens['collision_contract']='visual_lens_no_contact';lens['cast_shadow']=False
 fixtures.append(dict(name='DATUM_finish_light_'+name,position_xyz=p.tolist(),direction_xyz=f.tolist(),receiver_xyz=t.tolist(),physical_housing=body['name'],physical_lens=lens['name'],host=host,suggested_range_m=range_m,suggested_energy=energy,suggested_spot_angle_degrees=62,shadow_budget='existing shared maximum8 unchanged',settings_status='source trial only; parent graphical/selection checks mandatory'))

# Four coherent central coffer fields, clipped inside the actual glazing boundary.
roof_fields=[(-460.60,-451.60),(-450.40,-433.60),(-432.40,-416.60),(-415.40,-403.40)]
for i,(za,zb) in enumerate(roof_fields):
 outer=chamfer(-43.45,-18.55,za,zb,2.40 if i in [0,3] else .80);inner=chamfer(-42.0,-20.0,za+1.20,zb-1.20,.85)
 ring_profile('Finish_RoofCoffer_%d_SplayedWalnut'%i,outer,inner,60.37,60.76,60.60,60.76,'warm_walnut','D10_shared_table_reserved_cap_underside')
 rows=prism('Finish_RoofCoffer_%d_PaleCentralField'%i,Polygon(inner),60.60,60.70,'ivory_enamel','Finish_RoofCoffer_%d_SplayedWalnut'%i)
 for row in rows:row['notes']='Supported on the continuous inner coffer seat; overhead non-walkable finish, no structural-floor registration'
 # Small muted warm-metal ledge at the genuine profiled inner junction.
 border=Polygon(inner).difference(Polygon(chamfer(-41.92,-20.08,za+1.28,zb-1.28,.85)))
 prism('Finish_RoofCoffer_%d_InnerJunction'%i,border,60.575,60.605,'champagne_metal','Finish_RoofCoffer_%d_SplayedWalnut'%i)

# Whole-market bay backing and supported perimeter coffers. Old central fields,
# all9 fixture panels and their source exits remain exposed.
for i,(za,zb) in enumerate([(-456.8,-444.6),(-443,-427.3),(-425.8,-409)]):
 z0,z1=za+1.60,zb-1.60;host='GP_MarketBayRear_'+str(i)
 box('Finish_Market_%d_StoneBase'%i,-53.34,-53.245,52.50,52.74,z0,z1,'warm_stone',host,[dict(point_xyz=[-53.34,52.62,(z0+z1)*.5],normal_xyz=[1,0,0])])
 box('Finish_Market_%d_PaleStockField'%i,-53.34,-53.265,52.74,57.65,z0,z1,'ivory_enamel',host,[dict(point_xyz=[-53.34,55.20,(z0+z1)*.5],normal_xyz=[1,0,0])])
 box('Finish_Market_%d_WarmHeader'%i,-53.265,-53.205,55.62,56.15,z0+.18,z1-.18,'warm_walnut','Finish_Market_%d_PaleStockField'%i)
 # Real faceted end-return solid expands toward the supported canopy.
 for side,z in enumerate([z0,z1]):
  sign=1 if side==0 else -1
  v=[(-53.34,52.74,z),(-53.205,52.74,z),(-53.205,55.60,z),(-53.12,57.65,z),(-53.34,57.65,z)]
  v2=[(x,y,zz+sign*.16) for x,y,zz in v]
  add('Finish_Market_%d_SplayedEnd_%d'%(i,side),v+v2,[tuple(reversed(range(5))),tuple(range(5,10))]+[(j,(j+1)%5,(j+1)%5+5,j+5) for j in range(5)],'warm_walnut',host)
 outer=Polygon(chamfer(-53.56,-48.14,za+.04,zb-.04,.73));inner=Polygon(chamfer(-52.62,-49.08,za+1.03,zb-1.03,.58))
 ring=outer.difference(inner).difference(shapely.union_all([source_footprint('GP_UpperPier_',.025),source_footprint('GP_OrangeReveal_',.015),source_footprint('GP_MarketBayRear_',.0)]))
 rows=prism('Finish_Market_%d_SupportedCanopyCoffer'%i,ring,57.65,57.95,'warm_walnut','GP_BayCanopy_'+str(i))
 for row in rows:row['notes']='Top joins actual canopy underside; source piers relieved by25mm. Central fixture field remains open.'

# Sheltered rear wet edge. This is ceiling/wall lining, never a duplicate floor.
wet_interval=(-456.72,-398.28);host='GP_WestWall.001'
box('Finish_WetWest_StonePlinth',-53.72,-53.60,46.20,47.08,*wet_interval,'warm_stone',host,[dict(point_xyz=[-53.72,46.7,-440],normal_xyz=[1,0,0])])
box('Finish_WetWest_PaleQuietField',-53.72,-53.63,47.08,51.80,*wet_interval,'ivory_enamel',host,[dict(point_xyz=[-53.72,49.4,-440],normal_xyz=[1,0,0])])
# Four differently sized end-conditioned wall bays; the canopy carries their
# shared hospitality hierarchy while the existing lounge floor stays untouched.
for i,(za,zb) in enumerate([(-456.45,-452.95),(-449.05,-434.95),(-431.05,-417.95),(-414.05,-398.55)]):
 box('Finish_WetWest_%d_RecessBacking'%i,-53.63,-53.608,47.28,50.92,za+.20,zb-.20,'warm_stone','Finish_WetWest_PaleQuietField')
 # Splayed crown solid, not a strip pretending to be a new room shell.
 profile=[(-53.63,50.90),(-53.50,50.90),(-53.40,51.65),(-53.40,52.20),(-53.72,52.20)]
 v=[(x,y,z) for z in [za,zb] for x,y in profile];n=len(profile)
 add('Finish_WetWest_%d_ProfiledCrown'%i,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],'warm_walnut',host)
wet_soffit=planar_box(-53.72,wet_interval[0],-47.85,wet_interval[1]).difference(source_footprint('GP_SculptedPier_',.025))
rows=prism('Finish_WetWest_ShelteredSoffit',wet_soffit,52.12,52.26,'ivory_enamel','D09_orchard_market_gallery_underside')
# Deep edge profile attaches to the same real soffit and gives the resting edge
# a deliberate section without hiding any of the x=-46.3 source lights.
rows+=prism('Finish_WetWest_WarmCeilingReturn',planar_box(-48.18,wet_interval[0],-47.85,wet_interval[1]).difference(source_footprint('GP_SculptedPier_',.025)),51.75,52.12,'warm_walnut','Finish_WetWest_ShelteredSoffit')

# Arrival fascia: only the exposed long face toward the dry arrival/ramp.
# Keep the upper240mm source slab/coping band intact, and clip every adjacent
# original solid from the2mm finish footprint; never wrap hidden/end faces.
arrival_faces=[('GP_RaisedEdgeFascia','z',1),('GP_RaisedEdgeFascia.001','z',-1),('GP_RaisedEdgeFascia.002','x',1),('GP_RaisedEdgeFascia.003','x',1),('GP_RaisedEdgeFascia.004','x',1)]
for source_name,axis,sign in arrival_faces:
 src=OLD[source_name];a=np.array(src['world_vertices']);ni=2 if axis=='z' else 0;ui=0 if axis=='z' else 2;plane=float(a[:,ni].max() if sign>0 else a[:,ni].min());n0,n1=sorted([plane,plane+sign*.002]);shape=planar_box(float(a[:,ui].min()),44.002,float(a[:,ui].max()),45.95)
 clipped=[]
 for other in S['source_parts']:
  if other['name']==source_name or other.get('export_excluded'):continue
  q=np.array(other['world_vertices']);lo=q.min(0);hi=q.max(0)
  if min(n1,hi[ni])-max(n0,lo[ni])<=1e-7:continue
  cutter=planar_box(lo[ui]-.0022,lo[1]-.0022,hi[ui]+.0022,hi[1]+.0022)
  if shape.intersection(cutter).area>1e-9:clipped.append(other['name']);shape=shape.difference(cutter)
 assert not shape.is_empty,('No exposed arrival face remains',source_name)
 rows=prism('Finish_Arrival_'+source_name+'_Exposed',shape,n0,n1,'aquatic_edge_tile',source_name)
 for row in rows:
  # prism helper treats its two planar coordinates as(x,z) and extrusion asY.
  # Here they represent(u,height) and the facade normal coordinate instead.
  row['world_vertices']=[([v[0],v[2],v[1]] if axis=='z' else [v[1],v[2],v[0]]) for v in row['world_vertices']]
  row['collision_contract']='visual_finish_original_contact_unchanged';row['notes']='Exposed dry-side face only; old floor/slab band and adjacent original solids excluded; clipped neighbours:'+','.join(clipped)
  point=shape.representative_point();w=[point.x,point.y,plane] if axis=='z' else [plane,point.y,point.x];normal=[0,0,sign] if axis=='z' else [sign,0,0];row['contact_witnesses']=[dict(point_xyz=w,normal_xyz=normal)]

# Six upward/outward source-backed roof washes, away from both old vault panels.
for z in [-451,-433,-416]:
 for sign in [-1,1]:
  name='RoofWash_%s_%s'%(abs(z),'Fore' if sign<0 else 'Aft')
  fixture(name,[-31,59.48,z+sign*.70],[-31,60.60,z+sign*6.60],[-31,59.48,z+sign*.22],[0,0,sign],'GP_RoofRib_'+str(z),1.10,.28,12,.65)
# Two real wet-rest sources on the new fixed wall face, below the new soffit.
for z in [-444,-425]:
 fixture('WetRestWash_'+str(abs(z)),[-53.25,49.72,z],[-48.41505124154828,47.184652225477144,z-.04530190464635],[-53.608,49.72,z],[1,0,0],'Finish_WetWest_%d_RecessBacking'%(1 if z==-444 else 2),.52,.32,9,.60)
 fixtures[-1]['receiver_host']='wet_rest_'+str(abs(z));fixtures[-1]['receiver_source_part']='drained_contact_panel_4';fixtures[-1]['receiver_native_glb_mesh']='AST-AQU-001__aquatic_clay_sling';fixtures[-1]['receiver_native_triangle_index']=2831;fixtures[-1]['receiver_native_triangle_xyz']=[[.005497202277183533,.9770994186401367,-.8824999928474426],[.0524325929582119,.9853038787841797,-.9162500500679016],[.005497136153280735,.9822092652320862,-.9162500500679016]];fixtures[-1]['receiver_note']='First visible retained lounger head/back surface on the unchanged central direction; no ray-through-body claim'

# Display source geometry is supplied by the independently checked stock-fit
# contract. The saved plan remains explicitly incomplete until those6 arrive.
mount_file=HERE/'source/display_light_mounts.json'
if mount_file.exists():
 mounts=json.loads(mount_file.read_text())['proposals'];assert len(mounts)==6
 for f in mounts:
  name='DisplayLight_'+f['host_display'];lo,hi=f['housing_proposal_world_bounds'];host=f['host_display']+'::'+f['physical_host_part']
  rows=prism(name+'_SupportedBarHousing',Polygon(chamfer(lo[0],hi[0],lo[2],hi[2],.012)),lo[1],hi[1],'champagne_metal',host);body=rows[0]
  body['contact_witnesses']=[dict(point_xyz=f['mount_world_xyz'],normal_xyz=[0,-1,0],contact='actual retained under-surround triangle',source_triangle_local_xyz=f['attachment_source_triangles_local_xyz'])]
  p=f['lens_proposal_world_xyz'];rows=prism(name+'_OpalLens',Polygon(chamfer(lo[0]+.010,hi[0]-.010,lo[2]+.020,hi[2]-.020,.009)),p[1]+.002,lo[1]+.001,'lens',body['name']);lens=rows[0];lens['collision_contract']='visual_lens_no_contact';lens['cast_shadow']=False
  fixtures.append(dict(name='DATUM_finish_light_'+name,position_xyz=p,direction_xyz=[0,-1,0],receiver_xyz=f['receiver_rays'][0]['receiver_world_xyz'],all_source_receiver_rays=f['receiver_rays'],physical_housing=body['name'],physical_lens=lens['name'],host=host,suggested_range_m=4,suggested_energy=.45,suggested_spot_angle_degrees=62,shadow_budget='existing shared maximum8 unchanged',settings_status='source trial only; actual stock illumination/selection not accepted'))
assert len(fixtures) in [8,14]
for p in parts:
 a=np.array(p['world_vertices']);p['bounds_min_xyz']=a.min(0).tolist();p['bounds_max_xyz']=a.max(0).tolist();assert np.isfinite(a).all();assert min(p['bounds_min_xyz'][1],p['bounds_max_xyz'][1])>=44-.001 and p['bounds_max_xyz'][1]<=60.761
 volume=sum(float(np.dot(a[f[0]],np.cross(a[f[j]],a[f[j+1]]))) for f in p['faces'] for j in range(1,len(f)-1))/6
 assert abs(volume)>1e-10,(p['name'],'zero enclosed volume')
 if volume<0:p['faces']=[list(reversed(f)) for f in p['faces']]
 p['signed_volume_m3']=abs(volume)
main_opening=Polygon(S['opening']['main_boundary'])
for p in parts:
 if p['name'].startswith('Finish_RoofCoffer_'):
  footprint=MultiPoint([(v[0],v[2]) for v in p['world_vertices']]).convex_hull
  assert main_opening.buffer(-.14,join_style='mitre').covers(footprint),('Roof finish would cross retained glazing head',p['name'])
# Source floor-underside supports must have every attachment vertex in the exact
# compiler polygon and at its true bottom elevation, not a guessed floor datum.
for p in parts:
 if not p['support'].endswith('_underside'):continue
 key=p['support'][:-10];f=FLOORS[key];surface=float(f['floor_y'])-float(f['thickness']);shape=shapely.union_all([Polygon(t) for t in f['triangles']]);top=max(v[1] for v in p['world_vertices'])
 assert abs(top-surface)<.00001,(p['name'],top,surface)
 footprint=MultiPoint([(v[0],v[2]) for v in p['world_vertices']]).convex_hull
 # A concave split mesh may have a convex hull across a relieved pier, but all
 # its actual vertices must be supported; source profiles have no floor holes here.
 assert all(shape.buffer(1e-7).covers(shapely.Point(v[0],v[2])) for v in p['world_vertices'] if abs(v[1]-top)<1e-7),p['name']
 checks.append(dict(part=p['name'],support=key,surface_y=surface,attachment_vertices_supported=True))
result=dict(schema=1,status='source_geometry_plan_pending_display_mounts' if len(fixtures)<14 else 'source_geometry_plan_pending_Blender_and_contact_QA',parent_design_id='AST-AQU-016',derived_export='AST-AQU-016_finish_envelope.glb',coordinate_frame='Godot world metres, convert to Blender (x,-z,y)',original_inputs={'connected_contract_sha256':sha(CAT/'assets/grand_pool_orchard_section/source/connected_contract.json'),'original_blend_sha256':sha(CAT/'assets/grand_pool_orchard_section/source/AST-AQU-016.blend'),'old_runtime_contract_sha256':sha(GAME/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json'),'retained_furnishings_sha256':sha(GAME/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json')},parts=parts,fixtures=fixtures,roof_fields=roof_fields,ceiling_support_checks=checks,old_fixture_markers=S['fixtures'],required_sign_count=11,limits=['No Blender/Godot/import/render job','No new floors or altered panes/voids/routes/controllers/oldmodel bytes','Exact source contacts, old-fixture cone exits, allgeometry interference, light selection and signlegibility remain mandatory gates'])
(HERE/'source/finish_contract.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'qa/geometry_plan_summary.json').write_text(json.dumps(dict(status=result['status'],parts=len(parts),fixtures=len(fixtures),ceiling_support_checks=len(checks),source_sha256=result['original_inputs']),indent=2)+'\n');print(json.dumps(dict(status=result['status'],parts=len(parts),fixtures=len(fixtures),ceiling_support_checks=len(checks)),indent=2))
