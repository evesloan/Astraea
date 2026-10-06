"""Pure independent actual-GLB gates for the section source candidate."""
from pathlib import Path
import json,hashlib,sys,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'));from geometry_review import glb,Query,PRISMS
G=glb(R/'exports/AST-ENG-008_workbay_section.glb');S=json.loads((R/'qa/section_export_build.json').read_text());C=json.loads((R/'source/runtime_contract.proposal.json').read_text());controls=json.loads((R/'source/calibration_control_manifest.json').read_text())['controls'];nodes={n['name']:n for n in G['nodes']};q=Query(G['meshes']);geo=uv=norm=0
for m in G['meshes']:
 t=m['triangles'];idx=m['indices'];n=m['normals']@np.linalg.inv(nodes[m['node']]['world_matrix'][:3,:3]);cr=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);geo+=int((np.linalg.norm(cr,axis=1)<1e-12).sum());norm+=int((np.einsum('ij,ij->i',cr,n[idx].mean(1))< -1e-10).sum());v=m['uv'][idx];area=np.abs((v[:,1,0]-v[:,0,0])*(v[:,2,1]-v[:,0,1])-(v[:,1,1]-v[:,0,1])*(v[:,2,0]-v[:,0,0]));uv+=int((area<1e-13).sum());assert np.isfinite(t).all() and np.isfinite(v).all()
prisms={k:q.prism_hits(b) for k,b in PRISMS.items()};ret=[]
for p in ['/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/exports/AST-ENG-008.glb',str(R.parent.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb')]:ret+=glb(p)['meshes']
context=Query(G['meshes']+ret);rays=[]
for c in controls:
 eye=np.array(c['proposed_eye_xyz']);target=np.array(c['target_center_xyz']);h=context.rays(eye,eye+(target-eye)*1.15);rays.append({'id':c['id'],'pass':bool(h and h[0]['node']=='ACT_'+c['id']),'first_hit':h[0]['node'] if h else None})
gate=[]
for c in C['gate']['targets']:
 eye=np.array(c['approach_xyz'])+np.array([0,1.65,0]);target=np.array(c['position_xyz']);h=context.rays(eye,eye+(target-eye)*1.15);gate.append({'marker':c['marker'],'pass':bool(h and h[0]['node']==c['mesh']),'first_hit':h[0]['node'] if h else None})
leaf=np.concatenate([m['triangles'].reshape(-1,3) for m in G['meshes'] if m['node']==C['gate']['source_node']]);bounds=np.r_[leaf.min(0),leaf.max(0)];expected=np.array(C['gate']['closed_leaf_bounds_xyz']);leaferr=float(abs(bounds-expected).max())
# Direct exact-oriented material triangulation from source dump.
def triangle_multiset(meshes):
 from collections import Counter
 out=Counter()
 for material,tt in meshes:
  for tr in tt:
   p=[tuple(np.round(v,5)) for v in tr];i=min(range(3),key=lambda j:p[j]);out[(material,)+tuple(p[(i+j)%3] for j in range(3))]+=1
 return out
D=np.load(R/'qa/section_source_triangles.npz');A=triangle_multiset([(str(D['material_names'][i]),D['triangles'][D['material_ids']==i]) for i in range(len(D['material_names']))]);B=triangle_multiset([(m['material'],m['triangles']) for m in G['meshes']]);miss=sum((A-B).values());extra=sum((B-A).values())
contracts={n['name']:n['extras'].get('collision_contract') for n in G['nodes'] if n['extras'].get('collision_contract')};act=[n for n in nodes if n.startswith('ACT_ENG2_')];proxy=[n for n in contracts if contracts[n]=='contact_only_glass_26mm'];visual=[n for n in contracts if contracts[n]=='visual_only_glass'];floor_bad=[r['name'] for r in S['parts'] if str(r.get('kind','')).startswith('compiler_')]
report={'passed':geo==uv==norm==0 and not any(prisms.values()) and all(r['pass'] for r in rays) and all(r['pass'] for r in gate) and leaferr<.0001 and miss==extra==0 and len(act)==120 and len(proxy)==10 and bool(visual) and not floor_bad,'scope':'Actual source candidate binary geometry/material-triangle/UV/marker/ray/prism/closed-door checks, not Game traversal or visual acceptance','source_sha256':S['source_sha256'],'export_sha256':G['sha256'],'triangles':sum(len(m['triangles']) for m in G['meshes']),'source_triangles':S['triangles'],'source_triangles_missing':miss,'source_triangles_extra':extra,'degenerate_geometry':geo,'collapsed_uv':uv,'opposed_normals':norm,'control_count':len(act),'glass_contact_proxy_meshes':proxy,'no_preview_floors_or_context':not floor_bad and S['retained_context_excluded'],'prisms':prisms,'control_rays':rays,'gate_rays':gate,'closed_leaf_bounds_xyz':bounds.tolist(),'closed_leaf_bounds_error_m':leaferr,'collision_contracts':contracts}
(R/'qa/section_independent_export_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['control_rays','collision_contracts']},indent=2));assert report['passed']
