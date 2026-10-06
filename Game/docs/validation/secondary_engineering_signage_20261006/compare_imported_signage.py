"""Compare actual native LOD0 sign triangles/UVs to the frozen glTF export.
No engine, project edit, or acceptance of readability. Never use get_faces here.
"""
from pathlib import Path
import argparse,hashlib,json,sys,collections,itertools
import numpy as np
from scipy.spatial import cKDTree
PARSER=Path('/workspace/scratch/375c2e438292/engineering-density-review/geometry_review.py')
PARSER_SHA='64aea0bd73c42c5f640c02c031a28e8b17d8fe225e0dafb9b8587b17c11ca60a'
assert hashlib.sha256(PARSER.read_bytes()).hexdigest()==PARSER_SHA
sys.path.insert(0,str(PARSER.parent));from geometry_review import glb
SOURCE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/cell_restriction_signage_candidate_20261006/exports/AST-ENG-008_cell_restriction_signage_004.glb')
SOURCE_SHA='985fec01390bc3ccf3543df9062ce8ce448a99014e5a92695dea8390b1b990b1'
# Godot4.6.3 GLTFDocument::_parse_meshes reverses source index winding.
# Only cyclic-equivalent reversal is legitimate; one isolated opposite winding
# must not pass merely because its positions/UVs still match.
PERMS=[(0,2,1),(1,0,2),(2,1,0)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(source,data,uv,rows):
 expected={(m['node'],m['material']):m for m in source['meshes']};assert len(expected)==3
 seen=set();records=[]
 for group in rows:
  for surface in group['surfaces']:
   key=(group['name'],surface['material']);assert key in expected and key not in seen,key;seen.add(key)
   offset=int(surface['triangle_offset']);count=int(surface['triangles']);a=data[offset:offset+count];u=uv[offset:offset+count];e=expected[key];x=e['triangles'];v=e['uv'][e['indices']];assert a.shape==x.shape and u.shape==v.shape,(key,a.shape,x.shape)
   # Position identity candidates are source triangle centroids, then every
   # corner is verified against the source, with its paired UV and material.
   tree=cKDTree(x.mean(axis=1));_,candidate=tree.query(a.mean(axis=1),k=min(8,len(x)))
   if candidate.ndim==1:candidate=candidate[:,None]
   chosen=[];used=set();maxpos=np.zeros(3);maxuv=0.;winding=collections.Counter()
   for i in range(len(a)):
    matches=[]
    for j in candidate[i]:
     j=int(j)
     if j in used:continue
     toler=np.maximum(2.0*np.abs(np.spacing(np.abs(x[j]).astype(np.float32))).astype(float),1e-7)
     for perm in PERMS:
      order=list(perm);pe=np.abs(a[i,order]-x[j]);ue=np.abs(u[i,order]-v[j])
      if np.all(pe<=toler) and np.all(ue<=1e-6):matches.append((float(pe.max()),float(ue.max()),j,perm,pe))
    assert matches,('No exact source triangle/material/UV identity within2float32ULPs',key,i,a[i].tolist(),u[i].tolist())
    _,ue,j,perm,pe=min(matches,key=lambda t:(t[0],t[1],t[2],t[3]));used.add(j);chosen.append(j);maxpos=np.maximum(maxpos,pe.max(axis=0));maxuv=max(maxuv,ue);winding[str(perm)]+=1
   assert len(used)==count
   records.append({'node':key[0],'material':key[1],'triangles':count,'max_position_error_xyz_m':maxpos.tolist(),'max_uv_error':maxuv,'actual_corner_permutations':dict(winding),'every_source_triangle_used_once':True})
 assert seen==set(expected) and sum(r['triangles']for r in records)==6672
 return records

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--artifact-dir',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--self-test',action='store_true');o=parser.parse_args();assert sha(SOURCE)==SOURCE_SHA
 source=glb(SOURCE)
 if o.self_test:
  xyz=[];uv=[];rows=[];offset=0
  for name in sorted({m['node']for m in source['meshes']}):
   row={'name':name,'surfaces':[]}
   for m in [m for m in source['meshes']if m['node']==name]:
    n=len(m['triangles']);xyz.extend(m['triangles'][:,[0,2,1]].astype('f4').tolist());uv.extend(m['uv'][m['indices']][:,[0,2,1]].astype('f4').tolist());row['surfaces'].append({'material':m['material'],'triangle_offset':offset,'triangles':n});offset+=n
   rows.append(row)
  xyz=np.array(xyz);uv=np.array(uv);records=compare(source,xyz,uv,rows)
  for label,badpos,baduv in [('normal-plane0.5mm',xyz.copy(),uv.copy()),('UVcorner0.01',xyz.copy(),uv.copy()),('isolated_winding_flip',xyz.copy(),uv.copy())]:
   if label.startswith('normal'):badpos[0,:,0]+=.0005
   elif label.startswith('UV'):baduv[0,0,0]+=.01
   else:badpos[0]=badpos[0,[0,2,1]];baduv[0]=baduv[0,[0,2,1]]
   try:compare(source,badpos,baduv,rows)
   except AssertionError:pass
   else:raise AssertionError('Mutation was wrongly accepted: '+label)
  report={'status':'PURE_SELF_TEST_PASS','actual_runtime_evidence':False,'triangles':6672,'positive_cases':['frozen glTF cast tofloat32 with engine-compatible corner reversal'],'negative_cases':['normal-plane0.5mm','UVcorner0.01','isolated_winding_flip'],'records':records}
 else:
  assert o.artifact_dir is not None and o.output is not None and not o.output.exists()
  meta=o.artifact_dir/'engineering_signage_imported_source.json';pos=o.artifact_dir/'engineering_signage_triangles.float32';tex=o.artifact_dir/'engineering_signage_uv.float32';r=json.loads(meta.read_text());assert r['model_sha256']==SOURCE_SHA and r['triangles']==6672
  xyz=np.frombuffer(pos.read_bytes(),dtype='<f4').reshape(-1,3,3).astype(float);uv=np.frombuffer(tex.read_bytes(),dtype='<f4').reshape(-1,3,2).astype(float);assert len(xyz)==len(uv)==6672;records=compare(source,xyz,uv,r['groups'])
  report={'status':'NATIVE_RENDER_SOURCE_EQUIVALENCE_PASS','source_sha256':SOURCE_SHA,'native_input_sha256':{p.name:sha(p)for p in [meta,pos,tex]},'triangles':6672,'position_tolerance':'At most2float32ULPs independently per coordinate (floor1e-7m); source plane/UV/material/topology never substituted. Existing real collision and0.15–0.25mm ink gap gates remain separate.','uv_absolute_tolerance':1e-6,'winding_policy':'Only cyclic-equivalent Godot reversal (odd permutations) of each frozen glTF source triangle; isolated opposite winding is rejected.','engine_source':'https://github.com/godotengine/godot/blob/4.6.3-stable/modules/gltf/gltf_document.cpp','records':records,'visual_readability_accepted':False,'physics_scope':'Separate existing gate/steps/tools test; these native arrays are not collision proof.'}
 if o.output:
  assert not o.output.exists();o.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
