"""Read-only native GLB placement, supports and other-component reservation separation."""
from pathlib import Path
import json,hashlib,numpy as np
from independent_geometry import Native,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07';e=json.loads((OUT/'arrangement/evidence.json').read_text());tests=[];world={};bounds=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value,**kw):tests.append({'name':name,'pass':bool(value),**kw})
for r in e['imports']:
 n=Native(ROOT/r['export']);a=np.deg2rad(r['yaw_source_degrees']);R=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);offset=np.asarray(r['placement_source_m']);source=n.tris@C;placed=source@R.T+offset;n.tris=placed@C.T;world[r['id']]=n
 check(r['id']+'_export_receipt_current',sha(ROOT/r['export'])==r['export_sha256'])
 sourceaudit=json.loads((OUT/f'independent_source_{r["id"]}.json').read_text());check(r['id']+'_final_source_audit_current',sha(ROOT/r['source'])==sourceaudit['sha256'])
 check(r['id']+'_installed_lowest_contact',abs(placed[:,:,2].min()-(.9 if r['id'].endswith('003') else 0))<1e-6)
 for idx,v in n.node_vertices.items():
  p=(v@C)@R.T+offset;bounds.append({'id':r['id'],'node':n.g.doc['nodes'][idx]['name'],'lo':p.min(axis=0),'hi':p.max(axis=0)})
for r in e['actual_beverage_support_contacts']:
 p=np.asarray(r['point_world_m']);a=world['AST-HSP-001'].nearest(C@p,role='warm_stone');b=world['AST-HSP-003'].nearest(C@p,role='dark_rubber');check('actual_host_pair_'+r['name'],a['distance_m']<1e-6 and b['distance_m']<1e-6,host=a,foot=b)
for r in e['actual_counter_mating_samples']:
 a=world['AST-HSP-001'].nearest(C@r['left_actual_m']);b=world['AST-HSP-002'].nearest(C@r['right_actual_m']);gap=np.linalg.norm(np.asarray(a['point_gltf_m'])-b['point_gltf_m']);check('actual_seam_'+r['part'],a['distance_m']<1e-6 and b['distance_m']<1e-6 and abs(gap-.002)<1e-6,gap_m=float(gap))
for r in e['other_component_reservations']:
 lo=np.asarray(r['min_world_m']);hi=np.asarray(r['max_world_m']);inter=[];tested=0
 for b in bounds:
  if b['id']==r['owner']:continue
  tested+=1;overlap=np.minimum(hi,b['hi'])-np.maximum(lo,b['lo'])
  if (overlap>1e-6).all():inter.append({'id':b['id'],'node':b['node'],'overlap_m':overlap.tolist()})
 check('reservation_'+r['owner']+'_'+r['name'],not inter and tested>0,meshes_tested=tested,intersections=inter)
lo=np.array([.31,-.92,0]);hi=np.array([1.09,-.10,1.66]);wrong=[b['node'] for b in bounds if b['id']=='AST-HSP-001' and (np.minimum(hi,b['hi'])-np.maximum(lo,b['lo'])>1e-6).all()]
check('wrong_under_counter_body_reservation_control',bool(wrong),blocking_nodes=wrong)
out={'numeric_pass':len(tests)>30 and all(t['pass'] for t in tests),'checks':tests,'placement_evidence_sha256':sha(OUT/'arrangement/evidence.json'),'scope':'Actual native GLB vertices and node transforms converted once to the documented fixture placement. Other-component mesh AABB separation is conservative; own openings/sweeps are separately tested. Not an approved room layout, species reach, routing or installed service design.'}
(OUT/'independent_assembly_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['numeric_pass'],'checks':len(tests),'failed':[t for t in tests if not t['pass']]},indent=2))
