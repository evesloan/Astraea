"""Add an explicitly reviewed B-family section and its authored receiving floor.
Requires a local receiving ledger and an explicit connection configuration.
No slot assignment, bulk automatic approvals, or runtime acceptance implied.
"""
from pathlib import Path
import json,hashlib,shutil,struct,sys
from compile_received_section_floors import compile_received

def adopt(root,ledger_path,request):
    root=Path(root);game=root/'Game';ledger=json.loads(Path(ledger_path).read_text())
    key=request['programme_key'];item=next(x for x in ledger if x['programme_key']==key)
    src=Path(item['extracted_root'])/'B'/request['folder'];placement=json.loads((src/'placements.json').read_text());proposal=json.loads((src/'docs/floor_proposal.json').read_text())
    assert placement['programme_key']==key and placement['rotation_xyz_degrees']==[0,0,0] and placement['scale_xyz']==[1,1,1]
    definitions=json.loads((game/'data/architecture/received_sections.json').read_text());floors=json.loads((game/'data/architecture/received_section_floors.json').read_text());assert key not in [x['programme_key'] for x in definitions['sections']]
    t=placement['translation_xyz'];polys=[proposal['local_xz']] if 'local_xz' in proposal else proposal['polygons_local_xz'];ids=[]
    if request.get('reuse_source_floor_owner'):
        from shapely.geometry import Polygon
        from shapely.ops import unary_union
        base=json.loads((game/'data/generated/structural_meshes.json').read_text())
        old=next(r for r in base['regions'] if r['id']==request['reuse_source_floor_owner'])
        assert abs(old['floor_y']-t[1])<1e-6
        retained=unary_union([Polygon(tri) for tri in old['triangles']])
        assert all(retained.buffer(1e-7).covers(Polygon([[x+t[0],z+t[2]] for x,z in poly])) for poly in polys)
        ids.append(old['id']);polys=[]
    for i,poly in enumerate(polys):
        id_=request['floor_prefix']+('_source_floor' if len(polys)==1 else f'_source_floor_{i}')
        ids.append(id_);floors['regions'].append({'id':id_,'programme_key':key,'kind':'authored_room_floor','boundary':[[x+t[0],z+t[2]] for x,z in poly],'material_role':request.get('material_role','staff_floor')})
    for i,link in enumerate(request['connections']):
        id_=request['floor_prefix']+f'_connection_{i}';ids.append(id_);floors['regions'].append({'id':id_,'programme_key':key,'kind':'explicit_connection','connection_to':link['owner'],'boundary':link['boundary'],'material_role':request.get('material_role','staff_floor')})
    compiled=json.loads(json.dumps(compile_received(game,floors)));prior=json.loads((game/'data/generated/received_structural_meshes.json').read_text());assert compiled['regions'][:len(prior['regions'])]==prior['regions']
    blob=(src/'exports/section.glb').read_bytes();j=json.loads(blob[20:20+struct.unpack_from('<I',blob,12)[0]]);model=f'SOL_{key}_source001.glb'
    dest=root/'BlenderCatalogue/assets/received_sections_20261008/B'/request['folder'];assert not dest.exists();assert not (game/'assets/models'/model).exists()
    programme=next(x for x in json.loads((game/'data/whole_ship_layout.json').read_text())['programmes'] if x['programme_key']==key)
    section={'programme_key':key,'name':placement.get('name',programme['name']),'model_file':model,'source_sha256':hashlib.sha256(blob).hexdigest(),'translation_xyz':t,'rotation_y':0,'source_archive_sha256':item['archive_sha256'],'retained_handoff_commit':'7667074ace2d325a336041f6e33887eeb709813e' if item['set']=='expansion50' else 'b179438a495478d6ac22c4f00a09edb40be80b1d','editable_source':str(dest.relative_to(root)/'source/native.blend'),'floor_owner_ids':ids,'portal_xyz':request['portal_xyz'],'source_mesh_count':sum('mesh' in n for n in j['nodes']),'integration_validation':'pending','operational_and_final_art_acceptance':False}
    for option in ['approach_start_xyz','inward_direction_x','portal_basis','retained_external_gate']:
        if option in request:section[option]=request[option]
    shutil.copytree(src,dest);(game/'assets/models'/model).write_bytes(blob);definitions['sections'].append(section)
    for name,content in [('data/architecture/received_sections.json',definitions),('data/architecture/received_section_floors.json',floors),('data/generated/received_structural_meshes.json',compiled)]:
        path=game/name;temporary=path.with_suffix(path.suffix+'.new');temporary.write_text(json.dumps(content,indent=2)+'\n');temporary.replace(path)
    return {'section':key,'meshes':section['source_mesh_count'],'floor_owners':ids,'prior_owners_unchanged':True}

if __name__=='__main__':
    game=Path(__file__).resolve().parents[1]
    print(json.dumps(adopt(game.parent,sys.argv[1],json.loads(Path(sys.argv[2]).read_text()))))
