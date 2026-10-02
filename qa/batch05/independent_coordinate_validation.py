"""Actual native GLB hierarchy and triangle checks against converted source records."""
from pathlib import Path
import json,sys,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';sys.path.insert(0,str(ROOT/'qa'));from inspect_glb_independent import GLB
C=np.array([[1.,0,0],[0,0,1],[0,-1,0]])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(rel):return json.loads((ROOT/rel).read_text())
class Native:
 def __init__(self,rel):
  self.rel=rel;self.g=GLB(ROOT/rel);self.world={};self.parents={};self.tris=[];self.materials=[];self.nodes=[]
  def visit(i,parent,anc):
   assert i not in anc;n=self.g.doc['nodes'][i];w=parent@self.g.matrix(n);self.world[i]=w
   if 'mesh' in n:
    for p in self.g.doc['meshes'][n['mesh']]['primitives']:
     v=self.g.accessor(p['attributes']['POSITION']);v=(np.column_stack([v,np.ones(len(v))])@w.T)[:,:3];idx=self.g.accessor(p['indices']).ravel().reshape(-1,3);t=v[idx];self.tris.extend(t);self.materials.extend([self.g.doc['materials'][p['material']]['name']]*len(t));self.nodes.extend([n.get('name',str(i))]*len(t))
   for ch in n.get('children',[]):self.parents[ch]=i;visit(ch,w,anc|{i})
  for n in self.g.doc['scenes'][self.g.doc.get('scene',0)]['nodes']:visit(n,np.eye(4),set())
  self.tris=np.array(self.tris);self.materials=np.array(self.materials);self.nodes=np.array(self.nodes)
 def nearest(self,p,role=None):
  mask=np.ones(len(self.tris),bool) if role is None else np.array([role in m for m in self.materials]);idx=np.where(mask)[0];t=self.tris[mask];p=np.asarray(p);a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=np.einsum('ij,ij->i',n,n);proj=p-n*(np.einsum('ij,ij->i',p-a,n)/np.maximum(nn,1e-30))[:,None]
  v=proj-a;d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac);d20=np.einsum('ij,ij->i',v,ab);d21=np.einsum('ij,ij->i',v,ac);den=d00*d11-d01*d01;u=(d11*d20-d01*d21)/np.maximum(den,1e-30);vv=(d00*d21-d01*d20)/np.maximum(den,1e-30);inside=(u>=0)&(vv>=0)&(u+vv<=1)&(nn>1e-20)
  candidates=[proj];ds=[np.where(inside,np.sum((proj-p)**2,axis=1),np.inf)]
  for x,y in [(a,b),(b,c),(c,a)]:
   e=y-x;f=np.clip(np.einsum('ij,ij->i',p-x,e)/np.maximum(np.einsum('ij,ij->i',e,e),1e-30),0,1);q=x+f[:,None]*e;candidates.append(q);ds.append(np.sum((q-p)**2,axis=1))
  ds=np.array(ds);kind,i=np.unravel_index(np.argmin(ds),ds.shape);k=idx[i];normal=n[i]/max(np.linalg.norm(n[i]),1e-30)
  return {'distance_m':float(math.sqrt(ds[kind,i])),'nearest_point_gltf_m':candidates[kind][i].tolist(),'face_normal_gltf':normal.tolist(),'material':str(self.materials[k]),'node':str(self.nodes[k]),'triangle_index':int(k)}
cache={}
def native(rel):
 if rel not in cache:cache[rel]=Native(rel)
 return cache[rel]
checks=[]
def check(name,manifest,field,glb,p,kind='surface',role=None,tolerance=.0001,normal=None):
 n=native(glb);p=np.array(p,float);q=C@p;got=n.nearest(q,role);wrong=n.nearest(p,role);r={'name':name,'record':manifest+'#'+field,'record_frame':'Blender Z-up asset/source metres','kind':kind,'source_point_m':p.tolist(),'expected_gltf_point_m':q.tolist(),'actual_native_mesh_test':got,'wrong_axis_negative_control':{'fault':'Intentionally use source XYZ unchanged in native GLB Y-up','wrong_point_m':p.tolist(),'distance_to_expected_surface_role_m':wrong['distance_m']},'tolerance_m':tolerance}
 if kind=='surface':r['pass']=got['distance_m']<=tolerance
 elif kind=='grip_centerline_pose':r['expected_distance_to_tube_surface_m']=[.020,.024];r['pass']=.020<=got['distance_m']<=.024;r['note']='Centreline record is intentionally inside grip tube; it is not a surface-contact position. Nearest actual triangle is a measured geometric witness.'
 if normal is not None:r['expected_gltf_normal']=list(C@normal);r['actual_face_normal_dot_expected']=float(np.dot(got['face_normal_gltf'],C@normal))
 r['wrong_axis_detected']=(not .020<=wrong['distance_m']<=.024) if kind=='grip_centerline_pose' else wrong['distance_m']>tolerance
 r['negative_control_rule']='Must fail the same acceptance interval/tolerance as the correctly converted record, even if wrong axes happen to be near another surface.'
 checks.append(r)
# Current aquatic source records.
m='assets/aquatic_lounge/AST-AQU-001.manifest.json';j=read(m);check('aquatic lounger pelvic support',m,'contact_proposals.pelvic_contact_m','assets/aquatic_lounge/exports/AST-AQU-001.glb',j['contact_proposals']['pelvic_contact_m'],role='clay_sling',tolerance=.002)
m='assets/aquatic_float/AST-AQU-006.manifest.json';j=read(m)
for i,p in enumerate(j['design_proposals']['seat_contact_proposals']):check('aquatic float measured membrane '+str(i),m,'design_proposals.seat_contact_proposals.'+str(i),'assets/aquatic_float/exports/AST-AQU-006.glb',p['position_m'],role='teal_sling',normal=np.array(p['normal']))
for i,p in enumerate(j['design_proposals']['grips']):check('aquatic float grip '+p['side'],m,'design_proposals.grips.'+str(i)+'.center_m','assets/aquatic_float/exports/AST-AQU-006.glb',p['center_m'],'grip_centerline_pose','dark_grip')
check('aquatic float headrest',m,'design_proposals.headrest_contact_m','assets/aquatic_float/exports/AST-AQU-006.glb',j['design_proposals']['headrest_contact_m'],role='pearl_float',tolerance=.0001)
m='assets/aquatic_edges/AST-AQU-003.manifest.json';j=read(m);pad=j['host_contact_pads'][0];p=(np.array(pad['bounds_min_m'])+pad['bounds_max_m'])/2;p[2]=pad['receiving_z_m'];check('aquatic coping receiving mount',m,'host_contact_pads.0.underside_center_derived_from_bounds','assets/aquatic_edges/AST-AQU-003.glb',p,role='satin_alloy',normal=np.array([0,0,-1]))
# Prior preserved families: values read from their actual manifests.
m='assets/furniture/AST-FUR-001_day_window_bench.manifest.json';j=read(m);check('prior guest bench crown',m,'seat_contact_proposal.seat_centres_m.0','assets/furniture/AST-FUR-001_day_window_bench.glb',j['seat_contact_proposal']['seat_centres_m'][0],tolerance=.005)
m='assets/library_study/AST-LIB-STUDY-01_open_shared_table.manifest.json';j=read(m);check('prior library light receiver',m,'fixture_mounts.0.origin_m','assets/library_study/AST-LIB-STUDY-01_open_shared_table.glb',j['fixture_mounts'][0]['origin_m'],normal=np.array(j['fixture_mounts'][0]['normal']))
m='assets/staff_workbay/AST-STF-007_supply_work_cabinet.manifest.json';j=read(m);staff=j;check('prior staff counter',m,'target_proposals.counter_front_contact_m','assets/staff_workbay/AST-STF-007_supply_work_cabinet.glb',j['target_proposals']['counter_front_contact_m'],normal=np.array([0,0,1]))
m='assets/botanical_planter/AST-BOT-004.manifest.json';j=read(m);pl=j['planting_opening'];p=[(pl['min_xy_m'][0]+pl['max_xy_m'][0])/2,(pl['min_xy_m'][1]+pl['max_xy_m'][1])/2,pl['soil_top_z_m']];check('prior botanical soil centre',m,'planting_opening.soil_surface_center_derived_from_bounds','assets/botanical_planter/'+j['runtime_glb'],p,role='soil',normal=np.array([0,0,1]))
# Actual articulated pivot hierarchy, not an assumed asset root.
g=native('assets/staff_workbay/AST-STF-007_supply_work_cabinet.glb');pi=next(i for i,n in enumerate(g.g.doc['nodes']) if n.get('name')==staff['door']['pivot_node_name']);pivot=g.world[pi][:3,3];expect=C@staff['door']['pivot_blender_m'];children=g.g.doc['nodes'][pi]['children'];vertex_node=children[0];node=g.g.doc['nodes'][vertex_node];pr=g.g.doc['meshes'][node['mesh']]['primitives'][0];loc=g.g.accessor(pr['attributes']['POSITION'])[0];nativeworld=(g.world[vertex_node]@np.append(loc,1))[:3];ang=math.radians(-105);cz,sz=math.cos(ang),math.sin(ang);Rs=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]);Rg=C@Rs@C.T;posedg=pivot+Rg@(nativeworld-pivot);sourced=C.T@nativeworld;poseds=np.array(staff['door']['pivot_blender_m'])+Rs@(sourced-staff['door']['pivot_blender_m']);poseerror=np.linalg.norm(posedg-C@poseds)
pivotrec={'asset':'AST-STF-007','actual_pivot_node_index':pi,'actual_parent_matrix':g.world[pi].tolist(),'source_pivot_m':staff['door']['pivot_blender_m'],'expected_pivot_gltf_m':expect.tolist(),'actual_hierarchy_pivot_gltf_m':pivot.tolist(),'pivot_error_m':float(np.linalg.norm(pivot-expect)),'actual_child_nodes':[g.g.doc['nodes'][i]['name'] for i in children],'source_axis':staff['door']['axis_blender'],'converted_axis':list(C@staff['door']['axis_blender']),'documented_gltf_axis':staff['door']['axis_gltf_Yup'],'actual_native_child_vertex_m':nativeworld.tolist(),'same_signed_minus105_degree_basis_pose_error_m':float(poseerror),'wrong_native_Z_axis_minus105_pose_error_m':float(np.linalg.norm((pivot+Rs@(nativeworld-pivot))-posedg)),'pass':bool(np.linalg.norm(pivot-expect)<1e-6 and poseerror<1e-6),'current_explicit_frame_metadata':g.g.doc['nodes'][pi].get('extras',{})}
meta=pivotrec['current_explicit_frame_metadata'];pivotrec['metadata_checks']={'revision':meta.get('coordinate_metadata_revision')=='hinge-frame-metadata-02','source_axis_explicit':meta.get('hinge_axis_blender_source')==[0,0,1],'native_axis_explicit':meta.get('hinge_axis_gltf_yup')==[0,1,0],'source_pivot_explicit':meta.get('hinge_pivot_blender_source_m')==staff['door']['pivot_blender_m'],'native_pivot_explicit':meta.get('hinge_pivot_gltf_yup_m')==staff['door']['pivot_gltf_Yup_m'],'old_unqualified_axis_removed':'axis' not in meta}
pivotrec['pass']=pivotrec['pass'] and all(pivotrec['metadata_checks'].values())
# Zero origins/void centres are datums, never automatically physical contacts.
floatman=read('assets/aquatic_float/AST-AQU-006.manifest.json');void=np.array(floatman['design_proposals']['seat_center_datum_m']);fd=native('assets/aquatic_float/exports/AST-AQU-006.glb');voidrec={'source_point_m':void.tolist(),'gltf_point_m':list(C@void),'kind':'open_drain_datum_not_contact','nearest_membrane_distance_m':fd.nearest(C@void,'teal_sling')['distance_m'],'note':'Do not interpret a transformed origin or this drain centre as a surface contact.'}
origins=[]
for rel,notes in [('assets/aquatic_lounge/exports/AST-AQU-001.glb','floor datum'),('assets/aquatic_edges/AST-AQU-003.glb','first seam/deck datum'),('assets/aquatic_float/exports/AST-AQU-006.glb','proposed design waterline datum')]:
 n=native(rel);origins.append({'glb':rel,'source_origin_m':[0,0,0],'mapped_asset_origin_m':[0,0,0],'meaning':notes,'root_nodes':[{'name':n.g.doc['nodes'][i].get('name'),'actual_world_matrix':n.world[i].tolist()} for i in n.g.doc['scenes'][n.g.doc.get('scene',0)]['nodes']],'note':'Exporter baked axis conversion into mesh positions for these static roots. Origin consistency is not proof of floor contact or buoyancy.'})
out={'coordinate_contracts':[{'path':rel,'sha256':sha(ROOT/rel)} for rel in ['standards/COORDINATE_CONTRACT.md','standards/coordinate_compatibility.json']],'basis_source_to_gltf':C.tolist(),'determinant':float(np.linalg.det(C)),'method':'Read actual GLB binary positions/indices and compose complete scene node matrices/TRS. Compare converted source records with closest points on actual native glTF triangles. No Blender importer reversal and no dimension-only pass.','surface_and_pose_checks':checks,'articulated_pivot_check':pivotrec,'open_drain_datum':voidrec,'static_origin_records':origins,'files':[{'path':r,'sha256':sha(ROOT/r),'nodes_resolved':len(n.world),'triangles_tested':len(n.tris)} for r,n in cache.items()],'all_representative_checks_pass':all(r['pass'] for r in checks) and pivotrec['pass'],'all_surface_wrong_axis_controls_detected':all(r['wrong_axis_detected'] for r in checks),'limitations':['Finite representative exchange checks, not every catalogue annotation.','No native-engine placement, collision, animation controller, species fit or physical behavior claim.','Current staff pivot native GLB extras now explicitly name both source +Z and GLB +Y axes and pivots. Archived unqualified axis metadata is covered by the compatibility history; it is absent from the current export.']}
(OUT/'independent_coordinate_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'checks':[{'name':r['name'],'distance_m':r['actual_native_mesh_test']['distance_m'],'pass':r['pass'],'negative_distance_m':r['wrong_axis_negative_control']['distance_to_expected_surface_role_m'],'negative_detected':r['wrong_axis_detected']} for r in checks],'pivot':pivotrec,'all_pass':out['all_representative_checks_pass'],'negative_controls':out['all_surface_wrong_axis_controls_detected']},indent=2))
