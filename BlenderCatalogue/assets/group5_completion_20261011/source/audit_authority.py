"""Current identity, large-venue and literal physical-light source review."""
from pathlib import Path
import json,hashlib,numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def read(path):return json.loads((ROOT/path).read_text())
def write(name,d):(P/'qa'/name).write_text(json.dumps(d,indent=2)+'\n')
original=read('BlenderCatalogue/assets/shopping_promenade_20261009/docs/PLACEMENT_AND_CONNECTORS.json')
current=read('Game/data/architecture/SHOPPING_PROMENADE.json')
authority_files=['DesignArchive/Planning/v2/inputs/historical_baseline.json','DesignArchive/Planning/v3/inputs/historical_baseline.json','DesignArchive/Planning/Supporting_Analyses/d09-retail-handoff/D09_exact_coverage_rows.json','DesignArchive/Planning/Supporting_Analyses/d09-retail-handoff/D09_atlas_vector_evidence.json']
identity={'status':'HOLD','verified_new_joins':15,'preserved_R070_join':1,'unresolved_joins':84,'source_files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in authority_files},'finding':'Historical registry/crosswalk retains all 100 R names and capacities but no full address-to-position joins; labelled inset proves only R064-R071 and R089-R096. Four-bank fore-to-aft proposal cannot recover missing original identities. All 84 nulls preserved.','physical_door_ids':'Immutable existing footprint key + public/workbay/stock threshold suffix; never proposed room address. Save migration remains unimplemented.'}
assert sum(r.get('stable_room_id') is None for r in current['chunks'] if 'front_sign_x' in r)==84
write('IDENTITY_AUTHORITY.json',identity)
sections=read('Game/data/architecture/received_sections.json')['sections']
rows=[]
for r in sections:
    if r['programme_key'].startswith('D09'):
        path='Game/assets/models/'+r['model_file'];native=r['editable_source']
        rows.append({'programme_key':r['programme_key'],'name':r['name'],'current_runtime':path,'current_runtime_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'native_metadata_path':native,'native_metadata_path_exists':(ROOT/native).is_file(),'native_sha256':hashlib.sha256((ROOT/native).read_bytes()).hexdigest() if (ROOT/native).is_file() else None,'preserved':True,'full_fitout_and_operational_acceptance':False,'source_meshes':r['source_mesh_count'],'scope':'current received source registration; missing metadata native references are unresolved, with no substitute or change'})
for key,name,script,model in [('D09_directory_01','Orchard Market','grand_pool_section.gd',''),('D09_directory_04','Thread & Shell','thread_shell.gd','AST-RTL-007.glb'),('D09_directory_06','Conversation Salon','ship.gd','AST-SAL-007.glb'),('D09_directory_08','Living Gifts','living_gifts.gd','AST-RTL-006.glb')]:
    row={'programme_key':key,'name':name,'owner':'Game/scripts/'+script,'owner_sha256':hashlib.sha256((ROOT/'Game/scripts'/script).read_bytes()).hexdigest(),'preserved':True,'full_fitout_and_operational_acceptance':False}
    if model:row.update(current_runtime='Game/assets/models/'+model,current_runtime_sha256=hashlib.sha256((ROOT/'Game/assets/models'/model).read_bytes()).hexdigest())
    else:row['source_manifest']='Game/data/architecture/GRAND_POOL_SECTION_RUNTIME.json'
    rows.append(row)
assert len(rows)==10 and len({r['programme_key'] for r in rows})==10
recovery_path=P/'qa/VENUE_SOURCE_RECOVERY.json'
if recovery_path.exists():
    recovered={r['programme_key']:r for r in json.loads(recovery_path.read_text())['rows']}
    for row in rows:
        if row['programme_key'] not in recovered:continue
        r=recovered[row['programme_key']]
        row.update(recovered_native='BlenderCatalogue/assets/group5_completion_20261011/'+r['native']['recovered_path'],recovered_native_sha256=r['native']['sha256'],recovered_archive_sha256=r['archive_sha256'],recovered_export_matches_current_runtime=r['archived_export_matches_current_runtime'],source_provenance='exact matching archived source/export recovered' if r['archived_export_matches_current_runtime'] else 'archived original recovered;later current entry-correction source still held')
        row['scope']='Current source/export provenance audited;original metadata left unchanged;no venue fit-out or operational acceptance.'
counterpart_path=P/'docs/CURRENT_MAKER_COUNTERPART.json'
if counterpart_path.exists():
    counterpart=json.loads(counterpart_path.read_text())
    row=next(r for r in rows if r['programme_key']==counterpart['programme_key'])
    assert row['current_runtime_sha256']==counterpart['current_runtime_sha256']
    row.update(explicit_current_editable_counterpart='BlenderCatalogue/assets/group5_completion_20261011/'+counterpart['native'],counterpart_native_sha256=counterpart['native_sha256'],counterpart_geometry_error_m=counterpart['geometry_max_bidirectional_vertex_error_m'],counterpart_role='explicit derived current geometry/material source;original correction-native and procedural/font authoring held')
lighting_path=ROOT/'Game/data/architecture/group5/LARGE_VENUE_LIGHTING.json'
if lighting_path.exists():
    lighting={r['programme_key']:r for r in json.loads(lighting_path.read_text())['venues']}
    for row in rows:
        if row['programme_key'] not in lighting:continue
        r=lighting[row['programme_key']]
        row.update(first_pass_light_sources=len(r['fixtures']),lighting_contract='Game/data/architecture/group5/LARGE_VENUE_LIGHTING.json',pixel_lighting_and_hardware_accepted=False)
        if r.get('fixture_clearance'):row['selected_fixture_derivative']=r['fixture_clearance']
write('TEN_LARGE_VENUES.json',{'status':'preserved_current_construction_WIP','venues':sorted(rows,key=lambda r:r['programme_key']),'count':10,'distinct_from_small_shops':True,'cross_group_interfaces':{'Orchard_Market':'Group6 Grand Pool/Orchard shared source and hull interfaces; do not duplicate or overwrite','Orchard_Food_Hall':'Group8 D10_directory_04, existing orchard_exchange_lift_001 and switchback; preserve D09_directory_04 link','shared_staff_risers':'Group3 and integration owner; four existing district circuits have no completed shared-riser adoption'},'final_art_or_gameplay_accepted':False})
geometry=read('BlenderCatalogue/assets/shopping_promenade_20261009/qa/source_geometry.json')
lights=read('BlenderCatalogue/assets/shopping_promenade_20261009/docs/LIGHT_SOURCES.json');proof=[]
for row in lights:
    point=np.array(row['local_xyz']);candidates=[]
    for layer in ['shell','fitout']:
        for part in geometry.get(row['chunk_id']+'__'+layer,[]):
            if part['material']!='fixture_lens':continue
            verts=np.array(part['vertices_xyz']);lo=verts.min(axis=0);hi=verts.max(axis=0)
            dist=float(np.linalg.norm(point-np.minimum(hi,np.maximum(lo,point))))
            candidates.append((dist,part['part']))
    best=min(candidates) if candidates else (float('inf'),'missing')
    # These deliberate downward source offsets put the emitter below its lens.
    # Test the literal source convention, rather than an invented universal gap.
    prefix=row['chunk_id'].split('_')[0]
    expected={'SHOP':.004,'COURT':.03,'SERVICE':.01,'LINK':.04,'STAFFLINK':.04}[prefix]
    proof.append({'id':row['id'],'nearest_physical_lens':best[1],'source_gap_m':best[0],'authored_downward_lens_offset_m':expected,'passed':abs(best[0]-expected)<.00001})
write('PHYSICAL_FIXTURE_LIGHT_AUDIT.json',{'status':'PASS' if all(r['passed'] for r in proof) else 'HOLD','source_lights':len(lights),'proof':proof,'existing_runtime_sources':len(current['lights']),'scope':'507 retained runtime specifications against literal physical source-lens vertices; no new light budget, ambient override or unmeasured GPU/normal-game visual acceptance'})
print('GROUP5_AUTHORITY',len(rows),'venues',len(lights),'lights',sum(r['passed'] for r in proof),'lens matches; unresolved identities84')
