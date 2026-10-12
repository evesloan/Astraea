"""Actual exported stairs, upper approaches and retained moving-cabin fit.

Pure raw GLB inspection: this never imports into Godot or claims adopted floors.
"""
import pathlib,sys,json,math,hashlib
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from source_paths import section
from premium_frame import PremiumFrame
from glb_tools import read_glb,projected_grid,route_check
from reconcile_house_adjunct import clip_axis
unit=int(sys.argv[1]);row,O,native,export=section(unit)
c=json.loads((O/'SECTION_CONTRACT.json').read_text());frame=PremiumFrame(c['reservation']['proposed_floor_boundary'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(native)==c['native_sha256'] and sha(export)==c['export_sha256']
g,nodes=read_glb(export);lookup={n['name']:n for n in nodes};fails=[];stairs=[]
def path(points):return [(frame.world(u,v)[0],frame.world(u,v)[2]) for u,v in points]
def sweep(name,points,floor,radius=.38,height=2.25):
 polys,grid=projected_grid(nodes,floor,height);result=route_check(polys,grid,path(points),radius);result['name']=name;result['floor_y']=floor
 if not result['passed']:fails.append(result)
 return result
for rec in c['private_stair_records']:
 node=lookup[rec['object']];top=102+rec['top_h'];error=abs(node['bounds'][1][1]-top)
 if error>.0002:fails.append({'stair_actual_top':rec['object'],'error_m':error})
 u=sum(rec['u'])/2;v=sum(rec['v'])/2
 # A body on steps clears above the next18cm riser. Treads/stringers remain
 # in the actual scene; only the lowest30cm leg volume is excluded.
 result=sweep(rec['object']+'_body',[(u,v),(u,v)],top+.30,height=1.95)
 stairs.append({'object':rec['object'],'actual_top_y':node['bounds'][1][1],'actual_top_error_m':error,'run_m':rec['run_m'],'declared_width_m':rec['width_m'],'upper_body_sweep':result})
bridge=lookup.get('PrivateStairUpperLanding')
if not bridge:fails.append({'missing_actual_upper_landing_bridge':True})
else:
 loc=[frame.inverse((p[0],-p[2],p[1])) for p in bridge['vertices']]
 bounds=[[min(p[i] for p in loc) for i in range(3)],[max(p[i] for p in loc) for i in range(3)]]
 if abs(bounds[1][2]-4.5)>.0002 or bounds[0][1]>14.8501 or bounds[1][1]<15.2799:fails.append({'upper_bridge_actual_bounds':bounds})
for name in ['StairUpperVoidLeftPanel','StairUpperVoidInnerPanel','StairUpperVoidRearPanel','StairUpperVoidForePanel']:
 if name not in lookup:fails.append({'missing_actual_void_guard':name})
routes=[sweep('upper_stair_exit_to_lift',[(3.35,15.42),(3.35,14.4),(3.35,13),(7,13),(7,15.3)],106.525),sweep('upper_viewing_approach',[(7,13),(10.6,13),(13.4,13),(16.4,13)],106.525),sweep('lower_lift_landing',[(4,9.2),(4.4,13),(7,13),(7,15.3)],102.025)]
# Rigid cabin fit is measured in its own unchanged native axes. The actual
# exported mesh is mapped back from Y-up, preserving every component.
lift=c['private_lift_proposal'];cp=R/lift['cabin_export'];_,cn=read_glb(cp)
cab=[(p[0],-p[2],p[1]) for n in cn for p in n['vertices']]
cb=[[min(p[k] for p in cab) for k in range(3)],[max(p[k] for p in cab) for k in range(3)]]
inner=lift.get('rigid_shaft_inner_box_cabin_native_xyz',[[-2.02,-.02,0],[2.02,3.64,7.5]])
fit={'retained_cabin_glb_sha256':sha(cp),'actual_cabin_native_axis_bounds':cb,'shaft_inner_cabin_axis_bounds':inner,'horizontal_clearance_m':[cb[0][0]-inner[0][0],inner[1][0]-cb[1][0],cb[0][1]-inner[0][1],inner[1][1]-cb[1][1]],'upper_roof_clearance_m':inner[1][2]-(4.5+cb[1][2]),'Root_pit_required_m':-cb[0][2],'controller_and_transfer_acceptance':'HELD'}
if min(fit['horizontal_clearance_m'])<.0198 or fit['upper_roof_clearance_m']<.0598:fails.append({'retained_cabin_rigid_fit':fit})
origin=lift['lower_origin_world'];yaw=lift['proper_yaw_radians'];co,si=math.cos(yaw),math.sin(yaw);walls=[]
for n in nodes:
 if not n['name'].startswith(('LiftLeft','LiftRight','LiftRear','LiftFront','LiftDoorHeader','LiftShaftCap')):continue
 ps=[]
 for p in n['vertices']:
  dx=p[0]-origin[0];dy=-p[2]+origin[2];ps.append((dx*co+dy*si,-dx*si+dy*co,p[1]-origin[1]))
 bounds=[[min(p[k] for p in ps) for k in range(3)],[max(p[k] for p in ps) for k in range(3)]];walls.append((n['name'],bounds))
collisions=[]
for stop in [0,4.5]:
 for n in cn:
  ps=[(p[0],-p[2],p[1]+stop) for p in n['vertices']]
  for name,bounds in walls:
   for tri in n['triangles']:
    poly=[ps[k] for k in tri]
    for axis in range(3):
     poly=clip_axis(poly,axis,bounds[0][axis]+.0002,True);poly=clip_axis(poly,axis,bounds[1][axis]-.0002,False)
    if poly:collisions.append({'cabin_stop_offset_y':stop,'cabin_mesh':n['name'],'shaft_mesh':name,'actual_triangle':tri,'overlapping_clipped_vertices_in_cabin_axes':poly});break
if collisions:fails.append({'actual_retained_cabin_shaft_solid_overlap':collisions})
fit['actual_cabin_triangles_tested_against_saved_shaft_boxes']=True;fit['actual_solid_overlaps']=collisions
data={'status':'FAIL' if fails else 'PASS','native_sha256':sha(native),'export_sha256':sha(export),'stairs':stairs,'routes':routes,'retained_cabin_fit':fit,'failures':fails,'limits':['Actual source geometry only; upper receiver floor, slab voids and support held Root','No stair/lift accessibility, moving controller or installed actor certification','Conversation terrace remains a separate Root floor proposal, not constructed source floor']}
out=O/'PRIVATE_LEVELS_VERIFICATION.json';out.write_text(json.dumps(data,indent=2));print('ACTUAL PRIVATE LEVELS',unit,data['status'],len(fails))
if fails:raise RuntimeError('Preserve actual private-level evidence before repair')
c.setdefault('additional_source_files',{})[out.relative_to(R).as_posix()]=sha(out);c['additional_source_files']['verify_private_levels.py']=sha(pathlib.Path(__file__));(O/'SECTION_CONTRACT.json').write_text(json.dumps(c,indent=2))
