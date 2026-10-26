"""Additive, unselected five-stop grade binding; never rewrites predecessors."""
import hashlib,json,math,pathlib
R=pathlib.Path(__file__).resolve().parents[2]
D=R/'Game/grand_arrivals_tram_20261026/integration_r001'
assert not D.exists()
P='res://grand_arrivals_tram_20261026/integration_r001/'
oldroot=R/'Game/aquatic_tram_interior_20261026/integration'
pins={}
def read(path):
 p=R/path;pins[path]=hashlib.sha256(p.read_bytes()).hexdigest();return p.read_text(encoding='utf-8')
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
kernel=read('recovery/grand_arrivals_embarkation_20261026/author_grade_kernel_r007.py')
kernel=kernel[:kernel.index('knots=')].replace('assert not D.exists()','')
ns={'__file__':str(R/'recovery/grand_arrivals_embarkation_20261026/author_grade_kernel_r007.py')};exec(kernel,ns)
fit=ns['fit']
plan=json.loads(read('Game/grand_arrivals_tram_20261026/grade_r007/MOTOR_PLAN.json'))
rows=json.loads(read('Game/grand_arrivals_tram_20261026/grade_r007/POSES.json'))
section=json.loads(read('Game/aquatic_tram_interior_20261026/r009/PLAN.json'))
stops=[]
for original in section['stops']:
 st=original.copy();target=st['world_xyz'] if st['station']!='FORWARD' else [-12.6,.365,-449]
 at=min(rows,key=lambda r:math.dist([r[1],r[11],r[2]],target))[0]
 if st['station']=='FORWARD':at=6.
 else:
  lo,hi=at-.5,at+.5
  def err(at):
   r=fit(at)[0];return math.dist([r[1],r[11],r[2]],target)
  for _ in range(55):
   a=lo+(hi-lo)/3;b=hi-(hi-lo)/3
   if err(a)<err(b):hi=b
   else:lo=a
  at=(lo+hi)/2
 row=fit(at)[0];assert math.dist([row[1],row[11],row[2]],target)<1e-7
 if st['station']!='FORWARD':assert abs(math.atan2(math.sin(row[3]-st['body_yaw']-math.pi),math.cos(row[3]-st['body_yaw']-math.pi)))<1e-7
 st.update(distance_m=at,world_xyz=[row[1],row[11],row[2]],body_yaw=row[3],body_pitch=row[12])
 stops.append(st)
 if not any(abs(r[0]-at)<1e-9 for r in rows):rows.append(row)
rows.sort(key=lambda r:r[0]);D.mkdir()
def write(name,s): (D/name).write_text(s,encoding='utf-8',newline='\n')
def js(name,x):write(name,json.dumps(x,indent=2)+'\n')
write('POSES.json',json.dumps(rows,separators=(',',':'))+'\n')
plan['stops']=stops;plan['pose_file']=P+'POSES.json';plan['pose_sha256']=hashlib.sha256((D/'POSES.json').read_bytes()).hexdigest()
plan['pose_columns']+=['body_y','body_pitch','rear_pitch','rear_roll','front_pitch','front_roll']
plan['source_route_points_xz']=[[r[0],r[2]] for r in ns['p']]
plan['central_exact_pose']=next(fit(s['distance_m'])[0] for s in stops if s['station']=='CENTRAL')
plan['group1_adoption_scope']='Original station identities retained; lower FORWARD source candidate, not installed admission'
js('MOTOR_PLAN.json',plan)
section['stops']=stops;section['safe_body_cursor_range_m']=plan['safe_body_cursor_range_m']
section['active']=False;section['central']['new_pose']=plan['central_exact_pose'];js('SECTION_PLAN.json',section)
assembly=read('Game/aquatic_tram_interior_20261026/integration/assembly.gd')
assembly=replace(assembly,'var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://aquatic_tram_interior_20261026/r009/PLAN.json"))','var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("'+P+'SECTION_PLAN.json"))')
assembly=replace(assembly,'initial_station:String="CENTRAL"','initial_station:String="FORWARD"')
assembly=replace(assembly,'Transform3D(Basis(Vector3.UP,initial.body_yaw),Vector3(initial.world_xyz[0],56.1,initial.world_xyz[2]))','Transform3D(Basis.from_euler(Vector3(initial.body_pitch,initial.body_yaw,0)),Vector3(initial.world_xyz[0],initial.world_xyz[1],initial.world_xyz[2]))')
assembly=assembly.replace('res://aquatic_tram_interior_20261026/integration/boarding.gd',P+'boarding.gd').replace('res://aquatic_tram_interior_20261026/integration/motor.gd',P+'motor.gd')
assembly=replace(assembly,'\t\tn.add_child(bridge)','\t\tif st.label=="FORWARD":bridge.position=Vector3(-14.8,.365,-449);bridge.rotation.y=0\n\t\tn.add_child(bridge)')
assembly=replace(assembly,'\treturn assembly','\tvar crossing:Node3D=load("res://grand_arrivals_tram_20261026/crossing_r002/controller.gd").new()\n\tcrossing.name="ForwardGroundCrossing";assembly.add_child(crossing)\n\tassembly.set_meta("lower_arrivals_integration_candidate",true)\n\treturn assembly')
write('assembly.gd',assembly)
boarding=read('Game/aquatic_tram_interior_20261026/integration/boarding.gd')
boarding=boarding.replace('res://aquatic_tram_interior_20261026/integration/boarding.gd',P+'boarding.gd').replace('res://aquatic_tram_interior_20261026/r009/PLAN.json',P+'SECTION_PLAN.json')
boarding=replace(boarding,'\tn.set_meta("integration_boarding_admitted",false)','\t\t# Reverse travel heading preserves the same world-side station portal.\n\t\tmount.vehicle_door_side="STARBOARD" if mount.vehicle_door_side=="PORT" else "PORT"\n\t\tif mount.station=="FORWARD":mount.origin=[-14.8,.365,-449];mount.yaw=0;mount.vehicle_door_side="STARBOARD"\n\tn.set_meta("integration_boarding_admitted",false)')
boarding=replace(boarding,'\tvar policies:Dictionary={};','\tvar old_forward:=Transform3D(Basis(Vector3.UP,PI),Vector3(-3.4,56.1,-432))\n\tvar new_forward:=Transform3D(Basis.IDENTITY,Vector3(-14.8,.365,-449))\n\tvar forward_count:=0\n\tvar policies:Dictionary={};')
boarding=replace(boarding,'\t\tif policies[str(mesh.name)]!=','\t\telif str(mesh.name).begins_with("FORWARD_"):\n\t\t\tmesh.global_transform=base.global_transform*new_forward*old_forward.affine_inverse()*base.global_transform.affine_inverse()*mesh.global_transform;forward_count+=1\n\t\tif policies[str(mesh.name)]!=')
boarding=replace(boarding,'assert(count==policies.size() and central_count==8 and fore_count==8 and aft_count==8)','assert(count==policies.size() and central_count==8 and fore_count==8 and aft_count==8 and forward_count==8)')
write('boarding.gd',boarding)
motor='''extends "res://grand_arrivals_tram_20261026/crossing_r002/loaded_actuator.gd"
# A fresh assembly only: the original six portal frames are converted exactly
# once by inherited _ready. No second motor, preconverted clone or bypass.
static func attach_section(parent:Node3D,body:AnimatableBody3D,boarding:Node3D,cart_restraint:Node3D)->Node3D:
 assert(parent.get_meta("lower_arrivals_integration_candidate",false))
 assert(not body.has_meta("group4_source_actuator") and not body.has_meta("exact_original_portal_contact_components"))
 var originals:=0
 for col:CollisionShape3D in body.find_children("*","CollisionShape3D",false,false):
  if col.shape is ConcavePolygonShape3D:originals+=1
 assert(originals==6,"Fresh original boarding portals must precede the one motor")
 var n:Node3D=load("PREFIXmotor.gd").new()
 n.name="Group4LoadedSourceTravelActuator"
 n.plan=JSON.parse_string(FileAccess.get_file_as_string("PREFIXMOTOR_PLAN.json"))
 n.vehicle=body;n.safety=boarding;n.restraint=cart_restraint
 n.set_meta("integration_motion_admitted",false)
 cart_restraint.motor=n
 parent.add_child(n)
 body.set_meta("group4_source_actuator",n.get_instance_id())
 n.configure_crossing(parent.get_node("ForwardGroundCrossing"))
 return n
'''.replace('PREFIX',P)
write('motor.gd',motor)
pins['Game/aquatic_tram_interior_20261026/integration/CONTRACTS.json']=hashlib.sha256((oldroot/'CONTRACTS.json').read_bytes()).hexdigest()
js('AUTHORING_RECEIPT.json',{'selected':False,'source_pins':pins,'stops':stops,'pose_count':len(rows),'scope':'Five-stop pose/portal and fresh original vehicle binding. Full inherited world receiving, support, original loaded joint and rider acceptance pending. Original production untouched.'})
print(json.dumps({'output':str(D),'stops':stops,'poses':len(rows)}))
