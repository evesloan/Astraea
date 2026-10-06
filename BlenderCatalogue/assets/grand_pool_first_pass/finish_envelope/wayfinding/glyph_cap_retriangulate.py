"""Candidate exact-boundary cap edge flips. Pure geometry; no Blender or I/O.

Only flips an internal diagonal shared by two coplanar triangles. Vertices,
outer edges and exact rational filled area must stay identical. This does not
remove thin features, move contour points, change the glyph or relax an area gate.
Source build, independent reopen and rendered readability gates remain mandatory.
"""
from fractions import Fraction
from collections import Counter, defaultdict

def _edges(t):return [tuple(sorted((t[i],t[(i+1)%3]))) for i in range(3)]
def _area2(v,t,axes):
    a,b,c=[[Fraction(v[i][j]) for j in axes] for i in t]
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def _area(v,t):
    a,b,c=[v[i] for i in t];p=[b[i]-a[i] for i in range(3)];q=[c[i]-a[i] for i in range(3)]
    cross=[p[1]*q[2]-p[2]*q[1],p[2]*q[0]-p[0]*q[2],p[0]*q[1]-p[1]*q[0]]
    return sum(x*x for x in cross)**.5/2

def repair_cap_triangles(vertices,triangles,minimum_area=1e-12):
    """Returns new triangles and evidence; fails if any bad triangle cannot be repaired."""
    v=[tuple(float(x) for x in row) for row in vertices];tri=[tuple(row) for row in triangles];steps=[]
    original_boundary=Counter(e for t in tri for e in _edges(t))
    for iteration in range(len(tri)+1):
        bad=[i for i,t in enumerate(tri) if _area(v,t)<=minimum_area]
        if not bad:
            final_boundary=Counter(e for t in tri for e in _edges(t))
            assert {e:n for e,n in original_boundary.items() if n!=2}=={e:n for e,n in final_boundary.items() if n!=2}
            return tri,steps
        adjacency=defaultdict(list)
        for i,t in enumerate(tri):
            for e in _edges(t):adjacency[e].append(i)
        choices=[]
        for i in bad:
            for e in _edges(tri[i]):
                if len(adjacency[e])!=2:continue
                j=next(k for k in adjacency[e] if k!=i)
                ids=set(tri[i]+tri[j])
                if len(ids)!=4:continue
                constant=[axis for axis in range(3) if len({v[k][axis] for k in ids})==1]
                if len(constant)!=1:continue
                axes=[axis for axis in range(3) if axis!=constant[0]]
                a,c=e;b=next(k for k in tri[i] if k not in e);d=next(k for k in tri[j] if k not in e)
                aa,bb=_area2(v,tri[i],axes),_area2(v,tri[j],axes)
                if not bb or (aa and (aa>0)!=(bb>0)):continue
                # Existing shared edge must occur in opposite directions.
                def direction(t):
                    for k in range(3):
                        if {t[k],t[(k+1)%3]}==set(e):return 1 if (t[k],t[(k+1)%3])==e else -1
                if direction(tri[i])==direction(tri[j]):continue
                pair=[(b,d,a),(d,b,c)]
                pair=[t if (_area2(v,t,axes)>0)==(bb>0) else (t[0],t[2],t[1]) for t in pair]
                areas=[_area2(v,t,axes) for t in pair]
                if not all(areas) or any((x>0)!=(bb>0) for x in areas):continue
                if abs(aa)+abs(bb)!=sum(abs(x) for x in areas):continue
                old_edges=Counter(_edges(tri[i])+_edges(tri[j]));new_edges=Counter(_edges(pair[0])+_edges(pair[1]))
                if {x:n for x,n in old_edges.items() if n==1}!={x:n for x,n in new_edges.items() if n==1}:continue
                quality=min(float(abs(x))/2 for x in areas)
                if quality<=minimum_area:continue
                choices.append((quality,i,j,e,pair,constant[0],str(abs(aa)+abs(bb))))
        if not choices:raise ValueError('No exact-area, unchanged-boundary cap diagonal repair for triangles '+str(bad))
        quality,i,j,e,pair,axis,exact_area2=max(choices,key=lambda x:(x[0],-x[1],-x[2],x[3]))
        before=[tri[i],tri[j]];tri[i],tri[j]=pair
        steps.append({'triangle_indices':[i,j],'before':before,'after':pair,'constant_axis':axis,'exact_double_area':exact_area2,'new_minimum_triangle_area':quality,'vertices_moved':0,'outer_edges_changed':0})
    raise ValueError('Cap repair did not converge')

if __name__=='__main__':
    v=[(-1.,0.,0.),(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)]
    t,record=repair_cap_triangles(v,[(0,1,2),(0,2,3)])
    assert len(record)==1 and len(t)==2 and all(_area(v,f)>.4 for f in t)
    vv=[(-1.,0.,0.),(0.,-1e-14,0.),(1.,0.,0.),(0.,1.,0.)]
    tt,rr=repair_cap_triangles(vv,[(0,1,2),(2,3,0)])
    assert len(rr)==1 and all(_area(vv,f)>.4 for f in tt)
    try:repair_cap_triangles(v,[(0,1,2)])
    except ValueError:pass
    else:raise AssertionError('An unsupported boundary triangle must fail')
    print('Three pure cap-retriangulation tests passed; candidate not yet applied')
