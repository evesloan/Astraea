from pathlib import Path
import json,struct,hashlib,math
ROOT=Path(__file__).resolve().parents[1];report=json.loads((ROOT/'qa/SOURCE_PRESERVATION.json').read_text());spec=report['receiving_spec']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FORMATS={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)};WIDTH={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def load(path):
    raw=Path(path).read_bytes();assert struct.unpack_from('<4sII',raw,0)==(b'glTF',2,len(raw));offset=12;doc=None;binary=None
    while offset<len(raw):
        size,kind=struct.unpack_from('<II',raw,offset);data=raw[offset+8:offset+8+size];offset+=8+size
        if kind==0x4e4f534a:doc=json.loads(data)
        elif kind==0x004e4942:binary=data
    def accessor(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];fmt,size=FORMATS[a['componentType']];width=WIDTH[a['type']];step=v.get('byteStride',size*width);start=v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*width,binary,start+i*step) for i in range(a['count'])]
    records={};triangles={}
    for node in doc['nodes']:
        name=node['name'];row={k:v for k,v in node.items() if k not in ['mesh','children']}
        if 'mesh' in node:
            assert not any(k in node for k in ['matrix','translation','rotation','scale']),('Expected baked retained core mesh',name)
            primitives=[];tris=[]
            for pr in doc['meshes'][node['mesh']]['primitives']:
                attrs={k:accessor(v) for k,v in pr['attributes'].items()};inds=accessor(pr['indices']);mat=doc['materials'][pr['material']]
                primitives.append({'attributes':attrs,'indices':inds,'material':mat,'mode':pr.get('mode',4)})
                pos=attrs['POSITION'];idx=[i[0] for i in inds]
                assert all(math.isfinite(x) for p in pos for x in p)
                for i in range(0,len(idx),3):tris.append([(pos[idx[i+j]][0],pos[idx[i+j]][1],pos[idx[i+j]][2]-432) for j in range(3)])
            row['primitives']=primitives;triangles[name]=tris
        records[name]=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    images=[]
    for im in doc.get('images',[]):
        view=doc['bufferViews'][im['bufferView']];start=view.get('byteOffset',0);images.append(hashlib.sha256(binary[start:start+view['byteLength']]).hexdigest())
    return records,triangles,sorted(images)

old,oldtris,oldimages=load(spec['existing_runtime_export']);new,newtris,newimages=load(report['export'])
preserved=set(old)-set(report['removed']);assert len(preserved)==905
diff=[n for n in preserved if old[n]!=new.get(n)];assert not diff,diff
assert set(old)-set(new)==set(report['removed']);assert set(new)-set(old)==set(report['added']);assert oldimages==newimages
sub=lambda a,b:tuple(x-y for x,y in zip(a,b));dot=lambda a,b:sum(x*y for x,y in zip(a,b));cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def ray(a,b,tri):
    p,q,r=tri;d=sub(b,a);e1=sub(q,p);e2=sub(r,p);h=cross(d,e2);det=dot(e1,h)
    if abs(det)<1e-10:return False
    inv=1/det;s=sub(a,p);u=inv*dot(s,h)
    if u< -1e-7 or u>1+1e-7:return False
    qv=cross(s,e1);v=inv*dot(d,qv)
    if v< -1e-7 or u+v>1+1e-7:return False
    t=inv*dot(e2,qv);return 1e-7<t<1-1e-7

clear=[]
for y in [21.05,21.4,22.2,23.35]:
    for z in [-433.75,-432,-430.25]:
        a=(-8.12,y,z);b=(-7.55,y,z);old_hits=[n for n in report['removed'] if any(ray(a,b,t) for t in oldtris[n])]
        new_hits=[n for n,tris in newtris.items() if any(ray(a,b,t) for t in tris)]
        assert old_hits and not new_hits,(a,new_hits)
        clear.append({'from':a,'to':b,'retained_preimage_blocked':old_hits,'new_derivative_clear':True})
bounds=[]
for part in spec['new_parts']:
    pts=[p for t in newtris[part['name']] for p in t];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];b=part['world_bounds_xyz'];expected_lo=[b[k][0] for k in ['x','y','z']];expected_hi=[b[k][1] for k in ['x','y','z']]
    assert all(abs(a-b)<3e-5 for a,b in zip(lo+hi,expected_lo+expected_hi)),part['name']
    center=[(a+b)/2 for a,b in zip(lo,hi)];a=[lo[0]-.02,center[1],center[2]];b=[hi[0]+.02,center[1],center[2]];assert any(ray(a,b,t) for t in newtris[part['name']])
    bounds.append({'name':part['name'],'actual_min_xyz':lo,'actual_max_xyz':hi,'positive_solid_ray':True})
out={'status':'PASS','old_export_sha256':sha(spec['existing_runtime_export']),'new_export_sha256':sha(report['export']),'preserved_native_nodes':len(preserved),'preserved_native_geometry_metadata_and_materials_exact':True,'packed_image_hashes_unchanged':True,'new_part_bounds_and_positive_contacts':bounds,'clear_aperture_rays_with_preimage_negative_controls':clear,'scope':'Actual native GLB source correspondence and bounded aperture/closure screen. No Godot import, floor support, clinical pressure, dynamic doors or player/cart acceptance.'}
(ROOT/'qa/NATIVE_RECEIVING_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','preserved_nodes':len(preserved),'new_parts':len(bounds),'clear_aperture_rays':len(clear),'export':out['new_export_sha256']}))
