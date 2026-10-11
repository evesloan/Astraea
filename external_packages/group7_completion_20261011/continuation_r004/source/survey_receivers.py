"""Read actual retained native boundary meshes; never resave an input."""
import bpy,json,hashlib,sys,itertools
from pathlib import Path
import numpy as np

P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
OLD=C.parent/'group7_hull_atrium_20261009/continuation_r002'
inputs=[C/'source/natives/G7_Completion_r003.blend']
rows=[];pins={}
def relevant(lo,hi,term):
    if not any(lo[2]<=z+.85 and hi[2]>=z-.85 for z in [-510,510]):return False
    if hi[1]<60.8 or lo[1]>110.8:return False
    end=65 if term=='Fore' else 49;start=70.92 if term=='Fore' else 54.175
    width=start+(end-start)*(min(106.5,max(69.5,hi[1]))-69.5)/37
    return max(abs(lo[0]),abs(hi[0]))>=width-1.5 or (lo[1]<69.8 and hi[1]>69.35) or (lo[1]<106.8 and hi[1]>106.2) or (lo[0]<7.25 and hi[0]>-7.25 and hi[1]>106.2)
for file in inputs:
    before=hashlib.sha256(file.read_bytes()).hexdigest();pins[file.relative_to(R).as_posix()]=before
    bpy.ops.wm.open_mainfile(filepath=str(file))
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        category=ob.get('contact_category','')
        if not category.startswith('solid_'):continue
        pts=[ob.matrix_world@q.co for q in ob.data.vertices]
        a=np.array([(q.x,q.z,-q.y)for q in pts]);lo=a.min(axis=0);hi=a.max(axis=0)
        term='Fore'if (lo[2]+hi[2])<0 else'Aft'
        if not relevant(lo,hi,term):continue
        rows.append({'source_mode':'ACTUAL_NATIVE_R003','native':file.relative_to(R).as_posix(),'name':ob.name,'terminal':term,'category':category,'vertices_world_xyz':a.tolist(),'faces':[list(f.vertices)for f in ob.data.polygons],'minimum':lo.tolist(),'maximum':hi.tolist()})
    assert hashlib.sha256(file.read_bytes()).hexdigest()==before
sys.path.insert(0,str(OLD.parent/'source'))
from check_retained_exports import read,acc,nodes
checks=0
for term in ['Fore','Aft']:
    native=OLD/('source/natives/G7C2_'+term+'_Terminal_r002.blend')
    glb=OLD/('exports/terminal/G7C2_'+term+'_Architecture_r002.glb')
    geometry=OLD/('qa/G7C2_'+term+'_geometry.json')
    for file in [native,glb,geometry]:pins[file.relative_to(R).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
    d,b=read(glb);cloud={}
    for n,m in nodes(d):
        cat=n.get('extras',{}).get('contact_category','')
        if not cat.startswith('solid_'):continue
        for prim in d['meshes'][n['mesh']]['primitives']:
            a=acc(d,b,prim['attributes']['POSITION']);a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3]
            cloud.setdefault(cat,set()).update(tuple(q)for q in np.round(a/.0001).astype(int))
    for row in json.loads(geometry.read_text()):
        cat=row['contact_category'];a=np.array(row['vertices_world_xyz']);lo=a.min(axis=0);hi=a.max(axis=0)
        if not cat.startswith('solid_') or not relevant(lo,hi,term):continue
        for q in np.round(a/.0001).astype(int):
            assert any(tuple(q+off)in cloud[cat]for off in itertools.product([-1,0,1],repeat=3)),row['object'];checks+=1
        faces=[]
        if row['object'].endswith('_SteppedRoof'):
            count=len(a)//2;faces=[list(reversed(range(count))),list(range(count,2*count))]+[[i,(i+1)%count,(i+1)%count+count,i+count]for i in range(count)]
        rows.append({'source_mode':'RETAINED_NATIVE_RECORD_VERTICES_CORROBORATED_DECODED_GLB','native':native.relative_to(R).as_posix(),'export':glb.relative_to(R).as_posix(),'name':row['object'],'terminal':term,'category':cat,'vertices_world_xyz':a.tolist(),'faces':faces,'minimum':lo.tolist(),'maximum':hi.tolist()})
report={'status':'ACTUAL_NATIVE_R003_AND_GLB_CORROBORATED_RETAINED_RECEIVERS_READ_ONLY','source_pins':pins,'receiver_parts':rows,'retained_vertex_glb_matches':checks,'retained_vertex_quantization_m':.0001,'retained_terminal_native_format':'BLENDER17-01v0501','provided_blender':'4.3.2','retained_terminal_native_direct_read':'HELD_UNSUPPORTED_FORMAT_FAILED_SURVEY002','retained_native_resaves':0,'pressure_or_capacity_accepted':False}
(P/'qa/ACTUAL_RECEIVERS.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
print('G7_R004_ACTUAL_NATIVE_RECEIVERS',len(rows),'pins',pins)
