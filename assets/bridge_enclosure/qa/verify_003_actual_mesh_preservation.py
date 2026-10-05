from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];P=C/'assets/bridge_platform';baseline=Path('/tmp/astraea-before-enclosure-003.blend')
allow=set(json.loads((R/'qa/prior_003_parts.json').read_text())['allowlist_assemblies'])
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':
   result[o.name]={'type':o.type,'matrix':list(v for r in o.matrix_world for v in r),'properties':{k:o[k]for k in o.keys()}};continue
  result[o.name]={'type':'MESH','matrix':list(v for r in o.matrix_world for v in r),'vertices':[list(v.co)for v in o.data.vertices],'polygons':[list(f.vertices)for f in o.data.polygons],'uv':[list(x.uv)for x in o.data.uv_layers.active.data],'materials':[m.name for m in o.data.materials],'properties':{k:o[k]for k in o.keys()}}
 return result
A=capture(baseline);B=capture(P/'source/AST-CMD-003.blend');assert A.keys()==B.keys();changed=[];same=[]
for n,a in A.items():
 b=B[n]
 if a==b:same.append(n);continue
 assert a['properties']['assembly']in allow,n
 assert all(a[k]==b[k]for k in['type','matrix','polygons','materials','properties']),n
 assert all(v[0]==w[0] and v[1]==w[1]for v,w in zip(a['vertices'],b['vertices'])),n
 changed.append({'name':n,'assembly':a['properties']['assembly'],'before_sha256':hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest(),'after_sha256':hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest(),'changes':'Only vertical vertices and correspondingly regenerated metric UVs'})
assert len(changed)==32
report={'pass':True,'baseline_source_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'revised_source_sha256':hashlib.sha256((P/'source/AST-CMD-003.blend').read_bytes()).hexdigest(),'compared_objects':len(A),'unchanged_objects':len(same),'changed_meshes':changed,'method':'Reopen both actual editable Blender sources; compare complete ordered mesh vertices, faces,UVs,materials,world transforms,custom properties and all marker objects. Only32 approved mesh pieces may differ in vertical coordinates and metric UVs.'}
(R/'qa/003_actual_mesh_preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('ACTUAL_003_PRESERVED',len(same),'changed',len(changed))
