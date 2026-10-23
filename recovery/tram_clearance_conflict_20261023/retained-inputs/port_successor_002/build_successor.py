#!/usr/bin/env python3
"""Successor source proposal only. All writes stay in this separately versioned directory."""
from pathlib import Path
import bpy,math,json,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009'
freeze=json.loads((F/'FROZEN_FIRST_BATCH.json').read_text())
assert all(hashlib.sha256((F/n).read_bytes()).hexdigest()==a['sha256'] for n,a in freeze['files'].items()),'frozen source changed'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.open_mainfile(filepath=str(F/'Group4_Foremid_Tram_Source.blend'))
G=lambda p:(p[0],p[2],-p[1]);old={}
for co in bpy.data.collections:
 if co.name=='UNEXPORTED_REFERENCE_AND_STUDIO':continue
 rows=[]
 for ob in co.objects:
  row={'name':ob.name,'type':ob.type,'role':ob.get('role',''),'policy':ob.get('collision_policy',''),'datum':ob.get('datum_kind','')}
  if ob.type=='MESH':row.update(vs=[G(ob.matrix_world@v.co) for v in ob.data.vertices],fs=[tuple(p.vertices) for p in ob.data.polygons],mat=ob.data.materials[0].name)
  else:row['pos']=G(ob.matrix_world.translation)
  rows.append(row)
 old[co.name]=rows
# Reuse the frozen builder's mesh/UV/material vocabulary, not its original placements or outputs.
scaffold=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0]
scaffold=scaffold.replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name", "OUT=W;FAMILY='group4_tram_connections_port_successor_002'")
scaffold=scaffold.replace("assert FAMILY=='group4_tram_connections_20261009'",'')
scaffold=scaffold.replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']", "IDS=['AST-TRM-G4-010','AST-TRM-G4-011','AST-TRM-G4-012','AST-TRM-G4-013','AST-TRM-G4-014','AST-TRM-G4-015','AST-TRM-G4-016']")
scaffold=scaffold.replace("'AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'", "'AFT_STATIC_SOURCE','CONTINUOUS_GUIDEWAY_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'")
scaffold=scaffold.replace("bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)", "bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\nfor cc in list(bpy.data.collections):bpy.data.collections.remove(cc)")
exec(scaffold,globals())
def cp(row,fn,co,prefix='V2__',flip=False):
 if row['type']=='MESH':
  fs=[tuple(reversed(f)) for f in row['fs']] if flip else row['fs']
  return mesh(prefix+row['name'],[fn(p) for p in row['vs']],fs,materials[row['mat']],row['role'],row['policy'],co)
 ob=marker(prefix+row['name'],fn(row['pos']),row['datum'],co)
 if 'BOARDING_GATE' in row['name'] or 'BRIDGE_STOW' in row['name']:ob['datum_kind']='root-owned retractable2.18m-wide bridge,1.0926m reach; source portal clear2.22m, vehicle clear2.33m; interlock and operating gate not supplied'
 if row['name']=='TRAM_PORT_DOOR_SILL':ob['datum_kind']='port physical aperture2.33m clear; closed door and bridge interlock supplied by root later'
 return ob
def bnd(ob):
 ps=[G(ob.matrix_world@v.co) for v in ob.data.vertices];return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def endguard(name,z,x0,x1,y=56.1):
 box(name+'_infill',((x0+x1)/2,y+.65,z),(x1-x0,1.08,.06),glass,'closed end guard')
 tube(name+'_rail',(x0,y+1.13,z),(x1,y+1.13,z),.055,metal,'end handrail')
# Body length and wheel gauge/chord retained. Two open side portals, future doors owned by root.
current=collections['TRAM_EDITABLE_COMPONENT'];k=2.3/2.7
for row in old['TRAM_EDITABLE_COMPONENT']:
 n=row['name']
 if n.startswith('Tram_Starboard_'):continue
 if n.startswith('Cart_Restraint_'):
  def fn(p):
   dx=.10 if 'Anchor_' in n else .05; yy=-.01+(p[1]-.17)*.1 if 'Anchor_' in n else -.015+(p[1]-.07)*.15
   return (p[0]+(dx if p[0]>0 else -dx),yy,p[2]-.78)
 elif n.startswith(('Tram_Wheel_','Tram_Operator_','Tram_Control_')):fn=lambda p:p
 else:fn=lambda p:(p[0]*k,p[1],p[2])
 ob=cp(row,fn,current)
 if row['type']=='MESH' and n.startswith(('Tram_PortPocket_','Tram_Door_Post_','Tram_Port_Header')):
  cp(row,lambda p:(-p[0]*k,p[1],p[2]),current,'V2_Starboard__',True)
 if n=='TRAM_EXISTING_CART_DOCK':ob.location=B((0,0,.15));ob['datum_kind']='existing physical cart only, dockZ0.15; mounts are not operating clamps'
 if n=='TRAM_PLAYER_STANCE':ob.location=B((0,0,-.95))
marker('V2_TRAM_REAR_CART_OPERATOR_STANCE',(0,0,1.77),'0.3m radius; existing0.95m handle reach to gripZ0.82')
marker('V2_TRAM_STARBOARD_DOOR_SILL',(1.3*k,0,0),'second2.4m portal; root-owned powered doors/interlock pending')
for z in [-1.5,1.5]:marker('V2_BOGIE_STEERING_KINGPIN_'+str(z),(0,-.2,z),'3m chord, original gauge1.72m; curved steering mechanics not supplied')
# Four off-central station interfaces now face the selected port trunk. No lower slab exports.
stations=[]
for label,core,catch,file in [('FORWARD',-432,-432,'AST-TRM-G4-013_forward_source.glb'),('AFT',432,432,'AST-TRM-G4-015_aft_source.glb')]:
 current=collections[label+'_STATIC_SOURCE']
 for row in old[label+'_STATIC_SOURCE']:
  n=row['name']
  if '__GuidewayWeb_' in n or '__GuideRail_' in n or '__GUIDEWAY_INTERFACE_' in n:continue
  ob=cp(row,lambda p:(-p[0],p[1],p[2]),current,flip=True)
  if row['type']!='MESH' and n.endswith('COMMONS_LIFT_ROOT'):ob['datum_kind']='yaw+PI/2 standard cabin, localgate0, two stops52.5/56.1; root integration'
  if row['type']!='MESH' and n.endswith('BOARDING_GATE_MOUNT'):ob['datum_kind']='starboard tram door, gap1.0926m, bridge width2.4m; root interlock required'
 for z in [catch-3,catch+3]:endguard('V2_'+label+'_PodEnd_'+str(z),z,-3.4,1.8)
 stations.append({'label':label,'asset':file,'catchment_z':catch,'actual_core_z':core,'platform_xz':[-3.4,catch-3,1.8,catch+3],'track_x':-5.6,'boarding_edge_x':-3.4,'lift_root':[5.6,0,core-17.2],'lift_yaw_rad':math.pi/2,'lower_lift_recess_xz':[3.4,core-21,7.8,core-17],'recess_existing_slab_overlap_m2':2.4,'lower_missing_only_strip_xz':[4,core-32.5,7.8,core-12.9],'emergency_flight_width_m':2.4,'upper_connector_x':[3.45,7.72],'lower_floor_exported':False})
# Foremid is specifically recoordinated around retained Orchard Exchange and Thread&Shell.
mid_ob=[];current=collections['FORE_MIDSHIP_STATIC_SOURCE']
for row in old['FORE_MIDSHIP_STATIC_SOURCE']:
 n=row['name']
 if n.startswith(('Guideway_','Guide_Rail_','Pier_OuterFascia_','Platform_Cantilever_','Platform_Diagonal_','GUIDEWAY_INTERFACE_','UNEXPORTED_')):continue
 if n.startswith(('Emergency_','Upper_Approach_','LOWER_STAIR_','UPPER_STAIR_')):
  ob=cp(row,lambda p:(6+(p[0]+4.9)*.6,p[1],p[2]+17),current);mid_ob.append(ob)
 elif n.startswith(('BoardingLift_','LiftApproach_','REUSE_COMMONS_LIFT_ROOT','BOARDING_LIFT_')):
  ob=cp(row,lambda p:(-p[0],p[1],-428.6-p[2]),current);mid_ob.append(ob)
  if n=='REUSE_COMMONS_LIFT_ROOT':ob['datum_kind']='yaw+PI/2 standard cabin, localgate0; lower52.5/upper56.1'
 elif n.startswith(('Guest_','GUEST_')):continue
 elif n=='CORE_TRANSFER_D09':mid_ob.append(marker('V2__'+n,(1,52.5,-252),'retained fore-midship aft opening, catchment−216'))
 elif n=='D09_PEDESTRIAN_AXIS':mid_ob.append(marker('V2__'+n,(0,52.5,-216),'existing X−2..2 lower pedestrian axis remains clear'))
 else:mid_ob.append(cp(row,lambda p:(-5.6-p[0],p[1],p[2]),current,flip=True))
# New lateral returns bridge actual stair/lift upper landings to the boarding platform.
box('V2_Foremid_StairReturn',(3.19,55.975,-213.3),(2.38,.25,4.6),stone,'upper stair return, no lower axis obstruction')
box('V2_Foremid_LiftReturn',(2.7,55.975,-226.6),(1.4,.25,4.0),stone,'upper4m-deep lift turn to platform')
for z in [-228.6,-224.6]:endguard('V2_Foremid_LiftReturnGuard_'+str(z),z,2,3.4)
box('V2_Foremid_GuestWaitingScreen',(7.7,53.5,-210),(.12,2,3),ivory,'separate abstract-transit wait edge, future lower receiver')
marker('V2_Foremid_GUEST_ABSTRACT_WAIT',(5.6,52.5,-210),'abstract guest wait separate from physical tram, no controller supplied')
marker('V2_Foremid_BOARDING_BRIDGE_STOW_AXIS',(-3.4,56.1,-216),'starboard sillX−4.4926;1.0926m reach, root interlocked bridge')
# Actual axial receiving piers are additive geometric candidates; load acceptance stays held.
for i,z in enumerate([-228,-222,-216,-210,-204]):
 for x in [-2.4,2.4]:
  box('V2_Foremid_Foot_%s_%s'%(i,x),(x,52.54,z),(.42,.08,.75),metal,'actual D09 slab contact')
  box('V2_Foremid_Pier_%s_%s'%(i,x),(x,54.12,z),(.30,3.08,.4),ivory,'source receiver pier outside4m lower axis')
 box('V2_Foremid_Beam_'+str(i),(0,55.615,z),(15.5,.13,.55),metal,'platform/annex crossbearer candidate, capacity unaccepted')
 box('V2_Foremid_PlatformJoist_'+str(i),(-.7,55.79,z),(5.4,.22,.55),metal,'actual positive platform/beam overlap')
# Preserve the already-clear aft-midship starboard proposal before changing foremid only.
aft_seed=[]
for ob in list(collections['FORE_MIDSHIP_STATIC_SOURCE'].objects):
 row={'name':ob.name,'type':ob.type,'role':ob.get('role',''),'policy':ob.get('collision_policy',''),'datum':ob.get('datum_kind','')}
 if ob.type=='MESH':row.update(vs=[G(ob.matrix_world@v.co) for v in ob.data.vertices],fs=[tuple(p.vertices) for p in ob.data.polygons],mat=ob.data.materials[0].name)
 else:row['pos']=G(ob.location)
 aft_seed.append(row)
# Thread&Shell canopy/porch extends into the foremid starboard access. Preserve it entirely.
# Reuse original full-width station on the outer port side of the same selected trunk.
current=collections['FORE_MIDSHIP_STATIC_SOURCE']
for ob in list(current.objects):
 if ob in parts:parts.remove(ob)
 if ob in markers:markers.remove(ob)
 bpy.data.objects.remove(ob,do_unlink=True)
for row in old['FORE_MIDSHIP_STATIC_SOURCE']:
 n=row['name']
 if n.startswith(('Guideway_','Guide_Rail_','Pier_OuterFascia_','Platform_Cantilever_','Platform_Diagonal_','GUIDEWAY_INTERFACE_','UNEXPORTED_')):continue
 if n in ['CORE_TRANSFER_D09','D09_PEDESTRIAN_AXIS']:cp(row,lambda p:p,current)
 else:cp(row,lambda p:(p[0]-5.6,p[1],p[2]),current)
for i,z in enumerate([-248,-240,-232,-224,-216,-208,-200,-192,-184]):
 for x in [-2.4,2.4]:
  box('V2_Foremid_OuterPort_Foot_'+str((i,x)),(x,52.54,z),(.42,.08,.75),metal,'actual D09 slab contact')
  box('V2_Foremid_OuterPort_Pier_'+str((i,x)),(x,54.12,z),(.30,3.08,.4),ivory,'source receiving pier outside4m lower axis')
 box('V2_Foremid_OuterPort_Beam_'+str(i),(-5.4,55.615,z),(16.4,.13,.55),metal,'outer-port annex cantilever candidate, foundation/capacity held')
 if -240<=z<=-200:box('V2_Foremid_OuterPort_PlatformJoist_'+str(i),(-10.5,55.79,z),(5.4,.22,.55),metal,'positive platform/beam receiving overlap')
marker('V2_Foremid_BOARDING_BRIDGE_STOW_AXIS',(-7.8,56.1,-216),'port sillX−6.7074;1.0926m reach; root interlocked bridge')
# Reflect the completed new foremid proposal, with the actual aft-core opening retained.
current=collections['AFT_MIDSHIP_STATIC_SOURCE']
for row in aft_seed:
 ob=cp(row,lambda p:(p[0],p[1],-p[2]),current,'Aftmid_',True)
 if row['type']!='MESH' and row['name']=='V2__CORE_TRANSFER_D09':ob.location=B((1,52.5,259))
 if row['type']!='MESH' and row['name']=='V2__REUSE_COMMONS_LIFT_ROOT':ob['datum_kind']='yaw−PI/2 standard cabin; same local two stops'
for label,sig,file,core in [('FORE_MIDSHIP',1,'AST-TRM-G4-010_fore_midship_source.glb',-272),('AFT_MIDSHIP',-1,'AST-TRM-G4-012_aft_midship_source.glb',272)]:
 zlo,zhi=sorted([-228*sig,-204*sig]);rec=[3.4,-232.4*sig,7.8,-228.4*sig];rec[1],rec[3]=sorted([rec[1],rec[3]])
 stations.append({'label':label,'asset':file,'catchment_z':-216*sig,'actual_core_z':core,'platform_xz':[-3.4,zlo,2,zhi],'track_x':-5.6,'boarding_edge_x':-3.4,'lift_root':[5.6,0,-228.6*sig],'lift_yaw_rad':sig*math.pi/2,'lower_lift_recess_xz':rec,'recess_existing_slab_overlap_m2':2.4,'lower_missing_only_strip_xz':[4,min(-232.4*sig,-211*sig),7.8,max(-232.4*sig,-211*sig)],'emergency_flight_width_m':1.44,'emergency_status':'compact secondary source stair only; cart and broad-species movement uses reused4m lift; accessibility acceptance held','lower_floor_exported':False})
 if label=='FORE_MIDSHIP':stations[-1].update(platform_xz=[-13.2,-228,-7.8,-204],boarding_edge_x=-7.8,lift_root=[-11.2,0,-200],lift_yaw_rad=-math.pi/2,lower_lift_recess_xz=[-13.4,-200.2,-9,-196.2],recess_existing_slab_overlap_m2=0,lower_missing_only_strip_xz=[-13.4,-240.5,-4,-196.2],emergency_flight_width_m=2.4,emergency_status='original full-width2.4m secondary stairs on outer port side',station_side='outer port, independently screened to preserve Thread&Shell canopy and Orchard',pit_status='17.6m² exclusion in new missing-only annex, zero existing floor cut')
# Central six-metre catchment remains at−72 and on the unchanged axial bypass.
current=collections['CENTRAL_STATIC_SOURCE']
for row in old['CENTRAL_STATIC_SOURCE']:
 n=row['name']
 if not any(s in n for s in ['Boarding_Post_','Boarding_Header','LocalCanopy','Canopy_Recess','PodRoof_','BOARDING_GATE_MOUNT','LIGHT_DATUM_','Lamp_Backplate_','Perch_']):continue
 cp(row,lambda p:p,current)
box('V2_Central_BoardingFloor',(-5,55.975,-71.6),(5.6,.25,6.8),stone,'single nonoverlapping central platform/lift turn floor')
for a,b in [(-75,-72.5),(-68.5,-68.2)]:guard('V2_Central_Outer_'+str(a),-7.73,a,b,56.1)
for a,b in [(-75,-73.2),(-70.8,-68.2)]:guard('V2_Central_Tram_'+str(a),-2.24,a,b,56.1)
endguard('V2_Central_NorthEnd',-75,-7.8,-2.2);endguard('V2_Central_SouthEnd',-68.2,-3.4,-2.2)
# Lift local housing from original foremid rotated/translated to the existing broad apron.
for row in old['FORE_MIDSHIP_STATIC_SOURCE']:
 n=row['name']
 if n.startswith('BoardingLift_') and n!='BoardingLift_UpperLanding':cp(row,lambda p:(p[0],p[1],p[2]+131.8),current,'V2_Central__')
marker('V2_Central_COMMONS_LIFT_ROOT',(-5.6,0,-68.2),'yaw−PI/2, localgate0; heights52.5/56.1; existing fore-apron recess17.6m²')
for y in [52.5,56.1]:marker('V2_Central_LIFT_GATE_'+str(y),(-5.6,y,-68.2),'toward−Z, standard cabin/gates reused by root')
# Compact independent secondary stair outside both the port tie and existing core.
for row in old['FORE_MIDSHIP_STATIC_SOURCE']:
 if row['name'].startswith(('Emergency_','Upper_Approach_','LOWER_STAIR_','UPPER_STAIR_')):cp(row,lambda p:(-11.38+(p[0]+4.9)*.6,p[1],p[2]+160.4),current,'V2_Central__')
box('V2_Central_StairReturn',(-8.78,55.975,-70.5),(1.96,.25,4),stone,'upper stair crossreturn to port platform')
for z in [-72.5,-68.5]:endguard('V2_Central_StairReturnGuard_'+str(z),z,-9.76,-7.8)
marker('V2_Central_CORE_TRANSFER_D09',(-1,52.5,-80),'retained primary-core aft opening,28m catchment offset on lower fore-apron')
marker('V2_Central_CATCHMENT',(0,56.1,-72),'unchanged approved axial arrival and protected starboard bypass')
marker('V2_Central_GUEST_ABSTRACT_WAIT',(-11.8,52.5,-65),'future screened abstract transit edge, no physical cart duplication')
stations.append({'label':'CENTRAL','asset':'AST-TRM-G4-014_central_source.glb','catchment_z':-72,'actual_core_z':-100,'platform_xz':[-7.8,-75,-2.2,-68.2],'track_x':0,'boarding_edge_x':-2.2,'lift_root':[-5.6,0,-68.2],'lift_yaw_rad':-math.pi/2,'lower_lift_recess_xz':[-7.8,-68.4,-3.4,-64.4],'recess_existing_slab_overlap_m2':17.6,'lower_missing_only_strip_xz':None,'emergency_flight_width_m':1.44,'lower_floor_exported':False,'central_access_recoordination':'existing lower apron connects actual core to new lift/stair; previous elevated port core connector omitted because it conflicts selected trunk'})
# Continuous source rail, selected port outside exact protected central authority.
route_gate=json.loads((W/'SELECTED_ROUTE_SOURCE_GATE.json').read_text());assert all(not c['source_triangle_aabb_contacts'] and not c['stair_reserved_headroom_contacts'] and not c['group7_plan_contacts'] for c in route_gate['checks'])
curve=json.loads((W/'BYPASS_COMPACT_LONG_BODY_CURVATURE.json').read_text());chosen=curve['selected_source_candidate'];assert chosen['radius_m']==2.2
route=[(-5.6,-466),(-5.6,-85.3)]
route += [(-5.6*(1+math.cos(math.pi*t))/2,-85.3+13.3*t) for t in [i/64 for i in range(1,65)]]
for s in chosen['segments']:
 if s['kind']=='line':route.append(tuple(s['end']))
 else:
  for i in range(1,33):a=s['angle0']+s['delta']*i/32;route.append((s['center'][0]+s['radius']*math.cos(a),s['center'][1]+s['radius']*math.sin(a)))
route += [(-5.6*(1-math.cos(math.pi*t))/2,72+20*t) for t in [i/64 for i in range(1,65)]];route.append((-5.6,466))
# Split long straights into8m editable rail panels, curves keep their bounded sample tessellation.
pts=[route[0]]
for a,b in zip(route,route[1:]):
 dist=math.hypot(b[0]-a[0],b[1]-a[1]);steps=max(1,math.ceil(dist/8))
 for i in range(1,steps+1):pts.append((a[0]+(b[0]-a[0])*i/steps,a[1]+(b[1]-a[1])*i/steps))
current=collections['CONTINUOUS_GUIDEWAY_SOURCE']
def ribbon(name,offset,width,y0,y1):
 vs=[]
 for i,p in enumerate(pts):
  if i==0:v=Vector((pts[1][0]-p[0],0,pts[1][1]-p[1]))
  elif i==len(pts)-1:v=Vector((p[0]-pts[i-1][0],0,p[1]-pts[i-1][1]))
  else:v=Vector((pts[i+1][0]-pts[i-1][0],0,pts[i+1][1]-pts[i-1][1]))
  v.normalize();n=Vector((v.z,0,-v.x))
  for y,w in [(y0,offset-width/2),(y0,offset+width/2),(y1,offset-width/2),(y1,offset+width/2)]:vs.append((p[0]+n.x*w,y,p[1]+n.z*w))
 fs=[(0,2,3,1)]
 for i in range(len(pts)-1):
  a=4*i;b=a+4;fs += [(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)]
 a=4*(len(pts)-1);fs.append((a,a+1,a+3,a+2));return mesh(name,vs,fs,metal,'continuous source rail/web, no operating controller')
ribbon('V2_Continuous_Web',0,3.2,55.55,55.68)
for off in [-.86,.86]:ribbon('V2_Continuous_Rail_'+str(off),off,.09,55.68,55.74)
# Bounded receiving pads: real D09 axial feet outside cores; core rail hangs from actual D10 slab.
compiled=json.loads((R/'Game/data/generated/structural_meshes.json').read_text());receivers=[];held=[]
def covered(q,r):
 def sg(a,b,c):return (a[0]-c[0])*(b[1]-c[1])-(b[0]-c[0])*(a[1]-c[1])
 return any(not(min(v:= [sg(q,t[0],t[1]),sg(q,t[1],t[2]),sg(q,t[2],t[0])])< -1e-7 and max(v)>1e-7) for t in r['triangles'])
def owners(x,z,y):return [r['id'] for r in compiled['regions'] if r['floor_y']==y and covered((x,z),r)]
cores=[-432,-272,-100,272,432]
for z in range(-460,461,8):
 if -90<z<100:continue
 if -228<=z<=-204 or 204<=z<=228:continue
 core=next((c for c in cores if c-13<=z<=c+20),None)
 if core is None:
  for x in [-2.4,2.4]:
   own=owners(x,z,52.5)
   if len(own)!=1:held.append({'xyz':[x,52.5,z],'reason':'D09 receiver not unique','owners':own});continue
   box('V2_Trunk_Foot_'+str((x,z)),(x,52.54,z),(.42,.08,.75),metal,'actual D09 receiving foot')
   box('V2_Trunk_Pier_'+str((x,z)),(x,54.12,z),(.3,3.08,.4),ivory,'receiving pier outside4m ground axis')
   receivers.append({'xyz':[x,52.5,z],'owner':own[0],'type':'D09 slab contact'})
  box('V2_Trunk_Cantilever_'+str(z),(-2.3,55.615,z),(10.2,.13,.55),metal,'cantilever receiving beam, structural capacity held')
 else:
  for x in [-7.35,-3.9]:
   own=owners(x,z,61)
   if len(own)!=1:held.append({'xyz':[x,60.76,z],'reason':'D10 receiver not unique','owners':own});continue
   box('V2_Core_RailHanger_'+str((x,z)),(x,58.255,z),(.1,5.01,.1),metal,'rail hanger to actual D10 core slab')
   box('V2_Core_RailBearing_'+str((x,z)),(x,60.775,z),(.24,.07,.36),metal,'named slab underside bearing')
   receivers.append({'xyz':[x,60.76,z],'owner':own[0],'type':'D10 underside contact'})
# Central/tie framing left explicitly held where atrium receiving choices need root integration.
held.append({'scope':'north/south ties and central starboard bypass','reason':'source rail only; local existing central apron station bearings retained, continuous atrium receiving frame not supplied. No protected floor cut or borrowed support capacity.'})
for p in [(-5.6,-466),(-5.6,-85.3),(0,-72),(0,72),(-5.6,92),(-5.6,466)]:marker('V2_LINE_INTERFACE_'+str(p),(p[0],56.1,p[1]),'source guideway datum, root operating/receiving integration pending')
# Deterministic compact exports via fixed sorted selections. Keep individual native editable members.
exports=[('FORE_MIDSHIP_STATIC_SOURCE','AST-TRM-G4-010_fore_midship_source.glb'),('TRAM_EDITABLE_COMPONENT','AST-TRM-G4-011_cart_tram_component.glb'),('AFT_MIDSHIP_STATIC_SOURCE','AST-TRM-G4-012_aft_midship_source.glb'),('FORWARD_STATIC_SOURCE','AST-TRM-G4-013_forward_source.glb'),('CENTRAL_STATIC_SOURCE','AST-TRM-G4-014_central_source.glb'),('AFT_STATIC_SOURCE','AST-TRM-G4-015_aft_source.glb'),('CONTINUOUS_GUIDEWAY_SOURCE','AST-TRM-G4-016_continuous_guideway.glb')]
for co,file in exports:
 bpy.ops.object.select_all(action='DESELECT')
 for ob in sorted(collections[co].objects,key=lambda o:o.name):ob.select_set(True)
 bpy.context.view_layer.objects.active=next(iter(collections[co].objects))
 bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
rows=[{'mesh':ob.name,'collection':ob.users_collection[0].name,'role':ob['role'],'policy':ob['collision_policy'],'min':bnd(ob)[0],'max':bnd(ob)[1],'faces':len(ob.data.polygons)} for ob in parts]
(W/'MESH_PARTS.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
for i in stations:
 i.update(reuse_cabin='AST-CIR-003.glb',reuse_controller='Game/scripts/commons_lift.gd',local_gate_origin_xz=[0,0],floor_heights=[52.5,56.1],deck_numbers=[9,9],stop_ids=['G4_'+i['label']+'_LOWER','G4_'+i['label']+'_BOARDING'],vehicle_door_side=('port' if i['label'] in ['CENTRAL','FORE_MIDSHIP'] else 'starboard'),nominal_portal_post_spacing_m=2.4,actual_portal_clear_length_m=2.22,bridge_usable_width_proposal_m=2.18,boarding_width_m=2.18,bridge_geometry_status='root-owned moving bridge2.18m fits actual2.22m station and2.33m vehicle aperture; mounts only',bridge_reach_m=abs(i['boarding_edge_x']-(i['track_x']+(-1.3*k if i['label'] in ['CENTRAL','FORE_MIDSHIP'] else 1.3*k))),source_only=True)
meta={'schema':'astraea.group4.source_successor.v2','family':FAMILY,'ids':IDS,'status':'SOURCE_ONLY_UNINSTALLED','whole_group_complete':False,'frozen_first_receipt_sha256':hashlib.sha256((F/'FROZEN_FIRST_BATCH.json').read_bytes()).hexdigest(),'alignment_choice':'Root selected continuous portX−5.6 outside exact unchanged central starboard bypass, preserving Orchard Exchange and Thread&Shell. This is next source proposal, no whole-world/runtime route acceptance.','protected_polyline_xz':curve['protected_polyline_xz'],'group7_reservations':curve['group7_reservations'],'stations':stations,'body':{'exterior_width_m':2.3,'length_m':4.88,'height_m':2.87,'bogie_chord_m':3,'wheel_gauge_m':1.72,'cart_dock':[0,0,.15],'front_stance':[0,0,-.95],'rear_cart_operator_stance':[0,0,1.77],'side_door_aperture_z':[-1.2,1.2],'doors':'both physical apertures open, root-powered doors not supplied','restraint_mounts':'recessed flush channel/anchor source bases only; no raised rail blocking caster entry, root moving clamps not supplied','controls':'existing E interactions retained; no parallel controller','cart':'custodian_cart_001 and all four loose product IDs unchanged, no duplicate cart exported'},'guideway':{'asset':exports[-1][1],'rail_head_y':55.74,'floor_y':56.1,'soffit_y':55.55,'corner_radius_m':2.2,'central_body_margin_pass_m':.15,'central_body_margin_fail_m':.2,'tie_body_margin_pass_m':.2,'route_points_xz':pts,'receiving_contacts':receivers,'held_receivers':held,'central_authority':'six-point protected polyline never edited; tangent fillets are source rail geometry within retained4m strip'},'source_input_pins':route_gate['source_pins'],'remaining':['actual receiving floor fills and five bounded lift pits','central/tie receiving frame, all foundation/hull/load capacity checks','root existing cabin/gate/controller reuse and operating interfaces','closed tram doors, withdrawable bridge, steering/bogies, cart restraints, motion/safe stop/pause/save','five normal boarding and arrivals, remaining destination/neighborhood links','NPC finite-time abstract transit and screened boarding arrangements','bounded actual-main fit/import checks and source integration','in-engine/CRT/player-species/lighting/material/GPU final acceptance'],'acceptance':'Source construction and bounded source tests only. No installation, wholeGroup4 completion, transport operation or final art claim.'}
(W/'SUCCESSOR_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
# Preserve textures locally packed, with verified retained source hashes, no new textures/caches.
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
collections['TRAM_EDITABLE_COMPONENT'].hide_render=True
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(W/'Group4_Port_Successor_002.blend'),compress=True)
print('SUCCESSOR_SOURCE_EXPORTED',len(parts),'editable meshes',len(receivers),'receivers',len(held),'held receiving records')
