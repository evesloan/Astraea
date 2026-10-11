"""Literal source vertex bounds screen, keeping every failed attempt."""
from pathlib import Path
import json,numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
d=json.loads((ROOT/'Game/data/architecture/group5/CONSTRUCTION.json').read_text())
source=json.loads((ROOT/'BlenderCatalogue/assets/shopping_promenade_20261009/qa/source_geometry.json').read_text())
fail=[];count=0;poses=0
for r in d['doors']:
    q=r['width']/4;h=r['height'];yaw=r['rotation_y'];s=1 if yaw<0 else -1
    origin=np.array(r['local_xyz']);rotation=np.array([[0,0,-s],[0,1,0],[s,0,0]],dtype=float)
    targets=[]
    for layer in ['shell','fitout']:
        for obj in source.get(r['chunk_id']+'__'+layer,[]):
            a=np.array(obj['vertices_xyz']);targets.append((obj['part'],a.min(axis=0),a.max(axis=0)))
    for f in np.linspace(0,1,21):
        for sign in [-1,1]:
            for index in [0,1]:
                center=sign*(3 if index==0 else 1)*q/2+sign*(q+.05 if index==0 else q*2+.05)*f
                # True source handle depth included; wall-side surface mounts remain clear.
                lo=np.array([center-q/2,.025,-.06*index-.075]);hi=np.array([center+q/2,h-.025,-.06*index+.022])
                points=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])@rotation.T+origin
                a=points.min(axis=0);b=points.max(axis=0);poses+=1
                for name,x,y in targets:
                    count+=1
                    overlap=np.minimum(b,y)-np.maximum(a,x)
                    if np.all(overlap>1e-5):fail.append({'door':r['physical_id'],'fraction':float(f),'panel':[sign,index],'source_part':name,'overlap_xyz_m':overlap.tolist()})
receipt={'status':'PASS' if not fail else 'HOLD','sampled_actual_panel_bounds':poses,'literal_source_mesh_comparisons':count,'potential_contacts':fail,'scope':'Conservative literal source vertex AABB screen, including handle bounds; 21 door poses; not exact curved-mesh intersection, player movement, capacity or engineering acceptance'}
(P/'qa/SOURCE_DOOR_FIT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('GROUP5_SOURCE_FIT',receipt['status'],poses,count,'potential contacts',len(fail))
if fail:print(json.dumps(fail[:12],indent=2))
