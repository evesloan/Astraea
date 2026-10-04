"""Close the bounded Batch09 review only when every final exact-hash gate passes."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
evidence=[]
for name,key in [('independent_guest_interfaces.json','passed'),('independent_library_interfaces.json','passed'),('independent_guest_visual_review.json','passed'),('independent_library_visual_review.json','passed'),('independent_study_mounts.json','passed'),('independent_rebuild_receipts.json','passed'),('independent_preservation_report.json','pass')]:
 p=OUT/name;r=json.loads(p.read_text());assert r[key],name;evidence.append(bind(p))
 if 'visual_review'in name:
  for view in r['views']:
   assert sha(ROOT/view['image'])==view['image_sha256'],view['image']
assets=[]
for family in ['guest_use','library_use']:
 a=json.loads((OUT/('independent_guest_interfaces.json'if family=='guest_use'else'independent_library_interfaces.json')).read_text());byid={r['id']:r for r in a['assets']}
 vr=json.loads((OUT/('independent_guest_visual_review.json'if family=='guest_use'else'independent_library_visual_review.json')).read_text())
 for mp in sorted((ROOT/'assets'/family).glob('AST-*.manifest.json')):
  m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=mp.parent/m['source'];gp=mp.parent/m['export'];sr=OUT/f'independent_source_{ident}.json';er=OUT/f'independent_export_{ident}.json';s=json.loads(sr.read_text());e=json.loads(er.read_text());assert s['sha256']==sha(sp)and e['sha256']==sha(gp);assert not e['issues'] and s['source_unchanged_after_load'] and e['source_audit_current'];assert e['source_export_vertex_hausdorff_m']<1e-5 and e['source_export_tessellation_equivalent'];assert e['used_source_vs_glb_texture_bytes_equal']
  for b in byid[ident]['bindings'].values():assert sha(ROOT/b['path'])==b['sha256']
  views=[v for v in vr['views']if v.get('current_source_sha256',v['source_sha256'])==sha(sp)and v['export_sha256']==sha(gp)];assert len(views)>=2,(ident,'missing current views')
  evidence.extend([bind(sr),bind(er)]);assets.append({'catalogue_id':ident,'source':bind(sp),'export':bind(gp),'manifest':bind(mp),'triangles':e['triangles'],'materials':len(e['materials']),'render_views_inspected':len(views),'physical_marker_and_coordinate_checks':len(byid[ident]['markers']),'clear_and_blocked_geometry_paths':len(byid[ident]['void_and_blocked_tests']),'pass':True})
index=OUT/'interface_normalized_index_proposed.json';j=json.loads(index.read_text());assert len(j['assets'])==51
for row in j['assets']:
 for b in row['source_export_manifest_bindings'].values():assert sha(ROOT/b['path'])==b['sha256']
files=[]
for family in ['guest_use','library_use']:
 for p in sorted((ROOT/'assets'/family).rglob('*')):
  if p.is_file()and'qa'not in p.parts and'__pycache__'not in p.parts and p.suffix in ['.py','.blend','.glb','.json','.png','.md','.txt']:files.append(bind(p))
receipt={'scope':'Exact final new-family production sources, exports, metadata, textures, generators and documentation; excludes QA-only media. Existing source/common protection has its own baseline receipt.','files':files,'assets':assets,'engine_adopted_instances':0}
rp=OUT/'independent_final_source_hash_receipt.json';rp.write_text(json.dumps(receipt,indent=2)+'\n')
result={'passed':True,'scope':'Bounded six-design component source/export/material/visual/interface/collision-proposal/source-rebuild review','baseline_commit':'620908833951216425172c95dfdb337ec33afc4c','new_unique_artistic_designs':6,'resulting_catalogue_unique_designs':51,'actual_new_export_triangles':sum(a['triangles']for a in assets),'assets':assets,'source_receipt':bind(rp),'interface_proposal':bind(index),'evidence':evidence,'limits':['Original Godot project remains unavailable. No engine physics/controller, working light or terminal UI, room/whole-ship route, species fit, target-PC performance or whole-room acceptance.','Collision review uses stated finite clear/blocked controls and actual source/native geometry. It is not continuous global collision coverage/error certification.','Service covers, controls and stocked journals remain fixed represented components. No unprovided motion trajectory or electrical maintenance procedure is implied.','Source-only rebuilds were executed by lead and independently hash/scope checked here; six GLBs and fifteen generated textures reproduce byte-identically.','Full/compact archive restoration, remote push and durable Library delivery remain separate lead gates.']}
(OUT/'independent_final_review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'designs':6,'triangles':result['actual_new_export_triangles'],'production_files_bound':len(files),'source_receipt_sha256':sha(rp)},indent=2))
