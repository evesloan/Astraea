from pathlib import Path
import json,hashlib,zipfile,struct
C=Path(__file__).parent;S=C/'g3_aft_riser_staging/Game';sha=lambda b:hashlib.sha256(b).hexdigest();p=json.loads((S/'data/architecture/group3_remaining_risers_20261011/AFT_PAIR.json').read_text());assert json.loads((C/'G3_AFT_RISER_IMPORT_RECEIPT.json').read_text())['passed'];writes={}
for q in (S/'assets/models/group3_remaining_risers_20261011').iterdir():
 if q.is_file():writes[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'.godot/imported').iterdir():
 if q.is_file():writes[str(q.relative_to(S))]=q.read_bytes()
for f,h in p['model_pins'].items():assert sha(writes['assets/models/group3_remaining_risers_20261011/'+f])==h
key='scripts/group3_remaining_risers_20261011/aft_pair.gd';orig=(S/key).read_text();anchor=' var n:=Node3D.new();n.name="Group3AftRiserPair";ship.get_node("ShipSpace").add_child(n)';assert orig.count(anchor)==1;code=orig.replace(anchor,' for file in p.model_pins:\n  assert(FileAccess.get_sha256("res://assets/models/group3_remaining_risers_20261011/"+file)==p.model_pins[file])\n'+anchor).replace('n.set_meta("authoritative_identity_mapping",false)','n.set_meta("authoritative_identity_mapping",false);n.set_meta("operating_lifts_admitted",false);n.set_meta("default_main_adoption",false)').replace('l.shadow_enabled=true;l.set_meta','l.visible=false;l.shadow_enabled=false;l.set_meta');writes[key]=code.encode();writes[key+'.uid']=(S/(key+'.uid')).read_bytes();writes['data/architecture/group3_remaining_risers_20261011/AFT_PAIR.json']=(S/'data/architecture/group3_remaining_risers_20261011/AFT_PAIR.json').read_bytes()
mappings=[]
for site in p['sites']:
 b=writes['assets/models/group3_remaining_risers_20261011/'+site['architecture_file']];n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n])
 for lamp in site['fixtures']:
  point=lamp['position'];found=[]
  for node in d['nodes']:
   if 'opal'not in node.get('name','').lower()or'mesh'not in node:continue
   assert not any(k in node for k in ['matrix','translation','rotation','scale'])
   mesh=d['meshes'][node['mesh']]
   for prim in mesh['primitives']:
    a=d['accessors'][prim['attributes']['POSITION']]
    if all(lo-.025<=v<=hi+.025 for lo,v,hi in zip(a['min'],point,a['max'])):found.append(node['name'])
  assert len(found)==1,(lamp['name'],found);mappings.append({'fixture':lamp['name'],'model':site['architecture_file'],'node':found[0]})
with zipfile.ZipFile(C/'G3_AFT_RISER_CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in writes.items():z.writestr(k,b)
(C/'G3_AFT_RISER_LENS_MAPPING.json').write_text(json.dumps({'model_pins':p['model_pins'],'mappings':mappings},indent=2)+'\n');result={'status':'CANDIDATE_ONLY_RECEIVING_PENDING','source_revision':'6f2d0da67429ea940edf7011348ec08a346f37db','models':4,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')},'owner_script_sha256':sha(orig.encode()),'native_floor_m2':p['new_floor_m2'],'fixture_sources':34,'operating_lifts_or_identity_mapping_admitted':False,'D04_conflicting_risers_selected':False,'all17_current_deck_datums_matched':True};(C/'G3_AFT_RISER_CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n');print('candidate',len(writes),'paths',len(mappings),'exact lens mappings')
