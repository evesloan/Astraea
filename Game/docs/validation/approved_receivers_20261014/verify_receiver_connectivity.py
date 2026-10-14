"""Independent rectangle SAT check for connected receiving flange networks."""
from pathlib import Path
import json,math
P=Path(__file__).resolve().parent/'receiver_frame_candidate'
plan=json.loads((P/'MEMBERS.json').read_text())
def rectangle(member):
    a,b=member['a'],member['b'];dx,dz=b[0]-a[0],b[2]-a[2];length=math.hypot(dx,dz)
    if length<1e-8:
        return [(a[0]-.12,a[2]-.12),(a[0]+.12,a[2]-.12),
                (a[0]+.12,a[2]+.12),(a[0]-.12,a[2]+.12)]
    ux,uz=-dz/length*.18,dx/length*.18
    return [(a[0]+ux,a[2]+uz),(b[0]+ux,b[2]+uz),
            (b[0]-ux,b[2]-uz),(a[0]-ux,a[2]-uz)]
def intersects(a,b):
    for polygon in [a,b]:
        for c,d in zip(polygon,polygon[1:]+polygon[:1]):
            nx,nz=d[1]-c[1],c[0]-d[0]
            aa=[x*nx+z*nz for x,z in a];bb=[x*nx+z*nz for x,z in b]
            if max(aa)<min(bb)-1e-7 or max(bb)<min(aa)-1e-7:return False
    return True
failed=[]
for row in plan['regions']:
    members=row['members'];footprints=list(map(rectangle,members));seen={0}
    while True:
        addition={j for i in seen for j in range(len(members))
                  if j not in seen and intersects(footprints[i],footprints[j])}
        if not addition:break
        seen|=addition
    if len(seen)!=len(members):
        failed.append({'region':row['region_id'],
                       'disconnected_members':[members[i]['name']for i in range(len(members))if i not in seen]})
receipt={'status':'PASS_CONNECTED_RECEIVING_FLANGE_NETWORKS'if not failed else'HOLD_DISCONNECTED_MEMBERS',
         'regions':len(plan['regions']),'members':sum(len(r['members'])for r in plan['regions']),
         'failed':failed,'geometry_connectivity_is_not_capacity_acceptance':True}
(P/'PROFILE_PLAN_CONNECTIVITY_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));assert not failed
