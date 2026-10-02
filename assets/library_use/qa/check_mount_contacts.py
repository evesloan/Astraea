"""Resolve actual exported fixture/table vertices and test contact in exchange coordinates."""
from pathlib import Path
import runpy,json,hashlib
import numpy as np
D=runpy.run_path(str(Path(__file__).with_name('validate_glb.py')));ROOT=D['ROOT'];BASE=D['BASE'];read=D['read'];acc=D['acc'];globals_=D['globals'];distance=D['triangle_distance'];sha=D['sha']
def arrays(path):
 j,b=read(path);out=[];tris=[]
 for idx,mat in globals_(j).items():
  nd=j['nodes'][idx]
  if 'mesh' not in nd:continue
  for pr in j['meshes'][nd['mesh']]['primitives']:
   ps=acc(j,b,pr['attributes']['POSITION']);ps=(np.c_[ps,np.ones(len(ps))]@mat.T)[:,:3];ix=acc(j,b,pr['indices']).astype(int).reshape(-1,3);out.extend(ps);tris.extend(ps[ix])
 return np.array(out),tris
lamp=ROOT/'exports/AST-LIB-008.glb';ps,ts=arrays(lamp);contact=np.unique(np.round(ps[abs(ps[:,1])<1e-7],8),axis=0);mf=json.loads((ROOT/'AST-LIB-008.manifest.json').read_text());reports=[]
for m,filename in zip(mf['compatible_mounts'],['AST-LIB-STUDY-01_open_shared_table.glb','AST-LIB-STUDY-02_sheltered_single_edge.glb']):
 p=BASE/'assets/library_study'/filename;_,tri=arrays(p);s=m['fixture_translation_source_m'];offset=np.array([s[0],s[2],-s[1]]);world=contact+offset
 # Only triangles coplanar with actual receiver surface, avoiding misleading support elsewhere.
 plane=[t for t in tri if max(abs(t[:,1]-s[2]))<2e-6];dist=[min(distance(v,*t) for t in plane) for v in world];err=max(dist)
 reports.append({'fixture_export_sha256':sha(lamp),'support_asset':m['asset'],'support_glb':str(p.relative_to(BASE)),'support_export_sha256':sha(p),'actual_contact_vertices_count':len(contact),'source_translation_m':s,'exchange_translation_m':offset.tolist(),'receiver_height_source_z_m':s[2],'actual_coplanar_receiver_triangles':len(plane),'maximum_foot_vertex_distance_to_receiver_m':err,'nominal_mating_footprint_m':m['mating_shoe_size_m'],'receiver_plate_size_m':m['receiver_plate_size_m'],'all_actual_support_vertices_on_receiver_surface':err<1e-6,'qualification':'Exchange geometry contact only. Whole fixture stability, electrical feed, body reach, room fit and engine physics remain pending'})
 assert err<1e-6
(ROOT/'qa/receiver_contact_validation.json').write_text(json.dumps(reports,indent=2));print('BOTH_RECEIVER_CONTACTS_PASS',[(r['support_asset'],r['maximum_foot_vertex_distance_to_receiver_m']) for r in reports])
