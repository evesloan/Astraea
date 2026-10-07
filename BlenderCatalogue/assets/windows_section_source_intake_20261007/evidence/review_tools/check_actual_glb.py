"""Independent actual GLB node/vertex bounds, images, lights and floor exclusion."""
import json,struct,math,hashlib,argparse
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--glb',required=True);ap.add_argument('--bounds',required=True);ap.add_argument('--require-lights',action='store_true');args=ap.parse_args()
R=Path(args.package).resolve();assert R.is_relative_to(Path(__file__).resolve().parents[1]);p=(R/args.glb).resolve();assert p.is_relative_to(R);limits=json.loads(args.bounds);b=p.read_bytes()
magic,version,length=struct.unpack_from('<III',b,0);assert magic==0x46546c67 and version==2 and length==len(b)
n,kind=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n]);off=20+n
size,kind=struct.unpack_from('<II',b,off);blob=b[off+8:off+8+size]
I=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
def mul(a,b):return [sum(a[k*4+r]*b[c*4+k] for k in range(4)) for c in range(4) for r in range(4)]
def transform(n):
    if 'matrix' in n:return n['matrix']
    x,y,z,w=n.get('rotation',[0,0,0,1]);sx,sy,sz=n.get('scale',[1,1,1]);tx,ty,tz=n.get('translation',[0,0,0])
    return [(1-2*y*y-2*z*z)*sx,(2*x*y+2*z*w)*sx,(2*x*z-2*y*w)*sx,0,(2*x*y-2*z*w)*sy,(1-2*x*x-2*z*z)*sy,(2*y*z+2*x*w)*sy,0,(2*x*z+2*y*w)*sz,(2*y*z-2*x*w)*sz,(1-2*x*x-2*y*y)*sz,0,tx,ty,tz,1]
def point(m,p):return [sum(m[c*4+r]*p[c] for c in range(3))+m[12+r] for r in range(3)]
def positions(idx):
    a=g['accessors'][idx];assert a['componentType']==5126 and a['type']=='VEC3'
    v=g['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
    return [struct.unpack_from('<fff',blob,start+i*stride) for i in range(a['count'])]
cache={};mins=[float('inf')]*3;maxs=[-float('inf')]*3;nodes=[];bad=[]
def walk(i,parent):
    node=g['nodes'][i];M=mul(parent,transform(node));name=node.get('name',str(i));nodes.append(name)
    if 'mesh' in node:
        lo=[float('inf')]*3;hi=[-float('inf')]*3
        for prim in g['meshes'][node['mesh']]['primitives']:
            idx=prim['attributes']['POSITION']
            if idx not in cache:cache[idx]=positions(idx)
            for p in cache[idx]:
                q=point(M,p)
                assert all(math.isfinite(v) for v in q),name
                for k in range(3):lo[k]=min(lo[k],q[k]);hi[k]=max(hi[k],q[k]);mins[k]=min(mins[k],q[k]);maxs[k]=max(maxs[k],q[k])
        if any(lo[k]<limits[0][k]-.003 or hi[k]>limits[1][k]+.003 for k in range(3)):bad.append({'node':name,'min':lo,'max':hi})
    for c in node.get('children',[]):walk(c,M)
for i in g['scenes'][g.get('scene',0)]['nodes']:walk(i,I)
floor_names=[n for n in nodes if 'SOURCE_PREVIEW_ONLY' in n]
images=g.get('images',[]);external_images=[i for i in images if 'uri' in i and not i['uri'].startswith('data:')]
lights=g.get('extensions',{}).get('KHR_lights_punctual',{}).get('lights',[])
report={'glb_sha256':hashlib.sha256(b).hexdigest(),'actual_vertex_bounds_glb':[mins,maxs],'nodes':len(nodes),'unique_position_accessors':len(cache),'bad_bounds':bad,'preview_floor_nodes':floor_names,'embedded_images':len(images)-len(external_images),'external_images':external_images,'punctual_lights':len(lights),'pass':not bad and not floor_names and not external_images and bool(images) and (bool(lights) or not args.require_lights),'limitations':'Exchange geometry only. No runtime traversal, image quality, species fit or performance claim.'}
(R/'qa/receiving_source_review/ACTUAL_GLB_VERTEX_CHECK.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['pass']
