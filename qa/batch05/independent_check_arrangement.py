"""Read final saved inspection arrangement; no render/save or game claims."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';p=OUT/'arrangement/inspection_fixture.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
e=json.loads((OUT/'arrangement/evidence.json').read_text());names=[x['name'] for x in e['imports']];groups={n:[] for n in names};fixtures=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 n=o
 while n.parent:n=n.parent
 if n.name in groups:groups[n.name].append(o)
 elif o.name.startswith('QA ONLY'):fixtures.append(o)
def geo(obs):
 vs=[];fs=[]
 for o in obs:
  m=o.data;m.calc_loop_triangles();ix=len(vs);vs.extend(o.matrix_world@v.co for v in m.vertices);fs.extend(tuple(i+ix for i in t.vertices) for t in m.loop_triangles)
 return vs,fs,BVHTree.FromPolygons(vs,fs,all_triangles=True)
fixture=geo(fixtures)[2];r={'arrangement_sha256':before,'scope':'Final saved Blender inspection fixture read independently. Fixtures are not game geometry. Finite geometry samples and conservative clear bounds are not navigation, safety, fluid or physics validation.','groups':[],'import_hashes_match':[]}
geos={}
for name,obs in groups.items():
 vs,fs,b=geo(obs);geos[name]=(vs,fs,b);row=next(x for x in e['imports'] if x['name']==name);r['import_hashes_match'].append({'name':name,'file':row['file'],'matches':hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()==row['sha256']});r['groups'].append({'name':name,'mesh_parts':len(obs),'triangles':len(fs),'min_m':[min(v[k] for v in vs) for k in range(3)],'max_m':[max(v[k] for v in vs) for k in range(3)]})
b=geos['Entry'][2];r['entry_level_rays']=[]
for y,z in [(-.3,0),(.16,-.18),(.48,-.36),(.8,-.54),(1.25,-.72)]:
 co,n,idx,d=b.ray_cast(Vector((0,y,1.2)),Vector((0,0,-1)),3);r['entry_level_rays'].append({'source_y_m':y,'expected_z_m':z,'actual_point_m':list(co) if co else None,'pass':bool(co and abs(co.z-z)<1e-5)})
r['entry_center_route_ray_clear']=b.ray_cast(Vector((0,-.4,.6)),Vector((0,1,0)),1.9)[0] is None
rail=b.ray_cast(Vector((0,-.35,.9)),Vector((1,0,0)),1)[0];r['positive_rail_control_point_m']=list(rail) if rail else None
r['floor_geometry_samples']=[]
for name,target in [('Lounger',0),('Table',0),('Float on lower display',-.72)]:
 vs,_,b=geos[name];v=min(vs,key=lambda p:p.z);h=fixture.ray_cast(v+Vector((0,0,.001)),Vector((0,0,-1)),2)[0];r['floor_geometry_samples'].append({'asset':name,'actual_lowest_mesh_vertex_m':list(v),'fixture_downward_hit_m':list(h) if h else None,'intended_fixture_z_m':target,'pass':bool(h and abs(v.z-target)<1e-6 and abs(h.z-v.z)<1e-6)})
r['host_pad_support_samples']=[]
for pad in e['host_pad_contacts']:
 x=(pad['min_xy_m'][0]+pad['max_xy_m'][0])/2;y=(pad['min_xy_m'][1]+pad['max_xy_m'][1])/2;z=pad['receiving_z_m'];h=fixture.ray_cast(Vector((x,y,z+.001)),Vector((0,0,-1)),2)[0];r['host_pad_support_samples'].append({'asset':pad['asset'],'pad':pad['pad'],'receiving_z_m':z,'actual_fixture_z_m':h.z if h else None,'pass':bool(h and abs(h.z-z)<1e-6)})
strip={'min':[-1.42,-2.6,.03],'max':[-.70,-1.8,1.9]};r['opposite_lounger_transfer_bounds_m']=strip;r['unrelated_components_in_transfer_bounds']=[]
for row in r['groups']:
 if row['name']=='Lounger':continue
 overlap=[min(row['max_m'][i],strip['max'][i])-max(row['min_m'][i],strip['min'][i]) for i in range(3)]
 if all(x>0 for x in overlap):r['unrelated_components_in_transfer_bounds'].append(row['name'])
r['read_only_hash_unchanged']=before==hashlib.sha256(p.read_bytes()).hexdigest();r['pass']=all(x['matches'] for x in r['import_hashes_match']) and all(x['pass'] for x in r['entry_level_rays']+r['floor_geometry_samples']+r['host_pad_support_samples']) and r['entry_center_route_ray_clear'] and bool(rail) and not r['unrelated_components_in_transfer_bounds'] and r['read_only_hash_unchanged']
(OUT/'independent_composition_geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'entry_clear':r['entry_center_route_ray_clear'],'rail_control':r['positive_rail_control_point_m'],'support_samples':r['floor_geometry_samples'],'host_pad_failures':[x for x in r['host_pad_support_samples'] if not x['pass']],'transfer_obstructions':r['unrelated_components_in_transfer_bounds']},indent=2))
