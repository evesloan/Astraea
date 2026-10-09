"""Read-only conservative AABB audit of actual retained GLB receiver meshes."""
from pathlib import Path
import json,struct,hashlib,math
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2];GAME=ROOT/'Game'
def identity():return [[1. if i==j else 0. for j in range(4)]for i in range(4)]
def mm(a,b):return [[sum(a[i][k]*b[k][j]for k in range(4))for j in range(4)]for i in range(4)]
def trs(node):
    if 'matrix'in node:return [[node['matrix'][j*4+i]for j in range(4)]for i in range(4)]
    x,y,z,w=node.get('rotation',[0,0,0,1]);s=node.get('scale',[1,1,1]);t=node.get('translation',[0,0,0])
    a=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],[0,0,0,1]]
    for i in range(3):
        for j in range(3):a[i][j]*=s[j]
    return a
def point(m,p):return [sum(m[i][j]*p[j]for j in range(3))+m[i][3]for i in range(3)]
def glb_bounds(path,translation):
    b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);result=[]
    root=identity()
    for i,t in enumerate(translation):root[i][3]=t
    def visit(i,parent):
        node=g['nodes'][i];world=mm(parent,trs(node))
        if 'mesh'in node:
            for primitive in g['meshes'][node['mesh']]['primitives']:
                a=g['accessors'][primitive['attributes']['POSITION']];lo=a['min'];hi=a['max']
                corners=[point(world,[x,y,z])for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]]
                result.append({'node':node.get('name',str(i)),'bounds':[min(p[0]for p in corners),max(p[0]for p in corners),min(p[1]for p in corners),max(p[1]for p in corners),min(p[2]for p in corners),max(p[2]for p in corners)]})
        for child in node.get('children',[]):visit(child,world)
    for i in g['scenes'][g.get('scene',0)]['nodes']:visit(i,root)
    return result,hashlib.sha256(b).hexdigest()
def volume(a,b):return math.prod(max(0,min(a[i+1],b[i+1])-max(a[i],b[i]))for i in [0,2,4])
models=[]
received=json.loads((GAME/'data/architecture/received_sections.json').read_text())
for row in received['sections']:
    if row['programme_key'].startswith('D05'):
        models.append({'programme':row['programme_key'],'file':row['model_file'],'translation':row['translation_xyz']})
remaining=json.loads((GAME/'data/architecture/REMAINING_BATCH_SECTIONS.json').read_text())
for row in remaining['sections']:
    if row['key'].startswith('D05'):
        models.append({'programme':row['key'],'file':Path(row['runtime']).name,'translation':row['position']})
welcome=json.loads((GAME/'data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json').read_text())
models.append({'programme':'D05_directory_01','file':welcome['architecture_file'],'translation':welcome['origin_xyz']})
terminals=json.loads((HERE/'source/CLINICAL_TERMINALS.json').read_text());report=[]
for model in models:
    path=GAME/'assets/models'/model['file'];bounds,sha=glb_bounds(path,model['translation'])
    local=[]
    for joint in terminals['terminal_interfaces']:
        if joint['programme_key']!=model['programme']:continue
        x,y,z=joint['source_origin'];query=[x-.3,x+.3,21,23.4,z-1.8,z+1.8]
        hits=[{'node':p['node'],'bounds':p['bounds'],'conservative_overlap_m3':volume(p['bounds'],query)}for p in bounds if volume(p['bounds'],query)>1e-7 and p['bounds'][3]>21.05]
        local.append({'role':joint['role'],'receiver_query_box':query,'mesh_bound_candidates':hits,'state':'Exact triangles and a reversible aperture must be checked by root before integration'if hits else'No AABB candidates in narrow receiver query; actual receiver access remains unverified'})
    report.append({'programme':model['programme'],'file':model['file'],'sha256':sha,'translation':model['translation'],'retained_native_mesh_bound_count':len(bounds),'terminals':local})
out={'schema':1,'method':'Actual GLB node TRS and position-accessor bounds, plus existing runtime placements. Conservative bounds candidates are not exact triangle intersection tests.','retained_models':report,'all_sources_modified':False,'scope':'Read-only native receiver inventory. Existing rear panels remain retained; new terminal source is held until real aperture and floor receiving checks.'}
(HERE/'qa/RETAINED_CLINICAL_RECEIVER_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'models':len(report),'terminal_checks':sum(len(r['terminals'])for r in report),'candidate_nodes':sum(len(t['mesh_bound_candidates'])for r in report for t in r['terminals'])}))
