"""Keep untouched source GLB primitives byte-exact in a separate successor.

Blender's edited native source remains editable. Only changed members use its
export; untouched members retain the original arrays/material/image bytes.
"""
from pathlib import Path
import json,struct,copy,hashlib
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r002'
def read(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);return d,b[28+n:28+n+d['buffers'][0]['byteLength']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((D/'BUILD.json').read_text());receipts=[]
for owner,file in [('Orchard','AST-RTL-009.glb'),('Retail','AST-RTL-007.glb')]:
 source=R/'Game/assets/models'/file;export=D/(owner+'_receiving_successor.glb');s,sb=read(source);d,db=read(export)
 assert not s.get('extensionsUsed') and not s.get('skins') and not s.get('animations')
 assert all(not n.get('children') for n in s['nodes']+d['nodes'])
 base=(len(db)+3)//4*4;binary=db+b'\0'*(base-len(db))+sb
 keys=['bufferViews','accessors','images','samplers','textures','materials','meshes'];off={k:len(d.get(k,[])) for k in keys}
 src=copy.deepcopy(s)
 for v in src.get('bufferViews',[]):assert v.get('buffer',0)==0;v['byteOffset']=v.get('byteOffset',0)+base
 for a in src.get('accessors',[]):assert 'sparse' not in a;a['bufferView']+=off['bufferViews']
 for im in src.get('images',[]):assert 'uri' not in im;im['bufferView']+=off['bufferViews']
 for t in src.get('textures',[]):
  t['source']+=off['images']
  if 'sampler' in t:t['sampler']+=off['samplers']
 def textures(v):
  if isinstance(v,dict):
   for k,x in v.items():
    if k.endswith('Texture') and isinstance(x,dict) and 'index' in x:x['index']+=off['textures']
    textures(x)
  elif isinstance(v,list):
   for x in v:textures(x)
 for m in src.get('materials',[]):textures(m)
 for m in src['meshes']:
  for p in m['primitives']:
   assert not p.get('targets') and not p.get('extensions')
   p['attributes']={k:v+off['accessors'] for k,v in p['attributes'].items()}
   if 'indices' in p:p['indices']+=off['accessors']
   if 'material' in p:p['material']+=off['materials']
 for k in keys:d.setdefault(k,[]).extend(src.get(k,[]))
 original={n['name']:n for n in s['nodes']};keep={k.split('/',1)[1] for k in build['unchanged_native_members'] if k.startswith(owner+'/')};count=0
 for i,n in enumerate(d['nodes']):
  if n.get('name') in keep:
   replacement=copy.deepcopy(original[n['name']]);replacement['mesh']+=off['meshes'];d['nodes'][i]=replacement;count+=1
 assert count==len(keep)
 d['buffers']=[{'byteLength':len(binary)}]
 js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\0'*((-len(binary))%4)
 payload=struct.pack('<4sII',b'glTF',2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
 out=D/(owner+'_receiving_exact.glb');assert not out.exists();out.write_bytes(payload)
 receipts.append({'owner':owner,'preserved_members':count,'source_sha256':sha(source),'edited_export_sha256':sha(export),'output':out.name,'sha256':sha(out),'bytes':out.stat().st_size})
out=D/'EXACT_EXPORT_RECEIPT.json';assert not out.exists();out.write_text(json.dumps({'selected':False,'method':'Original untouched primitive arrays, materials, image bytes and node transforms retained; changed members use native successor export.','files':receipts},indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipts))
