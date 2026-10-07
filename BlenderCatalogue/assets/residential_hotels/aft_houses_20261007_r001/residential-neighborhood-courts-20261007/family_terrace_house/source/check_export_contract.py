from pathlib import Path
import json,hashlib,runpy,math
import numpy as np
S=Path(__file__).resolve().parents[1];O=S/'outputs/house_r001';P=json.loads((O/'PLAN.json').read_text());decode=runpy.run_path(str(S.parents[1]/'residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py'))['decode'];j,tri,markers,names=decode(O/'architecture.glb')
ids=[];expected=[];expected_triangles=0
for node in j['nodes']:
 if 'mesh'not in node:continue
 e=node['extras'];ids.extend(x['source_part_id']for x in e['source_part_ranges'])
for p in P['parts']:
 if p['kind']=='mesh':v=np.array(p['verts'],float);expected_triangles+=sum(len(f)-2 for f in p['faces'])
 else:
  a=np.array(p['a'],float);b=np.array(p['b'],float);t=(b-a)/np.linalg.norm(b-a);s=np.array([0,0,1.])if abs(t[2])<.95 else np.array([1.,0,0]);s=s-t*np.dot(s,t);s/=np.linalg.norm(s);u=np.cross(t,s);v=np.array([point+s*w+u*h for point in [a,b]for w,h in [(-p['width']/2,-p['depth']/2),(p['width']/2,-p['depth']/2),(p['width']/2,p['depth']/2),(-p['width']/2,p['depth']/2)]]);expected_triangles+=12
 expected.extend(v.tolist())
assert len(ids)==len(P['parts']) and len(set(ids))==len(P['parts']) and set(ids)=={p['name']for p in P['parts']}
assert len(tri)==expected_triangles,(len(tri),expected_triangles)
actual=np.unique(np.round(tri.reshape(-1,3),7),axis=0);expected=np.unique(np.round(np.array(expected),7),axis=0)
def screen(a,b):
 index={}
 for p in b:index.setdefault(tuple(np.round(p/.001).astype(int)),[]).append(p)
 maximum=0;unmatched=[]
 for p in a:
  key=np.round(p/.001).astype(int);found=[]
  for dx in [-1,0,1]:
   for dy in [-1,0,1]:
    for dz in [-1,0,1]:found.extend(index.get((key[0]+dx,key[1]+dy,key[2]+dz),[]))
  distance=min((float(np.abs(p-q).max())for q in found),default=1.)
  maximum=max(maximum,distance)
  if distance>.00006:unmatched.append(p.tolist())
 return maximum,unmatched
forward,missing=screen(expected,actual);back,extra=screen(actual,expected);assert not missing and not extra,(missing[:3],extra[:3])
receipt=json.loads((O/'SOURCE_RECEIPT.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(O/'house.blend')==receipt['house_blend_sha256']and sha(O/'architecture.glb')==receipt['architecture_glb_sha256']
report={'status':'PASS_EXACT_PART_ID_TRIANGLE_AND_VERTEX_EXPORT_SCREEN','source_parts':len(ids),'compact_mesh_batches':len(j['meshes']),'triangles':len(tri),'source_vertices_unique':len(expected),'GLB_vertices_unique':len(actual),'max_source_to_export_error_m':forward,'max_export_to_source_error_m':back,'embedded_external_buffer_uris':[b.get('uri')for b in j['buffers']if b.get('uri')],'embedded_external_image_uris':[b.get('uri')for b in j.get('images',[])if b.get('uri')],'source_and_export_receipt_hashes_match':True,'range_metadata_scope':'source_part_ranges indexes the editable merged mesh beforeglTFUV/normal vertex splitting; stablepart IDs are authoritative. These are not advertised as nativeGLBindex offsets.','actual_Godot_import':False,'full_house_acceptance':False}
(O/'EXPORT_CONTRACT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
