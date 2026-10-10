"""One final readback of local accepted archives, original files and pinned closure."""
import pathlib,json,hashlib,zipfile,ast,datetime,sys
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R));from source_paths import section
PREFIX='Group2C_rebuild_root/'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while data:=f.read(1048576):h.update(data)
 return h.hexdigest()
def audit_archive(receipt,O,native,export,c,review):
 archive=R/receipt['archive_path'];assert archive.stat().st_size==receipt['archive_bytes'];assert sha(archive)==receipt['archive_sha256'];assert receipt['native_sha256']==sha(native)==c['native_sha256'];assert receipt['export_sha256']==sha(export)==c['export_sha256'];assert review['native_sha256']==c['native_sha256'] and review['export_sha256']==c['export_sha256']
 with zipfile.ZipFile(archive) as z:
  names=set(z.namelist());mp=PREFIX+(O/'MANIFEST.json').relative_to(R).as_posix();manifest=json.loads(z.read(mp));closure=manifest.get('pinned_dependency_closure',manifest.get('closure'));assert closure
  for dep in closure:
   data=z.read(PREFIX+dep['path']);assert len(data)==dep['bytes'] and hashlib.sha256(data).hexdigest()==dep['sha256'],(archive,dep['path'])
  for p in [native,export]:assert hashlib.sha256(z.read(PREFIX+p.relative_to(R).as_posix())).hexdigest()==sha(p)
  contract=json.loads(z.read(PREFIX+(O/'SECTION_CONTRACT.json').relative_to(R).as_posix()));assert contract['native_sha256']==c['native_sha256'] and contract['export_sha256']==c['export_sha256']
  for v in c['source_views']:
   p=O/v['file'];assert sha(p)==v['sha256'];assert hashlib.sha256(z.read(PREFIX+p.relative_to(R).as_posix())).hexdigest()==v['sha256'];assert next(q for q in review['views'] if q['name']==v['name'])['sha256']==v['sha256']
  missing=[];local={p.stem for p in R.glob('*.py')}
  for name in names:
   if not name.endswith('.py'):continue
   tree=ast.parse(z.read(name).decode('utf-8-sig'))
   for node in ast.walk(tree):
    modules=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
    for module in modules:
     if module in local and PREFIX+module+'.py' not in names:missing.append([name,module])
  assert not missing,('Missing executable local import closure',archive.name,missing)
 return {**receipt,'original_native_path':native.relative_to(R).as_posix(),'original_export_path':export.relative_to(R).as_posix(),'contract_path':(O/'SECTION_CONTRACT.json').relative_to(R).as_posix(),'manifest_path':(O/'MANIFEST.json').relative_to(R).as_posix(),'actual_pixel_review_path':(O/'PIXEL_REVIEW.json').relative_to(R).as_posix(),'archive_all_manifest_members_rehashed':True,'local_import_closure_checked':True}
status=json.loads((R/'GROUP2_STATUS.json').read_text());inventory=json.loads((R/'LUXURY_81_INVENTORY.json').read_text());units=[];facilities=[];superseded=[]
assert len(inventory['records'])==81
for u in status['verified_source_candidates']:
 row,O,native,export=section(u);c=json.loads((O/'SECTION_CONTRACT.json').read_text());n=json.loads((O/'NATIVE_VERIFICATION.json').read_text());g=json.loads((O/'EXPORT_VERIFICATION.json').read_text());review=json.loads((O/'PIXEL_REVIEW.json').read_text());assert n['status']==g['status']=='PASS';assert n['native_sha256']==g['native_sha256']==c['native_sha256'];assert g['export_sha256']==c['export_sha256'];assert review['actual_views_inspected']==6;assert c['identity']==row['identity'];assert len(n['rest_contacts'])==len(row['identity']['proposed_rest_slot_ids'])
 choices=sorted((R/'deliveries').glob(f'Group2C_D17_{u}_*_source_r*.json'));assert choices,u;receipt=json.loads(choices[-1].read_text());assert receipt['unit_source_index']==u
 superseded.extend(json.loads(p.read_text()) for p in choices[:-1]);entry=audit_archive(receipt,O,native,export,c,review);entry.update(tier=row['reservation']['tier'],identity=row['identity'],placement=c['reservation'],proposed_rest_anchors=len(n['rest_contacts']),installed_acceptance=False);units.append(entry);print('ARCHIVE_READBACK_PASS',u,flush=True)
for house in status.get('verified_private_house_adjuncts',[]):
 O=R/'facilities'/house;c=json.loads((O/'SECTION_CONTRACT.json').read_text());review=json.loads((O/'PIXEL_REVIEW.json').read_text());receipt=json.loads((R/'deliveries'/f'Group2C_{house}_private_adjunct_source_r001.json').read_text());assert all(json.loads((O/name).read_text())['status']=='PASS' for name in ['NATIVE_VERIFICATION.json','EXPORT_VERIFICATION.json','EDITABLE_TEXT_PARITY.json']);entry=audit_archive(receipt,O,O/'house_adjunct.blend',O/'house_adjunct.glb',c,review);entry.update(placement={'boundary':c['boundary'],'floor_y':102,'roof_limit_y':105.3});facilities.append(entry);print('ADJUNCT_ARCHIVE_READBACK_PASS',house,flush=True)
if '--final' in sys.argv:assert len(units)==80 and len(facilities)==6 and status['source_units_pending_acceptance']==[790]
supports=['GROUP2_STATUS.json','LUXURY_81_INVENTORY.json','GROUP2_GROUP7_BOUNDARY_SHEET.json','ALL81_FLOOR_PROPOSALS.json','PRIVATE_MULTILEVEL_FLOOR_ADDENDUM.json','EXCLUSIVE_FACILITIES_CROSSWALK.json','ROYALTY790_PROTECTED_ROOF_BLOCKER.json','PUBLICATION_BLOCK_20261010.json','SOURCE_README.md']
index={'schema':'astraea.group2C_final_local_source_handoff.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner':'Eve','Group2_status':'UNFINISHED','source_root':str(R),'reviewed_luxury_source_candidates':len(units),'reviewed_house_private_adjuncts':len(facilities),'proposed_rest_anchors':sum(x['proposed_rest_anchors'] for x in units),'pending_source_units':status['source_units_pending_acceptance'],'new_guest_units':0,'installed_acceptance':False,'master_sha256':'222e547eb695f51b11aa928ac30fb36e437866c3bccd8d857c81c5901a700008','pinned_checkpoint':'77a745750169a8ee853e71785f82fd2862bdaba5','current_inputs_checked':'9311ce52e625a5ef797770931a598dd78fb3c66e','placement':'World-coordinate zero-origin GLB Y-up; exact private reservation in each entry; Root-owned floors omitted from native/export','luxury_sources':units,'private_house_adjuncts':facilities,'superseded_archives_preserved':superseded,'supporting_files':[{'path':x,'bytes':(R/x).stat().st_size,'sha256':sha(R/x)} for x in supports],'last_independently_retained_commit':'7e3b22d9e517a9e83ebff30e7c7a22485ce7a1af','remote_retention':'Only existing independently verified receipts attest remote retention; newer local archives have not been uploaded since automatic approval review rejection.','Root_gates':['Protected790 successor roof/beam/slab opening','All receiver floors, support and external connections','Genuine enclosing frontage/privacy; no fabricated exterior windows','Existing controller and actor/rest/fluid/physical-cart adoption','Installed Godot import/normal-arrival/streaming/persistence/regression/final art acceptance'],'actual_model_effort':'Not independently exposed','verification':'Actual originals, final reviewed image hashes, native/export QA receipts, entire per-file ZIP dependency manifests and executable local Python import closure read back independently.'}
p=R/'DELIVERY_INDEX.json';p.write_text(json.dumps(index,indent=2));(R/'DELIVERY_INDEX_SHA256.json').write_text(json.dumps({'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)},indent=2));print('FINAL_INDEX',len(units),len(facilities),index['proposed_rest_anchors'],sha(p),flush=True)
