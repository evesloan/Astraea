"""Archive one actual reviewed luxury source section with its pinned rebuild closure."""
import pathlib,json,hashlib,zipfile,sys,datetime
R=pathlib.Path(__file__).resolve().parent;unit=int(sys.argv[1]);sys.path.insert(0,str(R));from source_paths import section;row,P,native_path,export_path=section(unit);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();c=json.loads((P/'SECTION_CONTRACT.json').read_text());native=native_path;export=export_path;n=json.loads((P/'NATIVE_VERIFICATION.json').read_text());g=json.loads((P/'EXPORT_VERIFICATION.json').read_text());review=json.loads((P/'PIXEL_REVIEW.json').read_text());assert n['status']==g['status']=='PASS';assert sha(native)==c['native_sha256']==n['native_sha256']==g['native_sha256']==review['native_sha256'];assert sha(export)==c['export_sha256']==g['export_sha256']==review['export_sha256'];assert review['actual_views_inspected']==6
for v in c['source_views']:assert sha(P/v['file'])==v['sha256']
helpers=['build_first_deluxe.py','place_deluxe_family.py','verify_first_native.py','verify_first_export.py','glb_tools.py','heavy.py','package_luxury.py','plan_luxury.py','INPUT_PIN_RECEIPT.json','CURRENT_INPUT_RECEIPT_9311.json','LUXURY_81_INVENTORY.json','ALL_81_NEIGHBOUR_SCREEN.json','PRECISE_RETAINED_TIDAL_INTERSECTIONS.json','GROUP2_GROUP7_BOUNDARY_SHEET.json','ALL81_FLOOR_PROPOSALS.json','SOURCE_README.md','reconcile_house_adjunct.py','premium_frame.py']
paths=[native,export,P/'SECTION_CONTRACT.json',P/'NATIVE_VERIFICATION.json',P/'EXPORT_VERIFICATION.json',P/'PIXEL_REVIEW.json',P/'SAVED_NATIVE_VERTICES.json.gz']+[P/v['file'] for v in c['source_views']]
paths.extend([R/'editable_label.py',R/'source_paths.py'])
for rel,expected in c.get('additional_source_files',{}).items():
 dependency=R/rel;assert sha(dependency)==expected;paths.append(dependency)
if c.get('geometry_rebuild_dependencies'):
 paths.append(R/'build_premium.py')
 for dep,expected in c['geometry_rebuild_dependencies'].items():
  assert sha(R/dep)==expected,'Rebuild source changed since final native/export';paths.append(R/dep)
if c.get('habitat_study'):paths.append(R/'build_deluxe_variant.py')
if c.get('review_view_rebuild'):paths.append(R/c['review_view_rebuild']['script'])
if c.get('habitat_study'):
 catalogue={x['catalogue_id']:x for x in json.loads((R/'inputs/BlenderCatalogue/catalogue_manifest.json').read_text())['assets']}
 for imp in c['imports']:
  if imp['catalogue_id'].startswith('AST-RST-'):
   paths.append(R/'inputs/BlenderCatalogue'/catalogue[imp['catalogue_id']]['manifest'])
for imp in c['imports']:
 if 'source_path' in imp:paths.append(R/'inputs'/imp['source_path'])
paths += [R/'inputs/BlenderCatalogue/catalogue_manifest.json',R/'inputs/Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb',R/'inputs/Game/docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx',R/'inputs/Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json',R/'inputs/Game/docs/master_source/MASTER_CURRENT_APPLICATION.json',R/'inputs/Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md',R/'inputs/Game/data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json',R/'inputs/Game/data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json',R/'inputs/Game/data/architecture/packages/upper_hull/HOUSE_CROWN_BOUNDARY_CONTRACT.json',R/'inputs/Game/data/design_contract.json',R/'inputs/BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']
paths += list((R/'inputs/master_embedded').glob('*'))
for directory in ['inputs/BlenderCatalogue/references/premium','inputs/BlenderCatalogue/references/residential_20261004']:
 paths+= [p for p in (R/directory).glob('*') if p.is_file()]
paths += [R/name for name in helpers]
if unit!=876:paths += [R/'sections/876_deluxe/876_deluxe.blend',R/'sections/876_deluxe/SECTION_CONTRACT.json',R/'sections/876_deluxe/PIXEL_REVIEW.json']
paths += [p for p in (R/'inputs_9311').rglob('*') if p.is_file() and p.suffix=='.json']
members={}
for p in paths:
 assert p.exists(),p
 members[p.relative_to(R).as_posix()]=p
closure=[{'path':k,'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in sorted(members.items())]
manifest={'schema':'astraea.group2_source_archive.v1','unit_source_index':unit,'identity':c['identity'],'status':'Verified editable luxury source candidate; Group2 checklist remains unfinished','native_sha256':sha(native),'export_sha256':sha(export),'native_bytes':native.stat().st_size,'export_bytes':export.stat().st_size,'placement':'Zero-origin GLB Y-up world coordinates in the exact exclusive reservation; no receiver floor','reservation':c['reservation'],'native_export_qa':'PASS: independently reopened native and parsed actual export','actual_eye_level_views':6,'source_geometry_only':True,'no_guest_units_added':True,'no_save_or_registry_migration':True,'remaining':c['remaining'],'pinned_dependency_closure':closure,'model_effort':'Actual model/effort not exposed for independent verification','failed_evidence_local':'sections/876_deluxe/failed_attempt_01..05 retained unchanged outside approved final archive'}
(P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2));members[(P/'MANIFEST.json').relative_to(R).as_posix()]=P/'MANIFEST.json';D=R/'deliveries';D.mkdir(exist_ok=True);revision=sys.argv[2] if len(sys.argv)>2 else 'r001';assert revision in ['r001','r002'];archive=D/f'Group2C_D17_{unit}_{row["reservation"]["tier"].title()}_source_{revision}.zip';assert not archive.exists(),'Published archives are immutable'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for k,p in sorted(members.items()):z.write(p,'Group2C_rebuild_root/'+k)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in closure:assert hashlib.sha256(z.read('Group2C_rebuild_root/'+row['path'])).hexdigest()==row['sha256']
assert archive.stat().st_size<100_000_000,'Per-file limit; preserve local archive if oversize'
summary={'unit_source_index':unit,'archive_path':archive.relative_to(R).as_posix(),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'native_sha256':sha(native),'export_sha256':sha(export),'source_qa_passed':True,'actual_reviewed_eye_level_views':6,'files':len(members),'scope':manifest['status'],'remaining_root_gates':c['remaining']};archive.with_suffix('.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
