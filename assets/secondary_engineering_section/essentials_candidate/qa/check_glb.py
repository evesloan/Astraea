"""Independent binary accessor/transform QA, scratch-only reports."""
from pathlib import Path
import json,struct,hashlib,math
import numpy as np
R=Path(__file__).resolve().parents[1];p=R/'exports/AST-ENG-008_essentials.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];A=json.loads(b[20:20+n]);BIN=b[28+n:]
def read(i):
 a=A['accessors'][i];v=A['bufferViews'][a['bufferView']];fmt,size={5126:('f',4),5125:('I',4),5123:('H',2),5121:('B',1)}[a['componentType']];num={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];off=v.get('byteOffset',0)+a.get('byteOffset',0);st=v.get('byteStride',size*num);return np.array([struct.unpack_from('<'+fmt*num,BIN,off+j*st) for j in range(a['count'])])
PR=json.loads((R/'qa/source_build.json').read_text())['actual_clearance_prisms'];prism_hits={n:0 for n in PR}
minv=np.array([1e9]*3);maxv=-minv;triangles=0;badgeo=0;baduv=0;badnorm=0;meshbounds=[];uv_failures=[]
def walk(i,P):
 global minv,maxv,triangles,badgeo,baduv,badnorm
 node=A['nodes'][i];M=np.eye(4)
 if 'matrix'in node:M=np.array(node['matrix']).reshape(4,4).T
 else:
  x,y,z,w=node.get('rotation',[0,0,0,1]);M[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(node.get('scale',[1,1,1]));M[:3,3]=node.get('translation',[0,0,0])
 M=P@M
 if 'mesh'in node:
  vs=[]
  for pr in A['meshes'][node['mesh']]['primitives']:
   v=read(pr['attributes']['POSITION']);uv=read(pr['attributes']['TEXCOORD_0']);norm=read(pr['attributes']['NORMAL']);idx=read(pr['indices']).flatten().astype(int).reshape(-1,3);assert np.isfinite(v).all() and np.isfinite(uv).all() and np.isfinite(norm).all();assert idx.max()<len(v)
   v=(np.c_[v,np.ones(len(v))]@M.T)[:,:3];norm=norm@np.linalg.inv(M[:3,:3]);tri=v[idx];cr=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cr,axis=1);uvt=uv[idx];uvarea=np.abs((uvt[:,1,0]-uvt[:,0,0])*(uvt[:,2,1]-uvt[:,0,1])-(uvt[:,1,1]-uvt[:,0,1])*(uvt[:,2,0]-uvt[:,0,0]));badgeo+=int((area<1e-12).sum());baduv+=int((uvarea<1e-13).sum());uv_failures.extend([{'node':node['name'],'positions':tri[j].tolist(),'uvs':uvt[j].tolist()} for j in np.flatnonzero(uvarea<1e-13)]);dot=np.einsum('ij,ij->i',cr,norm[idx].mean(1));badnorm+=int((dot< -1e-10).sum());triangles+=len(idx);vs.extend(v)
   for pname,pb in PR.items():
    pb=np.array(pb);prism_hits[pname]+=int(np.all(np.minimum(tri.max(1),pb[3:])-np.maximum(tri.min(1),pb[:3])>1e-5,axis=1).sum())
  vs=np.array(vs);lo=vs.min(0);hi=vs.max(0);minv=np.minimum(minv,lo);maxv=np.maximum(maxv,hi);meshbounds.append({'name':node['name'],'bounds_xyz':lo.tolist()+hi.tolist(),'collision':node.get('extras',{}).get('collision_contract')})
 for c in node.get('children',[]):walk(c,M)
for node in A['scenes'][A.get('scene',0)]['nodes']:walk(node,np.eye(4))
S=json.loads((R/'qa/source_build.json').read_text());expected=sum(x['triangles'] for x in S['actual_evaluated_parts']);rows=S['actual_evaluated_parts'];lo=np.array([min(x['bounds_xyz'][i] for x in rows) for i in range(3)]);hi=np.array([max(x['bounds_xyz'][i+3] for x in rows) for i in range(3)]);error=max(abs(lo-minv).max(),abs(hi-maxv).max())
inputs={k:hashlib.sha256(Path(k).read_bytes()).hexdigest()==h for k,h in S['input_hashes'].items()}
# Actual source-evaluated component bounds establish seated contacts independently of declarations.
def selected(prefix):return [r for r in rows if r['name'].startswith(prefix)]
def extreme(prefix,axis,mode):
 rr=selected(prefix);assert rr,prefix;return (min if mode=='min' else max)(r['bounds_xyz'][axis+(0 if mode=='min' else 3)] for r in rr)
contacts=[]
def contact(name,value,expected):contacts.append({'name':name,'actual':value,'expected':expected,'error_m':abs(value-expected),'pass':abs(value-expected)<.00005})
contact('cabinet feet on compiler floor',extreme('WorkbenchStorage_',1,'min'),6)
contact('cabinet rear on south wall',extreme('WorkbenchStorage_',2,'max'),-400.18)
for x in [23,26,29]:contact('control backing '+str(x),extreme('ConsoleBacking_'+str(x),2,'min'),-462.95)
contact('isolation rear pads',extreme('Isolation_',2,'max'),-441.4)
contact('instrument rear pads',extreme('BenchInstrument_',2,'max'),-401.8)
contact('bench top panels',extreme('BenchWorktop_',1,'min'),6.9)
contact('toolboard wall standoffs',extreme('ToolboardWallStandoff_',2,'max'),-400.18)
for n,z,f in [('spares',-462.5,1),('quarantine',-462.5,1),('consumables',-401.5,-1),('bagged_returns',-401.5,-1)]:contact(n+' front overlay seat',extreme(n+'_DoorFront',2,'min' if f==1 else 'max'),z+f*.65)
report={'passed':not any(prism_hits.values()) and badgeo==0 and baduv==0 and badnorm==0 and error<.0002 and expected==triangles and all(inputs.values()) and all(x['pass'] for x in contacts),'scope':'Independent actual GLB accessor/transform and evaluated-source contact check; no engine/runtime/visual acceptance','export_sha256':hashlib.sha256(b).hexdigest(),'triangles':triangles,'source_triangles':expected,'mesh_groups':len(meshbounds),'materials':len(A['materials']),'bounds_max_error_m':float(error),'degenerate_geometry_triangles':badgeo,'collapsed_uv_triangles':baduv,'opposed_normal_triangles':badnorm,'all_retained_inputs_unchanged':all(inputs.values()),'contacts':contacts,'embedded_image_count':len(A.get('images',[])),'embedded_images':all('bufferView'in x for x in A.get('images',[])),'mesh_bounds':meshbounds,'uv_failures':uv_failures,'actual_export_triangle_prism_hits':prism_hits}
(R/'qa/independent_glb_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['mesh_bounds','contacts']},indent=2));assert report['passed']
