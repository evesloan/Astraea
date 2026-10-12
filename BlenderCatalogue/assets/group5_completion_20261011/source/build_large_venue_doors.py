"""Source-parametric foyer sliders;never execute historical export loops."""
from pathlib import Path
import bpy,bmesh,json,hashlib,importlib.util,ast
P=Path(__file__).resolve().parents[1];CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('retail_palette',CAT/'standards/retail_materials.py')
palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
glass=bpy.data.materials.new('GROUP5_large_foyer_glass');glass.use_nodes=True
shader=glass.node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(.18,.32,.30,1)
shader.inputs['Roughness'].default_value=.25;shader.inputs['Transmission Weight'].default_value=.25
shader.inputs['Alpha'].default_value=.3;glass.diffuse_color=(.18,.32,.30,.3);glass.surface_render_method='DITHERED';M['glass']=glass
template=P/'source/build_components.py';parsed=ast.parse(template.read_text())
FACES=ast.literal_eval(next(n.value for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FACES' for t in n.targets)))
# Reuse only the vetted UV/normal-aware primitive functions. Historical top-level
# builders resave old filenames and must never be executed during new authoring.
functions=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']]
exec(compile(ast.Module(body=functions,type_ignores=[]),str(template),'exec'),globals())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for width in [8.0,10.0]:
    height=3.9;quarter=width/4;half=width/2
    native=P/'source/large_venue_doors'/('large_foyer_'+str(int(width))+'m_r001.blend')
    export=P/'exports/large_venue_doors'/('large_foyer_'+str(int(width))+'m_r001.glb')
    if native.exists() and export.exists():
        native_sha=sha(native);export_sha=sha(export)
        bpy.ops.wm.open_mainfile(filepath=str(native))
        repeated=Path('/tmp')/('group5_large_foyer_'+str(int(width))+'m_repeat.glb')
        bpy.ops.export_scene.gltf(filepath=str(repeated),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
        assert sha(repeated)==export_sha and sha(native)==native_sha
        M={role:bpy.data.materials['ASTRAEA_'+role] for role in ['ivory_enamel','champagne_metal','retail_terracotta_enamel']}
        M['glass']=bpy.data.materials['GROUP5_large_foyer_glass']
        records.append({'width_m':width,'height_m':height,'source_meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),
            'native':str(native.relative_to(P)),'native_sha256':native_sha,'export':str(export.relative_to(P)),
            'export_sha256':export_sha,'primitive_template_sha256':sha(template),'fresh_native_repeat_export_byte_identical':True,
            'packed_image_sources':[x.name for x in bpy.data.images if x.packed_file],'panels':4,'wall_mounts':2,'role_and_pressure_acceptance':False})
        continue
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    root=empty('GROUP5_LARGE_FOYER_'+str(int(width))+'M');track=empty('FixedTrack');track.parent=root
    reach=half+quarter+.09
    cube('track_back',(-reach,height+.01,-.02),(reach,height+.20,.04),'ivory_enamel',track)
    cube('track_cap',(-reach,height+.18,-.09),(reach,height+.24,.06),'retail_terracotta_enamel',track)
    cube('track_brass',(-reach,height+.07,-.085),(reach,height+.12,-.075),'champagne_metal',track)
    for x in [-half-.2,half+.2]:
        cube('track_wall_mount_'+str(x),(x-.06,height+.03,.035),(x+.06,height+.06,.21),'champagne_metal',track)
    for side,sgn in [('L',-1),('R',1)]:
        for index in range(2):
            panel=empty('Panel_'+side+str(index));panel.parent=root
            low=-half if side=='L' and index==0 else -quarter if side=='L' else quarter if index==0 else 0
            high=low+quarter;depth=-.06*index
            for name,a,b,c,d in [('stile_left',low,low+.045,.025,height-.025),('stile_right',high-.045,high,.025,height-.025),('bottom_rail',low+.045,high-.045,.025,.11),('top_rail',low+.045,high-.045,height-.11,height-.025),('middle_rail',low+.045,high-.045,1.03,1.085)]:
                cube('Panel_'+side+str(index)+'_'+name,(a,c,depth-.022),(b,d,depth+.022),'champagne_metal',panel)
            cube('Panel_'+side+str(index)+'_glass',(low+.045,.11,depth-.009),(high-.045,height-.11,depth+.009),'glass',panel)
            center=(low+high)/2
            cube('Panel_'+side+str(index)+'_handle',(center-.025,1.11,depth-.075),(center+.025,1.45,depth-.055),'champagne_metal',panel)
            panel['opening_displacement_x']=sgn*((quarter+.05) if index==0 else (half+.05))
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']='Two wide foyer variants for literal existing8m/10m openings;no original cuts,floors,room IDs or capacity changes'
    native.parent.mkdir(exist_ok=True);export.parent.mkdir(exist_ok=True)
    assert not native.exists() and not export.exists(),'Saved revisions remain immutable'
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
    native_sha=sha(native);export_sha=sha(export)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    repeated=Path('/tmp')/('group5_large_foyer_'+str(int(width))+'m_repeat.glb')
    bpy.ops.export_scene.gltf(filepath=str(repeated),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
    assert sha(repeated)==export_sha and sha(native)==native_sha
    records.append({'width_m':width,'height_m':height,'source_meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),
        'native':str(native.relative_to(P)),'native_sha256':native_sha,'export':str(export.relative_to(P)),
        'export_sha256':export_sha,'primitive_template_sha256':sha(template),
        'fresh_native_repeat_export_byte_identical':True,'packed_image_sources':[x.name for x in bpy.data.images if x.packed_file],
        'panels':4,'wall_mounts':2,'role_and_pressure_acceptance':False})
(P/'docs/LARGE_VENUE_DOOR_COMPONENTS.json').write_text(json.dumps({'status':'PASS_SOURCE_COMPONENTS','variants':records,
    'scope':'Two selected source components only;source-floor,moving-source fit and actual controller integration require separate checks;whole-group acceptance remains false'},indent=2)+'\n')
print('GROUP5_LARGE_FOYER_DOOR_SOURCES_PASS',[(r['width_m'],r['source_meshes']) for r in records])
