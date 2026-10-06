"""Read-only offline diagnosis of VISUAL_STUDY004 native Variant surface arrays.
No engine, imports, images, project mutations or relaxed acceptance limits.
"""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,hashlib,json,struct,sys,datetime
import numpy as np
from godot_normal_codec import roundtrip, SOURCES as CODEC_SOURCES
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
HERE=Path(__file__).resolve().parent
STUDY=HERE.parent/'pool-feature-VISUAL_STUDY004'
NORMAL_LIMIT=1e-4 # exact existing native keeper bound; diagnostic does not alter it
SLOTS=['vertex','normal','tangent','color','uv','uv2','custom0','custom1','custom2','custom3','bones','weights','index']
TYPES={0:'Nil',28:'Array',29:'PackedByteArray',30:'PackedInt32Array',31:'PackedInt64Array',32:'PackedFloat32Array',33:'PackedFloat64Array',35:'PackedVector2Array',36:'PackedVector3Array',37:'PackedColorArray',38:'PackedVector4Array'}
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def jsonable(v):
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,np.generic):return v.item()
 raise TypeError(type(v).__name__)
class VariantReader:
 """Restricted decoder for var_to_bytes(mesh.surface_get_arrays()). Never objects."""
 def __init__(self,raw):self.raw=raw;self.at=0
 def take(self,n):
  require(n>=0 and self.at+n<=len(self.raw),'Truncated Variant bytes')
  b=self.raw[self.at:self.at+n];self.at+=n;return b
 def u32(self):return struct.unpack('<I',self.take(4))[0]
 def value(self,depth=0):
  require(depth<=4,'Unexpected deep Variant')
  start=self.at;header=self.u32();kind=header&255;flags=header>>16;require((header&0xff00)==0,'Unknown header data')
  require(kind in TYPES,'Unexpected/object-bearing Variant type '+str(kind))
  if kind==0:
   require(flags==0,'Nil header flags');value=None
  elif kind==28:
   require(flags in [0,1],'Unexpected typed/object Array')
   subtype=self.u32() if flags==1 else None
   require(subtype in [None,0],'Expected Variant outer array')
   count=self.u32();require(count==13,'Mesh array must contain 13 slots');value=[self.value(depth+1) for _ in range(count)]
  else:
   require(flags in [0,1],'Unexpected packed flags')
   count=self.u32();require(count<100000000,'Implausible packed count')
   dtype,width={29:('u1',1),30:('<i4',1),31:('<i8',1),32:('<f4',1),33:('<f8',1),35:('<f8' if flags else '<f4',2),36:('<f8' if flags else '<f4',3),37:('<f4',4),38:('<f8' if flags else '<f4',4)}[kind]
   require(flags==0 or kind in [35,36,38],'64-bit flag invalid for fixed packed type')
   size=np.dtype(dtype).itemsize*width*count;value=np.frombuffer(self.take(size),dtype=dtype).copy()
   if width!=1:value=value.reshape(count,width)
   if kind==29:self.take((-size)%4)
  return dict(type=TYPES[kind],kind=kind,header=header,offset=start,bytes=self.at-start,value=value,encoded_sha256=hashlib.sha256(self.raw[start:self.at]).hexdigest())
def decode_variant(path,expected_sha=None):
 raw=Path(path).read_bytes()
 if expected_sha:require(hashlib.sha256(raw).hexdigest()==expected_sha,'Dump hash changed')
 reader=VariantReader(raw);outer=reader.value();require(reader.at==len(raw),'Trailing Variant bytes')
 require(outer['kind']==28,'Expected top-level Array');return outer['value']
def decode_glb(path,expected_sha):
 b=Path(path).read_bytes();require(hashlib.sha256(b).hexdigest()==expected_sha,'Unaccepted GLB bytes')
 require(struct.unpack_from('<III',b)==(0x46546c67,2,len(b)),'Bad GLB header')
 n,kind=struct.unpack_from('<II',b,12);require(kind==0x4e4f534a,'Missing JSON');doc=json.loads(b[20:20+n]);nb,kind=struct.unpack_from('<II',b,20+n);require(kind==0x004e4942,'Missing binary');binary=b[28+n:28+n+nb]
 def acc(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];require('sparse' not in a and not a.get('normalized'),'Unexpected accessor')
  dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];size=np.dtype(dtype).itemsize
  at=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size*width)
  x=np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=at,strides=(stride,size)).copy();return x
 nodes={n['name']:n for n in doc['nodes']};surfaces={}
 for name,node in nodes.items():
  if 'mesh' not in node:continue
  for si,p in enumerate(doc['meshes'][node['mesh']]['primitives']):
   at=p['attributes'];pos=acc(at['POSITION']);norm=acc(at['NORMAL']);uv=acc(at['TEXCOORD_0']);ix=acc(p['indices']).ravel().astype(np.int64).reshape(-1,3)[:,[0,2,1]]
   surfaces[name,si]={'p':pos[ix],'n':norm[ix],'u':uv[ix],'vertices':pos,'normals':norm,'uvs':uv,'indices':ix,'attributes':at,'material':doc['materials'][p['material']]['name']}
 return doc,surfaces
def f32(a):
 x=np.asarray(a,dtype='<f4').copy();x[x==0]=0;return x
def key(p,u=None):return (f32(p) if u is None else np.concatenate([f32(p),f32(u)],axis=-1)).tobytes()
def canonical(p,u=None):
 ks=[key(np.roll(p,-s,axis=0),None if u is None else np.roll(u,-s,axis=0)) for s in range(3)];s=min(range(3),key=lambda i:ks[i]);return ks[s],s
def error(a,b):return float(np.max(np.linalg.norm(np.asarray(a,dtype=np.float32)-np.asarray(b,dtype=np.float32),axis=-1),initial=0))
def native_triangles(slots):
 p=slots[0]['value'];n=slots[1]['value'];u=slots[4]['value'];ix=slots[12]['value'];require(p is not None and n is not None and u is not None,'Missing required raw attributes')
 if ix is None:ix=np.arange(len(p),dtype=np.int32)
 require(len(ix)%3==0 and np.min(ix)>=0 and np.max(ix)<len(p),'Invalid native triangle indices');ix=ix.reshape(-1,3).astype(np.int64)
 require(len(p)==len(n)==len(u),'Native attribute counts differ');return p[ix],n[ix],u[ix],ix

def reproduce_old_greedy(expected,p,n,u):
 buckets=defaultdict(list)
 for i in range(len(expected['p'])):buckets[key(expected['p'][i],expected['u'][i])].append(i)
 first_failure=None;matched=0;maximum=0.0
 for i in range(len(p)):
  found=False;position_uv_candidates=[]
  for s in range(3):
   k=key(np.roll(p[i],-s,axis=0),np.roll(u[i],-s,axis=0))
   for at,j in enumerate(buckets.get(k,[])):
    e=error(np.roll(n[i],-s,axis=0),expected['n'][j]);position_uv_candidates.append({'glb_triangle':j,'cyclic_shift':s,'normal_error':e})
    if e>NORMAL_LIMIT:continue
    buckets[k].pop(at);matched+=1;maximum=max(maximum,e);found=True;break
   if found:break
  if not found:
   first_failure={'native_triangle':i,'category':'NORMAL_BOUND_OR_GREEDY_DUPLICATE' if position_uv_candidates else 'EXACT_POSITION_UV_CYCLIC_KEY_ABSENT','position_uv_candidates':position_uv_candidates,'native_positions':p[i],'native_uvs':u[i],'native_normals':n[i]};break
 return {'matched_before_first_failure':matched,'first_failure':first_failure,'maximum_matched_normal_error':maximum,'complete':first_failure is None and all(not x for x in buckets.values())}
def surface_diagnosis(expected,slots,format_value,provenance):
 p,n,u,ix=native_triangles(slots);ep,en,eu=expected['p'],expected['n'],expected['u'];predicted_normals,encoded=roundtrip(en);codec_errors=[];eg=defaultdict(list);ag=defaultdict(list)
 for i in range(len(ep)):
  k,s=canonical(ep[i],eu[i]);eg[k].append((i,s))
 for i in range(len(p)):
  k,s=canonical(p[i],u[i]);ag[k].append((i,s))
 exact_counts={k:len(v) for k,v in eg.items()}=={k:len(v) for k,v in ag.items()}
 unmatched_keys=[];normal_issues=[];corner_errors=[];full_bijection=True;codec_bijection=True;codec_bit_exact_count=0;pair_records=[]
 for k,actual in ag.items():
  target=eg.get(k,[])
  if len(actual)!=len(target):
   full_bijection=False;codec_bijection=False;unmatched_keys.extend([i for i,s in actual]);continue
  costs=np.array([[error(np.roll(n[i],-s,axis=0),np.roll(en[j],-t,axis=0)) for j,t in target] for i,s in actual])
  adjacency=costs<=NORMAL_LIMIT;matching=maximum_bipartite_matching(csr_matrix(adjacency),perm_type='column')
  codec_costs=np.array([[error(np.roll(n[i],-s,axis=0),np.roll(predicted_normals[j],-t,axis=0)) for j,t in target] for i,s in actual])
  codec_matching=maximum_bipartite_matching(csr_matrix(codec_costs==0.0),perm_type='column')
  if np.any(codec_matching<0):codec_bijection=False
  if np.any(matching<0):full_bijection=False
  for ai,(i,s) in enumerate(actual):
   # Nearest attribute-identical GLB normal is diagnostic only; all thresholds stay fixed.
   ti=int(np.argmin(costs[ai]));j,t=target[ti];e=float(costs[ai,ti]);corner_errors.extend(np.linalg.norm(np.roll(n[i],-s,axis=0)-np.roll(en[j],-t,axis=0),axis=1).tolist())
   row={'native_triangle':i,'glb_triangle':j,'minimum_normal_error_over_exact_position_uv_matches':e,'source_part':provenance.get(j,{}).get('source_part'),'source_triangle':provenance.get(j,{}).get('source_triangle')}
   ci=int(codec_matching[ai]) if int(codec_matching[ai])>=0 else int(np.argmin(codec_costs[ai]));cj,ct=target[ci]
   actual_normal=np.roll(n[i],-s,axis=0);predicted_normal=np.roll(predicted_normals[cj],-ct,axis=0)
   bit_exact=actual_normal.astype('<f4').tobytes()==predicted_normal.astype('<f4').tobytes();codec_bit_exact_count+=int(bit_exact)
   row.update(codec_glb_triangle=cj,codec_source_part=provenance.get(cj,{}).get('source_part'),source_codec_encoded_uint16_canonical=np.roll(encoded[cj],-ct,axis=0),predicted_native_normal_canonical=predicted_normal,actual_native_normal_canonical=actual_normal,native_minus_codec_float32=(actual_normal-predicted_normal).astype(np.float32),native_codec_bits_exact=bit_exact,native_vs_source_derived_codec_error=float(codec_costs[ai,ci]))
   codec_errors.append(row['native_vs_source_derived_codec_error']);pair_records.append(row)
   if e>NORMAL_LIMIT:normal_issues.append({**row,'native_positions':p[i],'native_uvs':u[i],'native_normals_canonical':np.roll(n[i],-s,axis=0),'glb_normals_canonical':np.roll(en[j],-t,axis=0)})
 allkeys=set(eg)|set(ag)
 if any(len(eg.get(k,[]))!=len(ag.get(k,[])) for k in allkeys):full_bijection=False;codec_bijection=False
 positions_exact=Counter(canonical(x)[0] for x in ep)==Counter(canonical(x)[0] for x in p)
 reverse_match=Counter(canonical(x[[0,2,1]],y[[0,2,1]])[0] for x,y in zip(p,u))==Counter(canonical(x,y)[0] for x,y in zip(ep,eu))
 tangents=slots[2]['value'];tangent_report={'present':tangents is not None,'source_glb_has_tangents':'TANGENT' in expected['attributes'],'native_scalar_count':len(tangents) if tangents is not None else 0}
 if tangents is not None and len(tangents)==len(slots[0]['value'])*4:
  t=tangents.reshape(-1,4);tangent_report.update(xyz_length_min=float(np.min(np.linalg.norm(t[:,:3],axis=1))),xyz_length_max=float(np.max(np.linalg.norm(t[:,:3],axis=1))),max_abs_dot_with_native_normal=float(np.max(np.abs(np.sum(t[:,:3]*slots[1]['value'],axis=1)))),handedness_values=np.unique(t[:,3]).tolist())
 old=reproduce_old_greedy(expected,p,n,u)
 category=('EXACT_POSITION_UV_WITH_NORMAL_BOUND_EXCEEDANCES' if exact_counts and normal_issues else 'GREEDY_DUPLICATE_MATCHER_FALSE_FAILURE' if full_bijection and not old['complete'] else 'EXACT_CYCLIC_ATTRIBUTES_WITHIN_EXISTING_NORMAL_BOUND' if full_bijection else 'UV_MISMATCH' if positions_exact else 'WINDING_REVERSAL' if reverse_match else 'POSITION_OR_TOPOLOGY_MISMATCH')
 return {'category':category,'native_triangles':len(p),'glb_triangles':len(ep),'exact_position_uv_cyclic_multiset':exact_counts,'exact_position_only_cyclic_multiset':positions_exact,'reverse_winding_matches':reverse_match,'complete_existing_bound_bijection':full_bijection,'existing_normal_codec_limit':NORMAL_LIMIT,'normal_error_max':max(corner_errors,default=None),'normal_error_percentiles':np.percentile(corner_errors,[50,90,99,100]).tolist() if corner_errors else [],'normal_exceeding_triangles':len(normal_issues),'normal_exceeding_corners':sum(e>NORMAL_LIMIT for e in corner_errors),'normal_examples':normal_issues[:12],'unmatched_native_key_examples':unmatched_keys[:12],'old_matcher_semantics':old,'tangents':tangent_report,'surface_format':int(format_value),'surface_format_hex':hex(int(format_value)),'compression_enabled':bool(int(format_value)&(1<<29)),'format_version_bits':(int(format_value)>>35)&255,'slot_headers':[dict(slot=SLOTS[i],**{k:v for k,v in x.items() if k!='value'}) for i,x in enumerate(slots)],'triangle_diagnostic_pairs':pair_records,'source_derived_codec_diagnostic':{'sources':CODEC_SOURCES,'predicted_source_roundtrip_max':float(np.max(np.linalg.norm(predicted_normals-en,axis=2))),'predicted_source_corners_exceeding_existing_bound':int(np.count_nonzero(np.linalg.norm(predicted_normals-en,axis=2)>NORMAL_LIMIT)),'native_vs_codec_max':max(codec_errors,default=None),'complete_source_codec_numeric_bijection':codec_bijection,'native_triangles_numeric_exact_to_codec':sum(x==0 for x in codec_errors),'native_triangles_bits_exact_to_codec':codec_bit_exact_count,'compared_triangles':len(codec_errors),'acceptance_tolerance_changed':False}}
def array_comparison(a,b):
 rows=[]
 for i,(x,y) in enumerate(zip(a,b)):
  v,w=x['value'],y['value'];equal=x['encoded_sha256']==y['encoded_sha256'];row={'slot':SLOTS[i],'encoded_bytes_equal':equal,'import_type':x['type'],'after_draw_type':y['type']}
  if isinstance(v,np.ndarray) and isinstance(w,np.ndarray):
   row['import_shape']=list(v.shape);row['after_draw_shape']=list(w.shape)
   if v.shape==w.shape:
    row['numeric_value_equal']=bool(np.array_equal(v,w));row['changed_elements']=int(np.count_nonzero(v!=w));row['max_abs_delta']=float(np.max(np.abs(v.astype(float)-w.astype(float)),initial=0))
  rows.append(row)
 return {'all_slots_bit_identical':all(x['encoded_bytes_equal'] for x in rows),'slots':rows}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--asset',default='AST-BOT-002_pool_loggia_mass_00');ap.add_argument('--out',required=True);args=ap.parse_args();out=HERE/args.out
 require('/' not in args.out and args.out not in ['.','..'] and not out.exists(),'Use a fresh local output label');out.mkdir()
 d=read(STUDY/'NATIVE_INPUTS.json');asset=next(x for x in d['assets'] if x['name']==args.asset);doc,expected=decode_glb(asset['path'],asset['sha256']);manifest=STUDY/'output/native_arrays'/f'{args.asset}_ACTUAL_NATIVE_DUMP.json'
 base={'status':'PENDING_ACTUAL_ARRAYS','verification':'UNVERIFIED_IMPORT_EQUIVALENCE','installed':False,'geometry_acceptance':False,'physical_acceptance':False,'final_acceptance':False,'engine_launched':False,'normal_bound_unchanged':NORMAL_LIMIT,'asset':args.asset,'accepted_glb_sha256':asset['sha256'],'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 if not manifest.exists():base['missing_input']=str(manifest)
 else:
  m=read(manifest);require(m['glb_sha256']==asset['sha256'],'Dump references wrong GLB');prov=read(asset['provenance']);by=defaultdict(dict)
  for row in prov['triangles']:by[row['node'],int(row['primitive'])][int(row['export_triangle'])]=row
  after_path=STUDY/'output/after_first_candidate_draw/AFTER_FIRST_CANDIDATE_CAPTURE_DRAW.json';after=read(after_path) if after_path.exists() else None
  after_map={(int(x['mesh_resource_id']),int(x['surface'])):x for x in after['surfaces']} if after else {}
  rows=[]
  for node in m['nodes']:
   for s in node.get('surfaces',[]):
    key2=node['name'],int(s['surface']);require(key2 in expected,'Native mesh name/primitive not in accepted GLB');dump=s['raw_arrays_godot_variant_binary'];slots=decode_variant(dump['file'],dump['sha256'])
    r=surface_diagnosis(expected[key2],slots,int(s['format']),by[key2]);r.update(mesh=node['name'],surface=int(s['surface']),raw_dump=dump,import_world_transform=node['actual_world_transform'])
    pairs=r.pop('triangle_diagnostic_pairs');(out/(node['name']+'_s'+str(s['surface'])+'_PAIRS.json')).write_text(json.dumps({'verification':base['verification'],'installed':False,'geometry_acceptance':False,'pairs':pairs},indent=2,default=jsonable)+'\n')
    a=after_map.get((int(node['mesh_resource_id']),int(s['surface'])))
    if a:
     ds=a['raw_arrays_godot_variant_binary'];later=decode_variant(ds['file'],ds['sha256']);r['after_draw_comparison']=array_comparison(slots,later);r['after_draw_format']=a['format'];r['format_unchanged']=int(s['format'])==int(a['format'])
     if not r['after_draw_comparison']['all_slots_bit_identical']:
      rr=surface_diagnosis(expected[key2],later,int(a['format']),by[key2]);rr.pop('triangle_diagnostic_pairs');r['after_draw_diagnosis']=rr
    else:r['after_draw_comparison']='PENDING_AFTER_DRAW_DUMP'
    rows.append(r)
  base.update(status='OFFLINE_ACTUAL_ARRAY_DIAGNOSIS',manifest_sha256=sha(manifest),surfaces=rows,after_draw_manifest_sha256=sha(after_path) if after else None,categories=dict(Counter(r['category'] for r in rows)),all_source_meshes_inspected=len(rows)==len(expected))
 (out/'DIAGNOSIS.json').write_text(json.dumps(base,indent=2,default=jsonable)+'\n');print(json.dumps({'status':base['status'],'file':str(out/'DIAGNOSIS.json'),'sha256':sha(out/'DIAGNOSIS.json'),'categories':base.get('categories'),'after_draw_available':base.get('after_draw_manifest_sha256') is not None}))
if __name__=='__main__':main()
