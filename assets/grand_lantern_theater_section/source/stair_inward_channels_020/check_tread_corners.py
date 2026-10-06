"""Supplementary pure actual-vertex tread corner rays; no engine execution."""
from pathlib import Path
import json,sys
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from fixture_recipe import read,sha,write_new,STATIC
from check_geometry import mesh_query,glb,Query
r=read(R/'REOPENED_GEOMETRY.json');q=Query(glb(STATIC)['meshes']);newq=mesh_query(r['objects']);refq=mesh_query(list(r['actual_source_references'].values()));rows=[];blocked=[]
for f in r['fixtures']:
 source=np.array(f['attachment_world'])
 for s in f['samples']:
  v=np.array(r['actual_source_references'][s['tread']]['vertices_world'][:4]);targets=[v.mean(0)]+list(v)
  for i,p in enumerate(targets):
   target=p+[0,.05,0];hits={'retained_static':q.rays(source,target),'actual_guard_tread_reference':refq.rays(source,target),'new_channel_geometry':newq.rays(source,target)}
   item={'fixture':f['flight'],'tread':s['tread'],'sample':'center'if i==0 else'corner_'+str(i),'receiver_world':target.tolist(),'blocked':any(hits.values())};rows.append(item)
   if item['blocked']:blocked.append({**item,'hits':{k:v[:2]for k,v in hits.items()if v}})
report={'status':'PASS_ACTUAL_TREAD_CENTER_AND_CORNER_RAYS'if not blocked else'BLOCKED_TREAD_CORNER_RAYS','reopened_geometry_sha256':sha(R/'REOPENED_GEOMETRY.json'),'saved_source_sha256':r['saved_source_sha256'],'samples':len(rows),'unique_treads':len({s['tread']for s in rows}),'new_runtime_lights':0,'native_illumination_proven':False,'receiver_height_above_each_tread_m':.05,'rows':rows,'blocked':blocked}
write_new(R/'TREAD_CORNERS_QA.json',report);print(report['status'],len(rows),'samples;',len(blocked),'blocked')
if blocked:raise SystemExit(1)
