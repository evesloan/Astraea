"""Pure-math Court A preparation. No Blender, Godot, shared writes or source edits.

Outputs only beside this file; preserves earlier draft revisions alongside the current contract.
The composition is deliberately a single new, standalone AST-CUL-005 derivative.
"""
from pathlib import Path
import json, math, hashlib, sys
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import triangulate, unary_union

R=Path(__file__).resolve().parent
A=R.parents[1]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
P=C/'assets/grand_lantern_theater_section'
G=Path('/workspace/shared/astraea-godot-production-20261003')
BASE=P/'source/firstpass_003/source_repair003/AST-CUL-005_firstpass_003.blend'
BASE_HASH='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
F=69.5
objects=[]; instances=[]; seats=[]; soils=[]; mounts=[]; support_footprints=[]
materials={}
for p in [C/'materials/material_manifest.json',C/'materials/botanical/manifest.json']:
 for role,spec in read(p)['materials'].items():
  file=p.parent/(spec.get('file') or spec['base_color_file'])
  assert sha(file)==spec['sha256'],file
  materials[role]={**spec,'source_texture':str(file),'source_manifest':str(p),'reuse_exact_graph_when_present':True}

def out(name,data):
 with (R/name).open('w') as f: json.dump(data,f,indent=2,allow_nan=False);f.write('\n')

def metric_uv(v,faces,role,preferred_v='y'):
 """Face-local true metre coordinates, never an oblique dominant-axis shrink.
 Curved strips retain separate per-face loops. Timber V follows requested grain.
 """
 sx,sy=materials[role]['meters_per_tile_uv']; result=[]
 grain={'x':np.array([1.,0,0]),'y':np.array([0.,1,0]),'z':np.array([0.,0,1])}[preferred_v]
 for face in faces:
  p=v[face]; n=np.zeros(3)
  for k in range(1,len(p)-1): n+=np.cross(p[k]-p[0],p[k+1]-p[0])
  n/=np.linalg.norm(n)
  vv=grain-n*np.dot(grain,n)
  if np.linalg.norm(vv)<1e-8:
   vv=p[1]-p[0];vv-=n*np.dot(vv,n)
  vv/=np.linalg.norm(vv);u=np.cross(vv,n)
  # Offset only; no normalization to 0..1, so material metre density is real.
  result.append([[float(np.dot(q-v[0],u)/sx),float(np.dot(q-v[0],vv)/sy)]for q in p])
 return result

def emit(name,vs,fs,mat,role,**kw):
 v=np.asarray(vs,dtype=np.float32).astype(float);fs=[list(f)for f in fs]
 origin=v.mean(0);w=v-origin
 vol=sum(np.dot(w[f[0]],np.cross(w[f[k]],w[f[k+1]]))/6 for f in fs for k in range(1,len(f)-1))
 if vol<0:fs=[list(reversed(f))for f in fs];vol=-vol
 assert vol>1e-10,(name,vol)
 edges={}
 for f in fs:
  for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
 assert set(edges.values())=={2},name
 assert len(name.encode())<64
 row={'name':name,'semantic_id':'D11.CourtA.Completion004.'+name,'vertices_world':v.tolist(),'faces':fs,'material_family':mat,'role':role,'collides':role not in ['cosmetic_floor_textile','noncolliding_artwork','botanical_leaf'], 'closed_volume_m3':float(vol),'bounds_world':[v.min(0).tolist(),v.max(0).tolist()],**kw}
 row['face_uv']=metric_uv(v,fs,mat,kw.get('grain_axis','y'))
 objects.append(row);return row

def prism(name,poly,y0,y1,mat,role,**kw):
 # Triangulate concave cap polygons while retaining the same boundary vertices.
 p=Polygon(poly);assert p.is_valid and p.area>0,name
 if not p.exterior.is_ccw:poly=list(reversed(poly));p=Polygon(poly)
 n=len(poly);vs=[[x,y,z]for y in[y0,y1]for x,z in poly];fs=[]
 for t in triangulate(p):
  if p.covers(t.representative_point()):
   ix=[min(range(n),key=lambda i:math.dist(poly[i],q))for q in list(t.exterior.coords)[:3]]
   fs.extend([ix[::-1],[i+n for i in ix]])
 fs.extend([[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)])
 return emit(name,vs,fs,mat,role,**kw)

def rect(lo,hi):return [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]
def cube(name,lo,hi,mat,role,**kw):return prism(name,rect([lo[0],lo[2]],[hi[0],hi[2]]),lo[1],hi[1],mat,role,**kw)
def ellipse(cx,cz,rx,rz,n=24):return [(cx+rx*math.cos(i*math.tau/n),cz+rz*math.sin(i*math.tau/n))for i in range(n)]
def strip(points,oa,ob):return [(x+oa,z)for x,z in points]+[(x+ob,z)for x,z in reversed(points)]
def mirror(poly):return [(-139-x,z)for x,z in poly]
def transform(p,yaw,origin):
 c,s=math.cos(yaw),math.sin(yaw);x,y,z=p
 return [origin[0]+x*c+z*s,origin[1]+y,origin[2]-x*s+z*c]

measure=read(A.parent/'RETAINED_MODULE_MEASUREMENTS.json');measure.update(read(A/'RETAINED_FOCAL_ASSET_BOUNDS.json'))
def retained(name,asset,position,yaw=0,**kw):
 m=measure[asset];assert sha(C/m['source'])==m['source_sha256'];assert sha(C/m['export'])==m['export_sha256']
 lo,hi=[m['bounds_gltf'][k]for k in['min','max']]
 corners=[transform([x,y,z],yaw,position)for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]]
 row={'id':name,'asset':asset,'source':str(C/m['source']),'source_sha256':m['source_sha256'],'export':str(C/m['export']),'export_sha256':m['export_sha256'],'position_world':position,'yaw_radians':yaw,'scale':[1,1,1],'bounds_world':[np.min(corners,0).tolist(),np.max(corners,0).tolist()],**kw};instances.append(row);return row

# Six-place social pair. The 2.2-ish metre reservation includes standing access,
# not a 2.2 m solid island that would consume the 3.1 m protected clear spine.
for side in ['W','E']:
 reflect=(lambda p:p)if side=='W'else mirror
 points=[]
 for i in range(17):
  t=-1+2*i/16;points.append((-72.92+.08*t+.18*t*t,-137.45+1.45*t))
 name='A4_'+side
 footprint=reflect(strip(points,-.69,.70))
 # Profiled grounded plinth, concealed floor contact is exact Y69.5.
 prism(name+'_plinth',footprint,F,F+.12,'warm_stone','fixed_furnishing',contact='Compiler-owned D11 structural floor only')
 support_footprints.append({'id':name+'_plinth','polygon_xz':footprint,'floor_y':F})
 # Actual open soil trough: separate outer/inner strips and terminal closures.
 basin=reflect(strip(points,-.68,.015));soil=reflect(strip(points,-.62,-.04))
 prism(name+'_basin_bottom',basin,F+.12,F+.19,'ivory_enamel','fixed_furnishing')
 for label,a,b in [('outer',-.68,-.62),('inner',-.04,.015)]:prism(name+'_basin_'+label,reflect(strip(points,a,b)),F+.19,F+.70,'ivory_enamel','fixed_furnishing')
 for k in[0,-1]:
  q=points[k];z0=q[1] if k==0 else q[1]-.065
  poly=rect([q[0]-.62,z0],[q[0]-.04,z0+.065]);prism(name+'_basin_end'+str(k),reflect(poly),F+.19,F+.70,'ivory_enamel','fixed_furnishing')
 soil_points=points[1:-1];soil=reflect(strip(soil_points,-.62,-.04))
 prism(name+'_soil',soil,F+.19,F+.64,'botanical_soil','plant_root_receiver',soil_depth_m=.45)
 soils.append({'id':name+'_soil','polygon_xz':soil,'bottom_y':F+.19,'top_y':F+.64})
 prism(name+'_seat_support',reflect(strip(points,.005,.645)),F+.12,F+.345,'warm_walnut','fixed_furnishing',grain_axis='z')
 # Cushion rings: shoulders are inset and crowned, not flat stretched boxes.
 cp=points[1:-1]
 rings=[(F+.34,.045,.625),(F+.365,.025,.66),(F+.445,.045,.65),(F+.475,.09,.60)]
 outlines=[reflect(strip(cp,a,b))for y,a,b in rings];n=len(outlines[0]);v=[[x,y,z]for (y,a,b),poly in zip(rings,outlines)for x,z in poly];fs=[]
 for t in triangulate(Polygon(outlines[0])):
  if Polygon(outlines[0]).covers(t.representative_point()):
   ix=[min(range(n),key=lambda i:math.dist(outlines[0][i],q))for q in list(t.exterior.coords)[:3]];fs.append(ix[::-1]);fs.append([i+3*n for i in ix])
 for j in range(3):
  for i in range(n):fs.append([j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i])
 emit(name+'_crowned_cushion',v,fs,'clay_weave'if side=='W'else'teal_weave','fixed_furnishing',seat_height_m=.475,grain_axis='z')
 prism(name+'_curved_back_shell',reflect(strip(points,-.01,.095)),F+.345,F+.995,'warm_walnut','fixed_furnishing',grain_axis='z')
 prism(name+'_back_pad',reflect(strip(cp,.095,.155)),F+.49,F+.945,'oatmeal_weave','fixed_furnishing',grain_axis='z')
 for k,t in enumerate([-.57,0,.57]):
  z=-137.45+1.45*t;bx=-72.92+.08*t+.18*t*t
  x=bx+.39;x=x if side=='W'else-139-x
  aim=[-139-x,F+.82,z-.25] # Actual other curved sofa, slightly toward reception.
  ap=[]
  for zz in np.linspace(z-.39,z+.39,9):
   tt=(zz+137.45)/1.45;ap.append((-72.92+.08*tt+.18*tt*tt,float(zz)))
  approach=reflect(strip(ap,.73,1.55))
  seats.append({'id':name+'_seat'+str(k),'seat_contact_world':[x,F+.475,z],'eye_world':[x,F+1.2,z],'focus_world':aim,'secondary_focus_world':[-69.5,71.0,-140.3],'front_approach_polygon_xz':approach,'standing_point_world':[(bx+1.10)if side=='W'else-139-(bx+1.10),F,z], 'no_new_audience_capacity':True})
 # Compact flowering lower bank. Retained whole crowns remain unscaled.
 for k,t in enumerate([-.64,-.21,.22,.65]):
  z=-137.45+1.45*t;bx=-72.92+.08*t+.18*t*t;x=bx-.3375
  retained(name+'_rose'+str(k),'AST-BOT-003',[x if side=='W'else-139-x,F+.637,z],math.pi/2,root_receiver=name+'_soil',root_radius_m=.035,soil_patch_radius_m=.085,minimum_soil_depth_m=.14)
 # Tables sit at the open south end, not in front of knees or in the spine.
 tx=-72.15 if side=='W'else-66.85
 retained(name+'_table','AST-FUR-003',[tx,F,-139.38],0,table_contents='One paired programme stack in the inset actual top; no potted filler')

counter=retained('A4_reception','AST-CUL-002',[-69.5,F,-140.3],0,
 public_front_world=[0,0,1],staff_open_side_world=[0,0,-1],drawer_travel_world=[0,0,-.28],
 retained_lower_writing_surface_world=[-69.97,70.305,-140.26],
 storage_contact_world=[-69.27,69.767,-140.3],
 service_standing_world=[-69.25,F,-141.40],public_standing_world=[-69.4,F,-139.35],
 low_writing_standing_world=[-69.97,F,-139.38])

# Rear backing: one fitted curved composition, with closed fabric inserts at
# recessed front depths in NEW panels. Existing glass/walls are never cut.
xs=np.linspace(-73.45,-65.55,21)
rear=[(float(x),float(-145.66+.50*((x+69.5)/3.95)**2))for x in xs]
poly=[(x,z-.10)for x,z in rear]+[(x,z+.10)for x,z in reversed(rear)]
prism('A4_back_plinth',poly,F,F+.14,'warm_stone','fixed_furnishing')
support_footprints.append({'id':'A4_back_plinth','polygon_xz':poly,'floor_y':F})
prism('A4_back_walnut_dado',poly,F+.14,F+.93,'warm_walnut','acoustic_backing',grain_axis='y')
# Five broad panels with substantial stiles: no per-slat microgeometry.
for j in range(5):
 x0=-73.45+j*1.58;x1=x0+1.58;pp=[p for p in rear if x0-1e-6<=p[0]<=x1+1e-6]
 if pp[0][0]>x0+1e-6:pp.insert(0,(x0,-145.66+.50*((x0+69.5)/3.95)**2))
 if pp[-1][0]<x1-1e-6:pp.append((x1,-145.66+.50*((x1+69.5)/3.95)**2))
 top=73.36 if j==2 else 72.64
 prism('A4_back_core'+str(j),[(x,z-.10)for x,z in pp]+[(x,z+.025)for x,z in reversed(pp)],F+.93,top,'warm_walnut','acoustic_backing')
 # Fabric is recessed 60 mm behind the 100 mm forward reveal.
 middle=[p for p in pp if x0+.10<=p[0]<=x1-.10]
 middle=[(x0+.10,-145.66+.50*((x0+.10+69.5)/3.95)**2)]+middle+[(x1-.10,-145.66+.50*((x1-.10+69.5)/3.95)**2)]
 prism('A4_back_fabric'+str(j),[(x,z+.025)for x,z in middle]+[(x,z+.04)for x,z in reversed(middle)],F+1.05,top-.12,'clay_weave'if j in[0,4]else'oatmeal_weave','acoustic_insert')
 for k,x in enumerate([x0,x1-.075]):
  z=-145.66+.50*((x+.0375+69.5)/3.95)**2
  cube('A4_back_stile'+str(j)+'_'+str(k),[x,F+.93,z+.025],[x+.075,top,z+.10],'warm_walnut','acoustic_backing')
 # Broad horizontal reveal rails stop at each bay, permitting actual recess.
 for k,y in enumerate([F+.93,top-.12]):
  prism('A4_back_rail'+str(j)+'_'+str(k),[(x,z+.025)for x,z in pp]+[(x,z+.10)for x,z in reversed(pp)],y,y+.12,'warm_walnut','acoustic_backing',grain_axis='x')

# Mounted programme face uses a newly authored original image; source-backed
# AST-CUL-001 cassette vocabulary, no copied real-world logo or claim of times.
cube('A4_sign_bearing',[-70.13,72.26,-145.645],[-68.87,73.27,-145.49],'warm_walnut','acoustic_backing',contact='Centre backing core/front face, bounded bearing overlap')
cube('A4_sign_frame',[-70.17,72.23,-145.51],[-68.83,73.31,-145.47],'champagne_metal','acoustic_backing')
# Graphic specifications, not a falsely accepted new texture.
graphic={'id':'A4_SunCorp_programme','support':'A4_sign_frame','front_plane_z':-145.465,'bounds_world':[[-70.125,72.275,-145.47],[-68.875,73.265,-145.465]],'material_role':'court_A_original_programme','uv':'Front UV spans exactly [0,1] x [0,1]; no metric repeat of artwork','status':'NEW ORIGINAL ART DRAFT REQUIRED BEFORE BLENDER BUILD','text':['SUNCORP CULTURE','GRAND LANTERN','A THOUSAND SMALL WORLDS','PROGRAMME STUDY'],'copy_source':'Retained fictional title and theatre; original SunCorp lettering/orbit motif; no current showtime or admission claim'}

# Side ceiling ribbons, at human-scale 3.35 m underside, retain a 4.1 m-wide
# open central strip to the old vault/coffer. Bearings use SIX existing piers.
arch=read(A/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json')['objects']
for side in ['W','E']:
 s=-1 if side=='W'else 1;outer=-73.60 if side=='W'else-65.40
 # Shaped inner edge is closest to the axis over the seating, retreats at ends.
 zvals=np.linspace(-146.2,-130.4,25)
 inner=[((-71.70+.15*math.cos((z+138.3)/7.9*math.pi))if side=='W'else(-67.30-.15*math.cos((z+138.3)/7.9*math.pi)),float(z))for z in zvals]
 p=[(outer,float(z))for z in zvals]+list(reversed(inner))
 prism('A4_'+side+'_canopy_shell',p,72.885,73.08,'warm_walnut','supported_ceiling',grain_axis='z')
 prism('A4_'+side+'_canopy_soft',p,72.85,72.885,'oatmeal_weave','supported_ceiling',grain_axis='z')
 # Low-cost shaped edge band; no new light and no changes to source identities.
 band=inner+[(x+(-.035 if side=='W'else .035),z)for x,z in reversed(inner)]
 prism('A4_'+side+'_canopy_edge',band,72.85,73.08,'champagne_metal','supported_ceiling')
 for j,z in enumerate([-130.4,-138.3,-146.2]):
  old=next(o for o in arch if o['name']==f'FP2_D11_COURT_A_PIER_{j}_{s}')
  vv=np.array(old['vertices_world']);x=float(vv[:,0].max()if side=='W'else vv[:,0].min())
  end=-72.24 if side=='W'else-66.76
  profile=[(x,72.62),(end,72.79),(end,72.885),(x,72.885)]
  vs=[[px,y,z+dz]for dz in[-.16,.16]for px,y in profile]
  row=emit(f'A4_{side}_bracket{j}',vs,[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'champagne_metal','supported_ceiling',bearing_source=old['name'])
  mounts.append({'new':row['name'],'retained_support':old['name'],'bearing_plane_x':x,'bearing_z':[z-.16,z+.16],'bearing_y':[72.62,72.885],'canopy_contact_y':72.885,'new_to_old_contact':'Flush end face only; no existing pier cut or hidden fastening model','minimum_under_bracket_headroom_m':3.12})

# The cloth is cosmetic, follows the slab and omits every pier, new support,
# table/counter footprint and rear basin. It creates no walking floor or void.
rug=Polygon(ellipse(-69.5,-138.2,3.95,6.15,48))
cut=[]
for row in support_footprints:cut.append(Polygon(row['polygon_xz']).buffer(.025,join_style=2))
for o in arch:
 if '_D11_COURT_A_'in o['name']and('_PIER_'in o['name']or'_FOOT_'in o['name']):
  v=np.array(o['vertices_world']);cut.append(Polygon(v[:,[0,2]]).convex_hull.buffer(.025))
cut.append(box(-71.925,-143.925,-67.075,-142.075))
for row in instances:
 if row['asset']in['AST-CUL-002','AST-FUR-003']:
  lo,hi=row['bounds_world'];cut.append(box(lo[0]-.025,lo[2]-.025,hi[0]+.025,hi[2]+.025))
rug=rug.difference(unary_union(cut))
# Triangular prism islands preserve exact holes. Group into ONE authored mesh.
rv=[];rf=[]
for poly in([rug]if rug.geom_type=='Polygon'else rug.geoms):
 for t in triangulate(poly):
  if not poly.covers(t.representative_point()):continue
  tri=list(t.exterior.coords)[:3];off=len(rv);rv.extend([[x,y,z]for y in[F+.0005,F+.0055]for x,z in tri]);rf.extend([[off+2,off+1,off],[off+3,off+4,off+5],[off,off+1,off+4,off+3],[off+1,off+2,off+5,off+4],[off+2,off,off+3,off+5]])
emit('A4_fitted_teal_rug',rv,rf,'teal_weave','cosmetic_floor_textile',walking_floor_credit=False,grain_axis='z')

# Dense lower bank in the existing REAL 4.5 x 1.5 m soil. Keep old plants exact.
oldgarden=read(A/'PLANTED_COURT_GEOMETRY_002.json')
oldsoil=next(o for o in oldgarden['objects']if o['name']=='FP2_D11_GROVE_A_real_soil_volume')
sv=np.array(oldsoil['vertices_world']);soilpoly=Polygon(sv[:,[0,2]]).convex_hull
soils.append({'id':oldsoil['name'],'polygon_xz':list(soilpoly.exterior.coords)[:-1],'bottom_y':float(sv[:,1].min()),'top_y':float(sv[:,1].max()),'retained':True})
for i,x in enumerate([-71.15,-70.49,-69.83,-69.17,-68.51,-67.85]):
 retained('A4_rear_leaf'+str(i),'AST-BOT-002',[x,70.147,-143.27],0,root_receiver=oldsoil['name'],root_radius_m=.032,soil_patch_radius_m=.13,minimum_soil_depth_m=.22)
for i,x in enumerate([-71.39,-70.76,-70.13,-69.50,-68.87,-68.24,-67.61]):
 retained('A4_rear_rose'+str(i),'AST-BOT-003',[x,70.147,-142.9],0,root_receiver=oldsoil['name'],root_radius_m=.035,soil_patch_radius_m=.085,minimum_soil_depth_m=.14)

reservations=[
 {'id':'central_clear_spine','polygon_xz':rect([-71.05,-139.73],[-67.95,-134.55]),'y':[F,72.5],'clear_width_m':3.1,'scope':'Inner court only. Front usher and focal counter terminate this axis.'},
 {'id':'front_cross_aisle','polygon_xz':rect([-73.50,-135.90],[-65.50,-134.40]),'y':[F,72.5],'clear_width_m':1.5,'scope':'Existing usher rear work reservations end Z−134.35; do not stand/park inside this cross-aisle.'},
 {'id':'reception_public','polygon_xz':rect([-70.50,-139.75],[-68.40,-138.95]),'y':[F,71.5]},
 {'id':'reception_service','polygon_xz':rect([-70.35,-141.85],[-68.55,-140.95]),'y':[F,71.5],'source_void':'AST-CUL-002 staff_service_approach and drawer travel; separate no-storage pocket'},
 {'id':'reception_service_entry_west','polygon_xz':rect([-71.28,-141.85],[-70.35,-139.87]),'y':[F,71.5]},
]
for s in seats:reservations.append({'id':s['id']+'_approach','polygon_xz':s['front_approach_polygon_xz'],'y':[F,71.5]})

route={
 'entry_dogleg_waypoints_xz':[[-77.5,-137.5],[-75.5,-135.43],[-71.5,-135.43],[-69.5,-138.95]],
 'entry_explanation':'Enter from verified west aisle beyond the retained front usher; turn through the broad cross-aisle BEFORE the seating pair. This is not a 3.1 m entry slot through the usher line.',
 'old_main_route_preserved':[[-2,-126],[-45.5,-126],[-45.5,-151],[-77.5,-151],[-77.5,-137]],
 'capsule_radius_m':.3,'capsule_height_m':1.8,
 'cart_compound_contacts':str(G/'data/architecture/cleaning_cart_contacts.json'),
 'operator_local_center_xz':[0,1.62],'operator_radius_m':.3,
 'pending':'Exact dog-leg cart swept envelope is screened separately; no claim that a cart can turn in every standing pocket.'}

inputs=[BASE,Path(__file__),R.parent/'COURT_A_COMPLETION_PLAN.md',R.parent/'REFERENCE_USE.json',A/'build_planted_courts.py',A/'build_arrival_architecture.py',A/'COMPOSED_ARRIVAL_LIGHT_ARCHITECTURE_002.json',A/'PLANTED_COURT_GEOMETRY_002.json',G/'data/generated/structural_meshes.json',G/'scripts/player.gd',G/'data/architecture/cleaning_cart_contacts.json',C/'catalogue_manifest.json']
assert sha(BASE)==BASE_HASH
contract={'status':'SCRATCH_ONLY_EXACT_ADDITIVE_GEOMETRY_DRAFT_ENGINE_UNRUN','base_source':str(BASE),'base_source_sha256':BASE_HASH,'asset_identity':'AST-CUL-005 same-family Court A derivative; no new catalogue ID','standalone_source_proposal':'AST-CUL-005_arrival_court_A_004.blend','existing_source_or_runtime_mutated':False,'protected_audience_chairs':2200,'additive_only':True,'existing_instances_moved':[], 'coordinates':'Godot world X,Y-up,Z metres; Blender map (x,-z,y)','objects':objects,'retained_instances':instances,'seats':seats,'soil_receivers':soils,'mounts':mounts,'grounded_supports':support_footprints,'reservations':reservations,'routes':route,'original_programme_art':graphic,'material_contracts':{k:materials[k]for k in sorted({o['material_family']for o in objects})},'pool_broadleaf_candidate':{'status':'PENDING_RETENTION_AND_COMPOSED_IMAGE_REVIEW_NOT_USED','proposal':'Re-author individually connected blades/petioles from BOT-002 method to fit this soil; preserve node contact, full blade support and per-leaf tip normals. Do not export/reuse unretained pool prototypes or stretch a whole plant.'},'acceptance':{'pure_geometry':False,'blender_source':False,'visual':False,'native_contacts':False,'species_fit':False,'acoustics_or_load_certification':False},'input_sha256':{str(p):sha(p)for p in inputs}}
out('COURT_A_GEOMETRY_CONTRACT.json',contract)
print(json.dumps({'objects':len(objects),'instances':len(instances),'seats':len(seats),'triangles_nominal':sum(sum(len(f)-2 for f in o['faces'])for o in objects),'source_unchanged':sha(BASE)==BASE_HASH},indent=2))
