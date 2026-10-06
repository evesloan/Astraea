"""Independent read-only evaluated-source / GLB equivalence checker.

Uses actual accessor data and scene transforms, never source contract vertices.
Triangle matching is a complete bipartite bijection with cyclic winding and all
corner attributes. KD-tree candidate search has no rounded-coordinate hash keys.
Geometry limit stays 50 micrometres. Local-coordinate equality and transform
checks separately restrict any accepted difference to export representation.
"""
import argparse, hashlib, json, math, struct, sys, traceback
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

POSITION_LIMIT=50e-6
# Local vertices are saved/exported float32 with only an axis permutation. There
# is no legitimate new local quantization. The tiny bound covers float64 inverse
# reconstruction from snapshot001 (measured residual <= 2.85e-14 m), not edits.
LOCAL_LIMIT=1e-10
NORMAL_LIMIT=2e-6
NUMERIC_LIMIT=2e-7
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise AssertionError(msg)
def close(a,b,tol=NUMERIC_LIMIT):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    return a.shape==b.shape and bool(np.isfinite(a).all() and np.isfinite(b).all() and np.max(np.abs(a-b),initial=0)<=tol)

def decode(path):
    raw=Path(path).read_bytes();magic,version,length=struct.unpack_from('<III',raw)
    require(magic==0x46546c67 and version==2 and length==len(raw),'Invalid GLB header')
    offset=12;chunks={}
    while offset<len(raw):
        n,kind=struct.unpack_from('<II',raw,offset);offset+=8
        require(offset+n<=len(raw) and kind not in chunks,'Invalid or duplicate GLB chunk')
        chunks[kind]=raw[offset:offset+n];offset+=n
    require(set(chunks)=={0x4e4f534a,0x004e4942},'Unexpected GLB chunk inventory')
    doc=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942]
    require(len(doc.get('buffers',[]))==1 and 'uri' not in doc['buffers'][0],'GLB must be self-contained')
    require(doc['buffers'][0]['byteLength']<=len(binary),'Invalid GLB buffer length')
    require(not any(doc.get(k) for k in ['animations','skins','cameras']),'Unexpected animation/skin/camera')
    require(not any(e in doc.get('extensionsUsed',[]) for e in ['KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_mesh_quantization']),'Unexpected compressed/quantized geometry')
    def view(i):
        v=doc['bufferViews'][i];start=v.get('byteOffset',0);end=start+v['byteLength']
        require(v.get('buffer',0)==0 and 0<=start<=end<=len(binary),'Invalid buffer view')
        return v,start,end
    def acc(i):
        a=doc['accessors'][i];require('sparse' not in a and not a.get('normalized'),'Unsupported sparse/normalized accessor')
        v,start,end=view(a['bufferView']);start+=a.get('byteOffset',0)
        fmt='<'+{5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        width=struct.calcsize(fmt);stride=v.get('byteStride',width)
        require(stride>=width and a['count']>0 and start+(a['count']-1)*stride+width<=end,'Invalid accessor bounds')
        x=np.array([struct.unpack_from(fmt,binary,start+k*stride) for k in range(a['count'])],dtype=float)
        require(np.isfinite(x).all(),'Nonfinite accessor values');return x
    def matrix(n):
        if 'matrix' in n:return np.asarray(n['matrix'],float).reshape((4,4),order='F')
        x,y,z,w=n.get('rotation',[0,0,0,1]);require(abs(x*x+y*y+z*z+w*w-1)<2e-6,'Non-unit node quaternion')
        length=math.sqrt(x*x+y*y+z*z+w*w);x,y,z,w=[v/length for v in [x,y,z,w]]
        r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                    [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                    [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
        m=np.eye(4);m[:3,:3]=r@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
    nodes={};seen=set();prims=[]
    def visit(i,parent,pm):
        require(i not in seen,'Node graph cycle or repeated node');seen.add(i);n=doc['nodes'][i]
        name=n.get('name');require(name and name not in nodes,'Missing or duplicate node name')
        m=pm@matrix(n);require(np.isfinite(m).all() and np.linalg.det(m[:3,:3])>0,'Invalid/mirrored world matrix')
        r={'name':name,'index':i,'parent':parent,'matrix':m,'extras':n.get('extras',{}),'mesh':n.get('mesh'),'primitives':[]};nodes[name]=r
        if 'mesh' in n:
            for pi,p in enumerate(doc['meshes'][n['mesh']]['primitives']):
                require(p.get('mode',4)==4 and not p.get('targets') and not p.get('extensions'),'Unsupported primitive')
                attrs=p['attributes'];require(set(attrs)=={'POSITION','NORMAL','TEXCOORD_0'},'Unexpected/missing attributes: '+name+str(attrs))
                pos=acc(attrs['POSITION']);norm=acc(attrs['NORMAL']);uv=acc(attrs['TEXCOORD_0'])
                require(len(pos)==len(norm)==len(uv),'Attribute cardinality mismatch')
                ix=acc(p['indices']).astype(np.int64).ravel() if 'indices' in p else np.arange(len(pos))
                require(len(ix)%3==0 and min(ix)>=0 and max(ix)<len(pos),'Invalid triangle indices');ix=ix.reshape((-1,3))
                world=(m[:3,:3]@pos.T).T+m[:3,3];wn=(np.linalg.inv(m[:3,:3]).T@norm.T).T
                require(np.max(np.abs(np.linalg.norm(norm,axis=1)-1))<NORMAL_LIMIT,'Nonunit exported corner normals')
                wn/=np.linalg.norm(wn,axis=1)[:,None]
                q={'node':name,'primitive':pi,'material':p['material'],'positions':world[ix],'local_positions':pos[ix],
                   'normals':wn[ix],'uvs':uv[ix],'triangles':len(ix)}
                r['primitives'].append(q);prims.append(q)
        for child in n.get('children',[]):visit(child,name,m)
    require(len(doc.get('scenes',[]))==1,'Exactly one export scene required')
    for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,None,np.eye(4))
    require(len(seen)==len(doc['nodes']),'Unreferenced export nodes')
    images=[]
    for im in doc.get('images',[]):
        require('uri' not in im and im.get('mimeType')=='image/png','Embedded PNG required')
        v,start,end=view(im['bufferView']);data=binary[start:end]
        require(data.startswith(b'\x89PNG\r\n\x1a\n'),'Invalid PNG signature')
        width,height=struct.unpack_from('>II',data,16)
        images.append({'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'size':[width,height]})
    return {'doc':doc,'nodes':nodes,'primitives':prims,'images':images}

def compare_properties(expected,actual,name):
    for k,v in expected.items():require(k in actual and actual[k]==v,'Changed/missing property '+name+'.'+k)

def compare_matrix(source,node):
    expected=np.array(source['world_matrix_godot']);actual=node['matrix']
    require(close(expected[:3,:3],actual[:3,:3]),'World basis changed: '+source['name'])
    # Blender derives child-local matrices using a float32 parent inverse. At
    # world Z ~= -450 m this can emit an ~8.6 um local translation although the
    # saved evaluated world matrix rounded to the parent's origin. The accepted
    # decoded origin must round back to the EXACT saved float32 source origin.
    # This measures representation in the source's own precision; it does not
    # introduce an arbitrary positional epsilon or move/weld any corner.
    require(np.array_equal(expected[:3,3].astype(np.float32),actual[:3,3].astype(np.float32)) and
            np.max(np.abs(expected[:3,3]-actual[:3,3]))<=POSITION_LIMIT,
            'World origin no longer round-trips to source float32: '+source['name'])
    return float(np.max(np.abs(expected-actual)))

def material_check(source,mi,decoded):
    d=decoded['doc'];m=d['materials'][mi];nodes={n['name']:n for n in source['nodes']};links=source['links']
    outputs=[n for n in nodes.values() if n['type']=='OUTPUT_MATERIAL' and n['active_output']]
    require(len(outputs)==1,'Ambiguous active material output: '+source['name'])
    out=outputs[0];surface=[l for l in links if l[2:]==[out['name'],'Surface']]
    require(len(surface)==1 and surface[0][1]=='BSDF','Unsupported shader output graph')
    bs=nodes[surface[0][0]];require(bs['type']=='BSDF_PRINCIPLED','Expected actual Principled surface')
    inputs=bs['inputs'];allowed_links={tuple(surface[0])};textures={}
    for channel in ['Base Color','Emission Color']:
        incoming=[l for l in links if l[2:]==[bs['name'],channel]]
        require(len(incoming)<=1,'Multiple shader input links')
        if incoming:
            l=incoming[0];tex=nodes[l[0]];require(tex['type']=='TEX_IMAGE' and l[1]=='Color','Unsupported '+channel+' shader expression')
            require(tex['image']['projection']=='FLAT' and tex['image']['colorspace']=='sRGB','Unsupported image projection/colorspace')
            require(not any(k[2]==tex['name'] for k in links),'Unexpected image UV mapping graph')
            textures[channel]=tex['image'];allowed_links.add(tuple(l))
    require(set(map(tuple,links))==allowed_links,'Unverified source shader links: '+source['name'])
    for key in ['Subsurface Weight','Transmission Weight','Coat Weight','Sheen Weight','Anisotropic','Thin Film Thickness','Diffuse Roughness']:
        require(abs(inputs.get(key,0))<1e-8,'Unsupported nonzero shader feature '+key)
    require(close(inputs.get('IOR',1.5),1.5) and close(inputs.get('Specular IOR Level',.5),.5),'Unsupported nondefault IOR/specular')
    require(close(inputs.get('Specular Tint',[1,1,1,1]),[1,1,1,1]),'Unsupported specular tint')
    require(close(inputs.get('Alpha',1),1),'Source alpha is not opaque')
    require(m.get('alphaMode','OPAQUE')=='OPAQUE','Export changed alpha mode')
    require(bool(m.get('doubleSided',False))==source['double_sided'],'Export changed culling')
    require(m.get('name')==source['name'],'Wrong source material assignment')
    compare_properties(source['extras'],m.get('extras',{}),'material '+source['name'])
    pbr=m.get('pbrMetallicRoughness',{})
    require(close(pbr.get('metallicFactor',1),inputs['Metallic']),'Metallic factor changed')
    require(close(pbr.get('roughnessFactor',1),inputs['Roughness']),'Roughness factor changed')
    base=[1.,1.,1.,1.] if 'Base Color' in textures else inputs['Base Color']
    base=base[:3]+[inputs.get('Alpha',1)]
    require(close(pbr.get('baseColorFactor',[1,1,1,1]),base),'Base color factor changed')
    strength=inputs.get('Emission Strength',1)
    color=[1.,1.,1.] if 'Emission Color' in textures else inputs.get('Emission Color',[0,0,0])[:3]
    emission=np.array(color)*strength;ext=m.get('extensions',{})
    require(set(ext)<={'KHR_materials_emissive_strength'},'Unexpected material extension '+str(ext))
    actual=np.array(m.get('emissiveFactor',[0,0,0]))*ext.get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1)
    require(close(actual,emission),'Emission color/strength changed')
    require(not any(m.get(k) for k in ['normalTexture','occlusionTexture']) and not pbr.get('metallicRoughnessTexture'),'Unexpected PBR texture channel')
    used=[]
    for channel,container,key in [('Base Color',pbr,'baseColorTexture'),('Emission Color',m,'emissiveTexture')]:
        if channel not in textures:
            require(key not in container,'Unexpected '+key);continue
        require(key in container,'Missing '+key);ref=container[key]
        require(ref.get('texCoord',0)==0 and not ref.get('extensions'),'Unexpected UV channel/texture transform')
        tex=d['textures'][ref['index']];require(not tex.get('extensions'),'Unexpected texture extension')
        img=decoded['images'][tex['source']];s=textures[channel]
        require(img['sha256']==s['packed_sha256'] and img['size']==s['size'],'Image bytes/resolution changed: '+source['name']+' '+channel)
        sampler=d.get('samplers',[])[tex['sampler']] if 'sampler'in tex else {}
        wrap={'REPEAT':10497,'EXTEND':33071,'MIRROR':33648}.get(s['extension'])
        require(wrap is not None and sampler.get('wrapS',10497)==wrap and sampler.get('wrapT',10497)==wrap,'Image wrap changed')
        mag=9728 if s['interpolation']=='Closest' else 9729 if s['interpolation']=='Linear' else None
        require(mag is not None and sampler.get('magFilter',9729)==mag,'Image filtering changed')
        require(sampler.get('minFilter',9987) in ([9728,9984,9986] if mag==9728 else [9729,9985,9987]),'Image minification filtering changed')
        used.append({'channel':channel,'sha256':img['sha256'],'size':img['size'],'image_index':tex['source'],'sampler':sampler})
    return {'source_material':source['name'],'material_index':mi,'metallic':inputs['Metallic'],'roughness':inputs['Roughness'],
            'base_color_factor':base,'emission_effective':emission.tolist(),'double_sided':source['double_sided'],'images':used}

def concat(rows):
    def value(row,key):
        if key=='local_positions' and key not in row:
            # Snapshot 001 predates the redundant local array. Recover it from the
            # full precision world snapshot and retained source world matrix.
            # This is an invertible coordinate change, not a mesh alteration.
            m=np.array(row['world_matrix_godot'],float);p=np.asarray(row['positions'],float)
            return np.einsum('ij,tkj->tki',np.linalg.inv(m[:3,:3]),p-m[:3,3])
        return np.asarray(row[key],float)
    return {k:np.concatenate([value(r,k) for r in rows],axis=0) for k in ['positions','local_positions','normals','uvs']}

def match_triangles(expected,actual,check_local=True):
    ep,ap=expected['positions'],actual['positions'];eu,au=expected['uvs'],actual['uvs'];en,an=expected['normals'],actual['normals']
    require(ep.shape==ap.shape and eu.shape==au.shape and en.shape==an.shape,'Triangle/corner cardinality differs')
    require(ep.ndim==3 and ep.shape[1:]==(3,3),'Invalid triangle shape')
    n=len(ep);tree=cKDTree(ep.mean(axis=1));candidates=tree.query_ball_point(ap.mean(axis=1),r=POSITION_LIMIT)
    rows=[];cols=[];measurements={}
    for ai,possible in enumerate(candidates):
        for ei in possible:
            for shift in range(3):
                p=np.roll(ap[ai],-shift,axis=0);pd=float(np.max(np.linalg.norm(ep[ei]-p,axis=1)))
                if pd>POSITION_LIMIT:continue
                # UV export flips V and stores float32. Test the exact representable
                # result, rather than applying a broad UV epsilon at large UV values.
                uv=np.roll(au[ai],-shift,axis=0);expected_uv=eu[ei].astype(np.float32).astype(float)
                ud=float(np.max(np.abs(eu[ei]-uv)))
                if not np.array_equal(expected_uv,uv):continue
                nd=float(np.max(np.linalg.norm(en[ei]-np.roll(an[ai],-shift,axis=0),axis=1)))
                if nd>NORMAL_LIMIT:continue
                ld=0.
                if check_local:
                    ld=float(np.max(np.abs(expected['local_positions'][ei]-np.roll(actual['local_positions'][ai],-shift,axis=0))))
                    if ld>LOCAL_LIMIT:continue
                rows.append(ai);cols.append(ei);measurements[(ai,ei)]=(pd,ud,nd,ld,shift);break
        require(len(rows)>0 and rows[-1]==ai,'No cyclic-winding full-attribute source triangle for exported triangle '+str(ai))
    graph=csr_matrix((np.ones(len(rows),dtype=np.int8),(rows,cols)),shape=(n,n))
    match=maximum_bipartite_matching(graph,perm_type='column')
    require(len(match)==n and np.all(match>=0) and len(set(match))==n,'No complete triangle bijection; duplicated/lost topology')
    vals=[measurements[(ai,int(ei))] for ai,ei in enumerate(match)]
    return {'triangles':n,'corner_count':n*3,'max_position_deviation_m':max(v[0] for v in vals),
            'max_uv_float32_rounding':max(v[1] for v in vals),'max_normal_deviation':max(v[2] for v in vals),
            'max_local_coordinate_deviation_m':max(v[3] for v in vals),'local_coordinates_checked':check_local,
            'complete_bijection':True,'cyclic_winding_preserved':True,'uvs_exact_float32_export':True}

def run(a):
    s=json.loads(a.snapshot.read_text());require(s['source_bytes_unchanged'] and sha(s['source'])==s['source_sha256'],'Snapshot source pin changed')
    g=decode(a.glb);nodes=g['nodes'];source={o['name']:o for o in s['objects']};meshes={k:v for k,v in source.items() if v['type']=='MESH'}
    reports=[];material_reports={};mapping=[];markers=[]
    def group(label,parts,node):
        materials={meshes[p]['material'] for p in parts};require(len(materials)==1,'Mixed source material group: '+label)
        mat=next(iter(materials));mi={p['material'] for p in node['primitives']};require(len(mi)==1,'Mixed GLB material group: '+label);mi=next(iter(mi))
        if (mat,mi) not in material_reports:material_reports[(mat,mi)]=material_check(s['materials'][mat],mi,g)
        expected=concat([meshes[p] for p in parts]);actual=concat(node['primitives'])
        check_local=True
        if s['kind'] in ['envelope','architecture']:
            # Envelope's checked source has identity transforms, including joined
            # export batches. Explicitly verify this before comparing local corners.
            require(close(node['matrix'],np.eye(4)),'Envelope batch changed transform')
            require(all(close(meshes[p]['world_matrix_godot'],np.eye(4)) for p in parts),'Envelope source is not world-authored')
        else:compare_matrix(meshes[parts[0]],node)
        result=match_triangles(expected,actual,check_local)
        reports.append({'node':label,'source_parts':parts,'material':mat,**result})
        for p in parts:mapping.append({'source_part':p,'node':label,'material':mat,'collision_contract':meshes[p]['extras'].get('collision_contract')})
    if s['kind'] in ['envelope','architecture']:
        require(a.batches is not None and a.contract is not None,'Envelope requires --batches and --contract')
        batches=json.loads(a.batches.read_text());contract=json.loads(a.contract.read_text())
        require(batches['source_sha256']==s['source_sha256'] and batches['export_sha256']==sha(a.glb),'Batch receipt pins mismatch')
        records={p['name']:p for p in contract['parts']};require(set(records)==set(meshes),'Contract/source inventory mismatch')
        expected_groups={}
        for name,r in records.items():
            center=[(a+b)*.5 for a,b in zip(r['bounds_min_xyz'],r['bounds_max_xyz'])]
            key=(math.floor(center[0]/16),math.floor(center[1]/8),math.floor(center[2]/16),r['material_role'],r['collision_contract'],r.get('cast_shadow',True))
            expected_groups.setdefault(key,set()).add(name)
        require(len(batches['batches'])==len(expected_groups),'Batch count mismatch')
        seen=set();batch_names=set()
        for b in batches['batches']:
            name=b['name'];require(name in nodes and name not in batch_names,'Missing/duplicate runtime batch');batch_names.add(name)
            parts=b['source_parts'];require(parts and len(set(parts))==len(parts) and not seen.intersection(parts),'Duplicate source batch membership');seen.update(parts)
            require(set(parts) in expected_groups.values(),'Batch membership violates material/spatial/collision grouping')
            node=nodes[name];require(node['mesh'] is not None,'Batch is not a mesh')
            require(json.loads(node['extras'].get('source_part_names','null'))==parts,'Actual GLB source membership differs from batch receipt')
            for p in parts:
                r=records[p];require(b['material_role']==r['material_role'] and b['collision_contract']==r['collision_contract'] and b['cast_shadow']==r.get('cast_shadow',True),'Batch role/collision/shadow mismatch')
                require(meshes[p]['extras'].get('collision_contract')==r['collision_contract'],'Source collision contract changed')
            require(node['extras'].get('collision_contract')==b['collision_contract'] and node['extras'].get('cast_shadow')==b['cast_shadow'],'Actual collision/shadow batch metadata mismatch')
            group(name,parts,node)
        require(seen==set(meshes),'Missing source mesh from runtime batches')
        expected_nodes=batch_names|{n for n,o in source.items() if o['type']=='EMPTY'}
        require(set(nodes)==expected_nodes,'Unexpected/missing exported node inventory')
    else:
        require(set(nodes)==set(source),'Unexpected/missing exported hierarchy or reference contamination')
        for name,o in source.items():
            node=nodes[name];require(node['parent']==o['parent'],'Parent changed: '+name)
            compare_properties(o['extras'],node['extras'],name);compare_matrix(o,node)
            if o['type']=='MESH':require(node['mesh'] is not None,'Missing exported mesh');group(name,[name],node)
            else:require(node['mesh'] is None,'Unexpected mesh on source marker/root')
    part_to_node={m['source_part']:m['node'] for m in mapping}
    for name,o in source.items():
        if o['type']!='EMPTY':continue
        node=nodes[name];require(node['mesh'] is None and node['parent']==o['parent'],'Marker type/parent changed')
        compare_properties(o['extras'],node['extras'],name);err=compare_matrix(o,node)
        marker={'name':name,'max_matrix_deviation':err,'position_godot':node['matrix'][:3,3].tolist(),'properties_preserved':True}
        for k in ['physical_housing','physical_lens']:
            if k in o['extras']:
                require(o['extras'][k] in part_to_node,'Missing marker physical source part')
                marker[k+'_source_part']=o['extras'][k];marker[k+'_runtime_node']=part_to_node[o['extras'][k]]
        markers.append(marker)
    used_materials={r['material_index'] for r in material_reports.values()}
    require(used_materials==set(range(len(g['doc'].get('materials',[])))),'Unreferenced export material')
    used_images={im['image_index'] for r in material_reports.values() for im in r['images']}
    require(used_images==set(range(len(g['images']))),'Unreferenced or unchecked export image')
    return {'status':'PASS','kind':s['kind'],'source_sha256':s['source_sha256'],'snapshot_sha256':sha(a.snapshot),'glb_sha256':sha(a.glb),
            'source_meshes':len(meshes),'export_mesh_nodes':sum(n['mesh'] is not None for n in nodes.values()),'triangles':sum(r['triangles'] for r in reports),
            'position_limit_m':POSITION_LIMIT,'local_position_limit_m':LOCAL_LIMIT,'normal_limit':NORMAL_LIMIT,
            'max_position_deviation_m':max(r['max_position_deviation_m'] for r in reports),
            'max_local_coordinate_deviation_m':max(r['max_local_coordinate_deviation_m'] for r in reports),
            'max_uv_float32_rounding':max(r['max_uv_float32_rounding'] for r in reports),
            'max_normal_deviation':max(r['max_normal_deviation'] for r in reports),
            'materials':list(material_reports.values()),'markers_and_roots':markers,'triangle_groups':reports,'collision_node_mapping':mapping,
            'limits':['Actual decoded derivative only; runtime collision adoption/contacts and rendered readability remain separate gates.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--glb',type=Path,required=True)
    p.add_argument('--batches',type=Path);p.add_argument('--contract',type=Path);p.add_argument('--report',type=Path,required=True)
    a=p.parse_args();require(not a.report.exists(),'Preserve previous QA report; choose a new output')
    try:r=run(a)
    except Exception as e:r={'status':'FAIL','error':str(e),'traceback':traceback.format_exc(),'glb_sha256':sha(a.glb) if a.glb.exists() else None}
    a.report.parent.mkdir(parents=True,exist_ok=True)
    with a.report.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ['materials','markers_and_roots','triangle_groups','collision_node_mapping','traceback']},indent=2))
    if r['status']!='PASS':sys.exit(1)
if __name__=='__main__':main()
