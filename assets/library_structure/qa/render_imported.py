"""Imported GLB-only structure evidence; optional linked independent stock.

blender -b -t 2 --python qa/render_imported.py -- --stock /path/group.glb
No generated inspection scene is an additional artistic asset or a ship room.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector, Matrix
BASE=Path(__file__).resolve().parents[1]
CAT=BASE.parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
stock_path=Path(args[args.index('--stock')+1]) if '--stock' in args else None
views=args[args.index('--views')+1].split(',') if '--views' in args else ['neutral','standing','detail','terminal']

def import_glb(path):
    existing=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [ob for ob in bpy.data.objects if ob not in existing and ob.type=='MESH']

def point(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()

def stage():
    sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=32
    sc.cycles.samples=24;sc.cycles.use_denoising=False
    sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_percentage=100
    sc.world=bpy.data.worlds.new('Component QA neutral world');sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.37,.40,.45,1)
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
    mat=bpy.data.materials.new('QA_ONLY_neutral_floor');mat.use_nodes=True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.18,.21,.235,1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
    bpy.ops.mesh.primitive_plane_add(size=200,location=(2,0,-.006));bpy.context.object.data.materials.append(mat)
    bpy.context.object.name='QA_ONLY_neutral_floor'
    for name,loc,power,size in [('key',(-2,-4,7),1150,5),('fill',(7,-2,5),850,5),('rear',(1,6,5),1000,4)]:
        data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data)
        bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;point(ob,(2.5,.4,1.6))
    data=bpy.data.cameras.new('QA_ONLY_camera');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);sc.camera=ob
    return ob

def render(cam,name,location,target,res,ortho=None,lens=48):
    sc=bpy.context.scene;cam.location=location;point(cam,target)
    cam.data.type='ORTHO' if ortho else 'PERSP'
    if ortho:cam.data.ortho_scale=ortho
    cam.data.lens=lens;sc.render.resolution_x,sc.render.resolution_y=res
    sc.render.image_settings.file_format='PNG';sc.render.filepath=str(BASE/'qa'/f'{name}.png')
    bpy.ops.render.render(write_still=True)

def main():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    api=json.loads((BASE/'stock_anchors.json').read_text());stock_templates=[];stock_paths=[]
    if stock_path:
        stock_paths=[stock_path]
        for suffix in ['_reordered','_short_flat']:
            variant=stock_path.with_name(stock_path.stem+suffix+'.glb')
            if variant.exists():stock_paths.append(variant)
        for p in stock_paths:
            group=import_glb(p);stock_templates.append(group)
            # Save imported origins; these are floor/shelf-base stock assets.
            for ob in group:ob.hide_render=True;ob.hide_set(True)
    count=0;variant_counts={p.name:0 for p in stock_paths}
    for asset_index,inst in enumerate(api['assembly_instances']):
        yaw=math.radians(inst['rotation_z_degrees']);T=Matrix.Translation(Vector(inst['translation_m']))@Matrix.Rotation(yaw,4,'Z')
        for ob in import_glb(BASE/'exports'/f"{inst['id']}.glb"):
            ob.matrix_world=T@ob.matrix_world;ob.name=inst['id']+'_'+ob.name
        for anchor in api['assets'][inst['id']]:
            A=T@Matrix.Translation(Vector(anchor['position_m']))@Matrix.Rotation(math.radians(anchor['rotation_z_degrees']),4,'Z')
            level=int(anchor['id'].split('_s')[1][:2])-1;cell=int(anchor['id'].split('_c')[1])-1
            variant=(2*level+cell+level//2+asset_index)%len(stock_templates) if stock_templates else 0
            for template in stock_templates[variant] if stock_templates else []:
                ob=template.copy();ob.data=template.data;bpy.context.collection.objects.link(ob)
                ob.name='QA_STOCK_'+anchor['id']+'_'+template.name;ob.matrix_world=A@template.matrix_world
                ob.hide_render=False;ob.hide_set(False)
            if stock_templates:count+=1;variant_counts[stock_paths[variant].name]+=1
    # Optional contextual study placement uses the approved component API.
    # Keep it hidden in clean structural and join views.
    context=[];study_record=None
    integration=CAT/'assets/library_study/integration_api.json'
    if integration.exists():
        table_api=next(x for x in json.loads(integration.read_text()) if x['catalogue_id']=='AST-LIB-STUDY-01')
        offset=Vector((1.2,-2.7,0));chair=table_api['approach']['candidate_chairs'][1];folio=table_api['bookstock_mounts'][0]
        placements=[(CAT/'assets/library_study/AST-LIB-STUDY-01_open_shared_table.glb',offset,0),
            (CAT/'assets/furniture/AST-FUR-002_day_reading_chair.glb',offset+Vector(chair['origin_m']),chair['rotation_z_degrees']),
            (CAT/'assets/library_contents/AST-LIB-007_open_folio_stack.glb',offset+Vector(folio['origin_m']),folio['rotation_z_degrees'])]
        for p,loc,angle in placements:
            T=Matrix.Translation(loc)@Matrix.Rotation(math.radians(angle),4,'Z')
            for ob in import_glb(p):
                ob.matrix_world=T@ob.matrix_world;ob.hide_render=True;ob.name='QA_STUDY_CONTEXT_'+ob.name;context.append(ob)
        study_record={'table_translation_m':list(offset),'chair_origin_m':list(offset+Vector(chair['origin_m'])),
           'chair_rotation_z_degrees':chair['rotation_z_degrees'],'folio_origin_m':list(offset+Vector(folio['origin_m'])),
           'folio_rotation_z_degrees':folio['rotation_z_degrees'],'shelf_near_plinth_y_min_m':-.445,
           'chair_rear_y_max_m':-1.1827080631256104,'clear_gap_chair_rear_to_plinth_m':.7377080631256104,
           'purpose':'Independent component study relationship; no original room navigation/rig acceptance',
           'source_api':'assets/library_study/integration_api.json'}
    cam=stage()
    plans={
      'neutral':('structure_stocked_neutral_640',(8,-10,5.1),(2.55,.32,1.78),(640,360),8.25,48),
      'standing':('structure_stocked_standing_640',(7.8,-11.3,1.65),(2.25,-.75,1.63),(640,360),None,47),
      'detail':('structure_stocked_join_detail_1280',(4.3,-4,3.7),(2.55,-.21,2.62),(1280,720),3.45,48),
      'terminal':('structure_terminal_closed_1280',(6.8,5.6,2.8),(4.65,1.85,1.7),(960,1280),4.35,48)}
    for key in views:
        hidden=[]
        for ob in context:ob.hide_render=key!='standing'
        if key=='terminal':
            for ob in bpy.context.scene.objects:
                if ob.type=='MESH' and not ob.hide_render and not ob.name.startswith(('AST-LIB-STR-003','QA_ONLY_')):
                    hidden.append(ob);ob.hide_render=True
        render(cam,*plans[key])
        for ob in hidden:ob.hide_render=False
    (BASE/'qa/render_evidence.json').write_text(json.dumps({'scope':'Imported GLB Blender component evidence only; no original ship room, game or CRT acceptance',
       'structure_source':'exports/AST-LIB-STR-001.glb; AST-LIB-STR-002.glb; AST-LIB-STR-003.glb',
       'stock_sources':[str(p) for p in stock_paths],'stock_group_instances':count,'variant_instance_counts':variant_counts,
       'stock_mesh_data':'Each derived arrangement imported once; anchors duplicate linked mesh/material data',
       'standing_study_context':study_record,'views':views},indent=2)+'\n')
    print('IMPORTED_COMPONENT_RENDER_COMPLETE',count)

if __name__=='__main__':main()
