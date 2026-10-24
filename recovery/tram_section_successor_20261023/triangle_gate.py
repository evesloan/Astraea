#!/usr/bin/env python3
"""Source triangle/capsule checks for this bounded tram section; never admission.

Triangles are transformed through GLTF nodes, clipped to the actual Y interval,
then tested against the full projected polyline capsule (not vertex sampling).
No engine, source replacement or false whole-world clearance claim.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, struct, sys
sys.dont_write_bytecode = True
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PINS={}

def raw(path):
    path=path.resolve();data=path.read_bytes();PINS[str(path.relative_to(ROOT))]={"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()};return data

def glb(path, origin=(0,0,0), yaw=0):
    data=raw(path);assert struct.unpack_from('<4sII',data)==(b'glTF',2,len(data))
    size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
    doc=json.loads(data[20:20+size]);bs,bk=struct.unpack_from('<II',data,20+size);assert bk==0x004e4942
    binary=data[28+size:28+size+bs]
    def accessor(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];assert 'sparse' not in a
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dtype).itemsize
        return np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',item*n),item)).copy()
    def matrix(node):
        if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
        x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4)
        m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(node.get('scale',[1,1,1]))
        m[:3,3]=node.get('translation',[0,0,0]);return m
    world=np.eye(4);world[:3,:3]=[[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]];world[:3,3]=origin
    def visit(index,parent,ancestors):
        node=doc['nodes'][index];transform=parent@matrix(node);name=node.get('name',str(index))
        if 'mesh' in node:
            for pi,p in enumerate(doc['meshes'][node['mesh']]['primitives']):
                assert p.get('mode',4)==4
                points=accessor(p['attributes']['POSITION']).astype(float)@transform[:3,:3].T+transform[:3,3]
                indices=accessor(p['indices']).reshape(-1) if 'indices' in p else np.arange(len(points))
                yield {'name':name,'primitive':pi,'points':points,'indices':indices.reshape(-1,3),'triangles':points[indices].reshape(-1,3,3),'ancestors':ancestors,'material':doc.get('materials',[])[p['material']] if 'material' in p else {}}
        for child in node.get('children',[]):yield from visit(child,transform,ancestors+[name])
    for index in doc['scenes'][doc.get('scene',0)]['nodes']:yield from visit(index,world,[])

def clip_y(poly,value,above):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        aa=a[1]>=value if above else a[1]<=value;bb=b[1]>=value if above else b[1]<=value
        if aa:result.append(a)
        if aa!=bb:result.append(a+(b-a)*((value-a[1])/(b[1]-a[1])))
    return result

def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]

def point_segments(point,a,b):
    delta=b-a;dd=np.sum(delta*delta,axis=1)
    t=np.clip(np.sum((point-a)*delta,axis=1)/np.maximum(dd,1e-24),0,1)
    return np.linalg.norm(point-(a+t[:,None]*delta),axis=1)

def polygon_route_distance(poly,route):
    a,b=route[:-1],route[1:];distance=np.inf
    # Polygon endpoints to route edges, route endpoints to polygon edges, plus
    # edge crossings and endpoints inside a nondegenerate convex projection.
    for p,q in zip(poly,poly[1:]+poly[:1]):
        distance=min(distance,float(point_segments(p,a,b).min()),float(point_segments(q,a,b).min()))
        edge=q-p;den=float(edge@edge)
        if den<1e-24:continue
        for points in (a,b):
            t=np.clip((points-p)@edge/den,0,1);distance=min(distance,float(np.linalg.norm(points-(p+t[:,None]*edge),axis=1).min()))
        ca=cross(edge,a-p);cb=cross(edge,b-p);cp=cross(b-a,p-a);cq=cross(b-a,q-a)
        if np.any((ca*cb<0)&(cp*cq<0)):return 0.
    area=sum(cross(p,q) for p,q in zip(poly,poly[1:]+poly[:1]))
    if abs(area)>1e-10:
        signs=np.array([cross(q-p,route-p) for p,q in zip(poly,poly[1:]+poly[:1])])
        if np.any(np.all(signs>=-1e-10,axis=0)|np.all(signs<=1e-10,axis=0)):return 0.
    return distance

def swept_hits(triangles,route,band,radius=2):
    lo=np.min(triangles,axis=1);hi=np.max(triangles,axis=1)
    selected=np.flatnonzero((hi[:,1]>band[0]+1e-6)&(lo[:,1]<band[1]-1e-6)&(hi[:,0]>=route[:,0].min()-radius)&(lo[:,0]<=route[:,0].max()+radius)&(hi[:,2]>=route[:,1].min()-radius)&(lo[:,2]<=route[:,1].max()+radius))
    witnesses=[];count=0
    for index in selected:
        poly=clip_y(list(triangles[index]),band[0]+1e-6,True)
        if poly:poly=clip_y(poly,band[1]-1e-6,False)
        if len(poly)<2:continue
        dist=polygon_route_distance([p[[0,2]] for p in poly],route)
        if dist<radius-1e-6:
            count+=1
            if len(witnesses)<2:witnesses.append({'triangle':int(index),'distance_m':dist,'vertices':triangles[index].tolist()})
    return count,witnesses,len(selected)

def part_triangles(part):
    points=np.array(part['vertices']);indices=[]
    for face in part['faces']:
        indices.extend([face[0],face[i],face[i+1]] for i in range(1,len(face)-1))
    return points[np.array(indices)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert args.candidate.resolve().parent==HERE and args.output.resolve().parent==HERE and not args.output.exists()
    args.candidate=args.candidate.resolve()
    plan=json.loads(raw(args.candidate/'CANDIDATE.json'));parts=json.loads(raw(args.candidate/'MESHES.json'))
    route=np.array(plan['route_points_xz']);length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(route,axis=0),axis=1))]
    begin,end=plan['central_interval_m'];route=route[(length>=begin-1e-6)&(length<=end+1e-6)]
    protected=np.array(plan['protected_route_xz']);sources=[]
    core=json.loads(raw(ROOT/'Game/data/architecture/PRIMARY_ATRIUM_CORE.json'))
    sources += [('core',ROOT/'Game/assets/models'/core.get('enclosure_file','AST-CIR-005.glb'),core['origin'],0),('atrium',ROOT/'Game/assets/models/AST-ATR-001.glb',(0,0,0),0)]
    for x,z in [(-31,-18),(-31,18),(31,-18),(31,18),(-18,-46),(18,-46),(-18,46),(18,46)]:
        yaw=(0 if x>0 else math.pi)if abs(x)>abs(z)else(math.pi/2 if z<0 else -math.pi/2)
        for filename in ['AST-STR-001-H826.glb','AST-STR-002-H826.glb']:sources.append((f'{filename}@{x},{z}',ROOT/'Game/assets/models'/filename,(x,52.5,z),yaw))
    for code in ['014_central_source','017_receiving_module','018_central_stair_receiving']:
        sources.append((code,ROOT/f'Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-{code}.glb',(0,0,0),0))
    removed_prefix=('M003_Site_','M003_UnderwebGirder_','M003_SouthFoot_')
    removed_exact={'V2_Central_NorthEnd_infill','V2_Central_NorthEnd_rail','V2__CENTRAL__Boarding_Post_-73.2','V2__CENTRAL__Boarding_Post_-70.8','V2__CENTRAL__Boarding_Header'}
    hits=[];counts={'source_triangles':0,'source_band_candidates':0,'candidate_triangles':0};removed=[]
    for label,path,origin,yaw in sources:
        for obj in glb(path,origin,yaw):
            if obj['name'].startswith(removed_prefix)or obj['name']in removed_exact:removed.append(label+'/'+obj['name']);continue
            counts['source_triangles']+=len(obj['triangles'])
            n,w,c=swept_hits(obj['triangles'],route,[55.55,60.1]);counts['source_band_candidates']+=c
            if n:hits.append({'kind':'retained_source_in_new_route','owner':label+'/'+obj['name'],'triangles':n,'witnesses':w})
    for part in parts:
        triangles=part_triangles(part);counts['candidate_triangles']+=len(triangles)
        for kind,path,band in [('new_part_in_protected_lower',protected,[52.55,56.55]),('new_part_in_upper_running',route,[56.1,60.1])]:
            n,w,_=swept_hits(triangles,path,band)
            if n:hits.append({'kind':kind,'owner':part['name'],'triangles':n,'witnesses':w})
    report={'schema':'astraea.tram.section.triangle_gate.r002','status':'FAIL'if hits else'BOUNDED_SOURCE_TRIANGLES_CLEAR','scope':'Retained core/atrium/8 bearings, CENTRAL station/stair/retained receivers, authored candidate; NOT whole ship or physical admission','candidate':str(args.candidate.relative_to(ROOT)),'counts':counts,'hits':hits,'planned_removed_parts':removed,'source_pins':PINS,'remaining':['All later district details and live installed contacts','Whole-path body swept hull on curves','Apron/stair/access connected engine checks','Actual support/native inspection and load capacity','Docking/bridge/door/joint physical gate; all admission stays false']}
    args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'counts':counts,'hit_owners':[(x['kind'],x['owner'],x['triangles'])for x in hits]}))

if __name__=='__main__':main()
