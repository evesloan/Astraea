"""Final independent manifest, texture-source, topology and size checks."""
from pathlib import Path
import hashlib,json,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch03';sys.path.insert(0,str(ROOT/'qa'));sys.path.insert(0,str(ROOT/'qa/batch02'))
from inspect_glb_independent import GLB
from geometry_checks import triangles
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
known={sha(p):str(p.relative_to(ROOT)) for p in (ROOT/'materials/staff').glob('*.png')}
checks=[];texture=[];topology=[];sources=[]
for family in ['wall','overhead','workbay']:
 base=ROOT/'assets'/('staff_'+family);blends=json.loads((OUT/f'independent_{family}_blend_report.json').read_text())
 for b in blends:
  p=Path(b['path']);p=p if p.is_absolute() else ROOT/p
  sources.append({'source':str(p.relative_to(ROOT)),'reload_sha256':b['sha256'],'current_sha256':sha(p),'reload_still_current':b['sha256']==sha(p),'load_success':b['load_success'],'editable_mesh_objects':sum(o['type']=='MESH' for o in b['objects']),'objects_with_modifiers':sum(bool(o.get('modifiers')) for o in b['objects']),'unit_scale':b['units']})
 for p in sorted(base.rglob('*.glb')):
  g=GLB(p).inspect();m=json.loads((base/(p.stem+'.manifest.json')).read_text());source=base/m['source'] if 'source' in m else p.with_suffix('.blend');expected_tri=m.get('triangles',m.get('evaluated_triangles',m.get('triangles_evaluated')));bounds=m.get('dimensions_m',m.get('bounds_blender_z_up',{}).get('dimensions_m'))
  row={'asset':m['catalogue_id'],'source':str(source.relative_to(ROOT)),'export':str(p.relative_to(ROOT)),'triangles':g['triangles'],'bytes':p.stat().st_size,'source_sha256':sha(source),'export_sha256':g['sha256'],'source_hash_matches_manifest':sha(source)==m.get('source_sha256',m.get('blend_sha256')),'export_hash_matches_manifest':g['sha256']==m['glb_sha256'],'triangle_count_matches':g['triangles']==expected_tri,'max_dimension_error_m':float(np.abs(np.array(bounds)-g['dimensions_xyz']).max()),'parser_issues':g['issues'],'collapsed_uv_triangles':sum(x.get('collapsed_uv_triangles',0) for n in g['nodes'] for x in n['primitives']),'collapsed_uv_area_m2':sum(x.get('collapsed_uv_surface_m2',0) for n in g['nodes'] for x in n['primitives']),'materials': [x['name'] for x in g['materials']]}
  checks.append(row)
  for im in g['images']:texture.append({'asset':m['catalogue_id'],'embedded_hash':im.get('embedded_sha256'),'source':known.get(im.get('embedded_sha256')),'embedded':im['embedded']})
  for r in triangles(p):
   t=r['triangles'];v,idx=np.unique(np.round(t.reshape(-1,3),7),axis=0,return_inverse=True);f=idx.reshape(-1,3);edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);un,count=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
   topology.append({'asset':m['catalogue_id'],'node':r['node'],'material':r['role'],'boundary_edges_at_1e_7m':int((count==1).sum()),'higher_valence_edges_at_1e_7m':int((count>2).sum()),'scope':'Position-welded export screen; touching closed solids may form higher-valence edges. Not a Boolean-union manifold claim.'})
files=[p for family in ['wall','overhead','workbay'] for p in (ROOT/'assets'/('staff_'+family)).rglob('*') if p.is_file()]
size={'decimal_byte_limit':8_000_000,'oversize_files':[str(p.relative_to(ROOT)) for p in files if p.stat().st_size>=8_000_000],'largest_file':str(max(files,key=lambda p:p.stat().st_size).relative_to(ROOT)),'largest_bytes':max(p.stat().st_size for p in files)}
for name,data in [('independent_manifest_checks.json',checks),('independent_texture_source_check.json',texture),('independent_export_edge_screen.json',topology),('independent_final_source_checks.json',sources),('independent_asset_size_check.json',size)]: (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'assets':len(checks),'triangles':sum(c['triangles'] for c in checks),'source_reload_failures':[s for s in sources if not(s['load_success'] and s['reload_still_current'])],'manifest_failures':[c for c in checks if not(c['source_hash_matches_manifest'] and c['export_hash_matches_manifest'] and c['triangle_count_matches'] and c['max_dimension_error_m']<1e-6)],'uv_collapsed_area_total':sum(c['collapsed_uv_area_m2'] for c in checks),'texture_misses':[x for x in texture if not x['source']],'boundary_edges':[x for x in topology if x['boundary_edges_at_1e_7m']],'size':size},indent=2))
