"""Inspect authored r002 native mesh bounds; conservative screen, not body acceptance."""
import bpy,json
from pathlib import Path
G=Path(__file__).resolve().parents[2];p=json.loads((G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE.json').read_text());rows=[]
for r in p['rooms']:
 bpy.ops.wm.open_mainfile(filepath=str(G.parent/'BlenderCatalogue'/r['native_source']))
 solids=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.get('runtime_collision',False):continue
  v=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(x[k] for x in v) for k in range(3)];hi=[max(x[k] for x in v) for k in range(3)]
  solids.append((o.name,o.get('reserved_rest_slot_id'),[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]))
 clashes=[]
 for slot,b in r['construction_statistics']['rest_bounds'].items():
  for name,rest,lo,hi in solids:
   if rest or 'Floor' in name or 'Ceiling' in name:continue
   overlap=[min(b[1][k],hi[k])-max(b[0][k],lo[k]) for k in range(3)]
   if min(overlap)>.025:clashes.append({'slot':slot,'mesh':name,'overlap_xyz':overlap})
 rows.append({'allocation':r['allocation']['source_envelope_index'],'solid_mesh_count':len(solids),'potential_aabb_clashes':clashes})
result={'scope':'Conservative native r002 rest envelope AABB screen, not triangle collision or occupied-body acceptance','rooms':rows,'potential_clash_count':sum(len(r['potential_aabb_clashes']) for r in rows)}
(G/'docs/validation/night_garden_specialty_20261020/REST_ENVELOPE_R002.json').write_text(json.dumps(result,indent=2)+'\n');print('NATIVE_SCREEN_COMPLETE',result['potential_clash_count'])
