"""Numerical proposal checks only; no engine/physics acceptance implied."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
BASE=Path(__file__).resolve().parents[1];d=json.loads((BASE/'collision_proposals.json').read_text());well=np.array([[0,-.06,.20],[-.12,-.06,.10],[.12,-.06,.10],[0,-.25,.20],[0,.22,.30]]);wedges=[]
for w in d['body_proposal']['wedges']:
    a=np.array(w['convex_hull_input_points_m']);h=ConvexHull(a);inside=np.all(well@h.equations[:,:3].T+h.equations[:,3]<=1e-9,axis=1);wedges.append({'index':w['index'],'volume_m3':float(h.volume),'well_test_points_inside':inside.tolist(),'passes':bool(h.volume>0 and not inside.any())})
s=d['seat_proposal']['sampled_surface'];a=np.array(s['vertices_m']);t=a[np.array(s['top_triangles'])];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);positive=bool(np.all(cross[:,2]>0));closed=False
# The centre drain has no sampled vertex or face spanning the inner ellipse.
inner=a[:16];radii=np.linalg.norm(inner[:,:2]-[0,-.06],axis=1)
chains=d['grip_proposal']['capsule_chains'];continuous=all(all(np.linalg.norm(np.array(x['b_m'])-np.array(y['a_m']))<1e-8 for x,y in zip(c['capsules'],c['capsules'][1:]))for c in chains)
out={'scope':'Collision proposal data checks only. No actual engine dynamics or buoyancy claim.','well_test_points_m':well.tolist(),'coaming_wedges':wedges,'sampled_seat_triangles':len(t),'all_sampled_seat_top_normals_positive_z':positive,'minimum_sampled_drain_radius_m':float(radii.min()),'handle_capsule_chains_continuous':continuous,'all_passed':all(w['passes']for w in wedges) and positive and continuous and float(radii.min())>.01};(BASE/'qa/collision_proposal_checks.json').write_text(json.dumps(out,indent=2)+'\n');assert out['all_passed'];print('COLLISION_PROPOSAL_NUMERIC_PASS; well test points outside each coaming wedge, open drain, positive top winding, continuous grips')
