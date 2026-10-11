from pathlib import Path
import json,copy
W=Path(__file__).resolve().parent
R=W.parents[2]
p=json.load(open(W/'RUNTIME_PLAN.json'))
p['revision']='r006'
p['previous_native_export_records']=copy.deepcopy(p['native_export_records'])
parts={q['name']:q for q in p['parts']}
def resize(q,lo,hi):
 old=[min(v[i]for v in q['verts'])for i in range(3)]
 q['verts']=[[lo[i]if abs(v[i]-old[i])<1e-8 else hi[i]for i in range(3)]for v in q['verts']]
for g in p['gates']:
 if g['name']not in ['D04PC_ToolPane_928_1','D04PC_ToolPane_952_0']:
  continue
 n=g['name'];old=g['service_opening_z'];a,b=(-425.45,-424.05)if g['home_index']==928 else(-436.65,-435.4)
 lo=[-58.76,17.72,a+.16];hi=[-58.70,18.53,b-.16]
 resize(parts[n+'_Leaf'],lo,hi)
 g.update(leaf_min=lo,leaf_max=hi,closed_center=[(x+y)/2 for x,y in zip(lo,hi)],pivot=[-58.70,17.7,lo[2]],candidate_open_degrees=90,service_opening_z=[a,b],tool_pane_width_m=b-a)
 for side,x in [('Home',hi[0]),('Outer',lo[0]-.04)]:
  resize(parts[n+'_Handle_'+side],[x,18.08,hi[2]-.25],[x+.04,18.22,hi[2]-.09])
 resize(parts[n+'_Jamb_0'],[-58.95,17.7,a],[-58.70,18.55,lo[2]])
 resize(parts[n+'_Jamb_1'],[-58.95,17.7,hi[2]],[-58.70,18.55,b])
 resize(parts[n+'_Control'],[-58.70,17.92,b-.14],[-58.62,18.12,b-.04]);g['control_at']=[-58.619,18.02,b-.09]
 for c in p['cuts']:
  if c['name']==f'D04H{g["home_index"]}_GardenGlass':
   for volume in c['volumes']:
    if abs(volume['min'][2]-old[0])<.001:
     volume['min'][2]=a;volume['max'][2]=b
ns={'__file__':str(W/'finish_end_panes.py')}
s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text()
exec(s[:s.index('from shapely import affinity')],ns)
for idx,(a,b)in [(928,(-425.45,-424.05)),(952,(-436.65,-435.4))]:
 z=a+.38;i=0
 while z<b-.12:
  ns['cube'](f'D04PC_FixedEndToolBarrier_{idx}_{i}',[-58.98,16.5,z-.012],[-58.96,18.55,z+.012],category='person_access_barrier')
  z+=.4;i+=1
p['parts'].extend(ns['parts'])
p['maintenance_method']['upper_pane_widths_m']={g['name']:g['tool_pane_width_m']for g in p['gates']if 'tool_pane_width_m'in g}
p['maintenance_method'].pop('upper_tool_pane_width_m',None)
(W/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
print('END_TOOL_PANES',len(ns['parts']))
