"""8240mm closed width and8340mm open clearance preserve the actual maker throat."""
from pathlib import Path
import ast,bpy,bmesh,json,hashlib,importlib.util,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('palette',CAT/'standards/retail_materials.py');palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
glass=bpy.data.materials.new('GROUP5_maker_foyer_glass');glass.use_nodes=True;bs=glass.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.32,.30,1);bs.inputs['Alpha'].default_value=.3;bs.inputs['Transmission Weight'].default_value=.25;bs.inputs['Roughness'].default_value=.25;glass.diffuse_color=(.18,.32,.30,.3);glass.surface_render_method='DITHERED';M['glass']=glass
template=P/'source/build_components.py';tree=ast.parse(template.read_text());FACES=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FACES' for t in n.targets)))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']],type_ignores=[]),str(template),'exec'),globals())
native=P/'source/maker_foyer/maker_foyer_8240mm_r001.blend';export=P/'exports/maker_foyer/maker_foyer_8240mm_r001.glb';assert not native.exists() and not export.exists()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);root=empty('GROUP5_MAKER_FOYER_8240MM');track=empty('FixedTrack');track.parent=root
width=8.24;height=3.9;quarter=width/4;half=width/2;reach=half+quarter+.09
cube('track_back',(-reach,height+.01,-.02),(reach,height+.20,.04),'ivory_enamel',track);cube('track_cap',(-reach,height+.18,-.09),(reach,height+.24,.06),'retail_terracotta_enamel',track);cube('track_brass',(-reach,height+.07,-.085),(reach,height+.12,-.075),'champagne_metal',track)
for x in [-half-.2,half+.2]:cube('track_wall_mount_'+str(x),(x-.06,height+.03,.035),(x+.06,height+.06,.21),'champagne_metal',track)
for side,sgn in [('L',-1),('R',1)]:
    for index in range(2):
        panel=empty('Panel_'+side+str(index));panel.parent=root
        low=-half if side=='L' and index==0 else -quarter if side=='L' else quarter if index==0 else 0;high=low+quarter;depth=-.06*index
        for name,a,b,c,d in [('stile_left',low,low+.045,.025,height-.025),('stile_right',high-.045,high,.025,height-.025),('bottom_rail',low+.045,high-.045,.025,.11),('top_rail',low+.045,high-.045,height-.11,height-.025),('middle_rail',low+.045,high-.045,1.03,1.085)]:cube('Panel_'+side+str(index)+'_'+name,(a,c,depth-.022),(b,d,depth+.022),'champagne_metal',panel)
        cube('Panel_'+side+str(index)+'_glass',(low+.045,.11,depth-.009),(high-.045,height-.11,depth+.009),'glass',panel);center=(low+high)/2;cube('Panel_'+side+str(index)+'_handle',(center-.025,1.11,depth-.075),(center+.025,1.45,depth-.055),'champagne_metal',panel)
        panel['opening_displacement_x']=sgn*((quarter+.05) if index==0 else (half+.05))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']='Explicit8.24m maker source-throat variant,avoids narrowing retained8.24m throat;original8m native/export unchanged'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp/group5-maker8240-door-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==esha and sha(native)==nsha
target=ROOT/'Game/assets/models/group5/maker_foyer'/export.name;assert not target.exists();shutil.copyfile(export,target)
(P/'docs/MAKER_FULL_APERTURE_DOOR.json').write_text(json.dumps({'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/maker_foyer/'+export.name,'model_sha256':esha,'width_m':width,'height_m':height,'original_source_throat_width_m':8.24,'open_leaf_inner_edge_clearance_m':width+.10,'source_meshes':33,'fresh_native_repeat_export_byte_identical':True,'scope':'Original source maximum width preserved;largest species,engineering,save/role/pressure and final-art acceptance held'},indent=2)+'\n');print('MAKER_FULL_APERTURE_DOOR_PASS',esha)
