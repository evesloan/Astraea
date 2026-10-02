#!/usr/bin/env python3
"""Read actual GLB bytes. No renderer, source changes, or engine claims."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05'
sys.path.insert(0,str(ROOT/'qa'))
from inspect_glb_independent import GLB
reports=[]
for folder in ['aquatic_lounge','aquatic_edges','aquatic_float']:
 for path in sorted((ROOT/'assets'/folder).rglob('*.glb')):
  if any(x in path.parts for x in ['history','backup','source_backups']):continue
  g=GLB(path);r=g.inspect();r['material_count']=len(g.doc.get('materials',[]));r['mesh_count']=len(g.doc.get('meshes',[]));r['primitive_count']=sum(len(m['primitives']) for m in g.doc.get('meshes',[]));r['opaque_material_audit']=[];r['topology_by_primitive']=[]
  for m in g.doc.get('materials',[]):
   p=m.get('pbrMetallicRoughness',{});a=m.get('alphaMode','OPAQUE');f=p.get('baseColorFactor',[1,1,1,1])[3]
   r['opaque_material_audit'].append({'name':m.get('name'),'alphaMode':a,'alphaFactor':f,'doubleSided':m.get('doubleSided',False),'metallic':p.get('metallicFactor',1),'roughness':p.get('roughnessFactor',1)})
   if a!='OPAQUE' or f!=1:r['issues'].append('Nonopaque material: '+str(m.get('name')))
  for mesh in g.doc.get('meshes',[]):
   for p in mesh['primitives']:
    pos=g.accessor(p['attributes']['POSITION']).astype(float)
    fs=g.accessor(p['indices']).ravel().reshape(-1,3) if 'indices' in p else np.arange(len(pos)).reshape(-1,3)
    _,iv=np.unique(np.round(pos,6),axis=0,return_inverse=True);tri=iv[fs]
    edges=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);edges.sort(axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
    mat=g.doc['materials'][p['material']].get('name') if 'material' in p else None
    rec={'mesh':mesh.get('name'),'material':mat,'weld_tolerance_m':1e-6,'triangles':len(tri),'boundary_edges':int((counts==1).sum()),'nonmanifold_edges':int((counts>2).sum()),'welded_vertices':len(np.unique(iv))}
    r['topology_by_primitive'].append(rec)
  r['scope']='Actual GLB structural and geometry checks. Topology welds within individual material primitives; split-material boundaries are not by themselves a defect. Not a full Khronos validator or an engine/performance test.'
  reports.append(r)
(OUT/'independent_glb_report.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps([{'asset':Path(r['path']).stem,'triangles':r['triangles'],'materials':r['material_count'],'primitives':r['primitive_count'],'dimensions_xyz':r.get('dimensions_xyz'),'issues':r['issues']} for r in reports],indent=2))
