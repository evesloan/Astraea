from pathlib import Path
import sys,json,numpy as np,hashlib
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph
results=[]
for ident in ['AST-AQU-007','AST-AQU-008']:
 s=json.loads((OUT/f'independent_source_{ident}.json').read_text());a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];floor=[o['name']for o in s['objects']if o['type']=='MESH'and o['min_xyz'][2]<.00002];g=contact_graph(tri,labels,floor);results.append({'catalogue_id':ident,'source_sha256':s['sha256'],'support_graph':g});print(ident,'passed',g['passed'],'isolated',g['isolated_parts'],flush=True)
(OUT/'independent_towel_initial_support.json').write_text(json.dumps({'assets':results},indent=2)+'\n')
