from pathlib import Path
import json,hashlib,zipfile,struct
C=Path(__file__).parent;S=C/'g3_fore_staging/Game';sha=lambda b:hashlib.sha256(b).hexdigest();p=json.loads((S/'data/architecture/group3_fore_starboard_clinical_20261011/FORE.json').read_text());assert json.loads((C/'G3_FORE_IMPORT_RECEIPT.json').read_text())['passed'];writes={};docs={}
for q in (S/'assets/models/group3_fore_starboard_clinical_20261011').iterdir():
 if q.is_file():writes[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'.godot/imported').iterdir():
 if q.is_file():writes[str(q.relative_to(S))]=q.read_bytes()
for f,h in p['model_pins'].items():
 b=writes['assets/models/group3_fore_starboard_clinical_20261011/'+f];assert sha(b)==h;n,_=struct.unpack_from('<II',b,12);docs[f]=json.loads(b[20:20+n])
omitted=[]
key='scripts/group3_fore_starboard_clinical_20261011/physical_package.gd';orig=(S/key).read_text();anchor=' var n:=Node3D.new();n.name="Group3ForeStarboardClinical";ship.get_node("ShipSpace").add_child(n)';assert orig.count(anchor)==1;code=orig.replace(anchor,' for file in p.model_pins:\n  assert(FileAccess.get_sha256("res://assets/models/group3_fore_starboard_clinical_20261011/"+file)==p.model_pins[file])\n'+anchor).replace('n.set_meta("clinical_operational_acceptance",false)','n.set_meta("clinical_operational_acceptance",false);n.set_meta("operating_lift_and_dispatch_admitted",false);n.set_meta("default_main_adoption",false)').replace('l.shadow_enabled=true;l.set_meta','l.visible=false;l.shadow_enabled=false;l.set_meta');writes[key]=code.encode();writes[key+'.uid']=(S/(key+'.uid')).read_bytes();writes['data/architecture/group3_fore_starboard_clinical_20261011/FORE.json']=(S/'data/architecture/group3_fore_starboard_clinical_20261011/FORE.json').read_bytes()
mappings=[]
for lamp in p['fixtures']:
 point=lamp['position'];found=[]
 for file,d in docs.items():
  for node in d['nodes']:
   if 'opal'not in node.get('name','').lower()or'mesh'not in node:continue
   assert not any(k in node for k in ['matrix','translation','rotation','scale'])
   for prim in d['meshes'][node['mesh']]['primitives']:
    a=d['accessors'][prim['attributes']['POSITION']]
    if all(lo-.025<=v<=hi+.025 for lo,v,hi in zip(a['min'],point,a['max'])):found.append({'model':file,'node':node['name']})
 assert len(found)==1,(lamp['name'],found);mappings.append({'fixture':lamp['name'],**found[0]})
with zipfile.ZipFile(C/'G3_FORE_CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in writes.items():z.writestr(k,b)
(C/'G3_FORE_LENS_MAPPING.json').write_text(json.dumps({'model_pins':p['model_pins'],'mappings':mappings},indent=2)+'\n');result={'status':'CANDIDATE_ONLY_RECEIVING_PENDING','source_revision':'6f2d0da67429ea940edf7011348ec08a346f37db','models':7,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')},'owner_script_sha256':sha(orig.encode()),'native_floor_m2':p['new_floor_m2'],'fixture_sources':26,'current_custodial_cart_relocated':False,'operating_lift_or_gate_identity_mapping_admitted':False,'source_defined_bounded_fore_derivatives_only':True};(C/'G3_FORE_CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n');print('candidate',len(writes),'paths',len(mappings),'lens mappings',len(omitted),'declared own-derivative omissions')
