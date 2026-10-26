"""Source-preserving grade successor and exact three-metre kingpin fit.
No selected scene/contract is changed. All output paths are new.
"""
import bisect,hashlib,json,math,pathlib
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/grade_r001'
assert not D.exists()
plan_path=R/'Game/grand_arrivals_tram_20261026/r001/PLAN.json'
plan=json.loads(plan_path.read_text());p=plan['route_xyz']
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mul(a,s):return [x*s for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def length(a):return math.sqrt(dot(a,a))
def unit(a):return mul(a,1/length(a))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def frame(t):
 z=unit(t);x=unit([z[2],0,-z[0]]);return [x,cross(z,x),z]
# The authored datum is floor height. Original wheel centre is -.2m along
# the local up direction; preserve this normal offset on grades.
t=[unit(sub(p[min(i+1,len(p)-1)],p[max(0,i-1)])) for i in range(len(p))]
rail=[sub(q,mul(frame(ti)[1],.2)) for q,ti in zip(p,t)]
s=[0.]
for a,b in zip(rail,rail[1:]):s.append(s[-1]+math.dist(a,b))
assert all(b>a for a,b in zip(s,s[1:]))
def sample(at):
 i=max(0,min(len(s)-2,bisect.bisect_right(s,at)-1));f=(at-s[i])/(s[i+1]-s[i])
 return add(rail[i],mul(sub(rail[i+1],rail[i]),f)),unit(add(mul(t[i],1-f),mul(t[i+1],f)))
def euler_yxz(cols):
 # Godot default YXZ: columns of R_y(yaw) R_x(pitch) R_z(roll).
 x,y,z=cols;pitch=math.asin(max(-1,min(1,-z[1])))
 return [pitch,math.atan2(z[0],z[2]),math.atan2(x[1],y[1])]
def fit(at):
 lo=1.5;hi=lo
 while math.dist(sample(at-hi)[0],sample(at+hi)[0])<3 and hi<8:hi+=.025
 assert hi<8,('Cannot fit original kingpin chord',at)
 for _ in range(36):
  h=(lo+hi)/2
  if math.dist(sample(at-h)[0],sample(at+h)[0])<3:lo=h
  else:hi=h
 h=(lo+hi)/2;a,ta=sample(at-h);b,tb=sample(at+h)
 body=frame(sub(b,a));origin=add(mul(add(a,b),.5),mul(body[1],.2));e=euler_yxz(body)
 trucks=[];errors=[]
 for q,tangent,z in [(a,ta,-1.5),(b,tb,1.5)]:
  local=[dot(sub(q,origin),axis) for axis in body]
  errors.append(math.dist(local,[0,-.2,z]))
  cols=[[dot(c,axis) for axis in body] for c in frame(tangent)]
  trucks.append(euler_yxz(cols))
 row=[at,origin[0],origin[2],e[1],0,trucks[0][1],at-h,0,trucks[1][1],at+h,.25,origin[1],e[0],trucks[0][0],trucks[0][2],trucks[1][0],trucks[1][2]]
 return row,max(errors),abs(length(sub(a,b))-3)
knots=[4+i*.25 for i in range(math.floor((s[-1]-8)/.25)+1)]+[s[-1]-4]
rows=[];errors=[]
for at in knots:
 row,err,chord=fit(at);rows.append(row);errors.append([err,chord])
assert max(max(e) for e in errors)<1e-7
D.mkdir(parents=True)
(D/'POSES.json').write_bytes((json.dumps(rows,separators=(',',':'))+'\n').encode())
base_path=R/'Game/scripts/group4_tram_source_actuator.gd';base=base_path.read_text(encoding='utf-8')
old='assert(vehicle.global_position.distance_to(Vector3(initial_pose[1],56.1,initial_pose[2]))<.001,"Prebound initial cursor must match the newly assembled physical car before any pose write")'
new='assert(vehicle.global_transform.is_equal_approx(grade_body_pose(initial_pose)),"Prebound graded cursor must match the assembled car position AND orientation before any pose write")'
assert base.count(old)==1;base=base.replace(old,new)
base=base.replace('for i in [3,5,8]:','for i in [3,5,8,12,13,14,15,16]:')
old='var p:Array=pose_at(at);vehicle.global_position=Vector3(p[1],56.1,p[2]);vehicle.global_rotation=Vector3(0,p[3],0)'
assert base.count(old)==1;base=base.replace(old,'var p:Array=pose_at(at);vehicle.global_transform=grade_body_pose(p)')
old='var column:=4+i*3;bogies[i].position=Vector3(p[column],-.2,-1.5 if i==0 else 1.5);bogies[i].rotation=Vector3(0,p[column+1],0)'
assert base.count(old)==1;base=base.replace(old,'var column:=4+i*3;bogies[i].position=Vector3(p[column],-.2,-1.5 if i==0 else 1.5);bogies[i].rotation=Vector3(p[13+i*2],p[column+1],p[14+i*2])')
base+='\nfunc grade_body_pose(p:Array)->Transform3D:\n assert(p.size()==17,"Exact graded pose schema required")\n return Transform3D(Basis.from_euler(Vector3(p[12],p[3],0)),Vector3(p[1],p[11],p[2]))\n'
# The inherited static factory would otherwise instantiate the old planar class.
base=base.replace('load("res://scripts/group4_tram_source_actuator.gd").new()', 'load("res://grand_arrivals_tram_20261026/grade_r001/actuator.gd").new()')
base=base.replace('const DATA:="res://data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json"','const DATA:="res://grand_arrivals_tram_20261026/grade_r001/MOTOR_PLAN.json"')
(D/'actuator.gd').write_bytes(base.encode())
loaded_path=R/'Game/scripts/group4_loaded_tram_actuator.gd';loaded=loaded_path.read_text()
loaded=loaded.replace('res://scripts/group4_tram_source_actuator.gd','res://grand_arrivals_tram_20261026/grade_r001/actuator.gd').replace('res://scripts/group4_loaded_tram_actuator.gd','res://grand_arrivals_tram_20261026/grade_r001/loaded_actuator.gd')
loaded=loaded.replace('if not p.active and not candidate_only:return null','if not candidate_only:return null # Unselected graded route cannot be attached by production callers.')
(D/'loaded_actuator.gd').write_bytes(loaded.encode())
motor=json.loads((R/'Game/data/architecture/GROUP4_TRAVEL_SOURCE_CANDIDATE.json').read_text());motor.update(active=False,whole_group_complete=False,pose_file='res://grand_arrivals_tram_20261026/grade_r001/POSES.json',pose_sha256=hashlib.sha256((D/'POSES.json').read_bytes()).hexdigest(),source_route_total_m=s[-1],safe_body_cursor_range_m=[rows[0][0],rows[-1][0]],stops=[],motion_scope='Unselected grade-capable successor. Original restraints and departure guards retained; route/hardware admission held.')
(D/'MOTOR_PLAN.json').write_bytes((json.dumps(motor,indent=2)+'\n').encode())
receipt={'selected':False,'scope':'Unselected authored 3D pose/controller successor; exact kingpin fit only, not hardware clearance, wheel contact under interpolation, rider carry or installed route acceptance','source_pins':{p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [plan_path,base_path,loaded_path]},'poses':len(rows),'safe_range':[rows[0][0],rows[-1][0]],'max_kingpin_error_m':max(e[0] for e in errors),'max_chord_error_m':max(e[1] for e in errors),'max_body_pitch_rad':max(abs(r[12]) for r in rows),'max_truck_pitch_rad':max(abs(r[i]) for r in rows for i in [13,15]),'max_truck_roll_rad':max(abs(r[i]) for r in rows for i in [14,16]),'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir()}}
(D/'RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt,indent=2))
