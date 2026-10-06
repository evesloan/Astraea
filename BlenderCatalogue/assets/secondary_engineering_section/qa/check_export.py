"""Read-only non-engine GLB verification against dimensioned source plan.
Writes reports ONLY inside this new package. Retained tracked inputs checked against HEAD.
"""
from pathlib import Path
import json,struct,math,hashlib,subprocess
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=R/'exports/AST-ENG-008.glb'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
b=G.read_bytes();magic,version,length=struct.unpack_from('<4sII',b);assert magic==b'glTF' and version==2 and length==len(b)
o=12;chunks={}
while o<len(b):
    n,t=struct.unpack_from('<II',b,o);o+=8;chunks[t]=b[o:o+n];o+=n
D=json.loads(chunks[0x4E4F534A]);B=chunks[0x004E4942];plan=json.loads((R/'source/geometry_plan.json').read_text());surfaces=json.loads((R/'source/surface_manifest.json').read_text())
checks=[]
def check(n,ok,detail=None):checks.append(dict(check=n,pass_check=bool(ok),detail=detail));assert ok,(n,detail)
formats={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'};sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def accessor(i):
    a=D['accessors'][i];v=D['bufferViews'][a['bufferView']];f=formats[a['componentType']];n=sizes[a['type']];s=struct.calcsize('<'+f*n);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',s)
    return [struct.unpack_from('<'+f*n,B,start+j*stride) for j in range(a['count'])]
def bounds(v):return [min(p[i] for p in v) for i in range(3)]+[max(p[i] for p in v) for i in range(3)]
expected={p['name']:p for p in plan['parts'] if p['export']};nodes={n['name']:n for n in D['nodes'] if 'mesh' in n}
check('exact expected surface node set',set(nodes)==set(expected),{'expected':len(expected),'actual':len(nodes)})
material_profile=next(m for m in D['materials'] if m['name']=='ASTRAEA_bridge_pressure_glass');pbr=material_profile['pbrMetallicRoughness'];check('exact retained glass alpha roughness metallic profile',abs(pbr['baseColorFactor'][3]-.28)<1e-5 and abs(pbr['roughnessFactor']-.22)<1e-5 and abs(pbr['metallicFactor']-.08)<1e-5 and material_profile.get('alphaMode')=='BLEND',material_profile)
check('compiler previews excluded',all('PREVIEW' not in n and not v.get('extras',{}).get('preview_only') for n,v in nodes.items()))
palette=json.loads((C/'materials/staff/manifest.json').read_text())['materials']
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def normal(a):
    l=math.sqrt(dot(a,a));return tuple(x/l for x in a)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
records=[];triangles=0
for name,node in nodes.items():
    check(name+' untransformed source coordinates',not any(k in node for k in ['translation','rotation','scale','matrix']))
    pts=[];materials=[]
    for p in D['meshes'][node['mesh']]['primitives']:
        check(name+' triangles',p.get('mode',4)==4);v=accessor(p['attributes']['POSITION']);uv=accessor(p['attributes']['TEXCOORD_0']);norm=accessor(p['attributes']['NORMAL']);ix=[x[0] for x in accessor(p['indices'])]
        check(name+' finite vertices UV normals',all(math.isfinite(x) for a in v+uv+norm for x in a))
        role=expected[name]['material_role'];tile=palette.get(role,{}).get('meters_per_tile_uv',[1,1]);uv_error=0;uv_reference={}
        for pos,nrm,tex in zip(v,norm,uv):
            key=tuple(nrm);refpos,refuv=uv_reference.setdefault(key,(pos,tex));delta=tuple(pos[i]-refpos[i] for i in range(3));q=(delta[0],-delta[2],delta[1]);n=(nrm[0],-nrm[2],nrm[1]);u=(1,0,0) if abs(n[0])<.7 else (0,1,0);u=normal(tuple(u[i]-n[i]*dot(u,n) for i in range(3)));w=normal(cross(n,u));wantuv=(dot(q,u)/tile[0],-dot(q,w)/tile[1]);gotuv=tuple(tex[i]-refuv[i] for i in range(2));uv_error=max(uv_error,max(abs(a-b) for a,b in zip(wantuv,gotuv)))
        check(name+' approved metric UV scale',uv_error<.01,uv_error)
        check(name+' complete UV and normals',len(uv)==len(v)==len(norm));check(name+' valid triangle indices',len(ix)%3==0 and all(i<len(v) for i in ix))
        check(name+' material slot present',0<=p['material']<len(D['materials']));materials.append(D['materials'][p['material']]['name']);pts+=v;triangles+=len(ix)//3
    want=bounds(expected[name]['vertices_xyz']);got=bounds(pts);err=max(abs(a-b) for a,b in zip(want,got));check(name+' bounds match pure source',err<5e-5,err)
    role=expected[name]['material_role'];check(name+' material role matches',all(m==('ASTRAEA_bridge_pressure_glass' if role=='section_sealed_glass' else 'ASTRAEA_'+role) for m in materials),materials)
    check(name+' collision extras preserved',node['extras']['collision_contract']==expected[name]['collision'])
    records.append(dict(name=name,bounds_xyz_min_max=got,materials=materials,floor_contact_y6=abs(got[1]-6)<5e-5))
check('expected fixture markers exported',all(any(n['name']==m['name'] and n.get('extras',{}).get('housing')==m['housing'] for n in D['nodes']) for m in plan['markers']))
contacts={p['name'] for p in surfaces['source_surfaces'] if p['export'] and p['floor_contact_owner']};check('all compiler floor contacts match',contacts=={p['name'] for p in records if p['floor_contact_y6']})
# Existing registered asset sources/exports must remain byte-identical to retained tracked HEAD.
manifest=json.loads((C/'catalogue_manifest.json').read_text());preserved=[]
for a in manifest['assets']:
    for k in ['source','export']:
        rel=a.get(k)
        if not rel:continue
        p=C/rel
        if not p.is_file():continue
        retained=subprocess.run(['git','rev-parse','HEAD:'+rel],cwd=C,capture_output=True,text=True)
        if retained.returncode:raise AssertionError('Existing catalogue input lacks retained tracked baseline: '+rel)
        current=subprocess.check_output(['git','hash-object',str(p)],cwd=C,text=True).strip();check('retained '+rel,current==retained.stdout.strip())
        preserved.append(dict(catalogue_id=a['catalogue_id'],path=rel,sha256=sha(p),git_blob= current))
tracked_delta=subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=C,text=True).splitlines();check('no retained tracked files changed',not tracked_delta,tracked_delta)
report=dict(stage='actual GLB accessor geometry versus source plan; no runtime or visual acceptance',pass_check=True,meshes=len(nodes),triangles=triangles,fixture_markers=len(plan['markers']),sha256={p.name:sha(p) for p in [G,R/'source/AST-ENG-008.blend',R/'source/generate_section.py',R/'source/geometry_plan.json',R/'source/section_contract.json',C/'catalogue_manifest.json']},checks=checks,surfaces=records,retained_catalogue_inputs=preserved,retained_input_count=len(preserved),not_tested=['Blender source topology introspection','runtime capsule/cart traversal','dynamic doors/pockets','render or lighting acceptance','physical engineering'])
(R/'qa/source_export_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['stage','pass_check','meshes','triangles','fixture_markers','retained_input_count']}))
