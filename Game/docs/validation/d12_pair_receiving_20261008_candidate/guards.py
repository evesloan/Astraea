"""Pure source-driven geometry proposal. No native authoring or engine execution."""
from pathlib import Path
import ast,json,struct,hashlib,sys,math
import numpy as np
O=Path(__file__).resolve().parent;S=O.parent
sys.path.insert(0,str(S/'botanical_receiving_court_build_20261007/python_deps'))
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
ns={'np':np,'json':json,'struct':struct}
for path,names in [(S/'lounge_entry_successors_20261008/patch_runtime.py',{'read','acc','meshes'}),(S/'lounge_entry_successors_20261008/verify_geometry.py',{'clip','box_hits'})]:
 exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),ns)
solids=[];contacts=[];results=[]
faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def cuboid(name,lo,hi,support):
 a,b,c=lo;d,e,f=hi
 row={'name':name,'vertices':[[a,b,c],[d,b,c],[d,b,f],[a,b,f],[a,e,c],[d,e,c],[d,e,f],[a,e,f]],'faces':faces,'support':support,'kind':'box','lo':lo,'hi':hi};solids.append(row);return row

def xyz_bounds(v):v=np.array(v);return v.min(0).tolist(),v.max(0).tolist()

def inner_z(ms,x,y,negative):
 # Actual triangle/ray intersection on retained jamb. Cast +Z; choose inside-facing extreme.
 vv=[]
 for n,v,ix in ms:
  for tri in v[ix]:
   a,b,c=tri;d=np.array([0.,0.,1.]);e1=b-a;e2=c-a;h=np.cross(d,e2);det=np.dot(e1,h)
   if abs(det)<1e-10:continue
   s=np.array([x,y,0.])-a;u=np.dot(s,h)/det;q=np.cross(s,e1);w=np.dot(d,q)/det;t=np.dot(e2,q)/det
   if u>=-1e-9 and w>=-1e-9 and u+w<=1+1e-9:vv.append(float(t))
 assert vv,(x,y)
 return max(vv) if negative else min(vv)

adds=json.loads((O/'FLOOR_OWNER_ADDITIONS.json').read_text());current=json.loads((O/'isolated/Game/data/generated/structural_meshes.json').read_text()); floor=unary_union([Polygon(t) for r in current['regions'] if r['floor_y']==78 for t in r['triangles']])
for key,side in [('D12_directory_07',-1),('D12_directory_08',1)]:
 glb=S/'lounge_entry_successors_20261008'/key/'exports'/f'{key}_entry_successor.glb';ms=ns['meshes'](*ns['read'](glb.read_bytes()));start=len(solids);jamb_contacts=[]
 for neg,z in [(True,213.85),(False,218.15)]:
  tag=key+('_south' if neg else '_north');jamb=[r for r in ms if r[0]==key+('__portal_jamb-4' if neg else '__portal_jamb4')];assert len(jamb)==1
  # X=8.65 is beyond retained 0.09m nose bevel, so a full 0.1m width has equal interface.
  face=inner_z(jamb,side*8.65,78.2,neg);endz=face+(.2 if neg else -.2)
  # Branch stations and wing terminal station. All post feet remain on the candidate substrate.
  points=[(side*x,z) for x in [4.1,5.6,7.1,8.65]]+[(side*8.65,endz)]
  names=[]
  for j,(x,zz) in enumerate(points):
   foot=cuboid(f'{tag}_Foot{j}',[x-.1,78,zz-.1],[x+.1,78.04,zz+.1],key+'_branch_or_room_floor')
   post=cuboid(f'{tag}_Post{j}',[x-.05,78.04,zz-.05],[x+.05,79.02,zz+.05],foot['name']);names.append(post['name'])
   cuboid(f'{tag}_Cap{j}',[x-.05,79.02,zz-.05],[x+.05,79.10,zz+.05],post['name'])
  # Flush termination on the unchanged route edge; no 5cm slit beyond the first post.
  xx=sorted([side*4.,side*4.05]);cuboid(tag+'_RouteEndClosure',[xx[0],78.04,z-.05],[xx[1],79.10,z+.05],tag+'_Foot0 & '+tag+'_Post0')
  for j,(a,b) in enumerate(zip(points,points[1:])):
   axis=0 if a[1]==b[1] else 2;fixed=2 if axis==0 else 0;aa=sorted([a[0] if axis==0 else a[1], b[0] if axis==0 else b[1]]);fix=a[1] if axis==0 else a[0]
   for part,y0,y1,w,trim in [('Curb',78,78.04,.10,.10),('Panel',78.04,79.02,.05,.05),('Rail',79.02,79.10,.10,.05)]:
    lo=[0,y0,0];hi=[0,y1,0];lo[axis]=aa[0]+trim;hi[axis]=aa[1]-trim;lo[fixed]=fix-w/2;hi[fixed]=fix+w/2
    cuboid(f'{tag}_{part}{j}',lo,hi, names[j]+' & '+names[j+1] if part!='Curb' else key+'_floor')
  # Closure piece exactly follows the actual lower jamb bevel; no collision deletion or source edit.
  # A single solid infill spans floor to top rail and butts the terminal post outer face.
  ys=sorted({78.,79.10,*[float(y) for y in jamb[0][1][:,1] if 78<y<79.1]})
  profile=[(y,inner_z(jamb,side*8.65,y,neg)) for y in ys]
  # Confirm the cross section is invariant across the full terminal width.
  for x in [side*8.65-.05,side*8.65+.05]:
   assert max(abs(inner_z(jamb,x,y,neg)-zz) for y,zz in profile)<1e-7
  terminal=endz-(.05 if neg else -.05)
  footedge=endz-(.1 if neg else -.1)
  poly=[(78.,footedge),(78.04,footedge),(78.04,terminal),(79.10,terminal)]+list(reversed(profile))
  verts=[[x,y,zz] for x in [side*8.65-.05,side*8.65+.05] for y,zz in poly];n=len(poly)
  fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
  solids.append({'name':tag+'_SourceProfiledTerminal','vertices':verts,'faces':fs,'support':key+'_room_floor and '+names[-1],'kind':'jamb_profile','jamb':jamb[0][0],'profile_yz':profile})
  jamb_contacts.append({'jamb':jamb[0][0],'world_x_span':sorted([side*8.65-.05,side*8.65+.05]),'source_profile_yz':profile,'maximum_slice_disagreement_m':0.,'method':'Triangle ray intersection, exact fitted terminal; no source geometry changes'})
 # Tiny unsupported numeric errors are measured, never shifted away.
 checks=[];clearbox=box(min(side*4,side*16),214,max(side*4,side*16),218)
 for row in solids[start:]:
  lo,hi=xyz_bounds(row['vertices']);plan=Polygon([(v[0],v[2]) for v in row['vertices']]).convex_hull
  unsupported=plan.difference(floor).area;clear=plan.intersection(clearbox).area
  assert unsupported<1e-8,(row['name'],unsupported);assert clear<1e-10,(row['name'],clear)
  # Interior-shrunk box checks for ordinary pieces; fitted interface is validated by slice profiles.
  hits=[]
  if row['kind']=='box':
   hits=ns['box_hits'](ms,[a+1e-6 for a in lo],[b-1e-6 for b in hi]);assert not hits,(row['name'],hits)
  checks.append({'name':row['name'],'unsupported_plan_m2':unsupported,'clear_strip_intrusion_m2':clear,'source_solid_interior_hits':hits,'floor_contact':abs(lo[1]-78)<1e-8})
 results.append({'section':key,'jamb_interfaces':jamb_contacts,'solids':checks,'clear_strip':[214,218],'branch_guard_foot_extents_z':[[213.75,213.95],[218.05,218.25]],'guard_top_y':79.10,'floor_surface_y':78,'minimum_clear_strip_margin_m':.05})
json.dump({'schema':1,'asset_id':'AST-RCV-D12-PAIR-001','world_frame':'Godot XYZ metres; Blender=(X,-Z,Y)','status':'UNBUILT proposal','solids':solids},open(O/'GUARD_SOLIDS.json','w'),indent=2)
json.dump({'sections':results,'solid_count':len(solids),'native_or_engine_run':False,'engineering_status':'Geometry/contact proposal only; fixings, loads and slab bearing not certified'},open(O/'GUARD_SOURCE_CHECKS.json','w'),indent=2)
print('guard solids',len(solids),'floor coverage and source-interior/4m clearance passed')
