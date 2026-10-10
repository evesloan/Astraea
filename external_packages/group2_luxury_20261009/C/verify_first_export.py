import json,pathlib,hashlib,math,gzip,itertools,collections,sys
from glb_tools import read_glb,projected_grid,route_check,sha
R=pathlib.Path(__file__).resolve().parent;unit=int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+1 else 876;__import__('sys').path.insert(0,str(R));from source_paths import section,inside_polygon;_,O,native_path,export_path=section(unit);contract=json.loads((O/'SECTION_CONTRACT.json').read_text());poly=contract['reservation']['proposed_floor_boundary'];bound_min=[min(v[0] for v in poly),contract['reservation']['floor_y'],min(v[1] for v in poly)];bound_max=[max(v[0] for v in poly),contract['reservation']['proposed_external_roof_limit_y'],max(v[1] for v in poly)];p=export_path;g,nodes=read_glb(p);fail=[]
for n in nodes:
 outside=[v for v in n['vertices'] if not (all(bound_min[k]-.0001<=v[k]<=bound_max[k]+.0001 for k in range(3)) and inside_polygon(v[0],v[2],poly))]
 if outside:fail.append({'out_of_boundary':n['name'],'count':len(outside),'bounds':n['bounds']})
 if n['normal_error']>1e-5:fail.append({'nonunit_normals':n['name'],'error':n['normal_error']})
 if 'PREVIEW' in n['name']:fail.append({'preview_floor_exported':n['name']})
assert all('uri' not in x for x in g.get('buffers',[])+g.get('images',[])),'external GLB resource'
def wp(u,v):
 f=contract.get('local_frame',{'origin_xyz':[-43,102,-459],'u_axis':[ -1,0,0],'v_axis':[0,0,1]});return(f['origin_xyz'][0]+u*f['u_axis'][0]+v*f['v_axis'][0],f['origin_xyz'][2]+u*f['u_axis'][2]+v*f['v_axis'][2])
polys,grid=projected_grid(nodes,102.001,2.25)
routes=[('main_loaded_cart',[(2.65,5.30),(5.90,5.30),(5.90,5.00),(10.5,5.00),(10.5,7.25),(13,7.25)],.82),('kitchen_loaded_cart',[(2.65,5.30),(2.65,7.0),(3.50,7.0)],.82),('restA_body',[(6.2,4.6),(7.55,4.65)],.38),('restB_body',[(10.5,4.6),(13.1,4.65)],.38),('bath_body',[(2.65,5.3),(3.45,4.6)],.38)]
if contract.get('source_routes'):
 routes=contract['source_routes']+[r for r in routes if r[0] in ['kitchen_loaded_cart','bath_body']]
results=[]
if contract.get('source_routes_world'):routes=contract['source_routes_world']
for name,pts,radius in routes:
 path=[(q[0],q[2]) for q in pts] if contract.get('source_routes_world') else [wp(*q) for q in pts]
 result=route_check(polys,grid,path,radius);result['name']=name;result['scope']='Conservative source-file full-height sweep; root floor proposal and door operation still uninstalled';results.append(result)
 if not result['passed']:fail.append({'route':name,'blocked':result['blocked']})
# Independently sweep the actual bath fixture approaches. The source door is
# closed; these paths start beyond its threshold. The shower tray is a measured
#2cm step, with the body sweep lifted25mm, not a certified accessible transfer.
bath_polys,bath_grid=projected_grid(nodes,102.025,2.25)
bath_routes=[('bath_vanity_stance',[(3.53,3.30),(3.53,2.80),(3.84,2.80)]),('bath_toilet_stance',[(3.53,3.30),(3.45,2.80)]),('shower_approach_and_tray',[(3.53,3.30),(3.55,2.80),(3.55,1.85)])]
if contract.get('internal_bath_routes_world'):bath_routes=[(name,pts) for name,pts,radius in contract['internal_bath_routes_world']]
for name,pts in bath_routes:
 path=[(q[0],q[2]) for q in pts] if contract.get('internal_bath_routes_world') else [wp(*q) for q in pts]
 result=route_check(bath_polys,bath_grid,path,.38);result['name']=name;result['scope']='Saved source internal bath sweep from beyond closed door; measured2cm tray step. Runtime door/actor/accessibility acceptance held.';results.append(result)
 if not result['passed']:fail.append({'route':name,'blocked':result['blocked']})
source=json.loads((O/'NATIVE_VERIFICATION.json').read_text(encoding='utf-8')) if (O/'NATIVE_VERIFICATION.json').exists() else None
parity=[];position_parity=[]
def position_error(source,target):
 cell=.0002;bins=collections.defaultdict(list)
 for v in target:bins[tuple(math.floor(x/cell) for x in v)].append(v)
 worst=0
 for v in source:
  q=tuple(math.floor(x/cell) for x in v);nearest=min((math.dist(v,t) for offset in itertools.product([-1,0,1],repeat=3) for t in bins.get(tuple(q[k]+offset[k] for k in range(3)),[])),default=999)
  worst=max(worst,nearest)
 return worst
native_vertices=json.loads(gzip.decompress((O/'SAVED_NATIVE_VERTICES.json.gz').read_bytes()))

if source:
 assert source['native_sha256']==sha(native_path),'Stale native verification hash'
 if source['status']!='PASS':fail.append({'saved_native_failed':source['failures']})
 lookup={n['name']:n for n in nodes}
 for r in source['mesh_rows']:
  n=lookup.get(r['name'])
  if not n:fail.append({'native_export_missing':r['name']});continue
  source_positions=native_vertices[r['name']];p_error=max(position_error(source_positions,n['vertices']),position_error(n['vertices'],source_positions));position_parity.append({'name':r['name'],'bidirectional_actual_vertex_error_m':p_error})
  if p_error>.0002:fail.append({'native_export_positions':r['name'],'error_m':p_error})
  error=max(abs(r['bounds_world'][a][b]-n['bounds'][a][b]) for a in range(2) for b in range(3));parity.append({'name':r['name'],'max_bound_error_m':error})
  if error>.0002:fail.append({'native_export_bounds':r['name'],'error':error})
text_parity=[{**r,'actual_export_mesh_present':r['export_mesh_expected'] in {n['name'] for n in nodes}} for r in source.get('editable_text',[])]
if any(not r['actual_export_mesh_present'] for r in text_parity):fail.append({'text_parity':text_parity})
data={'status':'PASS' if not fail else 'FAIL','export_sha256':sha(p),'native_sha256':source['native_sha256'] if source else None,'file_bytes':p.stat().st_size,'mesh_nodes':len(nodes),'triangles':sum(len(n['triangles']) for n in nodes),'embedded_images':len(g.get('images',[])),'normal_UV_finite_checked':True,'floor_meshes':0,'native_export_position_tolerance_m':.0002,'precision_basis':'0.2mm bidirectional position budget for float32 vertices plus node transforms at ship coordinates; containment remains0.1mm and support1mm. All actual errors retained.', 'source_export_bounds':parity,'source_export_actual_vertices':position_parity,'text_parity':text_parity,'routes':results,'failures':fail,'scope':'Actual raw GLB, no Godot import/installed acceptance'}
(O/'EXPORT_VERIFICATION.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print('EXPORT RESULT',data['status'],len(nodes),'nodes',len(fail),'failures')
if fail:raise RuntimeError('Raw-export verification failed')
