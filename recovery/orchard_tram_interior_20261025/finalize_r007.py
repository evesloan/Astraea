"""Exact runtime graft; preserved predecessor and arrays, coherent native mount correction."""
from pathlib import Path
import copy,json,struct,hashlib
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r007'
def read(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);return d,b[28+n:28+n+d['buffers'][0]['byteLength']]
base=R/'Game/orchard_tram_interior_20261025/r006/OrchardInteriorReceiving.glb';d,binary=read(base);original=copy.deepcopy(d)
def append(p):
 global binary
 s,sb=read(p);offset=(len(binary)+3)//4*4;binary+=b'\0'*(offset-len(binary))+sb
 keys=['bufferViews','accessors','images','samplers','textures','materials','meshes'];off={k:len(d.get(k,[])) for k in keys}
 for v in s.get('bufferViews',[]):v['byteOffset']=v.get('byteOffset',0)+offset
 for a in s.get('accessors',[]):assert 'sparse' not in a;a['bufferView']+=off['bufferViews']
 for im in s.get('images',[]):im['bufferView']+=off['bufferViews']
 for t in s.get('textures',[]):
  t['source']+=off['images']
  if 'sampler' in t:t['sampler']+=off['samplers']
 def tex(v):
  if isinstance(v,dict):
   for k,x in v.items():
    if k.endswith('Texture') and isinstance(x,dict) and 'index' in x:x['index']+=off['textures']
    tex(x)
  elif isinstance(v,list):
   for x in v:tex(x)
 for m in s.get('materials',[]):tex(m)
 for m in s['meshes']:
  for p in m['primitives']:
   p['attributes']={k:v+off['accessors'] for k,v in p['attributes'].items()}
   if 'indices' in p:p['indices']+=off['accessors']
   if 'material' in p:p['material']+=off['materials']
 for k in keys:d.setdefault(k,[]).extend(s.get(k,[]))
 nodes={}
 for n in s['nodes']:
  if 'mesh' not in n:continue
  assert not n.get('children');n['mesh']+=off['meshes'];nodes[n['name']]=n
 return nodes
new=append(D/'OrchardReceiving_native_export.glb');receipt=json.loads((D/'BUILD.json').read_text())
for i,n in enumerate(d['nodes']):
 if n['name'] in receipt['changed_supports']:d['nodes'][i]=new[n['name']]
for name in receipt['new_posts']:d['scenes'][0]['nodes'].append(len(d['nodes']));d['nodes'].append(new[name])
fixtures=append(R/'Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-020_foremid_north_candidate.glb')
for lamp in receipt['fixtures']:
 lamp['source_delta_xyz'][0]+=.2;lamp['xyz'][0]+=.2
 for name in [lamp['name'],lamp['backplate']]:
  n=fixtures[name];assert not n.get('matrix');n['translation']=lamp['source_delta_xyz'];d['scenes'][0]['nodes'].append(len(d['nodes']));d['nodes'].append(n)
  if name==lamp['name']:
   # Only the retained physical opal lens emits; no global material replacement.
   for prim in d['meshes'][n['mesh']]['primitives']:
    mat=copy.deepcopy(d['materials'][prim['material']]);mat['name']+='_OrchardPoweredLens';mat['emissiveFactor']=[1,.89,.72]
    prim['material']=len(d['materials']);d['materials'].append(mat)
unchanged=[n['name'] for n,old in zip(d['nodes'],original['nodes']) if n==old]
assert len(unchanged)==269
d['buffers']=[{'byteLength':len(binary)}];js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\0'*((-len(binary))%4)
out=D/'OrchardReceiving_exact.glb';assert not out.exists();out.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary)
receipt['runtime_exact_members']=unchanged;receipt['mount_correction']='Fixture backplates seat on east face of pier-continuous posts; R007 first native preserved, final native shifts fittings +0.20m X.'
receipt['runtime_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();receipt['runtime_bytes']=out.stat().st_size
(D/'FINAL.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'unchanged_runtime_members':len(unchanged),'new_total':len(d['nodes']),'runtime_sha256':receipt['runtime_sha256']}))
