"""Accept an actually inspected adjunct and create one local immutable archive."""
import pathlib,json,sys,hashlib,zipfile
R=pathlib.Path(__file__).resolve().parent;house=sys.argv[1];assert '--actual-pixels-inspected' in sys.argv
O=R/'facilities'/house;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((O/'SECTION_CONTRACT.json').read_text());n=json.loads((O/'NATIVE_VERIFICATION.json').read_text());g=json.loads((O/'EXPORT_VERIFICATION.json').read_text());t=json.loads((O/'EDITABLE_TEXT_PARITY.json').read_text())
assert n['status']==g['status']==t['status']=='PASS'
native=O/'house_adjunct.blend';export=O/'house_adjunct.glb';assert sha(native)==c['native_sha256']==n['native_sha256']==g['native_sha256']==t['native_sha256'];assert sha(export)==c['export_sha256']==g['export_sha256']==t['export_sha256'];assert len(c['source_views'])==4
recipe=c.get('rebuild_recipe','build_house_adjunct.py');assert sha(R/recipe)==c['rebuild_source_sha256'];assert sha(R/'build_first_deluxe.py')==c['seed_sha256']
observations={'arrival':'Broad arrival/service spine opens to the sheltered fitted quiet gallery; local receiver surface shown only as Root proposal.','quiet_gallery':'Fitted bench, retained side table, reading stock and fan-shaped supported cover form the house-private resting bay.','care_threshold':'Closed clean/used-return cabinet, adjacent work surface and cool supported task light face their dry service approach.','privacy_return':'Open slatted privacy returns preserve a clear guest/care spine; Root external house links and court lighting held.'}
views=[]
for v in c['source_views']:
 assert sha(O/v['file'])==v['sha256'];views.append({**v,'actual_pixels_inspected':True,'observation':observations[v['name']]})
review={'status':'ACTUAL_FOUR_EYE_LEVEL_VIEWS_REVIEWED_SOURCE_ONLY','native_sha256':sha(native),'export_sha256':sha(export),'views':views,'installed_acceptance':False};(O/'PIXEL_REVIEW.json').write_text(json.dumps(review,indent=2));c['status']='BOUNDED_FIT_AND_ACTUAL_PIXELS_VERIFIED_PRIVATE_ADJUNCT';c['actual_pixel_review']=True;(O/'SECTION_CONTRACT.json').write_text(json.dumps(c,indent=2))
helpers=['build_house_adjunct.py','build_first_deluxe.py','verify_house_text.py','glb_tools.py','source_paths.py','editable_label.py','heavy.py','package_house_adjunct.py','EXCLUSIVE_FACILITIES_CROSSWALK.json','EXCLUSIVE_FACILITIES_PRECISE_LINE_SCREEN.json','reconcile_house_adjunct.py','LUXURY_81_INVENTORY.json','INPUT_PIN_RECEIPT.json','CURRENT_INPUT_RECEIPT_9311.json','GROUP2_GROUP7_BOUNDARY_SHEET.json','SOURCE_README.md']
helpers.append(recipe)
paths=[p for p in O.iterdir() if p.is_file() and p.name!='MANIFEST.json']+[R/x for x in helpers]
for dep,expected in c.get('additional_source_files',{}).items():assert sha(R/dep)==expected;paths.append(R/dep)
for imp in c['imports']:
 if 'source_path' in imp:
  p=R/'inputs'/imp['source_path'];assert sha(p)==imp['source_sha256'];paths.append(p)
paths+=[R/'inputs/BlenderCatalogue/catalogue_manifest.json',R/'inputs/Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb',R/'inputs/Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx',R/'inputs/Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json',R/'inputs/Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',R/'inputs/Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',R/'inputs/Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md',R/'inputs/Game/data/design_contract.json',R/'inputs/BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']
paths+=list((R/'inputs/master_embedded').glob('*'))+[p for p in (R/'inputs_9311').rglob('*.json') if p.is_file()]
for folder in ['inputs/BlenderCatalogue/references/premium','inputs/BlenderCatalogue/references/residential_20261004']:paths+=[p for p in (R/folder).glob('*') if p.is_file()]
members={p.relative_to(R).as_posix():p for p in paths};closure=[{'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)} for rel,p in sorted(members.items())]
manifest={'schema':'astraea.private_house_adjunct_source.v1','house':house,'status':c['status'],'source_boundary':c['boundary'],'floor_y':102,'roof_limit_y':105.3,'native_sha256':sha(native),'export_sha256':sha(export),'actual_reviewed_eye_level_views':4,'new_guest_units':0,'new_canonical_programme_keys':0,'Root_adoption_held':c['Root_adoption_held'],'placement':'World-coordinate zero-origin Y-up GLB; root receiver floor omitted from final native/export','closure':closure,'actual_model_effort':'Not exposed for independent verification'}
mp=O/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2));members[mp.relative_to(R).as_posix()]=mp
D=R/'deliveries';D.mkdir(exist_ok=True);archive=D/f'Group2C_{house}_private_adjunct_source_r001.zip';assert not archive.exists(),'Preserve immutable local archives'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for rel,p in sorted(members.items()):z.write(p,'Group2C_rebuild_root/'+rel)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for item in closure:assert hashlib.sha256(z.read('Group2C_rebuild_root/'+item['path'])).hexdigest()==item['sha256']
assert archive.stat().st_size<100_000_000
receipt={'house':house,'archive_path':archive.relative_to(R).as_posix(),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'native_sha256':sha(native),'export_sha256':sha(export),'actual_reviewed_eye_level_views':4,'scope':c['status'],'installed_acceptance':False};archive.with_suffix('.json').write_text(json.dumps(receipt,indent=2))
def atomic(p,data):
 temp=p.with_suffix(p.suffix+'.pending');temp.write_text(json.dumps(data,indent=2));temp.replace(p)
p=R/'EXCLUSIVE_FACILITIES_CROSSWALK.json';cross=json.loads(p.read_text());row=next(x for x in cross['source_proposals'] if x['house']==house);row['current_source_status']=c['status'];row['delivery']=receipt;atomic(p,cross)
p=R/'GROUP2_STATUS.json';status=json.loads(p.read_text());status.setdefault('verified_private_house_adjuncts',[]);status['verified_private_house_adjuncts']=sorted(set(status['verified_private_house_adjuncts']+[house]));status['required_private_house_adjuncts']=6;status['Group2_status']='UNFINISHED';atomic(p,status)
p=R/'GROUP2_GROUP7_BOUNDARY_SHEET.json';boundary=json.loads(p.read_text());boundary.setdefault('private_house_adjunct_sources',[]);boundary['private_house_adjunct_sources']=[x for x in boundary['private_house_adjunct_sources'] if x['house']!=house]+[{'house':house,'boundary':c['boundary'],'source_roof_limit_y':105.3,'native_sha256':sha(native),'export_sha256':sha(export),'receiver_and_connections':'Root adoption held','external_openings':False}];atomic(p,boundary)
print(json.dumps(receipt,indent=2))
