"""Fresh-process native reopen, actual GLB bounds check, optional source-only eye renders.
blender -b -t 2 --python source/review_section.py -- --render 01_arrival,03_changing_spine
"""
from pathlib import Path
import bpy,json,struct,sys,argparse,hashlib
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--render',default='');ap.add_argument('--samples',type=int,default=20)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
src=ROOT/'source/WP02_sports_care.blend';glb=ROOT/'exports/WP02_sports_care.glb'
bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
pts=[]
authored_signs=sorted(o.name for o in bpy.data.collections['WP02_ARCHITECTURE'].objects if o.type=='FONT')
assert authored_signs,'No authored native signage found'
for o in bpy.data.collections['WP02_ARCHITECTURE'].objects:
    if o.type not in {'MESH','CURVE','FONT'}:continue
    e=o.evaluated_get(dg);me=e.to_mesh()
    for v in me.vertices:
        q=e.matrix_world@v.co;pts.append((q.x,q.z,-q.y))
    e.to_mesh_clear()
def bounds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
sb=bounds(pts)
data=glb.read_bytes();magic,version,length=struct.unpack_from('<4sII',data,0);assert magic==b'glTF' and version==2
pos=12;doc=None;binary=None
while pos<len(data):
    n,t=struct.unpack_from('<II',data,pos);chunk=data[pos+8:pos+8+n];pos+=8+n
    if t==0x4E4F534A:doc=json.loads(chunk)
    elif t==0x004E4942:binary=chunk
def acc(idx):
    a=doc['accessors'][idx];bv=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126
    n={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];stride=bv.get('byteStride',n*4);off=bv.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+'f'*n,binary,off+i*stride) for i in range(a['count'])]
gp=[];names=[]
def visit(i,parent):
    node=doc['nodes'][i];names.append(node.get('name',''))
    if 'matrix' in node:local=Matrix([node['matrix'][j::4] for j in range(4)])
    else:
        t=Matrix.Translation(Vector(node.get('translation',[0,0,0])));r=node.get('rotation',[0,0,0,1]);rot=Quaternion((r[3],r[0],r[1],r[2])).to_matrix().to_4x4();s=node.get('scale',[1,1,1]);local=t@rot@Matrix.Diagonal(Vector((*s,1)))
    world=parent@local
    if 'mesh' in node:
        for prim in doc['meshes'][node['mesh']]['primitives']:
            for v in acc(prim['attributes']['POSITION']):gp.append(tuple(world@Vector(v)))
    for c in node.get('children',[]):visit(c,world)
for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,Matrix.Identity(4))
gb=bounds(gp);delta=max(abs(sb[k][i]-gb[k][i]) for k in (0,1) for i in range(3))
exported_mesh_names={node.get('name','') for node in doc['nodes'] if 'mesh' in node}
missing_authored_signs=sorted(set(authored_signs)-exported_mesh_names)
signage_exported=not missing_authored_signs

inside=sb[0][0]>=-.003 and sb[1][0]<=46.003 and sb[0][2]>=-62.003 and sb[1][2]<=6.003 and sb[0][1]>=-.003 and sb[1][1]<=8.003
# Source y range[-6,62] maps GLB z[-62,6]. No outside guest link or extra floor exported.
floor_excluded=not any('SOURCE_PREVIEW_ONLY' in n for n in names)
images_ok=all(im.packed_file or im.source!='FILE' for im in bpy.data.images)
receipt={'scope':'source/native/export QA only','native_reopen':True,'blender_version':bpy.app.version_string,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(data).hexdigest(),'source_glb_frame_bounds':sb,'actual_glb_bounds':gb,'bound_delta_m':delta,'within_allocation_and_single_deck':inside,'source_preview_floor_excluded_from_glb':floor_excluded,'all_native_file_images_packed':images_ok,'live_physics':False,'visual_acceptance':'pending human/parent inspection','authored_native_signs':authored_signs,'missing_authored_glb_signs':missing_authored_signs,'all_authored_signage_exported':signage_exported,'passed':inside and floor_excluded and images_ok and delta<.003 and signage_exported}
(ROOT/'qa/native_export_review.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
for camera in filter(None,args.render.split(',')):
    sc=bpy.context.scene;sc.camera=bpy.data.objects['REVIEW_'+camera];sc.cycles.samples=args.samples;sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=75;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(ROOT/'renders'/f'{camera}_source_only.png');bpy.ops.render.render(write_still=True)
assert receipt['passed'],'WP02 source QA failed; inspect receipt before adoption'
