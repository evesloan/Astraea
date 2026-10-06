from pathlib import Path
import json,sys,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'))
from geometry_review import Query,glb
s=json.loads((R/'source/dense_plan.json').read_text());meshes=[]
for p in s['parts']:
 v=np.array(p['vertices_xyz']);tri=[]
 for f in p['faces']:
  tri.extend([[v[f[0]],v[f[j]],v[f[j+1]]] for j in range(1,len(f)-1)])
 meshes.append({'node':p['name'],'triangles':np.array(tri),'primitive':0})
new=Query(meshes);retained=[]
for path in ['/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/exports/AST-ENG-008.glb',str(R.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb')]:retained+=glb(path)['meshes']
q=Query(meshes+retained);ray=[]
for c in s['controls']:
 target=np.array(c['target_center_xyz']);normal=np.array(c['target_normal_xyz']);eye=c['proposed_eye_xyz'];h=q.rays(eye,np.array(eye)+(target-np.array(eye))*1.15)
 ray.append({'id':c['id'],'distance_m':c['ordinary_eye_distance_m'],'first_hit':h[0]['node'] if h else None,'first_hit_xyz':h[0]['position_xyz'] if h else None,'pass':bool(h and h[0]['node'] in c['actuator_parts'])})
hits={n:new.prism_hits(b) for n,b in s['prisms'].items()};ports={m['name']:m for m in s['markers'] if m['kind']=='cable_port'}
connections=[]
for c in s['cables']:
 a=ports[c['from_port']];b=ports[c['to_port']];connections.append({'id':c['id'],'from_port':a['name'],'to_port':b['name'],'endpoint_error_m':max(np.linalg.norm(np.array(c['path_xyz'][0])-a['position_xyz']),np.linalg.norm(np.array(c['path_xyz'][-1])-b['position_xyz']))})
# Nominal floor-owner prism support only, explicitly not actual Godot character/compiled-floor support.
approaches=[{'id':c['id'],'pass':c['proposed_approach_xyz'][1]==6 and (20.18<c['proposed_approach_xyz'][0]<33.82) and ((-463.82<c['proposed_approach_xyz'][2]<-454.78) if c['bay']=='CONTROL' else (-409.22<c['proposed_approach_xyz'][2]<-400.18))} for c in s['controls']]
report={'scope':'Pure raw planned source plus actual retained GLB; no Blender/export/Godot proof','passed':not any(hits.values()) and all(r['pass'] for r in ray) and all(a['pass'] for a in approaches),'controls':len(ray),'rays':ray,'approach_floor_owner_plan':approaches,'new_triangle_prism_hits':hits,'cable_endpoints':connections,'input_hashes_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in s['input_hashes'].items())}
(R/'qa/pure_plan_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['rays','approach_floor_owner_plan','cable_endpoints']},indent=2));print('failed rays',json.dumps([r for r in ray if not r['pass']],indent=2));assert report['passed']
