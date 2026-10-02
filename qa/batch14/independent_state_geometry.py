"""Compare every native state mesh, material, attribute and hierarchy transform, not just root markers."""
from pathlib import Path
import json,hashlib,sys,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();a=ROOT/'assets/aquatic_towel_use/exports/AST-AQU-008.glb';b=a.with_name('AST-AQU-008_withdrawn.glb');x=Native(a);y=Native(b);xn=x.g.doc['nodes'];yn=y.g.doc['nodes'];xi={n.get('name'):i for i,n in enumerate(xn)};yi={n.get('name'):i for i,n in enumerate(yn)};root=xi['return_container_translation'];rows=[]
def moving(i):
 if i==root:return True
 while i in x.parents:
  i=x.parents[i]
  if i==root:return True
 return False
for name,i in xi.items():
 j=yi[name];expected=x.world[i].copy()
 if moving(i):expected[:3,3]+=C@np.array([0,.92,0])
 err=float(np.max(abs(y.world[j]-expected)));attributes=[]
 if 'mesh'in xn[i]:
  p=x.g.doc['meshes'][xn[i]['mesh']]['primitives'];q=y.g.doc['meshes'][yn[j]['mesh']]['primitives'];assert len(p)==len(q)
  for u,v in zip(p,q):
   for key in ['POSITION','NORMAL','TEXCOORD_0']:
    aa=x.g.accessor(u['attributes'][key]);bb=y.g.accessor(v['attributes'][key]);attributes.append({'attribute':key,'byte_equal':aa.dtype==bb.dtype and aa.shape==bb.shape and aa.tobytes()==bb.tobytes()})
   attributes.append({'attribute':'indices','byte_equal':np.array_equal(x.g.accessor(u['indices']),y.g.accessor(v['indices']))})
   attributes.append({'attribute':'material_record','byte_equal':x.g.doc['materials'][u['material']]==y.g.doc['materials'][v['material']]})
 rows.append({'node':name,'moves':moving(i),'world_transform_max_error':err,'mesh_attribute_checks':attributes,'pass':err<1e-6 and all(v['byte_equal']for v in attributes)})
r={'passed':set(xi)==set(yi)and all(v['pass']for v in rows),'closed_export_sha256':sha(a),'withdrawn_export_sha256':sha(b),'nodes':rows,'scope':'Every native node transform matches the intended bin-only0.92m translation. Every mesh primitive keeps the same index/position/normal/UV bytes and complete material record. No animation clip, physics or real wheel rolling is inferred.','executed_script_sha256':sha(Path(__file__))};(OUT/'independent_state_geometry.json').write_text(json.dumps(r,indent=2)+'\n');print('STATE GEOMETRY',r['passed'],len(rows),'nodes')
