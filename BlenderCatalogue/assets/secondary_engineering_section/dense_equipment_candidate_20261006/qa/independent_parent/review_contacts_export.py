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

base=glb(P/'assets/models/AST-ENG-008_receiving_shoulders.glb');ess=glb(P/'assets/models/AST-ENG-008_essentials.glb');oldrows=json.loads(Path('/workspace/scratch/375c2e438292/engineering-essentials/qa/source_build.json').read_text())['actual_evaluated_parts'];oldbounds={r['name']:r['bounds_xyz'] for r in oldrows};rows=[]
def pick(q):return q[0] if q else None
for c in plan['contacts']:
 p=np.array(c['position_xyz'],float);normal=np.array(c['normal_xyz'],float);node=c['part'];owners=[m for m in base['meshes']+parts if m['node']==c['owner']];mode='exact_named_mesh'
 if c['owner'].startswith('compiler_'):
  assert 8<=p[0]<=54 and -466<=p[2]<=-398 and normal.tolist()==[0,-1,0]
  owners=[{'node':'D02_secondary_engineering_floor','primitive':0,'triangles':np.array([[[8,6,-466],[54,6,-466],[54,6,-398]],[[8,6,-466],[54,6,-398],[8,6,-398]]])}];mode='tested_compiler_floor_top_plane'
 elif not owners and c['owner'] in oldbounds:
  b=np.array(oldbounds[c['owner']]);mode='exact_editable_part_bounds_filter_of_frozen_batched_export'
  for mesh in ess['meshes']:
   tri=mesh['triangles'];mask=np.all(tri.min(1)>=b[:3]-.0002,axis=1)&np.all(tri.max(1)<=b[3:]+.0002,axis=1)
   if mask.any():owners.append(dict(mesh,triangles=tri[mask]))
 part=[m for m in parts if m['node']==node];assert part,node
 a=pick(Query(part).rays(p+normal*.03,p-normal*.03));b=pick(Query(owners).rays(p-normal*.03,p+normal*.03)) if owners else None
 gap=float(np.linalg.norm(np.array(a['position_xyz'])-b['position_xyz'])) if a and b else None
 rows.append({'id':c['id'],'part':node,'owner':c['owner'],'owner_resolution':mode,'candidate_contact':a,'owner_contact':b,'actual_surface_gap_m':gap,'pass':gap is not None and gap<.001})
report={'scope':'Independent saved-source/equivalent actual-export contact versus retained export / tested compiler Y6 plane; future Godot import/physical contact still required','plan_sha256':hashlib.sha256((S/'dense_plan.json').read_bytes()).hexdigest(),'contact_count':len(rows),'passed':all(r['pass'] for r in rows),'contacts':rows}
f=R/(sys.argv[1] if len(sys.argv)>1 else 'CONTACT_EXPORT_ATTEMPT003.json');assert not f.exists();f.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'count':len(rows),'failures':[r for r in rows if not r['pass']]},indent=2))
