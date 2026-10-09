"""Install an explicitly reviewed, world-coordinate A-family section."""
from pathlib import Path
import json,hashlib,struct,shutil,sys
from compile_received_section_floors import compile_received

def adopt(root,ledger_path,key):
 root=Path(root);g=root/'Game';ledger=json.loads(Path(ledger_path).read_text());item=next(x for x in ledger if x['programme_key']==key);assert item['batch']=='A';src=Path(item['extracted_root'])/key
 contract=json.loads((src/'contract.json').read_text());assert contract['coordinate_mapping']=='Blender=(GodotX,-GodotZ,GodotY); world origin identity placement'
 definitions=json.loads((g/'data/architecture/received_sections.json').read_text());floors=json.loads((g/'data/architecture/received_section_floors.json').read_text());assert key not in [x['programme_key'] for x in definitions['sections']]
 portal=contract['portals'][0]['xyz'];sign=1 if portal[0]>0 else -1;deck=contract['deck'];y=contract['floor_y'];z=portal[2];edge=portal[0]
 # Follow the retained builder's wall/dado outside faces, folded rear corners,
 # and protected four-metre inlet. This is not the allocation rectangle.
 outline=[(0,-2),(2.86,-2),(2.86,-31.15),(42.5,-31.15),(43.65,-30),(43.65,30),(42.5,31.15),(2.86,31.15),(2.86,2),(0,2)]
 region=key+'_authored_floor';floor={'id':region,'programme_key':key,'kind':'authored_room_floor','boundary':[[edge+sign*u,z+v] for u,v in outline],'material_role':'staff_floor'}
 if key=='D01_directory_06':
  assert edge==52 and z==0;owner='D01_central_service_axis';join=4.0;approach=3.0
 elif abs(z)==216:
  assert abs(edge)==8;owner=deck+('_fore_route' if z<0 else '_aft_route');join=4.0;approach=3.0
 else:
  assert key in ['D01_directory_02','D01_directory_09'] and abs(z)==432,'Other A interfaces require explicit separate connection review'
  owner=deck+('_forward_public_core_floor' if z<0 else '_aft_public_core_floor');join=7.8;approach=6.0
 link={'id':key+'_spine_connection','programme_key':key,'kind':'explicit_connection','connection_to':owner,'boundary':[[sign*join,z-2],[edge,z-2],[edge,z+2],[sign*join,z+2]],'material_role':'staff_floor'}
 links=[link]
 if key=='D01_directory_06':
  link['boundary']=[[4,-2],[42,-2],[42,2],[4,2]]
  links.append(dict(id=key+'_side_connection',programme_key=key,kind='explicit_connection',connection_to='D01_service_side',boundary=[[48,-2],[52,-2],[52,2],[48,2]],material_role='staff_floor'))
 owner_ids=[region]+[r['id'] for r in links]
 if key=='D01_directory_06':owner_ids.append('D01_service_side')
 floors['regions'] += [floor]+links;new=json.loads(json.dumps(compile_received(g,floors)));old=json.loads((g/'data/generated/received_structural_meshes.json').read_text());assert new['regions'][:len(old['regions'])]==old['regions']
 b=(src/'exports'/(key+'.glb')).read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);name='SOL_'+key+'_source001.glb';dest=root/'BlenderCatalogue/assets/received_sections_20261008/A'/key;assert not dest.exists();assert not (g/'assets/models'/name).exists()
 shutil.copytree(src,dest);(g/'assets/models'/name).write_bytes(b)
 definitions['sections'].append({'programme_key':key,'name':contract['name'],'model_file':name,'source_sha256':hashlib.sha256(b).hexdigest(),'translation_xyz':[0,0,0],'rotation_y':0,'source_archive_sha256':item['archive_sha256'],'retained_handoff_commit':'7667074ace2d325a336041f6e33887eeb709813e','editable_source':str(dest.relative_to(root)/'source/native.blend'),'floor_owner_ids':owner_ids,'portal_xyz':portal,'approach_start_xyz':[sign*approach,y,z],'source_mesh_count':sum('mesh' in n for n in doc['nodes']),'integration_validation':'pending','operational_and_final_art_acceptance':False})
 for path,value in [('data/architecture/received_sections.json',definitions),('data/architecture/received_section_floors.json',floors),('data/generated/received_structural_meshes.json',new)]:
  p=g/path;q=p.with_suffix(p.suffix+'.new');q.write_text(json.dumps(value,indent=2)+'\n');q.replace(p)
 return {'section':key,'meshes':definitions['sections'][-1]['source_mesh_count'],'floor_owners':owner_ids}
if __name__=='__main__':print(json.dumps(adopt(Path(__file__).resolve().parents[2],sys.argv[1],sys.argv[2])))
