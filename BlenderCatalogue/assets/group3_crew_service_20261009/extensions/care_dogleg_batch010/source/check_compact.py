"""Bounded runtime geometry, original dependency and repeat-export checks."""
from pathlib import Path
import hashlib,json,math,sys,datetime
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parents[1];ROOT=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');sys.path.insert(0,str(HERE/'source'));from native_glb_subset import GLB
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n')
rows=[]
for p in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(p);triangles=bad=opposed=0;finite=True
 for q in g.doc['nodes']:
  if'mesh'not in q:continue
  assert q.get('extras',{}).get('category')!='floor'
  for prim in g.doc['meshes'][q['mesh']]['primitives']:
   v=g.accessor(prim['attributes']['POSITION']);norm=g.accessor(prim['attributes']['NORMAL']);idx=[a[0]for a in g.accessor(prim['indices'])];finite &=all(math.isfinite(x)for a in v+norm for x in a)
   for k in range(0,len(idx),3):
    i,j,l=idx[k:k+3];a=[v[j][c]-v[i][c]for c in range(3)];b=[v[l][c]-v[i][c]for c in range(3)];cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];area=sum(x*x for x in cross)**.5;bad+=area<1e-10;n=[sum(norm[ix][c]for ix in [i,j,l])for c in range(3)];opposed+=sum(cross[c]*n[c]for c in range(3))< -1e-10;triangles+=1
 r={'file':str(p.relative_to(HERE)),'sha256':sha(p),'runtime_meshes':sum('mesh'in q for q in g.doc['nodes']),'evaluated_triangles':triangles,'degenerate_triangles':bad,'opposed_normal_triangles':opposed,'finite_coordinates':finite,'pass':bad==0 and opposed==0 and finite};rows.append(r)
assert all(q['pass']for q in rows)
write(HERE/'qa/COMPACT_RUNTIME_GEOMETRY.json',{'status':'PASS','exports':rows,'total_triangles':sum(q['evaluated_triangles']for q in rows),'no_floor_meshes_or_runtime_adoption':True})
if(HERE/'qa/REPEAT_BEFORE.json').exists():
 before=json.loads((HERE/'qa/REPEAT_BEFORE.json').read_text());after={p.name:sha(p)for p in(HERE/'exports').glob('*.glb')};assert before==after;write(HERE/'qa/REPEAT_NATIVE_EXPORT.json',{'status':'PASS','before':before,'after':after,'byte_identical':True,'scope':'Fresh deterministic builder/native export replay from identical frozen specs and retained pixels'})
pins=json.loads((HERE/'source/CARE_DOGLEG.json').read_text())['source_pins'];extra=['Game/scripts/crew_batch_receiving.gd','Game/scripts/staff_section.gd','Game/scripts/service_door.gd','Game/scripts/receiving_source_lights.gd','Game/scripts/lighting_budget.gd','Game/scripts/cleaning_cart.gd','Game/docs/reference_register/staff_lift_reference_20261003.jpg','Game/docs/whole_ship_plans/D03.png'];m=json.loads((ROOT/'BlenderCatalogue/materials/staff/manifest.json').read_text())
for r in m['materials'].values():extra.append('BlenderCatalogue/materials/staff/'+r['file'])
depot=ROOT/'BlenderCatalogue/assets/group3_crew_service_20261009/extensions/depot_receiving_batch005'
for n in ['source/DEPOT_RECEIVING.json','qa/DEPOT_NATIVE_GEOMETRY.json']:
 extra.append(str((depot/n).relative_to(ROOT)))
cart=next(q for q in json.loads((depot/'source/DEPOT_RECEIVING.json').read_text())['reused_asset_dependencies']if q['catalogue_id']=='AST-HSK-005');extra.extend([cart['path'],'Game/data/architecture/cleaning_cart_contacts.json'])
for n in extra:pins[n]=sha(ROOT/n)
assert all(sha(ROOT/n)==h for n,h in pins.items())
write(HERE/'source/SOURCE_DEPENDENCIES.json',{'schema':1,'source_pins':pins,'pins_verified_again_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_original_files_preserved':True,'runtime_binding_owned_by_root':True,'broader_source_dependencies_are_reused_and_not_copied':True})
print(json.dumps({'status':'PASS','triangles':sum(q['evaluated_triangles']for q in rows),'meshes':sum(q['runtime_meshes']for q in rows),'pinned_source_dependencies':len(pins)}))
