from pathlib import Path
import json,copy
W=Path(__file__).resolve().parent;p=json.load(open(W/'RUNTIME_PLAN.json'));p['revision']='r005';p['previous_native_export_records']=copy.deepcopy(p['native_export_records']);parts={a['name']:a for a in p['parts']}
def bounds(q,lo,hi):
 old=[min(v[i]for v in q['verts'])for i in range(3)];q['verts']=[[lo[i]if abs(v[i]-old[i])<1e-8 else hi[i]for i in range(3)]for v in q['verts']]
specs={'D04PC_Hatch_928_0':(-429.55,-427.35,False),'D04PC_Hatch_952_1':(-434.05,-431.75,True),'D04PC_ToolPane_928_0':(-429.38,-427.40,False),'D04PC_ToolPane_952_1':(-434.0,-431.92,True)}
for g in p['gates']:
 if g['name']not in specs:continue
 n=g['name'];a,b,upper=specs[n];old=g['service_opening_z'];tool='ToolPane'in n;lo=[-58.76,17.72 if tool else16.52,a+(.02 if tool else.16)];hi=[-58.70,18.53 if tool else17.57,b-(.032 if tool else.16)];bounds(parts[n+'_Leaf'],lo,hi);g.update(leaf_min=lo,leaf_max=hi,closed_center=[(x+y)/2 for x,y in zip(lo,hi)],pivot=[-58.70,17.7 if tool else16.5,hi[2]if upper else lo[2]],candidate_open_degrees=-90 if upper else90,service_opening_z=[a,b])
 for side,x in [('Home',hi[0]),('Outer',lo[0]-(.04 if tool else.055))]:
  z=lo[2]+.09 if upper else hi[2]-.25;bounds(parts[n+'_Handle_'+side],[x,18.08 if tool else17.16,z],[x+(.04 if tool else.055),18.22 if tool else17.34,z+.16])
 for k,(z,Z)in enumerate([(a,lo[2]),(hi[2]if not tool else b-.02,b)]):bounds(parts[n+'_Jamb_'+str(k)],[-58.95,17.7 if tool else16.5,z],[-58.70,18.55 if tool else17.65,Z])
 if tool:bounds(parts[n+'_Control'],[-58.70,17.92,b-.018],[-58.62,18.12,b+.068]);g['control_at']=[-58.619,18.02,b+.025];g['tool_pane_width_m']=b-a
 else:bounds(parts[n+'_Control'],[-58.695,17.36,b-.14],[-58.62,17.56,b-.04]);g['control_at']=[-58.61,17.46,b-.09];bounds(parts[n+'_FixedHead'],[-58.95,17.57,lo[2]],[-58.70,17.65,hi[2]])
 for cut in p['cuts']:
  if cut['name']==f'D04H{g["home_index"]}_'+('GardenGlass'if tool else'GardenDado'):
   for v in cut['volumes']:
    if abs(v['min'][2]-old[0])<.001:v['min'][2]=a;v['max'][2]=b
# Fixed thin bars on the WEST mouth never enter the homeward leaf swings.
# Their spacing bounds every person-width gap, while tools pass between them.
ns={'__file__':str(W/'widen_middle_tool_reach.py')};R=W.parents[2];s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();exec(s[:s.index('from shapely import affinity')],ns)
for idx,(a,b)in [(928,(-429.55,-427.35)),(952,(-434.05,-431.75))]:
 z=a+.38;i=0
 while z<b-.12:
  ns['cube'](f'D04PC_FixedToolBarrier_{idx}_{i}',[-58.98,16.5,z-.012],[-58.96,18.55,z+.012],category='person_access_barrier');z+=.4;i+=1
p['parts'].extend(ns['parts']);p['maintenance_method'].update(middle_planter_source_wall_thickness_explicit=True,fixed_west_mouth_bar_pitch_m=.4,maximum_person_width_gap_m=.38,upper_middle_panes_widened_for_oblique_tool_reach=True,low_upper_openings_separated_by_fixed_header=True,standing_worker_capsule_diameter_m=.6);(W/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');print('MIDDLE_REACH_REVISION',len(ns['parts']))
