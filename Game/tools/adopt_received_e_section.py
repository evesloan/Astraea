"""Install specifically reviewed E source sections at their exact world coordinates."""
from pathlib import Path
import json,hashlib,struct,shutil,sys
from compile_received_section_floors import compile_received

def adopt(root,ledger_path,key):
 root=Path(root);g=root/'Game';item=next(x for x in json.loads(Path(ledger_path).read_text()) if x['programme_key']==key);assert item['batch']=='E'
 src=next(Path(item['extracted_root']).rglob('PLACEMENT.json')).parents[1];placement=json.loads((src/'docs/PLACEMENT.json').read_text());contract=json.loads((src/'docs/CONTRACT.json').read_text());proposal=json.loads((src/'docs/FLOOR_PROPOSAL.json').read_text())
 assert placement['translation']==[0,0,0] and placement['rotation_degrees']==[0,0,0] and placement['native_basis']=='x,-z,y'
 assert key in ['D11_directory_04','D11_directory_05','D11_directory_10','D06_directory_06','D10_directory_06','D10_directory_10','D11_directory_03','D11_directory_07','D11_directory_12','D11_directory_11']
 portal=contract.get('entry_xyz') or contract['portals'][0]['xyz'];edge,y,z=portal;sign=1 if edge>0 else -1
 definitions=json.loads((g/'data/architecture/received_sections.json').read_text());floors=json.loads((g/'data/architecture/received_section_floors.json').read_text());assert key not in [x['programme_key'] for x in definitions['sections']]
 region=key+'_authored_floor';link=key+'_spine_connection'
 if z==0:
  assert edge in [52,54];owner=key[:3]+'_atrium_circulation';join=54 if key=='D06_directory_06' else 51;start=join-1
 elif abs(z)==432:owner=key[:3]+'_aft_public_core_floor';join=7.8;start=6
 elif key=='D11_directory_03':
  assert edge==11 and z==-280;owner='D11_fore_midship_public_core_floor';join=7.8;start=6
 else:owner='D11_fore_route' if z<0 else 'D11_aft_route';join=4;start=3
 floors['regions'].append(dict(id=region,programme_key=key,kind='authored_room_floor',boundary=proposal['boundary'],material_role='guest_floor'))
 if abs(edge)-join>1e-7:
  floors['regions'].append(dict(id=link,programme_key=key,kind='explicit_connection',connection_to=owner,boundary=[[sign*join,z-2],[edge,z-2],[edge,z+2],[sign*join,z+2]],material_role='guest_floor'))
 else:link=owner

 new=json.loads(json.dumps(compile_received(g,floors)));old=json.loads((g/'data/generated/received_structural_meshes.json').read_text());assert new['regions'][:len(old['regions'])]==old['regions']
 b=(src/'exports'/(key+'.glb')).read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);name='SOL_'+key+'_source001.glb';dest=root/'BlenderCatalogue/assets/received_sections_20261008/E'/src.name;assert not dest.exists() and not (g/'assets/models'/name).exists()
 shutil.copytree(src,dest);(g/'assets/models'/name).write_bytes(b)
 row=dict(programme_key=key,name=contract['name'],model_file=name,source_sha256=hashlib.sha256(b).hexdigest(),translation_xyz=[0,0,0],rotation_y=0,source_archive_sha256=item['archive_sha256'],retained_handoff_commit='7667074ace2d325a336041f6e33887eeb709813e',editable_source=str(dest.relative_to(root)/'source'/(key+'.blend')),floor_owner_ids=[region,link],portal_xyz=portal,approach_start_xyz=[sign*start,y,z],source_mesh_count=sum('mesh' in n for n in doc['nodes']),integration_validation='pending',operational_and_final_art_acceptance=False)
 if key in ['D11_directory_03','D11_directory_04','D11_directory_05','D11_directory_07']:
  route=json.loads((src/'docs/APPROACH_PROPOSALS.json').read_text())[0];row['entry_walk_waypoints_xyz']=[[x,y,z] for x,z in route['points_xz'][:3]];row['route_source']='Retained level_guest_cart arrival and side-aisle approach; only ordinary-player entry/return tested'
 if key=='D11_directory_03':row['receiving_core_contract']='FORE_MIDSHIP_PUBLIC_CORE.json'
 definitions['sections'].append(row)
 for path,value in [('data/architecture/received_sections.json',definitions),('data/architecture/received_section_floors.json',floors),('data/generated/received_structural_meshes.json',new)]:
  p=g/path;q=p.with_suffix(p.suffix+'.new');q.write_text(json.dumps(value,indent=2)+'\n');q.replace(p)
 return {'section':key,'meshes':row['source_mesh_count']}
if __name__=='__main__':print(json.dumps(adopt(Path(__file__).resolve().parents[2],sys.argv[1],sys.argv[2])))
