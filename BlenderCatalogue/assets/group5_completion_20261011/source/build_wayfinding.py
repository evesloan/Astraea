"""Four location-specific physical directory variants, no proposed room numbers."""
from pathlib import Path
import bpy,bmesh,importlib.util,json,math
P=Path(__file__).resolve().parents[1];CAT=P.parents[1]
spec=importlib.util.spec_from_file_location('retail_palette',CAT/'standards/retail_materials.py')
pal=importlib.util.module_from_spec(spec);spec.loader.exec_module(pal);M=pal.materials()
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,lo,hi,role):
    v=[(x,y,z) for x,y,z in [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),(lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]]
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],F);me.update();me.materials.append(M[role])
    uv=me.uv_layers.new(name='metric_material_uv')
    for face in me.polygons:
        axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(face.normal[a]))]
        for li in face.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
    o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
def text(name,body,z,size):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.extrude=.002;c.resolution_u=2
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o)
    o.location=(0,-.083,z);o.rotation_euler=(1.57079632679,0,0);c.materials.append(M['champagne_metal'])
rows=[]
for side in ['port','starboard']:
    for end in ['forward','aft']:
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        box('weighted_plinth',(-.65,-.15,0),(.65,.15,.14),'warm_stone')
        box('profiled_column',(-.57,-.065,.14),(.57,.065,2.50),'ivory_enamel')
        box('recessed_orange_directory',(-.49,-.081,1.10),(.49,-.071,2.41),'retail_terracotta_enamel')
        box('recessed_orange_directory_back',(-.49,.071,1.10),(.49,.081,2.41),'retail_terracotta_enamel')
        box('crown',(-.61,-.09,2.49),(.61,.09,2.58),'ivory_enamel')
        text('heading','D09 / '+side.upper(),2.28,.085)
        text('district',end.upper()+' SHOPS',2.12,.075)
        lines=['ORCHARD MARKET','COPPER KETTLE','PAPER MOON BOOKS','THREAD & SHELL'] if end=='forward' else ['POST & PARCELS','LIVING GIFTS','STARLIGHT BAKERY','COMPANION GAMES']
        for i,line in enumerate(lines):text('venue_'+str(i),line,1.92-i*.14,.065)
        text('orientation',('TOWARDS BOW' if end=='forward' else 'TOWARDS STERN'),1.26,.075)
        text('atrium','ATRIUM / MIDSHIP',.89,.075)
        # Each face carries the same ship-axis orientation and original venue
        # names, readable from both axial travel directions.
        for front in list(bpy.context.scene.objects):
            if front.type=='FONT':
                rear=front.copy();rear.data=front.data.copy();rear.name=front.name+'_back'
                bpy.context.scene.collection.objects.link(rear)
                rear.location=(0,.083,front.location.z)
                rear.rotation_euler=(math.pi/2,0,math.pi)
        # Mesh text is native geometry, legible without a competing UI path.
        for o in list(bpy.context.scene.objects):
            if o.type=='FONT':
                bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
        name='guide_'+side+'_'+end+'_r003'
        native=P/'source'/(name+'.blend');out=P/'exports'/(name+'.glb')
        bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_texcoords=True,export_materials='EXPORT')
        rows.append({'variant':name,'venues':lines,'dimensions_m':[1.3,.3,2.58],'readable_faces':2})
(P/'docs/WAYFINDING_VARIANTS.json').write_text(json.dumps(rows,indent=2)+'\n')
print('GROUP5_WAYFINDING',len(rows))
