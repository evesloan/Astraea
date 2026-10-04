"""Read-only actual GLB geometry utilities for independent Batch06 review.

No Blender-import axis reversal, author helper or author assertions are used.
"""
from pathlib import Path
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'qa'))
from inspect_glb_independent import GLB
C = np.array([[1.,0,0],[0,0,1],[0,-1,0]])

class Native:
    def __init__(self, path):
        self.path=Path(path); self.g=GLB(self.path)
        self.world={}; self.parents={}; self.tris=[]; self.materials=[]; self.nodes=[]
        self.node_vertices={}
        def visit(i, parent, ancestors):
            assert i not in ancestors
            n=self.g.doc['nodes'][i]; w=parent @ self.g.matrix(n); self.world[i]=w
            if 'mesh' in n:
                vv=[]
                for p in self.g.doc['meshes'][n['mesh']]['primitives']:
                    v=self.g.accessor(p['attributes']['POSITION'])
                    v=(np.column_stack([v,np.ones(len(v))])@w.T)[:,:3]
                    idx=self.g.accessor(p['indices']).ravel().reshape(-1,3)
                    t=v[idx]; self.tris.extend(t); vv.extend(v)
                    self.materials.extend([self.g.doc['materials'][p['material']]['name']]*len(t))
                    self.nodes.extend([n.get('name',str(i))]*len(t))
                self.node_vertices[i]=np.asarray(vv)
            for ch in n.get('children',[]):
                self.parents[ch]=i; visit(ch,w,ancestors|{i})
        for n in self.g.doc['scenes'][self.g.doc.get('scene',0)]['nodes']:
            visit(n,np.eye(4),set())
        self.tris=np.asarray(self.tris); self.materials=np.asarray(self.materials)
        self.nodes=np.asarray(self.nodes)

    def select(self, role=None, node=None):
        mask=np.ones(len(self.tris),bool)
        if role is not None: mask &= np.asarray([role in m for m in self.materials])
        if node is not None: mask &= np.asarray([node in n for n in self.nodes])
        return mask

    def nearest(self, p, role=None, node=None):
        mask=self.select(role,node); idx=np.where(mask)[0]; t=self.tris[mask]
        if not len(t): raise ValueError(('No matching triangles',role,node))
        p=np.asarray(p); a,b,c=t[:,0],t[:,1],t[:,2]; ab=b-a; ac=c-a
        n=np.cross(ab,ac); nn=np.einsum('ij,ij->i',n,n)
        proj=p-n*(np.einsum('ij,ij->i',p-a,n)/np.maximum(nn,1e-30))[:,None]
        v=proj-a; d00=np.einsum('ij,ij->i',ab,ab); d01=np.einsum('ij,ij->i',ab,ac)
        d11=np.einsum('ij,ij->i',ac,ac); d20=np.einsum('ij,ij->i',v,ab); d21=np.einsum('ij,ij->i',v,ac)
        den=d00*d11-d01*d01; u=(d11*d20-d01*d21)/np.maximum(den,1e-30)
        vv=(d00*d21-d01*d20)/np.maximum(den,1e-30)
        inside=(u>=0)&(vv>=0)&(u+vv<=1)&(nn>1e-20)
        candidates=[proj]; ds=[np.where(inside,np.sum((proj-p)**2,axis=1),np.inf)]
        for x,y in [(a,b),(b,c),(c,a)]:
            e=y-x; f=np.clip(np.einsum('ij,ij->i',p-x,e)/np.maximum(np.einsum('ij,ij->i',e,e),1e-30),0,1)
            q=x+f[:,None]*e; candidates.append(q); ds.append(np.sum((q-p)**2,axis=1))
        ds=np.asarray(ds); kind,i=np.unravel_index(np.argmin(ds),ds.shape); k=idx[i]
        normal=n[i]/max(np.linalg.norm(n[i]),1e-30)
        return {'distance_m':float(np.sqrt(ds[kind,i])), 'point_gltf_m':candidates[kind][i].tolist(),
                'normal_gltf':normal.tolist(), 'material':str(self.materials[k]),
                'node':str(self.nodes[k]), 'triangle_index':int(k)}

    def segment_hits(self, a, b, role=None, node=None, eps=1e-8):
        """Moller-Trumbore finite segment intersections, including double sides."""
        a=np.asarray(a,float); b=np.asarray(b,float); d=b-a
        mask=self.select(role,node); inds=np.where(mask)[0]; t=self.tris[mask]
        e1=t[:,1]-t[:,0]; e2=t[:,2]-t[:,0]; h=np.cross(d,e2)
        det=np.einsum('ij,ij->i',e1,h); good=np.abs(det)>eps
        f=np.zeros_like(det); f[good]=1/det[good]; s=a-t[:,0]
        u=f*np.einsum('ij,ij->i',s,h); q=np.cross(s,e1)
        v=f*(q@d); frac=f*np.einsum('ij,ij->i',e2,q)
        good &= (u>=-eps)&(v>=-eps)&(u+v<=1+eps)&(frac>=-eps)&(frac<=1+eps)
        hitinds=np.where(good)[0]; hitinds=hitinds[np.argsort(frac[hitinds])]
        return [{'fraction':float(frac[i]),'point_gltf_m':(a+frac[i]*d).tolist(),
                 'node':str(self.nodes[inds[i]]),'material':str(self.materials[inds[i]]),
                 'triangle_index':int(inds[i])} for i in hitinds]

def rotate_axis(v, axis, angle):
    axis=np.asarray(axis,float);axis/=np.linalg.norm(axis);v=np.asarray(v,float)
    return v*np.cos(angle)+np.cross(axis,v)*np.sin(angle)+axis*np.dot(axis,v)*(1-np.cos(angle))
