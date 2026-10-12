"""Independent importer witnesses: source-factor JSON patch, literal BIN retained."""
from pathlib import Path
import struct,json,hashlib
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
definition=json.loads((ROOT/'Game/data/architecture/group5/LARGE_VENUE_MATERIAL_FACTORS.json').read_text())
out=Path('/tmp/group5-native-factor-importer-references');out.mkdir(exist_ok=True)
rows=[]
for row in definition['venues']:
    source=ROOT/'Game'/row['model_path'][6:];raw=source.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['model_sha256']
    old_n=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+old_n]);tail=raw[20+old_n:]
    selected={r['material_name']:r for r in row['materials']}
    changed=[]
    for material in gltf['materials']:
        if material['name'] not in selected:continue
        m=selected[material['name']]
        assert material['pbrMetallicRoughness'].get('baseColorFactor',[1,1,1,1])==m['original_export_factor']
        material['pbrMetallicRoughness']['baseColorFactor']=m['factor_linear_rgba'];changed.append(material['name'])
    assert len(changed)==len(selected)
    encoded=json.dumps(gltf,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
    new=struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(tail))+struct.pack('<II',len(encoded),0x4E4F534A)+encoded+tail
    target=out/(row['programme_key']+'.glb');target.write_bytes(new)
    assert new[20+len(encoded):]==tail
    rows.append({'programme_key':row['programme_key'],'path':str(target),'sha256':hashlib.sha256(new).hexdigest(),
                 'original_bin_chunk_sha256':hashlib.sha256(tail).hexdigest(),'bin_and_textures_unchanged':True,'changed_material_factors':changed})
(P/'qa/MATERIAL_IMPORTER_REFERENCE_FIXTURES.json').write_text(json.dumps({'status':'PASS_REFERENCE_BYTES',
    'rows':rows,'scope':'Independent ephemeral glTF importer witnesses with exact native linear baseColorFactor values. Original JSON other fields and complete BIN/images remain unchanged;not production export/model replacements.'},indent=2)+'\n')
print('GROUP5_MATERIAL_IMPORTER_REFERENCES_PASS',len(rows))
