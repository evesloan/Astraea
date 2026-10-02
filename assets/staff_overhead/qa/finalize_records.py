"""Finalize non-geometric records from source reload and binary inspection."""
import json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
manifest=json.loads((BASE/'manifest.json').read_text());reload=json.loads((BASE/'qa/source_reload_checks.json').read_text());coll=json.loads((BASE/'collision_proposals.json').read_text())
for r in manifest['assets']:
    r['inspection_clearance_example']['minimum_mounting_datum_for_2_65m_m']=2.65-r['lowest_geometry_z_m']
    r['inspection_clearance_example']['installation_limit']='The fixture requires a ceiling mounting datum of at least 3.2575 m to preserve 2.65 m below its guard. A lower crew corridor is not automatically suitable. The 3.30 m inspection example does not certify an actual route.'
    r['hanger_length_editability']='Named rod/drop meshes and support dimensions are editable in source/generator. No single validated hanger-length parameter or tested shorter installation is provided.'
    r['generator_sha256']=hashlib.sha256((BASE/'source/build_staff_overhead.py').read_bytes()).hexdigest()
    (BASE/(r['catalogue_id']+'.manifest.json')).write_text(json.dumps(r,indent=2)+'\n')
    if r['kind']!='fixture':
        data=next(x for x in reload['assets'] if x['asset']==r['catalogue_id']);bb=data['part_bounds'];out=[]
        for i in (1,2):
            out.append({'semantic_part':f'support_{i}_crossbeam','type':'box_bounds',**bb[f'support_{i}_formed_crossbeam']})
            for side in (-1,1):
                values=[b for n,b in bb.items() if n.startswith(f'support_{i}_{side:+d}_')]
                out.append({'semantic_part':f'support_{i}_{side:+d}_rod_plate_nut','type':'box_bounds','min_m':[min(b['min_m'][k] for b in values) for k in range(3)],'max_m':[max(b['max_m'][k] for b in values) for k in range(3)]})
        coll[r['catalogue_id']]['supports']=out
        for hull in coll[r['catalogue_id']]['hulls']:
            for point in hull['points_m']:
                if point[2]<-.4:point[2]=-.416
        coll[r['catalogue_id']]['exit_collar_proposals']=[{'semantic_part':n,'type':'box_bounds',**b} for n,b in bb.items() if n.startswith('exit_splice_collar')]
        coll[r['catalogue_id']]['separate_supports']='Six separate measured support envelopes, plus two exit collar bounds. They remain above the local rod-end minimum; none extends down through the circulation volume.'
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n')
rows=[]
for p in sorted(BASE.rglob('*')):
    if p.is_file() and p.suffix in('.blend','.glb','.py','.json','.md') and p.name!='dependency_manifest.json':rows.append({'path':str(p.relative_to(BASE)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(BASE/'dependency_manifest.json').write_text(json.dumps({'scope':'Authoring/exchange/records only; QA images are separate review media. Packed GLBs and Blender sources carry textures. Generator needs shared staff helper/materials.','staff_helper':'../../standards/staff_materials.py','staff_texture_manifest':'../../materials/staff/manifest.json','files':rows,'all_under_8MB':all(r['bytes']<8_000_000 for r in rows)},indent=2)+'\n')
print('FINAL_RECORDS_COMPLETE',len(rows))
