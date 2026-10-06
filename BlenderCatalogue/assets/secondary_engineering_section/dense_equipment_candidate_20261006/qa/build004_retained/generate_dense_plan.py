"""Pure geometry authoring plan for the scratch-only AST-ENG-008 dense_bays derivative.
No bpy import, no runtime/catalogue mutation; explicit semantic geometry and source markers.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1]
assert str(R)=='/workspace/scratch/375c2e438292/engineering-dense-bays'
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
P=Path('/workspace/shared/astraea-godot-production-20261003')
parts=[];markers=[];controls=[];cables=[];contacts=[];BAY='CONTROL';ASSEMBLY=''
PRISMS={'north_cart_strip':[20,6,-454.6,53.7,8.7,-451],'south_cart_strip':[20,6,-413,53.7,8.7,-409.4],'east_cart_strip':[48.3,6,-465.7,53.7,9.6,-398.3],'control_turn':[28.2,6,-460.8,31.8,8.7,-457.2],'workbay_turn':[28.2,6,-406.8,31.8,8.7,-403.2],'control_operating_face':[21.9,6,-462.4,30.1,8.4,-460.9]}
def mesh(n,v,f,role='staff_zinc',kind='static_surface',bevel=0,uvrect=None):
 p=dict(name=n,vertices_xyz=np.asarray(v).tolist(),faces=[list(x) for x in f],material_role=role,collision=kind,bay=BAY,assembly=ASSEMBLY,bevel=bevel)
 if uvrect:p['atlas_cell']=uvrect
 parts.append(p);return n
def box(n,b,role='staff_zinc',bevel=0,kind='static_surface'):
 x,y,z,X,Y,Z=b;assert X>x and Y>y and Z>z,(n,b)
 return mesh(n,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,kind,bevel)
def plate(n,c,w,h,d,role='staff_bluegrey_paint',ch=.04):
 x,y,z=c;ch=min(ch,w/4,h/4);a=[(-w/2+ch,-h/2),(w/2-ch,-h/2),(w/2,-h/2+ch),(w/2,h/2-ch),(w/2-ch,h/2),(-w/2+ch,h/2),(-w/2,h/2-ch),(-w/2,-h/2+ch)]
 return mesh(n,[(x+u,y+v,z+s*d/2) for s in [-1,1] for u,v in a],[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],role)
def tube(n,path,r,role='staff_zinc',N=10,kind='static_surface'):
 path=np.asarray(path,float);vs=[];prev=None
 for i,p in enumerate(path):
  t=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]);t/=np.linalg.norm(t)
  if prev is None:u=np.cross(t,[0,1,0] if abs(t[1])<.8 else [1,0,0]);u/=np.linalg.norm(u)
  else:u=prev-t*np.dot(prev,t);u/=np.linalg.norm(u)
  v=np.cross(t,u);prev=u
  vs.extend([p+r*(math.cos(2*math.pi*j/N)*u+math.sin(2*math.pi*j/N)*v) for j in range(N)])
 fs=[tuple(reversed(range(N))),tuple(range((len(path)-1)*N,len(path)*N))]+[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for k in range(len(path)-1) for j in range(N)]
 return mesh(n,vs,fs,role,kind)
def cyl(n,c,r,d,role='staff_zinc',axis='z',N=16,kind='static_surface'):
 a=np.asarray(c,float);v=np.array({'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}[axis]);return tube(n,[a-v*d/2,a+v*d/2],r,role,N,kind)
def rounded(path,r=.12,steps=5):
 out=[np.asarray(path[0],float)]
 for a,b,c in zip(path,path[1:],path[2:]):
  a,b,c=map(lambda x:np.array(x,float),(a,b,c));ab=b-a;bc=c-b;rr=min(r,np.linalg.norm(ab)*.42,np.linalg.norm(bc)*.42);q=b-ab/np.linalg.norm(ab)*rr;s=b+bc/np.linalg.norm(bc)*rr
  out.append(q)
  for t in np.linspace(0,1,steps+1)[1:]:out.append((1-t)**2*q+2*(1-t)*t*b+t*t*s)
 out.append(np.asarray(path[-1],float));return out

def marker(n,p,kind,**kw):markers.append(dict(name=n,position_xyz=list(p),kind=kind,bay=BAY,assembly=ASSEMBLY,**kw));return n
def contact(n,part,p,normal,owner,kind='bearing'):
 marker('CONTACT_'+n,p,'contact',owner=owner,part=part,normal_xyz=normal)
 contacts.append(dict(id=n,part=part,position_xyz=p,normal_xyz=normal,owner=owner,kind=kind))
def decal(n,c,w,h,cell,front=1):
 x,y,z=c;v=[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)]
 return mesh(n,v,[(0,1,2,3) if front==1 else (3,2,1,0)],'dense_instrument_pigment','none',uvrect=cell)
def bolts(n,c,w,h,front=1):
 x,y,z=c
 for a in [-1,1]:
  for b in [-1,1]:cyl(n+f'_bolt{a}_{b}',(x+a*(w/2-.04),y+b*(h/2-.04),z),.012,.016,'staff_zinc',N=6)
def panel(n,c,w,h,d=.11,front=1,cell=None):
 x,y,z=c;plate(n+'_shell',c,w,h,d,'staff_bluegrey_paint',.065);plate(n+'_gasket',(x,y,z+front*(d/2+.003)),w-.045,h-.045,.009,'staff_rubber',.055);plate(n+'_face',(x,y,z+front*(d/2+.012)),w-.073,h-.073,.018,'staff_white_paint',.045);bolts(n,(x,y,z+front*(d/2+.025)),w,h,front)
 if cell is not None:decal(n+'_legend',(x,y+h/2-.08,z+front*(d/2+.022)),w-.18,.065,cell,front)
 return z+front*(d/2+.026)
def port(n,p,direction,owner,r=.037):
 a=np.asarray(p,float);d=np.asarray(direction,float);d/=np.linalg.norm(d)
 tube(n+'_gland',[a-d*.035,a+d*.018],r,'staff_zinc',12);tube(n+'_collar',[a+d*.013,a+d*.048],r*.75,'staff_rubber',12)
 return marker('PORT_'+n,a+d*.042,'cable_port',owner=owner,direction_xyz=d.tolist())
def cable(n,pa,pb,path,r=.023,role='staff_cable_blue'):
 aa=next(m for m in markers if m['name']==pa)['position_xyz'];bb=next(m for m in markers if m['name']==pb)['position_xyz'];p=[aa]+path+[bb]
 tube(n,rounded(p,max(.06,r*5)),r,role,10);cables.append(dict(id=n,part=n,from_port=pa,to_port=pb,path_xyz=[list(map(float,x)) for x in p],radius_m=r))
def gauge(n,c,r=.13,front=1,style=0):
 x,y,z=c;cyl(n+'_rim',(x,y,z),r,.045,'staff_zinc',N=20);cyl(n+'_rubber',(x,y,z+front*.026),r*.89,.008,'staff_rubber',N=20);decal(n+'_dial',(x,y,z+front*.031),r*1.54,r*1.54,16+style%4,front)
 # Physical needle lies proud of printed ticks.
 tube(n+'_needle',[(x-.018,y-.012,z+front*.034),(x+r*.49,y+r*.45,z+front*.034)],.0055,'staff_cable_red',6)
def louvres(n,x,y,z,w,count=7,front=1):
 plate(n+'_recess',(x,y,z),w,.055*count+.06,.018,'staff_rubber',.02)
 for i in range(count):box(n+f'_fin{i}',(x-w/2+.025,y-.0275*count+i*.055,z-.016,x+w/2-.025,y-.0275*count+i*.055+.019,z+.016),'staff_zinc')
def actuator(id,panelid,c,front,kind,effect):
 x,y,z=c;prefix='ACT_'+id;normal=[0,0,front]
 # Socket and guard stay in static batching. Only authored actuator receives movable identity.
 cyl('Socket_'+id,(x,y,z-front*.012),.042,.022,'staff_zinc',N=12)
 movable=[]
 if kind in ['rotary','selector']:
  movable.append(cyl(prefix,(x,y,z+front*.02),.028 if kind=='rotary' else .033,.034,'staff_rubber',N=12,kind='actuator'))
  movable.append(box(prefix+'_index',(x-.004,y+.008,z+front*.038-.003,x+.004,y+.027,z+front*.038+.003),'staff_label',kind='actuator'))
 elif kind=='toggle':
  a=(x,y-.01,z);b=(x,y+.027,z+front*.045);movable.append(tube(prefix,[a,b],.012,'staff_zinc',8,kind='actuator'));movable.append(cyl(prefix+'_tip',b,.019,.025,'staff_white_paint',axis='y',N=10,kind='actuator'))
 elif kind=='guarded':
  for dx in [-.047,.047]:box('Guard_'+id+str(dx),(x+dx-.009,y-.042,min(z-front*.012,z+front*.073),x+dx+.009,y+.045,max(z-front*.012,z+front*.073)),'staff_cable_red')
  tube('GuardTop_'+id,[(x-.047,y+.045,z+front*.056),(x+.047,y+.045,z+front*.056)],.009,'staff_cable_red',8)
  movable.append(cyl(prefix,(x,y,z+front*.018),.03,.03,'staff_cable_red',N=12,kind='actuator'))
 else:movable.append(cyl(prefix,(x,y,z+front*.018),.029,.027,'staff_cable_blue' if kind=='push' else 'staff_white_paint',N=12,kind='actuator'))
 for part in parts:
  if part['name'] in movable:part['control_id']=id
 target=[x,y+(.027 if kind=='toggle' else 0),z+front*(.045 if kind=='toggle' else (.037 if kind in ['rotary','selector'] else .0315))]
 m=marker('TARGET_'+id,target,'control_target',normal_xyz=normal,control_id=id)
 # Normal-height supported candidate stand, selected individually along panel face.
 ap=[x,6,z+front*1.12];eye=[x,7.65,ap[2]];marker('APPROACH_'+id,ap,'approach',control_id=id)
 controls.append(dict(id=id,bay=BAY,panel=panelid,source_marker=m,actuator_mesh_name=prefix,actuator_parts=movable,kind=kind,target_center_xyz=target,target_normal_xyz=normal,target_half_extent_m=[.045,.045,.045],proposed_approach_xyz=ap,proposed_eye_xyz=eye,floor_owner='D02_secondary_engineering_floor',effect_candidate=effect,effect_scope='local panel only; proposed, no runtime script',pivot_xyz=[x,y,z],travel_axis_xyz=([1,0,0] if kind=='toggle' else normal),travel_type=('rotation' if kind in ['rotary','selector','toggle'] else 'translation'),travel_limits=([-20,20] if kind=='toggle' else ([-40,40] if kind in ['rotary','selector'] else [-.008,0])),travel_units=('degrees' if kind in ['rotary','selector','toggle'] else 'metres'),ordinary_eye_distance_m=math.dist(eye,target)))
def bank(panelid,c,cols,rows,front=1,pitch=.13,special=None):
 x,y,z=c
 for row in range(rows):
  for col in range(cols):
   slot=row*cols+col+1;id=f'ENG2_{BAY}_{panelid}_{slot:02d}';kind=['toggle','push','rotary','selector','push','toggle'][(row+col*2)%6];effect=['latch_click','momentary_travel','meter_step_return','local_led_sequence'][slot%4]
   if special and slot==special[0]:kind,effect=special[1:]
   actuator(id,panelid,(x+(col-(cols-1)/2)*pitch,y+(row-(rows-1)/2)*pitch,z),front,kind,effect)
def vertical_rack(n,x,z,w,h=2.64,front=1):
 # Open frame, floor feet, stepped top, recessed removable cartridges.
 for s in [-1,1]:
  foot=box(n+f'_foot{s}',(x+s*(w/2-.11)-.12,6,z-.34,x+s*(w/2-.11)+.12,6.075,z+.34),'staff_rubber',.018);contact(n+f'_floor{s}',foot,[x+s*(w/2-.11),6,z],[0,-1,0],'compiler_floor_Y6')
  box(n+f'_post{s}',(x+s*(w/2-.08)-.055,6.06,z-.27,x+s*(w/2-.08)+.055,6+h,z+.27),'staff_zinc',.016)
 plate(n+'_back',(x,6+h/2,z-front*.26),w-.16,h-.12,.065,'staff_bluegrey_paint',.08)
 plate(n+'_crown',(x,6+h-.07,z),w+.09,.22,.61,'staff_white_paint',.08)
 for i in range(4):
  yy=6.33+i*.48;face=panel(n+f'_cassette{i}',(x,yy,z+front*.1),w-.25,.39,.28,front,4+i)
  louvres(n+f'_vent{i}',x,yy-.02,face+front*.005,w-.47,3,front)
  for sx in [-1,1]:tube(n+f'_pull{i}_{sx}',[(x+sx*(w/2-.26),yy-.08,face),(x+sx*(w/2-.26),yy-.08,face+front*.07),(x+sx*(w/2-.26),yy+.08,face+front*.07),(x+sx*(w/2-.26),yy+.08,face)],.013,'staff_rubber',8)
 return n+'_back'
def service_spine(prefix,x0,x1,z,y,cap):
 # Open ladder tray, 3 cables, hangers to real ceiling. Not a fake shell.
 for dz in [-.24,.24]:box(prefix+f'_side{dz}',(x0,y-.055,z+dz-.022,x1,y+.075,z+dz+.022),'staff_zinc',.008)
 for i in range(int((x1-x0)/.34)+1):
  xx=x0+i*(x1-x0)/int((x1-x0)/.34);box(prefix+f'_rung{i}',(xx-.025,y-.055,z-.23,xx+.025,y-.018,z+.23),'staff_zinc')
 for j,xx in enumerate([x0+.2,(x0+x1)/2,x1-.2]):
  for s in [-1,1]:
   pp=box(prefix+f'_hanger{j}_{s}',(xx-.027,y+.045,z+s*.28-.027,xx+.027,cap,z+s*.28+.027),'staff_zinc');contact(prefix+f'_cap{j}_{s}',pp,[xx,cap,z+s*.28],[0,1,0],f'{BAY.lower()}_ceiling')
  box(prefix+f'_bearer{j}',(xx-.075,y-.09,z-.36,xx+.075,y-.055,z+.36),'staff_bluegrey_paint',.012)
 for j,dz in enumerate([-.14,0,.14]):
  for side,xx in [('L',x0),('R',x1)]:plate(prefix+f'_{side}_terminal{j}',(xx,y+.11,z+dz),.14,.24,.18,'staff_bluegrey_paint',.03)
  a=port(prefix+f'_L{j}',[x0+.07,y+.065,z+dz],[1,0,0],prefix+f'_L_terminal{j}',.031);b=port(prefix+f'_R{j}',[x1-.07,y+.065,z+dz],[-1,0,0],prefix+f'_R_terminal{j}',.031)
  cable(prefix+f'_bundle{j}',a,b,[],.032,['staff_rubber','staff_cable_blue','staff_cable_red'][j])
 return prefix

def build_control():
 global BAY,ASSEMBLY;BAY='CONTROL';ASSEMBLY='CALIBRATION_WALL'
 # Cabinet backing mass and load path surrounding, not replacing, existing console blocks.
 for k,x in enumerate([23,26,29]):
  n=f'Calibration_{k+1}';ASSEMBLY=n
  for sx in [-1,1]:
   st=box(n+f'_wall_stanchion{sx}',(x+sx*1.15-.065,6,-463.77,x+sx*1.15+.065,8.74,-463.35),'staff_bluegrey_paint',.018);contact(n+f'_foot{sx}',st,[x+sx*1.15,6,-463.55],[0,-1,0],'compiler_floor_Y6')
  plate(n+'_backpan',(x,7.58,-463.68),2.43,2.38,.20,'staff_bluegrey_paint',.14)
  # Larger offset header lets each console read as a useful station at normal distance.
  plate(n+'_folded_crown',(x,8.58,-463.39),2.53,.38,.57,'staff_white_paint',.085)
  decal(n+'_identity',(x,8.57,-463.093),1.8,.17,k,1)
  # Retained front is exactly the protected prism boundary: use top and side wraps only.
  for side in [-1,1]:
   xx=x+side*.918
   box(n+f'_pedestal_side{side}',(xx-.018,6.10,-463.19,xx+.018,7.06,-462.43),'staff_white_paint',.012)
   for j in range(5):box(n+f'_pedestal_side_rib{side}_{j}',(xx-.023,6.22+j*.14,-463.15,xx+.023,6.255+j*.14,-462.47),'staff_zinc')
  plate(n+'_top_return',(x,7.0875,-462.80),1.89,.075,.70,'staff_white_paint',.015)
  contact(n+'_pedestal_top',n+'_top_return',[x,7.05,-462.80],[0,-1,0],f'control_console_{x}')
  # Side wings angle visually via stepped chassis; retained AST-ENG-003 central face untouched.
  for side in [-1,1]:
   wing=n+('_LEFT' if side<0 else '_RIGHT');wx=x+side*.72
   face=panel(wing,(wx,7.43,-462.695),.44,.82,.14,1,8+k)
   bank(f'C{k+1}'+('L' if side<0 else 'R'),(wx,7.40,face+.004),3,4,1,.113,special=(12,'guarded','phase_courtesy_check_and_chime') if k==1 and side==1 else None)
   # Steel strap joins flange back to the retained pedestal top.
   box(wing+'_seat',(wx-.18,7.05,-463.16,wx+.18,7.08,-462.69),'staff_zinc');contact(wing+'_seat',wing+'_seat',[wx,7.05,-462.96],[0,-1,0],f'control_console_{x}')
  # Analog crowns are ornamental and not counted as operable controls.
  if k==0:
   for j,dx in enumerate([-.73,0,.73]):gauge(n+f'_pressure{j}',(x+dx,8.18,-463.08),.19,1,j)
   for j,dx in enumerate([-.36,.36]):louvres(n+f'_balance{j}',x+dx,8.15,-463.07,.24,4)
  elif k==1:
   for dx in [-.77,.77]:gauge(n+'_meter'+str(dx),(x+dx,8.18,-463.07),.18)
   plate(n+'_sequence_bank',(x,8.18,-463.1),.83,.35,.055,'staff_rubber',.035)
   for j in range(8):plate(n+f'_lamp{j}',(x-.325+j*.093,8.18,-463.067),.055,.19,.014,'staff_opal' if j<3 else 'staff_cable_blue',.017)
  else:
   for j in range(4):
    xx=x-.84+j*.56;plate(n+f'_relay{j}',(xx,8.17,-463.08),.44,.43,.15,'staff_zinc',.055)
    for i in range(4):box(n+f'_relay_slot{j}_{i}',(xx-.16,8.02+i*.076,-462.993,xx+.16,8.047+i*.076,-462.981),'staff_rubber')
  # Two real cable branches to top ports of the backing station, housed at both ends.
  for j in [-1,1]:
   xx=x+j*1.0;a=port(n+f'_top{j}',[xx,8.73,-463.44],[0,1,0],n+'_folded_crown',.053)
   plate(n+f'_upper_junction{j}',(xx,8.93,-461.76),.20,.22,.26,'staff_bluegrey_paint',.04)
   b=port(n+f'_feed{j}',[xx,8.93,-461.89],[0,0,-1],n+f'_upper_junction{j}',.053)
   cable(n+f'_branch{j}',a,b,[[xx,8.94,-463.44],[xx,8.94,-462.09]],.036,'staff_cable_blue' if j<0 else 'staff_rubber')
 ASSEMBLY='CONTROL_SERVICE_SPINE';service_spine('ControlCeiling',21.0,33.1,-461.75,8.83,9.30)
 # Connecting low bus rail and named plugs explain why the stations are together.
 box('Calibration_LowBus',(21.8,6.18,-463.5,30.2,6.31,-463.31),'staff_zinc',.018)
 for x in [23,26,29]:
  terminal=box('BaseRearTerminal'+str(x),(x-.12,6.90,-463.50,x+.12,7.06,-463.20),'staff_bluegrey_paint',.025)
  contact('BaseRearTerminalSeat'+str(x),terminal,[x,6.98,-463.20],[0,0,1],f'control_console_{x}','rear_terminal_mount')
  bracket=box('LowBusWallBracket'+str(x),(x-.07,6.205,-463.82,x+.07,6.285,-463.40),'staff_zinc')
  contact('LowBusWallSeat'+str(x),bracket,[x,6.24,-463.82],[0,0,-1],'control_north_wall0')
  a=port('LowBus'+str(x),[x,6.31,-463.38],[0,1,0],'Calibration_LowBus');b=port('BaseFeed'+str(x),[x,6.90,-463.38],[0,-1,0],'BaseRearTerminal'+str(x));cable('ConsoleRiser'+str(x),a,b,[],.025,'staff_cable_red')
 ASSEMBLY='WEST_RELAY_TOWER';vertical_rack('WestRelay',20.96,-463.0,1.39,2.65,1)
 ASSEMBLY='EAST_MONITOR_TOWER';vertical_rack('EastRelay',32.48,-462.12,1.48,2.78,1)
 # Broad wall equipment, materially and dimensionally varied, keeping all routes free.
 for j,x in enumerate([20.61,21.19]):
  cyl('WestCanister'+str(j),(x,7.39,-462.62),.18,1.48,'staff_white_paint','y',16)
  for yy in [6.76,7.94]:cyl('WestCanisterBand'+str((j,yy)),(x,yy,-462.62),.20,.08,'staff_zinc','y')
  gauge('WestCanisterGauge'+str(j),(x,8.16,-462.57),.12)
  box('WestCanisterFoot'+str(j),(x-.18,6.46,-462.79,x+.18,6.65,-462.45),'staff_zinc')
  # Real rack cassette is the bearing surface; rods are mechanically continuous.
  contact('CanisterSeat'+str(j),'WestCanister'+str(j),[x,6.65,-462.62],[0,-1,0],'WestCanisterFoot'+str(j))
 ASSEMBLY=''

def build_workbay():
 global BAY,ASSEMBLY;BAY='WORKBAY';ASSEMBLY='REPAIR_BENCH'
 # Bench fronts get long folded drawer returns and real pulls, avoiding old pull locations.
 for j,x in enumerate([22.0,24.0,26.0]):
  plate(f'BenchAccess{j}',(x,6.47,-402.026),1.77,.72,.035,'staff_white_paint',.08)
  for y in [6.32,6.58]:
   plate('BenchDrawer'+str((j,y)),(x,y,-402.050),1.65,.22,.015,'staff_bluegrey_paint',.035)
   tube('BenchPull'+str((j,y)),[(x-.20,y,-402.063),(x-.20,y,-402.12),(x+.20,y,-402.12),(x+.20,y,-402.063)],.017,'staff_zinc',8)
 # Vise has four bolted foot corners, slide, jaws and a recognizable screw handle.
 box('ViseBoltedFoot',(21.20,6.936,-401.80,21.85,6.99,-401.28),'staff_zinc',.03);contact('ViseBench','ViseBoltedFoot',[21.5,6.936,-401.54],[0,-1,0],'BenchWorktop_0')
 box('ViseSlide',(21.30,6.99,-401.65,21.75,7.11,-401.40),'staff_bluegrey_paint',.025)
 for x in [21.35,21.72]:box('ViseJaw'+str(x),(x-.045,7.06,-401.76,x+.045,7.31,-401.32),'staff_zinc',.008)
 cyl('ViseScrew',(21.63,7.10,-401.54),.027,.77,'staff_zinc','x',12);cyl('ViseScrewHub',(22.03,7.10,-401.54),.061,.10,'staff_bluegrey_paint','x',12);cyl('ViseTHandle',(22.08,7.10,-401.54),.014,.35,'staff_zinc','y',10)
 for x in [21.25,21.79]:
  for z in [-401.74,-401.34]:cyl('ViseBolt'+str((x,z)),(x,6.993,z),.024,.018,'staff_zinc','y',6)
 # A formed tester with a hooded oscilloscope face and twelve physical candidates.
 ASSEMBLY='BENCH_OSCILLOSCOPE';face=panel('BenchScope',(24.7,7.36,-401.20),1.12,.80,.57,-1,11)
 for x in [24.27,25.13]:
  foot=box('ScopeFoot'+str(x),(x-.065,6.936,-401.50,x+.065,6.97,-400.96),'staff_rubber',.012);contact('ScopeBench'+str(x),foot,[x,6.936,-401.24],[0,-1,0],'BenchWorktop_1')
 plate('ScopeHood',(24.49,7.47,face+.01),.57,.42,.07,'staff_rubber',.055);decal('ScopeTrace',(24.49,7.47,face-.027),.48,.34,20,-1)
 bank('SCOPE',(24.98,7.27,face-.008),2,6,-1,.103)
 # Paired docked slack leads: terminate in actual front jacks, held by a side hook.
 for j,yy in enumerate([7.13,7.28]):
  a=port('ScopeJack'+str(j),[24.35,yy,face],[0,0,-1],'BenchScope_face',.022)
  b=port('ScopeReturn'+str(j),[24.57,yy,face],[0,0,-1],'BenchScope_face',.022)
  cable('ScopeCoiledLead'+str(j),a,b,[[24.35,yy,-401.75],[24.10,6.995,-401.80],[23.85,7.08,-401.75],[23.96,7.33,-401.68],[24.12,7.39,-401.67],[24.38,7.16,-401.68],[24.57,yy,-401.65]],.012,['staff_cable_red','staff_rubber'][j])
 # Pump repair fixture on real V saddles, with rotor extension and removable shell halves.
 ASSEMBLY='PUMP_TEST_CRADLE';box('PumpCradleBase',(25.35,6.936,-401.76,26.74,6.99,-400.90),'staff_zinc',.04);contact('PumpBench','PumpCradleBase',[26.04,6.936,-401.35],[0,-1,0],'BenchWorktop_1')
 for x in [25.62,26.48]:
  for s in [-1,1]:tube('CradleLeg'+str((x,s)),[(x,6.99,-401.34+s*.29),(x,7.16,-401.34+s*.16)],.055,'staff_bluegrey_paint',8)
  cyl('CradleBand'+str(x),(x,7.25,-401.34),.205,.065,'staff_zinc','x',16)
 cyl('PumpMainShell',(26.06,7.25,-401.34),.188,.86,'staff_white_paint','x',16)
 for x in [25.67,26.12,26.49]:cyl('PumpRib'+str(x),(x,7.25,-401.34),.207,.068,'staff_bluegrey_paint','x',16)
 cyl('ExposedPumpRotor',(26.63,7.25,-401.34),.103,.40,'staff_zinc','x',14)
 for j in range(8):
  a=2*math.pi*j/8;d=(math.cos(a)*.124,math.sin(a)*.124);tube('RotorVane'+str(j),[(26.55,7.25+d[0],-401.34+d[1]),(26.80,7.25+d[0]*.78,-401.34+d[1]*.78)],.022,'staff_zinc',6)
 cyl('PumpInlet',(25.64,7.48,-401.34),.081,.25,'staff_zinc','y',12)
 # Spare bins, each with genuinely open top, on rear shelf; no solid fill blocks.
 ASSEMBLY='BENCH_STORAGE'
 for j,x in enumerate([27.38,27.98,28.58,29.18]):
  z=-400.61;y=8.055;box('BinBase'+str(j),(x-.24,y,z-.20,x+.24,y+.035,z+.16),'staff_bluegrey_paint')
  for sx in [-1,1]:box('BinSide'+str((j,sx)),(x+sx*.23-.012,y,z-.20,x+sx*.23+.012,y+.20,z+.16),'staff_bluegrey_paint')
  box('BinBack'+str(j),(x-.24,y,z+.135,x+.24,y+.22,z+.16),'staff_bluegrey_paint');box('BinFront'+str(j),(x-.24,y,z-.20,x+.24,y+.12,z-.18),'staff_bluegrey_paint');decal('BinLabel'+str(j),(x,y+.068,z-.202),.28,.06,21+j%3,-1)
  for k in range(3):cyl('StoredFuse'+str((j,k)),(x-.13+k*.13,y+.073,z-.01),.038,.20,'staff_zinc','z',8)
 # Perforated shelf: repeated strips create honest openings rather than a hole texture.
 for j in range(21):box('PerforatedShelfSlat'+str(j),(27.10+j*.115,8.020,-400.88,27.17+j*.115,8.055,-400.23),'staff_zinc')
 for x in [27.22,28.20,29.40]:
  tube('ShelfDiagonal'+str(x),[(x,7.75,-400.22),(x,8.025,-400.83)],.026,'staff_zinc',8);box('ShelfWallPad'+str(x),(x-.09,7.73,-400.235,x+.09,8.08,-400.18),'staff_zinc',.015);contact('ShelfWall'+str(x),'ShelfWallPad'+str(x),[x,7.9,-400.18],[0,0,1],'workbay_south_wall0')
 # Extraction hood above pump: tapered hood, actual flexible neck and wall collector.
 ASSEMBLY='EXTRACTION'
 v=[]
 for yy,w,d in [(7.82,.68,.48),(8.10,.28,.25)]:v.extend([(26.14+sx*w/2,yy,-401.37+sz*d/2) for sx,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]])
 mesh('ExtractionHood',v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'staff_zinc')
 box('HoodFilter',(25.85,7.805,-401.54,26.43,7.825,-401.20),'staff_rubber')
 plate('ExtractionCollector',(26.4,8.79,-400.45),.70,.48,.45,'staff_white_paint',.085)
 a=port('ExtractionNeck',[26.14,8.10,-401.37],[0,1,0],'ExtractionHood',.13);b=port('ExtractionCollectorFeed',[26.4,8.79,-400.69],[0,0,-1],'ExtractionCollector',.13);cable('ExtractionHose',a,b,[[26.14,8.54,-401.37],[26.4,8.79,-401.12]],.095,'staff_rubber')
 for yy in [8.24,8.36,8.48]:cyl('ExtractionRib'+str(yy),(26.14,yy,-401.37),.104,.028,'staff_zinc','y',12)
 box('ExtractionWallShoe',(26.17,8.65,-400.23,26.64,8.94,-400.18),'staff_zinc');contact('ExtractionWall','ExtractionWallShoe',[26.4,8.8,-400.18],[0,0,1],'workbay_south_wall0')
 # Articulated task head is visibly mounted, emitter proposal only.
 box('TaskArmBenchClamp',(26.72,6.936,-401.05,26.92,7.00,-400.78),'staff_zinc');contact('TaskClamp','TaskArmBenchClamp',[26.82,6.936,-400.9],[0,-1,0],'BenchWorktop_1')
 tube('TaskArmLower',[(26.82,7.0,-400.9),(26.82,7.76,-400.9)],.035,'staff_bluegrey_paint',10);tube('TaskArmUpper',[(26.82,7.76,-400.9),(26.45,7.88,-401.34)],.029,'staff_zinc',10)
 for p in [(26.82,7.76,-400.9),(26.45,7.88,-401.34)]:cyl('TaskArmHinge'+str(p),p,.074,.1,'staff_rubber','x',12)
 plate('TaskHead',(26.43,7.84,-401.45),.37,.17,.22,'staff_bluegrey_paint',.05);box('TaskOpal',(26.28,7.746,-401.55,26.58,7.758,-401.35),'staff_opal',kind='none');marker('LIGHT_PROPOSAL_bench_task',[26.43,7.73,-401.45],'fixture_exit',aim_xyz=[26.1,7.18,-401.35],active_runtime=False)
 # Morale unit, true floor feet and tray supported from cabinet body.
 ASSEMBLY='MORALE_CALIBRATION';x=28.46;z=-401.07
 for sx in [-1,1]:
  ft=box('MoraleFoot'+str(sx),(x+sx*.43-.075,6,z-.41,x+sx*.43+.075,6.14,z+.41),'staff_rubber',.025);contact('MoraleFloor'+str(sx),ft,[x+sx*.43,6,z],[0,-1,0],'compiler_floor_Y6')
 face=z-.426
 plate('MoraleBodyLower',(x,6.51,z),1.18,.80,.80,'staff_bluegrey_paint',.10)
 plate('MoraleBodyUpper',(x,7.73,z),1.18,.40,.80,'staff_white_paint',.08)
 plate('MoraleBodyRight',(x+.39,7.23,z),.39,.91,.80,'staff_bluegrey_paint',.045)
 plate('MoraleBodyLeft',(x-.50,7.23,z),.18,.91,.80,'staff_bluegrey_paint',.035)
 plate('MoraleBodyRear',(x-.14,7.22,z+.36),.74,.85,.08,'staff_bluegrey_paint',.04)
 louvres('MoraleVent',x,6.46,face-.013,.88,5,-1)
 # A deep dispensing aperture built from side cheeks, lintel and recessed back.
 box('MoraleApertureBack',(x-.35,6.96,face+.035,x+.08,7.42,face+.14),'staff_rubber')
 for xx in [x-.40,x+.12]:box('MoraleApertureCheek'+str(xx),(xx-.035,6.92,face-.11,xx+.035,7.46,face+.08),'staff_zinc',.012)
 box('MoraleLintel',(x-.43,7.42,face-.10,x+.15,7.49,face+.08),'staff_white_paint',.02)
 tray=box('MoraleReceivingTray',(x-.43,6.91,face-.44,x+.15,6.955,face+.065),'staff_zinc',.023)
 for xx in [x-.33,x+.05]:tube('MoraleTrayBracket'+str(xx),[(xx,6.69,face+.06),(xx,6.93,face-.37)],.028,'staff_bluegrey_paint',8)
 contact('MoraleTrayBearing',tray,[x-.14,6.91,face+.045],[0,-1,0],'MoraleBodyLower','rear_shelf_bearing')
 marker('EFFECT_morale_cake_output',[x-.14,6.98,face-.20],'effect_output',tray='MoraleReceivingTray',proposed_prop_max_xyz=[.24,.12,.20],runtime=False)
 bank('MORALE',(x+.39,7.24,face-.008),2,6,-1,.105,special=(12,'guarded','bounded_cake_candidate'))
 decal('MoraleLegend',(x,7.80,face-.01),.89,.11,13,-1)
 # Tall test cabinet at the east end, leaving the retained x31 cabinet completely visible.
 ASSEMBLY='EAST_TEST_RACK';x=32.98;z=-401.0
 for sx in [-1,1]:
  ft=box('TestRackFoot'+str(sx),(x+sx*.55-.10,6,z-.49,x+sx*.55+.10,6.12,z+.43),'staff_rubber',.025);contact('TestRackFloor'+str(sx),ft,[x+sx*.55,6,z],[0,-1,0],'compiler_floor_Y6')
 plate('TestRackBody',(x,7.39,z),1.42,2.67,.82,'staff_bluegrey_paint',.13)
 for yy in [6.4,6.76]:face=panel('TestRackDrawer'+str(yy),(x,yy,z-.41),1.25,.29,.08,-1,6);louvres('TestRackLowerVent'+str(yy),x,yy,face-.006,1.03,3,-1)
 face=panel('TestRackControlPanel',(x,7.45,z-.41),1.24,1.00,.11,-1,14);bank('TEST_RACK',(x,7.40,face-.006),6,4,-1,.155)
 for xx in [x-.39,x+.39]:gauge('TestRackMeter'+str(xx),(xx,8.16,z-.46),.22,-1,2)
 plate('TestRackCrown',(x,8.66,z-.02),1.55,.21,.86,'staff_white_paint',.065);decal('TestRackIdentity',(x,8.65,z-.461),1.21,.105,15,-1)
 # Two cable sockets on side edge connect the rack to a real upper wall junction.
 for j in [-1,1]:
  a=port('TestRackUpper'+str(j),[x+j*.38,8.76,z],[0,1,0],'TestRackCrown',.043);plate('WorkbayRackJunction'+str(j),(x+j*.38,9.18,z-.65),.20,.22,.24,'staff_bluegrey_paint',.035);b=port('TestRackSupply'+str(j),[x+j*.38,9.07,z-.65],[0,-1,0],'WorkbayRackJunction'+str(j),.043);cable('TestRackFeed'+str(j),a,b,[[x+j*.38,9.13,z],[x+j*.38,9.20,z-.37]],.031,'staff_cable_blue' if j<0 else 'staff_cable_red')
 ASSEMBLY='TEST_RACK_TASK_PROPOSAL'
 shoe=box('TestTaskMountShoe',(32.96,8.765,-401.2,33.20,8.815,-400.98),'staff_zinc',.012);contact('TestTaskRackSeat',shoe,[33.08,8.765,-401.1],[0,-1,0],'TestRackCrown')
 tube('TestTaskBentArm',rounded([[33.08,8.81,-401.1],[33.08,8.95,-401.1],[33.08,8.95,-402.02],[33.08,8.47,-402.02]],.09),.034,'staff_zinc',10)
 plate('TestTaskHousing',(33.08,8.40,-402.02),.68,.14,.25,'staff_bluegrey_paint',.045)
 box('TestTaskOpal',(32.80,8.311,-402.11,33.36,8.33,-401.93),'staff_opal',kind='none')
 marker('LIGHT_PROPOSAL_test_rack',[33.08,8.295,-402.02],'fixture_exit',aim_xyz=[32.98,7.4,-401.5],active_runtime=False)
 ASSEMBLY='WORKBAY_SERVICE_SPINE';service_spine('WorkbayCeiling',20.8,33.50,-401.65,9.18,9.60)
 # Service band behind the tools and cabinet, exact rear-wall seats.
 for xx in [21.0,27.4,29.8,33.5]:
  plate('WorkbayServicePad'+str(xx),(xx,8.98,-400.22),.40,.54,.08,'staff_zinc',.035);contact('WorkbayServiceWall'+str(xx),'WorkbayServicePad'+str(xx),[xx,8.98,-400.18],[0,0,1],'workbay_south_wall0')
 box('WorkbayWallBus',(20.80,8.91,-400.38,33.62,9.08,-400.26),'staff_bluegrey_paint',.026)
 ASSEMBLY=''

def add_west_workbay():
 global BAY,ASSEMBLY
 BAY='WORKBAY';ASSEMBLY='WEST_DIAGNOSTIC_WALL'
 start=len(parts);mi=len(markers);ci=len(contacts);cb=len(cables)
 vertical_rack('WestWorkRack',0,0,2.20,2.72,1)
 # Crown-borne transducer drums give the far wall a real machinery silhouette.
 for j,xx in enumerate([-.66,.0,.66]):
  gauge('WestWorkVacuum'+str(j),(xx,8.12,.30),.21,1,j)
  plate('WestWorkRelayCap'+str(j),(xx,8.51,.12),.55,.30,.36,'staff_white_paint',.055)
 # Remap this purpose-built west-wall unit from local frontal +Z to world +X.
 def pos(p):return [20.70+p[2],p[1],-406.45-p[0]]
 def normal(p):return [p[2],p[1],-p[0]]
 for p in parts[start:]:p['vertices_xyz']=[pos(v) for v in p['vertices_xyz']]
 for m in markers[mi:]:
  m['position_xyz']=pos(m['position_xyz'])
  for k in ['normal_xyz','direction_xyz']:
   if k in m:m[k]=normal(m[k])
 for c in contacts[ci:]:c['position_xyz']=pos(c['position_xyz']);c['normal_xyz']=normal(c['normal_xyz'])
 # Long supported manifold to the east of the rack, on its own visible floor skid.
 ASSEMBLY='WEST_FILTER_SKID'
 base=box('FilterSkid',(20.37,6,-404.52,21.35,6.14,-403.0),'staff_zinc',.045);contact('FilterSkidFloor',base,[20.8,6,-403.75],[0,-1,0],'compiler_floor_Y6')
 for j,z in enumerate([-404.15,-403.38]):
  foot=box('FilterBearing'+str(j),(20.49,6.14,z-.25,21.21,6.25,z+.25),'staff_bluegrey_paint',.025)
  cyl('FilterDrum'+str(j),(20.84,7.12,z),.25,1.74,'staff_white_paint','y',16)
  contact('FilterBearingSeat'+str(j),'FilterDrum'+str(j),[20.84,6.25,z],[0,-1,0],foot)
  for yy in [6.42,7.83]:cyl('FilterBand'+str((j,yy)),(20.84,yy,z),.276,.11,'staff_bluegrey_paint','y',16)
  a=port('FilterTop'+str(j),[20.84,7.99,z],[0,1,0],'FilterDrum'+str(j),.084)
  plate('FilterUpperJunction'+str(j),(20.84,8.78,z),.34,.26,.33,'staff_bluegrey_paint',.04)
  b=port('FilterRiserEnd'+str(j),[20.84,8.65,z],[0,-1,0],'FilterUpperJunction'+str(j),.084)
  cable('FilterRiser'+str(j),a,b,[],.057,'staff_cable_blue' if j==0 else 'staff_rubber')
  # Flange foot to ceiling load path, beside the visible pipe.
  post=box('FilterManifoldSupport'+str(j),(20.60,6.14,z-.042,20.67,9.6,z+.042),'staff_zinc',.008);contact('FilterCap'+str(j),post,[20.635,9.6,z],[0,1,0],'workbay_ceiling')
  box('FilterJunctionSeat'+str(j),(20.635,8.67,z-.065,20.75,8.85,z+.065),'staff_zinc')
 # Suspended task fixture is a proposal only; source-render baseline keeps it unlit.
 ASSEMBLY='WEST_TASK_PROPOSAL'
 stem=box('WestTaskStem',(22.93,9.20,-406.57,23.07,9.60,-406.43),'staff_zinc',.01);contact('WestTaskCap',stem,[23,9.60,-406.5],[0,1,0],'workbay_ceiling')
 plate('WestTaskHousing',(23,9.13,-406.5),.75,.18,.36,'staff_bluegrey_paint',.055)
 box('WestTaskOpal',(22.70,9.025,-406.64,23.30,9.044,-406.36),'staff_opal',kind='none')
 marker('LIGHT_PROPOSAL_west_rack',[23,9.005,-406.5],'fixture_exit',aim_xyz=[20.98,7.36,-405.8],active_runtime=False)
 ASSEMBLY=''

def main():
 build_control();build_workbay();add_west_workbay()
 import sys
 sys.path.insert(0,str(R/'source'));from north_wall_revision import add_north_services
 add_north_services(sys.modules[__name__])
 registry=json.loads((C/'catalogue_manifest.json').read_text());ids=[x['catalogue_id'] for x in registry['assets']];assert len(ids)==len(set(ids));entry=next(x for x in registry['assets'] if x['catalogue_id']=='AST-ENG-008');assert entry['family']=='secondary_engineering_section';console=next(x for x in registry['assets'] if x['catalogue_id']=='AST-ENG-003');assert console['family']=='utility_console'
 inputs={}
 for p in [C/'catalogue_manifest.json',C/entry['source'],C/entry['export'],C/console['source'],C/console['export'],C/'standards/staff_materials.py',C/'materials/staff/manifest.json',R.parent/'engineering-essentials/source/AST-ENG-008_essentials.blend',R.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb',P/'scripts/player.gd',P/'scripts/fixture_switch.gd',P/'scripts/secondary_engineering_essentials.gd']+list((C/'materials/staff').glob('*.png')):inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 for e in [entry,console]:
  for typ in ['source','export']:assert inputs[str(C/e[typ])]==e[typ+'_sha256']
 assert len(controls)==120 and sum(c['bay']=='CONTROL' for c in controls)==72 and sum(c['bay']=='WORKBAY' for c in controls)==48
 assert len({p['name'] for p in parts})==len(parts);assert len({m['name'] for m in markers})==len(markers);assert max(c['ordinary_eye_distance_m'] for c in controls)<2.5
 # Planned raw triangles only. The source and independent actual export gates repeat this later.
 hits={n:[] for n in PRISMS}
 for p in parts:
  v=np.array(p['vertices_xyz']);lo=v.min(0);hi=v.max(0);p['planned_bounds_xyz']=lo.tolist()+hi.tolist()
  for n,b in PRISMS.items():
   if np.all(np.minimum(hi,b[3:])-np.maximum(lo,b[:3])>1e-5):hits[n].append(p['name'])
 out=dict(catalogue_id='AST-ENG-008',family='secondary_engineering_section',derivative='dense_bays',scope='Additive source-only CONTROL + WORKBAY; no runtime adoption',coordinate_system='world Godot XYZ metres; Blender x,-z,y',parts=parts,markers=markers,controls=controls,cables=cables,contacts=contacts,prisms=PRISMS,input_hashes=inputs,catalogue_ownership_checked_entries=len(ids),planned_aabb_prism_hits=hits,no_new_floor=True,retained_console_reuse='Preserves existing AST-ENG-003-derived essentials faces in their authoritative retained GLB, no duplicate export',runtime_code=False)
 (R/'source/dense_plan.json').write_text(json.dumps(out,indent=2)+'\n')
 (R/'source/control_manifest.json').write_text(json.dumps({k:out[k] for k in ['catalogue_id','family','derivative','coordinate_system','controls','markers','cables','contacts','prisms']},indent=2)+'\n')
 print(json.dumps(dict(parts=len(parts),controls=len(controls),cables=len(cables),ports=sum(m['kind']=='cable_port' for m in markers),contacts=len(contacts),max_reach=max(c['ordinary_eye_distance_m'] for c in controls),hits=hits),indent=2))
 assert not any(hits.values()),hits
if __name__=='__main__':main()
