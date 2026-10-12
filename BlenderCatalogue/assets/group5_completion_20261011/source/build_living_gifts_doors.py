"""Existing openings only;left-stacked service leaves clear the retained stock screen."""
from pathlib import Path
import ast,bpy,bmesh,json,hashlib,importlib.util,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('palette',CAT/'standards/retail_materials.py');palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette);M=palette.materials()
glass=bpy.data.materials.new('GROUP5_living_public_glass');glass.use_nodes=True;bs=glass.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.18,.32,.30,1);bs.inputs['Alpha'].default_value=.3;bs.inputs['Transmission Weight'].default_value=.25;bs.inputs['Roughness'].default_value=.25;glass.diffuse_color=(.18,.32,.30,.3);glass.surface_render_method='DITHERED';M['glass']=glass
t=P/'source/build_components.py';tree=ast.parse(t.read_text());FACES=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='FACES' for a in n.targets)))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['cube','empty']],type_ignores=[]),str(t),'exec'),globals())
rows=[]
for kind,width,height in [('public',3.78,2.85),('service_left',2.0,3.0)]:
    native=P/'source/living_gifts_doors'/('living_'+kind+'_r001.blend');export=P/'exports/living_gifts_doors'/('living_'+kind+'_r001.glb');assert not native.exists() and not export.exists()
    if kind=='service_left':
        # Fresh reload from the previous iteration invalidates cached material refs.
        M={role:bpy.data.materials['ASTRAEA_'+role] for role in ['ivory_enamel','champagne_metal','retail_terracotta_enamel']}
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);root=empty('GROUP5_LIVING_'+kind.upper());track=empty('FixedTrack');track.parent=root
    quarter=width/4;half=width/2
    if kind=='public':left=-(half+quarter+.09);right=-left
    else:left=-(half+quarter+.14);right=half+.09
    cube('track_back',(left,height+.01,-.02),(right,height+.20,.04),'ivory_enamel',track);cube('track_cap',(left,height+.18,-.09),(right,height+.24,.06),'retail_terracotta_enamel',track);cube('track_brass',(left,height+.07,-.085),(right,height+.12,-.075),'champagne_metal',track)
    for x in [-half-.10,half+.10]:
        if kind=='public':a,b=.035,.305
        else:a,b=-.275,-.02
        cube('track_wall_mount_'+str(x),(x-.05,height+.03,a),(x+.05,height+.06,b),'champagne_metal',track)
    for label,low,rank in [('L0',-half,0),('L1',-quarter,1),('R0',quarter,3),('R1',0,2)]:
        panel=empty('Panel_'+label);panel.parent=root;high=low+quarter;depth=-(.06*int(label[1]) if kind=='public' else .12*rank)
        for name,a,b,c,d in [('stile_left',low,low+.045,.025,height-.025),('stile_right',high-.045,high,.025,height-.025),('bottom_rail',low+.045,high-.045,.025,.11),('top_rail',low+.045,high-.045,height-.11,height-.025),('middle_rail',low+.045,high-.045,1.03,1.085)]:cube('Panel_'+label+'_'+name,(a,c,depth-.022),(b,d,depth+.022),'champagne_metal',panel)
        cube('Panel_'+label+'_field',(low+.045,.11,depth-.009),(high-.045,height-.11,depth+.009),'glass' if kind=='public' else 'ivory_enamel',panel)
        center=(low+high)/2;cube('Panel_'+label+'_handle',(center-.025,1.11,depth-.075),(center+.025,1.45,depth-.055),'champagne_metal',panel)
        if kind=='public':travel=(-1 if label[0]=='L' else 1)*((quarter+.05) if label[1]=='0' else (half+.05))
        else:travel=-half-quarter-.05-low
        panel['opening_displacement_x']=travel;panel['collision_depth']=depth
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['scope']='Existing Living Gifts apertures;service-left mode projects aft onto existing retained floor,Group6/interface adoption held'
    native.parent.mkdir(exist_ok=True);export.parent.mkdir(exist_ok=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    nsha=sha(native);esha=sha(export);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=Path('/tmp')/('group5-living-'+kind+'-repeat.glb');bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==esha and sha(native)==nsha
    target=ROOT/'Game/assets/models/group5/living_gifts_doors'/export.name;target.parent.mkdir(exist_ok=True);assert not target.exists();shutil.copyfile(export,target)
    rows.append({'kind':kind,'native':str(native.relative_to(ROOT)),'native_sha256':nsha,'model_path':'res://assets/models/group5/living_gifts_doors/'+export.name,'model_sha256':esha,'width':width,'height':height,'source_meshes':33,'fresh_native_repeat_export_byte_identical':True,'service_depth_pitch_m':.12 if kind=='service_left' else None,'scope':'New source components only;actual original/native/column/floor fit,operating controls,physics and cross-group adoption tested separately'})
(P/'docs/LIVING_GIFTS_DOOR_COMPONENTS.json').write_text(json.dumps({'variants':rows,'source_only':True,'shared_interfaces_accepted':False},indent=2)+'\n');print('LIVING_DOOR_SOURCE_PASS',[(r['kind'],r['model_sha256']) for r in rows])
