from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;G={'__file__':str(W/'north_access_geometry.py'),'__name__':'geometry'};exec((W/'north_access_geometry.py').read_text(),G);U=G['U'];base=U['read'];a=W/'AST-TRM-G4-022_north_access_protection.glb';U['read']=lambda p:a.read_bytes() if 'AST-TRM-G4-022' in p else base(p)
def canonical(t):
 rows=[]
 for tri in t:rows.append(sorted([tuple(p) for p in tri]))
 return np.array(sorted(rows))
actual=dict(U['triangles'](a.name));rows=[]
for q in G['recipes']:
 x=canonical(actual[q['name']]);y=canonical(q['triangles']);assert x.shape==y.shape and np.allclose(x,y,rtol=0,atol=1e-4),(q['name'],x,y);rows.append({'mesh':q['name'],'maximum_vertex_error_m':float(np.abs(x-y).max()),'actual_triangle_point_sets_match_recipe':True})
assert len(actual)==48
rep={'status':'ALL_48_ACTUAL_EXPORTED_TRIANGLE_POINT_SETS_MATCH_BOUNDED_RECIPE','export_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'meshes':48,'triangles':576,'maximum_vertex_error_m':max(q['maximum_vertex_error_m'] for q in rows),'checks':rows,'limits':'Actual-source recipe binding with compact float export tolerance1e-4m; this is not Godot, live collision or whole-world acceptance.'};(W/'ACTUAL_EXPORT_MATCH_CHECK.json').write_text(json.dumps(rep,indent=2)+'\n');print(rep['status'],rep['maximum_vertex_error_m'])
