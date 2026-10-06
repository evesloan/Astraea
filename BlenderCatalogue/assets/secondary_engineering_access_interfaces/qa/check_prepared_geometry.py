"""Pure source-proposal dimensions/contact checks. Never engine acceptance."""
from pathlib import Path
import json,hashlib,math,struct,unittest
R=Path(__file__).resolve().parents[1];C=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clipped_triangle(tri,bounds,eps=1e-7):
    p=[list(v) for v in tri]
    for axis,lo,hi in zip(range(3),bounds[:3],bounds[3:]):
        for edge,sign in [(lo+eps,1),(hi-eps,-1)]:
            q=[]
            for a,b in zip(p,p[1:]+p[:1]):
                ia=sign*(a[axis]-edge)>=0;ib=sign*(b[axis]-edge)>=0
                if ia:q.append(a)
                if ia!=ib:
                    t=(edge-a[axis])/(b[axis]-a[axis]);q.append([a[k]+t*(b[k]-a[k]) for k in range(3)])
            p=q
            if not p:return False
    return len(p)>=3
F=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def boxtris(b):
    a,c,e,d,f,g=b;v=[(x,y,z) for y in [c,f] for x,z in [(a,e),(d,e),(d,g),(a,g)]]
    return [[v[i] for i in (p[0],p[j],p[j+1])] for p in F for j in range(1,len(p)-1)]
def glb(path):
    b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);off=20+n;binary=b[off+8:]
    def acc(i):
        a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];w={'SCALAR':1,'VEC3':3}[a['type']];stride=v.get('byteStride',struct.calcsize(fmt)*w);start=v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*w,binary,start+j*stride) for j in range(a['count'])]
    parent={c:i for i,n in enumerate(d['nodes']) for c in n.get('children',[])}
    def point(p,i):
        n=d['nodes'][i]
        if 'matrix' in n:
            m=n['matrix'];p=[sum(m[k+4*j]*p[j] for j in range(3))+m[k+12] for k in range(3)]
        else:
            p=[a*s for a,s in zip(p,n.get('scale',[1,1,1]))];x,y,z,w=n.get('rotation',[0,0,0,1]);u=[x,y,z];cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];t=[2*q for q in cross(u,p)];c=cross(u,t);p=[p[k]+w*t[k]+c[k]+n.get('translation',[0,0,0])[k] for k in range(3)]
        return point(p,parent[i]) if i in parent else p
    rows=[]
    for i,node in enumerate(d['nodes']):
        if 'mesh' not in node:continue
        for primitive in d['meshes'][node['mesh']]['primitives']:
            vs=[point(p,i) for p in acc(primitive['attributes']['POSITION'])];idx=[v[0] for v in acc(primitive['indices'])] if 'indices' in primitive else list(range(len(vs)))
            rows.extend((node.get('name','')+'@'+d['nodes'][parent[i]].get('name','') if i in parent else node.get('name',''),[vs[idx[k+j]] for j in range(3)]) for k in range(0,len(idx),3))
    return rows

def proposed_tall(rows):
    out=[]
    for n,t in rows:
        mapping={};base=n.split('@')[0].split('.')[0]
        if base=='ENTRY_fixed_ivory_enamel':mapping={2.5:2.7}
        elif base=='ENTRY_fixed_warm_walnut':mapping={2.32:2.52,2.5:2.7,2.64:2.84,2.66:2.86}
        elif base=='ENTRY_moving_ivory_enamel':mapping={2.445:2.645,2.485:2.685}
        elif base=='ENTRY_moving_champagne_metal':mapping={2.485:2.685}
        out.append((n,[[p[0],next((v for k,v in mapping.items() if abs(p[1]-k)<2e-6),p[1]),p[2]] for p in t]))
    return out
class Prepared(unittest.TestCase):
    def test_pins(self):
        for p,h in json.loads((R/'source/input_pins.json').read_text())['inputs'].items():self.assertEqual(sha(Path(p)),h,p)
    def test_source_section_prism_and_shoulders(self):
        plan=json.loads((C/'assets/secondary_engineering_section/source/geometry_plan.json').read_text());prism=[7.8,6,-433.2,9.1,8.7,-430.8];count=0
        for p in plan['parts']:
            if not p['export']:continue
            count+=1;v=p['vertices_xyz']
            for f in p['faces']:
                for j in range(1,len(f)-1):self.assertFalse(clipped_triangle([v[f[0]],v[f[j]],v[f[j+1]]],prism),p['name'])
        self.assertEqual(count,175)
        for z0,z1 in [(-433.8,-433.2),(-430.8,-430.2)]:
            for t in boxtris([8.31,6,z0,8.69,8.7,z1]):self.assertFalse(clipped_triangle(t,prism));self.assertFalse(clipped_triangle(t,[8.745,6,-434.56,8.855,8.7,-429.44]))
    def test_current_core_bounded_triangle_proposal(self):
        rows=glb(C/'assets/grand_pool_orchard_section/exports/AST-CIR-005_forward_pool_market.glb')
        prism=[7.635,6,-1.8,7.88,8.7,1.8];removed=[];retained=[]
        bounds=[[7.72,6,-13,7.88,11.76,20],[7.635,6.12,-13,7.685,6.78,20]]
        counts=[0,0]
        for n,t in rows:
            which=next((i for i,b in enumerate(bounds) if all(b[k]-2e-5<=p[k]<=b[k+3]+2e-5 for p in t for k in range(3)) and all(min(abs(p[k]-b[k]),abs(p[k]-b[k+3]))<2e-5 for p in t for k in range(3))),None)
            if which is not None:removed.append(t);counts[which]+=1
            else:retained.append(t)
        self.assertEqual(counts,[12,12]);self.assertTrue(any(clipped_triangle(t,prism) for t in removed))
        new=[]
        for b in bounds:
            for z0,z1 in [(-13,-1.8),(1.8,20)]:new+=boxtris([b[0],b[1],z0,b[3],b[4],z1])
        new+=boxtris([7.72,8.7,-1.8,7.88,11.76,1.8])
        for t in retained+new:self.assertFalse(clipped_triangle(t,prism),t)
        self.assertEqual(len(rows)-len(retained),24)
    def test_actual_old_door_triangle_proposal_sweep(self):
        rows=proposed_tall(glb(C/'assets/guest_entry_door/exports/AST-DOR-002_wide.glb'))
        self.assertAlmostEqual(max(p[1] for _,t in rows for p in t),2.86)
        # Source-only hypothesis using actual old triangles plus bounded Y map. New GLB must independently pass.
        moving=[(n,t) for n,t in rows if '_moving_' in n];fixed=[t for n,t in rows if '_fixed_' in n]
        self.assertTrue(moving)
        for f in [0,.15,.5,.85,1]:
            posed=[]
            for n,t in moving:
                sign=-1 if '@LEAF_LEFT' in n else 1;assert '@LEAF_' in n,n
                posed.append([[p[0]+sign*1.24*f,p[1],p[2]] for p in t])
            for t in posed:
                for p in t:self.assertGreaterEqual(p[1],.035-2e-6);self.assertLessEqual(p[1],2.685+2e-6)
            for root in ['LEAF_LEFT','LEAF_RIGHT']:
                verts=[p for (n,_),t in zip(moving,posed) if '@'+root in n for p in t]
                bounds=[min(p[k] for p in verts) for k in range(3)]+[max(p[k] for p in verts) for k in range(3)]
                for t in fixed:self.assertFalse(clipped_triangle(t,bounds),(f,root,t))
            if f==1:
                for t in fixed+posed:self.assertFalse(clipped_triangle(t,[-1.2,0,-.055,1.2,2.7,.055]),t)
        # Existing hollow cavity and proposed shoulders separated; surface joins excluded.
        self.assertAlmostEqual(2.7-2.685,.015);self.assertAlmostEqual(8.745-8.69,.055)
    def test_contacts_and_sweep(self):
        self.assertAlmostEqual(1.36-2.65/2,.035);self.assertAlmostEqual(1.36+2.65/2,2.685)
        self.assertAlmostEqual(1.43-2.86/2,0);self.assertAlmostEqual(1.43+2.86/2,2.86)
        self.assertAlmostEqual(.2*3.6,.72)
if __name__=='__main__':unittest.main(verbosity=2)
