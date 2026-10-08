from pathlib import Path
import json,struct,hashlib,copy
R=Path(__file__).resolve().parent;P=R/'incoming/WP12_night_table.glb';raw=P.read_bytes();assert hashlib.sha256(raw).hexdigest()=='6830a683917b7c1f98009dbf489f77673557250901f6913a562c4ec5022f1f47';n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);off=20+n;blen,bkind=struct.unpack_from('<II',raw,off);assert bkind==0x004e4942;b=raw[off+8:off+8+blen];nd=copy.deepcopy(d);mapping=[]
for i,node in enumerate(nd['nodes']):
 old=node.get('name');safe=f'WP12N_{i:05d}';assert 'source_node_index'not in node.get('extras',{}) and 'source_name'not in node.get('extras',{});node['name']=safe;node.setdefault('extras',{}).update({'source_name':old or '', 'source_node_index':i});mapping.append({'source_index':i,'source_name':old,'runtime_name':safe,'mesh_index':node.get('mesh'),'light_index':node.get('extensions',{}).get('KHR_lights_punctual',{}).get('light')})
restored=copy.deepcopy(nd)
for i,node in enumerate(restored['nodes']):
 if 'name'in d['nodes'][i]:node['name']=d['nodes'][i]['name']
 else:node.pop('name')
 node['extras'].pop('source_name');node['extras'].pop('source_node_index')
 if 'extras'not in d['nodes'][i]:assert not node['extras'];node.pop('extras')
assert restored==d
O=R/'runtime_candidate/assets/models';O.mkdir(parents=True,exist_ok=True);out=O/'WP12_night_table_runtime_names001.glb';assert not out.exists();j=json.dumps(nd,separators=(',',':'),ensure_ascii=True).encode();j+=b' '*((-len(j))%4);encoded=struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),bkind)+b;out.write_bytes(encoded)
Q=R/'runtime_candidate/data/architecture/night_table';Q.mkdir(parents=True,exist_ok=True);(Q/'NODE_NAME_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n');(Q/'BINARY_PRESERVATION.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'runtime_sha256':hashlib.sha256(encoded).hexdigest(),'binary_chunk_sha256':hashlib.sha256(b).hexdigest(),'source_json_restored_exactly':restored==d,'node_count':len(d['nodes']),'mesh_count':len(d['meshes']),'light_count':len(d['extensions']['KHR_lights_punctual']['lights']),'placement_world_xyz':[-31,61,216],'scope':'Only unique runtime node names and provenance extras; all transforms, mesh/resources/materials/light declarations and BIN bytes unchanged. Runtime lighting adjustment is separate.'},indent=2)+'\n');print('Prepared source-exact node-name derivative',len(mapping))
