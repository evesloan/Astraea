"""Bind full editable-source triangle corners/UV/normals to consolidated native GLB hierarchy."""
import json,runpy,numpy as np
from pathlib import Path
from collections import Counter,defaultdict
BASE=Path(__file__).resolve().parents[1];api=runpy.run_path(str(BASE/'qa/validate_glb.py'));rows=[]
C=np.array([[1,0,0],[0,0,1],[0,-1,0]])
def sig(corners):return tuple(sorted(tuple(round(float(x),6)for x in c[:3])for c in corners))
for rp in sorted(BASE.glob('AST-BOT-*.manifest.json')):
 r=json.loads(rp.read_text());src=json.loads((BASE/'qa'/(r['catalogue_id']+'_source_geometry.json')).read_text());doc,blob=api['read'](BASE/r['export']);nodes={};actual=defaultdict(list);actualpoints=defaultdict(list);actualnorms=defaultdict(dict)
 def walk(i,parent):
  n=doc['nodes'][i];m=parent@api['matrix'](n);nodes[n['name']]={'matrix':m,'extras':n.get('extras',{})}
  if'mesh'in n:
   for p in doc['meshes'][n['mesh']]['primitives']:
    role=doc['materials'][p['material']]['name'].replace('ASTRAEA_','');v=api['accessor'](doc,blob,p['attributes']['POSITION']);v=(m@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];normal=api['accessor'](doc,blob,p['attributes']['NORMAL'])@np.linalg.inv(m[:3,:3]);normal/=np.linalg.norm(normal,axis=1)[:,None];uv=api['accessor'](doc,blob,p['attributes']['TEXCOORD_0']);inds=api['accessor'](doc,blob,p['indices']).reshape(-1,3);actualpoints[role].extend(v)
    for tri in inds:
     corners=[np.concatenate([v[j],uv[j],normal[j]])for j in tri];key=sig(corners);actual[role].append(key);actualnorms[role][key]=np.array(sorted(corners,key=lambda c:tuple(c[:5])))
  for child in n.get('children',[]):walk(child,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 expected=defaultdict(list);expectedpoints=defaultdict(list);expectednorms=defaultdict(dict)
 for name,s in src.items():
  role=s['material_role'];expectedpoints[role].extend(np.array(s['vertices'])@C.T)
  for t in s['triangle_corners']:
   corners=[list(C@np.array(c['position']))+[c['uv'][0],1-c['uv'][1]]+list(C@np.array(c['normal']))for c in t];key=sig(corners);expected[role].append(key);expectednorms[role][key]=np.array(sorted(corners,key=lambda c:tuple(c[:5])))
 groups=[]
 for role,values in expected.items():
  a=np.array(expectedpoints[role]);b=np.array(actualpoints[role]);d=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2);e=max(float(d.min(0).max()),float(d.min(1).max()));ex,ac=Counter(values),Counter(actual[role]);mismatch=sum((ex-ac).values());uv_error=max([float(np.abs(expectednorms[role][key][:,3:5]-actualnorms[role][key][:,3:5]).max())for key in ex.keys()&ac.keys()]or[99]);normal_error=max([float(np.linalg.norm(expectednorms[role][key][:,5:]-actualnorms[role][key][:,5:],axis=1).max())for key in ex.keys()&ac.keys()]or[99]);groups.append({'material_role':role,'source_triangles':len(values),'native_triangles':len(actual[role]),'maximum_source_native_vertex_distance_m':e,'triangle_position_unmatched_at_1e6':mismatch,'maximum_uv_error':uv_error,'uv_tolerance':1e-6,'maximum_corner_normal_difference':normal_error,'normal_tolerance':.0002,'passes':e<1e-6 and ex==ac and normal_error<.0002 and uv_error<1e-6})
 markers=[]
 for m in r['physical_and_proposal_markers']:
  actualm=nodes[m['name']]['matrix'][:3,3];e=float(np.linalg.norm(actualm-np.array(m['gltf_m'])));markers.append({'name':m['name'],'actual_native_position_m':actualm.tolist(),'expected_native_position_m':m['gltf_m'],'error_m':e,'passes':e<1e-6})
 source_all=np.concatenate([np.array(s['vertices'])for s in src.values()]);native_all=np.concatenate([np.array(v)for v in actualpoints.values()]);wrong_error=float(np.linalg.norm(source_all.max(0)-native_all.max(0)))
 rows.append({'catalogue_id':r['catalogue_id'],'source_sha256':r['source_sha256'],'glb_sha256':r['glb_sha256'],'comparison':'All triangles matched by material role, native hierarchy world coordinates, UV V flip and normals; position corners quantized 1e-6, raw vertices tested <1e-6m, UV differences <1e-6; exported normal quantization tolerance 2e-4','editable_source_parts':len(src),'runtime_meshes':len(doc['meshes']),'group_checks':groups,'marker_checks':markers,'wrong_axis_bound_negative_control_error_m':wrong_error,'native_bounds':{'min_m':native_all.min(0).tolist(),'max_m':native_all.max(0).tolist()},'passes':all(x['passes']for x in groups+markers)and wrong_error>.05})
(BASE/'qa/source_native_geometry.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['passes']for r in rows)},indent=2)+'\n');print([(r['catalogue_id'],r['passes'],[(g['material_role'],g['triangle_position_unmatched_at_1e6'])for g in r['group_checks']])for r in rows])
