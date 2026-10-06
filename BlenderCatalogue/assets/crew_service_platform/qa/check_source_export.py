"""Non-engine GLB/source-plan and exact retained-work preservation QA."""
from pathlib import Path
import json,struct,hashlib,subprocess,math
import numpy as np
R=Path(__file__).resolve().parents[1];C=R.parents[1];BASE='83a9c871e50089063641d6c347b757411da88b18';glb=R/'exports/AST-STF-010.glb'
staff_manifest=json.loads((C/'materials/staff/manifest.json').read_text())
parts=json.loads((R/'source/geometry_parts.json').read_text());expected={p['name']:p for p in parts};contract=json.loads((R/'source/section_contract.json').read_text());review=json.loads((R/'PARENT_SOURCE_REVIEW.json').read_text())
raw=glb.read_bytes();magic,version,size=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and size==len(raw)
chunks=[];off=12
while off<len(raw):
 n,t=struct.unpack_from('<II',raw,off);off+=8;chunks.append((t,raw[off:off+n]));off+=n
D=json.loads(next(v for t,v in chunks if t==0x4e4f534a));binary=next(v for t,v in chunks if t==0x004e4942)
def accessor(i):
 a=D['accessors'][i];v=D['bufferViews'][a['bufferView']];dtype={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dt=np.dtype(dtype);offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dt.itemsize*n)
 return np.ndarray((a['count'],n),dtype=dt,buffer=binary,offset=offset,strides=(stride,dt.itemsize)).astype(float)
def local(node):
 if 'matrix' in node:return np.array(node['matrix']).reshape((4,4),order='F')
 x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]];m[:3,:3]=m[:3,:3]@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
parent={j:i for i,n in enumerate(D['nodes']) for j in n.get('children',[])};cache={}
def world(i):
 if i not in cache:cache[i]=(world(parent[i]) if i in parent else np.eye(4))@local(D['nodes'][i])
 return cache[i]
fail=[];seen=set();surfaces=[];triangle_count=0;uv_metric_errors=[];uv_counts=0;normals=0;marker_count=0;light_datums=[]
for i,node in enumerate(D['nodes']):
 name=node.get('name','')
 if name.startswith('CRW_RESERVED_GATE_'):
  marker_count+=1;e=node.get('extras',{});assert e.get('clear_width_m')==3.6 and e.get('clear_height_m')==2.65 and 'mesh' not in node
 if name.startswith('CRW_TASK_LIGHT_DATUM_'):
  j=int(name.rsplit('_',1)[1]);light=contract['light_markers'][j];e=node.get('extras',{});point=world(i)[:3,3];error=float(abs(point-np.array(light['xyz'])).max());assert error<5e-5
  assert 'mesh' not in node and e['datum_kind']=='supported_staff_task_light' and e['world_direction_godot_xyz']==[0,-1,0]
  assert e['source_housing'] in expected and expected[e['source_housing']]['kind']=='supported_light'
  supports=json.loads(e['source_supports_json']);assert len(supports)==2 and all(n in expected and expected[n]['kind']=='fixture_support' for n in supports)
  assert abs(e['lowest_fixture_y']-15.015)<1e-7
  light_datums.append(dict(name=name,xyz=point.tolist(),position_error_m=error,source_housing=e['source_housing'],source_supports=supports,world_direction=[0,-1,0]))
 if 'mesh' not in node:continue
 if name not in expected:fail.append('unexpected mesh '+name);continue
 seen.add(name);p=expected[name];points=[];m=world(i)
 for prim in D['meshes'][node['mesh']]['primitives']:
  attrs=prim['attributes'];assert 'POSITION' in attrs and 'NORMAL' in attrs and 'TEXCOORD_0' in attrs
  v=accessor(attrs['POSITION']);n=accessor(attrs['NORMAL']);uv=accessor(attrs['TEXCOORD_0']);assert np.isfinite(v).all() and np.isfinite(n).all() and np.isfinite(uv).all();uv_counts+=len(uv);normals+=len(n)
  vp=(m@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];points.extend(vp.tolist());idx=accessor(prim['indices']).astype(int).ravel();assert len(idx)%3==0 and idx.max()<len(vp);tri=vp[idx.reshape(-1,3)];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1)/2;assert (area>1e-9).all();centre=vp.mean(axis=0);out=np.einsum('ij,ij->i',cross,tri.mean(axis=1)-centre);assert (out>0).all(),name+' inward winding';triangle_count+=len(tri)
  role=D['materials'][prim['material']].get('extras',{}).get('astraea_material_role');assert role==p['role'],(name,role,p['role']);assert prim.get('mode',4)==4
  assert np.max(abs(np.linalg.norm(n,axis=1)-1))<1e-5
  # Recover Blender source axes and exact metre-scaled source-face UV projection.
  nw=n@np.linalg.inv(m[:3,:3]);nb=np.column_stack([nw[:,0],-nw[:,2],nw[:,1]]);vb=np.column_stack([vp[:,0],-vp[:,2],vp[:,1]])
  u=np.empty_like(nb)
  for ni,q in enumerate(nb):
   u[ni]=(np.array([1,0,0])-q*q[0]) if abs(q[2])>.7 else np.array([-q[1],q[0],0]);u[ni]/=np.linalg.norm(u[ni])
  vv=np.cross(nb,u);scale=staff_manifest['materials'][role]['meters_per_tile_uv'];predicted=np.column_stack([np.einsum('ij,ij->i',vb,u)/scale[0],1-np.einsum('ij,ij->i',vb,vv)/scale[1]])
  ue=float(abs(predicted-uv).max());assert ue<1e-4,(name,ue);uv_metric_errors.append(ue)
 pts=np.array(points);actual=np.array([[pts[:,0].min(),pts[:,0].max()],[pts[:,1].min(),pts[:,1].max()],[pts[:,2].min(),pts[:,2].max()]]).ravel();want=np.array(p['world_aabb']);err=float(abs(actual-want).max())
 if err>5e-5:fail.append(dict(name=name,error_m=err,want=want.tolist(),actual=actual.tolist()))
 surfaces.append(dict(name=name,maximum_bound_error_m=err,world_aabb=actual.tolist()))
assert not fail and seen==set(expected),(fail[:5],len(seen),len(expected));assert marker_count==len(contract['gate_reservations']);assert len(light_datums)==len(contract['light_markers']),('missing source-backed exported light datum nodes',len(light_datums),len(contract['light_markers']))
# Embedded staff images must have valid headers and bounds.
images=[]
for im in D.get('images',[]):
 assert 'bufferView' in im and im['mimeType']=='image/png';bv=D['bufferViews'][im['bufferView']];a=bv.get('byteOffset',0);data=binary[a:a+bv['byteLength']];assert data.startswith(b'\x89PNG\r\n\x1a\n');assert hashlib.sha256(data).hexdigest()==staff_manifest['materials'][im['name']]['sha256'];images.append(dict(name=im.get('name'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
# No proposed/compiler floors can be hidden inside asset; every mesh matched an approved source solid.
assert not any(p['world_aabb'][2]<12 for p in parts)
support=R/'source/SUPPORT_OWNERSHIP_PROPOSAL.json';assert hashlib.sha256(support.read_bytes()).hexdigest()==review['support_proposal_sha256']
# Exact Git object hashes for every retained tracked file, including binary exports/ENG008.
rows=subprocess.check_output(['git','-C',str(C),'ls-tree','-r','-z',BASE]).split(b'\0');preserved=[];modified=[]
for row in rows:
 if not row:continue
 info,path=row.split(b'\t',1);mode,kind,sha=info.decode().split();path=path.decode()
 if kind!='blob':continue
 f=C/path
 if not f.exists():modified.append(dict(path=path,reason='missing'));continue
 actual=subprocess.check_output(['git','-C',str(C),'hash-object','--',str(f)]).decode().strip()
 if actual!=sha:modified.append(dict(path=path,expected_blob=sha,actual_blob=actual))
 preserved.append(dict(path=path,git_blob=sha))
assert not modified,modified[:10]
manifest=json.loads(subprocess.check_output(['git','-C',str(C),'show',BASE+':catalogue_manifest.json']));assert len(manifest['assets'])==169
out=dict(schema='astraea_crew_service_export_qa_v1',engine_used=False,source_blend_exists=(R/'source/AST-STF-010.blend').is_file(),source_blend_sha256=hashlib.sha256((R/'source/AST-STF-010.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(raw).hexdigest(),glb_bytes=len(raw),source_meshes=len(expected),matched_glb_meshes=len(seen),triangles=triangle_count,uv_vertices=uv_counts,normal_vertices=normals,max_metre_scaled_uv_error=max(uv_metric_errors),all_embedded_staff_png_hashes_match=True,gate_marker_empties=marker_count,source_backed_downward_light_datums=len(light_datums),max_source_export_bound_error_m=max(p['maximum_bound_error_m'] for p in surfaces),source_material_roles=sorted({p['role'] for p in parts}),embedded_images=images,compiler_floor_exported=False,all_export_meshes_match_source_solids=True,support_proposal_matches_parent_approved_hash=True,retained_baseline=BASE,retained_catalogue_entries=169,retained_tracked_files_checked=len(preserved),retained_modified_files=modified,live_source_inspection=False,blend_object_uv_inspection='not independently inspected in Blender; generator source and exact GLB plan correspondence checked',runtime_import=False,cart_runtime=False,visual_acceptance=False)
(R/'qa/SOURCE_EXPORT_QA.json').write_text(json.dumps(out,indent=2)+'\n');(R/'qa/EXPORTED_LIGHT_DATUM_WITNESSES.json').write_text(json.dumps(light_datums,indent=2)+'\n');(R/'qa/EXPORTED_SURFACE_WITNESSES.json').write_text(json.dumps(surfaces,indent=2)+'\n');(R/'qa/RETAINED_BASELINE_PRESERVATION.json').write_text(json.dumps(preserved,indent=2)+'\n');print(json.dumps(out,indent=2))
