from pathlib import Path
import json,hashlib,sys,numpy as np,math
from geometry_review import glb,Query
P=Path('/workspace/shared/astraea-godot-production-20261003');S=Path('/workspace/scratch/375c2e438292/engineering-dense-bays/source');R=Path(__file__).resolve().parent
plan=json.loads((S/'dense_plan.json').read_text());parts=[]
for p in plan['parts']:
 v=np.array(p['vertices_xyz']);tri=[]
 for face in p['faces']:tri.extend(v[[face[0],face[i],face[i+1]]] for i in range(1,len(face)-1))
 parts.append({'node':p['name'],'primitive':0,'triangles':np.array(tri)})
base=glb(P/'assets/models/AST-ENG-008_receiving_shoulders.glb');ess=glb(P/'assets/models/AST-ENG-008_essentials.glb');q=Query(base['meshes']+ess['meshes']+parts)
lights={'CONTROL':([26,8.845,-459],[26,7.4,-462.95],7),'WORKBAY':([27,9.145,-405],[26.5,7,-401.4],8.5)};rows=[]
for c in plan['controls']:
 source,aim,reach=lights[c['bay']];source=np.array(source);axis=np.array(aim)-source;axis/=np.linalg.norm(axis);target=np.array(c['target_center_xyz']);d=target-source;distance=np.linalg.norm(d);d/=distance;angle=math.degrees(math.acos(np.clip(axis@d,-1,1)));hits=q.rays(source,target+d*.1);h=hits[0] if hits else None
 rows.append({'id':c['id'],'bay':c['bay'],'source_xyz':source.tolist(),'distance_m':float(distance),'cone_offset_deg':angle,'within_retained_range_cone':bool(distance<=reach and angle<=65),'first_hit_node':h['node'] if h else None,'first_hit_distance_m':h['distance_m'] if h else None,'blocked_before_control_zone':bool(h and h['distance_m']<distance-.1),'blocker_xyz':h['position_xyz'] if h and h['distance_m']<distance-.1 else None})
r={'scope':'Source-only first-hit/cone feasibility under unchanged local existing-fixture settings; not light intensity, renderer selection or visual acceptance','plan_sha256':hashlib.sha256((S/'dense_plan.json').read_bytes()).hexdigest(),'controls':rows,'within_range_cone':sum(bool(r['within_retained_range_cone']) for r in rows),'blocked_before_control_zone':sum(r['blocked_before_control_zone'] for r in rows)}
f=R/(sys.argv[1] if len(sys.argv)>1 else 'LIGHT_PLAN_ATTEMPT001.json');assert not f.exists();f.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'within_range_cone':r['within_range_cone'],'blocked_before_control_zone':r['blocked_before_control_zone'],'blocking_parts':sorted(set(x['first_hit_node'] for x in rows if x['blocked_before_control_zone']))},indent=2))
