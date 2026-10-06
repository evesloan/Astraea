"""Unbuilt room-composition revision, held for parent review. No writes on import."""
def add_north_services(p):
 p.BAY='WORKBAY';p.ASSEMBLY='NORTH_REPAIR_SERVICE_WALL'
 relocated=[c for c in p.controls if c['panel']=='TEST_RACK'];assert len(relocated)==24
 ids={c['id'] for c in relocated}
 p.parts[:]=[part for part in p.parts if not any(id in part['name'] for id in ids)]
 p.markers[:]=[marker for marker in p.markers if marker.get('control_id') not in ids]
 p.controls[:]=[control for control in p.controls if control['id'] not in ids]
 p.decal('EastRackRemoteDiagnostic',(32.98,7.41,-401.494),1.01,.63,20,-1)
 # Two anchored frames with real depths and an intentional open central machine bay.
 for i,x in enumerate([21.65,23.27,25.63,27.17]):
  foot=p.box('NorthServiceFoot'+str(i),(x-.15,6,-409.12,x+.15,6.11,-408.29),'staff_rubber',.026);p.contact('NorthServiceFloor'+str(i),foot,[x,6,-408.7],[0,-1,0],'compiler_floor_Y6')
  p.box('NorthServicePost'+str(i),(x-.055,6.09,-409.08,x+.055,(8.70 if i<2 else 8.37),-408.48),'staff_zinc',.017)
  p.plate('NorthServiceWallPad'+str(i),(x,8.42,-409.18),.28,.40,.08,'staff_zinc',.03);p.contact('NorthServiceWallSeat'+str(i),'NorthServiceWallPad'+str(i),[x,8.42,-409.22],[0,0,-1],'workbay_north_wall0')
  p.box('NorthServiceWallLink'+str(i),(x-.04,8.36,-409.14,x+.04,8.48,-408.49),'staff_zinc')
 # Split zinc shelves and shaped valve/relay modules, rather than a solid wall of boxes.
 for name,a,b in [('Return',21.55,23.38),('Relay',23.65,25.46),('Stock',25.51,27.28)]:
  p.plate('North'+name+'Crown',((a+b)/2,(8.65 if name!='Stock' else 8.25),-408.78),b-a+.10,.26,.86,'staff_white_paint',.075)
  p.box('North'+name+'Shelf',(a,6.37,-409.08,b,6.43,-408.31),'staff_zinc',.018)
  p.plate('North'+name+'Back',((a+b)/2,(7.43 if name!='Stock' else 7.20),-409.10),b-a,(2.16 if name!='Stock' else 1.75),.10,'staff_bluegrey_paint',.11)
 # Three deliberately large conduit/transducer silhouettes in the return zone.
 for j,x in enumerate([21.94,22.47,23.00]):
  p.cyl('NorthTransducer'+str(j),(x,7.29,-408.73),.155,1.34,'staff_white_paint','y',14)
  p.box('NorthTransducerFoot'+str(j),(x-.20,6.43,-408.92,x+.20,6.62,-408.52),'staff_bluegrey_paint',.016)
  p.contact('NorthTransducerSeat'+str(j),'NorthTransducer'+str(j),[x,6.62,-408.73],[0,-1,0],'NorthTransducerFoot'+str(j))
  for yy in [6.82,7.76]:p.cyl('NorthTransducerBand'+str((j,yy)),(x,yy,-408.73),.175,.075,'staff_zinc','y',14)
  p.box('NorthGaugeStem'+str(j),(x-.045,7.93,-408.75,x+.045,8.13,-408.575),'staff_zinc')
  p.gauge('NorthTransducerGauge'+str(j),(x,8.13,-408.57),.16,1,j)
  p.plate('NorthTransducerJunction'+str(j),(x,8.40,-408.80),.29,.24,.38,'staff_bluegrey_paint',.04)
  a=p.port('NorthTransducerTop'+str(j),[x,7.96,-408.73],[0,1,0],'NorthTransducer'+str(j),.056)
  b=p.port('NorthTransducerInput'+str(j),[x,8.28,-408.73],[0,-1,0],'NorthTransducerJunction'+str(j),.056)
  p.cable('NorthTransducerLead'+str(j),a,b,[],.034,'staff_cable_blue' if j==1 else 'staff_rubber')
 # Exposed repair cradle: stepped split housing, fins and a supported copper-coded bus.
 for x in [23.98,25.07]:p.box('NorthRelayCradle'+str(x),(x-.09,6.43,-408.94,x+.09,6.84,-408.42),'staff_zinc',.022)
 for i in range(6):
  x=23.88+i*.248;p.plate('NorthRelayFin'+str(i),(x,7.40,-408.72),.12,1.37,.48,'staff_white_paint',.055)
 p.box('NorthRelayLowerRail',(23.77,6.72,-408.94,25.27,6.83,-408.46),'staff_bluegrey_paint',.025)
 p.box('NorthRelayUpperRail',(23.77,8.03,-408.94,25.27,8.15,-408.46),'staff_zinc',.025)
 p.plate('NorthRelayCentre',(24.52,7.42,-408.61),1.03,.54,.40,'staff_bluegrey_paint',.095)
 p.louvres('NorthRelayCentreVent',24.52,7.42,-408.395,.83,6)
 # Useful stock cubbies have physical shelves/returns and shaped boxed cartridges.
 for j,y in enumerate([6.49,7.03,7.57]):
  p.box('NorthStockShelf'+str(j),(25.59,y,-409.04,27.18,y+.045,-408.39),'staff_zinc',.012)
  for i,x in enumerate([25.85,26.38,26.91]):
   p.plate('NorthStockCartridge'+str((j,i)),(x,y+.28,-408.72),.38,.47,.47,'staff_white_paint' if j==1 else 'staff_bluegrey_paint',.07)
   p.plate('NorthStockGrip'+str((j,i)),(x,y+.26,-408.47),.17,.075,.065,'staff_rubber',.025)
   p.decal('NorthStockTag'+str((j,i)),(x,y+.39,-408.482),.23,.075,21+j,1)
 # Twenty-four exact stable remote-control identities are redistributed from the east rack.
 for side,x in [('L',23.63),('R',25.39)]:
  panel='NorthRemote_'+side;face=p.panel(panel,(x,7.43,-408.49),.51,.87,.15,1,14)
  first=0 if side=='L' else 12
  for index,c in enumerate(relocated[first:first+12]):
   row=index//3;col=index%3
   p.actuator(c['id'],'TEST_RACK_REMOTE_'+side,(x+(col-1)*.13,7.38+(row-1.5)*.14,face+.006),1,c['kind'],c['effect_candidate'])
  # A mechanical cross-member carries the narrow remote panel between real uprights.
  p.box(panel+'_BackRail',(x-.28,7.23,-409.06,x+.28,7.29,-408.56),'staff_zinc')
  p.box(panel+'_TopRail',(x-.28,7.65,-409.06,x+.28,7.71,-408.56),'staff_zinc')
  a=p.port(panel+'_Output',[x,7.865,-408.49],[0,1,0],panel+'_shell',.035)
  p.plate(panel+'_HarnessBox',(24.08 if side=='L' else 25.11,8.40,-408.62),.25,.30,.30,'staff_bluegrey_paint',.035)
  xx=24.08 if side=='L' else 25.11
  b=p.port(panel+'_HarnessReceiver',[xx,8.25,-408.62],[0,-1,0],panel+'_HarnessBox',.035)
  p.cable(panel+'_ClimbingLead',a,b,[[x,8.04,-408.49],[xx,8.04,-408.62]],.022,'staff_cable_red' if side=='L' else 'staff_cable_blue')
 # Large upper loom wraps have real receiving boxes at both ends.
 for j,x in enumerate([24.02,24.52,25.02]):
  a=p.port('NorthRelayTop'+str(j),[x,8.15,-408.67],[0,1,0],'NorthRelayUpperRail',.048)
  p.plate('NorthLoomTerminal'+str(j),(x,9.21,-407.93),.19,.20,.23,'staff_bluegrey_paint',.035)
  b=p.port('NorthLoomInput'+str(j),[x,9.21,-408.045],[0,0,-1],'NorthLoomTerminal'+str(j),.048)
  dx=.20 if j==1 else 0
  p.cable('NorthRelayLoom'+str(j),a,b,[[x+dx,8.68,-408.67],[x+dx,8.97,-408.58],[x+dx,9.21,-408.23]],.031,['staff_rubber','staff_cable_blue','staff_cable_red'][j])
 # Second real ceiling spine over the north-side bank, away from door/headroom.
 p.ASSEMBLY='WORKBAY_NORTH_CEILING';p.service_spine('WorkbayNorthCeiling',20.9,27.5,-407.93,9.15,9.60)
 # West-side longitudinal return joins the old south and new north ceiling zones.
 for z in [-406.70,-404.60,-402.50]:
  pad=p.box('ReturnCapPad'+str(z),(20.48,9.55,z-.11,21.18,9.60,z+.11),'staff_zinc',.015);p.contact('ReturnCeilingSeat'+str(z),pad,[20.83,9.60,z],[0,1,0],'workbay_ceiling')
  for xx in [20.53,21.13]:p.box('ReturnHanger'+str((z,xx)),(xx-.021,9.28,z-.024,xx+.021,9.55,z+.024),'staff_zinc')
  p.box('ReturnCrossbar'+str(z),(20.49,9.26,z-.055,21.17,9.30,z+.055),'staff_zinc')
 for j,xx in enumerate([20.69,20.97]):
  for name,zz in [('South',-401.95),('North',-407.65)]:
   box_name=p.plate('Return'+name+'Box'+str(j),(xx,9.33,zz),.23,.29,.30,'staff_bluegrey_paint',.035)
   stem=p.box('Return'+name+'BoxStem'+str(j),(xx-.03,9.475,zz-.03,xx+.03,9.60,zz+.03),'staff_zinc')
   p.contact('Return'+name+'BoxCap'+str(j),stem,[xx,9.60,zz],[0,1,0],'workbay_ceiling')
   p.contact('Return'+name+'BoxSeat'+str(j),box_name,[xx,9.475,zz],[0,1,0],stem,'ceiling_hanger')
  a=p.port('ReturnSouth'+str(j),[xx,9.33,-402.10],[0,0,-1],'ReturnSouthBox'+str(j),.06)
  b=p.port('ReturnNorth'+str(j),[xx,9.33,-407.50],[0,0,1],'ReturnNorthBox'+str(j),.06)
  p.cable('WestCeilingReturn'+str(j),a,b,[],.045,'staff_rubber' if j==0 else 'staff_cable_blue')
 # Physical task housing mounted from the real bank, emitter forward of its hood.
 p.ASSEMBLY='NORTH_BANK_TASK_PROPOSAL'
 mount=p.box('NorthTaskMount',(24.40,8.78,-408.91,24.64,8.83,-408.61),'staff_zinc',.012)
 p.contact('NorthTaskCrownSeat',mount,[24.52,8.78,-408.76],[0,-1,0],'NorthRelayCrown')
 p.tube('NorthTaskArm',p.rounded([[24.52,8.82,-408.76],[24.52,8.97,-408.76],[24.52,8.97,-408.00],[24.52,8.82,-408.00]],.06),.032,'staff_zinc',10)
 p.plate('NorthTaskHousing',(24.52,8.76,-408.00),1.28,.13,.30,'staff_bluegrey_paint',.045)
 p.box('NorthTaskOpal',(23.95,8.676,-408.12,25.09,8.695,-407.88),'staff_opal',kind='none')
 p.marker('LIGHT_PROPOSAL_north_services',[24.52,8.66,-408.00],'fixture_exit',aim_xyz=[24.52,7.31,-408.58],active_runtime=False)
 p.ASSEMBLY=''
