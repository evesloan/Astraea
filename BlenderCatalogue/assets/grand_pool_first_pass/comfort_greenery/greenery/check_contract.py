"""Independent pure contract gate. Does not import the geometry authoring module."""
import json, math, hashlib, collections, sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent

def in_polygon(p,polygon,tol=1e-7):
    signs=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]): signs.append((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
    return min(signs)>=-tol or max(signs)<=tol
def in_box(p,b,tol=1e-6):return all(b[0][i]-tol<=p[i]<=b[1][i]+tol for i in range(3))
def triangles(part):
    v=np.array(part['vertices'],float)
    for f in part['faces']:
        for i in range(1,len(f)-1):yield v[[f[0],f[i],f[i+1]]]
def projected_coverage(asset):
    poly=asset['soil_polygon_xz'];pos=asset['position_xyz'];xx=np.linspace(min(p[0] for p in poly)+.018,max(p[0] for p in poly)-.018,111);zz=np.linspace(min(p[1] for p in poly)+.018,max(p[1] for p in poly)-.018,49);samples=np.array([[x,z] for x in xx for z in zz if in_polygon([x,z],poly)]);covered=np.zeros(len(samples),bool)
    for part in asset['parts']:
        if not part['material_role'].startswith('botanical_leaf_') or part['surface_kind']!='open_shaped_leaf':continue
        for t in triangles(part):
            t=np.column_stack((t[:,0]+pos[0],pos[2]-t[:,1]));e0=t[1]-t[0];e1=t[2]-t[0];d=e0[0]*e1[1]-e0[1]*e1[0]
            if abs(d)<1e-10:continue
            q=samples-t[0];u=(q[:,0]*e1[1]-q[:,1]*e1[0])/d;v=(e0[0]*q[:,1]-e0[1]*q[:,0])/d;covered|=(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)
    return float(covered.mean())
def run(path=None):
    path=Path(path or HERE/'greenery_contract.json');data=json.loads(path.read_text());errors=[];results=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    check(len(data['assets'])==23,'Exactly 23 botanical placements required');check(data['budget']['prospective_total_cap']==126,'Total cap');check(collections.Counter(a['parent_design_id'] for a in data['assets'])=={'AST-BOT-003':11,'AST-BOT-002':6,'AST-BOT-007':6},'Exact parent ownership/count')
    for a in data['assets']:
        name=a['name'];parts={p['name']:p for p in a['parts']};check(len(parts)==len(a['parts']),name+' duplicate semantic part');edges={};roots=set(a['root_parts']);check(roots<=parts.keys(),name+' missing root')
        for j in a['joints']:
            check(j['child'] in parts and j['parent'] in parts,name+' missing joint target');check(j['child'] not in edges,name+' multiply-parented support');edges[j['child']]=j['parent']
        for n in parts:
            seen=set();p=n
            while p not in roots and p in edges and p not in seen:seen.add(p);p=edges[p]
            check(p in roots,name+'/'+n+' no acyclic root support path')
        for p in parts.values():
            v=np.array(p['vertices']);check(np.isfinite(v).all(),name+'/'+p['name']+' nonfinite vertex');check(len(p['loop_uvs'])==sum(map(len,p['faces'])),name+' UV count');check(np.isfinite(p['loop_uvs']).all(),name+' nonfinite UV');check(p['material_role'] in ['botanical_bark','botanical_leaf_jade','botanical_leaf_sage','botanical_leaf_olive','botanical_flower'],name+' unauthorized material role')
            w=np.column_stack((v[:,0]+a['position_xyz'][0],v[:,2]+a['position_xyz'][1],a['position_xyz'][2]-v[:,1]));bad=[q.tolist() for q in w if not any(in_box(q,r['bounds']) for r in a['approved_reservations'])];check(not bad,name+'/'+p['name']+' outside approved envelope '+str(bad[:1]))
            # Every generated face must have nonzero area; supports must be closed.
            check(all(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-10 for t in triangles(p)),name+'/'+p['name']+' degenerate triangulation')
            if p['surface_kind']=='closed_support':
                counts=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in p['faces'] for i in range(len(f)));check(set(counts.values())=={2},name+'/'+p['name']+' support not topologically closed')
            if p['name'] in roots and a['kind']!='wet_whorl':
                feet=w[np.abs(v[:,2])<1e-7];check(len(feet)>=6,name+' insufficient physical soil contact vertices');check(all(in_polygon([q[0],q[2]],a['soil_polygon_xz']) for q in feet),name+' root outside actual octagon')
        row=dict(name=name,parts=a['part_count'],triangles=a['planned_triangle_count'],bounds_world=a['bounds_world'],root_count=len(roots),connected_parts=len(parts))
        if a['kind']=='basal':
            cov=projected_coverage(a);row['basal_leaf_vertical_soil_coverage_fraction']=cov;check(cov>=.67,name+' broad basal cover below 67% gate: '+str(cov))
        if a['kind']=='wet_whorl':check(a['bounds_local'][0][2]>=.025 and a['bounds_local'][1][2]<=.48,name+' wet crown fit')
        results.append(row)
    out=dict(status='PASS' if not errors else 'FAIL',scope='Pure planned geometry only; not evaluated Blender, contacts, source render, export or runtime acceptance',contract_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),assets=results,errors=errors)
    (HERE/'CONTRACT_CHECK_REPORT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return out
if __name__=='__main__':sys.exit(0 if run(sys.argv[1] if len(sys.argv)>1 else None)['status']=='PASS' else 1)
