from pathlib import Path
import json,hashlib,math,numpy as np
R=Path(__file__).resolve().parent;E=R.parent/'local_light_refinement006/FIXTURE_GEOMETRY_EXTRACT.json';d=json.loads(E.read_text());old=next(x for x in d['objects']if x['name'].endswith('_opal_lens'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();parts=[]
def add(name,v,f,material):
 v=np.array(v,dtype=np.float32).astype(float);f=[list(x)for x in f]
 volume=sum(np.dot(v[q[0]],np.cross(v[q[i]],v[q[i+1]]))/6 for q in f for i in range(1,len(q)-1))
 if volume<0:f=[x[::-1]for x in f];volume=-volume
 assert volume>0
 edges={}
 for face in f:
  for i,a in enumerate(face):
   b=face[(i+1)%len(face)];key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
 assert all(len(x)==2 and x[0]==x[1][::-1]for x in edges.values())
 parts.append({'name':name,'vertices_world':v.tolist(),'faces':f,'material_source':material,'bounds_world':[v.min(0).tolist(),v.max(0).tolist()],'closed_volume_m3':volume})
def prism(name,poly,lo,hi,mat):
 n=len(poly);v=[[x,y,z]for y in[lo,hi]for x,z in poly];f=[list(range(n)),list(range(2*n-1,n-1,-1))]+[[n+i,n+(i+1)%n,(i+1)%n,i]for i in range(n)];add(name,v,f,mat)
lo=min(p[1]for p in old['vertices_world']);hi=max(p[1]for p in old['vertices_world']);p=old['vertices_world'][:8];lx=-70.5;rx=-68.5;bz=-138.38;fz=-138.22
prism('CA8_opal_surround_left',[[p[i][0],p[i][2]]for i in[0]]+[[lx,p[0][2]],[lx,p[5][2]]]+[[p[i][0],p[i][2]]for i in[5,6,7]],lo,hi,'retained_opal')
prism('CA8_opal_surround_right',[[rx,p[1][2]]]+[[p[i][0],p[i][2]]for i in[1,2,3,4]]+[[rx,p[4][2]]],lo,hi,'retained_opal')
prism('CA8_opal_surround_rear',[[lx,p[0][2]],[rx,p[0][2]],[rx,bz],[lx,bz]],lo,hi,'retained_opal')
prism('CA8_opal_surround_front',[[lx,fz],[rx,fz],[rx,p[4][2]],[lx,p[4][2]]],lo,hi,'retained_opal')
a=np.array([0,-math.sin(math.radians(40)),-math.cos(math.radians(40))]);u=np.array([1,0,0]);v=np.array([0,math.cos(math.radians(40)),-math.sin(math.radians(40))]);origin=np.array([-69.5,73.75,-138.3]);center=origin+np.array([0,.005/(-a[1]),0]);width=1.96;height=.05;thickness=.004
# Outward emitting plane is the +normal face; 5 mm nominal free-air light offset.
vertices=[center+u*x+v*y+a*z for z in[-thickness,0]for y in[-height/2,height/2]for x in[-width/2,width/2]]
faces=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]];add('CA8_aimed_opal_lens',vertices,faces,'retained_opal')
# Two simple end cheeks carry the small angled lens back to the retained flat surround.
section=[(float(center[1]-v[1]*height/2+a[1]*(-thickness)),float(center[2]-v[2]*height/2+a[2]*(-thickness))),(float(center[1]-v[1]*height/2),float(center[2]-v[2]*height/2)),(float(center[1]+v[1]*height/2),float(center[2]+v[2]*height/2)),(float(center[1]+v[1]*height/2+a[1]*(-thickness)),float(center[2]+v[2]*height/2+a[2]*(-thickness)))]
# Convex hull in YZ additionally reaches original surround thickness at the hole sides.
def hull(points):
 pts=sorted(set(points));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);lower=[];upper=[]
 for x in pts:
  while len(lower)>=2 and cross(lower[-2],lower[-1],x)<=0:lower.pop()
  lower.append(x)
 for x in reversed(pts):
  while len(upper)>=2 and cross(upper[-2],upper[-1],x)<=0:upper.pop()
  upper.append(x)
 return lower[:-1]+upper[:-1]
section=hull(section+[(lo,bz),(hi,bz),(lo,fz),(hi,fz)])
for name,x0,x1 in [('CA8_metal_cheek_left',lx,-70.48),('CA8_metal_cheek_right',-68.52,rx)]:
 n=len(section);vv=[[x,y,z]for x in[x0,x1]for y,z in section];ff=[list(range(n)),list(range(2*n-1,n-1,-1))]+[[n+i,n+(i+1)%n,(i+1)%n,i]for i in range(n)];add(name,vv,ff,'retained_frame_metal')
allv=np.concatenate([np.array(x['vertices_world'])for x in parts]);frame=next(x for x in d['objects']if x['name'].endswith('_hollow_frame'));bounds=np.array(frame['vertices_world']);assert np.all(allv.min(0)>=bounds.min(0)-1e-8)and np.all(allv.max(0)<=bounds.max(0)+1e-8)
result={'status':'SOURCE_ONLY_BOUNDED_INSERT_PROPOSAL_NOT_BUILT','retained_geometry_extract':str(E),'retained_geometry_sha256':sha(E),'source_fixture_objects_preserved':[x['name']for x in d['objects']if x['name']!=old['name']],'replace_exact_one_in_new_derivative':old['name'],'original_flat_lens_outer_outline_and_bearing_retained':True,'new_central_aperture_xz':[[lx,bz],[rx,bz],[rx,fz],[lx,fz]],'source_light_position_unchanged':origin.tolist(),'aim_world':a.tolist(),'full_cone_degrees':75,'range_m':7.9,'energy':.8,'new_parts':parts,'aggregate_bounds_world':[allv.min(0).tolist(),allv.max(0).tolist()],'mesh_count':len(parts),'triangles':sum(len(f)-2 for x in parts for f in x['faces']),'physical_principle':'Small asymmetric lens aligned to actual beam inside retained mounted frame. Four surrounds preserve original outer outline; two end cheeks support lens. No gimbal, fastener or manufacturing internals. Original file is immutable.','pending':['Exact beam paths with revised lens and surround including float32 fit/contact','Editable new-source build and independent reopen','Native actual scene picture before adoption; no live replacement authorized by this file']}
(R/'SOURCE_INSERT_GEOMETRY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['new_parts','pending']}));print('SHA',sha(R/'SOURCE_INSERT_GEOMETRY.json'))
