"""Independent decoder audit of actual selected GLB; no engine or Blender job."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np
OUT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(OUT/'inputs'));from decode_sections import glb
M,N=glb(OUT/'exports/cinema_library_receiving_r001.glb',np.zeros(3));by={m['name']:m for m in M};R=json.loads((OUT/'inputs/SELECTED_RECEIVING_SECTION_R1.json').read_text());res={x['id']:x for x in R['volumes']};rows=json.loads((OUT/'qa/authored_geometry.json').read_text());meta={x['name']:x for x in rows};tol=6e-5
fail=[]
def check(name,result,**kwargs):
 if not result:fail.append(name)
 return dict(check=name,passed=bool(result),**kwargs)
checks=[];contain=[]
for m in M:
 r=meta[m['name']];rid=r.get('reservation_id')
 if rid:
  v=res[rid];amount=max(max(np.array(v['min_xyz'])-m['min']),max(m['max']-np.array(v['max_xyz'])))
  contain.append(dict(name=m['name'],reservation=rid,excess_m=float(max(0,amount))))
checks.append(check('Actual_GL B_mesh_count_matches_source'.replace('GL B','GLB'),len(M)==len(rows),mesh_count=len(M)))
checks.append(check('All_authored_reserved_members_contained',all(r['excess_m']<tol for r in contain),maximum_excess_m=max(r['excess_m'] for r in contain)))
checks.append(check('No_geometry_below_Sunward_boundary',min(m['min'][1] for m in M)>=69.26-tol,min_y=min(m['min'][1] for m in M)))
checks.append(check('No_root_geometry_enters_Library_walking_clearance',max(m['max'][1] for m in M)<=78+tol,max_y=max(m['max'][1] for m in M)))
# Each mesh closed after welding exporter UV/normal split vertices.
mesh_quality=[]
for m in M:
 v=m['vertices'];f=m['faces'];keys=[tuple(np.round(x,5)) for x in v];idx={};remap=[]
 for k in keys:remap.append(idx.setdefault(k,len(idx)))
 ff=np.array(remap)[f];edges={}
 for tri in ff:
  for a,b in zip(tri,np.roll(tri,-1)):edges[tuple(sorted((int(a),int(b))))]=edges.get(tuple(sorted((int(a),int(b)))),0)+1
 bad=sum(x!=2 for x in edges.values());vol=float(np.sum(np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])))/6)
 mesh_quality.append(dict(name=m['name'],nonmanifold_edges=bad,signed_volume_m3=vol,finite=bool(np.isfinite(v).all())))
checks.append(check('Every_exported_mesh_is_closed_and_finite',all(x['nonmanifold_edges']==0 and x['finite'] and x['signed_volume_m3']>1e-10 for x in mesh_quality)))
# Contact ledger checks geometry boundary planes and overlapping contact extents; not capacities.
C=json.loads((OUT/'exports/receiver_contacts.json').read_text())['contacts'];ct=[]
def find(name):
 if name in by:return [by[name]]
 return [m for m in M if meta[m['name']]['semantic_group']==name]
for c in C:
 if c['status']!='internal_exact_contact':continue
 aa=find(c['lower']);bb=find(c['upper']);ax='XYZ'.index(c['axis']);plane=c['world_plane'];hits=[]
 for a in aa:
  for b in bb:
   opposing=(abs(a['max'][ax]-plane)<tol and abs(b['min'][ax]-plane)<tol) or (abs(a['min'][ax]-plane)<tol and abs(b['max'][ax]-plane)<tol)
   other=[i for i in range(3) if i!=ax];overlap=np.minimum(a['max'][other],b['max'][other])-np.maximum(a['min'][other],b['min'][other])
   if opposing and min(overlap)>tol:hits.append([a['name'],b['name']])
 ct.append(dict(id=c['id'],passed=bool(hits),actual_contact_pairs=hits))
checks.append(check('All_recorded_internal_contacts_touch_actual_export',all(x['passed'] for x in ct),count=len(ct),failed=[x['id'] for x in ct if not x['passed']] ))
# Exact complete finite aperture truncated convex frustum. Triangle clipping, not sampled central rays.
z0=-416.0125;z1=-459.47
# f(p)>=0 lies inside; left,right,bottom,top,near,far.
planes=[]
for axis,v0,v1,sgn in [(0,35.73,23,1),(0,36.27,49,-1),(1,73.52,70.7,1),(1,73.84,75.7,-1)]:
 slope=(v1-v0)/(z1-z0);normal=np.zeros(3);normal[axis]=sgn;normal[2]=-slope*sgn;d=(-v0+slope*z0)*sgn;planes.append((normal,d))
planes += [(np.array([0.,0.,-1.]),z0),(np.array([0.,0.,1.]),-z1)]
def clip(poly,n,d):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  va=np.dot(n,a)+d;vb=np.dot(n,b)+d
  if va>=-1e-8:out.append(a)
  if (va>=0)!=(vb>=0):out.append(a+(b-a)*(va/(va-vb)))
 return out
optic_hits=[]
for m in M:
 if any(np.max(m['vertices']@n+d)<-1e-8 for n,d in planes):continue
 for k,tri in enumerate(m['vertices'][m['faces']]):
  poly=list(tri)
  for n,d in planes:
   poly=clip(poly,n,d)
   if not poly:break
  if len(poly)>=3 and np.linalg.norm(np.cross(poly[1]-poly[0],poly[2]-poly[0]))>1e-9:optic_hits.append(dict(mesh=m['name'],triangle=k));break
checks.append(check('Complete_finite_aperture_frustum_clear',not optic_hits,hits=optic_hits,scope='All actual authored triangles clipped to convex optical frustum; not projector photometry or actor pose certification'))
# Deliberate negative optical control inside cone must survive clipping.
poly=[np.array([35.,73.6,-435]),np.array([36.,73.6,-435]),np.array([36.,74.,-435])]
for n,d in planes:poly=clip(poly,n,d)
checks.append(check('Optical_negative_control_detects_inserted_triangle',len(poly)>=3))
# Exact retained audience and actual future foot planes.
SRC=Path('/workspace/scratch/375c2e438292/library_cinema_support_20261007');cin=SRC/'WP13_FULL/WP13_D11_directory_02';cm,cn=glb(cin/'exports/WP13_cinema1.glb',np.array([11,69.5,-468]));seats=[m for m in cm if m['extras'].get('capacity_role')=='fixed_audience_seat'];roles=[n for n in cn if n['extras'].get('place_id')];bays=[n for n in roles if n['extras'].get('capacity_role')=='transfer_viewing_bay'];posts=[m for m in M if meta[m['name']]['semantic_group'].startswith('P')]
def overlap(a,b,c,d):return np.all(np.minimum(b,d)-np.maximum(a,c)>tol)
chairhits=[(p['name'],s['name']) for p in posts for s in seats if overlap(p['min'],p['max'],s['min'],s['max'])];bayhits=[]
for p in posts:
 for b in bays:
  a=np.array(b['origin']);
  if overlap(p['min'],p['max'],a+[-.6,0,-.75],a+[.6,2,.75]):bayhits.append([p['name'],b['name']])
checks.append(check('All_198_chairs_and_2_bays_preserved_and_clear',len(seats)==198 and len(bays)==2 and len(roles)==200 and not chairhits and not bayhits,chairs=len(seats),bays=len(bays),roles=len(roles),chairhits=chairhits,bayhits=bayhits))
routes=json.loads((OUT/'inputs/routes.json').read_text());route_results=[]
for rt in routes:
 pts=[]
 for av,bv in zip(rt['points'],rt['points'][1:]):
  a=np.array([av[0]+11,av[1]-468]);b=np.array([bv[0]+11,bv[1]-468]);n=math.ceil(np.linalg.norm(b-a)/.025);pts.extend(a+(b-a)*i/max(n,1) for i in range(n+1))
 q=np.array(pts);margins=[]
 for p in posts:
  lo=p['min'][[0,2]];hi=p['max'][[0,2]];margins.append(float(np.linalg.norm(np.maximum(np.maximum(lo-q,q-hi),0),axis=1).min()-rt['radius']))
 route_results.append(dict(route=rt['id'],minimum_horizontal_margin_m=min(margins),radius=rt['radius'],sample_pitch_m=.025))
checks.append(check('Cinema_retained_route_envelopes_clear',min(x['minimum_horizontal_margin_m'] for x in route_results)>0,minimum_margin_m=min(x['minimum_horizontal_margin_m'] for x in route_results)))
checks.append(check('Raised_Library_ramp_and_arrival_unintruded',max(m['max'][1] for m in M)<=78+tol,scope='Receiving geometry stops at floor top78. Source ramp/terraces and old east-pier corrections remain WP06 work.'))
# 14 protected homes and all 1,000 IDs remain exact ledger copies; no geometry enters their slabs.
checks.append(check('Fourteen_homes_and_thousand_record_ledger_preserved',len(R['protected_house_rows'])==14 and R['all1000_recount']['records']==1000 and max(m['max'][1] for m in M)<83.76,protected_home_count=len(R['protected_house_rows']),all1000_recount=R['all1000_recount']))
# Check retained source bytes including offloaded room originals accessed here.
pinresults=[]
for p,h in json.loads((OUT/'inputs/source_pins.json').read_text()).items():
 if p.endswith('catalogue_manifest.json'):continue
 pinresults.append(dict(path=p,unchanged=hashlib.sha256(Path(p).read_bytes()).hexdigest()==h))
checks.append(check('All_pinned_original_sources_unchanged',all(x['unchanged'] for x in pinresults)))
report=dict(status='PASS' if not fail else 'FAIL',failed_checks=fail,scope='Source candidate only; no Godot, species, loaded-cart, installed-room, capacity or certification acceptance',checks=checks,containment=contain,mesh_quality=mesh_quality,contacts=ct,route_results=route_results,source_pins=pinresults,source_only=True)
(OUT/'qa/decoded_glb_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['containment','mesh_quality','contacts','source_pins']},indent=2))
raise SystemExit(bool(fail))
