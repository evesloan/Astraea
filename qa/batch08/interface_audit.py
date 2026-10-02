"""Read-only Batch08 interface inventory and native GLB evidence.

Writes only interface_* reports in this directory. Does not load Blender,
execute asset generators, edit asset metadata, or certify engine use.
"""
from pathlib import Path
import datetime, hashlib, json, re, sys
import numpy as np
sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'qa'))
from inspect_glb_independent import GLB
C=np.array([[1.,0,0],[0,0,1],[0,-1,0]])
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):
 p=Path(p)
 return {'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size,'sha256':sha(p)}
def write(name,x): (OUT/name).write_text(json.dumps(x,indent=2)+'\n')
def walk(v,p=''):
 yield p,v
 if isinstance(v,dict):
  for k,x in v.items(): yield from walk(x,p+'/'+str(k).replace('~','~0').replace('/','~1'))
 elif isinstance(v,list):
  for k,x in enumerate(v): yield from walk(x,p+'/'+str(k))
def numeric3(v):
 return isinstance(v,list) and len(v)==3 and all(isinstance(x,(int,float)) for x in v)
def pairs(d,ref):
 rows=[]
 # Only explicit matching vector/point fields. Bounds endpoints cannot be
 # checked individually because basis conversion reorders min/max corners.
 variants=[('blender_source','gltf_yup'),('blender','gltf_yup'),('blender','gltf_Yup'),('blender','glTF'),('source','glb'),('source','gltf')]
 for ptr,obj in walk(d):
  if not isinstance(obj,dict): continue
  used=set()
  for k,v in obj.items():
   if not numeric3(v) or any(x in k for x in ['min_','max_','dimensions','bounds','envelope']): continue
   for s,t in variants:
    if s not in k: continue
    other=k.replace(s,t)
    if other not in obj or not numeric3(obj[other]) or (k,other) in used: continue
    used.add((k,other));err=float(np.max(np.abs(C@v-np.array(obj[other]))))
    rows.append({'source':ref+'#'+ptr+'/'+k,'exchange':ref+'#'+ptr+'/'+other,'max_error':err,'pass':err<1e-6})
 return rows

class Native:
 def __init__(self,rel):
  self.g=GLB(ROOT/rel);self.rel=rel;self.world={};self.parent={};self.tris=[];self.node_ids=[];self.materials=[]
  d=self.g.doc;nodes=d.get('nodes',[])
  def visit(i,parent,anc):
   assert i not in anc and i not in self.world, 'cycle or repeated node parent'
   n=nodes[i];w=parent@self.g.matrix(n);self.world[i]=w
   if 'mesh' in n:
    for p in d['meshes'][n['mesh']]['primitives']:
     assert p.get('mode',4)==4
     v=self.g.accessor(p['attributes']['POSITION']).astype(float)
     v=(np.column_stack([v,np.ones(len(v))])@w.T)[:,:3]
     ix=self.g.accessor(p['indices']).ravel().reshape(-1,3) if 'indices' in p else np.arange(len(v)).reshape(-1,3)
     self.tris.extend(v[ix]);self.node_ids.extend([i]*len(ix));self.materials.extend([p.get('material')]*len(ix))
   for ch in n.get('children',[]):self.parent[ch]=i;visit(ch,w,anc|{i})
  for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,np.eye(4),set())
  self.tris=np.asarray(self.tris);self.node_ids=np.array(self.node_ids);self.materials=np.array(self.materials)
 def nearest(self,point,allowed=None):
  mask=np.ones(len(self.tris),bool) if allowed is None else np.isin(self.node_ids,allowed)
  indexes=np.flatnonzero(mask);t=self.tris[mask];p=np.array(point)
  if not len(t):return None
  a,b,c=t[:,0],t[:,1],t[:,2];ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=np.einsum('ij,ij->i',n,n)
  proj=p-n*(np.einsum('ij,ij->i',p-a,n)/np.maximum(nn,1e-30))[:,None]
  v=proj-a;d00=np.einsum('ij,ij->i',ab,ab);d01=np.einsum('ij,ij->i',ab,ac);d11=np.einsum('ij,ij->i',ac,ac);d20=np.einsum('ij,ij->i',v,ab);d21=np.einsum('ij,ij->i',v,ac);den=d00*d11-d01*d01
  u=(d11*d20-d01*d21)/np.maximum(den,1e-30);vv=(d00*d21-d01*d20)/np.maximum(den,1e-30)
  inside=(u>=0)&(vv>=0)&(u+vv<=1)&(nn>1e-20)
  ds=[np.where(inside,np.sum((proj-p)**2,axis=1),np.inf)];qs=[proj]
  for x,y in [(a,b),(b,c),(c,a)]:
   e=y-x;f=np.clip(np.einsum('ij,ij->i',p-x,e)/np.maximum(np.einsum('ij,ij->i',e,e),1e-30),0,1);q=x+f[:,None]*e;qs.append(q);ds.append(np.sum((q-p)**2,axis=1))
  ds=np.asarray(ds);kind,ii=np.unravel_index(np.argmin(ds),ds.shape);j=indexes[ii];ni=int(self.node_ids[j]);mi=self.materials[j]
  return {'distance_m':float(np.sqrt(ds[kind,ii])),'point_gltf_yup_m':qs[kind][ii].tolist(),'node_index':ni,'node_name':self.g.doc['nodes'][ni].get('name'),'material':self.g.doc['materials'][mi].get('name') if mi is not None else None,'triangle_index':int(j)}
 def evidence(self):
  d=self.g.doc;nodes=[];markers=[];legacy=[];surface=[]
  for i,n in enumerate(d.get('nodes',[])):
   e=n.get('extras',{});w=self.world.get(i);row={'index':i,'name':n.get('name'),'parent_index':self.parent.get(i),'children':n.get('children',[]),'mesh_index':n.get('mesh'),'extras':e,'local_matrix':self.g.matrix(n).tolist(),'world_matrix':None if w is None else w.tolist()};nodes.append(row)
   if w is None:continue
   for k in ['position_gltf_yup_m','point_gltf_yup','pivot_gltf_yup','hinge_pivot_gltf_yup_m']:
    if numeric3(e.get(k)):
     err=float(np.max(np.abs(w[:3,3]-e[k])));markers.append({'pointer':self.rel+'#/nodes/'+str(i)+'/extras/'+k,'node':n.get('name'),'node_world_origin_gltf_yup_m':w[:3,3].tolist(),'declared_gltf_yup_m':e[k],'error_m':err,'pass':err<1e-6})
     kind=e.get('kind','').lower()
     if 'physical' in kind and 'centreline' not in kind and 'centerline' not in kind and 'open_nozzle_mouth' not in kind:
      target=e.get('support_mesh',e.get('foot_mesh',e.get('wheel_mesh')))
      allowed=None
      if target:
       allowed=[j for j,nn in enumerate(d['nodes']) if target==nn.get('name') or any(target in str(nn.get('extras',{}).get(t,'')) for t in ['source_parts','semantic_parts','source_semantic_parts'])]
      got=self.nearest(e[k],allowed);surface.append({'node':n.get('name'),'kind':kind,'record_pointer':self.rel+'#/nodes/'+str(i)+'/extras','target_source_part':target,'target_export_nodes':allowed,'nearest_native_surface':got,'within_2mm':got is not None and got['distance_m']<=.002,'scope':'Neutral-pose geometric witness only. Contact normal may be support direction, not outward triangle normal.'})
     break
   for k in ['pivot','datum','axis']:
    v=e.get(k)
    if isinstance(v,str) and any(t in v for t in ['Z up','+Z up','front -Y']) and not any(t in v.lower() for t in ['blender','source']):legacy.append({'node_index':i,'node':n.get('name'),'key':k,'text':v,'interpretation':'Legacy descriptive source-axis prose; actual native GLB coordinates remain Y-up. Needs an explicit consumer-facing metadata interpretation, not geometry rotation.'})
  p=self.tris.reshape(-1,3);lo=p.min(0);hi=p.max(0)
  return {'nodes':nodes,'node_count':len(nodes),'resolved_scene_nodes':len(self.world),'orphan_node_indices':sorted(set(range(len(nodes)))-set(self.world)),'triangles':len(self.tris),'bounds_gltf_yup_m':{'min':lo.tolist(),'max':hi.tolist()},'dimensions_blender_xyz_m':(hi-lo)[[0,2,1]].tolist(),'materials':[{'index':i,'name':m.get('name'),'extras':m.get('extras',{})} for i,m in enumerate(d.get('materials',[]))],'external_uris':[v for _,o in walk(d) if isinstance(o,dict) for k,v in o.items() if k=='uri' and not str(v).startswith('data:')],'animations':len(d.get('animations',[])),'skins':len(d.get('skins',[])),'marker_origin_checks':markers,'physical_marker_surface_witnesses':surface,'legacy_source_axis_prose':legacy,'dual_frame_checks':pairs(d,self.rel)}

GROUPS={
 'units_and_frames':['units','coordinates','source_axes','source_frame','exchange_frame','glb_frame','source_up_axis','front_axis','axis','datum','export','export_settings'],
 'datum_and_pivot':['pivot','pivot_m','pivot_local_m','pivot_source_m','pivot_glb_m','pivot_blender_source_m','pivot_gltf_yup_m','pivot_description','pivot_meaning','datum','connection_api'],
 'connections':['seams','joins','connections','connection_api','connection_recipe','ports','shelf_top_stock_anchors','bookstock_mounts','fixture_mounts','ceiling_support_anchors','mounts','mating_section_file','joints'],
 'contact_and_pose':['seat_contact_proposal','contact_proposal','contact_proposals','support_contact_proposal','contact_annotations','contact_joins','floor_contacts','support_contacts','host_contact_pads','physical_contacts','native_marker_records','target_proposals','design_proposals','support_and_join_records','soil_placement','soil_contact_z_m','planting_opening','support_relationships','storage_openings','service_and_connection_markers','measured_contact_samples','support_design','shelf_top_stock_anchors','ceiling_support_anchors','mounts','controls','connection_api','resource_api'],
 'motion':['door','motion','controls','service','removable_export_nodes','drawer_proposal','proposed_motion_nodes','stock_groups','wheels'],
 'clearance_and_placement':['approach_proposal','approach','clear_volumes_m','reading_surface_use_rectangles_m','maintenance_clearances','clearances','staff_use','staff_shelf_access','front_approach_proposal','foliage_separation','proposed_installation','intended_fit','coping_relationship','inspection_clearance_example','fixture_anchor_data_only'],
 'collision':['collision','collision_proposal','collision_proposal_file'],
 'materials':['materials','material_roles','used_material_roles','materials_library','material_roles_and_uv','material_revision','materials_revision','shared_material_revision'],
 'dependencies':['source_generator','generator','texture_generator','source_generator_support_files','source_dependencies','dependencies','dependency_sha256','shared_material_dependency','shared_material_source','local_graphic_sources','resources','source_method','hashes']}

def resolve(token,folder):
 if not isinstance(token,str) or '\n' in token or len(token)>300:return []
 if token.startswith(('http:','https:','libfile_')):return []
 x=token.split('#')[0]
 bases=[folder,ROOT]
 if Path(x).is_absolute(): bases=[Path('/')]
 hits=[]
 for b in bases:
  q=Path(x) if Path(x).is_absolute() else b/x
  found=list(q.parent.glob(q.name)) if any(t in q.name for t in ['*','?','[']) and q.parent.exists() else ([q] if q.exists() else [])
  for p in found:
   p=p.resolve()
   if p.is_relative_to(ROOT) and p not in hits:hits.append(p)
 return hits

def run():
 catalogue=json.loads((ROOT/'catalogue_manifest.json').read_text());assets=catalogue['assets'];assert len(assets)==45 and len({a['catalogue_id'] for a in assets})==45
 native_rows=[];coverage=[];file_bindings={};pair_rows=[];path_rows=[];dependency_hash_checks=[];direction_checks=[]
 for a in assets:
  ident=a['catalogue_id'];mp=ROOT/a['manifest'];full=json.loads(mp.read_text());m=full;mptr=''
  if isinstance(full.get('assets'),list):
   ix=next(i for i,x in enumerate(full['assets']) if x.get('catalogue_id',x.get('id'))==ident);m=full['assets'][ix];mptr='/assets/'+str(ix)
  paths={k:binding(ROOT/a[k]) for k in ['source','export','manifest']}
  for b in paths.values():file_bindings[b['path']]=b
  n=Native(a['export']);ev=n.evidence();ev['catalogue_id']=ident;ev['file']=paths['export'];native_rows.append(ev)
  groups={k:[{'pointer':a['manifest']+'#'+mptr+'/'+field,'value':m[field]} for field in keys if field in m] for k,keys in GROUPS.items()}
  manifests=[mp]
  # Supplemental family/API/collision/dependency files only; no QA or derivatives.
  supplemental=[]
  for f in sorted(mp.parent.glob('*.json')):
   if f==mp or re.search(r'AST-[A-Z]+-.*(?:manifest|collision)',f.name):continue
   if f.name in ['family_summary.json','manifest.json','dependency_manifest.json'] or any(s in f.name for s in ['api','interface','anchor','collision','recipe','texture']):
    supplemental.append(binding(f));manifests.append(f);file_bindings[str(f.relative_to(ROOT))]=binding(f)
  for f in manifests:
   jd=json.loads(f.read_text());rel=str(f.relative_to(ROOT));pair_rows+=pairs(jd,rel)
   for ptr,obj in walk(jd):
    if isinstance(obj,dict):
     for key,val in obj.items():
      if numeric3(val) and any(t in key.lower() for t in ['normal','tangent','direction','axis']):
       ll=float(np.linalg.norm(val));direction_checks.append({'pointer':rel+'#'+ptr+'/'+key,'length':ll,'pass':abs(ll-1)<1e-4})
     for pk in ['path','file','base_color_file','source','export','source_blend','runtime_glb']:
      if isinstance(obj.get(pk),str) and obj.get('sha256'):
       declared_base=f.parent/jd['texture_root'] if pk=='base_color_file' and jd.get('path_base')=='directory_containing_this_manifest' and 'texture_root' in jd else f.parent
       for pp in resolve(obj[pk],declared_base):
        if pp.is_file():dependency_hash_checks.append({'pointer':rel+'#'+ptr,'target':str(pp.relative_to(ROOT)),'expected_sha256':obj['sha256'],'actual_sha256':sha(pp),'pass':obj['sha256']==sha(pp)});break
     for key,val in obj.items():
      if isinstance(val,str) and re.fullmatch('[a-f0-9]{64}',val) and '/' in key:
       for pp in resolve(key,f.parent):
        if pp.is_file():dependency_hash_checks.append({'pointer':rel+'#'+ptr+'/'+key,'target':str(pp.relative_to(ROOT)),'expected_sha256':val,'actual_sha256':sha(pp),'pass':val==sha(pp)});break
    if isinstance(obj,str) and (re.search(r'\.(?:py|json|blend|glb|png|jpg|npz|md)$',obj,re.I) or '*' in obj or obj.endswith('/')):
     declared_base=f.parent/jd['texture_root'] if ptr.endswith('/base_color_file') and jd.get('path_base')=='directory_containing_this_manifest' and 'texture_root' in jd else f.parent
     hits=resolve(obj,declared_base)
     path_rows.append({'asset':ident,'pointer':rel+'#'+ptr,'declared':obj,'resolved_catalogue_paths':[str(q.relative_to(ROOT)) for q in hits],'status':'resolved' if hits else 'unresolved_or_external_historical','role':'reference/evidence' if any(t in ptr.lower() for t in ['reference','evidence','qa','render','inspection','consumer_local']) else 'candidate_dependency_or_file'})
  mesh_roles={x['name'][8:] if str(x['name']).startswith('ASTRAEA_') else x['name'] for x in ev['materials']}
  declared=m.get('material_roles',m.get('used_material_roles',m.get('materials')))
  if isinstance(declared,list) and all(isinstance(x,str) for x in declared):declared=[x[8:] if x.startswith('ASTRAEA_') else x for x in declared]
  restoration=[]
  # Exact existing local scripts are restoration-useful inventory, not proof
  # that every listed script is required or safe to execute.
  for f in sorted(mp.parent.rglob('*.py')):
   if any(p in f.relative_to(mp.parent).parts for p in ['qa','derived','derived_lod','__pycache__']):continue
   restoration.append(binding(f));file_bindings[str(f.relative_to(ROOT))]=binding(f)
  stat={'catalogue_id':ident,'name':a['name'],'family':a['family'],'batch':a['batch'],'files':paths,'source_matches_catalogue_hash':paths['source']['sha256']==a['source_sha256'],'export_matches_catalogue_hash':paths['export']['sha256']==a['export_sha256'],'manifest_record_pointer':a['manifest']+'#'+mptr,'exact_existing_records':groups,'supplemental_family_files':supplemental,'restoration_useful_local_scripts':restoration,'native_glb_evidence_pointer':'qa/batch08/interface_native_glb_evidence.json#/assets/'+str(len(native_rows)-1),'dimensions_max_error_m':float(np.max(np.abs(np.array(ev['dimensions_blender_xyz_m'])-a['dimensions_blender_xyz_m']))),'native_material_roles':sorted(mesh_roles),'declared_material_roles':declared,'declared_material_roles_match_native':None if declared is None else set(declared)==mesh_roles,'scope_note':'Coverage and actual-byte exchange inspection only. Existing source-frame annotations remain source-frame; static/not-applicable fields are not invented. No engine adoption.'}
  coverage.append(stat)
 pair_rows=list({(x['source'],x['exchange']):x for x in pair_rows}.values())
 dependency_hash_checks=list({(x['pointer'],x['target']):x for x in dependency_hash_checks}.values())
 direction_checks=list({x['pointer']:x for x in direction_checks}.values())
 write('interface_dependency_hash_checks.json',{'checks':dependency_hash_checks,'count':len(dependency_hash_checks),'failures':[x for x in dependency_hash_checks if not x['pass']]})
 write('interface_direction_checks.json',{'checks':direction_checks,'count':len(direction_checks),'failures':[x for x in direction_checks if not x['pass']]})
 # Separate exact GLB node evidence from coverage; do not smuggle guessed
 # motion/contact semantics into normalized authoritative records.
 write('interface_native_glb_evidence.json',{'method':'Actual native GLB byte accessors and fully composed node transforms; no Blender import or source re-export. All scene triangles read.','basis_blender_source_to_gltf_yup':C.tolist(),'assets':native_rows})
 write('interface_coverage_map.json',{'revision':'batch08-interface-audit-proposal-01','catalogue':binding(ROOT/'catalogue_manifest.json'),'unique_designs':45,'status':'read_only_audit_proposed_index_not_engine_adoption','assets':coverage})
 write('interface_path_resolution.json',{'resolution':'Try catalogue root and the containing manifest directory; never guess unresolved paths. Historical references and evidence are not presumed runtime dependencies.','records':path_rows})
 write('interface_dual_frame_checks.json',{'method':'Only matching explicit source/exchange point or direction fields; no component-wise min/max transformation. These arithmetic checks do not prove physical meaning.','manifest_and_api_checks':pair_rows})
 for f in [ROOT/'standards/COORDINATE_CONTRACT.md',ROOT/'standards/coordinate_compatibility.json',ROOT/'standards/ASSET_CONTRACT.md',ROOT/'batches/batch08/CONTRACT.md',ROOT/'qa/inspect_glb_independent.py',ROOT/'qa/batch05/independent_coordinate_report.json',ROOT/'qa/batch05/cabinet_metadata_revision/verification_report.json',OUT/'library_texture_path_revision/revision_report.json',OUT/'library_texture_path_revision/isolated_rebuild_report.json',OUT/'interface_semantics.py',Path(__file__)]:
  if f.exists():file_bindings[str(f.relative_to(ROOT))]=binding(f)
 for f in [OUT/'interface_compact_source_audit.py',OUT/'interface_compact_source_static_scan.json',OUT/'interface_compact_source_initial_scan.json',OUT/'interface_compact_source_report.md']:
  if f.exists():file_bindings[str(f.relative_to(ROOT))]=binding(f)
 for f in [OUT/'source_output_directory_revision/revision_report.json',OUT/'source_output_directory_revision/isolated_rebuild_report.json',OUT/'independent_source_restoration_scope.json',OUT/'independent_flange_restoration_report.json']:
  if f.exists():file_bindings[str(f.relative_to(ROOT))]=binding(f)
 write('interface_input_bindings.json',{'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'catalogue_baseline':binding(ROOT/'catalogue_manifest.json'),'files':list(file_bindings.values()),'source_export_scope':'Exactly 45 catalogue source .blend and 45 visual GLB files; no assembly or LOD counted as a design.'})
 summary={'unique_assets':len(coverage),'source_hashes_match':sum(x['source_matches_catalogue_hash'] for x in coverage),'export_hashes_match':sum(x['export_matches_catalogue_hash'] for x in coverage),'native_glb_nodes':sum(x['node_count'] for x in native_rows),'native_glb_triangles':sum(x['triangles'] for x in native_rows),'marker_origin_checks':sum(len(x['marker_origin_checks']) for x in native_rows),'marker_origin_failures':[{'id':x['catalogue_id'],**r} for x in native_rows for r in x['marker_origin_checks'] if not r['pass']],'surface_witnesses':sum(len(x['physical_marker_surface_witnesses']) for x in native_rows),'surface_witnesses_over_2mm':[{'id':x['catalogue_id'],**r} for x in native_rows for r in x['physical_marker_surface_witnesses'] if not r['within_2mm']],'dual_frame_checks':len(pair_rows)+sum(len(x['dual_frame_checks']) for x in native_rows),'dual_frame_failures':[r for r in pair_rows if not r['pass']]+[r for x in native_rows for r in x['dual_frame_checks'] if not r['pass']],'dimension_failures':[{'id':x['catalogue_id'],'error_m':x['dimensions_max_error_m']} for x in coverage if x['dimensions_max_error_m']>1e-5],'material_role_failures':[x['catalogue_id'] for x in coverage if x['declared_material_roles_match_native'] is False],'legacy_source_axis_prose':[{'id':x['catalogue_id'],**r} for x in native_rows for r in x['legacy_source_axis_prose']],'external_glb_uris':[{'id':x['catalogue_id'],'uris':x['external_uris']} for x in native_rows if x['external_uris']]}
 write('interface_checks_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
