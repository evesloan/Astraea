"""Independent GLB decode and plan checks; no Godot, imports or model edits."""
from pathlib import Path
import json,struct,hashlib,math,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];rev=sys.argv[1] if len(sys.argv)>1 else 'r002'
plan_name=sys.argv[2] if len(sys.argv)>2 else 'NEIGHBORHOOD_PLAN.json'
plan=json.loads((ROOT/plan_name).read_text());byid={r['address']:r for r in plan['rooms']}
def matrix(n):
    if 'matrix' in n:return np.array(n['matrix']).reshape((4,4),order='F')
    x,y,z,w=n.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    m=np.eye(4);m[:3,:3]=rot@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
def decode(path):
    b=path.read_bytes();magic,version,length=struct.unpack_from('<III',b,0);assert magic==0x46546c67 and version==2 and length==len(b)
    cursor=12;chunks={}
    while cursor<len(b):
        size,kind=struct.unpack_from('<II',b,cursor);chunks[kind]=b[cursor+8:cursor+8+size];cursor+=8+size
    j=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
    def accessor(i):
        a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']];item=np.dtype(dtype).itemsize
        return np.ndarray((a['count'],components),dtype=dtype,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',item*components),item)).copy()
    points=[];marks={};triangle_count=0
    def walk(i,parent):
        nonlocal triangle_count
        n=j['nodes'][i];m=parent@matrix(n);name=n.get('name','')
        if name.startswith('DATUM_'):marks[name]=m[:3,3]
        if 'mesh' in n:
            for p in j['meshes'][n['mesh']]['primitives']:
                xyz=accessor(p['attributes']['POSITION']);q=np.c_[xyz,np.ones(len(xyz))]@m.T;points.extend(q[:,:3]);triangle_count+=len(accessor(p['indices']))//3
        for c in n.get('children',[]):walk(c,m)
    for i in j['scenes'][j.get('scene',0)]['nodes']:walk(i,np.eye(4))
    return j,np.array(points),marks,triangle_count
rows=[]
for path in sorted((ROOT/'outputs'/rev).glob('*/shell.glb')):
    address=path.parent.name;r=byid[address];receipt=json.loads((path.parent/'SOURCE_RECEIPT.json').read_text());j,points,markers,tri=decode(path)
    lo,hi=np.min(points,axis=0),np.max(points,axis=0);slo,shi=receipt['shell_stats']['source_bounds']
    expect_lo=np.array([slo[0],slo[2],-shi[1]]);expect_hi=np.array([shi[0],shi[2],-slo[1]])
    err=max(float(np.abs(lo-expect_lo).max()),float(np.abs(hi-expect_hi).max()));assert err<1e-5
    assert tri==receipt['shell_stats']['triangles'],(address,tri,receipt['shell_stats']['triangles'])
    assert len(j['meshes'])<=10
    for a in r['bed_anchors']:
        u,v,w=a['source_xyz'];actual=markers['DATUM_bed_'+str(a['historical_anchor_index'])]
        assert np.linalg.norm(actual-np.array([u,w,-v]))<1e-5
        yaw=r['source_yaw_godot'];x,z=actual[0],actual[2];world=np.array([math.cos(yaw)*x+math.sin(yaw)*z,actual[1],-math.sin(yaw)*x+math.cos(yaw)*z])+r['source_origin_world_xyz']
        if not address.startswith('PROTO__'):assert np.linalg.norm(world-a['world_xyz'])<1e-5
    if r['view_policy']!='real_atrium_candidate':assert not any('glass' in m.get('name','').lower() for m in j.get('materials',[]))
    rows.append({'address':address,'bounds_max_error_m':err,'shell_triangles':tri,'export_mesh_batches':len(j['meshes']),
      'checked_rest_anchor_count':len(r['bed_anchors']),'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
receipt={'status':'PASS_SOURCE_EXPORT_DECODE','revision':rev,'rooms':rows,'engine_jobs':0,
 'checks':['Complete GLB node hierarchy decoded','Y-up exchange bounds match evaluated source','Triangle totals preserved','Rest nodes match declared local coordinates; world positions also checked for non-prototype rooms','At most10 static shell material batches','No glass in rooms without a verified view candidate'],
 'limits':['No furniture contact/door-sweep/capsule/cart test','No normal Godot arrival or visuals','No final body/species fit','No overall district completion']}
(ROOT/'qa'/('SOURCE_EXPORT_CHECKS_'+rev+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
