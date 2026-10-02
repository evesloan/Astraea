#!/usr/bin/env python3
"""Read-only actual batch04 GLB inspection; does not trust author counters."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'qa'))
from inspect_glb_independent import GLB
OUT=ROOT/'qa/batch04'
reports=[]
for folder in ['botanical_canopy','botanical_understory','botanical_planter']:
 for path in sorted((ROOT/'assets'/folder).rglob('*.glb')):
  g=GLB(path);r=g.inspect();r['opaque_material_audit']=[];r['topology_by_primitive']=[]
  for m in g.doc.get('materials',[]):
   p=m.get('pbrMetallicRoughness',{}); alpha=m.get('alphaMode','OPAQUE');factor=p.get('baseColorFactor',[1,1,1,1])[3]
   r['opaque_material_audit'].append({'name':m.get('name'),'alphaMode':alpha,'alphaFactor':factor,'doubleSided':m.get('doubleSided',False),'alphaCutoff':m.get('alphaCutoff')})
   if alpha!='OPAQUE' or factor!=1:r['issues'].append('Nonopaque material: '+str(m.get('name')))
  for mesh in g.doc.get('meshes',[]):
   for p in mesh['primitives']:
    pos=g.accessor(p['attributes']['POSITION']).astype(float)
    faces=g.accessor(p['indices']).ravel().reshape(-1,3) if 'indices' in p else np.arange(len(pos)).reshape(-1,3)
    _,inv=np.unique(np.round(pos,6),axis=0,return_inverse=True);tri=inv[faces]
    edge=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);edge.sort(axis=1);edges,count=np.unique(edge,axis=0,return_counts=True)
    mat=g.doc['materials'][p['material']].get('name') if 'material' in p else None
    rec={'mesh':mesh.get('name'),'material':mat,'weld_tolerance_m':1e-6,'triangles':len(tri),'boundary_edges':int((count==1).sum()),'nonmanifold_edges':int((count>2).sum()),'welded_vertices':int(len(np.unique(inv)))}
    r['topology_by_primitive'].append(rec)
    if mat and ('bark' in mat or 'soil' in mat) and rec['boundary_edges']:r['issues'].append(str(mat)+': support boundary edges require inspection')
  reports.append(r)
(OUT/'independent_glb_report.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps([{'asset':Path(r['path']).stem,'triangles':r['triangles'],'dimensions_xyz':r.get('dimensions_xyz'),'issues':r['issues'],'topology':r['topology_by_primitive']} for r in reports],indent=2))
