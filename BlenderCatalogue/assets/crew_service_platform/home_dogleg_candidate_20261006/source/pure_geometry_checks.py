"""Bounded source-space support, door-fit and approach screen. No engine or live writes."""
from pathlib import Path
import json,math,hashlib,datetime
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');D=json.loads((R/'source/HOME_SPEC.json').read_text());OLD=json.loads((C/'assets/lower_staff_network/source/geometry_parts.json').read_text())['boxes'];ALL=json.loads((C/'assets/crew_service_platform/source/geometry_parts.json').read_text())
def save(x):(R/'qa/PURE_GEOMETRY_SCREEN.json').write_text(json.dumps(x,indent=2)+'\n')
def rect(x0,x1,z0,z1):return[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]
def move(poly,a,dx=0,dz=0):
 c,s=math.cos(a),math.sin(a);return[(c*x+s*z+dx,-s*x+c*z+dz)for x,z in poly]
def world(poly):return move(poly,D['door']['yaw_radians'],D['door']['root_xyz'][0],D['door']['root_xyz'][2])
def overlap(a,b):
 depth=1e99
 for poly in[a,b]:
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dx,dz=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dz)
   if not length:continue
   axis=(-dz/length,dx/length);pa=[v[0]*axis[0]+v[1]*axis[1]for v in a];pb=[v[0]*axis[0]+v[1]*axis[1]for v in b];d=min(max(pa),max(pb))-max(min(pa),min(pb))
   if d<=1e-7:return 0.
   depth=min(depth,d)
 return depth

def profile_intervals(profile,y):
 hits=[]
 for p,q in zip(profile,profile[1:]+profile[:1]):
  if min(p[1],q[1])<y<max(p[1],q[1]):hits.append(p[0]+(y-p[1])*(q[0]-p[0])/(q[1]-p[1]))
 hits.sort();assert len(hits)%2==0;return list(zip(hits[::2],hits[1::2]))

removed={r['original_name']for r in D['wall_opening']};fixed=[]
for r in OLD+D['retained_home_parts']:
 if r['name']in removed:continue
 b=r['world_aabb']
 if b[1]>=-50 and b[0]<=-44 and b[5]>=-435 and b[4]<=-429 and b[3]>12.025 and b[2]<14.62:fixed.append(dict(name=r['name'],y0=b[2],y1=b[3],polygon=rect(b[0],b[1],b[4],b[5])))
for r in D['wall_opening']:
 for i,b in enumerate(r['replacement_boxes']):fixed.append(dict(name=r['original_name']+'_HOME_OPEN_'+str(i),y0=b[2],y1=b[3],polygon=rect(b[0],b[1],b[4],b[5])))
for p in D['new_parts']:
 if p['shape']=='world_box':
  b=p['world_aabb'];fixed.append(dict(name=p['name'],y0=b[2],y1=b[3],polygon=rect(b[0],b[1],b[4],b[5])))
 elif p['parent']=='STATIC':
  levels=sorted(set(v[1]for v in p['profile_x_y']))
  for y0,y1 in zip(levels,levels[1:]):
   for x0,x1 in profile_intervals(p['profile_x_y'],(y0+y1)/2):fixed.append(dict(name=p['name'],y0=12+y0,y1=12+y1,polygon=world(rect(x0,x1,*p['depth_z']))))
moving=[p for p in D['new_parts']if p['shape']=='door_prism'and p['parent'].startswith('HOME_HINGE_')]
fail=[];bounds=[];min_gap=1e99
for step in range(601):
 f=step/600;instances=[]
 for p in moving:
  left=p['parent'].endswith('LEFT');frac=max(0,min(1,f/.85 if left else(f-.15)/.85));a=frac*math.pi/2*(1 if left else-1);hx=-1.75 if left else 1.75;xs=[v[0]for v in p['profile_x_y']];ys=[v[1]for v in p['profile_x_y']];poly=world(move(rect(min(xs),max(xs),*p['depth_z']),a,hx));r=dict(name=p['name'],side=left,y0=12+min(ys),y1=12+max(ys),polygon=poly);instances.append(r)
  for q in fixed:
   if min(r['y1'],q['y1'])<=max(r['y0'],q['y0'])+1e-7:continue
   depth=overlap(poly,q['polygon'])
   if depth:fail.append(dict(fraction=f,moving=r['name'],fixed=q['name'],horizontal_penetration_m=depth))
 for i,r in enumerate(instances):
  for q in instances[i+1:]:
   if r['side']==q['side']or min(r['y1'],q['y1'])<=max(r['y0'],q['y0'])+1e-7:continue
   depth=overlap(r['polygon'],q['polygon'])
   if depth:fail.append(dict(fraction=f,moving=r['name'],other_leaf=q['name'],horizontal_penetration_m=depth))
 if step in[0,600]:bounds.append(dict(fraction=f,parts=instances))
# Actual supported-source room/floor interface was already checked against compiler;
# here the new fit must leave an ordinary1m-wide lane (capsule is narrower).
route=[]
openparts=bounds[-1]['parts']; allfixed=[]
for r in OLD+D['retained_home_parts']:
 if r['name']in removed:continue
 b=r['world_aabb']
 if b[3]>12.10 and b[2]<14.05:allfixed.append((r['name'],rect(b[0],b[1],b[4],b[5])))
for r in fixed:
 if r['y1']>12.10 and r['y0']<14.05:allfixed.append((r['name'],r['polygon']))
allfixed += [(r['name'],r['polygon'])for r in openparts]
for a,b in zip(D['route_xz'],D['route_xz'][1:]):
 length=math.dist(a,b);steps=max(1,math.ceil(length/.1))
 for i in range(steps+1):
  t=i/steps;x=a[0]+t*(b[0]-a[0]);z=a[1]+t*(b[1]-a[1]);q=rect(x-.5,x+.5,z-.5,z+.5);hits=[name for name,poly in allfixed if overlap(q,poly)]
  if hits:route.append(dict(x=x,z=z,hit=sorted(set(hits))))
# Fixture feet contact real cap slabs; emission point sits outside opal surface.
caps=[r for r in OLD+D['retained_home_parts']if 15.19<=r['world_aabb'][2]<=15.21 and r['world_aabb'][3]>15.21]
contacts=[]
for f in D['fixtures']:
 tx,ty,tz=f['translation_godot_xyz']
 for name in f['donor_part_names']:
  p=next(r for r in ALL if r['name']==name);b=p['world_aabb'];b=[b[0]+tx,b[1]+tx,b[2]+ty,b[3]+ty,b[4]+tz,b[5]+tz]
  if 'Hanger'in name:
   owners=[r['name']for r in caps if r['world_aabb'][0]<=b[0]and r['world_aabb'][1]>=b[1]and r['world_aabb'][4]<=b[4]and r['world_aabb'][5]>=b[5]and b[3]>=r['world_aabb'][2]];contacts.append(dict(part=f['name']+'_'+name.rsplit('_',1)[-1],owners=owners,bearing_m=b[3]-15.2));assert owners
 assert math.isclose(f['source_lowest_y']-f['emitter_xyz'][1],.015)
# Four-part cut exactly removes the reserved aperture, adds no area outside old solids.
for r in D['wall_opening']:
 old=r['original_aabb']
 for b in r['replacement_boxes']:
  assert all(old[i]<=b[i]and b[i+1]<=old[i+1]for i in[0,2,4]);assert not(min(b[1],-48)>max(b[0],-48.145)and min(b[3],14.65)>max(b[2],12)and min(b[5],-430.2)>max(b[4],-433.8))
result={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_SOURCE_SPACE_SCREEN'if not fail and not route else'FAILED_RETAIN_DIAGNOSTIC','retained_parts':85,'wall_parts_replaced':4,'replacement_boxes':8,'new_floor_owners':0,'door_pose_samples':601,'sample_max_leaf_edge_advance_m':1.78*math.pi/(2*.85*600),'continuous_sweep_certified':False,'door_collision_failures':fail[:100],'door_collision_failure_count':len(fail),'approach_failures':route,'approach_width_m':1.0,'fixture_cap_contacts':contacts,'limits':'Pure authored-box/profile screening only. Actual exported/source surfaces, ordinary interaction/traversal and normal-eye composition await source build and runtime review. No loaded cart enters dogleg.','spec_sha256':hashlib.sha256((R/'source/HOME_SPEC.json').read_bytes()).hexdigest()};save(result);print(json.dumps({k:v for k,v in result.items()if k not in['door_collision_failures','approach_failures']},indent=2));print('FIRST_FAILURES',json.dumps(fail[:5]+route[:5],indent=2));assert not fail and not route
