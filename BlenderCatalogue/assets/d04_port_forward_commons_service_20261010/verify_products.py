from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];q=json.load(open(W/'PRODUCT_STAGING_ADDENDUM.json'));f=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(f)};exec(f.read_text(),ns);T=ns['triangles'];data={}
for n,t in T(q['record']['export']):
 key=next(b['name']for b in q['bindings']if n.startswith('D04CS_'+b['name']+'__'));data.setdefault(key,[]).append(t)
rows=[]
for b in q['bindings']:
 a=np.unique(np.concatenate(data[b['name']]).reshape(-1,3),axis=0);read=ns['read'];ns['read']=lambda _: (R/'BlenderCatalogue/assets/cleaning_cart/exports/AST-HSK-006.glb').read_bytes();orig=np.unique(np.concatenate([t.reshape(-1,3)for n,t in T('SOURCE',b['position'],b['yaw'])]),axis=0);ns['read']=read;delta=max(np.linalg.norm(a[:,None]-orig[None,:],axis=2).min(1).max(),np.linalg.norm(orig[:,None]-a[None,:],axis=2).min(1).max());assert delta<.00004
 local=np.column_stack([-a[:,0]-77.3,a[:,2]+356.9,a[:,1]-16.5]);assert np.all(local.min(0)>=[-.02,-.238,.525-.00004]) and np.all(local.max(0)<=[.839,.271,.875+.00004]),(b['name'],local.min(0),local.max(0));rows.append({'binding':b['name'],'source_rigid_vertex_error_m':float(delta),'cabinet_upper_shelf_clear_volume_contained':True,'base_y':float(a[:,1].min()),'source_shelf_y':17.025,'source_base_offset_m':float(a[:,1].min()-17.025)})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in q['source_pins'].items():assert sha(R/f)==h,f
report={'status':'PASS','rigid_original_bottles':rows,'source_pins_unchanged':3,'new_product_identity_or_chemistry':False,'operational_stock_refill_accepted':False};(W/'PRODUCT_GEOMETRY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
