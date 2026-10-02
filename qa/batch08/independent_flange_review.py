"""Independent actual-export flange cost, interface, profile and provenance audit."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch08';BASE=ROOT/'assets/utility_pipework/derived_lod'
sys.path.insert(0,str(ROOT/'qa/batch07'))
from independent_geometry import Native,C
from independent_collision_geometry import nearest_distances,sample_triangles,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=['utility_flange_economical','utility_flange_exact_profile_baseline','utility_flange_near_comparison','utility_flange_repeated_context'];assets={n:Native(BASE/'exports'/f'{n}.glb') for n in names}
old=Native(ROOT/'assets/utility_pipework/exports/AST-ENG-004.glb');near=assets['utility_flange_near_comparison'];econ=assets['utility_flange_economical'];exact=assets['utility_flange_exact_profile_baseline']
# Independent original inlet extraction binding. Exact triangle positions and roles must match.
t=old.tris;mask=((t[:,:,0]>=-1e-7)&(t[:,:,0]<=.0950001)).all(axis=1)&~(np.abs(t[:,:,0]-.085)<1e-7).all(axis=1)
def rows(tris,materials):
 out=[]
 for tri,mat in zip(tris,materials):
  v=sorted(tuple(float(x) for x in p) for p in tri);out.append((str(mat),tuple(v)))
 return sorted(out)
original_equal=rows(old.tris[mask],old.materials[mask])==rows(near.tris,near.materials)
reports=[]
for name,g in assets.items():
 r=g.g.inspect();used={str(m) for m in g.materials};matmap={m['name']:m for m in g.g.doc['materials']};oldmap={m['name']:m for m in old.g.doc['materials']}
 def material_signature(glb,mat):
  sig=json.loads(json.dumps(mat));p=sig.get('pbrMetallicRoughness',{});texture=p.get('baseColorTexture')
  if texture:
   im=glb.doc['images'][glb.doc['textures'][texture['index']]['source']];v=glb.doc['bufferViews'][im['bufferView']];texture['index']='image_sha256:'+hashlib.sha256(glb.bin[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]).hexdigest()
  return sig
 materials={m:material_signature(g.g,matmap[m])==material_signature(old.g,oldmap[m]) for m in used}
 markers=[]
 for i,n in enumerate(g.g.doc['nodes']):
  if not n.get('name','').startswith('PORT_'):continue
  e=n['extras'];p=np.asarray(e['position_blender_source_m']);q=np.asarray(e['position_gltf_yup_m']);nn=np.asarray(e['normal_gltf_yup']);rr=np.asarray(e['radial_zero_gltf_yup']);bp=json.loads(e['bolt_centres_blender_source_m_json']);bq=json.loads(e['bolt_centres_gltf_yup_m_json'])
  markers.append({'name':n['name'],'actual_node_position_m':g.world[i][:3,3].tolist(),'actual_node_origin_error_m':float(np.linalg.norm(g.world[i][:3,3]-q)),'source_exchange_position_error_m':float(np.linalg.norm(C@p-q)),'normal_error':float(np.linalg.norm(C@e['normal_blender_source']-nn)),'radial_error':float(np.linalg.norm(C@e['radial_zero_blender_source']-rr)),'bolt_positions_error_m':float(np.max(np.abs(np.asarray(bp)@C.T-bq))),'orthogonal_normal_radial_error':abs(float(nn@rr)),'kind':'pose/opening datum at bare mating-face centre, not solid surface contact','wrong_frame_radial_error':float(np.linalg.norm(np.asarray(e['radial_zero_blender_source'])-rr))})
 # Count actual referenced geometry bufferView payload, excluding images and unrelated preserved records.
 accessors=set()
 for node in g.g.doc['nodes']:
  if 'mesh' not in node:continue
  for p in g.g.doc['meshes'][node['mesh']]['primitives']:
   accessors.update(p['attributes'].values());accessors.add(p['indices'])
 views={g.g.doc['accessors'][a]['bufferView'] for a in accessors}
 geom_bytes=sum(g.g.doc['bufferViews'][v]['byteLength'] for v in views)
 reports.append({'name':name,'path':str(g.path.relative_to(ROOT)),'sha256':sha(g.path),'triangles':len(g.tris),'glb_bytes':len(g.g.data),'referenced_geometry_buffer_bytes':geom_bytes,'used_materials':sorted(used),'used_material_count':len(used),'serialized_material_count':len(g.g.doc['materials']),'serialized_image_count':len(g.g.doc['images']),'used_materials_exactly_match_original':materials,'structural_issues':r['issues'],'markers':markers})
profiles=[];checks=[]
for name,g in [(n,assets[n]) for n in names[:3]]:
 verts=np.unique(np.round(g.tris.reshape(-1,3),8),axis=0);front=verts[abs(verts[:,0])<1e-7];radius=np.linalg.norm(front[:,1:],axis=1)
 outer=front[abs(radius-.16)<1e-6];bore=front[abs(radius-.08)<1e-6];holes=[]
 for i in range(6):
  ang=2*np.pi*i/6;c=np.array([0,.13*np.cos(ang),-.13*np.sin(ang)]);h=front[np.linalg.norm(front-c,axis=1)<.02];hr=np.linalg.norm(h-c,axis=1)
  holes.append({'index':i,'nominal_center_gltf_m':c.tolist(),'vertices':len(h),'radius_range_m':[float(hr.min()),float(hr.max())]})
 profiles.append({'name':name,'outer_front_vertices':outer.tolist(),'bore_front_vertices':bore.tolist(),'hole_profiles':holes})
 for angle in np.linspace(0,2*np.pi,97,endpoint=False):
  for radius,expect in [(.0,False),(.079,False),(.105,True),(.155,True),(.162,False)]:
   p=np.array([-.01,radius*np.cos(angle),radius*np.sin(angle)]);q=p.copy();q[0]=.099
   hit=bool(segment_triangles(p,q,g.tris));checks.append({'name':name,'type':'bore_annulus_control','angle':float(angle),'radius_m':radius,'expected_blocked':expect,'actual_blocked':hit,'pass':hit==expect})
 for i in range(6):
  ang=2*np.pi*i/6;c=np.array([0,.13*np.cos(ang),-.13*np.sin(ang)])
  for a in np.linspace(0,2*np.pi,25,endpoint=False):
   p=c+np.array([-.001,.0085*np.cos(a),.0085*np.sin(a)]);q=p.copy();q[0]=.005
   hit=bool(segment_triangles(p,q,g.tris));checks.append({'name':name,'type':'front_hole_throat_clear','hole':i,'angle':float(a),'expected_blocked':False,'actual_blocked':hit,'pass':not hit})
 # Captive shank intentionally occupies deeper hole centre, unlike front throat.
 for i in range(6):
  ang=2*np.pi*i/6;c=np.array([0,.13*np.cos(ang),-.13*np.sin(ang)]);p=c.copy();p[0]=.005;q=c.copy();q[0]=.055
  hit=bool(segment_triangles(p,q,g.tris));checks.append({'name':name,'type':'captive_shank_blocked_control','hole':i,'expected_blocked':True,'actual_blocked':hit,'pass':hit})
# Bidirectional sampled actual-surface differences include triangle interiors.
surface=[]
for name,g in [('economical',econ),('exact_hole_option',exact)]:
 for direction,a,b in [('derived_to_original',g,near),('original_to_derived',near,g)]:
  pts,step=sample_triangles(a.tris,.009);d=nearest_distances(pts,b.tris);k=int(np.argmax(d));surface.append({'variant':name,'direction':direction,'samples':len(pts),'maximum_grid_edge_m':step,'sampled_max_surface_distance_m':float(d[k]),'p95_surface_distance_m':float(np.percentile(d,95)),'worst_gltf_point_m':pts[k].tolist()})
front_same={}
for field in ['outer_front_vertices','bore_front_vertices']:
 a=np.asarray(profiles[0][field]);b=np.asarray(profiles[2][field]);front_same[field]=float(max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max()))
result={'original_inlet_extraction_exact_actual_triangles_and_materials':original_equal,'exports':reports,'profiles':profiles,'original_economical_outer_and_bore_front_vertex_hausdorff_m':front_same,'geometry_controls':checks,'surface_comparison':surface,'pass':original_equal and all(not r['structural_issues'] and all(r['used_materials_exactly_match_original'].values()) and all(max(m[k] for k in ['actual_node_origin_error_m','source_exchange_position_error_m','normal_error','radial_error','bolt_positions_error_m','orthogonal_normal_radial_error'])<1e-6 for m in r['markers']) for r in reports) and max(front_same.values())<1e-7 and all(c['pass'] for c in checks),'limits':['Finite actual-geometry/profile and surface samples are bounded component evidence, not mechanical mating/flow/pressure/engine/LOD transition/runtime certification.','The 1320-triangle option changes hole faceting and omits rear easing, coarsens neck/shanks; source dimensions and bore/outer front loops remain. Original near geometry stays unchanged.','Near comparison keeps all four original serialized materials/images while using two. GLB file-size reduction includes removal of unused payload; referenced geometry bytes are separately measured.','No new unique artistic designs are counted.']}
(OUT/'independent_flange_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'pass':result['pass'],'controls':len(checks),'failures':[x for x in checks if not x['pass']][:10],'front_error':front_same,'surface':surface,'costs':[{'name':r['name'],'triangles':r['triangles'],'geometry_bytes':r['referenced_geometry_buffer_bytes']}for r in reports]},indent=2))
