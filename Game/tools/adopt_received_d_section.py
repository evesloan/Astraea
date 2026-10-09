"""Adopt reviewed D sources; preserve folded footprint, add an explicit connection."""
from pathlib import Path
import json,hashlib,struct,shutil,sys
from compile_received_section_floors import compile_received
from shapely.geometry import Polygon

def adopt(root,ledger_path,key):
 root=Path(root);g=root/'Game';ledger=json.loads(Path(ledger_path).read_text());item=next(x for x in ledger if x['programme_key']==key);assert item['batch']=='D';src=Path(item['extracted_root'])
 if key.startswith('D12'):src=src/key
 design=json.loads((src/'docs/design.json').read_text());proposal=json.loads((src/'docs/floor_proposal.json').read_text())
 if key.startswith('D12'):
  placement=json.loads((src/'docs/placement.json').read_text());assert placement['position']==[0,0,0] and placement['rotation_degrees']==[0,0,0];contract={'name':design['title'],'portals':[{'xyz':placement['entry_hold_xyz']}]}
 else:contract=json.loads((src/'docs/section_contract.json').read_text())
 assert key in ['D08_directory_03','D08_directory_04','D08_directory_07','D08_directory_05','D08_directory_06','D09_directory_05','D10_directory_05','D08_directory_02','D08_directory_09','D08_directory_10','D12_directory_01','D12_directory_09','D12_directory_10'];portal=contract['portals'][0]['xyz'];edge,y,z=portal;sign=design['side']
 if abs(edge)==8 and abs(z)==216:connection_edge=4;start=3;owner=key[:3]+('_fore_route' if z<0 else '_aft_route')
 elif abs(edge)==8 and abs(z)==432:
  connection_edge=7.8;start=6;owner=key[:3]+('_forward_public_core_floor' if z<0 else '_aft_public_core_floor')
 else:
  assert abs(edge) in [52,54] and z==0;connection_edge=54 if key.startswith('D09') else 51;start=connection_edge-1;owner=key[:3]+'_atrium_circulation'
 definitions=json.loads((g/'data/architecture/received_sections.json').read_text());floors=json.loads((g/'data/architecture/received_section_floors.json').read_text());assert key not in [x['programme_key'] for x in definitions['sections']]
 # Wall centres follow the proposed folded boundary; include their .36m thickness.
 padding=.25 if key.startswith('D12') else .18;shape=Polygon(proposal['boundary_world_xz']).buffer(padding,join_style=2);assert shape.is_valid and shape.geom_type=='Polygon'
 region=key+'_authored_floor';join=abs(edge)+min(x[0] for x in design['footprint'])-padding;link=key+'_spine_connection'
 floors['regions'] += [dict(id=region,programme_key=key,kind='authored_room_floor',boundary=list(shape.exterior.coords)[:-1],material_role='guest_floor'),dict(id=link,programme_key=key,kind='explicit_connection',connection_to=owner,boundary=[[sign*connection_edge,z-2],[sign*join,z-2],[sign*join,z+2],[sign*connection_edge,z+2]],material_role='guest_floor')]
 new=json.loads(json.dumps(compile_received(g,floors)));old=json.loads((g/'data/generated/received_structural_meshes.json').read_text());assert new['regions'][:len(old['regions'])]==old['regions']
 b=(src/'exports'/(key+'.glb')).read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
 name='SOL_'+key+'_source001.glb';dest=root/'BlenderCatalogue/assets/received_sections_20261008/D'/key;assert not dest.exists() and not (g/'assets/models'/name).exists()
 shutil.copytree(src,dest);(g/'assets/models'/name).write_bytes(b)
 definitions['sections'].append(dict(programme_key=key,name=contract['name'],model_file=name,source_sha256=hashlib.sha256(b).hexdigest(),translation_xyz=[0,0,0],rotation_y=0,source_archive_sha256=item['archive_sha256'],retained_handoff_commit=('b179438a495478d6ac22c4f00a09edb40be80b1d' if key.startswith('D12') else '7667074ace2d325a336041f6e33887eeb709813e'),editable_source=str(dest.relative_to(root)/'source/section.blend'),floor_owner_ids=[region,link],portal_xyz=portal,approach_start_xyz=[sign*start,y,z],source_mesh_count=sum('mesh' in n for n in doc['nodes']),integration_validation='pending',operational_and_final_art_acceptance=False))
 for path,value in [('data/architecture/received_sections.json',definitions),('data/architecture/received_section_floors.json',floors),('data/generated/received_structural_meshes.json',new)]:
  p=g/path;q=p.with_suffix(p.suffix+'.new');q.write_text(json.dumps(value,indent=2)+'\n');q.replace(p)
 return {'section':key,'meshes':definitions['sections'][-1]['source_mesh_count'],'floor_area':shape.area}
if __name__=='__main__':print(json.dumps(adopt(Path(__file__).resolve().parents[2],sys.argv[1],sys.argv[2])))
