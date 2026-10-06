"""Pure source-plan downward fixture ray diagnostic; not runtime illumination."""
from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1];D=json.loads((R/'source/geometry_plan.json').read_text())
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def ray(o,d,a,b,c):
    e1=sub(b,a);e2=sub(c,a);h=cross(d,e2);det=dot(e1,h)
    if abs(det)<1e-9:return None
    inv=1/det;s=sub(o,a);u=dot(s,h)*inv
    if u<0 or u>1:return None
    q=cross(s,e1);v=dot(d,q)*inv
    if v<0 or u+v>1:return None
    t=dot(e2,q)*inv;return t if t>=-1e-6 else None
out=[]
for m in D['markers']:
    p=m['position_xyz'];o=[p[0],p[1]-.08,p[2]];hits=[]
    for part in D['parts']:
        vv=part['vertices_xyz']
        for f in part['faces']:
            for i in range(1,len(f)-1):
                t=ray(o,(0,-1,0),vv[f[0]],vv[f[i]],vv[f[i+1]])
                if t is not None:hits.append((max(0,t),part['name'],part['export']))
    first=min(hits) if hits else None;out.append(dict(marker=m['name'],lens_lower_face_xyz=p,render_emitter_xyz=o,downward_first_hit=first,clear_to_compiler_floor=bool(first and first[1]=='PREVIEW_COMPILER_D02_FLOOR')))
assert all(r['clear_to_compiler_floor'] for r in out)
(R/'qa/fixture_ray_diagnostic.json').write_text(json.dumps(dict(stage='pure source triangles; central downward ray only; not full area/radiance/runtime check',render_only_emitter_offset_down_m=.08,pass_check=True,fixtures=out),indent=2)+'\n');print(str(len(out))+' offset fixture central rays clear to preview compiler floor')
