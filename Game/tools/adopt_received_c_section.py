"""Adopt reviewed C source with its authored floor proposal and explicit spine link.
Restricted to the reviewed D05 +/-216 m interfaces; no allocation/registry edits.
"""
from pathlib import Path
import json,hashlib,struct,shutil,sys
from compile_received_section_floors import compile_received
from shapely.geometry import Polygon
from shapely.ops import unary_union

def adopt(root,ledger_path,key):
 root=Path(root);g=root/'Game';ledger=json.loads(Path(ledger_path).read_text());item=next(x for x in ledger if x['programme_key']==key)
 assert item['batch']=='C';src=Path(item['extracted_root'])/key
 placement=json.loads((src/'docs/PLACEMENT.json').read_text());proposal=json.loads((src/'docs/FLOOR_PROPOSAL.json').read_text())
 assert placement['coordinate_contract']=='Blender=(X,-Z,Y); GLB Y-up world coordinates; identity placement'
 assert placement['placement_xyz']==[0,0,0] and placement['rotation_y']==0 and placement['scale']==[1,1,1]
 portal=placement['entry_proposal_xyz'];edge,y,z=portal;sign=1 if edge>0 else -1
 assert key in ['D05_directory_03','D05_directory_05','D05_directory_06','D05_directory_07','D05_directory_08','D07_directory_04','D07_directory_05','D07_directory_06','D07_directory_07','D07_directory_09']
 assert y==({'D05':21,'D07':35.5}[key[:3]])
 if abs(edge)==8 and abs(z)==216:join=4;start=3;owner=key[:3]+('_fore_route' if z<0 else '_aft_route')
 elif key=='D07_directory_09':
  assert edge==-8 and z==432;join=7.8;start=6;owner='D07_aft_public_core_floor'
 else:
  assert abs(edge)==52 and z==0;join=51;start=50;owner=key[:3]+'_atrium_circulation'

 definitions=json.loads((g/'data/architecture/received_sections.json').read_text());floors=json.loads((g/'data/architecture/received_section_floors.json').read_text())
 assert key not in [x['programme_key'] for x in definitions['sections']]
 base=json.loads((g/'data/generated/structural_meshes.json').read_text());old=json.loads((g/'data/generated/received_structural_meshes.json').read_text())
 existing=unary_union([Polygon(t) for r in base['regions']+old['regions'] if abs(r['floor_y']-y)<1e-6 for t in r['triangles']])
 shape=Polygon(proposal['boundary']);assert shape.is_valid
 remaining=shape.difference(existing);assert remaining.geom_type=='Polygon' and abs(remaining.area-shape.area)<1e-7,'Review overlap before adoption'
 region=key+'_authored_floor';link_id=key+'_spine_connection'
 floors['regions'] += [dict(id=region,programme_key=key,kind='authored_room_floor',boundary=proposal['boundary'],material_role=('staff_floor' if key.startswith('D05') else 'guest_floor')),dict(id=link_id,programme_key=key,kind='explicit_connection',connection_to=owner,boundary=[[sign*join,z-2],[edge,z-2],[edge,z+2],[sign*join,z+2]],material_role=('staff_floor' if key.startswith('D05') else 'guest_floor'))]
 new=json.loads(json.dumps(compile_received(g,floors)));assert new['regions'][:len(old['regions'])]==old['regions']
 b=(src/'exports/section.glb').read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
 name='SOL_'+key+'_source001.glb';dest=root/'BlenderCatalogue/assets/received_sections_20261008/C'/key
 assert not dest.exists() and not (g/'assets/models'/name).exists()
 shutil.copytree(src,dest);(g/'assets/models'/name).write_bytes(b)
 definitions['sections'].append(dict(programme_key=key,name=placement['title'],model_file=name,source_sha256=hashlib.sha256(b).hexdigest(),translation_xyz=[0,0,0],rotation_y=0,source_archive_sha256=item['archive_sha256'],retained_handoff_commit='7667074ace2d325a336041f6e33887eeb709813e',editable_source=str(dest.relative_to(root)/'source/section.blend'),floor_owner_ids=[region,link_id],portal_xyz=portal,approach_start_xyz=[sign*start,y,z],source_mesh_count=sum('mesh' in n for n in doc['nodes']),integration_validation='pending',operational_and_final_art_acceptance=False))
 for path,value in [('data/architecture/received_sections.json',definitions),('data/architecture/received_section_floors.json',floors),('data/generated/received_structural_meshes.json',new)]:
  p=g/path;q=p.with_suffix(p.suffix+'.new');q.write_text(json.dumps(value,indent=2)+'\n');q.replace(p)
 return {'section':key,'mesh_count':definitions['sections'][-1]['source_mesh_count'],'floor_area':shape.area,'retained_owners_preserved':True}
if __name__=='__main__':print(json.dumps(adopt(Path(__file__).resolve().parents[2],sys.argv[1],sys.argv[2])))
