#!/usr/bin/env python3
"""Generate fail-closed, two-prototype admission receipts from verified source bytes.
No engine launch/import. Limits estimate owned input data, not allocator/GPU/RID use.
"""
from pathlib import Path
import argparse, hashlib, json, struct
sha=lambda b:hashlib.sha256(b).hexdigest()

def estimate(path, root, expected):
    data=path.read_bytes()
    assert sha(data)==expected, f'raw source mismatch: {path}'
    magic,version,length=struct.unpack_from('<III',data)
    assert magic==0x46546C67 and version==2 and length==len(data)
    chunks={}; offset=12
    while offset<len(data):
        n,kind=struct.unpack_from('<II',data,offset); chunks[kind]=data[offset+8:offset+8+n];offset+=8+n
    gltf=json.loads(chunks[0x4E4F534A]); binary=chunks[0x004E4942]
    assert not gltf.get('skins') and not gltf.get('animations')
    meshes=0;faces=0
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        meshes+=1
        for prim in gltf['meshes'][node['mesh']]['primitives']:
            assert prim.get('mode',4)==4
            faces+=gltf['accessors'][prim.get('indices',prim['attributes']['POSITION'])]['count']
    dependencies={f'res://assets/models/{path.name}':expected}
    import_path=root/'retained/Game/assets/models'/f'{path.name}.import'
    dependencies[f'res://assets/models/{path.name}.import']=sha(import_path.read_bytes())
    decoded=0
    # Embedded PNG source bytes also identify the retained external importer output.
    for image in gltf.get('images',[]):
        assert image.get('mimeType')=='image/png' and 'bufferView' in image
        view=gltf['bufferViews'][image['bufferView']]; start=view.get('byteOffset',0)
        png=binary[start:start+view['byteLength']]
        assert png[:8]==b'\x89PNG\r\n\x1a\n'
        width,height=struct.unpack_from('>II',png,16);decoded+=width*height*4
        texture=root/'retained/Game/assets/models'/f'{path.stem}_{image["name"]}.png'
        # Imported external PNG encoding can differ. Verify recorded file independently;
        # dimensions come from the exact source image and the runtime receipt pins both.
        content=texture.read_bytes();assert content[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack_from('>II',content,16)==(width,height)
        dependencies['res://assets/models/'+texture.name]=sha(content)
    # Pin the retained imported scene, texture resources and import remaps too.
    for row in json.loads((root/'acquisition/FOCUSED_IMPORTED_MAP.json').read_text()):
        if Path(row['target']).name.startswith(path.stem):
            content=Path(row['source']).read_bytes();assert sha(content)==row['sha256']
            dependencies['res://'+row['target'][5:]]=row['sha256']
    nodes=len(gltf['nodes'])+1+meshes*3
    resources=len(gltf.get('meshes',[]))+len(gltf.get('materials',[]))+len(gltf.get('textures',[]))
    return {'nodes':nodes,'meshes':meshes,'face_vertices':faces,'resources':resources*2+meshes*3+16,
            'estimated_bytes':len(data)*4+faces*384+nodes*4096+decoded*4,
            'dependencies':dependencies,'source_nodes':len(gltf['nodes']),'decoded_texture_bytes':decoded,
            'estimate_note':'Conservative data allowance; not a hard native/GPU allocation cap. First draw not precompiled.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent);args=parser.parse_args();root=args.root.resolve()
    rows=json.loads((root/'acquisition/FOCUSED_SOURCE_MAP.json').read_text())
    tidal=next(r for r in rows if r['target']=='Game/assets/models/TIDAL_ROOM_01_r001.glb')
    private=json.loads((root/'retained/Game/data/architecture/startup_residency_20261020/private_shells.json').read_text())['rooms']['StarAtlasSpecialty_103.glb']
    sources={}
    for path,expected in [(Path(tidal['source']),tidal['sha256']),(root/'acquisition/pck-fixture/Game/assets/models/StarAtlasSpecialty_103.glb',private['sha256'])]:
        sources['res://assets/models/'+path.name]=estimate(path,root,expected)
    output=Path(__file__).resolve().parent/'payload/Game/scripts/route_activation_20261023/prewarm_estimates.json'
    output.write_text(json.dumps({'schema':1,'sources':sources},indent=2)+'\n')
    print(json.dumps({key:{k:v for k,v in value.items() if k!='dependencies'} for key,value in sources.items()},indent=2))
if __name__=='__main__':main()
