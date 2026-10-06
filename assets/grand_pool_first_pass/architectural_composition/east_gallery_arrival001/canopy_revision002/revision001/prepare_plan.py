from pathlib import Path
import json,math,struct,copy,hashlib
B=Path(__file__).resolve().parent;S=B.parents[1];OLD=S/'pool-opposite-gallery-proposal001/combined_source002/qa/BUILD_EVALUATED_CORE.json';plan=json.loads(OLD.read_text());parts={r['name']:r for r in plan['parts']};before=copy.deepcopy(parts)
f32=lambda x:struct.unpack('<f',struct.pack('<f',float(x)))[0]
def plane(x,z):return 56.02+.17*(x+10.85)
def strip(name,role,low,high,support):
 zs=[-454+i*9/24 for i in range(25)];v=[]
 for z in zs:
  front=-10.85-.30*math.sin(math.pi*(z+454)/9);rear=-8.2
  v.extend([[front,plane(front,z)+low,z],[rear,plane(rear,z)+low,z],[rear,plane(rear,z)+high,z],[front,plane(front,z)+high,z]])
 faces=[[3,2,1,0],[96,97,98,99]]
 for j in range(24):
  for i in range(4):a=j*4+i;b=j*4+(i+1)%4;c=(j+1)*4+(i+1)%4;d=(j+1)*4+i;faces.extend([[a,b,c],[a,c,d]])
 return dict(name=name,group='bay',material_role=role,vertices_xyz=v,faces=faces,support=support,parent_design_id='AST-AQU-016',collision='concave_static_surface',reservation='upper_east_gallery_rest_bay',semantic='Complete full-depth canopy layer; shallow pitched soffit with continuous bearing',grain_axis_xyz=[1,0,0])
parts['EAST_Bay_WarmRearCanopy']=strip('EAST_Bay_WarmRearCanopy','warm_walnut',0,.065,['EAST_Bay_ForeSweptReturn','EAST_Bay_AftSweptReturn','EAST_Bay_RearHeader'])
parts['EAST_Bay_PaleFrontCanopy']=strip('EAST_Bay_PaleFrontCanopy','ivory_enamel',.065,.28,['EAST_Bay_WarmRearCanopy','GP_EastWall.002'])
changed=set(['EAST_Bay_WarmRearCanopy','EAST_Bay_PaleFrontCanopy'])
for name in ['EAST_Bay_ForeSweptReturn','EAST_Bay_AftSweptReturn']:
 row=parts[name]
 for v in row['vertices_xyz']:
  if abs(v[1]-55.95)<1e-4:v[1]=plane(v[0],v[2])
 changed.add(name)
# The full rear header closes from the unchanged clay back into the same plane.
back=parts['EAST_Bay_CurvedClayBack'];count=len(back['vertices_xyz'])//2;poly=[[v[0],v[2]]for v in back['vertices_xyz'][:count]]
def solid(name,role,poly,bottom,top,support):
 n=len(poly);v=[[x,bottom(x,z),z]for x,z in poly]+[[x,top(x,z),z]for x,z in poly];faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
 return dict(name=name,group='bay',material_role=role,vertices_xyz=v,faces=faces,support=support,parent_design_id='AST-AQU-016',collision='concave_static_surface',reservation='upper_east_gallery_rest_bay',semantic='Fitted continuous physical mounting connection',grain_axis_xyz=[1,0,0])
parts['EAST_Bay_RearHeader']=solid('EAST_Bay_RearHeader','retail_terracotta_enamel',poly,lambda x,z:f32(56.4),plane,['EAST_Bay_CurvedClayBack','GP_EastWall.002'])
# Keep fixture plan coordinates and complete ring construction. Real Y and axis
# follow the new source underside, never a guessed marker or ranking offset.
fixtures=[]
for i in range(2):
 fixture=copy.deepcopy(plan['fixture_reservations'][i]);cx,old_y,cz=fixture['position_xyz'];N=20;rad=.085;inner=.061
 def loft(name,role,rings,support):
  n=len(rings[0]);v=sum(rings,[]);faces=[list(range(n-1,-1,-1)),list(range((len(rings)-1)*n,len(rings)*n))]
  for j in range(len(rings)-1):
   for k in range(n):a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k;faces.extend([[a,b,c],[a,c,d]])
  return dict(name=name,group='fixtures',material_role=role,vertices_xyz=v,faces=faces,support=[support],parent_design_id='AST-AQU-016',collision='concave_static_surface',reservation='upper_east_gallery_rest_bay',semantic='Actual housed fixture fitted into continuous soffit')
 def ring(radius,dy):return [[cx+radius*math.cos(2*math.pi*k/N),plane(cx+radius*math.cos(2*math.pi*k/N),cz+radius*math.sin(2*math.pi*k/N))+dy,cz+radius*math.sin(2*math.pi*k/N)]for k in range(N)]
 name=f'EAST_Bay_FixtureCup_{i}';parts[name]=loft(name,'champagne_metal',[ring(rad,0),ring(rad,-.10),ring(inner,-.10),ring(inner,-.028)],'EAST_Bay_WarmRearCanopy');changed.add(name)
 name=f'EAST_Bay_OpalLens_{i}';parts[name]=loft(name,'lens',[ring(inner,-.067),ring(inner,-.055)],f'EAST_Bay_FixtureCup_{i}');parts[name]['collision']='visual_lens_no_contact';parts[name]['cast_shadow']=False;changed.add(name)
 norm=math.sqrt(1+.17**2);fixture.update(position_xyz=[cx,plane(cx,cz)-.095,cz],direction_xyz=[.17/norm,-1/norm,0],source_axis_method='Outward normal of actual planar mounted lens/soffit',candidate_only=True,range_energy_aim='Two sources retained; actual receiver throw/native balance checked after source geometry')
 fixtures.append(fixture)
# A common short rail makes both screen mounts visibly one assembly.
names=['EAST_Display_Hanger_Fore','EAST_Display_Hanger_Aft'];centres=[]
for name in names:
 v=parts[name]['vertices_xyz'];centres.append((sum(p[0]for p in v)/len(v),sum(p[2]for p in v)/len(v)))
(a,b)=centres;dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);ux,uz=dx/length,dz/length;nx,nz=-uz,ux
start=(a[0]-ux*.08,a[1]-uz*.08);end=(b[0]+ux*.08,b[1]+uz*.08);w=.055
railpoly=[(start[0]+nx*w,start[1]+nz*w),(end[0]+nx*w,end[1]+nz*w),(end[0]-nx*w,end[1]-nz*w),(start[0]-nx*w,start[1]-nz*w)]
parts['EAST_Display_CommonMountRail']=solid('EAST_Display_CommonMountRail','champagne_metal',railpoly,lambda x,z:plane(x,z)-.06,plane,['EAST_Bay_WarmRearCanopy'])
for name,(cx,cz) in zip(names,centres):
 poly=[(cx-.03,cz-.03),(cx+.03,cz-.03),(cx+.03,cz+.03),(cx-.03,cz+.03)]
 parts[name]=solid(name,'champagne_metal',poly,lambda x,z:f32(54.72),lambda x,z:plane(x,z)-.06,['EAST_Display_CommonMountRail']);changed.add(name)
new_names=sorted(set(parts)-set(before))
# Old evaluated measurements do not describe the changed meshes. Recompute them
# from new actual source in the build/reopen; preserve unchanged records exactly.
geometry_fields=['evaluated_triangles','signed_volume_m3','minimum_triangle_area_m2','minimum_uv_area','uv_loops','local_vertices_blender','matrix_world_blender','material_indices','material_states','source_transform']
for name in changed|set(new_names):
 row=parts[name]
 for k in geometry_fields:row.pop(k,None)
 row['vertices_xyz']=[[f32(x)for x in v]for v in row['vertices_xyz']]
plan['parts']=[parts[r['name']]for r in plan['parts']]+[parts[x]for x in new_names];plan['fixture_reservations']=fixtures;plan['status']='CANOPY_COMPOSITION_CORRECTION_PURE_FIT_PENDING';plan['correction']={'changed_existing_parts':sorted(changed),'new_parts':new_names,'unchanged_existing_parts':sorted(set(before)-changed),'source_preimage':str(OLD),'source_preimage_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'lower_programme_unchanged':True,'no_optional_pier_facing':True,'front_soffit_min_y':min(v[1]for v in parts['EAST_Bay_WarmRearCanopy']['vertices_xyz']),'fixture_count':2,'screen_pose_content_unchanged':True}
plan['input_sha256'][str(S/'pool-east-gallery-resume002/REFERENCE_REVIEW.json')]=hashlib.sha256((S/'pool-east-gallery-resume002/REFERENCE_REVIEW.json').read_bytes()).hexdigest()
(B/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan['correction'],indent=2))
# Reuse the tested source/floor/route geometry predicates, with only the explicit
# scratch path and output allowlist changed. No predicate/tolerance changes.
s=(S/'pool-opposite-gallery-proposal001/source_blockin001/review_core.py').read_text();s=s.replace('P=S.parent;C=','P=Path("/workspace/scratch/375c2e438292/pool-opposite-gallery-proposal001");C=');(B/'review_core.py').write_text(s)
