"""Read-only source-composition clarification, no Blender/engine/import or source edits.
Strict noncoplanar segment-through-triangle-interior witnesses establish selected
surface penetrations. A no-witness result is NOT a clearance certificate; coplanar
or contained-solid cases are left unresolved. This is not an automatic removal list.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np
O=Path(__file__).resolve().parent;R=O.parent/'refined_002';sys.path.insert(0,str(R/'inputs'));from decode_sections import glb
M,_=glb(R/'exports/cinema_library_receiving_r001.glb',np.zeros(3));by={m['name']:m for m in M};C=Path('/workspace/scratch/375c2e438292/library_cinema_support_20261007/WP13_FULL/WP13_D11_directory_02/exports/WP13_cinema1.glb');cm,_=glb(C,np.array([11,69.5,-468]));cb={m['name']:m for m in cm};broad=json.load(open(R/'qa/predecessor_conflict_inventory.json'))['objects']
EPS=1e-6
def edges_cross(A,B):
 # Cross strictly inside each finite edge and inside each noncoplanar triangle,
 # excluding endpoints/triangle boundaries so an intended tangent touch is not a witness.
 T=B['vertices'][B['faces']];e1=T[:,1]-T[:,0];e2=T[:,2]-T[:,0]
 for ti,tri in enumerate(A['vertices'][A['faces']]):
  for ei,(a,b) in enumerate(zip(tri,np.roll(tri,-1,axis=0))):
   dr=b-a;L=float(np.linalg.norm(dr))
   if L<1e-9:continue
   dr/=L;p=np.cross(dr,e2);det=np.einsum('ij,ij->i',e1,p);valid=abs(det)>1e-8;inv=np.zeros_like(det);inv[valid]=1/det[valid];s=a-T[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=(q@dr)*inv;t=np.einsum('ij,ij->i',e2,q)*inv
   hits=valid&(u>EPS)&(v>EPS)&(u+v<1-EPS)&(t>1e-5)&(t<L-1e-5)
   if hits.any():
    j=int(np.flatnonzero(hits)[0]);return dict(edge_mesh=A['name'],edge_triangle=ti,edge=ei,intersected_mesh=B['name'],intersected_triangle=j,world_xyz=(a+dr*t[j]).tolist(),method='Strict finite edge crossing triangle interior, noncoplanar; endpoints/boundary tangency excluded')
 return None
results=[]
for row in broad:
 source=cb[row['retained_source_object']];witness=None
 for name in row['root_candidate_meshes']:
  root=by[name];witness=edges_cross(root,source) or edges_cross(source,root)
  if witness:break
 results.append(dict(retained_source_object=source['name'],classification='triangle_confirmed_surface_penetration' if witness else 'broad_phase_only_unresolved',witness=witness))
counts={k:sum(r['classification']==k for r in results) for k in ['triangle_confirmed_surface_penetration','broad_phase_only_unresolved']}
report={'scope':'Clarification of106 conservative AABB candidates. Not106 collisions, not automatic removal instructions. Intended exact bearing contacts are checked separately in the receiving contact ledger.','method':'Strict noncoplanar finite edge-through-triangle-interior witness in both directions for each broad-phase pair. No witness does not clear coplanar or contained-solid overlaps.','selected_native_sha256':hashlib.sha256((R/'source/cinema_library_receiving_r001.blend').read_bytes()).hexdigest(),'selected_glb_sha256':hashlib.sha256((R/'exports/cinema_library_receiving_r001.glb').read_bytes()).hexdigest(),'cinema_glb_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'counts':counts,'results':results,'required_owner_action':'WP13 reviews exact witnesses and retains/recomposes/removes only under its source authority; preserve audience, screen, routes, booths and care. Old roof/vault replacement and specific penetrating acoustic/wall/sign details are source composition holds, not a failure of the isolated frame optical checks.'}
(O/'TRIANGLE_CONFLICT_CLARIFICATION.json').write_text(json.dumps(report,indent=2));print(counts);print('\n'.join(r['retained_source_object'] for r in results if r['witness']))
