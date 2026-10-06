"""Pure Python independent GLB equivalence, real plane contacts and ray QA.
Reads frozen Game exports only; never imports or changes the Game project.
"""
from pathlib import Path
import collections, hashlib, io, json, math, struct, sys
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
R=Path(__file__).resolve().parents[1];Q=R/'qa';P=Path('/workspace/shared/astraea-godot-production-20261003')
G=R/'exports/AST-ENG-008_west_inspection_fixture.glb'
OUT=Q/'INDEPENDENT_EXPORT_CONTACT_RAYS.json'
assert not OUT.exists(),'Preserve prior evidence'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def decode(path):
 data=Path(path).read_bytes();magic,version,size=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and size==len(data)
 cursor=12;chunks={}
 while cursor<size:
  length,kind=struct.unpack_from('<II',data,cursor);chunks[kind]=data[cursor+8:cursor+8+length];cursor+=8+length
 doc=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942];rows=[];nodes=[]
 def read(i):
  a=doc['accessors'][i];assert 'sparse' not in a;v=doc['bufferViews'][a['bufferView']]
  fmt,nbytes={5126:('f',4),5125:('I',4),5123:('H',2),5122:('h',2),5121:('B',1),5120:('b',1)}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',nbytes*width)
  return np.array([struct.unpack_from('<'+fmt*width,blob,start+j*stride) for j in range(a['count'])])
 def walk(index,parent):
  node=doc['nodes'][index]
  if 'matrix' in node:local=np.array(node['matrix']).reshape(4,4).T
  else:
   x,y,z,w=node.get('rotation',[0,0,0,1]);local=np.eye(4);local[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(node.get('scale',[1,1,1]));local[:3,3]=node.get('translation',[0,0,0])
  world=parent@local;nodes.append({'index':index,'name':node.get('name',''),'mesh':node.get('mesh'),'world':world.tolist(),'extras':node.get('extras',{})})
  if 'mesh' in node:
   for pr in doc['meshes'][node['mesh']]['primitives']:
    assert pr.get('mode',4)==4;v=read(pr['attributes']['POSITION']);v=(np.c_[v,np.ones(len(v))]@world.T)[:,:3];ids=read(pr['indices']).astype(int).reshape(-1,3);mat=doc['materials'][pr['material']]
    rows.append({'node':node.get('name',''),'material':mat['name'],'triangles':v[ids],'uv':read(pr['attributes']['TEXCOORD_0'])[ids] if 'TEXCOORD_0' in pr['attributes'] else None,'file':str(path),'collision':node.get('extras',{}).get('collision_contract'),'alpha_mode':mat.get('alphaMode','OPAQUE')})
  for child in node.get('children',[]):walk(child,world)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return {'doc':doc,'blob':blob,'rows':rows,'nodes':nodes}
def image_bytes(glb,index):
 im=glb['doc']['images'][index];v=glb['doc']['bufferViews'][im['bufferView']];start=v.get('byteOffset',0);return glb['blob'][start:start+v['byteLength']]
source=np.load(Q/'reopened_source.npz',allow_pickle=False);st=source['triangles'];su=source['uv'];sm=source['materials'];so=source['objects'];g=decode(G)
assert len(g['nodes'])==5 and len([n for n in g['nodes'] if n['mesh'] is not None])==4
assert {n['name'] for n in g['nodes']}=={'WEST_mount','WEST_housing','WEST_opal','WEST_CapStem','DATUM_plant_west_front'}
assert not g['doc'].get('extensions',{}).get('KHR_lights_punctual')
et=np.concatenate([r['triangles'] for r in g['rows']]);eu=np.concatenate([r['uv'] for r in g['rows']]);em=np.array([r['material'] for r in g['rows'] for _ in r['triangles']]);eo=np.array([r['node'] for r in g['rows'] for _ in r['triangles']])
points,si=np.unique(st.reshape(-1,3),axis=0,return_inverse=True);tree=cKDTree(points);errors,ei=tree.query(et.reshape(-1,3),workers=1);back=cKDTree(et.reshape(-1,3)).query(points,workers=1)[0]
def canonical(ids,uv):
 rotations=[tuple(np.roll(ids,-i)) for i in range(3)];i=min(range(3),key=lambda j:rotations[j]);return rotations[i],np.roll(uv,-i,axis=0)
def keyed(ids,uv,objects,mats):
 out=collections.defaultdict(list)
 for x,u,o,m in zip(ids.reshape(-1,3),uv,objects,mats):
  key,value=canonical(x,u);out[(str(o),str(m),*key)].append(value)
 return out
sk=keyed(si,su,so,sm);ek=keyed(ei,eu,eo,em);missing=[];extra=[];uv_errors=[]
for key in set(sk)|set(ek):
 a=list(sk.get(key,[]));b=list(ek.get(key,[]))
 if len(a)>len(b):missing.extend([key]*(len(a)-len(b)))
 if len(b)>len(a):extra.extend([key]*(len(b)-len(a)))
 # These simple parts have unique oriented triangles; enforce rather than hide ambiguity.
 assert len(a)<=1 and len(b)<=1
 if a and b:uv_errors.append(float(np.max(np.abs(a[0]-b[0]))))
equivalence={'source_triangles':len(st),'export_triangles':len(et),'maximum_export_to_source_vertex_error_m':float(errors.max()),'maximum_source_to_export_vertex_error_m':float(back.max()),'oriented_object_material_triangles_missing':len(missing),'oriented_object_material_triangles_extra':len(extra),'maximum_loop_uv_error':max(uv_errors),'passed':bool(len(st)==len(et) and errors.max()<1e-4 and back.max()<1e-4 and not missing and not extra and max(uv_errors)<1e-4)}
source_mats=json.loads((Q/'SOURCE_MATERIALS.json').read_text());material_checks=[]
for m in g['doc']['materials']:
 s=source_mats[m['name']];pbr=m.get('pbrMetallicRoughness',{});ti=pbr['baseColorTexture'];tex=g['doc']['textures'][ti['index']];raw=image_bytes(g,tex['source']);source_raw=Path(s['base_color_texture']).read_bytes();im1=Image.open(io.BytesIO(raw)).convert('RGBA');im2=Image.open(io.BytesIO(source_raw)).convert('RGBA');pixels=bool(im1.size==im2.size and np.array_equal(np.array(im1),np.array(im2)));rerr=abs(pbr.get('roughnessFactor',1)-s['roughness']);merr=abs(pbr.get('metallicFactor',1)-s['metallic']);sampler=g['doc'].get('samplers',[{}])[tex.get('sampler',0)];factor=pbr.get('baseColorFactor',[1,1,1,1]);repeat=all(sampler.get(x,10497)==10497 for x in ['wrapS','wrapT'])
 material_checks.append({'material':m['name'],'texture_exact_bytes':raw==source_raw,'texture_identical_rgba_pixels':pixels,'roughness_error':rerr,'metallic_error':merr,'base_color_factor':factor,'alpha_mode':m.get('alphaMode','OPAQUE'),'uv_set':ti.get('texCoord',0),'repeat_wrap':repeat,'passed':pixels and rerr<1e-7 and merr<1e-7 and factor==[1,1,1,1] and ti.get('texCoord',0)==0 and repeat and m.get('alphaMode','OPAQUE')=='OPAQUE'})
marker=next(n for n in g['nodes'] if n['name']=='DATUM_plant_west_front');mark=np.array(marker['world'])[:3,3];emit=mark+[0,marker['extras']['emitter_offset_y_m'],0];marker_ok=np.max(np.abs(mark-[25.55,9.5,-432]))<2e-5 and np.max(np.abs(emit-[25.55,9.42,-432]))<2e-5 and marker['extras']['energy_approved'] is False
# Every installed AST-ENG-008 geometry export in frozen Game is read without imports.
retained_paths=sorted((P/'assets/models').glob('AST-ENG-008*.glb'));pins=json.loads((R/'INPUT_PINS.json').read_text());assert all(sha(p)==h for p,h in pins.items());retained_pins={str(p):sha(p) for p in retained_paths}
retained=[]
for p in retained_paths:retained+=decode(p)['rows']
all_rows=retained+g['rows'];all_tri=np.concatenate([r['triangles'] for r in all_rows]);owner=np.concatenate([np.full(len(r['triangles']),i) for i,r in enumerate(all_rows)]);e1=all_tri[:,1]-all_tri[:,0];e2=all_tri[:,2]-all_tri[:,0]
def ray(start,end):
 a=np.array(start,dtype=float);d=np.array(end,dtype=float)-a;length=np.linalg.norm(d);d/=length;h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);valid=abs(det)>1e-10;inv=np.zeros(len(det));inv[valid]=1/det[valid];q=a-all_tri[:,0];u=np.einsum('ij,ij->i',q,h)*inv;k=np.cross(q,e1);v=k@d*inv;t=np.einsum('ij,ij->i',e2,k)*inv;mask=valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-5)&(t<length+1e-4);ids=np.flatnonzero(mask);ids=ids[np.argsort(t[ids])]
 if not len(ids):return None
 i=int(ids[0]);row=all_rows[int(owner[i])];return {'node':row['node'],'file':row['file'],'distance_m':float(t[i]),'point_xyz':(a+t[i]*d).tolist()}
# Real source face area overlaps on the horizontal bearing planes.
def area(poly):
 p=np.array(poly);return 0.0 if len(p)<3 else abs(float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))))*.5
def clip(poly,edge_a,edge_b):
 result=[];p=list(poly)
 def side(v):return (edge_b[0]-edge_a[0])*(v[1]-edge_a[1])-(edge_b[1]-edge_a[1])*(v[0]-edge_a[0])
 for a,b in zip(p,p[1:]+p[:1]):
  sa,sb=side(a),side(b);ia,ib=sa>=-1e-10,sb>=-1e-10
  if ia:result.append(a)
  if ia!=ib:result.append(np.array(a)+(np.array(b)-a)*(sa/(sa-sb)))
 return result
def intersection_area(a,b):
 b=np.array(b);signed=float(np.sum(b[:,0]*np.roll(b[:,1],-1)-b[:,1]*np.roll(b[:,0],-1)))
 if signed<0:b=b[::-1]
 p=list(a)
 for v,w in zip(b,np.roll(b,-1,axis=0)):
  p=clip(p,v,w)
  if len(p)<3:return 0.0
 return area(p)
def triangles_for(node,rows):return np.concatenate([r['triangles'] for r in rows if r['node']==node])
def plane_faces(tris,y):return [t[:,[0,2]] for t in tris if np.max(np.abs(t[:,1]-y))<2e-5]
contacts=[]
for low,high in [('WEST_opal','WEST_housing'),('WEST_housing','WEST_mount'),('WEST_mount','WEST_CapStem'),('WEST_CapStem','containment_cap')]:
 lt=triangles_for(low,g['rows']);ht=triangles_for(high,retained if high=='containment_cap' else g['rows']);y0=float(lt[:,:,1].max());y1=float(ht[:,:,1].min());lf=plane_faces(lt,y0);hf=plane_faces(ht,y1);la=sum(area(t) for t in lf);ha=sum(area(t) for t in hf);bearing=sum(intersection_area(a,b) for a in lf for b in hf);expected=min(la,ha)
 contacts.append({'lower':low,'upper':high,'lower_top_y':y0,'upper_bottom_y':y1,'vertical_gap_m':y1-y0,'lower_horizontal_area_m2':la,'upper_horizontal_area_m2':ha,'actual_face_overlap_area_m2':bearing,'minimum_surface_fully_supported':abs(bearing-expected)<max(1e-6,expected*1e-5),'passed':abs(y1-y0)<2e-5 and bearing>1e-6 and abs(bearing-expected)<max(1e-6,expected*1e-5)})
# A strict-interior triangle/box clip: actual retained surfaces against each
# candidate's conservative enclosing volume; tangent authored contacts excluded.
def triangle_in_box(triangle,bounds):
 p=[np.array(v) for v in triangle]
 for axis,edge,sign in [(0,bounds[0],1),(0,bounds[3],-1),(1,bounds[1],1),(1,bounds[4],-1),(2,bounds[2],1),(2,bounds[5],-1)]:
  out=[]
  for a,b in zip(p,p[1:]+p[:1]):
   sa=sign*(a[axis]-edge);sb=sign*(b[axis]-edge);ia=sa>1e-6;ib=sb>1e-6
   if ia:out.append(a)
   if ia!=ib:out.append(a+(b-a)*((edge-a[axis])/(b[axis]-a[axis])))
  p=out
  if len(p)<3:return False
 return True
intrusions=[]
for row in g['rows']:
 t=row['triangles'];b=np.r_[t.min((0,1)),t.max((0,1))];hits=[]
 for retained_row in retained:
  rt=retained_row['triangles'];mask=np.all(np.minimum(rt.max(1),b[3:])-np.maximum(rt.min(1),b[:3])>1e-6,axis=1);count=sum(triangle_in_box(t,b) for t in rt[mask])
  if count:hits.append({'file':retained_row['file'],'node':retained_row['node'],'triangles':int(count)})
 intrusions.append({'candidate':row['node'],'conservative_bounds_xyz':b.tolist(),'retained_triangle_intrusions':hits,'passed':not hits})
# Actual reloaded source marker and actual exported fixture included in all rays.
aim=np.array([26.22,8.05,-432]);axis=aim-emit;axis/=np.linalg.norm(axis);samples=[]
for rad in [0,.2,.4,.59]:
 count=1 if rad==0 else 16
 for i in range(count):
  angle=2*math.pi*i/count;target=np.array([26.22,8.05+rad*math.cos(angle),-432+rad*math.sin(angle)]);delta=target-emit;distance=float(np.linalg.norm(delta));direction=delta/distance;cone=math.degrees(math.acos(float(np.clip(direction@axis,-1,1))));hit=ray(emit,target+direction*.01);ok=hit is not None and hit['node']=='machine_profiled_end_-1' and abs(hit['distance_m']-distance)<1e-4 and distance<4 and cone<32
  samples.append({'radius_m':rad,'target_xyz':target.tolist(),'distance_m':distance,'cone_offset_degrees':cone,'first_hit':hit,'passed':ok})
central_exit=ray(emit,emit+axis*.1)
# Verify all read pins again before final evidence.
assert retained_pins=={str(p):sha(p) for p in retained_paths};assert all(sha(p)==h for p,h in pins.items())
report={'status':'PASS' if equivalence['passed'] and all(x['passed'] for x in material_checks+contacts+intrusions+samples) and marker_ok and central_exit is None else 'FAIL','scope':'Saved-source/export equivalence; actual authored bearing-plane contacts; actual retained-surface conservative-volume screening and geometric source rays. No Game run, import, image, energy, ranking or adoption.','source_sha256':str(source['source_sha256']),'export_sha256':sha(G),'equivalence':equivalence,'materials':material_checks,'marker':{'xyz':mark.tolist(),'emitter_xyz':emit.tolist(),'passed':bool(marker_ok)},'contacts':contacts,'retained_triangle_volume_screen':intrusions,'retained_geometry_inputs':retained_pins,'retained_geometry_triangles':sum(len(r['triangles']) for r in retained),'central_emitter_exit_10cm_first_hit':central_exit,'receiver_samples':samples,'receiver_pass_count':sum(x['passed'] for x in samples),'all_read_inputs_unchanged':True,'limitations':['49 geometric rays sample the physical radius 0.65 m central disc only to radius 0.59 m; they do not cover the radius 1.73 m profiled endcap.','Triangle contact and no-intrusion tests are geometric QA, not mechanical structural certification or volumetric signed-solid containment proof.','Visible focal machinery, retained panes, ordinary guest viewpoints, motion, glare, full profiled silhouette and seated-eye composition still need actual-image review.','Native source admission under unchanged eight-active / 32-candidate selection, energy, source registry adoption and whole first-pass acceptance remain unapproved.']}
OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','equivalence','contacts','receiver_pass_count','central_emitter_exit_10cm_first_hit']},indent=2));assert report['status']=='PASS'
