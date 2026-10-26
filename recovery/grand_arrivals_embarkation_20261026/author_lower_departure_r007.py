"""Connected lower-hall boarding datum and original-section ground guideway."""
import json,pathlib,copy,math,hashlib,ast
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r007';assert not D.exists()
old=R/'Game/grand_arrivals_tram_20261026/r002/PLAN.json';plan=json.loads(old.read_text());points=plan['route_xyz'];parts=[]
prefix=[]
def line(a,b):
 n=max(1,math.ceil(math.dist(a,b)/.5))
 for i in range(n):prefix.append([a[0]+(b[0]-a[0])*i/n,.365,a[1]+(b[1]-a[1])*i/n])
def arc(c,r,a,b):
 n=max(1,math.ceil(abs(b-a)*r/.25))
 for i in range(n):
  t=a+(b-a)*i/n;prefix.append([c[0]+r*math.cos(t),.365,c[1]+r*math.sin(t)])
line([-12.6,-443],[-12.6,-455]);arc([-7.8,-455],4.8,math.pi,1.5*math.pi)
line([-7.8,-459.8],[.8,-459.8]);arc([.8,-455],4.8,-math.pi/2,0)
join=next(i for i,p in enumerate(points) if abs(p[0]-5.6)<1e-6 and abs(p[2]+455)<1e-6)
points=prefix+points[join:];plan['route_xyz']=points

end=next(i for i,p in enumerate(points) if abs(p[0]-5.6)<1e-6 and abs(p[2]+390)<1e-6);end_y=points[end][1];slope=22.2/305
for i,p in enumerate(points[:end+1]):
 x,y,z=p
 if i==end:continue
 if z<=-405:y=.365
 else:
  u=(z+405)/15;y=(2*u**3-3*u*u+1)*.365+(-2*u**3+3*u*u)*end_y+(u**3-u*u)*15*slope
 points[i]=[x,y,z]
assert all(points[i+1][1]>=points[i][1]-1e-8 for i in range(end))
original=json.loads(old.read_text())['route_xyz'];original_end=next(i for i,p in enumerate(original) if abs(p[0]-5.6)<1e-6 and abs(p[2]+390)<1e-6);assert points[end:]==original[original_end:]
plan['schema']='astraea.grand_arrivals.lower_route.r007';plan['station'].update(dock_xyz=[-12.6,.365,-449],platform_y=.365,accessible_approach='Two adjacent 4 m ramp lanes, 7.3 m run at 1:20, received on original D01 hall; actual walking/cart/threshold checks pending')
plan['station']['platform_xz']=[-20.8,-454,-14.8,-444]
plan['pier_preservation']='Hall dock and first turn shifted 0.6m west to preserve original ARR_ProfiledBearingPier_4 and its bands; exit and all upper source coordinates unchanged.'
plan['route_length_m']=sum(math.dist(a,b) for a,b in zip(points,points[1:]));plan['lower_datum_reason']='Original wheel centre -.2, radius .16; root .365 gives rail top .005 above floor, preserving original wheel geometry. No ground trench or protected slab deletion.'
plan['unchanged_after_z']=-390;plan['source_predecessor_sha256']=hashlib.sha256(old.read_bytes()).hexdigest();plan['status']='CONNECTED_LOWER_DEPARTURE_SOURCE_UNSELECTED'
def mesh(name,vertices,faces,role,purpose):parts.append({'name':name,'vertices':vertices,'faces':faces,'material':role,'purpose':purpose})
def box(name,lo,hi,role,purpose):
 x,y,z=lo;X,Y,Z=hi;mesh(name,[[x,y,z],[X,y,z],[x,Y,z],[X,Y,z],[x,y,Z],[X,y,Z],[x,Y,Z],[X,Y,Z]],[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],role,purpose)
floorpath=R/'Game/data/generated/structural_meshes.json';floors=json.loads(floorpath.read_text())['regions']
tree=ast.parse((R/'recovery/grand_arrivals_embarkation_20261026/author_receiving_r002.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['area','clip']],type_ignores=[]),'protected_polygon','exec'))
def coverage(region,rect):
 result=0
 for tri in region['triangles']:
  p=tri
  for axis,v,above in [(0,rect[0],True),(0,rect[2],False),(1,rect[1],True),(1,rect[3],False)]:
   p=clip(p,axis,v,above)
   if not p:break
  if p:result+=abs(area(p))
 return result
hall=next(f for f in floors if f['id']=='D01_arrivals_ground');spine=next(f for f in floors if f['id']=='D01_fore_route')
footprints=[('platform',[-20.8,-454,-14.8,-444]),('ramp',[-28.1,-453,-20.8,-445])]
for name,rect in footprints:assert abs(coverage(hall,rect)-(rect[2]-rect[0])*(rect[3]-rect[1]))<1e-6,(name,'missing original floor')
box('FORWARD_LowerPlatform',[-20.8,0,-454],[-14.8,.365,-444],'warm_stone','Original D01 floor received; same FORWARD station identity, no capacity claim')
for side,z0,z1 in [('Boarding',-453,-449),('Alighting',-449,-445)]:
 mesh('FORWARD_'+side+'Ramp',[[-28.1,0,z0],[-20.8,.365,z0],[-20.8,.365,z1],[-28.1,0,z1],[-28.1,-.03,z0],[-20.8,-.03,z0],[-20.8,-.03,z1],[-28.1,-.03,z1]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'warm_stone','4m clear ramp lane on retained floor; separated flow intent, not operating throughput')
for name,z0,z1 in [('North',-454,-450.11),('South',-447.89,-444)]:
 box('FORWARD_'+name+'PlatformPlinth',[-14.91,.365,z0],[-14.73,.525,z1],'warm_walnut','Station edge leaves original 2.22m portal aperture')
 box('FORWARD_'+name+'PlatformGlass',[-14.845,.525,z0],[-14.81,1.605,z1],'ArrivalsArchitecturalGlass','Retained transparent material; actual portal and bridge reuse still to bind')
 box('FORWARD_'+name+'PlatformCap',[-14.88,1.605,z0],[-14.78,1.685,z1],'champagne_metal','Guest guard cap')
for name,z in [('North',-454),('South',-444)]:
 box('FORWARD_'+name+'ReturnGlass',[-20.8,.525,z-.02],[-14.8,1.605,z+.02],'ArrivalsArchitecturalGlass','Protect platform side without closing ramp mouths')
 box('FORWARD_'+name+'ReturnCap',[-20.8,1.605,z-.05],[-14.8,1.685,z+.05],'champagne_metal','Connected side guard')
# Bridge only the measured four-metre missing floor between hall and spine.
gap=[-8,-462.8,-4,-456.8];assert coverage(hall,gap)<1e-6 and coverage(spine,gap)<1e-6
bearings=[('Hall',hall,[-8.3,-462.8,-8,-456.8]),('Spine',spine,[-4,-462.8,-3.7,-456.8])]
for name,f,rect in bearings:assert abs(coverage(f,rect)-1.8)<1e-6,(name,'missing bearing')
box('LowerExit_MissingOnlyFloor',[-8,-.24,-462.8],[-4,0,-456.8],'warm_stone','Exact missing-only connection; 1.8m2 bearing at each original receiver')
for i,z in enumerate([-462.5,-460.7,-458.9,-457.1]):box('LowerExit_ReceivedGirder_'+str(i),[-8.3,-.45,z-.10],[-3.7,-.18,z+.10],'champagne_metal','Embed into original hall/spine slabs; strength certification remains open')
for name,z in [('North',-462.8),('South',-456.8)]:
 box('LowerExit_'+name+'Glass',[-8.25,.16,z-.02],[-3.75,1.28,z+.02],'ArrivalsArchitecturalGlass','Guard actual bridge edge outside opening envelope')
 box('LowerExit_'+name+'Cap',[-8.25,1.28,z-.05],[-3.75,1.36,z+.05],'champagne_metal','Bridge guard return')
# Original rail section: 90mm heads, 60mm depth, 1.72m gauge, 3.2m web.
rail=points[:end+1]
for name,offset,half,top,bottom in [('LowerRail_Port',-.86,.045,-.36,-.42),('LowerRail_Starboard',.86,.045,-.36,-.42),('LowerRail_OriginalSectionWeb',0,1.6,-.42,-.55)]:
 verts=[];faces=[]
 for i,p in enumerate(rail):
  a=rail[max(i-1,0)];b=rail[min(i+1,len(rail)-1)];t=[b[j]-a[j] for j in range(3)];norm=math.sqrt(sum(v*v for v in t));t=[v/norm for v in t];h=math.hypot(t[0],t[2]);right=[t[2]/h,0,-t[0]/h];up=[t[1]*right[2]-t[2]*right[1],t[2]*right[0]-t[0]*right[2],t[0]*right[1]-t[1]*right[0]]
  for dx,dy in [(offset-half,bottom),(offset+half,bottom),(offset+half,top),(offset-half,top)]:verts.append([p[j]+right[j]*dx+up[j]*dy for j in range(3)])
  if i:
   for k in range(4):faces.append([4*(i-1)+k,4*(i-1)+(k+1)%4,4*i+(k+1)%4,4*i+k])
 faces.extend([[3,2,1,0],[len(verts)-4,len(verts)-3,len(verts)-2,len(verts)-1]])
 mesh(name,verts,faces,'champagne_metal','Original section dimensions on authored lower rail; wheel rolling contact intentional; no dynamic or traction acceptance')
D.mkdir(parents=True)
receipt={'selected':False,'source_floor_sha256':hashlib.sha256(floorpath.read_bytes()).hexdigest(),'platform_received_m2':60,'ramp_received_m2':58.4,'ramp_gradient':.05,'clear_lane_widths_m':[4,4],'missing_only_exit_floor_m2':24,'exit_original_bearings_m2':[1.8,1.8],'original_wheel_radius_m':.16,'original_wheel_centre_local_y':-.2,'rail_top_y':.005,'car_floor_y':.365,'original_bridge_reach_m':1.0925925925925921,'portal_clear_z':[-450.11,-447.89],'baggage_service':'Original service boundary, staff door and staffed handoff untouched; baggage custody remains unimplemented','holds':['Exact supported hall opening','Original open/closed portal and bridge binding','Complete station and forward-core room thresholds','Under-guideway support and original ground contact check','Guest circulation, grade hardware, rider operation and visual acceptance','Arrival-wave capacity/headway evidence']}
for name,value in [('PLAN.json',plan),('PARTS.json',parts),('RECEIVING.json',receipt)]: (D/name).write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'parts':len(parts),'route_rejoins_unchanged_z':-390,'car_floor_y':.365,'original_floor_received':True,'selected':False}))
