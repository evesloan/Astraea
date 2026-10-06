"""Read actual retained GLB triangles, without Blender or Godot. Writes only here."""
from pathlib import Path
import json, struct, math, hashlib
import numpy as np
OUT=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
BATCH=CAT/'assets/residential_production_batch'
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(n):
    if 'matrix' in n:return np.array(n['matrix']).reshape((4,4),order='F')
    x,y,z,w=n.get('rotation',[0,0,0,1]);r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4);m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
C=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]])
def decode(path):
    b=Path(path).read_bytes();magic,version,length=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and length==len(b)
    chunks={};cursor=12
    while cursor<len(b):
        size,kind=struct.unpack_from('<II',b,cursor);chunks[kind]=b[cursor+8:cursor+8+size];cursor+=8+size
    j=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
    def access(i):
        a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']];s=np.dtype(dt).itemsize
        return np.ndarray((a['count'],c),dtype=dt,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',s*c),s)).copy()
    rows=[];marks={}
    def walk(i,parent,chain):
        n=j['nodes'][i];m=parent@matrix(n);name=n.get('name','');chain=chain+[name];sm=C@m
        marks[name]=sm[:3,3]
        if 'mesh' in n:
            for p in j['meshes'][n['mesh']]['primitives']:
                assert p.get('mode',4)==4
                v=access(p['attributes']['POSITION']);v=(np.c_[v,np.ones(len(v))]@sm.T)[:,:3];inds=access(p['indices']).flatten().reshape((-1,3));tri=v[inds]
                rows.append({'name':name,'chain':chain,'triangles':tri,'material':j.get('materials',[])[p['material']].get('name','') if 'material'in p else ''})
        for child in n.get('children',[]):walk(child,m,chain)
    for i in j['scenes'][j.get('scene',0)]['nodes']:walk(i,np.eye(4),[])
    return rows,marks

def rz(t):
    c,s=math.cos(t),math.sin(t);return np.array([[c,-s,0],[s,c,0],[0,0,1.]])
def transform(tris,point,yaw):return tris@rz(yaw).T+np.array(point)
def merge(rows):return np.concatenate([r['triangles'] for r in rows])
def hits(tris,a,b):
    a=np.array(a);d=np.array(b)-a;e1=tris[:,1]-tris[:,0];e2=tris[:,2]-tris[:,0];p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p);valid=np.abs(det)>1e-9;inv=np.zeros_like(det);inv[valid]=1/det[valid];t=a-tris[:,0];u=np.einsum('ij,ij->i',t,p)*inv;q=np.cross(t,e1);v=np.einsum('j,ij->i',d,q)*inv;r=np.einsum('ij,ij->i',e2,q)*inv
    return bool(np.any(valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(r>=1e-8)&(r<=1-1e-8)))
def box(lo,hi):
    lo=np.array(lo);hi=np.array(hi);v=np.array([[hi[k]if i&(1<<k)else lo[k]for k in range(3)]for i in range(8)])
    inds=np.array([(0,2,3),(0,3,1),(4,5,7),(4,7,6),(0,1,5),(0,5,4),(2,6,7),(2,7,3),(0,4,6),(0,6,2),(1,3,7),(1,7,5)])
    return v[inds]

def sample_rays(tris,rays):
    failures=[{'label':label,'from':list(a),'to':list(b)}for label,a,b in rays if not hits(tris,a,b)]
    return {'tested':len(rays),'unblocked':len(failures),'examples':failures[:24]}

if __name__=='__main__':
    paths=sorted((BATCH/'outputs/production_r005').glob('*/shell.glb'))
    doorpath=CAT/'assets/guest_privacy_door/exports/AST-DOR-001.glb';door,dm=decode(doorpath)
    dstatic=merge([r for r in door if 'HINGE_LEFT'not in r['chain']]);dleaf=merge([r for r in door if 'HINGE_LEFT'in r['chain']]);dpoint=(-.7,2.9,0);dyaw=math.pi/2
    doortri=transform(merge(door),dpoint,dyaw);statictri=transform(dstatic,dpoint,dyaw);leaftri=transform(dleaf,dpoint,dyaw)
    header_patch=box([-.755,2.36,2.10],[-.735,3.44,2.25])
    corner_patch=box([-.84,.12,0],[-.70,.24,2.60])
    # Exact sightlines use shell/door boundaries only: a fixture cannot mask an enclosure defect.
    probes=[('front_corner_z_'+str(z),(-.78,-.2,z),(-.78,.5,z))for z in [.3,.6,1.,1.3,1.6,2.,2.3,2.55]]
    probes += [('door_head_z_'+str(z),(-.4,2.9,z),(-1.2,2.9,z))for z in [2.155,2.165,2.175]]
    envelope=[]
    for z in [.3,.6,1.,1.3,1.6,2.,2.3,2.55]:
        for x in np.arange(-3.43,-.761,.01):envelope.append(('front',tuple([float(x),-.2,z]),tuple([float(x),.5,z])))
        for y in np.arange(.25,3.93,.01):
            envelope.append(('inner',(-.4,float(y),z),(-1.2,float(y),z)))
            envelope.append(('outer',(-3.8,float(y),z),(-3.2,float(y),z)))
        for x in np.arange(-3.43,-.77,.03):envelope.append(('return',(float(x),4.3,z),(float(x),3.7,z)))
    for x in np.arange(-3.4,-.77,.1):
        for y in np.arange(.25,3.91,.1):envelope.append(('ceiling',(float(x),float(y),2.90),(float(x),float(y),2.3)))
    rows=[]
    # Shared bathroom geometry is checked independently in every generated prototype.
    for path in paths:
        shell,sm=decode(path);tri=np.concatenate([merge(shell),doortri]);proposed=np.concatenate([tri,corner_patch,header_patch])
        rows.append({'prototype':path.parent.name,'sha256':sha(path),'triangles':len(merge(shell)),'probe_before':sample_rays(tri,probes),'probe_after_analytic_patch':sample_rays(proposed,probes),'bath_markers':{n:v.tolist()for n,v in sm.items()if n.startswith('DATUM_bath')}})
    shell,sm=decode(paths[0]);tri=np.concatenate([merge(shell),doortri]);proposed=np.concatenate([tri,corner_patch,header_patch]);envelope_results={'before':sample_rays(tri,envelope),'after_analytic_patch':sample_rays(proposed,envelope)}
    fixtures=[]
    for marker,aid in [('bath_vanity','AST-SAN-001'),('bath_wc','AST-SAN-002'),('bath_shower','AST-SAN-003')]:
        p=CAT/'assets/guest_wash/exports'/(aid+'.glb');rr,mm=decode(p);tt=merge(rr)+sm['DATUM_'+marker];fixtures.append({'label':marker,'asset':aid,'sha256':sha(p),'source_bounds':[tt.min(axis=(0,1)).tolist(),tt.max(axis=(0,1)).tolist()],'standing_source':(mm['DATUM_standing']+sm['DATUM_'+marker]).tolist()})
    report={'scope':'Read-only GLB triangle decode and analytic source correction. No Blender/Godot execution. Not runtime acceptance.','engine_jobs':0,'door_sha256':sha(doorpath),'door_matches_game':sha(doorpath)==sha(GAME/'assets/models/AST-DOR-001.glb'),'door_hierarchy':[{k:v for k,v in r.items()if k!='triangles'}for r in door],'hinge_source':dm['HINGE_LEFT'].tolist(),'door_static_bounds_source':[statictri.min(axis=(0,1)).tolist(),statictri.max(axis=(0,1)).tolist()],'door_leaf_bounds_source':[leaftri.min(axis=(0,1)).tolist(),leaftri.max(axis=(0,1)).tolist()],'fixtures':fixtures,'prototypes':rows,'sampled_boundary_rays':envelope_results,'analytic_patch_bounds':{'entry_corner_closure':[[-.84,.12,0],[-.70,.24,2.60]],'bath_door_head_stop':[[-.755,2.36,2.10],[-.735,3.44,2.25]]}}
    (OUT/'BATHROOM_GLB_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['scope','door_matches_game','door_static_bounds_source','door_leaf_bounds_source','fixtures','sampled_boundary_rays']},indent=2));print('PROTOTYPES',len(rows),'before',rows[0]['probe_before']['unblocked'],'after',rows[0]['probe_after_analytic_patch']['unblocked'])
