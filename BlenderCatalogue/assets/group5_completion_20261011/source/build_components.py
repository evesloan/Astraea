"""Additive retail construction: original patterned materials, four-panel surface sliders.
No existing native/export is opened for write. Blender 4.3.2; metre Z-up source.
"""
import bpy, bmesh, json, math, hashlib, importlib.util
from pathlib import Path
P=Path(__file__).resolve().parents[1]
CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('retail_palette',CAT/'standards/retail_materials.py')
palette=importlib.util.module_from_spec(spec);spec.loader.exec_module(palette)
M=palette.materials()
glass=bpy.data.materials.new('GROUP5_retail_door_glass');glass.use_nodes=True
shader=glass.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=(.18,.32,.30,1)
shader.inputs['Roughness'].default_value=.25
shader.inputs['Transmission Weight'].default_value=.25
shader.inputs['Alpha'].default_value=.3
glass.diffuse_color=(.18,.32,.30,.3);glass.surface_render_method='DITHERED'
M['glass']=glass
FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
records=[r for r in json.loads((P/'docs/COMPONENTS.json').read_text()) if r['kind']=='service'] if (P/'docs/COMPONENTS.json').exists() else []
def cube(name,low,high,role,parent):
    mesh=bpy.data.meshes.new(name)
    # Input coordinates are runtime X/Y/Z; source maps to X/-Z/Y.
    verts=[(x,-z,y) for x,y,z in [(low[0],low[1],low[2]),(high[0],low[1],low[2]),(high[0],high[1],low[2]),(low[0],high[1],low[2]),(low[0],low[1],high[2]),(high[0],low[1],high[2]),(high[0],high[1],high[2]),(low[0],high[1],high[2])]]
    mesh.from_pydata(verts,[],FACES);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    mesh.materials.append(M[role]);uv=mesh.uv_layers.new(name='metric_material_uv')
    scale=M[role].get('meters_per_tile_uv',[1,1])
    for face in mesh.polygons:
        axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=axis]
        for li in face.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
    o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=parent
    o['material_role']=role;o['immutable_originals']='additive group5 source only'
    return o
def empty(name):
    o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);return o
for kind,width,height in [('public',3.6,3.8),('service',2.2,3.0)]:
    if kind=='service' and records:continue
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    root=empty('RETAIL_'+kind.upper()+'_SLIDER');track=empty('FixedTrack');track.parent=root
    quarter=width/4;half=width/2
    # Tracks surface-mount above the retained opening. No new jamb reduces it.
    reach=half+quarter+.09
    cube('track_back',(-reach,height+.01,-.02),(reach,height+.20,.04),'ivory_enamel',track)
    cube('track_cap',(-reach,height+.18,-.09),(reach,height+.24,.06),'retail_terracotta_enamel',track)
    cube('track_brass',(-reach,height+.07,-.085),(reach,height+.12,-.075),'champagne_metal',track)
    if kind=='public':
        # Exact surface supports meet the two retained nested jamb faces at v=-5.95.
        # Their tops stay below the curved crown's retained 3.85m bottom.
        for x in [-1.925,1.925]:
            cube('track_jamb_mount_'+str(x),(x-.06,3.811,.035),(x+.06,3.834,.17),'champagne_metal',track)
    for side,sgn in [('L',-1),('R',1)]:
        for index in range(2):
            panel=empty('Panel_'+side+str(index));panel.parent=root
            low=-half if side=='L' and index==0 else -quarter if side=='L' else quarter if index==0 else 0
            high=low+quarter;depth=-.06*index
            for name,a,b,c,d in [('stile_left',low,low+.045,.025,height-.025),('stile_right',high-.045,high,.025,height-.025),('bottom_rail',low+.045,high-.045,.025,.11),('top_rail',low+.045,high-.045,height-.11,height-.025),('middle_rail',low+.045,high-.045,1.03,1.085)]:
                cube('Panel_'+side+str(index)+'_'+name,(a,c,depth-.022),(b,d,depth+.022),'champagne_metal',panel)
            if kind=='public':
                cube('Panel_'+side+str(index)+'_glass',(low+.045,.11,depth-.009),(high-.045,height-.11,depth+.009),'glass',panel)
            else:
                cube('Panel_'+side+str(index)+'_enamel',(low+.045,.11,depth-.015),(high-.045,height-.11,depth+.015),'ivory_enamel',panel)
                cube('Panel_'+side+str(index)+'_kick',(low+.055,.13,depth-.029),(high-.055,.45,depth-.023),'retail_terracotta_enamel',panel)
            # Small handles remain inside each source panel's actual bounds.
            center=(low+high)/2
            cube('Panel_'+side+str(index)+'_handle',(center-.025,1.11,depth-.075),(center+.025,1.45,depth-.055),'champagne_metal',panel)
            panel['opening_displacement_x']=sgn*((quarter+.05) if index==0 else (half+.05))
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['construction_scope']='retail source-fit four-panel surface slider; no pressure/permission acceptance'
    revision='r002' if kind=='public' else 'r001'
    native=P/'source'/('retail_'+kind+'_slider_'+revision+'.blend');out=P/'exports'/('retail_'+kind+'_slider_'+revision+'.glb')
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT',export_extras=True)
    records.append({'kind':kind,'opening_width':width,'opening_height':height,'panel_width':quarter,'panel_height':height-.05,'panel_depth':.044,'open_outer_displacement':quarter+.05,'open_inner_displacement':half+.05,'native':str(native.relative_to(P)),'export':str(out.relative_to(P)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_meshes':sum(o.type=='MESH' for o in scene.objects)})
(P/'docs/COMPONENTS.json').write_text(json.dumps(records,indent=2)+'\n')
print('GROUP5_COMPONENTS',json.dumps(records))
