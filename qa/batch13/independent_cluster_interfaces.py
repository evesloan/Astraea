"""Actual botanical source/native surfaces, complete joins and bounded cost review."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.spatial import cKDTree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';BASE=ROOT/'assets/botanical_cluster'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles,sample_triangles
sys.path.insert(0,str(OUT));from independent_contact_graph import contact_graph,normal_witness
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
rows=[]
for mp in sorted(BASE.glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=BASE/m['source'];gp=BASE/m['export'];rp=OUT/f'independent_source_{ident}.json';s=json.loads(rp.read_text());assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256'];so={o['name']:o for o in s['objects']};a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];roles=a['material_names'];native=Native(gp);nt=native.tris@C;nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)};part={name:tri[labels==name]for name in np.unique(labels)}
 markers=[]
 for mr in m['physical_and_proposal_markers']:
  p=np.asarray(mr['source_m']);name=mr['name'];i=ni.get(name);world=native.world[i][:3,3]if i is not None else np.zeros(3);target=mr['physical_part'];r={'name':name,'kind':mr['kind'],'physical_target':target,'native_marker_present':i is not None,'source_marker_error_m':float(np.linalg.norm(np.asarray(so[name]['matrix_world'])[:3,3]-p)),'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'wrong_axis_interpretation_error_m':float(np.linalg.norm(world-p))}
  if target:
   n=np.asarray(mr['normal_source']);native_part=ident+'__'+target if ident+'__'+target in ni else target;native_mask=(native.nodes==native_part)if native_part in ni else native.materials==so[target]['materials'][0]
   r.update(distance_to_named_source_surface_m=float(nearest_distances([p],part[target])[0]),distance_to_native_surface_m=float(nearest_distances([C@p],native.tris[native_mask])[0]),source_outward_normal_witness=normal_witness(p,part[target],n),native_outward_normal_witness=normal_witness(C@p,native.tris[native_mask],C@n),direction_conversion_error=float(np.linalg.norm(C@n-mr['normal_gltf'])))
   r['physical_surface_verified']=max(r['distance_to_named_source_surface_m'],r['distance_to_native_surface_m'])<.0002 and r['source_outward_normal_witness']['pass']and r['native_outward_normal_witness']['pass']
  r['pass']=i is not None and max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'],r.get('direction_conversion_error',0))<1e-6 and r.get('physical_surface_verified',True);markers.append(r)
 joins=[]
 for j in m['joins']:
  p=np.asarray(j['probe_source_m']);checks=[]
  for partname in j['parts']:
   t=part[partname];ds=float(nearest_distances([p],t)[0]);open_leaf=so[partname]['properties'].get('surface_kind')=='open_folded_surface';ins=False if open_leaf else bool(inside_mesh([p],t)[0]);nname=ident+'__'+partname if ident+'__'+partname in ni else partname;gn=native.tris[(native.nodes==nname)if nname in ni else native.materials==so[partname]['materials'][0]]@C;dn=float(nearest_distances([p],gn)[0]);ign=False if open_leaf else bool(inside_mesh([p],gn)[0]);checks.append({'part':partname,'distance_source_m':ds,'inside_source_closed_support':ins,'distance_native_m':dn,'inside_native_closed_support':ign,'pass':(ds<.0002 or ins)and(dn<.0002 or ign)})
  joins.append({'name':j['name'],'source_probe_m':p.tolist(),'checks':checks,'pass':all(x['pass']for x in checks)})
 graph=contact_graph(tri,labels,m.get('root_graph_parts')or[m['root_graph_part']]);equiv=[]
 for name,t in part.items():
  nname=ident+'__'+name if ident+'__'+name in ni else name;named=nname in ni;v=t.reshape(-1,3);wtri=(native.tris[(native.nodes==nname)if named else native.materials==so[name]['materials'][0]]@C);w=wtri.reshape(-1,3);err=float(max(cKDTree(v).query(w)[0].max(),cKDTree(w).query(v)[0].max()))if named and len(w)else float(nearest_distances(np.concatenate([v,t.mean(1)]),wtri).max())if len(w)else 1e9;equiv.append({'part':str(name),'native_scope':'exact_named_part'if named else'same_material_role_consolidation','source_native_geometry_error_m':err,'method':'Symmetric vertex Hausdorff for named parts; all source vertices and triangle centroids to actual role surfaces for consolidated copies; complete bidirectional material geometry checked by export report','pass':err<1e-6})
 cp=BASE/m['collision_proposal_file'];col=json.loads(cp.read_text())[ident];hulls=[Hull(x['points_source_m'],x)for x in col['shapes']];frame=max([float(np.max(np.abs(np.array(x['points_source_m'])@C.T-x['points_gltf_m'])))for x in col['shapes']]+[0]);profiles=[]
 for h in hulls:
  covered=h.record.get('covered_parts',[]);actual=np.concatenate([part[x]for x in covered]);samples,step=sample_triangles(h.tris,.04);inside=np.zeros(len(samples),bool)
  for name in covered:inside|=inside_mesh(samples,part[name])
  external=samples[~inside];infl=float(nearest_distances(external,actual).max())if len(external)else 0;profiles.append({'name':h.record['name'],'covered_parts':covered,'sample_count':len(samples),'max_sample_grid_edge_m':step,'sampled_max_external_inflation_m':infl})
 material=[{'name':x.get('name'),'alphaMode':x.get('alphaMode','OPAQUE'),'doubleSided':x.get('doubleSided',False)}for x in native.g.doc['materials']]
 foliage_mask=np.array([so[x]['properties'].get('surface_kind')=='open_folded_surface' for x in labels]);foliage=tri[foliage_mask].reshape(-1,3);bounds={'min_m':foliage.min(0).tolist(),'max_m':foliage.max(0).tolist()}
 cost={'triangles':len(tri),'mesh_nodes':sum('mesh'in n for n in nodes),'primitives':sum(len(mesh['primitives'])for mesh in native.g.doc['meshes']),'materials':len(material),'double_sided_materials':sum(x['doubleSided']for x in material),'double_sided_triangle_count':sum(len(native.g.accessor(p['indices']).ravel())//3 for mesh in native.g.doc['meshes']for p in mesh['primitives']if material[p['material']]['doubleSided']),'alpha_materials':sum(x['alphaMode']!='OPAQUE'for x in material),'native_animations':len(native.g.doc.get('animations',[])),'native_skins':len(native.g.doc.get('skins',[])),'glb_bytes':gp.stat().st_size}
 r={'catalogue_id':ident,'bindings':{k:bind(p)for k,p in [('source',sp),('export',gp),('manifest',mp),('collision',cp),('source_audit',rp)]},'markers':markers,'all_declared_joins':joins,'all_part_contact_graph':graph,'named_native_geometry_equivalence':equiv,'actual_foliage_bounds_source_m':bounds,'lowest_foliage_z_m':float(foliage[:,2].min()),'material_cost':cost,'materials':material,'collision_shape_count':len(hulls),'collision_frame_error_m':frame,'collision_profile_samples':profiles,'sampled_max_external_inflation_m':max(x['sampled_max_external_inflation_m']for x in profiles),'pass':all(x['pass']for x in markers+joins+equiv)and graph['passed']and frame<1e-6 and cost['alpha_materials']==0,'limits':['Sampled hull external inflation is not a certified continuous maximum.','Fine foliage/petals are intentionally open opaque two-sided surfaces and noncolliding; no wind or engine adoption.','Part connectivity and declared joins are independently checked against triangles, not accepted from metadata alone.','Below-soil roots are not modelled; spatial reservations cannot establish long-term plant viability.']}
 rows.append(r);print(ident,'pass',r['pass'],'failed markers',[x['name']for x in markers if not x['pass']],'failed joins',[x['name']for x in joins if not x['pass']],'isolated',graph['isolated_parts'],'cost',cost,flush=True)
(OUT/'independent_botanical_cluster_interfaces.json').write_text(json.dumps({'passed':all(x['pass']for x in rows),'assets':rows,'executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
