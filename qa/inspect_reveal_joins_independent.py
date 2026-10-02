#!/usr/bin/env python3
"""Measure matching module end profiles from exported GLB geometry only."""
import json
from pathlib import Path
import sys
import numpy as np
from inspect_glb_independent import GLB

base = Path(sys.argv[1])
output = Path(sys.argv[2])

def positions(name):
    glb = GLB(base/(name+'.glb')); doc=glb.doc; out={}
    def walk(index, parent):
        node=doc['nodes'][index]; world=parent@glb.matrix(node)
        if 'mesh' in node:
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                p=glb.accessor(primitive['attributes']['POSITION'])
                p=np.column_stack((p,np.ones(len(p))))@world.T
                q=p[:,[0,2,1]]; q[:,1]*=-1
                out[doc['materials'][primitive['material']]['name']]=q
        for child in node.get('children',[]):walk(child,world)
    for root in doc['scenes'][doc.get('scene',0)]['nodes']:walk(root,np.eye(4))
    return out

h,j,s,t=[positions('AST-VR-01-'+kind) for kind in ['H','J','S','T']]
rows=[]
for role,header in h.items():
    for join,other,zlow,zhigh,zshift in [('H_to_J',j,-.005,.355,0),('S_to_J',j,-2.905,-2.195,2.2),('H_to_T',t,-.005,.355,0)]:
        source=s[role] if join=='S_to_J' else header
        a=source[np.abs(source[:,0]-source[:,0].max())<1e-5,1:]
        q=other[role]
        b=q[(np.abs(q[:,0]-q[:,0].min())<1e-5)&(q[:,2]>zlow)&(q[:,2]<zhigh),1:].copy()
        b[:,1]+=zshift
        distance=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=-1)
        rows.append({'join':join,'material':role,'source_cap_vertices':len(a),'target_cap_vertices':len(b),
                     'measured_gap_m':float(2.2+q[:,0].min()-source[:,0].max()),
                     'profile_vertex_hausdorff_m':float(max(distance.min(0).max(),distance.min(1).max()))})
result={'measurement':'Exported final cap vertices; common seam profiles compared in local depth/height space after declared module placements.',
        'scope':'Static visual seam compatibility only, not physical simulation or room fit.',
        'results':rows}
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
