from pathlib import Path
import json,hashlib,copy,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'RUNTIME_PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();p['revision']='r003';p['previous_native_export_records']=copy.deepcopy(p['native_export_records'])
reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles']
ns2={'__file__':str(W/'add_upper_reach_panes.py')};s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();exec(s[:s.index('from shapely import affinity')],ns2);cube=ns2['cube'];parts=ns2['parts']
panes={928:[(-429.38,-428.98),(-424.62,-424.22)],952:[(-436.48,-436.08),(-432.32,-431.92)]}
for idx,rows in panes.items():
 model=f'D04_PORT_FORWARD_HOME_{idx}_r001.glb';name=f'D04H{idx}_GardenGlass';tri=dict(T(model))[name];v=tri.reshape(-1,3)
 p['cuts'].append({'source_model':model,'name':name,'source_triangles_sha256':hashlib.sha256(tri.tobytes()).hexdigest(),'source_triangle_count':len(tri),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'volumes':[{'min':[-58.951,17.7,a],'max':[-58.769,18.55,b]}for a,b in rows],'kind':'narrow_upper_tool_pane'})
 for j,(a,b)in enumerate(rows):
  n=f'D04PC_ToolPane_{idx}_{j}';lo=[-58.76,17.72,a+.02];hi=[-58.70,18.53,b-.02];cube(n+'_Leaf',lo,hi,role='hospitality_glass',category='moving_leaf')
  for side,x in [('Home',hi[0]),('Outer',lo[0]-.04)]:cube(n+'_Handle_'+side,[x,18.08,b-.15],[x+.04,18.22,b-.05],category='moving_handle')
  cube(n+'_Control',[-58.695,17.92,b-.018],[-58.62,18.12,b],category='fixed_control')
  for k,(z,Z)in enumerate([(a,a+.02),(b-.02,b)]):cube(n+'_Jamb_'+str(k),[-58.95,17.7,z],[-58.70,18.55,Z],category='fixed_control_frame')
  p['gates'].append({'name':n,'id':n,'pivot':[-58.70,17.7,a+.02],'candidate_open_degrees':90,'requires_visit':True,'private_side_normal':[1,0,0],'closed_center':[(x+y)/2 for x,y in zip(lo,hi)],'leaf_min':lo,'leaf_max':hi,'members':[n+'_Leaf',n+'_Handle_Home',n+'_Handle_Outer'],'control_members':[n+'_Control',n+'_Jamb_1'],'control_at':[-58.61,18.02,b-.01],'home_index':idx,'service_opening_z':[a,b],'tool_pane_width_m':.4,'person_access':False})
p['parts'].extend(parts);p['maintenance_method']={'low_hatch_height_m':1.15,'upper_tool_pane_width_m':.4,'standing_worker_capsule_diameter_m':.6,'maximum_hand_extension_home_side_m':.45,'fixed_glass_outside_exact_panes':True,'every_plant_mesh_unchanged':True,'zero_person_route':True,'biology_or_task_simulation':False};(W/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');print('UPPER_TOOL_PANES',len(parts),len(p['cuts']),len(p['gates']))
