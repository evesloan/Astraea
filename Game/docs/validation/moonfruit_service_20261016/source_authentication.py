import json,struct,hashlib,pathlib
R=pathlib.Path('/workspace/Astraea');D=R/'BlenderCatalogue/assets/moonfruit_service_20261016';source=R/'BlenderCatalogue/assets/windows_section_source_intake_20261007/packages/WP05';native=source/'source/WP05_moonfruit.blend';old=source/'exports/WP05_moonfruit.glb';installed=R/'Game/assets/models/SOL_D10_directory_09_remaining_batch.glb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def chunks(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
a,ab=chunks(old);b,bb=chunks(installed)
assert ab==bb
changes=[]
def compare(a,b,path=''):
 if type(a)!=type(b):changes.append(path);return
 if isinstance(a,dict):
  for k in set(a)|set(b):
   if k not in a or k not in b:changes.append(path+'/'+k)
   else:compare(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b)
  for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
 elif a!=b:changes.append(path)
compare(a,b)
assert set(changes)=={'/nodes/3583/extras/approach_revision','/nodes/3583/translation/0','/nodes/3583/translation/2'};assert a['nodes'][3583]['name']==b['nodes'][3583]['name']=='WP05_MARK_clean_handoff' and 'mesh' not in a['nodes'][3583]
manifest=json.load(open(source/'exports/manifest.json'));assert sha(native)==manifest['source_sha256'] and sha(old)==manifest['glb_sha256']
r=dict(status='PASS_RETAINED_NATIVE_EXPORT_AND_INSTALLED_BINARY_IDENTITY',native_sha256=sha(native),retained_export_sha256=sha(old),installed_sha256=sha(installed),binary_payload_sha256=hashlib.sha256(ab).hexdigest(),json_changes=changes,change_scope='One previously corrected nonmesh clean-handoff marker; entire binary geometry/material/image payload and all mesh node transforms identical',native_unchanged=True)
(D/'SOURCE_AUTHENTICATION.json').write_text(json.dumps(r,indent=2)+'\n');print('source authenticated; existing marker correction fields',len(changes))
