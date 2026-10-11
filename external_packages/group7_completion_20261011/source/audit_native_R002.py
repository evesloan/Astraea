"""Read-only native integrity and source geometry audit, including immutable pins."""
from pathlib import Path
import bpy,json,hashlib,math,collections
P=Path(__file__).resolve().parents[1];R=P.parents[1];p=json.load(open(P/'docs/PLAN.json'));e=json.load(open(P/'docs/EXPORTS.json'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
before=sha(P/e['native']);bpy.ops.wm.open_mainfile(filepath=str(P/e['native']))
checks=0;errors=[];max_delta=0;triangles=collections.Counter();bounds={};source_cloud={}
for row in json.load(open(P/'qa/SOURCE_GEOMETRY_R002.json')):
    ob=bpy.data.objects.get(row['name']);assert ob and ob.type=='MESH',row['name']
    assert len(ob.data.vertices)==len(row['vertices_world_xyz']),row['name'];checks+=1
    for q,expect in zip(ob.data.vertices,row['vertices_world_xyz']):
        pt=ob.matrix_world@q.co;got=(pt.x,pt.z,-pt.y);delta=max(abs(a-b)for a,b in zip(got,expect));max_delta=max(max_delta,delta);assert delta<.0001,(row['name'],delta);checks+=1
    assert ob['contact_category']==row['category']and ob['group7_cell']==row['cell'];checks+=2
    assert ob.data.uv_layers.active
    for uv in ob.data.uv_layers.active.data:assert all(math.isfinite(q)for q in uv.uv);checks+=1
for ob in bpy.context.scene.objects:
    if ob.type!='MESH'or'group7_cell'not in ob:continue
    cell=ob['group7_cell'];ob.data.calc_loop_triangles();triangles[cell]+=len(ob.data.loop_triangles)
    points=[]
    for v in ob.data.vertices:
        pt=ob.matrix_world@v.co;q=(pt.x,pt.z,-pt.y);points.append(q)
        if cell not in bounds:bounds[cell]=[list(q),list(q)]
        else:
            for i in range(3):bounds[cell][0][i]=min(bounds[cell][0][i],q[i]);bounds[cell][1][i]=max(bounds[cell][1][i],q[i])
    source_cloud.setdefault(cell,[]).extend(points)
images=[]
for im in bpy.data.images:
    if im.name=='Render Result':continue
    assert im.packed_file,im.name;assert im.size[0]>0 and im.size[1]>0
    images.append({'name':im.name,'size':list(im.size),'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest()});checks+=2
for path,pin in p['source_pins'].items():assert sha(R/path)==pin,path;checks+=1
assert before==sha(P/e['native']);checks+=1
(P/'qa/NATIVE_POINT_CLOUD.json').write_text(json.dumps(source_cloud,separators=(',',':'))+'\n')
report={'status':'PASS','checks':checks,'native_sha256':before,'native_not_resaved':True,'authored_vertices_max_error_m':max_delta,'cell_triangles':dict(triangles),'cell_bounds':bounds,'packed_images':images,'source_pins_unchanged':True,'original_native_export_files_unmodified':True,'scope':'Read-only final native, complete authored vertices/UV finite values, cell triangles/bounds, packed images and exact retained source pins. Not structural capacity or final art acceptance.'}
(P/'qa/NATIVE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print('GROUP7_NATIVE_AUDIT_PASS',checks,max_delta)
