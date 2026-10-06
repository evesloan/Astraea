"""Offline fixed-triangle contact screen, reusing retained controller box geometry."""
from audit_bathroom import *

def triangle_box_hits(tris, center, rotation, half):
    # SAT tests triangle normal, box axes, and nine edge-cross-box-axis axes.
    t=(tris-center)@rotation
    keep=np.all(t.max(axis=1)>=-half-1e-8,axis=1)&np.all(t.min(axis=1)<=half+1e-8,axis=1);t=t[keep]
    if not len(t):return 0
    edges=[t[:,1]-t[:,0],t[:,2]-t[:,1],t[:,0]-t[:,2]]
    axes=[np.cross(edges[0],edges[1])]
    for edge in edges:
        for axis in np.eye(3):axes.append(np.cross(edge,axis))
    overlap=np.ones(len(t),dtype=bool)
    for axis in axes:
        p=np.einsum('nvc,nc->nv',t,axis);r=np.abs(axis)@half
        overlap &= (p.min(axis=1)<=r+1e-8)&(p.max(axis=1)>=-r-1e-8)
    return int(overlap.sum())

if __name__=='__main__':
    paths=sorted((BATCH/'outputs/production_r005').glob('*/shell.glb'));sr,sm=decode(paths[0]);door,dm=decode(CAT/'assets/guest_privacy_door/exports/AST-DOR-001.glb')
    static=np.concatenate([merge(sr),transform(merge([r for r in door if 'HINGE_LEFT'not in r['chain']]),(-.7,2.9,0),math.pi/2)])
    for marker,aid in [('bath_vanity','AST-SAN-001'),('bath_wc','AST-SAN-002'),('bath_shower','AST-SAN-003')]:
        rr,mm=decode(CAT/'assets/guest_wash/exports'/(aid+'.glb'));static=np.concatenate([static,merge(rr)+sm['DATUM_'+marker]])
    patches=np.concatenate([box([-.84,.12,0],[-.70,.24,2.60]),box([-.755,2.36,2.10],[-.735,3.44,2.25])])
    specs=[('LeafContact',[.525,0,1.0875],[1.026,.05,2.125]),('InnerHandleContact',[.925,.060,1.1],[.17,.035,.23]),('OuterHandleContact',[.925,-.060,1.1],[.17,.035,.23])]
    failures=[];patch_failures=[];margin=.002
    bounds=[]
    for step in range(301):
        angle=step*math.pi/2/300;rotation=rz(math.pi/2+angle);hinge=transform(dm['HINGE_LEFT'],(-.7,2.9,0),math.pi/2)
        for label,center,size in specs:
            center=np.array(center)@rotation.T+hinge;half=np.array(size)/2+margin
            lo=center-np.abs(rotation)@half;hi=center+np.abs(rotation)@half;bounds += [lo,hi]
            for name,tri,dest in [('retained',static,failures),('proposed',patches,patch_failures)]:
                candidates=tri[np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1)]
                n=triangle_box_hits(candidates,center,rotation,half)
                if n:dest.append({'angle_degrees':step*.3,'collider':label,'triangles':n})
    report={'status':'PASS_OFFLINE_SAMPLED_CONTACT_SCREEN'if not failures and not patch_failures else 'FAIL','scope':'301 evenly spaced angles, three retained controller contacts, 2 mm conservative inflation, exact retained GLB triangles plus analytic two-piece patch; not runtime physics/operation acceptance.','prototype':paths[0].parent.name,'sampled_angles':301,'contact_tests':903,'collision_box_inflation_m':margin,'existing_static_intersections':failures,'proposed_static_intersections':patch_failures,'inflated_sweep_bounds_source':[np.min(bounds,axis=0).tolist(),np.max(bounds,axis=0).tolist()]}
    (OUT/'BATHROOM_OFFLINE_SWEEP.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
