"""Enclose the retained maker fit-out within its own floor and recorded roof cap."""
from pathlib import Path
import ast,bpy,bmesh,json,hashlib,importlib.util,shutil
import numpy as np
from mathutils import Vector
from shapely.geometry import Polygon
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CAT=P.parents[1]
native=P/'source/maker_foyer/maker_ceiling_enclosure_r001.blend';export=P/'exports/maker_foyer/maker_ceiling_enclosure_r001.glb'
assert not native.exists() and not export.exists(),'Saved source revisions immutable'
spec=importlib.util.spec_from_file_location('palette',CAT/'standards/retail_materials.py');palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
t=P/'source/build_components.py';tree=ast.parse(t.read_text());FACES=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='FACES' for a in n.targets)))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']],type_ignores=[]),str(t),'exec'),globals())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);root=empty('GROUP5_MAKER_CEILING_ENCLOSURE')
floor_path=ROOT/'Game/data/generated/received_structural_meshes.json';floor=next(r for r in json.loads(floor_path.read_text())['regions'] if r['id']=='D09_directory_05_authored_floor');polygon=Polygon(floor['rings'][0])
def mesh(name,points,faces,role):
    data=bpy.data.meshes.new(name);data.from_pydata([(x,-z,y-52.5) for x,y,z in points],[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(M[role]);uv=data.uv_layers.new(name='MetricUV')
    for face in data.polygons:
        axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=axis]
        for li in face.loop_indices:
            v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj);obj.parent=root;return obj
for i,tri in enumerate(floor['triangles']):
    points=[(x,y,z) for y in [58.28,58.46] for x,z in tri]
    mesh('MakerCeilingPanel_'+str(i),points,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'ivory_enamel')
# Mitered nested rings make every cove corner join its neighbors exactly.
profile=[(.16,58.26),(.22,58.22),(.33,58.11),(.45,58.02),(.62,58.00),(.62,58.06),(.50,58.08),(.38,58.18),(.27,58.30),(.16,58.34)]
ring=floor['rings'][0];rings=[]
for offset,y in profile:
    inset=polygon.buffer(-offset,join_style=2);vertices=list(inset.exterior.coords)[:-1];assert len(vertices)==len(ring)
    ordered=[min(vertices,key=lambda p:(p[0]-r[0])**2+(p[1]-r[1])**2) for r in ring];assert len(set(ordered))==len(ring);rings.append(ordered)
for i in range(len(ring)):
    k=(i+1)%len(ring);points=[]
    for endpoint in [i,k]:points.extend([(verts[endpoint][0],y,verts[endpoint][1]) for verts,(_,y) in zip(rings,profile)])
    n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    mesh('MakerMiteredCove_'+str(i),points,faces,'warm_walnut')
def block(name,x0,x1,y0,y1,z0,z1,role):return cube(name,(x0,y0-52.5,z0),(x1,y1-52.5,z1),role,root)
# Side fields bear on the original low fore entry walls. A higher central
# transom preserves a4.9m public opening; the deeper canopy clears the3.9m door.
block('MakerForeUpperSouth',-56.67,-56.33,56.075,58.325,-24,-4.5,'ivory_enamel')
block('MakerForeUpperNorth',-56.67,-56.33,56.075,58.325,4.5,24,'ivory_enamel')
block('MakerForeRaisedTransom',-56.67,-56.33,57.40,58.325,-4.5,4.5,'retail_terracotta_enamel')
block('MakerRecessCanopy',-60.44,-56.50,56.85,57.03,-4.50,4.50,'ivory_enamel')
for z in [-1,1]:
    a,b=sorted([z*4.25,z*4.40])
    block('MakerCanopyBearing_'+str(z),-60.44,-56.56,56.475,56.875,a,b,'warm_walnut')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']='Existing maker floor enclosure with mitered coves,side upper fields and supported entrance canopy;no hull/sharedfloor/registry mutation or engineering sizing acceptance'
native.parent.mkdir(exist_ok=True);export.parent.mkdir(exist_ok=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-maker-ceiling-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True)
assert sha(repeat)==esha and sha(native)==nsha
target=ROOT/'Game/assets/models/group5/maker_foyer'/export.name;assert not target.exists();shutil.copyfile(export,target)
row={'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/maker_foyer/'+export.name,'model_sha256':esha,'origin_world_xyz':[0,52.5,0],'mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects),'maximum_top_y':58.46,'recorded_original_roof_cap_y':60.45,'main_underside_y':58.28,'canopy_underside_y':56.85,'door_track_top_y':56.64,'source_floor_owner':floor['id'],'source_floor_sha256':sha(floor_path),'fresh_native_repeat_export_byte_identical':True,'shared_source_changes':0,'scope':'Room enclosure/first-pass cove and canopy only;source bearing/interference and optical/controller tests separate;structural sizing,hull/species/CRT/hardware/final-art acceptance held'}
(P/'docs/MAKER_CEILING_ENCLOSURE.json').write_text(json.dumps(row,indent=2)+'\n');print('MAKER_CEILING_SOURCE_PASS',row['mesh_count'],esha)
