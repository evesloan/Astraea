"""One additive triage owner after authenticating every current medical-era record."""
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union
from theater_incremental_preservation import effective_shapes
PROOF_SHA='2d34c27e68d27c9dc5258e868d2d62ac3b55332103586003330379c69455bd3d'
PROOF_PATH='data/architecture/packages/medical/triage010/MEDICAL_TRIAGE_COMPILER_PROOF.json'
OWNER='D05_connected_triage_wing_floor'
def preserve_medical_triage_successor(root,layout,elevations,owned,outputs,preserve_welcome):
 p=root/PROOF_PATH;assert hashlib.sha256(p.read_bytes()).hexdigest()==PROOF_SHA
 proof=json.loads(p.read_text());assert proof['schema']==1 and proof['owner_id']==OWNER
 def retained(name):
  spec=proof['predecessors'][name];p=root/spec['retained_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256'];return json.loads(p.read_text())
 old=retained('data/spatial_layout.json');compiled=retained('data/generated/structural_meshes.json');summary=retained('docs/LAYOUT_COMPILE_CHECKS.json');assert compiled['source_checks']==summary
 assert {k:v for k,v in layout.items()if k!='regions'}=={k:v for k,v in old.items()if k!='regions'},'Every prior global and void record must remain exact'
 assert [r for r in layout['regions']if r['id']!=OWNER]==old['regions'],'Complete predecessor layout/order changed'
 assert [r for r in layout['regions']if r['id']==OWNER]==[proof['new_layout_record']]
 old_ids={r['id']for r in old['regions']};out_ids={r['id']for r in compiled['regions']}
 assert len({r['id']for r in layout['regions']})==len(layout['regions'])==len(old['regions'])+1
 assert len({r['id']for r in outputs})==len(outputs)==len(compiled['regions'])+1
 assert {r['id']for r in outputs}==out_ids|{OWNER}
 prior_shapes=effective_shapes(old,elevations)
 for ident in old_ids:assert prior_shapes[ident].equals(owned[ident]),('Old effective footprint changed',ident)
 new=next(r for r in outputs if r['id']==OWNER);expected=Polygon(proof['new_layout_record']['boundary'],proof['new_layout_record'].get('holes',[]))
 assert expected.is_valid and expected.area==544 and owned[OWNER].equals(expected)
 assert new['deck']=='D05'and new['floor_y']==21 and new['thickness']==.24 and abs(new['structural_area_m2']-544)<1e-9
 assert unary_union([Polygon(t)for t in new['triangles']]).equals(expected)
 # Re-run the unchanged welcome proof with its exact live predecessor set.
 projected=dict(layout);projected['regions']=[r for r in layout['regions']if r['id']!=OWNER]
 prior_outputs=[r for r in outputs if r['id']!=OWNER];prior_owned={k:v for k,v in owned.items()if k!=OWNER}
 prior_outputs,welcome_receipt=preserve_welcome(root,projected,elevations,prior_owned,prior_outputs)
 old_by_id={r['id']:r for r in compiled['regions']};reordered=[]
 for row in prior_outputs:
  before=old_by_id[row['id']];assert set(row)==set(before)
  for key in before:
   if key not in ('triangles','rings','structural_area_m2'):assert row[key]==before[key],('Old native metadata/chunk changed',row['id'],key)
  a=unary_union([Polygon(t)for t in row['triangles']]);b=unary_union([Polygon(t)for t in before['triangles']]);assert a.equals(b)and b.equals(prior_shapes[row['id']]);assert abs(row['structural_area_m2']-before['structural_area_m2'])<=1e-9
  if row!=before:reordered.append(row['id'])
 assert [r['id']for r in prior_outputs]==[r['id']for r in compiled['regions']]
 for row in layout['regions']:
  if row['id']!=OWNER and abs(elevations[row['deck']]+row.get('offset_y',0)-21)<1e-6:assert owned[row['id']].intersection(expected).area<1e-7,('Coplanar overlap',row['id'])
 preserved=[old_by_id.get(row['id'],row)for row in outputs]
 assert [r for r in preserved if r['id']!=OWNER]==compiled['regions'],'All complete prior compiled records/order must remain exact'
 return preserved,welcome_receipt,{'proof_sha256':PROOF_SHA,'retained_layout_records':len(old['regions']),'retained_compiled_records':len(compiled['regions']),'retained_void_records':len(old['voids']),'new_owner':OWNER,'new_area_m2':544,'equivalent_triangulation_reorders_restored':reordered,'complete_old_records_preserved':True,'scope':'Structural proof only; no runtime route, clinical or capacity acceptance'}
