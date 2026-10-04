"""Original editable swept balcony bay for Astraea. Draft; not an approved room.
Blender metres/Z-up. Origin is start of outer walking edge; tangent +X, depth +Y.
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT.parents[1]
RADIUS=10.0; ANGLE=math.radians(30); SEGMENTS=12; WIDTH=4.2
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for role in ['ivory_enamel','warm_stone','warm_walnut','champagne_metal','dark_rubber']:
    mat=bpy.data.materials.new(role);mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.68
    if role=='champagne_metal':bsdf.inputs['Metallic'].default_value=.5;bsdf.inputs['Roughness'].default_value=.4
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(CAT/'materials'/f'{role}.png'));tex.interpolation='Closest'
    mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);materials[role]=mat
mat=bpy.data.materials.new('gallery_glass');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.23,.49,.51,1);bsdf.inputs['Alpha'].default_value=.23;bsdf.inputs['Roughness'].default_value=.22
mat.diffuse_color=(.23,.49,.51,.23);mat.surface_render_method='DITHERED';materials['gallery_glass']=mat
parts=[]
def mesh(name,vertices,faces,role,uvs=None):
    data=bpy.data.meshes.new(name+'_mesh');data.from_pydata(vertices,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[role]);parts.append(ob)
    layer=data.uv_layers.new(name='AuthoredUV')
    for face in data.polygons:
        for li in face.loop_indices:
            index=data.loops[li].vertex_index;v=data.vertices[index].co
            layer.data[li].uv=uvs[index] if uvs else (v.x*.5,v.y*.5+v.z*.5)
    return ob

def point(theta,depth,height):
    return ((RADIUS-depth)*math.sin(theta),RADIUS-(RADIUS-depth)*math.cos(theta),height)

def sweep(name,profile,role,start=0,end=ANGLE,steps=SEGMENTS):
    verts=[];uv=[];n=len(profile);perimeter=[0.0]
    for i in range(1,n):perimeter.append(perimeter[-1]+math.dist(profile[i-1],profile[i]))
    for i in range(steps+1):
        angle=start+(end-start)*i/steps
        for j,(depth,height) in enumerate(profile):
            verts.append(point(angle,depth,height));uv.append((RADIUS*angle*.5,perimeter[j]*.5))
    faces=[tuple(reversed(range(n))),tuple(steps*n+j for j in range(n))]
    for i in range(steps):
        for j in range(n):k=(j+1)%n;faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    return mesh(name,verts,faces,role,uv)

sweep('ARC_Floor',[(.34,0),(WIDTH,0),(WIDTH,-.24),(.34,-.24)],'warm_stone')
sweep('ARC_ProfiledFascia',[(0,0),(.34,0),(.34,-.47),(.27,-.6),(.15,-.66),(.06,-.62),(0,-.49)],'ivory_enamel')
sweep('ARC_RecessedSoffit',[(.35,-.24),(WIDTH-.16,-.24),(WIDTH-.16,-.29),(.35,-.29)],'warm_walnut')
sweep('ARC_LowerShadowReveal',[(.03,-.5),(.065,-.5),(.065,-.53),(.03,-.53)],'dark_rubber')
sweep('ARC_GuardPlinth',[(.01,0),(.43,0),(.43,.14),(.32,.21),(.1,.21),(.01,.13)],'ivory_enamel')
sweep('ARC_ContinuousHandrail',[(.115,1.10),(.14,1.08),(.29,1.08),(.315,1.10),(.315,1.13),(.29,1.15),(.14,1.15),(.115,1.13)],'warm_walnut')
sweep('ARC_HandrailMetalSeat',[(.17,1.055),(.26,1.055),(.26,1.08),(.17,1.08)],'champagne_metal')
for i in range(4):
    start=ANGLE*i/4+.003;end=ANGLE*(i+1)/4-.003
    sweep(f'ARC_Glass_{i:02d}',[(.218,.235),(.236,.235),(.236,1.055),(.218,1.055)],'gallery_glass',start,end,3)
for i in range(5):
    angle=ANGLE*i/4;cx,cy,_=point(angle,.225,0);verts=[]
    levels=[(.16,.055),(.21,.045),(1.055,.027),(1.10,.035)]
    for height,radius in levels:
        for j in range(8):
            t=2*math.pi*j/8;verts.append((cx+radius*math.cos(t),cy+radius*math.sin(t),height))
    faces=[tuple(reversed(range(8))),tuple(24+j for j in range(8))]
    for k in range(3):
        for j in range(8):faces.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
    mesh(f'ARC_Post_{i:02d}',verts,faces,'champagne_metal')
for i,angle in enumerate([ANGLE/3,ANGLE*2/3]):
    # Short solid cantilever ribs remain entirely below the walking surface.
    sweep(f'ARC_UndersideRib_{i}',[(.28,-.2),(WIDTH-.12,-.2),(WIDTH-.12,-.38),(1.15,-.7),(.28,-.7)],'ivory_enamel',angle-.007,angle+.007,1)
for name,angle in [('START',0),('END',ANGLE)]:
    ob=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(ob);ob.location=point(angle,0,0);ob.rotation_euler.z=angle
    ob['connection']='Floor edge Z0; tangent +X in local socket frame. Hide one coincident post for repeated joins.'
for name,depth,height in [('FLOOR_START',.34,0),('CLEAR_INNER',WIDTH,0),('GUARD_TOP',.225,1.15)]:
    ob=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(ob);ob.location=point(0,depth,height)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
for ob in bpy.context.scene.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.file.pack_all()
blend=ROOT/'source'/'AST-ARC-001.blend';glb=ROOT/'exports'/'AST-ARC-001.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
vertices=[ob.matrix_world@Vector(v) for ob in parts for v in ob.bound_box]
lo=[min(v[i] for v in vertices) for i in range(3)];hi=[max(v[i] for v in vertices) for i in range(3)]
triangles=0
for ob in parts:ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles)
assert WIDTH-.43>=3.4
assert hi[2]<=1.15001 and lo[2]>=-.701
result={'catalogue_id':'AST-ARC-001','name':'Swept gallery bay with profiled fascia and restrained glazed guard','status':'Draft original design; component and in-engine fit review pending','unique_design':True,'source':str(blend.relative_to(ROOT)),'export':str(glb.relative_to(ROOT)),'generator':'source/build_swept_terrace.py','radius_m':RADIUS,'angle_degrees':30,'floor_width_m':WIDTH,'usable_floor_width_m':WIDTH-.43,'source_axes':'Blender XYZ, Z up; +X tangent at start, +Y inward depth','native_glb_mapping':'(x,y,z)->(x,z,-y)','source_bounds':{'min':lo,'max':hi},'triangles':triangles,'semantic_mesh_parts':[o.name for o in parts],'source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'collision_policy':'Static floor and guard surfaces only; never one convex hull across the curved open side. Body and cart route acceptance still pending.','join_policy':'End socket receives next start socket; omit one duplicate endpoint post. Floor ownership must replace, not overlap, authored slab. Source geometry remains editable.','design_count_note':'One authored design; copies/rotation/joins are not new designs.'}
(ROOT/'AST-ARC-001.manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print('ARC_SOURCE_CREATED',triangles,lo,hi)
