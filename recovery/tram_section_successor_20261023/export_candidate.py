#!/usr/bin/env python3
"""Deterministic source-only GLB authoring; no engine/import/native execution.

The section uses the retained CENTRAL material/image bytes. Bridge fixed members,
hinge/knuckles, topology, material identities and final tongue dimensions survive.
"""
from pathlib import Path
import argparse, copy, hashlib, json, struct, sys
sys.dont_write_bytecode=True
import numpy as np
from triangle_gate import glb, part_triangles
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def read_glb(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);nb=struct.unpack_from('<I',raw,20+n)[0]
    return doc,bytearray(raw[28+n:28+n+nb])

def write_glb(path,doc,binary):
    assert not path.exists()
    binary+=b'\0'*(-len(binary)%4);doc['buffers']=[{'byteLength':len(binary)}]
    j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*(-len(j)%4)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary)

def section(parts,source,out):
    old,data=read_glb(source)
    doc={'asset':{'version':'2.0','generator':'Astraea source-authored tram section r002; unadopted'},'scene':0,'scenes':[{'nodes':[]}],
         'nodes':[],'meshes':[],'materials':copy.deepcopy(old['materials']),'images':[],'textures':copy.deepcopy(old.get('textures',[])),
         'samplers':copy.deepcopy(old.get('samplers',[])),'accessors':[],'bufferViews':[]}
    binary=bytearray();image_hashes=[]
    def view(data,target=None):
        binary.extend(b'\0'*(-len(binary)%4));v={'buffer':0,'byteOffset':len(binary),'byteLength':len(data)}
        if target:v['target']=target
        binary.extend(data);doc['bufferViews'].append(v);return len(doc['bufferViews'])-1
    for image in old.get('images',[]):
        v=old['bufferViews'][image['bufferView']];b=bytes(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
        new=copy.deepcopy(image);new['bufferView']=view(b);doc['images'].append(new);image_hashes.append(hashlib.sha256(b).hexdigest())
    mats={m['name']:i for i,m in enumerate(doc['materials'])}
    def accessor(a,kind,component,with_bounds=False,target=34962):
        a=np.ascontiguousarray(a,dtype='<f4'if component==5126 else'<u4');n=len(doc['accessors'])
        item={'bufferView':view(a.tobytes(),target),'componentType':component,'count':len(a),'type':kind}
        if with_bounds:item.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
        doc['accessors'].append(item);return n
    for part in parts:
        triangles=part_triangles(part);p=triangles.reshape(-1,3)
        n=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);norm=np.linalg.norm(n,axis=1)
        assert np.all(norm>1e-12),part['name'];n/=norm[:,None]
        uv=[]
        for tri,normal in zip(triangles,n):
            axes=[i for i in range(3)if i!=np.argmax(np.abs(normal))];uv.extend(tri[:,axes]*.25)
        primitive={'attributes':{'POSITION':accessor(p,'VEC3',5126,True),'NORMAL':accessor(np.repeat(n,3,axis=0),'VEC3',5126),'TEXCOORD_0':accessor(uv,'VEC2',5126)},
                   'indices':accessor(np.arange(len(p)),'SCALAR',5125,False,34963),'material':mats[part['material']]}
        mesh=len(doc['meshes']);doc['meshes'].append({'name':part['name'],'primitives':[primitive]})
        doc['scenes'][0]['nodes'].append(len(doc['nodes']));doc['nodes'].append({'name':part['name'],'mesh':mesh,'extras':{'source_role':part['purpose'],'collision_policy':part['collision_policy']}})
    write_glb(out,doc,binary);return image_hashes

def bridge(source,out,plan):
    doc,binary=read_glb(source);source_binary=bytes(binary);old=plan['retained_bridge_reach_m'];new=plan['bridge_reach_m'];hinge=.08;scale=(new-hinge)/(old-hinge)
    nodes={n['name']:i for i,n in enumerate(doc['nodes'])if'name'in n};moving=set()
    def visit(i):
        moving.add(i)
        for c in doc['nodes'][i].get('children',[]):visit(c)
    visit(nodes['BRIDGE_MOVING_PANEL']);changed=[];fixed=[]
    def array(ai):
        a=doc['accessors'][ai];v=doc['bufferViews'][a['bufferView']];n={'VEC3':3,'VEC4':4}[a['type']]
        assert a['componentType']==5126
        return np.ndarray((a['count'],n),dtype='<f4',buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',4*n),4))
    for i,node in enumerate(doc['nodes']):
        if 'mesh'not in node:continue
        if i not in moving or node['name'].startswith('BRIDGE_MovingKnuckle_'):
            fixed.append(node['name']);continue
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            assert 'TANGENT'not in primitive['attributes'],'Regenerate transformed tangents explicitly if source changes'
            index=primitive['attributes']['POSITION'];positions=array(index);before=positions.copy();x=before[:,0]
            if node['name']=='BRIDGE_CabinReceivingTongue_20mm':positions[:,0]=x+(new-old);scales=np.ones(len(x))
            else:
                scales=np.where((x>hinge)&(x<old),scale,1.)
                positions[:,0]=np.where(x<=hinge,x,np.where(x>=old,x+(new-old),hinge+(x-hinge)*scale))
            if'NORMAL'in primitive['attributes']:
                normals=array(primitive['attributes']['NORMAL']);normals[:,0]/=scales;normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-20)
            doc['accessors'][index]['min']=positions.min(axis=0).tolist();doc['accessors'][index]['max']=positions.max(axis=0).tolist()
        changed.append(node['name'])
    doc['nodes'][nodes['DATUM_VEHICLE_RECEIVING_EDGE']]['translation'][0]=new
    doc['asset']['generator']='Astraea exact fixed/hinge bridge successor r002; moving deck extension only'
    write_glb(out,doc,binary)
    before={o['name']:o for o in glb(source)};after={o['name']:o for o in glb(out)}
    for name in fixed:
        assert np.array_equal(before[name]['points'],after[name]['points']),name
        assert np.array_equal(before[name]['indices'],after[name]['indices']),name
    for name in after:
        assert np.array_equal(before[name]['points'][:,1:],after[name]['points'][:,1:]),name
        assert before[name]['material']==after[name]['material'],name
    name='BRIDGE_CabinReceivingTongue_20mm'
    assert np.max(np.abs(after[name]['points']-before[name]['points']-[new-old,0,0]))<2e-7
    return {'fixed_and_knuckle_meshes_identical':len(fixed),'changed_moving_meshes':changed,'tongue_translation_m':new-old,'all_yz_and_materials_identical':True,'knuckle_hinge_zone_m':hinge,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert args.candidate.resolve().parent==HERE and args.output.resolve().parent==HERE and not args.output.exists()
    plan=json.loads((args.candidate/'CANDIDATE.json').read_text());parts=json.loads((args.candidate/'MESHES.json').read_text());args.output.mkdir()
    source=ROOT/'Game/source_derivatives/group4_completion_20261011'
    images=section(parts,source/'AST-TRM-G4-014_central_source.glb',args.output/'AST-TRM-SECTION-20261023-r002.glb')
    proof=bridge(source/'AST-TRM-G4-019_boarding_bridge.glb',args.output/'AST-TRM-BRIDGE-20261023-r002.glb',plan['central'])
    proof.update(section_meshes=len(parts),retained_embedded_image_sha256=images,engine_import_executed=False,native_recipe_executed=False)
    proof['files']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in args.output.iterdir()}
    (args.output/'EXPORT_RECEIPT.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

if __name__=='__main__':main()
