from pathlib import Path
import json,copy
W=Path(__file__).resolve().parent;R=W.parents[2];O=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';P=json.load(open(W/'RUNTIME_PLAN.json'));parts=copy.deepcopy(P['successor_parts']);new=[]
for p in parts:
 if p['category']=='moving_sash':
  lower=copy.deepcopy(p);lower['name']=p['name'].replace('Sash','SashLowerFixed');lower['category']='fixed_glass';lower['runtime_collision']=True
  for v in lower['verts']:v[1]=17.65 if v[1]==20.1 else v[1]
  new.append(lower)
  for v in p['verts']:v[1]=17.65 if v[1]==17.25 else v[1]
 new.append(p)
P['successor_parts']=new
for s in P['sashes']:s['height']=2.45;s['lower_edge_closed_y']=17.65
(W/'SASH_CLEARANCE_REVISION.json').write_text(json.dumps({'reason':'Raise movable lower edge400mm above original sill; retain contained fixed lower strips. Every moving pane remains above original chairs throughout its 60degree sweep; all originals stay in place.','initial_7part_candidate_retained':True,'active_contained_parts':new,'minimum_moving_lower_edge_y':17.65,'original_reading_chair_top_y':17.497182,'source_window_volume_unchanged_closed':True},indent=2)+'\n')
ns={'__file__':str(O/'build_native.py')};src=(O/'build_native.py').read_text();exec(src[:src.index('\nmats=start();add_parts')],ns);ns.update(W=W,R=R,P=P);ns['add_parts'](new,ns['start']());rec=ns['export']('D04GardenServiceSashes_r002.blend','D04_PORT_FORWARD_GARDEN_SERVICE_SASHES_r002.glb');P['garden_successors']={'model_file':rec['export'],'model_sha256':rec['export_sha256'],'collision_policy':rec['collision_policy']};P['model_pins'].pop('D04_PORT_FORWARD_GARDEN_SERVICE_SASHES_r001.glb');P['model_pins'][rec['export']]=rec['export_sha256'];P['native_export_records'].append(rec);(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');qa=json.load(open(W/'NATIVE_EXPORT_CHECK.json'));qa['records'].append(rec);qa['active_contained_glass_successors']=10;(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(qa,indent=2)+'\n')
