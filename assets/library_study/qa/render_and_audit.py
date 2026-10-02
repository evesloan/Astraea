"""Reload editable sources, then render actual imported GLBs in <=3 views."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent;QA=ROOT/'qa';BASE=ROOT.parent.parent

def points(ob,dg):
    eo=ob.evaluated_get(dg);me=eo.to_mesh();vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];me.calc_loop_triangles();tri=len(me.loop_triangles);eo.to_mesh_clear();return vs,tri

def audit(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));mf=json.loads(path.with_suffix('.manifest.json').read_text());dg=bpy.context.evaluated_depsgraph_get();allv=[];tris=0;parts=[];bad=[]
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        vs,tr=points(ob,dg);allv+=vs;tris+=tr
        lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
        parts.append((ob.name,lo,hi))
        if ob.matrix_world.determinant()<=0:bad.append(ob.name+': nonpositive transform')
        if not ob.data.uv_layers.active:bad.append(ob.name+': missing source UV')
    lo=[min(v[k] for v in allv) for k in range(3)];hi=[max(v[k] for v in allv) for k in range(3)]
    clearance=[]
    for volume in mf['clear_volumes_m']:
        collisions=[]
        for name,a,b in parts:
            if all(min(b[k],volume['max'][k])-max(a[k],volume['min'][k])>1e-6 for k in range(3)):collisions.append(name)
        clearance.append({'name':volume['name'],'part_AABB_intersections':collisions,'pass':not collisions})
        if collisions:bad.append('Clear volume intersects '+','.join(collisions))
    if abs(lo[2])>1e-7:bad.append('Not on floor')
    if tris!=mf['triangles_evaluated']:bad.append('Triangle count mismatch')
    packed=[]
    for im in bpy.data.images:
        if im.source!='FILE':continue
        ok=bool(im.packed_file);packed.append({'image':im.name,'packed':ok,'size':list(im.size)})
        if not ok:bad.append('Unpacked image '+im.name)
    report={'source':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reloaded':True,'min_m':lo,'max_m':hi,'triangles':tris,'semantic_parts':len(parts),'clearance_AABB_check':clearance,'packed_images':packed,'issues':bad,'status':'PASS' if not bad else 'FAIL'}
    (QA/(mf['catalogue_id']+'_source_reload.json')).write_text(json.dumps(report,indent=2));assert not bad,report

def point(ob,p):ob.rotation_euler=(Vector(p)-ob.location).to_track_quat('-Z','Y').to_euler()
def material(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.85;return m
def studio():
    s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_percentage=100
    s.world=bpy.data.worlds.new('QA_neutral_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.44,.47,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(material('QA_neutral_floor',(.19,.205,.22)))
    for name,loc,power,size in [('key',(-3,-4,5.8),700,5),('fill',(4,-1,3.4),420,4),('rim',(-1,4,4),500,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.name='QA_ONLY_'+name;ob.data.energy=power;ob.data.shape='DISK';ob.data.size=size;point(ob,(0,0,.7))
    bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='QA_ONLY_camera';s.camera=cam;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';return cam
def import_glb(path,origin=(0,0,0),yaw=0,prefix='QA'):
    before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));added=set(bpy.context.scene.objects)-before
    root=bpy.data.objects.new(prefix+'_placement',None);bpy.context.collection.objects.link(root)
    for ob in added:
        if ob.parent is None:ob.parent=root
    root.location=origin;root.rotation_euler.z=math.radians(yaw);return added
def render(cam,name,loc,target,size,lens):
    s=bpy.context.scene;cam.location=loc;point(cam,target);cam.data.lens=lens;s.render.resolution_x=size[0];s.render.resolution_y=size[1];s.render.filepath=str(QA/name);bpy.ops.render.render(write_still=True)

def main():
    for p in sorted(ROOT.glob('*.blend')):audit(p)
    print('ALL_EDITABLE_SOURCES_RELOAD_PASS',flush=True)
    api=json.loads((ROOT/'integration_api.json').read_text());chair=BASE/'assets/furniture/AST-FUR-002_day_reading_chair.glb'
    for i,rec in enumerate(api):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        glb=next(ROOT.glob(rec['catalogue_id']+'_*.glb'));import_glb(glb,prefix=rec['catalogue_id']);cam=studio()
        added=[]
        for j,c in enumerate(rec['approach']['candidate_chairs']):added.extend(import_glb(chair,c['origin_m'],c['rotation_z_degrees'],'QA_reused_chair_'+str(j)))
        if i==0:render(cam,'01_shared_chair_context_640.png',(3.45,-4.5,2.67),(0,0,.6),(640,360),42)
        else:
            render(cam,'02_single_chair_context_640.png',(2.50,-3.65,1.90),(-.10,-.10,.67),(640,360),42)
            for ob in added:ob.hide_render=True
            render(cam,'02_single_join_detail_1280.png',(2.40,-2.15,1.66),(-.23,.025,.70),(1280,720),57)
    print('IMPORTED_GLB_RENDER_COMPLETE',flush=True)

if __name__=='__main__':main()
