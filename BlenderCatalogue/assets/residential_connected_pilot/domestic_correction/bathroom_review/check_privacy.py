"""Dense retained-door seam and ordinary occupied-room sightline tests."""
from audit_bathroom import *
from itertools import product
p=sorted((BATCH/'outputs/production_r005').glob('*/shell.glb'))[0]
shell,sm=decode(p);door,dm=decode(CAT/'assets/guest_privacy_door/exports/AST-DOR-001.glb')
tri=np.concatenate([merge(shell),transform(merge(door),(-.7,2.9,0),math.pi/2)])
patch=np.concatenate([box([-.84,.12,0],[-.70,.24,2.60]),box([-.755,2.36,2.10],[-.735,3.44,2.25])]);proposed=np.concatenate([tri,patch])
# Use a local slab of exact triangles so detailed 5 mm seam grid is efficient.
slab=tri[np.all(tri.max(axis=1)>=np.array([-1.2,2.30,2.05]),axis=1)&np.all(tri.min(axis=1)<=np.array([-.4,3.50,2.30]),axis=1)]
head_rays=[('head_chamfer_and_seam',(-.4,float(y),float(z)),(-1.2,float(y),float(z)))for y,z in product(np.arange(2.31,3.491,.005),np.arange(2.055,2.291,.005))]
eyes=list(product([-.4,0.,.6,1.2],[.3,1.2,2.9,3.6,4.3,5.0],[.6,1.1,1.65,2.2]))
eyes +=list(product([-1.2,-.78,0.],[ -.6],[.6,1.1,1.65,2.2]))
targets=list(product([-3.,-2.5,-2.,-1.2],[.5,1.1,2.,3.1,3.7],[.45,.9,1.4,1.9]))
sight_rays=[('eye_to_bath_occupied_volume',eye,target)for eye,target in product(eyes,targets)]
report={'scope':'Finite triangle sightline tests. Transparent fixtures excluded; opacity must come from shell and real opaque door. No claim of all-direction mathematical watertightness or species fit.','prototype':p.parent.name,'head_seams':{'before':sample_rays(slab,head_rays),'after_analytic_patch':sample_rays(np.concatenate([slab,patch]),head_rays)},'occupied_room_sightlines':{'before':sample_rays(tri,sight_rays),'after_analytic_patch':sample_rays(proposed,sight_rays)}}
(OUT/'BATHROOM_PRIVACY_RAYS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
