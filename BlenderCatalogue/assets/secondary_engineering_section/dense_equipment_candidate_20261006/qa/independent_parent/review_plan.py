from pathlib import Path
import json,hashlib,sys,numpy as np
from geometry_review import glb,Query,PRISMS
P=Path('/workspace/shared/astraea-godot-production-20261003');S=Path('/workspace/scratch/375c2e438292/engineering-dense-bays/source');R=Path(__file__).resolve().parent
plan=json.loads((S/'dense_plan.json').read_text());cm=json.loads((S/'control_manifest.json').read_text());parts=[]
for p in plan['parts']:
 v=np.array(p['vertices_xyz']);tri=[]
 for face in p['faces']:
  tri.extend(v[[face[0],face[i],face[i+1]]] for i in range(1,len(face)-1))
 parts.append({'node':p['name'],'primitive':0,'triangles':np.array(tri)})
base=glb(P/'assets/models/AST-ENG-008_receiving_shoulders.glb');ess=glb(P/'assets/models/AST-ENG-008_essentials.glb');retained=base['meshes']+ess['meshes'];q=Query(retained+parts);new=Query(parts)
prisms={n:new.prism_hits(b) for n,b in PRISMS.items()};rows=[]
for c in cm['controls']:
 eye=np.array(c['proposed_eye_xyz']);target=np.array(c['target_center_xyz']);dist=np.linalg.norm(target-eye);feet=np.array(c['proposed_approach_xyz']);hits=q.rays(eye,target);near_hits=[h for h in hits if h['distance_m']<dist-.055 and h['node'] not in c['actuator_parts']]
 body=q.prism_hits(np.r_[feet+[-.3,.025,-.3],feet+[.3,1.775,.3]])
 rows.append({'id':c['id'],'eye_distance_m':float(dist),'before_target_obstructions':near_hits[:3],'approach_body_hits':sorted(set(h['node'] for h in body)),'within_ray':dist<=2.5,'approach_inside_validated_floor':8<feet[0]<54 and -466<feet[2]<-398 and abs(feet[1]-6)<1e-7,'eye_ordinary_height':abs(eye[1]-feet[1]-1.65)<1e-7})
report={'scope':'Independent pure planned geometry against actual retained exports; not evaluated/exported candidate or Godot proof','source_plan_sha256':hashlib.sha256((S/'dense_plan.json').read_bytes()).hexdigest(),'control_manifest_sha256':hashlib.sha256((S/'control_manifest.json').read_bytes()).hexdigest(),'retained_inputs':{base['path']:base['sha256'],ess['path']:ess['sha256']},'candidate_triangle_count':len(new.tri),'controls':rows,'control_count':len(rows),'exact_plan_prism_hits':{k:{'count':len(v),'parts':sorted(set(x['node'] for x in v))} for k,v in prisms.items()},'passed':len(rows)==120 and not any(prisms.values()) and all(not r['before_target_obstructions'] and not r['approach_body_hits'] and r['within_ray'] and r['approach_inside_validated_floor'] and r['eye_ordinary_height'] for r in rows)}
file=R/(sys.argv[1] if len(sys.argv)>1 else 'PLAN_REVIEW_ATTEMPT001.json');assert not file.exists(),'Preserve earlier diagnostic attempts';file.write_text(json.dumps(report,indent=2,default=lambda x:x.item())+'\n');print(json.dumps({'passed':report['passed'],'prisms':report['exact_plan_prism_hits'],'blocked_controls':[r for r in rows if r['before_target_obstructions'] or r['approach_body_hits']]},indent=2,default=lambda x:x.item()))
