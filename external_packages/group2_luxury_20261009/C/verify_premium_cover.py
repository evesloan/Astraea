"""Actual exported upward cover samples around a visibly dark ceiling step."""
import pathlib,sys,json,hashlib
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));from source_paths import section,inside_polygon;from premium_frame import PremiumFrame;from glb_tools import read_glb
u=int(sys.argv[1]);row,O,native,export=section(u);c=json.loads((O/'SECTION_CONTRACT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(export)==c['export_sha256'];f=PremiumFrame(c['reservation']['proposed_floor_boundary']);_,nodes=read_glb(export);roof=[n for n in nodes if any(k in n['name'].lower() for k in ['roof','cover','ceiling','pressure'])];samples=[]
for a in [11.3,11.45,11.6,11.8]:
 for b in [1,5.2,8.5,12.3]:
  x,y,z=f.world(a,b,1.65);assert inside_polygon(x,z,f.poly);hits=[]
  for n in roof:
   for tri in n['triangles']:
    p,q,t=[n['vertices'][k] for k in tri];den=(q[2]-t[2])*(p[0]-t[0])+(t[0]-q[0])*(p[2]-t[2])
    if abs(den)<1e-10:continue
    i=((q[2]-t[2])*(x-t[0])+(t[0]-q[0])*(z-t[2]))/den;j=((t[2]-p[2])*(x-t[0])+(p[0]-t[0])*(z-t[2]))/den;k=1-i-j
    if min(i,j,k)<-1e-7:continue
    h=i*p[1]+j*q[1]+k*t[1]
    if h>y+.001:hits.append((h,n['name']))
  hit=min(hits,default=None);samples.append({'local_uv':[a,b],'eye_world_xyz':[x,y,z],'actual_upward_hit':hit,'passed':hit is not None and hit[0]<=106.4501})
data={'status':'PASS' if all(x['passed'] for x in samples) else 'FAIL','native_sha256':c['native_sha256'],'export_sha256':sha(export),'actual_upward_samples':samples,'scope':'Sixteen source-only upward samples across the dark step; pressure/cover geometry present. No pressure, structural or installed visual certification.'};p=O/'BOUNDED_CEILING_STEP_CHECK.json';p.write_text(json.dumps(data,indent=2));assert data['status']=='PASS';c.setdefault('additional_source_files',{})[p.relative_to(R).as_posix()]=sha(p);c['additional_source_files'][pathlib.Path(__file__).name]=sha(pathlib.Path(__file__));(O/'SECTION_CONTRACT.json').write_text(json.dumps(c,indent=2));print('ACTUAL_CEILING_STEP_PASS',u,len(samples))
