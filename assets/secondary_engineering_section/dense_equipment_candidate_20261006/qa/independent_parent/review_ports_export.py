from pathlib import Path
import json,hashlib,sys,numpy as np
from geometry_review import glb,Query
P=Path('/workspace/shared/astraea-godot-production-20261003');S=Path('/workspace/scratch/375c2e438292/engineering-dense-bays/source');R=Path(__file__).resolve().parent
plan=json.loads((S/'dense_plan.json').read_text());parts=[]
source=Path('/workspace/scratch/375c2e438292/engineering-dense-bays/qa/reopened_source_triangles.npz')
evidence=json.loads((R/'SOURCE_EXPORT_EQUIVALENCE_ATTEMPT003.json').read_text());assert evidence['passed']
assert hashlib.sha256(source.read_bytes()).hexdigest()==evidence['source_npz_sha256']
assert hashlib.sha256((S.parent/'exports/AST-ENG-008_dense_bays.glb').read_bytes()).hexdigest()==evidence['export_sha256']
npz=np.load(source,allow_pickle=False)
for i,name in enumerate(npz['part_names']):parts.append({'node':str(name),'primitive':0,'triangles':npz['triangles'][npz['part_ids']==i]})

base=glb(P/'assets/models/AST-ENG-008_receiving_shoulders.glb');allrows=base['meshes']+parts;q=Query(allrows);rows=[]
for m in plan['markers']:
 if m.get('kind')!='cable_port':continue
 p=np.array(m['position_xyz']);direction=np.array(m['direction_xyz']);owners=[r for r in allrows if r['node']==m['owner']]
 hits=Query(owners).rays(p+direction*.005,p-direction*.10) if owners else [];hit=hits[0] if hits else None;gap=hit['distance_m']-.005 if hit else None
 # A port marker is at the connector tip, not the wall. Verify the actual named gland/collar spans its receiving face.
 connector=[x for x in parts if x['node'] in [m['name'][5:]+'_gland',m['name'][5:]+'_collar']]
 vv=np.concatenate([x['triangles'].reshape(-1,3) for x in connector]);in_connector=bool(hit and np.all(np.array(hit['position_xyz'])>=vv.min(0)-1e-6) and np.all(np.array(hit['position_xyz'])<=vv.max(0)+1e-6))
 rows.append({'port':m['name'],'owner':m['owner'],'first_owner_hit':hit,'owner_surface_offset_m':gap,'pass':in_connector,'connector_parts':[x['node'] for x in connector],'other_nearby_geometry':[] if hit else [{'node':h['node'],'point':h['position_xyz'],'distance':h['distance_m']} for h in q.rays(p+direction*.005,p-direction*.10)][:8]})
report={'scope':'Independent saved-source/equivalent actual-export cable-port receiving-face query; no Godot or runtime acceptance','plan_sha256':hashlib.sha256((S/'dense_plan.json').read_bytes()).hexdigest(),'passed':all(r['pass'] for r in rows),'port_count':len(rows),'ports':rows};f=R/(sys.argv[1] if len(sys.argv)>1 else 'PORT_EXPORT_ATTEMPT003.json');assert not f.exists();f.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'count':len(rows),'failures':[r for r in rows if not r['pass']]},indent=2))
